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

# Add Genesis modules to path
sys.path.insert(0, str(Path(__file__).parent))

# Import Genesis core
from genesis import Genesis as GenesisCore
from device_manager import get_device_manager
from accel_manager import AccelManager, get_accel_manager


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


class GenesisApp(App):
    """Main Genesis Android Application"""

    def build(self):
        """Build the app UI"""
        self.title = 'Genesis AI Assistant'

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

        return main_layout

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
                self.update_status('[color=ffff00]● INITIALIZING[/color]')

                # Initialize acceleration manager
                self.accel_manager = get_accel_manager()
                accel_profile = self.accel_manager.detect_and_benchmark()

                if accel_profile and accel_profile.ranked:
                    self.current_accel_mode = accel_profile.ranked[0]
                    self.update_accel_indicator(self.current_accel_mode)

                # Initialize Genesis core
                self.genesis_core = GenesisCore()
                self.update_status('[color=00ff00]● READY[/color]')

                # Report acceleration status
                accel_msg = self.get_accel_message()
                self.add_message(f'Genesis initialized successfully! {accel_msg}', is_user=False)
            except Exception as e:
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

        # Process in background thread
        def process_thread():
            try:
                self.update_status('[color=ffff00]● THINKING[/color]')

                if self.genesis_core:
                    # Use Genesis core to process
                    response = self.genesis_core.process_input(user_input)
                else:
                    response = "Genesis core is still initializing. Please wait a moment..."

                self.update_status('[color=00ff00]● READY[/color]')
                self.add_message(response, is_user=False)
            except Exception as e:
                self.update_status('[color=ff0000]● ERROR[/color]')
                self.add_message(f'Error: {str(e)}', is_user=False)

        threading.Thread(target=process_thread, daemon=True).start()

    def quick_action(self, action):
        """Handle quick action buttons"""
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
