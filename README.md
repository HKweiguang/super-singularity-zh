# Singularity · 超级奇点

> **通用工程全链路纪律框架，让 AI 从「能做」到「可信赖」。**

**版本**：v3.1.0 · **许可证**：MIT

---

## 先讲个故事

你让 AI 写个登录功能。它咔咔一顿输出，然后说："完成了！"

你打开一看——没做密码强度校验，没处理并发冲突，登录态也没设计。你问它怎么没做，它说："你没说要啊。"

这就是问题。**AI 不是不会做，是不知道该做到什么程度才算完。**

Singularity 解决的就是这个：**给 AI 立规矩，让它知道什么时候该停、什么时候该问、什么时候该验证。**

不是让 AI 更聪明，是让 AI 更靠谱。

---

## 这套规矩长什么样？

三层，简单到离谱：

```
先想明白 → 再做 → 做完验
```

展开说：

**第一层：动手之前先动脑子**

用户说"帮我做个功能"，Singularity 不会让 AI 直接写代码。它会先问：你真正想解决什么问题？有没有别的方案？风险在哪？

**第二层：做的时候不偷懒**

写计划、按步骤执行、改了上游记得同步下游、新方案替换旧方案时不让旧代码拖后腿。

**第三层：做完别直接说完成了**

有验收标准才能开始生成。一次只审查一个产物。审完别悬着——归档、发布、废弃、回滚，四选一。

<svg viewBox="0 0 720 420" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#666"/>
    </marker>
  </defs>
  <!-- Layer 1 -->
  <rect x="20" y="20" width="680" height="100" rx="8" fill="#e3f2fd" stroke="#2196f3" stroke-width="2"/>
  <text x="360" y="48" text-anchor="middle" font-size="16" font-weight="bold" fill="#1565c0">第一层：想明白（动手前）</text>
  <text x="200" y="78" text-anchor="middle" font-size="13" fill="#333">理解真实意图</text>
  <text x="360" y="78" text-anchor="middle" font-size="13" fill="#333">看正反两面</text>
  <text x="520" y="78" text-anchor="middle" font-size="13" fill="#333">写书面计划</text>

  <!-- Arrow -->
  <line x1="360" y1="120" x2="360" y2="150" stroke="#666" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Layer 2 -->
  <rect x="20" y="150" width="680" height="100" rx="8" fill="#e8f5e9" stroke="#4caf50" stroke-width="2"/>
  <text x="360" y="178" text-anchor="middle" font-size="16" font-weight="bold" fill="#2e7d32">第二层：动手做（执行中）</text>
  <text x="200" y="208" text-anchor="middle" font-size="13" fill="#333">按计划执行</text>
  <text x="360" y="208" text-anchor="middle" font-size="13" fill="#333">产物可追溯</text>
  <text x="520" y="208" text-anchor="middle" font-size="13" fill="#333">变更必传播</text>

  <!-- Arrow -->
  <line x1="360" y1="250" x2="360" y2="280" stroke="#666" stroke-width="2" marker-end="url(#arrow)"/>

  <!-- Layer 3 -->
  <rect x="20" y="280" width="680" height="100" rx="8" fill="#fff3e0" stroke="#ff9800" stroke-width="2"/>
  <text x="360" y="308" text-anchor="middle" font-size="16" font-weight="bold" fill="#e65100">第三层：验完交（完成后）</text>
  <text x="240" y="338" text-anchor="middle" font-size="13" fill="#333">有标准才生成</text>
  <text x="400" y="338" text-anchor="middle" font-size="13" fill="#333">一次只审一个</text>
  <text x="560" y="338" text-anchor="middle" font-size="13" fill="#333">四选一收尾</text>
</svg>

---

## 产物不只是代码

Singularity 管的是**任何可交付物**，不是只有代码。

一个 Markdown 的需求文档、一份 YAML 的配置、一张 UI 设计稿、一个三维 CAD 模型、一段语音脚本、一份 PDF 合同——都是产物，都适用同一套规矩。

