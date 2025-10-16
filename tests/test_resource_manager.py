"""
Unit tests for resource management utilities.

Tests the comprehensive resource management system including
context managers, resource tracking, and cleanup mechanisms.
"""

import pytest
import tempfile
import threading
import time
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
from contextlib import contextmanager

from utils.resource_manager import (
    ResourceManager,
    get_resource_manager,
    cleanup_all_resources,
    gpu_memory_context,
    temp_file_context,
    temp_directory_context,
    file_handle_context,
    process_context,
    api_client_context,
    ManagedResource,
    GPUResource,
    FileResource,
    cleanup_on_exit,
    with_resource_cleanup
)


class TestResourceManager:
    """Test ResourceManager class."""
    
    def test_initialization(self):
        """Test resource manager initialization."""
        manager = ResourceManager()
        assert manager is not None
        assert hasattr(manager, 'active_resources')
        assert hasattr(manager, 'cleanup_callbacks')
        assert isinstance(manager.active_resources, dict)
        assert isinstance(manager.cleanup_callbacks, list)
    
    def test_register_resource(self):
        """Test resource registration."""
        manager = ResourceManager()
        
        # Create a mock resource
        mock_resource = MagicMock()
        cleanup_func = MagicMock()
        
        manager.register_resource("test_resource", mock_resource, cleanup_func)
        
        assert "test_resource" in manager.active_resources
        assert manager.active_resources["test_resource"]["resource"] is mock_resource
        assert manager.active_resources["test_resource"]["cleanup_func"] is cleanup_func
        assert "created_at" in manager.active_resources["test_resource"]
    
    def test_unregister_resource(self):
        """Test resource unregistration."""
        manager = ResourceManager()
        
        # Register a resource
        mock_resource = MagicMock()
        manager.register_resource("test_resource", mock_resource)
        
        # Unregister it
        manager.unregister_resource("test_resource")
        
        assert "test_resource" not in manager.active_resources
    
    def test_cleanup_resource(self):
        """Test resource cleanup."""
        manager = ResourceManager()
        
        # Create a mock resource with cleanup function
        mock_resource = MagicMock()
        cleanup_func = MagicMock()
        
        manager.register_resource("test_resource", mock_resource, cleanup_func)
        
        # Cleanup the resource
        result = manager.cleanup_resource("test_resource")
        
        assert result is True
        cleanup_func.assert_called_once_with(mock_resource)
        assert "test_resource" not in manager.active_resources
    
    def test_cleanup_resource_not_found(self):
        """Test cleanup of non-existent resource."""
        manager = ResourceManager()
        
        result = manager.cleanup_resource("nonexistent_resource")
        
        assert result is False
    
    def test_cleanup_resource_without_cleanup_func(self):
        """Test resource cleanup without cleanup function."""
        manager = ResourceManager()
        
        # Create a mock resource without cleanup function
        mock_resource = MagicMock()
        mock_resource.close = MagicMock()
        
        manager.register_resource("test_resource", mock_resource)
        
        # Cleanup the resource
        result = manager.cleanup_resource("test_resource")
        
        assert result is True
        mock_resource.close.assert_called_once()
        assert "test_resource" not in manager.active_resources
    
    def test_cleanup_all(self):
        """Test cleanup of all resources."""
        manager = ResourceManager()
        
        # Register multiple resources
        mock_resource1 = MagicMock()
        mock_resource2 = MagicMock()
        cleanup_func1 = MagicMock()
        cleanup_func2 = MagicMock()
        
        manager.register_resource("resource1", mock_resource1, cleanup_func1)
        manager.register_resource("resource2", mock_resource2, cleanup_func2)
        
        # Cleanup all resources
        cleaned_count = manager.cleanup_all()
        
        assert cleaned_count == 2
        cleanup_func1.assert_called_once_with(mock_resource1)
        cleanup_func2.assert_called_once_with(mock_resource2)
        assert len(manager.active_resources) == 0
    
    def test_cleanup_all_with_failure(self):
        """Test cleanup of all resources with some failures."""
        manager = ResourceManager()
        
        # Register resources with one failing cleanup
        mock_resource1 = MagicMock()
        mock_resource2 = MagicMock()
        cleanup_func1 = MagicMock(side_effect=Exception("Cleanup failed"))
        cleanup_func2 = MagicMock()
        
        manager.register_resource("resource1", mock_resource1, cleanup_func1)
        manager.register_resource("resource2", mock_resource2, cleanup_func2)
        
        # Cleanup all resources
        cleaned_count = manager.cleanup_all()
        
        # Should still clean up the successful one
        assert cleaned_count == 1
        cleanup_func1.assert_called_once_with(mock_resource1)
        cleanup_func2.assert_called_once_with(mock_resource2)
        assert len(manager.active_resources) == 0


