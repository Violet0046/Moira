"""世界引擎 - 双轨驱动事件循环核心"""

import time
import random
from datetime import datetime, timedelta
from typing import Dict, Any
from enum import Enum

from agents.director import Director
from agents.actor import Actor
from agents.audience import Audience


class TrackType(Enum):
    """轨道类型"""
    ROUTINE = "routine"  # 常规轨道
    DRAMA = "drama"      # 戏剧轨道


class WorldEngine:
    """世界引擎 - 双轨驱动事件循环核心"""

    def __init__(self, world_data: Dict, protagonist: Dict):
        self.world_data = world_data
        self.protagonist = protagonist

        # 初始化智能体
        self.director = Director()
        self.actor = Actor(protagonist)
        self.audience = Audience()

        # 引擎状态
        self.running = False
        self.tick_interval = 60  # 默认60秒一次Tick
        self.tick_count = 0
        self.current_track = TrackType.ROUTINE

        # 概率参数
        self.drama_probability = 0.5  # 50%概率进入戏剧轨道（演示用）

        # 事件历史
        self.event_history = {
            "micro_events": [],
            "drama_events": [],
            "rejected_events": []
        }

        # 记忆系统（占位，后续连接ChromaDB）
        self.memory_system = None

    def start(self, tick_interval: int = 60):
        """启动引擎"""
        self.running = True
        self.tick_interval = tick_interval

        print(f"世界引擎启动 - Tick间隔: {tick_interval}秒")
        print(f"当前地点: {self.protagonist['current_state']['location']}")

        # 在实际应用中，这里应该使用后台线程或调度器
        # 这里简化为同步循环演示
        self.run_loop()

    def stop(self):
        """停止引擎"""
        self.running = False
        print("世界引擎停止")

    def run_loop(self):
        """主循环"""
        while self.running and self.tick_count < 10:  # 演示限制10次Tick
            self.tick()
            time.sleep(self.tick_interval)

        print(f"演示结束 - 共执行 {self.tick_count} 次Tick")

    def tick(self) -> Dict[str, Any]:
        """执行一次Tick（心跳）"""
        self.tick_count += 1
        timestamp = datetime.now()

        print(f"\n{'='*50}")
        print(f"Tick #{self.tick_count} - {timestamp.strftime('%H:%M:%S')}")
        print(f"{'='*50}")

        # 1. 状态路由 - 决定走哪条轨道
        self._route_to_track()

        # 2. 根据轨道执行不同逻辑
        if self.current_track == TrackType.ROUTINE:
            result = self._execute_routine_track()
        else:
            result = self._execute_drama_track()

        # 3. 更新世界状态
        self._update_world_state()

        return {
            "tick_number": self.tick_count,
            "timestamp": timestamp,
            "track": self.current_track.value,
            "result": result
        }

    def _route_to_track(self):
        """状态路由 - 决定轨道"""
        # 如果有活跃的戏剧事件，继续戏剧轨道
        if self.director.active_drama:
            self.current_track = TrackType.DRAMA
            print(f"→ 路由: 继续戏剧轨道（第{self.director.act_number}幕）")
            return

        # 否则根据概率选择
        if random.random() < self.drama_probability:
            self.current_track = TrackType.DRAMA
            print(f"→ 路由: 进入戏剧轨道（概率触发）")
        else:
            self.current_track = TrackType.ROUTINE
            print(f"→ 路由: 常规轨道（日常陪伴）")

    def _execute_routine_track(self) -> Dict[str, Any]:
        """执行常规轨道"""
        print(f"\n[常规轨道] 生成微事件...")

        # 1. 生成微事件
        micro_event = self._generate_micro_event()
        print(f"微事件: {micro_event['description']}")

        # 2. 主角反应
        actor_context = {
            "micro_event": micro_event,
            "protagonist": self.protagonist,
            "world_state": self.world_data
        }

        actor_thinking = self.actor.think(actor_context)
        actor_action = self.actor.act(actor_thinking["action"])

        print(f"主角反应: {actor_action.get('response', '无特殊反应')}")

        # 3. 存储到历史
        self.event_history["micro_events"].append({
            "tick": self.tick_count,
            "event": micro_event,
            "response": actor_action
        })

        return {
            "event_type": "micro_event",
            "event": micro_event,
            "actor_response": actor_action
        }

    def _execute_drama_track(self) -> Dict[str, Any]:
        """执行戏剧轨道"""
        print(f"\n[戏剧轨道]")

        # 检查是否需要创作新戏剧
        director_context = {
            "protagonist": self.protagonist,
            "world_state": self.world_data
        }

        director_thinking = self.director.think(director_context)

        # 如果有活跃剧本或需要创作新剧本
        if self.director.active_drama or director_thinking["action"] == "create_drama":

            # 1. 创作/获取剧本
            if not self.director.active_drama:
                print("剧本家: 创作新戏剧...")
                drama_event = self.director.act(director_thinking)
                self.actor.set_script(drama_event["script"])
                print(f"戏剧标题: {drama_event['title']}")
                print(f"戏剧概要: {drama_event['synopsis']}")
            else:
                drama_event = self.director.active_drama

            # 2. 主角按剧本演出
            print("\n主角: 开始演出...")
            actor_context = {
                "protagonist": self.protagonist,
                "world_state": self.world_data
            }

            # 演出过程（简化为一次执行整个剧本）
            performance_results = []
            while True:
                actor_thinking = self.actor.think(actor_context)
                if not actor_thinking.get("following_script"):
                    break

                actor_action = self.actor.act(actor_thinking["action"])

                # 只处理对话类型
                if actor_action.get('type') == 'dialogue':
                    content = actor_action.get('content', '')
                    action_desc = actor_action.get('action_desc', '')
                    char = actor_action.get('character', '')
                    print(f"  {char}: {content}")
                    if action_desc:
                        print(f"    ({action_desc})")

                    performance_results.append(actor_action)

                if actor_thinking.get("outcome") == "completed":
                    break

            # 3. 更新戏剧进展
            self.director.update_drama_progress("completed")

            # 4. 评论家评价
            print("\n评论家: 评价演出...")
            audience_context = {
                "drama_event": drama_event
            }

            audience_thinking = self.audience.think(audience_context)
            review = self.audience.act(audience_thinking)

            print(f"总体评分: {review['overall_score']:.1f}/10")
            print(f"评价: {'通过 [OK]' if review['approved'] else '未通过 [X]'}")
            print(f"评语: {review['feedback']}")

            # 5. 决定是否写入世界
            if review["approved"]:
                print("[OK] 演出优秀，写入世界记忆")
                self.event_history["drama_events"].append({
                    "tick": self.tick_count,
                    "event": drama_event,
                    "performance": performance_results,
                    "review": review
                })
            else:
                print("✗ 演出未达标，不写入世界")
                self.event_history["rejected_events"].append({
                    "tick": self.tick_count,
                    "event": drama_event,
                    "review": review
                })

            # 清除剧本
            self.actor.clear_script()
            self.director.clear_active_drama()

            return {
                "event_type": "drama",
                "drama_event": drama_event,
                "performance": performance_results,
                "review": review,
                "approved": review["approved"]
            }

        # 不需要创作戏剧，回退到常规轨道
        self.current_track = TrackType.ROUTINE
        return self._execute_routine_track()

    def _generate_micro_event(self) -> Dict[str, Any]:
        """生成微事件"""
        # 基于当前世界状态生成
        location = self.protagonist["current_state"]["location"]
        location_data = self.world_data["locations"][location]

        # 预定义的微事件模板
        micro_event_templates = [
            {
                "description": "路边的霓虹灯闪烁着温暖的光芒",
                "impact": {"mood": "平静"},
                "triggers": {"time": "evening", "location": "six_street"}
            },
            {
                "description": f"一阵微风拂过，带来了{location_data['features'][0]}的香气",
                "impact": {"energy": 5},
                "triggers": {"location": "six_street"}
            },
            {
                "description": f"在{location_data['features'][1]}听到了熟悉的音乐",
                "impact": {"mood": "愉快"},
                "triggers": {"location": "six_street"}
            },
            {
                "description": "看到天空中飘过的云朵，形状像是一只小猫",
                "impact": {"mood": "好奇"},
                "triggers": {"time": "afternoon"}
            },
            {
                "description": f"在{location_data['name']}遇到了一个友善的陌生人点头致意",
                "impact": {"mood": "开放"},
                "triggers": {"location": location}
            },
            {
                "description": "街角的便利店传来了烤面包的香气",
                "impact": {"energy": 3},
                "triggers": {"location": "six_street"}
            },
            {
                "description": "远处的电视屏幕正在播放关于空洞的新闻",
                "impact": {"mood": "沉思"},
                "triggers": {"location": "six_street"}
            },
            {
                "description": "一只流浪猫从脚边溜过，发出轻柔的叫声",
                "impact": {"mood": "愉悦"},
                "triggers": {"location": "six_street"}
            }
        ]

        # 简单选择
        selected_template = random.choice(micro_event_templates)

        return {
            "id": f"micro_{self.tick_count}_{datetime.now().isoformat()}",
            "type": "routine",
            "timestamp": datetime.now(),
            "location": location,
            "description": selected_template["description"],
            "triggers": selected_template["triggers"],
            "impact": selected_template["impact"]
        }

    def _update_world_state(self):
        """更新世界状态"""
        # 更新时间
        current_time = datetime.strptime(
            self.world_data["time_system"]["current_time"],
            "%H:%M"
        )
        new_time = current_time + timedelta(minutes=self.tick_interval)
        self.world_data["time_system"]["current_time"] = new_time.strftime("%H:%M")

    def get_event_history(self) -> Dict[str, Any]:
        """获取事件历史"""
        return self.event_history

    def get_current_state(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            "world": self.world_data,
            "protagonist": self.protagonist,
            "tick_count": self.tick_count,
            "current_track": self.current_track.value
        }

    def get_statistics(self) -> Dict[str, int]:
        """获取统计信息"""
        return {
            "total_ticks": self.tick_count,
            "micro_events": len(self.event_history["micro_events"]),
            "drama_events": len(self.event_history["drama_events"]),
            "rejected_events": len(self.event_history["rejected_events"])
        }
