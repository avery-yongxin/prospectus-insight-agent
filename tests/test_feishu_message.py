from __future__ import annotations

import unittest

from agent.feishu_bot import build_feishu_message
from agent.pipeline import ensure_schema


class FeishuMessageTest(unittest.TestCase):
    def test_build_feishu_message_uses_nested_summary_fields(self) -> None:
        data = ensure_schema(
            {
                "company_name": "英矽智能",
                "industry_analysis": {
                    "industry_status": ["AI 制药行业仍处于发展阶段"],
                },
                "business_analysis": {
                    "business_model": ["AI 平台服务", "自研管线开发"],
                },
                "risk_analysis": {
                    "main_risks": ["研发失败风险", "商业化不确定风险", "持续亏损风险"],
                },
                "due_diligence_questions": {
                    "company": ["股权架构是否稳定？"],
                    "financial": ["亏损原因是否可持续改善？"],
                },
            }
        )

        message = build_feishu_message(data, report_path="outputs/prospectus_report.md")

        self.assertIn("公司名称：英矽智能", message)
        self.assertIn("所属行业：AI 制药行业仍处于发展阶段", message)
        self.assertIn("核心业务：AI 平台服务；自研管线开发", message)
        self.assertIn("主要风险：研发失败风险；商业化不确定风险；持续亏损风险", message)
        self.assertIn("尽调问题数量：2", message)


if __name__ == "__main__":
    unittest.main()
