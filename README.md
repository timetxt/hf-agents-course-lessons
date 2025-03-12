# 🤖 Local LLM Agents Course Examples | 本地 LLM 智能体课程示例

<div align="center">
  <button id="lang-en" onclick="switchLanguage('en')" style="background-color: #4CAF50; color: white; padding: 10px 20px; margin: 5px; border: none; border-radius: 4px; cursor: pointer;">English</button>
  <button id="lang-zh" onclick="switchLanguage('zh')" style="background-color: #008CBA; color: white; padding: 10px 20px; margin: 5px; border: none; border-radius: 4px; cursor: pointer;">中文</button>
</div>

<div class="lang-en">
This repository contains reproductions of examples from the <a href="https://huggingface.co/learn/agents-course/zh-CN/">Hugging Face AI Agents Course</a>, modified to use local LLM models instead of the HuggingFace Inference API.
</div>

<div class="lang-zh" style="display: none;">
本仓库包含 <a href="https://huggingface.co/learn/agents-course/zh-CN/">Hugging Face AI 智能体课程</a> 中示例的复现，经过修改以使用本地 LLM 模型而非 HuggingFace 推理 API。
</div>

## 🎯 <span class="lang-en">Purpose</span><span class="lang-zh" style="display: none;">目的</span>

<div class="lang-en">
The original Hugging Face Agents Course provides excellent learning materials for understanding and building AI agents. However, using the HuggingFace Inference API comes with billing constraints that may limit learning opportunities. This repository aims to:

- Reproduce all course examples using local LLM models
- Provide a billing-free learning experience
- Allow learners to experiment without worrying about usage limits
- Demonstrate how to adapt agent frameworks to work with locally deployed models
</div>

<div class="lang-zh" style="display: none;">
原始的 Hugging Face 智能体课程提供了优秀的学习材料，用于理解和构建 AI 智能体。然而，使用 HuggingFace 推理 API 会带来计费限制，可能会限制学习机会。本仓库旨在：

- 使用本地 LLM 模型复现所有课程示例
- 提供免费的学习体验
- 让学习者无需担心使用限制即可进行实验
- 演示如何调整智能体框架以适配本地部署的模型
</div>

## 🧠 <span class="lang-en">Local Models vs. API</span><span class="lang-zh" style="display: none;">本地模型与 API 对比</span>

<div class="lang-en">
| Aspect | HF Inference API | Local LLM Approach |
|--------|-----------------|-------------------|
| Cost | Pay-per-use billing | Free (after model download) |
| Setup | Simple API calls | Requires local model setup |
| Performance | High (cloud infrastructure) | Depends on local hardware |
| Flexibility | Limited to available models | Any compatible model |
| Privacy | Data sent to external servers | All processing stays local |
</div>

<div class="lang-zh" style="display: none;">
| 方面 | HF 推理 API | 本地 LLM 方法 |
|--------|-----------------|-------------------|
| 成本 | 按使用量计费 | 免费（下载模型后） |
| 设置 | 简单的 API 调用 | 需要本地模型设置 |
| 性能 | 高（云基础设施） | 取决于本地硬件 |
| 灵活性 | 限于可用模型 | 任何兼容的模型 |
| 隐私 | 数据发送到外部服务器 | 所有处理都在本地 |
</div>

## 🛠️ <span class="lang-en">Getting Started</span><span class="lang-zh" style="display: none;">入门指南</span>

### <span class="lang-en">Prerequisites</span><span class="lang-zh" style="display: none;">前提条件</span>

<div class="lang-en">
- Basic knowledge of Python
- Basic understanding of LLMs (Large Language Models)
- A computer with sufficient resources to run local LLM models
  - Minimum 16GB RAM recommended
  - GPU with at least 8GB VRAM for better performance
</div>

<div class="lang-zh" style="display: none;">
- Python 基础知识
- 对大型语言模型 (LLMs) 的基本理解
- 具有足够资源运行本地 LLM 模型的计算机
  - 建议至少 16GB 内存
  - 为获得更好性能，建议 GPU 至少有 8GB 显存
</div>

### <span class="lang-en">Installation</span><span class="lang-zh" style="display: none;">安装</span>

```bash
# Clone this repository | 克隆此仓库
git clone https://github.com/timetxt/hf-agents-course-lessons.git
cd hf-agents-course-lessons

# Install dependencies | 安装依赖
pip install -r ./<course_section_folder>/requirements.txt
```

## 📚 <span class="lang-en">Course Structure</span><span class="lang-zh" style="display: none;">课程结构</span>

<div class="lang-en">
This repository follows the structure of the Hugging Face Agents Course:

1. **Agent Fundamentals**: Understanding tools, thoughts, actions, observations, and their formats
2. **Frameworks**: Implementing fundamentals in popular libraries like smolagents, LangGraph, LlamaIndex
3. **Use Cases**: Building real-life applications with agents
4. **Assignments**: Practical exercises to test your understanding

