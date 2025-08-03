import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from tavily import TavilyClient
from rich.console import Console
from rich.panel import Panel
from rich.json import JSON

console = Console()

class TavilySearcher:
    def __init__(self, api_key: str, max_results: int = 10):
        self.client = TavilyClient(api_key=api_key)
        self.max_results = max_results
        self.search_history = []
    
    def search(self, query: str, search_depth: str = "advanced", 
               include_domains: Optional[List[str]] = None,
               exclude_domains: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Execute search with detailed logging
        
        Args:
            query: Search query
            search_depth: "basic" or "advanced"
            include_domains: List of domains to include
            exclude_domains: List of domains to exclude
        """
        
        search_start_time = datetime.now()
        
        # Log search parameters
        search_params = {
            "query": query,
            "search_depth": search_depth,
            "max_results": self.max_results,
            "include_domains": include_domains,
            "exclude_domains": exclude_domains,
            "timestamp": search_start_time.isoformat()
        }
        
        console.print(Panel(
            f"[bold blue]🔍 开始搜索[/bold blue]\n"
            f"[cyan]查询:[/cyan] {query}\n"
            f"[cyan]搜索深度:[/cyan] {search_depth}\n"
            f"[cyan]最大结果数:[/cyan] {self.max_results}",
            title="Tavily 搜索参数",
            border_style="blue"
        ))
        
        try:
            # Execute search
            search_kwargs = {
                "query": query,
                "search_depth": search_depth,
                "max_results": self.max_results
            }
            
            if include_domains:
                search_kwargs["include_domains"] = include_domains
            if exclude_domains:
                search_kwargs["exclude_domains"] = exclude_domains
            
            response = self.client.search(**search_kwargs)
            
            search_end_time = datetime.now()
            search_duration = (search_end_time - search_start_time).total_seconds()
            
            # Process and log results
            processed_results = self._process_search_results(response, search_duration)
            
            # Store in history
            search_record = {
                "params": search_params,
                "results": processed_results,
                "duration_seconds": search_duration
            }
            self.search_history.append(search_record)
            
            self._log_search_results(processed_results, search_duration)
            
            return processed_results
            
        except Exception as e:
            error_msg = f"搜索失败: {str(e)}"
            console.print(f"[bold red]❌ {error_msg}[/bold red]")
            
            error_result = {
                "error": error_msg,
                "query": query,
                "timestamp": search_start_time.isoformat(),
                "results": [],
                "summary": ""
            }
            
            return error_result
    
    def _process_search_results(self, response: Dict[str, Any], duration: float) -> Dict[str, Any]:
        """Process raw search response into structured format"""
        
        results = response.get("results", [])
        
        processed_results = []
        for i, result in enumerate(results, 1):
            processed_result = {
                "rank": i,
                "title": result.get("title", ""),
                "url": result.get("url", ""),
                "content": result.get("content", ""),
                "score": result.get("score", 0),
                "published_date": result.get("published_date", "")
            }
            processed_results.append(processed_result)
        
        return {
            "query": response.get("query", ""),
            "results": processed_results,
            "results_count": len(processed_results),
            "search_duration_seconds": duration,
            "summary": response.get("answer", ""),
            "timestamp": datetime.now().isoformat()
        }
    
    def _log_search_results(self, results: Dict[str, Any], duration: float):
        """Log search results with rich formatting"""
        
        console.print(Panel(
            f"[bold green]✅ 搜索完成[/bold green]\n"
            f"[cyan]耗时:[/cyan] {duration:.2f} 秒\n"
            f"[cyan]结果数量:[/cyan] {results['results_count']}",
            title="搜索结果概览",
            border_style="green"
        ))
        
        # Log each result
        for result in results["results"]:
            console.print(Panel(
                f"[bold]排名 #{result['rank']}[/bold]\n"
                f"[cyan]标题:[/cyan] {result['title']}\n"
                f"[cyan]URL:[/cyan] {result['url']}\n"
                f"[cyan]评分:[/cyan] {result['score']}\n"
                f"[cyan]内容摘要:[/cyan] {result['content'][:200]}...",
                title=f"搜索结果 {result['rank']}",
                border_style="yellow"
            ))
        
        # Log summary if available
        if results.get("summary"):
            console.print(Panel(
                results["summary"],
                title="🤖 Tavily AI 总结",
                border_style="magenta"
            ))
    
    def get_search_history(self) -> List[Dict[str, Any]]:
        """Get complete search history"""
        return self.search_history
    
    def get_latest_search(self) -> Optional[Dict[str, Any]]:
        """Get the most recent search"""
        return self.search_history[-1] if self.search_history else None