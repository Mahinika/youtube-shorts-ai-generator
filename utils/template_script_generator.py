"""
Template-based Script Generator

Provides fallback script generation using predefined templates when AI providers fail.
Replaces Ollama as the fallback system with more reliable template-based content.
"""

import random
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from utils.logging_utils import get_logger

logger = get_logger("template_generator")


class TemplateScriptGenerator:
    """Generates YouTube Shorts scripts using predefined templates."""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.topic_keywords = self._load_topic_keywords()
    
    def _load_templates(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load script templates for different content types."""
        return {
            "fact_based": [
                {
                    "hook": "Did you know {topic}?",
                    "content": "Here's something that will blow your mind: {fact}. This is actually more common than you think!",
                    "engagement": "Want to know more about {topic}? Comment '{keyword}' below!",
                    "scene_descriptions": [
                        "Dynamic {topic} themed opening with bold text overlay",
                        "Close-up visual showcasing the key {topic} element",
                        "Animated graphics highlighting the surprising fact",
                        "Fast-paced montage of related {topic} examples",
                        "Engaging conclusion with call-to-action text"
                    ]
                },
                {
                    "hook": "This {topic} fact will shock you!",
                    "content": "Most people think {common_misconception}, but the truth is {actual_fact}. This changes everything!",
                    "engagement": "Did this surprise you? Comment your thoughts below!",
                    "scene_descriptions": [
                        "Eye-catching {topic} visual with shocking text reveal",
                        "Split-screen showing misconception vs reality",
                        "Animated data visualization of the fact",
                        "Dynamic montage of {topic} examples",
                        "Strong call-to-action with engagement prompt"
                    ]
                }
            ],
            "explanatory": [
                {
                    "hook": "Why does {topic} work this way?",
                    "content": "The answer is simpler than you think: {explanation}. Here's how it actually works...",
                    "engagement": "What else would you like to know about {topic}? Comment below!",
                    "scene_descriptions": [
                        "Clean, educational {topic} opening scene",
                        "Step-by-step visual explanation",
                        "Animated diagram showing the process",
                        "Real-world examples of {topic} in action",
                        "Clear conclusion with learning prompt"
                    ]
                },
                {
                    "hook": "Ever wondered about {topic}?",
                    "content": "It's actually fascinating: {explanation}. The science behind this is incredible!",
                    "engagement": "What's your take on {topic}? Share your thoughts!",
                    "scene_descriptions": [
                        "Curious, engaging {topic} introduction",
                        "Scientific visualization of the concept",
                        "Animated explanation with clear graphics",
                        "Multiple examples showing {topic} in practice",
                        "Thought-provoking conclusion"
                    ]
                }
            ],
            "story_based": [
                {
                    "hook": "The story of {topic} is incredible!",
                    "content": "It all started when {story_beginning}. What happened next will amaze you: {story_development}.",
                    "engagement": "What's your favorite {topic} story? Tell us below!",
                    "scene_descriptions": [
                        "Cinematic {topic} story opening",
                        "Historical or narrative visual sequence",
                        "Dramatic moment in the {topic} story",
                        "Climactic scene showing the outcome",
                        "Reflective conclusion with story prompt"
                    ]
                }
            ],
            "comparison": [
                {
                    "hook": "{topic1} vs {topic2} - which is better?",
                    "content": "Here's the surprising truth: {comparison}. Most people get this wrong!",
                    "engagement": "Which do you prefer? Comment your choice!",
                    "scene_descriptions": [
                        "Split-screen {topic1} vs {topic2} comparison",
                        "Side-by-side visual analysis",
                        "Animated comparison chart or graphic",
                        "Real-world examples of both options",
                        "Clear conclusion with preference prompt"
                    ]
                }
            ],
            "how_to": [
                {
                    "hook": "Want to {action}? Here's how!",
                    "content": "It's easier than you think: {step1}. Then {step2}. That's it!",
                    "engagement": "Try it and let me know how it goes! Comment your results!",
                    "scene_descriptions": [
                        "Clear {action} tutorial opening",
                        "Step 1 visual demonstration",
                        "Step 2 visual demonstration",
                        "Final result showing success",
                        "Encouraging conclusion with try-it prompt"
                    ]
                }
            ]
        }
    
    def _load_topic_keywords(self) -> Dict[str, List[str]]:
        """Load topic-specific keywords for better template matching."""
        return {
            "science": ["discovery", "research", "experiment", "study", "scientific", "data", "evidence"],
            "technology": ["innovation", "digital", "tech", "app", "software", "hardware", "AI", "future"],
            "history": ["ancient", "historical", "past", "timeline", "era", "century", "civilization"],
            "nature": ["natural", "wildlife", "environment", "ecosystem", "species", "habitat", "conservation"],
            "space": ["cosmic", "astronomical", "galaxy", "planet", "universe", "space", "NASA", "exploration"],
            "psychology": ["mental", "brain", "behavior", "psychology", "cognitive", "emotional", "mind"],
            "business": ["entrepreneur", "startup", "investment", "market", "economy", "finance", "success"],
            "entertainment": ["movie", "music", "celebrity", "entertainment", "culture", "trend", "viral"],
            "health": ["medical", "health", "fitness", "wellness", "disease", "treatment", "medicine"],
            "general": ["amazing", "incredible", "fascinating", "surprising", "interesting", "cool", "awesome"]
        }
    
    def _detect_content_type(self, prompt: str) -> str:
        """Detect the type of content based on the prompt."""
        prompt_lower = prompt.lower()
        
        # How-to indicators (check first to avoid being overridden by 'how' in question words)
        if any(phrase in prompt_lower for phrase in ['how to', 'learn to', 'tutorial', 'guide', 'steps to', 'way to', 'teach me']):
            return "how_to"
        
        # Comparison words suggest comparison content
        if any(word in prompt_lower for word in ['vs', 'versus', 'compare', 'difference', 'better', 'best']):
            return "comparison"
        
        # Story indicators
        if any(word in prompt_lower for word in ['story', 'history', 'tale', 'legend', 'myth', 'origin']):
            return "story_based"
        
        # Question words suggest explanatory content (check after how-to)
        if any(word in prompt_lower for word in ['what', 'why', 'how', 'when', 'where', 'explain', 'tell me']):
            return "explanatory"
        
        # Default to fact-based for most prompts
        return "fact_based"
    
    def _detect_topic_category(self, prompt: str) -> str:
        """Detect the topic category for better keyword matching."""
        prompt_lower = prompt.lower()
        
        for category, keywords in self.topic_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                return category
        
        return "general"
    
    def _generate_fact_content(self, prompt: str, template: Dict[str, Any]) -> Dict[str, str]:
        """Generate fact-based content using the template."""
        topic = prompt.split()[0] if prompt else "this topic"
        keyword = topic.upper()[:4] if len(topic) >= 4 else "FACT"
        
        # Generate a fact based on the topic
        facts = {
            "phone": "your phone tracks you 2,617 times per day",
            "brain": "your brain processes 70,000 thoughts daily",
            "space": "there are more stars than grains of sand on Earth",
            "ocean": "we've explored less than 5% of our oceans",
            "internet": "90% of the world's data was created in the last 2 years",
            "sleep": "you spend 1/3 of your life sleeping",
            "water": "your body is 60% water",
            "heart": "your heart beats 100,000 times per day"
        }
        
        # Find a relevant fact or create a generic one
        fact = facts.get(topic.lower(), f"{topic} is more fascinating than most people realize")
        common_misconception = f"most people think {topic} is simple"
        actual_fact = f"it's actually incredibly complex and amazing"
        
        return {
            "topic": topic,
            "fact": fact,
            "common_misconception": common_misconception,
            "actual_fact": actual_fact,
            "keyword": keyword
        }
    
    def _generate_explanatory_content(self, prompt: str, template: Dict[str, Any]) -> Dict[str, str]:
        """Generate explanatory content using the template."""
        topic = prompt.split()[0] if prompt else "this concept"
        
        explanations = {
            "memory": "your brain stores memories by strengthening neural connections",
            "gravity": "mass warps spacetime, creating the force we feel as gravity",
            "photosynthesis": "plants convert sunlight into energy using chlorophyll",
            "evolution": "species change over time through natural selection",
            "electricity": "electrons flow through conductors creating electrical current",
            "dreams": "your brain processes memories and emotions while you sleep"
        }
        
        explanation = explanations.get(topic.lower(), f"{topic} works through a fascinating process that most people don't understand")
        
        return {
            "topic": topic,
            "explanation": explanation
        }
    
    def _generate_story_content(self, prompt: str, template: Dict[str, Any]) -> Dict[str, str]:
        """Generate story-based content using the template."""
        topic = prompt.split()[0] if prompt else "this amazing story"
        
        stories = {
            "internet": "a small team of scientists wanted to share research data",
            "penicillin": "a scientist noticed mold growing on a forgotten petri dish",
            "post-it": "a scientist was trying to create super-strong glue but failed",
            "microwave": "a radar engineer noticed his chocolate bar melted in his pocket",
            "velcro": "a Swiss engineer noticed burrs sticking to his dog's fur"
        }
        
        story_beginning = stories.get(topic.lower(), f"it all started with a simple idea about {topic}")
        story_development = f"what happened next revolutionized everything we know about {topic}"
        
        return {
            "topic": topic,
            "story_beginning": story_beginning,
            "story_development": story_development
        }
    
    def _generate_comparison_content(self, prompt: str, template: Dict[str, Any]) -> Dict[str, str]:
        """Generate comparison content using the template."""
        # Handle "vs" and "versus" separators
        if " vs " in prompt.lower():
            parts = prompt.split(" vs ", 1)
            topic1 = parts[0].strip()
            topic2 = parts[1].strip()
        elif " versus " in prompt.lower():
            parts = prompt.split(" versus ", 1)
            topic1 = parts[0].strip()
            topic2 = parts[1].strip()
        else:
            words = prompt.split()
            topic1 = words[0] if len(words) > 0 else "Option A"
            topic2 = words[1] if len(words) > 1 else "Option B"
        
        comparisons = {
            "iphone android": "iPhone vs Android - both have unique strengths",
            "coffee tea": "Coffee vs Tea - both have different benefits",
            "cardio strength": "Cardio vs Strength - both are important",
            "keto paleo": "Keto vs Paleo - both work for different people"
        }
        
        comparison_key = f"{topic1.lower()} {topic2.lower()}"
        comparison = comparisons.get(comparison_key, f"{topic1} and {topic2} each have their own advantages")
        
        return {
            "topic1": topic1,
            "topic2": topic2,
            "comparison": comparison
        }
    
    def _generate_how_to_content(self, prompt: str, template: Dict[str, Any]) -> Dict[str, str]:
        """Generate how-to content using the template."""
        action = prompt.lower().replace('how to', '').strip() if 'how to' in prompt.lower() else prompt
        topic = action.split()[0] if action else "this task"
        
        steps = {
            "meditate": ["find a quiet space", "focus on your breathing"],
            "save money": ["track your expenses", "set a budget"],
            "learn": ["find good resources", "practice regularly"],
            "cook": ["gather ingredients", "follow the recipe"]
        }
        
        step1, step2 = steps.get(topic, ["start with the basics", "keep practicing"])
        
        return {
            "action": action,
            "topic": topic,
            "step1": step1,
            "step2": step2
        }
    
    def generate_script(self, prompt: str) -> Dict[str, Any]:
        """
        Generate a complete YouTube Shorts script using templates.
        
        Args:
            prompt: The user's prompt/topic
            
        Returns:
            Dictionary with topic, title, description, script, search_keywords, scene_descriptions
        """
        logger.info(f"Generating template-based script for: {prompt}")
        
        # Detect content type and topic category
        content_type = self._detect_content_type(prompt)
        topic_category = self._detect_topic_category(prompt)
        
        # Select a random template for the content type
        templates = self.templates[content_type]
        template = random.choice(templates)
        
        # Generate content based on type
        if content_type == "fact_based":
            content_data = self._generate_fact_content(prompt, template)
        elif content_type == "explanatory":
            content_data = self._generate_explanatory_content(prompt, template)
        elif content_type == "story_based":
            content_data = self._generate_story_content(prompt, template)
        elif content_type == "comparison":
            content_data = self._generate_comparison_content(prompt, template)
        elif content_type == "how_to":
            content_data = self._generate_how_to_content(prompt, template)
        else:
            content_data = self._generate_fact_content(prompt, template)
        
        # Format the script using the template
        try:
            script = template["hook"].format(**content_data) + " " + template["content"].format(**content_data) + " " + template["engagement"].format(**content_data)
        except KeyError as e:
            logger.warning(f"Template formatting error: {e}, using fallback")
            script = f"Let's explore {prompt}! This is more interesting than you might think. What would you like to know? Comment below!"
        
        # Generate scene descriptions
        try:
            scene_descriptions = [scene.format(**content_data) for scene in template["scene_descriptions"]]
        except KeyError:
            scene_descriptions = [
                f"Dynamic {prompt} themed opening scene",
                f"Close-up details showcasing {prompt} elements",
                f"Animated graphics highlighting key {prompt} facts",
                f"Fast-paced montage of {prompt} examples",
                f"Vibrant conclusion with engaging visuals"
            ]
        
        # Generate keywords
        base_keywords = prompt.lower().split()[:3] if prompt else ["content", "video", "short"]
        category_keywords = self.topic_keywords.get(topic_category, ["amazing", "interesting", "cool"])
        search_keywords = base_keywords + category_keywords[:2]
        
        # Clean up the prompt for title
        clean_prompt = prompt[:50] if prompt else "Amazing Content"
        
        result = {
            "topic": f"YouTube Short about {clean_prompt}",
            "title": clean_prompt,
            "description": f"A YouTube Short about {clean_prompt}\n\nGenerated using template-based system for reliable content creation.",
            "script": script,
            "search_keywords": search_keywords,
            "scene_descriptions": scene_descriptions
        }
        
        logger.info(f"Generated template-based script with {len(script.split())} words")
        return result


# Global instance
template_generator = TemplateScriptGenerator()


def generate_template_script(prompt: str) -> Dict[str, Any]:
    """
    Generate a script using the template system.
    
    Args:
        prompt: The user's prompt/topic
        
    Returns:
        Dictionary with complete script data
    """
    return template_generator.generate_script(prompt)
