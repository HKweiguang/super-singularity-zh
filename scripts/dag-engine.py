#!/usr/bin/env python3
"""
DAG 引擎 CLI
产物依赖 DAG 分析与编排

用法:
    python dag-engine.py --visualize ./docs/                  # 可视化 DAG
    python dag-engine.py --detect-cycles ./docs/              # 检测循环依赖
    python dag-engine.py --impact ./docs/prd-v1.md --dir ./docs/  # 变更影响分析
    python dag-engine.py --critical-path ./docs/              # 关键路径分析
    python dag-engine.py --execution-plan ./docs/             # 执行波次计划
    python dag-engine.py --dir ./docs/ --format json          # JSON 输出
"""

import argparse
import json
import sys
from pathlib import Path

from dag.extractor import UpstreamExtractor
from dag.graph import ArtifactDAG
from dag.formatter import DAGFormatter

# 引入 audit-engine 用于拓扑审计（直接调用，避免 subprocess 开销）
import sys
_audit_engine_path = Path(__file__).parent / "audit-engine"
if str(_audit_engine_path) not in sys.path:
    sys.path.insert(0, str(_audit_engine_path))


def run_topology_audit(dag: ArtifactDAG, dir_path: str, format_type: str = "text") -> str:
    """
    拓扑审计：按 DAG 波次顺序调用 audit-engine 审计
    先审上游（波次 0），再审下游（波次 1, 2, ...）
    """
    from pathlib import Path
    from engine import AuditEngine as _AuditEngine

    audit_engine = _AuditEngine()

    lines = []
    lines.append("🔍 拓扑审计（按 DAG 波次顺序）\n")
    lines.append(f"共 {len(dag.waves)} 个波次，逐波次审计...\n")

    all_passed = True
    audit_results = []

    for wave_idx, wave in enumerate(dag.waves):
        lines.append(f"\n{'='*50}")
        lines.append(f"🔵 波次 {wave_idx}（{len(wave)} 个产物）")
        lines.append(f"{'='*50}")

        wave_passed = True
        for file_path in wave:
            node = dag.nodes[file_path]
            name = Path(file_path).name

            # audit-engine 支持的类型：prd/interaction/ui/tech/test/generic
            audit_type = node.doc_type
            if audit_type not in ("prd", "interaction", "ui", "tech", "test", "generic"):
                audit_type = "generic"

            try:
                report = audit_engine.audit(file_path, audit_type)
                passed = report.get("passed", False)

                if passed:
                    lines.append(f"\n  ✅ {name} — 审计通过")
                    audit_results.append({"file": file_path, "wave": wave_idx, "passed": True})
                else:
                    lines.append(f"\n  ❌ {name} — 审计未通过")
                    wave_passed = False
                    all_passed = False
                    audit_results.append({"file": file_path, "wave": wave_idx, "passed": False})

                    summary = report.get("summary", {})
                    failed = summary.get("failed", 0)
                    total = summary.get("total_checkpoints", 0)
                    passed_count = summary.get("passed", 0)
                    lines.append(f"     检查点：总计 {total} | 通过 {passed_count} | 失败 {failed}")
                    for result_item in report.get("results", []):
                        for cp in result_item.get("checkpoints", []):
                            if cp.get("status") == "fail":
                                note = cp.get("note", "")
                                note_str = f" ({note})" if note else ""
                                lines.append(f"       ❌ [{cp.get('id')}] {cp.get('item')}{note_str}")

            except Exception as e:
                lines.append(f"\n  ⚠️ {name} — 审计执行失败: {e}")
                wave_passed = False
                all_passed = False

        if not wave_passed:
            lines.append(f"\n⛔ 波次 {wave_idx} 审计未全部通过，暂停后续波次审计。")
            lines.append("   请先修复当前波次的问题，再重新运行拓扑审计。")
            break

    # 汇总
    lines.append(f"\n{'='*50}")
    lines.append("📊 拓扑审计汇总")
    lines.append(f"{'='*50}")

    if all_passed:
        lines.append(f"\n✅ 全部 {len(audit_results)} 个产物审计通过")
    else:
        passed_count = sum(1 for r in audit_results if r["passed"])
        lines.append(f"\n❌ 审计结果：通过 {passed_count} / 总计 {len(audit_results)}")

    if format_type == "json":
        return json.dumps({
            "passed": all_passed,
            "audit_results": audit_results,
            "report": "\n".join(lines)
        }, ensure_ascii=False, indent=2)

    return "\n".join(lines)


