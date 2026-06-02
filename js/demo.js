(function () {
  const sampleBtn = document.getElementById("sampleBtn");
  const analyzeBtn = document.getElementById("analyzeBtn");
  const input = document.getElementById("prospectusInput");
  const resultPanel = document.getElementById("resultPanel");
  const notice = document.getElementById("inputNotice");

  const sampleText = [
    "示例科技股份有限公司是一家专注于产业数字化软件与数据服务的企业。",
    "公司主要产品包括数据治理平台、行业分析系统和企业协同工具，收入来源包括软件授权、技术服务和持续运维服务。",
    "报告期内，公司持续投入研发，面向制造、能源和公共服务等客户提供解决方案。",
    "风险因素包括客户集中度较高、研发投入持续增加、行业竞争加剧以及项目交付周期不确定。",
    "本次募集资金拟用于智能数据平台升级项目、研发中心建设项目和补充流动资金。"
  ].join("\n\n");

  function section(title, body) {
    return `<div class="result-section"><h3>${title}</h3><p>${body}</p></div>`;
  }

  function renderResult(text) {
    const lengthHint = text.length > 260 ? "文本包含较多业务、风险或募资信息，适合进入完整智能体流程。" : "文本较短，结果仅作为页面交互演示。";
    resultPanel.innerHTML = [
      section("公司画像", "示例科技股份有限公司，聚焦产业数字化软件与数据服务，面向企业客户提供平台型解决方案。"),
      section("业务模式", "以软件授权、技术服务、持续运维为主要模式，结合项目交付和客户长期服务形成收入。"),
      section("核心财务摘要", "静态演示不识别真实财务数据。真实应用会要求模型只基于招股说明书原文提取，不编造数字。"),
      section("风险因素", "客户集中度、研发投入、行业竞争、项目交付周期等风险需要结合原文进一步核验。"),
      section("募资用途", "模拟识别为平台升级、研发中心建设和补充流动资金。"),
      section("尽调问题", "1. 主要客户收入占比是否稳定？<br>2. 研发投入与产品商业化进度是否匹配？<br>3. 募资项目与现有业务的协同关系如何？"),
      section("飞书推送摘要", "公司：示例科技股份有限公司；行业：产业数字化软件；主要风险：客户集中度、竞争加剧、交付周期；报告路径：outputs/prospectus_report.md。"),
      section("演示提示", lengthHint)
    ].join("");
  }

  if (sampleBtn && input) {
    sampleBtn.addEventListener("click", () => {
      input.value = sampleText;
      notice.textContent = "已填入虚构示例文本，不包含真实敏感资料。";
    });
  }

  if (analyzeBtn && input && resultPanel) {
    analyzeBtn.addEventListener("click", () => {
      const text = input.value.trim();
      if (!text) {
        resultPanel.innerHTML = '<div class="empty-state">请先粘贴文本，或点击“使用示例文本”。</div>';
        notice.textContent = "没有检测到输入内容。";
        return;
      }
      notice.textContent = "已生成静态模拟结果。真实 AI 解读请运行 Streamlit 应用。";
      renderResult(text);
    });
  }
})();
