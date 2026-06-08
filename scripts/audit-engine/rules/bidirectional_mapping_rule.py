"""
双向映射检查规则
正向：上游产物中定义的编号 → 当前产物中是否有对应引用
反向：当前产物中引用的编号 → 上游产物中是否有定义
"""

from typing import Optional, Dict, List
from .base_rule import BaseRule, AuditResult, ResultStatus


class BidirectionalMappingRule(BaseRule):
    """检查上下游编号引用的双向一致性"""

    RULE_NAME = "bidirectional_mapping"
    DIMENSION = "数据"

    def check(self, document, context: Optional[Dict] = None) -> AuditResult:
        result = AuditResult(rule_name=self.RULE_NAME)
        context = context or {}

        # 从上下文中获取上游文档信息
        upstream_docs = context.get("upstream_docs", [])
        upstream_ids = context.get("upstream_ids", set())

        # 当前文档中的编号
        current_defined_ids = set()
        current_referenced_ids = set()

        for id_info in document.ids:
            id_str = id_info['id']
            # 简单判断：如果编号出现在标题或列表中，可能是定义；否则是引用
            line = id_info.get('context', '')
            if line.startswith('#') or line.startswith('-') or line.startswith('*'):
                current_defined_ids.add(id_str)
            else:
                current_referenced_ids.add(id_str)

        # 如果没有上游文档，只做当前文档内部的检查
        if not upstream_ids:
            result.add(self._make_checkpoint(
                id="B-UPSTREAM",
                item="存在上游文档用于双向映射检查",
                status=ResultStatus.NA,
                note="未提供上游文档信息，跳过双向映射检查"
            ))
            return result

        # 正向检查：上游定义的编号，当前文档是否引用了应该引用的
        # 根据契约矩阵，某些上游编号在当前产物类型中是强制引用的
        contract_matrix = context.get("contract_matrix", {})
        doc_type = context.get("doc_type", "generic")

        required_refs = set()
        for entry in contract_matrix.get(doc_type, []):
            if entry.get("mandatory", False):
                prefix = entry.get("id_prefix", "")
                required_refs.update({
                    uid for uid in upstream_ids
                    if uid.startswith(prefix)
                })

        missing_refs = required_refs - current_referenced_ids - current_defined_ids
        if missing_refs:
            result.add(self._make_checkpoint(
                id="B-FORWARD",
                item="当前产物引用了所有上游强制编号",
                status=ResultStatus.FAIL,
                note=f"缺少对上游编号的引用: {', '.join(sorted(missing_refs))}"
            ))
        else:
            result.add(self._make_checkpoint(
                id="B-FORWARD",
                item="当前产物引用了所有上游强制编号",
                status=ResultStatus.PASS
            ))

        # 反向检查：当前文档引用的编号，上游是否定义了
        orphan_refs = current_referenced_ids - upstream_ids - current_defined_ids
        if orphan_refs:
            result.add(self._make_checkpoint(
                id="B-REVERSE",
                item="当前产物引用的编号在上游有定义",
                status=ResultStatus.FAIL,
                note=f"引用了上游未定义的编号: {', '.join(sorted(orphan_refs))}"
            ))
        else:
            result.add(self._make_checkpoint(
                id="B-REVERSE",
                item="当前产物引用的编号在上游有定义",
                status=ResultStatus.PASS
            ))

        return result
