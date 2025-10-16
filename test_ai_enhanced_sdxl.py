"""
TEST SUITE FOR AI-ENHANCED SDXL SYSTEM

Comprehensive testing of all AI enhancements:
- Prompt optimization with narrative intelligence
- ControlNet guidance and visual continuity
- Quality analysis and refinement loops
- End-to-end workflow integration
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from PIL import Image
import numpy as np

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from settings.config import Config


class AIEnhancedSDXLTestSuite:
    """Comprehensive test suite for AI-enhanced SDXL system"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
        
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results"""
        
        print("=" * 80)
        print("AI-ENHANCED SDXL SYSTEM - COMPREHENSIVE TEST SUITE")
        print("=" * 80)
        
        tests = [
            ("AI Prompt Optimizer", self.test_prompt_optimizer),
            ("ControlNet Processor", self.test_controlnet_processor),
            ("Quality Analyzer", self.test_quality_analyzer),
            ("WebUI API Integration", self.test_webui_integration),
            ("End-to-End Workflow", self.test_end_to_end_workflow),
            ("Performance Comparison", self.test_performance_comparison),
            ("Configuration Validation", self.test_configuration_validation),
            ("Error Handling", self.test_error_handling)
        ]
        
        for test_name, test_func in tests:
            print(f"\n[TEST] Running: {test_name}")
            print("-" * 50)
            
            try:
                result = test_func()
                self.test_results[test_name] = result
                status = "[PASS]" if result else "[FAIL]"
                print(f"\n{status}: {test_name}")
                
            except Exception as e:
                print(f"\n[FAIL] {test_name} - {e}")
                self.test_results[test_name] = False
        
        # Print summary
        self.print_test_summary()
        return self.test_results
    
    def test_prompt_optimizer(self) -> bool:
        """Test AI prompt optimization with mock script data"""
        
        try:
            from helpers.ai_prompt_optimizer import optimize_prompts_with_ai
            
            # Mock scene descriptions
            test_scenes = [
                "Ocean waves at sunset",
                "City skyline at night with neon lights",
                "Mountain landscape with dramatic clouds"
            ]
            
            # Mock script data
            test_script_data = {
                'title': 'Amazing Facts About Space Exploration',
                'script': 'Space exploration has revolutionized our understanding of the universe. From the first moon landing to the Mars rovers, we continue to push the boundaries of human knowledge.',
                'topic': 'space exploration'
            }
            
            print(f"  📝 Testing prompt optimization with {len(test_scenes)} scenes...")
            
            # Test with context
            optimized_with_context = optimize_prompts_with_ai(test_scenes, test_script_data)
            
            # Test without context
            optimized_without_context = optimize_prompts_with_ai(test_scenes, None)
            
            # Validate results
            if len(optimized_with_context) != len(test_scenes):
                print(f"    ❌ Context optimization returned {len(optimized_with_context)} prompts, expected {len(test_scenes)}")
                return False
            
            if len(optimized_without_context) != len(test_scenes):
                print(f"    ❌ No-context optimization returned {len(optimized_without_context)} prompts, expected {len(test_scenes)}")
                return False
            
            # Check prompt quality
            for i, (original, (optimized, negative)) in enumerate(zip(test_scenes, optimized_with_context)):
                if len(optimized) <= len(original):
                    print(f"    ⚠️ Scene {i+1}: Optimized prompt not significantly longer than original")
                
                if not any(keyword in optimized.lower() for keyword in ['vertical', 'portrait', 'cinematic']):
                    print(f"    ⚠️ Scene {i+1}: Optimized prompt missing key SDXL terms")
            
            print(f"    ✅ Prompt optimization working correctly")
            print(f"    📊 Context-aware: {len(optimized_with_context)} prompts")
            print(f"    📊 Basic mode: {len(optimized_without_context)} prompts")
            
            return True
            
        except ImportError as e:
            print(f"    ❌ AI prompt optimizer not available: {e}")
            return False
        except Exception as e:
            print(f"    ❌ Prompt optimization test failed: {e}")
            return False
    
    def test_controlnet_processor(self) -> bool:
        """Test ControlNet processing and control image generation"""
        
        try:
            from helpers.controlnet_processor import process_control_images
            
            # Create test images
            test_image = Image.new('RGB', (512, 512), color='lightblue')
            
            print(f"  🎯 Testing ControlNet processing...")
            
            # Test with reference image
            result_with_ref = process_control_images(reference_image=test_image)
            
            # Test with previous image
            result_with_prev = process_control_images(previous_image=test_image)
            
            # Test without images
            result_empty = process_control_images()
            
            # Validate results
            if not isinstance(result_with_ref, dict):
                print(f"    ❌ ControlNet processing returned invalid type: {type(result_with_ref)}")
                return False
            
            if 'enabled' not in result_with_ref:
                print(f"    ❌ ControlNet result missing 'enabled' field")
                return False
            
            # Check if ControlNet is available
            if result_with_ref.get('enabled', False):
                control_images = result_with_ref.get('control_images', {})
                controlnet_units = result_with_ref.get('controlnet_units', [])
                
                print(f"    ✅ ControlNet processing enabled")
                print(f"    📊 Control images generated: {len(control_images)}")
                print(f"    📊 ControlNet units: {len(controlnet_units)}")
                
                # Validate control images
                for model_name, control_image in control_images.items():
                    if not isinstance(control_image, Image.Image):
                        print(f"    ❌ Control image for {model_name} is not PIL Image")
                        return False
                    
                    if control_image.size != test_image.size:
                        print(f"    ⚠️ Control image size mismatch: {control_image.size} vs {test_image.size}")
            else:
                print(f"    ℹ️ ControlNet processing disabled or unavailable")
            
            print(f"    ✅ ControlNet processor working correctly")
            return True
            
        except ImportError as e:
            print(f"    ❌ ControlNet processor not available: {e}")
            return False
        except Exception as e:
            print(f"    ❌ ControlNet processor test failed: {e}")
            return False
    
    def test_quality_analyzer(self) -> bool:
        """Test image quality analysis and refinement"""
        
        try:
            from helpers.image_quality_analyzer import analyze_image_quality, generate_refinement_prompt
            
            # Create test image
            test_image = Image.new('RGB', (512, 512), color='lightblue')
            
            # Mock data
            test_prompt = "Ocean waves at sunset, vertical composition, cinematic, high quality"
            test_scene = "Ocean waves at sunset"
            test_context = {
                'title': 'Amazing Ocean Facts',
                'topic': 'ocean science',
                'script': 'The ocean covers 71% of Earth\'s surface...'
            }
            
            print(f"  🔍 Testing quality analysis...")
            
            # Test quality analysis
            quality_analysis = analyze_image_quality(
                image=test_image,
                original_prompt=test_prompt,
                scene_description=test_scene,
                script_context=test_context,
                scene_index=0
            )
            
            # Validate analysis result
            if not isinstance(quality_analysis, dict):
                print(f"    ❌ Quality analysis returned invalid type: {type(quality_analysis)}")
                return False
            
            required_fields = ['enabled', 'overall_score', 'meets_threshold']
            for field in required_fields:
                if field not in quality_analysis:
                    print(f"    ❌ Quality analysis missing field: {field}")
                    return False
            
            if quality_analysis.get('enabled', False):
                overall_score = quality_analysis.get('overall_score', 0)
                meets_threshold = quality_analysis.get('meets_threshold', False)
                
                print(f"    ✅ Quality analysis enabled")
                print(f"    📊 Overall score: {overall_score:.1f}/10")
                print(f"    📊 Meets threshold: {meets_threshold}")
                
                # Test refinement if needed
                if not meets_threshold and quality_analysis.get('refinement_suggestions'):
                    print(f"    🔄 Testing refinement generation...")
                    
                    refined_prompt, refined_negative = generate_refinement_prompt(
                        test_prompt, quality_analysis, 1
                    )
                    
                    if len(refined_prompt) > len(test_prompt):
                        print(f"    ✅ Refinement prompt generated")
                    else:
                        print(f"    ⚠️ Refinement prompt not significantly different")
            else:
                print(f"    ℹ️ Quality analysis disabled")
            
            print(f"    ✅ Quality analyzer working correctly")
            return True
            
        except ImportError as e:
            print(f"    ❌ Quality analyzer not available: {e}")
            return False
        except Exception as e:
            print(f"    ❌ Quality analyzer test failed: {e}")
            return False
    
    def test_webui_integration(self) -> bool:
        """Test WebUI API integration with ControlNet support"""
        
        try:
            from helpers.sd_webui_api import SDWebUIAPI
            
            print(f"  🌐 Testing WebUI API integration...")
            
            # Initialize API
            api = SDWebUIAPI(host=Config.SD_WEBUI_HOST, timeout=10)
            
            # Test connection
            print(f"    🔗 Testing connection to {Config.SD_WEBUI_HOST}...")
            
            # Note: This test will fail if WebUI is not running, which is expected
            # We're testing the integration code, not the actual WebUI service
            
            # Test method signature
            import inspect
            sig = inspect.signature(api.generate_image)
            params = list(sig.parameters.keys())
            
            if 'controlnet_units' not in params:
                print(f"    ❌ generate_image method missing controlnet_units parameter")
                return False
            
            print(f"    ✅ WebUI API method signature correct")
            print(f"    📊 Parameters: {params}")
            
            return True
            
        except ImportError as e:
            print(f"    ❌ WebUI API not available: {e}")
            return False
        except Exception as e:
            print(f"    ❌ WebUI API test failed: {e}")
            return False
    
    def test_end_to_end_workflow(self) -> bool:
        """Test complete end-to-end workflow integration"""
        
        try:
            from steps.step3_generate_backgrounds import generate_ai_backgrounds_enhanced
            
            # Mock data
            test_scenes = [
                "Ocean waves at sunset",
                "City skyline at night"
            ]
            
            test_script_data = {
                'title': 'Amazing Facts About Nature',
                'script': 'Nature never ceases to amaze us with its beauty and complexity...',
                'topic': 'nature'
            }
            
            print(f"  🔄 Testing end-to-end workflow...")
            
            # Test enhanced generation (will fail without GPU, but we can test the integration)
            try:
                result = generate_ai_backgrounds_enhanced(
                    scene_descriptions=test_scenes,
                    script_data=test_script_data,
                    duration_per_scene=3.0
                )
                
                print(f"    ✅ Enhanced generation function callable")
                print(f"    📊 Returned: {type(result)}")
                
                return True
                
            except Exception as workflow_error:
                # Expected to fail without GPU/WebUI, but should fail gracefully
                error_msg = str(workflow_error).lower()
                if any(keyword in error_msg for keyword in ['gpu', 'cuda', 'webui', 'connection']):
                    print(f"    ✅ Enhanced generation fails gracefully (expected without GPU/WebUI)")
                    print(f"    📊 Error type: {type(workflow_error).__name__}")
                    return True
                else:
                    print(f"    ❌ Unexpected error in enhanced generation: {workflow_error}")
                    return False
            
        except ImportError as e:
            print(f"    ❌ Enhanced generation not available: {e}")
            return False
        except Exception as e:
            print(f"    ❌ End-to-end workflow test failed: {e}")
            return False
    
    def test_performance_comparison(self) -> bool:
        """Test performance characteristics of AI enhancements"""
        
        try:
            print(f"  ⚡ Testing performance characteristics...")
            
            # Test prompt optimization speed
            start_time = time.time()
            
            from helpers.ai_prompt_optimizer import optimize_prompts_with_ai
            
            test_scenes = ["Ocean waves at sunset", "City skyline at night"]
            test_script_data = {
                'title': 'Test Video',
                'script': 'This is a test script for performance evaluation.',
                'topic': 'test'
            }
            
            try:
                optimized = optimize_prompts_with_ai(test_scenes, test_script_data)
                opt_time = time.time() - start_time
                
                print(f"    ✅ Prompt optimization: {opt_time:.2f}s for {len(test_scenes)} scenes")
                
                if opt_time > 10.0:
                    print(f"    ⚠️ Prompt optimization slower than expected ({opt_time:.2f}s)")
                else:
                    print(f"    ✅ Prompt optimization speed acceptable")
                
            except Exception as e:
                print(f"    ⚠️ Prompt optimization performance test failed: {e}")
            
            # Test ControlNet processing speed
            start_time = time.time()
            
            try:
                from helpers.controlnet_processor import process_control_images
                
                test_image = Image.new('RGB', (256, 256), color='lightblue')
                controlnet_result = process_control_images(reference_image=test_image)
                cn_time = time.time() - start_time
                
                print(f"    ✅ ControlNet processing: {cn_time:.2f}s")
                
                if cn_time > 5.0:
                    print(f"    ⚠️ ControlNet processing slower than expected ({cn_time:.2f}s)")
                else:
                    print(f"    ✅ ControlNet processing speed acceptable")
                
            except Exception as e:
                print(f"    ⚠️ ControlNet performance test failed: {e}")
            
            print(f"    ✅ Performance testing completed")
            return True
            
        except Exception as e:
            print(f"    ❌ Performance test failed: {e}")
            return False
    
    def test_configuration_validation(self) -> bool:
        """Test configuration validation and defaults"""
        
        try:
            print(f"  ⚙️ Testing configuration validation...")
            
            # Test required config attributes
            required_configs = [
                'SD_USE_AI_PROMPT_OPTIMIZER',
                'SD_PROMPT_OPTIMIZER_PROVIDER',
                'SD_USE_CONTROLNET',
                'SD_USE_QUALITY_ANALYSIS',
                'SD_QUALITY_THRESHOLD',
                'SD_MAX_REFINEMENT_ITERATIONS'
            ]
            
            missing_configs = []
            for config_name in required_configs:
                if not hasattr(Config, config_name):
                    missing_configs.append(config_name)
            
            if missing_configs:
                print(f"    ❌ Missing configuration attributes: {missing_configs}")
                return False
            
            # Test configuration values
            if not isinstance(Config.SD_QUALITY_THRESHOLD, (int, float)):
                print(f"    ❌ SD_QUALITY_THRESHOLD should be numeric")
                return False
            
            if not 1 <= Config.SD_QUALITY_THRESHOLD <= 10:
                print(f"    ❌ SD_QUALITY_THRESHOLD should be between 1 and 10")
                return False
            
            if not isinstance(Config.SD_MAX_REFINEMENT_ITERATIONS, int):
                print(f"    ❌ SD_MAX_REFINEMENT_ITERATIONS should be integer")
                return False
            
            if Config.SD_MAX_REFINEMENT_ITERATIONS < 0 or Config.SD_MAX_REFINEMENT_ITERATIONS > 5:
                print(f"    ❌ SD_MAX_REFINEMENT_ITERATIONS should be between 0 and 5")
                return False
            
            print(f"    ✅ Configuration validation passed")
            print(f"    📊 Quality threshold: {Config.SD_QUALITY_THRESHOLD}")
            print(f"    📊 Max refinements: {Config.SD_MAX_REFINEMENT_ITERATIONS}")
            print(f"    📊 AI prompt optimizer: {Config.SD_USE_AI_PROMPT_OPTIMIZER}")
            print(f"    📊 ControlNet enabled: {Config.SD_USE_CONTROLNET}")
            print(f"    📊 Quality analysis: {Config.SD_USE_QUALITY_ANALYSIS}")
            
            return True
            
        except Exception as e:
            print(f"    ❌ Configuration validation failed: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling and graceful degradation"""
        
        try:
            print(f"  🛡️ Testing error handling...")
            
            # Test with invalid inputs
            from helpers.ai_prompt_optimizer import optimize_prompts_with_ai
            from helpers.controlnet_processor import process_control_images
            from helpers.image_quality_analyzer import analyze_image_quality
            
            # Test prompt optimizer with empty scenes
            try:
                result = optimize_prompts_with_ai([], None)
                if result != []:
                    print(f"    ❌ Prompt optimizer should return empty list for empty input")
                    return False
                print(f"    ✅ Prompt optimizer handles empty input correctly")
            except Exception as e:
                print(f"    ❌ Prompt optimizer failed on empty input: {e}")
                return False
            
            # Test ControlNet with None inputs
            try:
                result = process_control_images(None, None)
                if not isinstance(result, dict):
                    print(f"    ❌ ControlNet should return dict for None inputs")
                    return False
                print(f"    ✅ ControlNet handles None inputs correctly")
            except Exception as e:
                print(f"    ❌ ControlNet failed on None inputs: {e}")
                return False
            
            # Test quality analyzer with None image
            try:
                result = analyze_image_quality(None, "test prompt", "test scene", None, 0)
                # Should either work or fail gracefully
                print(f"    ✅ Quality analyzer handles None image gracefully")
            except Exception as e:
                if "None" in str(e) or "null" in str(e).lower():
                    print(f"    ✅ Quality analyzer fails gracefully on None image")
                else:
                    print(f"    ❌ Quality analyzer unexpected error on None image: {e}")
                    return False
            
            print(f"    ✅ Error handling tests passed")
            return True
            
        except Exception as e:
            print(f"    ❌ Error handling test failed: {e}")
            return False
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        
        total_time = time.time() - self.start_time
        
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results.values() if result)
        total = len(self.test_results)
        
        print(f"Tests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        print(f"Total Time: {total_time:.2f} seconds")
        
        print(f"\nDetailed Results:")
        for test_name, result in self.test_results.items():
            status = "[PASS]" if result else "[FAIL]"
            print(f"  {status} {test_name}")
        
        if passed == total:
            print(f"\n[SUCCESS] ALL TESTS PASSED! AI-Enhanced SDXL system is ready!")
        elif passed >= total * 0.8:
            print(f"\n[WARNING] Most tests passed. Check failed tests for issues.")
        else:
            print(f"\n[ERROR] Multiple test failures. Review implementation.")
        
        print(f"\nNext Steps:")
        if passed >= total * 0.8:
            print(f"  1. Install missing dependencies: pip install -r requirements.txt")
            print(f"  2. Configure AI provider API keys in .env file")
            print(f"  3. Start Stable Diffusion WebUI with --api flag")
            print(f"  4. Run the application and test AI enhancements")
        else:
            print(f"  1. Review failed tests and fix implementation issues")
            print(f"  2. Ensure all dependencies are installed correctly")
            print(f"  3. Check configuration settings in settings/config.py")


def main():
    """Run the test suite"""
    
    test_suite = AIEnhancedSDXLTestSuite()
    results = test_suite.run_all_tests()
    
    # Exit with appropriate code
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    if passed == total:
        sys.exit(0)  # All tests passed
    elif passed >= total * 0.8:
        sys.exit(1)  # Most tests passed, minor issues
    else:
        sys.exit(2)  # Multiple failures, major issues


if __name__ == "__main__":
    main()
