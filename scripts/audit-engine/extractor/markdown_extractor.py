"""
Markdown 产物提取器
负责从 Markdown 文件中提取结构化信息：章节、表格、编号、代码块、元数据
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Section:
    """文档章节"""
    level: int           # 标题级别：1=#, 2=##, ...
    title: str           # 标题文本
    line_number: int     # 行号（1-based）


@dataclass
class Table:
    """Markdown 表格"""
    headers: List[str]           # 表头
    rows: List[List[str]]        # 数据行
    line_number: int             # 起始行号
    raw_lines: List[str]         # 原始行内容


@dataclass
class CodeBlock:
    """代码块"""
    language: Optional[str]      # 语言标识
    content: str                 # 代码内容
    line_number: int             # 起始行号


@dataclass
class ExtractedDocument:
    """提取后的文档结构"""
    sections: List[Section] = field(default_factory=list)
    tables: List[Table] = field(default_factory=list)
    ids: List[Dict] = field(default_factory=list)        # [{id, line_number, context}]
    code_blocks: List[CodeBlock] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)
    raw_content: str = ""
    lines: List[str] = field(default_factory=list)


class MarkdownExtractor:
    """Markdown 文档提取器"""

    # 编号模式：REQ-001, UI-xxx, API-xxx 等
    ID_PATTERN = re.compile(r'\b([A-Z]{2,8}-\d{1,4})\b')

    def extract(self, content: str) -> ExtractedDocument:
        """提取文档结构"""
        doc = ExtractedDocument(raw_content=content)
        doc.lines = content.split('\n')

        self._extract_metadata(doc)
        self._extract_sections(doc)
        self._extract_tables(doc)
        self._extract_code_blocks(doc)
        self._extract_ids(doc)

        return doc

    def _extract_metadata(self, doc: ExtractedDocument) -> None:
        """提取产物头部元数据"""
        lines = doc.lines
        in_frontmatter = False
        frontmatter_lines = []

        # YAML frontmatter (--- ... ---)
        if lines and lines[0].strip() == '---':
            in_frontmatter = True
            for i, line in enumerate(lines[1:], start=2):
                if line.strip() == '---':
                    in_frontmatter = False
                    break
                frontmatter_lines.append(line)

        # 提取 frontmatter 中的键值对
        for line in frontmatter_lines:
            if ':' in line:
                key, value = line.split(':', 1)
                doc.metadata[key.strip()] = value.strip()

        # 提取产物头部标准字段（版本号、上游文档等）
        for i, line in enumerate(lines):
            if i > 50:  # 只扫描前50行
                break

            # 版本号: v1.0
            m = re.search(r'\*\*版本号\*\*\s*[:：]\s*v?([\d.]+)', line)
            if m:
                doc.metadata['version'] = m.group(1)

            # 制定日期
            m = re.search(r'\*\*制定日期\*\*\s*[:：]\s*(\d{4}-\d{2}-\d{2})', line)
            if m:
                doc.metadata['date'] = m.group(1)

            # 作者
            m = re.search(r'\*\*作者\*\*\s*[:：]\s*(.+)', line)
            if m:
                doc.metadata['author'] = m.group(1).strip()

            # 上游文档表格开始标记
            if '上游文档' in line:
                doc.metadata['has_upstream_table'] = 'true'

    def _extract_sections(self, doc: ExtractedDocument) -> None:
        """提取章节标题"""
        for i, line in enumerate(doc.lines, start=1):
            m = re.match(r'^(#{1,6})\s+(.+)$', line)
            if m:
                level = len(m.group(1))
                title = m.group(2).strip()
                doc.sections.append(Section(level=level, title=title, line_number=i))

    def _extract_tables(self, doc: ExtractedDocument) -> None:
        """提取 Markdown 表格"""
        lines = doc.lines
        i = 0
        while i < len(lines):
            line = lines[i]
            # 表格行以 | 开头且包含至少一个 |
            if line.strip().startswith('|') and '|' in line[1:]:
                table_lines = []
                start_line = i + 1
                # 收集连续的表格行
                while i < len(lines) and lines[i].strip().startswith('|'):
                    table_lines.append(lines[i])
                    i += 1

                if len(table_lines) >= 2:
                    # 第一行是表头
                    headers = [cell.strip() for cell in table_lines[0].split('|')[1:-1]]
                    # 第二行是分隔符 (---|---|---)
                    # 从第三行开始是数据
                    rows = []
                    for row_line in table_lines[2:]:
                        cells = [cell.strip() for cell in row_line.split('|')[1:-1]]
                        if cells:
                            rows.append(cells)

                    doc.tables.append(Table(
                        headers=headers,
                        rows=rows,
                        line_number=start_line,
                        raw_lines=table_lines
                    ))
                continue
            i += 1

    def _extract_code_blocks(self, doc: ExtractedDocument) -> None:
        """提取代码块"""
        lines = doc.lines
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.strip().startswith('```'):
                language = line.strip()[3:].strip() or None
                start_line = i + 1
                code_lines = []
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('```'):
                    code_lines.append(lines[i])
                    i += 1
                doc.code_blocks.append(CodeBlock(
                    language=language,
                    content='\n'.join(code_lines),
                    line_number=start_line
                ))
                i += 1  # 跳过结束 ```
                continue
            i += 1

    def _extract_ids(self, doc: ExtractedDocument) -> None:
        """提取编号引用"""
        for i, line in enumerate(doc.lines, start=1):
            for match in self.ID_PATTERN.finditer(line):
                doc.ids.append({
                    'id': match.group(1),
                    'line_number': i,
                    'context': line.strip()
                })

    def get_section_by_title(self, doc: ExtractedDocument, title_pattern: str) -> Optional[Section]:
        """按标题模式查找章节"""
        pattern = re.compile(title_pattern, re.IGNORECASE)
        for section in doc.sections:
            if pattern.search(section.title):
                return section
        return None

    def get_section_content(self, doc: ExtractedDocument, section: Section) -> str:
        """获取某个章节的内容（到下一个同级或更高级标题为止）"""
        lines = doc.lines
        start = section.line_number
        end = len(lines)

        for s in doc.sections:
            if s.line_number > start and s.level <= section.level:
                end = s.line_number - 1
                break

        return '\n'.join(lines[start:end])

    # ═══════════════════════════════════════════════════════════════════════════════
    # 章节级精确提取方法（精细提取层）
    # ═══════════════════════════════════════════════════════════════════════════════

    def section_text(self, doc: ExtractedDocument, header_pattern: str) -> str:
        """提取匹配 header_pattern 的 heading 及其后的全部文本（直到同级或更高级 heading）"""
        lines = doc.lines
        start_line = -1
        level = 6
        pattern = re.compile(header_pattern, re.IGNORECASE)

        for i, line in enumerate(lines):
            m = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            if m and pattern.search(m.group(2).strip()):
                start_line = i
                level = len(m.group(1))
                break

        if start_line == -1:
            return ""

        parts = []
        for line in lines[start_line + 1:]:
            m = re.match(r'^(#{1,6})\s+', line.strip())
            if m and len(m.group(1)) <= level:
                break
            parts.append(line)

        return '\n'.join(parts).strip()

    def table_after_heading(self, doc: ExtractedDocument, header_pattern: str) -> Optional[Table]:
        """在匹配 header_pattern 的 heading 后找到第一个 table"""
        tables = self.all_tables_after_heading(doc, header_pattern)
        return tables[0] if tables else None

    def all_tables_after_heading(self, doc: ExtractedDocument, header_pattern: str) -> List[Table]:
        """在匹配 header_pattern 的 heading 后找到所有 table，直到同级或更高级 heading"""
        start_line = -1
        level = 6
        pattern = re.compile(header_pattern, re.IGNORECASE)

        for i, line in enumerate(doc.lines):
            m = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
            if m and pattern.search(m.group(2).strip()):
                start_line = i
                level = len(m.group(1))
                break

        if start_line == -1:
            return []

        # 找到结束边界
        end_line = len(doc.lines)
        for section in doc.sections:
            if section.line_number > start_line + 1 and section.level <= level:
                end_line = section.line_number - 1
                break

        tables = []
        for table in doc.tables:
            if start_line < table.line_number <= end_line:
                tables.append(table)

        return tables

    def ids_in_section(self, doc: ExtractedDocument, header_pattern: str,
                       id_pattern: Optional[str] = None) -> List[Dict]:
        """从指定章节中提取编号"""
        text = self.section_text(doc, header_pattern)
        if not text:
            return []

        if id_pattern:
            pat = re.compile(id_pattern)
            results = []
            for i, line in enumerate(text.split('\n'), start=1):
                for match in pat.finditer(line):
                    results.append({
                        'id': match.group(0),
                        'line_number': i,
                        'context': line.strip()
                    })
            return results

        # 默认模式：使用文档级编号模式
        results = []
        for i, line in enumerate(text.split('\n'), start=1):
            for match in self.ID_PATTERN.finditer(line):
                results.append({
                    'id': match.group(1),
                    'line_number': i,
                    'context': line.strip()
                })
        return results

    def table_column_values(self, doc: ExtractedDocument, header_pattern: str,
                            column_name: str) -> List[str]:
        """在匹配 header_pattern 的 heading 后的第一个表格中，提取指定列的所有数据值"""
        table = self.table_after_heading(doc, header_pattern)
        if not table or not table.headers:
            return []

        if column_name not in table.headers:
            return []

        col_idx = table.headers.index(column_name)
        values = []
        for row in table.rows:
            if len(row) <= col_idx:
                continue
            val = row[col_idx].strip()
            # 跳过分隔符行（如 :---:）
            if re.match(r'^:?-+:?$', val):
                continue
            values.append(val)

        return values

    def column_values(self, doc: ExtractedDocument, column_name: str) -> List[str]:
        """扫描所有表格，找到包含指定列名的表格，提取该列的所有数据值"""
        values = []
        for table in doc.tables:
            if not table.headers:
                continue
            if column_name not in table.headers:
                continue
            col_idx = table.headers.index(column_name)
            for row in table.rows:
                if len(row) <= col_idx:
                    continue
                val = row[col_idx].strip()
                if re.match(r'^:?-+:?$', val):
                    continue
                values.append(val)
        return values
