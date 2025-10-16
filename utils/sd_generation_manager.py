"""
Stable Diffusion Generation Manager

Unified interface for generating AI backgrounds using both WebUI API and diffusers library.
Eliminates code duplication and provides consistent functionality across both methods.
"""

import os
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple, Union
import torch

from settings.config import Config
from utils.gpu_manager import get_gpu_manager, gpu_memory_context, check_gpu_compatibility, reset_gpu_state
from utils.performance_optimizer import performance_optimizer
from utils.resource_manager import GPUResource, ManagedResource, get_resource_manager

logger = logging.getLogger(__name__)

# Import WebUI API helper
try:
    from helpers.sd_webui_api import SDWebUIAPI
    WEBUI_AVAILABLE = True
except ImportError:
    WEBUI_AVAILABLE = False
    logger.warning("WebUI API module not available")

# Import AI enhancement modules
try:
    from helpers.ai_prompt_optimizer import optimize_prompts_with_ai
    from helpers.controlnet_processor import process_control_images
    from helpers.image_quality_analyzer import analyze_image_quality, generate_refinement_prompt
    AI_ENHANCEMENTS_AVAILABLE = True
except ImportError:
    AI_ENHANCEMENTS_AVAILABLE = False
    logger.warning("AI enhancement modules not available")


class SDGenerationError(Exception):
    """Base exception for SD generation errors"""
    pass


