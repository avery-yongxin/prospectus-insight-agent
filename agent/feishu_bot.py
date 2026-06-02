from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests


def _load_env_file() -> None:
    try:
        from dotenv import load_dotenv
    except ModuleNotFoundError:
        return
    load_dotenv()


def _flatten(value: Any, limit: int = 180) -> str:
    if value is None or value == "" or value == [] or value == {}:
        return "未识别"
    if isinstance(value, list):
        text = "；".join(_flatten(item, limit=limit) for item in value[:3])
    elif isinstance(value, dict):
        text = "；".join(f"{key}:{_flatten(val, limit=limit)}" for key, val in value.items())
    else:
        text = str(value)
    return text[:limit]


def _nested(data: dict[str, Any], section: str, key: str, fallback_key: str = "") -> Any:
    section_value = data.get(section)
    if isinstance(section_value, dict):
        value = section_value.get(key)
        if value not in (None, "", [], {}, "未识别"):
            return value
    if fallback_key:
        return data.get(fallback_key, "未识别")
    return "未识别"


def _count_questions(value: Any) -> int:
    if isinstance(value, list):
        return len(value)
    if isinstance(value, dict):
        return sum(_count_questions(item) for item in value.values())
    if value in (None, "", "未识别"):
        return 0
    return 1


def build_feishu_message(data: dict[str, Any], report_path: str = "outputs/prospectus_report.md") -> str:
    industry = _nested(data, "industry_analysis", "industry_status", "industry")
    business = _nested(data, "business_analysis", "business_model", "business_model")
    risks = _nested(data, "risk_analysis", "main_risks", "risk_factors")
    questions = data.get("due_diligence_questions") or []

    return (
        "ProspectusInsight 招股书解读摘要\n"
        f"公司名称：{data.get('company_name') or '未识别'}\n"
        f"所属行业：{_flatten(industry)}\n"
        f"核心业务：{_flatten(business)}\n"
        f"主要风险：{_flatten(risks)}\n"
        f"尽调问题数量：{_count_questions(questions)}\n"
        f"报告保存路径：{report_path}\n"
        "提示：本摘要仅用于公开资料整理，不构成投资建议。"
    )


def save_feishu_message(message: str, output_path: str | Path = "outputs/feishu_message.txt") -> None:
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(message, encoding="utf-8")


def send_feishu_message(message: str) -> str:
    _load_env_file()
    webhook = os.getenv("FEISHU_WEBHOOK_URL", "").strip()
    if not webhook:
        return "未配置飞书 Webhook，已跳过推送。"

    try:
        response = requests.post(
            webhook,
            json={"msg_type": "text", "content": {"text": message}},
            timeout=15,
        )
        response.raise_for_status()
    except Exception as exc:
        return f"飞书推送失败：{exc}"

    return "飞书推送成功。"
