"""
Workflow Builder
从 workflow.yaml 构建 DAG
"""

import sys
from pathlib import Path
from typing import Optional, List, Union

import yaml

from .models import Node, OutputSpec
from .graph import DAG


class WorkflowBuilder:
    """从 YAML workflow 文件构建 DAG"""

    def build_from_yaml(self, workflow_path: str) -> DAG:
        """读取 workflow.yaml 文件，构建 DAG"""
        path = Path(workflow_path)
        if not path.exists():
            raise FileNotFoundError(f"工作流文件不存在: {workflow_path}")

        data = yaml.safe_load(path.read_text(encoding='utf-8'))
        if not data:
            raise ValueError(f"工作流文件为空或解析失败: {workflow_path}")

        dag = DAG()

        nodes_data = data.get('nodes', [])
        if not nodes_data:
            raise ValueError(f"工作流文件未定义任何节点: {workflow_path}")

        # 读取顶层默认值（output.format 等）
        workflow_meta = data.get('workflow', {})
        defaults = workflow_meta.get('defaults', {})

        for node_data in nodes_data:
            merged_node = self._merge_defaults(node_data, defaults)
            node = self._parse_node(merged_node)
            dag.add_node(node)

        dag.build_edges()
        dag.compute_waves()
        dag.detect_cycles()

        return dag

    @staticmethod
    def _merge_defaults(node_data: dict, defaults: dict) -> dict:
        """合并顶层默认值到节点配置（浅合并，节点级字段覆盖默认值）"""
        merged = dict(node_data)

        # 合并 defaults.output
        if 'output' in defaults:
            merged.setdefault('output', {})
            for key, value in defaults['output'].items():
                merged['output'].setdefault(key, value)

        return merged

    def _parse_node(self, data: dict) -> Node:
        """解析单个节点数据"""
        node_id = data.get('id')
        if not node_id:
            raise ValueError("节点必须包含 'id' 字段")

        # 解析 output
        output_data = data.get('output')
        if not output_data:
            raise ValueError(f"节点 '{node_id}' 必须包含 'output' 字段")
        if not isinstance(output_data, dict):
            raise ValueError(f"节点 '{node_id}' 的 'output' 必须是字典")

        output = OutputSpec(
            path=output_data.get('path', ''),
            type=output_data.get('type', ''),
            format=output_data.get('format', ''),
        )
        if not output.path:
            raise ValueError(f"节点 '{node_id}' 的 output.path 不能为空")

        # 解析 inputs（兼容字符串和列表）
        raw_inputs = data.get('inputs', data.get('input', []))
        inputs = self._normalize_inputs(raw_inputs, node_id)

        # metadata（支持 name 在节点顶层或 metadata 内）
        name = data.get('name', '')
        metadata = data.get('metadata', {})
        if not isinstance(metadata, dict):
            metadata = {}
        if name:
            metadata['name'] = name

        return Node(
            id=node_id,
            inputs=inputs,
            output=output,
            metadata=metadata,
        )

    @staticmethod
    def _normalize_inputs(raw: Union[str, List[str], None], node_id: str) -> List[str]:
        """
        规范化 inputs 字段
        兼容：字符串（单个 input）、列表（多个 inputs）、None/空（源节点）
        """
        if raw is None:
            return []
        if isinstance(raw, str):
            if raw.strip() == '':
                return []
            return [raw.strip()]
        if isinstance(raw, list):
            result = []
            for item in raw:
                if isinstance(item, str) and item.strip():
                    result.append(item.strip())
            return result
        raise ValueError(f"节点 '{node_id}' 的 inputs 必须是字符串或字符串列表")


