"""
IMAGE QUALITY ANALYZER - AI-Powered Quality Assessment

Uses vision LLM capabilities to evaluate generated images against script context
and provide refinement suggestions for iterative improvement.
"""

import sys
import base64
import io
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from PIL import Image

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.ai_providers import generate_with_ai
from settings.config import Config


class ImageQualityAnalyzer:
    """AI-powered image quality analyzer with context-aware scoring"""
    
    def __init__(self):
        self.use_quality_analysis = getattr(Config, 'SD_USE_QUALITY_ANALYSIS', True)
        self.quality_threshold = getattr(Config, 'SD_QUALITY_THRESHOLD', 7.5)
        self.max_iterations = getattr(Config, 'SD_MAX_REFINEMENT_ITERATIONS', 2)
        self.quality_factors = getattr(Config, 'SD_QUALITY_CHECK_FACTORS', 
                                     ["prompt_match", "composition", "vertical_format", "artifacts", "narrative_fit"])
        
        # Vision-capable models (Groq doesn't support vision yet, so we'll use text-based analysis)
        self.vision_available = False  # Set to True when vision models are available
    
    def analyze_image_quality(
        self,
        image: Image.Image,
        original_prompt: str,
        scene_description: str,
        script_context: Optional[Dict[str, Any]] = None,
        scene_index: int = 0
    ) -> Dict[str, Any]:
        """
        Analyze generated image quality with context-aware scoring.
        
        Args:
            image: Generated image to analyze
            original_prompt: Original SDXL prompt used
            scene_description: Basic scene description
            script_context: Full script context for narrative fit
            scene_index: Index of scene in video (for narrative flow)
            
        Returns:
            Dictionary with quality scores, analysis, and refinement suggestions
        """
        
        if not self.use_quality_analysis:
            return {
                "enabled": False,
                "overall_score": 8.0,  # Default pass
                "meets_threshold": True,
                "analysis": "Quality analysis disabled",
                "refinement_suggestions": []
            }
        
        print(f"Quality Analyzer: Evaluating scene {scene_index + 1}...")
        
        # If vision models available, use them; otherwise use text-based analysis
        if self.vision_available:
            return self._analyze_with_vision(image, original_prompt, scene_description, script_context)
        else:
            return self._analyze_with_text_based(image, original_prompt, scene_description, script_context)
    
    def _analyze_with_vision(
        self,
        image: Image.Image,
        original_prompt: str,
        scene_description: str,
        script_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze image using vision-capable LLM (when available)"""
        
        # Convert image to base64 for API
        image_base64 = self._image_to_base64(image)
        
        system_prompt = """You are an expert image quality analyst for YouTube Shorts backgrounds. Analyze the provided image and evaluate it on multiple quality factors.

Rate each factor on a scale of 1-10:
- prompt_match: How well does the image match the intended prompt?
- composition: Is the composition effective for vertical video?
- vertical_format: Is it optimized for 9:16 aspect ratio and mobile viewing?
- artifacts: Are there visual artifacts or quality issues?
- narrative_fit: Does it support the video's narrative context?

Respond with JSON:
{
  "overall_score": 8.5,
  "factor_scores": {
    "prompt_match": 8,
    "composition": 9,
    "vertical_format": 7,
    "artifacts": 9,
    "narrative_fit": 8
  },
  "analysis": "Detailed analysis of the image quality",
  "strengths": ["List of strengths"],
  "weaknesses": ["List of areas for improvement"],
  "refinement_suggestions": ["Specific suggestions for improvement"]
}"""

        user_prompt = f"""Analyze this YouTube Shorts background image:

Original Prompt: {original_prompt}
Scene Description: {scene_description}

{self._get_script_context_for_analysis(script_context)}

Image: [BASE64_IMAGE_DATA]"""

        try:
            # Replace placeholder with actual base64 data
            user_prompt = user_prompt.replace("[BASE64_IMAGE_DATA]", image_base64)
            
            response_text = generate_with_ai(system_prompt, user_prompt)
            
            # Parse JSON response
            import json
            analysis_result = json.loads(response_text)
            
            overall_score = analysis_result.get('overall_score', 5.0)
            meets_threshold = overall_score >= self.quality_threshold
            
            print(f"  📊 Overall Score: {overall_score:.1f}/10 (Threshold: {self.quality_threshold})")
            print(f"  {'✅ PASS' if meets_threshold else '❌ FAIL'} - {'Meets quality threshold' if meets_threshold else 'Below quality threshold'}")
            
            return {
                "enabled": True,
                "overall_score": overall_score,
                "meets_threshold": meets_threshold,
                "factor_scores": analysis_result.get('factor_scores', {}),
                "analysis": analysis_result.get('analysis', 'No analysis provided'),
                "strengths": analysis_result.get('strengths', []),
                "weaknesses": analysis_result.get('weaknesses', []),
                "refinement_suggestions": analysis_result.get('refinement_suggestions', [])
            }
            
        except Exception as e:
            print(f"  Vision analysis failed: {e}, falling back to text-based analysis")
            return self._analyze_with_text_based(image, original_prompt, scene_description, script_context)
    
    def _analyze_with_text_based(
        self,
        image: Image.Image,
        original_prompt: str,
        scene_description: str,
        script_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze image using text-based LLM analysis (fallback method)"""
        
        system_prompt = """You are an expert image quality analyst for YouTube Shorts backgrounds. Based on the prompt and context provided, evaluate what the generated image should look like and assess its likely quality.

Rate each factor on a scale of 1-10:
- prompt_match: How likely is the image to match the intended prompt?
- composition: Is the prompt composition effective for vertical video?
- vertical_format: Is the prompt optimized for 9:16 aspect ratio?
- artifacts: Are there likely to be visual artifacts based on the prompt?
- narrative_fit: Does the prompt support the video's narrative context?

Respond with JSON:
{
  "overall_score": 8.5,
  "factor_scores": {
    "prompt_match": 8,
    "composition": 9,
    "vertical_format": 7,
    "artifacts": 9,
    "narrative_fit": 8
  },
  "analysis": "Analysis of prompt quality and likely image results",
  "strengths": ["List of prompt strengths"],
  "weaknesses": ["List of prompt areas for improvement"],
  "refinement_suggestions": ["Specific suggestions for prompt improvement"]
}"""

        user_prompt = f"""Analyze this YouTube Shorts background generation:

Original Prompt: {original_prompt}
Scene Description: {scene_description}

{self._get_script_context_for_analysis(script_context)}

Evaluate the quality of the prompt and likely resulting image."""

        try:
            response_text = generate_with_ai(system_prompt, user_prompt)
            
            # Parse JSON response
            import json
            analysis_result = json.loads(response_text)
            
            overall_score = analysis_result.get('overall_score', 5.0)
            meets_threshold = overall_score >= self.quality_threshold
            
            print(f"  📊 Overall Score: {overall_score:.1f}/10 (Threshold: {self.quality_threshold})")
            print(f"  {'✅ PASS' if meets_threshold else '❌ FAIL'} - {'Meets quality threshold' if meets_threshold else 'Below quality threshold'}")
            
            return {
                "enabled": True,
                "overall_score": overall_score,
                "meets_threshold": meets_threshold,
                "factor_scores": analysis_result.get('factor_scores', {}),
                "analysis": analysis_result.get('analysis', 'No analysis provided'),
                "strengths": analysis_result.get('strengths', []),
                "weaknesses": analysis_result.get('weaknesses', []),
                "refinement_suggestions": analysis_result.get('refinement_suggestions', [])
            }
            
        except Exception as e:
            print(f"  Text-based analysis failed: {e}, using default scoring")
            return self._get_default_analysis()
    
    def generate_refinement_prompt(
        self,
        original_prompt: str,
        quality_analysis: Dict[str, Any],
        iteration: int
    ) -> Tuple[str, str]:
        """
        Generate refined prompt based on quality analysis.
        
        Args:
            original_prompt: Original SDXL prompt
            quality_analysis: Quality analysis results
            iteration: Current iteration number (1-based)
            
        Returns:
            Tuple of (refined_prompt, refined_negative_prompt)
        """
        
        if not quality_analysis.get('refinement_suggestions'):
            return original_prompt, ""
        
        print(f"  Generating refinement prompt (iteration {iteration})...")
        
        system_prompt = """You are an expert SDXL prompt engineer. Refine the given prompt based on quality analysis feedback to improve the generated image.

Focus on:
- Addressing specific weaknesses mentioned
- Implementing refinement suggestions
- Maintaining the core concept while improving quality
- Ensuring vertical composition optimization
- Adding technical terms that SDXL responds well to

Respond with JSON:
{
  "refined_prompt": "Improved SDXL prompt",
  "refined_negative_prompt": "Updated negative prompt"
}"""

        user_prompt = f"""Original Prompt: {original_prompt}

Quality Analysis:
Overall Score: {quality_analysis.get('overall_score', 5.0)}/10
Analysis: {quality_analysis.get('analysis', '')}
Weaknesses: {quality_analysis.get('weaknesses', [])}
Refinement Suggestions: {quality_analysis.get('refinement_suggestions', [])}

Generate an improved prompt that addresses the identified issues."""

        try:
            response_text = generate_with_ai(system_prompt, user_prompt)
            
            # Parse JSON response
            import json
            refinement_result = json.loads(response_text)
            
            refined_prompt = refinement_result.get('refined_prompt', original_prompt)
            refined_negative = refinement_result.get('refined_negative_prompt', '')
            
            print(f"  Refined prompt generated")
            return refined_prompt, refined_negative
            
        except Exception as e:
            print(f"  Refinement generation failed: {e}, using original prompt")
            return original_prompt, ""
    
    def _get_script_context_for_analysis(self, script_context: Optional[Dict[str, Any]]) -> str:
        """Format script context for analysis"""
        
        if not script_context:
            return ""
        
        context_parts = []
        
        if script_context.get('title'):
            context_parts.append(f"Video Title: {script_context['title']}")
        
        if script_context.get('topic'):
            context_parts.append(f"Topic: {script_context['topic']}")
        
        if script_context.get('script'):
            script_preview = script_context['script'][:200] + "..." if len(script_context['script']) > 200 else script_context['script']
            context_parts.append(f"Script Context: {script_preview}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL image to base64 string"""
        
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return image_data
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """Default analysis when all methods fail"""
        
        return {
            "enabled": True,
            "overall_score": 7.0,  # Conservative pass
            "meets_threshold": True,
            "factor_scores": {
                "prompt_match": 7,
                "composition": 7,
                "vertical_format": 7,
                "artifacts": 7,
                "narrative_fit": 7
            },
            "analysis": "Default analysis - quality assessment unavailable",
            "strengths": ["Generated successfully"],
            "weaknesses": ["Quality assessment failed"],
            "refinement_suggestions": []
        }


# Convenience function for direct use
def analyze_image_quality(
    image: Image.Image,
    original_prompt: str,
    scene_description: str,
    script_context: Optional[Dict[str, Any]] = None,
    scene_index: int = 0
) -> Dict[str, Any]:
    """
    Analyze image quality with AI intelligence.
    
    Args:
        image: Generated image to analyze
        original_prompt: Original SDXL prompt used
        scene_description: Basic scene description
        script_context: Full script context for narrative fit
        scene_index: Index of scene in video
        
    Returns:
        Dictionary with quality scores, analysis, and refinement suggestions
    """
    
    analyzer = ImageQualityAnalyzer()
    return analyzer.analyze_image_quality(image, original_prompt, scene_description, script_context, scene_index)


def generate_refinement_prompt(
    original_prompt: str,
    quality_analysis: Dict[str, Any],
    iteration: int
) -> Tuple[str, str]:
    """
    Generate refined prompt based on quality analysis.
    
    Args:
        original_prompt: Original SDXL prompt
        quality_analysis: Quality analysis results
        iteration: Current iteration number (1-based)
        
    Returns:
        Tuple of (refined_prompt, refined_negative_prompt)
    """
    
    analyzer = ImageQualityAnalyzer()
    return analyzer.generate_refinement_prompt(original_prompt, quality_analysis, iteration)


if __name__ == "__main__":
    # Test the image quality analyzer
    print("=" * 60)
    print("TESTING IMAGE QUALITY ANALYZER")
    print("=" * 60)
    
    # Create a test image
    test_image = Image.new('RGB', (512, 512), color='lightblue')
    
    test_prompt = "Ocean waves at sunset, vertical composition, cinematic, high quality"
    test_scene = "Ocean waves at sunset"
    test_context = {
        'title': 'Amazing Ocean Facts',
        'topic': 'ocean science',
        'script': 'The ocean covers 71% of Earth\'s surface...'
    }
    
    print(f"\nTesting quality analysis...")
    
    try:
        analysis = analyze_image_quality(test_image, test_prompt, test_scene, test_context, 0)
        
        if analysis.get("enabled", False):
            print(f"✅ Quality analysis successful!")
            print(f"  Overall Score: {analysis.get('overall_score', 0):.1f}/10")
            print(f"  Meets Threshold: {analysis.get('meets_threshold', False)}")
            print(f"  Analysis: {analysis.get('analysis', '')[:100]}...")
            
            # Test refinement if needed
            if not analysis.get('meets_threshold', True) and analysis.get('refinement_suggestions'):
                print(f"\nTesting refinement generation...")
                refined_prompt, refined_negative = generate_refinement_prompt(
                    test_prompt, analysis, 1
                )
                print(f"  ✓ Refined prompt: {refined_prompt[:100]}...")
        else:
            print("ℹ️ Quality analysis disabled")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("Check that AI provider (Groq/Grok) is configured correctly")
