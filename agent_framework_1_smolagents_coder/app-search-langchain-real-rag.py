import os


from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from smolagents import Tool
from langchain_community.retrievers import BM25Retriever
from smolagents import CodeAgent, TransformersModel


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
model_id = 'Qwen/Qwen2.5-Coder-7B-Instruct'
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

class PartyPlanningRetrieverTool(Tool):
    name = "party_planning_retriever"
    description = "Uses semantic search to retrieve relevant party planning ideas for Alfred’s superhero-themed party at Wayne Manor."
    inputs = {
        "query": {
            "type": "string",
            "description": "The query to perform. This should be a query related to party planning or superhero themes.",
        }
    }
    output_type = "string"

    def __init__(self, docs, **kwargs):
        super().__init__(**kwargs)
        self.retriever = BM25Retriever.from_documents(
            docs, k=5  # 检索前 5 个文档
        )

    def forward(self, query: str) -> str:
        ## why below line made the llm model to pass the query as a string?
        print(type(query)) 
        assert isinstance(query, str), "Your search query must be a string"

        docs = self.retriever.invoke(
            query,
        )
        print(f'docs: {docs}')
        
        return "\nRetrieved ideas:\n" + "".join(
            [
                f"\n\n===== Idea {str(i)} =====\n" + doc.page_content
                for i, doc in enumerate(docs)
            ]
        )
        
# 模拟派对策划知识库
party_ideas = [
    {"text": "A superhero-themed masquerade ball with luxury decor, including gold accents and velvet curtains.", "source": "Party Ideas 1"},
    {"text": "Hire a professional DJ who can play themed music  for superheroes like Batman and Wonder Woman.", "source": "Entertainment Ideas"},
    {"text": "For catering, serve dishes named after superheroes, like 'The Hulk's Green Smoothie' and 'Iron Man's Power Steak.'", "source": "Catering Ideas"},
    {"text": "Decorate with iconic superhero logos and projections of Gotham and other superhero cities around the venue.", "source": "Decoration Ideas"},
    {"text": "Interactive experiences with VR where guests can engage in superhero simulations or compete in themed games.", "source": "Entertainment Ideas"}
]

source_docs = [
    Document(page_content=doc["text"], metadata={"source": doc["source"]})
    for doc in party_ideas
]

# 分割文档以提高搜索效率
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    add_start_index=True,
    strip_whitespace=True,
    separators=["\n\n", "\n", ".", " ", ""],
)
docs_processed = text_splitter.split_documents(source_docs)

# 创建检索工具
party_planning_retriever = PartyPlanningRetrieverTool(docs_processed)


def search_wth_rag(query):
    
    agent = CodeAgent(tools=[party_planning_retriever]
                         , model=model
                         , max_steps=8
                         , verbosity_level=1
                         , grammar=None
                         , planning_interval=None
                         , name="party_planning_agent"
                         , description="An agent that helps plan parties by searching with internal documents. You will provide final answer to user based on search results. The final answer should be provide line by line. IMPORTANT: When using the party_planning_retriever tool, pass the search query directly as a string, not as a dictionary." ####  the description is important, it is the key to the agent's success. however, the GPU memory is a limitation, so sometimes the agent will not be able to provide the final answer.
                         )
    return agent.run(query)

if __name__ == "__main__":
    print(f'{search_wth_rag("Find ideas for a luxury superhero-themed party, including entertainment, catering, and decoration options.")}')
    
