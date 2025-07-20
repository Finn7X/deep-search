"""
搜索规划器
基于查询分析结果动态确定搜索策略和参数
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from query_analyzer import QueryAnalysis, QueryComplexity

console = Console()

class SearchStrategy(Enum):
    DIRECT = "direct"                   # 直接搜索
    MULTI_ANGLE = "multi_angle"         # 多角度搜索
    SEQUENTIAL = "sequential"           # 序列搜索
    PARALLEL_DEEP = "parallel_deep"     # 并行深度搜索

@dataclass
class SearchPlan:
    strategy: SearchStrategy
    search_rounds: List['SearchRound']
    total_estimated_time: float
    priority_domains: List[str]
    fallback_queries: List[str]

@dataclass
class SearchRound:
    round_number: int
    queries: List[str]
    search_depth: str  # "basic" or "advanced"
    max_results: int
    include_domains: Optional[List[str]]
    exclude_domains: Optional[List[str]]
    timeout_seconds: int
    depends_on_previous: bool  # 是否依赖前一轮的结果

class SearchPlanner:
    def __init__(self, deepseek_client):
        self.deepseek_client = deepseek_client
        
        # 默认搜索配置
        self.default_config = {
            "max_results_simple": 5,
            "max_results_moderate": 8,
            "max_results_complex": 12,
            "max_results_multi_hop": 15,
            "timeout_basic": 30,
            "timeout_advanced": 60,
            "max_parallel_searches": 3
        }
        
        # 域名优先级配置
        self.domain_priorities = {
            "academic": ["arxiv.org", "scholar.google.com", "pubmed.ncbi.nlm.nih.gov", "ieee.org"],
            "technical": ["github.com", "stackoverflow.com", "docs.python.org", "developer.mozilla.org"],
            "news": ["reuters.com", "bbc.com", "cnn.com", "bloomberg.com"],
            "general": ["wikipedia.org", "britannica.com", "reddit.com"],
            "business": ["harvard.edu", "mit.edu", "stanford.edu", "fortune.com"]
        }
    
    def create_search_plan(self, query_analysis: QueryAnalysis, context: Optional[str] = None) -> SearchPlan:
        """
        基于查询分析创建搜索计划
        """
        console.print(Panel(
            f"[bold blue]📋 创建搜索计划[/bold blue]\n"
            f"[cyan]查询复杂度:[/cyan] {query_analysis.complexity.value}\n"
            f"[cyan]预估搜索轮次:[/cyan] {query_analysis.estimated_search_rounds}",
            title="搜索规划",
            border_style="blue"
        ))
        
        # 确定搜索策略
        strategy = self._determine_strategy(query_analysis)
        
        # 创建搜索轮次
        search_rounds = self._create_search_rounds(query_analysis, strategy, context)
        
        # 计算预估时间
        estimated_time = self._calculate_estimated_time(search_rounds)
        
        # 确定优先域名
        priority_domains = self._select_priority_domains(query_analysis)
        
        # 生成备选查询
        fallback_queries = self._generate_fallback_queries(query_analysis)
        
        search_plan = SearchPlan(
            strategy=strategy,
            search_rounds=search_rounds,
            total_estimated_time=estimated_time,
            priority_domains=priority_domains,
            fallback_queries=fallback_queries
        )
        
        self._log_search_plan(search_plan)
        return search_plan
    
    def _determine_strategy(self, query_analysis: QueryAnalysis) -> SearchStrategy:
        """确定搜索策略"""
        
        if query_analysis.complexity == QueryComplexity.SIMPLE:
            return SearchStrategy.DIRECT
        elif query_analysis.complexity == QueryComplexity.MODERATE:
            return SearchStrategy.MULTI_ANGLE
        elif query_analysis.complexity == QueryComplexity.COMPLEX:
            return SearchStrategy.SEQUENTIAL
        else:  # MULTI_HOP
            return SearchStrategy.PARALLEL_DEEP
    
    def _create_search_rounds(self, query_analysis: QueryAnalysis, 
                            strategy: SearchStrategy, context: Optional[str]) -> List[SearchRound]:
        """创建搜索轮次"""
        
        rounds = []
        
        if strategy == SearchStrategy.DIRECT:
            # 直接搜索策略 - 单轮搜索
            rounds.append(SearchRound(
                round_number=1,
                queries=[query_analysis.original_query],
                search_depth="basic",
                max_results=self.default_config["max_results_simple"],
                include_domains=query_analysis.domain_hints[:3] if query_analysis.domain_hints else None,
                exclude_domains=None,
                timeout_seconds=self.default_config["timeout_basic"],
                depends_on_previous=False
            ))
            
        elif strategy == SearchStrategy.MULTI_ANGLE:
            # 多角度搜索 - 使用搜索变体
            rounds.append(SearchRound(
                round_number=1,
                queries=query_analysis.search_variants[:3],
                search_depth="advanced",
                max_results=self.default_config["max_results_moderate"],
                include_domains=query_analysis.domain_hints[:3] if query_analysis.domain_hints else None,
                exclude_domains=None,
                timeout_seconds=self.default_config["timeout_advanced"],
                depends_on_previous=False
            ))
            
        elif strategy == SearchStrategy.SEQUENTIAL:
            # 序列搜索 - 先概述再深入
            rounds.append(SearchRound(
                round_number=1,
                queries=[query_analysis.original_query, f"{query_analysis.original_query} 概述"],
                search_depth="advanced",
                max_results=self.default_config["max_results_complex"],
                include_domains=None,
                exclude_domains=["reddit.com", "twitter.com"],  # 排除社交媒体
                timeout_seconds=self.default_config["timeout_advanced"],
                depends_on_previous=False
            ))
            
            # 第二轮基于子问题
            if query_analysis.sub_questions:
                rounds.append(SearchRound(
                    round_number=2,
                    queries=query_analysis.sub_questions[:2],
                    search_depth="advanced",
                    max_results=self.default_config["max_results_complex"],
                    include_domains=query_analysis.domain_hints[:2] if query_analysis.domain_hints else None,
                    exclude_domains=None,
                    timeout_seconds=self.default_config["timeout_advanced"],
                    depends_on_previous=True
                ))
                
        else:  # PARALLEL_DEEP
            # 并行深度搜索 - 多个维度同时探索
            rounds.append(SearchRound(
                round_number=1,
                queries=[query_analysis.original_query] + query_analysis.search_variants[:2],
                search_depth="advanced",
                max_results=self.default_config["max_results_multi_hop"],
                include_domains=None,
                exclude_domains=None,
                timeout_seconds=self.default_config["timeout_advanced"],
                depends_on_previous=False
            ))
            
            # 基于子问题的深入搜索
            if query_analysis.sub_questions:
                rounds.append(SearchRound(
                    round_number=2,
                    queries=query_analysis.sub_questions,
                    search_depth="advanced",
                    max_results=self.default_config["max_results_multi_hop"],
                    include_domains=query_analysis.domain_hints if query_analysis.domain_hints else None,
                    exclude_domains=None,
                    timeout_seconds=self.default_config["timeout_advanced"],
                    depends_on_previous=True
                ))
                
                # 可能的第三轮 - 专家级搜索
                rounds.append(SearchRound(
                    round_number=3,
                    queries=[],  # 将在执行时基于前两轮结果动态生成
                    search_depth="advanced",
                    max_results=10,
                    include_domains=query_analysis.domain_hints[:3] if query_analysis.domain_hints else None,
                    exclude_domains=["reddit.com", "twitter.com", "facebook.com"],
                    timeout_seconds=self.default_config["timeout_advanced"],
                    depends_on_previous=True
                ))
        
        return rounds
    
    def _select_priority_domains(self, query_analysis: QueryAnalysis) -> List[str]:
        """选择优先搜索域名"""
        
        priority_domains = []
        
        # 首先使用查询分析中的域名提示
        if query_analysis.domain_hints:
            priority_domains.extend(query_analysis.domain_hints)
        
        # 基于主要概念智能选择域名
        main_concepts_str = " ".join(query_analysis.main_concepts).lower()
        
        # 学术相关
        if any(term in main_concepts_str for term in ["研究", "论文", "学术", "理论", "算法"]):
            priority_domains.extend(self.domain_priorities["academic"][:2])
        
        # 技术相关
        if any(term in main_concepts_str for term in ["编程", "代码", "开发", "API", "框架"]):
            priority_domains.extend(self.domain_priorities["technical"][:2])
        
        # 商业相关
        if any(term in main_concepts_str for term in ["商业", "市场", "经济", "公司", "投资"]):
            priority_domains.extend(self.domain_priorities["business"][:2])
        
        # 新闻相关
        if any(term in main_concepts_str for term in ["新闻", "最新", "发展", "趋势", "事件"]):
            priority_domains.extend(self.domain_priorities["news"][:2])
        
        # 去重并限制数量
        unique_domains = list(dict.fromkeys(priority_domains))  # 保持顺序的去重
        return unique_domains[:5]  # 最多5个优先域名
    
    def _generate_fallback_queries(self, query_analysis: QueryAnalysis) -> List[str]:
        """生成备选查询（当主要搜索失败时使用）"""
        
        original = query_analysis.original_query
        fallbacks = [
            f"{original} 基础知识",
            f"{original} 简介",
            f"什么是 {original}",
            f"{original} 相关资料"
        ]
        
        return fallbacks[:3]
    
    def _calculate_estimated_time(self, search_rounds: List[SearchRound]) -> float:
        """计算预估搜索时间（秒）"""
        
        total_time = 0.0
        
        for round_info in search_rounds:
            # 每个查询的基础时间
            query_time = len(round_info.queries) * 5.0  # 每个查询5秒
            
            # 根据搜索深度调整
            if round_info.search_depth == "advanced":
                query_time *= 1.5
            
            # 根据结果数量调整
            result_factor = round_info.max_results / 10.0
            query_time *= result_factor
            
            total_time += query_time
        
        return total_time
    
    def _log_search_plan(self, search_plan: SearchPlan):
        """记录搜索计划"""
        
        console.print(Panel(
            f"[bold green]✅ 搜索计划创建完成[/bold green]\n"
            f"[cyan]策略:[/cyan] {search_plan.strategy.value}\n"
            f"[cyan]搜索轮次:[/cyan] {len(search_plan.search_rounds)}\n"
            f"[cyan]预估时间:[/cyan] {search_plan.total_estimated_time:.1f} 秒\n"
            f"[cyan]优先域名:[/cyan] {len(search_plan.priority_domains)} 个",
            title="搜索计划概览",
            border_style="green"
        ))
        
        # 详细搜索轮次表格
        table = Table(title="🎯 搜索轮次详情", style="cyan")
        table.add_column("轮次", style="yellow")
        table.add_column("查询数", style="green")
        table.add_column("搜索深度", style="blue")
        table.add_column("最大结果", style="magenta")
        table.add_column("依赖前轮", style="red")
        
        for round_info in search_plan.search_rounds:
            table.add_row(
                str(round_info.round_number),
                str(len(round_info.queries)),
                round_info.search_depth,
                str(round_info.max_results),
                "是" if round_info.depends_on_previous else "否"
            )
        
        console.print(table)
        
        # 显示优先域名
        if search_plan.priority_domains:
            console.print(Panel(
                "\n".join([f"• {domain}" for domain in search_plan.priority_domains]),
                title="🎯 优先搜索域名",
                border_style="yellow"
            ))
    
    def adapt_plan_based_on_results(self, search_plan: SearchPlan, 
                                   round_number: int, 
                                   search_results: List[Dict[str, Any]],
                                   current_knowledge: str) -> Optional[SearchRound]:
        """
        基于搜索结果动态调整搜索计划
        """
        console.print(Panel(
            f"[bold blue]🔄 动态调整搜索计划[/bold blue]\n"
            f"[cyan]当前轮次:[/cyan] {round_number}\n"
            f"[cyan]搜索结果数:[/cyan] {len(search_results)}",
            title="计划调整",
            border_style="blue"
        ))
        
        # 检查是否还有后续轮次
        next_round_number = round_number + 1
        next_round = None
        
        for round_info in search_plan.search_rounds:
            if round_info.round_number == next_round_number:
                next_round = round_info
                break
        
        if not next_round:
            return None
        
        # 如果下一轮依赖当前结果，动态生成查询
        if next_round.depends_on_previous and not next_round.queries:
            # 生成基于当前结果的新查询
            new_queries = self._generate_adaptive_queries(
                search_results, current_knowledge, next_round_number
            )
            next_round.queries = new_queries
        
        # 基于结果质量调整参数
        if len(search_results) < 3:  # 结果太少
            next_round.max_results = min(next_round.max_results + 5, 20)
            next_round.exclude_domains = None  # 移除域名限制
            console.print("[yellow]⚠️  结果较少，增加搜索范围[/yellow]")
        
        return next_round
    
    def _generate_adaptive_queries(self, search_results: List[Dict[str, Any]], 
                                 current_knowledge: str, round_number: int) -> List[str]:
        """基于搜索结果生成自适应查询"""
        
        # 提取搜索结果中的关键信息
        key_terms = []
        for result in search_results[:3]:
            title = result.get("title", "")
            content = result.get("content", "")
            # 简单的关键词提取（实际应用中可以使用更复杂的NLP方法）
            words = (title + " " + content).split()
            key_terms.extend([word for word in words if len(word) > 4][:5])
        
        # 基于轮次生成不同类型的查询
        if round_number == 2:
            # 第二轮：深入探索
            queries = [
                f"{' '.join(key_terms[:3])} 详细分析",
                f"{' '.join(key_terms[:2])} 实际应用",
            ]
        elif round_number == 3:
            # 第三轮：专家级查询
            queries = [
                f"{' '.join(key_terms[:2])} 最新研究",
                f"{' '.join(key_terms[:3])} 技术细节"
            ]
        else:
            # 默认查询
            queries = [f"{' '.join(key_terms[:2])} 相关信息"]
        
        console.print(Panel(
            "\n".join([f"• {q}" for q in queries]),
            title=f"🎯 第{round_number}轮自适应查询",
            border_style="cyan"
        ))
        
        return queries[:2]  # 最多返回2个查询