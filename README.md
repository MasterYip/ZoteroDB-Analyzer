# ZoteroDB-Analyzer

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Languages**: [English](README.md) | [中文](README_zh.md)

Zotero Database Analyzer for Literature Review Fast Composing - A comprehensive Python package for analyzing Zotero databases and generating structured literature reviews for LLM agents.

## Features

### 🔍 **Comprehensive Zotero Integration**

- Fetch literature items from personal or group Zotero libraries
- Advanced filtering by tags, collections, authors, keywords, date ranges, and item types
- Full metadata extraction including abstracts, DOIs, BibTeX citations
- Search functionality across your entire library

### 📊 **Intelligent Literature Categorization**

- Automatic categorization based on user-defined keywords
- Support for multiple classification schemes
- Smart content analysis for grouping related papers

### 📝 **LLM-Optimized Export Formats**

- **JSON format** for structured data processing
- **Markdown format** optimized for LLM consumption
- **Specialized context files** for literature review composition
- Support for both individual items and categorized collections

### 🤖 **Agent Integration**

- **Model Context Protocol (MCP) interface** for seamless agent integration
- Tools for fetching, categorizing, and exporting literature data
- Designed for use with Claude, GPT-4, and other LLM agents
- Perfect for automated literature review generation

## Installation

### From PyPI (when published)

```bash
pip install zoterodb-analyzer
```

### For Development

```bash
git clone https://github.com/MasterYip/ZoteroDB-Analyzer.git
cd ZoteroDB-Analyzer
pip install -e .
```

### With MCP Support

```bash
pip install zoterodb-analyzer[mcp]
```

## Quick Start

Set up Zotero credentials:

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

Run the examples:

```bash
python examples/basic_usage.py
```

Try the CLI:

```bash
zoterodb-analyzer --help
```

## Usage

### 1. Set up Zotero API Access

