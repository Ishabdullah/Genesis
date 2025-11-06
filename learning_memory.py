#!/usr/bin/env python3
"""
Genesis Learning & Memory System
Persistent memory with auto-pruning and continuous learning
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from threading import Lock
import statistics

class LearningMemory:
    """Persistent memory system with learning capabilities and auto-pruning"""

    def __init__(
        self,
        memory_dir: str = "data/memory",
        max_conversations: int = 1000,
        max_age_days: int = 90,
        prune_threshold: float = 0.8
    ):
        """
        Initialize learning memory system

        Args:
            memory_dir: Directory for memory storage
            max_conversations: Maximum conversations to retain
            max_age_days: Maximum age of conversations (days)
            prune_threshold: Trigger pruning when storage reaches this % of max
        """
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # Configuration
        self.max_conversations = max_conversations
        self.max_age_days = max_age_days
        self.prune_threshold = prune_threshold

        # Memory files
        self.conversation_memory_file = self.memory_dir / "conversation_memory.json"
        self.learning_log_file = self.memory_dir / "learning_log.json"
        self.performance_history_file = self.memory_dir / "performance_history.json"
        self.user_preferences_file = self.memory_dir / "user_preferences.json"

        # Thread-safe lock
        self._lock = Lock()

        # Load existing memory
        self.conversation_memory = self._load_json(self.conversation_memory_file, {"conversations": []})
        self.learning_log = self._load_json(self.learning_log_file, {"entries": []})
        self.performance_history = self._load_json(self.performance_history_file, {"history": []})
        self.user_preferences = self._load_json(self.user_preferences_file, {
            "style": "default",
            "verbosity": "normal",
            "topics": {},
            "feedback_patterns": {}
        })

        # Auto-prune if needed
        self._auto_prune()

    def _load_json(self, filepath: Path, default: Dict) -> Dict:
        """Load JSON file or return default"""
        try:
            if filepath.exists():
                with open(filepath, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠ Could not load {filepath.name}: {e}")
        return default

    def _save_json(self, filepath: Path, data: Dict):
        """Save data to JSON file"""
        try:
            with self._lock:
                with open(filepath, 'w') as f:
                    json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠ Could not save {filepath.name}: {e}")

    def add_conversation(
        self,
        user_input: str,
        assistant_response: str,
        metadata: Optional[Dict] = None
    ):
        """
        Store conversation exchange with metadata

        Args:
            user_input: User's input
            assistant_response: Genesis's response
            metadata: Additional metadata (response_time, confidence, etc.)
        """
        conversation = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input[:500],  # Truncate long inputs
            "assistant_response": assistant_response[:1000],  # Truncate long responses
            "metadata": metadata or {}
        }

        with self._lock:
            self.conversation_memory["conversations"].append(conversation)

            # Check if pruning needed
            if len(self.conversation_memory["conversations"]) >= self.max_conversations * self.prune_threshold:
                self._prune_conversations()

        self._save_json(self.conversation_memory_file, self.conversation_memory)

    def add_learning_entry(
        self,
        event_type: str,
        description: str,
        feedback: Optional[str] = None,
        improvement: Optional[str] = None
    ):
        """
        Log learning event

        Args:
            event_type: Type of learning (feedback, correction, adaptation)
            description: Description of what was learned
            feedback: User feedback if applicable
            improvement: How Genesis improved
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "description": description,
            "feedback": feedback,
            "improvement": improvement
        }

        with self._lock:
            self.learning_log["entries"].append(entry)

            # Keep last 500 learning entries
            if len(self.learning_log["entries"]) > 500:
                self.learning_log["entries"] = self.learning_log["entries"][-500:]

        self._save_json(self.learning_log_file, self.learning_log)

    def add_performance_record(
        self,
        response_time_ms: float,
        accuracy: Optional[bool] = None,
        claude_fallback: bool = False,
        error: Optional[str] = None
    ):
        """
        Record performance metrics

        Args:
            response_time_ms: Response time in milliseconds
            accuracy: Whether response was correct (if known)
            claude_fallback: Whether Claude was used
            error: Error message if any
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "response_time_ms": response_time_ms,
            "accuracy": accuracy,
            "claude_fallback": claude_fallback,
            "error": error
        }

        with self._lock:
            self.performance_history["history"].append(record)

            # Keep last 1000 performance records
            if len(self.performance_history["history"]) > 1000:
                self.performance_history["history"] = self.performance_history["history"][-1000:]

        self._save_json(self.performance_history_file, self.performance_history)

    def update_user_preference(self, key: str, value: Any):
        """
        Update user preference

        Args:
            key: Preference key
            value: Preference value
        """
        with self._lock:
            self.user_preferences[key] = value

        self._save_json(self.user_preferences_file, self.user_preferences)

    def get_relevant_context(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Retrieve relevant past conversations

        Args:
            query: Current query
            max_results: Maximum results to return

        Returns:
            List of relevant conversation entries
        """
        # Simple keyword matching (can be enhanced with embeddings)
        query_lower = query.lower()
        keywords = set(query_lower.split())

        scored_conversations = []
        for conv in self.conversation_memory["conversations"]:
            conv_text = (conv["user_input"] + " " + conv["assistant_response"]).lower()
            score = sum(1 for kw in keywords if kw in conv_text)
            if score > 0:
                scored_conversations.append((score, conv))

        # Sort by relevance score
        scored_conversations.sort(reverse=True, key=lambda x: x[0])

        return [conv for _, conv in scored_conversations[:max_results]]

    def get_memory_summary(self) -> str:
        """
        Generate memory system summary

        Returns:
            Formatted summary string
        """
        with self._lock:
            conv_count = len(self.conversation_memory["conversations"])
            learning_count = len(self.learning_log["entries"])
            perf_count = len(self.performance_history["history"])

            # Calculate statistics
            if perf_count > 0:
                recent_perf = self.performance_history["history"][-100:]
                avg_response = statistics.mean([p["response_time_ms"] for p in recent_perf])
                accurate_count = sum(1 for p in recent_perf if p.get("accuracy") is True)
                accuracy_pct = (accurate_count / len([p for p in recent_perf if p.get("accuracy") is not None]) * 100) if any(p.get("accuracy") is not None for p in recent_perf) else 0
            else:
                avg_response = 0
                accuracy_pct = 0

            # Memory usage
            total_size = sum(f.stat().st_size for f in self.memory_dir.glob("*.json") if f.exists())
            size_mb = total_size / (1024 * 1024)

            # Oldest conversation
            if conv_count > 0:
                oldest = datetime.fromisoformat(self.conversation_memory["conversations"][0]["timestamp"])
                age_days = (datetime.now() - oldest).days
            else:
                age_days = 0

        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║        🧠 GENESIS MEMORY & LEARNING SYSTEM                    ║
