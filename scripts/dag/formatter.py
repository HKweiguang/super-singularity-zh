"""
DAG 输出格式化器
支持文本、JSON、Mermaid 图格式
"""

import json
from typing import List, Dict
from pathlib import Path

from .graph import ArtifactDAG, ArtifactNode, CycleInfo, ImpactReport


class DAGFormatter:
    """格式化 DAG 分析结果"""

    @staticmethod
    def format_execution_plan(dag: ArtifactDAG) -> str:
        """格式化执行波次计划（文本）"""
        lines = []
        lines.append("📊 产物依赖 DAG 分析完成\n")
        lines.append(f"执行波次（共 {len(dag.waves)} 波）：\n")

        for i, wave in enumerate(dag.waves):
            lines.append(f"\n🔵 波次 {i}（可并行）：")
            for file_path in wave:
                node = dag.nodes[file_path]
                upstreams = dag.edges.get(file_path, [])
                if upstreams:
                    up_names = [Path(u).name for u in upstreams]
                    lines.append(f"   ├─ {node.name} ({Path(file_path).name}) ← 依赖：{', '.join(up_names)}")
                else:
                    lines.append(f"   ├─ {node.name} ({Path(file_path).name})")

        # 关键路径
        critical = dag.compute_critical_path()
        if critical:
            path_names = [Path(p).name for p in critical]
            lines.append(f"\n⏱️ 关键路径：{' → '.join(path_names)}")

        # 并行优化建议
        for i, wave in enumerate(dag.waves):
            if len(wave) > 1:
                names = [Path(f).name for f in wave]
                lines.append(f"⚡ 并行优化：波次 {i} 的 {', '.join(names)} 可同时生成")

        return "\n".join(lines)

    @staticmethod
    def format_visualization(dag: ArtifactDAG) -> str:
        """格式化 DAG 可视化（Mermaid）"""
        lines = []
        lines.append("```mermaid")
        lines.append("graph TD")

        # 定义节点
        for file_path, node in dag.nodes.items():
            name = Path(file_path).stem
            label = f"{node.name or name}"
            lines.append(f"    {name}[\"{label}\"]")

        # 定义边
        for node, upstreams in dag.edges.items():
            node_name = Path(node).stem
            for up in upstreams:
                if up in dag.nodes:
                    up_name = Path(up).stem
                    lines.append(f"    {up_name} --> {node_name}")

        lines.append("```")
        return "\n".join(lines)

    @staticmethod
    def format_cycles(cycle_info: CycleInfo) -> str:
        """格式化循环依赖报告"""
        if not cycle_info.has_cycle:
            return "✅ 未检测到循环依赖"

        lines = []
        lines.append("❌ 检测到循环依赖！\n")

        path = cycle_info.cycle_path
        for i in range(len(path) - 1):
            lines.append(f"产物 {Path(path[i]).name} 引用 → 产物 {Path(path[i+1]).name}")

        lines.append("\n建议：")
        lines.append("  1. 检查产物尾部引用的「上游文档」表格，确认是否误引了上游产物")
        lines.append("  2. 如果是合理的双向引用，建议拆分为「基线版」和「对齐版」")

        return "\n".join(lines)

    @staticmethod
    def format_impact(report: ImpactReport, dag: ArtifactDAG) -> str:
        """格式化变更影响报告"""
        lines = []
        lines.append("📢 变更影响分析\n")
        lines.append(f"修改：{Path(report.changed_file).name}\n")

        if report.direct_impacts:
            lines.append("直接影响（必须同步）：")
            for file_path, wave in sorted(report.direct_impacts, key=lambda x: x[1]):
                lines.append(f"  ├─ {Path(file_path).name} — 波次 {wave}")
            lines.append("")

        if report.indirect_impacts:
            lines.append("间接影响（级联更新）：")
            for file_path, wave in sorted(report.indirect_impacts, key=lambda x: x[1]):
                lines.append(f"  └─ {Path(file_path).name} — 波次 {wave}")
            lines.append("")

        if report.no_impacts:
            lines.append("无影响（无需操作）：")
            for file_path in report.no_impacts:
                lines.append(f"  ├─ {Path(file_path).name}")

        return "\n".join(lines)

    @staticmethod
    def format_critical_path(dag: ArtifactDAG) -> str:
        """格式化关键路径分析"""
        lines = []
        critical = dag.compute_critical_path()

        if not critical:
            return "暂无关键路径"

        path_names = [Path(p).name for p in critical]
        lines.append("⏱️ 关键路径分析\n")
        lines.append(f"关键路径（共 {len(critical)} 个节点，决定最短完成时间）：")
        lines.append(f"  {' → '.join(path_names)}")

        # 瓶颈节点
        bottlenecks = dag.get_bottleneck_nodes()
        if bottlenecks:
            lines.append(f"\n瓶颈节点：")
            for b in bottlenecks:
                lines.append(f"  • {Path(b).name}（只有 1 个上游入边，无法并行优化）")

        # 并行优化建议
        for i, wave in enumerate(dag.waves):
            if len(wave) > 1:
                names = [Path(f).name for f in wave]
                lines.append(f"\n✅ 波次 {i} 的 {', '.join(names)} 可同时生成")

        return "\n".join(lines)

    @staticmethod
    def to_json(dag: ArtifactDAG) -> str:
        """导出为 JSON"""
        data = {
            "nodes": [
                {
                    "file_path": n.file_path,
                    "name": n.name,
                    "version": n.version,
                    "doc_type": n.doc_type,
                    "wave": n.wave,
                    "upstream_refs": n.upstream_refs,
                }
                for n in dag.nodes.values()
            ],
            "edges": {
                k: v for k, v in dag.edges.items()
            },
            "waves": dag.waves,
            "critical_path": dag.compute_critical_path(),
            "has_cycle": dag.cycle_info.has_cycle if dag.cycle_info else False,
        }
        return json.dumps(data, ensure_ascii=False, indent=2)
