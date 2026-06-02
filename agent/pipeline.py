from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any

from agent.feishu_bot import build_feishu_message, save_feishu_message, send_feishu_message
from agent.llm_client import extract_structured_info, read_prompt
from agent.pdf_parser import extract_pdf_text
from agent.report_generator import save_markdown_report


OUTPUT_DIR = Path("outputs")
PROMPT_PATH = Path("prompts/extraction_prompt.md")

SCHEMA_TEMPLATE: dict[str, Any] = {
    "company_name": "未识别",
    "filing_type": "未识别",
    "listing_market": "未识别",
    "industry": "未识别",
    "company_profile": "未识别",
    "business_model": "未识别",
    "main_products_or_services": "未识别",
    "revenue_sources": "未识别",
    "key_financials": "未识别",
    "customers_and_suppliers": "未识别",
    "risk_factors": "未识别",
    "company_overview": {
        "basic_info": "未识别",
        "development_history": "未识别",
        "core_executives": "未识别",
        "ownership_structure": "未识别",
        "listing_information": "未识别",
    },
    "industry_analysis": {
        "industry_status": "未识别",
        "market_drivers": "未识别",
        "competitive_landscape": "未识别",
        "company_position": "未识别",
    },
    "business_analysis": {
        "business_model": "未识别",
        "core_products_or_services": "未识别",
        "revenue_breakdown": "未识别",
        "customers_and_suppliers": "未识别",
        "commercialization_progress": "未识别",
    },
    "financial_analysis": {
        "key_metrics": "未识别",
        "revenue_profit_cashflow": "未识别",
        "assets_and_liabilities": "未识别",
        "major_changes": "未识别",
        "financial_uncertainties": "未识别",
    },
    "risk_analysis": {
        "main_risks": "未识别",
        "risk_impacts": "未识别",
        "source_basis": "未识别",
    },
    "use_of_proceeds": {
        "projects": "未识别",
        "amounts_or_proportions": "未识别",
        "intended_uses": "未识别",
        "unidentified_items": "未识别",
    },
    "due_diligence_questions": {
        "company": "未识别",
        "business": "未识别",
        "financial": "未识别",
        "risk": "未识别",
        "fundraising": "未识别",
    },
    "evidence_snippets": {
        "company": "未识别",
        "industry": "未识别",
        "business": "未识别",
        "financial": "未识别",
        "risk": "未识别",
        "fundraising": "未识别",
    },
    "uncertainty_notes": "未识别",
}


def _is_missing(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def _normalize_with_template(value: Any, template: Any) -> Any:
    if isinstance(template, dict):
        source = value if isinstance(value, dict) else {}
        return {
            key: _normalize_with_template(source.get(key), child_template)
            for key, child_template in template.items()
        }
    return template if _is_missing(value) else value


def ensure_schema(data: dict[str, Any]) -> dict[str, Any]:
    normalized = _normalize_with_template(data or {}, SCHEMA_TEMPLATE)
    if normalized["industry"] == "未识别":
        normalized["industry"] = normalized["industry_analysis"]["industry_status"]
    if normalized["company_profile"] == "未识别":
        normalized["company_profile"] = normalized["company_overview"]["basic_info"]
    if normalized["business_model"] == "未识别":
        normalized["business_model"] = normalized["business_analysis"]["business_model"]
    if normalized["main_products_or_services"] == "未识别":
        normalized["main_products_or_services"] = normalized["business_analysis"]["core_products_or_services"]
    if normalized["revenue_sources"] == "未识别":
        normalized["revenue_sources"] = normalized["business_analysis"]["revenue_breakdown"]
    if normalized["customers_and_suppliers"] == "未识别":
        normalized["customers_and_suppliers"] = normalized["business_analysis"]["customers_and_suppliers"]
    if normalized["key_financials"] == "未识别":
        normalized["key_financials"] = normalized["financial_analysis"]["key_metrics"]
    if normalized["risk_factors"] == "未识别":
        normalized["risk_factors"] = normalized["risk_analysis"]["main_risks"]
    return normalized


def get_summary_value(data: dict[str, Any], path: list[str], fallback_key: str = "") -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict):
            current = None
            break
        current = current.get(key)
    if not _is_missing(current) and current != "未识别":
        return current
    if fallback_key:
        fallback = data.get(fallback_key)
        if not _is_missing(fallback):
            return fallback
    return "未识别"


