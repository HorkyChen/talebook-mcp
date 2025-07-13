#!/usr/bin/env python3
"""
配置生成器 - 为MCP客户端生成正确的配置文件
"""

import json
import os
import sys
from pathlib import Path

def get_project_root():
    """获取项目根目录的绝对路径"""
    script_dir = Path(__file__).parent.absolute()
    return script_dir.parent  # 返回上级目录，因为脚本现在在src目录下

def generate_config(project_path: Path, client_type: str = "generic"):
    """生成MCP客户端配置"""

    config_templates = {
        "generic": {
            "mcpServers": {
                "talebook-mcp": {
                    "command": "python",
                    "args": [str(project_path / "src" / "server.py")],
                    "env": {
                        "PYTHONPATH": str(project_path / "src")
                    },
                    "cwd": str(project_path),
                    "disabled": False
                }
            }
        },
        "claude": {
            "mcpServers": {
                "talebook-mcp": {
                    "command": "python",
                    "args": [str(project_path / "src" / "server.py")],
                    "env": {
                        "PYTHONPATH": str(project_path / "src"),
                        "LOG_LEVEL": "INFO"
                    },
                    "cwd": str(project_path),
                    "disabled": False,
                    "description": "Talebook MCP Server - Provides book management tools",
                    "icon": "📚"
                }
            }
        }
    }

    return config_templates.get(client_type, config_templates["generic"])

def main():
    """主函数"""
    project_root = get_project_root()

    print("🔧 Talebook MCP Server 配置生成器")
    print("=" * 50)
    print(f"项目路径: {project_root}")

    # 生成不同类型的配置
    configs = {
        "generic": generate_config(project_root, "generic"),
        "claude": generate_config(project_root, "claude")
    }

    # 保存配置文件
    for config_type, config in configs.items():
        filename = f"generated-{config_type}-config.json"
        filepath = project_root / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"✅ 已生成 {config_type} 配置: {filename}")

    print("\n📋 使用说明:")
    print("1. 选择适合您MCP客户端的配置文件")
    print("2. 将配置内容复制到您的MCP客户端配置文件中")
    print("3. 重启MCP客户端")
    print("4. 查看 MCP_CLIENT_SETUP.md 获取详细说明")

    # 显示Claude Desktop配置路径
    print("\n🔍 Claude Desktop 配置文件位置:")
    system = os.name
    if system == "posix":  # Linux/macOS
        if sys.platform == "darwin":  # macOS
            claude_config = "~/Library/Application Support/Claude/claude_desktop_config.json"
        else:  # Linux
            claude_config = "~/.config/claude/claude_desktop_config.json"
    else:  # Windows
        claude_config = "%APPDATA%\\Claude\\claude_desktop_config.json"

    print(f"   {claude_config}")

if __name__ == "__main__":
    main()
