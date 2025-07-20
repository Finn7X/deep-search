"""
查询分析和改写模块
负责分析用户查询，生成多个搜索变体，并识别搜索复杂度
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from rich.console import Console
from rich.panel import Panel

console = Console()

class QueryComplexity(Enum):
    SIMPLE = "simple"           # 单一概念查询
    MODERATE = "moderate"       # 需要2-3个概念结合
    COMPLEX = "complex"         # 需要多个概念和推理
    MULTI_HOP = "multi_hop"     # 需要多步推理和搜索

@dataclass
class QueryAnalysis:
    original_query: str
    complexity: QueryComplexity
    main_concepts: List[str]
    sub_questions: List[str]
    search_variants: List[str]
    requires_multi_hop: bool
    estimated_search_rounds: int
    domain_hints: List[str]
    reasoning: str

class QueryAnalyzer:
    def __init__(self, deepseek_client):
        self.deepseek_client = deepseek_client
        
    def analyze_query(self, query: str) -> QueryAnalysis:
        """
        深度分析用户查询，识别复杂度和搜索策略
        """
        console.print(Panel(
            f"[bold blue]🔍 开始查询分析[/bold blue]\n"
            f"[cyan]原始查询:[/cyan] {query}",
            title="查询分析",
            border_style="blue"
        ))
        
        # 构建分析提示词
        analysis_prompt = self._build_analysis_prompt(query)
        
        # 调用AI进行分析
        response = self.deepseek_client.chat_completion(
            messages=[{"role": "user", "content": analysis_prompt}],
            stream=False,
            temperature=0.3
        )
        
        if "error" in response:
            # 如果AI分析失败，使用基础分析
            return self._basic_analysis(query)
        
        try:
            # 清理响应内容，移除可能的markdown格式
            content = response["content"].strip()
            if content.startswith("```json"):
                content = content[7:]  # 移除开头的 ```json
            if content.endswith("```"):
                content = content[:-3]  # 移除结尾的 ```
            content = content.strip()
            
            # 解析AI返回的分析结果
            analysis_data = json.loads(content)
            return self._parse_analysis_response(query, analysis_data)
            
        except (json.JSONDecodeError, KeyError) as e:
            console.print(f"[yellow]⚠️  AI分析解析失败，使用基础分析: {e}[/yellow]")
            return self._basic_analysis(query)
    
    def _build_analysis_prompt(self, query: str) -> str:
        """构建查询分析提示词"""
        
        prompt = f"""
请深度分析以下用户查询，并返回JSON格式的分析结果：

用户查询: "{query}"

请分析并返回以下信息的JSON：

{{
    "complexity": "simple/moderate/complex/multi_hop",
    "main_concepts": ["概念1", "概念2", ...],
    "sub_questions": ["子问题1", "子问题2", ...],
    "search_variants": ["搜索变体1", "搜索变体2", ...],
    "requires_multi_hop": true/false,
    "estimated_search_rounds": 数字,
    "domain_hints": ["建议的搜索域名1", "域名2", ...],
    "reasoning": "分析推理过程的详细说明"
}}

分析标准：
1. complexity判断：
   - simple: 单一明确概念，如"什么是Python"
   - moderate: 需要2-3个概念结合，如"Python与Java的区别" 
   - complex: 多概念需要深度分析，如"机器学习在金融风控中的应用"
   - multi_hop: 需要多步推理，如"GPT-4相比GPT-3在代码生成能力上的提升如何影响程序员工作"

2. sub_questions: 将复杂查询分解为可独立搜索的子问题

3. search_variants: 生成3-5个不同角度的搜索关键词组合

4. estimated_search_rounds: 预估需要的搜索轮次(1-5)

5. domain_hints: 建议重点搜索的网站域名

6. requires_multi_hop: 是否需要基于前一次搜索结果进行下一次搜索

