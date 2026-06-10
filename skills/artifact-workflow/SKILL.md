---
name: artifact-workflow
description: 在生成或修改任何项目节点输出时使用，通过上游声明、下游传播确保工作流的端到端可追溯性
---

# 节点工作流（Node Workflow）

> v3.0

## 定位

本 skill 是 **一套协议 + 一份指南**。

| 层次 | 内容 | 说明 |
|------|------|------|
| **CORE（核心）** | 原则、协议 | 与领域无关，任何工作流都必须遵守 |
| **CUSTOM（自定义）** | 工作流定义方法、模板编写指南 | 用户按指南定义自己的节点 |

**使用前提**：`.artifacts/workflow.yaml` 必须存在。不存在时本 skill 不生效。

### 能力边界

- **编排 vs 执行**：artifact-workflow 只负责定义节点顺序、管理依赖、追踪变更传播；具体生成执行由 AI 或 MCP 工具完成
- **节点行为**：由 `output.format` 决定。若该 format 在 `tools` 中有 `output` 段，则用外部工具生成；否则 AI 生成
- **超出 AI 能力的产物**（如二进制文件、CAD 模型）：在 `tools` 中按 format 配置工具，节点声明对应 `output.format` 即可

---

## 1. 何时使用本 Skill

| 场景 | 处理方式 |
|------|---------|
| 用户要求生成/修改某类输出（如需求文档、设计方案、产物模型、配置文件等） | 读取 `.artifacts/workflow.yaml`，按工作流定义执行对应节点 |
| 用户想定义/调整自己的工作流 | 进入「工作流配置模式」，按第6节指南定义工作流 |
| 用户修改了某个节点输出，担心下游不一致 | 触发变更传播协议，扫描下游影响 |


---

## 2. 前置条件

本 skill **仅在 `.artifacts/workflow.yaml` 存在时生效**。不存在则警告提示。

执行任何步骤前，先执行：

```
1. 读取 AGENTS.md（如有）了解项目背景
2. 加载框架级全局契约（`.artifacts/top-level/project-top-level.md`，如有）
   — 定义跨所有产物类型的通用规则（编号、版本、变更传播）
3. 查找 `.artifacts/workflow.yaml`
   ├─ 存在 → 读取 workflow.yaml，确定当前节点、上下游关系
   │         确定当前节点的 output.type
   │         加载产物类型专属契约（`.artifacts/top-level/{type}-top-level.md`，如有）
   │           — 有则加载，无则跳过
   │           — 加载顺序：project-top-level 先，{type}-top-level 后（后者可覆盖前者）
   │         加载对应处理模板（`.artifacts/steps/{type}-step.md`）
   │         按自定义工作流执行
   └─ 不存在 → 警告提示用户：
              "未检测到 .artifacts/workflow.yaml，artifact-workflow 能力未激活。
               如需使用工作流管理，请先按第6节配置。"
4. 按核心原则执行
```

---

## 3. 核心原则（不可违背）

### 3.1 三个不变原则

| 原则 | 含义 | 反模式 |
|------|------|--------|
| **依赖可追溯** | 每个节点必须在 `workflow.yaml` 中声明 `inputs`（引用哪些上游输出） | 节点孤立存在，无法判断它基于什么输入 |
| **变更必传播** | 修改上游节点输出后，必须扫描下游影响、询问用户是否同步、拒绝则标注 `[待同步]` | 改了上游忘了改下游，导致实现漂移 |
| **契约驱动规范** | 跨节点共享的规则（编号、术语、状态）在「全局契约」中统一定义 | 各节点各自定义，导致不一致 |

### 3.2 三个工作模式

| 模式 | 触发条件 | 核心动作 |
|------|---------|---------|
| **新建模式** | 当前节点的输出不存在 | 加载框架级全局契约 + 当前节点的 type-top-level（如有）→ 解析上游 inputs → 按模板生成输出 → 经 audit-framework 审计 → 写入 |
| **修改模式** | 当前节点的输出已存在 | 加载现有输出 → 加载上游 → 扫描下游影响 → 执行修改 → 经 audit-framework 审计 → 更新 |
| **回改模式** | 执行中发现上游定义有缺陷/遗漏/矛盾 | 暂停 → 定位上游 → 评估下游影响 → 用户确认 → 级联修改 → 全量经 audit-framework 重新审计 |

---

## 4. 节点协议

### 4.0 工具配置

`workflow.yaml` 可选包含 `tools` 段，按「格式名」配置输入/输出工具。节点只需声明 `output.format`，自动适配。

```yaml
tools:
  "{格式名}":                 # 与节点 output.format 或上游 output.format 对应
    input:                    # 该格式作为输入时的解析工具（可选）
      type: mcp_call | script | manual
      config:
        ...
    output:                   # 该格式作为输出时的生成工具（可选）
      type: mcp_call | script | manual
      config:
        ...
```

**适配规则**：
- 节点 `output.format` 在 `tools` 中有 `output` 段 → 用该工具生成
- 节点 `output.format` 在 `tools` 中无 `output` 段 → 默认 `ai_generate`
- 上游 `output.format` 在 `tools` 中有 `input` 段 → AI 读取上游文件前，先用该工具预处理为可理解内容

**示例**：

```yaml
tools:
  step:                       # 三维模型格式
    input:
      type: script
      config:
        path: "scripts/step-parser.py"
    output:
      type: mcp_call
      config:
        endpoint: ...
  bin:
    output:
      type: script
      config:
        path: "scripts/build.sh"
```

---

### 4.1 节点定义标准

每个节点在 `workflow.yaml` 中必须声明：

