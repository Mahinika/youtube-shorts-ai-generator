"""
Data Processing Utilities

Provides common data processing, transformation, and analysis utilities
for the YouTube Shorts automation system.
"""

import json
import re
import logging
from typing import Any, Dict, List, Optional, Union, Tuple, Callable
from pathlib import Path
from utils.error_handler import ValidationError, FileOperationError
from utils.validation_utils import validate_string_input, validate_list_input


logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Centralized data processing utility for the YouTube Shorts automation system.
    
    Provides common data transformation, analysis, and processing functions.
    """
    
    def __init__(self):
        """Initialize data processor."""
        self.logger = logging.getLogger(f"{__name__}.DataProcessor")
    
    def clean_text(self, text: str, remove_emojis: bool = True, remove_special_chars: bool = False) -> str:
        """
        Clean and normalize text content.
        
        Args:
            text: Text to clean
            remove_emojis: Whether to remove emojis
            remove_special_chars: Whether to remove special characters
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        if remove_emojis:
            # Remove emojis and Unicode symbols
            emoji_pattern = re.compile(
                "["
                "\U0001F600-\U0001F64F"  # emoticons
                "\U0001F300-\U0001F5FF"  # symbols & pictographs
                "\U0001F680-\U0001F6FF"  # transport & map symbols
                "\U0001F1E0-\U0001F1FF"  # flags (iOS)
                "\U00002702-\U000027B0"  # dingbats
                "\U000024C2-\U0001F251"  # enclosed characters
                "\U0001F900-\U0001F9FF"  # supplemental symbols
                "\U0001FA70-\U0001FAFF"  # symbols and pictographs extended-A
                "\U00002600-\U000026FF"  # miscellaneous symbols
                "\U00002700-\U000027BF"  # dingbats
                "]+", 
                flags=re.UNICODE
            )
            text = emoji_pattern.sub('', text)
        
        if remove_special_chars:
            # Keep only alphanumeric characters and basic punctuation
            text = re.sub(r'[^a-zA-Z0-9\s.,!?;:\-()]', '', text)
        
        # Clean up multiple spaces again
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def extract_keywords(self, text: str, min_length: int = 3, max_keywords: int = 20) -> List[str]:
        """
        Extract keywords from text.
        
        Args:
            text: Text to extract keywords from
            min_length: Minimum keyword length
            max_keywords: Maximum number of keywords to return
            
        Returns:
            List of keywords
        """
        if not text:
            return []
        
        # Clean text
        clean_text = self.clean_text(text, remove_emojis=True, remove_special_chars=True)
        
        # Split into words and filter
        words = re.findall(r'\b[a-zA-Z]+\b', clean_text.lower())
        
        # Filter by length and frequency
        word_counts = {}
        for word in words:
            if len(word) >= min_length:
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Sort by frequency and length
        keywords = sorted(
            word_counts.keys(),
            key=lambda w: (word_counts[w], len(w)),
            reverse=True
        )
        
        return keywords[:max_keywords]
    
    def estimate_reading_time(self, text: str, words_per_minute: int = 200) -> float:
        """
        Estimate reading time for text.
        
        Args:
            text: Text to analyze
            words_per_minute: Average reading speed
            
        Returns:
            Estimated reading time in minutes
        """
        if not text:
            return 0.0
        
        # Count words
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words)
        
        # Calculate reading time
        reading_time = word_count / words_per_minute
        
        return round(reading_time, 2)
    
    def split_text_into_chunks(self, text: str, max_chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """
        Split text into overlapping chunks.
        
        Args:
            text: Text to split
            max_chunk_size: Maximum chunk size
            overlap: Overlap between chunks
            
        Returns:
            List of text chunks
        """
        if not text or len(text) <= max_chunk_size:
            return [text] if text else []
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + max_chunk_size
            
            # Try to break at word boundary
            if end < len(text):
                # Find last space before end
                last_space = text.rfind(' ', start, end)
                if last_space > start:
                    end = last_space
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - overlap
            if start >= len(text):
                break
        
        return chunks
    
    def normalize_json_data(self, data: Any) -> Any:
        """
        Normalize JSON data by converting to standard types.
        
        Args:
            data: Data to normalize
            
        Returns:
            Normalized data
        """
        if isinstance(data, dict):
            return {str(k): self.normalize_json_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.normalize_json_data(item) for item in data]
        elif isinstance(data, (int, float, str, bool, type(None))):
            return data
        else:
            # Convert other types to string
            return str(data)
    
    def validate_json_structure(self, data: Dict[str, Any], required_fields: List[str]) -> bool:
        """
        Validate JSON structure has required fields.
        
        Args:
            data: Data to validate
            required_fields: List of required field names
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(data, dict):
            return False
        
        for field in required_fields:
            if field not in data:
                return False
        
        return True
    
    def merge_dictionaries(self, *dicts: Dict[str, Any], deep: bool = True) -> Dict[str, Any]:
        """
        Merge multiple dictionaries.
        
        Args:
            *dicts: Dictionaries to merge
            deep: Whether to perform deep merge
            
        Returns:
            Merged dictionary
        """
        if not dicts:
            return {}
        
        result = dicts[0].copy()
        
        for d in dicts[1:]:
            if deep:
                result = self._deep_merge(result, d)
            else:
                result.update(d)
        
        return result
    
    def _deep_merge(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Deep merge two dictionaries."""
        result = dict1.copy()
        
        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts using simple word overlap.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        if not text1 or not text2:
            return 0.0
        
        # Clean and normalize texts
        clean1 = set(self.clean_text(text1, remove_special_chars=True).lower().split())
        clean2 = set(self.clean_text(text2, remove_special_chars=True).lower().split())
        
        if not clean1 or not clean2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(clean1.intersection(clean2))
        union = len(clean1.union(clean2))
        
        return intersection / union if union > 0 else 0.0
    
    def extract_metadata(self, text: str) -> Dict[str, Any]:
        """
        Extract metadata from text content.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with metadata
        """
        if not text:
            return {}
        
        # Basic statistics
        word_count = len(re.findall(r'\b\w+\b', text))
        char_count = len(text)
        line_count = len(text.splitlines())
        
        # Extract potential hashtags
        hashtags = re.findall(r'#\w+', text)
        
        # Extract potential mentions
        mentions = re.findall(r'@\w+', text)
        
        # Extract URLs
        urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
        
        # Estimate reading time
        reading_time = self.estimate_reading_time(text)
        
        return {
            "word_count": word_count,
            "char_count": char_count,
            "line_count": line_count,
            "hashtags": hashtags,
            "mentions": mentions,
            "urls": urls,
            "reading_time_minutes": reading_time,
            "keywords": self.extract_keywords(text, max_keywords=10)
        }


def process_script_data(script_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process and normalize script data.
    
    Args:
        script_data: Raw script data
        
    Returns:
        Processed script data
        
    Raises:
        ValidationError: If script data is invalid
    """
    processor = DataProcessor()
    
    # Validate required fields
    required_fields = ["title", "script", "scene_descriptions"]
    if not processor.validate_json_structure(script_data, required_fields):
        raise ValidationError(
            "Script data missing required fields",
            error_code="MISSING_REQUIRED_FIELDS",
            details={"required_fields": required_fields, "provided_fields": list(script_data.keys())}
        )
    
    # Process and clean text fields
    processed_data = {}
    
    for key, value in script_data.items():
        if isinstance(value, str):
            # Clean text content
            processed_data[key] = processor.clean_text(value)
        elif key == "scene_descriptions" and isinstance(value, list):
            # Process scene descriptions
            processed_data[key] = [
                processor.clean_text(desc) for desc in value
                if isinstance(desc, str)
            ]
        else:
            processed_data[key] = value
    
    # Add metadata
    if "script" in processed_data:
        metadata = processor.extract_metadata(processed_data["script"])
        processed_data["metadata"] = metadata
    
    return processed_data


def extract_timestamps_from_script(script: str, duration: float) -> List[Dict[str, Any]]:
    """
    Extract word timestamps from script for caption generation.
    
    Args:
        script: Script text
        duration: Total duration in seconds
        
    Returns:
        List of word timestamp dictionaries
    """
    processor = DataProcessor()
    
    # Clean script
    clean_script = processor.clean_text(script)
    
    # Split into words
    words = re.findall(r'\b\w+\b', clean_script)
    
    if not words:
        return []
    
    # Calculate timing
    time_per_word = duration / len(words)
    
    timestamps = []
    current_time = 0.0
    
    for word in words:
        timestamps.append({
            "word": word,
            "start_time": round(current_time, 2),
            "end_time": round(current_time + time_per_word, 2),
            "duration": round(time_per_word, 2)
        })
        current_time += time_per_word
    
    return timestamps


def analyze_content_quality(content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze content quality and provide recommendations.
    
    Args:
        content: Content dictionary to analyze
        
    Returns:
        Quality analysis results
    """
    processor = DataProcessor()
    
    analysis = {
        "overall_score": 0.0,
        "issues": [],
        "recommendations": [],
        "metrics": {}
    }
    
    # Analyze title
    if "title" in content:
        title = content["title"]
        title_length = len(title)
        
        if title_length < 10:
            analysis["issues"].append("Title too short")
            analysis["recommendations"].append("Make title more descriptive (10+ characters)")
        elif title_length > 100:
            analysis["issues"].append("Title too long")
            analysis["recommendations"].append("Shorten title (under 100 characters)")
        else:
            analysis["overall_score"] += 0.2
    
    # Analyze script
    if "script" in content:
        script = content["script"]
        script_metadata = processor.extract_metadata(script)
        
        analysis["metrics"]["word_count"] = script_metadata["word_count"]
        analysis["metrics"]["reading_time"] = script_metadata["reading_time_minutes"]
        
        if script_metadata["word_count"] < 50:
            analysis["issues"].append("Script too short")
            analysis["recommendations"].append("Add more content (50+ words)")
        elif script_metadata["word_count"] > 500:
            analysis["issues"].append("Script too long")
            analysis["recommendations"].append("Consider shortening script (under 500 words)")
        else:
            analysis["overall_score"] += 0.4
        
        # Check for engaging elements
        if any(word in script.lower() for word in ["amazing", "incredible", "unbelievable", "wow"]):
            analysis["overall_score"] += 0.1
        
        if "?" in script:
            analysis["overall_score"] += 0.1  # Questions engage viewers
    
    # Analyze scene descriptions
    if "scene_descriptions" in content:
        scenes = content["scene_descriptions"]
        
        if len(scenes) < 2:
            analysis["issues"].append("Too few scenes")
            analysis["recommendations"].append("Add more visual variety (2+ scenes)")
        elif len(scenes) > 8:
            analysis["issues"].append("Too many scenes")
            analysis["recommendations"].append("Reduce scene count for better pacing (under 8 scenes)")
        else:
            analysis["overall_score"] += 0.2
        
        # Check scene quality
        for i, scene in enumerate(scenes):
            if len(scene) < 10:
                analysis["issues"].append(f"Scene {i+1} description too short")
                analysis["recommendations"].append(f"Make scene {i+1} description more detailed")
    
    # Check for keywords
    if "search_keywords" in content:
        keywords = content["search_keywords"]
        if len(keywords) < 3:
            analysis["issues"].append("Too few keywords")
            analysis["recommendations"].append("Add more search keywords (3+ keywords)")
        else:
            analysis["overall_score"] += 0.1
    
    # Normalize score
    analysis["overall_score"] = min(1.0, analysis["overall_score"])
    
    return analysis


def create_data_summary(data: Dict[str, Any]) -> str:
    """
    Create a human-readable summary of data.
    
    Args:
        data: Data to summarize
        
    Returns:
        Summary string
    """
    processor = DataProcessor()
    
    summary_parts = []
    
    if "title" in data:
        summary_parts.append(f"Title: {data['title']}")
    
    if "script" in data:
        script_metadata = processor.extract_metadata(data["script"])
        summary_parts.append(f"Script: {script_metadata['word_count']} words, {script_metadata['reading_time_minutes']:.1f} min read")
    
    if "scene_descriptions" in data:
        summary_parts.append(f"Scenes: {len(data['scene_descriptions'])} descriptions")
    
    if "duration_seconds" in data:
        summary_parts.append(f"Duration: {data['duration_seconds']:.1f} seconds")
    
    return " | ".join(summary_parts)