<svg viewBox="0 0 720 340" xmlns="http://www.w3.org/2000/svg">
  <!-- Document -->
  <rect x="20" y="20" width="150" height="130" rx="8" fill="#e3f2fd" stroke="#2196f3" stroke-width="2"/>
  <text x="95" y="45" text-anchor="middle" font-size="14" font-weight="bold" fill="#1565c0">文档类</text>
  <text x="95" y="70" text-anchor="middle" font-size="12" fill="#333">Markdown → PRD</text>
  <text x="95" y="90" text-anchor="middle" font-size="12" fill="#333">YAML → 配置</text>
  <text x="95" y="110" text-anchor="middle" font-size="12" fill="#333">PDF → 合规报告</text>

  <!-- Model -->
  <rect x="190" y="20" width="150" height="130" rx="8" fill="#e8f5e9" stroke="#4caf50" stroke-width="2"/>
  <text x="265" y="45" text-anchor="middle" font-size="14" font-weight="bold" fill="#2e7d32">模型类</text>
  <text x="265" y="70" text-anchor="middle" font-size="12" fill="#333">CAD → 机械零件</text>
  <text x="265" y="90" text-anchor="middle" font-size="12" fill="#333">BIM → 建筑结构</text>
  <text x="265" y="110" text-anchor="middle" font-size="12" fill="#333">STL → 3D 打印</text>

  <!-- Data -->
  <rect x="360" y="20" width="150" height="130" rx="8" fill="#fff3e0" stroke="#ff9800" stroke-width="2"/>
  <text x="435" y="45" text-anchor="middle" font-size="14" font-weight="bold" fill="#e65100">数据类</text>
  <text x="435" y="70" text-anchor="middle" font-size="12" fill="#333">Excel → BOM 清单</text>
  <text x="435" y="90" text-anchor="middle" font-size="12" fill="#333">SQL → 表结构</text>
  <text x="435" y="110" text-anchor="middle" font-size="12" fill="#333">JSON → API 契约</text>

  <!-- Media -->
  <rect x="530" y="20" width="170" height="130" rx="8" fill="#fce4ec" stroke="#e91e63" stroke-width="2"/>
  <text x="615" y="45" text-anchor="middle" font-size="14" font-weight="bold" fill="#c2185b">媒体类</text>
  <text x="615" y="70" text-anchor="middle" font-size="12" fill="#333">视频 → 演示 demo</text>
  <text x="615" y="90" text-anchor="middle" font-size="12" fill="#333">PNG/SVG → UI 稿</text>
  <text x="615" y="110" text-anchor="middle" font-size="12" fill="#333">音频 → 语音脚本</text>

  <!-- Code & Binary -->
  <rect x="20" y="170" width="330" height="70" rx="8" fill="#f3e5f5" stroke="#9c27b0" stroke-width="2"/>
  <text x="185" y="195" text-anchor="middle" font-size="14" font-weight="bold" fill="#6a1b9a">源码 / 二进制</text>
  <text x="185" y="220" text-anchor="middle" font-size="12" fill="#333">Python / Java / C++ / 固件 / 镜像 / 编译产物</text>

  <!-- Config -->
  <rect x="370" y="170" width="330" height="70" rx="8" fill="#e0f7fa" stroke="#00bcd4" stroke-width="2"/>
  <text x="535" y="195" text-anchor="middle" font-size="14" font-weight="bold" fill="#00838f">配置 / 脚本</text>
  <text x="535" y="220" text-anchor="middle" font-size="12" fill="#333">环境配置 / 安全策略 / CI-CD 脚本 / 监控规则</text>
  <!-- Bottom note -->
  <text x="360" y="280" text-anchor="middle" font-size="13" fill="#666">软件、硬件、制造、建筑、医疗、金融、内容、法律、运营……</text>
  <text x="360" y="305" text-anchor="middle" font-size="14" font-weight="bold" fill="#333">任何领域、任何格式都适用同一套纪律</text>
</svg>

---

## 产物之间怎么关联？DAG

产物不是孤立的。PRD 改了一个需求，设计稿、技术方案、测试用例都要跟着变。

Singularity 用 **DAG（有向无环图）** 管理这种依赖。

### 最简单的例子

概念方案 → 详细设计 → 制造数据 + 测试计划

