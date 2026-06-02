from __future__ import annotations

from pathlib import Path
from typing import Any


def _as_text(value: Any) -> str:
    if value is None or value == "":
        return "未识别"
    if isinstance(value, list):
        if not value:
            return "未识别"
        return "\n".join(f"- {_as_text(item)}" for item in value)
    if isinstance(value, dict):
        if not value:
            return "未识别"
        return "\n".join(f"- **{key}**：{_as_text(val)}" for key, val in value.items())
    return str(value)


def _nested(data: dict[str, Any], section: str, key: str) -> Any:
    value = data.get(section)
    if not isinstance(value, dict):
        return "未识别"
    return value.get(key, "未识别")


def build_markdown_report(data: dict[str, Any], source_file: str = "") -> str:
    company = data.get("company_name") or "未识别"
    filing_type = data.get("filing_type") or "招股说明书"
    market = data.get("listing_market") or "未识别"

    return f"""# ProspectusInsight 招股说明书智能解读报告

> 本报告仅基于用户上传的公开招股说明书文本生成，用于学习辅助和初步资料整理，不构成投资建议。关键数据、口径和结论均需人工复核。

## 1. 分析对象与资料来源

- 公司名称：{company}
- 文件类型：{filing_type}
- 拟上市市场：{market}
- 资料来源：{source_file or "用户上传 PDF"}
- 生成说明：AI 输出可能存在识别误差，所有重要信息应回到原文核验。

## 2. 公司简介

### 2.1 基本信息

{_as_text(_nested(data, "company_overview", "basic_info"))}

### 2.2 发展历程

{_as_text(_nested(data, "company_overview", "development_history"))}

### 2.3 核心高管

{_as_text(_nested(data, "company_overview", "core_executives"))}

### 2.4 股权架构

{_as_text(_nested(data, "company_overview", "ownership_structure"))}

### 2.5 上市信息

{_as_text(_nested(data, "company_overview", "listing_information"))}

## 3. 行业分析

### 3.1 行业发展现状

{_as_text(_nested(data, "industry_analysis", "industry_status"))}

### 3.2 市场驱动因素

{_as_text(_nested(data, "industry_analysis", "market_drivers"))}

### 3.3 竞争格局

{_as_text(_nested(data, "industry_analysis", "competitive_landscape"))}

### 3.4 公司行业地位

{_as_text(_nested(data, "industry_analysis", "company_position"))}

## 4. 业务分析

### 4.1 业务模式

{_as_text(_nested(data, "business_analysis", "business_model"))}

### 4.2 核心产品或服务

{_as_text(_nested(data, "business_analysis", "core_products_or_services"))}

### 4.3 收入拆分

{_as_text(_nested(data, "business_analysis", "revenue_breakdown"))}

### 4.4 客户与供应商

{_as_text(_nested(data, "business_analysis", "customers_and_suppliers"))}

### 4.5 商业化进展

{_as_text(_nested(data, "business_analysis", "commercialization_progress"))}

## 5. 财务分析

### 5.1 主要财务指标

{_as_text(_nested(data, "financial_analysis", "key_metrics"))}

### 5.2 收入、利润和现金流变化

{_as_text(_nested(data, "financial_analysis", "revenue_profit_cashflow"))}

### 5.3 资产负债情况

{_as_text(_nested(data, "financial_analysis", "assets_and_liabilities"))}

### 5.4 关键变化

{_as_text(_nested(data, "financial_analysis", "major_changes"))}

### 5.5 财务不确定性

{_as_text(_nested(data, "financial_analysis", "financial_uncertainties"))}

## 6. 风险提示

### 6.1 主要风险

{_as_text(_nested(data, "risk_analysis", "main_risks"))}

### 6.2 风险影响

{_as_text(_nested(data, "risk_analysis", "risk_impacts"))}

### 6.3 原文依据

{_as_text(_nested(data, "risk_analysis", "source_basis"))}

## 7. 募资用途

### 7.1 募资项目

{_as_text(_nested(data, "use_of_proceeds", "projects"))}

### 7.2 金额或比例

{_as_text(_nested(data, "use_of_proceeds", "amounts_or_proportions"))}

### 7.3 资金用途

{_as_text(_nested(data, "use_of_proceeds", "intended_uses"))}

### 7.4 未识别项目

{_as_text(_nested(data, "use_of_proceeds", "unidentified_items"))}

## 8. 尽调问题清单

### 8.1 公司与治理

{_as_text(_nested(data, "due_diligence_questions", "company"))}

### 8.2 业务与产品

{_as_text(_nested(data, "due_diligence_questions", "business"))}

### 8.3 财务与经营

{_as_text(_nested(data, "due_diligence_questions", "financial"))}

### 8.4 风险核验

{_as_text(_nested(data, "due_diligence_questions", "risk"))}

### 8.5 募资用途核验

{_as_text(_nested(data, "due_diligence_questions", "fundraising"))}

## 9. 证据片段与不确定性说明

### 9.1 证据片段

{_as_text(data.get("evidence_snippets"))}

### 9.2 不确定性说明

{_as_text(data.get("uncertainty_notes"))}
"""


def save_markdown_report(data: dict[str, Any], output_path: str | Path, source_file: str = "") -> str:
    report = build_markdown_report(data, source_file=source_file)
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(report, encoding="utf-8")
    return report
