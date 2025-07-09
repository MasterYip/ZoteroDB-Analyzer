# ZoteroDB-Analyzer

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Zotero 数据库分析器，用于快速构建文献综述 - 一个全面的 Python 包，用于分析 Zotero 数据库并为 LLM 代理生成结构化的文献综述。

## 功能特性

### 🔍 **全面的 Zotero 集成**

- 从个人或团队 Zotero 库中获取文献项目
- 通过标签、集合、作者、关键词、日期范围和项目类型进行高级过滤
- 完整的元数据提取，包括摘要、DOI、BibTeX 引文
- 在整个文献库中搜索功能

### 📊 **智能文献分类**

- 基于用户定义关键词的自动分类
- 支持多种分类方案
- 智能内容分析，用于分组相关论文

### 📝 **LLM 优化的导出格式**

- **JSON 格式**，用于结构化数据处理
- **Markdown 格式**，优化用于 LLM 消费
- **专用上下文文件**，用于文献综述撰写
- 支持单个项目和分类集合

### 🤖 **代理集成**

- **模型上下文协议 (MCP) 接口**，用于无缝代理集成
- 用于获取、分类和导出文献数据的工具
- 专为与 Claude、GPT-4 和其他 LLM 代理一起使用而设计
- 完美适用于自动文献综述生成

## 安装

### 从 PyPI 安装（发布后）

```bash
pip install zoterodb-analyzer
```

### 开发版本

```bash
git clone https://github.com/MasterYip/ZoteroDB-Analyzer.git
cd ZoteroDB-Analyzer
pip install -e .
```

### 带 MCP 支持

```bash
pip install zoterodb-analyzer[mcp]
```

## 快速开始

设置 Zotero 凭据：

```bash
# Linux Bash
export ZOTERO_API_KEY="your_api_key"
export ZOTERO_LIBRARY_ID="your_user_id"
# Windows Cmd
set ZOTERO_API_KEY="your_api_key"
set ZOTERO_LIBRARY_ID="your_user_id"
# Windows PowerShell
$env:ZOTERO_LIBRARY_ID='your_user_id'
$env:ZOTERO_API_KEY='your_api_key'
```

运行示例：

```bash
python examples/basic_usage.py
```

尝试 CLI：

```bash
zoterodb-analyzer --help
```

## 使用方法

### 1. 设置 Zotero API 访问

