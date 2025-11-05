#!/usr/bin/env python3
"""
Genesis Claude Fallback Orchestrator
Handles escalation to Claude Code when local model is uncertain
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

class ClaudeFallback:
    """Manages fallback to Claude Code for uncertain responses"""

    def __init__(
        self,
        enable_flag_file: str = "/data/data/com.termux/files/home/.genesis_assist",
        log_dir: str = "logs",
        data_dir: str = "data"
    ):
        """
        Initialize Claude fallback system

        Args:
            enable_flag_file: Path to file that controls fallback (exists = enabled)
            log_dir: Directory for fallback logs
            data_dir: Directory for learning data
        """
        self.enable_flag_file = enable_flag_file
        self.log_dir = Path(log_dir)
        self.data_dir = Path(data_dir)

        # Create directories
        self.log_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)

        # Log files
        self.fallback_log = self.log_dir / "fallback_history.log"
        self.retrain_data = self.data_dir / "retrain_set.json"

        # Initialize retrain dataset if doesn't exist
        if not self.retrain_data.exists():
            with open(self.retrain_data, 'w') as f:
                json.dump({"examples": []}, f)

    def is_enabled(self) -> bool:
        """
        Check if Claude fallback is enabled

        Returns:
            True if fallback is enabled
        """
        return os.path.exists(self.enable_flag_file)

    def enable(self):
        """Enable Claude fallback"""
        Path(self.enable_flag_file).touch()
        print("✓ Claude fallback enabled")

    def disable(self):
        """Disable Claude fallback"""
        if os.path.exists(self.enable_flag_file):
            os.remove(self.enable_flag_file)
        print("✓ Claude fallback disabled")

    def request_claude_assist(
        self,
        user_prompt: str,
        local_response: str,
        uncertainty_analysis: Dict[str, Any]
    ) -> Optional[str]:
        """
        Request assistance from Claude Code

        Args:
            user_prompt: Original user prompt
            local_response: Local model's uncertain response
            uncertainty_analysis: Uncertainty detection results

        Returns:
            Claude's response or None if failed
        """
        if not self.is_enabled():
            return None

        try:
            # Construct prompt for Claude
            claude_prompt = self._build_claude_prompt(
                user_prompt,
                local_response,
                uncertainty_analysis
            )

            # Request Claude assistance via the bridge
            # This assumes Genesis is running in Termux where Claude Code can access it
            # We'll use a special marker file for Claude to read

            request_file = Path("/tmp/genesis_claude_request.json")
            response_file = Path("/tmp/genesis_claude_response.json")

            # Clean up old response
            if response_file.exists():
                response_file.unlink()

            # Write request
            request_data = {
                "timestamp": datetime.now().isoformat(),
                "user_prompt": user_prompt,
                "local_response": local_response,
                "uncertainty_analysis": uncertainty_analysis,
                "claude_prompt": claude_prompt
            }

            with open(request_file, 'w') as f:
                json.dump(request_data, f, indent=2)

            # Wait for Claude Code to respond (polling with timeout)
            # In a real implementation, this would be an HTTP call or socket connection
            # For now, we'll provide a mechanism for Claude to write a response file

            print("\n⚡ Requesting Claude assistance...")
            print("💡 Waiting for Claude Code to provide refined response...")

            # Simulate: In production, Claude Code would monitor the request file
            # and write to response_file. For demo, we'll show the structure:

            # ACTUAL IMPLEMENTATION: Call Claude via subprocess or API
            # For this demo in Termux context, we provide the interface
            claude_response = self._call_claude_direct(claude_prompt)

            return claude_response

        except Exception as e:
            print(f"⚠ Claude fallback error: {e}")
            return None

    def _call_claude_direct(self, prompt: str) -> Optional[str]:
        """
        Direct call to Claude (placeholder for actual implementation)

        In production, this would:
        1. Use Claude API if available
        2. Use Claude Code bridge if running
        3. Use stdio communication with parent process

        Args:
            prompt: Prompt for Claude

        Returns:
            Claude's response or None if Claude is not available
        """
        # Try multiple connection methods

        # METHOD 1: Check if Claude Code bridge is running
        try:
            import requests
            response = requests.post(
                "http://127.0.0.1:5050/claude_assist",
                json={"prompt": prompt},
                timeout=5
            )
            if response.status_code == 200:
                return response.json().get("response")
        except:
            pass  # Bridge not available

        # METHOD 2: Check for Claude API key
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if api_key:
            try:
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                message = client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}]
                )
                return message.content[0].text
            except Exception as e:
                print(f"⚠ Claude API error: {e}")
                pass  # API not available or error

        # METHOD 3: Use marker file for Claude Code to monitor
        request_file = Path("/tmp/genesis_needs_claude.txt")
        response_file = Path("/tmp/claude_response.txt")

        try:
            # Write request
            with open(request_file, 'w') as f:
                f.write(prompt)

            # Wait for response (max 30 seconds)
            import time
            for _ in range(30):
                if response_file.exists():
                    with open(response_file, 'r') as f:
                        claude_response = f.read()
                    response_file.unlink()  # Clean up
                    request_file.unlink()
                    return claude_response
                time.sleep(1)

            # Timeout - clean up
            if request_file.exists():
                request_file.unlink()

        except Exception as e:
            print(f"⚠ File communication error: {e}")

        # All methods failed - Claude is not available
        return None
        # response = client.messages.create(...)

        # OPTION 3: Use a communication file that Claude Code monitors
        # This is what we'll implement for Termux context

        marker_start = "<<<GENESIS_CLAUDE_REQUEST>>>"
        marker_end = "<<<GENESIS_CLAUDE_REQUEST_END>>>"

        # Print marked request that Claude Code can intercept
        print(f"\n{marker_start}")
        print(json.dumps({
            "request_type": "fallback_assist",
            "prompt": prompt
        }, indent=2))
        print(f"{marker_end}\n")

        # In actual usage, Claude Code (parent) would see this and inject response
        # For now, return None to indicate async processing

        return None  # Claude Code will inject response via another mechanism

    def _build_claude_prompt(
        self,
        user_prompt: str,
        local_response: str,
        uncertainty_analysis: Dict[str, Any]
    ) -> str:
        """
        Build a comprehensive prompt for Claude

        Args:
            user_prompt: Original user request
            local_response: Local model's attempt
            uncertainty_analysis: Uncertainty metrics

        Returns:
            Formatted prompt for Claude
        """
        confidence = uncertainty_analysis.get('confidence_score', 0.0)
        reason = uncertainty_analysis.get('reason', 'unknown')

        prompt = f"""You are assisting Genesis, a local AI running on-device. Genesis attempted to answer the user's question but showed uncertainty (confidence: {confidence:.2f}).

