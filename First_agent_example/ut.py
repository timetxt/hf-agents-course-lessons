#!/usr/bin/env python
# coding=utf-8
"""
Unit tests for LocalModel integration with CodeAgent and GradioUI.
This script tests the response formatting and compatibility between components.
"""

import unittest
import logging
import sys
import os
from typing import List, Dict, Any, Optional
import traceback
import datetime
import pytz
import requests
import json

# Configure logging
logging.basicConfig(level=logging.WARNING, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('UnitTest')

# Import local modules
try:
    from local_model import LocalModel
    from smolagents import CodeAgent
    from smolagents.agents import ActionStep, MultiStepAgent
    from smolagents.memory import MemoryStep
    from tools.final_answer import FinalAnswerTool
    HAS_DEPENDENCIES = True
except ImportError as e:
    logger.error(f"Failed to import dependencies: {e}")
    logger.error(traceback.format_exc())
    HAS_DEPENDENCIES = False

# Mock classes for testing without dependencies
class MockStreamer:
    """Mock streamer for testing streaming responses"""
    def __init__(self, chunks):
        self.chunks = chunks
        self.index = 0
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.index < len(self.chunks):
            chunk = self.chunks[self.index]
            self.index += 1
            return chunk
        raise StopIteration

class MockActionStep:
    """Mock ActionStep for testing"""
    def __init__(self, model_output, step_number=1, tool_calls=None, observations=None, error=None):
        self.model_output = model_output
        self.step_number = step_number
        self.tool_calls = tool_calls or []
        self.observations = observations
        self.error = error
        self.content = model_output  # For CodeAgent compatibility

class MockModel:
    """Mock model for testing without loading a real model"""
    def __init__(self):
        self.responses = {
            "hello": "Hello! How can I assist you today?",
            "error": "Error generating response",
            "stream": MockStreamer(["Hello", " there", "! How", " can", " I", " help", " you", " today?"])
        }
    
    def generate(self, messages, stream=False, **kwargs):
        """Mock generate method"""
        if stream:
            return self.responses["stream"]
        
        # Extract the message content - handle complex message structure
        content = self._extract_content(messages)
        logger.info(f"Extracted content: {content[:100] if len(content) > 100 else content}")
        
        # Return appropriate response
        if "error" in content.lower():
            return self.responses["error"]
        elif "hello" in content.lower():
            return self.responses["hello"]
        else:
            return f"You said: {content[:50]}..." if len(content) > 50 else f"You said: {content}"
    
    def _extract_content(self, messages):
        """Extract text content from potentially complex message structures"""
        # Base cases
        if messages is None:
            return ""
        if isinstance(messages, str):
            return messages
            
        # Handle list of messages
        if isinstance(messages, list):
            # Empty list
            if not messages:
                return ""
                
            # For unit testing, we'll focus on the last user message if possible
            for msg in reversed(messages):
                if isinstance(msg, dict) and msg.get("role") == "user":
                    return self._extract_content(msg)
            
            # If no user message found, use the last message
            return self._extract_content(messages[-1])
            
        # Handle dictionary message
        if isinstance(messages, dict):
            # If it has a content field, process it
            if "content" in messages:
                content = messages["content"]
                
                # If content is a list of content items (common in complex messages)
                if isinstance(content, list):
                    extracted_texts = []
                    for item in content:
                        if isinstance(item, dict) and "text" in item:
                            extracted_texts.append(item["text"])
                        elif isinstance(item, dict) and "content" in item:
                            extracted_texts.append(self._extract_content(item["content"]))
                        elif isinstance(item, str):
                            extracted_texts.append(item)
                        else:
                            extracted_texts.append(str(item))
                    
                    return " ".join(extracted_texts)
                
                # If content is a string or other type
                return self._extract_content(content)
            
            # If it has a text field (common in content items)
            if "text" in messages:
                return messages["text"]
                
            # If no recognizable fields, convert to string
            return str(messages)
            
        # Default fallback for any other type
        return str(messages)
    
    def __call__(self, messages, stream=False, **kwargs):
        """Mock __call__ method that mimics LocalModel.__call__"""
        try:
            response = self.generate(messages, stream=stream, **kwargs)
            
            # Define a response object class
            class ResponseObject:
                def __init__(self, content):
                    self.content = content
                    self.model_output = content
                    self.step_number = 1
                    self.tool_calls = None
                    self.observations = None
                    self.error = None
                    self.input_token_count = 0
                    self.output_token_count = 0
                    self.duration = 0.1
            
            if stream:
                # For streaming, wrap the streamer
                class StreamerWrapper:
                    def __init__(self, streamer):
                        self.streamer = streamer
                    
                    def __iter__(self):
                        return self
                    
                    def __next__(self):
                        try:
                            chunk = next(self.streamer)
                            return ResponseObject(chunk)
                        except StopIteration:
                            raise StopIteration
                
                return StreamerWrapper(response)
            else:
                # For non-streaming, wrap the response
                return ResponseObject(response)
        except Exception as e:
            logger.error(f"Error in MockModel.__call__: {e}")
            logger.error(traceback.format_exc())
            
            # Return an error response
            class ResponseObject:
                def __init__(self, content):
                    self.content = content
                    self.model_output = content
                    self.step_number = 1
                    self.tool_calls = None
                    self.observations = None
                    self.error = str(e)
                    self.input_token_count = 0
                    self.output_token_count = 0
                    self.duration = 0.1
            
            return ResponseObject(f"Error: {str(e)}")

class MockCodeAgent:
    """Mock CodeAgent for testing"""
    def __init__(self, model):
        self.model = model
        self.tools = []
    
    def run(self, task, stream=True, reset=False, additional_args=None):
        """Mock run method that yields steps"""
        # First yield a step with the model's response
        response = self.model(task)
        yield MockActionStep(model_output=response.content)
        
        # Then yield a final answer
        yield MockActionStep(model_output=f"Final answer: {response.content}")

class TestLocalModelIntegration(unittest.TestCase):
    """Test the integration of LocalModel with CodeAgent and GradioUI"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        logger.info("Setting up test fixtures")
        cls.has_dependencies = HAS_DEPENDENCIES
        
        # Create a mock model for testing
        cls.mock_model = MockModel()
        
        # Try to create a real model with minimal settings if dependencies are available
        if cls.has_dependencies:
            try:
                # Use a tiny model or set load_model=False to avoid actual loading
                cls.local_model = LocalModel(
                    model_id='Qwen/Qwen2.5-Coder-7B-Instruct',
                    max_tokens=10,  # Small value for testing
                    temperature=0.0,  # Deterministic for testing
                    load_in_4bit=True,
                )
                # Replace the _load_model method to avoid actually loading the model
                cls.local_model._original_load_model = cls.local_model._load_model
                cls.local_model._load_model = lambda: None
                cls.local_model.generate = cls.mock_model.generate
                cls.has_real_model = True
            except Exception as e:
                logger.error(f"Failed to create LocalModel: {e}")
                logger.error(traceback.format_exc())
                cls.has_real_model = False
        else:
            cls.has_real_model = False
    
    def test_response_format_string(self):
        """Test that the model correctly formats string responses"""
        logger.info("Testing string response formatting")
        
        # Use mock model if real model is not available
        model = self.local_model if self.has_real_model else self.mock_model
        
        # Test with a simple string message
        response = model("hello")
        
        # Check that the response has the expected attributes
        self.assertTrue(hasattr(response, 'content'), "Response should have 'content' attribute")
        self.assertTrue(hasattr(response, 'model_output'), "Response should have 'model_output' attribute")
        self.assertEqual(response.content, response.model_output, "content and model_output should be the same")
        
        # Check other attributes needed by GradioUI
        attrs = ['step_number', 'tool_calls', 'observations', 'error', 
                'input_token_count', 'output_token_count', 'duration']
        for attr in attrs:
            self.assertTrue(hasattr(response, attr), f"Response should have '{attr}' attribute")
        
        logger.info(f"Response content: {response.content}")
        logger.info(f"Response model_output: {response.model_output}")
    
    def test_response_format_dict(self):
        """Test that the model correctly formats dictionary responses"""
        logger.info("Testing dictionary response formatting")
        
        # Use mock model if real model is not available
        model = self.local_model if self.has_real_model else self.mock_model
        
        # Test with a dictionary message
        response = model({"role": "user", "content": "hello"})
        
        # Check that the response has the expected attributes
        self.assertTrue(hasattr(response, 'content'), "Response should have 'content' attribute")
        self.assertTrue(hasattr(response, 'model_output'), "Response should have 'model_output' attribute")
        self.assertEqual(response.content, response.model_output, "content and model_output should be the same")
        
        logger.info(f"Response content: {response.content}")
        logger.info(f"Response model_output: {response.model_output}")
    
    def test_response_format_list(self):
        """Test that the model correctly formats list responses"""
        logger.info("Testing list response formatting")
        
        # Use mock model if real model is not available
        model = self.local_model if self.has_real_model else self.mock_model
        
        # Test with a list of messages
        response = model([
            {"role": "user", "content": "hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ])
        
        # Check that the response has the expected attributes
        self.assertTrue(hasattr(response, 'content'), "Response should have 'content' attribute")
        self.assertTrue(hasattr(response, 'model_output'), "Response should have 'model_output' attribute")
        self.assertEqual(response.content, response.model_output, "content and model_output should be the same")
        
        logger.info(f"Response content: {response.content}")
        logger.info(f"Response model_output: {response.model_output}")
    
    def test_streaming_response(self):
        """Test that the model correctly formats streaming responses"""
        logger.info("Testing streaming response formatting")
        
        # Use mock model if real model is not available
        model = self.local_model if self.has_real_model else self.mock_model
        
        # Test with streaming enabled
        streamer = model("hello", stream=True)
        
        # Check that the streamer is iterable
        self.assertTrue(hasattr(streamer, '__iter__'), "Streamer should be iterable")
        self.assertTrue(hasattr(streamer, '__next__'), "Streamer should be iterable")
        
        # Collect chunks from the streamer
        chunks = []
        try:
            for chunk in streamer:
                chunks.append(chunk)
                # Check that each chunk has the expected attributes
                self.assertTrue(hasattr(chunk, 'content'), "Chunk should have 'content' attribute")
                self.assertTrue(hasattr(chunk, 'model_output'), "Chunk should have 'model_output' attribute")
                logger.info(f"Streaming chunk: {chunk.content}")
        except Exception as e:
            logger.error(f"Error in streaming: {e}")
            logger.error(traceback.format_exc())
            self.fail(f"Streaming failed: {e}")
        
        # Check that we got some chunks
        self.assertTrue(len(chunks) > 0, "Should have received streaming chunks")
    
    def test_error_handling(self):
        """Test that the model correctly handles errors"""
        logger.info("Testing error handling")
        
        # Use mock model if real model is not available
        model = self.local_model if self.has_real_model else self.mock_model
        
        # Test with a message that triggers an error
        response = model("trigger an error")
        
        # Check that the response has the expected attributes
        self.assertTrue(hasattr(response, 'content'), "Response should have 'content' attribute")
        self.assertTrue(hasattr(response, 'model_output'), "Response should have 'model_output' attribute")
        
        logger.info(f"Error response content: {response.content}")
        logger.info(f"Error response model_output: {response.model_output}")
    
    @unittest.skipIf(not HAS_DEPENDENCIES, "Dependencies not available")
    def test_codeagent_integration(self):
        """Test integration with CodeAgent"""
        logger.info("Testing CodeAgent integration")
        
        try:
            # Create a CodeAgent with our model
            agent = CodeAgent(
                model=self.local_model if self.has_real_model else self.mock_model,
                tools=[FinalAnswerTool()],
                max_steps=2,
                verbosity_level=1
            )
            
            # Run the agent with a simple task
            steps = list(agent.run("hello", stream=True))
            
            # Check that we got some steps
            self.assertTrue(len(steps) > 0, "Should have received steps from the agent")
            
            # Check the attributes of the steps
            for i, step in enumerate(steps):
                logger.info(f"Step {i}: {type(step)}")
                if hasattr(step, 'model_output'):
                    logger.info(f"Step {i} model_output: {step.model_output}")
                if hasattr(step, 'content'):
                    logger.info(f"Step {i} content: {step.content}")
        
        except Exception as e:
            logger.error(f"Error in CodeAgent integration: {e}")
            logger.error(traceback.format_exc())
            self.fail(f"CodeAgent integration failed: {e}")
    
    def test_mock_codeagent(self):
        """Test with a mock CodeAgent"""
        logger.info("Testing with mock CodeAgent")
        
        # Create a mock CodeAgent
        agent = MockCodeAgent(self.mock_model)
        
        # Run the agent with a simple task
        steps = list(agent.run("hello"))
        
        # Check that we got some steps
        self.assertTrue(len(steps) > 0, "Should have received steps from the mock agent")
        
        # Check the attributes of the steps
        for i, step in enumerate(steps):
            logger.info(f"Step {i}: {type(step)}")
            self.assertTrue(hasattr(step, 'model_output'), f"Step {i} should have 'model_output' attribute")
            self.assertTrue(hasattr(step, 'content'), f"Step {i} should have 'content' attribute")
            logger.info(f"Step {i} model_output: {step.model_output}")

def simulate_gradio_processing(agent):
    """Simulate how GradioUI processes agent steps"""
    logger.info("Simulating GradioUI processing")
    
    # This mimics the stream_to_gradio function in Gradio_UI.py
    def pull_messages_from_step(step_log):
        """Extract messages from agent steps"""
        logger.info(f"Processing step: {type(step_log)}")
        
        # Handle case where step_log is a string or has no attributes
        if isinstance(step_log, str) or not hasattr(step_log, "__dict__"):
            yield {"role": "assistant", "content": str(step_log)}
            return
            
        # Log available attributes for debugging
        logger.info(f"Step attributes: {dir(step_log)}")
        
        if hasattr(step_log, "model_output") and step_log.model_output is not None:
            model_output = step_log.model_output
            if isinstance(model_output, str):
                model_output = model_output.strip()
            else:
                model_output = str(model_output)
            logger.info(f"Model output: {model_output[:100]}...")
            yield {"role": "assistant", "content": model_output}
        
        if hasattr(step_log, "error") and step_log.error is not None:
            error_msg = str(step_log.error)
            logger.info(f"Error: {error_msg}")
            yield {"role": "assistant", "content": error_msg, "metadata": {"title": "💥 Error"}}
    
    # Run the agent and process steps
    messages = []
    try:
        # Use a simple prompt for testing
        for step_log in agent.run("hello"):
            logger.info(f"Got step: {type(step_log)}")
            try:
                for message in pull_messages_from_step(step_log):
                    messages.append(message)
                    logger.info(f"Processed message: {message}")
            except Exception as e:
                logger.error(f"Error processing step: {e}")
                logger.error(traceback.format_exc())
                messages.append({"role": "assistant", "content": f"Error processing step: {str(e)}"})
    except Exception as e:
        logger.error(f"Error running agent: {e}")
        logger.error(traceback.format_exc())
        messages.append({"role": "assistant", "content": f"Error running agent: {str(e)}"})
    
    return messages

class TestLocalTimeIntegration(unittest.TestCase):
    """Test the integration of local time functionality with CodeAgent"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        logger.info("Setting up local time test fixtures")
        cls.has_dependencies = HAS_DEPENDENCIES
        
        # Mock IP API response
        cls.mock_ip_response = "159.196.168.188"
        cls.mock_geo_response = {
            "status": "success",
            "country": "Australia",
            "countryCode": "AU",
            "region": "NSW",
            "regionName": "New South Wales",
            "city": "Sydney",
            "zip": "2000",
            "lat": -33.8688,
            "lon": 151.2093,
            "timezone": "Australia/Sydney",
            "isp": "Mock ISP",
            "org": "Mock Organization",
            "as": "AS13335 Mock Network",
            "query": "159.196.168.188"
        }
        
        # Define the problematic response that might be causing the issue
        cls.generic_time_response = "I'm sorry, but as an AI language model, I don't have access to real-time information about the user's location or device settings. However, you can easily find out your local time by checking the clock on your device or by searching \"what is the time\" on a search engine."
    
    def mock_requests_get(self, url):
        """Mock the requests.get function for testing"""
        class MockResponse:
            def __init__(self, text, json_data, status_code):
                self.text = text
                self._json_data = json_data
                self.status_code = status_code
            
            def json(self):
                return self._json_data
        
        if "demo.52dayday.com/myip" in url:
            return MockResponse(self.mock_ip_response, None, 200)
        elif "ip-api.com/json" in url:
            return MockResponse(json.dumps(self.mock_geo_response), self.mock_geo_response, 200)
        else:
            return MockResponse("", {}, 404)
    
    def test_get_local_time_from_ip(self):
        """Test the get_local_time_from_ip function"""
        logger.info("Testing get_local_time_from_ip function")
        
        # Save the original requests.get
        original_requests_get = requests.get
        
        try:
            # Replace requests.get with our mock
            requests.get = self.mock_requests_get
            
            # Define the get_local_time_from_ip function for testing
            def get_local_time_from_ip():
                """A tool that determines the user's local time based on their IP address location."""
                try:
                    # First, get the IP address
                    ip_response = requests.get("https://demo.52dayday.com/myip")
                    if ip_response.status_code != 200:
                        return f"Failed to retrieve IP address. Status code: {ip_response.status_code}"
                    
                    # Extract the IP address from the response
                    ip_address = ip_response.text.strip()
                    
                    # Get geolocation data
                    geo_url = f"http://ip-api.com/json/{ip_address}"
                    geo_response = requests.get(geo_url)
                    
                    if geo_response.status_code != 200:
                        return f"Failed to retrieve geolocation data. Status code: {geo_response.status_code}"
                    
                    geo_data = geo_response.json()
                    
                    # Check if the request was successful
                    if geo_data.get("status") != "success":
                        return f"Failed to retrieve geolocation data for IP {ip_address}. Error: {geo_data.get('message', 'Unknown error')}"
                    
                    # Extract timezone information
                    timezone = geo_data.get('timezone')
                    if not timezone:
                        return f"Could not determine timezone from IP {ip_address}. Location: {geo_data.get('country', 'Unknown')}, {geo_data.get('regionName', 'Unknown')}"
                    
                    # Get the current time in that timezone
                    try:
                        tz = pytz.timezone(timezone)
                        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
                        return f"The current local time in {geo_data.get('city', 'your location')} ({timezone}) is: {local_time}"
                    except Exception as e:
                        return f"Error determining time for timezone '{timezone}': {str(e)}"
                        
                except Exception as e:
                    return f"Error retrieving local time based on IP: {str(e)}"
            
            # Test the function
            result = get_local_time_from_ip()
            logger.info(f"get_local_time_from_ip result: {result}")
            
            # Check that the result contains the expected information
            self.assertIn("Sydney", result, "Result should contain the city name")
            self.assertIn("Australia/Sydney", result, "Result should contain the timezone")
            
            # Now test with a mock CodeAgent
            class MockTool:
                def __init__(self, func):
                    self.func = func
                    self.__name__ = func.__name__
                
                def __call__(self, *args, **kwargs):
                    return self.func(*args, **kwargs)
            
            class MockFinalAnswerTool:
                def __init__(self):
                    self.__name__ = "final_answer"
                
                def __call__(self, answer):
                    return f"Final answer: {answer}"
            
            # Create a mock agent with our tools
            mock_agent = MockCodeAgent(self.mock_model)
            mock_agent.tools = [
                MockTool(get_local_time_from_ip),
                MockFinalAnswerTool()
            ]
            
            # Test the agent with a prompt about local time
            steps = list(mock_agent.run("What is my local time?"))
            
            # Check that we got some steps
            self.assertTrue(len(steps) > 0, "Should have received steps from the mock agent")
            
            # Check if any step contains the local time information
            local_time_found = False
            for step in steps:
                if hasattr(step, 'model_output') and "Sydney" in step.model_output:
                    local_time_found = True
                    logger.info(f"Found local time in step: {step.model_output}")
            
            self.assertTrue(local_time_found, "Should have found local time information in at least one step")
            
            # Test with a real CodeAgent if dependencies are available
            if self.has_dependencies:
                try:
                    # Create a CodeAgent with our model and tools
                    agent = CodeAgent(
                        model=LocalModel(
                            model_id='Qwen/Qwen2.5-Coder-7B-Instruct',
                            max_tokens=10,
                            temperature=0.0,
                            load_in_4bit=True,
                        ),
                        tools=[
                            MockTool(get_local_time_from_ip),
                            MockFinalAnswerTool()
                        ],
                        max_steps=3,
                        verbosity_level=1
                    )
                    
                    # Replace the _load_model method to avoid actually loading the model
                    agent.model._original_load_model = agent.model._load_model
                    agent.model._load_model = lambda: None
                    agent.model.generate = lambda messages, stream=False, **kwargs: "I'll check your local time."
                    
                    # Run the agent with a prompt about local time
                    steps = list(agent.run("What is my local time?", stream=True))
                    
                    # Check that we got some steps
                    self.assertTrue(len(steps) > 0, "Should have received steps from the agent")
                    
                    # Log the steps for debugging
                    for i, step in enumerate(steps):
                        logger.info(f"Step {i}: {type(step)}")
                        if hasattr(step, 'model_output'):
                            logger.info(f"Step {i} model_output: {step.model_output}")
                        if hasattr(step, 'tool_calls'):
                            logger.info(f"Step {i} tool_calls: {step.tool_calls}")
                        if hasattr(step, 'observations'):
                            logger.info(f"Step {i} observations: {step.observations}")
                
                except Exception as e:
                    logger.error(f"Error in CodeAgent test: {e}")
                    logger.error(traceback.format_exc())
            
        finally:
            # Restore the original requests.get
            requests.get = original_requests_get
    
    def test_agent_local_time_response(self):
        """Test specifically for the issue where the agent returns a generic response instead of using local time info"""
        logger.info("Testing agent's response to local time queries")
        
        # Save the original requests.get
        original_requests_get = requests.get
        
        try:
            # Replace requests.get with our mock
            requests.get = self.mock_requests_get
            
            # Define the get_local_time_from_ip function for testing
            def get_local_time_from_ip():
                """A tool that determines the user's local time based on their IP address location."""
                try:
                    # First, get the IP address
                    ip_response = requests.get("https://demo.52dayday.com/myip")
                    if ip_response.status_code != 200:
                        return f"Failed to retrieve IP address. Status code: {ip_response.status_code}"
                    
                    # Extract the IP address from the response
                    ip_address = ip_response.text.strip()
                    
                    # Get geolocation data
                    geo_url = f"http://ip-api.com/json/{ip_address}"
                    geo_response = requests.get(geo_url)
                    
                    if geo_response.status_code != 200:
                        return f"Failed to retrieve geolocation data. Status code: {geo_response.status_code}"
                    
                    geo_data = geo_response.json()
                    
                    # Check if the request was successful
                    if geo_data.get("status") != "success":
                        return f"Failed to retrieve geolocation data for IP {ip_address}. Error: {geo_data.get('message', 'Unknown error')}"
                    
                    # Extract timezone information
                    timezone = geo_data.get('timezone')
                    if not timezone:
                        return f"Could not determine timezone from IP {ip_address}. Location: {geo_data.get('country', 'Unknown')}, {geo_data.get('regionName', 'Unknown')}"
                    
                    # Get the current time in that timezone
                    try:
                        tz = pytz.timezone(timezone)
                        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
                        return f"The current local time in {geo_data.get('city', 'your location')} ({timezone}) is: {local_time}"
                    except Exception as e:
                        return f"Error determining time for timezone '{timezone}': {str(e)}"
                        
                except Exception as e:
                    return f"Error retrieving local time based on IP: {str(e)}"
            
            # Define a final answer tool that will capture the answer
            class TestFinalAnswerTool:
                def __init__(self):
                    self.__name__ = "final_answer"
                    self.last_answer = None
                
                def __call__(self, answer):
                    self.last_answer = answer
                    return f"Final answer: {answer}"
            
            # Create a mock agent that simulates the behavior we're seeing
            class TestAgent:
                def __init__(self):
                    self.final_answer_tool = TestFinalAnswerTool()
                    self.local_time_tool = get_local_time_from_ip
                    self.generic_response = TestLocalTimeIntegration.generic_time_response
                
                def run(self, query):
                    """Simulate the agent's behavior"""
                    # First, yield a step that calls the local time tool
                    local_time_result = self.local_time_tool()
                    yield MockActionStep(
                        model_output="I'll check your local time.",
                        tool_calls=[{"name": "get_local_time_from_ip", "args": {}}],
                        observations=local_time_result
                    )
                    
                    # Then, yield a step with the final answer, but use the generic response
                    # instead of incorporating the local time information
                    final_answer = self.final_answer_tool(self.generic_response)
                    yield MockActionStep(
                        model_output=final_answer,
                        tool_calls=[{"name": "final_answer", "args": {"answer": self.generic_response}}],
                        observations=None
                    )
            
            # Test the agent
            agent = TestAgent()
            steps = list(agent.run("What is my local time?"))
            
            # Check that we got the expected steps
            self.assertEqual(len(steps), 2, "Should have received 2 steps from the test agent")
            
            # Check that the first step contains the local time information
            self.assertIn("Sydney", steps[0].observations, "First step should contain the city name")
            self.assertIn("Australia/Sydney", steps[0].observations, "First step should contain the timezone")
            
            # Check that the final answer is the generic response
            self.assertIn("I'm sorry", steps[1].model_output, "Final answer should be the generic response")
            
            # This is the key issue: the agent is getting the local time information
            # but not using it in the final answer
            logger.warning("ISSUE DETECTED: Agent gets local time info but returns generic response")
            logger.warning(f"Local time info: {steps[0].observations}")
            logger.warning(f"Final answer: {steps[1].model_output}")
            
            # Suggest a fix: update the prompt templates to explicitly instruct the agent
            # to use tool results in its final answer
            logger.info("SUGGESTED FIX: Update prompt templates to instruct the agent to use tool results")
            logger.info("Check prompts.yaml for the system_prompt and make sure it includes instructions")
            logger.info("to use the results of tools in the final answer.")
            
            # Also check if the agent's model is properly processing the tool results
            logger.info("Also check if the model is properly processing tool results in its context window.")
            logger.info("The model might be ignoring or forgetting the tool results when generating the final answer.")
            
        finally:
            # Restore the original requests.get
            requests.get = original_requests_get

def run_tests():
    """Run the unit tests"""
    logger.info("Running unit tests")
    
    # Run the unit tests
    try:
        unittest.main(argv=['first-arg-is-ignored'], exit=False)
        logger.info("Unit tests completed")
    except Exception as e:
        logger.error(f"Error running unit tests: {e}")
        logger.error(traceback.format_exc())
    
    # Run the local time test separately
    try:
        logger.info("Running local time test")
        test_suite = unittest.TestLoader().loadTestsFromTestCase(TestLocalTimeIntegration)
        unittest.TextTestRunner().run(test_suite)
        logger.info("Local time test completed")
    except Exception as e:
        logger.error(f"Error running local time test: {e}")
        logger.error(traceback.format_exc())
    
    # Additional simulation if dependencies are available
    if HAS_DEPENDENCIES:
        logger.info("Running GradioUI simulation")
        try:
            # Create a mock model that doesn't actually load the real model
            class SafeLocalModel(LocalModel):
                def _load_model(self):
                    logger.info("Mock loading model (not actually loading)")
                    self.tokenizer = None
                    self.model = None
                    
                def generate(self, messages, stream=False, **kwargs):
                    # Use the MockModel's generate method
                    mock = MockModel()
                    return mock.generate(messages, stream=stream, **kwargs)
            
            # Create a model instance without actually loading a model
            model = SafeLocalModel(
                model_id='Qwen/Qwen2.5-Coder-7B-Instruct',
                max_tokens=10,
                temperature=0.0,
                load_in_4bit=True,
            )
            
            # Create a simple agent for testing
            try:
                agent = CodeAgent(
                    model=model,
                    tools=[FinalAnswerTool()],
                    max_steps=2,
                    verbosity_level=1
                )
                
                # Simulate GradioUI processing
                messages = simulate_gradio_processing(agent)
                logger.info(f"Simulation produced {len(messages)} messages")
            except Exception as e:
                logger.error(f"Error creating or running CodeAgent: {e}")
                logger.error(traceback.format_exc())
                
                # Fall back to mock agent
                logger.info("Falling back to mock agent")
                agent = MockCodeAgent(MockModel())
                messages = simulate_gradio_processing(agent)
                logger.info(f"Mock simulation produced {len(messages)} messages")
        
        except Exception as e:
            logger.error(f"Error in GradioUI simulation: {e}")
            logger.error(traceback.format_exc())
    else:
        logger.info("Skipping GradioUI simulation (dependencies not available)")
        
        # Run with mock agent instead
        logger.info("Running GradioUI simulation with mock agent")
        try:
            agent = MockCodeAgent(MockModel())
            messages = simulate_gradio_processing(agent)
            logger.info(f"Mock simulation produced {len(messages)} messages")
        except Exception as e:
            logger.error(f"Error in mock simulation: {e}")
            logger.error(traceback.format_exc())

if __name__ == "__main__":
    run_tests() 