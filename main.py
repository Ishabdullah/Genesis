#!/usr/bin/env python3
"""
Genesis Android App - Simplified Entry Point
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
import logging
import traceback
from pathlib import Path
from datetime import datetime

# Detect if this is a debug build
DEBUG_MODE = os.environ.get('GENESIS_DEBUG', '1') == '1'

# Configure comprehensive logging for debug builds
if DEBUG_MODE:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.StreamHandler(sys.stderr)
        ]
    )
    logging.info("=" * 60)
    logging.info("GENESIS AI ASSISTANT - DEBUG MODE ENABLED")
    logging.info(f"Python version: {sys.version}")
    logging.info(f"Platform: {sys.platform}")
    logging.info(f"Working directory: {os.getcwd()}")
    logging.info("=" * 60)
else:
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

logger = logging.getLogger(__name__)


class FuturisticTextInput(TextInput):
    """Custom futuristic text input with neon styling"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.05, 0.05, 0.15, 1)
        self.foreground_color = (0, 1, 1, 1)  # Cyan
        self.cursor_color = (0, 1, 1, 1)

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
        self.bold = True

        with self.canvas.before:
            Color(0.1, 0.5, 0.8, 0.8)  # Neon blue
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(15)])

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size


class ChatMessage(BoxLayout):
    """Individual chat message widget with styling"""

    def __init__(self, text, is_user=True, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'horizontal'
        self.size_hint_y = None
        self.padding = [dp(10), dp(5)]
        self.spacing = dp(10)

        # Message label
        message_text_color = (0, 1, 1, 1) if is_user else (0.5, 1, 0.5, 1)

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

        # Avatar
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
        logger.info("Building Genesis app UI...")
        self.title = 'Genesis AI Assistant'
        logger.debug(f"Window size: {Window.size}")

        # Set window background
        Window.clearcolor = (0.02, 0.02, 0.08, 1)

        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # Header
        header = BoxLayout(size_hint_y=None, height=dp(70), padding=dp(5))
        with header.canvas.before:
            Color(0.05, 0.15, 0.3, 1)
            self.header_rect = RoundedRectangle(pos=header.pos, size=header.size, radius=[dp(15)])
        header.bind(pos=self.update_header_rect, size=self.update_header_rect)

        title_label = Label(
            text='[b]🧬 GENESIS[/b]\n[size=12sp]AI Assistant[/size]',
            markup=True,
            color=(0, 1, 1, 1),
            halign='center'
        )
        header.add_widget(title_label)

        self.status_label = Label(
            text='[color=00ff00]● READY[/color]',
            markup=True,
            size_hint_x=None,
            width=dp(100),
            font_size='12sp'
        )
        header.add_widget(self.status_label)

        main_layout.add_widget(header)

        # Chat history
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
            ('ℹ️', 'Info')
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

        # Add welcome message
        self.add_message('Welcome to Genesis AI Assistant! 🧬', is_user=False)
        self.add_message(
            'This is the Android preview version.\n\n'
            'Full AI capabilities will be added soon!\n\n'
            'Try the quick action buttons below!',
            is_user=False
        )

        logger.info("✅ Genesis app UI build complete!")
        if DEBUG_MODE:
            logger.debug("Debug mode active - comprehensive logging enabled")

        return main_layout

    def update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size

    def update_chat_bg(self, instance, value):
        self.chat_bg.pos = instance.pos
        self.chat_bg.size = instance.size

    @mainthread
    def update_status(self, status_text):
        """Update status indicator"""
        self.status_label.text = status_text

    @mainthread
    def add_message(self, text, is_user=True):
        """Add message to chat"""
        message = ChatMessage(text, is_user=is_user)
        self.chat_layout.add_widget(message)
        Clock.schedule_once(lambda dt: setattr(self.chat_scroll, 'scroll_y', 0), 0.1)

    def send_message(self, instance=None):
        """Send message"""
        user_input = self.input_field.text.strip()
        if not user_input:
            logger.debug("Empty input, ignoring send request")
            return

        logger.info(f"User message: {user_input}")
        self.input_field.text = ''
        self.add_message(user_input, is_user=True)

        # Simple echo response for now
        def process_thread():
            try:
                logger.debug("Processing message in thread...")
                self.update_status('[color=ffff00]● PROCESSING[/color]')

                # Simple responses
                response = self.get_simple_response(user_input.lower())
                logger.debug(f"Generated response: {response[:50]}...")

                self.update_status('[color=00ff00]● READY[/color]')
                self.add_message(response, is_user=False)
                logger.info("✅ Message processed successfully")
            except Exception as e:
                logger.error(f"❌ Error processing message: {str(e)}")
                if DEBUG_MODE:
                    logger.error("Full stack trace:")
                    logger.error(traceback.format_exc())
                self.update_status('[color=ff0000]● ERROR[/color]')
                error_msg = f'Error: {str(e)}'
                if DEBUG_MODE:
                    error_msg += f'\n\nStack trace:\n{traceback.format_exc()}'
                self.add_message(error_msg, is_user=False)

        threading.Thread(target=process_thread, daemon=True).start()

    def get_simple_response(self, text):
        """Get a simple response based on input"""
        if 'hello' in text or 'hi' in text:
            return "Hello! I'm Genesis, your AI assistant. Full capabilities coming soon!"
        elif 'help' in text or 'what can you do' in text:
            return (
                "I'm Genesis AI Assistant!\n\n"
                "Currently in preview mode. Coming soon:\n"
                "• Natural language processing\n"
                "• Device control (GPS, camera, flashlight)\n"
                "• Code execution\n"
                "• File operations\n"
                "• And much more!"
            )
        elif 'thanks' in text or 'thank you' in text:
            return "You're welcome! Happy to help! 🧬"
        else:
            return (
                f"I received your message: '{text}'\n\n"
                "Full AI capabilities are being integrated.\n"
                "This is a preview version showing the UI!"
            )

    def quick_action(self, action):
        """Handle quick action buttons"""
        logger.info(f"Quick action triggered: {action}")

        action_responses = {
            'Location': 'GPS location feature coming soon!\n\nWill show your current coordinates and address.',
            'Camera': 'Camera integration coming soon!\n\nWill allow photo capture via voice commands.',
            'Light': 'Flashlight control coming soon!\n\nWill toggle your device flashlight on/off.',
            'Info': (
                'Genesis AI Assistant v0.1.0-alpha\n\n'
                'Platform: Android\n'
                'UI: Futuristic Neon Theme\n'
                'Status: Early Development\n'
                f'Debug Mode: {"ON" if DEBUG_MODE else "OFF"}\n\n'
                'Build system optimization in progress!'
            )
        }

        response = action_responses.get(action, 'Feature coming soon!')
        self.add_message(response, is_user=False)
        logger.debug(f"Quick action '{action}' completed")

    def on_pause(self):
        """Handle app pause (Android)"""
        logger.info("🔄 App pausing (backgrounded)")
        return True

    def on_resume(self):
        """Handle app resume (Android)"""
        logger.info("🔄 App resuming (foregrounded)")
        pass


if __name__ == '__main__':
    try:
        logger.info("=" * 60)
        logger.info("Starting Genesis AI Assistant...")
        logger.info(f"Version: 0.1.0-alpha")
        logger.info(f"Debug mode: {DEBUG_MODE}")
        logger.info("=" * 60)
        GenesisApp().run()
    except Exception as e:
        logger.critical(f"❌ FATAL ERROR: App crashed during startup!")
        logger.critical(f"Error: {str(e)}")
        logger.critical("Full stack trace:")
        logger.critical(traceback.format_exc())
        raise
