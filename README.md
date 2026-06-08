# Singularity · 超级奇点

> **通用工程全链路支持框架，实现 AI 从「能做」到「可信赖」的能力跃迁。**

**版本**：v2.1.0  
**许可证**：MIT

---

## 为什么需要 Singularity？

当前 AI 助手普遍存在以下问题：

- ❌ **盲目执行** —— 用户说什么就做什么，不问背后的真实目标
- ❌ **计划缺失** —— 直接动手写代码，没有书面计划作为执行契约
- ❌ **辩证匮乏** —— 只给单一方案，不分析风险和对立面
- ❌ **验证缺位** —— 声称完成却不验证，声称修复却不测试
- ❌ **产物孤立** —— PRD 改了，下游设计文档却不同步
- ❌ **得过且过** —— 跳过子任务、偷工减料，交付不完整

**Singularity 以纪律约束为基石，以产物链引擎为载体，以系统方法论为骨架——先理解再行动，先计划再执行，先辩证再结论，先验证再声称。**

---

## 核心特性

| 特性 | 说明 |
|------|------|
| **纪律约束** | 10 大核心 Skill 强制 AI 在任何行动前完成分析、计划、辩证 |
| **产物链引擎** | 自定义工作流，产物依赖可追溯、变更必传播、审计双轨制 |
| **审计框架** | 机械检查（脚本）+ 语义检查（AI），确保产物质量 |
| **DAG 引擎** | 可视化产物依赖图、检测循环依赖、变更影响分析 |
| **干净演进** | 新方案替换旧方案，旧逻辑不成为新实现的锚 |

---

## 十大核心纪律

| Skill | 定位 | 核心铁律 |
|-------|------|---------|
| `objective-analysis` | **会话入口** | 先理解再行动。每次对话以 4 问扫描开场 |
| `plan-before-execution` | **执行前提** | 没有书面计划，不得执行 |
| `dialectical-thinking` | **决策前** | 没有对立面分析，不得形成结论 |
| `complete-task-execution` | **执行中** | 不跳步、不偷懒，子任务必须全部完成 |
| `evidence-before-claims` | **验收前** | 没有验证就不能声称完成 |
| `systematic-problem-solving` | **问题处理** | 没有根因调查就不能提出解决方案 |
| `clean-evolution` | **方案演进** | 新东西替换旧东西，旧东西不成为新东西的锚 |
| `artifact-workflow` | **产物管理** | 依赖可追溯、变更必传播、审计双轨制 |
| `audit-framework` | **质量检查** | 没有系统质量检查就不能接受任何产物 |
| `using-singularity` | **会话启动** | 自动加载 objective-analysis，建立全链路纪律 |

### 扩展能力

| Skill | 定位 |
|-------|------|
| `acceptance-criteria-first` | 生成产物前，先定义验收标准 |
| `review-before-acceptance` | 产物交付前，强制审查不自认一次过 |
| `artifact-isolation` | 并行开发多个特性时，防止产物互相污染 |
| `artifact-finishing` | 审查通过后，四选一明确收尾决策 |
| `idea-evaluation` | 新想法提出时，先评估兼容性和影响范围 |

---

## 工具链

### 审计引擎（audit-engine）

机械检查脚本，支持产物格式、连续性、编号映射、契约追溯等自动化检查。

```bash
# 单文件审计
python3 scripts/audit-engine/cli.py --file <产物路径> --type <产物类型>

# 目录批量审计
python3 scripts/audit-engine/cli.py --dir <产物目录> --type <产物类型>

# 生成检查清单
python3 scripts/audit-engine/cli.py --model-checklist --type <产物类型>
```

**支持产物类型**：`prd` / `interaction` / `ui` / `tech` / `test` / `generic` 及用户自定义类型。

### DAG 引擎（dag-engine）

产物依赖分析工具，支持可视化、循环检测、变更影响分析和执行计划生成。

```bash
# 可视化依赖图
python3 scripts/dag-engine.py --dir <产物目录> --visualize

# 检测循环依赖
python3 scripts/dag-engine.py --dir <产物目录> --detect-cycles

# 变更影响分析
python3 scripts/dag-engine.py --dir <产物目录> --impact <修改文件>

# 执行计划（波次调度 + 关键路径）
python3 scripts/dag-engine.py --dir <产物目录> --execution-plan
```

---

