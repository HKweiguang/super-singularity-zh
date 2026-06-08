"""
上游引用提取器
从 Markdown 产物文件中提取「上游文档」表格中的引用关系
"""

import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class ArtifactMeta:
    """产物元数据"""
    file_path: str
    name: str = ""
    version: str = ""
    doc_type: str = "generic"
    upstream_refs: List[str] = field(default_factory=list)


class UpstreamExtractor:
    """提取产物文件中的上游文档引用"""

    def _load_type_patterns(self) -> Dict[str, str]:
        """从 artifact_types.yaml 动态加载类型推断模式"""
        import sys
        from pathlib import Path

        config_dir = Path(__file__).parent.parent / "audit-engine" / "config"
        if str(config_dir) not in sys.path:
            sys.path.insert(0, str(config_dir))

        try:
            from config import load_artifact_types
            config = load_artifact_types()
            patterns = {}
            for doc_type, type_config in config.get("types", {}).items():
                for pattern in type_config.get("filename_patterns", []):
                    patterns[pattern] = doc_type
            return patterns
        except Exception:
            # 回退到最小默认配置
            return {
                r"prd|需求文档|产品需求": "prd",
                r"interaction|交互设计|交互": "interaction",
                r"ui|设计稿|视觉": "ui",
                r"tech|技术方案|架构": "tech",
                r"test|测试计划|测试": "test",
            }

    def extract(self, file_path: str) -> ArtifactMeta:
        """从单个文件提取元数据和上游引用"""
        path = Path(file_path)
        content = path.read_text(encoding='utf-8')
        lines = content.split('\n')

        meta = ArtifactMeta(file_path=file_path)
        meta.name = self._extract_name(lines)
        meta.version = self._extract_version(lines)
        meta.doc_type = self._infer_type(path.name)
        meta.upstream_refs = self._extract_upstream_refs(lines, path.parent)

        return meta

    def extract_directory(self, dir_path: str) -> List[ArtifactMeta]:
        """扫描目录下的所有产物文件"""
        metas = []
        path = Path(dir_path)

        for md_file in path.glob("**/*.md"):
            # 排除草稿、实验和废弃文件
            if any(marker in md_file.name for marker in ["-draft", "-exp-", "[已废弃]"]):
                continue
            try:
                meta = self.extract(str(md_file))
                metas.append(meta)
            except Exception as e:
                print(f"警告：无法提取 {md_file}: {e}")

        return metas

    def _extract_name(self, lines: List[str]) -> str:
        """从第一级标题提取产物名称"""
        for line in lines[:30]:
            m = re.match(r'^#\s+(.+)$', line.strip())
            if m:
                return m.group(1).strip()
        return ""

    def _extract_version(self, lines: List[str]) -> str:
        """提取版本号"""
        for line in lines[:30]:
            m = re.search(r'\*\*版本号\*\*\s*[:：]\s*v?([\d.]+)', line)
            if m:
                return m.group(1)
        return ""

    def _infer_type(self, filename: str) -> str:
        """从文件名推断产物类型"""
        lower = filename.lower()
        type_patterns = self._load_type_patterns()
        for pattern, doc_type in type_patterns.items():
            if re.search(pattern, lower):
                return doc_type
        return "generic"

    def _extract_upstream_refs(self, lines: List[str], base_dir: Path) -> List[str]:
        """
        提取「上游文档」表格中的引用路径
        返回相对于扫描根目录的路径列表
        """
        upstream_refs = []
        in_upstream_table = False
        table_started = False

        for i, line in enumerate(lines):
            # 检测「上游文档」标题或表格
            if '上游文档' in line and not table_started:
                in_upstream_table = True
                continue

            if in_upstream_table:
                # 表格分隔行 |---|---|
                if re.match(r'\|[-\s|]+\|', line.strip()):
                    table_started = True
                    continue

                # 表格数据行
                if table_started and line.strip().startswith('|'):
                    cells = [c.strip() for c in line.split('|')[1:-1]]
                    if len(cells) >= 1:
                        doc_ref = cells[0]
                        # 忽略表头和空行
                        if doc_ref and doc_ref not in ['文档', '---']:
                            # 提取路径（去除 Markdown 链接格式 [name](path)）
                            path_match = re.search(r'\[(.+?)\]\((.+?)\)', doc_ref)
                            if path_match:
                                upstream_refs.append(path_match.group(2))
                            else:
                                upstream_refs.append(doc_ref)

                # 表格结束（空行或非表格行）
                elif table_started and line.strip() and not line.strip().startswith('|'):
                    break

                # 如果没找到表格格式，尝试简单列表格式
                if not table_started and re.match(r'[-*]\s+(.+)', line.strip()):
                    m = re.match(r'[-*]\s+(.+)', line.strip())
                    if m:
                        ref = m.group(1).strip()
                        # 排除表头说明文字
                        if ref and '文档' not in ref:
                            upstream_refs.append(ref)

        # 规范化路径：转为绝对路径以便匹配
        normalized = []
        for ref in upstream_refs:
            # 去除 Markdown 格式残留
            ref = re.sub(r'[\*\[\]\(\)]', '', ref)
            if ref:
                normalized.append(ref)

        return normalized
