"""
STABLE DIFFUSION WEBUI API INTEGRATION

Provides API integration with AUTOMATIC1111's Stable Diffusion WebUI.
This allows using the WebUI's powerful features while keeping our existing workflow.
"""

import base64
import io
import json
import time
from pathlib import Path
from typing import Optional, List

import requests
from PIL import Image


class SDWebUIAPI:
    """Interface to AUTOMATIC1111 Stable Diffusion WebUI API"""
    
    def __init__(self, host: str = "http://127.0.0.1:7860", timeout: int = 300):
        """
        Initialize WebUI API client
        
        Args:
            host: WebUI API host URL (default: http://127.0.0.1:7860)
            timeout: Request timeout in seconds (default: 300 for slow generations)
        """
        self.host = host.rstrip('/')
        self.timeout = timeout
        self._check_connection()
    
    def _check_connection(self) -> bool:
        """Check if WebUI API is accessible"""
        try:
            response = requests.get(f"{self.host}/sdapi/v1/options", timeout=5)
            if response.status_code == 200:
                print(f"✓ Connected to Stable Diffusion WebUI at {self.host}")
                return True
        except requests.exceptions.RequestException:
            pass
        
        print(f"⚠ Warning: Cannot connect to WebUI at {self.host}")
        print("  Make sure the WebUI is running with --api flag")
        print("  Example: webui-user.bat --api")
        return False
    
    def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: int = 1080,
        height: int = 1920,
        steps: int = 20,
        cfg_scale: float = 7.5,
        sampler: str = "DPM++ 2M Karras",
        seed: int = -1,
    ) -> Optional[Image.Image]:
        """
        Generate a single image using the WebUI API
        
        Args:
            prompt: Positive prompt describing the image
            negative_prompt: Negative prompt (what to avoid)
            width: Image width in pixels (must be divisible by 8)
            height: Image height in pixels (must be divisible by 8)
            steps: Number of sampling steps (20-50 recommended)
            cfg_scale: Guidance scale (7-12 recommended)
            sampler: Sampling method (see WebUI for options)
            seed: Random seed (-1 for random)
        
        Returns:
            PIL Image or None if generation failed
        """
        
        # Validate dimensions
        if width % 8 != 0 or height % 8 != 0:
            raise ValueError("Width and height must be divisible by 8")
        
        # Build API request
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "sampler_name": sampler,
            "seed": seed,
            "n_iter": 1,
            "batch_size": 1,
        }
        
        try:
            print(f"  Generating via WebUI API ({width}x{height}, {steps} steps)...")
            start_time = time.time()
            
            response = requests.post(
                f"{self.host}/sdapi/v1/txt2img",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code != 200:
                print(f"  API Error: {response.status_code} - {response.text}")
                return None
            
            # Parse response
            result = response.json()
            
            # Decode base64 image
            if "images" in result and len(result["images"]) > 0:
                image_data = base64.b64decode(result["images"][0])
                image = Image.open(io.BytesIO(image_data))
                
                gen_time = time.time() - start_time
                print(f"  ✓ Generated in {gen_time:.1f}s")
                
                return image
            else:
                print("  Error: No images in API response")
                return None
                
        except requests.exceptions.Timeout:
            print(f"  Error: Generation timed out after {self.timeout}s")
            return None
        except Exception as e:
            print(f"  Error generating image: {e}")
            return None
    
    def generate_batch(
        self,
        prompts: List[str],
        negative_prompt: str = "",
        width: int = 1080,
        height: int = 1920,
        steps: int = 20,
        cfg_scale: float = 7.5,
        sampler: str = "DPM++ 2M Karras",
    ) -> List[Image.Image]:
        """
        Generate multiple images from a list of prompts
        
        Args:
            prompts: List of positive prompts
            negative_prompt: Common negative prompt for all images
            width: Image width
            height: Image height
            steps: Sampling steps
            cfg_scale: Guidance scale
            sampler: Sampling method
        
        Returns:
            List of PIL Images (may be shorter if some failed)
        """
        
        images = []
        for i, prompt in enumerate(prompts):
            print(f"\n[{i+1}/{len(prompts)}] {prompt[:60]}...")
            
            image = self.generate_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                steps=steps,
                cfg_scale=cfg_scale,
                sampler=sampler,
            )
            
            if image:
                images.append(image)
            else:
                print(f"  ⚠ Failed to generate image {i+1}")
        
        return images
    
    def get_models(self) -> List[str]:
        """Get list of available Stable Diffusion models"""
        try:
            response = requests.get(f"{self.host}/sdapi/v1/sd-models", timeout=10)
            if response.status_code == 200:
                models = response.json()
                return [model["title"] for model in models]
            return []
        except Exception as e:
            print(f"Error getting models: {e}")
            return []
    
    def get_samplers(self) -> List[str]:
        """Get list of available samplers"""
        try:
            response = requests.get(f"{self.host}/sdapi/v1/samplers", timeout=10)
            if response.status_code == 200:
                samplers = response.json()
                return [sampler["name"] for sampler in samplers]
            return []
        except Exception as e:
            print(f"Error getting samplers: {e}")
            return []
    
    def interrupt(self):
        """Interrupt current generation"""
        try:
            requests.post(f"{self.host}/sdapi/v1/interrupt", timeout=5)
            print("Generation interrupted")
        except Exception as e:
            print(f"Error interrupting: {e}")


def test_api():
    """Test the WebUI API connection and generation"""
    print("=" * 60)
    print("TESTING STABLE DIFFUSION WEBUI API")
    print("=" * 60)
    
    # Initialize API
    api = SDWebUIAPI()
    
    # Get available models
    print("\nAvailable models:")
    models = api.get_models()
    for model in models[:5]:  # Show first 5
        print(f"  - {model}")
    
    # Get available samplers
    print("\nAvailable samplers:")
    samplers = api.get_samplers()
    for sampler in samplers[:5]:  # Show first 5
        print(f"  - {sampler}")
    
    # Test generation
    print("\n" + "=" * 60)
    print("Testing image generation...")
    print("=" * 60)
    
    test_prompt = "beautiful sunset over ocean, cinematic, high quality, vertical composition"
    
    image = api.generate_image(
        prompt=test_prompt,
        negative_prompt="blurry, low quality, ugly",
        width=544,  # Small for quick test
        height=960,
        steps=10,  # Fast
        cfg_scale=7.5,
    )
    
    if image:
        # Save test image
        output_path = Path("test_webui_output.png")
        image.save(output_path)
        print(f"\n✓ Test successful! Image saved to {output_path}")
        print(f"  Size: {image.size}")
    else:
        print("\n✗ Test failed - check WebUI is running with --api flag")


if __name__ == "__main__":
    test_api()

