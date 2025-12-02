# 🎬 SubPoint

**YouTube Smart Content Extractor** - Download audio, extract subtitles, AI-powered summarization

English | [简体中文](./README_ZH.md)

---

## ✨ Features

- 📥 **Audio Download** - Download high-quality MP3 audio from YouTube
- 📝 **Subtitle Extraction** - Auto-fetch CC subtitles, fallback to Whisper speech recognition
- 🤖 **AI Summary** - GPT-powered intelligent analysis with structured summaries
- 📁 **Complete Output** - Audio file + Transcript + Summary report
- 🔄 **Auto Follow** - Configure channel URL to auto-fetch latest video

## 🚀 Quick Start

### Requirements

- Python 3.10+
- FFmpeg
- OpenAI API Key (for AI summarization)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-repo/SubPoint.git
cd SubPoint

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install FFmpeg
brew install ffmpeg       # macOS
sudo apt install ffmpeg   # Ubuntu/Debian
choco install ffmpeg      # Windows
```

### Configuration

Create a `.env` file:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
WHISPER_MODEL=base

# Optional: YouTube channel URL for auto-fetching latest video
YOUTUBE_CHANNEL_URL=https://www.youtube.com/@ChannelName/videos
```

## 📖 Usage

### Basic Usage

```bash
python main.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### Command Options

| Option | Description | Default |
|--------|-------------|---------|
| `-o, --output` | Output directory | `./output` |
| `-l, --lang` | Subtitle language | `zh` |
| `-s, --summary-lang` | Summary language (zh/en) | `zh` |
| `-w, --whisper-model` | Whisper model size | `base` |
| `-m, --ai-model` | AI model for summary | env var |
| `-f, --force-whisper` | Force Whisper transcription | - |
| `--skip-summary` | Skip AI summarization | - |
| `-i, --info-only` | Show video info only | - |

### Examples

```bash
# Basic usage
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Custom output directory and language
python main.py "URL" -o ./my_output -l en

# Force Whisper with medium model
python main.py "URL" -f -w medium

# Download only, skip summary
python main.py "URL" --skip-summary

# View video info
python main.py "URL" -i

# 🆕 Auto-fetch latest video from channel (requires YOUTUBE_CHANNEL_URL in .env)
python main.py
```

### Auto Follow Mode

After configuring `YOUTUBE_CHANNEL_URL` in `.env`, simply run `python main.py` to auto-fetch and process the latest video:

```bash
# Configure in .env
YOUTUBE_CHANNEL_URL=https://www.youtube.com/@RhinoFinance/videos

# Then just run
python main.py
```

## 📂 Output Structure

```
output/
├── Video_Title.mp3                        # Audio file
├── Video_Title_transcript.txt             # Plain text transcript
├── Video_Title_transcript_timestamped.txt # Timestamped transcript
└── Video_Title_transcript_summary.md      # AI summary report
```

## 🔧 Whisper Model Selection

| Model | Parameters | English Accuracy | Speed | VRAM |
|-------|------------|------------------|-------|------|
| tiny | 39M | ~50% | ⚡⚡⚡ | ~1GB |
| base | 74M | ~70% | ⚡⚡ | ~1GB |
| small | 244M | ~80% | ⚡ | ~2GB |
| medium | 769M | ~85% | 🐢 | ~5GB |
| large | 1550M | ~90% | 🐢🐢 | ~10GB |

**Recommendations**:
- English content → `base` or `small`
- Chinese/Multilingual → `medium` or `large`
- GPU acceleration requires CUDA-enabled PyTorch

## ⚠️ Notes

1. **API Key** - Valid OpenAI API Key required for AI summarization
2. **Network** - Stable internet connection needed for YouTube downloads
3. **Copyright** - Comply with YouTube ToS, only download authorized content
4. **First Run** - Whisper models are downloaded automatically on first use

## 🛠️ Tech Stack

| Component | Purpose |
|-----------|---------|
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | YouTube download |
| [OpenAI Whisper](https://github.com/openai/whisper) | Speech recognition |
| [OpenAI API](https://platform.openai.com/) | AI summarization |
| [Rich](https://github.com/Textualize/rich) | Terminal formatting |
| [Click](https://click.palletsprojects.com/) | CLI framework |

## 📄 License

MIT License