## 安装使用

### 作为 Kimi Code 插件

1. 将本仓库克隆或复制到 Kimi Code 的插件目录：
   ```bash
   git clone git@github.com:HKweiguang/super-singularity-zh.git
   ```

2. 在 Kimi Code 中加载插件，会话启动时将自动激活 `using-singularity` skill。

3. 所有后续对话将自动遵循 Singularity 纪律栈：客观分析 → 辩证审视 → 计划 → 执行 → 验证 → 审计。

### 产物工作流自定义

在项目根目录创建 `.artifacts/` 目录即可自定义工作流：

```
project-root/
├── AGENTS.md
└── .artifacts/
    ├── workflow.md              ← 工作流定义
    ├── steps/                   ← 步骤模板
    │   ├── requirement-step.md
    │   ├── design-step.md
    │   └── implementation-step.md
    ├── top-level/               ← 全局契约
    │   └── project-top-level.md
    └── audit-rules.yaml         ← 自定义审计规则
```

### 开箱即用模板

当项目未自定义 `.artifacts/` 时，Singularity 自动回退到插件内置的 `references/` 模板：

| 模板 | 路径 | 说明 |
|------|------|------|
| **通用顶层定义** | `references/top-level/generic-top-level-template.md` | 定义跨产物共享的术语、状态值、编号契约、版本里程碑 |
| **通用工作流** | `references/workflow/generic-workflow.md` | 定义产物类型、步骤顺序、审计规则、变更传播 |
| **通用步骤模板** | `references/steps/generic-step.md` | 任何产物类型的通用骨架（头部、章节、边界、审计） |
| **软件工程步骤示例** | `references/steps/software-engineering-step.md` | `generic-step.md` 在 PRD 产物上的具体化 |
| **填写示例** | `references/examples/generic-example.md` | 完整填写的「智能工单系统」顶层定义示例 |

> **框架 vs 领域实例**：Singularity 提供**通用协议和最小模板**；`e2e-solution-guard` 提供**软件工程领域的完整实例**（PRD/交互/UI/技术/测试 的全套模板和流程）。两者互补——通用纪律用 Singularity，软件工程产物管理用 e2e-solution-guard。

---

## 项目结构

```
super-singularity-zh/
├── .kimi-plugin/
│   └── plugin.json            ← 插件元数据
├── package.json               ← 包信息
├── skills/                    ← 15 个核心 Skill
│   ├── using-singularity/
│   ├── objective-analysis/
│   ├── plan-before-execution/
│   ├── dialectical-thinking/
│   ├── complete-task-execution/
│   ├── evidence-before-claims/
│   ├── systematic-problem-solving/
│   ├── clean-evolution/
│   ├── artifact-workflow/
│   ├── audit-framework/
│   ├── acceptance-criteria-first/
│   ├── review-before-acceptance/
│   ├── artifact-isolation/
│   ├── artifact-finishing/
│   └── idea-evaluation/
├── scripts/
│   ├── audit-engine/          ← 审计引擎
│   │   ├── cli.py
│   │   ├── engine.py
│   │   ├── rules/             ← 审计规则
│   │   ├── extractor/         ← Markdown 提取器
│   │   ├── checklists/        ← 语义检查清单
│   │   └── config/            ← 配置与模板
│   └── dag/                   ← DAG 引擎
│       ├── extractor.py
│       ├── graph.py
│       └── formatter.py
├── references/                ← 开箱即用模板（通用协议 + 最小示例）
│   ├── top-level/
│   │   └── generic-top-level-template.md
│   ├── steps/
│   │   ├── generic-step.md
│   │   └── software-engineering-step.md
│   ├── workflow/
│   │   └── generic-workflow.md
│   └── examples/
│       └── generic-example.md
├── templates/                 ← 向后兼容（逐步迁移到 references/）
│   └── steps/
└── README.md
```

---

## 核心原则速查

```
先理解  →  再行动
先计划  →  再执行
先辩证  →  再结论
先验证  →  再声称
```

---

## 贡献

Singularity 是一个开放的纪律框架。欢迎通过 Issue 和 PR 提出改进建议。

---

## 致谢

Singularity 的设计灵感来源于系统工程、质量控制理论和辩证唯物主义方法论。它不是一个银弹，而是一套**让 AI 在通用工程领域变得更可信赖的纪律契约**。
