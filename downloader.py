"""
YouTube 下载模块
使用 yt-dlp 下载音频和字幕
"""
import os
import re
from pathlib import Path
from typing import Optional, Tuple
import yt_dlp
from rich.console import Console

from config import OUTPUT_DIR, AUDIO_FORMAT, AUDIO_QUALITY

console = Console()


def sanitize_filename(title: str) -> str:
    """清理文件名，移除非法字符"""
    # 移除或替换非法字符
    title = re.sub(r'[<>:"/\\|?*]', '', title)
    title = re.sub(r'\s+', ' ', title).strip()
    return title[:100]  # 限制长度


def get_video_info(url: str, cookies_from_browser: Optional[str] = None) -> dict:
    """获取视频基本信息"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    if cookies_from_browser:
        ydl_opts['cookiesfrombrowser'] = (cookies_from_browser,)
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return {
            'id': info.get('id', ''),
            'title': info.get('title', 'unknown'),
            'duration': info.get('duration', 0),
            'channel': info.get('channel', ''),
            'upload_date': info.get('upload_date', ''),
            'has_subtitles': bool(info.get('subtitles')),
            'has_auto_captions': bool(info.get('automatic_captions')),
            'subtitles': info.get('subtitles', {}),
            'automatic_captions': info.get('automatic_captions', {}),
        }


def download_audio(url: str, output_dir: Optional[Path] = None, cookies_from_browser: Optional[str] = None) -> Tuple[Path, str]:
    """
    下载YouTube视频的音频
    
    返回: (音频文件路径, 视频标题)
    """
    output_dir = output_dir or OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 先获取视频信息
    info = get_video_info(url, cookies_from_browser)
    safe_title = sanitize_filename(info['title'])
    
    console.print(f"[cyan]📹 视频标题:[/cyan] {info['title']}")
    console.print(f"[cyan]📺 频道:[/cyan] {info['channel']}")
    console.print(f"[cyan]⏱️  时长:[/cyan] {info['duration'] // 60}分{info['duration'] % 60}秒")
    
    # 检查本地是否已存在音频文件
    audio_path = output_dir / f"{safe_title}.{AUDIO_FORMAT}"
    if audio_path.exists():
        console.print(f"[green]✅ 本地已存在音频文件，跳过下载:[/green] {audio_path.name}")
        return audio_path, info['title']
    
    output_template = str(output_dir / f"{safe_title}.%(ext)s")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': AUDIO_FORMAT,
            'preferredquality': AUDIO_QUALITY,
        }],
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
    }
    if cookies_from_browser:
        ydl_opts['cookiesfrombrowser'] = (cookies_from_browser,)
    
    console.print("[yellow]⬇️  正在下载音频...[/yellow]")
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    console.print(f"[green]✅ 音频下载完成:[/green] {audio_path.name}")
    
    return audio_path, info['title']


def download_subtitles(url: str, output_dir: Optional[Path] = None, lang: str = 'en', cookies_from_browser: Optional[str] = None) -> Optional[Path]:
    """
    下载YouTube视频的字幕
    优先下载手动字幕，如果没有则下载自动生成的字幕
    
    返回: 字幕文件路径，如果没有字幕则返回 None
    """
    output_dir = output_dir or OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    
    info = get_video_info(url, cookies_from_browser)
    safe_title = sanitize_filename(info['title'])
    
    # 检查是否有字幕
    has_manual = lang in info['subtitles']
    has_auto = lang in info['automatic_captions']
    
    if not has_manual and not has_auto:
        # 尝试其他语言
        available_langs = list(info['subtitles'].keys()) + list(info['automatic_captions'].keys())
        if available_langs:
            console.print(f"[yellow]⚠️  没有 {lang} 字幕，可用语言: {', '.join(set(available_langs)[:5])}[/yellow]")
        else:
            console.print("[yellow]⚠️  该视频没有任何字幕[/yellow]")
            return None
    
    output_template = str(output_dir / f"{safe_title}.%(ext)s")
    
    ydl_opts = {
        'skip_download': True,  # 不下载视频
        'writesubtitles': True,
        'writeautomaticsub': not has_manual,  # 如果没有手动字幕，下载自动字幕
        'subtitleslangs': [lang],
        'subtitlesformat': 'srt/vtt/best',
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
    }
    if cookies_from_browser:
        ydl_opts['cookiesfrombrowser'] = (cookies_from_browser,)
    
    console.print(f"[yellow]📝 正在下载字幕 ({'手动' if has_manual else '自动生成'})...[/yellow]")
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    
    # 查找下载的字幕文件
    for ext in ['srt', 'vtt', 'en.srt', 'en.vtt', f'{lang}.srt', f'{lang}.vtt']:
        subtitle_path = output_dir / f"{safe_title}.{ext}"
        if subtitle_path.exists():
            console.print(f"[green]✅ 字幕下载完成:[/green] {subtitle_path.name}")
            return subtitle_path
    
    # 模糊搜索字幕文件
    for file in output_dir.glob(f"{safe_title}*"):
        if file.suffix in ['.srt', '.vtt']:
            console.print(f"[green]✅ 字幕下载完成:[/green] {file.name}")
            return file
    
    console.print("[yellow]⚠️  字幕下载失败[/yellow]")
    return None


def check_subtitle_availability(url: str, cookies_from_browser: Optional[str] = None) -> dict:
    """
    检查视频的字幕可用性
    """
    info = get_video_info(url, cookies_from_browser)
    return {
        'has_subtitles': info['has_subtitles'],
        'has_auto_captions': info['has_auto_captions'],
        'manual_langs': list(info['subtitles'].keys()),
        'auto_langs': list(info['automatic_captions'].keys()),
    }


if __name__ == "__main__":
    # 测试
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    info = get_video_info(test_url)
    print(info)