请确保返回有效的JSON格式。
"""
        return prompt
    
    def _parse_analysis_response(self, query: str, analysis_data: Dict[str, Any]) -> QueryAnalysis:
        """解析AI分析响应"""
        
        try:
            complexity = QueryComplexity(analysis_data.get("complexity", "moderate"))
        except ValueError:
            complexity = QueryComplexity.MODERATE
        
        analysis = QueryAnalysis(
            original_query=query,
            complexity=complexity,
            main_concepts=analysis_data.get("main_concepts", []),
            sub_questions=analysis_data.get("sub_questions", []),
            search_variants=analysis_data.get("search_variants", [query]),
            requires_multi_hop=analysis_data.get("requires_multi_hop", False),
            estimated_search_rounds=min(analysis_data.get("estimated_search_rounds", 1), 5),
            domain_hints=analysis_data.get("domain_hints", []),
            reasoning=analysis_data.get("reasoning", "基于AI分析")
        )
        
        self._log_analysis_result(analysis)
        return analysis
    
    def _basic_analysis(self, query: str) -> QueryAnalysis:
        """基础查询分析（当AI分析失败时的备选方案）"""
        
        # 简单的规则基础分析
        query_lower = query.lower()
        
        # 判断复杂度
        complexity_indicators = {
            "simple": ["什么是", "定义", "介绍"],
            "moderate": ["比较", "区别", "优缺点", "VS", "对比"],
            "complex": ["应用", "影响", "趋势", "发展", "分析"],
            "multi_hop": ["如何影响", "基于", "导致", "为什么会", "深层原因"]
        }
        
        complexity = QueryComplexity.SIMPLE
        for level, indicators in complexity_indicators.items():
            if any(indicator in query for indicator in indicators):
                complexity = QueryComplexity(level)
        
        # 生成搜索变体
        search_variants = [
            query,
            f"{query} 详细解释",
            f"{query} 最新发展"
        ]
        
        analysis = QueryAnalysis(
            original_query=query,
            complexity=complexity,
            main_concepts=query.split()[:3],  # 简单提取前3个词作为概念
            sub_questions=[query],
            search_variants=search_variants,
            requires_multi_hop=complexity in [QueryComplexity.COMPLEX, QueryComplexity.MULTI_HOP],
            estimated_search_rounds=1 if complexity == QueryComplexity.SIMPLE else 2,
            domain_hints=[],
            reasoning="基于规则的基础分析"
        )
        
        self._log_analysis_result(analysis)
        return analysis
    
    def _log_analysis_result(self, analysis: QueryAnalysis):
        """记录分析结果"""
        
        console.print(Panel(
            f"[bold green]✅ 查询分析完成[/bold green]\n"
            f"[cyan]复杂度:[/cyan] {analysis.complexity.value}\n"
            f"[cyan]主要概念:[/cyan] {', '.join(analysis.main_concepts)}\n"
            f"[cyan]需要多跳搜索:[/cyan] {'是' if analysis.requires_multi_hop else '否'}\n"
            f"[cyan]预估搜索轮次:[/cyan] {analysis.estimated_search_rounds}\n"
            f"[cyan]子问题数量:[/cyan] {len(analysis.sub_questions)}\n"
            f"[cyan]搜索变体数量:[/cyan] {len(analysis.search_variants)}",
            title="分析结果",
            border_style="green"
        ))
        
        if analysis.sub_questions:
            console.print(Panel(
                "\n".join([f"• {q}" for q in analysis.sub_questions]),
                title="🎯 子问题分解",
                border_style="yellow"
            ))
        
        if analysis.search_variants:
            console.print(Panel(
                "\n".join([f"• {v}" for v in analysis.search_variants]),
                title="🔍 搜索变体",
                border_style="cyan"
            ))
    
    def generate_follow_up_queries(self, original_query: str, 
                                  search_results: List[Dict[str, Any]], 
                                  current_knowledge: str) -> List[str]:
        """
        基于搜索结果生成后续查询
        用于多跳搜索
        """
        
        console.print(Panel(
            "[bold blue]🧠 生成后续查询[/bold blue]",
            title="多跳搜索",
            border_style="blue"
        ))
        
        # 构建后续查询生成提示词
        follow_up_prompt = f"""
基于原始查询和当前搜索结果，生成2-3个有针对性的后续搜索查询。

原始查询: "{original_query}"

当前已知信息:
{current_knowledge}

最近搜索结果摘要:
{self._summarize_search_results(search_results)}

请生成2-3个后续搜索查询，用于深入探索相关信息。要求：
1. 每个查询应该探索不同的角度或细节
2. 查询应该基于已有信息，但寻求更深层的洞察
3. 避免重复已经充分回答的内容
4. 返回JSON格式: {{"follow_up_queries": ["查询1", "查询2", "查询3"]}}
"""
        
        response = self.deepseek_client.chat_completion(
            messages=[{"role": "user", "content": follow_up_prompt}],
            stream=False,
            temperature=0.4
        )
        
        if "error" in response:
            # 如果AI生成失败，使用规则生成
            return self._generate_rule_based_follow_ups(original_query, search_results)
        
        try:
            # 清理响应内容，移除可能的markdown格式
            content = response["content"].strip()
            if content.startswith("```json"):
                content = content[7:]  # 移除开头的 ```json
            if content.endswith("```"):
                content = content[:-3]  # 移除结尾的 ```
            content = content.strip()
            
            follow_up_data = json.loads(content)
            follow_up_queries = follow_up_data.get("follow_up_queries", [])
            
            console.print(Panel(
                "\n".join([f"• {q}" for q in follow_up_queries]),
                title="🎯 后续查询",
                border_style="green"
            ))
            
            return follow_up_queries[:3]  # 最多返回3个
            
        except (json.JSONDecodeError, KeyError):
            return self._generate_rule_based_follow_ups(original_query, search_results)
    
    def _summarize_search_results(self, search_results: List[Dict[str, Any]]) -> str:
        """总结搜索结果"""
        summaries = []
        for result in search_results[:3]:  # 只取前3个结果
            summaries.append(f"- {result.get('title', '')}: {result.get('content', '')[:200]}...")
        return "\n".join(summaries)
    
    def _generate_rule_based_follow_ups(self, original_query: str, 
                                      search_results: List[Dict[str, Any]]) -> List[str]:
        """基于规则生成后续查询（备选方案）"""
        
        follow_ups = [
            f"{original_query} 实际应用案例",
            f"{original_query} 最新进展",
            f"{original_query} 相关技术对比"
        ]
        
        return follow_ups[:2]  # 返回前2个