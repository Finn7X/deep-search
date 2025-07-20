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

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行应用
```bash
python main.py
```

### 3. 首次运行
- 系统已预配置Tavily API Key
- 需要输入您的DeepSeek API Key（首次运行时会提示）

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

### API Keys
- **Tavily API**: 已预配置 
- **DeepSeek API**: 需要用户提供

### 环境变量（可选）
```bash
export TAVILY_API_KEY="your_tavily_key"
export DEEPSEEK_API_KEY="your_deepseek_key"
export DEEPSEEK_MODEL="deepseek-chat"
export MAX_SEARCH_RESULTS="10"
```

## 📊 系统架构

### 核心组件
1. **QueryAnalyzer** - 查询分析和改写
2. **SearchPlanner** - 动态搜索策略规划
3. **ReActAgent** - 推理-行动循环框架
4. **DeepSearchEngine** - 核心搜索引擎
5. **TavilySearcher** - 增强搜索客户端
6. **DeepSeekClient** - AI推理客户端

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