class SDGenerationManager:
    """
    Unified manager for Stable Diffusion generation using both WebUI and diffusers.
    
    Provides consistent interface and eliminates code duplication between methods.
    """
    
    def __init__(self, method: str = "auto", use_enhancements: bool = True):
        """
        Initialize SD Generation Manager.
        
        Args:
            method: Generation method ("webui", "diffusers", or "auto")
            use_enhancements: Whether to use AI enhancements (prompt optimization, quality analysis)
        """
        self.method = method.lower() if method != "auto" else self._detect_best_method()
        self.use_enhancements = use_enhancements and AI_ENHANCEMENTS_AVAILABLE
        self.gpu_manager = get_gpu_manager()
        self.resource_manager = get_resource_manager()
        self._webui_api = None
        self._diffusers_pipe = None
        self._gpu_resource = None
        
        logger.info(f"SD Generation Manager initialized: method={self.method}, enhancements={self.use_enhancements}")
    
    def _detect_best_method(self) -> str:
        """Detect the best available method for SD generation."""
        if WEBUI_AVAILABLE and getattr(Config, 'SD_WEBUI_HOST', None):
            return "webui"
        return "diffusers"
    
    def _get_webui_api(self) -> SDWebUIAPI:
        """Get or create WebUI API instance."""
        if self._webui_api is None:
            if not WEBUI_AVAILABLE:
                raise SDGenerationError("WebUI API not available")
            self._webui_api = SDWebUIAPI(
                host=Config.SD_WEBUI_HOST,
                timeout=Config.SD_WEBUI_TIMEOUT
            )
        return self._webui_api
    
    def _get_diffusers_pipe(self):
        """Get or create diffusers pipeline."""
        if self._diffusers_pipe is None:
            try:
                from diffusers import DiffusionPipeline
            except ImportError:
                raise SDGenerationError("diffusers package not installed")
            
            device = "cuda" if check_gpu_compatibility()[0] else "cpu"
            if device == "cpu":
                raise SDGenerationError("GPU required for diffusers method")
            
            logger.info(f"Loading SDXL model: {Config.STABLE_DIFFUSION_MODEL}")
            
            with gpu_memory_context():
                self._diffusers_pipe = DiffusionPipeline.from_pretrained(
                    Config.STABLE_DIFFUSION_MODEL,
                    torch_dtype=torch.float16,
                    use_safetensors=True,
                    variant="fp16" if device == "cuda" else None,
                ).to(device)
                
                # Enable memory optimizations
                if Config.SD_ATTENTION_SLICING:
                    self._diffusers_pipe.enable_attention_slicing(1)
                    logger.info("Enabled attention slicing")
                
                if Config.SD_LOW_MEMORY_MODE:
                    self._diffusers_pipe.enable_vae_slicing()
                    logger.info("Enabled VAE slicing")
        
        return self._diffusers_pipe
    
    def _optimize_prompts(self, scene_descriptions: List[str], script_data: Optional[Dict] = None) -> List[Tuple[str, str]]:
        """Optimize prompts using AI enhancement if available."""
        if not self.use_enhancements:
            # Fallback to simple prompts
            optimized_prompts = []
            for scene_desc in scene_descriptions:
                optimized_prompts.append((
                    f"{scene_desc}, vertical composition, portrait orientation, "
                    f"cinematic, high quality, detailed, vibrant colors, "
                    f"mobile optimized, 9:16 aspect ratio",
                    "blurry, low quality, distorted, ugly, bad composition, horizontal"
                ))
            return optimized_prompts
        
        logger.info("🤖 AI Enhancement: Optimizing prompts with narrative intelligence...")
        try:
            return optimize_prompts_with_ai(scene_descriptions, script_data)
        except Exception as e:
            logger.warning(f"AI prompt optimization failed: {e}, using fallback prompts")
            # Fallback to simple prompts
            optimized_prompts = []
            for scene_desc in scene_descriptions:
                optimized_prompts.append((
                    f"{scene_desc}, vertical composition, portrait orientation, "
                    f"cinematic, high quality, detailed, vibrant colors, "
                    f"mobile optimized, 9:16 aspect ratio",
                    "blurry, low quality, distorted, ugly, bad composition, horizontal"
                ))
            return optimized_prompts
    
    def _analyze_and_refine_image(
        self, 
        image: Any, 
        prompt: str, 
        scene_desc: str, 
        script_data: Optional[Dict] = None,
        scene_index: int = 0,
        generation_method: str = "webui"
    ) -> Any:
        """Analyze image quality and refine if needed."""
        if not self.use_enhancements:
            return image
        
        logger.info(f"🔍 Quality Analysis: Evaluating generated image...")
        
        try:
            quality_analysis = analyze_image_quality(
                image=image,
                original_prompt=prompt,
                scene_description=scene_desc,
                script_context=script_data,
                scene_index=scene_index
            )
            
            if quality_analysis.get('meets_threshold', True):
                logger.info(f"✅ Image meets quality threshold ({quality_analysis.get('overall_score', 0):.1f}/10)")
                return image
            
            logger.warning(f"⚠️ Quality below threshold ({quality_analysis.get('overall_score', 0):.1f}/10)")
            
            # Try refinement
            max_iterations = getattr(Config, 'SD_MAX_REFINEMENT_ITERATIONS', 2)
            for iteration in range(1, max_iterations + 1):
                logger.info(f"🔄 Refinement iteration {iteration}/{max_iterations}...")
                
                refined_prompt, refined_negative = generate_refinement_prompt(
                    prompt, quality_analysis, iteration
                )
                
                # Regenerate with refined prompt
                if generation_method == "webui":
                    refined_image = self._generate_webui_image(refined_prompt, refined_negative)
                else:
                    refined_image = self._generate_diffusers_image(refined_prompt, refined_negative)
                
                if refined_image:
                    refined_analysis = analyze_image_quality(
                        image=refined_image,
                        original_prompt=refined_prompt,
                        scene_description=scene_desc,
                        script_context=script_data,
                        scene_index=scene_index
                    )
                    
                    if refined_analysis.get('meets_threshold', False):
                        logger.info(f"✅ Refined image meets quality threshold!")
                        return refined_image
                    else:
                        logger.warning(f"⚠️ Refinement {iteration} still below threshold")
                        if iteration < max_iterations:
                            quality_analysis = refined_analysis
                else:
                    logger.warning(f"❌ Refinement {iteration} failed to generate")
            
            return image  # Return original if refinement failed
            
        except Exception as e:
            logger.warning(f"Quality analysis failed: {e}, using original image")
            return image
    
    def _generate_webui_image(self, prompt: str, negative_prompt: str, controlnet_data: Optional[Dict] = None) -> Optional[Any]:
        """Generate image using WebUI API."""
        try:
            api = self._get_webui_api()
            return api.generate_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=Config.SD_GENERATION_WIDTH,
                height=Config.SD_GENERATION_HEIGHT,
                steps=Config.SD_INFERENCE_STEPS,
                cfg_scale=Config.SD_GUIDANCE_SCALE,
                sampler=Config.SD_WEBUI_SAMPLER,
                controlnet_units=controlnet_data.get("controlnet_units", []) if controlnet_data else None
            )
        except Exception as e:
            logger.error(f"WebUI generation failed: {e}")
            return None
    
    def _generate_diffusers_image(self, prompt: str, negative_prompt: str) -> Optional[Any]:
        """Generate image using diffusers pipeline."""
        try:
            pipe = self._get_diffusers_pipe()
            
            # Clear GPU memory before generation
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                torch.cuda.ipc_collect()
            
            # Generate image
            result = pipe(
                prompt,
                height=Config.SD_GENERATION_HEIGHT,
                width=Config.SD_GENERATION_WIDTH,
                num_inference_steps=Config.SD_INFERENCE_STEPS,
                guidance_scale=Config.SD_GUIDANCE_SCALE,
                negative_prompt=negative_prompt,
            )
            
            return result.images[0] if result.images else None
            
        except Exception as e:
            logger.error(f"Diffusers generation failed: {e}")
            return None
    
    def _upscale_image(self, image: Any) -> Any:
        """Upscale image to final resolution if needed."""
        if (Config.SD_GENERATION_WIDTH != Config.VIDEO_WIDTH or 
            Config.SD_GENERATION_HEIGHT != Config.VIDEO_HEIGHT):
            
            from PIL import Image as PILImage
            image = image.resize(
                (Config.VIDEO_WIDTH, Config.VIDEO_HEIGHT), 
                PILImage.Resampling.LANCZOS
            )
            logger.info(f"✓ Upscaled to {Config.VIDEO_WIDTH}x{Config.VIDEO_HEIGHT}")
        
        return image
    
    def _save_image(self, image: Any, index: int, temp_dir: Path) -> str:
        """Save image to disk and return path."""
        image_path = temp_dir / f"ai_background_{index}.png"
        image.save(image_path)
        logger.info(f"✓ Saved: {image_path.name}")
        return str(image_path)
    
    def generate_backgrounds(
        self, 
        scene_descriptions: List[str], 
        script_data: Optional[Dict] = None,
        duration_per_scene: float = 3.0
    ) -> List[str]:
        """
        Generate AI backgrounds using the configured method.
        
        Args:
            scene_descriptions: List of text descriptions for each scene
            script_data: Full script context from UI
            duration_per_scene: How long each scene should display
            
        Returns:
            List of paths to generated images
        """
        logger.info(f"Generating AI backgrounds using {self.method} method...")
        
        # Optimize scene count for performance
        max_scenes = getattr(Config, 'SD_MAX_SCENES', 3)
        optimized_scenes = scene_descriptions[:max_scenes]
        if len(scene_descriptions) > max_scenes:
            logger.info(f"OPTIMIZATION: Reduced from {len(scene_descriptions)} to {max_scenes} scenes")
        
        # Optimize prompts
        optimized_prompts = self._optimize_prompts(optimized_scenes, script_data)
        
        # Prepare output
        image_paths = []
        temp_dir = Path(Config.TEMP_DIR)
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        previous_image = None  # For ControlNet continuity
        
        try:
            for i, (scene_desc, prompt_data) in enumerate(zip(optimized_scenes, optimized_prompts)):
                logger.info(f"[Scene {i+1}/{len(optimized_scenes)}]")
                
                # Unpack prompt data
                if isinstance(prompt_data, tuple) and len(prompt_data) == 2:
                    prompt, negative_prompt = prompt_data
                else:
                    prompt = prompt_data
                    negative_prompt = "blurry, low quality, distorted, ugly, bad composition, horizontal"
                
                # Process ControlNet if available
                controlnet_data = None
                if (self.use_enhancements and 
                    getattr(Config, 'SD_USE_CONTROLNET', True) and 
                    self.method == "webui"):
                    
                    logger.info(f"🎯 ControlNet: Generating control images for visual guidance...")
                    controlnet_data = process_control_images(
                        reference_image=None,
                        previous_image=previous_image
                    )
                
                # Generate image
                if self.method == "webui":
                    image = self._generate_webui_image(prompt, negative_prompt, controlnet_data)
                else:
                    image = self._generate_diffusers_image(prompt, negative_prompt)
                
                if not image:
                    logger.error(f"✗ Failed to generate scene {i+1}")
                    continue
                
                # Analyze and refine if needed
                image = self._analyze_and_refine_image(
                    image, prompt, scene_desc, script_data, i, self.method
                )
                
                # Upscale and save
                image = self._upscale_image(image)
                image_path = self._save_image(image, i, temp_dir)
                image_paths.append(image_path)
                
                # Store for ControlNet continuity
                previous_image = image
                
                # Cleanup
                del image
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
        
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            if self.method == "webui" and WEBUI_AVAILABLE:
                logger.info("Falling back to diffusers method...")
                fallback_manager = SDGenerationManager("diffusers", self.use_enhancements)
                return fallback_manager.generate_backgrounds(scene_descriptions, script_data, duration_per_scene)
            raise SDGenerationError(f"All generation methods failed: {e}")
        
        finally:
            # Cleanup resources
            self.cleanup()
        
        logger.info(f"✓ Generated {len(image_paths)} AI backgrounds")
        return image_paths
    
    def cleanup(self):
        """Clean up resources."""
        # Cleanup diffusers pipeline
        if self._diffusers_pipe is not None:
            try:
                if torch.cuda.is_available():
                    self._diffusers_pipe = self._diffusers_pipe.to("cpu")
                del self._diffusers_pipe
                self._diffusers_pipe = None
                logger.info("Cleaned up diffusers pipeline")
            except Exception as e:
                logger.warning(f"Error during diffusers cleanup: {e}")
        
        # Cleanup GPU resource
        if self._gpu_resource is not None:
            try:
                self._gpu_resource.cleanup()
                self._gpu_resource = None
                logger.info("Cleaned up GPU resource")
            except Exception as e:
                logger.warning(f"Error during GPU cleanup: {e}")
        
        # Cleanup WebUI API
        if self._webui_api is not None:
            try:
                self._webui_api = None
                logger.info("Cleaned up WebUI API")
            except Exception as e:
                logger.warning(f"Error during WebUI cleanup: {e}")


