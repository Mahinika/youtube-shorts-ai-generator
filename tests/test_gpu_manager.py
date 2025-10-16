"""
Unit tests for GPU memory management utilities.

Tests the comprehensive GPU memory management system including
context managers, VRAM monitoring, and OOM prevention.
"""

import pytest
import torch
from unittest.mock import patch, MagicMock, mock_open
from contextlib import contextmanager

from utils.gpu_manager import (
    GPUMemoryManager,
    get_gpu_manager,
    gpu_memory_context,
    check_gpu_compatibility,
    get_gpu_info,
    GPUMemoryError
)


class TestGPUMemoryManager:
    """Test GPUMemoryManager class."""
    
    def test_initialization(self):
        """Test GPU memory manager initialization."""
        manager = GPUMemoryManager()
        assert manager is not None
        assert hasattr(manager, 'get_memory_info')
        assert hasattr(manager, 'clear_cache')
        assert hasattr(manager, 'get_memory_usage')
    
    @patch('torch.cuda.is_available')
    def test_get_memory_info_cuda_available(self, mock_cuda_available):
        """Test get_memory_info when CUDA is available."""
        mock_cuda_available.return_value = True
        
        with patch('torch.cuda.memory_allocated', return_value=1024*1024*1024), \
             patch('torch.cuda.memory_reserved', return_value=2048*1024*1024), \
             patch('torch.cuda.get_device_properties') as mock_props:
            
            # Mock GPU properties
            mock_props.return_value = MagicMock(
                total_memory=6*1024*1024*1024,  # 6GB
                name="RTX 2060"
            )
            
            manager = GPUMemoryManager()
            memory_info = manager.get_memory_info()
            
            assert memory_info['allocated'] == 1024*1024*1024
            assert memory_info['reserved'] == 2048*1024*1024
            assert memory_info['total'] == 6*1024*1024*1024
            assert memory_info['free'] == 4*1024*1024*1024  # 6GB - 2GB reserved
            assert memory_info['device_name'] == "RTX 2060"
    
    @patch('torch.cuda.is_available')
    def test_get_memory_info_cuda_unavailable(self, mock_cuda_available):
        """Test get_memory_info when CUDA is not available."""
        mock_cuda_available.return_value = False
        
        manager = GPUMemoryManager()
        memory_info = manager.get_memory_info()
        
        assert memory_info['allocated'] == 0
        assert memory_info['reserved'] == 0
        assert memory_info['total'] == 0
        assert memory_info['free'] == 0
        assert memory_info['device_name'] == "CPU"
    
    @patch('torch.cuda.is_available')
    def test_clear_cache_cuda_available(self, mock_cuda_available):
        """Test clear_cache when CUDA is available."""
        mock_cuda_available.return_value = True
        
        with patch('torch.cuda.empty_cache') as mock_empty_cache, \
             patch('torch.cuda.ipc_collect') as mock_ipc_collect, \
             patch('gc.collect') as mock_gc_collect:
            
            manager = GPUMemoryManager()
            manager.clear_cache()
            
            mock_empty_cache.assert_called_once()
            mock_ipc_collect.assert_called_once()
            mock_gc_collect.assert_called_once()
    
    @patch('torch.cuda.is_available')
    def test_clear_cache_cuda_unavailable(self, mock_cuda_available):
        """Test clear_cache when CUDA is not available."""
        mock_cuda_available.return_value = False
        
        with patch('torch.cuda.empty_cache') as mock_empty_cache, \
             patch('torch.cuda.ipc_collect') as mock_ipc_collect, \
             patch('gc.collect') as mock_gc_collect:
            
            manager = GPUMemoryManager()
            manager.clear_cache()
            
            # Should not call CUDA functions when CUDA is not available
            mock_empty_cache.assert_not_called()
            mock_ipc_collect.assert_not_called()
            mock_gc_collect.assert_called_once()
    
    @patch('torch.cuda.is_available')
    def test_get_memory_usage(self, mock_cuda_available):
        """Test get_memory_usage method."""
        mock_cuda_available.return_value = True
        
        with patch('torch.cuda.memory_allocated', return_value=1024*1024*1024), \
             patch('torch.cuda.memory_reserved', return_value=2048*1024*1024), \
             patch('torch.cuda.get_device_properties') as mock_props:
            
            mock_props.return_value = MagicMock(
                total_memory=6*1024*1024*1024,
                name="RTX 2060"
            )
            
            manager = GPUMemoryManager()
            usage = manager.get_memory_usage()
            
            assert 'allocated_mb' in usage
            assert 'reserved_mb' in usage
            assert 'total_mb' in usage
            assert 'free_mb' in usage
            assert 'usage_percent' in usage
            assert usage['allocated_mb'] == 1024
            assert usage['reserved_mb'] == 2048
            assert usage['total_mb'] == 6144
            assert usage['free_mb'] == 4096
            assert usage['usage_percent'] == pytest.approx(33.33, rel=1e-2)


