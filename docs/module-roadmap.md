# Module Roadmap

## 核心模块

1. `core`
   负责配置、日志、通用异常、时间与 ID 生成。

2. `domain`
   定义 Moira 的核心对象与规则，是整个项目最先要稳住的部分。

3. `application`
   实现创建 run、推进 run、注入干预、结算场景等用例。

4. `infrastructure`
   放数据库、Redis、LLM、向量检索、消息队列等适配器。

5. `orchestration`
   多智能体状态图，控制导演、角色、NPC、评审之间的协作顺序。

6. `api`
   暴露 HTTP 接口，为前端或控制台提供统一入口。

## 推荐实现顺序

1. 项目骨架和配置
2. 领域模型
3. 数据库模型与仓储
4. run 生命周期用例
5. 编排图最小闭环
6. LLM 接口与结构化输出
7. 记忆系统
8. 可观测性与测试

## 第一批必须先做的领域对象

- `NarrativeRun`
- `WorldState`
- `AgentRole`
- `SceneState`
- `StoryEvent`
- `MemoryRecord`

## 第一批 API

- `POST /api/v1/runs`
- `GET /api/v1/runs/{run_id}`
- `POST /api/v1/runs/{run_id}/advance`
- `POST /api/v1/runs/{run_id}/interventions`
- `GET /api/v1/runs/{run_id}/events`