```yaml
- id: "{节点唯一标识}"
  inputs: # 上游输出路径列表（空列表 = 源节点）
    - "{上游输出路径1}"
    - "{上游输出路径2}"
  output: # 单一输出
    path: "{输出路径}"        # 支持通配符（输出集合）
    type: "{产物类型}"        # 决定模板文件名：.artifacts/steps/{type}-step.md
    format: "{输出格式}"      # AI 原生支持的格式直接写；非 AI 格式需在 tools 配置
  prompt: "{AI 指令}"        # 可选。AI 生成节点自定义指令，覆盖 steps 模板默认内容
  metadata: # 可选元数据
    name: "{显示名称}"
    version: "{版本号}"
```

**约束**：
- 每个节点可以有多个 `inputs`，但只能有一个 `output`
- `output.path` 的通配符模式在工作流内必须唯一（不允许两个节点输出相同模式）
  — 若发生冲突，报错并拒绝加载 workflow.yaml，由用户修正
- `inputs` 和 `output.path` 均支持通配符（`*`、`?`、`**`）
- DAG 边由 `inputs` 与上游节点的 `output.path` 匹配自动推导

### 4.2 节点边界规则

| 规则 | 说明 |
|------|------|
| 不写已在上游定义的内容 | 如需求文档不写制造细节 |
| 不写属于下游职责的内容 | 如需求文档不写测试验证 |
| 发现越界内容时标记并提示迁移 | 不在当前节点中默默兼容 |

---

## 5. 变更传播协议

### 5.1 修改上游节点时的强制流程

```
修改节点 A 的 output
    ↓
扫描 workflow.yaml 中所有以 A.output.path 为 input 的下游节点
    ↓
列出影响范围（直接影响 → 间接影响 → 无影响）
    ↓
询问用户是否级联修改/重执行下游节点
    ├─ 用户确认 → 标记下游节点为 pending，重新执行
    └─ 用户拒绝 → 在下游节点 metadata 中标注 [待同步]
    ↓
重新验证（经 audit-framework 全量审计，禁止缩减维度）
```

> **当前状态**：DAG 影响分析工具 `dag-engine.py` 基础功能已可用，AI 可调用脚本自动分析，也可按 §4 节点协议手动推导依赖关系。

### 5.2 修改下游节点时的边界检查

```
修改节点 B
    ↓
读取 B 的 inputs 对应的上游节点 A
    ↓
检查 B 的修改是否超出 A.output 的定义范围
    ├─ 未超出 → 直接修改
    └─ 超出 → 停止，提示先修改上游节点 A
```

---

## 6. 如何自定义工作流

项目在工作目录下创建 `.artifacts/` 目录，按以下结构组织：

```
project-root/
├── AGENTS.md
└── .artifacts/
    ├── workflow.yaml              ← 工作流定义（YAML 格式）
    ├── steps/                   ← 处理模板（每种节点类型一个文件）
    │   ├── concept-step.md
    │   ├── design-step.md
    │   └── 3d_model-step.md
    ├── top-level/               ← 全局契约（跨节点共享规则）
    │   ├── project-top-level.md   ← 框架级规则（跨所有产物类型，必须存在）
    │   └── {type}-top-level.md    ← 产物类型专属规范（可选，按 output.type 匹配加载）
    └── audit-rules.yaml         ← 可选：audit-framework 自定义审计规则（非 artifact-workflow 职责）
```

### 6.1 完整示例

参见同目录下 `examples/workflow.yaml` 文件，包含一个三节点工作流（概念方案 → 详细设计 → 制造数据）的完整定义，可直接复制到项目 `.artifacts/` 目录中使用。

---

## 7. 工具调用

### 7.1 DAG 引擎（依赖分析）

**当前状态**：`dag-engine.py` 基础功能已可用（DAG 构建、循环检测、影响分析、执行波次、可视化），持续迭代中。以下命令从项目根目录执行：

```bash
# 从 YAML workflow 构建 DAG 并可视化
python3 <skill-path>/scripts/dag-engine.py --workflow .artifacts/workflow.yaml --visualize

# 检测循环依赖
python3 <skill-path>/scripts/dag-engine.py --workflow .artifacts/workflow.yaml --detect-cycles

# 变更影响分析（指定节点 ID）
python3 <skill-path>/scripts/dag-engine.py --workflow .artifacts/workflow.yaml --impact <节点ID>

# 执行波次调度 + 关键路径
python3 <skill-path>/scripts/dag-engine.py --workflow .artifacts/workflow.yaml --execution-plan
```

> `<skill-path>` 为 artifact-workflow skill 的实际安装路径。在 Kimi Code 中可通过 skill 目录定位。

---

## 必需子技能

本 skill 只负责节点工作流编排，所有执行纪律由以下 skill 强制执行：

- **在执行任何步骤之前：**
  - **必需子技能：** 使用 `plan-before-execution` —— 开工前检查是否有书面计划
- **在步骤执行期间：**
  - **必需子技能：** 使用 `complete-task-execution` —— 不跳过任何子任务地执行
- **在审计节点输出时：**
  - **必需子技能：** 使用 `audit-framework` —— 在 6 个维度和 3 个层级上进行系统性质量检查
- **在声称完成之前：**
  - **必需子技能：** 使用 `evidence-before-claims` —— 在验收前用证据验证
- **在发现上游定义中的缺陷时：**
  - **必需子技能：** 使用 `systematic-problem-solving` —— 在修补之前找到根因
- **在传播变更或演进设计时：**
  - **必需子技能：** 使用 `clean-evolution` —— 干净地替换旧的，绝不无决策地层叠
- **当工作流步骤涉及编写或修改代码时：**
  - **必需子技能：** 使用 `superpowers:subagent-driven-development` 或 `superpowers:test-driven-development` —— 代码实现属于 superpowers 的领域

---

*Skill 版本：v3.0.0*
