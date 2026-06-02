from __future__ import annotations

import unittest

from agent.pipeline import ensure_schema
from agent.report_generator import build_markdown_report


class DetailedReportGeneratorTest(unittest.TestCase):
    def test_build_markdown_report_renders_detailed_sections(self) -> None:
        data = ensure_schema(
            {
                "company_name": "英矽智能",
                "filing_type": "招股说明书",
                "listing_market": "港交所",
                "company_overview": {
                    "basic_info": "公司专注于 AI 药物研发。",
                    "development_history": ["成立后搭建 AI 平台", "推进自研管线"],
                    "core_executives": "管理层信息来自原文披露。",
                    "ownership_structure": "未识别",
                    "listing_information": "拟在港交所上市。",
                },
                "industry_analysis": {
                    "industry_status": "AI 制药行业仍处于发展阶段。",
                    "competitive_landscape": ["行业参与者包括平台型公司和传统药企"],
                },
                "business_analysis": {
                    "business_model": "平台服务与管线开发结合。",
                    "core_products_or_services": ["Pharma.AI 平台", "自研管线"],
                    "revenue_breakdown": "报告期收入按原文披露口径整理。",
                },
                "financial_analysis": {
                    "key_metrics": {"收入": "收入增长", "利润": "仍处亏损"},
                    "revenue_profit_cashflow": "经营现金流需结合原文复核。",
                },
                "risk_analysis": {
                    "main_risks": ["研发失败风险"],
                    "risk_impacts": "可能影响商业化和持续经营表现。",
                },
                "use_of_proceeds": {
                    "projects": ["研发项目", "平台建设"],
                },
                "due_diligence_questions": {
                    "financial": ["报告期亏损的主要原因是什么？"],
                },
                "evidence_snippets": {
                    "business": ["[第 10 页] 公司披露平台服务与管线开发。"],
                },
                "uncertainty_notes": ["股权架构未识别，需人工复核。"],
            }
        )

        report = build_markdown_report(data, source_file="sample.pdf")

        self.assertIn("## 2. 公司简介", report)
        self.assertIn("### 2.2 发展历程", report)
        self.assertIn("## 3. 行业分析", report)
        self.assertIn("### 4.3 收入拆分", report)
        self.assertIn("## 5. 财务分析", report)
        self.assertIn("### 6.1 主要风险", report)
        self.assertIn("## 9. 证据片段与不确定性说明", report)
        self.assertIn("- 成立后搭建 AI 平台", report)
        self.assertIn("- **收入**：收入增长", report)
        self.assertIn("股权架构未识别，需人工复核", report)

    def test_build_markdown_report_shows_unidentified_for_missing_nested_sections(self) -> None:
        data = ensure_schema({"company_name": "示例公司"})

        report = build_markdown_report(data)

        self.assertIn("### 2.3 核心高管\n\n未识别", report)
        self.assertIn("### 3.3 竞争格局\n\n未识别", report)
        self.assertIn("### 5.4 关键变化\n\n未识别", report)


if __name__ == "__main__":
    unittest.main()
