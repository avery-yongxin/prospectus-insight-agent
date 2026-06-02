from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import streamlit as st

from agent.feishu_bot import send_feishu_message
from agent.llm_client import LLMCallError, LLMConfigError
from agent.pdf_parser import PDFParseError
from agent.pipeline import run_pipeline


def as_display_text(value: Any) -> Any:
    if value is None or value == "" or value == [] or value == {}:
        return "未识别"
    return value


def nested(data: dict[str, Any], section: str, key: str) -> Any:
    section_value = data.get(section)
    if not isinstance(section_value, dict):
        return "未识别"
    return as_display_text(section_value.get(key))


def _escape_markdown(text: Any) -> str:
    return str(text).replace("\\", "\\\\").replace("\n", "  \n")


def _format_value(value: Any, level: int = 0) -> str:
    value = as_display_text(value)
    if isinstance(value, list):
        return "\n".join(f"{'  ' * level}- {_format_value(item, level + 1).lstrip()}" for item in value)
    if isinstance(value, dict):
        blocks: list[str] = []
        for key, item in value.items():
            item = as_display_text(item)
            if isinstance(item, (list, dict)):
                blocks.append(f"{'  ' * level}**{key}**\n{_format_value(item, level)}")
            else:
                blocks.append(f"{'  ' * level}- **{key}**：{_escape_markdown(item)}")
        return "\n\n".join(blocks) if blocks else "未识别"
    return _escape_markdown(value)


def render_value(value: Any) -> None:
    st.markdown(_format_value(value))


st.set_page_config(page_title="ProspectusInsight Agent", page_icon="PI", layout="wide")

st.title("ProspectusInsight Agent")
st.caption("招股说明书智能解读与公司画像生成助手")

st.warning(
    "项目边界：本工具只做公开资料整理和初步分析，不构成投资建议；"
    "不生成买入、卖出、目标价、投资评级或收益预测；AI 输出需人工复核。"
)

uploaded_file = st.file_uploader("上传一份招股说明书 PDF", type=["pdf"])
company_name = st.text_input("公司名称（可选，留空则由 AI 从文本中识别）")
push_feishu = st.checkbox("解读完成后推送飞书机器人", value=False)

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if st.button("开始解读", type="primary"):
    if uploaded_file is None:
        st.error("请先上传招股说明书 PDF。")
    else:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.getbuffer())
            temp_path = temp_file.name

        try:
            with st.spinner("正在解析 PDF、调用模型并生成报告..."):
                st.session_state.last_result = run_pipeline(
                    temp_path,
                    company_name=company_name.strip(),
                    push_feishu=push_feishu,
                )
            st.success("解读完成。")
        except LLMConfigError as exc:
            st.error(str(exc))
        except (PDFParseError, LLMCallError) as exc:
            st.error(str(exc))
        except Exception as exc:
            st.error(f"运行失败：{exc}")
        finally:
            Path(temp_path).unlink(missing_ok=True)

result = st.session_state.last_result
if result:
    data = result["analysis"]
    st.subheader("智能解读结果")
    tabs = st.tabs(["公司简介", "行业分析", "业务分析", "财务分析", "风险与募资", "证据与复核"])

    with tabs[0]:
        st.markdown("**基本信息**")
        render_value(nested(data, "company_overview", "basic_info"))
        st.markdown("**发展历程**")
        render_value(nested(data, "company_overview", "development_history"))
        st.markdown("**核心高管**")
        render_value(nested(data, "company_overview", "core_executives"))
        st.markdown("**股权架构**")
        render_value(nested(data, "company_overview", "ownership_structure"))
        st.markdown("**上市信息**")
        render_value(nested(data, "company_overview", "listing_information"))
    with tabs[1]:
        st.markdown("**行业发展现状**")
        render_value(nested(data, "industry_analysis", "industry_status"))
        st.markdown("**市场驱动因素**")
        render_value(nested(data, "industry_analysis", "market_drivers"))
        st.markdown("**竞争格局**")
        render_value(nested(data, "industry_analysis", "competitive_landscape"))
        st.markdown("**公司行业地位**")
        render_value(nested(data, "industry_analysis", "company_position"))
    with tabs[2]:
        st.markdown("**业务模式**")
        render_value(nested(data, "business_analysis", "business_model"))
        st.markdown("**主要产品或服务**")
        render_value(nested(data, "business_analysis", "core_products_or_services"))
        st.markdown("**收入拆分**")
        render_value(nested(data, "business_analysis", "revenue_breakdown"))
        st.markdown("**客户与供应商**")
        render_value(nested(data, "business_analysis", "customers_and_suppliers"))
        st.markdown("**商业化进展**")
        render_value(nested(data, "business_analysis", "commercialization_progress"))
    with tabs[3]:
        st.markdown("**核心财务摘要**")
        render_value(nested(data, "financial_analysis", "key_metrics"))
        st.markdown("**收入、利润和现金流变化**")
        render_value(nested(data, "financial_analysis", "revenue_profit_cashflow"))
        st.markdown("**资产负债情况**")
        render_value(nested(data, "financial_analysis", "assets_and_liabilities"))
        st.markdown("**关键变化**")
        render_value(nested(data, "financial_analysis", "major_changes"))
        st.markdown("**财务不确定性**")
        render_value(nested(data, "financial_analysis", "financial_uncertainties"))
    with tabs[4]:
        st.markdown("**主要风险**")
        render_value(nested(data, "risk_analysis", "main_risks"))
        st.markdown("**风险影响**")
        render_value(nested(data, "risk_analysis", "risk_impacts"))
        st.markdown("**募资项目**")
        render_value(nested(data, "use_of_proceeds", "projects"))
        st.markdown("**金额或比例**")
        render_value(nested(data, "use_of_proceeds", "amounts_or_proportions"))
        st.markdown("**资金用途**")
        render_value(nested(data, "use_of_proceeds", "intended_uses"))
    with tabs[5]:
        st.markdown("**尽调问题**")
        render_value(data.get("due_diligence_questions", "未识别"))
        st.markdown("**证据片段**")
        render_value(data.get("evidence_snippets", "未识别"))
        st.markdown("**不确定性说明**")
        render_value(data.get("uncertainty_notes", "未识别"))

    report_path = Path(result["report_path"])
    if report_path.exists():
        st.download_button(
            "保存 Markdown 报告",
            data=report_path.read_text(encoding="utf-8"),
            file_name="prospectus_report.md",
            mime="text/markdown",
        )

    if st.button("推送飞书机器人"):
        message_path = Path(result["feishu_message_path"])
        message = message_path.read_text(encoding="utf-8") if message_path.exists() else ""
        st.info(send_feishu_message(message))
