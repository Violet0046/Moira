"""Moira AI - 双轨驱动事件循环系统"""

from word_engine.core import WorldEngine
from world_data import WORLD_DATA, PROTAGONIST
from utils.logger import MoiraLogger


def main():
    """主函数"""
    # 初始化日志
    logger = MoiraLogger()
    logger.info("Moira AI 系统启动")
    logger.info("=" * 50)
    logger.info(f"世界: {WORLD_DATA['name']}")
    logger.info(f"主角: {PROTAGONIST['name']}")
    logger.info("=" * 50)

    # 初始化世界引擎
    logger.info("初始化世界引擎...")
    engine = WorldEngine(WORLD_DATA, PROTAGONIST)

    # 启动引擎（演示模式：运行15次Tick后停止）
    logger.info("启动演示模式 - 2秒间隔，运行15次Tick\n")
    engine.start(tick_interval=2)  # 2秒间隔，便于演示

    # 输出事件历史
    logger.info("\n\n" + "=" * 50)
    logger.info("事件历史摘要")
    logger.info("=" * 50)

    history = engine.get_event_history()
    stats = engine.get_statistics()

    logger.info(f"总Tick数: {stats['total_ticks']}")
    logger.info(f"微事件数量: {stats['micro_events']}")
    logger.info(f"戏剧事件数量: {stats['drama_events']}")
    logger.info(f"被拒事件数量: {stats['rejected_events']}")

    # 显示主角最终状态
    logger.info("\n主角最终状态:")
    logger.info(f"- 位置: {engine.protagonist['current_state']['location']}")
    logger.info(f"- 能量: {engine.protagonist['current_state']['energy']}")
    logger.info(f"- 心情: {engine.protagonist['current_state']['mood']}")

    # 显示通过的事件
    if history["drama_events"]:
        logger.info("\n通过并写入世界的戏剧事件:")
        for event in history["drama_events"]:
            logger.info(f"  - {event['event']['title']} (评分: {event['review']['overall_score']:.1f})")

    # 显示被拒的事件
    if history["rejected_events"]:
        logger.info("\n被拒的戏剧事件:")
        for event in history["rejected_events"]:
            logger.info(f"  - {event['event']['title']} (评分: {event['review']['overall_score']:.1f})")

    logger.info("\n演示完成!")


if __name__ == "__main__":
    main()
