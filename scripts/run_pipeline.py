from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.llm_client import LLMCallError, LLMConfigError
from agent.pdf_parser import PDFParseError
from agent.pipeline import run_pipeline


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ProspectusInsight pipeline.")
    parser.add_argument("--pdf", required=True, help="Path to prospectus PDF.")
    parser.add_argument("--company", default="", help="Optional company name.")
    parser.add_argument("--push-feishu", action="store_true", help="Push summary to Feishu webhook if configured.")
    args = parser.parse_args()

    print("[1/5] PDF 提取与清洗...")
    try:
        result = run_pipeline(args.pdf, company_name=args.company, push_feishu=args.push_feishu)
    except LLMConfigError as exc:
        print(f"配置错误：{exc}")
        return 2
    except PDFParseError as exc:
        print(f"PDF 解析失败：{exc}")
        return 3
    except LLMCallError as exc:
        print(f"模型调用失败：{exc}")
        return 4
    except Exception as exc:
        print(f"运行失败：{exc}")
        return 1

    print("[2/5] LLM 抽取完成。")
    print("[3/5] JSON/CSV/Markdown 已保存。")
    print("[4/5] 飞书摘要文件已生成。")
    print(f"[5/5] 飞书状态：{result['feishu_status']}")
    print(f"Markdown 报告：{result['report_path']}")
    print(f"JSON 输出：{result['json_path']}")
    print(f"CSV 输出：{result['csv_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