def select_relevant_text(text: str, max_chars: int = 28000) -> str:
    """Keep sections most likely to contain core prospectus information."""
    if len(text) <= max_chars:
        return text

    keywords = [
        "公司概况",
        "发行人基本情况",
        "主营业务",
        "业务模式",
        "产品",
        "服务",
        "收入",
        "财务",
        "主要客户",
        "供应商",
        "风险因素",
        "募集资金",
        "募资用途",
    ]
    paragraphs = re.split(r"\n{2,}", text)
    scored: list[tuple[int, int, str]] = []
    for index, paragraph in enumerate(paragraphs):
        score = sum(3 for keyword in keywords if keyword in paragraph)
        score += 1 if re.search(r"\d+(?:\.\d+)?\s*(万元|亿元|%)", paragraph) else 0
        scored.append((score, -index, paragraph))

    selected = [paragraphs[0]]
    total = len(selected[0])
    for score, _, paragraph in sorted(scored, reverse=True):
        if score <= 0:
            continue
        if paragraph in selected:
            continue
        if total + len(paragraph) + 2 > max_chars:
            continue
        selected.append(paragraph)
        total += len(paragraph) + 2
    return "\n\n".join(selected)


def save_json(data: dict[str, Any], output_path: str | Path) -> None:
    Path(output_path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _flat(value: Any) -> str:
    if isinstance(value, (list, tuple)):
        return "；".join(str(item) for item in value)
    if isinstance(value, dict):
        return "；".join(f"{key}:{val}" for key, val in value.items())
    return str(value)


def save_summary_csv(data: dict[str, Any], output_path: str | Path) -> None:
    fields = [
        "company_name",
        "industry",
        "business_model",
        "revenue_sources",
        "key_financials",
        "risk_factors",
        "use_of_proceeds",
        "uncertainty_notes",
    ]
    row = {
        "company_name": _flat(data.get("company_name", "未识别")),
        "industry": _flat(get_summary_value(data, ["industry_analysis", "industry_status"], "industry")),
        "business_model": _flat(
            get_summary_value(data, ["business_analysis", "business_model"], "business_model")
        ),
        "revenue_sources": _flat(
            get_summary_value(data, ["business_analysis", "revenue_breakdown"], "revenue_sources")
        ),
        "key_financials": _flat(
            get_summary_value(data, ["financial_analysis", "key_metrics"], "key_financials")
        ),
        "risk_factors": _flat(get_summary_value(data, ["risk_analysis", "main_risks"], "risk_factors")),
        "use_of_proceeds": _flat(get_summary_value(data, ["use_of_proceeds", "projects"])),
        "uncertainty_notes": _flat(data.get("uncertainty_notes", "未识别")),
    }
    with Path(output_path).open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerow(row)


def run_pipeline(pdf_path: str | Path, company_name: str = "", push_feishu: bool = False) -> dict[str, Any]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf_path = Path(pdf_path)

    text = extract_pdf_text(pdf_path, OUTPUT_DIR / "extracted_text.txt")
    selected_text = select_relevant_text(text)
    prompt = read_prompt(PROMPT_PATH)
    analysis = ensure_schema(extract_structured_info(prompt, selected_text, company_name=company_name))

    save_json(analysis, OUTPUT_DIR / "prospectus_analysis.json")
    save_markdown_report(analysis, OUTPUT_DIR / "prospectus_report.md", source_file=str(pdf_path))
    save_summary_csv(analysis, OUTPUT_DIR / "prospectus_summary.csv")
    message = build_feishu_message(analysis, report_path=str(OUTPUT_DIR / "prospectus_report.md"))
    save_feishu_message(message, OUTPUT_DIR / "feishu_message.txt")
    feishu_status = send_feishu_message(message) if push_feishu else "未请求飞书推送，已生成摘要文件。"

    return {
        "analysis": analysis,
        "report_path": str(OUTPUT_DIR / "prospectus_report.md"),
        "json_path": str(OUTPUT_DIR / "prospectus_analysis.json"),
        "csv_path": str(OUTPUT_DIR / "prospectus_summary.csv"),
        "feishu_message_path": str(OUTPUT_DIR / "feishu_message.txt"),
        "feishu_status": feishu_status,
    }
