# 🧬 Genesis AI Assistant - Android App

<div align="center">

![Genesis Logo](icon_192.png)

**Privacy-First AI Assistant for Android**

[![Version](https://img.shields.io/badge/Version-2.3.0--preview-blue.svg)](https://github.com/Ishabdullah/Genesis)
[![Platform](https://img.shields.io/badge/Platform-Android%207.0%2B-green.svg)](https://www.android.com)
[![Build](https://img.shields.io/badge/Build-Automated-brightgreen.svg)](https://github.com/Ishabdullah/Genesis/actions)
[![Branch](https://img.shields.io/badge/Branch-claude%2Fgenesis--android--production-orange.svg)](#)

[Download APK](#-download-apk) • [Features](#-features) • [Installation](#-installation) • [Roadmap](#-roadmap)

</div>

---

## 📱 About This Branch

This is the **Android App** branch of Genesis - transforming the powerful Termux-based AI workstation into a native Android application with a futuristic UI.

**Branch:** `claude/genesis-android-production-011CUsnEhM8wFNiRFhG1A4SC`
**Status:** 🔄 In Development - Preview Version
**Stage:** Phase 3 Complete - UI Shell Ready

---

## ✨ What's New in Android Version

### 🎨 Futuristic UI
- **Neon Theme** - Cyberpunk-inspired cyan/blue color scheme
- **Custom Widgets** - Styled buttons, inputs, and message bubbles
- **Smooth Animations** - Polished, responsive interactions
- **DNA Helix Branding** - Unique app icon and theme

### 📱 Android-Native Features
- **Material Design** - Modern Android UI patterns
- **Gesture Support** - Touch-optimized interface
- **Dark Theme** - Easy on the eyes
- **Portrait/Landscape** - Adaptive layout

### 🚀 Preview Capabilities (Current)
- ✅ Chat interface with message history
- ✅ Futuristic UI with neon styling
- ✅ Quick action buttons
- ✅ Status indicators
- ✅ Simple conversational responses

### 🔄 Coming Soon
- ⏳ Full AI inference (LLM integration)
- ⏳ Device control (GPS, camera, flashlight)
- ⏳ NPU/GPU/CPU acceleration
- ⏳ File operations
- ⏳ Code execution
- ⏳ Web search integration

---

## 📥 Download APK

### Latest Build

**Download from GitHub Actions:**
1. Go to [Actions Tab](https://github.com/Ishabdullah/Genesis/actions)
2. Click latest "Build Genesis Android APK" workflow
3. Download `genesis-ai-apk` from Artifacts (after build completes)
4. Extract ZIP and install APK

**Build Status:** Check [GitHub Actions](https://github.com/Ishabdullah/Genesis/actions) for current build status

**Requirements:**
- Android 7.0+ (API 21+)
- 50+ MB storage
- ARM 32/64-bit processor

---

## 🛠️ Installation

### Step 1: Enable Unknown Sources
```
Settings → Security → Install Unknown Apps
→ Select your file manager → Enable
```

### Step 2: Install APK
1. Download APK from GitHub Actions artifacts
2. Transfer to your Android device
3. Tap the APK file
4. Tap "Install"

### Step 3: Launch & Enjoy
Open Genesis and explore the futuristic UI!

---

## 🎯 Current Features

### ✅ Working Now (Preview v2.3.0)

**UI & Interaction:**
- 💬 Chat interface with scrollable history
- 🎨 Futuristic neon theme (cyan/blue)
- 📝 Message input with validation
- 🔘 Quick action buttons
- 📊 Status indicators
- 🧬 Branded design elements

**Basic Responses:**
- 👋 Greetings and basic conversation
- ℹ️ Help information
- 🔄 Simple echo responses
- 📱 Feature previews

**Quick Actions:**
- 📍 **Location** - Preview of GPS integration
- 📸 **Camera** - Preview of camera control
- 🔦 **Light** - Preview of flashlight toggle
- ℹ️ **Info** - App information display

### 🔄 In Development

**AI Core Integration:**
- 🧠 LLM inference engine
- 💭 Context-aware responses
- 🔍 Smart question understanding
- 📚 Knowledge base

**Device Control:**
- 📍 Real GPS location
- 📸 Camera photo capture
- 🔦 Flashlight on/off
- 🎤 Audio recording
- ☀️ Brightness control
- 🔊 Volume adjustment

**Advanced Features:**
- ⚡ Hardware acceleration (NPU/GPU/CPU)
- 🗂️ File operations
- 💻 Code execution sandbox
- 🌐 Web search
- 🎙️ Voice input/output

---

## 🏗️ Development Status

### Phase Progress

| Phase | Description | Status |
|-------|-------------|--------|
| **Phase 1** | Foundation & Architecture | ✅ Complete |
| **Phase 2** | Hardware Acceleration | ✅ Complete |
| **Phase 3** | Build System & UI | ✅ Complete |
| **Phase 4** | Device Integration | 🔄 Next |
| **Phase 5** | LLM Integration | ⏳ Pending |
| **Phase 6-12** | Advanced Features | ⏳ Pending |

**Overall Progress:** ~25% (Phase 3 of 12)

### What's Done ✅

- [x] Futuristic Android UI built
- [x] GitHub Actions build pipeline
- [x] App icon and branding
- [x] Custom styled widgets
- [x] Chat interface functional
- [x] Quick action buttons
- [x] Status indicators
- [x] Build automation

### What's Next 🔄

- [ ] Integrate LLM inference
- [ ] Add device control APIs
- [ ] Implement hardware acceleration
- [ ] Package AI model
- [ ] Add voice support
- [ ] File operations UI
- [ ] Settings screen
- [ ] Performance optimization

---

## 🎨 Screenshots

### Main Interface
```
┌─────────────────────────────────┐
│  🧬 GENESIS    │ ● READY       │
├─────────────────────────────────┤
│                                  │
│  🧬 Welcome to Genesis!          │
│     This is the Android preview  │
│                                  │
│  👤 Hello!                       │
│                                  │
│  🧬 Hello! I'm Genesis, your     │
│     AI assistant. Full           │
│     capabilities coming soon!    │
│                                  │
├─────────────────────────────────┤
│ 📍   📸   🔦   ℹ️              │
│ Location Camera Light Info      │
├─────────────────────────────────┤
│ Ask Genesis anything...    [⚡]  │
└─────────────────────────────────┘
```

---

## 📊 Technical Details

### Architecture

```
┌─────────────────────────────────┐
│     Kivy UI Framework           │
├─────────────────────────────────┤
│   Genesis Android App (main.py) │
├─────────────────────────────────┤
│         Python 3.11             │
├─────────────────────────────────┤
│     Python-for-Android (p4a)    │
├─────────────────────────────────┤
│      Android System APIs        │
└─────────────────────────────────┘
```

### Technology Stack

**Frontend:**
- Kivy 2.2.1 (UI framework)
- Custom widgets with canvas graphics
- Material-inspired design

**Backend:**
- Python 3.11
- Threading for async operations
- Simple response system (preview)

**Build:**
- Buildozer (APK packaging)
- Python-for-Android (p4a)
- GitHub Actions (CI/CD)

### Dependencies

```
python3
kivy (UI framework)
pillow (image processing)
requests (HTTP client)
certifi (SSL certificates)
urllib3 (HTTP library)
pyjnius (Python-Java bridge)
android (Android APIs)
plyer (cross-platform APIs)
```

---

## 🔧 Building from Source

### Prerequisites
```bash
# Install Buildozer
pip install buildozer cython==0.29.36

# System dependencies (Ubuntu/Debian)
sudo apt-get install -y \
    python3 build-essential git \
    libsdl2-dev libsdl2-image-dev \
    libsdl2-mixer-dev libsdl2-ttf-dev \
    openjdk-17-jdk
```

### Build APK
```bash
# Clone repository
git clone https://github.com/Ishabdullah/Genesis.git
cd Genesis

# Checkout Android branch
git checkout claude/genesis-android-production-011CUsnEhM8wFNiRFhG1A4SC

# Generate icon
python3 create_icon.py

# Build APK
buildozer android debug

# APK will be in bin/
ls -lh bin/*.apk
```

**First build takes 30-60 minutes** (downloads Android SDK/NDK)
**Subsequent builds:** 15-30 minutes (cached)

---

## 🛣️ Roadmap

### v2.3.0-preview (Current) ✅
- Futuristic UI implementation
- Basic chat interface
- Quick action buttons
- App branding and icon
- GitHub Actions build

### v2.4.0 (Next Release)
- LLM integration
- Device control APIs
- Hardware acceleration
- Voice input support
- Settings screen

### v2.5.0
- File operations
- Code execution
- Web search
- Advanced memory
- Performance optimization

### v3.0.0 (Full Release)
- All features complete
- App store ready
- Comprehensive testing
- Documentation complete
- Public release

---

## 📚 Documentation

### For Users
- **README.md** (this file) - Overview and installation
- **BUILD_FIX_SUMMARY.md** - Build troubleshooting
- **BUILD_COMPLETE_SUMMARY.md** - Build guide

### For Developers
- **IMPLEMENTATION_PLAN.md** - 12-phase development plan
- **PROJECT_HANDOFF.md** - Technical documentation
- **DEBUG_FEATURES.md** - Developer debug tools
- **buildozer.spec** - Build configuration

### Quick Links
- [GitHub Actions](https://github.com/Ishabdullah/Genesis/actions)
- [Issues](https://github.com/Ishabdullah/Genesis/issues)
- [Original Genesis](https://github.com/Ishabdullah/Genesis) (Termux version)

---

## ❓ FAQ

### Is this the full Genesis AI?
Not yet. This is a **preview version** showcasing the UI. Full AI capabilities are being integrated.

### When will it be feature-complete?
Following the 12-phase plan in IMPLEMENTATION_PLAN.md. Estimated 12-16 weeks for full release.

### Can I use it now?
Yes! The UI and chat interface work. Full AI features coming soon.

### Will it work offline?
Yes, once LLM integration is complete, it will work 100% offline.

### What about the Termux version?
The original Termux version is still available on the main branch. This is the Android app version.

### How is this different from the CLI version?
- Native Android app vs Termux CLI
- Graphical UI vs text-only
- Touch interface vs keyboard-only
- More accessible to general users

---

## 🤝 Contributing

This is an active development branch. Contributions welcome!

### Ways to Help
- 🐛 Test the preview app and report issues
- 💡 Suggest UI improvements
- 📝 Improve documentation
- 🔧 Submit pull requests

### Development Setup
```bash
git checkout claude/genesis-android-production-011CUsnEhM8wFNiRFhG1A4SC
# Make changes
# Test locally
# Submit PR
```

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Credits

**Development:**
- Genesis AI Project
- Anthropic (Claude assistance)
- Kivy Team (UI framework)
- Python-for-Android (p4a)

**Technologies:**
- Kivy 2.2.1
- Python 3.11
- Buildozer
- GitHub Actions

---

## 📞 Support

### Get Help
- **Issues:** [GitHub Issues](https://github.com/Ishabdullah/Genesis/issues)
- **Build Status:** [GitHub Actions](https://github.com/Ishabdullah/Genesis/actions)
- **Documentation:** See docs in repository

### Stay Updated
- **Watch Repo:** Get notified of updates
- **Check Actions:** See latest builds
- **Follow Branch:** Track development progress

---

## 🎯 Current Status Summary

**What Works:** ✅ UI, Chat Interface, Basic Responses
**What's Coming:** ⏳ AI, Device Control, Advanced Features
**Build Status:** 🔄 Check [Actions](https://github.com/Ishabdullah/Genesis/actions)
**Phase:** 3 of 12 (~25% complete)
**Version:** 2.3.0-preview

---

<div align="center">

## 🚀 Experience the Future of AI

**Download the preview and see the futuristic UI!**

[Get Latest APK](#-download-apk) • [View Progress](#-development-status) • [Contribute](#-contributing)

---

Made with 🧬 by the Genesis AI Team

**Version 2.3.0-preview** • Built for Android 7.0+

*Privacy-First • On-Device • Open Source*

</div>
