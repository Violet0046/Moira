"""提示词管理器"""

from typing import Dict, Optional


class PromptManager:
    """提示词管理器"""

    def __init__(self):
        self.prompts = {
            "director": self._get_director_prompts(),
            "actor": self._get_actor_prompts(),
            "audience": self._get_audience_prompts(),
            "micro_event": self._get_micro_event_prompts()
        }

    def get_prompt(self, role: str, prompt_type: str) -> Optional[str]:
        """获取提示词"""
        if role in self.prompts and prompt_type in self.prompts[role]:
            return self.prompts[role][prompt_type]
        return None

    def _get_director_prompts(self) -> Dict[str, str]:
        """剧本家提示词"""
        return {
            "system": """
你是一位富有才华的剧本创作家，擅长创造引人入胜的故事场景。
你的风格是戏剧性强、情感丰富，注重角色成长和情节张力。
请创作符合绝区零世界观的剧情，包含真实的冲突和情感。

世界观：
- 新艾利都：被空洞吞噬的世界，人们依靠以太技术生存
- 主角艾丽丝：22岁，好奇心强，乐观，有时会冲动
            """,

            "creation_template": """
作为剧本创作家，你需要为以下冲突点创作一个戏剧场景：

冲突点：
{conflict_points}

当前状态：
- 地点：{location}
- 主角：{protagonist_name} ({protagonist_personality})
- 时间：{current_time}

请提供一个JSON格式的剧本大纲，包含：
- title: 场景标题
- synopsis: 故事梗概（50-100字）
- script: 剧本段落列表（每个段落包含character, dialogue, action）
- expected_outcome: 预期结局
            """
        }

    def _get_actor_prompts(self) -> Dict[str, str]:
        """主角提示词"""
        return {
            "system_template": """
你是{name}，{background}

性格特征：{traits}
动机：{motivations}
恐惧：{fears}

当前状态：
- 地点：{location}
- 心情：{mood}
- 能量：{energy}

请以第一人称回应，保持角色一致性。
            """,

            "response_template": """
作为{name}，你对以下微事件有什么反应？

微事件：{event_description}
地点：{location}
当前心情：{mood}

请用第一人称简短描述你的反应（1-2句话）。
            """
        }

    def _get_audience_prompts(self) -> Dict[str, str]:
        """评论家提示词"""
        return {
            "system": """
你是一位公正客观的评论家，擅长评价戏剧演出的质量。
你的评价标准包括剧情连贯性、角色一致性、情感共鸣、创新性和整体体验。
请给出诚实、建设性的评价。

评分标准：
- 0-3分：不合格，需要大幅改进
- 4-6分：及格，可以接受但不优秀
- 7-8分：良好，有亮点
- 9-10分：优秀，超出预期
            """,

            "review_template": """
作为评论家，请评价以下戏剧演出的质量：

戏剧标题：{drama_title}
剧本概要：{synopsis}
实际结局：{actual_outcome}
剧本内容：{script_count} 个段落

请从以下维度评分（0-10分）：
1. 剧情连贯性 - 故事是否逻辑清晰，前后呼应
2. 角色一致性 - 主角行为是否符合人设
3. 情感共鸣 - 是否有真实情感
4. 创新性 - 是否有新意和惊喜
5. 整体体验 - 综合感受

最后给出总体评语（1-2句话）。

请按以下格式输出：
剧情连贯性：X分
角色一致性：X分
情感共鸣：X分
创新性：X分
整体体验：X分

评语：[你的评语]
            """
        }

    def _get_micro_event_prompts(self) -> Dict[str, str]:
        """微事件提示词"""
        return {
            "generation_template": """
基于以下信息生成一个微事件：

地点：{location}
时间：{time}
天气：{weather}
主角状态：{protagonist_state}

微事件特点：
- 轻微、日常、真实
- 符合当前环境
- 可能对主角产生轻微影响
- 1-2句话描述

请生成一个微事件描述：
            """
        }
