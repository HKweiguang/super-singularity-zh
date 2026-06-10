"""
Mermaid 图格式化器
"""

from dag_core.graph import DAG


class MermaidFormatter:
    """格式化 DAG 为 Mermaid 流程图"""

    @staticmethod
    def format_dag(dag: DAG) -> str:
        """生成 Mermaid graph TD 图"""
        lines = []
        lines.append("```mermaid")
        lines.append("graph TD")

        # 定义节点，按波次分组着色
        colors = ["fill:#e1f5fe", "fill:#fff3e0", "fill:#e8f5e9", "fill:#fce4ec", "fill:#f3e5f5"]

        for node_id, node in dag.nodes.items():
            label = node_id
            if node.metadata.get('name'):
                label = f"{node.metadata['name']}"

            style = ""
            if node.wave >= 0:
                color = colors[node.wave % len(colors)]
                style = f":::wave{node.wave}"
                lines.append(f"    style {node_id} {color}")

            lines.append(f'    {node_id}["{label}<br/><small>{node.output.path}</small>"]{style}')

        # 定义边
        for node_id, upstream_ids in dag.edges.items():
            for upstream_id in upstream_ids:
                lines.append(f"    {upstream_id} --> {node_id}")

        lines.append("```")
        return "\n".join(lines)

    @staticmethod
    def format_execution_plan(dag: DAG) -> str:
        """生成带波次标注的 Mermaid 图"""
        return MermaidFormatter.format_dag(dag)
