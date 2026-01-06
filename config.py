"""
SubPoint 配置文件
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 项目路径
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"

# OpenAI 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# OpenAI Audio（CLI / Transcription）默认参数
# 说明：
# - 这些配置用于 `openai audio.transcriptions.create` / `openai audio.translations.create` 的默认值
# - 通过环境变量可覆盖（推荐写入 .env）
OPENAI_AUDIO_TRANSCRIBE_MODEL = os.getenv("OPENAI_AUDIO_TRANSCRIBE_MODEL", "whisper-1")
OPENAI_AUDIO_TRANSLATE_MODEL = os.getenv("OPENAI_AUDIO_TRANSLATE_MODEL", "whisper-1")
OPENAI_AUDIO_RESPONSE_FORMAT = os.getenv("OPENAI_AUDIO_RESPONSE_FORMAT") or None
OPENAI_AUDIO_LANGUAGE = os.getenv("OPENAI_AUDIO_LANGUAGE") or None
_temp = os.getenv("OPENAI_AUDIO_TEMPERATURE")
if _temp in (None, ""):
    OPENAI_AUDIO_TEMPERATURE = None
else:
    try:
        OPENAI_AUDIO_TEMPERATURE = float(_temp)
    except ValueError:
        OPENAI_AUDIO_TEMPERATURE = None
OPENAI_AUDIO_PROMPT = os.getenv("OPENAI_AUDIO_PROMPT") or None

# Whisper 配置
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")  # tiny, base, small, medium, large

# YouTube 频道配置（可选，用于自动获取最新视频）
YOUTUBE_CHANNEL_URL = os.getenv("YOUTUBE_CHANNEL_URL", "")

# 下载配置
AUDIO_FORMAT = "mp3"
AUDIO_QUALITY = "192"

# 确保输出目录存在
OUTPUT_DIR.mkdir(exist_ok=True)

