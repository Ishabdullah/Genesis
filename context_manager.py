#!/usr/bin/env python3
"""
Genesis Context Manager
Session memory, long-term memory, and context rehydration
"""

import json
import pickle
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import deque


class ContextManager:
    """Manages session memory, long-term memory, and context persistence"""

    def __init__(
        self,
        data_dir: str = "data/memory",
        session_size: int = 20,
        long_term_size: int = 1000
    ):
        """
        Initialize context manager

        Args:
            data_dir: Directory for memory storage
            session_size: Max items in session memory (RAM)
            long_term_size: Max items in long-term memory (disk)
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # File paths
        self.session_file = self.data_dir / "session_memory.json"
        self.longterm_file = self.data_dir / "longterm_memory.json"
        self.preferences_file = self.data_dir / "user_preferences.json"

        # Session memory (RAM) - fast access
        self.session_memory = deque(maxlen=session_size)

        # Long-term memory (disk) - persistent
        self.long_term_memory = []
        self.long_term_size = long_term_size

        # User preferences
        self.user_preferences = {}

        # Context metadata
        self.session_metadata = {
            "session_id": self._generate_session_id(),
            "start_time": datetime.now().isoformat(),
            "query_count": 0,
            "last_topic": None,
            "tone_preference": None,
            "verbosity_preference": None
        }

        # Load existing data
        self._load_session()
        self._load_long_term()
        self._load_preferences()

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        timestamp = datetime.now().isoformat()
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]

    def _load_json(self, filepath: Path, default):
        """Load JSON file with fallback"""
        try:
            if filepath.exists():
                with open(filepath, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Warning: Could not load {filepath.name}: {e}")
        return default

    def _save_json(self, filepath: Path, data):
        """Save data to JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️ Warning: Could not save {filepath.name}: {e}")

    def _load_session(self):
        """Load previous session memory (context rehydration)"""
        data = self._load_json(self.session_file, {"items": [], "metadata": {}})

        # Load last session's interactions
        items = data.get("items", [])
        if items:
            # Load up to 10 most recent items from last session
            for item in items[-10:]:
                self.session_memory.append(item)

        # Load session metadata
        prev_metadata = data.get("metadata", {})
        if prev_metadata:
            self.session_metadata["last_topic"] = prev_metadata.get("last_topic")
            self.session_metadata["tone_preference"] = prev_metadata.get("tone_preference")
            self.session_metadata["verbosity_preference"] = prev_metadata.get("verbosity_preference")

    def _load_long_term(self):
        """Load long-term memory from disk"""
        self.long_term_memory = self._load_json(self.longterm_file, [])

    def _load_preferences(self):
        """Load user preferences"""
        self.user_preferences = self._load_json(self.preferences_file, {})

    def save_session(self):
        """Save current session to disk"""
        data = {
            "session_id": self.session_metadata["session_id"],
            "saved_at": datetime.now().isoformat(),
            "items": list(self.session_memory),
            "metadata": self.session_metadata
        }
        self._save_json(self.session_file, data)

    def save_long_term(self):
        """Save long-term memory to disk"""
        self._save_json(self.longterm_file, self.long_term_memory)

    def save_preferences(self):
        """Save user preferences to disk"""
        self._save_json(self.preferences_file, self.user_preferences)

    def add_interaction(
        self,
        query: str,
        response: str,
        metadata: Optional[Dict] = None
    ):
        """
        Add interaction to both session and long-term memory

        Args:
            query: User query
            response: Genesis response
            metadata: Optional metadata dict
        """
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_metadata["session_id"],
            "query": query,
            "response": response,
            "metadata": metadata or {}
        }

        # Add to session memory (RAM)
        self.session_memory.append(interaction)

        # Add to long-term memory (disk) if important
        if self._is_important(interaction):
            self.long_term_memory.append(interaction)

            # Trim long-term memory if needed
            if len(self.long_term_memory) > self.long_term_size:
                # Keep most recent
                self.long_term_memory = self.long_term_memory[-self.long_term_size:]

        # Update metadata
        self.session_metadata["query_count"] += 1
        self.session_metadata["last_topic"] = self._extract_topic(query)

        # Auto-save periodically
        if self.session_metadata["query_count"] % 5 == 0:
            self.save_session()
            self.save_long_term()

    def _is_important(self, interaction: Dict) -> bool:
        """
        Determine if interaction should be stored in long-term memory

        Args:
            interaction: Interaction dict

        Returns:
            True if important enough to persist
        """
        metadata = interaction.get("metadata", {})

        # Always store if user gave feedback
        if metadata.get("had_feedback"):
            return True

        # Store if confidence is high
        if metadata.get("confidence_score", 0) > 0.8:
            return True

        # Store if it's a complex query
        query_words = len(interaction["query"].split())
        if query_words > 15:
            return True

        # Store if external sources were used
        if metadata.get("used_websearch") or metadata.get("used_perplexity") or metadata.get("used_claude"):
            return True

        # Store coding queries
        if metadata.get("problem_type") in ["programming", "code_generation"]:
            return True

        return False

    def _extract_topic(self, query: str) -> Optional[str]:
        """Extract topic from query for context tracking"""
        # Simple topic extraction (first 3 significant words)
        words = query.lower().split()
        significant_words = [
            w for w in words
            if len(w) > 3 and w not in ['what', 'when', 'where', 'which', 'how', 'does', 'can']
        ]
        return " ".join(significant_words[:3]) if significant_words else None

    def get_session_context(self, max_items: int = 10) -> List[Dict]:
        """
        Get recent session context

        Args:
            max_items: Max items to return

        Returns:
            List of recent interactions
        """
        return list(self.session_memory)[-max_items:]

    def get_relevant_long_term_context(
        self,
        query: str,
        max_items: int = 5
    ) -> List[Dict]:
        """
        Get relevant context from long-term memory

        Args:
            query: Current query
            max_items: Max items to return

        Returns:
            List of relevant past interactions
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())

        # Score each long-term memory item by relevance
        scored_items = []
        for item in self.long_term_memory[-100:]:  # Check last 100
            item_words = set(item["query"].lower().split())
            relevance = len(query_words & item_words) / max(len(query_words), 1)

            if relevance > 0.2:  # Threshold
                scored_items.append((relevance, item))

        # Sort by relevance and return top items
        scored_items.sort(reverse=True, key=lambda x: x[0])
        return [item for _, item in scored_items[:max_items]]

    def get_full_context(self, query: str, max_session: int = 10, max_longterm: int = 5) -> Dict:
        """
        Get complete context for a query (session + relevant long-term)

        Args:
            query: Current query
            max_session: Max session items
            max_longterm: Max long-term items

        Returns:
            Context dictionary
        """
        return {
            "session_context": self.get_session_context(max_session),
            "longterm_context": self.get_relevant_long_term_context(query, max_longterm),
            "session_metadata": self.session_metadata,
            "user_preferences": self.user_preferences
        }

    def format_context_string(self, context: Dict, include_responses: bool = False) -> str:
        """
        Format context as string for LLM prompt

        Args:
            context: Context dictionary
            include_responses: Whether to include full responses

        Returns:
            Formatted context string
        """
        lines = []

        # Session context
        if context["session_context"]:
            lines.append("Recent conversation:")
            for item in context["session_context"][-5:]:
                lines.append(f"User: {item['query']}")
                if include_responses:
                    response = item['response'][:100] + "..." if len(item['response']) > 100 else item['response']
                    lines.append(f"Genesis: {response}")

        # Relevant long-term context
        if context["longterm_context"]:
            lines.append("\nRelevant past context:")
            for item in context["longterm_context"][:3]:
                lines.append(f"- {item['query']} [{item['timestamp'][:10]}]")

        # User preferences
        if context["user_preferences"]:
            lines.append("\nUser preferences:")
            for key, value in context["user_preferences"].items():
                lines.append(f"- {key}: {value}")

        return "\n".join(lines)

    def set_preference(self, key: str, value: Any):
        """Set user preference"""
        self.user_preferences[key] = value
        self.save_preferences()

    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get user preference with default"""
        return self.user_preferences.get(key, default)

    def clear_session(self):
        """Clear session memory (start fresh)"""
        self.session_memory.clear()
        self.session_metadata = {
            "session_id": self._generate_session_id(),
            "start_time": datetime.now().isoformat(),
            "query_count": 0,
            "last_topic": None,
            "tone_preference": None,
            "verbosity_preference": None
        }
        self.save_session()

    def get_summary(self) -> str:
        """Get context summary"""
        session_size = len(self.session_memory)
        longterm_size = len(self.long_term_memory)

        return f"""
╔══════════════════════════════════════════════════════════════╗
║           🧠 CONTEXT & MEMORY SUMMARY                         ║
╚══════════════════════════════════════════════════════════════╝

📝 SESSION MEMORY (RAM)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Session ID:                  {self.session_metadata['session_id']}
Items in memory:             {session_size}/{self.session_memory.maxlen}
Queries this session:        {self.session_metadata['query_count']}
Last topic:                  {self.session_metadata.get('last_topic', 'N/A')}

💾 LONG-TERM MEMORY (Disk)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total stored:                {longterm_size}/{self.long_term_size}
Oldest entry:                {self.long_term_memory[0]['timestamp'][:10] if self.long_term_memory else 'N/A'}
Newest entry:                {self.long_term_memory[-1]['timestamp'][:10] if self.long_term_memory else 'N/A'}

👤 USER PREFERENCES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total preferences:           {len(self.user_preferences)}
"""


# Global instance
_context_manager_instance = None


def get_context_manager() -> ContextManager:
    """Get or create global ContextManager instance"""
    global _context_manager_instance
    if _context_manager_instance is None:
        _context_manager_instance = ContextManager()
    return _context_manager_instance


if __name__ == "__main__":
    # Test the context manager
    manager = ContextManager()

    # Add some test interactions
    manager.add_interaction(
        "What is Python?",
        "Python is a high-level programming language...",
        {"confidence_score": 0.9}
    )

    manager.add_interaction(
        "How do I use decorators?",
        "Decorators are functions that modify other functions...",
        {"problem_type": "programming"}
    )

    # Get context
    context = manager.get_full_context("Tell me more about Python decorators")

    print(manager.get_summary())
    print("\n" + "="*60)
    print("FORMATTED CONTEXT:")
    print("="*60)
    print(manager.format_context_string(context))
