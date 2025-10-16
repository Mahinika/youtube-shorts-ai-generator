"""
AI PROMPT OPTIMIZER - Context-Aware SDXL Enhancement

Receives full script context from Script Generator UI and transforms basic scene descriptions
into SDXL-optimized prompts with narrative intelligence and style consistency.
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.ai_providers import generate_with_ai
from settings.config import Config


class AIPromptOptimizer:
    """Context-aware prompt optimizer that enhances scene descriptions with SDXL intelligence"""
    
    def __init__(self):
        self.provider = getattr(Config, 'SD_PROMPT_OPTIMIZER_PROVIDER', 'groq').lower()
        self.context_aware = getattr(Config, 'SD_PROMPT_CONTEXT_AWARE', True)
        self.vertical_optimization = True  # Always optimize for 9:16 YouTube Shorts
        
    def optimize_prompts_with_context(
        self, 
        scene_descriptions: List[str], 
        script_data: Optional[Dict] = None
    ) -> List[Tuple[str, str]]:
        """
        Optimize scene descriptions with full script context for SDXL generation.
        
        Args:
            scene_descriptions: List of basic scene descriptions from script
            script_data: Full script context (title, script, topic, etc.)
            
        Returns:
            List of (optimized_prompt, negative_prompt) tuples
        """
        
        if not scene_descriptions:
            return []
            
        print("AI Prompt Optimizer: Enhancing scene descriptions with narrative intelligence...")
        
        # If no context available, do basic optimization
        if not script_data or not self.context_aware:
            print("  📝 Using basic optimization (no script context)")
            return self._basic_optimization(scene_descriptions)
        
        # Extract context information
        video_title = script_data.get('title', '')
        narrator_script = script_data.get('script', '')
        video_topic = script_data.get('topic', '')
        
        print(f"  📖 Context: '{video_title}' - {len(scene_descriptions)} scenes")
        
        # Analyze narrative flow and style
        narrative_analysis = self._analyze_narrative_context(
            video_title, narrator_script, video_topic
        )
        
        # Optimize each scene with context
        optimized_prompts = []
        for i, scene_desc in enumerate(scene_descriptions):
            print(f"  Optimizing scene {i+1}/{len(scene_descriptions)}: {scene_desc[:50]}...")
            
            # Determine scene role in narrative
            scene_role = self._determine_scene_role(i, len(scene_descriptions))
            
            # Generate optimized prompt
            optimized_prompt, negative_prompt = self._optimize_single_scene(
                scene_desc, 
                narrative_analysis, 
                scene_role,
                video_title
            )
            
            optimized_prompts.append((optimized_prompt, negative_prompt))
        
        print(f"  Optimized {len(optimized_prompts)} prompts with AI intelligence")
        return optimized_prompts
    
    def _analyze_narrative_context(
        self, 
        title: str, 
        script: str, 
        topic: str
    ) -> Dict[str, str]:
        """Analyze the narrative context to understand video style and mood"""
        
        system_prompt = """You are an expert visual storytelling analyst. Analyze the provided video content to determine the optimal visual style for AI image generation.

Focus on:
- Overall mood and tone
- Visual style (cinematic, documentary, educational, dramatic)
- Color palette preferences
- Lighting style
- Composition approach
- Technical quality level

Respond with a JSON object containing: mood, visual_style, color_palette, lighting, composition, quality_level."""

        user_prompt = f"""Analyze this YouTube Short content:

Title: {title}
Topic: {topic}
Script: {script[:500]}...

