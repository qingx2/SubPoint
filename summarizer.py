"""
AI 总结模块
使用 OpenAI API 对内容进行总结
"""
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.markdown import Markdown
from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL, OUTPUT_DIR

console = Console()

# 总结提示词模板
SUMMARY_PROMPT_ZH = """你是一个专业的内容总结专家。请对以下内容进行全面分析和总结。

**要求：**
1. 首先提供一个简洁的摘要（2-3句话）
2. 列出核心要点（使用项目符号）
3. 提取关键信息和重要数据
4. 如果有的话，总结主要观点和结论
5. 标注任何行动项或建议

**输出格式：**
# 内容总结

## 📌 摘要
[简洁的内容概述]

## 🎯 核心要点
- [要点1]
- [要点2]
- ...

## 💡 关键信息
[重要的数据、事实、引用等]

## 📝 主要观点
[主要论点和结论]

## ✅ 行动建议（如适用）
[可执行的建议或下一步]

---

**以下是需要总结的内容：**

{content}
"""

SUMMARY_PROMPT_EN = """You are a professional content summarizer. Please analyze and summarize the following content comprehensively.

**Requirements:**
1. Provide a brief summary (2-3 sentences)
2. List key points (using bullet points)
3. Extract important information and data
4. Summarize main arguments and conclusions if any
5. Note any action items or recommendations

**Output Format:**
# Content Summary

## 📌 Summary
[Brief overview of the content]

## 🎯 Key Points
- [Point 1]
- [Point 2]
- ...

## 💡 Key Information
[Important data, facts, quotes, etc.]

## 📝 Main Arguments
[Main arguments and conclusions]

## ✅ Action Items (if applicable)
[Actionable recommendations or next steps]

---

**Content to summarize:**

{content}
"""


def get_client() -> OpenAI:
    """获取 OpenAI 客户端"""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY 未设置，请在 .env 文件中配置")
    
    return OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL if OPENAI_BASE_URL else None,
    )


def summarize_text(
    text: str,
    language: str = "zh",
    model: Optional[str] = None,
    custom_prompt: Optional[str] = None,
) -> str:
    """
    使用 AI 总结文本内容
    
    Args:
        text: 要总结的文本
        language: 输出语言 ('zh' 或 'en')
        model: 使用的模型
        custom_prompt: 自定义提示词
    
    Returns:
        总结结果
    """
    client = get_client()
    model = model or OPENAI_MODEL
    
    # 选择提示词
    if custom_prompt:
        prompt = custom_prompt.format(content=text)
    else:
        prompt_template = SUMMARY_PROMPT_ZH if language == "zh" else SUMMARY_PROMPT_EN
        prompt = prompt_template.format(content=text)
    
    # 如果文本太长，进行分块处理
    max_chars = 100000  # 大约 25000 tokens
    if len(text) > max_chars:
        console.print("[yellow]⚠️  内容较长，将进行分块总结[/yellow]")
        return summarize_long_text(text, language, model)
    
    console.print(f"[yellow]🤖 正在使用 {model} 生成总结...[/yellow]")
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个专业的内容分析和总结专家。"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )
    
    return response.choices[0].message.content


def summarize_long_text(
    text: str,
    language: str = "zh",
    model: Optional[str] = None,
    chunk_size: int = 80000,
) -> str:
    """
    分块总结长文本
    """
    client = get_client()
    model = model or OPENAI_MODEL
    
    # 分块
    chunks = []
    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])
    
    console.print(f"[cyan]📚 分成 {len(chunks)} 个部分进行总结[/cyan]")
    
    # 分别总结每个部分
    chunk_summaries = []
    for i, chunk in enumerate(chunks, 1):
        console.print(f"[yellow]🔄 总结第 {i}/{len(chunks)} 部分...[/yellow]")
        
        prompt = f"请简洁总结以下内容的要点：\n\n{chunk}"
        
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个专业的内容总结专家。请提供简洁的要点总结。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        chunk_summaries.append(response.choices[0].message.content)
    
    # 合并总结
    console.print("[yellow]🔄 合并所有部分的总结...[/yellow]")
    
    combined = "\n\n---\n\n".join([f"**第{i}部分总结:**\n{s}" for i, s in enumerate(chunk_summaries, 1)])
    
    final_prompt = SUMMARY_PROMPT_ZH if language == "zh" else SUMMARY_PROMPT_EN
    final_prompt = final_prompt.format(content=combined)
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个专业的内容分析和总结专家。以下是分段总结，请整合为一个完整的总结。"},
            {"role": "user", "content": final_prompt},
        ],
        temperature=0.3,
    )
    
    return response.choices[0].message.content


def summarize_file(
    file_path: Path,
    output_dir: Optional[Path] = None,
    language: str = "zh",
    model: Optional[str] = None,
) -> Path:
    """
    总结文件内容并保存
    
    Args:
        file_path: 要总结的文件路径
        output_dir: 输出目录
        language: 输出语言
        model: 使用的模型
    
    Returns:
        总结文件路径
    """
    output_dir = output_dir or OUTPUT_DIR
    
    # 读取文件
    console.print(f"[cyan]📖 读取文件:[/cyan] {file_path.name}")
    text = file_path.read_text(encoding='utf-8')
    
    if not text.strip():
        raise ValueError("文件内容为空")
    
    console.print(f"[cyan]📊 内容长度:[/cyan] {len(text)} 字符")
    
    # 生成总结
    summary = summarize_text(text, language=language, model=model)
    
    # 保存总结
    output_path = output_dir / f"{file_path.stem}_summary.md"
    output_path.write_text(summary, encoding='utf-8')
    
    console.print(f"[green]✅ 总结完成:[/green] {output_path.name}")
    
    # 在控制台显示总结
    console.print("\n" + "="*50)
    console.print(Markdown(summary))
    console.print("="*50 + "\n")
    
    return output_path


if __name__ == "__main__":
    # 测试
    test_text = """
    这是一个测试文本。今天我们讨论了人工智能的发展趋势。
    主要有以下几点：
    1. 大语言模型正在快速发展
    2. AI 工具正在改变工作方式
    3. 安全和伦理问题需要关注
    """
    
    try:
        result = summarize_text(test_text)
        print(result)
    except ValueError as e:
        print(f"错误: {e}")

