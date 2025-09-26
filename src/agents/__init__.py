"""Agent implementations for the AI Co-Scientist system."""

from .supervisor import SupervisorAgent
from .generation import GenerationAgent
from .reflection import ReflectionAgent

__all__ = [
    'SupervisorAgent',
    'GenerationAgent',
    'ReflectionAgent',
]