Determine the optimal visual style for background images that will support this narration."""

        try:
            analysis_text = generate_with_ai(system_prompt, user_prompt)
            
            # Parse JSON response (fallback to defaults if parsing fails)
            try:
                import json
                analysis = json.loads(analysis_text)
                return {
                    'mood': analysis.get('mood', 'engaging'),
                    'visual_style': analysis.get('visual_style', 'cinematic'),
                    'color_palette': analysis.get('color_palette', 'vibrant'),
                    'lighting': analysis.get('lighting', 'dramatic'),
                    'composition': analysis.get('composition', 'dynamic'),
                    'quality_level': analysis.get('quality_level', 'high')
                }
            except (json.JSONDecodeError, AttributeError):
                print("  ⚠️ Could not parse narrative analysis, using defaults")
                return self._get_default_narrative_analysis()
                
        except Exception as e:
            print(f"  ⚠️ Narrative analysis failed: {e}, using defaults")
            return self._get_default_narrative_analysis()
    
    def _determine_scene_role(self, scene_index: int, total_scenes: int) -> str:
        """Determine the role of this scene in the narrative flow"""
        
        if total_scenes == 1:
            return "complete_story"
        elif scene_index == 0:
            return "opener"  # Hook the viewer
        elif scene_index == total_scenes - 1:
            return "climax"  # Strong finish
        elif scene_index < total_scenes / 2:
            return "build"  # Build interest
        else:
            return "development"  # Develop the story
    
    def _optimize_single_scene(
        self, 
        scene_desc: str, 
        narrative_analysis: Dict[str, str],
        scene_role: str,
        video_title: str
    ) -> Tuple[str, str]:
        """Optimize a single scene description with full context"""
        
        system_prompt = """You are an expert SDXL prompt engineer specializing in YouTube Shorts backgrounds.

Transform the given scene description into an optimized SDXL prompt that will generate high-quality vertical background images.

CRITICAL REQUIREMENTS:
- Generate prompts that work well with SDXL models
- Always include vertical composition (9:16 aspect ratio)
- Use cinematic, professional terminology
- Include technical photography terms (lighting, camera angles, depth of field)
- Add art style descriptors that SDXL understands
- Optimize for YouTube Shorts mobile viewing

RESPOND WITH JSON:
{
  "optimized_prompt": "detailed SDXL prompt",
  "negative_prompt": "what to avoid in this scene"
}"""

        user_prompt = f"""Scene Description: {scene_desc}

Video Title: {video_title}
Scene Role: {scene_role}
Visual Style: {narrative_analysis['visual_style']}
Mood: {narrative_analysis['mood']}
Color Palette: {narrative_analysis['color_palette']}
Lighting: {narrative_analysis['lighting']}
Composition: {narrative_analysis['composition']}

