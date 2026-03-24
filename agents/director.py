"""剧本家 - 全知视角的剧情创作者"""

from typing import Dict, Any, List
from datetime import datetime
from agents.base_agent import BaseAgent
import json

class Director(BaseAgent):
    """剧本家 - 全知视角的剧情创作者"""

    def __init__(self):
        super().__init__(
            agent_id="director_001",
            name="剧本创作家",
            personality={
                "traits": ["富有想象力", "戏剧感强", "关注角色成长"],
                "style": "戏剧性、情感丰富、注重情节张力"
            }
        )
        self.active_drama = None
        self.act_number = 0
        self.scene_number = 0

    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """思考是否需要创作新戏剧"""
        # 如果有活跃的戏剧，继续执行
        if self.active_drama:
            return {"action": "continue_drama"}

        # 检查是否有足够的动机/冲突点
        protagonist = context.get("protagonist", {})
        world_state = context.get("world_state", {})

        # 分析当前状态，寻找戏剧冲突点
        conflict_points = self._analyze_conflicts(protagonist, world_state)

        if conflict_points and self._should_create_drama(conflict_points):
            return {
                "action": "create_drama",
                "conflict_points": conflict_points
            }

        return {"action": "continue_routine"}

    def act(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """执行动作"""
        if action["action"] == "create_drama":
            return self.create_drama_scenario(action["conflict_points"])
        return {}

    def create_drama_scenario(self, conflict_points: List[str]) -> Dict[str, Any]:
        """创作戏剧场景"""
        prompt = self._build_creation_prompt(conflict_points)

        # 使用LLM创作剧本
        script_outline = self.query_llm(
            prompt,
            system_prompt=self._get_director_system_prompt()
        )

        # 解析剧本（简化版）
        drama_event = self._parse_script_response(script_outline)

        self.active_drama = drama_event
        return drama_event

    def _parse_script_response(self, response: str) -> Dict[str, Any]:
        """解析剧本响应"""
        try:
            # 尝试解析JSON
            # 先提取JSON部分
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                parsed = json.loads(json_str)
            else:
                # 如果解析失败，使用默认剧本
                parsed = self._get_default_script()
        except json.JSONDecodeError:
            # JSON解析失败，使用默认剧本
            parsed = self._get_default_script()

        # 构建完整的事件对象
        return {
            "id": f"drama_{datetime.now().isoformat()}",
            "act_number": self.act_number + 1,
            "scene_number": self.scene_number + 1,
            "timestamp": datetime.now(),
            "title": parsed.get("title", "未命名戏剧"),
            "synopsis": parsed.get("synopsis", ""),
            "script": parsed.get("script", []),
            "characters": ["艾丽丝"],
            "expected_outcome": parsed.get("expected_outcome", "")
        }

    def _get_default_script(self) -> Dict[str, Any]:
        """获取默认剧本（用于演示）"""
        return {
            "title": "霓虹灯下的抉择",
            "synopsis": "艾丽丝在第六街遇到了一个神秘的陌生人，他似乎知道关于空洞的重要秘密",
            "script": [
                {"character": "艾丽丝", "dialogue": "你是谁？为什么一直跟着我？", "action": "警惕地后退一步"},
                {"character": "陌生人", "dialogue": "我是来帮助你的，艾丽丝。关于空洞，你知道的还不够多。", "action": "递过一张折叠的纸条"},
                {"character": "艾丽丝", "dialogue": "这...这是什么？", "action": "接过纸条，仔细查看"},
                {"character": "陌生人", "dialogue": "这是你一直在寻找的答案。但是，要小心，有人在监视我们。", "action": "环顾四周，压低声音"}
            ],
            "expected_outcome": "艾丽丝获得重要线索，但陷入了更大的危险"
        }

    def _analyze_conflicts(self, protagonist: Dict, world_state: Dict) -> List[str]:
        """分析当前冲突点"""
        conflicts = []

        # 检查主角状态
        current_state = protagonist.get("current_state", {})
        if current_state.get("energy", 100) < 30:
            conflicts.append("主角极度疲劳，需要休息但面临紧急任务")

        if current_state.get("mood") == "焦虑":
            conflicts.append("主角面临内心挣扎")

        # 检查世界状态
        active_threats = world_state.get("active_threats", [])
        if active_threats:
            conflicts.append(f"外部威胁: {active_threats[0]}")

        # 检查记忆种子
        memory_seeds = protagonist.get("memory_seeds", [])
        if len(memory_seeds) < 2:
            conflicts.append("主角记忆不足，需要探索和发现")

        # 如果没有找到冲突，添加默认冲突用于演示
        if not conflicts:
            conflicts.append("偶然事件：神秘的陌生人出现")

        return conflicts

    def _should_create_drama(self, conflict_points: List[str]) -> bool:
        """决定是否需要创作戏剧"""
        # 简单决策：至少有一个冲突点
        return len(conflict_points) > 0

    def _build_creation_prompt(self, conflict_points: List[str]) -> str:
        """构建创作提示词"""
        return f"""
作为剧本创作家，你需要为以下冲突点创作一个戏剧场景：

冲突点：
{', '.join(conflict_points)}

请提供一个JSON格式的剧本大纲，包含：
- title: 场景标题
- synopsis: 故事梗概
- script: 剧本段落列表（每个段落包含character, dialogue, action）
- expected_outcome: 预期结局

背景：
- 地点：新艾利都第六街
- 主角：艾丽丝（22岁，好奇心强，乐观，有时会冲动）
- 当前时间：{datetime.now().strftime("%Y-%m-%d %H:%M")}
"""

    def _get_director_system_prompt(self) -> str:
        """获取剧本家系统提示词"""
        return """
你是一位富有才华的剧本创作家，擅长创造引人入胜的故事场景。
你的风格是戏剧性强、情感丰富，注重角色成长和情节张力。
请创作符合绝区零世界观的剧情，包含真实的冲突和情感。
"""

    def update_drama_progress(self, actual_outcome: str):
        """更新戏剧进展"""
        if self.active_drama:
            self.active_drama["actual_outcome"] = actual_outcome
            self.scene_number += 1
            if actual_outcome == "completed":
                self.act_number += 1
                self.scene_number = 0

    def clear_active_drama(self):
        """清除当前活跃戏剧"""
        self.active_drama = None
