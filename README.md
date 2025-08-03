# Deep Search 2.0

真正的深度搜索工具 - 基于ReAct框架的智能搜索系统

## 🚀 功能特性

### 核心能力
- **智能查询分析** - 自动识别查询复杂度并生成搜索变体
- **动态搜索规划** - 基于查询特点动态调整搜索策略
- **ReAct智能代理** - 多轮推理-行动-反思循环
- **多跳搜索支持** - 支持需要多步推理的复杂问题
- **深度结果整合** - 智能去重、过滤和质量评估

### 搜索策略
- **Direct** - 简单直接搜索
- **Multi-angle** - 多角度搜索
- **Sequential** - 序列化深入搜索  
- **Parallel Deep** - 并行深度搜索

## 🛠️ 安装和使用

### 1. 克隆仓库
```bash
git clone https://github.com/Finn7X/deep-search.git
cd deep-search
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置API密钥
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入您的API密钥
nano .env  # 或使用其他编辑器
```

在 `.env` 文件中填入您的API密钥：
```bash
TAVILY_API_KEY=your_tavily_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### 4. 运行应用
```bash
python main.py
```

## 📋 使用示例

### 简单查询
```
什么是量子计算
```
- 自动识别为简单查询
- 使用Direct搜索策略

### 复杂查询
```
量子计算在密码学中的应用和对现有加密系统的影响
```
- 自动识别为复杂查询
- 使用Sequential或Parallel Deep策略
- 多轮ReAct推理

### 多跳推理查询
```
GPT-4相比GPT-3的改进如何影响AI应用的发展趋势
```
- 自动识别为多跳查询
- 执行3-5轮ReAct循环
- 深度知识整合

## 🎯 CLI 命令

- `/help` - 显示详细帮助信息
- `/history` - 查看搜索历史
- `/stats` - 显示会话统计
- `/insights` - 查看最近搜索的深度洞察
- `/config` - 显示当前配置
- `/clear` - 清空会话历史
- `/quit` 或 `/exit` - 退出应用

## 🔧 配置说明

### 获取API密钥

#### Tavily API Key
1. 访问 [Tavily官网](https://tavily.com)
2. 注册账户并获取API Key
3. 将key填入 `.env` 文件中的 `TAVILY_API_KEY`

#### DeepSeek API Key  
1. 访问 [DeepSeek平台](https://platform.deepseek.com)
2. 注册账户并获取API Key
3. 将key填入 `.env` 文件中的 `DEEPSEEK_API_KEY`

### 环境变量配置
所有配置都通过 `.env` 文件管理：
```bash
# 必需的API密钥
TAVILY_API_KEY=your_tavily_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here

# 可选配置
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
MAX_SEARCH_RESULTS=10
MAX_CONVERSATION_HISTORY=20
```

## 📁 项目结构

```
deep-search/
├── src/                    # 源代码目录
│   ├── __init__.py
│   ├── core/              # 核心模块
│   │   ├── __init__.py
│   │   ├── config.py      # 配置管理
│   │   ├── engine.py      # 深度搜索引擎
│   │   └── workflow.py    # 搜索工作流
│   ├── agents/            # 智能代理
│   │   ├── __init__.py
│   │   ├── query_analyzer.py  # 查询分析器
│   │   └── react_agent.py     # ReAct代理框架
│   ├── search/            # 搜索相关
│   │   ├── __init__.py
│   │   ├── planner.py     # 搜索规划器
│   │   └── tavily_search.py   # Tavily搜索客户端
│   └── clients/           # 外部API客户端
│       ├── __init__.py
│       └── deepseek_client.py # DeepSeek API客户端
├── tests/                 # 测试文件
│   ├── __init__.py
│   ├── test_search.py     # 搜索功能测试
│   └── quick_test.py      # 快速测试
├── docs/                  # 文档目录
│   └── Deep-RAG-Implementation-Plan.md
├── main.py               # 应用程序入口点
├── requirements.txt      # Python依赖包
├── CLAUDE.md            # 项目开发指南
└── README.md            # 项目说明文档
```

## 📊 系统架构

### 核心组件
1. **src/core/engine.py** - DeepSearchEngine核心搜索引擎
2. **src/agents/query_analyzer.py** - QueryAnalyzer查询分析和改写
3. **src/search/planner.py** - SearchPlanner动态搜索策略规划
4. **src/agents/react_agent.py** - ReActAgent推理-行动循环框架
5. **src/search/tavily_search.py** - TavilySearcher增强搜索客户端
6. **src/clients/deepseek_client.py** - DeepSeekClient AI推理客户端
7. **src/core/config.py** - 配置管理和环境变量处理

### 模块职责
- **core/** - 核心功能模块，包含主要的搜索引擎和配置
- **agents/** - 智能代理模块，负责查询分析和ReAct推理
- **search/** - 搜索相关模块，包含搜索规划和执行
- **clients/** - 外部服务客户端，处理API通信

### 工作流程
1. 🧠 **查询分析** - 识别复杂度，提取概念，生成变体
2. 📋 **搜索规划** - 选择策略，规划轮次，设置参数
3. 🤖 **ReAct执行** - 推理→行动→观察→反思循环
4. 📊 **结果整合** - 去重、过滤、质量评估、洞察生成

## 🎨 特色功能

### 智能分析
- 自动识别查询复杂度（Simple/Moderate/Complex/Multi-hop）
- 智能提取主要概念和子问题
- 生成多个搜索角度和变体

### 适应性搜索
- 基于查询特点动态调整搜索参数
- 根据中间结果修改搜索策略
- 智能域名选择和结果过滤

### 深度洞察
- 搜索过程分析和效果评估
- ReAct代理性能监控
- 信息发现质量统计

## 🚀 快速开始

1. 克隆项目并安装依赖
2. 运行 `python main.py`
3. 输入您的DeepSeek API Key
4. 开始体验真正的深度搜索！

## 💡 使用建议

- 对于复杂问题，让系统自动运行完整的ReAct循环
- 使用 `/insights` 命令了解搜索过程的深度分析
- 查看搜索历史了解不同复杂度问题的处理方式
- 复杂查询可能需要较长时间，请耐心等待

---

**Deep Search 2.0** - 让搜索更智能，让知识更深入！