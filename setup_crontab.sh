#!/bin/bash
# 自动配置微博搜索增量更新的crontab任务

echo "=== 微博搜索增量更新 - Crontab自动配置脚本 ==="

# 获取当前脚本目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT_PATH="$SCRIPT_DIR/run_incremental.sh"

echo "项目目录: $SCRIPT_DIR"
echo "执行脚本: $SCRIPT_PATH"

# 检查脚本是否存在
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "错误: 找不到执行脚本 $SCRIPT_PATH"
    exit 1
fi

# 检查脚本是否可执行
if [ ! -x "$SCRIPT_PATH" ]; then
    echo "设置脚本执行权限..."
    chmod +x "$SCRIPT_PATH"
fi

# 创建日志目录
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

# 设置日志文件路径
LOG_FILE="$LOG_DIR/crontab_execution.log"

echo "日志文件: $LOG_FILE"

# 检查是否已经存在相同的crontab任务
EXISTING_TASK=$(crontab -l 2>/dev/null | grep "run_incremental.sh")

if [ -n "$EXISTING_TASK" ]; then
    echo "发现已存在的crontab任务:"
    echo "$EXISTING_TASK"
    echo ""
    read -p "是否要替换现有任务? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "取消配置"
        exit 0
    fi
    
    # 删除现有任务
    crontab -l 2>/dev/null | grep -v "run_incremental.sh" | crontab -
    echo "已删除现有任务"
fi

# 显示时间间隔选项
echo ""
echo "请选择执行频率:"
echo "1) 每15分钟执行一次"
echo "2) 每30分钟执行一次 (推荐)"
echo "3) 每小时执行一次"
echo "4) 自定义"

read -p "请输入选项 (1-4): " -n 1 -r
echo

case $REPLY in
    1)
        CRON_SCHEDULE="*/15 * * * *"
        DESCRIPTION="每15分钟"
        ;;
    2)
        CRON_SCHEDULE="*/30 * * * *"
        DESCRIPTION="每30分钟"
        ;;
    3)
        CRON_SCHEDULE="0 * * * *"
        DESCRIPTION="每小时"
        ;;
    4)
        echo "请输入cron表达式 (例如: */30 * * * *):"
        read -r CRON_SCHEDULE
        DESCRIPTION="自定义时间"
        ;;
    *)
        echo "无效选项，使用默认设置: 每30分钟"
        CRON_SCHEDULE="*/30 * * * *"
        DESCRIPTION="每30分钟"
        ;;
esac

# 构建完整的crontab命令
CRON_COMMAND="$CRON_SCHEDULE $SCRIPT_PATH >> $LOG_FILE 2>&1"

echo ""
echo "将添加以下crontab任务:"
echo "$CRON_COMMAND"
echo "执行频率: $DESCRIPTION"

read -p "确认添加? (Y/n): " -n 1 -r
echo

if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo "取消配置"
    exit 0
fi

# 添加crontab任务
(crontab -l 2>/dev/null; echo "$CRON_COMMAND") | crontab -

if [ $? -eq 0 ]; then
    echo "✅ Crontab任务添加成功!"
    echo ""
    echo "当前crontab任务列表:"
    crontab -l | grep -E "(run_incremental|weibo)"
    echo ""
    echo "📋 管理命令:"
    echo "  查看任务: crontab -l"
    echo "  编辑任务: crontab -e"
    echo "  删除任务: crontab -r"
    echo ""
    echo "📄 日志文件:"
    echo "  执行日志: $LOG_FILE"
    echo "  应用日志: $LOG_DIR/incremental_update_YYYYMMDD.log"
    echo ""
    echo "🔍 查看日志:"
    echo "  tail -f $LOG_FILE"
    echo ""
    echo "⚠️  注意事项:"
    echo "  - 确保系统时间正确"
    echo "  - 定期检查日志文件"
    echo "  - 避免在高峰时段频繁执行"
else
    echo "❌ Crontab任务添加失败"
    exit 1
fi