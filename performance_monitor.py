#!/usr/bin/env python3
"""
Genesis Performance Monitoring Module
Tracks response times, correctness, fallbacks, and system health
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from threading import Lock
import statistics

class PerformanceMonitor:
    """Autonomous performance tracking and monitoring system"""

    def __init__(self, metrics_file: str = "data/genesis_metrics.json"):
        """
        Initialize performance monitor

        Args:
            metrics_file: Path to metrics storage file
        """
        self.metrics_file = Path(metrics_file)
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)

        # Thread-safe lock for concurrent access
        self._lock = Lock()

        # Current session tracking
        self._current_query_start: Optional[float] = None
        self._last_query_id: Optional[str] = None
        self._last_response: Optional[str] = None

        # Load existing metrics
        self.metrics = self._load_metrics()

    def _load_metrics(self) -> Dict[str, Any]:
        """
        Load metrics from file

        Returns:
            Metrics dictionary
        """
        try:
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠ Could not load metrics: {e}")

        # Initialize empty metrics
        return {
            "queries": [],
            "fallbacks": [],
            "errors": [],
            "feedback": {
                "correct": 0,
                "incorrect": 0
            },
            "statistics": {
                "total_queries": 0,
                "total_fallbacks": 0,
                "total_errors": 0,
                "avg_response_time_ms": 0.0
            },
            "session_start": datetime.now().isoformat()
        }

    def _save_metrics(self):
        """Save metrics to file (async-safe)"""
        try:
            with self._lock:
                with open(self.metrics_file, 'w') as f:
                    json.dump(self.metrics, f, indent=2)
        except Exception as e:
            print(f"⚠ Could not save metrics: {e}")

    def start_query(self, user_input: str) -> str:
        """
        Mark the start of a query

        Args:
            user_input: User's input text

        Returns:
            Query ID for tracking
        """
        self._current_query_start = time.time()
        self._last_query_id = f"q_{int(time.time() * 1000)}"

        return self._last_query_id

    def end_query(
        self,
        query_id: str,
        user_input: str,
        response: str,
        was_direct_command: bool = False,
        had_fallback: bool = False,
        confidence_score: Optional[float] = None,
        error: Optional[str] = None,
        source: str = "local"
    ):
        """
        Record query completion and metrics

        Args:
            query_id: Query identifier
            user_input: User's input
            response: Genesis's response
            was_direct_command: Whether this was a direct command (instant)
            had_fallback: Whether Claude fallback was used
            confidence_score: Confidence score (0.0 - 1.0) if available
            error: Error message if any
            source: Response source ("local", "perplexity", "claude")
        """
        if self._current_query_start is None:
            return

        # Calculate response time
        response_time_ms = (time.time() - self._current_query_start) * 1000

        # Store last response for feedback
        self._last_response = response

        # Create query record
        query_record = {
            "id": query_id,
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input[:200],  # Truncate long inputs
            "response_time_ms": round(response_time_ms, 2),
            "was_direct_command": was_direct_command,
            "had_fallback": had_fallback,
            "confidence_score": confidence_score,
            "error": error,
            "source": source,  # Track response source
            "feedback": None  # Will be updated if user provides feedback
        }

        with self._lock:
            # Add to queries list
            self.metrics["queries"].append(query_record)

            # Update statistics
            self.metrics["statistics"]["total_queries"] += 1

            if error:
                self.metrics["statistics"]["total_errors"] += 1

            # Update average response time
            all_times = [q["response_time_ms"] for q in self.metrics["queries"]]
            self.metrics["statistics"]["avg_response_time_ms"] = round(
                statistics.mean(all_times), 2
            )

        # Save asynchronously (non-blocking)
        self._save_metrics()

        # Reset current query
        self._current_query_start = None

    def record_fallback(self, user_input: str, local_confidence: float, success: bool):
        """
        Record Claude fallback event

        Args:
            user_input: User's input that triggered fallback
            local_confidence: Confidence score that triggered fallback
            success: Whether Claude was successfully reached
        """
        fallback_record = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input[:200],
            "local_confidence": local_confidence,
            "success": success
        }

        with self._lock:
            self.metrics["fallbacks"].append(fallback_record)
            self.metrics["statistics"]["total_fallbacks"] += 1

            # Update last query with fallback info
            if self.metrics["queries"]:
                self.metrics["queries"][-1]["had_fallback"] = True
                self.metrics["queries"][-1]["fallback_success"] = success

        self._save_metrics()

    def record_error(self, error_type: str, error_message: str, context: Optional[str] = None):
        """
        Record system error

        Args:
            error_type: Type of error (timeout, exception, etc.)
            error_message: Error message
            context: Additional context
        """
        error_record = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": error_message,
            "context": context
        }

        with self._lock:
            self.metrics["errors"].append(error_record)
            self.metrics["statistics"]["total_errors"] += 1

            # Keep only last 100 errors to prevent file bloat
            if len(self.metrics["errors"]) > 100:
                self.metrics["errors"] = self.metrics["errors"][-100:]

        self._save_metrics()

    def record_feedback(self, is_correct: bool):
        """
        Record user feedback for last response

        Args:
            is_correct: True if user marked response as correct
        """
        feedback_type = "correct" if is_correct else "incorrect"

        with self._lock:
            # Update feedback counts
            self.metrics["feedback"][feedback_type] += 1

            # Update last query with feedback
            if self.metrics["queries"]:
                self.metrics["queries"][-1]["feedback"] = feedback_type

        self._save_metrics()

        return feedback_type

    def get_performance_summary(self) -> str:
        """
        Generate performance summary report

        Returns:
            Formatted summary string
        """
        with self._lock:
            stats = self.metrics["statistics"]
            feedback = self.metrics["feedback"]
            total_queries = stats["total_queries"]

            # Calculate percentages
            total_feedback = feedback["correct"] + feedback["incorrect"]
            correct_pct = (feedback["correct"] / total_feedback * 100) if total_feedback > 0 else 0
            incorrect_pct = (feedback["incorrect"] / total_feedback * 100) if total_feedback > 0 else 0

            # Fallback rate
            fallback_rate = (stats["total_fallbacks"] / total_queries * 100) if total_queries > 0 else 0

            # Recent response times
            recent_queries = self.metrics["queries"][-10:]
            recent_times = [q["response_time_ms"] for q in recent_queries]

            # Calculate response time stats
            if recent_times:
                min_time = min(recent_times)
                max_time = max(recent_times)
                avg_recent = statistics.mean(recent_times)
            else:
                min_time = max_time = avg_recent = 0.0

            # Direct command vs LLM breakdown
            direct_commands = sum(1 for q in self.metrics["queries"] if q["was_direct_command"])
            llm_queries = total_queries - direct_commands

            # Source breakdown
            source_counts = {"local": 0, "perplexity": 0, "claude": 0}
            for q in self.metrics["queries"]:
                source = q.get("source", "local")
                if source in source_counts:
                    source_counts[source] += 1

            # Recent errors
            recent_errors = self.metrics["errors"][-5:]

            # Build report
            report = f"""
