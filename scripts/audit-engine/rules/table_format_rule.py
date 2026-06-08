"""
表格格式检查规则
验证 Markdown 表格的格式正确性
"""

from typing import Optional, Dict
from .base_rule import BaseRule, AuditResult, ResultStatus


class TableFormatRule(BaseRule):
    """检查表格格式是否正确"""

    RULE_NAME = "table_format"
    DIMENSION = "结构"

    def check(self, document, context: Optional[Dict] = None) -> AuditResult:
        result = AuditResult(rule_name=self.RULE_NAME)

        if not document.tables:
            result.add(self._make_checkpoint(
                id="T0",
                item="文档包含表格",
                status=ResultStatus.NA,
                note="本文档无表格，跳过表格格式检查"
            ))
            return result

        for idx, table in enumerate(document.tables, start=1):
            # 检查表头非空
            has_headers = all(h.strip() for h in table.headers)
            result.add(self._make_checkpoint(
                id=f"T{idx}-1",
                item=f"表格 {idx} 表头非空",
                status=ResultStatus.PASS if has_headers else ResultStatus.FAIL,
                line_number=table.line_number,
                note=None if has_headers else "表格表头存在空单元格"
            ))

            # 检查数据行列数与表头一致
            if table.rows:
                col_count = len(table.headers)
                row_lengths = [len(row) for row in table.rows]
                consistent = all(l == col_count for l in row_lengths)
                result.add(self._make_checkpoint(
                    id=f"T{idx}-2",
                    item=f"表格 {idx} 数据行列数与表头一致",
                    status=ResultStatus.PASS if consistent else ResultStatus.FAIL,
                    line_number=table.line_number,
                    note=None if consistent else f"表头 {col_count} 列，数据行长度不一致: {set(row_lengths)}"
                ))

            # 检查数据行非空
            has_data = any(any(cell.strip() for cell in row) for row in table.rows)
            result.add(self._make_checkpoint(
                id=f"T{idx}-3",
                item=f"表格 {idx} 包含数据",
                status=ResultStatus.PASS if has_data else ResultStatus.FAIL,
                line_number=table.line_number,
                note=None if has_data else "表格数据行全部为空"
            ))

        return result
