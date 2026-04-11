# Moira Production Architecture

## 目标

Moira 要解决的不是“多个智能体互相说话”，而是“叙事运行时”的工程化问题:

- 世界状态如何稳定演化
- 多智能体如何按固定职责协作
- 记忆如何沉淀并参与后续推理
- 用户如何在运行中干预叙事
- 整个过程如何被追踪、回放、评估与重试

## 为什么旧原型像玩具

- 世界引擎、提示词、状态更新、记忆存储、终端交互耦合在一个进程里
- agent 间靠临时字典和 prompt 传参，没有稳定领域模型
- 记忆层直接绑死到单一向量库，没有事件溯源和结构化状态
- 没有运行实例概念，无法可靠恢复、回放、审计
- 没有明确的边界: 领域逻辑、基础设施、LLM 适配器混杂

## 推荐架构

### 1. API Gateway

对外暴露:

- 创建 narrative run
- 推进一轮叙事
- 注入用户指令
- 查询 run 状态、事件流、记忆摘要
- 回放指定场景

### 2. Domain Layer

核心聚合:

- `NarrativeRun`: 一次叙事实例
- `WorldState`: 世界快照
- `Character`: 主角/NPC/导演代理的结构化画像
- `Scene`: 场景定义与出场条件
- `StoryEvent`: 微事件、关键事件、用户干预、系统裁决
- `MemoryRecord`: 结构化记忆与检索元数据

这一层不依赖具体 LLM、数据库或 Web 框架。

### 3. Application Layer

负责用例编排:

- 创建 run
- 推进 tick/turn
- 触发场景切换
- 执行评审与结算
- 写入事件与状态

### 4. Orchestration Layer

使用状态图描述多智能体协作顺序，而不是把逻辑写死在 if/else:

- `World Planner`
- `Director`
- `Actor`
- `NPC Ensemble`
- `Critic/Judge`
- `Memory Synthesizer`

LangGraph 适合做这一层，因为它更接近可控状态图，而不是黑箱 agent。

### 5. Infrastructure Layer

适配外部系统:

- PostgreSQL: 结构化状态、事件、配置、运行记录
- Redis: 短期缓存、会话态、任务分发
- LLM Gateway: 模型调用、重试、路由、限流
- Vector Store: 后续可接 pgvector，避免一开始把状态散落到独立记忆库

## 建议的生产落地方式

- 第一阶段采用“模块化单体 + 清晰边界”
- 不一开始拆微服务
- 把工作流设计成可持久化状态机
- 当 run 生命周期变长、失败恢复要求更强时，再引入 Temporal 做 durable execution

## 数据流

1. 用户创建 narrative run
2. 系统加载 world template / character setup
3. 编排图决定本轮由哪些 agent 参与
4. 每个 agent 只消费结构化输入并返回结构化输出
5. Application 层统一做裁决、持久化、事件发布
6. 记忆提炼任务异步沉淀长期记忆
7. API/前端按 run_id 查询当前状态与历史
