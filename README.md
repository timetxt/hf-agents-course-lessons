# 🤖 Local LLM Agents Course Examples | 本地 LLM 智能体课程示例

This repository contains reproductions of examples from the [Hugging Face AI Agents Course](https://huggingface.co/learn/agents-course/zh-CN/), modified to use local LLM models instead of the HuggingFace Inference API.

本仓库包含 [Hugging Face AI 智能体课程](https://huggingface.co/learn/agents-course/zh-CN/) 中示例的复现，经过修改以使用本地 LLM 模型而非 HuggingFace 推理 API。

## 🎯 Purpose | 目的

The original Hugging Face Agents Course provides excellent learning materials for understanding and building AI agents. However, using the HuggingFace Inference API comes with billing constraints that may limit learning opportunities. This repository aims to:

原始的 Hugging Face 智能体课程提供了优秀的学习材料，用于理解和构建 AI 智能体。然而，使用 HuggingFace 推理 API 会带来计费限制，可能会限制学习机会。本仓库旨在：

- Reproduce all course examples using local LLM models | 使用本地 LLM 模型复现所有课程示例
- Provide a billing-free learning experience | 提供免费的学习体验
- Allow learners to experiment without worrying about usage limits | 让学习者无需担心使用限制即可进行实验
- Demonstrate how to adapt agent frameworks to work with locally deployed models | 演示如何调整智能体框架以适配本地部署的模型

## 🧠 Local Models vs. API | 本地模型与 API 对比

| Aspect 方面 | HF Inference API 推理 API | Local LLM Approach 本地 LLM 方法 |
|--------|-----------------|-------------------|
| Cost 成本 | Pay-per-use billing 按使用量计费 | Free (after model download) 免费（下载模型后） |
| Setup 设置 | Simple API calls 简单的 API 调用 | Requires local model setup 需要本地模型设置 |
| Performance 性能 | High (cloud infrastructure) 高（云基础设施） | Depends on local hardware 取决于本地硬件 |
| Flexibility 灵活性 | Limited to available models 限于可用模型 | Any compatible model 任何兼容的模型 |
| Privacy 隐私 | Data sent to external servers 数据发送到外部服务器 | All processing stays local 所有处理都在本地 |

## 🛠️ Getting Started | 入门指南

### Prerequisites | 前提条件

- Basic knowledge of Python | Python 基础知识
- Basic understanding of LLMs (Large Language Models) | 对大型语言模型 (LLMs) 的基本理解
- A computer with sufficient resources to run local LLM models | 具有足够资源运行本地 LLM 模型的计算机
  - Minimum 16GB RAM recommended | 建议至少 16GB 内存
  - GPU with at least 8GB VRAM for better performance | 为获得更好性能，建议 GPU 至少有 8GB 显存

### Installation | 安装

```bash
# Clone this repository | 克隆此仓库
git clone https://github.com/timetxt/hf-agents-course-lessons.git
cd hf-agents-course-lessons

# Install dependencies | 安装依赖
pip install -r ./<course_section_folder>/requirements.txt
```

## 📚 Course Structure | 课程结构

This repository follows the structure of the Hugging Face Agents Course:

本仓库遵循 Hugging Face 智能体课程的结构：

1. **Agent Fundamentals | 智能体基础**: Understanding tools, thoughts, actions, observations, and their formats | 理解工具、思考、行动、观察及其格式
2. **Frameworks | 框架**: Implementing fundamentals in popular libraries like smolagents, LangGraph, LlamaIndex | 在流行库（如 smolagents、LangGraph、LlamaIndex）中实现基础功能
3. **Use Cases | 用例**: Building real-life applications with agents | 使用智能体构建实际应用
4. **Assignments | 作业**: Practical exercises to test your understanding | 测试理解的实践练习

Each section contains examples adapted to work with local LLM models.

每个部分都包含适用于本地 LLM 模型的示例。

## 🔧 Supported Local Models | 支持的本地模型

This repository supports Qwen2.5 local LLM models, including:

本仓库支持 Qwen2.5 本地 LLM 模型，包括：

- [Qwen2.5-Coder-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct)


## 📝 Examples | 示例

Each example in this repository includes:

本仓库中的每个示例包括：

- Complete source code | 完整源代码
- Instructions for running with local models | 使用本地模型运行的说明
- Explanations of how the example works | 示例工作原理的解释
- Comparison with the original HF Inference API approach | 与原始 HF 推理 API 方法的比较


## 🤝 Contributing | 贡献

Contributions are welcome! If you'd like to improve existing examples or add new ones, please:

欢迎贡献！如果您想改进现有示例或添加新示例，请：

1. Fork the repository | 复刻仓库
2. Create a new branch for your feature | 为您的功能创建新分支
3. Add your changes | 添加您的更改
4. Submit a pull request | 提交拉取请求

## 📄 License | 许可证

This project is licensed under the MIT License - see the LICENSE file for details.

本项目采用 MIT 许可证 - 详情请参阅 LICENSE 文件。

## 🙏 Acknowledgments | 致谢

- The Hugging Face team for creating the original [AI Agents Course](https://huggingface.co/learn/agents-course/) | 感谢 Hugging Face 团队创建原始 [AI 智能体课程](https://huggingface.co/learn/agents-course/)
- Contributors to the various agent frameworks used in this repository | 感谢本仓库中使用的各种智能体框架的贡献者
- The open-source LLM community for making powerful models accessible locally | 感谢开源 LLM 社区使强大的模型可在本地访问

## 📞 Contact | 联系方式

If you have any questions or suggestions, please open an issue in this repository.

如果您有任何问题或建议，请在本仓库中开启一个 issue。

---

Happy learning with local LLM agents! 🚀 

祝您使用本地 LLM 智能体学习愉快！🚀 