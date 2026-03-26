"""文件系统 MCP Server

提供规划文件的标准化读写操作。
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server


# 创建 MCP Server
server = Server("flood-agent-filesystem")

# 配置
ALLOWED_PATHS: List[str] = []
PLANS_DIR: str = "./plans"
DATA_DIR: str = "./data"


def set_allowed_paths(paths: List[str]):
    """设置允许访问的路径"""
    global ALLOWED_PATHS
    ALLOWED_PATHS = [os.path.abspath(p) for p in paths]


def _validate_path(path: str) -> str:
    """验证路径是否在允许范围内"""
    abs_path = os.path.abspath(path)
    
    if not ALLOWED_PATHS:
        # 默认使用相对路径限制
        if not (abs_path.startswith(os.path.abspath(PLANS_DIR)) or 
                abs_path.startswith(os.path.abspath(DATA_DIR))):
            raise ValueError(f"路径不在允许范围内: {path}")
    else:
        if not any(abs_path.startswith(allowed) for allowed in ALLOWED_PATHS):
            raise ValueError(f"路径不在允许范围内: {path}")
    
    return abs_path


def _ensure_dirs():
    """确保目录存在"""
    os.makedirs(PLANS_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)


@server.list_tools()
async def list_tools() -> List[Tool]:
    """定义可用工具"""
    return [
        Tool(
            name="write_planning_markdown",
            description="将决策规划写入标准化的 markdown 文件",
            inputSchema={
                "type": "object",
                "properties": {
                    "plan_name": {
                        "type": "string",
                        "description": "规划名称，用于生成文件名"
                    },
                    "content": {
                        "type": "string",
                        "description": "markdown 格式的规划内容"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "规划的元数据，如作者、版本等"
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "输出目录，默认为 ./plans",
                        "default": "./plans"
                    }
                },
                "required": ["plan_name", "content"]
            }
        ),
        Tool(
            name="read_planning_file",
            description="读取规划文件并解析元数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "plan_id": {
                        "type": "string",
                        "description": "规划ID或文件名"
                    },
                    "parse_metadata": {
                        "type": "boolean",
                        "description": "是否解析 YAML frontmatter",
                        "default": True
                    }
                },
                "required": ["plan_id"]
            }
        ),
        Tool(
            name="list_plans",
            description="列出所有规划文件",
            inputSchema={
                "type": "object",
                "properties": {
                    "filter": {
                        "type": "string",
                        "description": "文件名过滤条件"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "最大返回数量",
                        "default": 100
                    }
                }
            }
        ),
        Tool(
            name="append_to_plan",
            description="向规划文件追加内容",
            inputSchema={
                "type": "object",
                "properties": {
                    "plan_id": {
                        "type": "string",
                        "description": "规划文件ID"
                    },
                    "content": {
                        "type": "string",
                        "description": "要追加的内容"
                    }
                },
                "required": ["plan_id", "content"]
            }
        ),
        Tool(
            name="delete_plan",
            description="删除规划文件",
            inputSchema={
                "type": "object",
                "properties": {
                    "plan_id": {
                        "type": "string",
                        "description": "规划文件ID"
                    }
                },
                "required": ["plan_id"]
            }
        ),
        Tool(
            name="write_data_json",
            description="将数据写入 JSON 文件",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "文件名（不含路径）"
                    },
                    "data": {
                        "type": "object",
                        "description": "要写入的数据"
                    },
                    "indent": {
                        "type": "integer",
                        "description": "缩进空格数",
                        "default": 2
                    }
                },
                "required": ["filename", "data"]
            }
        ),
        Tool(
            name="read_data_json",
            description="从 JSON 文件读取数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "文件名（不含路径）"
                    }
                },
                "required": ["filename"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """处理工具调用"""
    _ensure_dirs()
    
    try:
        if name == "write_planning_markdown":
            return await _handle_write_planning(arguments)
        elif name == "read_planning_file":
            return await _handle_read_planning(arguments)
        elif name == "list_plans":
            return await _handle_list_plans(arguments)
        elif name == "append_to_plan":
            return await _handle_append_to_plan(arguments)
        elif name == "delete_plan":
            return await _handle_delete_plan(arguments)
        elif name == "write_data_json":
            return await _handle_write_data_json(arguments)
        elif name == "read_data_json":
            return await _handle_read_data_json(arguments)
        else:
            raise ValueError(f"未知工具: {name}")
    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "error": str(e)
            }, ensure_ascii=False)
        )]


async def _handle_write_planning(args: Dict[str, Any]) -> List[TextContent]:
    """处理写入规划文件"""
    plan_name = args["plan_name"]
    content = args["content"]
    metadata = args.get("metadata", {})
    output_dir = args.get("output_dir", PLANS_DIR)
    
    # 验证路径
    output_path = _validate_path(output_dir)
    os.makedirs(output_path, exist_ok=True)
    
    # 生成标准化文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in plan_name)
    filename = f"plan_{timestamp}_{safe_name}.md"
    filepath = os.path.join(output_path, filename)
    
    # 构建标准化头部
    default_metadata = {
        "plan_name": plan_name,
        "created_at": datetime.now().isoformat(),
        "version": "1.0",
        "server": "flood-agent-filesystem",
    }
    default_metadata.update(metadata)
    
    # 构建 YAML frontmatter
    yaml_lines = ["---"]
    for key, value in default_metadata.items():
        if isinstance(value, str):
            yaml_lines.append(f"{key}: \"{value}\"")
        else:
            yaml_lines.append(f"{key}: {value}")
    yaml_lines.append("---")
    yaml_lines.append("")
    
    full_content = "\n".join(yaml_lines) + content
    
    # 写入文件
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(full_content)
    
    return [TextContent(
        type="text",
        text=json.dumps({
            "success": True,
            "filepath": filepath,
            "filename": filename,
            "plan_name": plan_name,
            "created_at": default_metadata["created_at"]
        }, ensure_ascii=False, indent=2)
    )]


async def _handle_read_planning(args: Dict[str, Any]) -> List[TextContent]:
    """处理读取规划文件"""
    plan_id = args["plan_id"]
    parse_metadata = args.get("parse_metadata", True)
    
    # 查找文件
    filepath = os.path.join(PLANS_DIR, plan_id)
    if not os.path.exists(filepath):
        # 尝试查找匹配的文件
        files = os.listdir(PLANS_DIR)
        matching = [f for f in files if plan_id in f and f.endswith('.md')]
        if matching:
            filepath = os.path.join(PLANS_DIR, matching[0])
        else:
            raise FileNotFoundError(f"未找到规划文件: {plan_id}")
    
    # 验证路径
    filepath = _validate_path(filepath)
    
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    result = {
        "success": True,
        "filepath": filepath,
        "content": content
    }
    
    # 解析 YAML frontmatter
    if parse_metadata and content.startswith("---"):
        try:
            parts = content.split("---", 2)
            if len(parts) >= 3:
                yaml_content = parts[1].strip()
                markdown_content = parts[2].strip()
                
                # 简单解析 YAML
                metadata = {}
                for line in yaml_content.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip()
                        value = value.strip().strip('"')
                        metadata[key] = value
                
                result["metadata"] = metadata
                result["content"] = markdown_content
        except Exception as e:
            result["parse_error"] = str(e)
    
    return [TextContent(
        type="text",
        text=json.dumps(result, ensure_ascii=False, indent=2)
    )]


async def _handle_list_plans(args: Dict[str, Any]) -> List[TextContent]:
    """处理列出规划文件"""
    filter_str = args.get("filter", "")
    limit = args.get("limit", 100)
    
    _ensure_dirs()
    
    files = []
    for filename in os.listdir(PLANS_DIR):
        if filename.endswith('.md'):
            if not filter_str or filter_str in filename:
                filepath = os.path.join(PLANS_DIR, filename)
                stat = os.stat(filepath)
                files.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                })
    
    # 按修改时间排序
    files.sort(key=lambda x: x["modified"], reverse=True)
    files = files[:limit]
    
    return [TextContent(
        type="text",
        text=json.dumps({
            "success": True,
            "count": len(files),
            "plans": files
        }, ensure_ascii=False, indent=2)
    )]


async def _handle_append_to_plan(args: Dict[str, Any]) -> List[TextContent]:
    """处理追加内容到规划文件"""
    plan_id = args["plan_id"]
    content = args["content"]
    
    filepath = os.path.join(PLANS_DIR, plan_id)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"未找到规划文件: {plan_id}")
    
    filepath = _validate_path(filepath)
    
    with open(filepath, "a", encoding="utf-8") as f:
        f.write("\n\n")
        f.write(f"<!-- Appended at {datetime.now().isoformat()} -->\n")
        f.write(content)
    
    return [TextContent(
        type="text",
        text=json.dumps({
            "success": True,
            "filepath": filepath,
            "message": "内容已追加"
        }, ensure_ascii=False)
    )]


async def _handle_delete_plan(args: Dict[str, Any]) -> List[TextContent]:
    """处理删除规划文件"""
    plan_id = args["plan_id"]
    
    filepath = os.path.join(PLANS_DIR, plan_id)
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"未找到规划文件: {plan_id}")
    
    filepath = _validate_path(filepath)
    os.remove(filepath)
    
    return [TextContent(
        type="text",
        text=json.dumps({
            "success": True,
            "deleted": plan_id
        }, ensure_ascii=False)
    )]


async def _handle_write_data_json(args: Dict[str, Any]) -> List[TextContent]:
    """处理写入 JSON 数据"""
    filename = args["filename"]
    data = args["data"]
    indent = args.get("indent", 2)
    
    if not filename.endswith('.json'):
        filename += '.json'
    
    filepath = os.path.join(DATA_DIR, filename)
    filepath = _validate_path(filepath)
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)
    
    return [TextContent(
        type="text",
        text=json.dumps({
            "success": True,
            "filepath": filepath,
            "size": os.path.getsize(filepath)
        }, ensure_ascii=False)
    )]


async def _handle_read_data_json(args: Dict[str, Any]) -> List[TextContent]:
    """处理读取 JSON 数据"""
    filename = args["filename"]
    
    if not filename.endswith('.json'):
        filename += '.json'
    
    filepath = os.path.join(DATA_DIR, filename)
    filepath = _validate_path(filepath)
    
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return [TextContent(
        type="text",
        text=json.dumps({
            "success": True,
            "data": data
        }, ensure_ascii=False, indent=2)
    )]


async def main():
    """启动 MCP Server"""
    import sys
    
    # 从命令行参数获取允许的路径
    if len(sys.argv) > 1:
        set_allowed_paths(sys.argv[1:])
    else:
        set_allowed_paths([PLANS_DIR, DATA_DIR])
    
    from mcp.server.stdio import stdio_server as mcp_stdio_server
    
    async with mcp_stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())