"""
内部交叉引用检查规则
验证产物内部的章节引用、编号引用是否指向存在的内容
"""

import re
from typing import Optional, Dict
from .base_rule import BaseRule, AuditResult, ResultStatus


class BrokenLinkRule(BaseRule):
    """检查内部交叉引用是否有效"""

    RULE_NAME = "broken_link"
    DIMENSION = "结构"

    # 引用模式：如 "见 §3"、"参考 REQ-001"、"详见 4.2 节"
    SECTION_REF_PATTERN = re.compile(r'[见参详].*?§(\d+(?:\.\d+)*)')
    NUMBERED_REF_PATTERN = re.compile(r'第\s*(\d+(?:\.\d+)*)\s*[章节节]')

    def check(self, document, context: Optional[Dict] = None) -> AuditResult:
        result = AuditResult(rule_name=self.RULE_NAME)

        # 收集所有章节编号
        section_numbers = set()
        for section in document.sections:
            # 从标题中提取编号，如 "## 3. 功能需求" → "3"
            m = re.match(r'(\d+(?:\.\d+)*)[.、\s]', section.title)
            if m:
                section_numbers.add(m.group(1))

        # 收集所有存在的编号
        existing_ids = {id_info['id'] for id_info in document.ids}

        broken_refs = []

        for i, line in enumerate(document.lines, start=1):
            # 检查章节引用
            for match in self.SECTION_REF_PATTERN.finditer(line):
                ref = match.group(1)
                if ref not in section_numbers:
                    broken_refs.append((i, f"§{ref}", "章节引用不存在"))

            for match in self.NUMBERED_REF_PATTERN.finditer(line):
                ref = match.group(1)
                if ref not in section_numbers:
                    broken_refs.append((i, f"第 {ref} 节", "章节引用不存在"))

        if broken_refs:
            for line_no, ref, reason in broken_refs:
                result.add(self._make_checkpoint(
                    id="L-BROKEN",
                    item=f"内部引用 '{ref}' 有效",
                    status=ResultStatus.FAIL,
                    line_number=line_no,
                    note=reason
                ))
        else:
            result.add(self._make_checkpoint(
                id="L-OK",
                item="所有内部交叉引用有效",
                status=ResultStatus.PASS
            ))

        return result
