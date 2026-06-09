"""
审计引擎
按产物类型组合规则集，执行审计并输出结构化结果
"""

import json
from dataclasses import asdict
from typing import Dict, List, Optional, Set
from pathlib import Path

from extractor import MarkdownExtractor
from rules import (
    BaseRule, AuditResult,
    SectionExistsRule, TableFormatRule, IdFormatRule,
    IdContinuityRule, BrokenLinkRule, BidirectionalMappingRule,
    ContractTraceabilityRule,
    TerminologyRule
)
from config import load_artifact_types


# 通用规则集（适用于所有产物类型）
_GENERIC_RULES = [
    SectionExistsRule,
    TableFormatRule,
    IdFormatRule,
    IdContinuityRule,
    BrokenLinkRule,
]

# 带上下游追溯的规则集（需要上下文时启用）
_FULL_RULES = _GENERIC_RULES + [BidirectionalMappingRule, ContractTraceabilityRule, TerminologyRule]


def _build_rule_sets() -> Dict[str, List]:
    """动态构建规则集：从 artifact_types.yaml 读取所有类型，统一注册通用规则"""
    config = load_artifact_types()
    types = config.get("types", {})

    rule_sets = {}
    for doc_type in types:
        # 所有类型使用相同的通用规则集
        # 双向映射规则仅在提供了 upstream_ids 上下文时才会实际生效
        rule_sets[doc_type] = _FULL_RULES

    # 确保 generic 存在
    if "generic" not in rule_sets:
        rule_sets["generic"] = _GENERIC_RULES

    return rule_sets


# 运行时构建（支持热更新配置）
RULE_SETS = _build_rule_sets()


class AuditEngine:
    """审计引擎"""

    def __init__(self):
        self.extractor = MarkdownExtractor()

    def audit(self, file_path: str, doc_type: str = "generic",
              context: Optional[Dict] = None) -> Dict:
        """
        执行审计

        Args:
            file_path: 产物文件路径
            doc_type: 产物类型（prd/interaction/ui/tech/test/generic）
            context: 可选上下文（上游文档信息、契约矩阵等）

        Returns:
            结构化审计报告（JSON 可序列化）
        """
        # 读取文件
        content = Path(file_path).read_text(encoding='utf-8')

        # 提取文档结构
        document = self.extractor.extract(content)

        # 准备上下文
        ctx = context or {}
        ctx["doc_type"] = doc_type
        ctx["file_path"] = file_path

        # 获取规则集
        rule_classes = RULE_SETS.get(doc_type, RULE_SETS["generic"])

        # 执行各规则
        results: List[AuditResult] = []
        all_passed = True

        for RuleClass in rule_classes:
            rule = RuleClass()
            result = rule.check(document, ctx)
            results.append(result)
            if not result.passed:
                all_passed = False

        # 构建报告
        report = {
            "file": file_path,
            "doc_type": doc_type,
            "passed": all_passed,
            "metadata": document.metadata,
            "summary": self._build_summary(results),
            "results": [self._serialize_result(r) for r in results],
        }

        return report

    def audit_directory(self, dir_path: str, doc_type: str = "generic",
                        context: Optional[Dict] = None) -> List[Dict]:
        """审计目录下的所有 .md 文件"""
        reports = []
        path = Path(dir_path)

        for md_file in path.glob("**/*.md"):
            # 排除草稿和实验文件
            if any(marker in md_file.name for marker in ["-draft", "-exp-", "[已废弃]"]):
                continue
            report = self.audit(str(md_file), doc_type, context)
            reports.append(report)

        return reports

    def _build_summary(self, results: List[AuditResult]) -> Dict:
        """构建摘要统计"""
        total = 0
        passed = 0
        failed = 0
        na = 0

        for result in results:
            for cp in result.checkpoints:
                total += 1
                if cp.status.value == "pass":
                    passed += 1
                elif cp.status.value == "fail":
                    failed += 1
                else:
                    na += 1

        return {
            "total_checkpoints": total,
            "passed": passed,
            "failed": failed,
            "na": na,
            "pass_rate": round(passed / (total - na) * 100, 1) if (total - na) > 0 else 0,
        }

    def _serialize_result(self, result: AuditResult) -> Dict:
        """序列化审计结果"""
        return {
            "rule_name": result.rule_name,
            "passed": result.passed,
            "checkpoints": [
                {
                    "id": cp.id,
                    "dimension": cp.dimension,
                    "item": cp.item,
                    "status": cp.status.value,
                    "line_number": cp.line_number,
                    "note": cp.note,
                }
                for cp in result.checkpoints
            ]
        }

    def generate_model_checklist(self, doc_type: str = "generic") -> Dict:
        """
        生成模型检查清单（--model-checklist 模式）
        脚本穷举列出全部检查点，AI 负责逐条判断
        """
        rule_classes = RULE_SETS.get(doc_type, RULE_SETS["generic"])

        checklist = {
            "doc_type": doc_type,
            "dimensions": ["结构", "数据", "状态", "错误", "性能", "安全"],
            "checkpoints": [],
            "expected_checkpoint_ids": [],
            "execution_discipline": {
                "must_respond_every_item": True,
                "must_provide_coverage_statement": True,
                "max_single_step_items": 10,
                "overage_action": "如果检查项超过 10 项，必须先输出分步计划，禁止自行减项"
            }
        }

        # 为每个规则创建空检查点模板
        for RuleClass in rule_classes:
            rule = RuleClass()
            # 创建模拟文档来获取检查点模板
            from extractor import ExtractedDocument
            mock_doc = ExtractedDocument()
            result = rule.check(mock_doc, {"doc_type": doc_type})

            for cp in result.checkpoints:
                checklist["checkpoints"].append({
                    "id": cp.id,
                    "dimension": cp.dimension,
                    "item": cp.item,
                    "result": "[待 AI 判断：pass / fail / na]",
                    "note": ""
                })
                checklist["expected_checkpoint_ids"].append(cp.id)

        return checklist
