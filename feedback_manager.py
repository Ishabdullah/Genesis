#!/usr/bin/env python3
"""
Genesis Feedback Manager
Enhanced feedback system with notes, learning, and adaptive weighting
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class FeedbackManager:
    """Manages user feedback, learning events, and adaptive confidence weighting"""

    def __init__(self, data_dir: str = "data/memory"):
        """
        Initialize feedback manager

        Args:
            data_dir: Directory for feedback data storage
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Feedback storage
        self.feedback_file = self.data_dir / "feedback_log.json"
        self.learning_file = self.data_dir / "learning_events.json"
        self.weights_file = self.data_dir / "source_weights.json"

        # Load existing data
        self.feedback_history = self._load_json(self.feedback_file, [])
        self.learning_events = self._load_json(self.learning_file, [])
        self.source_weights = self._load_json(self.weights_file, self._default_weights())

        # Statistics
        self.session_stats = {
            "correct": 0,
            "incorrect": 0,
            "refinements": 0,
            "learning_events": 0
        }

    def _default_weights(self) -> Dict:
        """Default source confidence weights"""
        return {
            "websearch": {
                "base_confidence": 0.70,
                "bonus_time_sensitive": 0.15,
                "success_count": 0,
                "total_count": 0
            },
            "perplexity": {
                "base_confidence": 0.75,
                "bonus_synthesis": 0.10,
                "success_count": 0,
                "total_count": 0
            },
            "claude": {
                "base_confidence": 0.85,
                "bonus_coding": 0.20,
                "success_count": 0,
                "total_count": 0
            },
            "local": {
                "base_confidence": 0.60,
                "bonus_math": 0.30,
                "success_count": 0,
                "total_count": 0
            }
        }

    def _load_json(self, filepath: Path, default):
        """Load JSON file with fallback to default"""
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

    def add_feedback(
        self,
        query: str,
        response: str,
        is_correct: bool,
        note: Optional[str] = None,
        source: str = "local",
        confidence: float = 0.0,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Record user feedback with optional note

        Args:
            query: Original user query
            response: Genesis response
            is_correct: Whether response was correct
            note: Optional feedback note
            source: Source that generated response
            confidence: Response confidence score
            metadata: Optional additional metadata

        Returns:
            Feedback event dictionary
        """
        feedback_event = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response": response[:200] + "..." if len(response) > 200 else response,
            "is_correct": is_correct,
            "note": note,
            "source": source,
            "confidence": confidence,
            "metadata": metadata or {},
            "feedback_type": "refinement" if is_correct and note else "correction"
        }

        # Update statistics
        if is_correct:
            if note:
                self.session_stats["refinements"] += 1
            else:
                self.session_stats["correct"] += 1
        else:
            self.session_stats["incorrect"] += 1

        # Store feedback
        self.feedback_history.append(feedback_event)
        self._save_json(self.feedback_file, self.feedback_history)

        # Update source weights
        self._update_source_weights(source, is_correct, confidence)

        # Create learning event if needed
        if not is_correct or (is_correct and note):
            self._create_learning_event(feedback_event)

        return feedback_event

    def _update_source_weights(self, source: str, is_correct: bool, confidence: float):
        """
        Update adaptive confidence weights based on feedback

        Args:
            source: Source that was used
            is_correct: Whether response was correct
            confidence: Original confidence score
        """
        if source not in self.source_weights:
            return

        weights = self.source_weights[source]
        weights["total_count"] += 1

        if is_correct:
            weights["success_count"] += 1

        # Calculate success rate
        success_rate = weights["success_count"] / weights["total_count"]

        # Adjust base confidence (learning rate: 0.05)
        learning_rate = 0.05
        target_confidence = 0.9 if is_correct else 0.5
        adjustment = learning_rate * (target_confidence - weights["base_confidence"])

        # Clamp to reasonable range
        weights["base_confidence"] = max(0.4, min(0.95,
            weights["base_confidence"] + adjustment
        ))

        # Save updated weights
        self._save_json(self.weights_file, self.source_weights)

    def _create_learning_event(self, feedback_event: Dict):
        """
        Create a learning event for future training

        Args:
            feedback_event: Feedback event dictionary
        """
        learning_event = {
            "timestamp": feedback_event["timestamp"],
            "query": feedback_event["query"],
            "response": feedback_event["response"],
            "is_correct": feedback_event["is_correct"],
            "note": feedback_event["note"],
            "source": feedback_event["source"],
            "event_type": "positive_refinement" if feedback_event["is_correct"] else "error_correction",
            "priority": "high" if not feedback_event["is_correct"] else "medium"
        }

        self.learning_events.append(learning_event)
        self.session_stats["learning_events"] += 1

        # Save learning events
        self._save_json(self.learning_file, self.learning_events)

    def get_source_confidence(
        self,
        source: str,
        query_type: Optional[str] = None,
        is_time_sensitive: bool = False,
        is_coding: bool = False
    ) -> float:
        """
        Get adaptive confidence score for a source

        Args:
            source: Source name
            query_type: Type of query (optional)
            is_time_sensitive: Whether query is time-sensitive
            is_coding: Whether query involves coding

        Returns:
            Adjusted confidence score
        """
        if source not in self.source_weights:
            return 0.5

        weights = self.source_weights[source]
        confidence = weights["base_confidence"]

        # Apply bonuses
        if source == "websearch" and is_time_sensitive:
            confidence += weights.get("bonus_time_sensitive", 0)
        elif source == "perplexity" and query_type == "synthesis":
            confidence += weights.get("bonus_synthesis", 0)
        elif source == "claude" and is_coding:
            confidence += weights.get("bonus_coding", 0)
        elif source == "local" and query_type == "math":
            confidence += weights.get("bonus_math", 0)

        return min(0.99, confidence)

    def get_best_source_for_query(
        self,
        query_type: str,
        is_time_sensitive: bool = False,
        is_coding: bool = False
    ) -> Tuple[str, float]:
        """
        Determine best source for a query based on learned weights

        Args:
            query_type: Type of query
            is_time_sensitive: Whether query is time-sensitive
            is_coding: Whether query involves coding

        Returns:
            (best_source, expected_confidence) tuple
        """
        scores = {}

        for source in self.source_weights.keys():
            scores[source] = self.get_source_confidence(
                source, query_type, is_time_sensitive, is_coding
            )

        # Special prioritization
        if is_time_sensitive:
            scores["websearch"] *= 1.3
        if is_coding:
            scores["claude"] *= 1.4
        if query_type == "math":
            scores["local"] *= 1.2

        best_source = max(scores.items(), key=lambda x: x[1])
        return best_source

    def get_feedback_summary(self) -> str:
        """Get formatted feedback summary"""
        total = self.session_stats["correct"] + self.session_stats["incorrect"]

        if total == 0:
            success_rate = 0.0
        else:
            success_rate = (self.session_stats["correct"] / total) * 100

        summary = f"""
╔══════════════════════════════════════════════════════════════╗
║           📊 FEEDBACK & LEARNING SUMMARY                      ║
╚══════════════════════════════════════════════════════════════╝

📈 SESSION STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Feedback:              {total}
  ✓ Correct:                 {self.session_stats["correct"]}
  ✗ Incorrect:               {self.session_stats["incorrect"]}
  📝 Refinements:            {self.session_stats["refinements"]}
Success Rate:                {success_rate:.1f}%

🎓 LEARNING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Learning Events:             {self.session_stats["learning_events"]}
Total Stored:                {len(self.learning_events)}

🎯 SOURCE CONFIDENCE (Adaptive)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

        for source, weights in self.source_weights.items():
            if weights["total_count"] > 0:
                success_rate = (weights["success_count"] / weights["total_count"]) * 100
                summary += f"\n  {source.capitalize():12} {weights['base_confidence']:.2f} ({weights['success_count']}/{weights['total_count']} = {success_rate:.0f}%)"

        return summary

    def export_learning_data(self, filepath: Optional[str] = None) -> str:
        """
        Export learning events for training

        Args:
            filepath: Optional custom export path

        Returns:
            Path to exported file
        """
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = self.data_dir / f"learning_export_{timestamp}.json"

        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_events": len(self.learning_events),
            "source_weights": self.source_weights,
            "learning_events": self.learning_events
        }

        self._save_json(Path(filepath), export_data)
        return str(filepath)


# Global instance
_feedback_manager_instance = None


def get_feedback_manager() -> FeedbackManager:
    """Get or create global FeedbackManager instance"""
    global _feedback_manager_instance
    if _feedback_manager_instance is None:
        _feedback_manager_instance = FeedbackManager()
    return _feedback_manager_instance


if __name__ == "__main__":
    # Test the feedback manager
    manager = FeedbackManager()

    # Test feedback
    manager.add_feedback(
        query="What is 2+2?",
        response="4",
        is_correct=True,
        note="Perfect, concise answer",
        source="local",
        confidence=0.99
    )

    # Test incorrect feedback
    manager.add_feedback(
        query="Who is president?",
        response="Old data",
        is_correct=False,
        note="Used outdated information",
        source="local",
        confidence=0.85
    )

    print(manager.get_feedback_summary())

    # Test source confidence
    best_source, conf = manager.get_best_source_for_query(
        "general", is_time_sensitive=True
    )
    print(f"\nBest source for time-sensitive query: {best_source} ({conf:.2f})")
