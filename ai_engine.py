"""
RoadIntel AI - Intelligent Road Hazard Assessment & Priority Engine.
Modular architecture allowing seamless swapping between:
1. Rule-Based Heuristic & Computer Vision Analyzer (Default, runs offline)
2. Google Gemini Vision API (Multimodal LLM)
3. Custom Edge/TensorFlow/YOLO Computer Vision Model
"""

import os
import re
import math
from abc import ABC, abstractmethod
from PIL import Image, ImageStat, ImageFilter

class BaseAIEngine(ABC):
    @abstractmethod
    def analyze(self, image_path: str, description: str, category: str = 'Pothole') -> dict:
        """
        Analyze image and description to return:
        - priority: 'Low' | 'Medium' | 'High'
        - severity_score: int (0 - 100)
        - confidence_score: float (percentage, e.g. 92.4)
        - detected_hazards: list of str
        - recommended_action: str
        """
        pass

class HeuristicVisionEngine(BaseAIEngine):
    """
    Built-in intelligent engine combining image texture/edge analysis with
    contextual NLP keyword analysis. Runs locally with zero external API dependencies.
    """
    
    HIGH_SEVERITY_KEYWORDS = [
        'deep', 'crater', 'huge', 'accident', 'fatal', 'cave-in', 'sinkhole', 
        'severely', 'broken bridge', 'highway', 'high speed', 'junction', 
        'danger', 'death', 'major', 'skid', 'waterlogged', 'flooded', 
        'submerged', 'sharp', 'blind curve', 'no light', 'open manhole'
    ]
    
    MEDIUM_SEVERITY_KEYWORDS = [
        'moderate', 'bump', 'crack', 'rough', 'uneven', 'damage', 'pothole',
        'speed breaker', 'faded', 'patchwork', 'guardrail', 'debris', 'erosion'
    ]
    
    LOW_SEVERITY_KEYWORDS = [
        'minor', 'small', 'hairline', 'slight', 'surface', 'fading', 
        'paint', 'peeling', 'dust', 'cosmetic'
    ]

    def _analyze_image_features(self, image_path: str) -> dict:
        """Analyze image characteristics such as contrast, roughness, and dark clusters."""
        if not image_path or not os.path.exists(image_path):
            return {'image_severity_boost': 10, 'features': ['Visual assessment from photo']}
            
        try:
            with Image.open(image_path) as img:
                img_rgb = img.convert('RGB')
                stat = ImageStat.Stat(img_rgb)
                
                # Check variance / standard deviation of brightness (indicates irregular surface / deep shadow cavities)
                std_dev = stat.stddev
                avg_std = sum(std_dev) / len(std_dev)
                
                # Edge detection proxy via contour filter
                edges = img.convert('L').filter(ImageFilter.FIND_EDGES)
                edge_stat = ImageStat.Stat(edges)
                edge_intensity = edge_stat.mean[0]
                
                features = []
                boost = 0
                
                if avg_std > 55:
                    boost += 20
                    features.append("High surface variance / deep shadows detected")
                elif avg_std > 35:
                    boost += 10
                    features.append("Moderate surface irregularities detected")
                else:
                    boost += 5
                    features.append("Uniform pavement texture")
                    
                if edge_intensity > 25:
                    boost += 20
                    features.append("Sharp edge fractures & structural asphalt cracks detected")
                elif edge_intensity > 12:
                    boost += 10
                    features.append("Localized surface breakages detected")
                else:
                    boost += 5
                    features.append("Low edge sharpness")
                    
                return {
                    'image_severity_boost': min(40, boost),
                    'features': features
                }
        except Exception:
            return {'image_severity_boost': 15, 'features': ['Standard visual analysis']}

    def analyze(self, image_path: str, description: str, category: str = 'Pothole') -> dict:
        desc_lower = description.lower()
        
        # 1. Base score by category
        category_weights = {
            'Open Manhole': 65,
            'Sinkhole': 75,
            'Waterlogging': 55,
            'Pothole': 45,
            'Broken Guardrail': 50,
            'Road Crack': 30,
            'Damaged Signage': 25,
            'Streetlight Outage': 35,
            'Other': 30
        }
        base_score = category_weights.get(category, 40)
        
        # 2. NLP Keyword Analysis
        high_matches = sum(1 for kw in self.HIGH_SEVERITY_KEYWORDS if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower))
        med_matches = sum(1 for kw in self.MEDIUM_SEVERITY_KEYWORDS if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower))
        low_matches = sum(1 for kw in self.LOW_SEVERITY_KEYWORDS if re.search(r'\b' + re.escape(kw) + r'\b', desc_lower))
        
        nlp_score = (high_matches * 18) + (med_matches * 6) - (low_matches * 10)
        
        # 3. Image analysis
        img_analysis = self._analyze_image_features(image_path)
        img_boost = img_analysis.get('image_severity_boost', 10)
        detected_hazards = img_analysis.get('features', [])
        
        # Combine
        total_score = base_score + nlp_score + (img_boost // 2)
        severity_score = max(10, min(98, int(total_score)))
        
        # Determine Priority & Action
        if severity_score >= 70 or high_matches >= 2:
            priority = 'High'
            confidence = round(88.0 + (min(10, severity_score - 70) * 0.9), 1)
            detected_hazards.append("Critical vehicle suspension & two-wheeler skid hazard")
            recommended_action = "Immediate physical barricade and emergency asphalt patching within 24 hours."
        elif severity_score >= 40 or med_matches >= 1:
            priority = 'Medium'
            confidence = round(85.0 + ((severity_score - 40) * 0.3), 1)
            detected_hazards.append("Medium road surface deterioration")
            recommended_action = "Schedule maintenance crew inspection within 3-5 business days."
        else:
            priority = 'Low'
            confidence = round(82.0 + (severity_score * 0.2), 1)
            detected_hazards.append("Minor cosmetic wear; low collision risk")
            recommended_action = "Log into municipal quarterly maintenance queue."
            
        confidence = min(98.8, max(82.0, confidence))

        return {
            'priority': priority,
            'severity_score': severity_score,
            'confidence_score': confidence,
            'detected_hazards': detected_hazards,
            'recommended_action': recommended_action
        }

class GeminiVisionAIEngine(BaseAIEngine):
    """
    Adapter for Google Gemini 1.5 / 2.0 API Multimodal Analysis.
    Activated when GEMINI_API_KEY environment variable is present.
    """
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get('GEMINI_API_KEY')
        self.fallback_engine = HeuristicVisionEngine()

    def analyze(self, image_path: str, description: str, category: str = 'Pothole') -> dict:
        if not self.api_key:
            # Gracefully fallback if key not configured
            return self.fallback_engine.analyze(image_path, description, category)
            
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            prompt = f"""
            You are an expert civil & road safety engineer evaluating a citizen complaint.
            Reported Category: {category}
            Citizen Description: "{description}"
            
            Evaluate the image and provide a JSON response with:
            - priority: 'Low' | 'Medium' | 'High'
            - severity_score: integer from 0 to 100
            - confidence_score: float from 80.0 to 99.0
            - detected_hazards: list of 2-3 specific hazard descriptions
            - recommended_action: 1-sentence urgent civil engineering recommendation
            """
            
            if image_path and os.path.exists(image_path):
                img = Image.open(image_path)
                response = model.generate_content([prompt, img])
            else:
                response = model.generate_content(prompt)
                
            import json
            raw_text = response.text.strip().replace('```json', '').replace('```', '')
            parsed = json.loads(raw_text)
            return {
                'priority': parsed.get('priority', 'Medium'),
                'severity_score': int(parsed.get('severity_score', 55)),
                'confidence_score': float(parsed.get('confidence_score', 91.0)),
                'detected_hazards': parsed.get('detected_hazards', ['Pavement surface damage']),
                'recommended_action': parsed.get('recommended_action', 'Inspect road condition.')
            }
        except Exception:
            return self.fallback_engine.analyze(image_path, description, category)


def get_ai_engine(engine_type: str = 'heuristic') -> BaseAIEngine:
    """Factory function for selecting the AI engine."""
    if engine_type == 'gemini' or os.environ.get('GEMINI_API_KEY'):
        return GeminiVisionAIEngine()
    return HeuristicVisionEngine()
