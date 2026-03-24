"""长期记忆系统 - 基于ChromaDB"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
from functools import wraps


def async_wrapper(func):
    """将同步函数包装为异步"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, func, *args, **kwargs)
    return wrapper


class MemorySystem:
    """记忆系统 - 基于ChromaDB的长期记忆"""

    def __init__(self, persist_directory: str = "./moira_memory"):
        """初始化记忆系统"""
        # 创建持久化客户端
        self.client = chromadb.PersistentClient(path=persist_directory, settings=Settings(
            anonymized_telemetry=False,
            allow_reset=True
        ))

        # 初始化集合
        self.collections = {}
        self._init_collections()

    def _init_collections(self):
        """初始化ChromaDB集合"""
        # 事件集合（存储通过的戏剧事件）
        self.collections["drama_events"] = self.client.get_or_create_collection(
            name="drama_events",
            metadata={"description": "存储通过评论家评价的戏剧事件"}
        )

        # 角色记忆集合（存储角色的记忆片段）
        self.collections["character_memories"] = self.client.get_or_create_collection(
            name="character_memories",
            metadata={"description": "存储角色的个人记忆和经历"}
        )

        # 微事件集合（存储常规轨道的微事件）
        self.collections["micro_events"] = self.client.get_or_create_collection(
            name="micro_events",
            metadata={"description": "存储日常微事件"}
        )

        # NPC信息集合
        self.collections["npcs"] = self.client.get_or_create_collection(
            name="npcs",
            metadata={"description": "存储NPC相关信息"}
        )

    def add_drama_event(self, drama_event: Dict[str, Any], performance: List[Dict],
                       review: Dict[str, Any]):
        """添加戏剧事件到记忆"""
        event_id = drama_event["id"]

        # 构建事件文本（用于向量检索）
        event_text = f"""
标题: {drama_event['title']}
概要: {drama_event['synopsis']}
剧本内容: {len(drama_event['script'])} 段
评分: {review['overall_score']:.1f}/10
评价: {review['feedback']}
时间: {drama_event['timestamp']}
        """.strip()

        # 构建元数据
        metadata = {
            "event_type": "drama",
            "title": drama_event['title'],
            "location": drama_event.get('location', 'unknown'),
            "timestamp": drama_event['timestamp'].isoformat(),
            "act_number": drama_event.get('act_number', 1),
            "scene_number": drama_event.get('scene_number', 1),
            "score": review['overall_score'],
            "approved": review['approved'],
            "importance": "high" if review['approved'] else "low"
        }

        # 添加到集合
        self.collections["drama_events"].add(
            documents=[event_text],
            metadatas=[metadata],
            ids=[event_id]
        )

        # 同时添加到角色记忆
        if performance:
            for perf in performance:
                if perf.get('type') == 'dialogue':
                    character = perf.get('character', 'unknown')
                    content = perf.get('content', '')
                    self.add_character_memory(
                        character_id=character,
                        content=f"在《{drama_event['title']}》中: {content}",
                        memory_type="drama_participation",
                        emotional_valence="neutral",
                        event_id=event_id
                    )

    def add_character_memory(self, character_id: str, content: str,
                           memory_type: str = "episodic",
                           emotional_valence: str = "neutral",
                           event_id: Optional[str] = None,
                           **kwargs):
        """添加角色记忆"""
        memory_id = f"{character_id}_{datetime.now().isoformat()}_{hash(content)}"

        metadata = {
            "character_id": character_id,
            "memory_type": memory_type,
            "emotional_valence": emotional_valence,
            "timestamp": datetime.now().isoformat(),
            "importance": "medium"
        }

        if event_id:
            metadata["event_id"] = event_id

        # 添加自定义元数据
        metadata.update(kwargs)

        self.collections["character_memories"].add(
            documents=[content],
            metadatas=[metadata],
            ids=[memory_id]
        )

    def add_micro_event(self, micro_event: Dict[str, Any], response: Dict[str, Any]):
        """添加微事件到记忆"""
        event_id = micro_event["id"]

        event_text = f"""
事件: {micro_event['description']}
地点: {micro_event['location']}
时间: {micro_event['timestamp']}
反应: {response.get('response', '无')}
        """.strip()

        metadata = {
            "event_type": "micro",
            "location": micro_event['location'],
            "timestamp": micro_event['timestamp'].isoformat(),
            "importance": "low"
        }

        self.collections["micro_events"].add(
            documents=[event_text],
            metadatas=[metadata],
            ids=[event_id]
        )

    def add_npc(self, npc_id: str, name: str, description: str,
               personality: str, role: str, location: str,
               **kwargs):
        """添加NPC信息到记忆"""
        npc_text = f"""
姓名: {name}
描述: {description}
性格: {personality}
角色: {role}
位置: {location}
        """.strip()

        metadata = {
            "npc_id": npc_id,
            "name": name,
            "role": role,
            "location": location,
            "timestamp": datetime.now().isoformat()
        }

        metadata.update(kwargs)

        self.collections["npcs"].add(
            documents=[npc_text],
            metadatas=[metadata],
            ids=[npc_id]
        )

    def search_memories(self, query: str, agent_id: Optional[str] = None,
                      memory_type: Optional[str] = None,
                      n_results: int = 5) -> List[Dict[str, Any]]:
        """搜索记忆（同步）"""
        # 确定搜索哪个集合
        collection = self._get_collection_for_search(agent_id, memory_type)

        # 构建过滤条件
        where = {}
        if memory_type:
            where["memory_type"] = memory_type

        # 执行搜索
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where if where else None
        )

        # 格式化结果
        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'id': results['ids'][0][i] if results['ids'] else None,
                    'distance': results['distances'][0][i] if results['distances'] else None
                })

        return formatted_results

    @async_wrapper
    def search_memories_async(self, query: str, agent_id: Optional[str] = None,
                           memory_type: Optional[str] = None,
                           n_results: int = 5) -> List[Dict[str, Any]]:
        """异步搜索记忆"""
        return self.search_memories(query, agent_id, memory_type, n_results)

    def search_npc(self, query: str, location: Optional[str] = None,
                 n_results: int = 5) -> List[Dict[str, Any]]:
        """搜索NPC（同步）"""
        where = {}
        if location:
            where["location"] = location

        results = self.collections["npcs"].query(
            query_texts=[query],
            n_results=n_results,
            where=where if where else None
        )

        formatted_results = []
        if results['documents'] and results['documents'][0]:
            for i, doc in enumerate(results['documents'][0]):
                formatted_results.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'id': results['ids'][0][i] if results['ids'] else None
                })

        return formatted_results

    def _get_collection_for_search(self, agent_id: Optional[str],
                                 memory_type: Optional[str]):
        """根据搜索参数确定使用的集合"""
        if memory_type == "drama":
            return self.collections["drama_events"]
        elif agent_id and agent_id.startswith("actor"):
            # 主角的记忆从character_memories查找
            return self.collections["character_memories"]
        else:
            # 默认搜索角色记忆
            return self.collections["character_memories"]

    def add_memory(self, agent_id: str, content: str, memory_type: str = "event",
                   emotional_valence: str = "neutral", **kwargs):
        """通用记忆添加接口"""
        if agent_id.startswith("actor"):
            self.add_character_memory(
                character_id=agent_id,
                content=content,
                memory_type=memory_type,
                emotional_valence=emotional_valence,
                **kwargs
            )
        elif memory_type == "drama":
            # 这个方法不直接支持，需要完整事件数据
            pass

    def get_stats(self) -> Dict[str, int]:
        """获取记忆统计信息"""
        stats = {}
        for name, collection in self.collections.items():
            try:
                stats[name] = collection.count()
            except:
                stats[name] = 0
        return stats

    def reset(self):
        """重置所有记忆（慎用）"""
        self.client.reset()
        self._init_collections()

    def get_recent_memories(self, collection_name: str = "drama_events",
                          n_results: int = 10) -> List[Dict[str, Any]]:
        """获取最近的记忆"""
        if collection_name not in self.collections:
            return []

        collection = self.collections[collection_name]

        # 按时间排序获取最近的记录
        # ChromaDB不支持直接时间排序，需要获取后手动排序
        results = collection.get(
            limit=n_results,
            include=["documents", "metadatas", "ids"]
        )

        if not results['documents']:
            return []

        # 按timestamp降序排序
        indexed_results = []
        for i, doc in enumerate(results['documents']):
            indexed_results.append({
                'content': doc,
                'metadata': results['metadatas'][i] if results['metadatas'] else {},
                'id': results['ids'][i] if results['ids'] else None
            })

        indexed_results.sort(
            key=lambda x: x['metadata'].get('timestamp', ''),
            reverse=True
        )

        return indexed_results[:n_results]
