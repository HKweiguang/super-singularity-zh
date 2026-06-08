"""
编号格式检查规则
验证编号格式是否符合全局契约
"""

from typing import Optional, Dict
from .base_rule import BaseRule, AuditResult, ResultStatus


class IdFormatRule(BaseRule):
    """检查编号格式是否正确"""

    RULE_NAME = "id_format"
    DIMENSION = "数据"

    def check(self, document, context: Optional[Dict] = None) -> AuditResult:
        from config import load_id_patterns, get_id_prefixes

        result = AuditResult(rule_name=self.RULE_NAME)
        doc_type = (context or {}).get("doc_type", "generic")

        # 从配置加载编号格式和允许前缀
        id_patterns = load_id_patterns()
        valid_prefixes = set(get_id_prefixes(doc_type))
        # 如果产物类型没有定义前缀，回退到所有已知前缀
        if not valid_prefixes:
            valid_prefixes = set(id_patterns.keys())

        if not document.ids:
            result.add(self._make_checkpoint(
                id="I0",
                item="文档包含编号引用",
                status=ResultStatus.NA,
                note="本文档无编号引用，跳过格式检查"
            ))
            return result

        for idx, id_info in enumerate(document.ids, start=1):
            id_str = id_info['id']
            prefix = id_str.split('-')[0] if '-' in id_str else id_str

            # 检查前缀是否在允许列表中
            if prefix not in valid_prefixes:
                result.add(self._make_checkpoint(
                    id=f"I{idx}",
                    item=f"编号 '{id_str}' 使用允许的前缀",
                    status=ResultStatus.FAIL,
                    line_number=id_info['line_number'],
                    note=f"前缀 '{prefix}' 不在允许列表中。允许的前缀: {', '.join(valid_prefixes)}"
                ))
                continue

            # 检查格式是否匹配
            pattern = id_patterns.get(prefix)
            valid = bool(pattern.match(id_str)) if pattern else False
            result.add(self._make_checkpoint(
                id=f"I{idx}",
                item=f"编号 '{id_str}' 格式正确",
                status=ResultStatus.PASS if valid else ResultStatus.FAIL,
                line_number=id_info['line_number'],
                note=None if valid else f"编号 '{id_str}' 格式不符合 {prefix}-XXX 规范"
            ))

        return result
