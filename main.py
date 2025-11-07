#!/usr/bin/env python3
"""
Genesis Android App - Main Entry Point
A futuristic AI assistant with device control capabilities
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.clock import Clock, mainthread
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.gridlayout import GridLayout
from kivy.metrics import dp
import threading
import sys
import os
from pathlib import Path
import platform
import json
from datetime import datetime

# Add Genesis modules to path
sys.path.insert(0, str(Path(__file__).parent))

# Import Genesis core
from genesis import Genesis as GenesisCore
from device_manager import get_device_manager
from accel_manager import AccelManager, get_accel_manager

# Detect if this is a debug build
DEBUG_MODE = os.environ.get('GENESIS_DEBUG', '1') == '1'  # Default to debug for APK debug builds

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class FuturisticTextInput(TextInput):
    """Custom futuristic text input with neon styling"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.05, 0.05, 0.15, 1)
        self.foreground_color = (0, 1, 1, 1)  # Cyan
        self.cursor_color = (0, 1, 1, 1)
        self.font_name = 'RobotoMono-Regular'
        self.padding = [dp(15), dp(15)]

        with self.canvas.before:
            Color(0.1, 0.5, 0.8, 0.3)  # Neon blue glow
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class FuturisticButton(Button):
    """Custom futuristic button with neon styling"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.color = (0, 1, 1, 1)  # Cyan text
        self.font_name = 'RobotoMono-Regular'
        self.bold = True

        with self.canvas.before:
            Color(0.1, 0.5, 0.8, 0.8)  # Neon blue
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(15)])

        self.bind(pos=self.update_rect, size=self.update_rect)
        self.bind(on_press=self.on_button_press)
        self.bind(on_release=self.on_button_release)

    def update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def on_button_press(self, *args):
        with self.canvas.before:
            Color(0.2, 0.7, 1, 1)  # Brighter on press

    def on_button_release(self, *args):
        with self.canvas.before:
            Color(0.1, 0.5, 0.8, 0.8)  # Back to normal


class ChatMessage(BoxLayout):
    """Individual chat message widget with styling"""

    def __init__(self, text, is_user=True, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.padding = [dp(10), dp(5)]
        self.spacing = dp(10)

        # Message bubble
        message_bg_color = (0.1, 0.5, 0.8, 0.3) if is_user else (0.2, 0.2, 0.3, 0.5)
        message_text_color = (0, 1, 1, 1) if is_user else (0.5, 1, 0.5, 1)  # Cyan for user, green for AI

        message_label = Label(
            text=text,
            color=message_text_color,
            size_hint_y=None,
            markup=True,
            halign='left',
            valign='top',
            padding=[dp(15), dp(10)]
        )
        message_label.bind(
            width=lambda *x: message_label.setter('text_size')(message_label, (message_label.width, None)),
            texture_size=lambda *x: message_label.setter('height')(message_label, message_label.texture_size[1] + dp(20))
        )

        # Add avatar/icon space
        avatar = Label(
            text='👤' if is_user else '🧬',
            font_size='24sp',
            size_hint_x=None,
            width=dp(40)
        )

        if is_user:
            self.add_widget(avatar)
            self.add_widget(message_label)
        else:
            self.add_widget(message_label)
            self.add_widget(avatar)

        self.height = message_label.height + dp(10)


class DebugPanel(BoxLayout):
    """Debug information panel for developers"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(200)
        self.padding = [dp(5), dp(5)]
        self.spacing = dp(3)

        with self.canvas.before:
            Color(0.1, 0.1, 0.2, 0.95)  # Dark background
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(5)])

        self.bind(pos=self.update_rect, size=self.update_rect)

        # Debug info label
        self.debug_label = Label(
            text='[b][color=ffff00]DEBUG MODE[/color][/b]\nInitializing...',
            markup=True,
            color=(0.8, 0.8, 0.8, 1),
            font_size='9sp',
            size_hint_y=1,
            halign='left',
            valign='top',
            text_size=(Window.width - dp(20), None)
        )
        self.debug_label.bind(
            width=lambda *x: self.debug_label.setter('text_size')(
                self.debug_label, (self.debug_label.width, None)
            )
        )
        self.add_widget(self.debug_label)

        # Start update timer
        Clock.schedule_interval(self.update_debug_info, 2.0)  # Update every 2 seconds

    def update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def update_debug_info(self, dt):
        """Update debug information"""
        try:
            info_lines = [
                '[b][color=ffff00]🔧 DEBUG MODE[/color][/b]',
                f'[color=00ffff]Time:[/color] {datetime.now().strftime("%H:%M:%S")}'
            ]

            # Memory info
            if PSUTIL_AVAILABLE:
                process = psutil.Process()
                mem_info = process.memory_info()
                mem_mb = mem_info.rss / 1024 / 1024
                cpu_percent = process.cpu_percent(interval=0.1)
                info_lines.append(f'[color=00ff00]Memory:[/color] {mem_mb:.1f} MB | [color=00ff00]CPU:[/color] {cpu_percent:.1f}%')

            # Device info
            info_lines.append(f'[color=ff00ff]Platform:[/color] {platform.system()} {platform.release()}')

            # App info
            app = App.get_running_app()
            if hasattr(app, 'genesis_core') and app.genesis_core:
                info_lines.append('[color=00ff00]Core:[/color] ✓ Initialized')
            else:
                info_lines.append('[color=ffaa00]Core:[/color] ⚠ Not Ready')

            if hasattr(app, 'accel_manager') and app.accel_manager:
                info_lines.append(f'[color=00ffff]Accel:[/color] {app.current_accel_mode.upper()}')
            else:
                info_lines.append('[color=ffaa00]Accel:[/color] ⚠ Not Initialized')

            # Module status
            modules_loaded = []
            if 'genesis' in sys.modules:
                modules_loaded.append('genesis')
            if 'device_manager' in sys.modules:
                modules_loaded.append('device')
            if 'accel_manager' in sys.modules:
                modules_loaded.append('accel')

            info_lines.append(f'[color=8888ff]Modules:[/color] {", ".join(modules_loaded)}')

            # Thread count
            thread_count = threading.active_count()
            info_lines.append(f'[color=ff8800]Threads:[/color] {thread_count} active')

            self.debug_label.text = '\n'.join(info_lines)
        except Exception as e:
            self.debug_label.text = f'[color=ff0000]Debug Error:[/color] {str(e)}'


