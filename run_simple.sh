#!/bin/bash
# 微博搜索简单运行脚本

# 设置脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 设置Python环境
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "已激活虚拟环境"
else
    echo "警告: 未找到虚拟环境，使用系统Python"
fi

# 执行爬虫
echo "开始执行微博搜索爬虫..."
python3 -m scrapy crawl search

# 检查执行结果
if [ $? -eq 0 ]; then
    echo "爬虫执行成功"
else
    echo "爬虫执行失败"
    exit 1
fi