"""主角 - 与世界互动的角色"""

from typing import Dict, Any, List
from datetime import datetime
from agents.base_agent import BaseAgent
from utils.prompt_manager import PromptManager


class Actor(BaseAgent):
    """主角 - 与世界互动的角色"""

    def __init__(self, protagonist_data: Dict[str, Any]):
        super().__init__(
            agent_id="actor_001",
            name=protagonist_data["name"],
            personality=protagonist_data["personality"]
        )
        self.profile = protagonist_data
        self.current_drama_script = None
        self.script_position = 0

        # 提示词管理器
        self.prompt_manager = PromptManager()

    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """主角思考和决策 - 增加记忆搜索"""
        # 1. 先搜索相关记忆作为上下文
        memory_context = self._search_relevant_memories(context)

        # 2. 检查是否有当前剧本
        if self.current_drama_script:
            return self._follow_script(context, memory_context)
        else:
            return self._free_think(context, memory_context)

    def act(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """执行主角行为"""
        action_type = action.get("type")

        if action_type == "dialogue":
            return self._speak(action.get("content", ""), action.get("action_desc", ""))
        elif action_type == "move":
            return self._move(action["destination"])
        elif action_type == "interact":
            return self._interact(action["target"])
        elif action_type == "micro_response":
            return self._micro_response(action["micro_event"])

        return {}

    def _follow_script(self, context: Dict[str, Any], memory_context: str = "") -> Dict[str, Any]:
        """按照剧本行动"""
        if self.script_position < len(self.current_drama_script):
            current_line = self.current_drama_script[self.script_position]

            # 检查是否是NPC对话，需要获取NPC信息
            character = current_line.get("character", "")
            if character != self.name and self.long_term_memory:
                # 从记忆或提示词管理器获取NPC信息
                npc_info = self._get_npc_info(character, context.get("location", ""))
                if npc_info:
                    self.remember(f"npc_{character}", npc_info)

            # 执行当前剧本行
            action = {
                "type": "dialogue",
                "character": character,
                "content": current_line["dialogue"],
                "action_desc": current_line.get("action", "")
            }

            self.script_position += 1

            return {
                "action": action,
                "following_script": True,
                "script_progress": f"{self.script_position}/{len(self.current_drama_script)}"
            }

        # 剧本完成
        return {
            "action": {"type": "script_complete"},
            "following_script": False,
            "outcome": "completed"
        }

    def _free_think(self, context: Dict[str, Any], memory_context: str = "") -> Dict[str, Any]:
        """自由思考和反应"""
        micro_event = context.get("micro_event")
        if micro_event:
            return {
                "action": {
                    "type": "micro_response",
                    "micro_event": micro_event,
                    "response": self._generate_response(micro_event, context, memory_context)
                },
                "following_script": False
            }

        return {"action": {"type": "idle"}}

    def _generate_response(self, micro_event: Dict, context: Dict[str, Any], memory_context: str = "") -> str:
        """生成对微事件的反应（使用记忆搜索）"""

        # 获取当前状态
        location = self.profile['current_state']['location']
        mood = self.profile['current_state']['mood']

        # 构建提示词模板参数
        template_params = {
            "name": self.name,
            "event_description": micro_event['description'],
            "location": location,
            "mood": mood,
            "background": self.profile['background'],
            "traits": ", ".join(self.profile["personality"]["traits"]),
            "motivations": ", ".join(self.profile["personality"]["motivations"]),
            "fears": ", ".join(self.profile["personality"]["fears"]),
            "energy": self.profile['current_state']['energy'],
            "memory_context": memory_context
        }

        # 从PromptManager获取提示词模板
        response_template = self.prompt_manager.get_prompt("actor", "response_template")
        if response_template:
            prompt = response_template.format(**template_params)
        else:
            # 回退到简单格式
            prompt = f"""作为{self.name}，你对以下微事件有什么反应？

微事件：{micro_event['description']}
地点：{location}
当前心情：{mood}

请用第一人称简短描述你的反应（1-2句话）。
"""

        system_prompt = self._get_actor_system_prompt()

        # 调用LLM（启用记忆搜索）
        # 注意：这里的 query_llm 暂未在 base_agent 中支持 use_memory=True，
        # 如果你后续还没实现，可能会在这里报错。作为修复语法，这里保留你的原样。
        response = self.query_llm(prompt, system_prompt, use_memory=True, top_k=3)

        # 将这次反应存储为记忆
        self._store_experience_memory(micro_event, response)

        return response

    def _get_npc_info(self, character_name: str, location: str) -> Dict[str, Any]:
        """获取NPC信息"""
        # 首先从工作记忆查找
        npc_info = self.recall(f"npc_{character_name}")
        if npc_info:
            return npc_info

        # 从长期记忆搜索
        if self.long_term_memory:
            # 注意：需确保 long_term_memory 实例中有 search_npc 方法
            results = getattr(self.long_term_memory, 'search_npc', lambda **kwargs: [])(
                query=character_name,
                location=location,
                n_results=1
            )
            if results:
                return {
                    'name': character_name,
                    'description': results[0]['metadata'].get('description', ''),
                    'personality': results[0]['metadata'].get('personality', ''),
                    'role': results[0]['metadata'].get('role', '')
                }

        # 从PromptManager获取默认NPC模板
        npc_template = self.prompt_manager.get_prompt("npc", "default_template")
        if npc_template:
            return {
                'name': character_name,
                'description': npc_template.get('description', '未知的陌生人'),
                'personality': npc_template.get('personality', '神秘'),
                'role': npc_template.get('role', '路人')
            }

        return None

    def _search_relevant_memories(self, context: Dict[str, Any]) -> str:
        """搜索相关记忆作为决策上下文"""
        query = self._build_search_query(context)
        # 注意：_search_memory 在当前类和基类中尚未实现，这里增加一个安全回退避免报错
        if hasattr(self, '_search_memory'):
            results = self._search_memory(query, top_k=5)
            return self._format_memory_context(results)
        return ""

    def _build_search_query(self, context: Dict[str, Any]) -> str:
        """根据上下文构建搜索查询"""
        # 根据微事件或剧本内容构建查询
        if context.get("micro_event"):
            return context["micro_event"]["description"]
        elif self.current_drama_script:
            return " ".join([line["dialogue"] for line in self.current_drama_script[:3]])
        return "当前情境"

    def _format_memory_context(self, results: List[Dict]) -> str:
        """格式化记忆上下文"""
        if not results:
            return ""

        context_parts = []
        for i, result in enumerate(results, 1):
            context_parts.append(f"[记忆{i}] {result.get('content', '')}")
            if result.get('metadata', {}).get('emotional_valence'):
                # 修复了原来这里漏掉的右括号 ")"
                context_parts[-1] += f" (情感: {result['metadata']['emotional_valence']})"

        return "\n".join(context_parts)

    def _store_experience_memory(self, micro_event: Dict, response: str):
        """存储经历到记忆"""
        memory_content = f"在{micro_event['location']}经历了：{micro_event['description']}，我的反应是：{response}"

        # 存储到长期记忆
        if self.long_term_memory and hasattr(self, 'store_memory'):
            self.store_memory(
                content=memory_content,
                memory_type="experience",
                emotional_valence=self._get_emotional_valence(micro_event),
                location=micro_event['location'],
                event_id=micro_event['id']
            )

    def _get_emotional_valence(self, micro_event: Dict) -> str:
        """判断事件的情感倾向"""
        description = micro_event.get('description', '')
        positive_keywords = ['温暖', '美好', '舒适', '愉悦', '愉快', '轻松']
        negative_keywords = ['危险', '威胁', '恐惧', '黑暗', '寒冷', '孤独']

        for word in positive_keywords:
            if word in description:
                return "positive"

        for word in negative_keywords:
            if word in description:
                return "negative"

        return "neutral"

    def _speak(self, dialogue: str, action_desc: str = "") -> Dict[str, Any]:
        """说话"""
        # 将重要对话存储为记忆
        if len(dialogue) > 10:  # 只存储较长的对话
            if self.long_term_memory and hasattr(self, 'store_memory'):
                self.store_memory(
                    content=f"我说：{dialogue}",
                    memory_type="dialogue",
                    emotional_valence="neutral",
                    location=self.profile['current_state']['location']
                )

        result = {
            "type": "dialogue",
            "character": self.name,
            "content": dialogue,
            "timestamp": datetime.now()
        }
        if action_desc:
            result["action_desc"] = action_desc
        return result

    def _move(self, destination: str) -> Dict[str, Any]:
        """移动"""
        from_location = self.profile["current_state"]["location"]
        self.profile["current_state"]["location"] = destination

        # 存储移动记忆
        if self.long_term_memory and hasattr(self, 'store_memory'):
            self.store_memory(
                content=f"从{from_location}移动到{destination}",
                memory_type="movement",
                emotional_valence="neutral",
                location=destination
            )

        return {
            "type": "movement",
            "from": from_location,
            "to": destination,
            "timestamp": datetime.now()
        }

    def _interact(self, target: str) -> Dict[str, Any]:
        """交互"""
        # 存储交互记忆
        if self.long_term_memory and hasattr(self, 'store_memory'):
            self.store_memory(
                content=f"与{target}进行了交互",
                memory_type="interaction",
                emotional_valence="neutral",
                location=self.profile['current_state']['location']
            )

        return {
            "type": "interaction",
            "character": self.name,
            "target": target,
            "timestamp": datetime.now()
        }

    def _micro_response(self, micro_event: Dict) -> Dict[str, Any]:
        """微事件响应"""
        response_text = self._generate_response(micro_event, {"micro_event": micro_event}, "")

        # 更新主角状态
        if micro_event.get("impact"):
            for key, value in micro_event["impact"].items():
                if key == "mood":
                    self.profile["current_state"]["mood"] = value
                elif key == "energy" and isinstance(value, (int, float)):
                    self.profile["current_state"]["energy"] = max(0, min(100,
                        self.profile["current_state"]["energy"] + value))

        return {
            "type": "micro_response",
            "event_id": micro_event["id"],
            "response": response_text,
            "state_changes": micro_event.get("impact", {}),
            "timestamp": datetime.now()
        }

    def set_script(self, script: list):
        """设置当前剧本"""
        self.current_drama_script = script
        self.script_position = 0

        # 将新剧本信息存入记忆
        if self.long_term_memory and script and hasattr(self, 'store_memory'):
            first_line = script[0] if script else {}
            scenario_info = f"进入新戏剧场景：{first_line.get('dialogue', '')}"
            self.store_memory(
                content=scenario_info,
                memory_type="drama_start",
                emotional_valence="neutral",
                location=self.profile['current_state']['location']
            )

    def clear_script(self):
        """清除当前剧本"""
        self.current_drama_script = None
        self.script_position = 0

    def _get_actor_system_prompt(self) -> str:
        """获取主角系统提示词（使用PromptManager）"""
        # 从PromptManager获取系统提示词
        system_prompt = self.prompt_manager.get_prompt("actor", "system_template")
        if system_prompt:
            params = {
                "name": self.name,
                "background": self.profile['background'],
                "traits": ", ".join(self.profile["personality"]["traits"]),
                "motivations": ", ".join(self.profile["personality"]["motivations"]),
                "fears": ", ".join(self.profile["personality"]["fears"]),
                "location": self.profile['current_state']['location'],
                "mood": self.profile['current_state']['mood'],
                "energy": self.profile['current_state']['energy']
            }
            return system_prompt.format(**params)

        # 回退到默认格式
        traits = ", ".join(self.profile["personality"]["traits"])
        motivations = ", ".join(self.profile["personality"]["motivations"])
        fears = ", ".join(self.profile["personality"]["fears"])

        return f"""
你是{self.name}，{self.profile['background']}

性格特征：{traits}
动机：{motivations}
恐惧：{fears}

当前状态：
- 地点：{self.profile['current_state']['location']}
- 心情：{self.profile['current_state']['mood']}
- 能量：{self.profile['current_state']['energy']}

请以第一人称回应，保持角色一致性。
"""

    def update_profile(self, key_path: str, value: Any):
        """更新主角档案（支持嵌套路径）"""
        keys = key_path.split(".")
        current = self.profile
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value

    def get_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            "name": self.name,
            "location": self.profile["current_state"]["location"],
            "energy": self.profile["current_state"]["energy"],
            "mood": self.profile["current_state"]["mood"]
        }