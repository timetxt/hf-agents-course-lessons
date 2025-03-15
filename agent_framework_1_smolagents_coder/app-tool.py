import yaml
import os
from smolagents import GradioUI, CodeAgent, HfApiModel, TransformersModel

from smolagents import ToolCallingAgent, DuckDuckGoSearchTool, TransformersModel



# Get current directory path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

from tools.web_search import DuckDuckGoSearchTool as WebSearch
from tools.visit_webpage import VisitWebpageTool as VisitWebpage
from tools.suggest_menu import SimpleTool as SuggestMenu
from tools.catering_service_tool import SimpleTool as CateringServiceTool
from tools.superhero_party_theme_generator import SuperheroPartyThemeTool as SuperheroPartyThemeGenerator
from tools.final_answer import FinalAnswerTool as FinalAnswer



# model = HfApiModel(
# model_id='Qwen/Qwen2.5-Coder-32B-Instruct',
# provider=None,
# )

from transformers import BitsAndBytesConfig, AutoModelForCausalLM, AutoTokenizer
import torch
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('ModelLoader')

# Set PyTorch memory management environment variables
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

# Set cache directory to local .cache folder
os.environ["HF_HOME"] = os.path.join(os.getcwd(), ".cache", "huggingface")

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

# web_search = WebSearch()
# visit_webpage = VisitWebpage()
# suggest_menu = SuggestMenu()
# catering_service_tool = CateringServiceTool()
# superhero_party_theme_generator = SuperheroPartyThemeGenerator()
# final_answer = FinalAnswer()


# with open(os.path.join(CURRENT_DIR, "prompts.yaml"), 'r') as stream:
    prompt_templates = yaml.safe_load(stream)
    

agent = ToolCallingAgent(tools=[DuckDuckGoSearchTool()]
                         , model=model
                         , max_steps=10
                         , verbosity_level=2
                         , grammar=None
                         , planning_interval=None
                         , name="party_planning_agent"
                         , description="An agent that helps plan parties by searching for information, suggesting menus, and generating party themes."
                         )

if __name__ == "__main__":
    agent.run("Search for the best music recommendations for a party at the Wayne's mansion.")

# agent = CodeAgent(
#     model=model,
#     tools=[web_search, visit_webpage, suggest_menu, catering_service_tool, superhero_party_theme_generator],
#     managed_agents=[],
#     max_steps=10,
#     verbosity_level=2,
#     grammar=None,
#     planning_interval=None,
#     name="party_planning_agent",
#     description="An agent that helps plan parties by searching for information, suggesting menus, and generating party themes.",
#     prompt_templates=prompt_templates
# )
# if __name__ == "__main__":
#     GradioUI(agent).launch(share=False)
