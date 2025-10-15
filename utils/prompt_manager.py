"""
Prompt management utilities for loading and formatting prompt templates.
"""

import os
from pathlib import Path
from typing import Dict, Optional
from string import Template


class PromptManager:
    """Manages loading and formatting of prompt templates."""

    def __init__(self, prompts_dir: Optional[Path] = None):
        """Initialize prompt manager.

        Args:
            prompts_dir: Directory containing prompt templates. Defaults to 'prompts/'.
        """
        if prompts_dir is None:
            # Find prompts directory relative to this file
            current_dir = Path(__file__).parent.parent
            self.prompts_dir = current_dir / "prompts"
        else:
            self.prompts_dir = Path(prompts_dir)

        self._prompts_cache: Dict[str, str] = {}

    def get_prompt(self, prompt_name: str, **kwargs) -> str:
        """Get a prompt template and format it with provided variables.

        Args:
            prompt_name: Name of the prompt file (without .txt extension)
            **kwargs: Variables to substitute in the template

        Returns:
            Formatted prompt string
        """
        if prompt_name not in self._prompts_cache:
            prompt_path = self.prompts_dir / f"{prompt_name}.txt"
            if not prompt_path.exists():
                raise FileNotFoundError(f"Prompt template not found: {prompt_path}")

            with open(prompt_path, 'r', encoding='utf-8') as f:
                self._prompts_cache[prompt_name] = f.read().strip()

        template = Template(self._prompts_cache[prompt_name])
        return template.safe_substitute(**kwargs)

    def get_topic_context(self, topic: str) -> str:
        """Get topic-specific context based on topic keywords.

        Args:
            topic: Topic string to analyze

        Returns:
            Topic context string
        """
        topic_lower = topic.lower()

        # Priority-based topic detection (more specific first)
        topic_patterns = [
            # Entertainment/Gaming (highest priority for specific terms)
            ('entertainment', ['game', 'gaming', 'video game', 'movie', 'film', 'tv show', 'character', 'marines', 'orcs', 'battle', 'fight', 'warrior', 'fantasy']),

            # Science (more specific terms)
            ('science', ['scientific', 'research', 'experiment', 'discovery', 'theory', 'quantum', 'physics', 'chemistry', 'biology', 'astronomy', 'evolution']),

            # Technology (specific tech terms)
            ('technology', ['software', 'hardware', 'programming', 'algorithm', 'machine learning', 'blockchain', 'cybersecurity', 'robotics']),

            # Art (creative terms)
            ('art', ['painting', 'sculpture', 'photography', 'drawing', 'gallery', 'museum', 'artist', 'creative', 'design']),

            # History (historical terms)
            ('history', ['historical', 'ancient', 'civilization', 'empire', 'war', 'battle', 'revolution', 'century', 'era']),

            # Psychology (mental health terms)
            ('psychology', ['psychological', 'cognitive', 'mental health', 'therapy', 'behavior', 'personality', 'emotion']),

            # Business (business terms)
            ('business', ['entrepreneur', 'startup', 'investment', 'profit', 'market', 'economy', 'finance', 'corporate']),

            # Broad categories (lower priority)
            ('science', ['space', 'universe', 'planet', 'star', 'galaxy']),
            ('technology', ['computer', 'phone', 'internet', 'app', 'device']),
            ('art', ['music', 'dance', 'theater', 'performance']),
        ]

        # Find the best matching topic
        for topic_file, keywords in topic_patterns:
            if any(keyword in topic_lower for keyword in keywords):
                try:
                    return self.get_prompt(f"topic_contexts/{topic_file}")
                except FileNotFoundError:
                    continue

        # Default to general knowledge
        return self.get_prompt("topic_contexts/general")

    def clear_cache(self):
        """Clear the prompt cache to force reloading from disk."""
        self._prompts_cache.clear()


# Global prompt manager instance
prompt_manager = PromptManager()
