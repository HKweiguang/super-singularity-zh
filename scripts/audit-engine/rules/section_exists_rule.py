"""
必填章节检查规则
验证产物是否包含必需的章节
"""

from typing import Optional, Dict
from .base_rule import BaseRule, AuditResult, ResultStatus


class SectionExistsRule(BaseRule):
    """检查必填章节是否存在"""

    RULE_NAME = "section_exists"
    DIMENSION = "结构"

    def check(self, document, context: Optional[Dict] = None) -> AuditResult:
        from config import get_required_sections

        result = AuditResult(rule_name=self.RULE_NAME)
        doc_type = (context or {}).get("doc_type", "generic")

        # 从配置获取该产物类型的必填章节
        required = get_required_sections(doc_type)

        # 检查产物头部标准
        has_version = bool(document.metadata.get("version"))
        result.add(self._make_checkpoint(
            id="S1",
            item="产物头部包含版本号",
            status=ResultStatus.PASS if has_version else ResultStatus.FAIL,
            note=None if has_version else "请在产物头部添加版本号，如：**版本号**：v1.0"
        ))

        has_date = bool(document.metadata.get("date"))
        result.add(self._make_checkpoint(
            id="S2",
            item="产物头部包含制定日期",
            status=ResultStatus.PASS if has_date else ResultStatus.FAIL,
            note=None if has_date else "请在产物头部添加制定日期，如：**制定日期**：2026-06-08"
        ))

        has_upstream = document.metadata.get("has_upstream_table") == "true"
        result.add(self._make_checkpoint(
            id="S3",
            item="产物头部包含上游文档表格",
            status=ResultStatus.PASS if has_upstream else ResultStatus.FAIL,
            note=None if has_upstream else "请在产物头部添加上游文档引用表格"
        ))

        # 检查必填章节
        import re
        section_titles = [s.title for s in document.sections]

        for idx, pattern in enumerate(required, start=4):
            regex = re.compile(pattern, re.IGNORECASE)
            found = any(regex.search(title) for title in section_titles)
            result.add(self._make_checkpoint(
                id=f"S{idx}",
                item=f"包含章节：{pattern}",
                status=ResultStatus.PASS if found else ResultStatus.FAIL,
                note=None if found else f"未找到匹配 '{pattern}' 的章节"
            ))

        return result