class GenesisApp(App):
    """Main Genesis Android Application"""

    def build(self):
        """Build the app UI"""
        self.title = 'Genesis AI Assistant'
        self.debug_logs = []  # Store debug logs

        # Set window background to dark futuristic theme
        Window.clearcolor = (0.02, 0.02, 0.08, 1)

        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # Header with gradient background
        header = BoxLayout(size_hint_y=None, height=dp(70), padding=dp(5))
        with header.canvas.before:
            Color(0.05, 0.15, 0.3, 1)
            self.header_rect = RoundedRectangle(pos=header.pos, size=header.size, radius=[dp(15)])
        header.bind(pos=self.update_header_rect, size=self.update_header_rect)

        # Title
        title_label = Label(
            text='[b]🧬 GENESIS[/b]\n[size=12sp]AI Workstation[/size]',
            markup=True,
            color=(0, 1, 1, 1),
            font_name='RobotoMono-Regular',
            halign='center'
        )
        header.add_widget(title_label)

        # Status and acceleration indicator
        status_box = BoxLayout(orientation='vertical', size_hint_x=None, width=dp(120))

        self.status_label = Label(
            text='[color=00ff00]● READY[/color]',
            markup=True,
            font_size='12sp',
            halign='center'
        )
        status_box.add_widget(self.status_label)

        self.accel_label = Label(
            text='[color=666666]CPU[/color]',
            markup=True,
            font_size='10sp',
            halign='center'
        )
        status_box.add_widget(self.accel_label)

        header.add_widget(status_box)

        main_layout.add_widget(header)

        # Debug panel (only in debug mode)
        if DEBUG_MODE:
            self.debug_panel = DebugPanel()
            main_layout.add_widget(self.debug_panel)
            self.log_debug("Debug mode enabled")

        # Chat history (ScrollView)
        self.chat_scroll = ScrollView(size_hint=(1, 1))
        self.chat_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5), padding=dp(5))
        self.chat_layout.bind(minimum_height=self.chat_layout.setter('height'))

        with self.chat_scroll.canvas.before:
            Color(0.03, 0.03, 0.1, 0.8)
            self.chat_bg = RoundedRectangle(pos=self.chat_scroll.pos, size=self.chat_scroll.size, radius=[dp(10)])
        self.chat_scroll.bind(pos=self.update_chat_bg, size=self.update_chat_bg)

        self.chat_scroll.add_widget(self.chat_layout)
        main_layout.add_widget(self.chat_scroll)

        # Quick action buttons
        quick_actions = GridLayout(cols=4, size_hint_y=None, height=dp(50), spacing=dp(5))

        quick_action_buttons = [
            ('📍', 'Location'),
            ('📸', 'Camera'),
            ('🔦', 'Light'),
            ('⚡', 'Accel')
        ]

        for emoji, action in quick_action_buttons:
            btn = FuturisticButton(
                text=f'{emoji}\n[size=10]{action}[/size]',
                markup=True,
                font_size='16sp'
            )
            btn.bind(on_press=lambda x, a=action: self.quick_action(a))
            quick_actions.add_widget(btn)

        main_layout.add_widget(quick_actions)

        # Input area
        input_layout = BoxLayout(size_hint_y=None, height=dp(60), spacing=dp(5))

        self.input_field = FuturisticTextInput(
            hint_text='Ask Genesis anything...',
            hint_text_color=(0, 0.7, 0.7, 0.5),
            multiline=False,
            font_size='16sp'
        )
        self.input_field.bind(on_text_validate=self.send_message)

        send_button = FuturisticButton(
            text='⚡\nSEND',
            markup=True,
            size_hint_x=None,
            width=dp(80),
            font_size='14sp'
        )
        send_button.bind(on_press=self.send_message)

        input_layout.add_widget(self.input_field)
        input_layout.add_widget(send_button)

        main_layout.add_widget(input_layout)

        # Initialize Genesis core
        self.genesis_core = None
        self.device_manager = get_device_manager()
        self.accel_manager = None
        self.current_accel_mode = 'cpu'

        # Add welcome message
        self.add_message('Welcome to Genesis AI Assistant! 🧬', is_user=False)
        self.add_message('I have full device control capabilities. Try asking me to:\n• "Turn on flashlight"\n• "What\'s my location?"\n• "Take a photo"\n• Or ask me anything!', is_user=False)

        # Initialize Genesis in background
        Clock.schedule_once(lambda dt: self.initialize_genesis(), 0.5)

        # Add debug info if in debug mode
        if DEBUG_MODE:
            self.show_debug_welcome()

        return main_layout

    def show_debug_welcome(self):
        """Show debug mode welcome message"""
        debug_msg = (
            "[color=ffff00]🔧 DEBUG MODE ACTIVE[/color]\n"
            "Developer features enabled:\n"
            "• Real-time performance monitoring\n"
            "• Memory usage tracking\n"
            "• Module status display\n"
            "• Error logging\n"
            "\nThis panel only appears in debug APK builds."
        )
        self.add_message(debug_msg, is_user=False)

    def log_debug(self, message):
        """Log debug message"""
        if DEBUG_MODE:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {message}"
            self.debug_logs.append(log_entry)
            # Keep only last 100 logs
            if len(self.debug_logs) > 100:
                self.debug_logs = self.debug_logs[-100:]
            print(f"[DEBUG] {log_entry}")

    def update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size

    def update_chat_bg(self, instance, value):
        self.chat_bg.pos = instance.pos
        self.chat_bg.size = instance.size

    def initialize_genesis(self):
        """Initialize Genesis core in background"""
        def init_thread():
            try:
                self.log_debug("Starting Genesis initialization")
                self.update_status('[color=ffff00]● INITIALIZING[/color]')

                # Initialize acceleration manager
                self.log_debug("Initializing acceleration manager")
                self.accel_manager = get_accel_manager()

                self.log_debug("Running acceleration detection and benchmark")
                accel_profile = self.accel_manager.detect_and_benchmark()

                if accel_profile and accel_profile.ranked:
                    self.current_accel_mode = accel_profile.ranked[0]
                    self.update_accel_indicator(self.current_accel_mode)
                    self.log_debug(f"Acceleration mode: {self.current_accel_mode.upper()}")

                # Initialize Genesis core
                self.log_debug("Initializing Genesis core")
                self.genesis_core = GenesisCore()
                self.update_status('[color=00ff00]● READY[/color]')
                self.log_debug("Genesis core initialized successfully")

                # Report acceleration status
                accel_msg = self.get_accel_message()
                self.add_message(f'Genesis initialized successfully! {accel_msg}', is_user=False)
            except Exception as e:
                self.log_debug(f"ERROR: {str(e)}")
                self.update_status('[color=ff0000]● ERROR[/color]')
                self.add_message(f'Error initializing Genesis: {str(e)}', is_user=False)

        threading.Thread(target=init_thread, daemon=True).start()

    def get_accel_message(self):
        """Get friendly acceleration status message"""
        mode_messages = {
            'npu': '🚀 NPU Acceleration Active (10x power efficiency)',
            'gpu': '⚡ GPU Acceleration Active (3x faster)',
            'cpu': '🖥️ CPU Mode (Standard performance)'
        }
        return mode_messages.get(self.current_accel_mode, 'Running on CPU')

    @mainthread
    def update_status(self, status_text):
        """Update status indicator"""
        self.status_label.text = status_text

    @mainthread
    def update_accel_indicator(self, mode):
        """Update acceleration mode indicator"""
        mode_colors = {
            'npu': 'ff00ff',  # Magenta for NPU
            'gpu': '00ffff',  # Cyan for GPU
            'cpu': '666666'   # Gray for CPU
        }
        mode_labels = {
            'npu': 'NPU ⚡',
            'gpu': 'GPU ⚡',
            'cpu': 'CPU'
        }
        color = mode_colors.get(mode, '666666')
        label = mode_labels.get(mode, 'CPU')
        self.accel_label.text = f'[color={color}]{label}[/color]'

    @mainthread
    def add_message(self, text, is_user=True):
        """Add message to chat"""
        message = ChatMessage(text, is_user=is_user)
        self.chat_layout.add_widget(message)
        # Auto-scroll to bottom
        Clock.schedule_once(lambda dt: setattr(self.chat_scroll, 'scroll_y', 0), 0.1)

    def send_message(self, instance=None):
        """Send message to Genesis"""
        user_input = self.input_field.text.strip()
        if not user_input:
            return

        # Clear input
        self.input_field.text = ''

        # Add user message
        self.add_message(user_input, is_user=True)

        # Check for debug commands
        if DEBUG_MODE and user_input.startswith('#debug'):
            self.handle_debug_command(user_input)
            return

        # Process in background thread
        def process_thread():
            try:
                self.log_debug(f"Processing: {user_input[:50]}...")
                self.update_status('[color=ffff00]● THINKING[/color]')

                start_time = datetime.now()

                if self.genesis_core:
                    # Use Genesis core to process
                    response = self.genesis_core.process_input(user_input)
                else:
                    response = "Genesis core is still initializing. Please wait a moment..."

                elapsed = (datetime.now() - start_time).total_seconds()
                self.log_debug(f"Response generated in {elapsed:.2f}s")

                self.update_status('[color=00ff00]● READY[/color]')
                self.add_message(response, is_user=False)
            except Exception as e:
                self.log_debug(f"ERROR in send_message: {str(e)}")
                self.update_status('[color=ff0000]● ERROR[/color]')
                self.add_message(f'Error: {str(e)}', is_user=False)

        threading.Thread(target=process_thread, daemon=True).start()

    def handle_debug_command(self, command):
        """Handle debug commands"""
        if command == '#debug logs':
            # Show recent debug logs
            if self.debug_logs:
                logs = '\n'.join(self.debug_logs[-20:])  # Last 20 logs
                self.add_message(f'[color=ffff00]Recent Debug Logs:[/color]\n{logs}', is_user=False)
            else:
                self.add_message('No debug logs yet.', is_user=False)

        elif command == '#debug status':
            # Show detailed status
            status_info = self.get_debug_status()
            self.add_message(status_info, is_user=False)

        elif command == '#debug memory':
            # Show memory info
            if PSUTIL_AVAILABLE:
                process = psutil.Process()
                mem = process.memory_info()
                mem_percent = process.memory_percent()
                info = (
                    f"[color=00ff00]Memory Usage:[/color]\n"
                    f"RSS: {mem.rss / 1024 / 1024:.1f} MB\n"
                    f"VMS: {mem.vms / 1024 / 1024:.1f} MB\n"
                    f"Percent: {mem_percent:.1f}%"
                )
                self.add_message(info, is_user=False)
            else:
                self.add_message('psutil not available', is_user=False)

        elif command == '#debug help':
            help_text = (
                "[color=ffff00]Debug Commands:[/color]\n"
                "#debug logs - Show recent debug logs\n"
                "#debug status - Show detailed status\n"
                "#debug memory - Show memory usage\n"
                "#debug help - Show this help"
            )
            self.add_message(help_text, is_user=False)

        else:
            self.add_message('Unknown debug command. Type #debug help', is_user=False)

    def get_debug_status(self):
        """Get detailed debug status"""
        status_lines = ["[color=ffff00]System Status:[/color]"]

        # Python version
        status_lines.append(f"Python: {sys.version.split()[0]}")

        # Device info
        status_lines.append(f"Platform: {platform.system()} {platform.release()}")

        # Kivy version
        from kivy import __version__ as kivy_version
        status_lines.append(f"Kivy: {kivy_version}")

        # Genesis modules
        if self.genesis_core:
            status_lines.append("Genesis Core: ✓ Loaded")
        else:
            status_lines.append("Genesis Core: ✗ Not loaded")

        if self.accel_manager:
            status_lines.append(f"Acceleration: ✓ {self.current_accel_mode.upper()}")
        else:
            status_lines.append("Acceleration: ✗ Not initialized")

        # Thread info
        status_lines.append(f"Active Threads: {threading.active_count()}")

        # Memory (if available)
        if PSUTIL_AVAILABLE:
            process = psutil.Process()
            mem_mb = process.memory_info().rss / 1024 / 1024
            status_lines.append(f"Memory: {mem_mb:.1f} MB")

        return '\n'.join(status_lines)

    def quick_action(self, action):
        """Handle quick action buttons"""
        self.log_debug(f"Quick action: {action}")

        if action == 'Accel':
            # Show acceleration status
            if self.accel_manager:
                profile = self.accel_manager.detect_and_benchmark()
                if profile and profile.ranked:
                    modes = ', '.join(profile.ranked)
                    self.add_message(f'Available acceleration: {modes}\nCurrent: {self.current_accel_mode.upper()}', is_user=False)
                else:
                    self.add_message('Acceleration detection in progress...', is_user=False)
            else:
                self.add_message('Acceleration manager not initialized', is_user=False)
            return

        action_map = {
            'Location': 'What is my current location?',
            'Camera': 'Take a photo',
            'Light': 'Toggle flashlight'
        }

        if action in action_map:
            self.input_field.text = action_map[action]
            self.send_message()

    def on_pause(self):
        """Handle app pause (Android)"""
        return True

    def on_resume(self):
        """Handle app resume (Android)"""
        pass


if __name__ == '__main__':
    # Ensure data directories exist
    data_dir = Path(__file__).parent / 'data'
    data_dir.mkdir(exist_ok=True)
    (data_dir / 'memory').mkdir(exist_ok=True)
    (data_dir / 'media').mkdir(exist_ok=True)

    # Run the app
    GenesisApp().run()
