# 🤖 Local LLM Agents Course Examples | 本地 LLM 智能体课程示例

<div align="center">
  <a href="#english-content">English</a> | <a href="#chinese-content">中文</a>
</div>

<a id="english-content"></a>
## English Content

This repository contains reproductions of examples from the [Hugging Face AI Agents Course](https://huggingface.co/learn/agents-course/zh-CN/), modified to use local LLM models instead of the HuggingFace Inference API.

### 🎯 Purpose

The original Hugging Face Agents Course provides excellent learning materials for understanding and building AI agents. However, using the HuggingFace Inference API comes with billing constraints that may limit learning opportunities. This repository aims to:

- Reproduce all course examples using local LLM models
- Provide a billing-free learning experience
- Allow learners to experiment without worrying about usage limits
- Demonstrate how to adapt agent frameworks to work with locally deployed models

### 🧠 Local Models vs. API

| Aspect | HF Inference API | Local LLM Approach |
|--------|-----------------|-------------------|
| Cost | Pay-per-use billing | Free (after model download) |
| Setup | Simple API calls | Requires local model setup |
| Performance | High (cloud infrastructure) | Depends on local hardware |
| Flexibility | Limited to available models | Any compatible model |
| Privacy | Data sent to external servers | All processing stays local |

### 🛠️ Getting Started

#### Prerequisites

- Basic knowledge of Python
- Basic understanding of LLMs (Large Language Models)
- A computer with sufficient resources to run local LLM models
  - Minimum 16GB RAM recommended
  - GPU with at least 8GB VRAM for better performance

#### Installation

```bash
# Clone this repository
git clone https://github.com/timetxt/hf-agents-course-lessons.git
cd hf-agents-course-lessons

# Install dependencies
pip install -r ./<course_section_folder>/requirements.txt
```

### 📚 Course Structure

This repository follows the structure of the Hugging Face Agents Course:

1. **Agent Fundamentals**: Understanding tools, thoughts, actions, observations, and their formats
2. **Frameworks**: Implementing fundamentals in popular libraries like smolagents, LangGraph, LlamaIndex
3. **Use Cases**: Building real-life applications with agents
4. **Assignments**: Practical exercises to test your understanding

Each section contains examples adapted to work with local LLM models.

### 🔧 Supported Local Models

This repository supports Qwen2.5 local LLM models, including:

- [Qwen2.5-Coder-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct)

### 📝 Examples

Each example in this repository includes:

- Complete source code
- Instructions for running with local models
- Explanations of how the example works
- Comparison with the original HF Inference API approach

### 🤝 Contributing

Contributions are welcome! If you'd like to improve existing examples or add new ones, please:

1. Fork the repository
2. Create a new branch for your feature
3. Add your changes
4. Submit a pull request

### 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

### 🙏 Acknowledgments

- The Hugging Face team for creating the original [AI Agents Course](https://huggingface.co/learn/agents-course/)
- Contributors to the various agent frameworks used in this repository
- The open-source LLM community for making powerful models accessible locally

### 📞 Contact

If you have any questions or suggestions, please open an issue in this repository.

Happy learning with local LLM agents! 🚀 

---

<a id="chinese-content"></a>
## 中文内容

本仓库包含 [Hugging Face AI 智能体课程](https://huggingface.co/learn/agents-course/zh-CN/) 中示例的复现，经过修改以使用本地 LLM 模型而非 HuggingFace 推理 API。

### 🎯 目的

原始的 Hugging Face 智能体课程提供了优秀的学习材料，用于理解和构建 AI 智能体。然而，使用 HuggingFace 推理 API 会带来计费限制，可能会限制学习机会。本仓库旨在：

- 使用本地 LLM 模型复现所有课程示例
- 提供免费的学习体验
- 让学习者无需担心使用限制即可进行实验
- 演示如何调整智能体框架以适配本地部署的模型

### 🧠 本地模型与 API 对比

| 方面 | HF 推理 API | 本地 LLM 方法 |
|--------|-----------------|-------------------|
| 成本 | 按使用量计费 | 免费（下载模型后） |
| 设置 | 简单的 API 调用 | 需要本地模型设置 |
| 性能 | 高（云基础设施） | 取决于本地硬件 |
| 灵活性 | 限于可用模型 | 任何兼容的模型 |
| 隐私 | 数据发送到外部服务器 | 所有处理都在本地 |

### 🛠️ 入门指南

#### 前提条件

- Python 基础知识
- 对大型语言模型 (LLMs) 的基本理解
- 具有足够资源运行本地 LLM 模型的计算机
  - 建议至少 16GB 内存
  - 为获得更好性能，建议 GPU 至少有 8GB 显存

#### 安装

```bash
# 克隆此仓库
git clone https://github.com/timetxt/hf-agents-course-lessons.git
cd hf-agents-course-lessons

# 安装依赖
pip install -r ./<course_section_folder>/requirements.txt
```

### 📚 课程结构

本仓库遵循 Hugging Face 智能体课程的结构：

1. **智能体基础**: 理解工具、思考、行动、观察及其格式
2. **框架**: 在流行库（如 smolagents、LangGraph、LlamaIndex）中实现基础功能
3. **用例**: 使用智能体构建实际应用
4. **作业**: 测试理解的实践练习

每个部分都包含适用于本地 LLM 模型的示例。

### 🔧 支持的本地模型

本仓库支持 Qwen2.5 本地 LLM 模型，包括：

- [Qwen2.5-Coder-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct)

### 📝 示例

本仓库中的每个示例包括：

- 完整源代码
- 使用本地模型运行的说明
- 示例工作原理的解释
- 与原始 HF 推理 API 方法的比较

### 🤝 贡献

欢迎贡献！如果您想改进现有示例或添加新示例，请：

1. 复刻仓库
2. 为您的功能创建新分支
3. 添加您的更改
4. 提交拉取请求

### 📄 许可证

本项目采用 MIT 许可证 - 详情请参阅 LICENSE 文件。

### 🙏 致谢

- 感谢 Hugging Face 团队创建原始 [AI 智能体课程](https://huggingface.co/learn/agents-course/)
- 感谢本仓库中使用的各种智能体框架的贡献者
- 感谢开源 LLM 社区使强大的模型可在本地访问

### 📞 联系方式

如果您有任何问题或建议，请在本仓库中开启一个 issue。

祝您使用本地 LLM 智能体学习愉快！🚀 