"""
契约驱动追溯规则
从契约矩阵读取追溯要求，检查上游定义的强制编号类型是否在当前产物中有对应引用。

核心设计：编号体系从"枚举式"升级为"契约驱动式"——
新增编号类型时只需在契约矩阵添加一行，审计自动覆盖。
"""

import re
from typing import Optional, Dict, List, Set
from pathlib import Path

from .base_rule import BaseRule, AuditResult, ResultStatus


class ContractTraceabilityRule(BaseRule):
    """
    契约驱动追溯规则

    检查逻辑：
    1. 加载契约矩阵配置
    2. 根据当前产物类型，筛选出需要引用的上游编号要求
    3. 从上游文档中提取对应类型的所有编号实例
    4. 检查这些编号是否在当前产物中出现
    """

    RULE_NAME = "contract_traceability"
    DIMENSION = "数据"

    # 产物类型 → 上游类型映射（用于查找上游文档）
    UPSTREAM_TYPE_MAP = {
        "interaction": ["prd"],
        "ui": ["prd", "interaction"],
        "tech": ["prd", "interaction", "ui"],
        "test": ["prd", "ui", "tech"],
    }

    def check(self, document, context: Optional[Dict] = None) -> AuditResult:
        result = AuditResult(rule_name=self.RULE_NAME)
        context = context or {}

        doc_type = context.get("doc_type", "generic")
        upstream_docs = context.get("upstream_docs", {})

        # 加载契约矩阵
        contract_matrix = self._load_contract_matrix()
        if not contract_matrix:
            result.add(self._make_checkpoint(
                id="CT-CONFIG",
                item="契约矩阵配置存在且可解析",
                status=ResultStatus.NA,
                note="契约矩阵配置不存在或无法解析，跳过契约追溯检查"
            ))
            return result

        # 获取当前产物类型需要遵循的契约规则
        type_rules = contract_matrix.get(doc_type, [])
        if not type_rules:
            result.add(self._make_checkpoint(
                id="CT-RULES",
                item="当前产物类型有契约规则定义",
                status=ResultStatus.NA,
                note=f"产物类型 '{doc_type}' 在契约矩阵中无规则定义，跳过检查"
            ))
            return result

        # 筛选强制规则
        mandatory_rules = [r for r in type_rules if r.get("mandatory", False)]
        if not mandatory_rules:
            result.add(self._make_checkpoint(
                id="CT-MANDATORY",
                item="存在强制契约规则需要检查",
                status=ResultStatus.NA,
                note="当前产物类型的契约规则均为非强制，跳过检查"
            ))
            return result

        # 逐个检查强制规则
        all_passed = True
        for idx, rule in enumerate(mandatory_rules, 1):
            prefix = rule.get("id_prefix", "")
            note = rule.get("note", "")
            downstream_location = rule.get("downstream_location", "产物中")

            # 从所有相关上游文档中提取该前缀的编号
            upstream_ids = self._extract_upstream_ids(upstream_docs, prefix)

            if not upstream_ids:
                # 上游没有定义该类型的编号，跳过
                result.add(self._make_checkpoint(
                    id=f"CT-{idx:03d}",
                    item=f"上游未定义 {prefix} 类型编号",
                    status=ResultStatus.NA,
                    note=f"契约规则: {note}"
                ))
                continue

            # 检查这些编号是否在当前产物中出现
            found_ids = self._find_ids_in_document(document, upstream_ids)
            missing = upstream_ids - found_ids

            if missing:
                all_passed = False
                result.add(self._make_checkpoint(
                    id=f"CT-{idx:03d}",
                    item=f"{prefix} 编号在 {downstream_location} 有引用",
                    status=ResultStatus.FAIL,
                    note=f"缺失 {len(missing)} 个 {prefix} 编号: {', '.join(sorted(missing)[:10])}"
                         f"{' 等...' if len(missing) > 10 else ''}"
                ))
            else:
                result.add(self._make_checkpoint(
                    id=f"CT-{idx:03d}",
                    item=f"{prefix} 编号在 {downstream_location} 有引用",
                    status=ResultStatus.PASS,
                    note=f"全部 {len(upstream_ids)} 个 {prefix} 编号均已引用"
                ))

        return result

    def _load_contract_matrix(self) -> Dict:
        """加载契约矩阵配置"""
        config_path = Path(__file__).parent.parent / "config" / "contract_matrix.yaml"
        if not config_path.exists():
            return {}

        try:
            import yaml
            with open(config_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
        except Exception:
            return {}

        # 合并 upstream_xxx 规则和直接的类型规则
        matrix = {}

        # 处理直接的类型规则（如 prd:, interaction:）
        for key, value in data.items():
            if key.startswith("upstream_"):
                continue
            if isinstance(value, list):
                matrix.setdefault(key, []).extend(value)

        # 处理 upstream_xxx 规则：将其映射到对应的下游类型
        for key, value in data.items():
            if not key.startswith("upstream_"):
                continue
            upstream_type = key.replace("upstream_", "")
            for entry in value:
                downstream_type = entry.get("downstream_type", "")
                if downstream_type:
                    matrix.setdefault(downstream_type, []).append({
                        "id_prefix": entry.get("id_prefix", ""),
                        "mandatory": entry.get("mandatory", False),
                        "downstream_location": entry.get("downstream_location", "产物中"),
                        "note": f"来自 {upstream_type} 的强制引用要求"
                    })

        return matrix

    def _extract_upstream_ids(self, upstream_docs: Dict, prefix: str) -> Set[str]:
        """从上游文档中提取指定前缀的所有编号"""
        ids = set()
        for path, doc in upstream_docs.items():
            if not hasattr(doc, 'ids'):
                continue
            for id_info in doc.ids:
                id_str = id_info.get('id', '')
                if id_str.startswith(prefix):
                    ids.add(id_str)
        return ids

    def _find_ids_in_document(self, document, target_ids: Set[str]) -> Set[str]:
        """检查一组编号是否在给定文档中出现"""
        found = set()
        if not hasattr(document, 'ids'):
            return found
        for id_info in document.ids:
            id_str = id_info.get('id', '')
            if id_str in target_ids:
                found.add(id_str)
        return found