<svg viewBox="0 0 600 120" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow2" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#666"/>
    </marker>
  </defs>
  <rect x="20" y="30" width="120" height="60" rx="8" fill="#e3f2fd" stroke="#2196f3" stroke-width="2"/>
  <text x="80" y="65" text-anchor="middle" font-size="14" fill="#1565c0">概念方案</text>

  <line x1="140" y1="60" x2="200" y2="60" stroke="#666" stroke-width="2" marker-end="url(#arrow2)"/>

  <rect x="200" y="30" width="120" height="60" rx="8" fill="#fff3e0" stroke="#ff9800" stroke-width="2"/>
  <text x="260" y="65" text-anchor="middle" font-size="14" fill="#e65100">详细设计</text>

  <line x1="320" y1="50" x2="380" y2="35" stroke="#666" stroke-width="2" marker-end="url(#arrow2)"/>
  <line x1="320" y1="70" x2="380" y2="85" stroke="#666" stroke-width="2" marker-end="url(#arrow2)"/>

  <rect x="380" y="10" width="120" height="50" rx="8" fill="#e8f5e9" stroke="#4caf50" stroke-width="2"/>
  <text x="440" y="40" text-anchor="middle" font-size="14" fill="#2e7d32">制造数据</text>

  <rect x="380" y="65" width="120" height="50" rx="8" fill="#fce4ec" stroke="#e91e63" stroke-width="2"/>
  <text x="440" y="95" text-anchor="middle" font-size="14" fill="#c2185b">测试计划</text>
</svg>

概念方案改了，详细设计必须同步，制造数据和测试计划跟着更新。

### 依赖怎么建立

每个产物是一个节点，在 `workflow.yaml` 里声明：

```yaml
- id: "设计稿"
  inputs:
    - "PRD.md"          # 引用上游输出
  output:
    path: "design.md"
    type: "design"
```

**关键在这里**：节点 B 的 `inputs` 引用了节点 A 的 `output.path`，DAG 边就自动形成了。

<svg viewBox="0 0 560 160" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow3" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#666"/>
    </marker>
  </defs>
  <!-- Node A -->
  <rect x="20" y="20" width="200" height="120" rx="8" fill="#e3f2fd" stroke="#2196f3" stroke-width="2"/>
  <text x="120" y="50" text-anchor="middle" font-size="15" font-weight="bold" fill="#1565c0">节点 A：PRD</text>
  <text x="120" y="80" text-anchor="middle" font-size="12" fill="#333">inputs: []</text>
  <text x="120" y="110" text-anchor="middle" font-size="12" fill="#333">output.path: PRD.md</text>

  <line x1="220" y1="80" x2="320" y2="80" stroke="#666" stroke-width="2" marker-end="url(#arrow3)"/>
  <text x="270" y="72" text-anchor="middle" font-size="11" fill="#666">引用</text>

  <!-- Node B -->
  <rect x="320" y="20" width="220" height="120" rx="8" fill="#e8f5e9" stroke="#4caf50" stroke-width="2"/>
  <text x="430" y="50" text-anchor="middle" font-size="15" font-weight="bold" fill="#2e7d32">节点 B：设计稿</text>
  <text x="430" y="80" text-anchor="middle" font-size="12" fill="#333">inputs: [PRD.md]</text>
  <text x="430" y="110" text-anchor="middle" font-size="12" fill="#333">output.path: design.md</text>
</svg>

改了 PRD，DAG 引擎自动扫描下游，标出设计稿、技术方案、测试计划——哪些要同步。

---

## 和 Superpowers 的关系

一句话：**Singularity 管"该不该做"，Superpowers 管"怎么做"。**

| | Singularity | Superpowers |
|--|-------------|-------------|
| 管什么 | 纪律约束 | 技术实现 |
| 回答 | "先理解还是先动手？" | "怎么写测试？" |
| 产物 | 任何可交付物 | 主要聚焦代码 |

**实际怎么配合？**

