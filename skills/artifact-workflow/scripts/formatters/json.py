"""
JSON 格式化器
"""

import json
from dag_core.graph import DAG


class JSONFormatter:
    """导出 DAG 为 JSON"""

    @staticmethod
    def format_dag(dag: DAG) -> str:
        """导出完整 DAG 数据"""
        data = {
            "nodes": [
                {
                    "id": node.id,
                    "inputs": node.inputs,
                    "output": {
                        "path": node.output.path,
                        "format": node.output.format,
                    },
                    "metadata": node.metadata,
                    "wave": node.wave,
                }
                for node in dag.nodes.values()
            ],
            "edges": dag.edges,
            "waves": dag.waves,
            "root_nodes": dag.root_nodes,
            "critical_path": dag.compute_critical_path(),
            "has_cycle": dag.cycle_info.has_cycle if dag.cycle_info else False,
            "cycle_path": dag.cycle_info.cycle_path if dag.cycle_info else [],
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    @staticmethod
    def format_impact(report, dag: DAG) -> str:
        """导出影响分析为 JSON"""
        data = {
            "changed_node": report.changed_node,
            "direct_impacts": [
                {"node_id": nid, "wave": wave}
                for nid, wave in report.direct_impacts
            ],
            "indirect_impacts": [
                {"node_id": nid, "wave": wave}
                for nid, wave in report.indirect_impacts
            ],
            "no_impacts": report.no_impacts,
        }
        return json.dumps(data, ensure_ascii=False, indent=2)
