# ProspectusInsight Agent：招股说明书智能解读与公司画像生成助手

ProspectusInsight Agent 是一个面向课程大作业的 AI 智能体项目。用户上传一份上市公司招股说明书 PDF 后，系统解析公开披露文本，调用 OpenAI-compatible API 抽取关键信息，生成公司画像、业务模式、核心财务摘要、风险因素、募资用途、尽调问题和飞书机器人推送摘要。

本项目只用于公开资料整理、学习辅助和初步分析，不构成投资建议。AI 输出的重要数据、事实和结论必须人工复核。

## 为什么选择招股说明书

招股说明书是企业上市过程中重要的公开披露文件，包含公司历史沿革、主营业务、财务数据、风险因素、募集资金用途等信息。它篇幅长、信息密度高、章节分散，适合训练 AI Agent 的文档解析、信息抽取、报告生成和协同推送能力。

## 真实场景与痛点

金融专业学生、行研实习生、投行/咨询/数据分析初学者在阅读招股说明书时，经常遇到以下问题：

- 文件页数多，第一次阅读难以抓住重点。
- 公司画像、业务模式、风险因素和财务信息分散在不同章节。
- 人工整理 Markdown 报告、CSV 表格和小组摘要耗时较长。
- 资料整理后还需要通过飞书等协同工具同步给团队成员。
- AI 结果可能存在遗漏或误读，需要明确证据和人工复核流程。

## 服务对象

- 金融专业学生
- 行业研究实习生
- 投行、咨询、数据分析初学者
- 需要练习公开披露文件阅读和资料整理的小组成员

## 项目目标与边界

目标：

- 提供一个可运行的 Streamlit 智能体应用。
- 自动完成 PDF 文本解析、结构化抽取、报告生成、文件保存和飞书摘要推送。
- 用静态网页展示项目功能、工作流、可靠性原则和课程价值。

边界：

- 当前版本只做“招股说明书”智能解读。
- 当前版本不做年报、多年度对比、公告分析、估值模型或投资评级。
- 不提供交易决策、目标价、收益预测或结果准确性承诺。
- 未识别信息必须标注“未识别”，关键数据必须回到原文核验。
- GitHub 仓库不上传真实敏感文件、内部底稿或未公开材料。

## 功能模块

- `agent/app.py`：Streamlit 应用界面，支持 PDF 上传、公司名输入、结果展示、报告下载、飞书推送。
- `agent/pdf_parser.py`：使用 PyMuPDF 提取 PDF 文本，保留页码信息，并识别扫描版或空文本异常。
- `agent/llm_client.py`：读取 `.env` 配置并调用 OpenAI-compatible API。
- `agent/pipeline.py`：串联 PDF 解析、文本筛选、LLM 抽取、JSON 容错、Markdown/CSV/JSON 输出和飞书摘要生成。
- `agent/report_generator.py`：根据结构化 JSON 生成审慎的 Markdown 报告。
- `agent/feishu_bot.py`：通过飞书自定义机器人 Webhook 推送短摘要。
- `code/` 静态网页：用于网页设计作业和项目展示。

## 智能体工作流

用户上传 PDF → PDF 文本解析 → 文本清洗 → 重点内容筛选 → LLM 信息抽取 → 结构化 JSON → Markdown 报告 → CSV 摘要 → 飞书消息 → 人工复核。

## 技术架构

- Python：智能体后端、CLI、文件处理。
- Streamlit：交互式应用界面。
- PyMuPDF：PDF 文本解析。
- OpenAI SDK：OpenAI-compatible API 调用。
- pandas / csv：摘要表格输出。
- python-dotenv：环境变量配置。
- requests：飞书 Webhook 调用。
- HTML + CSS + JavaScript：静态展示网站。

## 安装方式

进入 `code` 目录后运行：

```bash
pip install -r requirements.txt
```

## .env 配置方式

复制示例配置：

```bash
copy .env.example .env
```

填写：

```text
LLM_API_KEY=你的 API Key
LLM_BASE_URL=OpenAI-compatible Base URL，可留空使用默认 OpenAI 地址
LLM_MODEL=模型名称
FEISHU_WEBHOOK_URL=飞书自定义机器人 Webhook，可选
```


## Streamlit 运行方式

```bash
python -m streamlit run agent/app.py
```

页面功能：

- 上传一份招股说明书 PDF。
- 可选输入公司名称。
- 点击“开始解读”运行 pipeline。
- 查看公司画像、业务模式、产品服务、收入来源、财务摘要、风险因素、募资用途、尽调问题和人工复核提示。
- 下载 Markdown 报告。
- 可选推送飞书机器人。

## CLI 运行方式

```bash
python scripts/test_api.py
python scripts/test_feishu.py
python scripts/run_pipeline.py --pdf data/example_prospectus.pdf --company "示例公司"
```

如果配置了飞书 Webhook，可加：

```bash
python scripts/run_pipeline.py --pdf data/example_prospectus.pdf --company "示例公司" --push-feishu
```

## 飞书机器人配置说明

1. 在飞书群中添加自定义机器人。
2. 复制 Webhook URL。
3. 写入 `.env` 的 `FEISHU_WEBHOOK_URL`。
4. 运行 `python scripts/test_feishu.py` 测试。

如果未配置 Webhook，程序会提示“未配置飞书 Webhook，已跳过推送”，不会崩溃。

## 输出文件说明

- `outputs/extracted_text.txt`：PDF 提取文本。
- `outputs/prospectus_analysis.json`：结构化抽取结果。
- `outputs/prospectus_report.md`：Markdown 解读报告。
- `outputs/prospectus_summary.csv`：摘要表格。
- `outputs/feishu_message.txt`：飞书推送摘要。

## 测试方式

- API 测试：`python scripts/test_api.py`
- 飞书测试：`python scripts/test_feishu.py`
- Pipeline 测试：`python scripts/run_pipeline.py --pdf data/example_prospectus.pdf --company "示例公司"`
- 前端测试：直接打开 `index.html`，访问 Demo、工作流、可靠性、关于项目页面。

## 风险控制

- 只基于上传资料生成，不补充无来源信息。
- 未识别内容标记为“未识别”。
- 模型输出 JSON 缺字段时自动补齐。
- API Key 缺失、Webhook 缺失、PDF 无文本等异常都有友好提示。
- 报告中明确说明 AI 输出需要人工复核。
- 不上传 `.env`、真实 Webhook、真实敏感文件或内部资料。

## 未来拓展方向

后续版本可以扩展到年报、半年报、公告、多公司对比、NotebookLM 核验或 Coze 工作流。
