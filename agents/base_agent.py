"""智能体基类"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from openai import OpenAI
from openai import AsyncOpenAI
import os
from dotenv import load_dotenv
import asyncio
import time

# 加载环境变量
load_dotenv()

class BaseAgent(ABC):
    """智能体基类"""

    def __init__(self, agent_id: str, name: str, personality: Dict[str, Any]):
        self.agent_id = agent_id
        self.name = name
        self.personality = personality

        # 初始化API客户端（同步和异步）
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or api_key == "your_api_key_here":
            raise ValueError("OPENAI_API_KEY not found in .env file or not set properly")

        self.client = OpenAI(api_key=api_key)
        self.async_client = AsyncOpenAI(api_key=api_key)

        # 工作记忆
        self.memory = {}

        # 长期记忆系统（ChromaDB）
        self.long_term_memory = None

    def set_memory_system(self, memory_system):
        """设置长期记忆系统"""
        self.long_term_memory = memory_system

    @abstractmethod
    def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """思考并产生行为"""
        pass

    @abstractmethod
    def act(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """执行行为"""
        pass

    def query_llm(self, prompt: str, system_prompt: Optional[str] = None,
                 use_memory: bool = True, top_k: int = 3) -> str:
        """调用大语言模型（同步版本）"""
        # 如果启用记忆且记忆系统可用，搜索相关记忆
        memory_context = ""
        if use_memory and self.long_term_memory:
            memory_context = self._search_memory(prompt, top_k)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # 构建用户提示词，包含记忆上下文
        user_content = prompt
        if memory_context:
            user_content = f"相关记忆:\n{memory_context}\n\n当前请求:\n{prompt}"

        messages.append({"role": "user", "content": user_content})

        try:
            response = self.client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"LLM调用失败: {e}")

    async def query_llm_async(self, prompt: str, system_prompt: Optional[str] = None,
                          use_memory: bool = True, top_k: int = 3) -> str:
        """异步调用大语言模型"""
        # 如果启用记忆且记忆系统可用，搜索相关记忆
        memory_context = ""
        if use_memory and self.long_term_memory:
            memory_context = await self._search_memory_async(prompt, top_k)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # 构建用户提示词，包含记忆上下文
        user_content = prompt
        if memory_context:
            user_content = f"相关记忆:\n{memory_context}\n\n当前请求:\n{prompt}"

        messages.append({"role": "user", "content": user_content})

        try:
            response = await self.async_client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"LLM异步调用失败: {e}")

    def _search_memory(self, query: str, top_k: int = 3) -> str:
        """搜索相关记忆（同步）"""
        if not self.long_term_memory:
            return ""

        try:
            results = self.long_term_memory.search_memories(
                query=query,
                agent_id=self.agent_id,
                n_results=top_k
            )

            if not results:
                return ""

            # 格式化记忆上下文
            context_parts = []
            for i, result in enumerate(results, 1):
                context_parts.append(f"[记忆{i}] {result.get('content', '')}")
                if result.get('metadata', {}).get('emotional_valence'):
                    context_parts[-1] += f" (情感: {result['metadata']['emotional_valence']})"

            return "\n".join(context_parts)
        except Exception as e:
            print(f"[记忆搜索警告: {e}]")
            return ""

    async def _search_memory_async(self, query: str, top_k: int = 3) -> str:
        """异步搜索相关记忆"""
        if not self.long_term_memory:
            return ""

        try:
            results = await self.long_term_memory.search_memories_async(
                query=query,
                agent_id=self.agent_id,
                n_results=top_k
            )

            if not results:
                return ""

            # 格式化记忆上下文
            context_parts = []
            for i, result in enumerate(results, 1):
                context_parts.append(f"[记忆{i}] {result.get('content', '')}")
                if result.get('metadata', {}).get('emotional_valence'):
                    context_parts[-1] += f" (情感: {result['metadata']['emotional_valence']})"

            return "\n".join(context_parts)
        except Exception as e:
            print(f"[记忆搜索警告: {e}]")
            return ""

    def store_memory(self, content: str, memory_type: str = "event",
                   emotional_valence: str = "neutral", **kwargs):
        """存储记忆到长期记忆"""
        if not self.long_term_memory:
            return

        try:
            self.long_term_memory.add_memory(
                agent_id=self.agent_id,
                content=content,
                memory_type=memory_type,
                emotional_valence=emotional_valence,
                **kwargs
            )
        except Exception as e:
            print(f"[记忆存储警告: {e}]")

    def remember(self, key: str, value: Any):
        """存储到工作记忆"""
        self.memory[key] = value

    def recall(self, key: str) -> Any:
        """从工作记忆检索"""
        return self.memory.get(key)

    def clear_memory(self):
        """清空工作记忆"""
        self.memory.clear()
