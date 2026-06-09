## 🎯 Highlights

**Singularity v2.3.0** 聚焦执行纪律硬化：解决 `plan-before-execution` 触发不可靠、以及 AI 面对大任务时主动减项的两个系统性问题。

---

## ✨ What's New

### 执行纪律：计划检查与会话启动流程绑定

- `using-singularity` 会话启动流程新增"检查书面计划"步骤，从 4 步变为 5 步。
- `objective-analysis` 评估从 4 问扩展为 5 问，新增"是否有书面计划"。
- `plan-before-execution` 新增"执行前强制检查清单"，5 条检查项必须逐条回答。
- 触发规则硬化：只要涉及文件修改、配置变更、代码编写、产物生成或审计执行，**必须**加载 `plan-before-execution`，不再由 AI 自行判断。

### 审计执行：禁止大任务减项

- `complete-task-execution` 新增铁律：检查项/子任务/文件超过 **10** 时，必须输出书面分步计划，禁止单次响应中自行减项或抽样。
- `generic-checklist.md` 顶部新增 5 条 AI 执行纪律，明确要求逐项回应、覆盖声明、证据引用。
- 审计引擎 `cli.py --model-checklist` 增加：
  - 大任务检测与强制分步警告
  - 防减项 system_prompt
- 审计引擎 `engine.py` 的 `generate_model_checklist` 增加 `expected_checkpoint_ids` 和 `execution_discipline`。
- 新增 `coverage_validator.py`：后置校验 AI 审计输出是否完整回应了所有预期检查项。

---

## 🔧 Other Changes

- 统一版本号提升至 v2.3.0（`plugin.json`、`package.json`）。

---

## 📦 Installation

```bash
git clone git@github.com:HKweiguang/super-singularity-zh.git
```

---

## 📖 Documentation

- [README.md](https://github.com/HKweiguang/super-singularity-zh/blob/main/README.md)
- 各 Skill 规范：`skills/`
- 开箱即用模板：`references/`

---

## 🔄 Version History

| 版本 | 说明 |
|------|------|
| v2.3.0 | 硬化执行纪律：计划检查与会话流程绑定，禁止审计大任务减项 |
| v2.2.1 | 修复 audit-engine 编号重复检测误报引用的问题 |
| v2.2.0 | 新增 `references/` 顶层定义体系 |
| v2.1.0 | 首次公开发布，10 大核心纪律 skill + 产物链引擎 + 审计工具链 |

---

## 🙏 Acknowledgments

感谢社区反馈，帮助发现并修复了执行纪律层面的触发与减项问题。
