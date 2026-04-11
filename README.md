# Moira

Moira 是一个面向生产环境的多智能体叙事平台，不再把“导演/角色/评审/记忆/世界状态”揉成一个脚本原型，而是拆成可测试、可观测、可扩展的服务化架构。

## 推荐技术栈

- API 层: FastAPI
- 配置与数据契约: Pydantic v2 + pydantic-settings
- 关系数据与状态持久化: PostgreSQL + SQLAlchemy 2.0 Async ORM
- 缓存/队列: Redis
- 智能体编排: LangGraph
- 观测性: structlog + OpenTelemetry

## 分层结构

```text
src/moira/
  api/               HTTP 接口层
  application/       用例与编排入口
  domain/            叙事核心领域模型
  infrastructure/    数据库、缓存、LLM、向量检索等适配器
  orchestration/     多智能体状态图与工作流
  core/              配置、日志、通用基础设施
tests/
docs/
```

## 第一阶段目标

1. 打稳项目骨架与配置体系
2. 定义核心领域模型: 世界、角色、场景、事件、记忆、运行实例
3. 接入数据库与仓储
4. 建立叙事编排图
5. 接入 LLM 网关和记忆检索
6. 做可回放、可追踪、可暂停的 narrative run

## 本地启动

```bash
uvicorn moira.main:app --reload --app-dir src
```

## 文档

- 架构说明见 [docs/architecture.md](docs/architecture.md)
- 模块路线见 [docs/module-roadmap.md](docs/module-roadmap.md)
