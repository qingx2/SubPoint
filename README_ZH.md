# 🎬 SubPoint

**YouTube 智能内容提取工具** - 下载音频、提取字幕、AI 智能总结

[English](./README.md) | 简体中文

---

## ✨ 功能特性

- 📥 **音频下载** - 从 YouTube 下载高质量 MP3 音频
- 📝 **字幕提取** - 优先获取 CC 字幕，无字幕时自动使用 Whisper 语音识别
- 🤖 **AI 总结** - GPT 智能分析，提取核心要点与结构化总结
- 📁 **完整输出** - 音频文件 + 字幕文档 + 总结报告

## 🚀 快速开始

### 环境要求

- Python 3.10+
- FFmpeg
- OpenAI API Key（用于 AI 总结）

### 安装步骤

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/SubPoint.git
cd SubPoint

# 2. 创建虚拟环境
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装 FFmpeg
brew install ffmpeg       # macOS
sudo apt install ffmpeg   # Ubuntu/Debian
choco install ffmpeg      # Windows
```

### 配置环境变量

创建 `.env` 文件：

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
WHISPER_MODEL=base
```

## 📖 使用方法

### 基本用法

```bash
python main.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

### 命令选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `-o, --output` | 输出目录 | `./output` |
| `-l, --lang` | 字幕语言 | `zh` |
| `-s, --summary-lang` | 总结语言 (zh/en) | `zh` |
| `-w, --whisper-model` | Whisper 模型 | `base` |
| `-m, --ai-model` | AI 总结模型 | 环境变量 |
| `-f, --force-whisper` | 强制使用 Whisper | - |
| `--skip-summary` | 跳过 AI 总结 | - |
| `-i, --info-only` | 仅显示视频信息 | - |

### 使用示例

```bash
# 基本使用
python main.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# 指定输出目录和字幕语言
python main.py "URL" -o ./my_output -l en

# 强制 Whisper 转录，使用 medium 模型
python main.py "URL" -f -w medium

# 仅下载，不生成总结
python main.py "URL" --skip-summary

# 查看视频信息
python main.py "URL" -i
```

## 📂 输出结构

```
output/
├── 视频标题.mp3                        # 音频文件
├── 视频标题_transcript.txt             # 纯文本字幕
├── 视频标题_transcript_timestamped.txt # 带时间戳字幕
└── 视频标题_transcript_summary.md      # AI 总结报告
```

## 🔧 Whisper 模型选择

| 模型 | 参数量 | 英文准确率 | 速度 | 显存 |
|------|--------|-----------|------|------|
| tiny | 39M | ~50% | ⚡⚡⚡ | ~1GB |
| base | 74M | ~70% | ⚡⚡ | ~1GB |
| small | 244M | ~80% | ⚡ | ~2GB |
| medium | 769M | ~85% | 🐢 | ~5GB |
| large | 1550M | ~90% | 🐢🐢 | ~10GB |

**建议**：
- 英文内容 → `base` 或 `small`
- 中文/多语言 → `medium` 或 `large`
- GPU 加速需安装 CUDA 版 PyTorch

## ⚠️ 注意事项

1. **API Key** - AI 总结功能需要有效的 OpenAI API Key
2. **网络** - YouTube 下载需稳定网络连接
3. **版权** - 请遵守 YouTube 使用条款，仅下载有权使用的内容
4. **首次运行** - Whisper 模型会自动下载

## 🛠️ 技术栈

| 组件 | 用途 |
|------|------|
| [yt-dlp](https://github.com/yt-dlp/yt-dlp) | YouTube 下载 |
| [OpenAI Whisper](https://github.com/openai/whisper) | 语音识别 |
| [OpenAI API](https://platform.openai.com/) | AI 总结 |
| [Rich](https://github.com/Textualize/rich) | 终端美化 |
| [Click](https://click.palletsprojects.com/) | CLI 框架 |

## 📄 License

MIT License

