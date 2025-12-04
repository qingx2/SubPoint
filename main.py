#!/usr/bin/env python3
"""
SubPoint - YouTube 音频下载、字幕提取与 AI 总结工具

功能：
1. 下载 YouTube 视频音频
2. 提取/生成字幕（自动CC或Whisper语音识别）
3. 使用 AI 对内容进行总结
4. 输出：原版音频、字幕文档、总结文档
"""
import sys
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config import OUTPUT_DIR, WHISPER_MODEL, OPENAI_MODEL, YOUTUBE_CHANNEL_URL
from downloader import download_audio, download_subtitles, check_subtitle_availability, get_video_info, get_latest_video_from_channel
from transcriber import get_transcript
from summarizer import summarize_file

console = Console()


def print_banner():
    """打印工具横幅"""
    banner = """
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║   🎬 SubPoint - YouTube 智能内容提取工具                  ║
║                                                           ║
║   📥 下载音频 → 📝 提取字幕 → 🤖 AI 总结                 ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="cyan")


def print_results(audio_path: Path, transcript_path: Path, summary_path: Path, video_title: str):
    """打印处理结果"""
    table = Table(title=f"✅ 处理完成: {video_title}", show_header=True, header_style="bold magenta")
    table.add_column("文件类型", style="cyan")
    table.add_column("文件路径", style="green")
    table.add_column("大小", style="yellow")
    
    def get_size(path: Path) -> str:
        if path.exists():
            size = path.stat().st_size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        return "N/A"
    
    table.add_row("🎵 音频文件", str(audio_path.name), get_size(audio_path))
    table.add_row("📄 字幕文档", str(transcript_path.name), get_size(transcript_path))
    table.add_row("📋 总结文档", str(summary_path.name), get_size(summary_path))
    
    console.print()
    console.print(table)
    console.print()
    
    # 输出可点击的目录链接
    output_path = audio_path.parent.absolute()
    console.print(f"[cyan]📁 输出目录:[/cyan] [link=file://{output_path}]{output_path}[/link]")
    console.print("[dim]💡 点击上方路径可直接打开目录[/dim]")


@click.command()
@click.argument('url', required=False, default=None)
@click.option('--output', '-o', type=click.Path(), default=None, help='输出目录')
@click.option('--lang', '-l', default='zh', help='字幕语言 (默认: zh)')
@click.option('--summary-lang', '-s', default='zh', type=click.Choice(['zh', 'en']), help='总结语言 (默认: zh)')
@click.option('--whisper-model', '-w', default=None, help=f'Whisper 模型 (默认: {WHISPER_MODEL})')
@click.option('--ai-model', '-m', default=None, help=f'AI 总结模型 (默认: {OPENAI_MODEL})')
@click.option('--force-whisper', '-f', is_flag=True, help='强制使用 Whisper 转录，忽略现有字幕')
@click.option('--skip-summary', is_flag=True, help='跳过 AI 总结步骤')
@click.option('--info-only', '-i', is_flag=True, help='仅显示视频信息，不下载')
@click.option('--cookies', '-c', default='chrome', help='从浏览器读取cookies (safari/chrome/firefox/edge，默认: safari)')
def main(
    url: Optional[str],
    output: Optional[str],
    lang: str,
    summary_lang: str,
    whisper_model: Optional[str],
    ai_model: Optional[str],
    force_whisper: bool,
    skip_summary: bool,
    info_only: bool,
    cookies: str,
):
    """
    SubPoint - YouTube 内容提取与 AI 总结工具
    
    URL: YouTube 视频链接（可选，不提供时从 .env 中的 YOUTUBE_CHANNEL_URL 获取最新视频）
    
    示例:
        python main.py "https://www.youtube.com/watch?v=xxxxx"
        python main.py "https://www.youtube.com/watch?v=xxxxx" -l zh -s en
        python main.py "https://www.youtube.com/watch?v=xxxxx" -f --whisper-model medium
        python main.py  # 自动从配置的频道获取最新视频
    """
    print_banner()
    
    # 设置输出目录
    output_dir = Path(output) if output else OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 如果没有提供 URL，从 .env 配置的频道获取最新视频
        if not url:
            if not YOUTUBE_CHANNEL_URL:
                console.print("[red]❌ 错误: 未提供视频链接，且 .env 中未配置 YOUTUBE_CHANNEL_URL[/red]")
                console.print("[yellow]💡 提示: 请在 .env 文件中添加 YOUTUBE_CHANNEL_URL=https://www.youtube.com/@频道名/videos[/yellow]")
                sys.exit(1)
            
            console.print(Panel("[bold]自动获取频道最新视频[/bold]", style="magenta"))
            url = get_latest_video_from_channel(YOUTUBE_CHANNEL_URL, cookies_from_browser=cookies)
            
            if not url:
                console.print("[red]❌ 无法从频道获取视频链接[/red]")
                sys.exit(1)
            
            console.print()
        
        # 1. 获取视频信息
        console.print(Panel("[bold]步骤 1/4: 获取视频信息[/bold]", style="blue"))
        console.print(f"[cyan]🍪 使用浏览器 cookies:[/cyan] {cookies}")
        
        info = get_video_info(url, cookies_from_browser=cookies)
        subtitle_info = check_subtitle_availability(url, cookies_from_browser=cookies)
        
        console.print(f"[cyan]📹 标题:[/cyan] {info['title']}")
        console.print(f"[cyan]📺 频道:[/cyan] {info['channel']}")
        console.print(f"[cyan]⏱️  时长:[/cyan] {info['duration'] // 60}分{info['duration'] % 60}秒")
        console.print(f"[cyan]📝 手动字幕:[/cyan] {', '.join(subtitle_info['manual_langs'][:5]) or '无'}")
        console.print(f"[cyan]🤖 自动字幕:[/cyan] {', '.join(subtitle_info['auto_langs'][:5]) or '无'}")
        
        if info_only:
            console.print("\n[yellow]仅显示信息模式，退出[/yellow]")
            return
        
        console.print()
        
        # 2. 下载音频
        console.print(Panel("[bold]步骤 2/4: 下载音频[/bold]", style="blue"))
        audio_path, video_title = download_audio(url, output_dir, cookies_from_browser=cookies)
        console.print()
        
        # 3. 获取/生成字幕
        console.print(Panel("[bold]步骤 3/4: 提取字幕[/bold]", style="blue"))
        
        subtitle_path = None
        need_whisper = force_whisper
        
        if not force_whisper:
            # 尝试下载字幕
            has_subtitle = lang in subtitle_info['manual_langs'] or lang in subtitle_info['auto_langs']
            
            if has_subtitle:
                subtitle_path = download_subtitles(url, output_dir, lang=lang, cookies_from_browser=cookies)
            
            if not subtitle_path:
                console.print("[yellow]⚠️  无法获取字幕，将使用 Whisper 进行语音识别[/yellow]")
                need_whisper = True
        
        # 获取转录文本
        transcript_path = get_transcript(
            audio_path=audio_path,
            subtitle_path=subtitle_path,
            output_dir=output_dir,
            force_whisper=need_whisper,
            language=lang if need_whisper else None,
        )
        console.print()
        
        # 4. AI 总结
        if skip_summary:
            console.print(Panel("[bold]步骤 4/4: 跳过 AI 总结[/bold]", style="yellow"))
            summary_path = output_dir / f"{audio_path.stem}_summary.md"
            summary_path.write_text("# 总结已跳过\n\n用户选择跳过 AI 总结步骤。", encoding='utf-8')
        else:
            console.print(Panel("[bold]步骤 4/4: AI 内容总结[/bold]", style="blue"))
            summary_path = summarize_file(
                file_path=transcript_path,
                output_dir=output_dir,
                language=summary_lang,
                model=ai_model,
            )
        
        console.print()
        
        # 输出结果
        print_results(audio_path, transcript_path, summary_path, video_title)
        
    except KeyboardInterrupt:
        console.print("\n[red]❌ 用户取消操作[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ 错误: {e}[/red]")
        console.print_exception()
        sys.exit(1)


@click.group()
def cli():
    """SubPoint - YouTube 内容提取与 AI 总结工具"""
    pass


@cli.command()
@click.argument('url')
def info(url: str):
    """查看视频信息"""
    print_banner()
    
    info = get_video_info(url)
    subtitle_info = check_subtitle_availability(url)
    
    table = Table(title="视频信息", show_header=False)
    table.add_column("属性", style="cyan")
    table.add_column("值", style="green")
    
    table.add_row("标题", info['title'])
    table.add_row("频道", info['channel'])
    table.add_row("时长", f"{info['duration'] // 60}分{info['duration'] % 60}秒")
    table.add_row("上传日期", info.get('upload_date', 'N/A'))
    table.add_row("视频ID", info['id'])
    table.add_row("手动字幕", ', '.join(subtitle_info['manual_langs']) or '无')
    table.add_row("自动字幕", ', '.join(subtitle_info['auto_langs'][:10]) or '无')
    
    console.print(table)


if __name__ == '__main__':
    # 如果直接运行
    # 支持: 无参数自动获取最新视频 / 带URL参数 / 带选项参数
    main()

