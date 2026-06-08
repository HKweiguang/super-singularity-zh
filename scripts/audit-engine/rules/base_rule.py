"""
审计规则基类
所有审计规则继承此类，实现 check 方法
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class ResultStatus(Enum):
    PASS = "pass"
    FAIL = "fail"
    NA = "na"  # 不适用


@dataclass
class Checkpoint:
    """单个检查点结果"""
    id: str
    dimension: str           # 所属维度：结构、数据、状态、错误、性能、安全
    item: str                # 检查项描述
    status: ResultStatus
    line_number: Optional[int] = None
    note: Optional[str] = None


@dataclass
class AuditResult:
    """规则审计结果"""
    rule_name: str
    checkpoints: List[Checkpoint] = field(default_factory=list)
    passed: bool = True

    def add(self, checkpoint: Checkpoint) -> None:
        self.checkpoints.append(checkpoint)
        if checkpoint.status == ResultStatus.FAIL:
            self.passed = False


class BaseRule(ABC):
    """审计规则抽象基类"""

    RULE_NAME = "base"
    DIMENSION = "结构"  # 默认维度

    @abstractmethod
    def check(self, document, context: Optional[Dict] = None) -> AuditResult:
        """
        执行审计检查

        Args:
            document: ExtractedDocument 实例
            context: 可选的上下文信息（如上游文档、产物类型等）

        Returns:
            AuditResult 审计结果
        """
        pass

    def _make_checkpoint(self, id: str, item: str, status: ResultStatus,
                         line_number: Optional[int] = None,
                         note: Optional[str] = None) -> Checkpoint:
        """便捷方法：创建检查点"""
        return Checkpoint(
            id=id,
            dimension=self.DIMENSION,
            item=item,
            status=status,
            line_number=line_number,
            note=note
        )
