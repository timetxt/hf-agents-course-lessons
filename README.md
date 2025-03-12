# 🤖 Local LLM Agents Course Examples

This repository contains reproductions of examples from the [Hugging Face AI Agents Course](https://huggingface.co/learn/agents-course/zh-CN/), modified to use local LLM models instead of the HuggingFace Inference API.

## 🎯 Purpose

The original Hugging Face Agents Course provides excellent learning materials for understanding and building AI agents. However, using the HuggingFace Inference API comes with billing constraints that may limit learning opportunities. This repository aims to:

- Reproduce all course examples using local LLM models
- Provide a billing-free learning experience
- Allow learners to experiment without worrying about usage limits
- Demonstrate how to adapt agent frameworks to work with locally deployed models

## 🧠 Local Models vs. API

| Aspect | HF Inference API | Local LLM Approach |
|--------|-----------------|-------------------|
| Cost | Pay-per-use billing | Free (after model download) |
| Setup | Simple API calls | Requires local model setup |
| Performance | High (cloud infrastructure) | Depends on local hardware |
| Flexibility | Limited to available models | Any compatible model |
| Privacy | Data sent to external servers | All processing stays local |

## 🛠️ Getting Started

### Prerequisites

- Basic knowledge of Python
- Basic understanding of LLMs (Large Language Models)
- A computer with sufficient resources to run local LLM models
  - Minimum 16GB RAM recommended
  - GPU with at least 8GB VRAM for better performance

### Installation

```bash
# Clone this repository
git clone https://github.com/yourusername/ai-agent.git
cd ai-agent

# Install dependencies
pip install -r requirements.txt
```

## 📚 Course Structure

This repository follows the structure of the Hugging Face Agents Course:

1. **Agent Fundamentals**: Understanding tools, thoughts, actions, observations, and their formats
2. **Frameworks**: Implementing fundamentals in popular libraries like smolagents, LangGraph, LlamaIndex
3. **Use Cases**: Building real-life applications with agents
4. **Assignments**: Practical exercises to test your understanding

Each section contains examples adapted to work with local LLM models.

## 🔧 Supported Local Models

This repository supports various local LLM models, including:

- [Qwen2.5-Coder-7B-Instruct](https://huggingface.co/Qwen/Qwen2.5-7B-Instruct)
- [Llama 3](https://huggingface.co/meta-llama)
- [Mistral](https://huggingface.co/mistralai)
- Other compatible models that can be run locally

## 📝 Examples

Each example in this repository includes:

- Complete source code
- Instructions for running with local models
- Explanations of how the example works
- Comparison with the original HF Inference API approach

## 🤝 Contributing

Contributions are welcome! If you'd like to improve existing examples or add new ones, please:

1. Fork the repository
2. Create a new branch for your feature
3. Add your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- The Hugging Face team for creating the original [AI Agents Course](https://huggingface.co/learn/agents-course/)
- Contributors to the various agent frameworks used in this repository
- The open-source LLM community for making powerful models accessible locally

## 📞 Contact

If you have any questions or suggestions, please open an issue in this repository.

---

Happy learning with local LLM agents! 🚀 