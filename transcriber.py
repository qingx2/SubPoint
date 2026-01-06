"""
语音转录模块
使用 OpenAI Whisper 进行语音识别
"""
import re
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from config import WHISPER_MODEL, OUTPUT_DIR

console = Console()


def parse_vtt_to_text(vtt_path: Path) -> str:
    """将VTT字幕文件转换为纯文本"""
    content = vtt_path.read_text(encoding='utf-8')
    
    # 移除VTT头部
    content = re.sub(r'^WEBVTT.*?\n\n', '', content, flags=re.DOTALL)
    
    # 移除时间戳行
    content = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}.*?\n', '', content)
    
    # 移除空行和标签
    content = re.sub(r'<[^>]+>', '', content)
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    # 去重连续相同的行（自动字幕常见问题）
    deduped = []
    for line in lines:
        if not deduped or line != deduped[-1]:
            deduped.append(line)
    
    return ' '.join(deduped)


def parse_srt_to_text(srt_path: Path) -> str:
    """将SRT字幕文件转换为纯文本"""
    content = srt_path.read_text(encoding='utf-8')
    
    # 移除序号行
    content = re.sub(r'^\d+\s*$', '', content, flags=re.MULTILINE)
    
    # 移除时间戳行
    content = re.sub(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', '', content)
    
    # 移除标签
    content = re.sub(r'<[^>]+>', '', content)
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    # 去重
    deduped = []
    for line in lines:
        if not deduped or line != deduped[-1]:
            deduped.append(line)
    
    return ' '.join(deduped)


def subtitle_to_text(subtitle_path: Path) -> str:
    """将字幕文件转换为纯文本"""
    suffix = subtitle_path.suffix.lower()
    
    if suffix == '.vtt':
        return parse_vtt_to_text(subtitle_path)
    elif suffix == '.srt':
        return parse_srt_to_text(subtitle_path)
    else:
        # 尝试直接读取
        return subtitle_path.read_text(encoding='utf-8')


def transcribe_audio(
    audio_path: Path,
    output_dir: Optional[Path] = None,
    model_name: Optional[str] = None,
    language: Optional[str] = None
) -> Path:
    """
    使用 Whisper 转录音频文件
    
    Args:
        audio_path: 音频文件路径
        output_dir: 输出目录
        model_name: Whisper 模型名称 (tiny, base, small, medium, large)
        language: 语言代码 (如 'en', 'zh', 'ja' 等)，None 表示自动检测
    
    Returns:
        转录文本文件路径
    """
    import whisper
    
    output_dir = output_dir or OUTPUT_DIR
    model_name = model_name or WHISPER_MODEL
    
    # 检查输出文件是否已存在
    output_path = output_dir / f"{audio_path.stem}_transcript.txt"
    if output_path.exists():
        console.print(f"[yellow]⏭️  转录文件已存在，跳过转录:[/yellow] {output_path.name}")
        return output_path
    
    console.print(f"[yellow]🔄 正在加载 Whisper 模型 ({model_name})...[/yellow]")
    model = whisper.load_model(model_name)
    
    console.print("[yellow]🎙️  正在转录音频 (这可能需要几分钟)...[/yellow]")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("转录中...", total=None)
        
        # 转录
        result = model.transcribe(
            str(audio_path),
            language=language,
            verbose=False,
        )
        
        progress.update(task, completed=True)
    
    # 检测到的语言
    detected_lang = result.get('language', 'unknown')
    console.print(f"[cyan]🌐 检测到语言:[/cyan] {detected_lang}")
    
    # 保存完整文本
    text = result['text'].strip()
    # output_path 已在函数开头定义，这里直接使用
    output_path.write_text(text, encoding='utf-8')
    
    # 保存带时间戳的版本
    segments = result.get('segments', [])
    if segments:
        timestamped_output = output_dir / f"{audio_path.stem}_transcript_timestamped.txt"
        timestamped_lines = []
        for seg in segments:
            start = format_timestamp(seg['start'])
            end = format_timestamp(seg['end'])
            timestamped_lines.append(f"[{start} --> {end}] {seg['text'].strip()}")
        timestamped_output.write_text('\n'.join(timestamped_lines), encoding='utf-8')
        console.print(f"[green]✅ 带时间戳转录保存至:[/green] {timestamped_output.name}")
    
    console.print(f"[green]✅ 转录完成:[/green] {output_path.name}")
    
    return output_path


def format_timestamp(seconds: float) -> str:
    """将秒数格式化为时间戳"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def get_transcript(
    audio_path: Path,
    subtitle_path: Optional[Path] = None,
    output_dir: Optional[Path] = None,
    force_whisper: bool = False,
    language: Optional[str] = None,
) -> Path:
    """
    获取转录文本
    
    优先使用已有字幕，如果没有或强制使用 Whisper 则进行语音识别
    
    Args:
        audio_path: 音频文件路径
        subtitle_path: 字幕文件路径（可选）
        output_dir: 输出目录
        force_whisper: 强制使用 Whisper 转录
        language: 语言代码
    
    Returns:
        转录文本文件路径
    """
    output_dir = output_dir or OUTPUT_DIR
    
    # 如果有字幕且不强制使用 Whisper
    if subtitle_path and subtitle_path.exists() and not force_whisper:
        console.print("[cyan]📄 使用已下载的字幕文件[/cyan]")
        text = subtitle_to_text(subtitle_path)
        
        output_path = output_dir / f"{audio_path.stem}_transcript.txt"
        output_path.write_text(text, encoding='utf-8')
        
        console.print(f"[green]✅ 字幕转换完成:[/green] {output_path.name}")
        return output_path
    
    # 使用 Whisper 转录
    console.print("[cyan]🎙️  使用 Whisper 进行语音识别[/cyan]")
    return transcribe_audio(audio_path, output_dir, language=language)


if __name__ == "__main__":
    # 测试
    test_audio = Path("test.mp3")
    if test_audio.exists():
        result = transcribe_audio(test_audio)
        print(f"转录结果: {result}")