Each section contains examples adapted to work with local LLM models.
</div>

<div class="lang-zh" style="display: none;">
本仓库遵循 Hugging Face 智能体课程的结构：

1. **智能体基础**: 理解工具、思考、行动、观察及其格式
2. **框架**: 在流行库（如 smolagents、LangGraph、LlamaIndex）中实现基础功能
3. **用例**: 使用智能体构建实际应用
4. **作业**: 测试理解的实践练习

每个部分都包含适用于本地 LLM 模型的示例。
</div>

## 🔧 <span class="lang-en">Supported Local Models</span><span class="lang-zh" style="display: none;">支持的本地模型</span>

<div class="lang-en">
This repository supports Qwen2.5 local LLM models, including:

- [Qwen2.5-Coder-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct)
</div>

<div class="lang-zh" style="display: none;">
本仓库支持 Qwen2.5 本地 LLM 模型，包括：

- [Qwen2.5-Coder-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct)
</div>

## 📝 <span class="lang-en">Examples</span><span class="lang-zh" style="display: none;">示例</span>

<div class="lang-en">
Each example in this repository includes:

- Complete source code
- Instructions for running with local models
- Explanations of how the example works
- Comparison with the original HF Inference API approach
</div>

<div class="lang-zh" style="display: none;">
本仓库中的每个示例包括：

- 完整源代码
- 使用本地模型运行的说明
- 示例工作原理的解释
- 与原始 HF 推理 API 方法的比较
</div>

## 🤝 <span class="lang-en">Contributing</span><span class="lang-zh" style="display: none;">贡献</span>

<div class="lang-en">
Contributions are welcome! If you'd like to improve existing examples or add new ones, please:

1. Fork the repository
2. Create a new branch for your feature
3. Add your changes
4. Submit a pull request
</div>

<div class="lang-zh" style="display: none;">
欢迎贡献！如果您想改进现有示例或添加新示例，请：

1. 复刻仓库
2. 为您的功能创建新分支
3. 添加您的更改
4. 提交拉取请求
</div>

## 📄 <span class="lang-en">License</span><span class="lang-zh" style="display: none;">许可证</span>

<div class="lang-en">
This project is licensed under the MIT License - see the LICENSE file for details.
</div>

<div class="lang-zh" style="display: none;">
本项目采用 MIT 许可证 - 详情请参阅 LICENSE 文件。
</div>

## 🙏 <span class="lang-en">Acknowledgments</span><span class="lang-zh" style="display: none;">致谢</span>

<div class="lang-en">
- The Hugging Face team for creating the original [AI Agents Course](https://huggingface.co/learn/agents-course/)
- Contributors to the various agent frameworks used in this repository
- The open-source LLM community for making powerful models accessible locally
</div>

<div class="lang-zh" style="display: none;">
- 感谢 Hugging Face 团队创建原始 [AI 智能体课程](https://huggingface.co/learn/agents-course/)
- 感谢本仓库中使用的各种智能体框架的贡献者
- 感谢开源 LLM 社区使强大的模型可在本地访问
</div>

## 📞 <span class="lang-en">Contact</span><span class="lang-zh" style="display: none;">联系方式</span>

<div class="lang-en">
If you have any questions or suggestions, please open an issue in this repository.
</div>

<div class="lang-zh" style="display: none;">
如果您有任何问题或建议，请在本仓库中开启一个 issue。
</div>

---

<div class="lang-en">
Happy learning with local LLM agents! 🚀 
</div>

<div class="lang-zh" style="display: none;">
祝您使用本地 LLM 智能体学习愉快！🚀 
</div>

<script>
function switchLanguage(lang) {
  // Hide all language elements
  var enElements = document.getElementsByClassName('lang-en');
  var zhElements = document.getElementsByClassName('lang-zh');
  
  if (lang === 'en') {
    // Show English, hide Chinese
    for (var i = 0; i < enElements.length; i++) {
      enElements[i].style.display = '';
    }
    for (var i = 0; i < zhElements.length; i++) {
      zhElements[i].style.display = 'none';
    }
    // Highlight the English button
    document.getElementById('lang-en').style.backgroundColor = '#45a049';
    document.getElementById('lang-zh').style.backgroundColor = '#008CBA';
  } else {
    // Show Chinese, hide English
    for (var i = 0; i < enElements.length; i++) {
      enElements[i].style.display = 'none';
    }
    for (var i = 0; i < zhElements.length; i++) {
      zhElements[i].style.display = '';
    }
    // Highlight the Chinese button
    document.getElementById('lang-en').style.backgroundColor = '#4CAF50';
    document.getElementById('lang-zh').style.backgroundColor = '#007B9A';
  }
}

// Initialize with English by default
document.addEventListener('DOMContentLoaded', function() {
  switchLanguage('en');
});
</script> 