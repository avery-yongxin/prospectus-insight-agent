from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


def main() -> int:
    load_dotenv()
    api_key = os.getenv("LLM_API_KEY", "").strip()
    base_url = os.getenv("LLM_BASE_URL", "").strip() or None
    model = os.getenv("LLM_MODEL", "").strip()

    missing = [name for name, value in {"LLM_API_KEY": api_key, "LLM_MODEL": model}.items() if not value]
    if missing:
        print(f"跳过 API 连通性测试，缺少配置：{', '.join(missing)}。请参考 .env.example。")
        return 0

    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "请回复：API 测试成功"}],
            temperature=0,
        )
        content = response.choices[0].message.content if response.choices else ""
    except Exception as exc:
        print(f"LLM API 测试失败：{exc}")
        return 1

    print(f"LLM API 可用。模型返回：{content}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    raise SystemExit(main())

