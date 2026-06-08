## 🎯 Highlights

**Singularity v2.2.0 —— 通用工程全链路支持框架。**

本版本补齐了框架的关键拼图——从"协议规范"到"开箱即用模板"的桥梁。新增 `references/` 顶层定义体系，让用户拿到手就知道产物链怎么建、契约怎么写、工作流怎么配。

---

## ✨ What's New

### references/ 顶层定义体系

全新 `references/` 目录，提供通用框架的**开箱即用模板**：

| 模板 | 说明 |
|------|------|
| `references/top-level/generic-top-level-template.md` | 通用跨产物契约模板——项目概述、产物类型定义、术语表、状态值、编号引用契约、版本里程碑、明确不做、待决策问题 |
| `references/workflow/generic-workflow.md` | 通用工作流定义模板——产物类型声明、步骤定义、审计规则、变更传播规则 |
| `references/steps/generic-step.md` | 通用步骤模板——产物头部标准、章节结构、边界规则、审计要求（含 3 轮轮次控制）、变更传播 |
| `references/steps/software-engineering-step.md` | 领域示例——`generic-step` 在软件工程 PRD 产物上的具体化应用 |
| `references/examples/generic-example.md` | 完整填写示例——以"智能工单系统"为案例，展示顶层定义的完整填写方式 |

### 设计原则

- **通用性优先**：所有模板不绑定特定领域，术语、状态值、编号契约均为通用概念
- **协议→实践桥梁**：`artifact-workflow` 之前只有协议（"应该做什么"），现在有了模板（"怎么做"）
- **框架 vs 实例分离**：通用模板归 Singularity，软件工程精细模板归 `e2e-solution-guard`，两者互补

---

## 📦 Installation

作为 Kimi Code 插件使用：

```bash
git clone git@github.com:HKweiguang/super-singularity-zh.git
```

然后在 Kimi Code 中加载插件即可。会话启动时将自动激活 `using-singularity` skill。

---

## 📖 Documentation

- 完整文档见仓库 [README.md](https://github.com/HKweiguang/super-singularity-zh/blob/main/README.md)
- 各 Skill 的详细规范位于 `skills/` 目录下
- 开箱即用模板位于 `references/` 目录下

---

## 🔄 Version History

| 版本 | 说明 |
|------|------|
| v2.2.0 | 新增 `references/` 顶层定义体系，补齐"协议→实践"桥梁 |
| v2.1.0 | 首次公开发布，包含 10 大核心纪律 skill + 产物链引擎 + 审计工具链 |

---

## 🙏 Acknowledgments

感谢所有为 Singularity 框架提供反馈和测试的用户。
