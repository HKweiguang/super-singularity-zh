"""
DAG 数据结构与核心算法
包括：拓扑排序、波次分层、关键路径、循环检测、变更影响分析
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
from collections import deque, defaultdict
from pathlib import Path


@dataclass
class ArtifactNode:
    """DAG 节点（产物）"""
    file_path: str
    name: str = ""
    version: str = ""
    doc_type: str = "generic"
    upstream_refs: List[str] = field(default_factory=list)
    wave: int = -1  # 所属执行波次


@dataclass
class CycleInfo:
    """循环依赖信息"""
    has_cycle: bool = False
    cycle_path: List[str] = field(default_factory=list)


@dataclass
class ImpactReport:
    """变更影响报告"""
    changed_file: str
    direct_impacts: List[Tuple[str, int]] = field(default_factory=list)   # (file, wave)
    indirect_impacts: List[Tuple[str, int]] = field(default_factory=list) # (file, wave)
    no_impacts: List[str] = field(default_factory=list)


class ArtifactDAG:
    """产物依赖 DAG"""

    def __init__(self):
        self.nodes: Dict[str, ArtifactNode] = {}  # file_path -> Node
        self.edges: Dict[str, List[str]] = defaultdict(list)  # node -> upstream_nodes
        self.reverse_edges: Dict[str, List[str]] = defaultdict(list)  # node -> downstream_nodes
        self.waves: List[List[str]] = []  # 执行波次
        self.cycle_info: Optional[CycleInfo] = None

    def add_node(self, node: ArtifactNode) -> None:
        """添加节点"""
        self.nodes[node.file_path] = node

    def build_edges(self, base_dir: str = ".") -> None:
        """
        根据上游引用构建边
        将上游引用路径匹配到已扫描的节点
        """
        base = Path(base_dir).resolve()

        # 建立文件名到路径的映射（用于模糊匹配）
        file_map: Dict[str, str] = {}
        for path in self.nodes:
            p = Path(path)
            file_map[p.name] = path
            file_map[p.stem] = path

        for node in self.nodes.values():
            for ref in node.upstream_refs:
                # 尝试精确匹配
                matched = False

                # 1. 直接匹配文件路径
                ref_path = Path(ref)
                if not ref_path.is_absolute():
                    ref_path = base / ref_path

                resolved = str(ref_path.resolve())
                if resolved in self.nodes:
                    self._add_edge(node.file_path, resolved)
                    matched = True
                    continue

                # 2. 匹配文件名
                if ref in file_map:
                    self._add_edge(node.file_path, file_map[ref])
                    matched = True
                    continue

                # 3. 尝试模糊匹配（去掉扩展名）
                ref_stem = Path(ref).stem
                if ref_stem in file_map:
                    self._add_edge(node.file_path, file_map[ref_stem])
                    matched = True
                    continue

                if not matched and ref:
                    # 记录未匹配的上游引用
                    pass

    def _add_edge(self, from_node: str, to_node: str) -> None:
        """添加有向边：from_node 依赖于 to_node"""
        if to_node not in self.edges[from_node]:
            self.edges[from_node].append(to_node)
            self.reverse_edges[to_node].append(from_node)

    def topological_sort(self) -> List[str]:
        """拓扑排序（Kahn 算法）"""
        in_degree = {node: 0 for node in self.nodes}

        for node, upstreams in self.edges.items():
            for up in upstreams:
                if up in in_degree:
                    in_degree[node] += 1

        queue = deque([n for n, d in in_degree.items() if d == 0])
        result = []

        while queue:
            node = queue.popleft()
            result.append(node)

            # 找到所有依赖当前节点的下游节点
            for downstream in self.reverse_edges[node]:
                if downstream in in_degree:
                    in_degree[downstream] -= 1
                    if in_degree[downstream] == 0:
                        queue.append(downstream)

        return result

    def compute_waves(self) -> List[List[str]]:
        """
        计算执行波次（分层）
        波次 0：无入边（无上游依赖）
        波次 N：所有上游都在波次 < N 中
        """
        if not self.nodes:
            return []

        # 计算每个节点的最大上游深度
        depths = {node: 0 for node in self.nodes}
        topo = self.topological_sort()

        for node in topo:
            upstreams = self.edges.get(node, [])
            if upstreams:
                max_depth = 0
                for up in upstreams:
                    if up in depths:
                        max_depth = max(max_depth, depths[up] + 1)
                depths[node] = max_depth

        # 按深度分组
        max_wave = max(depths.values()) if depths else 0
        waves = [[] for _ in range(max_wave + 1)]

        for node, depth in depths.items():
            waves[depth].append(node)
            self.nodes[node].wave = depth

        self.waves = waves
        return waves

    def detect_cycles(self) -> CycleInfo:
        """
        检测循环依赖（DFS + 三色标记）
        白色=未访问，灰色=访问中，黑色=已完成
        """
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {node: WHITE for node in self.nodes}
        parent = {}

        def dfs(node: str, path: List[str]) -> Optional[List[str]]:
            color[node] = GRAY

            for upstream in self.edges.get(node, []):
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

            color[node] = BLACK
            return None

        for node in self.nodes:
            if color[node] == WHITE:
                cycle = dfs(node, [node])
                if cycle:
                    self.cycle_info = CycleInfo(has_cycle=True, cycle_path=cycle)
                    return self.cycle_info

        self.cycle_info = CycleInfo(has_cycle=False)
        return self.cycle_info

    def compute_critical_path(self) -> List[str]:
        """
        计算关键路径（最长路径）
        假设每个节点的耗时相等（权重=1），最长路径决定最短完成时间
        """
        if not self.nodes:
            return []

        topo = self.topological_sort()

        # 到每个节点的最长距离
        dist = {node: 0 for node in self.nodes}
        prev = {node: None for node in self.nodes}

        for node in topo:
            upstreams = self.edges.get(node, [])
            if upstreams:
                max_dist = -1
                best_prev = None
                for up in upstreams:
                    if up in dist and dist[up] + 1 > max_dist:
                        max_dist = dist[up] + 1
                        best_prev = up
                if max_dist >= 0:
                    dist[node] = max_dist
                    prev[node] = best_prev

        # 找到最长路径的终点
        if not dist:
            return []

        end_node = max(dist, key=lambda k: dist[k])

        # 回溯路径
        path = []
        node = end_node
        while node is not None:
            path.append(node)
            node = prev[node]

        return list(reversed(path))

    def analyze_impact(self, changed_file: str) -> ImpactReport:
        """
        精确变更传播分析
        反向遍历受影响子图
        """
        report = ImpactReport(changed_file=changed_file)

        if changed_file not in self.nodes:
            report.no_impacts = list(self.nodes.keys())
            return report

        # BFS 从变更节点反向遍历（找下游）
        visited = set()
        queue = deque([(changed_file, 0)])  # (node, distance)
        direct = set()
        indirect = set()

        while queue:
            node, distance = queue.popleft()
            if node in visited:
                continue
            visited.add(node)

            for downstream in self.reverse_edges.get(node, []):
                if downstream not in visited:
                    queue.append((downstream, distance + 1))
                    if distance == 0:
                        direct.add(downstream)
                    else:
                        indirect.add(downstream)

        # 分类
        for f in direct:
            wave = self.nodes.get(f, ArtifactNode(f)).wave
            report.direct_impacts.append((f, wave))

        for f in indirect:
            wave = self.nodes.get(f, ArtifactNode(f)).wave
            report.indirect_impacts.append((f, wave))

        # 无影响的节点
        all_affected = {changed_file} | direct | indirect
        report.no_impacts = [f for f in self.nodes if f not in all_affected]

        return report

    def get_bottleneck_nodes(self) -> List[str]:
        """获取瓶颈节点（入边=1 且无法并行优化的节点）"""
        bottlenecks = []
        for node in self.nodes:
            upstreams = self.edges.get(node, [])
            if len(upstreams) == 1:
                bottlenecks.append(node)
        return bottlenecks