<svg viewBox="0 0 640 380" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow5" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#666"/>
    </marker>
  </defs>
  <!-- User -->
  <rect x="20" y="20" width="100" height="50" rx="8" fill="#fce4ec" stroke="#e91e63" stroke-width="2"/>
  <text x="70" y="50" text-anchor="middle" font-size="14" fill="#c2185b">用户</text>

  <!-- Arrow down -->
  <line x1="70" y1="70" x2="70" y2="110" stroke="#666" stroke-width="2" marker-end="url(#arrow5)"/>
  <text x="100" y="95" font-size="11" fill="#666">帮我做个功能</text>

  <!-- Singularity box -->
  <rect x="20" y="110" width="250" height="180" rx="8" fill="#e3f2fd" stroke="#2196f3" stroke-width="2"/>
  <text x="145" y="140" text-anchor="middle" font-size="15" font-weight="bold" fill="#1565c0">Singularity</text>
  <text x="145" y="165" text-anchor="middle" font-size="12" fill="#333">理解意图 + 辩证分析</text>
  <text x="145" y="190" text-anchor="middle" font-size="12" fill="#333">写书面计划</text>
  <text x="145" y="215" text-anchor="middle" font-size="12" fill="#333">验证 + 审查 + 收尾</text>

  <!-- Arrow to Superpowers -->
  <line x1="270" y1="200" x2="350" y2="200" stroke="#666" stroke-width="2" marker-end="url(#arrow5)"/>
  <text x="310" y="190" text-anchor="middle" font-size="11" fill="#666">按计划执行</text>

  <!-- Superpowers box -->
  <rect x="350" y="110" width="250" height="180" rx="8" fill="#e8f5e9" stroke="#4caf50" stroke-width="2"/>
  <text x="475" y="140" text-anchor="middle" font-size="15" font-weight="bold" fill="#2e7d32">Superpowers</text>
  <text x="475" y="165" text-anchor="middle" font-size="12" fill="#333">TDD / 子智能体开发</text>
  <text x="475" y="190" text-anchor="middle" font-size="12" fill="#333">按技术最佳实践实现</text>

  <!-- Arrow back -->
  <line x1="475" y1="290" x2="475" y2="330" stroke="#666" stroke-width="2" marker-end="url(#arrow5)"/>

  <!-- Product -->
  <rect x="400" y="330" width="150" height="40" rx="8" fill="#fff3e0" stroke="#ff9800" stroke-width="2"/>
  <text x="475" y="355" text-anchor="middle" font-size="13" fill="#e65100">产物完成</text>

  <!-- Arrow to user -->
  <path d="M400 350 L200 350 L200 290" stroke="#666" stroke-width="2" fill="none" marker-end="url(#arrow5)"/>
  <text x="300" y="370" text-anchor="middle" font-size="11" fill="#666">交付</text>
</svg>

Singularity 先定规矩，Superpowers 按规矩干活。配套使用，缺一不可。

---

## 审查：一次只审一个

审查不是走形式。Singularity 的审查流程长这样：

