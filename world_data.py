"""Moira世界数据 - 绝区零世界背景和主角人设"""

# 世界背景数据结构
WORLD_DATA = {
    "name": "新艾利都",
    "description": "一个被空洞吞噬的世界，人们依靠以太技术生存",
    "locations": {
        "six_street": {
            "name": "第六街",
            "description": "新艾利都的繁华商业区，充满了霓虹灯和商店",
            "weather": "晴朗",
            "time_phase": "evening",
            "features": ["咖啡馆", "游戏厅", "便利店", "广场"],
            "npcs": ["路人A", "店主", "学生"]
        },
        "hollow": {
            "name": "空洞",
            "description": "危险的异次元空间，充满以太怪物和神秘现象",
            "weather": "迷雾",
            "time_phase": "eternal_night",
            "features": ["以太怪物", "古代遗迹", "神秘现象"],
            "npcs": []
        },
        "cafe": {
            "name": "第六街咖啡馆",
            "description": "舒适的咖啡店，适合休息和思考",
            "weather": "室内",
            "time_phase": "any",
            "features": ["咖啡", "轻音乐", "舒适座椅"],
            "npcs": ["咖啡师", "其他客人"]
        }
    },
    "time_system": {
        "current_time": "18:30",  # 24小时制
        "day_of_week": "Friday",
        "weather": "晴朗",
        "season": "夏季"
    },
    "global_events": [],  # 已发生的世界级事件
    "active_threats": []  # 当前的威胁或任务
}

# 主角人设数据
PROTAGONIST = {
    "name": "艾丽丝",
    "age": 22,
    "personality": {
        "traits": ["好奇心强", "乐观", "有时会冲动"],
        "motivations": ["探索空洞", "帮助他人", "寻找真相"],
        "fears": ["孤独", "失去朋友", "空洞吞噬"]
    },
    "background": "来自外城的年轻探索者，最近来到新艾利都",
    "current_state": {
        "location": "six_street",
        "energy": 80,
        "mood": "平静",
        "inventory": ["以太分析仪", "压缩饼干", "通讯器"],
        "relationships": {
            "剧本家": "合作伙伴",
            "评论家": "信任的朋友"
        }
    },
    "memory_seeds": [
        "第一次来到第六街时的霓虹灯光",
        "在空洞边缘看到的神秘现象",
        "与朋友们的欢乐时光"
    ]
}

# 事件历史记录
EVENT_HISTORY = {
    "micro_events": [],
    "drama_events": [],
    "rejected_events": []
}
