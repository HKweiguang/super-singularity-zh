# Singularity · 超级奇点

> **通用工程全链路纪律框架，让 AI 从「能做」到「可信赖」。**

**版本**：v3.1.0  
**许可证**：MIT

---

## Singularity 是什么？

Singularity 是一套**通用工程纪律**，不是工具集。

它回答的不是"用什么技术"，而是**"在什么时机、以什么顺序、用什么标准做决策"**。简单说：它给 AI 立规矩——先理解再动手，先验证再声称，一次只审查一个产物。

> **关键区别**：Singularity 的产物不限于代码。PRD、交互设计、UI 原型、技术方案、测试计划、合规报告……任何可交付物都是产物，都适用同一套纪律。

---

## 核心架构：三层纪律

```
┌─────────────────────────────────────────────────────────────┐
│  第一层：思考纪律（做任何事之前）                              │
│  ─────────────────────────────────                           │
│  objective-analysis  →  理解真实意图                          │
│  dialectical-thinking  →  看正反两面                          │
│  plan-before-execution  →  书面计划再开工                      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  第二层：执行纪律（做事过程中）                                │
│  ─────────────────────────────────                           │
│  complete-task-execution  →  不跳步、不偷懒                   │
│  evidence-before-claims  →  验证后才声称完成                   │
│  artifact-workflow  →  产物依赖可追溯、变更必传播              │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  第三层：交付纪律（产物完成后）                                │
│  ─────────────────────────────────                           │
│  acceptance-criteria-first  →  先定义标准再生成                 │
│  artifact-review  →  一次只审一个产物                         │
│  artifact-finishing  →  四选一明确收尾状态                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 和 Superpowers 的关系

| | **Singularity** | **Superpowers** |
|--|----------------|-----------------|
| **定位** | 纪律框架（**什么时候做、按什么顺序**） | 能力框架（**怎么做、用什么工具**） |
| **适用产物** | **任何产物**：PRD、设计、文档、配置、代码…… | **主要聚焦代码**：TDD、git、代码审查、子智能体开发 |
| **回答的问题** | "先理解还是先动手？" "验证通过才能声称完成吗？" | "怎么写测试？" "怎么用 git worktree？" "怎么派发子智能体？" |
| **关系** | **前置约束** —— Singularity 决定能不能开始 | **后置实现** —— Superpowers 决定怎么实现 |

**一句话：Singularity 管"该不该做"，Superpowers 管"怎么做"。两者配套使用。**

---

## 什么时候用 Singularity，什么时候用 Superpowers？

```
用户说"帮我写个 PRD / 画个设计稿 / 做个技术方案 / 写段代码"
    ↓
Singularity: objective-analysis → 先理解用户真正想要什么
    ↓
Singularity: dialectical-thinking → 分析风险和对立面
    ↓
Singularity: plan-before-execution → 写书面计划
    ↓
Superpowers: TDD / subagent-driven-development / design-system → 按领域最佳实践实现
    ↓
Singularity: evidence-before-claims → 验证后才声称完成
    ↓
Singularity: artifact-review → 审查产物质量
    ↓
Superpowers: requesting-code-review → 请求审查（代码或设计）
    ↓
Singularity: artifact-finishing → 明确收尾状态
```

---

## 14 个核心 Skill

| 层级 | Skill | 一句话说明 |
|------|-------|-----------|
| 会话启动 | `using-singularity` | 每次会话自动加载纪律栈 |
| 思考 | `objective-analysis` | 先理解真实意图，再行动 |
| 思考 | `dialectical-thinking` | 没有对立面分析，不得形成结论 |
| 思考 | `plan-before-execution` | 没有书面计划，不得执行 |
| 执行 | `complete-task-execution` | 不跳步、不偷懒 |
| 执行 | `evidence-before-claims` | 没有验证就不能声称完成 |
| 执行 | `systematic-problem-solving` | 没有根因调查就不能提出解决方案 |
| 执行 | `clean-evolution` | 新方案替换旧方案，旧逻辑不拖后腿 |
| 产物 | `artifact-workflow` | 产物依赖可追溯、变更必传播 |
| 产物 | `acceptance-criteria-first` | 没有验收标准不得生成内容 |
| 审查 | `artifact-review` | 一次只审查一个产物 |
| 收尾 | `artifact-finishing` | 四选一：归档 / 发布 / 废弃 / 回滚 |
| 变更 | `artifact-isolation` | 并行开发不互相污染 |
| 决策 | `idea-evaluation` | 未经 gap 分析禁止直接输出产物 |

---

## v3.1.0 核心变更

- **统一审查入口**：`audit-framework` + `review-before-acceptance` 合并为 `artifact-review`
- **一次只审查一个产物**：审查报告只出一份，但过程中可查阅上游产物
- **职责分离**：`evidence-before-claims` 从审查子步骤变为**前置条件**
- **DAG 接入**：审查流程引入依赖链扫描
- **移除 "机械检查"**：所有检查统一由 AI 执行

---

## 快速开始

### 安装

```bash
git clone git@github.com:HKweiguang/super-singularity-zh.git
```

在 Kimi Code 中加载插件，会话启动时自动激活 `using-singularity`。

### 自定义工作流

在项目根目录创建 `.artifacts/workflow.yaml` 即可定义自己的产物工作流。产物类型可以是任何格式——Markdown、YAML、JSON、设计稿、三维模型……Singularity 只要求遵守纪律，不限制你用什么工具链。

---

## 核心原则

```
先理解  →  再行动
先计划  →  再执行
先辩证  →  再结论
先验证  →  再声称
```

---

## 致谢

Singularity 的设计灵感来源于系统工程、质量控制理论和辩证唯物主义方法论。它不是一个银弹，而是一套**让 AI 在通用工程领域变得更可信赖的纪律契约**。
