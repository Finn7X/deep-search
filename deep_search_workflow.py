import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from config import Config
from tavily_search import TavilySearcher
from deepseek_client import DeepSeekClient

console = Console()

class DeepSearchWorkflow:
    def __init__(self, config: Config):
        self.config = config
        self.tavily = TavilySearcher(config.tavily_api_key, config.max_search_results)
        self.deepseek = DeepSeekClient(
            config.deepseek_api_key, 
            config.deepseek_base_url, 
            config.deepseek_model
        )
        self.session_history = []
        self.workflow_stats = {
            "total_searches": 0,
            "total_questions": 0,
            "total_tokens": 0,
            "session_start": datetime.now().isoformat()
        }
    
    def process_question(self, question: str, search_depth: str = "advanced",
                        include_domains: Optional[List[str]] = None,
                        exclude_domains: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Complete deep search workflow for a question
        
        Args:
            question: User's question
            search_depth: Tavily search depth ("basic" or "advanced")
            include_domains: Domains to focus search on
            exclude_domains: Domains to exclude from search
        """
        
        workflow_start_time = datetime.now()
        
        console.print(Panel(
            f"[bold magenta]🚀 开始深度搜索工作流[/bold magenta]\n"
            f"[cyan]问题:[/cyan] {question}\n"
            f"[cyan]开始时间:[/cyan] {workflow_start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            title="Deep Search 工作流",
            border_style="magenta"
        ))
        
        workflow_result = {
            "question": question,
            "workflow_start_time": workflow_start_time.isoformat(),
            "search_results": None,
            "ai_response": None,
            "workflow_end_time": None,
            "total_duration_seconds": 0,
            "error": None
        }
        
        try:
            # Step 1: Execute search
            console.print("\n" + "="*60)
            console.print("[bold yellow]步骤 1: 执行搜索[/bold yellow]")
            console.print("="*60)
            
            search_results = self.tavily.search(
                query=question,
                search_depth=search_depth,
                include_domains=include_domains,
                exclude_domains=exclude_domains
            )
            
            if "error" in search_results:
                workflow_result["error"] = search_results["error"]
                return workflow_result
            
            workflow_result["search_results"] = search_results
            self.workflow_stats["total_searches"] += 1
            
            # Step 2: Prepare context for AI
            console.print("\n" + "="*60)
            console.print("[bold yellow]步骤 2: 准备AI上下文[/bold yellow]")
            console.print("="*60)
            
            context = self._prepare_ai_context(question, search_results)
            
            # Step 3: Generate AI response
            console.print("\n" + "="*60)
            console.print("[bold yellow]步骤 3: 生成AI回答[/bold yellow]")
            console.print("="*60)
            
            # Get conversation history
            conversation_messages = self.deepseek.get_conversation_history(
                max_messages=self.config.max_conversation_history
            )
            
            # Add current context
            conversation_messages.append({
                "role": "user",
                "content": context
            })
            
            ai_response = self.deepseek.chat_completion(
                messages=conversation_messages,
                stream=True,
                temperature=0.7
            )
            
            if "error" in ai_response:
                workflow_result["error"] = ai_response["error"]
                return workflow_result
            
            workflow_result["ai_response"] = ai_response
            
            # Update conversation history
            self.deepseek.add_to_conversation("user", question)
            self.deepseek.add_to_conversation("assistant", ai_response["content"])
            
            # Step 4: Finalize workflow
            workflow_end_time = datetime.now()
            total_duration = (workflow_end_time - workflow_start_time).total_seconds()
            
            workflow_result["workflow_end_time"] = workflow_end_time.isoformat()
            workflow_result["total_duration_seconds"] = total_duration
            
            # Update session statistics
            self.workflow_stats["total_questions"] += 1
            self.workflow_stats["total_tokens"] += ai_response.get("usage", {}).get("total_tokens", 0)
            
            # Store in session history
            self.session_history.append(workflow_result)
            
            # Log workflow summary
            self._log_workflow_summary(workflow_result)
            
            return workflow_result
            
        except Exception as e:
            error_msg = f"工作流执行失败: {str(e)}"
            console.print(f"[bold red]❌ {error_msg}[/bold red]")
            
            workflow_result["error"] = error_msg
            workflow_result["workflow_end_time"] = datetime.now().isoformat()
            
            return workflow_result
    
    def _prepare_ai_context(self, question: str, search_results: Dict[str, Any]) -> str:
        """Prepare context for AI based on search results"""
        
        console.print(Panel(
            "[bold blue]📝 准备AI上下文[/bold blue]\n"
            f"[cyan]搜索结果数量:[/cyan] {search_results['results_count']}\n"
            f"[cyan]是否包含摘要:[/cyan] {'是' if search_results.get('summary') else '否'}",
            title="上下文准备",
            border_style="blue"
        ))
        
        context_parts = [
            f"用户问题: {question}",
            "",
            "基于以下搜索结果回答用户问题："
        ]
        
        # Add Tavily summary if available
        if search_results.get("summary"):
            context_parts.extend([
                "",
                "AI搜索摘要:",
                search_results["summary"]
            ])
        
        # Add search results
        context_parts.extend([
            "",
            f"详细搜索结果 (共{search_results['results_count']}条):"
        ])
        
        for i, result in enumerate(search_results["results"], 1):
            context_parts.extend([
                f"\n--- 结果 {i} ---",
                f"标题: {result['title']}",
                f"来源: {result['url']}",
                f"内容: {result['content']}",
                f"相关性评分: {result['score']}"
            ])
        
        context_parts.extend([
            "",
            "请基于以上信息提供一个准确、详细且有用的回答。如果搜索结果不足以回答问题，请说明限制。"
        ])
        
        context = "\n".join(context_parts)
        
        console.print(Panel(
            f"[green]✅ 上下文准备完成[/green]\n"
            f"[cyan]上下文长度:[/cyan] {len(context)} 字符",
            title="上下文统计",
            border_style="green"
        ))
        
        return context
    
    def _log_workflow_summary(self, workflow_result: Dict[str, Any]):
        """Log complete workflow summary"""
        
        # Create summary table
        table = Table(title="🎯 Deep Search 工作流总结", style="cyan")
        table.add_column("指标", style="yellow")
        table.add_column("值", style="green")
        
        table.add_row("问题", workflow_result["question"])
        table.add_row("总耗时", f"{workflow_result['total_duration_seconds']:.2f} 秒")
        
        if workflow_result["search_results"]:
            search_results = workflow_result["search_results"]
            table.add_row("搜索耗时", f"{search_results['search_duration_seconds']:.2f} 秒")
            table.add_row("搜索结果数", str(search_results['results_count']))
        
        if workflow_result["ai_response"]:
            ai_response = workflow_result["ai_response"]
            table.add_row("AI生成耗时", f"{ai_response['duration_seconds']:.2f} 秒")
            
            usage = ai_response.get("usage", {})
            if "total_tokens" in usage:
                table.add_row("消耗tokens", str(usage["total_tokens"]))
        
        table.add_row("完成时间", workflow_result["workflow_end_time"])
        
        console.print(table)
        
        # Session statistics
        console.print(Panel(
            f"[bold blue]📊 本次会话统计[/bold blue]\n"
            f"[cyan]总问题数:[/cyan] {self.workflow_stats['total_questions']}\n"
            f"[cyan]总搜索次数:[/cyan] {self.workflow_stats['total_searches']}\n"
            f"[cyan]总消耗tokens:[/cyan] {self.workflow_stats['total_tokens']}\n"
            f"[cyan]会话开始时间:[/cyan] {self.workflow_stats['session_start']}",
            title="会话统计",
            border_style="blue"
        ))
    
    def get_session_history(self) -> List[Dict[str, Any]]:
        """Get complete session history"""
        return self.session_history
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history from DeepSeek client"""
        return self.deepseek.conversation_history
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.deepseek.clear_conversation()
        console.print("[yellow]🔄 对话历史已清空，但会话历史保留[/yellow]")
    
    def get_workflow_stats(self) -> Dict[str, Any]:
        """Get workflow statistics"""
        return self.workflow_stats.copy()