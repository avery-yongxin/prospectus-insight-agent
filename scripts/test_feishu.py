from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent.feishu_bot import send_feishu_message


def main() -> int:
    message = "ProspectusInsight 飞书机器人测试消息：连接正常。"
    status = send_feishu_message(message)
    print(status)
    return 0 if "失败" not in status else 1


if __name__ == "__main__":
    raise SystemExit(main())
