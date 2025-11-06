# Genesis Changelog

All notable changes to Genesis will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.7.0] - 2025-11-06

### 🎉 Major Feature: Temporal Awareness & Time-Based Fallback

Genesis now has **temporal awareness** - the ability to understand when questions require current information beyond its training data cutoff.

### Added

#### Core Temporal Features
- **`time_sync.py`** - Real-time device clock synchronization module
  - Tracks device time with 60-second auto-refresh
  - Knowledge cutoff awareness (CodeLlama-7B: Dec 31, 2023)
  - Temporal metadata generation
  - Staleness detection for cached data
  - Background sync thread with safe error handling

- **`websearch.py`** - Free multi-source web search engine
  - **DuckDuckGo HTML search** (no API key required)
  - **Wikipedia API integration** for encyclopedic knowledge
  - **ArXiv API integration** for academic papers
  - Concurrent multi-source querying (3 sources in parallel)
  - Result aggregation with confidence scoring
  - 15-minute intelligent caching system
  - Automatic retry with fallback for failed sources

#### Enhanced Reasoning
- **Temporal query detection** in `reasoning.py`
  - Recognizes 18+ temporal keywords: "latest", "current", "now", "recent", "2025", etc.
  - Pattern matching for time-sensitive phrases
  - Automatic confidence reduction for queries beyond knowledge cutoff
  - Metadata tracking: `time_sensitive`, `temporal_uncertain`, `should_trigger_fallback`

#### Layered Fallback System
- **New 5-tier fallback chain**:
  1. 🧬 Calculated Answer (MathReasoner) - deterministic math
  2. 🌐 Genesis WebSearch - free multi-source search (NEW)
  3. 🔍 Perplexity CLI - external research API
  4. ☁️ Claude Fallback - interpretive reasoning
  5. 🧬 Local LLM - with uncertainty disclaimer

#### Memory Enhancements
- **Staleness detection** in `memory.py`
  - Timestamp tracking for all conversations
  - `check_staleness()` method with configurable threshold (default: 24 hours)
  - `get_fresh_context_string()` filters stale memories
  - Metadata support for temporal information

#### Testing & Validation
- **`test_temporal_awareness.py`** - comprehensive test suite
  - 7 test categories covering all temporal features
  - Time sync basic functionality tests
  - Temporal query detection validation
  - Query classification verification
  - WebSearch module integration tests
  - Temporal metadata generation tests
  - Real-world scenario tests (president query, etc.)
  - Time difference calculation tests
  - Success rate tracking and summary reporting

#### Integration
- Seamless integration into `genesis.py` main loop
  - Time context injection for all time-sensitive queries
  - Visual indicators: `[Time Context]`, `[Step X/3]` progress
  - Source attribution with new `websearch` source type
  - Performance tracking for WebSearch operations
  - Temporal metadata storage in learning memory

### Changed

- **Fallback priority order** - WebSearch now attempted before Perplexity
- **Confidence scoring** - Automatically reduced for time-sensitive queries
- **Query classification** - Returns 3-tuple: `(type, confidence, metadata)`
- **Memory add_interaction()** - Now accepts optional metadata parameter
- **Learning memory** - Stores temporal metadata for all interactions

### Enhanced

- **User feedback messages** - More informative temporal awareness notifications
- **Performance monitoring** - Tracks WebSearch usage alongside other sources
- **Source tracking** - New `websearch` source type in all logs and metrics
- **README.md** - Comprehensive temporal awareness documentation
  - New "Temporal Awareness & Time-Based Fallback" section
  - Updated fallback chain diagrams
  - Example queries with expected behavior
  - Testing instructions

### Technical Details

- **New dependencies**: None (uses stdlib + existing deps)
- **New modules**: 2 (time_sync.py, websearch.py)
- **Modified modules**: 3 (reasoning.py, genesis.py, memory.py)
- **Test coverage**: 7 new test categories
- **API keys required**: 0 (WebSearch uses free endpoints)
- **Performance impact**: Minimal (<100ms for time sync operations)

### Examples

#### Before v1.7
```
Genesis> Who is the president right now?
[Returns outdated information from 2023 training data]
Confidence: High (0.85) ❌ INCORRECT
```

#### After v1.7
```
Genesis> Who is the president right now?

[Time Context] Current system date/time: 2025-11-06 18:24:02
[Thinking...] This query is time-sensitive... Consulting live data sources...

[Step 1/3] Trying Genesis WebSearch...
✓ WebSearch successful (confidence: 0.85)

Donald J. Trump is the 47th President of the United States (2025-present)
Source: websearch ✅ CORRECT
```

### Backward Compatibility

- ✅ **Fully backward compatible** - existing functionality unchanged
- ✅ **Optional dependencies** - Perplexity CLI remains optional
- ✅ **Graceful degradation** - works offline if WebSearch unavailable
- ✅ **Existing data preserved** - memory files compatible

### Testing

Run the comprehensive test suite:
```bash
cd ~/Genesis
python3 test_temporal_awareness.py
```

Expected: All tests passing with ~95%+ success rate.

---

## [1.6.0] - 2025-11-05

### Added
- Multi-turn context handling
- Comprehensive evaluation framework
- Session management system
- 15-interaction context stack
- Natural retry patterns

### Fixed
- Reasoning chain persistence across retries
- Context boundary detection
- Question ID tracking for proper session separation

---

## [1.5.0] - 2025-11-04

### Added
- Complete reasoning & retry system overhaul
- MathReasoner with algebraic solving
- Deterministic calculation engine
- Feedback learning with notes
- Performance monitoring dashboard

### Fixed
- All math accuracy issues
- Retry command handling
- Memory persistence bugs

---

## [1.0.0] - 2025-10-30

### Added
- Initial Genesis release
- Local LLM integration (CodeLlama-7B)
- Basic file operations
- Simple reasoning traces
- Memory management
- Code execution sandbox

---

## Contributing

See [README.md](README.md) for contribution guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