class TestContextManagers:
    """Test context managers."""
    
    @patch('torch.cuda.is_available')
    def test_gpu_memory_context(self, mock_cuda_available):
        """Test GPU memory context manager."""
        mock_cuda_available.return_value = True
        
        with patch('torch.cuda.empty_cache') as mock_empty_cache, \
             patch('torch.cuda.ipc_collect') as mock_ipc_collect, \
             patch('gc.collect') as mock_gc_collect:
            
            with gpu_memory_context(clear_cache=True):
                pass
            
            mock_empty_cache.assert_called_once()
            mock_ipc_collect.assert_called_once()
            mock_gc_collect.assert_called_once()
    
    def test_temp_file_context(self):
        """Test temporary file context manager."""
        with temp_file_context(suffix=".test", prefix="test_", delete=True) as temp_path:
            assert isinstance(temp_path, Path)
            assert temp_path.suffix == ".test"
            assert temp_path.name.startswith("test_")
            # File should exist during context
            assert temp_path.exists()
        
        # File should be deleted after context
        assert not temp_path.exists()
    
    def test_temp_directory_context(self):
        """Test temporary directory context manager."""
        with temp_directory_context(prefix="test_") as temp_dir:
            assert isinstance(temp_dir, Path)
            assert temp_dir.name.startswith("test_")
            # Directory should exist during context
            assert temp_dir.exists()
            assert temp_dir.is_dir()
        
        # Directory should be deleted after context
        assert not temp_dir.exists()
    
    def test_file_handle_context(self):
        """Test file handle context manager."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp:
            tmp.write("test content")
            tmp_path = tmp.name
        
        try:
            with file_handle_context(tmp_path, mode='r', encoding='utf-8') as f:
                content = f.read()
                assert content == "test content"
        finally:
            Path(tmp_path).unlink()
    
    def test_process_context(self):
        """Test process context manager."""
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.poll.return_value = None  # Process is running
            mock_popen.return_value = mock_process
            
            with process_context(["echo", "test"]) as process:
                assert process is mock_process
            
            # Should terminate the process
            mock_process.terminate.assert_called_once()
            mock_process.wait.assert_called_once()
    
    def test_api_client_context(self):
        """Test API client context manager."""
        class MockAPIClient:
            def __init__(self):
                self.connected = True
            
            def close(self):
                self.connected = False
        
        with api_client_context(MockAPIClient) as client:
            assert isinstance(client, MockAPIClient)
            assert client.connected is True
        
        # Client should be closed after context
        assert client.connected is False


class TestManagedResource:
    """Test ManagedResource base class."""
    
    def test_managed_resource_initialization(self):
        """Test managed resource initialization."""
        cleanup_func = MagicMock()
        resource = ManagedResource("test_resource", cleanup_func)
        
        assert resource.name == "test_resource"
        assert resource.cleanup_func is cleanup_func
        assert resource._is_cleaned_up is False
    
    def test_managed_resource_context_manager(self):
        """Test managed resource as context manager."""
        cleanup_func = MagicMock()
        
        with ManagedResource("test_resource", cleanup_func) as resource:
            assert resource.name == "test_resource"
            assert resource._is_cleaned_up is False
        
        # Cleanup should be called on exit
        cleanup_func.assert_called_once()
        assert resource._is_cleaned_up is True
    
    def test_managed_resource_cleanup(self):
        """Test managed resource cleanup method."""
        cleanup_func = MagicMock()
        resource = ManagedResource("test_resource", cleanup_func)
        
        resource.cleanup()
        
        cleanup_func.assert_called_once()
        assert resource._is_cleaned_up is True
    
    def test_managed_resource_double_cleanup(self):
        """Test that cleanup is only called once."""
        cleanup_func = MagicMock()
        resource = ManagedResource("test_resource", cleanup_func)
        
        resource.cleanup()
        resource.cleanup()  # Second cleanup should not call function
        
        cleanup_func.assert_called_once()
    
    def test_managed_resource_destructor(self):
        """Test managed resource destructor."""
        cleanup_func = MagicMock()
        resource = ManagedResource("test_resource", cleanup_func)
        
        del resource
        
        cleanup_func.assert_called_once()


class TestGPUResource:
    """Test GPUResource class."""
    
    @patch('torch.cuda.is_available')
    def test_gpu_resource_cleanup(self, mock_cuda_available):
        """Test GPU resource cleanup."""
        mock_cuda_available.return_value = True
        
        with patch('torch.cuda.empty_cache') as mock_empty_cache, \
             patch('torch.cuda.ipc_collect') as mock_ipc_collect, \
             patch('gc.collect') as mock_gc_collect:
            
            resource = GPUResource("test_gpu")
            resource.cleanup()
            
            mock_empty_cache.assert_called_once()
            mock_ipc_collect.assert_called_once()
            mock_gc_collect.assert_called_once()
    
    @patch('torch.cuda.is_available')
    def test_gpu_resource_context_manager(self, mock_cuda_available):
        """Test GPU resource as context manager."""
        mock_cuda_available.return_value = True
        
        with patch('torch.cuda.empty_cache') as mock_empty_cache, \
             patch('torch.cuda.ipc_collect') as mock_ipc_collect, \
             patch('gc.collect') as mock_gc_collect:
            
            with GPUResource("test_gpu") as resource:
                assert resource.name == "test_gpu"
            
            # Cleanup should be called on exit
            mock_empty_cache.assert_called_once()
            mock_ipc_collect.assert_called_once()
            mock_gc_collect.assert_called_once()


class TestFileResource:
    """Test FileResource class."""
    
    def test_file_resource_cleanup(self):
        """Test file resource cleanup."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            resource = FileResource(tmp_path, "test_file")
            resource.cleanup()
            
            # File should be deleted
            assert not Path(tmp_path).exists()
        finally:
            # Cleanup in case test fails
            if Path(tmp_path).exists():
                Path(tmp_path).unlink()
    
    def test_file_resource_context_manager(self):
        """Test file resource as context manager."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = tmp.name
        
        try:
            with FileResource(tmp_path, "test_file") as resource:
                assert resource.file_path == Path(tmp_path)
                assert Path(tmp_path).exists()
            
            # File should be deleted after context
            assert not Path(tmp_path).exists()
        finally:
            # Cleanup in case test fails
            if Path(tmp_path).exists():
                Path(tmp_path).unlink()


class TestDecorators:
    """Test decorators."""
    
    def test_cleanup_on_exit(self):
        """Test cleanup_on_exit decorator."""
        cleanup_func = MagicMock()
        
        @cleanup_on_exit
        def test_cleanup():
            cleanup_func()
        
        # The function should be registered for cleanup on exit
        # We can't easily test the actual exit behavior, but we can verify
        # the function is callable
        assert callable(test_cleanup)
    
    def test_with_resource_cleanup(self):
        """Test with_resource_cleanup decorator."""
        cleanup_func = MagicMock()
        
        @with_resource_cleanup(cleanup_func)
        def test_func():
            return "success"
        
        result = test_func()
        
        assert result == "success"
        cleanup_func.assert_called_once()
    
    def test_with_resource_cleanup_exception(self):
        """Test with_resource_cleanup decorator with exception."""
        cleanup_func = MagicMock()
        
        @with_resource_cleanup(cleanup_func)
        def test_func():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            test_func()
        
        # Cleanup should still be called even with exception
        cleanup_func.assert_called_once()


class TestSingletonPattern:
    """Test singleton pattern for resource manager."""
    
    def test_get_resource_manager_singleton(self):
        """Test that get_resource_manager returns the same instance."""
        manager1 = get_resource_manager()
        manager2 = get_resource_manager()
        
        assert manager1 is manager2
        assert isinstance(manager1, ResourceManager)
    
    def test_cleanup_all_resources(self):
        """Test cleanup_all_resources function."""
        manager = get_resource_manager()
        
        # Register a test resource
        mock_resource = MagicMock()
        cleanup_func = MagicMock()
        manager.register_resource("test_resource", mock_resource, cleanup_func)
        
        # Cleanup all resources
        cleaned_count = cleanup_all_resources()
        
        assert cleaned_count == 1
        cleanup_func.assert_called_once_with(mock_resource)


if __name__ == "__main__":
    pytest.main([__file__])
