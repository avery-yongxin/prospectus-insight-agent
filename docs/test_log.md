# 测试日志

## 用例 1：正常招股说明书 PDF

- 测试目标：验证 PDF 提取、LLM 抽取、报告生成和输出文件保存。
- 输入：`data/example_prospectus.pdf`，公司名称“示例公司”。
- 预期结果：生成 `extracted_text.txt`、`prospectus_analysis.json`、`prospectus_report.md`、`prospectus_summary.csv`、`feishu_message.txt`。
- 实际结果占位：待测试后填写。
- 迭代优化措施：若模型输出不稳定，收紧 Prompt 并增加 JSON 解析容错。

## 用例 2：用户只粘贴文本或使用示例文本

- 测试目标：验证静态 Demo 页面交互。
- 输入：Demo 页示例文本。
- 预期结果：页面生成模拟公司画像、业务模式、风险因素、募资用途和飞书摘要。
- 实际结果占位：待测试后填写。
- 迭代优化措施：增加空输入提示和模拟结果边界说明。

## 用例 3：空文件

- 测试目标：验证空 PDF 的异常处理。
- 输入：0 KB PDF 文件。
- 预期结果：提示“PDF 文件为空，请上传有效的招股说明书 PDF”。
- 实际结果占位：待测试后填写。
- 迭代优化措施：在 Streamlit 上传后先检查文件大小。

## 用例 4：扫描版 PDF

- 测试目标：验证无法提取文本时的提示。
- 输入：扫描版招股说明书 PDF。
- 预期结果：提示“未能提取到足够文本。该 PDF 可能是扫描版，请先 OCR 后再上传”。
- 实际结果占位：待测试后填写。
- 迭代优化措施：后续版本可接入 OCR，但当前版本不实现。

## 用例 5：缺少 API Key

- 测试目标：验证未配置 `.env` 时不崩溃。
- 输入：不配置 `LLM_API_KEY` 后运行 pipeline。
- 预期结果：提示复制 `.env.example` 为 `.env` 并填写 API Key。
- 实际结果占位：待测试后填写。
- 迭代优化措施：在 Streamlit 页面和 CLI 中展示一致提示。

## 用例 6：飞书 Webhook 未配置

- 测试目标：验证未配置飞书 Webhook 时的处理。
- 输入：不配置 `FEISHU_WEBHOOK_URL`，运行 `python scripts/test_feishu.py`。
- 预期结果：提示“未配置飞书 Webhook，已跳过推送”，退出码为 0。
- 实际结果占位：待测试后填写。
- 迭代优化措施：飞书推送作为可选功能，不影响报告生成。

## 用例 7：LLM 输出字段缺失或 JSON 格式异常

- 测试目标：验证模型返回异常时的容错能力。
- 输入：模拟模型缺少字段或返回非 JSON 文本。
- 预期结果：缺字段填“未识别”；非 JSON 返回清晰错误提示。
- 实际结果占位：待测试后填写。
- 迭代优化措施：加强 Prompt 中严格 JSON 约束，保留正则提取 JSON 的 fallback。

## 详细报告结构验证

- 测试目标：验证新版嵌套 JSON schema、详细 Markdown 报告、飞书摘要和 Streamlit 展示入口。
- 验证命令：`PYTHONPATH=. python3 -m unittest tests.test_detailed_schema tests.test_detailed_report_generator tests.test_feishu_message -v`
- 实际结果：通过，6 个测试均为 OK。
- 验证命令：`python3 -m py_compile agent/pipeline.py agent/report_generator.py agent/feishu_bot.py agent/app.py agent/llm_client.py agent/pdf_parser.py`
- 实际结果：通过，无语法错误输出。
- 样例命令：`python3 scripts/run_pipeline.py --pdf ../英矽智能招股说明书.pdf --company "英矽智能"`
- 实际结果：当前环境缺少 `pymupdf`，且没有可用 `pip` 模块，端到端 PDF pipeline 未在本环境完成；代码已在缺少依赖时返回友好提示。
- 检查重点：嵌套 JSON 字段、Markdown 九大章节、未识别标注、简体中文输出、无投资建议表述。
