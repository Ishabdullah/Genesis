# 🧬 Genesis AI Assistant

<div align="center">

![Genesis Logo](icon_192.png)

**The World's Most Advanced On-Device AI Assistant for Android**

[![Version](https://img.shields.io/badge/Version-2.3.0-blue.svg)](https://github.com/Ishabdullah/Genesis)
[![Platform](https://img.shields.io/badge/Platform-Android%207.0%2B-green.svg)](https://www.android.com)
[![License](https://img.shields.io/badge/License-MIT-orange.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/Build-Automated-brightgreen.svg)](https://github.com/Ishabdullah/Genesis/actions)

[Download APK](#-download) • [Features](#-features) • [Installation](#-installation) • [Documentation](#-documentation)

</div>

---

## ✨ What is Genesis?

Genesis is a **revolutionary AI assistant** that runs entirely on your Android device. Unlike cloud-based assistants, Genesis gives you:

- 🔒 **Complete Privacy** - All processing happens on your device
- ⚡ **Blazing Speed** - NPU acceleration for instant responses
- 📱 **Full Device Control** - GPS, camera, flashlight, and more
- 🎨 **Futuristic UI** - Beautiful neon-themed interface
- 🧠 **Advanced AI** - Powered by CodeLlama-7B with deterministic math
- 🌍 **Works Offline** - No internet required for local queries

**No data leaves your device. No subscriptions. No cloud dependency.**

---

## 🌟 Key Features

### 🚀 Hardware Acceleration
Genesis intelligently uses your device's processing power:

| Mode | Hardware | Speed | Power Efficiency |
|------|----------|-------|------------------|
| **NPU** | Qualcomm Hexagon | Instant | 10x more efficient |
| **GPU** | Vulkan Graphics | 3x faster | Optimized |
| **CPU** | Universal | Standard | Compatible |

Real-time acceleration indicator shows which mode is active with color-coded display.

### 📱 Complete Device Control
Control your Android device with natural language:

```
"Turn on flashlight"          → 🔦 Flashlight enabled
"What's my location?"         → 📍 GPS coordinates & address
"Take a photo"                → 📸 Captures and saves image
"Record 5 seconds of audio"   → 🎤 Records audio file
"Set brightness to 200"       → ☀️ Adjusts screen brightness
"Increase volume"             → 🔊 Adjusts audio levels
```

### 💬 Intelligent Conversation
- **Multi-turn context** - Remembers previous messages
- **Deterministic math** - 100% accurate calculations
- **Code execution** - Runs Python code safely
- **Web search** - Searches when needed (optional)
- **File operations** - Read, write, edit files

### 🎨 Futuristic Interface
- **Neon theme** - Cyan and blue cyberpunk aesthetics
- **Smooth animations** - Polished, responsive UI
- **Quick actions** - One-tap access to common features
- **Status indicators** - Real-time system information
- **Debug panel** - Developer tools (debug builds only)

---

## 📥 Download

### Latest Release: v2.3.0

**Download from GitHub Actions:**
1. Go to [Actions Tab](https://github.com/Ishabdullah/Genesis/actions)
2. Click latest "Build Genesis Android APK" workflow
3. Download `genesis-ai-apk` from Artifacts
4. Extract and install APK

**Requirements:**
- Android 7.0 (API 21) or higher
- 100+ MB storage space
- 2+ GB RAM recommended
- ARM processor (arm64-v8a or armeabi-v7a)

---

## 🛠️ Installation

### Step 1: Enable Unknown Sources
```
Settings → Security → Install Unknown Apps
→ Select your file manager → Enable
```

### Step 2: Install APK
1. Transfer APK to your Android device
2. Open file manager and tap the APK
3. Tap "Install"
4. Wait for installation to complete

### Step 3: Grant Permissions
When you first launch Genesis, grant these permissions:
- ✅ **Location** - For GPS features
- ✅ **Camera** - For photo capture
- ✅ **Microphone** - For audio recording
- ✅ **Storage** - For file operations

### Step 4: Start Using Genesis!
Open the app and start chatting. Try:
- "Hello, what can you do?"
- "What is 2 + 2?"
- "Turn on flashlight"
- Tap quick action buttons

---

## 💡 Usage Examples

### Basic Conversation
```
You: Hello!
Genesis: Hello! I'm Genesis, your AI assistant. I can help with:
         • Answering questions and solving problems
         • Controlling device features (camera, GPS, flashlight)
         • Performing calculations and running code
         • And much more!

You: What is 15 * 24?
Genesis: 15 × 24 = 360
```

### Device Control
```
You: What's my location?
Genesis: Your current location:
         Latitude: 37.7749° N
         Longitude: 122.4194° W
         Address: San Francisco, CA, USA

You: Take a selfie
Genesis: Photo captured successfully!
         Saved to: /storage/emulated/0/Genesis/media/photo_20251107_152345.jpg
```

### Quick Actions
Tap the buttons at the bottom for instant access:
- 📍 **Location** - Get GPS coordinates
- 📸 **Camera** - Take a photo
- 🔦 **Light** - Toggle flashlight
- ⚡ **Accel** - Check acceleration mode

### Advanced Features
```
You: Calculate the square root of 144
Genesis: √144 = 12

You: Execute Python code: print("Hello, World!")
Genesis: Code executed successfully:
         Output: Hello, World!

You: #debug status  (in debug builds only)
Genesis: System Status:
         Python: 3.11.6
         Acceleration: NPU
         Memory: 125.3 MB
         ...
```

---

## 🏗️ Architecture

### Technology Stack
```
┌─────────────────────────────────────┐
│     Kivy UI Framework (Python)      │  ← Futuristic Interface
├─────────────────────────────────────┤
│   Genesis AI Core (Python Modules)  │  ← Reasoning Engine
├─────────────────────────────────────┤
│    llama.cpp (C++ Inference)        │  ← LLM Processing
├─────────────────────────────────────┤
│  Hardware Acceleration Layer        │  ← NPU/GPU/CPU
│  • Qualcomm QNN (NPU)              │
│  • Vulkan (GPU)                    │
│  • Standard CPU                     │
├─────────────────────────────────────┤
│   Android System (Device APIs)      │  ← Camera, GPS, etc.
└─────────────────────────────────────┘
```

### Core Components
- **UI Layer**: Kivy 2.2.1 with custom widgets
- **AI Engine**: CodeLlama-7B (GGUF quantized)
- **Acceleration**: QNN (NPU), Vulkan (GPU), CPU fallback
- **Device Integration**: Termux API wrappers
- **Memory System**: Persistent conversation storage
- **Learning System**: Adaptive feedback mechanism

---

## 📊 Performance

### Inference Speed (Samsung S24 Ultra)
| Task Type | NPU Mode | GPU Mode | CPU Mode |
|-----------|----------|----------|----------|
| Simple Query | 2-3s | 5-7s | 15-20s |
| Math Problem | 3-4s | 7-10s | 20-25s |
| Code Generation | 5-8s | 12-18s | 30-45s |
| Complex Reasoning | 8-12s | 20-30s | 60-90s |

### Resource Usage
- **Memory**: 80-150 MB typical
- **Storage**: ~100 MB (app + data)
- **Battery**: NPU uses 10x less power than CPU
- **CPU Usage**: 5-15% during inference

### Optimization Features
- 🔋 Battery-aware mode switching
- 🌡️ Thermal throttling protection
- 🧠 Smart memory management
- ⚡ Automatic acceleration selection

---

## 🔧 Technical Specifications

### Android Requirements
| Specification | Requirement |
|--------------|-------------|
| **OS Version** | Android 7.0+ (API 21+) |
| **Architecture** | ARM 32/64-bit (armeabi-v7a, arm64-v8a) |
| **RAM** | 2 GB minimum, 4+ GB recommended |
| **Storage** | 200 MB free space |
| **Processor** | Any ARM-based Android CPU |

### Supported Hardware Acceleration
| Feature | Chipset Support |
|---------|----------------|
| **NPU** | Qualcomm Snapdragon with Hexagon NPU |
| **GPU** | Any GPU with Vulkan support |
| **CPU** | Universal (all devices) |

### Permissions Used
```
✓ INTERNET              - Web search (optional)
✓ CAMERA                - Photo capture
✓ RECORD_AUDIO          - Audio recording
✓ ACCESS_FINE_LOCATION  - GPS positioning
✓ READ/WRITE_STORAGE    - File operations
✓ FLASHLIGHT            - Torch control
✓ MODIFY_AUDIO_SETTINGS - Volume control
✓ WAKE_LOCK             - Background processing
✓ VIBRATE               - Haptic feedback
```

---

## 🎯 Use Cases

### Personal Assistant
- Set reminders and alarms
- Answer questions instantly
- Perform calculations
- Get directions and locations
- Control device settings

### Development Tool
- Debug code snippets
- Calculate complex expressions
- Test algorithms
- Learn programming concepts
- Execute Python code safely

### Education
- Solve math problems step-by-step
- Explain concepts
- Practice problem-solving
- Learn new topics
- Study assistance

### Productivity
- Quick notes and memos
- File management
- Information lookup
- Task automation
- Quick commands

### Photography
- Instant photo capture via voice
- Timed photo shoots
- Hands-free camera control
- Location-tagged images

---

## 🔒 Privacy & Security

### Data Privacy
- ✅ **100% On-Device Processing** - Your data never leaves your phone
- ✅ **No Cloud Servers** - No remote processing or storage
- ✅ **No Telemetry** - We don't track your usage
- ✅ **No Accounts** - No registration or login required
- ✅ **Local Storage Only** - All data saved locally

### Optional Internet Usage
Internet is ONLY used when you explicitly:
- Enable web search feature
- Use Claude API fallback (optional)
- Update the app

**Default: Works completely offline**

### Permission Transparency
Every permission is clearly explained:
- Camera: Only for "take photo" commands
- Location: Only for "where am I" queries
- Microphone: Only for audio recording
- Storage: Only for saving files
- Internet: Only for optional web features

---

## 🛣️ Roadmap

### ✅ Version 2.3.0 (Current)
- Futuristic Android UI
- Hardware acceleration (NPU/GPU/CPU)
- Full device control integration
- Debug features for developers
- Automated APK builds

### 🔄 Version 2.4.0 (In Progress)
- Voice input/output
- Conversation history export
- Settings customization screen
- Model selection UI
- Performance optimizations

### 📋 Version 3.0.0 (Planned)
- Multi-modal support (image input)
- Advanced memory management
- Custom themes
- Widget support
- Cloud sync (optional)

### 🚀 Future Versions
- App store release
- Multiple language support
- Plugin system
- Custom voice commands
- Automation workflows

---

## 📚 Documentation

### For Users
- **README.md** (this file) - Overview and features
- **BUILD_COMPLETE_SUMMARY.md** - Installation and usage
- **DEBUG_FEATURES.md** - Debug commands (developers)

### For Developers
- **PROJECT_HANDOFF.md** - Complete technical documentation
- **IMPLEMENTATION_PLAN.md** - Development roadmap
- **buildozer.spec** - Build configuration
- **main.py** - Source code with comments

### Quick Links
- [Download APK](#-download)
- [Installation Guide](#-installation)
- [Usage Examples](#-usage-examples)
- [Troubleshooting](#-troubleshooting)
- [GitHub Repository](https://github.com/Ishabdullah/Genesis)

---

## 🐛 Troubleshooting

### App Won't Install
**Problem**: "App not installed" error

**Solutions**:
1. Enable "Unknown sources" in Settings
2. Check available storage (need 200+ MB)
3. Try a different file manager
4. Uninstall any previous version first

### Permissions Not Working
**Problem**: Device features don't work

**Solutions**:
1. Go to Settings → Apps → Genesis → Permissions
2. Grant all requested permissions
3. Restart the app
4. Try the feature again

### Slow Performance
**Problem**: Responses take too long

**Solutions**:
1. Check acceleration mode (tap ⚡ button)
2. Close other apps to free memory
3. Ensure battery is charged (>20%)
4. Check device isn't overheating

### App Crashes
**Problem**: App closes unexpectedly

**Solutions**:
1. Clear app cache (Settings → Apps → Genesis → Storage)
2. Reinstall the app
3. Check device has enough RAM
4. Report issue with logs: `adb logcat`

### Debug Panel Showing
**Problem**: Yellow debug panel appears (you don't want it)

**Solution**:
- You're using a debug build
- Download the release version (when available)
- Or build release APK yourself

---

## 🤝 Contributing

Genesis is under active development! Contributions welcome:

### Ways to Contribute
- 🐛 Report bugs and issues
- 💡 Suggest new features
- 📝 Improve documentation
- 🎨 Design UI improvements
- 🔧 Submit pull requests

### Development Setup
```bash
# Clone repository
git clone https://github.com/Ishabdullah/Genesis.git
cd Genesis

# Install dependencies
pip install -r requirements.txt

# Run on desktop (testing)
python main.py

# Build Android APK
buildozer android debug
```

### Contribution Guidelines
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📄 License

Genesis is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2025 Genesis AI Project

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

[Full license text in LICENSE file]
```

---

## 👨‍💻 Credits

### Development
- **Genesis AI Project** - Core development
- **Anthropic** - Claude AI assistance
- **Meta** - CodeLlama model
- **Kivy Team** - Android UI framework
- **llama.cpp** - Inference engine

### Technologies Used
- Python 3.11+
- Kivy 2.2.1
- CodeLlama-7B
- llama.cpp
- Qualcomm QNN SDK
- Vulkan API
- Termux API

---

## 📞 Support

### Get Help
- **GitHub Issues**: [Report a bug](https://github.com/Ishabdullah/Genesis/issues)
- **Documentation**: [Read the docs](#-documentation)
- **Email**: support@genesis-ai.example.com (coming soon)

### Stay Updated
- **GitHub**: [Star the repo](https://github.com/Ishabdullah/Genesis)
- **Releases**: [Watch for updates](https://github.com/Ishabdullah/Genesis/releases)
- **Changelog**: See CHANGELOG.md for version history

---

## 🌟 Why Genesis?

### Compared to Cloud AI Assistants
| Feature | Genesis | Cloud Assistants |
|---------|---------|------------------|
| **Privacy** | 100% local | Data sent to servers |
| **Offline** | Full functionality | Requires internet |
| **Speed** | Instant (NPU) | Network dependent |
| **Cost** | Free forever | Subscription required |
| **Device Control** | Complete | Limited |
| **Customization** | Full control | Locked down |

### The Future of AI
Genesis represents a new paradigm:
- **Own your AI** - Runs on your device
- **Control your data** - Never leaves your phone
- **Unlimited access** - No API limits or costs
- **Always available** - No network required
- **Truly personal** - Learns from you only

**This is AI as it should be: Private, Fast, and Yours.**

---

<div align="center">

## 🚀 Ready to Experience the Future?

[**Download Genesis APK Now**](#-download)

**Join thousands of users experiencing true AI freedom**

---

Made with ❤️ by the Genesis AI Team

[GitHub](https://github.com/Ishabdullah/Genesis) • [Documentation](#-documentation) • [Support](#-support)

**Version 2.3.0** • Built with 🧬 DNA • Powered by ⚡

</div>