Generate an optimized SDXL prompt for this scene."""

        try:
            response_text = generate_with_ai(system_prompt, user_prompt)
            
            # Parse JSON response
            try:
                import json
                result = json.loads(response_text)
                
                optimized_prompt = result.get('optimized_prompt', scene_desc)
                negative_prompt = result.get('negative_prompt', '')
                
                # Add standard vertical optimization if not already present
                if 'vertical' not in optimized_prompt.lower() and 'portrait' not in optimized_prompt.lower():
                    optimized_prompt += ", vertical composition, portrait orientation, 9:16 aspect ratio"
                
                # Add standard quality boosters
                quality_boosters = [
                    "high quality", "detailed", "cinematic", "professional photography",
                    "vibrant colors", "sharp focus", "mobile optimized"
                ]
                
                for booster in quality_boosters:
                    if booster not in optimized_prompt.lower():
                        optimized_prompt += f", {booster}"
                
                # Ensure negative prompt has standard avoidances
                standard_negatives = [
                    "blurry", "low quality", "distorted", "ugly", "bad composition",
                    "horizontal", "landscape orientation", "text", "watermark"
                ]
                
                for neg in standard_negatives:
                    if neg not in negative_prompt.lower():
                        if negative_prompt:
                            negative_prompt += ", " + neg
                        else:
                            negative_prompt = neg
                
                return optimized_prompt, negative_prompt
                
            except (json.JSONDecodeError, AttributeError):
                print(f"    ⚠️ Could not parse AI response, using fallback optimization")
                return self._fallback_optimization(scene_desc, narrative_analysis)
                
        except Exception as e:
            print(f"    ⚠️ AI optimization failed: {e}, using fallback")
            return self._fallback_optimization(scene_desc, narrative_analysis)
    
    def _basic_optimization(self, scene_descriptions: List[str]) -> List[Tuple[str, str]]:
        """Basic optimization without script context"""
        
        optimized_prompts = []
        
        for scene_desc in scene_descriptions:
            # Simple enhancement with standard SDXL terms
            enhanced_prompt = (
                f"{scene_desc}, vertical composition, portrait orientation, "
                f"cinematic, high quality, detailed, vibrant colors, "
                f"mobile optimized, 9:16 aspect ratio, professional photography"
            )
            
            negative_prompt = (
                "blurry, low quality, distorted, ugly, bad composition, "
                "horizontal, landscape orientation, text, watermark"
            )
            
            optimized_prompts.append((enhanced_prompt, negative_prompt))
        
        return optimized_prompts
    
    def _fallback_optimization(
        self, 
        scene_desc: str, 
        narrative_analysis: Dict[str, str]
    ) -> Tuple[str, str]:
        """Fallback optimization when AI fails"""
        
        # Apply narrative analysis to enhance the prompt
        style_terms = []
        
        if narrative_analysis['visual_style'] == 'cinematic':
            style_terms.extend(['cinematic lighting', 'dramatic composition'])
        elif narrative_analysis['visual_style'] == 'documentary':
            style_terms.extend(['documentary style', 'natural lighting'])
        elif narrative_analysis['visual_style'] == 'educational':
            style_terms.extend(['clear composition', 'professional lighting'])
        
        if narrative_analysis['mood'] == 'dramatic':
            style_terms.extend(['dramatic lighting', 'high contrast'])
        elif narrative_analysis['mood'] == 'peaceful':
            style_terms.extend(['soft lighting', 'calm atmosphere'])
        elif narrative_analysis['mood'] == 'energetic':
            style_terms.extend(['dynamic composition', 'vibrant colors'])
        
        # Build enhanced prompt
        enhanced_prompt = scene_desc
        if style_terms:
            enhanced_prompt += ", " + ", ".join(style_terms)
        
        enhanced_prompt += ", vertical composition, portrait orientation, high quality, detailed, 9:16 aspect ratio"
        
        negative_prompt = "blurry, low quality, distorted, ugly, bad composition, horizontal, text, watermark"
        
        return enhanced_prompt, negative_prompt
    
    def _get_default_narrative_analysis(self) -> Dict[str, str]:
        """Default narrative analysis when AI analysis fails"""
        return {
            'mood': 'engaging',
            'visual_style': 'cinematic',
            'color_palette': 'vibrant',
            'lighting': 'dramatic',
            'composition': 'dynamic',
            'quality_level': 'high'
        }


# Convenience function for direct use
def optimize_prompts_with_ai(
    scene_descriptions: List[str], 
    script_data: Optional[Dict] = None
) -> List[Tuple[str, str]]:
    """
    Optimize scene descriptions with AI intelligence.
    
    Args:
        scene_descriptions: List of scene descriptions
        script_data: Full script context from UI
        
    Returns:
        List of (optimized_prompt, negative_prompt) tuples
    """
    
    optimizer = AIPromptOptimizer()
    return optimizer.optimize_prompts_with_context(scene_descriptions, script_data)


if __name__ == "__main__":
    # Test the AI prompt optimizer
    print("=" * 60)
    print("TESTING AI PROMPT OPTIMIZER")
    print("=" * 60)
    
    # Test with mock script data
    test_scenes = [
        "Ocean waves at sunset",
        "City skyline at night with neon lights",
        "Mountain landscape with dramatic clouds"
    ]
    
    test_script_data = {
        'title': 'Amazing Facts About Space Exploration',
        'script': 'Space exploration has revolutionized our understanding of the universe...',
        'topic': 'space exploration'
    }
    
    print(f"\nTesting with {len(test_scenes)} scenes...")
    
    try:
        optimized = optimize_prompts_with_ai(test_scenes, test_script_data)
        
        print(f"\n✅ Successfully optimized {len(optimized)} prompts!")
        
        for i, (prompt, negative) in enumerate(optimized):
            print(f"\nScene {i+1}:")
            print(f"  Prompt: {prompt[:100]}...")
            print(f"  Negative: {negative[:50]}...")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("Check that AI provider (Groq/Grok) is configured correctly")
