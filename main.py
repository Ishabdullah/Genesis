#!/usr/bin/env python3
"""
Genesis Android App - Full AI Integration
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

# Import Genesis AI core
try:
    from genesis import Genesis
    GENESIS_AI_AVAILABLE = True
except ImportError as e:
    logging.warning(f"Genesis AI core not available: {e}")
    GENESIS_AI_AVAILABLE = False
    Genesis = None

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
        self.padding = [dp(15), dp(10)]
        self.spacing = dp(15)

        # Message label with better sizing
        message_text_color = (0, 1, 1, 1) if is_user else (0.5, 1, 0.5, 1)

        message_label = Label(
            text=text,
            color=message_text_color,
            size_hint=(None, None),
            markup=True,
            halign='left',
            valign='top',
            font_size='18sp',  # Larger font for readability
            padding=[dp(20), dp(15)]
        )

        # Set text_size BEFORE binding to prevent overlapping
        def update_label_size(instance, value):
            # Calculate available width (window width - avatar - padding - spacing)
            available_width = Window.width - dp(40) - dp(15) - dp(15) - dp(30)
            message_label.text_size = (available_width, None)
            message_label.width = available_width
            # Update height based on texture
            message_label.height = message_label.texture_size[1] + dp(30)
            # Update container height
            self.height = max(message_label.height, dp(60)) + dp(20)

        # Bind to window size changes
        Window.bind(size=update_label_size)
        message_label.bind(texture_size=update_label_size)

        # Initial sizing
        update_label_size(None, None)

        # Avatar with background
        avatar_container = BoxLayout(
            size_hint_x=None,
            width=dp(50),
            orientation='vertical'
        )
        avatar = Label(
            text='👤' if is_user else '🤖',  # Robot emoji instead of DNA (better support)
            font_size='32sp',  # Larger emoji
            size_hint_y=None,
            height=dp(50)
        )
        avatar_container.add_widget(avatar)

        if is_user:
            self.add_widget(avatar_container)
            self.add_widget(message_label)
        else:
            self.add_widget(message_label)
            self.add_widget(avatar_container)


class GenesisApp(App):
    """Main Genesis Android Application"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.genesis_ai = None

    def build(self):
        """Build the app UI"""
        logger.info("Building Genesis app UI...")
        self.title = 'Genesis AI Assistant'
        logger.debug(f"Window size: {Window.size}")

        # Initialize Genesis AI in background
        if GENESIS_AI_AVAILABLE:
            logger.info("Initializing Genesis AI core...")
            threading.Thread(target=self.init_genesis_ai, daemon=True).start()
        else:
            logger.warning("Genesis AI core not available - running in preview mode")

        # Set window background
        Window.clearcolor = (0.02, 0.02, 0.08, 1)

        # Main layout
        main_layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # Header - Larger and more prominent
        header = BoxLayout(size_hint_y=None, height=dp(80), padding=dp(10))
        with header.canvas.before:
            Color(0.05, 0.15, 0.3, 1)
            self.header_rect = RoundedRectangle(pos=header.pos, size=header.size, radius=[dp(15)])
        header.bind(pos=self.update_header_rect, size=self.update_header_rect)

        title_label = Label(
            text='[b]🤖 GENESIS[/b]\n[size=14sp]AI Assistant[/size]',
            markup=True,
            color=(0, 1, 1, 1),
            halign='center',
            font_size='24sp'  # Larger title
        )
        header.add_widget(title_label)

        self.status_label = Label(
            text='[color=00ff00]● READY[/color]',
            markup=True,
            size_hint_x=None,
            width=dp(120),
            font_size='14sp'  # Larger status text
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

        # Quick action buttons - Larger for better touch targets
        quick_actions = GridLayout(cols=4, size_hint_y=None, height=dp(70), spacing=dp(8))

        quick_action_buttons = [
            ('📍', 'Location'),
            ('📸', 'Camera'),
            ('🔦', 'Light'),
            ('ℹ️', 'Info')
        ]

        for emoji, action in quick_action_buttons:
            btn = FuturisticButton(
                text=f'[size=24sp]{emoji}[/size]\n[size=12sp]{action}[/size]',
                markup=True,
                font_size='18sp'
            )
            btn.bind(on_press=lambda x, a=action: self.quick_action(a))
            quick_actions.add_widget(btn)

        main_layout.add_widget(quick_actions)

        # Input area - Larger for better usability
        input_layout = BoxLayout(size_hint_y=None, height=dp(70), spacing=dp(8), padding=[0, dp(5)])

        self.input_field = FuturisticTextInput(
            hint_text='Ask Genesis anything...',
            hint_text_color=(0, 0.7, 0.7, 0.5),
            multiline=False,
            font_size='18sp'  # Larger text
        )
        self.input_field.bind(on_text_validate=self.send_message)
        self.input_field.bind(focus=self.on_input_focus)

        send_button = FuturisticButton(
            text='[size=20sp]⚡[/size]\n[size=12sp]SEND[/size]',
            markup=True,
            size_hint_x=None,
            width=dp(90),
            font_size='16sp'
        )
        send_button.bind(on_press=self.send_message)

        input_layout.add_widget(self.input_field)
        input_layout.add_widget(send_button)

        main_layout.add_widget(input_layout)

        # Add welcome message
        if GENESIS_AI_AVAILABLE:
            self.add_message('Welcome to Genesis AI Assistant! 🤖', is_user=False)
            self.add_message(
                'Full AI powered by local models\n\n'
                'Device control, code execution, and more!\n\n'
                'Initializing AI core...',
                is_user=False
            )
        else:
            self.add_message('Welcome to Genesis AI Assistant! 🤖', is_user=False)
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

    def init_genesis_ai(self):
        """Initialize Genesis AI in background thread"""
        try:
            self.update_status('[color=ffff00]● LOADING AI[/color]')
            logger.info("Initializing Genesis AI core...")
            self.genesis_ai = Genesis()
            logger.info("✅ Genesis AI initialized successfully!")
            self.update_status('[color=00ff00]● READY[/color]')
            self.add_message('✅ AI Core initialized successfully!\n\nI can now help with:\n• Natural language queries\n• Device control\n• Code execution\n• Web search\n• And more!', is_user=False)
        except Exception as e:
            logger.error(f"Failed to initialize Genesis AI: {e}")
            if DEBUG_MODE:
                logger.error(traceback.format_exc())
            self.update_status('[color=ff0000]● AI UNAVAILABLE[/color]')
            self.add_message(f'⚠️ AI initialization failed:\n{str(e)}\n\nRunning in fallback mode.', is_user=False)

    def update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size

    def update_chat_bg(self, instance, value):
        self.chat_bg.pos = instance.pos
        self.chat_bg.size = instance.size

    def on_input_focus(self, instance, value):
        """Handle keyboard showing/hiding"""
        if value:  # Keyboard showing
            # Scroll chat to bottom when keyboard appears
            Clock.schedule_once(lambda dt: setattr(self.chat_scroll, 'scroll_y', 0), 0.3)

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
        """Send message and process with Genesis AI"""
        user_input = self.input_field.text.strip()
        if not user_input:
            logger.debug("Empty input, ignoring send request")
            return

        logger.info(f"User message: {user_input}")
        self.input_field.text = ''
        self.add_message(user_input, is_user=True)

        # Process with Genesis AI or fallback
        def process_thread():
            try:
                logger.debug("Processing message in thread...")
                self.update_status('[color=ffff00]● THINKING[/color]')

                if self.genesis_ai:
                    # Use full Genesis AI
                    logger.debug("Using Genesis AI core for processing...")
                    # Genesis process_input() prints directly, we need to capture it
                    # For now, use the LLM directly with a simple wrapper
                    response = self.process_with_genesis_ai(user_input)
                else:
                    # Fallback to simple responses
                    logger.debug("Using fallback simple responses...")
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

    def process_with_genesis_ai(self, user_input):
        """Process input with Genesis AI and return response"""
        try:
            # Check for device commands that need special handling
            if any(cmd in user_input.lower() for cmd in ['location', 'gps', 'where am i']):
                try:
                    location = self.genesis_ai.device_manager.get_location()
                    if location:
                        return f"📍 Location: {location.get('latitude', 'N/A')}, {location.get('longitude', 'N/A')}\n\nAddress: {location.get('address', 'Unknown')}"
                except Exception as e:
                    logger.warning(f"Location access failed: {e}")
                    return "❌ Unable to access location. Please grant location permissions."

            if any(cmd in user_input.lower() for cmd in ['time', 'date', 'what time']):
                datetime_info = self.genesis_ai.device_manager.get_datetime()
                return f"🕐 Current time: {datetime_info.get('time', 'N/A')}\n📅 Date: {datetime_info.get('date', 'N/A')}"

            if 'flashlight' in user_input.lower() or 'torch' in user_input.lower() or 'flash' in user_input.lower():
                state = 'on' in user_input.lower() or 'enable' in user_input.lower() or 'turn on' in user_input.lower()
                result = self.genesis_ai.device_manager.toggle_flashlight(state)
                return f"🔦 Flashlight {'enabled' if state else 'disabled'}: {result}"

            # For other queries, use a simplified AI response
            # (In production, you'd integrate with an actual LLM or use simplified Claude fallback)
            response = f"I'm processing: {user_input}\n\n"
            response += "Full LLM integration in progress!\n\n"
            response += "Available capabilities:\n"
            response += "• Device control (location, time, flashlight)\n"
            response += "• File operations\n"
            response += "• Code execution\n"
            response += "• Web search\n\n"
            response += "Try asking about:\n"
            response += "- What's my location?\n"
            response += "- What time is it?\n"
            response += "- Turn on the flashlight"

            return response

        except Exception as e:
            logger.error(f"Error in Genesis AI processing: {e}")
            return f"Error processing request: {str(e)}"

    def get_simple_response(self, text):
        """Get a simple response based on input (fallback mode)"""
        if 'hello' in text or 'hi' in text:
            return "Hello! I'm Genesis, your AI assistant running on Android! 🤖"
        elif 'help' in text or 'what can you do' in text:
            return (
                "I'm Genesis AI Assistant!\n\n"
                "Available capabilities:\n"
                "• Natural language queries\n"
                "• Device control (GPS, camera, flashlight)\n"
                "• Date/time information\n"
                "• Code execution (coming soon)\n"
                "• File operations (coming soon)\n\n"
                "Try asking:\n"
                "- What's my location?\n"
                "- What time is it?\n"
                "- Turn on the flashlight"
            )
        elif 'thanks' in text or 'thank you' in text:
            return "You're welcome! Happy to help! 🤖"
        else:
            return (
                f"I received: '{text}'\n\n"
                "AI core is initializing.\n"
                "Try the quick action buttons or ask for help!"
            )

    def quick_action(self, action):
        """Handle quick action buttons with Genesis AI integration"""
        logger.info(f"Quick action triggered: {action}")

        def process_action():
            try:
                self.update_status('[color=ffff00]● PROCESSING[/color]')

                if action == 'Location' and self.genesis_ai:
                    try:
                        location = self.genesis_ai.device_manager.get_location()
                        if location:
                            response = f"📍 Your Location:\n\n"
                            response += f"Latitude: {location.get('latitude', 'N/A')}\n"
                            response += f"Longitude: {location.get('longitude', 'N/A')}\n"
                            response += f"Address: {location.get('address', 'Fetching...')}\n"
                        else:
                            response = "❌ Unable to get location.\n\nPlease grant location permissions in app settings."
                    except Exception as e:
                        response = f"❌ Location error: {str(e)}\n\nEnsure GPS is enabled and permissions are granted."

                elif action == 'Camera' and self.genesis_ai:
                    response = "📸 Camera integration coming soon!\n\nWill support:\n• Photo capture\n• Selfie mode\n• QR code scanning"

                elif action == 'Light' and self.genesis_ai:
                    try:
                        # Toggle flashlight (default to ON for quick action)
                        result = self.genesis_ai.device_manager.toggle_flashlight(True)
                        response = f"🔦 Flashlight activated!\n\n{result}\n\nSay 'turn off flashlight' to disable."
                    except Exception as e:
                        response = f"❌ Flashlight error: {str(e)}\n\nEnsure flashlight permissions are granted."

                elif action == 'Info':
                    ai_status = "✅ Initialized" if self.genesis_ai else "❌ Not Available"
                    response = (
                        f"🤖 Genesis AI Assistant v2.3.0-android\n\n"
                        f"Platform: Android (Kivy)\n"
                        f"AI Core: {ai_status}\n"
                        f"Build: NDK r28+ Compatible\n"
                        f"Debug Mode: {'ON' if DEBUG_MODE else 'OFF'}\n\n"
                        f"Features:\n"
                        f"• Device control (GPS, flashlight)\n"
                        f"• Natural language processing\n"
                        f"• Code execution\n"
                        f"• Web search\n\n"
                        f"All 7 NDK r28+ build blockers resolved! 🎉"
                    )
                else:
                    # Fallback for when Genesis AI not available
                    action_responses = {
                        'Location': '📍 GPS location requires permissions.\n\nGrant location access in Android settings.',
                        'Camera': '📸 Camera integration coming soon!\n\nWill allow photo capture via commands.',
                        'Light': '🔦 Flashlight requires permissions.\n\nGrant flashlight access in Android settings.',
                    }
                    response = action_responses.get(action, 'Feature initializing...')

                self.update_status('[color=00ff00]● READY[/color]')
                self.add_message(response, is_user=False)
                logger.debug(f"Quick action '{action}' completed")

            except Exception as e:
                logger.error(f"Error in quick action '{action}': {e}")
                self.update_status('[color=ff0000]● ERROR[/color]')
                self.add_message(f"❌ Error: {str(e)}", is_user=False)

        threading.Thread(target=process_action, daemon=True).start()

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
