import os
import torch
import logging
import traceback
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from threading import Thread
from typing import Dict, List, Optional, Union, Any

# Configure logging
logging.basicConfig(level=logging.WARNING, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('LocalModel')

class LocalModel:
    """
    A model class that loads and runs models locally using the transformers library.
    Compatible with the smolagents library.
    """
    
    def __init__(
        self,
        model_id: str,
        max_tokens: int = 2048,
        temperature: float = 0.5,
        device: str = None,
        load_in_8bit: bool = False,
        load_in_4bit: bool = True,
        custom_role_conversions: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize the local model.
        
        Args:
            model_id: The model ID or path to load from HuggingFace or local directory
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature
            device: Device to run the model on ('cuda', 'cpu', etc.). If None, will use CUDA if available
            load_in_8bit: Whether to load the model in 8-bit precision
            load_in_4bit: Whether to load the model in 4-bit precision
            custom_role_conversions: Custom role conversions for chat models
        """
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.custom_role_conversions = custom_role_conversions or {}
        
        self.model_id = model_id
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.load_in_8bit = load_in_8bit
        self.load_in_4bit = load_in_4bit
        
        # Set cache directory to local .cache folder
        os.environ["HF_HOME"] = os.path.join(os.getcwd(), ".cache", "huggingface")
        
        logger.info(f"Loading model {model_id} on {self.device}...")
        self._load_model()
        
    def _load_model(self):
        """Load the model and tokenizer"""
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, trust_remote_code=True)
        
        # Configure quantization parameters
        quantization_config = None
        if self.load_in_4bit:
            from transformers import BitsAndBytesConfig
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_use_double_quant=True,
            )
        elif self.load_in_8bit:
            from transformers import BitsAndBytesConfig
            quantization_config = BitsAndBytesConfig(load_in_8bit=True)
        
        # Load the model with appropriate configuration
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            device_map="auto" if self.device == "cuda" else self.device,
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            trust_remote_code=True,
            quantization_config=quantization_config,
        )
    
    def _format_messages(self, messages: List[Dict[str, str]]) -> str:
        """Format messages for the model"""
        logger.info(f"Formatting messages: {messages}")
        
        # Debug: Check the type of messages
        logger.info(f"Type of messages: {type(messages)}")
        
        # Handle case where messages is a string instead of a list
        if isinstance(messages, str):
            logger.warning(f"Received string instead of list of messages: {messages}")
            # Convert string to proper message format
            return f"User: {messages}\nAssistant: "
        
        # Handle case where messages is a single dict instead of a list
        if isinstance(messages, dict):
            logger.warning(f"Received dict instead of list of messages: {messages}")
            messages = [messages]
        
        # For Qwen models, we'll use their chat template
        if hasattr(self.tokenizer, "apply_chat_template"):
            logger.info("Using tokenizer's chat template")
            try:
                # Convert any non-string content to string before applying template
                processed_messages = []
                for i, message in enumerate(messages):
                    logger.info(f"Processing message {i}: {message} (type: {type(message)})")
                    
                    # Handle case where message is a string
                    if isinstance(message, str):
                        logger.warning(f"Message {i} is a string, not a dict: {message}")
                        processed_message = {"role": "user", "content": message}
                    else:
                        processed_message = message.copy()
                        # Ensure message has content field
                        if "content" not in processed_message:
                            logger.warning(f"Message {i} has no content field: {processed_message}")
                            processed_message["content"] = ""
                        
                        content = processed_message.get("content", "")
                        
                        # Handle complex content structure (list of dicts with 'type' and 'text')
                        if isinstance(content, list):
                            # Extract text from content items
                            extracted_text = []
                            for item in content:
                                if isinstance(item, dict) and "text" in item:
                                    extracted_text.append(item["text"])
                                elif isinstance(item, str):
                                    extracted_text.append(item)
                                else:
                                    extracted_text.append(str(item))
                            
                            # Join extracted text
                            content = "\n".join(extracted_text)
                            logger.info(f"Extracted text from complex content: {content[:100]}...")
                            processed_message["content"] = content
                        elif not isinstance(content, str):
                            # Convert non-string content to string
                            logger.info(f"Converting non-string content to string: {content}")
                            processed_message["content"] = str(content)
                    
                    processed_messages.append(processed_message)
                
                logger.info(f"Processed messages: {processed_messages}")
                formatted_input = self.tokenizer.apply_chat_template(
                    processed_messages, 
                    tokenize=False, 
                    add_generation_prompt=True
                )
                logger.info(f"Formatted input (first 100 chars): {formatted_input[:100]}...")
                return formatted_input
            except Exception as e:
                logger.error(f"Error in apply_chat_template: {e}")
                logger.error(traceback.format_exc())
                # Fall back to simple format
                logger.info("Falling back to simple format due to error")
        
        # Fallback to a simple format if the tokenizer doesn't have a chat template
        logger.info("Using fallback simple format")
        formatted_input = ""
        try:
            for i, message in enumerate(messages):
                logger.info(f"Processing message {i} for simple format: {message} (type: {type(message)})")
                
                # Handle case where message is a string
                if isinstance(message, str):
                    logger.warning(f"Message {i} is a string, not a dict: {message}")
                    formatted_input += f"User: {message}\n"
                    continue
                
                role = message.get("role", "user")
                # Ensure content is always a string
                if "content" not in message:
                    logger.warning(f"Message {i} has no content field: {message}")
                    content = ""
                else:
                    content = message.get("content", "")
                    
                    # Handle complex content structure (list of dicts with 'type' and 'text')
                    if isinstance(content, list):
                        # Extract text from content items
                        extracted_text = []
                        for item in content:
                            if isinstance(item, dict) and "text" in item:
                                extracted_text.append(item["text"])
                            elif isinstance(item, str):
                                extracted_text.append(item)
                            else:
                                extracted_text.append(str(item))
                        
                        # Join extracted text
                        content = "\n".join(extracted_text)
                        logger.info(f"Extracted text from complex content: {content[:100]}...")
                    elif not isinstance(content, str):
                        # Convert non-string content to string
                        logger.info(f"Converting non-string content to string: {content}")
                        content = str(content)
                
                formatted_input += f"{role.capitalize()}: {content}\n"
            
            formatted_input += "Assistant: "
            logger.info(f"Final formatted input (first 100 chars): {formatted_input[:100]}...")
            return formatted_input
        except Exception as e:
            logger.error(f"Error in fallback formatting: {e}")
            logger.error(traceback.format_exc())
            # Last resort fallback
            return "User: Please help me.\nAssistant: "
    
    def generate(
        self, 
        messages: List[Dict[str, str]], 
        stream: bool = False, 
        **kwargs
    ) -> Union[str, Any]:
        """
        Generate a response from the model.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            stream: Whether to stream the response
            **kwargs: Additional arguments to pass to the model
            
        Returns:
            The generated text or a streaming iterator
        """
        try:
            logger.info(f"Generate called with messages: {messages}")
            formatted_input = self._format_messages(messages)
            
            inputs = self.tokenizer(formatted_input, return_tensors="pt").to(self.device)
            
            generation_config = {
                "max_new_tokens": self.max_tokens,
                "temperature": self.temperature,
                "do_sample": self.temperature > 0,
                "pad_token_id": self.tokenizer.eos_token_id,
            }
            
            # Remove unsupported parameters
            if 'stop_sequences' in kwargs:
                kwargs.pop('stop_sequences')
            
            generation_config.update(kwargs)
            
            if stream:
                streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)
                generation_config["streamer"] = streamer
                
                # Start generation in a separate thread
                thread = Thread(
                    target=self.model.generate,
                    kwargs={**inputs, **generation_config}
                )
                thread.start()
                
                # Return the streamer that yields text chunks
                return streamer
            else:
                # Generate without streaming
                with torch.no_grad():
                    output_ids = self.model.generate(**inputs, **generation_config)
                
                # Decode the output, skipping the input prompt
                prompt_length = inputs.input_ids.shape[1]
                output_text = self.tokenizer.decode(
                    output_ids[0][prompt_length:], 
                    skip_special_tokens=True
                )
                
                logger.info(f"Generated output (first 100 chars): {output_text[:100]}...")
                return output_text
        except Exception as e:
            logger.error(f"Error in generate: {e}")
            logger.error(traceback.format_exc())
            return f"Error generating response: {str(e)}"
            
    # Implement the interface expected by CodeAgent
    def __call__(self, messages, stream=False, **kwargs):
        """
        Call method to match the interface expected by CodeAgent
        """
        logger.info(f"__call__ invoked with messages: {messages}")
        
        # Import ActionStep if available, otherwise create a dummy class
        try:
            from smolagents.agents import ActionStep
            logger.info("Successfully imported ActionStep from smolagents.agents")
            
            # Define a response object class that inherits from ActionStep
            class ResponseObject(ActionStep):
                def __init__(self, content):
                    # Initialize with default values
                    super().__init__(
                        model_output=content,
                        step_number=None,
                        tool_calls=None,
                        observations=None,
                        error=None
                    )
                    # The 'content' attribute is used by CodeAgent
                    self.content = content
                    # Set token counts and duration
                    self.input_token_count = 0
                    self.output_token_count = 0
                    self.duration = None
                    
                def __str__(self):
                    return f"ResponseObject(content={self.content[:50]}...)" if len(self.content) > 50 else f"ResponseObject(content={self.content})"
        except ImportError:
            logger.warning("Could not import ActionStep from smolagents.agents, using fallback class")
            
            # Fallback response object if ActionStep is not available
            class ResponseObject:
                def __init__(self, content):
                    # The 'content' attribute is used by CodeAgent
                    self.content = content
                    # The 'model_output' attribute is used by Gradio_UI.py in pull_messages_from_step
                    self.model_output = content
                    # Additional attributes that Gradio_UI.py might check for
                    self.step_number = None
                    self.tool_calls = None
                    self.observations = None
                    self.error = None
                    self.input_token_count = 0
                    self.output_token_count = 0
                    self.duration = None
                    
                def __str__(self):
                    return f"ResponseObject(content={self.content[:50]}...)" if len(self.content) > 50 else f"ResponseObject(content={self.content})"
        
        try:
            # Log the type and structure of the messages
            logger.info(f"Messages type: {type(messages)}")
            if isinstance(messages, list):
                for i, msg in enumerate(messages):
                    logger.info(f"Message {i} type: {type(msg)}")
                    if hasattr(msg, 'keys'):
                        logger.info(f"Message {i} keys: {msg.keys()}")
            
            response = self.generate(messages, stream=stream, **kwargs)
            logger.info(f"Raw response type: {type(response)}")
            
            if stream:
                logger.info(f"Handling streaming response")
                # For streaming, we need to ensure each chunk has the expected attributes
                class StreamerWrapper:
                    def __init__(self, streamer):
                        self.streamer = streamer
                    
                    def __iter__(self):
                        return self
                    
                    def __next__(self):
                        try:
                            chunk = next(self.streamer)
                            logger.info(f"Streaming chunk: {chunk[:50]}..." if len(chunk) > 50 else f"Streaming chunk: {chunk}")
                            # Return a response object with the chunk as content and model_output
                            return ResponseObject(chunk)
                        except StopIteration:
                            logger.info("End of stream")
                            raise StopIteration
                        except Exception as e:
                            logger.error(f"Error in streamer: {e}")
                            error_response = ResponseObject(f"Error in stream: {str(e)}")
                            error_response.error = str(e)
                            return error_response
                
                wrapper = StreamerWrapper(response)
                logger.info(f"Returning streamer wrapper: {wrapper}")
                return wrapper
            else:
                # Non-streaming case
                if isinstance(response, str):
                    logger.info(f"Response is a string: {response[:100]}...")
                    formatted_response = ResponseObject(response)
                    logger.info(f"Returning response object: {formatted_response}")
                    return formatted_response
                elif hasattr(response, 'content'):
                    # If response already has a content attribute but is not an ActionStep,
                    # we need to convert it to our ResponseObject
                    logger.info(f"Response already has content attribute: {response.content[:100] if hasattr(response.content, '__len__') else response.content}")
                    
                    try:
                        from smolagents.agents import ActionStep
                        if not isinstance(response, ActionStep):
                            logger.info("Converting response to ActionStep")
                            content = response.content
                            formatted_response = ResponseObject(content)
                            return formatted_response
                    except ImportError:
                        pass
                    
                    # Ensure all expected attributes are present
                    for attr in ['model_output', 'step_number', 'tool_calls', 'observations', 'error', 
                                'input_token_count', 'output_token_count', 'duration']:
                        if not hasattr(response, attr):
                            if attr == 'model_output':
                                setattr(response, attr, response.content)
                            elif attr in ['input_token_count', 'output_token_count']:
                                setattr(response, attr, 0)
                            else:
                                setattr(response, attr, None)
                    
                    return response
                else:
                    # If response is something else, convert to string and wrap
                    logger.warning(f"Response is an unexpected type: {type(response)}")
                    formatted_response = ResponseObject(str(response))
                    logger.info(f"Returning wrapped response: {formatted_response}")
                    return formatted_response
                
        except Exception as e:
            logger.error(f"Error in __call__: {e}")
            logger.error(traceback.format_exc())
            # Return a response object with the error message
            error_response = ResponseObject(f"Error: {str(e)}")
            error_response.error = str(e)
            logger.info(f"Returning error response: {error_response}")
            return error_response 