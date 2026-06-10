#!/usr/bin/env python3
"""
DAG 引擎 CLI（v2.0）
基于 input/output 节点模型的通用工作流 DAG 分析工具

用法:
    python dag-engine.py --workflow .artifacts/workflow.yaml --visualize
    python dag-engine.py --workflow .artifacts/workflow.yaml --detect-cycles
    python dag-engine.py --workflow .artifacts/workflow.yaml --impact prd
    python dag-engine.py --workflow .artifacts/workflow.yaml --execution-plan
"""

import argparse
import json
import sys
from pathlib import Path

from dag_core import DAG, WorkflowBuilder
from formatters import TextFormatter, JSONFormatter, MermaidFormatter


def build_dag_from_workflow(workflow_path: str) -> DAG:
    """从 YAML workflow 构建 DAG"""
    builder = WorkflowBuilder()
    return builder.build_from_yaml(workflow_path)


def get_formatter(format_type: str):
    """获取格式化器"""
    formatters = {
        "text": TextFormatter(),
        "json": JSONFormatter(),
        "mermaid": MermaidFormatter(),
    }
    return formatters.get(format_type, TextFormatter())


def main():
    parser = argparse.ArgumentParser(description="Singularity DAG 引擎 v2.0")

    parser.add_argument("--workflow", required=True, help="YAML 工作流文件路径")

    # 分析子命令
    parser.add_argument("--visualize", action="store_true", help="可视化 DAG（Mermaid）")
    parser.add_argument("--detect-cycles", action="store_true", help="检测循环依赖")
    parser.add_argument("--impact", help="变更影响分析（指定变更的节点 ID）")
    parser.add_argument("--critical-path", action="store_true", help="关键路径分析")
    parser.add_argument("--execution-plan", action="store_true", help="执行波次计划（默认）")

    # 输出控制
    parser.add_argument("--format", default="text", choices=["text", "json", "mermaid"],
                        help="输出格式")
    parser.add_argument("--output", help="输出文件路径（默认 stdout）")

    args = parser.parse_args()

    # 构建 DAG
    try:
        dag = build_dag_from_workflow(args.workflow)
    except Exception as e:
        print(f"❌ DAG 构建失败: {e}", file=sys.stderr)
        sys.exit(1)

    # 循环检测（优先级最高，有循环时其他分析可能不准确）
    if dag.cycle_info and dag.cycle_info.has_cycle:
        formatter = get_formatter(args.format)
        if args.format == "json":
            output = json.dumps({
                "has_cycle": True,
                "cycle_path": dag.cycle_info.cycle_path,
            }, ensure_ascii=False, indent=2)
        else:
            output = TextFormatter().format_cycles(dag)

        if args.output:
            Path(args.output).write_text(output, encoding='utf-8')
            print(f"报告已保存至：{args.output}")
        else:
            print(output)

        print("\n⚠️ 检测到循环依赖，请先解决后再执行其他分析。")
        sys.exit(1)

    # 执行分析
    formatter = get_formatter(args.format)

    if args.detect_cycles:
        if args.format == "json":
            output = json.dumps({"has_cycle": False}, ensure_ascii=False, indent=2)
        else:
            output = TextFormatter().format_cycles(dag)

    elif args.impact:
        report = dag.analyze_impact(args.impact)
        if args.format == "json":
            output = JSONFormatter().format_impact(report, dag)
        else:
            output = TextFormatter().format_impact(report, dag)

    elif args.critical_path:
        if args.format == "json":
            output = JSONFormatter().format_dag(dag)
        else:
            output = TextFormatter().format_critical_path(dag)

    elif args.visualize:
        if args.format == "mermaid":
            output = MermaidFormatter().format_dag(dag)
        elif args.format == "json":
            output = JSONFormatter().format_dag(dag)
        else:
            output = MermaidFormatter().format_dag(dag)

    else:
        # 默认：执行波次计划
        if args.format == "json":
            output = JSONFormatter().format_dag(dag)
        elif args.format == "mermaid":
            output = MermaidFormatter().format_execution_plan(dag)
        else:
            output = TextFormatter().format_execution_plan(dag)

    # 输出
    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        print(f"报告已保存至：{args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
