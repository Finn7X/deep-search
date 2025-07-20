"""
ReAct代理框架
实现 Reasoning + Acting 的循环：规划 -> 执行 -> 观察 -> 反思
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.table import Table
from rich.live import Live
from rich.text import Text

console = Console()

class AgentState(Enum):
    REASONING = "reasoning"     # 推理分析阶段
    PLANNING = "planning"       # 制定行动计划
    ACTING = "acting"          # 执行搜索行动
    OBSERVING = "observing"    # 观察搜索结果
    REFLECTING = "reflecting"  # 反思和评估
    CONCLUDED = "concluded"    # 得出结论

@dataclass
class AgentAction:
    action_type: str           # search, analyze, synthesize, conclude
    parameters: Dict[str, Any]
    reasoning: str
    expected_outcome: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class AgentObservation:
    action: AgentAction
    results: Dict[str, Any]
    success: bool
    insights: List[str]
    new_questions: List[str]
    confidence_score: float    # 0-1, 对结果的信心程度
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class AgentReflection:
    observations: List[AgentObservation]
    summary: str
    knowledge_gaps: List[str]
    next_actions: List[str]
    should_continue: bool
    overall_progress: float    # 0-1, 整体进度
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

class ReActAgent:
    def __init__(self, deepseek_client, tavily_searcher):
        self.deepseek_client = deepseek_client
        self.tavily_searcher = tavily_searcher
        self.state = AgentState.REASONING
        
        # 代理记忆
        self.memory = {
            "original_query": "",
            "accumulated_knowledge": "",
            "action_history": [],
            "observation_history": [],
            "reflection_history": [],
            "current_round": 0,
            "max_rounds": 5
        }
        
        # 配置参数
        self.config = {
            "max_search_rounds": 5,
            "confidence_threshold": 0.8,
            "knowledge_sufficiency_threshold": 0.7,
            "max_tokens_per_reasoning": 2000
        }
    
    def execute_deep_search(self, original_query: str, query_analysis: Any, 
                          search_plan: Any) -> Dict[str, Any]:
        """
        执行完整的深度搜索ReAct循环
        """
        console.print(Panel(
            f"[bold magenta]🤖 启动ReAct代理[/bold magenta]\n"
            f"[cyan]原始查询:[/cyan] {original_query}\n"
            f"[cyan]搜索策略:[/cyan] {search_plan.strategy.value}\n"
            f"[cyan]最大轮次:[/cyan] {self.config['max_search_rounds']}",
            title="ReAct Deep Search 开始",
            border_style="magenta"
        ))
        
        # 初始化代理记忆
        self.memory["original_query"] = original_query
        self.memory["query_analysis"] = query_analysis
        self.memory["search_plan"] = search_plan
        self.memory["start_time"] = datetime.now().isoformat()
        
        # 开始ReAct循环
        final_result = self._react_loop()
        
        # 生成最终报告
        final_report = self._generate_final_report(final_result)
        
        console.print(Panel(
            f"[bold green]✅ ReAct搜索完成[/bold green]\n"
            f"[cyan]总轮次:[/cyan] {self.memory['current_round']}\n"
            f"[cyan]最终状态:[/cyan] {self.state.value}\n"
            f"[cyan]知识积累:[/cyan] {len(self.memory['accumulated_knowledge'])} 字符",
            title="ReAct 完成总结",
            border_style="green"
        ))
        
        return final_report
    
    def _react_loop(self) -> Dict[str, Any]:
        """
        核心ReAct循环：Reasoning + Acting
        """
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console,
            expand=True
        ) as progress:
            
            task = progress.add_task("ReAct Deep Search 进行中...", total=self.config["max_search_rounds"])
            
            while (self.memory["current_round"] < self.config["max_search_rounds"] and 
                   self.state != AgentState.CONCLUDED):
                
                self.memory["current_round"] += 1
                round_num = self.memory["current_round"]
                
                progress.update(task, description=f"第 {round_num} 轮 ReAct 循环", advance=1)
                
                console.print(f"\n{'='*60}")
                console.print(f"[bold yellow]🔄 第 {round_num} 轮 ReAct 循环[/bold yellow]")
                console.print(f"{'='*60}")
                
                # 1. Reasoning: 推理和规划
                self.state = AgentState.REASONING
                reasoning_result = self._reasoning_phase()
                
                if not reasoning_result["should_continue"]:
                    self.state = AgentState.CONCLUDED
                    break
                
                # 2. Acting: 执行行动
                self.state = AgentState.ACTING
                action = reasoning_result["planned_action"]
                observation = self._acting_phase(action)
                
                # 3. Observing & Reflecting: 观察和反思
                self.state = AgentState.REFLECTING
                reflection = self._reflecting_phase([observation])
                
                # 检查是否应该继续
                if not reflection.should_continue or reflection.overall_progress >= 0.9:
                    self.state = AgentState.CONCLUDED
                    break
        
        return self._finalize_results()
    
    def _reasoning_phase(self) -> Dict[str, Any]:
        """
        推理阶段：分析当前状况，规划下一步行动
        """
        console.print(Panel(
            "[bold blue]🧠 推理分析阶段[/bold blue]",
            title=f"第 {self.memory['current_round']} 轮 - 推理",
            border_style="blue"
        ))
        
        # 构建推理提示词
        reasoning_prompt = self._build_reasoning_prompt()
        
        # 调用AI进行推理
        response = self.deepseek_client.chat_completion(
            messages=[{"role": "user", "content": reasoning_prompt}],
            stream=False,
            temperature=0.3,
            max_tokens=self.config["max_tokens_per_reasoning"]
        )
        
        if "error" in response:
            # 如果AI推理失败，使用规则推理
            return self._rule_based_reasoning()
        
        try:
            # 清理响应内容，移除可能的markdown格式
            content = response["content"].strip()
            if content.startswith("```json"):
                content = content[7:]  # 移除开头的 ```json
            if content.endswith("```"):
                content = content[:-3]  # 移除结尾的 ```
            content = content.strip()
            
            reasoning_data = json.loads(content)
            return self._parse_reasoning_response(reasoning_data)
        except (json.JSONDecodeError, KeyError):
            return self._rule_based_reasoning()
    
    def _build_reasoning_prompt(self) -> str:
        """构建推理提示词"""
        
        prompt = f"""
