import os
import logging
import requests
from PIL import Image
import numpy as np
from typing import List, Tuple, Optional
import cv2
import io

logger = logging.getLogger(__name__)

class ImageAnalyzer:
    """Helper class for analyzing and selecting the best image from multiple options"""
    
    def __init__(self):
        """Initialize the image analyzer"""
        self.metrics = {
            "sharpness": 0.3,  # Weight for sharpness score
            "contrast": 0.2,   # Weight for contrast score
            "detail": 0.3,     # Weight for detail score
            "noise": 0.2       # Weight for noise score (lower is better)
        }
    
    def download_image(self, url: str) -> Optional[Image.Image]:
        """Download image from URL and return as PIL Image"""
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                return Image.open(io.BytesIO(response.content))
            return None
        except Exception as e:
            logger.error(f"Error downloading image: {str(e)}")
            return None
    
    def calculate_sharpness(self, img_array: np.ndarray) -> float:
        """Calculate image sharpness using Laplacian variance"""
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        return cv2.Laplacian(gray, cv2.CV_64F).var()
    
    def calculate_contrast(self, img_array: np.ndarray) -> float:
        """Calculate image contrast"""
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        return gray.std()
    
    def calculate_detail(self, img_array: np.ndarray) -> float:
        """Calculate image detail level using edge detection"""
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        return np.mean(edges)
    
    def calculate_noise(self, img_array: np.ndarray) -> float:
        """Estimate image noise level"""
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        noise = cv2.fastNlMeansDenoising(gray)
        return np.mean(np.abs(gray - noise))
    
    def analyze_image(self, image_path_or_obj) -> dict:
        """
        Analyze a single image and return its quality metrics
        
        Args:
            image_path_or_obj: Either a file path or a PIL Image object
            
        Returns:
            Dictionary with quality metrics and overall score
        """
        try:
            # Load image if path is provided
            if isinstance(image_path_or_obj, str):
                if not os.path.exists(image_path_or_obj):
                    logger.error(f"Image file not found: {image_path_or_obj}")
                    return {"quality_score": 0.0}
                image = Image.open(image_path_or_obj)
            else:
                image = image_path_or_obj
            
            # Convert PIL Image to numpy array for OpenCV processing
            img_array = np.array(image)
            
            # Calculate individual metrics
            sharpness = self.calculate_sharpness(img_array)
            contrast = self.calculate_contrast(img_array)
            detail = self.calculate_detail(img_array)
            noise = self.calculate_noise(img_array)
            
            # Normalize scores
            max_sharpness = 1000  # Adjust these values based on typical ranges
            max_contrast = 100
            max_detail = 50
            max_noise = 30
            
            normalized_scores = {
                "sharpness": min(sharpness / max_sharpness, 1.0),
                "contrast": min(contrast / max_contrast, 1.0),
                "detail": min(detail / max_detail, 1.0),
                "noise": 1.0 - min(noise / max_noise, 1.0)  # Invert noise score
            }
            
            # Calculate weighted score
            total_score = sum(score * self.metrics[metric] 
                            for metric, score in normalized_scores.items())
            
            # Return all metrics and scores
            return {
                "raw_metrics": {
                    "sharpness": sharpness,
                    "contrast": contrast,
                    "detail": detail,
                    "noise": noise
                },
                "normalized_scores": normalized_scores,
                "quality_score": total_score
            }
            
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            return {"quality_score": 0.0}
    
    def select_best_image(self, image_urls: List[str]) -> Tuple[int, float]:
        """
        Analyze multiple images and select the best one
        
        Args:
            image_urls: List of image URLs to analyze
            
        Returns:
            Tuple of (best_index, best_score)
        """
        try:
            scores = []
            
            for url in image_urls:
                image = self.download_image(url)
                if image:
                    analysis = self.analyze_image(image)
                    scores.append(analysis["quality_score"])
                else:
                    scores.append(0.0)
            
            if not scores:
                return 0, 0.0
            
            best_index = scores.index(max(scores))
            return best_index, scores[best_index]
            
        except Exception as e:
            logger.error(f"Error selecting best image: {str(e)}")
            return 0, 0.0
    
    def split_grid_image(self, grid_image: Image.Image) -> List[Image.Image]:
        """Split a 2x2 grid image into individual images"""
        width, height = grid_image.size
        cell_width = width // 2
        cell_height = height // 2
        
        images = []
        for y in range(2):
            for x in range(2):
                left = x * cell_width
                top = y * cell_height
                right = left + cell_width
                bottom = top + cell_height
                
                cell = grid_image.crop((left, top, right, bottom))
                images.append(cell)
        
        return images
    
    def analyze_grid_image(self, grid_image: Image.Image) -> int:
        """
        Analyze a grid image and return the index of the best image (0-3)
        
        Args:
            grid_image: PIL Image containing 2x2 grid of images
            
        Returns:
            Index of the best image (0-3)
        """
        try:
            # Split grid into individual images
            images = self.split_grid_image(grid_image)
            
            # Analyze each image
            scores = [self.analyze_image(img)["quality_score"] for img in images]
            
            # Return index of best score
            return scores.index(max(scores))
            
        except Exception as e:
            logger.error(f"Error analyzing grid image: {str(e)}")
            return 0  # Default to first image if analysis fails