def create_sd_manager(method: str = "auto", use_enhancements: bool = True) -> SDGenerationManager:
    """Create a new SD Generation Manager instance."""
    return SDGenerationManager(method, use_enhancements)


@performance_optimizer.cached_function(
    cache_key_func=lambda scene_descriptions, duration_per_scene, method, use_enhancements: 
        f"ai_backgrounds:{method}:{use_enhancements}:{hash(tuple(scene_descriptions))}:{duration_per_scene}",
    use_disk=True,
    ttl=7200  # 2 hour cache
)
def generate_ai_backgrounds_unified(
    scene_descriptions: List[str], 
    script_data: Optional[Dict] = None,
    duration_per_scene: float = 3.0,
    method: str = "auto",
    use_enhancements: bool = True
) -> List[str]:
    """
    Unified function for generating AI backgrounds.
    
    This replaces the separate WebUI and diffusers functions with a single,
    consistent interface that eliminates code duplication.
    
    Args:
        scene_descriptions: List of text descriptions for each scene
        script_data: Full script context from UI
        duration_per_scene: How long each scene should display
        method: Generation method ("webui", "diffusers", or "auto")
        use_enhancements: Whether to use AI enhancements
        
    Returns:
        List of paths to generated images
    """
    manager = create_sd_manager(method, use_enhancements)
    return manager.generate_backgrounds(scene_descriptions, script_data, duration_per_scene)
