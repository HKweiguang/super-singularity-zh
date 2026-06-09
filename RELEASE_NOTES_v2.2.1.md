## 🎯 Highlights

**Singularity v2.2.1** 在 v2.2.0 的 `references/` 顶层定义体系基础上，修复了审计引擎的编号重复检测误报问题。

---

## 🐛 Bug Fixes

### audit-engine：编号重复检测不再误报引用

**问题**：`id_continuity_rule` 将文档内对同一编号的**多次引用**（如正文中"参见 REQ-001"、表格"关联故事"列中的 `STORY-001`）误判为"重复定义"，产生干扰性报错。

**修复**：在 `MarkdownExtractor` 中增加 `is_definition` 标记，区分两种位置：
- **定义位置**：表格第一列（编号列）、列表项开头 —— 参与重复检测
- **引用位置**：正文、表格其他列 —— 不参与重复检测，仅做统计

**验证**：
- `REQ-001` 定义 1 次 + 正文引用 2 次 → **PASS**（不再误报）
- `REQ-001` 在表格第一列出现 2 次 → **FAIL**（仍能正确检出真正重复）

**向后兼容**：旧代码路径中无 `is_definition` 字段的编号默认视为定义，不影响现有规则。

---

## ✨ What's New (from v2.2.0)

### references/ 顶层定义体系

- `references/top-level/generic-top-level-template.md` — 通用跨产物契约模板
- `references/workflow/generic-workflow.md` — 通用工作流定义模板
- `references/steps/generic-step.md` — 通用步骤模板（含审计要求）
- `references/steps/software-engineering-step.md` — 软件工程 PRD 示例
- `references/examples/generic-example.md` — "智能工单系统"完整填写示例

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
| v2.2.1 | 修复 audit-engine 编号重复检测误报引用的问题 |
| v2.2.0 | 新增 `references/` 顶层定义体系 |
| v2.1.0 | 首次公开发布，10 大核心纪律 skill + 产物链引擎 + 审计工具链 |

---

## 🙏 Acknowledgments

感谢社区反馈，帮助发现并修复了编号重复检测的误报问题。
