"""智能体基类"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from openai import OpenAI
import os

class BaseAgent(ABC):
    """智能体基类"""

    def __init__(self, agent_id: str, name: str, personality: Dict[str, Any]):
        self.agent_id = agent_id
        self.name = name
        self.personality = personality
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "dummy_key"))
        self.memory = {}  # 工作记忆
        self.long_term_memory = None  # ChromaDB连接（后续实现）

    @abstractmethod
    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """思考并产生行为"""
        pass

    @abstractmethod
    def act(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """执行行为"""
        pass

    def query_llm(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """调用大语言模型"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            # 如果API调用失败，返回默认响应用于演示
            print(f"[LLM调用失败: {e}] 使用模拟响应")
            return self._mock_llm_response(prompt, system_prompt)

    def _mock_llm_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """模拟LLM响应（用于演示）"""
        if "剧本" in prompt or "戏剧" in prompt:
            return """{
  "title": "霓虹灯下的抉择",
  "synopsis": "艾丽丝在第六街遇到了一个神秘的陌生人，他似乎知道关于空洞的重要秘密",
  "script": [
    {"character": "艾丽丝", "dialogue": "你是谁？为什么一直跟着我？", "action": "警惕地后退一步"},
    {"character": "陌生人", "dialogue": "我是来帮助你的，艾丽丝。关于空洞，你知道的还不够多。", "action": "递过一张折叠的纸条"},
    {"character": "艾丽丝", "dialogue": "这...这是什么？", "action": "接过纸条，仔细查看"},
    {"character": "陌生人", "dialogue": "这是你一直在寻找的答案。但是，要小心，有人在监视我们。", "action": "环顾四周，压低声音"}
  ],
  "expected_outcome": "艾丽丝获得重要线索，但陷入了更大的危险"
}"""
        elif "评价" in prompt or "评分" in prompt:
            return """剧情连贯性：8分
角色一致性：9分
情感共鸣：7分
创新性：8分
整体体验：8分

评语：整体演出流畅，角色塑造鲜明，情感表达自然。"""
        elif "反应" in prompt:
            return "我微微眯起眼睛，感受着这份微小的美好，心中的疲惫似乎消散了一些。"
        else:
            return "我理解了，让我想想..."

    def remember(self, key: str, value: Any):
        """存储到工作记忆"""
        self.memory[key] = value

    def recall(self, key: str) -> Any:
        """从工作记忆检索"""
        return self.memory.get(key)

    def clear_memory(self):
        """清空工作记忆"""
        self.memory.clear()