你是一个专业的深度搜索ReAct代理。请分析当前情况并规划下一步行动。

## 原始查询
{self.memory["original_query"]}

## 当前轮次
第 {self.memory["current_round"]} 轮 (最大 {self.config["max_search_rounds"]} 轮)

## 已积累的知识
{self.memory.get("accumulated_knowledge", "暂无")}

## 历史行动摘要
{self._summarize_action_history()}

## 上一轮观察结果
{self._summarize_recent_observations()}

## 任务要求
请分析当前情况，判断是否需要继续搜索，如果需要，请规划下一步最有价值的搜索行动。

请返回JSON格式的推理结果：
{{
    "current_understanding": "对问题的当前理解程度 (0-1)",
    "knowledge_gaps": ["知识缺口1", "知识缺口2"],
    "should_continue": true/false,
    "reasoning": "详细的推理过程",
    "planned_action": {{
        "action_type": "search/analyze/synthesize",
        "parameters": {{
            "queries": ["查询1", "查询2"],
            "search_depth": "basic/advanced",
            "focus_areas": ["重点领域1", "领域2"]
        }},
        "reasoning": "为什么要执行这个行动",
        "expected_outcome": "期望获得什么结果"
    }}
}}

判断标准：
1. 如果对原始查询的理解度 >= 0.8，考虑结束搜索
2. 如果发现重要知识缺口，继续搜索
3. 如果已达到最大轮次，必须结束
4. 优先填补最关键的知识缺口
"""
        return prompt
    
    def _parse_reasoning_response(self, reasoning_data: Dict[str, Any]) -> Dict[str, Any]:
        """解析推理响应"""
        
        understanding = reasoning_data.get("current_understanding", 0.5)
        should_continue = reasoning_data.get("should_continue", True)
        
        # 记录推理结果
        console.print(Panel(
            f"[bold green]✅ 推理完成[/bold green]\n"
            f"[cyan]理解程度:[/cyan] {understanding:.1%}\n"
            f"[cyan]是否继续:[/cyan] {'是' if should_continue else '否'}\n"
            f"[cyan]知识缺口:[/cyan] {len(reasoning_data.get('knowledge_gaps', []))} 个",
            title="推理结果",
            border_style="green"
        ))
        
        if reasoning_data.get("knowledge_gaps"):
            console.print(Panel(
                "\\n".join([f"• {gap}" for gap in reasoning_data["knowledge_gaps"]]),
                title="🎯 知识缺口",
                border_style="yellow"
            ))
        
        return reasoning_data
    
    def _rule_based_reasoning(self) -> Dict[str, Any]:
        """基于规则的推理（AI推理失败时的备选方案）"""
        
        round_num = self.memory["current_round"]
        
        # 简单规则：前3轮继续搜索，之后根据知识积累决定
        should_continue = round_num <= 3 or len(self.memory["accumulated_knowledge"]) < 1000
        
        return {
            "current_understanding": min(round_num * 0.2, 0.8),
            "knowledge_gaps": [f"第{round_num}轮知识补充"],
            "should_continue": should_continue,
            "reasoning": "基于规则的推理决策",
            "planned_action": {
                "action_type": "search",
                "parameters": {
                    "queries": [self.memory["original_query"] + f" 第{round_num}轮"],
                    "search_depth": "advanced",
                    "focus_areas": ["基础信息"]
                },
                "reasoning": "继续收集相关信息",
                "expected_outcome": "获得更多相关知识"
            }
        }
    
    def _acting_phase(self, action: Dict[str, Any]) -> AgentObservation:
        """
        执行阶段：执行规划的搜索行动
        """
        console.print(Panel(
            f"[bold green]🎯 执行搜索行动[/bold green]\n"
            f"[cyan]行动类型:[/cyan] {action.get('action_type', 'search')}\n"
            f"[cyan]查询数量:[/cyan] {len(action.get('parameters', {}).get('queries', []))}",
            title=f"第 {self.memory['current_round']} 轮 - 执行",
            border_style="green"
        ))
        
        agent_action = AgentAction(
            action_type=action.get("action_type", "search"),
            parameters=action.get("parameters", {}),
            reasoning=action.get("reasoning", ""),
            expected_outcome=action.get("expected_outcome", "")
        )
        
        # 执行搜索
        search_results = []
        queries = action.get("parameters", {}).get("queries", [])
        
        for query in queries:
            console.print(f"[cyan]🔍 搜索查询:[/cyan] {query}")
            
            result = self.tavily_searcher.search(
                query=query,
                search_depth=action.get("parameters", {}).get("search_depth", "advanced")
            )
            
            if not result.get("error"):
                search_results.extend(result.get("results", []))
        
        # 分析搜索结果，提取洞察
        insights, new_questions, confidence = self._analyze_search_results(search_results, agent_action)
        
        observation = AgentObservation(
            action=agent_action,
            results={"search_results": search_results, "total_results": len(search_results)},
            success=len(search_results) > 0,
            insights=insights,
            new_questions=new_questions,
            confidence_score=confidence
        )
        
        # 更新记忆
        self.memory["action_history"].append(agent_action)
        self.memory["observation_history"].append(observation)
        
        console.print(Panel(
            f"[bold green]✅ 行动执行完成[/bold green]\n"
            f"[cyan]搜索结果:[/cyan] {len(search_results)} 条\n"
            f"[cyan]新洞察:[/cyan] {len(insights)} 个\n"
            f"[cyan]信心度:[/cyan] {confidence:.1%}",
            title="执行结果",
            border_style="green"
        ))
        
        return observation
    
    def _analyze_search_results(self, search_results: List[Dict[str, Any]], 
                              action: AgentAction) -> Tuple[List[str], List[str], float]:
        """分析搜索结果，提取洞察和新问题"""
        
        if not search_results:
            return [], ["搜索结果为空，需要调整搜索策略"], 0.1
        
        # 简单的结果分析（实际应用中可以使用更复杂的NLP分析）
        insights = []
        new_questions = []
        
        # 统计高质量结果
        high_quality_results = [r for r in search_results if r.get("score", 0) > 0.7]
        
        if high_quality_results:
            insights.append(f"找到 {len(high_quality_results)} 个高质量结果")
            
            # 提取主要主题
            titles = [r.get("title", "") for r in high_quality_results[:3]]
            insights.append(f"主要主题涉及: {', '.join(titles)}")
        
        # 基于结果数量和质量计算信心度
        confidence = min(len(high_quality_results) / 5.0, 1.0)
        
        # 生成新问题
        if confidence < 0.6:
            new_questions.append("需要更具体的搜索词")
            new_questions.append("考虑从不同角度搜索")
        
        return insights, new_questions, confidence
    
    def _reflecting_phase(self, observations: List[AgentObservation]) -> AgentReflection:
        """
        反思阶段：评估观察结果，决定下一步策略
        """
        console.print(Panel(
            "[bold purple]🤔 反思评估阶段[/bold purple]",
            title=f"第 {self.memory['current_round']} 轮 - 反思",
            border_style="purple"
        ))
        
        # 更新积累的知识
        self._update_accumulated_knowledge(observations)
        
        # 评估整体进度
        overall_progress = self._evaluate_progress()
        
        # 识别知识缺口
        knowledge_gaps = self._identify_knowledge_gaps()
        
        # 决定是否继续
        should_continue = (
            overall_progress < 0.8 and 
            self.memory["current_round"] < self.config["max_search_rounds"] and
            len(knowledge_gaps) > 0
        )
        
        reflection = AgentReflection(
            observations=observations,
            summary=f"第{self.memory['current_round']}轮收集了{sum(len(obs.results.get('search_results', [])) for obs in observations)}条搜索结果",
            knowledge_gaps=knowledge_gaps,
            next_actions=["继续深入搜索"] if should_continue else ["准备总结结论"],
            should_continue=should_continue,
            overall_progress=overall_progress
        )
        
        self.memory["reflection_history"].append(reflection)
        
        console.print(Panel(
            f"[bold purple]✅ 反思完成[/bold purple]\n"
            f"[cyan]整体进度:[/cyan] {overall_progress:.1%}\n"
            f"[cyan]知识缺口:[/cyan] {len(knowledge_gaps)} 个\n"
            f"[cyan]是否继续:[/cyan] {'是' if should_continue else '否'}",
            title="反思结果",
            border_style="purple"
        ))
        
        return reflection
    
    def _update_accumulated_knowledge(self, observations: List[AgentObservation]):
        """更新积累的知识"""
        
        for obs in observations:
            search_results = obs.results.get("search_results", [])
            for result in search_results[:3]:  # 只取前3个高质量结果
                content = result.get("content", "")[:500]  # 限制长度
                if content:
                    self.memory["accumulated_knowledge"] += f"\\n\\n{content}"
        
        # 限制总知识长度
        if len(self.memory["accumulated_knowledge"]) > 10000:
            self.memory["accumulated_knowledge"] = self.memory["accumulated_knowledge"][-8000:]
    
    def _evaluate_progress(self) -> float:
        """评估整体搜索进度"""
        
        # 基于轮次、知识积累量、信心度等因素评估进度
        round_progress = self.memory["current_round"] / self.config["max_search_rounds"]
        knowledge_progress = min(len(self.memory["accumulated_knowledge"]) / 5000, 1.0)
        
        # 计算平均信心度
        recent_observations = self.memory["observation_history"][-3:]  # 最近3次观察
        avg_confidence = 0.5
        if recent_observations:
            avg_confidence = sum(obs.confidence_score for obs in recent_observations) / len(recent_observations)
        
        overall_progress = (round_progress * 0.3 + knowledge_progress * 0.4 + avg_confidence * 0.3)
        return min(overall_progress, 1.0)
    
    def _identify_knowledge_gaps(self) -> List[str]:
        """识别当前知识缺口"""
        
        gaps = []
        
        # 基于最近的观察识别缺口
        recent_observations = self.memory["observation_history"][-2:]
        
        for obs in recent_observations:
            if obs.confidence_score < 0.6:
                gaps.append("搜索结果质量需要提升")
            
            gaps.extend(obs.new_questions[:2])  # 添加新问题作为知识缺口
        
        # 去重
        unique_gaps = list(dict.fromkeys(gaps))
        return unique_gaps[:3]  # 最多返回3个主要缺口
    
    def _finalize_results(self) -> Dict[str, Any]:
        """整理最终搜索结果"""
        
        return {
            "original_query": self.memory["original_query"],
            "total_rounds": self.memory["current_round"],
            "final_state": self.state.value,
            "accumulated_knowledge": self.memory["accumulated_knowledge"],
            "action_history": self.memory["action_history"],
            "observation_history": self.memory["observation_history"],
            "reflection_history": self.memory["reflection_history"],
            "final_progress": self._evaluate_progress(),
            "end_time": datetime.now().isoformat()
        }
    
    def _generate_final_report(self, react_results: Dict[str, Any]) -> Dict[str, Any]:
        """生成最终的深度搜索报告"""
        
        # 收集所有搜索结果
        all_search_results = []
        for obs in react_results["observation_history"]:
            all_search_results.extend(obs.results.get("search_results", []))
        
        # 生成AI总结
        summary = self._generate_ai_summary(react_results)
        
        return {
            "query": react_results["original_query"],
            "summary": summary,
            "total_search_rounds": react_results["total_rounds"],
            "total_search_results": len(all_search_results),
            "search_results": all_search_results,
            "accumulated_knowledge": react_results["accumulated_knowledge"],
            "execution_details": {
                "actions": len(react_results["action_history"]),
                "observations": len(react_results["observation_history"]),
                "reflections": len(react_results["reflection_history"]),
                "final_progress": react_results["final_progress"]
            },
            "timestamp": react_results["end_time"]
        }
    
    def _generate_ai_summary(self, react_results: Dict[str, Any]) -> str:
        """使用AI生成最终总结"""
        
        summary_prompt = f"""