class TestGPUMemoryContext:
    """Test GPU memory context manager."""
    
    @patch('torch.cuda.is_available')
    def test_gpu_memory_context_cuda_available(self, mock_cuda_available):
        """Test GPU memory context when CUDA is available."""
        mock_cuda_available.return_value = True
        
        with patch('torch.cuda.empty_cache') as mock_empty_cache, \
             patch('torch.cuda.ipc_collect') as mock_ipc_collect, \
             patch('gc.collect') as mock_gc_collect:
            
            with gpu_memory_context(clear_cache=True):
                pass
            
            mock_empty_cache.assert_called_once()
            mock_ipc_collect.assert_called_once()
            mock_gc_collect.assert_called_once()
    
    @patch('torch.cuda.is_available')
    def test_gpu_memory_context_cuda_unavailable(self, mock_cuda_available):
        """Test GPU memory context when CUDA is not available."""
        mock_cuda_available.return_value = False
        
        with patch('torch.cuda.empty_cache') as mock_empty_cache, \
             patch('torch.cuda.ipc_collect') as mock_ipc_collect, \
             patch('gc.collect') as mock_gc_collect:
            
            with gpu_memory_context(clear_cache=True):
                pass
            
            # Should not call CUDA functions when CUDA is not available
            mock_empty_cache.assert_not_called()
            mock_ipc_collect.assert_not_called()
            mock_gc_collect.assert_called_once()
    
    @patch('torch.cuda.is_available')
    def test_gpu_memory_context_no_clear(self, mock_cuda_available):
        """Test GPU memory context with clear_cache=False."""
        mock_cuda_available.return_value = True
        
        with patch('torch.cuda.empty_cache') as mock_empty_cache, \
             patch('torch.cuda.ipc_collect') as mock_ipc_collect, \
             patch('gc.collect') as mock_gc_collect:
            
            with gpu_memory_context(clear_cache=False):
                pass
            
            # Should not call CUDA functions when clear_cache=False
            mock_empty_cache.assert_not_called()
            mock_ipc_collect.assert_not_called()
            mock_gc_collect.assert_called_once()
    
    @patch('torch.cuda.is_available')
    def test_gpu_memory_context_exception_handling(self, mock_cuda_available):
        """Test GPU memory context with exception handling."""
        mock_cuda_available.return_value = True
        
        with patch('torch.cuda.empty_cache') as mock_empty_cache, \
             patch('torch.cuda.ipc_collect') as mock_ipc_collect, \
             patch('gc.collect') as mock_gc_collect:
            
            with pytest.raises(ValueError):
                with gpu_memory_context(clear_cache=True):
                    raise ValueError("Test error")
            
            # Should still call cleanup functions even if exception occurs
            mock_empty_cache.assert_called_once()
            mock_ipc_collect.assert_called_once()
            mock_gc_collect.assert_called_once()


