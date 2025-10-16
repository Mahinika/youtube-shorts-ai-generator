"""
File Operations Utilities

Provides common file operations, path management, and file system utilities
for the YouTube Shorts automation system.
"""

import os
import shutil
import tempfile
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Generator
from contextlib import contextmanager
from utils.error_handler import FileOperationError, ValidationError
from utils.validation_utils import validate_file_path_input, validate_string_input


logger = logging.getLogger(__name__)


class FileManager:
    """
    Centralized file management utility for the YouTube Shorts automation system.
    
    Provides safe file operations, path management, and cleanup utilities.
    """
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize file manager.
        
        Args:
            base_dir: Base directory for file operations (defaults to project root)
        """
        if base_dir is None:
            base_dir = Path(__file__).parent.parent
        
        self.base_dir = base_dir.resolve()
        self.temp_dir = self.base_dir / "temp_files"
        self.output_dir = self.base_dir / "finished_videos"
        self.logs_dir = self.base_dir / "logs"
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        directories = [self.temp_dir, self.output_dir, self.logs_dir]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Ensured directory exists: {directory}")
    
    def safe_write(self, file_path: Union[str, Path], content: str, encoding: str = 'utf-8') -> Path:
        """
        Safely write content to a file with atomic operation.
        
        Args:
            file_path: Path to write to
            content: Content to write
            encoding: File encoding
            
        Returns:
            Path to the written file
            
        Raises:
            FileOperationError: If write operation fails
        """
        try:
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to temporary file first, then move (atomic operation)
            temp_path = file_path.with_suffix(file_path.suffix + '.tmp')
            
            with open(temp_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            # Atomic move
            shutil.move(str(temp_path), str(file_path))
            
            logger.debug(f"Successfully wrote {len(content)} characters to {file_path}")
            return file_path
            
        except Exception as e:
            raise FileOperationError(
                f"Failed to write file {file_path}: {e}",
                error_code="WRITE_FAILED",
                details={"file_path": str(file_path), "content_length": len(content)}
            )
    
    def safe_read(self, file_path: Union[str, Path], encoding: str = 'utf-8') -> str:
        """
        Safely read content from a file.
        
        Args:
            file_path: Path to read from
            encoding: File encoding
            
        Returns:
            File content as string
            
        Raises:
            FileOperationError: If read operation fails
        """
        try:
            file_path = validate_file_path_input(
                file_path, "file_path", must_exist=True, must_be_file=True
            )
            
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            
            logger.debug(f"Successfully read {len(content)} characters from {file_path}")
            return content
            
        except Exception as e:
            raise FileOperationError(
                f"Failed to read file {file_path}: {e}",
                error_code="READ_FAILED",
                details={"file_path": str(file_path)}
            )
    
    def safe_copy(self, src: Union[str, Path], dst: Union[str, Path]) -> Path:
        """
        Safely copy a file.
        
        Args:
            src: Source file path
            dst: Destination file path
            
        Returns:
            Path to the copied file
            
        Raises:
            FileOperationError: If copy operation fails
        """
        try:
            src_path = validate_file_path_input(
                src, "src", must_exist=True, must_be_file=True
            )
            dst_path = Path(dst)
            
            # Ensure destination directory exists
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(src_path, dst_path)
            
            logger.debug(f"Successfully copied {src_path} to {dst_path}")
            return dst_path
            
        except Exception as e:
            raise FileOperationError(
                f"Failed to copy file {src} to {dst}: {e}",
                error_code="COPY_FAILED",
                details={"src": str(src), "dst": str(dst)}
            )
    
    def safe_move(self, src: Union[str, Path], dst: Union[str, Path]) -> Path:
        """
        Safely move a file.
        
        Args:
            src: Source file path
            dst: Destination file path
            
        Returns:
            Path to the moved file
            
        Raises:
            FileOperationError: If move operation fails
        """
        try:
            src_path = validate_file_path_input(
                src, "src", must_exist=True, must_be_file=True
            )
            dst_path = Path(dst)
            
            # Ensure destination directory exists
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(src_path), str(dst_path))
            
            logger.debug(f"Successfully moved {src_path} to {dst_path}")
            return dst_path
            
        except Exception as e:
            raise FileOperationError(
                f"Failed to move file {src} to {dst}: {e}",
                error_code="MOVE_FAILED",
                details={"src": str(src), "dst": str(dst)}
            )
    
    def get_unique_filename(self, base_path: Union[str, Path], max_attempts: int = 1000) -> Path:
        """
        Get a unique filename by adding a counter if the file exists.
        
        Args:
            base_path: Base file path
            max_attempts: Maximum number of attempts to find unique name
            
        Returns:
            Unique file path
            
        Raises:
            FileOperationError: If unable to find unique filename
        """
        base_path = Path(base_path)
        
        if not base_path.exists():
            return base_path
        
        stem = base_path.stem
        suffix = base_path.suffix
        parent = base_path.parent
        
        for i in range(1, max_attempts + 1):
            new_path = parent / f"{stem}_{i}{suffix}"
            if not new_path.exists():
                logger.debug(f"Found unique filename: {new_path}")
                return new_path
        
        raise FileOperationError(
            f"Unable to find unique filename for {base_path} after {max_attempts} attempts",
            error_code="UNIQUE_FILENAME_FAILED",
            details={"base_path": str(base_path), "max_attempts": max_attempts}
        )
    
    def cleanup_temp_files(self, pattern: str = "*", max_age_hours: int = 24) -> int:
        """
        Clean up temporary files older than specified age.
        
        Args:
            pattern: File pattern to match
            max_age_hours: Maximum age in hours
            
        Returns:
            Number of files cleaned up
        """
        import time
        
        cleaned_count = 0
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600
        
        try:
            for file_path in self.temp_dir.glob(pattern):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > max_age_seconds:
                        file_path.unlink()
                        cleaned_count += 1
                        logger.debug(f"Cleaned up old temp file: {file_path}")
            
            logger.info(f"Cleaned up {cleaned_count} temporary files")
            return cleaned_count
            
        except Exception as e:
            logger.warning(f"Error during temp file cleanup: {e}")
            return cleaned_count
    
    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get detailed information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
            
        Raises:
            FileOperationError: If file info cannot be retrieved
        """
        try:
            file_path = validate_file_path_input(
                file_path, "file_path", must_exist=True, must_be_file=True
            )
            
            stat = file_path.stat()
            
            return {
                "path": str(file_path),
                "name": file_path.name,
                "size": stat.st_size,
                "size_mb": round(stat.st_size / 1024 / 1024, 2),
                "created": stat.st_ctime,
                "modified": stat.st_mtime,
                "extension": file_path.suffix,
                "is_readable": os.access(file_path, os.R_OK),
                "is_writable": os.access(file_path, os.W_OK)
            }
            
        except Exception as e:
            raise FileOperationError(
                f"Failed to get file info for {file_path}: {e}",
                error_code="FILE_INFO_FAILED",
                details={"file_path": str(file_path)}
            )
    
    def find_files(self, pattern: str, directory: Optional[Path] = None) -> List[Path]:
        """
        Find files matching a pattern.
        
        Args:
            pattern: File pattern to match
            directory: Directory to search in (defaults to temp_dir)
            
        Returns:
            List of matching file paths
        """
        if directory is None:
            directory = self.temp_dir
        
        try:
            files = list(directory.glob(pattern))
            logger.debug(f"Found {len(files)} files matching pattern '{pattern}' in {directory}")
            return files
        except Exception as e:
            logger.warning(f"Error finding files with pattern '{pattern}': {e}")
            return []
    
    @contextmanager
    def temp_file(self, suffix: str = ".tmp", prefix: str = "temp_") -> Generator[Path, None, None]:
        """
        Context manager for temporary files.
        
        Args:
            suffix: File suffix
            prefix: File prefix
            
        Yields:
            Path to temporary file
        """
        temp_file = None
        try:
            temp_file = tempfile.NamedTemporaryFile(
                suffix=suffix, prefix=prefix, dir=self.temp_dir, delete=False
            )
            temp_path = Path(temp_file.name)
            temp_file.close()
            
            logger.debug(f"Created temporary file: {temp_path}")
            yield temp_path
            
        finally:
            if temp_file and temp_path.exists():
                try:
                    temp_path.unlink()
                    logger.debug(f"Cleaned up temporary file: {temp_path}")
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary file {temp_path}: {e}")