def build_dag(dir_path: str) -> ArtifactDAG:
    """构建 DAG"""
    extractor = UpstreamExtractor()
    metas = extractor.extract_directory(dir_path)

    dag = ArtifactDAG()
    for meta in metas:
        from dag.graph import ArtifactNode
        node = ArtifactNode(
            file_path=meta.file_path,
            name=meta.name,
            version=meta.version,
            doc_type=meta.doc_type,
            upstream_refs=meta.upstream_refs,
        )
        dag.add_node(node)

    dag.build_edges(dir_path)
    dag.compute_waves()
    dag.detect_cycles()

    return dag


def main():
    parser = argparse.ArgumentParser(description="Super-Singularity DAG 引擎")
    parser.add_argument("--dir", required=True, help="产物目录路径")
    parser.add_argument("--visualize", action="store_true", help="可视化 DAG（Mermaid）")
    parser.add_argument("--detect-cycles", action="store_true", help="检测循环依赖")
    parser.add_argument("--impact", help="变更影响分析（指定变更的文件路径）")
    parser.add_argument("--critical-path", action="store_true", help="关键路径分析")
    parser.add_argument("--execution-plan", action="store_true", help="执行波次计划")
    parser.add_argument("--audit-topology", action="store_true",
                        help="拓扑审计：按 DAG 波次顺序调用 audit-engine 审计")
    parser.add_argument("--format", default="text", choices=["text", "json", "mermaid"],
                        help="输出格式")
    parser.add_argument("--output", help="输出文件路径（默认 stdout）")

    args = parser.parse_args()

    # 构建 DAG
    dag = build_dag(args.dir)

    # 循环检测（优先级最高，有循环时其他分析可能不准确）
    if dag.cycle_info and dag.cycle_info.has_cycle:
        output = DAGFormatter.format_cycles(dag.cycle_info)
        if args.format == "json":
            import json
            output = json.dumps({
                "has_cycle": True,
                "cycle_path": dag.cycle_info.cycle_path
            }, ensure_ascii=False, indent=2)

        if args.output:
            Path(args.output).write_text(output, encoding='utf-8')
            print(f"报告已保存至：{args.output}")
        else:
            print(output)

        print("\n⚠️ 检测到循环依赖，请先解决后再执行其他分析。")
        sys.exit(1)

    # 拓扑审计：按波次顺序调用 audit-engine
    if args.audit_topology:
        output = run_topology_audit(dag, args.dir, args.format)

    elif args.visualize:
        if args.format == "mermaid":
            output = DAGFormatter.format_visualization(dag)
        elif args.format == "json":
            output = DAGFormatter.to_json(dag)
        else:
            output = DAGFormatter.format_visualization(dag)

    elif args.detect_cycles:
        output = DAGFormatter.format_cycles(dag.cycle_info)

    elif args.impact:
        report = dag.analyze_impact(args.impact)
        if args.format == "json":
            import json
            output = json.dumps({
                "changed_file": report.changed_file,
                "direct_impacts": report.direct_impacts,
                "indirect_impacts": report.indirect_impacts,
                "no_impacts": report.no_impacts,
            }, ensure_ascii=False, indent=2)
        else:
            output = DAGFormatter.format_impact(report, dag)

    elif args.critical_path:
        if args.format == "json":
            import json
            output = json.dumps({
                "critical_path": dag.compute_critical_path(),
                "bottleneck_nodes": dag.get_bottleneck_nodes(),
            }, ensure_ascii=False, indent=2)
        else:
            output = DAGFormatter.format_critical_path(dag)

    elif args.execution_plan:
        if args.format == "json":
            output = DAGFormatter.to_json(dag)
        else:
            output = DAGFormatter.format_execution_plan(dag)

    else:
        # 默认输出执行计划
        if args.format == "json":
            output = DAGFormatter.to_json(dag)
        else:
            output = DAGFormatter.format_execution_plan(dag)

    # 输出
    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"报告已保存至：{args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