**Original User Request:**
{user_prompt}

**Genesis's Uncertain Response:**
{local_response}

**Uncertainty Detected:**
{reason}

**Your Task:**
Please provide a complete, confident, and accurate response to the user's original request. Your response will be presented to the user as a "Claude-assisted" answer, helping Genesis learn from high-quality examples.

**Response Guidelines:**
1. Directly address the user's request
2. Be specific and actionable
3. Include code examples if applicable
4. Explain your reasoning clearly
5. Keep it concise but comprehensive

Please provide your response:"""

        return prompt

    def log_fallback_event(
        self,
        user_prompt: str,
        local_response: str,
        claude_response: Optional[str],
        uncertainty_analysis: Dict[str, Any]
    ):
        """
        Log a fallback event for analysis and learning

        Args:
            user_prompt: Original user prompt
            local_response: Local model response
            claude_response: Claude's response
            uncertainty_analysis: Uncertainty metrics
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "user_prompt": user_prompt,
            "local_response": local_response,
            "local_confidence": uncertainty_analysis.get('confidence_score', 0.0),
            "uncertainty_reason": uncertainty_analysis.get('reason', 'unknown'),
            "claude_response": claude_response,
            "fallback_triggered": claude_response is not None
        }

        # Append to log file
        try:
            with open(self.fallback_log, 'a') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            print(f"⚠ Could not write fallback log: {e}")

    def add_to_retrain_dataset(
        self,
        user_prompt: str,
        local_response: str,
        claude_response: str,
        uncertainty_analysis: Dict[str, Any]
    ):
        """
        Add a fallback example to the retraining dataset

        This can be used later for fine-tuning or few-shot learning

        Args:
            user_prompt: User's question
            local_response: Local model's uncertain answer
            claude_response: Claude's improved answer
            uncertainty_analysis: Uncertainty metrics
        """
        try:
            # Load existing dataset
            with open(self.retrain_data, 'r') as f:
                dataset = json.load(f)

            # Add new example
            example = {
                "timestamp": datetime.now().isoformat(),
                "input": user_prompt,
                "local_output": local_response,
                "local_confidence": uncertainty_analysis.get('confidence_score', 0.0),
                "improved_output": claude_response,
                "improvement_reason": uncertainty_analysis.get('reason', 'unknown')
            }

            dataset['examples'].append(example)

            # Save updated dataset
            with open(self.retrain_data, 'w') as f:
                json.dump(dataset, f, indent=2)

        except Exception as e:
            print(f"⚠ Could not add to retrain dataset: {e}")

    def get_fallback_stats(self) -> Dict[str, Any]:
        """
        Get statistics about fallback usage

        Returns:
            Dictionary with fallback statistics
        """
        stats = {
            "enabled": self.is_enabled(),
            "total_fallbacks": 0,
            "successful_fallbacks": 0,
            "failed_fallbacks": 0,
            "retrain_examples": 0
        }

        # Count log entries
        try:
            if self.fallback_log.exists():
                with open(self.fallback_log, 'r') as f:
                    for line in f:
                        if line.strip():
                            stats['total_fallbacks'] += 1
                            event = json.loads(line)
                            if event.get('claude_response'):
                                stats['successful_fallbacks'] += 1
                            else:
                                stats['failed_fallbacks'] += 1
        except Exception:
            pass

        # Count retrain examples
        try:
            if self.retrain_data.exists():
                with open(self.retrain_data, 'r') as f:
                    dataset = json.load(f)
                    stats['retrain_examples'] = len(dataset.get('examples', []))
        except Exception:
            pass

        return stats


# CLI utility
if __name__ == "__main__":
    import sys

    fallback = ClaudeFallback()

    if len(sys.argv) < 2:
        print("Genesis Claude Fallback Control")
        print("\nUsage:")
        print("  python claude_fallback.py enable   - Enable Claude fallback")
        print("  python claude_fallback.py disable  - Disable Claude fallback")
        print("  python claude_fallback.py status   - Show fallback status")
        print("  python claude_fallback.py stats    - Show fallback statistics")
        sys.exit(0)

    command = sys.argv[1].lower()

    if command == "enable":
        fallback.enable()
    elif command == "disable":
        fallback.disable()
    elif command == "status":
        if fallback.is_enabled():
            print("✓ Claude fallback is ENABLED")
        else:
            print("✗ Claude fallback is DISABLED")
    elif command == "stats":
        stats = fallback.get_fallback_stats()
        print("\nFallback Statistics:")
        print(f"  Status: {'ENABLED' if stats['enabled'] else 'DISABLED'}")
        print(f"  Total fallbacks: {stats['total_fallbacks']}")
        print(f"  Successful: {stats['successful_fallbacks']}")
        print(f"  Failed: {stats['failed_fallbacks']}")
        print(f"  Retrain examples: {stats['retrain_examples']}")
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
