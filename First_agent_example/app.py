from smolagents import CodeAgent,DuckDuckGoSearchTool, load_tool,tool
import datetime
import requests
import pytz
import yaml
import logging
from tools.final_answer import FinalAnswerTool
from local_model import LocalModel

from Gradio_UI import GradioUI

# Configure logging for app.py
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('AppFunctions')

# Below is an example of a tool that does nothing. Amaze us with your creativity !
# @tool
# def my_custom_tool() -> str:
#     """A tool that checks the user's IP address and returns geographic location information including timezone.
    
#     Returns:
#         A string containing the IP address, geographic location information, and timezone.
#     """
#     try:
#         # First, get the IP address
#         ip_response = requests.get("https://demo.52dayday.com/myip")
#         if ip_response.status_code != 200:
#             return f"Failed to retrieve IP address. Status code: {ip_response.status_code}"
        
#         # Extract the IP address from the response (assuming it's just a plain text IP)
#         ip_address = ip_response.text.strip()
        
#         # Now, use ip-api.com to get geolocation data
#         geo_url = f"http://ip-api.com/json/{ip_address}"
#         geo_response = requests.get(geo_url)
        
#         if geo_response.status_code == 200:
#             geo_data = geo_response.json()
            
#             # Check if the request was successful
#             if geo_data.get("status") == "success":
#                 # Extract timezone information
#                 timezone = geo_data.get('timezone', 'Unknown')
                
#                 return (f"Your IP address is {ip_address}\n"
#                         f"Location: {geo_data.get('country', 'Unknown')}, "
#                         f"{geo_data.get('regionName', 'Unknown')}, "
#                         f"{geo_data.get('city', 'Unknown')}\n"
#                         f"ISP: {geo_data.get('isp', 'Unknown')}\n"
#                         f"Timezone: {timezone}\n"
#                         f"Coordinates: {geo_data.get('lat', 'Unknown')}, {geo_data.get('lon', 'Unknown')}")
#             else:
#                 return f"Failed to retrieve geolocation data for IP {ip_address}. Error: {geo_data.get('message', 'Unknown error')}"
#         else:
#             return f"Failed to retrieve geolocation data. Status code: {geo_response.status_code}"
#     except Exception as e:
#         return f"Error retrieving IP or geolocation information: {str(e)}"

@tool
def get_local_time_from_ip() -> str:
    """A tool that determines the user's local time based on their IP address location.
    This tool first gets the user's IP address, then determines their timezone from geolocation,
    and finally returns the current time in that timezone.
    
    Returns:
        A string containing the current local time based on the user's IP location.
    """
    logger.info("Function called: get_local_time_from_ip()")
    try:
        # First, get the IP address
        logger.info("Requesting IP address from demo.52dayday.com/myip")
        ip_response = requests.get("https://demo.52dayday.com/myip")
        if ip_response.status_code != 200:
            error_msg = f"Failed to retrieve IP address. Status code: {ip_response.status_code}"
            logger.error(error_msg)
            return error_msg
        
        # Extract the IP address from the response
        ip_address = ip_response.text.strip()
        logger.info(f"Retrieved IP address: {ip_address}")
        
        # Get geolocation data
        logger.info(f"Requesting geolocation data for IP: {ip_address}")
        geo_url = f"http://ip-api.com/json/{ip_address}"
        geo_response = requests.get(geo_url)
        
        if geo_response.status_code != 200:
            error_msg = f"Failed to retrieve geolocation data. Status code: {geo_response.status_code}"
            logger.error(error_msg)
            return error_msg
        
        geo_data = geo_response.json()
        logger.info(f"Retrieved geolocation data: {geo_data}")
        
        # Check if the request was successful
        if geo_data.get("status") != "success":
            error_msg = f"Failed to retrieve geolocation data for IP {ip_address}. Error: {geo_data.get('message', 'Unknown error')}"
            logger.error(error_msg)
            return error_msg
        
        # Extract timezone information
        timezone = geo_data.get('timezone')
        if not timezone:
            error_msg = f"Could not determine timezone from IP {ip_address}. Location: {geo_data.get('country', 'Unknown')}, {geo_data.get('regionName', 'Unknown')}"
            logger.error(error_msg)
            return error_msg
        
        # Get the current time in that timezone
        try:
            tz = pytz.timezone(timezone)
            local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            result = f"The current local time in {geo_data.get('city', 'your location')} ({timezone}) is: {local_time}"
            logger.info(f"Successfully determined local time: {result}")
            return result
        except Exception as e:
            error_msg = f"Error determining time for timezone '{timezone}': {str(e)}"
            logger.error(error_msg)
            return error_msg
            
    except Exception as e:
        error_msg = f"Error retrieving local time based on IP: {str(e)}"
        logger.error(error_msg)
        return error_msg

@tool
def get_current_time_in_timezone(timezone: str) -> str:
    """A tool that fetches the current local time in a specified timezone.
    Args:
        timezone: A string representing a valid timezone (e.g., 'America/New_York').
    """
    logger.info(f"Function called: get_current_time_in_timezone(timezone='{timezone}')")
    
    # Special case for "local" timezone - use IP-based location
    if timezone.lower() == "local":
        logger.info("Special case: 'local' timezone requested, redirecting to get_local_time_from_ip()")
        return get_local_time_from_ip()
        
    try:
        # Create timezone object
        tz = pytz.timezone(timezone)
        # Get current time in that timezone
        local_time = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        result = f"The current local time in {timezone} is: {local_time}"
        logger.info(f"Successfully determined time for timezone '{timezone}': {result}")
        return result
    except Exception as e:
        error_msg = f"Error fetching time for timezone '{timezone}': {str(e)}"
        logger.error(error_msg)
        return error_msg


final_answer = FinalAnswerTool()

# Using LocalModel instead of HfApiModel to run the model locally
model = LocalModel(
    max_tokens=2096,
    temperature=0.5,
    model_id='Qwen/Qwen2.5-Coder-7B-Instruct',  # Model will be downloaded locally
    load_in_4bit=True,  # Use 4-bit quantization to reduce memory usage
    device=None,  # Will use CUDA if available, otherwise CPU
)


# Import tool from Hub
image_generation_tool = load_tool("agents-course/text-to-image", trust_remote_code=True)

with open("prompts.yaml", 'r') as stream:
    prompt_templates = yaml.safe_load(stream)
    
agent = CodeAgent(
    model=model,
    tools=[final_answer, get_current_time_in_timezone
        #    , my_custom_tool
           , get_local_time_from_ip
           , image_generation_tool], ## add your tools here (don't remove final answer)
    max_steps=6,
    verbosity_level=1,
    grammar=None,
    planning_interval=None,
    name=None,
    description=None,
    prompt_templates=prompt_templates
)

logger.info("Starting GradioUI with configured agent")
GradioUI(agent).launch()