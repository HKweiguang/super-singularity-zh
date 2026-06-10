"""
DAG 数据结构与核心算法
基于 Node 模型的拓扑排序、循环检测、波次分层、关键路径、影响分析

约束：多 input / 单 output
- 每个节点可以有多个 inputs（多个上游依赖）
- 每个节点只能有一个 output（单一输出）
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
from collections import deque, defaultdict
import fnmatch

from .models import Node


@dataclass
class CycleInfo:
    """循环依赖信息"""
    has_cycle: bool = False
    cycle_path: List[str] = field(default_factory=list)


@dataclass
class ImpactReport:
    """变更影响报告"""
    changed_node: str
    direct_impacts: List[Tuple[str, int]] = field(default_factory=list)    # (node_id, wave)
    indirect_impacts: List[Tuple[str, int]] = field(default_factory=list)  # (node_id, wave)
    no_impacts: List[str] = field(default_factory=list)


class DAG:
    """
    有向无环图

    约束：每个节点可以有多个入边（多 inputs => 多上游），但只有一个出边（单 output）
    """

    def __init__(self):
        self.nodes: Dict[str, Node] = {}                    # node_id -> Node
        self.edges: Dict[str, List[str]] = defaultdict(list)  # node_id -> [upstream_node_ids]
        self.reverse_edges: Dict[str, List[str]] = defaultdict(list)  # node_id -> [downstream_node_ids]
        self.waves: List[List[str]] = []                    # 执行波次
        self.cycle_info: Optional[CycleInfo] = None
        self.root_nodes: List[str] = []                     # 源节点（无上游）

    def add_node(self, node: Node) -> None:
        """添加节点"""
        if node.id in self.nodes:
            raise ValueError(f"节点 ID 重复: {node.id}")
        self.nodes[node.id] = node

    def build_edges(self) -> None:
        """
        根据 inputs/outputs 通配符匹配构建边

        对每个节点的每个 input，检查是否匹配某个上游节点的 output.path
        如果匹配多个上游，选择最精确匹配
        """
        # 建立 output.path -> node_id 映射
        output_map: Dict[str, str] = {}
        for node in self.nodes.values():
            if node.output.path in output_map:
                raise ValueError(
                    f"输出路径冲突: 节点 '{node.id}' 和 '{output_map[node.output.path]}' "
                    f"都声明了 output.path='{node.output.path}'"
                )
            output_map[node.output.path] = node.id

        for node in self.nodes.values():
            if not node.inputs:
                # 无 inputs = 源节点
                self.root_nodes.append(node.id)
                continue

            matched_upstreams: Set[str] = set()
            for input_pattern in node.inputs:
                matched = self._find_best_match(input_pattern, output_map)
                if matched:
                    matched_upstreams.add(matched)

            if matched_upstreams:
                self.edges[node.id] = sorted(matched_upstreams)
                for upstream in matched_upstreams:
                    self.reverse_edges[upstream].append(node.id)
            else:
                # 所有 inputs 都无匹配 = 外部输入
                self.root_nodes.append(node.id)

    @staticmethod
    def _find_best_match(input_pattern: str, output_map: Dict[str, str]) -> Optional[str]:
        """
        用通配符匹配找最佳上游节点

        匹配规则：input_pattern 是否被某个 output_pattern 覆盖
        歧义消解：多个匹配时，选择最精确的 output_pattern
        """
        matches = []
        for output_pattern, upstream_id in output_map.items():
            if fnmatch.fnmatch(input_pattern, output_pattern):
                matches.append((output_pattern, upstream_id))

        if not matches:
            return None
        if len(matches) == 1:
            return matches[0][1]

        # 歧义消解：按特异性排序，选最具体的
        def specificity(pattern: str) -> tuple:
            """
            返回用于排序的元组，越小越具体
            (是否有通配符, 通配符总分, 非通配符负长度)
            """
            has_double_star = '**' in pattern
            wildcard_score = (
                pattern.count('*') - (2 if has_double_star else 0)
                + pattern.count('?')
                + (10 if has_double_star else 0)
            )
            clean_len = len(pattern.replace('*', '').replace('?', ''))
            return (wildcard_score > 0, wildcard_score, -clean_len)

        matches.sort(key=lambda x: specificity(x[0]))
        return matches[0][1]

    def topological_sort(self) -> List[str]:
        """拓扑排序（Kahn 算法）"""
        in_degree = {node_id: 0 for node_id in self.nodes}

        for node_id, upstreams in self.edges.items():
            in_degree[node_id] = len(upstreams)

        queue = deque([n for n, d in in_degree.items() if d == 0])
        result = []

        while queue:
            node_id = queue.popleft()
            result.append(node_id)

            for downstream in self.reverse_edges.get(node_id, []):
                in_degree[downstream] -= 1
                if in_degree[downstream] == 0:
                    queue.append(downstream)

        return result

    def compute_waves(self) -> List[List[str]]:
        """
        计算执行波次（分层）
        波次 0：无入边（源节点）
        波次 N：所有上游都在波次 <= N-1，且至少有一个上游在波次 N-1
        """
        if not self.nodes:
            return []

        depths = {node_id: 0 for node_id in self.nodes}
        topo = self.topological_sort()

        for node_id in topo:
            upstreams = self.edges.get(node_id, [])
            if upstreams:
                max_depth = max(depths.get(up, 0) for up in upstreams)
                depths[node_id] = max_depth + 1

        max_wave = max(depths.values()) if depths else 0
        waves = [[] for _ in range(max_wave + 1)]

        for node_id, depth in depths.items():
            waves[depth].append(node_id)
            self.nodes[node_id].wave = depth

        self.waves = waves
        return waves

    def detect_cycles(self) -> CycleInfo:
        """
        检测循环依赖（DFS + 三色标记）
        白色=未访问，灰色=访问中，黑色=已完成
        """
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {node_id: WHITE for node_id in self.nodes}

        def dfs(node_id: str, path: List[str]) -> Optional[List[str]]:
            color[node_id] = GRAY

            for upstream in self.edges.get(node_id, []):
                if upstream not in self.nodes:
                    continue
                if color[upstream] == GRAY:
                    # 发现循环
                    cycle_start = path.index(upstream)
                    return path[cycle_start:] + [upstream]

                if color[upstream] == WHITE:
                    result = dfs(upstream, path + [upstream])
                    if result:
                        return result

            color[node_id] = BLACK
            return None

        for node_id in self.nodes:
            if color[node_id] == WHITE:
                cycle = dfs(node_id, [node_id])
                if cycle:
                    self.cycle_info = CycleInfo(has_cycle=True, cycle_path=cycle)
                    return self.cycle_info

        self.cycle_info = CycleInfo(has_cycle=False)
        return self.cycle_info

    def compute_critical_path(self) -> List[str]:
        """
        计算关键路径（最长路径）
        假设每个节点耗时相等（权重=1）
        """
        if not self.nodes:
            return []

        topo = self.topological_sort()
        dist = {node_id: 0 for node_id in self.nodes}
        prev = {node_id: None for node_id in self.nodes}

        for node_id in topo:
            upstreams = self.edges.get(node_id, [])
            if upstreams:
                best_upstream = max(upstreams, key=lambda up: dist.get(up, 0))
                if dist[best_upstream] + 1 > dist[node_id]:
                    dist[node_id] = dist[best_upstream] + 1
                    prev[node_id] = best_upstream

        if not dist:
            return []

        end_node = max(dist, key=lambda k: dist[k])

        path = []
        node = end_node
        while node is not None:
            path.append(node)
            node = prev[node]

        return list(reversed(path))

    def analyze_impact(self, changed_node_id: str) -> ImpactReport:
        """
        变更影响分析
        从变更节点反向遍历下游子图
        """
        report = ImpactReport(changed_node=changed_node_id)

        if changed_node_id not in self.nodes:
            report.no_impacts = list(self.nodes.keys())
            return report

        # BFS 从变更节点反向遍历（找下游）
        visited = set()
        queue = deque([(changed_node_id, 0)])  # (node_id, distance)
        direct = set()
        indirect = set()

        while queue:
            node_id, distance = queue.popleft()
            if node_id in visited:
                continue
            visited.add(node_id)

            for downstream in self.reverse_edges.get(node_id, []):
                if downstream not in visited:
                    queue.append((downstream, distance + 1))
                    if distance == 0:
                        direct.add(downstream)
                    else:
                        indirect.add(downstream)

        for nid in direct:
            wave = self.nodes.get(nid).wave if nid in self.nodes else -1
            report.direct_impacts.append((nid, wave))

        for nid in indirect:
            wave = self.nodes.get(nid).wave if nid in self.nodes else -1
            report.indirect_impacts.append((nid, wave))

        all_affected = {changed_node_id} | direct | indirect
        report.no_impacts = [nid for nid in self.nodes if nid not in all_affected]

        return report

    def get_bottleneck_nodes(self) -> List[str]:
        """获取瓶颈节点（只有一个下游依赖的节点）"""
        bottlenecks = []
        for node_id in self.nodes:
            downstreams = self.reverse_edges.get(node_id, [])
            if len(downstreams) == 1:
                bottlenecks.append(node_id)
        return bottlenecks