<svg viewBox="0 0 900 260" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <marker id="arrow4" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#666"/>
    </marker>
  </defs>
  <!-- Steps -->
  <rect x="20" y="100" width="100" height="60" rx="8" fill="#e3f2fd" stroke="#2196f3" stroke-width="2"/>
  <text x="70" y="135" text-anchor="middle" font-size="13" fill="#1565c0">产物完成</text>

  <line x1="120" y1="130" x2="160" y2="130" stroke="#666" stroke-width="2" marker-end="url(#arrow4)"/>

  <rect x="160" y="100" width="120" height="60" rx="8" fill="#fff3e0" stroke="#ff9800" stroke-width="2"/>
  <text x="220" y="125" text-anchor="middle" font-size="12" fill="#e65100">验证通过？</text>
  <text x="220" y="145" text-anchor="middle" font-size="11" fill="#666">evidence-before-claims</text>

  <!-- No loop -->
  <path d="M220 160 L220 200 L80 200 L80 160" stroke="#e53935" stroke-width="2" fill="none" marker-end="url(#arrow4)"/>
  <text x="150" y="195" text-anchor="middle" font-size="11" fill="#e53935">修复</text>

  <line x1="280" y1="130" x2="330" y2="130" stroke="#666" stroke-width="2" marker-end="url(#arrow4)"/>

  <rect x="330" y="100" width="100" height="60" rx="8" fill="#e3f2fd" stroke="#2196f3" stroke-width="2"/>
  <text x="380" y="135" text-anchor="middle" font-size="13" fill="#1565c0">准备</text>

  <line x1="430" y1="130" x2="480" y2="130" stroke="#666" stroke-width="2" marker-end="url(#arrow4)"/>

  <rect x="480" y="100" width="120" height="60" rx="8" fill="#e8f5e9" stroke="#4caf50" stroke-width="2"/>
  <text x="540" y="125" text-anchor="middle" font-size="12" fill="#2e7d32">检查清单</text>
  <text x="540" y="145" text-anchor="middle" font-size="11" fill="#666">6 维度客观检查</text>

  <line x1="600" y1="130" x2="650" y2="130" stroke="#666" stroke-width="2" marker-end="url(#arrow4)"/>

  <rect x="650" y="100" width="120" height="60" rx="8" fill="#fce4ec" stroke="#e91e63" stroke-width="2"/>
  <text x="710" y="125" text-anchor="middle" font-size="12" fill="#c2185b">独立审查</text>
  <text x="710" y="145" text-anchor="middle" font-size="11" fill="#666">3 维度主观判断</text>

  <line x1="710" y1="160" x2="710" y2="200" stroke="#666" stroke-width="2" marker-end="url(#arrow4)"/>

  <rect x="650" y="200" width="120" height="50" rx="8" fill="#fff3e0" stroke="#ff9800" stroke-width="2"/>
  <text x="710" y="230" text-anchor="middle" font-size="12" fill="#e65100">通过？</text>

  <!-- Loop back -->
  <path d="M650 225 L580 225 L580 130" stroke="#e53935" stroke-width="2" fill="none" marker-end="url(#arrow4)"/>
  <text x="610" y="220" text-anchor="middle" font-size="11" fill="#e53935">修复</text>

  <!-- Final -->
  <line x1="770" y1="225" x2="820" y2="225" stroke="#666" stroke-width="2" marker-end="url(#arrow4)"/>
  <rect x="820" y="195" width="60" height="60" rx="8" fill="#e8f5e9" stroke="#4caf50" stroke-width="2"/>
  <text x="850" y="230" text-anchor="middle" font-size="13" fill="#2e7d32">下游</text>
</svg>

**一次只审一个产物**。出一份报告，主角是一个产物。但审查过程中可以查阅上游产物作为参考。

---

## 14 个核心纪律

`using-singularity` —— 每次会话自动加载纪律栈  
`objective-analysis` —— 先理解真实意图，再行动  
`dialectical-thinking` —— 没有对立面分析，不得形成结论  
`plan-before-execution` —— 没有书面计划，不得执行  
`complete-task-execution` —— 不跳步、不偷懒  
`evidence-before-claims` —— 没有验证就不能声称完成  
`systematic-problem-solving` —— 没有根因调查就不能提出解决方案  
`clean-evolution` —— 新方案替换旧方案  
`artifact-workflow` —— 产物依赖可追溯、变更必传播  
`acceptance-criteria-first` —— 没有验收标准不得生成内容  
`artifact-review` —— 一次只审查一个产物  
`artifact-finishing` —— 归档 / 发布 / 废弃 / 回滚 四选一  
`artifact-isolation` —— 并行开发不互相污染  
`idea-evaluation` —— 未经 gap 分析禁止直接输出产物

---

## v3.1.0 改了什么

- `audit-framework` + `review-before-acceptance` 合并为 `artifact-review`，统一审查入口
- `evidence-before-claims` 从审查子步骤变为**前置条件**
- 审查流程引入 DAG 引擎做端到端链检查
- 移除"机械检查"概念，所有检查统一由 AI 执行

---

## 快速开始

```bash
git clone git@github.com:HKweiguang/super-singularity-zh.git
```

在 Kimi Code 中加载插件，会话启动时自动激活。

---

Singularity 不是一个银弹，是一套**让 AI 在通用工程领域变得更可信赖的纪律契约**。