First, get your [Zotero API](https://www.zotero.org/support/dev/web_api/v3/start) credentials:

1. `your_api_key`. Go to [Zotero Settings](https://www.zotero.org/settings/keys) to create a new private key with library access.
2. `your_user_id`. Go to your user profile and the URL is `https://www.zotero.org/<your_user_name>/<your_user_id>`.

### 2. Configure Environment Variables

#### Windows Command Prompt

```cmd
set ZOTERO_LIBRARY_ID=your_user_id
set ZOTERO_API_KEY=your_api_key
```

#### Windows PowerShell

```powershell
$env:ZOTERO_LIBRARY_ID='your_user_id'
$env:ZOTERO_API_KEY='your_api_key'
```

#### Windows Permanent Environment Variables

1. Press `Win+R`, type `sysdm.cpl`, press Enter
2. Go to Advanced > Environment Variables
3. Add `ZOTERO_LIBRARY_ID` and `ZOTERO_API_KEY` as new variables

#### Linux/macOS

```bash
export ZOTERO_LIBRARY_ID='your_user_id'
export ZOTERO_API_KEY='your_api_key'
```

To make it permanent, add to `~/.bashrc` or `~/.zshrc`:

```bash
echo 'export ZOTERO_LIBRARY_ID="your_user_id"' >> ~/.bashrc
echo 'export ZOTERO_API_KEY="your_api_key"' >> ~/.bashrc
```

### 3. Basic Usage

```python
from zoterodb_analyzer import ZoteroAnalyzer, ContentExporter, FilterCriteria, LiteratureCategory

# Initialize analyzer
analyzer = ZoteroAnalyzer(
    library_id="your_user_id",
    library_type="user",  # or "group"
    api_key="your_api_key"
)

# Fetch items with filtering
filter_criteria = FilterCriteria(
    tags=["machine learning", "robotics"],
    date_range=(2020, 2024),
    item_types=[ItemType.JOURNAL_ARTICLE]
)

items = analyzer.fetch_items(filter_criteria, limit=50)
print(f"Found {len(items)} items")

# Export for LLM consumption
exporter = ContentExporter("output")
exported_files = exporter.export_items(items, format=ExportFormat.MARKDOWN)
print(f"Exported to: {exported_files['markdown']}")
```

### 4. Advanced Categorization

```python
# Define literature categories
categories = [
    LiteratureCategory(
        name="Diffusion Models",
        description="Papers on diffusion models in robotics",
        keywords=["diffusion", "denoising", "generative model"]
    ),
    LiteratureCategory(
        name="Reinforcement Learning",
        description="RL approaches for robot control",
        keywords=["reinforcement learning", "policy gradient", "Q-learning"]
    )
]

# Categorize items
categorized_items = analyzer.categorize_items(items, categories)

# Export categorized literature for LLM context
exported_files = exporter.export_categorized_items(
    categorized_items, 
    format=ExportFormat.BOTH
)

# Create LLM-optimized context file
llm_context = exporter.export_for_llm_context(
    categorized_items, 
    context_type="related_works"
)
```

## Command Line Interface

The package includes a powerful CLI for easy automation:

```bash
# Fetch and export literature
zoterodb-analyzer fetch \
    --library-id YOUR_USER_ID \
    --api-key YOUR_API_KEY \
    --tags "machine learning,robotics" \
    --year-range 2020-2024 \
    --format both \
    --categories-file categories.json

# List available collections
zoterodb-analyzer collections --library-id YOUR_USER_ID --api-key YOUR_API_KEY

# Search your library
zoterodb-analyzer search \
    --library-id YOUR_USER_ID \
    --api-key YOUR_API_KEY \
    --query "deep learning" \
    --limit 20
```

### Categories File Format

Create a `categories.json` file to define your literature categories:

```json
[
  {
    "name": "Diffusion Models",
    "description": "Papers on diffusion models and generative approaches",
    "keywords": ["diffusion", "denoising", "DDPM", "score-based"]
  },
  {
    "name": "Robot Learning",
    "description": "Learning approaches for robotics",
    "keywords": ["robot learning", "imitation learning", "demonstration"]
  }
]
```

## MCP Integration for LLM Agents

The package provides a Model Context Protocol server for seamless integration with LLM agents:

```python
from zoterodb_analyzer.mcp_server import ZoteroMCPServer

# Initialize MCP server
mcp_server = ZoteroMCPServer(
    default_library_id="your_user_id",
    default_api_key="your_api_key"
)

# Available tools for agents:
# - fetch_literature: Get literature with filtering
# - categorize_literature: Categorize and export literature
# - search_literature: Search library contents
# - get_collections: List available collections
# - get_tags: Get library tags
# - export_for_llm: Create LLM-optimized exports
```

### 🔧 **VS Code Copilot MCP Configuration**

![MCP Demo](doc/mcp_demo.png)

To integrate ZoteroDB Analyzer with VS Code Copilot, follow these steps:

#### 1. **Prepare the MCP Server**

First, ensure the package is installed:

```bash
# Install the package
pip install -e .
```

#### 2. **Configure VS Code Github Copilot**

Add the following configuration to your VS Code Copilot settings. Open your VS Code settings and add this MCP server configuration:

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

**⚠️ Important Notes:**

- Replace `your_user_id` and `your_api_key` with your actual Zotero credentials
- Use double backslashes `\\` for Windows paths in JSON configuration
- Keep your API key secure and consider using environment variables instead of hardcoding

#### 3. **Alternative: Using Environment Variables**

For better security, you can configure the MCP server to use system environment variables:

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

Then set your credentials as system environment variables (as described in the Environment Variables section above).

#### 4. **Test the Integration**

Once configured, restart VS Code Copilot. You can then use the following MCP tools in your conversations:

- **`fetch_literature`** - Search and retrieve papers from your Zotero library
- **`categorize_literature`** - Automatically categorize papers for literature reviews
- **`search_literature`** - Search your library with text queries
- **`get_collections`** - List your Zotero collections
- **`get_tags`** - Get all tags from your library
- **`export_for_llm`** - Export literature in LLM-optimized formats

#### 5. **Example Usage with Copilot**

After configuration, you can ask Copilot things like:

- *"Search my Zotero library for papers about diffusion models"*
- *"Categorize my recent machine learning papers for a literature review"*
- *"Find papers by [author name] in my library"*
- *"Export papers about robotics in markdown format for my thesis"*

The MCP server will automatically handle the requests and provide structured literature data that Copilot can use to help with your research and writing tasks.

### 🧪 **Testing the MCP Server**

You can test the MCP server functionality before integrating with Copilot:

```bash
# Test the MCP server directly
python test_mcp_client.py

# Run the MCP server manually
python mcp_server_runner.py
```

## Environment Variables

Set environment variables for easier usage:

```bash
export ZOTERO_API_KEY="your_api_key"
export ZOTERO_LIBRARY_ID="your_user_id"
export ZOTERO_LIBRARY_TYPE="user"  # or "group"
```

## Use Cases

### 📚 **Academic Literature Reviews**

- Automatically categorize papers by research themes
- Generate structured content for Related Works sections
- Extract key metadata and abstracts for analysis

### 🤖 **Agent-Assisted Research**

- Provide structured literature context to LLM agents
- Enable agents to query and analyze your research library
- Automate literature review generation

### 📊 **Research Analysis**

- Analyze research trends across time periods
- Identify key authors and publication venues
- Track citation patterns and relationships

## API Reference

### Core Classes

- **`ZoteroAnalyzer`**: Main class for fetching and analyzing Zotero data
- **`ContentExporter`**: Handles exporting to various formats
- **`FilterCriteria`**: Defines filtering parameters for literature search
- **`LiteratureCategory`**: Represents a category for organizing literature
- **`ZoteroItem`**: Represents a single literature item with metadata

### Key Methods

- `fetch_items()`: Retrieve items with optional filtering
- `categorize_items()`: Organize items into predefined categories
- `search_items()`: Search library using text queries
- `export_items()`: Export items in JSON/Markdown formats
- `export_for_llm_context()`: Create LLM-optimized context files

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use ZoteroDB-Analyzer in your research, please cite:

```bibtex
@software{zoterodb_analyzer,
  title={ZoteroDB-Analyzer: A Python Package for Literature Review Automation},
  author={Raymon Yip},
  year={2024},
  url={https://github.com/MasterYip/ZoteroDB-Analyzer}
}
```

## Support

- 📖 **Documentation**: [Link to docs]
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/MasterYip/ZoteroDB-Analyzer/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/MasterYip/ZoteroDB-Analyzer/discussions)
- 📧 **Contact**: <contact@zoterodb-analyzer.com>

## Roadmap

- [ ] Web interface for non-technical users
- [ ] Integration with additional reference managers
- [ ] Advanced citation network analysis
- [ ] Automated literature trend detection
- [ ] Support for full-text analysis
