"""
DAG 核心数据模型
基于 input/output 转换器的节点原语
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class OutputSpec:
    """输出规范"""
    path: str       # 支持通配符，如 "src/**/*.ts", "artifacts/*.dwg"
    type: str       # 产物类型，决定模板文件名: .artifacts/steps/{type}-step.md
    format: str     # 格式（markdown, json, dwg, ts, ...）


@dataclass
class Node:
    """
    工作流节点 = 多个输入 → 单一输出

    约束：
    - 每个节点可以有多个 inputs（多个上游依赖），但只有一个 output
    - inputs 为空列表表示源节点（无上游依赖）
    - output.path 支持通配符，但不能和其他节点的 output.path 产生不可消解的歧义
    """
    id: str
    inputs: List[str]               # 多个输入（文件路径、通配符模式），空列表表示源节点
    output: OutputSpec              # 单一输出
    metadata: Dict[str, Any] = field(default_factory=dict)
    wave: int = -1                  # 所属执行波次（运行时由 DAG.compute_waves 填充）
