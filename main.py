#!/usr/bin/env python3
"""
Deep Search Application

真正的深度搜索工具：
- 智能查询分析和改写
- 动态搜索参数规划
- ReAct多轮推理-行动框架
- 多跳搜索支持
- 详细的过程日志记录
"""

import os
import sys
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich.table import Table

from config import Config, load_config
from deep_search_engine import DeepSearchEngine

console = Console()

class DeepSearchApp:
    def __init__(self):
        self.config = None
        self.search_engine = None
        self.running = True
    
    def setup(self) -> bool:
        """Setup the application with API keys and configuration"""
        
        console.print(Panel(
            Text.from_markup(
                "[bold magenta]🔍 Deep Search 2.0 应用[/bold magenta]\n\n"
                "[cyan]全新功能特性:[/cyan]\n"
                "• 智能查询分析和改写\n"
                "• 动态搜索参数规划\n"
                "• ReAct多轮推理-行动框架\n"
                "• 多跳搜索支持\n"
                "• 深度结果整合分析\n"
                "• 详细的过程日志记录"
            ),
            title="欢迎使用 Deep Search 2.0",
            border_style="magenta"
        ))
        
        try:
            # Load configuration
            self.config = load_config()
            
            # Check DeepSeek API key
            if not self.config.deepseek_api_key:
                console.print("[yellow]⚠️  未找到 DeepSeek API Key[/yellow]")
                api_key = Prompt.ask("请输入您的 DeepSeek API Key", password=True)
                if not api_key.strip():
                    console.print("[red]❌ 未提供API Key，无法继续[/red]")
                    return False
                self.config.deepseek_api_key = api_key
            
            # Initialize Deep Search Engine
            self.search_engine = DeepSearchEngine(self.config)
            
            console.print(Panel(
                f"[bold green]✅ Deep Search 2.0 初始化完成[/bold green]\n"
                f"[cyan]Tavily API:[/cyan] 已配置\n"
                f"[cyan]DeepSeek API:[/cyan] 已配置\n"
                f"[cyan]DeepSeek 模型:[/cyan] {self.config.deepseek_model}\n"
                f"[cyan]查询分析器:[/cyan] ✅ 启用\n"
                f"[cyan]搜索规划器:[/cyan] ✅ 启用\n"
                f"[cyan]ReAct代理:[/cyan] ✅ 启用",
                title="配置状态",
                border_style="green"
            ))
            
            return True
            
        except Exception as e:
            console.print(f"[bold red]❌ 初始化失败: {str(e)}[/bold red]")
            return False
    
    def show_help(self):
        """Show available commands"""
        
        help_text = """
[bold cyan]可用命令:[/bold cyan]

[yellow]/help[/yellow] - 显示此帮助信息
[yellow]/clear[/yellow] - 清空会话历史
[yellow]/history[/yellow] - 显示搜索历史
[yellow]/stats[/yellow] - 显示会话统计
[yellow]/config[/yellow] - 显示当前配置
[yellow]/insights[/yellow] - 显示最近搜索的深度洞察
[yellow]/quit[/yellow] 或 [yellow]/exit[/yellow] - 退出应用

[bold cyan]Deep Search 2.0 特性:[/bold cyan]
• [green]智能查询分析[/green] - 自动识别查询复杂度和搜索策略
• [green]动态搜索规划[/green] - 基于查询特点动态调整搜索参数
• [green]ReAct智能代理[/green] - 多轮推理-行动-反思循环
• [green]多跳搜索[/green] - 支持需要多步推理的复杂问题
• [green]结果智能整合[/green] - 去重、过滤、质量评估

[bold cyan]使用说明:[/bold cyan]
直接输入您的问题，系统会自动：
1. 分析查询复杂度和主要概念
2. 规划最优搜索策略
3. 执行多轮ReAct搜索循环
4. 整合结果并生成深度回答

[bold cyan]示例问题:[/bold cyan]
• 什么是量子计算 (简单查询)
• 量子计算与传统计算的区别 (中等复杂度)
• 量子计算在密码学中的应用和对现有加密系统的影响 (复杂查询)
• GPT-4相比GPT-3的改进如何影响AI应用的发展趋势 (多跳推理)
        """
        
        console.print(Panel(help_text, title="Deep Search 2.0 帮助", border_style="cyan"))
    
    def show_search_history(self):
        """Show search history"""
        
        history = self.search_engine.get_session_history()
        
        if not history:
            console.print("[yellow]📝 暂无搜索历史[/yellow]")
            return
        
        console.print(Panel(
            f"[bold blue]📚 搜索历史 (共 {len(history)} 次搜索)[/bold blue]",
            border_style="blue"
        ))
        
        for i, search_result in enumerate(history, 1):
            console.print(Panel(
                f"[cyan]查询:[/cyan] {search_result['query']}\n"
                f"[cyan]复杂度:[/cyan] {search_result.get('query_analysis', {}).get('complexity', 'N/A')}\n"
                f"[cyan]搜索轮次:[/cyan] {search_result.get('search_process', {}).get('total_search_rounds', 0)}\n"
                f"[cyan]结果数量:[/cyan] {search_result.get('high_quality_results', 0)}\n"
                f"[cyan]耗时:[/cyan] {search_result.get('total_duration_seconds', 0):.1f} 秒",
                title=f"🔍 搜索 {i} - {search_result.get('timestamp', '未知时间')[:19]}",
                border_style="cyan"
            ))
    
    def show_stats(self):
        """Show session statistics"""
        
        stats = self.search_engine.get_session_stats()
        
        console.print(Panel(
            f"[bold blue]📊 Deep Search 2.0 会话统计[/bold blue]\n"
            f"[cyan]会话开始时间:[/cyan] {stats['session_start']}\n"
            f"[cyan]总搜索次数:[/cyan] {stats['total_queries']}\n"
            f"[cyan]总搜索轮次:[/cyan] {stats['total_search_rounds']}\n"
            f"[cyan]总搜索结果:[/cyan] {stats['total_search_results']}\n"
            f"[cyan]总AI调用:[/cyan] {stats['total_ai_calls']}",
            title="会话统计",
            border_style="blue"
        ))
    
    def show_config(self):
        """Show current configuration"""
        
        console.print(Panel(
            f"[bold blue]⚙️  Deep Search 2.0 配置[/bold blue]\n"
            f"[cyan]DeepSeek 模型:[/cyan] {self.config.deepseek_model}\n"
            f"[cyan]DeepSeek Base URL:[/cyan] {self.config.deepseek_base_url}\n"
            f"[cyan]最大搜索结果:[/cyan] {self.config.max_search_results}\n"
            f"[cyan]最大对话历史:[/cyan] {self.config.max_conversation_history}\n"
            f"[cyan]Tavily API Key:[/cyan] {'已配置' if self.config.tavily_api_key else '未配置'}\n"
            f"[cyan]DeepSeek API Key:[/cyan] {'已配置' if self.config.deepseek_api_key else '未配置'}\n"
            f"[cyan]查询分析器:[/cyan] ✅ 启用\n"
            f"[cyan]搜索规划器:[/cyan] ✅ 启用\n"
            f"[cyan]ReAct代理:[/cyan] ✅ 启用",
            title="配置信息",
            border_style="blue"
        ))
    
    def show_latest_insights(self):
        """Show insights from the latest search"""
        
        history = self.search_engine.get_session_history()
        
        if not history:
            console.print("[yellow]📊 暂无搜索记录，无法显示洞察[/yellow]")
            return
        
        latest_search = history[-1]
        insights = latest_search.get("insights", {})
        
        if not insights:
            console.print("[yellow]📊 最近搜索暂无洞察数据[/yellow]")
            return
        
        # 显示查询复杂度评估
        complexity_info = insights.get("query_complexity_assessment", {})
        console.print(Panel(
            f"[cyan]识别复杂度:[/cyan] {complexity_info.get('identified_complexity', 'N/A')}\n"
            f"[cyan]需要多跳搜索:[/cyan] {'是' if complexity_info.get('required_multi_hop') else '否'}\n"
            f"[cyan]预估轮次:[/cyan] {complexity_info.get('estimated_rounds', 0)}\n"
            f"[cyan]实际轮次:[/cyan] {complexity_info.get('actual_rounds', 0)}",
            title="🧠 查询复杂度分析",
            border_style="blue"
        ))
        
        # 显示信息发现洞察
        discovery_info = insights.get("information_discovery", {})
        console.print(Panel(
            f"[cyan]找到信息源:[/cyan] {discovery_info.get('total_sources_found', 0)} 个\n"
            f"[cyan]唯一域名:[/cyan] {discovery_info.get('unique_domains', 0)} 个\n"
            f"[cyan]平均相关性:[/cyan] {discovery_info.get('average_relevance_score', 0):.2f}",
            title="🔍 信息发现分析",
            border_style="yellow"
        ))
        
        # 显示ReAct性能
        react_info = insights.get("react_agent_performance", {})
        console.print(Panel(
            f"[cyan]推理循环:[/cyan] {react_info.get('reasoning_cycles', 0)} 次\n"
            f"[cyan]自适应查询:[/cyan] {react_info.get('adaptive_queries_generated', 0)} 个\n"
            f"[cyan]知识积累:[/cyan] {react_info.get('knowledge_accumulation_size', 0)} 字符",
            title="🤖 ReAct代理性能",
            border_style="green"
        ))
    
    
    def run(self):
        """Main application loop"""
        
        if not self.setup():
            return
        
        console.print("\n" + "="*60)
        console.print("[bold green]🚀 Deep Search 2.0 已启动！输入 /help 查看帮助信息[/bold green]")
        console.print("="*60 + "\n")
        
        while self.running:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold cyan]请输入您的问题[/bold cyan]", default="").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith("/"):
                    command = user_input.lower()
                    
                    if command in ["/quit", "/exit"]:
                        if Confirm.ask("确定要退出吗？"):
                            self.running = False
                            console.print("[yellow]👋 感谢使用 Deep Search 2.0！[/yellow]")
                            break
                    elif command == "/help":
                        self.show_help()
                    elif command == "/clear":
                        self.search_engine.clear_session()
                        console.print("[green]✅ 会话已清空[/green]")
                    elif command == "/history":
                        self.show_search_history()
                    elif command == "/stats":
                        self.show_stats()
                    elif command == "/config":
                        self.show_config()
                    elif command == "/insights":
                        self.show_latest_insights()
                    else:
                        console.print(f"[red]❌ 未知命令: {user_input}[/red]")
                        console.print("[yellow]输入 /help 查看可用命令[/yellow]")
                    
                    continue
                
                # Validate question
                if not user_input.strip():
                    console.print("[yellow]⚠️  请输入有效的问题[/yellow]")
                    continue
                
                # Execute Deep Search 2.0
                console.print("\n" + "🔥"*20 + " 启动 Deep Search 2.0 " + "🔥"*20)
                
                result = self.search_engine.deep_search(user_input)
                
                if result.get("error"):
                    console.print(f"\n[bold red]❌ Deep Search 失败: {result['error']}[/bold red]")
                elif result.get("success"):
                    # 显示AI回答
                    console.print("\n" + "="*60)
                    console.print("[bold green]🎯 Deep Search 2.0 最终回答[/bold green]")
                    console.print("="*60)
                    
                    console.print(Panel(
                        result.get("answer", "无法生成回答"),
                        title="🤖 AI 深度分析回答",
                        border_style="green"
                    ))
                    
                    # 显示搜索摘要
                    search_process = result.get("search_process", {})
                    console.print(Panel(
                        f"[cyan]搜索策略:[/cyan] {search_process.get('strategy', 'N/A')}\n"
                        f"[cyan]搜索轮次:[/cyan] {search_process.get('total_search_rounds', 0)}\n"
                        f"[cyan]ReAct行动:[/cyan] {search_process.get('react_actions', 0)}\n"
                        f"[cyan]高质量结果:[/cyan] {result.get('high_quality_results', 0)} 条\n"
                        f"[cyan]总耗时:[/cyan] {result.get('total_duration_seconds', 0):.1f} 秒",
                        title="📊 搜索过程摘要",
                        border_style="blue"
                    ))
                    
                    console.print("\n[bold green]✅ Deep Search 2.0 完成！输入 /insights 查看详细洞察[/bold green]")
                else:
                    console.print("\n[bold red]❌ Deep Search 2.0 未能成功完成[/bold red]")
                
            except KeyboardInterrupt:
                console.print("\n[yellow]⚠️  操作被中断[/yellow]")
                if Confirm.ask("是否退出应用？"):
                    self.running = False
                    console.print("[yellow]👋 感谢使用 Deep Search 2.0！[/yellow]")
            except Exception as e:
                console.print(f"[bold red]❌ 发生错误: {str(e)}[/bold red]")
                console.print("[yellow]请重试或输入 /help 获取帮助[/yellow]")

def main():
    """Main entry point"""
    app = DeepSearchApp()
    app.run()

if __name__ == "__main__":
    main()
