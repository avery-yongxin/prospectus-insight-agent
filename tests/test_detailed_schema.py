from __future__ import annotations

import unittest

from agent.pipeline import ensure_schema, get_summary_value


class DetailedSchemaTest(unittest.TestCase):
    def test_ensure_schema_fills_nested_missing_fields(self) -> None:
        data = {
            "company_name": "英矽智能",
            "company_overview": {
                "basic_info": "AI 制药公司",
            },
            "business_analysis": {
                "business_model": ["提供 AI 药物研发平台服务"],
            },
        }

        normalized = ensure_schema(data)

        self.assertEqual(normalized["company_name"], "英矽智能")
        self.assertEqual(normalized["company_overview"]["basic_info"], "AI 制药公司")
        self.assertEqual(normalized["company_overview"]["development_history"], "未识别")
        self.assertEqual(normalized["company_overview"]["core_executives"], "未识别")
        self.assertEqual(normalized["industry_analysis"]["competitive_landscape"], "未识别")
        self.assertEqual(normalized["financial_analysis"]["key_metrics"], "未识别")
        self.assertEqual(normalized["risk_analysis"]["main_risks"], "未识别")
        self.assertEqual(normalized["due_diligence_questions"]["financial"], "未识别")

    def test_ensure_schema_keeps_existing_lists_and_dicts(self) -> None:
        data = {
            "company_name": "示例公司",
            "industry_analysis": {
                "industry_status": ["行业处于快速发展阶段", "政策支持力度较高"],
            },
            "financial_analysis": {
                "key_metrics": {
                    "收入": "报告期收入增长",
                    "利润": "仍处亏损状态",
                },
            },
        }

        normalized = ensure_schema(data)

        self.assertEqual(
            normalized["industry_analysis"]["industry_status"],
            ["行业处于快速发展阶段", "政策支持力度较高"],
        )
        self.assertEqual(normalized["financial_analysis"]["key_metrics"]["收入"], "报告期收入增长")
        self.assertEqual(normalized["financial_analysis"]["major_changes"], "未识别")

    def test_get_summary_value_reads_nested_paths_and_legacy_fallback(self) -> None:
        data = ensure_schema(
            {
                "industry": "生物科技",
                "business_analysis": {
                    "business_model": "AI 药物研发平台与管线开发",
                },
                "risk_analysis": {
                    "main_risks": ["研发失败风险", "商业化不确定风险"],
                },
            }
        )

        self.assertEqual(get_summary_value(data, ["industry_analysis", "industry_status"], "industry"), "生物科技")
        self.assertEqual(
            get_summary_value(data, ["business_analysis", "business_model"], "business_model"),
            "AI 药物研发平台与管线开发",
        )
        self.assertEqual(
            get_summary_value(data, ["risk_analysis", "main_risks"], "risk_factors"),
            ["研发失败风险", "商业化不确定风险"],
        )


if __name__ == "__main__":
    unittest.main()