╚══════════════════════════════════════════════════════════════╝

📚 PERSISTENT MEMORY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Conversations Stored:           {conv_count} / {self.max_conversations}
Learning Entries:               {learning_count}
Performance Records:            {perf_count}
Memory Age:                     {age_days} days
Storage Size:                   {size_mb:.2f} MB

📈 PERFORMANCE HISTORY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Average Response Time:          {avg_response:.2f} ms
Learned Accuracy:               {accuracy_pct:.1f}%
Records Tracked:                {perf_count}

🎓 LEARNING LOG
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Learning Entries:         {learning_count}
Recent Improvements:            {len([e for e in self.learning_log["entries"][-50:] if e.get("improvement")])}

⚙️ AUTO-PRUNING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Max Conversations:              {self.max_conversations}
Max Age:                        {self.max_age_days} days
Prune Threshold:                {self.prune_threshold * 100:.0f}%
Next Prune At:                  {int(self.max_conversations * self.prune_threshold)} conversations

💾 STORAGE LOCATIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Conversations:                  {self.conversation_memory_file}
Learning Log:                   {self.learning_log_file}
Performance:                    {self.performance_history_file}
Preferences:                    {self.user_preferences_file}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Commands: #memory | #prune_memory | #export_memory
"""
        return summary

    def _prune_conversations(self):
        """
        Automatically prune old/irrelevant conversations

        Pruning Strategy:
        1. Remove conversations older than max_age_days
        2. Remove low-quality conversations (errors, very short responses)
        3. Keep most recent conversations
        4. Keep conversations with high engagement (long responses, feedback)
        """
        print(f"\n🧹 Auto-pruning memory...")

        conversations = self.conversation_memory["conversations"]
        cutoff_date = datetime.now() - timedelta(days=self.max_age_days)

        # Score each conversation
        scored = []
        for conv in conversations:
            timestamp = datetime.fromisoformat(conv["timestamp"])
            score = 0

            # Age factor (newer is better)
            age_days = (datetime.now() - timestamp).days
            if age_days < self.max_age_days:
                score += (self.max_age_days - age_days) / self.max_age_days * 10

            # Length factor (longer conversations have more context)
            response_len = len(conv.get("assistant_response", ""))
            if response_len > 100:
                score += min(response_len / 100, 5)

            # Metadata factors
            metadata = conv.get("metadata", {})
            if metadata.get("feedback") == "correct":
                score += 5
            if metadata.get("had_fallback"):
                score += 3  # Fallback conversations are valuable
            if metadata.get("error"):
                score -= 2  # Errors are less valuable

            scored.append((score, conv))

        # Sort by score and keep top conversations
        scored.sort(reverse=True, key=lambda x: x[0])
        target_count = int(self.max_conversations * 0.7)  # Keep 70% after pruning
        pruned_conversations = [conv for _, conv in scored[:target_count]]

        # Update memory
        with self._lock:
            old_count = len(self.conversation_memory["conversations"])
            self.conversation_memory["conversations"] = pruned_conversations
            new_count = len(pruned_conversations)

        print(f"✓ Pruned {old_count - new_count} conversations ({old_count} → {new_count})")

        # Log pruning event
        self.add_learning_entry(
            event_type="memory_pruning",
            description=f"Pruned {old_count - new_count} conversations",
            improvement=f"Optimized memory from {old_count} to {new_count} conversations"
        )

    def _auto_prune(self):
        """Check and trigger auto-pruning if needed"""
        conv_count = len(self.conversation_memory["conversations"])
        if conv_count >= self.max_conversations * self.prune_threshold:
            self._prune_conversations()
            self._save_json(self.conversation_memory_file, self.conversation_memory)

    def manual_prune(self):
        """Manually trigger memory pruning"""
        self._prune_conversations()
        self._save_json(self.conversation_memory_file, self.conversation_memory)

    def export_memory(self, output_dir: Optional[str] = None) -> str:
        """
        Export all memory to timestamped backup

        Args:
            output_dir: Output directory (defaults to memory_dir/exports)

        Returns:
            Path to exported backup
        """
        if output_dir is None:
            output_dir = self.memory_dir / "exports"

        export_path = Path(output_dir)
        export_path.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = export_path / f"genesis_memory_backup_{timestamp}.json"

        backup_data = {
            "export_timestamp": datetime.now().isoformat(),
            "conversation_memory": self.conversation_memory,
            "learning_log": self.learning_log,
            "performance_history": self.performance_history,
            "user_preferences": self.user_preferences
        }

        with open(export_file, 'w') as f:
            json.dump(backup_data, f, indent=2)

        return str(export_file)

    def get_recent_learning(self, count: int = 10) -> List[Dict]:
        """
        Get recent learning entries

        Args:
            count: Number of entries to return

        Returns:
            List of recent learning entries
        """
        return self.learning_log["entries"][-count:]

    def _save_conversation_memory(self):
        """Save conversation memory to file"""
        with self._lock:
            self._save_json(self.conversation_memory_file, self.conversation_memory)

    def _save_learning_log(self):
        """Save learning log to file"""
        with self._lock:
            self._save_json(self.learning_log_file, self.learning_log)

    def add_feedback_note(self, query: str, note: str, is_correct: bool):
        """
        Add feedback note to learning memory

        Args:
            query: The query that was evaluated
            note: Feedback note from user
            is_correct: Whether feedback was positive

        """
        with self._lock:
            # Find matching conversation in memory
            for conv in reversed(self.conversation_memory["conversations"]):
                if conv["user_input"] == query:
                    # Add feedback note to conversation
                    if "metadata" not in conv:
                        conv["metadata"] = {}
                    conv["metadata"]["feedback_note"] = note
                    conv["metadata"]["feedback_correct"] = is_correct
                    conv["metadata"]["feedback_timestamp"] = datetime.now().isoformat()
                    break

            # Add to learning log
            self.learning_log["entries"].append({
                "timestamp": datetime.now().isoformat(),
                "type": "feedback_note",
                "query": query[:200],
                "note": note,
                "is_correct": is_correct
            })

            # Save both files
            self._save_conversation_memory()
            self._save_learning_log()
