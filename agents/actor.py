"""主角 - 与世界互动的角色"""

from typing import Dict, Any
from datetime import datetime
from agents.base_agent import BaseAgent

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

    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """主角思考和决策"""
        # 检查是否有当前剧本
        if self.current_drama_script:
            return self._follow_script(context)
        else:
            return self._free_think(context)

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

    def _follow_script(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """按照剧本行动"""
        if self.script_position < len(self.current_drama_script):
            current_line = self.current_drama_script[self.script_position]

            # 执行当前剧本行
            action = {
                "type": "dialogue",
                "character": current_line.get("character", self.name),
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

    def _free_think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """自由思考和反应"""
        micro_event = context.get("micro_event")
        if micro_event:
            return {
                "action": {
                    "type": "micro_response",
                    "micro_event": micro_event,
                    "response": self._generate_response(micro_event)
                },
                "following_script": False
            }

        return {"action": {"type": "idle"}}

    def _generate_response(self, micro_event: Dict) -> str:
        """生成对微事件的反应"""
        prompt = f"""
作为{self.name}，你对以下微事件有什么反应？

微事件：{micro_event['description']}
地点：{micro_event['location']}
当前心情：{self.profile['current_state']['mood']}

请用第一人称简短描述你的反应（1-2句话）。
"""

        system_prompt = self._get_actor_system_prompt()
        return self.query_llm(prompt, system_prompt)

    def _speak(self, dialogue: str, action_desc: str = "") -> Dict[str, Any]:
        """说话"""
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
        self.profile["current_state"]["location"] = destination
        return {
            "type": "movement",
            "from": self.profile["current_state"]["location"],
            "to": destination,
            "timestamp": datetime.now()
        }

    def _interact(self, target: str) -> Dict[str, Any]:
        """交互"""
        return {
            "type": "interaction",
            "character": self.name,
            "target": target,
            "timestamp": datetime.now()
        }

    def _micro_response(self, micro_event: Dict) -> Dict[str, Any]:
        """微事件响应"""
        response_text = self._generate_response(micro_event)

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

    def clear_script(self):
        """清除当前剧本"""
        self.current_drama_script = None
        self.script_position = 0

    def _get_actor_system_prompt(self) -> str:
        """获取主角系统提示词"""
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
