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

# Whisper 配置
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")  # tiny, base, small, medium, large

# 下载配置
AUDIO_FORMAT = "mp3"
AUDIO_QUALITY = "192"

# 确保输出目录存在
OUTPUT_DIR.mkdir(exist_ok=True)

