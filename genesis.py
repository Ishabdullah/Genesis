#!/usr/bin/env python3
"""
Genesis - Local AI Workstation
A Claude-Code-like environment running entirely in Termux
"""

import os
import sys
import subprocess
import re
from pathlib import Path

# Import Genesis modules
from memory import MemoryManager
from executor import CodeExecutor
from tools import GenesisTools
from genesis_bridge import GenesisBridge, execute_remote_code
from uncertainty_detector import UncertaintyDetector
from claude_fallback import ClaudeFallback
from performance_monitor import PerformanceMonitor
from learning_memory import LearningMemory

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

class Genesis:
    """Main Genesis AI Workstation controller"""

    def __init__(self):
        """Initialize Genesis system"""
        self.memory = MemoryManager()
        self.executor = CodeExecutor()
        self.tools = GenesisTools()
        self.bridge = GenesisBridge()
        self.bridge_running = False
        self.uncertainty = UncertaintyDetector()
        self.claude_fallback = ClaudeFallback()
        self.performance = PerformanceMonitor()
        self.learning = LearningMemory()
        self.llama_path = "./llama.cpp/llama-cli"
        self.model_path = "./models/CodeLlama-7B-Instruct.Q4_K_M.gguf"
        self.running = True

        # Genesis identity and system prompt
        self.identity = """I'm Genesis, a local AI assistant running entirely on your device using the CodeLlama-7B model. I can execute code, manage files, and help with development tasks - all while keeping your data private and working offline."""

        # System prompt template optimized for CodeLlama-Instruct
        self.system_prompt = """You are Genesis, a local AI assistant running on the user's device.

IDENTITY: When asked who you are or to identify yourself, respond:
"I'm Genesis, a local AI assistant running entirely on your device using the CodeLlama-7B model."

For file/directory operations, use these commands:
- LIST: /path/to/dir - list directory contents
- READ: /path/to/file - read file
- WRITE: /path/to/file - write file (followed by content in code block)
- SEARCH: pattern in /path - search for text in files

IMPORTANT: Only use READ: to read files if explicitly asked. Do NOT read README.md unless user specifically requests it.

For shell commands (ls, pwd, cat, etc.), execute them directly.
Keep responses brief and action-focused."""

    def print_header(self):
        """Display Genesis header"""
        assist_status = "ON" if self.claude_fallback.is_enabled() else "OFF"
        assist_color = Colors.GREEN if self.claude_fallback.is_enabled() else Colors.DIM

        print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}")
        print("🧬 Genesis — Local AI Workstation")
        print("Powered by CodeLlama-7B running on Samsung S24 Ultra")
        print(f"{assist_color}Claude Assist: {assist_status}{Colors.RESET}{Colors.CYAN}")
        print(f"{'=' * 60}{Colors.RESET}\n")
        print(f"{Colors.DIM}Commands: #exit | #help | #assist | #performance | #memory{Colors.RESET}\n")

    def print_help(self):
        """Display help information"""
        help_text = f"""
{Colors.BOLD}Genesis Commands:{Colors.RESET}

{Colors.GREEN}#exit{Colors.RESET}       - Exit Genesis
{Colors.GREEN}#reset{Colors.RESET}      - Clear conversation memory
{Colors.GREEN}#help{Colors.RESET}       - Show this help message
{Colors.GREEN}#stats{Colors.RESET}      - Show memory statistics
{Colors.GREEN}#pwd{Colors.RESET}        - Show current directory
{Colors.GREEN}#bridge{Colors.RESET}     - Start/stop Claude Code bridge server
{Colors.GREEN}#assist{Colors.RESET}     - Toggle Claude fallback assist (on/off)
{Colors.GREEN}#assist-stats{Colors.RESET} - Show Claude assist statistics

{Colors.BOLD}Performance Monitoring:{Colors.RESET}
{Colors.GREEN}#performance{Colors.RESET}   - Show comprehensive performance metrics
{Colors.GREEN}#correct{Colors.RESET}       - Mark last response as correct
{Colors.GREEN}#incorrect{Colors.RESET}     - Mark last response as incorrect
{Colors.GREEN}#reset_metrics{Colors.RESET} - Reset all performance metrics

{Colors.BOLD}Memory & Learning:{Colors.RESET}
{Colors.GREEN}#memory{Colors.RESET}        - Show persistent memory summary
{Colors.GREEN}#prune_memory{Colors.RESET}  - Manually trigger memory pruning
{Colors.GREEN}#export_memory{Colors.RESET} - Export memory backup

{Colors.BOLD}File Operations:{Colors.RESET}
You can ask Genesis to read, write, list, or manipulate files.
Examples:
  - "Read the file config.json"
  - "Write a Python script that prints hello world to test.py"
  - "List files in the current directory"

{Colors.BOLD}Code Execution:{Colors.RESET}
Ask Genesis to write Python code and it will execute automatically.
Example: "Write a script to calculate fibonacci numbers"
"""
        print(help_text)

    def toggle_bridge(self):
        """Start or stop the Genesis-Claude Code bridge"""
        if not self.bridge_running:
            print(f"\n{Colors.CYAN}Starting Genesis Bridge...{Colors.RESET}\n")
            self.bridge.start()
            self.bridge_running = True
            print(f"\n{Colors.BOLD}Claude Code can now connect using:{Colors.RESET}")
            print(f'{Colors.DIM}curl -X POST -H "Content-Type: application/json" \\')
            print(f'     -H "X-Genesis-Key: localonly" \\')
            print(f'     -d \'{{"code":"print(\\"test\\")"}} \' \\')
            print(f'     http://127.0.0.1:5050/run{Colors.RESET}\n')
        else:
            print(f"\n{Colors.YELLOW}Bridge is already running on 127.0.0.1:5050{Colors.RESET}\n")
            print("Use #exit to stop Genesis and the bridge\n")

    def toggle_claude_assist(self):
        """Toggle Claude fallback assist on/off"""
        if self.claude_fallback.is_enabled():
            self.claude_fallback.disable()
            print(f"\n{Colors.YELLOW}Claude assist disabled{Colors.RESET}")
            print("Genesis will run entirely locally without fallback\n")
        else:
            self.claude_fallback.enable()
            print(f"\n{Colors.GREEN}Claude assist enabled{Colors.RESET}")
            print("Genesis will request Claude's help when uncertain")
            print("Logs: ~/Genesis/logs/fallback_history.log\n")

    def show_assist_stats(self):
        """Show Claude assist statistics"""
        stats = self.claude_fallback.get_fallback_stats()

        print(f"\n{Colors.BOLD}Claude Assist Statistics:{Colors.RESET}\n")
        print(f"Status: {'ENABLED' if stats['enabled'] else 'DISABLED'}")
        print(f"Total fallbacks: {stats['total_fallbacks']}")
        print(f"Successful: {stats['successful_fallbacks']}")
        print(f"Failed: {stats['failed_fallbacks']}")
        print(f"Learning examples: {stats['retrain_examples']}")

        if stats['total_fallbacks'] > 0:
            success_rate = (stats['successful_fallbacks'] / stats['total_fallbacks']) * 100
            print(f"Success rate: {success_rate:.1f}%")

        print(f"\nLogs: ~/Genesis/logs/fallback_history.log")
        print(f"Dataset: ~/Genesis/data/retrain_set.json\n")

    def check_llama_cpp(self) -> bool:
        """Check if llama.cpp is available"""
        # Try multiple possible binary names (new CMake build locations)
        possible_paths = [
            "./llama.cpp/build/bin/llama-cli",
            "./llama.cpp/build/bin/main",
            "./llama.cpp/llama-cli",
            "./llama.cpp/main"
        ]

        for path in possible_paths:
            if os.path.exists(path):
                self.llama_path = path
                return True

        return False

    def call_llm(self, user_prompt: str) -> str:
        """
        Call the local LLM with user prompt and conversation history

        Args:
            user_prompt: User's input

        Returns:
            LLM response
        """
        try:
            # Build context from recent conversation history
            context = self.memory.get_context_string()

            # Add instruction about using tools
            tool_instructions = """You are Genesis. Be direct, concise, and focused.

Available tools:
- LIST: /path - list directory
- READ: /path/file - read file
- SEARCH: pattern in /path - search content
- Python code in ```python blocks

Rules:
1. Answer the user's CURRENT question only
2. Do NOT repeat previous conversations or examples
3. Be brief and action-oriented
4. Use tools when appropriate for the task
5. For math: calculate and give answer only
6. For string operations: perform and show result only
7. For code: write clean, working code without extra commentary
"""

            # Use CodeLlama-Instruct format with minimal context
            if context:
                # Include only last exchange for continuity (reduced from 2 to 1)
                recent = context.split('\n')[-4:]  # Last 1 Q&A pair (4 lines)
                context_str = '\n'.join(recent)
                full_prompt = f"[INST] {tool_instructions}\n\nLast exchange:\n{context_str}\n\nCurrent question: {user_prompt} [/INST]"
            else:
                full_prompt = f"[INST] {tool_instructions}\n\nQuestion: {user_prompt} [/INST]"

            # Call llama.cpp with balanced parameters
            cmd = [
                self.llama_path,
                "-m", self.model_path,
                "-p", full_prompt,
                "-n", "250",  # Increased to avoid mid-sentence cuts
                "-t", "8",    # All cores
                "--temp", "0.5",  # Slightly higher for more natural text
                "--top-p", "0.9",
                "--top-k", "40",
                "-c", "1024",  # Increased context window
                "--no-display-prompt",
                "-b", "512",  # Batch size
                "--mirostat", "2",  # Mirostat for quality
                "--mirostat-lr", "0.1",
                "--mirostat-ent", "5.0",
                "--repeat-penalty", "1.1"  # Prevent repetition
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # Increased timeout for context processing
            )

            response = result.stdout.strip()

            # Clean up response (remove prompt echo if present)
            if "Assistant:" in response:
                response = response.split("Assistant:")[-1].strip()

            return response if response else "⚠ No response from model"

        except subprocess.TimeoutExpired:
            return "⚠ LLM timeout - try a shorter prompt"
        except FileNotFoundError:
            return f"⚠ LLM binary not found at {self.llama_path}"
        except Exception as e:
            return f"⚠ LLM error: {str(e)}"

    def execute_shell_command(self, command: str) -> tuple[bool, str]:
        """
        Execute shell command safely

        Args:
            command: Shell command to execute

        Returns:
            (success, output) tuple
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=os.getcwd()
            )

            output = result.stdout
            if result.stderr:
                output += f"\n{result.stderr}"

            return result.returncode == 0, output

        except subprocess.TimeoutExpired:
            return False, "⚠ Command timeout (30s limit)"
        except Exception as e:
            return False, f"⚠ Command error: {str(e)}"

    def handle_direct_command(self, user_input: str) -> tuple[bool, str]:
        """
        Handle commands that can be executed directly without LLM

        Args:
            user_input: User's input

        Returns:
            (handled, result) - True if command was handled directly
        """
        input_lower = user_input.lower().strip()

        # Identity queries
        identity_triggers = [
            "who are you", "identify yourself", "what are you",
            "genesis identify", "tell me about yourself",
            "who is genesis", "what is genesis"
        ]
        if any(trigger in input_lower for trigger in identity_triggers):
            return True, self.identity

        # List directory commands
        if input_lower in ["ls", "list files", "show files", "list directory"]:
            return True, self.tools.list_directory(".")

        if input_lower.startswith("ls "):
            path = user_input[3:].strip()
            return True, self.tools.list_directory(path)

        # Home directory listing
        if "files in" in input_lower and "home" in input_lower:
            return True, self.tools.list_directory(os.path.expanduser("~"))

        # Current directory
        if input_lower in ["pwd", "current directory", "where am i"]:
            return True, self.tools.get_current_directory()

        # Read file commands
        if input_lower.startswith("cat "):
            filepath = user_input[4:].strip()
            return True, self.tools.read_file(filepath)

        # Change directory
        if input_lower.startswith("cd "):
            path = user_input[3:].strip()
            return True, self.tools.change_directory(path)

        # Git commands (all git operations)
        if input_lower.startswith("git "):
            success, output = self.execute_shell_command(user_input)
            return True, output

        # Find files
        if input_lower.startswith("find "):
            # Parse: find pattern [in path]
            parts = user_input[5:].strip().split(" in ")
            pattern = parts[0].strip()
            path = parts[1].strip() if len(parts) > 1 else "."
            return True, self.tools.find_files(pattern, path)

        # Grep/search
        if input_lower.startswith("grep "):
            # Parse: grep pattern [in file/path]
            parts = user_input[5:].strip().split(" in ")
            pattern = parts[0].strip()
            target = parts[1].strip() if len(parts) > 1 else None

            if target and Path(target).is_file():
                return True, self.tools.grep_files(pattern, filepath=target)
            else:
                return True, self.tools.grep_files(pattern, path=target or ".")

        # Package installation
        if input_lower.startswith(("pip install", "npm install", "apt install")):
            success, output = self.execute_shell_command(user_input)
            return True, output

        # Environment variables
        if input_lower.startswith("echo $"):
            var = user_input[6:].strip()
            value = os.environ.get(var, f"⚠ ${var} not set")
            return True, value

        # Process management
        if input_lower in ["ps", "ps aux", "top"]:
            success, output = self.execute_shell_command(user_input)
            return True, output[:2000]  # Limit output

        # Generic shell commands (be careful with this)
        # Allow common safe commands
        safe_commands = ["whoami", "hostname", "date", "uptime", "df", "du", "which", "whereis"]
        if input_lower.split()[0] in safe_commands:
            success, output = self.execute_shell_command(user_input)
            return True, output

        # Simple math calculations
        if any(word in input_lower for word in ["what is", "calculate", "compute", "solve"]):
            # Extract potential math expression
            import re
            # Look for patterns like "what is 8 × 7 + 6" or "calculate 2+2"
            math_patterns = [
                r"what\s+is\s+([0-9\s+\-*/×÷().\^]+)",
                r"calculate\s+([0-9\s+\-*/×÷().\^]+)",
                r"compute\s+([0-9\s+\-*/×÷().\^]+)",
                r"solve\s+([0-9\s+\-*/×÷().\^]+)"
            ]

            for pattern in math_patterns:
                match = re.search(pattern, input_lower)
                if match:
                    expr = match.group(1).strip()
                    # Replace unicode math symbols
                    expr = expr.replace('×', '*').replace('÷', '/')
                    expr = expr.replace('^', '**')
                    try:
                        result = eval(expr, {"__builtins__": {}})
                        return True, f"The answer is {result}"
                    except:
                        pass  # Fall through to LLM if can't evaluate

        # String reversal
        if "reverse" in input_lower and "string" in input_lower:
            # Extract the string to reverse
            import re
            # Look for patterns like "reverse this string: Genesis" or "reverse 'hello'"
            patterns = [
                r"reverse\s+(?:this\s+)?string:?\s*['\"]?([^'\"]+?)['\"]?\s*$",
                r"reverse\s+['\"]([^'\"]+)['\"]",
            ]

            for pattern in patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    text = match.group(1).strip()
                    reversed_text = text[::-1]
                    return True, f"Reversed: {reversed_text}"

        # Memory recall - check learning memory for context
        if any(phrase in input_lower for phrase in ["what's my", "what is my", "do you remember", "recall"]):
            # Get relevant context from learning memory
            relevant = self.learning.get_relevant_context(user_input, max_results=3)
            if relevant:
                # Check if any conversation contains the answer
                for conv in relevant:
                    if "favorite" in input_lower and "favorite" in conv.get("user_input", "").lower():
                        # Extract the answer from the original conversation
                        response = conv.get("assistant_response", "")
                        if response:
                            return True, f"Based on our previous conversation: {response}"

        # Not a direct command
        return False, ""

    def process_tool_calls(self, text: str) -> str:
        """
        Process tool calls mentioned in LLM response

        Args:
            text: LLM response text

        Returns:
            Text with tool results appended
        """
        results = []

        # Check for READ commands
        read_pattern = r'READ:\s*([^\n]+)'
        for match in re.finditer(read_pattern, text):
            filepath = match.group(1).strip()
            result = self.tools.read_file(filepath)
            results.append(f"\n{Colors.CYAN}[File Read]{Colors.RESET}\n{result}")

        # Check for WRITE commands
        write_pattern = r'WRITE:\s*([^\n]+)\n```(?:python)?\n(.*?)```'
        for match in re.finditer(write_pattern, text, re.DOTALL):
            filepath = match.group(1).strip()
            content = match.group(2).strip()
            result = self.tools.write_file(filepath, content)
            results.append(f"\n{Colors.GREEN}[File Write]{Colors.RESET}\n{result}")

        # Check for LIST commands
        list_pattern = r'LIST:\s*([^\n]+)'
        for match in re.finditer(list_pattern, text):
            dirpath = match.group(1).strip()
            result = self.tools.list_directory(dirpath)
            results.append(f"\n{Colors.BLUE}[Directory List]{Colors.RESET}\n{result}")

        # Check for SEARCH commands
        search_pattern = r'SEARCH:\s*([^\n]+)'
        for match in re.finditer(search_pattern, text):
            search_spec = match.group(1).strip()
            # Parse: pattern in /path
            if " in " in search_spec:
                parts = search_spec.split(" in ", 1)
                pattern = parts[0].strip()
                path = parts[1].strip() if len(parts) > 1 else "."
            else:
                pattern = search_spec
                path = "."
            result = self.tools.grep_files(pattern, path=path)
            results.append(f"\n{Colors.CYAN}[Search Results]{Colors.RESET}\n{result}")

        return "".join(results)

    def process_code_execution(self, text: str) -> str:
        """
        Extract and execute Python code blocks

        IMPORTANT: Only executes code blocks that don't contain tool directives
        All code blocks are combined into a single execution to preserve state

        Args:
            text: LLM response text

        Returns:
            Execution results
        """
        code_blocks = self.executor.extract_code_blocks(text)

        if not code_blocks:
            return ""

        # Filter out code blocks with tool directives
        tool_directives = ['READ:', 'WRITE:', 'LIST:', 'SEARCH:']
        valid_blocks = []

        for i, code in enumerate(code_blocks, 1):
            has_tool_directive = any(directive in code for directive in tool_directives)
            if has_tool_directive:
                print(f"\n{Colors.DIM}[Skipping Code Block {i} - contains tool directive]{Colors.RESET}")
            else:
                valid_blocks.append(code)

        if not valid_blocks:
            return ""

        # Combine all valid code blocks into one execution
        # This preserves variables and functions between blocks
        combined_code = "\n\n".join(valid_blocks)

        print(f"\n{Colors.YELLOW}[Executing {len(valid_blocks)} code block(s)]{Colors.RESET}")
        print(f"{Colors.DIM}{combined_code[:200]}{'...' if len(combined_code) > 200 else ''}{Colors.RESET}\n")

        success, output = self.executor.execute_code(combined_code)

        if success:
            return f"{Colors.GREEN}✓ Execution successful:{Colors.RESET}\n{output}"
        else:
            return f"{Colors.RED}✗ Execution failed:{Colors.RESET}\n{output}"

    def process_input(self, user_input: str):
        """
        Process user input and generate response

        Args:
            user_input: User's input text
        """
        # Handle special commands
        if user_input.lower() == "#exit":
            print(f"\n{Colors.CYAN}Goodbye! 🧬{Colors.RESET}\n")
            self.running = False
            return

        if user_input.lower() == "#reset":
            self.memory.reset()
            return

        if user_input.lower() == "#help":
            self.print_help()
            return

        if user_input.lower() == "#stats":
            stats = self.memory.get_stats()
            print(f"\n{Colors.BOLD}Memory Statistics:{Colors.RESET}")
            print(f"Conversations: {stats['total_conversations']}")
            print(f"Memory size: {stats['memory_size_kb']:.2f} KB\n")
            return

        if user_input.lower() == "#pwd":
            print(self.tools.get_current_directory())
            return

        if user_input.lower() == "#bridge":
            self.toggle_bridge()
            return

        if user_input.lower() == "#assist":
            self.toggle_claude_assist()
            return

        if user_input.lower() == "#assist-stats":
            self.show_assist_stats()
            return

        # Performance monitoring commands
        if user_input.lower() == "#performance":
            print(self.performance.get_performance_summary())
            return

        if user_input.lower() == "#correct":
            feedback = self.performance.record_feedback(is_correct=True)
            print(f"\n{Colors.GREEN}✓ Last response marked as correct{Colors.RESET}")
            print(f"{Colors.DIM}Thank you for the feedback!{Colors.RESET}\n")
            return

        if user_input.lower() == "#incorrect":
            feedback = self.performance.record_feedback(is_correct=False)
            print(f"\n{Colors.RED}✗ Last response marked as incorrect{Colors.RESET}")
            print(f"{Colors.DIM}Thank you for the feedback! I'll learn from this.{Colors.RESET}\n")
            return

        if user_input.lower() == "#reset_metrics":
            self.performance.reset_metrics()
            print(f"\n{Colors.CYAN}✓ All performance metrics reset{Colors.RESET}\n")
            return

        if user_input.lower() == "#memory":
            print(self.learning.get_memory_summary())
            return

        if user_input.lower() == "#prune_memory":
            self.learning.manual_prune()
            print(f"\n{Colors.CYAN}✓ Memory pruned{Colors.RESET}\n")
            return

        if user_input.lower() == "#export_memory":
            export_path = self.learning.export_memory()
            print(f"\n{Colors.GREEN}✓ Memory exported to {export_path}{Colors.RESET}\n")
            return

        # Start performance tracking
        query_id = self.performance.start_query(user_input)

        # Check for direct commands that don't need LLM
        handled, result = self.handle_direct_command(user_input)
        if handled:
            print(f"\n{Colors.BOLD}Genesis:{Colors.RESET}")
            print(result)
            self.memory.add_interaction(user_input, result)

            # Store in learning memory
            self.learning.add_conversation(
                user_input=user_input,
                assistant_response=result,
                metadata={
                    "was_direct_command": True,
                    "confidence_score": 1.0,
                    "had_fallback": False
                }
            )

            # Record direct command performance (instant)
            self.performance.end_query(
                query_id=query_id,
                user_input=user_input,
                response=result,
                was_direct_command=True,
                had_fallback=False,
                confidence_score=1.0,
                error=None
            )
            return

        # Process through LLM
        print(f"\n{Colors.DIM}[Thinking...]{Colors.RESET}\n")

        try:
            response = self.call_llm(user_input)
        except Exception as e:
            # Record error
            self.performance.record_error("llm_error", str(e), user_input)
            raise

        # Check for uncertainty and trigger fallback if needed
        should_fallback, uncertainty_analysis = self.uncertainty.should_trigger_fallback(response)

        claude_response = None
        if should_fallback and self.claude_fallback.is_enabled():
            print(f"\n{Colors.YELLOW}⚡ Genesis is uncertain (confidence: {uncertainty_analysis['confidence_score']:.2f})")
            print(f"   Requesting Claude assistance...{Colors.RESET}\n")

            # Record fallback attempt
            claude_reachable = False

            # Request Claude's help
            claude_response = self.claude_fallback.request_claude_assist(
                user_input,
                response,
                uncertainty_analysis
            )

            # Check if Claude was reachable
            claude_reachable = (claude_response is not None)

            # Record fallback in performance monitor
            self.performance.record_fallback(
                user_input=user_input,
                local_confidence=uncertainty_analysis['confidence_score'],
                success=claude_reachable
            )

            if claude_response is None:
                print(f"\n{Colors.RED}⚠ Unable to reach Claude Code for assistance{Colors.RESET}")
                print(f"{Colors.YELLOW}Genesis cannot complete this task reliably.{Colors.RESET}\n")
                print(f"{Colors.DIM}Reasons:{Colors.RESET}")
                print(f"  • Task complexity exceeds Genesis capabilities")
                print(f"  • Confidence score: {uncertainty_analysis['confidence_score']:.2f} (< 0.60 threshold)")
                print(f"  • Claude Code is not available for fallback\n")
                print(f"{Colors.CYAN}Suggestions:{Colors.RESET}")
                print(f"  1. Try a simpler version of your request")
                print(f"  2. Break the task into smaller steps")
                print(f"  3. Use direct commands (ls, git, find, grep)")
                print(f"  4. Set up Claude API key: export ANTHROPIC_API_KEY=your_key")
                print(f"  5. Ensure Claude Code bridge is running\n")

                # Still log the attempt
                self.claude_fallback.log_fallback_event(
                    user_input,
                    response,
                    None,  # Claude response was None
                    uncertainty_analysis
                )

                # Show the uncertain response anyway with disclaimer
                print(f"{Colors.DIM}Showing Genesis's uncertain response (use with caution):{Colors.RESET}\n")
                print(f"{Colors.BOLD}Genesis (uncertain):{Colors.RESET}")
                print(response)

                # Save to memory with warning
                self.memory.add_interaction(
                    user_input,
                    f"⚠ UNCERTAIN RESPONSE (confidence: {uncertainty_analysis['confidence_score']:.2f}):\n{response}"
                )
                return

            # Log the successful fallback event
            self.claude_fallback.log_fallback_event(
                user_input,
                response,
                claude_response,
                uncertainty_analysis
            )

            # Add to retraining dataset if we got a Claude response
            if claude_response:
                self.claude_fallback.add_to_retrain_dataset(
                    user_input,
                    response,
                    claude_response,
                    uncertainty_analysis
                )

        # Display response
        if claude_response:
            print(f"{Colors.BOLD}{Colors.CYAN}Genesis (Claude-assisted):{Colors.RESET}")
            print(claude_response)
            final_response = claude_response
        else:
            print(f"{Colors.BOLD}Genesis:{Colors.RESET}")
            print(response)
            final_response = response

            # Show uncertainty warning if fallback was skipped
            if should_fallback and not self.claude_fallback.is_enabled():
                print(f"\n{Colors.YELLOW}⚠ Genesis is uncertain about this response{Colors.RESET}")
                print(f"{Colors.DIM}Confidence score: {uncertainty_analysis['confidence_score']:.2f} (< 0.60 threshold){Colors.RESET}")
                print(f"\n{Colors.CYAN}Genesis cannot complete this task reliably without Claude assistance.{Colors.RESET}\n")
                print(f"{Colors.DIM}Options:{Colors.RESET}")
                print(f"  1. Enable Claude assist: {Colors.GREEN}#assist{Colors.RESET}")
                print(f"  2. Try a simpler version of your request")
                print(f"  3. Break the task into smaller steps")
                print(f"  4. Use direct commands when possible (ls, git, find)\n")
                print(f"{Colors.DIM}The response above should be used with caution.{Colors.RESET}")

        # Process tool calls
        tool_results = self.process_tool_calls(final_response)
        if tool_results:
            print(tool_results)

        # Execute code blocks
        code_results = self.process_code_execution(final_response)
        if code_results:
            print(f"\n{code_results}")

        # Save to memory
        full_response = final_response
        if tool_results:
            full_response += "\n" + tool_results
        if code_results:
            full_response += "\n" + code_results

        self.memory.add_interaction(user_input, full_response)

        # Store in learning memory with metadata
        self.learning.add_conversation(
            user_input=user_input,
            assistant_response=full_response,
            metadata={
                "had_fallback": claude_response is not None,
                "confidence_score": uncertainty_analysis.get('confidence_score'),
                "was_direct_command": False
            }
        )

        # Record query performance
        self.performance.end_query(
            query_id=query_id,
            user_input=user_input,
            response=full_response,
            was_direct_command=False,
            had_fallback=(claude_response is not None),
            confidence_score=uncertainty_analysis.get('confidence_score'),
            error=None
        )

    def get_multiline_input(self) -> str:
        """
        Get multiline input from user

        Returns:
            Complete user input
        """
        print(f"{Colors.BOLD}{Colors.GREEN}Genesis>{Colors.RESET} ", end='', flush=True)

        lines = []
        try:
            first_line = input()
            lines.append(first_line)

            # Check if user wants multiline (ends with backslash)
            while lines[-1].endswith('\\'):
                lines[-1] = lines[-1][:-1]  # Remove backslash
                print(f"{Colors.GREEN}      >{Colors.RESET} ", end='', flush=True)
                lines.append(input())

        except EOFError:
            return "#exit"
        except KeyboardInterrupt:
            print()
            return ""

        return '\n'.join(lines).strip()

    def run(self):
        """Main Genesis loop"""
        self.print_header()

        # Check if llama.cpp is available
        if not self.check_llama_cpp():
            print(f"{Colors.RED}⚠ Error: llama.cpp not found{Colors.RESET}")
            print("Please run setup_genesis.sh first\n")
            return

        # Check if model exists
        if not os.path.exists(self.model_path):
            print(f"{Colors.RED}⚠ Error: Model not found at {self.model_path}{Colors.RESET}")
            print("Please ensure the model is properly linked\n")
            return

        print(f"{Colors.GREEN}✓ System ready{Colors.RESET}\n")

        # Main interaction loop
        while self.running:
            try:
                user_input = self.get_multiline_input()

                if not user_input:
                    continue

                self.process_input(user_input)

            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Use #exit to quit{Colors.RESET}\n")
            except Exception as e:
                print(f"{Colors.RED}⚠ Error: {e}{Colors.RESET}\n")

        # Cleanup
        self.executor.clean_runtime()

def main():
    """Entry point"""
    genesis = Genesis()
    genesis.run()

if __name__ == "__main__":
    main()
