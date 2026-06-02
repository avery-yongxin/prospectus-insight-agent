from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import os


class LLMConfigError(RuntimeError):
    """Raised when LLM configuration is missing or invalid."""


class LLMCallError(RuntimeError):
    """Raised when the LLM request fails or returns unusable content."""


@dataclass(frozen=True)
class LLMSettings:
    api_key: str
    base_url: str | None
    model: str


def load_llm_settings() -> LLMSettings:
    try:
        from dotenv import load_dotenv
    except ModuleNotFoundError:
        load_dotenv = None

    if load_dotenv:
        load_dotenv()
    api_key = os.getenv("LLM_API_KEY", "").strip()
    base_url = os.getenv("LLM_BASE_URL", "").strip() or None
    model = os.getenv("LLM_MODEL", "").strip()

    if not api_key:
        raise LLMConfigError("未配置 LLM_API_KEY，请复制 .env.example 为 .env 并填写 API Key。")
    if not model:
        raise LLMConfigError("未配置 LLM_MODEL，请在 .env 中填写 OpenAI-compatible 模型名称。")
    return LLMSettings(api_key=api_key, base_url=base_url, model=model)


def read_prompt(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def _extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?", "", cleaned, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"```$", "", cleaned).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not match:
            raise LLMCallError("模型未返回 JSON 对象。")
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError as exc:
            raise LLMCallError(f"模型返回 JSON 格式异常：{exc}") from exc


def extract_structured_info(prompt: str, prospectus_text: str, company_name: str = "") -> dict[str, Any]:
    settings = load_llm_settings()
    try:
        from openai import OpenAI
    except ModuleNotFoundError as exc:
        raise LLMConfigError("未安装 openai 依赖，请先运行 pip install -r requirements.txt。") from exc

    client = OpenAI(api_key=settings.api_key, base_url=settings.base_url)

    user_content = (
        f"可选公司名称：{company_name or '未提供，请从文本识别'}\n\n"
        f"招股说明书文本如下：\n{prospectus_text}"
    )
    try:
        response = client.chat.completions.create(
            model=settings.model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=0.2,
        )
    except Exception as exc:
        raise LLMCallError(f"LLM 调用失败：{exc}") from exc

    content = response.choices[0].message.content if response.choices else ""
    if not content:
        raise LLMCallError("LLM 返回为空。")
    return _extract_json(content)