def get_file_manager(base_dir: Optional[Path] = None) -> FileManager:
    """
    Get a FileManager instance.
    
    Args:
        base_dir: Base directory for file operations
        
    Returns:
        FileManager instance
    """
    return FileManager(base_dir)


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: Directory path
        
    Returns:
        Path to the directory
    """
    try:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Ensured directory exists: {path}")
        return path
    except Exception as e:
        raise FileOperationError(
            f"Failed to create directory {path}: {e}",
            error_code="DIRECTORY_CREATION_FAILED",
            details={"path": str(path)}
        )


def get_safe_filename(filename: str, max_length: int = 100) -> str:
    """
    Get a safe filename by removing invalid characters and limiting length.
    
    Args:
        filename: Original filename
        max_length: Maximum filename length
        
    Returns:
        Safe filename
    """
    import re
    
    # Remove invalid characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove multiple underscores
    safe_name = re.sub(r'_+', '_', safe_name)
    
    # Remove leading/trailing underscores and dots
    safe_name = safe_name.strip('_.')
    
    # Limit length
    if len(safe_name) > max_length:
        name, ext = os.path.splitext(safe_name)
        safe_name = name[:max_length - len(ext)] + ext
    
    # Ensure it's not empty
    if not safe_name:
        safe_name = "unnamed_file"
    
    return safe_name


def get_file_size_mb(file_path: Union[str, Path]) -> float:
    """
    Get file size in megabytes.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File size in megabytes
    """
    try:
        file_path = validate_file_path_input(
            file_path, "file_path", must_exist=True, must_be_file=True
        )
        size_bytes = file_path.stat().st_size
        return round(size_bytes / 1024 / 1024, 2)
    except Exception as e:
        logger.warning(f"Could not get file size for {file_path}: {e}")
        return 0.0


def is_video_file(file_path: Union[str, Path]) -> bool:
    """
    Check if a file is a video file based on extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file is a video file
    """
    video_extensions = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv'}
    return Path(file_path).suffix.lower() in video_extensions


def is_audio_file(file_path: Union[str, Path]) -> bool:
    """
    Check if a file is an audio file based on extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file is an audio file
    """
    audio_extensions = {'.mp3', '.wav', '.m4a', '.aac', '.ogg', '.flac', '.wma'}
    return Path(file_path).suffix.lower() in audio_extensions


def is_image_file(file_path: Union[str, Path]) -> bool:
    """
    Check if a file is an image file based on extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file is an image file
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    return Path(file_path).suffix.lower() in image_extensions
