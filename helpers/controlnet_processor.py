"""
CONTROLNET PROCESSOR - Visual Guidance for SDXL

Provides control image generation for structural consistency and visual continuity
across YouTube Shorts background scenes using ControlNet models.
"""

import sys
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

import numpy as np
from PIL import Image
import cv2

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from settings.config import Config

try:
    from controlnet_aux import CannyDetector, MidasDetector
    CONTROLNET_AVAILABLE = True
except ImportError:
    CONTROLNET_AVAILABLE = False
    print("Warning: controlnet_aux not available. ControlNet features disabled.")


class ControlNetProcessor:
    """Processes images for ControlNet guidance and visual continuity"""
    
    def __init__(self):
        self.use_controlnet = getattr(Config, 'SD_USE_CONTROLNET', True)
        self.controlnet_models = getattr(Config, 'SD_CONTROLNET_MODELS', ["canny", "depth_midas"])
        self.controlnet_weight = getattr(Config, 'SD_CONTROLNET_WEIGHT', 0.7)
        self.use_prev_frame = getattr(Config, 'SD_CONTROLNET_USE_PREV_FRAME', True)
        
        # Initialize detectors if available
        if CONTROLNET_AVAILABLE and self.use_controlnet:
            self.canny_detector = CannyDetector()
            self.midas_detector = MidasDetector.from_pretrained("lllyasviel/ControlNet")
            print("ControlNet detectors initialized")
        else:
            self.canny_detector = None
            self.midas_detector = None
            print("ControlNet detectors not available")
    
    def generate_control_images(
        self, 
        reference_image: Optional[Image.Image] = None,
        previous_image: Optional[Image.Image] = None
    ) -> Dict[str, Any]:
        """
        Generate control images for SDXL guidance.
        
        Args:
            reference_image: Reference image for structural guidance
            previous_image: Previous scene image for visual continuity
            
        Returns:
            Dictionary with control images and metadata
        """
        
        if not self.use_controlnet or not CONTROLNET_AVAILABLE:
            return {"enabled": False, "controlnet_units": []}
        
        print("ControlNet: Generating control images for visual guidance...")
        
        control_images = {}
        controlnet_units = []
        
        # Use previous image for continuity if available and enabled
        source_image = previous_image if (self.use_prev_frame and previous_image) else reference_image
        
        if not source_image:
            print("  ⚠️ No source image available for ControlNet processing")
            return {"enabled": False, "controlnet_units": []}
        
        # Generate control images based on enabled models
        if "canny" in self.controlnet_models:
            canny_image = self._generate_canny_control(source_image)
            if canny_image:
                control_images["canny"] = canny_image
                controlnet_units.append(self._create_canny_unit(canny_image))
                print("  Canny edge detection completed")
        
        if "depth_midas" in self.controlnet_models:
            depth_image = self._generate_depth_control(source_image)
            if depth_image:
                control_images["depth"] = depth_image
                controlnet_units.append(self._create_depth_unit(depth_image))
                print("  Depth estimation completed")
        
        if "openpose" in self.controlnet_models:
            pose_image = self._generate_pose_control(source_image)
            if pose_image:
                control_images["pose"] = pose_image
                controlnet_units.append(self._create_pose_unit(pose_image))
                print("  Pose estimation completed")
        
        print(f"  Generated {len(control_images)} control images")
        
        return {
            "enabled": True,
            "control_images": control_images,
            "controlnet_units": controlnet_units,
            "source_image": source_image,
            "models_used": list(control_images.keys())
        }
    
    def _generate_canny_control(self, source_image: Image.Image) -> Optional[Image.Image]:
        """Generate Canny edge detection control image"""
        
        try:
            # Convert PIL to numpy array
            img_array = np.array(source_image)
            
            # Convert to grayscale if needed
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Apply Canny edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Convert back to PIL Image
            canny_image = Image.fromarray(edges).convert('RGB')
            
            return canny_image
            
        except Exception as e:
            print(f"    ⚠️ Canny detection failed: {e}")
            return None
    
    def _generate_depth_control(self, source_image: Image.Image) -> Optional[Image.Image]:
        """Generate depth estimation control image"""
        
        try:
            # Use Midas detector if available
            if self.midas_detector:
                depth_image = self.midas_detector(source_image)
                return depth_image
            else:
                # Fallback: Simple depth approximation using blur
                img_array = np.array(source_image)
                blurred = cv2.GaussianBlur(img_array, (15, 15), 0)
                depth_image = Image.fromarray(blurred)
                return depth_image
                
        except Exception as e:
            print(f"    ⚠️ Depth estimation failed: {e}")
            return None
    
    def _generate_pose_control(self, source_image: Image.Image) -> Optional[Image.Image]:
        """Generate pose estimation control image"""
        
        try:
            # For now, return a simple structural guide
            # In production, would use OpenPose detector
            img_array = np.array(source_image)
            
            # Create a simple pose-like structure guide
            height, width = img_array.shape[:2]
            pose_guide = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Draw basic structural lines (simplified pose skeleton)
            cv2.line(pose_guide, (width//2, 0), (width//2, height//3), (255, 255, 255), 3)
            cv2.line(pose_guide, (width//2, height//3), (width//4, height//2), (255, 255, 255), 3)
            cv2.line(pose_guide, (width//2, height//3), (3*width//4, height//2), (255, 255, 255), 3)
            cv2.line(pose_guide, (width//2, height//2), (width//2, height), (255, 255, 255), 3)
            
            pose_image = Image.fromarray(pose_guide)
            return pose_image
            
        except Exception as e:
            print(f"    ⚠️ Pose estimation failed: {e}")
            return None
    
    def _create_canny_unit(self, canny_image: Image.Image) -> Dict[str, Any]:
        """Create ControlNet unit for Canny edge detection"""
        
        # Convert PIL image to base64 for API
        import io
        import base64
        
        buffer = io.BytesIO()
        canny_image.save(buffer, format='PNG')
        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return {
            "enabled": True,
            "input_image": image_data,
            "module": "canny",
            "model": "control_v11p_sd15_canny",
            "weight": self.controlnet_weight,
            "resize_mode": 1,  # Resize to fit
            "lowvram": True,   # Memory optimization
            "processor_res": 512,
            "threshold_a": 50,
            "threshold_b": 150,
            "guidance_start": 0.0,
            "guidance_end": 1.0,
            "control_mode": 0  # Balanced
        }
    
    def _create_depth_unit(self, depth_image: Image.Image) -> Dict[str, Any]:
        """Create ControlNet unit for depth estimation"""
        
        # Convert PIL image to base64 for API
        import io
        import base64
        
        buffer = io.BytesIO()
        depth_image.save(buffer, format='PNG')
        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return {
            "enabled": True,
            "input_image": image_data,
            "module": "depth_midas",
            "model": "control_v11f1p_sd15_depth",
            "weight": self.controlnet_weight,
            "resize_mode": 1,  # Resize to fit
            "lowvram": True,   # Memory optimization
            "processor_res": 512,
            "guidance_start": 0.0,
            "guidance_end": 1.0,
            "control_mode": 0  # Balanced
        }
    
    def _create_pose_unit(self, pose_image: Image.Image) -> Dict[str, Any]:
        """Create ControlNet unit for pose estimation"""
        
        # Convert PIL image to base64 for API
        import io
        import base64
        
        buffer = io.BytesIO()
        pose_image.save(buffer, format='PNG')
        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return {
            "enabled": True,
            "input_image": image_data,
            "module": "openpose",
            "model": "control_v11p_sd15_openpose",
            "weight": self.controlnet_weight * 0.5,  # Lower weight for pose
            "resize_mode": 1,  # Resize to fit
            "lowvram": True,   # Memory optimization
            "processor_res": 512,
            "guidance_start": 0.0,
            "guidance_end": 0.8,  # Stop early for pose
            "control_mode": 0  # Balanced
        }
    
    def get_controlnet_payload(self, controlnet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate ControlNet payload for WebUI API"""
        
        if not controlnet_data.get("enabled", False):
            return {}
        
        controlnet_units = controlnet_data.get("controlnet_units", [])
        
        if not controlnet_units:
            return {}
        
        # Limit to first 2 units for memory efficiency (RTX 2060 6GB)
        active_units = controlnet_units[:2]
        
        return {
            "alwayson_scripts": {
                "ControlNet": {
                    "args": active_units
                }
            }
        }
    
    def save_control_images(
        self, 
        controlnet_data: Dict[str, Any], 
        output_dir: Path,
        scene_index: int
    ) -> List[Path]:
        """Save control images for debugging and analysis"""
        
        if not controlnet_data.get("enabled", False):
            return []
        
        control_images = controlnet_data.get("control_images", {})
        saved_paths = []
        
        for model_name, control_image in control_images.items():
            filename = f"control_{scene_index}_{model_name}.png"
            filepath = output_dir / filename
            
            try:
                control_image.save(filepath)
                saved_paths.append(filepath)
                print(f"  💾 Saved {model_name} control image: {filename}")
            except Exception as e:
                print(f"    ⚠️ Failed to save {model_name} control image: {e}")
        
        return saved_paths


# Convenience function for direct use
def process_control_images(
    reference_image: Optional[Image.Image] = None,
    previous_image: Optional[Image.Image] = None
) -> Dict[str, Any]:
    """
    Process images for ControlNet guidance.
    
    Args:
        reference_image: Reference image for structural guidance
        previous_image: Previous scene image for visual continuity
        
    Returns:
        Dictionary with control images and metadata
    """
    
    processor = ControlNetProcessor()
    return processor.generate_control_images(reference_image, previous_image)


if __name__ == "__main__":
    # Test the ControlNet processor
    print("=" * 60)
    print("TESTING CONTROLNET PROCESSOR")
    print("=" * 60)
    
    # Create a test image
    test_image = Image.new('RGB', (512, 512), color='white')
    
    print(f"\nTesting with controlnet_available: {CONTROLNET_AVAILABLE}")
    
    try:
        result = process_control_images(test_image)
        
        if result.get("enabled", False):
            print(f"✅ ControlNet processing successful!")
            print(f"  Models used: {result.get('models_used', [])}")
            print(f"  Control units: {len(result.get('controlnet_units', []))}")
        else:
            print("ℹ️ ControlNet processing disabled or not available")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        print("Make sure controlnet_aux is installed: pip install controlnet_aux")