首先，获取您的 [Zotero API](https://www.zotero.org/support/dev/web_api/v3/start) 凭据：

1. `your_api_key`：前往 [Zotero 设置](https://www.zotero.org/settings/keys) 创建具有库访问权限的新私钥。
2. `your_user_id`：前往您的用户配置文件，URL 为 `https://www.zotero.org/<your_user_name>/<your_user_id>`。

### 2. 配置环境变量

#### Windows 命令提示符

```cmd
set ZOTERO_LIBRARY_ID=your_user_id
set ZOTERO_API_KEY=your_api_key
```

#### Windows PowerShell

```powershell
$env:ZOTERO_LIBRARY_ID='your_user_id'
$env:ZOTERO_API_KEY='your_api_key'
```

#### Windows 永久环境变量

1. 按 `Win+R`，输入 `sysdm.cpl`，按回车
2. 进入高级 > 环境变量
3. 添加 `ZOTERO_LIBRARY_ID` 和 `ZOTERO_API_KEY` 作为新变量

#### Linux/macOS

```bash
export ZOTERO_LIBRARY_ID='your_user_id'
export ZOTERO_API_KEY='your_api_key'
```

要使其永久生效，请添加到 `~/.bashrc` 或 `~/.zshrc`：

```bash
echo 'export ZOTERO_LIBRARY_ID="your_user_id"' >> ~/.bashrc
echo 'export ZOTERO_API_KEY="your_api_key"' >> ~/.bashrc
```

### 3. 基本使用

```python
from zoterodb_analyzer import ZoteroAnalyzer, ContentExporter, FilterCriteria, LiteratureCategory

# 初始化分析器
analyzer = ZoteroAnalyzer(
    library_id="your_user_id",
    library_type="user",  # 或 "group"
    api_key="your_api_key"
)

# 使用过滤器获取项目
filter_criteria = FilterCriteria(
    tags=["machine learning", "robotics"],
    date_range=(2020, 2024),
    item_types=[ItemType.JOURNAL_ARTICLE]
)

items = analyzer.fetch_items(filter_criteria, limit=50)
print(f"找到 {len(items)} 个项目")

# 导出供 LLM 使用
exporter = ContentExporter("output")
exported_files = exporter.export_items(items, format=ExportFormat.MARKDOWN)
print(f"导出到: {exported_files['markdown']}")
```

### 4. 高级分类

```python
# 定义文献类别
categories = [
    LiteratureCategory(
        name="扩散模型",
        description="机器人学中的扩散模型论文",
        keywords=["diffusion", "denoising", "generative model"]
    ),
    LiteratureCategory(
        name="强化学习",
        description="机器人控制的强化学习方法",
        keywords=["reinforcement learning", "policy gradient", "Q-learning"]
    )
]

# 分类项目
categorized_items = analyzer.categorize_items(items, categories)

# 导出分类文献供 LLM 使用
exported_files = exporter.export_categorized_items(
    categorized_items, 
    format=ExportFormat.BOTH
)

# 创建 LLM 优化的上下文文件
llm_context = exporter.export_for_llm_context(
    categorized_items, 
    context_type="related_works"
)
```

## 命令行界面

该包包含一个功能强大的 CLI，便于自动化：

```bash
# 获取并导出文献
zoterodb-analyzer fetch \
    --library-id YOUR_USER_ID \
    --api-key YOUR_API_KEY \
    --tags "machine learning,robotics" \
    --year-range 2020-2024 \
    --format both \
    --categories-file categories.json

# 列出可用集合
zoterodb-analyzer collections --library-id YOUR_USER_ID --api-key YOUR_API_KEY

# 搜索您的库
zoterodb-analyzer search \
    --library-id YOUR_USER_ID \
    --api-key YOUR_API_KEY \
    --query "deep learning" \
    --limit 20
```

### 类别文件格式

创建一个 `categories.json` 文件来定义您的文献类别：

```json
[
  {
    "name": "扩散模型",
    "description": "关于扩散模型和生成方法的论文",
    "keywords": ["diffusion", "denoising", "DDPM", "score-based"]
  },
  {
    "name": "机器人学习",
    "description": "机器人学习方法",
    "keywords": ["robot learning", "imitation learning", "demonstration"]
  }
]
```

## LLM 代理的 MCP 集成

该包为 LLM 代理提供了模型上下文协议服务器，实现无缝集成：

```python
from zoterodb_analyzer.mcp_server import ZoteroMCPServer

# 初始化 MCP 服务器
mcp_server = ZoteroMCPServer(
    default_library_id="your_user_id",
    default_api_key="your_api_key"
)

# 代理可用的工具：
# - fetch_literature: 使用过滤器获取文献
# - categorize_literature: 分类和导出文献
# - search_literature: 搜索库内容
# - get_collections: 列出可用集合
# - get_tags: 获取库标签
# - export_for_llm: 创建 LLM 优化的导出
```

### 🔧 **VS Code Copilot MCP 配置**

![MCP 演示](doc/mcp_demo.png)

要将 ZoteroDB Analyzer 与 VS Code Copilot 集成，请按照以下步骤操作：

#### 1. **准备 MCP 服务器**

首先，确保包已安装：

```bash
# 安装包
pip install -e .
```

#### 2. **配置 VS Code Github Copilot**

将以下配置添加到您的 VS Code Copilot 设置中。打开您的 VS Code 设置并添加此 MCP 服务器配置：

```json
{
  "mcp": {
    "servers": {
      "MCP_ZoteroDB": {
        "type": "stdio",
        "command": "python",
        "args": [
          "E:\\<path-to-this-pkg>\\mcp_server_runner.py"
        ],
        "env": {
          "ZOTERO_LIBRARY_ID": "your_user_id",
          "ZOTERO_API_KEY": "your_api_key"
        }
      }
    }
  }
}
```

**⚠️ 重要提示：**

- 将 `your_user_id` 和 `your_api_key` 替换为您的实际 Zotero 凭据
- 在 JSON 配置中，Windows 路径使用双反斜杠 `\\`
- 保持您的 API 密钥安全，考虑使用环境变量而不是硬编码

#### 3. **替代方案：使用环境变量**

为了更好的安全性，您可以配置 MCP 服务器使用系统环境变量：

```json
{
  "mcp": {
    "servers": {
      "MCP_ZoteroDB": {
        "type": "stdio",
        "command": "python",
        "args": [
          "E:\\<path-to-this-pkg>\\mcp_server_runner.py"
        ]
      }
    }
  }
}
```

然后将您的凭据设置为系统环境变量（如上述环境变量部分所述）。

#### 4. **测试集成**

配置完成后，重启 VS Code Copilot。然后您可以在对话中使用以下 MCP 工具：

- **`fetch_literature`** - 从您的 Zotero 库中搜索和检索论文
- **`categorize_literature`** - 自动分类论文以进行文献综述
- **`search_literature`** - 使用文本查询搜索您的库
- **`get_collections`** - 列出您的 Zotero 集合
- **`get_tags`** - 从您的库中获取所有标签
- **`export_for_llm`** - 以 LLM 优化格式导出文献

#### 5. **与 Copilot 的示例使用**

配置完成后，您可以向 Copilot 询问诸如：

- *"在我的 Zotero 库中搜索关于扩散模型的论文"*
- *"为文献综述分类我最近的机器学习论文"*
- *"在我的库中查找 [作者姓名] 的论文"*
- *"以 Markdown 格式导出关于机器人学的论文供我的论文使用"*

MCP 服务器将自动处理请求并提供结构化的文献数据，Copilot 可以使用这些数据来帮助您进行研究和写作任务。

### 🧪 **测试 MCP 服务器**

您可以在与 Copilot 集成之前测试 MCP 服务器功能：

```bash
# 直接测试 MCP 服务器
python test_mcp_client.py

# 手动运行 MCP 服务器
python mcp_server_runner.py
```

## 环境变量

设置环境变量以便于使用：

```bash
export ZOTERO_API_KEY="your_api_key"
export ZOTERO_LIBRARY_ID="your_user_id"
export ZOTERO_LIBRARY_TYPE="user"  # 或 "group"
```

## 使用场景

### 📚 **学术文献综述**

- 根据研究主题自动分类论文
- 为相关工作章节生成结构化内容
- 提取关键元数据和摘要进行分析

### 🤖 **代理辅助研究**

- 为 LLM 代理提供结构化的文献上下文
- 使代理能够查询和分析您的研究库
- 自动化文献综述生成

### 📊 **研究分析**

- 分析不同时间段的研究趋势
- 识别关键作者和出版场所
- 跟踪引用模式和关系

## API 参考

### 核心类

- **`ZoteroAnalyzer`**: 用于获取和分析 Zotero 数据的主类
- **`ContentExporter`**: 处理导出为各种格式
- **`FilterCriteria`**: 定义文献搜索的过滤参数
- **`LiteratureCategory`**: 表示组织文献的类别
- **`ZoteroItem`**: 表示带有元数据的单个文献项目

### 主要方法

- `fetch_items()`: 使用可选过滤器检索项目
- `categorize_items()`: 将项目组织为预定义类别
- `search_items()`: 使用文本查询搜索库
- `export_items()`: 以 JSON/Markdown 格式导出项目
- `export_for_llm_context()`: 创建 LLM 优化的上下文文件

## 贡献

我们欢迎贡献！请参阅我们的[贡献指南](CONTRIBUTING.md)了解详细信息。

1. Fork 存储库
2. 创建功能分支
3. 进行更改
4. 添加测试
5. 提交拉取请求

## 许可证

本项目根据 MIT 许可证授权 - 有关详细信息，请参阅 [LICENSE](LICENSE) 文件。

## 引用

如果您在研究中使用 ZoteroDB-Analyzer，请引用：

```bibtex
@software{zoterodb_analyzer,
  title={ZoteroDB-Analyzer: A Python Package for Literature Review Automation},
  author={Raymon Yip},
  year={2024},
  url={https://github.com/MasterYip/ZoteroDB-Analyzer}
}
```

## 支持

- 📖 **文档**: [文档链接]
- 🐛 **错误报告**: [GitHub Issues](https://github.com/MasterYip/ZoteroDB-Analyzer/issues)
- 💬 **讨论**: [GitHub Discussions](https://github.com/MasterYip/ZoteroDB-Analyzer/discussions)
- 📧 **联系**: <contact@zoterodb-analyzer.com>

## 路线图

- [ ] 面向非技术用户的 Web 界面
- [ ] 与其他参考管理器集成
- [ ] 高级引用网络分析
- [ ] 自动文献趋势检测
- [ ] 全文分析支持
