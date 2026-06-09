#!/usr/bin/env python3
"""
审计引擎 CLI

用法:
    python cli.py --file docs/prd-v1.md --type prd
    python cli.py --dir docs/ --type prd
    python cli.py --model-checklist --type prd
    python cli.py --file docs/prd-v1.md --upstream docs/story-v1.md
"""

import argparse
import json
import sys
from pathlib import Path

from engine import AuditEngine


def load_upstream_ids(file_paths: list) -> set:
    """从上游文档中提取编号定义"""
    from extractor import MarkdownExtractor
    extractor = MarkdownExtractor()
    ids = set()

    for path in file_paths:
        content = Path(path).read_text(encoding='utf-8')
        doc = extractor.extract(content)
        for id_info in doc.ids:
            ids.add(id_info['id'])

    return ids


def load_contract_matrix() -> dict:
    """加载契约矩阵配置"""
    config_path = Path(__file__).parent / "config" / "contract_matrix.yaml"
    if not config_path.exists():
        return {}

    try:
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        print("警告：未安装 PyYAML，契约矩阵功能不可用", file=sys.stderr)
        return {}


def format_report(report: dict, format_type: str = "json") -> str:
    """格式化审计报告"""
    if format_type == "json":
        return json.dumps(report, ensure_ascii=False, indent=2)

    # 文本格式
    lines = []
    lines.append("=" * 60)
    lines.append(f"审计报告：{report['file']}")
    lines.append(f"产物类型：{report['doc_type']}")
    lines.append(f"结果：{'✅ 通过' if report['passed'] else '❌ 未通过'}")
    lines.append("=" * 60)

    summary = report.get("summary", {})
    lines.append(f"\n检查点统计：总计 {summary.get('total_checkpoints', 0)} | "
                 f"通过 {summary.get('passed', 0)} | "
                 f"失败 {summary.get('failed', 0)} | "
                 f"不适用 {summary.get('na', 0)} | "
                 f"通过率 {summary.get('pass_rate', 0)}%")

    for result in report.get("results", []):
        lines.append(f"\n【{result['rule_name']}】{'✅' if result['passed'] else '❌'}")
        for cp in result["checkpoints"]:
            icon = "✅" if cp["status"] == "pass" else ("❌" if cp["status"] == "fail" else "⏭️")
            line_info = f"(L{cp['line_number']})" if cp["line_number"] else ""
            lines.append(f"  {icon} [{cp['id']}] {cp['item']} {line_info}")
            if cp["note"]:
                lines.append(f"      备注：{cp['note']}")

    lines.append("\n" + "-" * 60)
    lines.append("📋 下一步：按 artifact-workflow §4.3 执行语义检查")
    lines.append("   参考：checklists/{type}-checklist.md 逐项判断")
    lines.append("-" * 60)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Super-Singularity 审计引擎")
    parser.add_argument("--file", help="审计单个文件")
    parser.add_argument("--dir", help="审计目录下的所有 .md 文件")
    parser.add_argument("--type", default="generic", help="产物类型")
    parser.add_argument("--config-dir", help="自定义配置目录路径（覆盖默认和项目级配置）")
    parser.add_argument("--upstream", nargs="+", help="上游文档路径（用于双向映射检查）")
    parser.add_argument("--model-checklist", action="store_true",
                        help="生成模型检查清单（AI 逐条判断模式）")
    parser.add_argument("--format", default="text", choices=["text", "json"],
                        help="输出格式")
    parser.add_argument("--output", help="输出文件路径（默认 stdout）")

    args = parser.parse_args()

    # 设置自定义配置目录（需在加载类型之前）
    if args.config_dir:
        from config import set_config_dir
        set_config_dir(args.config_dir)

    # 动态加载类型选项并验证
    from config import load_artifact_types
    type_choices = list(load_artifact_types().get("types", {}).keys())
    if args.type not in type_choices:
        parser.error(
            f"argument --type: invalid choice: '{args.type}' "
            f"(choose from {', '.join(type_choices)})"
        )

    engine = AuditEngine()

    # 构建上下文
    context = {}

    # 加载上游文档编号
    if args.upstream:
        upstream_ids = load_upstream_ids(args.upstream)
        context["upstream_ids"] = upstream_ids
        context["upstream_docs"] = args.upstream

    # 加载契约矩阵
    contract_matrix = load_contract_matrix()
    if contract_matrix:
        context["contract_matrix"] = contract_matrix

    # 生成模型检查清单模式
    if args.model_checklist:
        from config import load_checklist

        checklist = engine.generate_model_checklist(args.type)
        semantic_checklist = load_checklist(args.type)

        # 将语义检查清单附加到输出
        if semantic_checklist:
            checklist["semantic_checklist"] = {
                "source": f"checklists/{args.type}-checklist.md (或 generic-checklist.md)",
                "content": semantic_checklist
            }

        # 大任务检测：检查项超过阈值时附加强制分步警告
        item_count = len(checklist.get("checkpoints", []))
        max_single_step = checklist.get("execution_discipline", {}).get("max_single_step_items", 10)
        if item_count > max_single_step:
            checklist["warning"] = (
                f"检查项数量为 {item_count}，超过单次执行阈值 {max_single_step}。"
                f"AI 必须先输出书面分步计划，用户确认后按步骤执行。"
                f"禁止自行减项或抽样。"
            )

        # 附加防减项系统 prompt
        checklist["system_prompt"] = (
            "你是一个严格的审计执行者。以下规则不可违背：\n"
            "1. 必须回应清单中的每一项，不得跳过、合并或用'等其他'概括。\n"
            "2. 输出开头必须包含覆盖声明：'应检查 N 项，已回应 N 项，遗漏 0 项'。\n"
            "3. 如果检查项超过 10 项，必须先输出分步计划，禁止单次减项执行。\n"
            "4. 每项结论必须引用产物原文片段作为证据。\n"
            "5. 如果上下文不足，必须停止并请求拆分，不得截断。"
        )

        output = json.dumps(checklist, ensure_ascii=False, indent=2)

        if args.output:
            Path(args.output).write_text(output, encoding='utf-8')
            print(f"模型检查清单已保存至：{args.output}")
        else:
            print(output)
        return

    # 审计模式
    if args.file:
        report = engine.audit(args.file, args.type, context)
        output = format_report(report, args.format)
    elif args.dir:
        reports = engine.audit_directory(args.dir, args.type, context)
        if args.format == "json":
            output = json.dumps(reports, ensure_ascii=False, indent=2)
        else:
            output = "\n\n".join(format_report(r, "text") for r in reports)
    else:
        parser.print_help()
        sys.exit(1)

    # 输出
    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"审计报告已保存至：{args.output}")
    else:
        print(output)

    # 如果有失败，返回非零退出码
    if args.file:
        sys.exit(0 if report["passed"] else 1)
    elif args.dir:
        all_passed = all(r["passed"] for r in reports)
        sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
