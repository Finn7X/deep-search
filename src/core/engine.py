"""
深度搜索引擎核心
整合所有组件，提供完整的深度搜索功能
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.live import Live

from .config import Config
from ..search.tavily_search import TavilySearcher
from ..clients.deepseek_client import DeepSeekClient
from ..agents.query_analyzer import QueryAnalyzer, QueryAnalysis
from ..search.planner import SearchPlanner, SearchPlan
from ..agents.react_agent import ReActAgent

console = Console()

class DeepSearchEngine:
    """
    深度搜索引擎 - 整合所有组件的核心类
    实现真正的Deep Search功能：查询改写、动态搜索、多轮ReAct
    """
    
    def __init__(self, config: Config):
        self.config = config
        
        # 初始化核心组件
        self.tavily_searcher = TavilySearcher(config.tavily_api_key, config.max_search_results)
        self.deepseek_client = DeepSeekClient(
            config.deepseek_api_key, 
            config.deepseek_base_url, 
            config.deepseek_model
        )
        
        # 初始化AI组件
        self.query_analyzer = QueryAnalyzer(self.deepseek_client)
        self.search_planner = SearchPlanner(self.deepseek_client)
        self.react_agent = ReActAgent(self.deepseek_client, self.tavily_searcher)
        
        # 搜索统计
        self.session_stats = {
            "total_queries": 0,
            "total_search_rounds": 0,
            "total_search_results": 0,
            "total_ai_calls": 0,
            "session_start": datetime.now().isoformat()
        }
        
        # 会话历史
        self.session_history = []
    
    def deep_search(self, query: str, user_preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        执行完整的深度搜索流程
        
        Args:
            query: 用户查询
            user_preferences: 用户偏好设置（可选）
        
        Returns:
            完整的深度搜索结果
        """
        search_start_time = datetime.now()
        
        console.print(Panel(
            f"[bold magenta]🚀 启动Deep Search引擎[/bold magenta]\n"
            f"[cyan]查询:[/cyan] {query}\n"
            f"[cyan]开始时间:[/cyan] {search_start_time.strftime('%Y-%m-%d %H:%M:%S')}",
            title="Deep Search Engine",
            border_style="magenta"
        ))
        
        try:
            # 第一阶段：查询分析
            console.print("\\n" + "="*60)
            console.print("[bold blue]📋 第一阶段：智能查询分析[/bold blue]")
            console.print("="*60)
            
            query_analysis = self.query_analyzer.analyze_query(query)
            
            # 第二阶段：搜索规划
            console.print("\\n" + "="*60) 
            console.print("[bold yellow]🎯 第二阶段：动态搜索规划[/bold yellow]")
            console.print("="*60)
            
            search_plan = self.search_planner.create_search_plan(query_analysis)
            
            # 第三阶段：ReAct深度搜索
            console.print("\\n" + "="*60)
            console.print("[bold green]🤖 第三阶段：ReAct智能搜索[/bold green]")
            console.print("="*60)
            
            react_results = self.react_agent.execute_deep_search(query, query_analysis, search_plan)
            
            # 第四阶段：结果整合和优化
            console.print("\\n" + "="*60)
            console.print("[bold purple]📊 第四阶段：结果整合分析[/bold purple]")
            console.print("="*60)
            
            final_results = self._integrate_and_optimize_results(
                query, query_analysis, search_plan, react_results, search_start_time
            )
            
            # 更新会话统计
            self._update_session_stats(final_results)
            
            # 记录到会话历史
            self.session_history.append(final_results)
            
            # 显示最终摘要
            self._display_final_summary(final_results)
            
            return final_results
            
        except Exception as e:
            error_msg = f"Deep Search执行失败: {str(e)}"
            console.print(f"[bold red]❌ {error_msg}[/bold red]")
            
            return {
                "query": query,
                "error": error_msg,
                "timestamp": datetime.now().isoformat(),
                "success": False
            }
    
    def _integrate_and_optimize_results(self, query: str, query_analysis: QueryAnalysis, 
                                      search_plan: SearchPlan, react_results: Dict[str, Any],
                                      start_time: datetime) -> Dict[str, Any]:
        """
        整合和优化搜索结果
        """
        console.print(Panel(
            "[bold purple]🔗 整合所有搜索结果[/bold purple]",
            title="结果整合",
            border_style="purple"
        ))
        
        end_time = datetime.now()
        total_duration = (end_time - start_time).total_seconds()
        
        # 收集所有搜索结果
        all_search_results = react_results.get("search_results", [])
        
        # 结果去重和质量过滤
        filtered_results = self._filter_and_deduplicate_results(all_search_results)
        
        # 生成增强的AI回答
        enhanced_answer = self._generate_enhanced_answer(
            query, query_analysis, filtered_results, react_results
        )
        
        # 生成搜索洞察
        search_insights = self._generate_search_insights(query_analysis, search_plan, react_results)
        
        # 构建最终结果
        final_results = {
            "query": query,
            "success": True,
            "timestamp": end_time.isoformat(),
            "total_duration_seconds": total_duration,
            
            # 核心结果
            "answer": enhanced_answer,
            "search_results": filtered_results,
            "total_results_found": len(all_search_results),
            "high_quality_results": len(filtered_results),
            
            # 分析结果
            "query_analysis": {
                "complexity": query_analysis.complexity.value,
                "main_concepts": query_analysis.main_concepts,
                "requires_multi_hop": query_analysis.requires_multi_hop,
                "estimated_vs_actual_rounds": {
                    "estimated": query_analysis.estimated_search_rounds,
                    "actual": react_results.get("total_search_rounds", 0)
                }
            },
            
            # 搜索过程
            "search_process": {
                "strategy": search_plan.strategy.value,
                "total_search_rounds": react_results.get("total_search_rounds", 0),
                "react_actions": react_results.get("execution_details", {}).get("actions", 0),
                "react_reflections": react_results.get("execution_details", {}).get("reflections", 0)
            },
            
            # 深度洞察
            "insights": search_insights,
            
            # 元数据
            "metadata": {
                "search_engine_version": "2.0",
                "query_analyzer_used": True,
                "search_planner_used": True,
                "react_agent_used": True,
                "ai_model": self.config.deepseek_model
            }
        }
        
        return final_results
    
    def _filter_and_deduplicate_results(self, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        过滤和去重搜索结果
        """
        console.print(Panel(
            f"[cyan]📝 过滤和去重搜索结果[/cyan]\\n原始结果: {len(search_results)} 条",
            title="结果处理",
            border_style="cyan"
        ))
        
        if not search_results:
            return []
        
        # 去重（基于URL）
        seen_urls = set()
        unique_results = []
        
        for result in search_results:
            url = result.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        # 质量过滤（保留评分较高的结果）
        quality_threshold = 0.6
        high_quality_results = [
            result for result in unique_results 
            if result.get("score", 0) >= quality_threshold
        ]
        
        # 如果高质量结果太少，降低标准
        if len(high_quality_results) < 3:
            quality_threshold = 0.4
            high_quality_results = [
                result for result in unique_results 
                if result.get("score", 0) >= quality_threshold
            ]
        
        # 按评分排序，取前15个
        sorted_results = sorted(high_quality_results, key=lambda x: x.get("score", 0), reverse=True)
        final_results = sorted_results[:15]
        
        console.print(Panel(
            f"[green]✅ 结果处理完成[/green]\\n"
            f"去重后: {len(unique_results)} 条\\n"
            f"高质量: {len(high_quality_results)} 条\\n"
            f"最终保留: {len(final_results)} 条",
            title="处理结果",
            border_style="green"
        ))
        
        return final_results
    
    def _generate_enhanced_answer(self, query: str, query_analysis: QueryAnalysis, 
                                filtered_results: List[Dict[str, Any]], 
                                react_results: Dict[str, Any]) -> str:
        """
        生成增强的AI回答
        """
        console.print(Panel(
            "[bold blue]🤖 生成增强AI回答[/bold blue]",
            title="AI回答生成",
            border_style="blue"
        ))
        
        # 构建增强的上下文
        enhanced_context = self._build_enhanced_context(
            query, query_analysis, filtered_results, react_results
        )
        
        # 生成回答
        enhanced_prompt = f"""
作为一个专业的深度搜索分析师，请基于以下完整的搜索分析过程和结果，提供一个全面、准确、深入的回答。

{enhanced_context}

请提供一个结构化的详细回答，要求：
1. 直接准确地回答用户问题
2. 提供具体的事实、数据和例子
3. 引用可靠的信息来源
4. 分析不同观点和角度
5. 指出任何不确定性或限制
6. 如果是复杂问题，提供分层次的分析
7. 总结关键要点和实用建议

回答应该专业、客观、有深度，体现出多轮深度搜索的价值。
"""
        
        response = self.deepseek_client.chat_completion(
            messages=[{"role": "user", "content": enhanced_prompt}],
            stream=True,
            temperature=0.2
        )
        
        if "error" in response:
            return f"基于{len(filtered_results)}条高质量搜索结果的分析，无法生成AI回答。请查看详细搜索结果。"
        
        return response.get("content", "回答生成失败")
    
    def _build_enhanced_context(self, query: str, query_analysis: QueryAnalysis,
                              filtered_results: List[Dict[str, Any]], 
                              react_results: Dict[str, Any]) -> str:
        """
        构建增强的上下文信息
        """
        context_parts = [
            f"用户查询: {query}",
            "",
            f"查询复杂度分析: {query_analysis.complexity.value}",
            f"主要概念: {', '.join(query_analysis.main_concepts)}",
            f"是否需要多跳搜索: {'是' if query_analysis.requires_multi_hop else '否'}",
            "",
            f"搜索过程概述:",
            f"- 总搜索轮次: {react_results.get('total_search_rounds', 0)}",
            f"- ReAct行动次数: {react_results.get('execution_details', {}).get('actions', 0)}",
            f"- 最终搜索进度: {react_results.get('execution_details', {}).get('final_progress', 0):.1%}",
            "",
            "高质量搜索结果:"
        ]
        
        # 添加搜索结果
        for i, result in enumerate(filtered_results[:10], 1):
            context_parts.extend([
                f"",
                f"结果 {i}:",
                f"标题: {result.get('title', '')}",
                f"来源: {result.get('url', '')}",
                f"相关性: {result.get('score', 0):.2f}",
                f"内容: {result.get('content', '')[:400]}..."
            ])
        
        # 添加ReAct积累的知识
        accumulated_knowledge = react_results.get("accumulated_knowledge", "")
        if accumulated_knowledge:
            context_parts.extend([
                "",
                "ReAct代理积累的深度知识:",
                accumulated_knowledge[:2000] + "..." if len(accumulated_knowledge) > 2000 else accumulated_knowledge
            ])
        
        return "\\n".join(context_parts)
    
    def _generate_search_insights(self, query_analysis: QueryAnalysis, 
                                search_plan: SearchPlan, 
                                react_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成搜索过程洞察
        """
        insights = {
            "query_complexity_assessment": {
                "identified_complexity": query_analysis.complexity.value,
                "required_multi_hop": query_analysis.requires_multi_hop,
                "estimated_rounds": query_analysis.estimated_search_rounds,
                "actual_rounds": react_results.get("total_search_rounds", 0)
            },
            
            "search_strategy_effectiveness": {
                "planned_strategy": search_plan.strategy.value,
                "total_planned_rounds": len(search_plan.search_rounds),
                "actual_react_actions": react_results.get("execution_details", {}).get("actions", 0),
                "final_progress_achieved": react_results.get("execution_details", {}).get("final_progress", 0)
            },
            
            "information_discovery": {
                "total_sources_found": len(react_results.get("search_results", [])),
                "unique_domains": len(set(r.get("url", "").split("/")[2] for r in react_results.get("search_results", []) if r.get("url"))),
                "average_relevance_score": self._calculate_average_score(react_results.get("search_results", []))
            },
            
            "react_agent_performance": {
                "reasoning_cycles": react_results.get("execution_details", {}).get("reflections", 0),
                "adaptive_queries_generated": self._count_adaptive_queries(react_results),
                "knowledge_accumulation_size": len(react_results.get("accumulated_knowledge", ""))
            }
        }
        
        return insights
    
    def _calculate_average_score(self, results: List[Dict[str, Any]]) -> float:
        """计算平均相关性评分"""
        if not results:
            return 0.0
        
        scores = [r.get("score", 0) for r in results if "score" in r]
        return sum(scores) / len(scores) if scores else 0.0
    
    def _count_adaptive_queries(self, react_results: Dict[str, Any]) -> int:
        """统计自适应查询数量"""
        # 简单统计 - 实际实现中可以更详细地追踪
        return react_results.get("total_search_rounds", 0) * 2
    
    def _update_session_stats(self, results: Dict[str, Any]):
        """更新会话统计"""
        self.session_stats["total_queries"] += 1
        self.session_stats["total_search_rounds"] += results.get("search_process", {}).get("total_search_rounds", 0)
        self.session_stats["total_search_results"] += results.get("total_results_found", 0)
        self.session_stats["total_ai_calls"] += results.get("search_process", {}).get("react_actions", 0)
    
    def _display_final_summary(self, results: Dict[str, Any]):
        """显示最终摘要"""
        
        # 创建摘要表格
        table = Table(title="🎯 Deep Search 完成摘要", style="cyan")
        table.add_column("指标", style="yellow")
        table.add_column("结果", style="green")
        
        table.add_row("查询复杂度", results["query_analysis"]["complexity"])
        table.add_row("搜索策略", results["search_process"]["strategy"])
        table.add_row("搜索轮次", str(results["search_process"]["total_search_rounds"]))
        table.add_row("ReAct行动", str(results["search_process"]["react_actions"]))
        table.add_row("找到结果", f"{results['total_results_found']} 条")
        table.add_row("高质量结果", f"{results['high_quality_results']} 条")
        table.add_row("总耗时", f"{results['total_duration_seconds']:.1f} 秒")
        
        console.print(table)
        
        # 显示洞察摘要
        insights = results["insights"]
        console.print(Panel(
            f"[bold blue]📊 搜索洞察[/bold blue]\\n"
            f"[cyan]信息发现:[/cyan] 来源 {insights['information_discovery']['unique_domains']} 个域名\\n"
            f"[cyan]平均相关性:[/cyan] {insights['information_discovery']['average_relevance_score']:.2f}\\n"
            f"[cyan]ReAct性能:[/cyan] {insights['react_agent_performance']['reasoning_cycles']} 次推理循环\\n"
            f"[cyan]知识积累:[/cyan] {insights['react_agent_performance']['knowledge_accumulation_size']} 字符",
            title="智能洞察",
            border_style="blue"
        ))
    
    def get_session_stats(self) -> Dict[str, Any]:
        """获取会话统计"""
        return self.session_stats.copy()
    
    def get_session_history(self) -> List[Dict[str, Any]]:
        """获取会话历史"""
        return self.session_history.copy()
    
    def clear_session(self):
        """清空会话"""
        self.session_history.clear()
        self.deepseek_client.clear_conversation()
        console.print("[yellow]🔄 Deep Search会话已清空[/yellow]")