╔══════════════════════════════════════════════════════════════╗
║           🧬 GENESIS PERFORMANCE METRICS                      ║
╚══════════════════════════════════════════════════════════════╝

📊 OVERALL STATISTICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Queries Processed:        {total_queries}
  • Direct Commands (instant):  {direct_commands}
  • LLM Queries (20-30s):        {llm_queries}

🌐 RESPONSE SOURCES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  🧬 Local (Genesis):           {source_counts['local']}
  🔍 Perplexity Research:       {source_counts['perplexity']}
  ☁️  Claude Fallback:           {source_counts['claude']}

⚡ RESPONSE SPEED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Average Response Time:          {stats['avg_response_time_ms']:.2f} ms
Recent (Last 10):
  • Fastest:                    {min_time:.2f} ms
  • Slowest:                    {max_time:.2f} ms
  • Average:                    {avg_recent:.2f} ms

✅ USER FEEDBACK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Feedback Given:           {total_feedback}
  ✓ Correct (#correct):         {feedback['correct']} ({correct_pct:.1f}%)
  ✗ Incorrect (#incorrect):     {feedback['incorrect']} ({incorrect_pct:.1f}%)

🤖 CLAUDE FALLBACK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Fallbacks:                {stats['total_fallbacks']}
Fallback Rate:                  {fallback_rate:.1f}%
Recent Fallbacks:               {len([f for f in self.metrics['fallbacks'][-10:]])}
"""

            # Add fallback success rate if we have fallbacks
            if self.metrics["fallbacks"]:
                successful = sum(1 for f in self.metrics["fallbacks"] if f["success"])
                success_rate = (successful / len(self.metrics["fallbacks"]) * 100)
                report += f"Claude Reachability:            {success_rate:.1f}%\n"

            # Add error section
            report += f"""
⚠️  ERRORS & ISSUES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Errors:                   {stats['total_errors']}
Recent Errors (Last 5):
"""

            if recent_errors:
                for i, error in enumerate(recent_errors, 1):
                    timestamp = error['timestamp'].split('T')[1][:8]
                    report += f"  {i}. [{timestamp}] {error['type']}: {error['message'][:50]}\n"
            else:
                report += "  No recent errors ✓\n"

            # Add performance rating
            report += "\n"
            rating = self._calculate_performance_rating(
                correct_pct, stats['avg_response_time_ms'], fallback_rate
            )
            report += rating

            report += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            report += "Commands: #correct | #incorrect | #performance | #reset_metrics\n"

            return report

    def _calculate_performance_rating(
        self,
        correct_pct: float,
        avg_response_ms: float,
        fallback_rate: float
    ) -> str:
        """
        Calculate overall performance rating

        Args:
            correct_pct: Percentage of correct responses
            avg_response_ms: Average response time
            fallback_rate: Percentage of fallbacks

        Returns:
            Performance rating string
        """
        # Score components (0-100 each)
        correctness_score = correct_pct
        speed_score = min(100, max(0, 100 - (avg_response_ms / 500 * 100)))
        reliability_score = 100 - (fallback_rate * 2)  # Fallbacks aren't bad, just tracking

        # Weighted average
        overall_score = (correctness_score * 0.5) + (speed_score * 0.3) + (reliability_score * 0.2)

        # Determine rating
        if overall_score >= 90:
            rating = "🌟 EXCELLENT"
            color = "green"
        elif overall_score >= 75:
            rating = "✅ GOOD"
            color = "green"
        elif overall_score >= 60:
            rating = "⚠️  FAIR"
            color = "yellow"
        else:
            rating = "❌ NEEDS IMPROVEMENT"
            color = "red"

        return f"""
🎯 PERFORMANCE RATING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Score:                  {overall_score:.1f}/100
Rating:                         {rating}

Component Scores:
  • Correctness:                {correctness_score:.1f}/100
  • Speed:                      {speed_score:.1f}/100
  • Reliability:                {reliability_score:.1f}/100
"""

    def reset_metrics(self):
        """Reset all metrics to initial state"""
        with self._lock:
            self.metrics = {
                "queries": [],
                "fallbacks": [],
                "errors": [],
                "feedback": {
                    "correct": 0,
                    "incorrect": 0
                },
                "statistics": {
                    "total_queries": 0,
                    "total_fallbacks": 0,
                    "total_errors": 0,
                    "avg_response_time_ms": 0.0
                },
                "session_start": datetime.now().isoformat()
            }

        self._save_metrics()

    def get_recent_queries(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent queries

        Args:
            count: Number of recent queries to return

        Returns:
            List of query records
        """
        with self._lock:
            return self.metrics["queries"][-count:]

    def export_metrics(self, output_file: Optional[str] = None) -> str:
        """
        Export metrics to file

        Args:
            output_file: Output file path (defaults to timestamped file)

        Returns:
            Path to exported file
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"data/genesis_metrics_export_{timestamp}.json"

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with self._lock:
            with open(output_path, 'w') as f:
                json.dump(self.metrics, f, indent=2)

        return str(output_path)
