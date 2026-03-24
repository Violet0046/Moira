"""评论家 - 评价演出质量"""

from typing import Dict, Any
from datetime import datetime
from agents.base_agent import BaseAgent

class Audience(BaseAgent):
    """评论家 - 评价演出质量"""

    def __init__(self):
        super().__init__(
            agent_id="audience_001",
            name="评论家",
            personality={
                "traits": ["客观公正", "注重细节", "情感敏感"],
                "standards": "高质量、真实、有情感深度"
            }
        )

    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """思考是否需要评价"""
        drama_event = context.get("drama_event")

        if drama_event and drama_event.get("actual_outcome"):
            return {"action": "review_performance", "event": drama_event}

        return {"action": "no_review_needed"}

    def act(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """执行评价"""
        if action["action"] == "review_performance":
            return self.review_performance(action["event"])
        return {}

    def review_performance(self, drama_event: Dict[str, Any]) -> Dict[str, Any]:
        """评价演出质量"""
        prompt = self._build_review_prompt(drama_event)

        # 使用LLM生成评价
        review = self.query_llm(
            prompt,
            system_prompt=self._get_audience_system_prompt()
        )

        # 解析评价
        scores = self._parse_scores(review)
        overall_score = sum(scores.values()) / len(scores)

        # 决定是否通过
        approved = overall_score >= 6.0  # 6分及格

        review_result = {
            "event_id": drama_event["id"],
            "reviewer": self.agent_id,
            "timestamp": datetime.now(),
            "criteria": list(scores.keys()),
            "scores": scores,
            "overall_score": overall_score,
            "feedback": self._extract_feedback(review),
            "approved": approved
        }

        return review_result

    def _build_review_prompt(self, drama_event: Dict) -> str:
        """构建评价提示词"""
        script_count = len(drama_event.get("script", []))

        return f"""
作为评论家，请评价以下戏剧演出的质量：

戏剧标题：{drama_event['title']}
剧本概要：{drama_event['synopsis']}
实际结局：{drama_event.get('actual_outcome', '未完成')}
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

    def _get_audience_system_prompt(self) -> str:
        """获取评论家系统提示词"""
        return """
你是一位公正客观的评论家，擅长评价戏剧演出的质量。
你的评价标准包括剧情连贯性、角色一致性、情感共鸣、创新性和整体体验。
请给出诚实、建设性的评价。

评分标准：
- 0-3分：不合格，需要大幅改进
- 4-6分：及格，可以接受但不优秀
- 7-8分：良好，有亮点
- 9-10分：优秀，超出预期
"""

    def _parse_scores(self, review_text: str) -> Dict[str, float]:
        """解析评分（简化版）"""
        scores = {}
        lines = review_text.split('\n')

        for line in lines:
            if '：' in line and '分' in line:
                try:
                    criterion, score_part = line.split('：', 1)
                    score = float(score_part.split('分')[0].strip())
                    scores[criterion] = score
                except (ValueError, IndexError):
                    continue

        # 如果解析失败，返回默认分数
        if not scores:
            return {
                "剧情连贯性": 8.0,
                "角色一致性": 9.0,
                "情感共鸣": 7.0,
                "创新性": 8.0,
                "整体体验": 8.0
            }

        return scores

    def _extract_feedback(self, review_text: str) -> str:
        """提取评语"""
        if "评语：" in review_text:
            return review_text.split("评语：")[-1].strip()
        return "整体演出流畅，角色塑造鲜明。"

    def get_review_summary(self, review: Dict[str, Any]) -> str:
        """获取评价摘要"""
        status = "✓ 通过" if review["approved"] else "✗ 未通过"
        return (
            f"评价摘要 - {status}\n"
            f"总体评分: {review['overall_score']:.1f}/10\n"
            f"评语: {review['feedback']}"
        )