基于以下深度搜索过程和结果，请生成一个全面、准确的回答。

原始问题: {react_results["original_query"]}

搜索过程概述:
- 总共进行了 {react_results["total_rounds"]} 轮ReAct搜索
- 积累的知识: {len(react_results["accumulated_knowledge"])} 字符
- 最终进度: {react_results["final_progress"]:.1%}

积累的知识内容:
{react_results["accumulated_knowledge"][:3000]}...

请基于以上信息提供一个详细、准确且有用的回答。要求：
1. 直接回答原始问题
2. 提供具体的事实和数据
3. 指出信息来源的可靠性
4. 如有不确定的地方，请明确说明
5. 总结要结构清晰、逻辑连贯
"""
        
        response = self.deepseek_client.chat_completion(
            messages=[{"role": "user", "content": summary_prompt}],
            stream=False,
            temperature=0.2
        )
        
        if "error" in response:
            return f"基于 {react_results['total_rounds']} 轮深度搜索，收集了相关信息，但AI总结生成失败。请查看详细搜索结果。"
        
        return response.get("content", "总结生成失败")
    
    def _summarize_action_history(self) -> str:
        """总结历史行动"""
        actions = self.memory["action_history"]
        if not actions:
            return "暂无历史行动"
        
        summary = []
        for i, action in enumerate(actions[-3:], 1):  # 只显示最近3个行动
            summary.append(f"{i}. {action.action_type}: {action.reasoning[:100]}...")
        
        return "\\n".join(summary)
    
    def _summarize_recent_observations(self) -> str:
        """总结最近的观察结果"""
        observations = self.memory["observation_history"]
        if not observations:
            return "暂无观察结果"
        
        recent_obs = observations[-2:]  # 最近2次观察
        summary = []
        
        for obs in recent_obs:
            result_count = len(obs.results.get("search_results", []))
            summary.append(f"搜索结果: {result_count} 条, 信心度: {obs.confidence_score:.1%}")
        
        return "\\n".join(summary)