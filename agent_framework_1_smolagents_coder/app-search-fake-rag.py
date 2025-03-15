import os

from smolagents import CodeAgent, DuckDuckGoSearchTool, TransformersModel


# Get current directory path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


from transformers import BitsAndBytesConfig
import torch
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ModelLoader')

# Set PyTorch memory management environment variables
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

# Configure 4-bit quantization for memory efficiency
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
)

# Use a smaller model to reduce memory requirements
model_id = 'Qwen/Qwen2.5-Coder-3B-Instruct'
logger.info(f"Loading model {model_id}...")

# Try to clear CUDA cache before loading model
torch.cuda.empty_cache()

try:
    # Let TransformersModel handle model loading directly
    model = TransformersModel(
        model_id=model_id,
        device_map="auto",
        torch_dtype=torch.float16,
        trust_remote_code=True,
        max_new_tokens=512,
        kwargs={
            "quantization_config": quantization_config,
            "low_cpu_mem_usage": True
        }
    )
    
    logger.info("Model loaded successfully!")
    
except Exception as e:
    logger.error(f"Error loading model: {e}")
    raise

# 初始化搜索工具
search_tool = DuckDuckGoSearchTool()

def search_web_agent(query):
    agent = CodeAgent(tools=[search_tool]
                         , model=model
                         , max_steps=5
                         , verbosity_level=2
                         , grammar=None
                         , planning_interval=None
                         , name="party_planning_agent"
                         , description="An agent that helps plan parties by searching for information and provide the information to the user as final answer" #### initially I did not include string "as final answer" in the description, so the agent did not provide the information to the user as final answer, this caused the agent to not provide valid information to the user as final answer. This is an important lesson to learn.
                         )
    return agent.run(query)

if __name__ == "__main__":
    print(f'{search_web_agent("Search for luxury superhero-themed party ideas, including decorations, entertainment, and catering.")}')
    
