import json
from typing import List, Dict, Any, Optional, Generator
from datetime import datetime
import openai
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text

console = Console()

class DeepSeekClient:
    def __init__(self, api_key: str, base_url: str = "https://api.deepseek.com", 
                 model: str = "deepseek-chat"):
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = model
        self.conversation_history = []
        self.total_tokens_used = 0
    
    def chat_completion(self, messages: List[Dict[str, str]], 
                       stream: bool = True, 
                       temperature: float = 0.7,
                       max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute chat completion with detailed logging
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            stream: Whether to stream the response
            temperature: Temperature for response generation
            max_tokens: Maximum tokens in response
        """
        
        request_start_time = datetime.now()
        
        # Log request parameters
        request_params = {
            "model": self.model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
            "message_count": len(messages),
            "timestamp": request_start_time.isoformat()
        }
        
        console.print(Panel(
            f"[bold blue]🤖 调用 DeepSeek API[/bold blue]\n"
            f"[cyan]模型:[/cyan] {self.model}\n"
            f"[cyan]消息数量:[/cyan] {len(messages)}\n"
            f"[cyan]温度参数:[/cyan] {temperature}\n"
            f"[cyan]流式输出:[/cyan] {stream}",
            title="DeepSeek 请求参数",
            border_style="blue"
        ))
        
        # Log the latest user message
        if messages and messages[-1].get("role") == "user":
            console.print(Panel(
                messages[-1]["content"],
                title="📝 用户输入",
                border_style="cyan"
            ))
        
        try:
            completion_kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "stream": stream
            }
            
            if max_tokens:
                completion_kwargs["max_tokens"] = max_tokens
            
            if stream:
                return self._handle_streaming_response(completion_kwargs, request_start_time)
            else:
                return self._handle_non_streaming_response(completion_kwargs, request_start_time)
                
        except Exception as e:
            error_msg = f"DeepSeek API 调用失败: {str(e)}"
            console.print(f"[bold red]❌ {error_msg}[/bold red]")
            
            return {
                "error": error_msg,
                "content": "",
                "usage": {},
                "request_params": request_params,
                "duration_seconds": 0
            }
    
    def _handle_streaming_response(self, completion_kwargs: Dict[str, Any], 
                                 request_start_time: datetime) -> Dict[str, Any]:
        """Handle streaming response with live updates"""
        
        response_content = ""
        
        console.print(Panel(
            "[bold green]🔄 正在生成回答...[/bold green]",
            title="DeepSeek 响应",
            border_style="green"
        ))
        
        try:
            response_stream = self.client.chat.completions.create(**completion_kwargs)
            
            # Create live display for streaming content
            response_text = Text()
            
            with Live(Panel(response_text, title="🤖 AI 回答", border_style="green"), 
                     refresh_per_second=10) as live:
                
                for chunk in response_stream:
                    if chunk.choices[0].delta.content:
                        content_chunk = chunk.choices[0].delta.content
                        response_content += content_chunk
                        response_text.append(content_chunk)
                        live.update(Panel(response_text, title="🤖 AI 回答", border_style="green"))
            
            request_end_time = datetime.now()
            duration = (request_end_time - request_start_time).total_seconds()
            
            # Log completion
            console.print(Panel(
                f"[bold green]✅ 回答生成完成[/bold green]\n"
                f"[cyan]耗时:[/cyan] {duration:.2f} 秒\n"
                f"[cyan]回答长度:[/cyan] {len(response_content)} 字符",
                title="生成完成",
                border_style="green"
            ))
            
            return {
                "content": response_content,
                "usage": {"completion_tokens": len(response_content.split())},
                "duration_seconds": duration,
                "timestamp": request_end_time.isoformat()
            }
            
        except Exception as e:
            console.print(f"[bold red]❌ 流式响应处理失败: {str(e)}[/bold red]")
            return {
                "error": str(e),
                "content": response_content,
                "usage": {},
                "duration_seconds": 0
            }
    
    def _handle_non_streaming_response(self, completion_kwargs: Dict[str, Any], 
                                     request_start_time: datetime) -> Dict[str, Any]:
        """Handle non-streaming response"""
        
        completion_kwargs["stream"] = False
        
        try:
            response = self.client.chat.completions.create(**completion_kwargs)
            
            request_end_time = datetime.now()
            duration = (request_end_time - request_start_time).total_seconds()
            
            content = response.choices[0].message.content
            usage = response.usage.dict() if response.usage else {}
            
            # Update token usage
            if "total_tokens" in usage:
                self.total_tokens_used += usage["total_tokens"]
            
            # Log response
            console.print(Panel(
                content,
                title="🤖 AI 回答",
                border_style="green"
            ))
            
            console.print(Panel(
                f"[bold green]✅ 回答生成完成[/bold green]\n"
                f"[cyan]耗时:[/cyan] {duration:.2f} 秒\n"
                f"[cyan]提示词tokens:[/cyan] {usage.get('prompt_tokens', 'N/A')}\n"
                f"[cyan]完成tokens:[/cyan] {usage.get('completion_tokens', 'N/A')}\n"
                f"[cyan]总tokens:[/cyan] {usage.get('total_tokens', 'N/A')}",
                title="生成统计",
                border_style="green"
            ))
            
            return {
                "content": content,
                "usage": usage,
                "duration_seconds": duration,
                "timestamp": request_end_time.isoformat()
            }
            
        except Exception as e:
            console.print(f"[bold red]❌ 非流式响应处理失败: {str(e)}[/bold red]")
            return {
                "error": str(e),
                "content": "",
                "usage": {},
                "duration_seconds": 0
            }
    
    def add_to_conversation(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_conversation_history(self, max_messages: Optional[int] = None) -> List[Dict[str, str]]:
        """Get conversation history for API calls"""
        history = self.conversation_history
        if max_messages:
            history = history[-max_messages:]
        
        # Return only role and content for API
        return [{"role": msg["role"], "content": msg["content"]} for msg in history]
    
    def clear_conversation(self):
        """Clear conversation history"""
        self.conversation_history = []
        console.print("[yellow]🔄 对话历史已清空[/yellow]")
    
    def get_token_usage(self) -> int:
        """Get total tokens used in this session"""
        return self.total_tokens_used