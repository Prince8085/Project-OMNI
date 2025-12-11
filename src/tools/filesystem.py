"""
File system tools for Project OMNI.
Provides safe file operations with permission checking.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class FileSystemTools:
    """Tools for file system operations."""
    
    def __init__(self, permission_manager=None):
        """Initialize file system tools."""
        self.permission_manager = permission_manager
    
    def read_file(self, file_path: str) -> str:
        """
        Read contents of a file.
        
        Args:
            file_path: Path to file to read
            
        Returns:
            File contents as string
        """
        try:
            path = Path(file_path).expanduser()
            
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if not path.is_file():
                raise ValueError(f"Path is not a file: {file_path}")
            
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise
    
    def write_file(self, file_path: str, content: str, overwrite: bool = False) -> bool:
        """
        Write content to a file.
        
        Args:
            file_path: Path to file to write
            content: Content to write
            overwrite: Whether to overwrite existing file
            
        Returns:
            True if successful
        """
        try:
            path = Path(file_path).expanduser()
            
            # Check if file exists and overwrite is False
            if path.exists() and not overwrite:
                raise FileExistsError(f"File exists and overwrite=False: {file_path}")
            
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Successfully wrote file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error writing file {file_path}: {e}")
            raise
    
    def list_directory(self, dir_path: str, pattern: str = "*") -> List[str]:
        """
        List contents of a directory.
        
        Args:
            dir_path: Path to directory
            pattern: Glob pattern for filtering (default: "*")
            
        Returns:
            List of file/directory paths
        """
        try:
            path = Path(dir_path).expanduser()
            
            if not path.exists():
                raise FileNotFoundError(f"Directory not found: {dir_path}")
            
            if not path.is_dir():
                raise ValueError(f"Path is not a directory: {dir_path}")
            
            # List files matching pattern
            items = [str(item) for item in path.glob(pattern)]
            return sorted(items)
            
        except Exception as e:
            logger.error(f"Error listing directory {dir_path}: {e}")
            raise
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get information about a file or directory.
        
        Args:
            file_path: Path to file or directory
            
        Returns:
            Dictionary with file information
        """
        try:
            path = Path(file_path).expanduser()
            
            if not path.exists():
                raise FileNotFoundError(f"Path not found: {file_path}")
            
            stat = path.stat()
            
            info = {
                'path': str(path),
                'name': path.name,
                'is_file': path.is_file(),
                'is_dir': path.is_dir(),
                'size_bytes': stat.st_size,
                'modified_time': stat.st_mtime,
                'created_time': stat.st_ctime,
            }
            
            if path.is_file():
                info['extension'] = path.suffix
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            raise
    
    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file.
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if successful
        """
        try:
            path = Path(file_path).expanduser()
            
            if not path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            if not path.is_file():
                raise ValueError(f"Path is not a file: {file_path}")
            
            path.unlink()
            logger.info(f"Successfully deleted file: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {e}")
            raise
    
    def move_file(self, source: str, destination: str) -> bool:
        """
        Move a file from source to destination.
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Returns:
            True if successful
        """
        try:
            src_path = Path(source).expanduser()
            dst_path = Path(destination).expanduser()
            
            if not src_path.exists():
                raise FileNotFoundError(f"Source file not found: {source}")
            
            # Create destination parent directories if needed
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.move(str(src_path), str(dst_path))
            logger.info(f"Successfully moved {source} to {destination}")
            return True
            
        except Exception as e:
            logger.error(f"Error moving file from {source} to {destination}: {e}")
            raise
    
    def create_directory(self, dir_path: str) -> bool:
        """
        Create a directory.
        
        Args:
            dir_path: Path to directory to create
            
        Returns:
            True if successful
        """
        try:
            path = Path(dir_path).expanduser()
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Successfully created directory: {dir_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating directory {dir_path}: {e}")
            raise
