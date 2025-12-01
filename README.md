# 🎬 SubPoint

YouTube 智能内容提取工具 - 下载音频、提取字幕、AI 总结

## ✨ 功能

- **📥 音频下载** - 从 YouTube 视频下载高质量音频 (MP3)
- **📝 字幕提取** - 自动获取 CC 字幕，无字幕时使用 Whisper 语音识别
- **🤖 AI 总结** - 使用 GPT 对内容进行智能总结，提取核心要点
- **📁 完整输出** - 原版音频 + 字幕文档 + 总结文档

## 📦 安装

### 1. 克隆项目

```bash
cd SubPoint
```

### 2. 创建虚拟环境（推荐）

```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 安装 FFmpeg（必需）

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Windows (使用 Chocolatey)
choco install ffmpeg
```

### 5. 配置环境变量

创建 `.env` 文件：

```bash
# OpenAI API 配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# Whisper 模型配置 (tiny, base, small, medium, large)
WHISPER_MODEL=base
```

## 🚀 使用方法

### 基本用法

```bash
python main.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 完整选项

```bash
python main.py "URL" [选项]

选项:
  -o, --output PATH       输出目录
  -l, --lang TEXT         字幕语言 (默认: zh)
  -s, --summary-lang      总结语言 [zh|en] (默认: zh)
  -w, --whisper-model     Whisper 模型 (tiny/base/small/medium/large)
  -m, --ai-model          AI 总结模型
  -f, --force-whisper     强制使用 Whisper 转录
  --skip-summary          跳过 AI 总结
  -i, --info-only         仅显示视频信息
  --help                  显示帮助
```

### 示例

```bash
# 基本使用 - 下载并总结
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# 指定输出目录和字幕语言
python main.py "https://www.youtube.com/watch?v=xxxxx" -o ./my_output -l zh

# 使用中文总结，英文字幕
python main.py "https://www.youtube.com/watch?v=xxxxx" -l zh -s zh

# 强制使用 Whisper 转录（忽略现有字幕）
python main.py "https://www.youtube.com/watch?v=xxxxx" -f -w medium

# 仅下载，跳过 AI 总结
python main.py "https://www.youtube.com/watch?v=xxxxx" --skip-summary

# 仅查看视频信息
python main.py "https://www.youtube.com/watch?v=xxxxx" -i
```

## 📂 输出文件

运行后会在 `output/` 目录生成：

```
output/
├── 视频标题.mp3              # 原版音频
├── 视频标题_transcript.txt   # 字幕/转录文本
├── 视频标题_transcript_timestamped.txt  # 带时间戳的转录（Whisper）
└── 视频标题_summary.md       # AI 总结文档
```

## 🔧 Whisper 模型说明

| 模型 | 参数量 | 英文准确率 | 相对速度 | 显存需求 |
|------|--------|------------|----------|----------|
| tiny | 39M | ~50% | 最快 | ~1GB |
| base | 74M | ~70% | 快 | ~1GB |
| small | 244M | ~80% | 中等 | ~2GB |
| medium | 769M | ~85% | 较慢 | ~5GB |
| large | 1550M | ~90% | 最慢 | ~10GB |

建议：
- 英文内容：使用 `base` 或 `small`
- 中文/其他语言：使用 `medium` 或 `large`
- GPU 加速：确保安装了 CUDA 版本的 PyTorch

## ⚠️ 注意事项

1. **API Key** - 需要有效的 OpenAI API Key 才能使用 AI 总结功能
2. **网络要求** - 下载 YouTube 视频需要稳定的网络连接
3. **版权提醒** - 请遵守 YouTube 使用条款，仅下载有权使用的内容
4. **首次运行** - Whisper 模型会在首次使用时自动下载

## 🛠️ 技术栈

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube 下载
- [OpenAI Whisper](https://github.com/openai/whisper) - 语音识别
- [OpenAI API](https://platform.openai.com/) - AI 总结
- [Rich](https://github.com/Textualize/rich) - 终端美化
- [Click](https://click.palletsprojects.com/) - CLI 框架

## 📄 License

MIT License

