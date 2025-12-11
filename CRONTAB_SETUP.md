# 微博搜索增量更新 - Crontab配置指南

## 自动配置crontab（推荐）

运行以下命令自动配置定时任务：

```bash
# 获取当前脚本的绝对路径
SCRIPT_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/run_incremental.sh"

# 添加crontab任务（每30分钟执行一次）
(crontab -l 2>/dev/null; echo "*/30 * * * * $SCRIPT_PATH >> /tmp/weibo_incremental.log 2>&1") | crontab -

# 验证crontab是否添加成功
crontab -l | grep incremental
```

## 手动配置crontab

1. 编辑crontab：
```bash
crontab -e
```

2. 添加以下行（请替换为实际路径）：
```bash
# 每30分钟执行一次微博搜索增量更新
*/30 * * * * /path/to/your/weibo-search/run_incremental.sh >> /tmp/weibo_incremental.log 2>&1

# 或者每小时执行一次
0 * * * * /path/to/your/weibo-search/run_incremental.sh >> /tmp/weibo_incremental.log 2>&1

# 或者每15分钟执行一次
*/15 * * * * /path/to/your/weibo-search/run_incremental.sh >> /tmp/weibo_incremental.log 2>&1
```

## Crontab时间格式说明

```
* * * * * command
│ │ │ │ │
│ │ │ │ └─── 星期几 (0-7, 0和7都表示周日)
│ │ │ └───── 月份 (1-12)
│ │ └─────── 日期 (1-31)
│ └───────── 小时 (0-23)
└─────────── 分钟 (0-59)
```

## 常用时间配置示例

```bash
# 每30分钟执行一次
*/30 * * * * /path/to/script

# 每小时执行一次
0 * * * * /path/to/script

# 每天凌晨2点执行
0 2 * * * /path/to/script

# 每周一凌晨3点执行
0 3 * * 1 /path/to/script

# 工作日每小时执行
0 * * * 1-5 /path/to/script
```

## 管理crontab任务

```bash
# 查看当前用户的crontab任务
crontab -l

# 编辑crontab任务
crontab -e

# 删除所有crontab任务
crontab -r

# 删除特定任务（编辑后删除对应行）
crontab -e
```

## 日志管理

系统会自动生成以下日志：

1. **Crontab执行日志**: `/tmp/weibo_incremental.log`
2. **应用程序日志**: `logs/incremental_update_YYYYMMDD.log`

查看日志：
```bash
# 查看crontab执行日志
tail -f /tmp/weibo_incremental.log

# 查看应用程序日志
tail -f logs/incremental_update_$(date +%Y%m%d).log

# 查看最近的错误
grep -i error /tmp/weibo_incremental.log
```

## 故障排除

1. **检查crontab服务状态**：
```bash
# macOS
sudo launchctl list | grep cron

# Linux
systemctl status cron
```

2. **检查脚本权限**：
```bash
ls -la run_incremental.sh
# 应该显示 -rwxr-xr-x
```

3. **手动测试脚本**：
```bash
./run_incremental.sh
```

4. **检查Python环境**：
```bash
which python3
python3 --version
```

## 注意事项

1. 确保脚本路径使用绝对路径
2. 确保Python虚拟环境路径正确
3. 定期检查日志文件，避免磁盘空间不足
4. 建议在非高峰时段运行，避免对微博服务器造成过大压力