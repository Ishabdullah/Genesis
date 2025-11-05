#!/usr/bin/env python3
"""
Genesis Memory Manager
Handles conversation history and context persistence
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any

class MemoryManager:
    """Manages conversation memory and context for Genesis"""

    def __init__(self, memory_file: str = "memory.json", max_conversations: int = 20):
        """
        Initialize memory manager

        Args:
            memory_file: Path to JSON file storing memory
            max_conversations: Maximum number of conversation turns to keep
        """
        self.memory_file = memory_file
        self.max_conversations = max_conversations
        self.conversations: List[Dict[str, Any]] = []
        self.context: Dict[str, Any] = {}
        self.load()

    def load(self):
        """Load memory from disk"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.conversations = data.get('conversations', [])
                    self.context = data.get('context', {})
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠ Warning: Could not load memory: {e}")
                self.conversations = []
                self.context = {}
        else:
            self.conversations = []
            self.context = {}

    def save(self):
        """Save memory to disk"""
        try:
            data = {
                'conversations': self.conversations,
                'context': self.context,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"⚠ Warning: Could not save memory: {e}")

    def add_interaction(self, user_input: str, assistant_output: str):
        """
        Add a user-assistant interaction to memory

        Args:
            user_input: User's prompt
            assistant_output: Assistant's response
        """
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'user': user_input,
            'assistant': assistant_output
        }
        self.conversations.append(interaction)

        # Trim to max conversations (keep most recent)
        if len(self.conversations) > self.max_conversations:
            self.conversations = self.conversations[-self.max_conversations:]

        self.save()

    def get_context_string(self) -> str:
        """
        Build a context string from recent conversations

        Returns:
            Formatted string of conversation history
        """
        if not self.conversations:
            return ""

        context_parts = []
        for conv in self.conversations[-10:]:  # Last 10 interactions
            context_parts.append(f"User: {conv['user']}")
            context_parts.append(f"Assistant: {conv['assistant']}")

        return "\n".join(context_parts)

    def reset(self):
        """Clear all memory"""
        self.conversations = []
        self.context = {}
        self.save()
        print("✓ Memory cleared")

    def update_context(self, key: str, value: Any):
        """
        Update persistent context variables

        Args:
            key: Context key
            value: Context value
        """
        self.context[key] = value
        self.save()

    def get_context(self, key: str, default: Any = None) -> Any:
        """
        Retrieve a context variable

        Args:
            key: Context key
            default: Default value if key not found

        Returns:
            Context value or default
        """
        return self.context.get(key, default)

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            'total_conversations': len(self.conversations),
            'context_keys': list(self.context.keys()),
            'memory_size_kb': os.path.getsize(self.memory_file) / 1024 if os.path.exists(self.memory_file) else 0
        }
