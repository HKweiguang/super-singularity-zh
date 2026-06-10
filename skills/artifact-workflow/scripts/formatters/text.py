"""
文本格式化器
"""

from typing import List
from dag_core.graph import DAG, ImpactReport


class TextFormatter:
    """格式化 DAG 分析结果为文本"""

    @staticmethod
    def format_execution_plan(dag: DAG) -> str:
        """格式化执行波次计划"""
        lines = []
        lines.append("📊 工作流 DAG 分析完成\n")
        lines.append(f"节点总数：{len(dag.nodes)}")
        lines.append(f"执行波次（共 {len(dag.waves)} 波）：\n")

        for i, wave in enumerate(dag.waves):
            lines.append(f"\n🔵 波次 {i}（可并行）：")
            for node_id in wave:
                node = dag.nodes[node_id]
                upstream_ids = dag.edges.get(node_id, [])

                if upstream_ids:
                    upstream_descs = []
                    for uid in upstream_ids:
                        up_node = dag.nodes[uid]
                        upstream_descs.append(f"{uid} ({up_node.output.path})")
                    upstream_info = f" ← 依赖：{', '.join(upstream_descs)}"
                else:
                    upstream_info = " ← 源节点（无依赖）"

                name = node.metadata.get('name', node_id)
                lines.append(
                    f"   ├─ {name}"
                    f"\n   │    输出: {node.output.path}"
                    f"\n   │    格式: {node.output.format}"
                    f"{upstream_info}"
                )

        # 关键路径
        critical = dag.compute_critical_path()
        if critical:
            lines.append(f"\n⏱️ 关键路径：{' → '.join(critical)}")

        # 并行优化建议
        for i, wave in enumerate(dag.waves):
            if len(wave) > 1:
                lines.append(f"\n⚡ 波次 {i} 的 {', '.join(wave)} 可同时执行")

        # 瓶颈节点
        bottlenecks = dag.get_bottleneck_nodes()
        if bottlenecks:
            lines.append(f"\n🔒 瓶颈节点（单一下游依赖）：")
            for b in bottlenecks:
                down = dag.reverse_edges.get(b, [])
                lines.append(f"   • {b} → {down[0] if down else '无'}")

        return "\n".join(lines)

    @staticmethod
    def format_cycles(dag: DAG) -> str:
        """格式化循环依赖报告"""
        if not dag.cycle_info or not dag.cycle_info.has_cycle:
            return "✅ 未检测到循环依赖"

        lines = []
        lines.append("❌ 检测到循环依赖！\n")

        path = dag.cycle_info.cycle_path
        for i in range(len(path) - 1):
            node_a = dag.nodes[path[i]]
            node_b = dag.nodes[path[i + 1]]
            lines.append(f"节点 {path[i]} (输出: {node_a.output.path}) → 节点 {path[i+1]} (输入: {', '.join(node_b.inputs)})")

        lines.append("\n建议：")
        lines.append("  1. 检查 workflow.yaml 中节点的 inputs/output 定义，确认是否存在循环引用")
        lines.append("  2. 将循环中的某个节点拆分为多个节点，或引入中间节点打破循环")

        return "\n".join(lines)

    @staticmethod
    def format_impact(report: ImpactReport, dag: DAG) -> str:
        """格式化变更影响报告"""
        lines = []
        lines.append("📢 变更影响分析\n")
        changed = dag.nodes.get(report.changed_node)
        changed_output = changed.output.path if changed else "未知"
        lines.append(f"修改节点：{report.changed_node} (输出: {changed_output})\n")

        if report.direct_impacts:
            lines.append("直接影响（必须同步）：")
            for node_id, wave in sorted(report.direct_impacts, key=lambda x: x[1]):
                name = dag.nodes[node_id].metadata.get('name', node_id)
                lines.append(f"  ├─ {name} — 波次 {wave}")
            lines.append("")

        if report.indirect_impacts:
            lines.append("间接影响（级联更新）：")
            for node_id, wave in sorted(report.indirect_impacts, key=lambda x: x[1]):
                name = dag.nodes[node_id].metadata.get('name', node_id)
                lines.append(f"  └─ {name} — 波次 {wave}")
            lines.append("")

        if report.no_impacts:
            lines.append("无影响（无需操作）：")
            for node_id in report.no_impacts:
                name = dag.nodes[node_id].metadata.get('name', node_id)
                lines.append(f"  ├─ {name}")

        return "\n".join(lines)

    @staticmethod
    def format_critical_path(dag: DAG) -> str:
        """格式化关键路径分析"""
        lines = []
        critical = dag.compute_critical_path()

        if not critical:
            return "暂无关键路径"

        lines.append("⏱️ 关键路径分析\n")
        lines.append(f"关键路径（共 {len(critical)} 个节点，决定最短完成时间）：")

        for i, node_id in enumerate(critical):
            node = dag.nodes[node_id]
            name = node.metadata.get('name', node_id)
            prefix = "  " if i == 0 else "  → "
            lines.append(f"{prefix}{name} ({node.output.path})")

        # 瓶颈
        bottlenecks = dag.get_bottleneck_nodes()
        if bottlenecks:
            lines.append(f"\n瓶颈节点：")
            for b in bottlenecks:
                lines.append(f"  • {b}（单一输出被单一依赖，无法并行优化）")

        return "\n".join(lines)
