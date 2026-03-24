"""Moira日志系统"""

import logging
from typing import Optional


class MoiraLogger:
    """Moira专用日志系统"""

    def __init__(self, name: str = "Moira"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # 清除已有的处理器
        self.logger.handlers.clear()

        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)

    def debug(self, message: str):
        """调试日志"""
        self.logger.debug(message)

    def info(self, message: str):
        """信息日志"""
        self.logger.info(message)

    def warning(self, message: str):
        """警告日志"""
        self.logger.warning(message)

    def error(self, message: str):
        """错误日志"""
        self.logger.error(message)

    def log_event(self, event_type: str, event_data: dict):
        """记录事件"""
        description = event_data.get('description', 'No description')
        self.info(f"Event [{event_type}]: {description}")

    def log_tick(self, tick_number: int, track: str, result: dict):
        """记录Tick"""
        event_type = result.get('event_type', 'N/A')
        self.info(f"Tick #{tick_number} - Track: {track} - Event: {event_type}")

    def log_performance_review(self, event_id: str, score: float, approved: bool):
        """记录演出评价"""
        status = "APPROVED" if approved else "REJECTED"
        self.info(f"Performance Review [{event_id}] - Score: {score:.1f}/10 - {status}")