class TestGPUCompatibility:
    """Test GPU compatibility checking."""
    
    @patch('torch.cuda.is_available')
    def test_check_gpu_compatibility_cuda_available(self, mock_cuda_available):
        """Test GPU compatibility check when CUDA is available."""
        mock_cuda_available.return_value = True
        
        with patch('torch.cuda.get_device_properties') as mock_props:
            # Mock GPU properties
            mock_props.return_value = MagicMock(
                total_memory=6*1024*1024*1024,  # 6GB
                name="RTX 2060",
                major=7,
                minor=5
            )
            
            compatible, message = check_gpu_compatibility()
            
            assert compatible is True
            assert "RTX 2060" in message
            assert "6.0 GB" in message
    
    @patch('torch.cuda.is_available')
    def test_check_gpu_compatibility_cuda_unavailable(self, mock_cuda_available):
        """Test GPU compatibility check when CUDA is not available."""
        mock_cuda_available.return_value = False
        
        compatible, message = check_gpu_compatibility()
        
        assert compatible is False
        assert "CUDA not available" in message
    
    @patch('torch.cuda.is_available')
    def test_check_gpu_compatibility_insufficient_memory(self, mock_cuda_available):
        """Test GPU compatibility check with insufficient memory."""
        mock_cuda_available.return_value = True
        
        with patch('torch.cuda.get_device_properties') as mock_props:
            # Mock GPU with insufficient memory
            mock_props.return_value = MagicMock(
                total_memory=1*1024*1024*1024,  # 1GB
                name="GTX 1050",
                major=6,
                minor=1
            )
            
            compatible, message = check_gpu_compatibility()
            
            assert compatible is False
            assert "insufficient memory" in message.lower()
    
    @patch('torch.cuda.is_available')
    def test_check_gpu_compatibility_exception_handling(self, mock_cuda_available):
        """Test GPU compatibility check with exception handling."""
        mock_cuda_available.return_value = True
        
        with patch('torch.cuda.get_device_properties', side_effect=Exception("GPU error")):
            compatible, message = check_gpu_compatibility()
            
            assert compatible is False
            assert "GPU error" in message


class TestGPUInfo:
    """Test GPU information retrieval."""
    
    @patch('torch.cuda.is_available')
    def test_get_gpu_info_cuda_available(self, mock_cuda_available):
        """Test get_gpu_info when CUDA is available."""
        mock_cuda_available.return_value = True
        
        with patch('torch.cuda.get_device_properties') as mock_props, \
             patch('torch.cuda.memory_allocated', return_value=1024*1024*1024), \
             patch('torch.cuda.memory_reserved', return_value=2048*1024*1024):
            
            # Mock GPU properties
            mock_props.return_value = MagicMock(
                total_memory=6*1024*1024*1024,  # 6GB
                name="RTX 2060",
                major=7,
                minor=5,
                max_threads_per_block=1024,
                max_threads_per_multiprocessor=2048,
                multiprocessor_count=30
            )
            
            gpu_info = get_gpu_info()
            
            assert gpu_info['device_name'] == "RTX 2060"
            assert gpu_info['total_memory'] == 6*1024*1024*1024
            assert gpu_info['allocated_memory'] == 1024*1024*1024
            assert gpu_info['reserved_memory'] == 2048*1024*1024
            assert gpu_info['compute_capability'] == "7.5"
            assert gpu_info['max_threads_per_block'] == 1024
            assert gpu_info['max_threads_per_multiprocessor'] == 2048
            assert gpu_info['multiprocessor_count'] == 30
    
    @patch('torch.cuda.is_available')
    def test_get_gpu_info_cuda_unavailable(self, mock_cuda_available):
        """Test get_gpu_info when CUDA is not available."""
        mock_cuda_available.return_value = False
        
        gpu_info = get_gpu_info()
        
        assert gpu_info['device_name'] == "CPU"
        assert gpu_info['total_memory'] == 0
        assert gpu_info['allocated_memory'] == 0
        assert gpu_info['reserved_memory'] == 0
        assert gpu_info['compute_capability'] == "N/A"
        assert gpu_info['max_threads_per_block'] == 0
        assert gpu_info['max_threads_per_multiprocessor'] == 0
        assert gpu_info['multiprocessor_count'] == 0


class TestGPUMemoryError:
    """Test GPUMemoryError exception."""
    
    def test_gpu_memory_error(self):
        """Test GPUMemoryError exception creation."""
        error = GPUMemoryError("GPU memory exhausted")
        assert str(error) == "GPU memory exhausted"
        assert isinstance(error, Exception)


class TestSingletonPattern:
    """Test singleton pattern for GPU manager."""
    
    def test_get_gpu_manager_singleton(self):
        """Test that get_gpu_manager returns the same instance."""
        manager1 = get_gpu_manager()
        manager2 = get_gpu_manager()
        
        assert manager1 is manager2
        assert isinstance(manager1, GPUMemoryManager)


if __name__ == "__main__":
    pytest.main([__file__])
