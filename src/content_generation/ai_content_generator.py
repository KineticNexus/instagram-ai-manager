import os
import json
import time
import random
import logging
import requests
from typing import Dict, List, Optional, Tuple, Any
from dotenv import load_dotenv
import subprocess
from PIL import Image
from .image_analyzer import ImageAnalyzer
import re

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("content_generator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AIContentGenerator:
    """
    A class to generate content using AI services (OpenAI for text, Midjourney for images)
    """
    
    # Class-level variables to track API validation status
    _api_keys_tested = False
    _openai_api_validated = False
    _midjourney_api_validated = False
    
    def __init__(self, openai_api_key, midjourney_api_key):
        """Initialize the AI content generator"""
        self.openai_api_key = openai_api_key
        self.midjourney_api_key = midjourney_api_key
        self.midjourney_api_url = "https://api.goapi.ai"
        
        # Set up OpenAI client
        try:
            from openai import OpenAI
            self.openai_client = OpenAI(api_key=openai_api_key)
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {str(e)}")
            self.openai_client = None
        
        # Set up paths for storing generated images
        self.static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                      "web_interface", "static")
        self.generated_images_dir = os.path.join(self.static_dir, "generated_images")
        self.fallback_images_dir = os.path.join(self.static_dir, "fallback_images")
        
        # Ensure the directories exist
        os.makedirs(self.generated_images_dir, exist_ok=True)
        os.makedirs(self.fallback_images_dir, exist_ok=True)
        
        # Copy default fallback image if none exist
        if not os.listdir(self.fallback_images_dir):
            import shutil
            default_img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "default_fallback.jpg")
            if os.path.exists(default_img_path):
                shutil.copy(default_img_path, os.path.join(self.fallback_images_dir, "default_fallback.jpg"))
            logger.info(f"Added default fallback image to {self.fallback_images_dir}")
        
        # Topics for Kinetic Nexus content
        self.topics = {
            "análisis de mercados": "Professional data visualization showing market analysis, modern infographics with business charts, corporate style",
            "inteligencia comercial": "Modern business intelligence dashboard with real-time analytics, professional data visualization, corporate theme",
            "comercio internacional": "Global trade network visualization with connected markets, professional business infographic, world trade flow",
            "estrategia global": "Strategic business planning visualization, modern corporate style with growth indicators and global markets"
        }
        
        # Business regions
        self.business_regions = [
            "América Latina", "Norteamérica", "Europa", "Asia-Pacífico",
            "Medio Oriente", "África", "Sudeste Asiático", "Unión Europea",
            "Mercosur", "Alianza del Pacífico"
        ]
        
        # Style elements to add variety
        self.style_elements = [
            "modern office setting", "executive style", "professional business environment",
            "corporate boardroom atmosphere", "digital business concept", "minimalist business style",
            "data-driven visualization", "global business perspective", "strategic planning concept"
        ]
        
        # Test API keys (but don't fail initialization if they're invalid)
        logger.info("Testing API keys")
        self._test_api_keys()
        logger.info("AIContentGenerator initialized successfully")

    def _test_api_keys(self):
        """Test API keys by making minimal API calls, but don't fail if they don't work"""
        # Flag to track if we've already tested the API keys
        if AIContentGenerator._api_keys_tested:
            logger.info("API keys already tested, skipping redundant test")
            return True
        
        # Test OpenAI API key
        openai_valid = False
        if self.openai_api_key and not AIContentGenerator._openai_api_validated:
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.openai_api_key}"
                }
                
                data = {
                    "model": "gpt-3.5-turbo",  # Use a smaller model for testing
                    "messages": [
                        {"role": "user", "content": "test"}
                    ],
                    "max_tokens": 5
                }
                
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=10  # Add a timeout to avoid hanging
                )
                
                if response.status_code == 200:
                    logger.info("OpenAI API key is valid")
                    openai_valid = True
                    AIContentGenerator._openai_api_validated = True
                else:
                    logger.warning(f"OpenAI API key test failed: {response.status_code} - {response.text}")
            except Exception as e:
                logger.warning(f"Error testing OpenAI API key: {str(e)}")
        else:
            # If OpenAI was already validated, mark as valid
            if AIContentGenerator._openai_api_validated:
                logger.info("OpenAI API key already validated, skipping test")
                openai_valid = True
        
        # Just verify Midjourney API key exists - DO NOT make a test API call
        midjourney_valid = False
        if self.midjourney_api_key:
            # Skip actual API testing to avoid unnecessary costs
            logger.info("Midjourney API key provided (skipping validation to avoid API costs)")
            self.midjourney_api_url = "https://api.goapi.ai"
            midjourney_valid = True
            AIContentGenerator._midjourney_api_validated = True
        
        # Mark that we've tested the API keys at the class level
        AIContentGenerator._api_keys_tested = True
        
        return openai_valid or midjourney_valid
    
    def generate_prompt(self, topic):
        """Generate a prompt for image creation based on the topic."""
        prompts = {
            "análisis de mercados": 
                "Professional data visualization showing market analysis, modern infographics with business charts, corporate style",
            "inteligencia comercial":
                "Modern business intelligence dashboard with real-time analytics, professional data visualization, corporate theme",
            "comercio internacional":
                "Global trade network visualization with connected markets, professional business infographic, world trade flow",
            "estrategia global":
                "Strategic business planning visualization, modern corporate style with growth indicators and global markets"
        }
        
        base_prompt = prompts.get(topic, "Modern business consulting visualization, professional corporate environment")
        style = random.choice(self.style_elements)
        region = random.choice(self.business_regions)
        
        # Remove aspect ratio from prompt as it's causing issues
        return f"{base_prompt}, {style}, focus on {region}, professional lighting, 4k, detailed"

    def generate_caption(self, topic: str) -> str:
        """Generate a caption for the given topic"""
        try:
            system_prompt = """You are an expert at creating engaging Spanish captions for Instagram posts about business intelligence and international trade.
            Create a caption that is informative, professional, and engaging. Include relevant hashtags at the end.
            The caption should be 2-3 paragraphs long and include:
            1. An engaging opening line with emojis
            2. Key insights or information about the topic
            3. A call to action
            4. 8-10 relevant Spanish hashtags"""
            
            user_prompt = f"Create a Spanish caption for an Instagram post about: {topic}"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_api_key}"
            }
            
            data = {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 300
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                # Return a default caption as fallback
                return f"""🌐 Descubre las últimas tendencias en {topic} con Kinetic Nexus

Nuestro equipo de expertos analiza constantemente el mercado global para brindarte información estratégica y actualizada. Contacta con nosotros para conocer más sobre nuestros servicios de consultoría internacional.

#InteligenciaComercial #ComercioInternacional #KineticNexus #ConsultoríaEstrategica #MercadosGlobales #ExportaciónMX #NegociosInternacionales #AnálisisDeMercado"""
            
            result = response.json()
            caption = result["choices"][0]["message"]["content"]
            
            # Ensure we have hashtags
            if not any(word.startswith('#') for word in caption.split()):
                caption += f"\n\n{' '.join(random.sample(self.hashtags, 8))}"
            
            return caption
            
        except Exception as e:
            logger.error(f"Error generating caption: {str(e)}")
            # Return a default caption as fallback
            return f"""🌐 Descubre las últimas tendencias en {topic} con Kinetic Nexus

Nuestro equipo de expertos analiza constantemente el mercado global para brindarte información estratégica y actualizada. Contacta con nosotros para conocer más sobre nuestros servicios de consultoría internacional.

#InteligenciaComercial #ComercioInternacional #KineticNexus #ConsultoríaEstrategica #MercadosGlobales #ExportaciónMX #NegociosInternacionales #AnálisisDeMercado"""

    def generate_image_prompt(self, caption: str) -> str:
        """
        Generate an image prompt based on the caption
        
        Args:
            caption: The caption to base the image prompt on
            
        Returns:
            Generated image prompt
        """
        try:
            # Use OpenAI to generate a Midjourney-optimized prompt
            system_prompt = """You are a professional photographer and Midjourney prompt expert. 
            You need to create a Midjourney compatible prompt for a business-related image.
            Your prompt should describe a professional business image related to international trade,
            market analysis, or business intelligence.
            
            The prompt should be highly detailed and include:
            - Clear description of the business concept
            - Style elements (corporate, professional, modern)
            - Lighting, color palette, and composition details
            - Avoid any text generation in the image
            - Include --ar 4:5 at the end for Instagram ratio
            
            Keep prompt length to 200-300 characters.
            ONLY return the prompt, nothing else."""
            
            user_prompt = f"Create a Midjourney prompt for a professional business image related to: {caption}"
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.openai_api_key}"
            }
            
            data = {
                "model": "gpt-4",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 300
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                # Return a default prompt
                return "Modern business visualization, corporate professional environment, market analysis dashboard, clean design, strategic planning, realistic, 4k detailed --ar 4:5"
            
            result = response.json()
            prompt = result["choices"][0]["message"]["content"]
            
            # Ensure prompt has appropriate tags
            if "--ar" not in prompt:
                prompt += " --ar 4:5"
                
            return prompt
        
        except Exception as e:
            logger.error(f"Error generating image prompt: {str(e)}")
            return "Modern business visualization, corporate professional environment, market analysis dashboard, clean design, strategic planning, realistic, 4k detailed --ar 4:5"

    def generate_midjourney_image(self, prompt: str, filename: str = None) -> dict:
        """
        Generate an image using Midjourney API
        
        Args:
            prompt: The prompt to generate an image from
            filename: Optional filename to save the image as
            
        Returns:
            Dictionary with status and image_path
        """
        if not self.midjourney_api_key:
            logger.error("Midjourney API key not found")
            return {"status": "error", "message": "Midjourney API key not found"}
        
        try:
            # Prepare the API request
            headers = {
                "X-API-KEY": self.midjourney_api_key
            }
            
            data = {
                "prompt": prompt,
                "aspect_ratio": "4:5",  # Instagram-optimized ratio
                "negative_prompt": "text, watermark, low quality, pixelated, blurry"
            }
            
            logger.info(f"Sending request to Midjourney API with prompt: {prompt}")
            
            # Send request to Midjourney API
            response = requests.post(
                f"{self.midjourney_api_url}/v1/midjourney/imagine",
                headers=headers,
                json=data
            )
            
            if response.status_code != 200:
                logger.error(f"Midjourney API error: {response.status_code} - {response.text}")
                return {"status": "error", "message": f"Midjourney API error: {response.status_code}"}
            
            result = response.json()
            logger.info(f"Midjourney API response received: {result}")
            
            if "taskId" not in result:
                logger.error("No taskId in Midjourney API response")
                return {"status": "error", "message": "No taskId in Midjourney API response"}
            
            task_id = result["taskId"]
            
            # Poll for task completion
            max_attempts = 30
            attempt = 0
            while attempt < max_attempts:
                attempt += 1
                logger.info(f"Polling for task {task_id}, attempt {attempt}/{max_attempts}")
                
                # Check task status
                status_response = requests.get(
                    f"{self.midjourney_api_url}/v1/midjourney/task/{task_id}",
                    headers=headers
                )
                
                if status_response.status_code != 200:
                    logger.error(f"Error checking task status: {status_response.status_code} - {status_response.text}")
                    time.sleep(10)  # Wait before retry
                    continue
                
                status_result = status_response.json()
                
                # Check if the task is completed
                if status_result.get("status") == "SUCCESS":
                    # Get the image URL
                    image_url = status_result.get("imageUrl")
                    if not image_url:
                        logger.error("No image URL in SUCCESS response")
                        return {"status": "error", "message": "No image URL in SUCCESS response"}
                    
                    # Download the image
                    image_response = requests.get(image_url, stream=True)
                    if image_response.status_code != 200:
                        logger.error(f"Error downloading image: {image_response.status_code}")
                        return {"status": "error", "message": f"Error downloading image: {image_response.status_code}"}
                    
                    # Save the image
                    if not filename:
                        filename = f"midjourney_{int(time.time())}.png"
                    
                    image_path = os.path.join(self.generated_images_dir, filename)
                    with open(image_path, 'wb') as img_file:
                        for chunk in image_response.iter_content(chunk_size=8192):
                            img_file.write(chunk)
                    
                    logger.info(f"Image saved to {image_path}")
                    
                    # Run the image analyzer to verify image quality
                    analyzer = ImageAnalyzer()
                    analysis_result = analyzer.analyze_image(image_path)
                    
                    if analysis_result.get("quality_score", 0) < 0.6:
                        logger.warning(f"Image quality score too low: {analysis_result.get('quality_score')}")
                        return {
                            "status": "low_quality", 
                            "message": "Generated image has low quality score",
                            "image_path": image_path
                        }
                    
                    return {
                        "status": "success", 
                        "image_path": image_path,
                        "analysis": analysis_result
                    }
                
                elif status_result.get("status") == "FAILED":
                    logger.error(f"Task failed: {status_result.get('error', 'Unknown error')}")
                    return {"status": "error", "message": f"Task failed: {status_result.get('error', 'Unknown error')}"}
                
                # Wait before checking again
                time.sleep(10)
            
            logger.error(f"Timeout waiting for task {task_id}")
            return {"status": "error", "message": f"Timeout waiting for task {task_id}"}
            
        except Exception as e:
            logger.error(f"Error generating Midjourney image: {str(e)}")
            return {"status": "error", "message": f"Error: {str(e)}"}

    def generate_content(self, topic: str = None) -> dict:
        """
        Generate a complete Instagram post (image + caption)
        
        Args:
            topic: Optional topic to generate content for, otherwise random
            
        Returns:
            Dictionary with status, image_path and caption
        """
        # Select a topic if not provided
        if not topic:
            topic = random.choice(list(self.topics.keys()))
        
        logger.info(f"Generating content for topic: {topic}")
        
        # Generate caption
        caption = self.generate_caption(topic)
        logger.info(f"Generated caption: {caption[:100]}...")
        
        # Generate image prompt from caption
        image_prompt = self.generate_image_prompt(caption)
        logger.info(f"Generated image prompt: {image_prompt}")
        
        # Generate image
        filename = f"{topic.replace(' ', '_')}_{int(time.time())}.png"
        image_result = self.generate_midjourney_image(image_prompt, filename)
        
        if image_result["status"] == "success":
            logger.info(f"Successfully generated image: {image_result['image_path']}")
            return {
                "status": "success",
                "topic": topic,
                "caption": caption,
                "image_path": image_result["image_path"],
                "image_prompt": image_prompt,
                "image_analysis": image_result.get("analysis", {})
            }
        else:
            logger.warning(f"Failed to generate image: {image_result['message']}")
            
            # Fall back to a static image
            fallback_images = os.listdir(self.fallback_images_dir)
            if fallback_images:
                fallback_image = random.choice(fallback_images)
                fallback_path = os.path.join(self.fallback_images_dir, fallback_image)
                logger.info(f"Using fallback image: {fallback_path}")
                
                return {
                    "status": "partial_success",
                    "topic": topic,
                    "caption": caption,
                    "image_path": fallback_path,
                    "image_prompt": image_prompt,
                    "error": image_result["message"]
                }
            else:
                logger.error("No fallback images available")
                return {
                    "status": "error",
                    "topic": topic,
                    "caption": caption,
                    "image_prompt": image_prompt,
                    "error": f"Failed to generate image and no fallback images available: {image_result['message']}"
                }