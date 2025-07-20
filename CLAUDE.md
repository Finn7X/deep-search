# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Deep Search 2.0 is an advanced Python application that implements true deep search capabilities using ReAct (Reasoning + Acting) framework. It combines intelligent query analysis, dynamic search planning, multi-hop reasoning, and comprehensive result integration to provide sophisticated search and analysis capabilities.

## Development Commands

- **Install dependencies**: `pip install -r requirements.txt`
- **Run the application**: `python main.py`
- **Run with Python 3 explicitly**: `python3 main.py`

## Core Dependencies

- **tavily-python**: Tavily search API client for web search
- **openai**: Used for DeepSeek API integration (compatible with OpenAI API format)
- **python-dotenv**: Environment variable management
- **rich**: Advanced terminal UI and formatting

## Code Architecture

### Core Components

- **main.py**: Main application with Deep Search 2.0 CLI interface
- **config.py**: Configuration management and API key handling
- **deep_search_engine.py**: Core engine that orchestrates the entire deep search process
- **query_analyzer.py**: Intelligent query analysis and rewriting module
- **search_planner.py**: Dynamic search strategy planning based on query complexity
- **react_agent.py**: ReAct framework implementation (Reasoning + Acting cycles)
- **tavily_search.py**: Enhanced Tavily search integration with detailed logging
- **deepseek_client.py**: DeepSeek API client with streaming and conversation support

### Deep Search 2.0 Features

#### 1. Intelligent Query Analysis
- **Complexity Detection**: Automatically identifies query complexity (simple/moderate/complex/multi_hop)
- **Concept Extraction**: Extracts main concepts and generates sub-questions
- **Search Variants**: Creates multiple search query variations for comprehensive coverage
- **Multi-hop Recognition**: Identifies queries requiring multi-step reasoning

#### 2. Dynamic Search Planning
- **Strategy Selection**: Chooses optimal search strategy based on query analysis
  - Direct: Single straightforward search
  - Multi-angle: Multiple perspectives on the same topic  
  - Sequential: Step-by-step exploration
  - Parallel Deep: Concurrent multi-dimensional search
- **Parameter Optimization**: Dynamically adjusts search depth, result count, domain preferences
- **Adaptive Planning**: Modifies search plan based on intermediate results

#### 3. ReAct Agent Framework
- **Reasoning Phase**: Analyzes current situation and plans next actions
- **Acting Phase**: Executes planned search actions
- **Observing Phase**: Analyzes search results and extracts insights
- **Reflecting Phase**: Evaluates progress and decides whether to continue
- **Multi-round Cycles**: Supports up to 5 reasoning-acting cycles for complex queries

#### 4. Advanced Result Processing
- **Deduplication**: Removes duplicate results based on URL and content similarity
- **Quality Filtering**: Filters results based on relevance scores and content quality
- **Knowledge Integration**: Accumulates and synthesizes knowledge across search rounds
- **Source Diversity**: Ensures results come from diverse, authoritative sources

#### 5. Comprehensive Insights
- **Process Analytics**: Detailed analysis of search complexity and strategy effectiveness
- **Performance Metrics**: ReAct agent performance, information discovery statistics
- **Quality Assessment**: Average relevance scores, source diversity, knowledge accumulation

### Configuration

The application uses the following configuration:
- Tavily API key: `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`
- DeepSeek API key: `sk-dfe52d327a2b4cce839a1ffde2c243cc`
- DeepSeek model: `deepseek-chat`
- Max search results: 10-15 (dynamically adjusted)
- ReAct max rounds: 5
- Quality threshold: 0.6

### CLI Commands

- `/help`: Show comprehensive help and feature overview
- `/history`: Display search history with complexity analysis
- `/stats`: Show session statistics (searches, rounds, results, AI calls)
- `/config`: Display current configuration and component status
- `/insights`: Show detailed insights from the latest search
- `/clear`: Clear session history
- `/quit` or `/exit`: Exit the application

### Usage Examples

#### Simple Query
Input: "什么是量子计算"
- Complexity: Simple
- Strategy: Direct search
- Expected rounds: 1

#### Complex Query  
Input: "量子计算在密码学中的应用和对现有加密系统的影响"
- Complexity: Complex
- Strategy: Sequential or Parallel Deep
- Expected rounds: 2-3
- Features: Multi-angle analysis, expert-level search

#### Multi-hop Query
Input: "GPT-4相比GPT-3的改进如何影响AI应用的发展趋势"
- Complexity: Multi-hop
- Strategy: Parallel Deep
- Expected rounds: 3-5
- Features: Multi-step reasoning, knowledge synthesis

### Environment Variables

Optional environment variables:
- `TAVILY_API_KEY`: Tavily search API key
- `DEEPSEEK_API_KEY`: DeepSeek API key  
- `DEEPSEEK_BASE_URL`: DeepSeek API endpoint (default: https://api.deepseek.com)
- `DEEPSEEK_MODEL`: Model name (default: deepseek-chat)
- `MAX_SEARCH_RESULTS`: Maximum search results (default: 10)
- `MAX_CONVERSATION_HISTORY`: Maximum conversation messages (default: 20)

## Development Notes

- The system automatically handles query complexity analysis - no manual parameter specification needed
- ReAct agent provides detailed logging of reasoning processes
- All components include comprehensive error handling and fallback mechanisms
- Rich terminal interface provides real-time feedback on search progress
- Results include both immediate answers and deep analytical insights