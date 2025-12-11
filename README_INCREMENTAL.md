# 微博搜索增量更新系统

## 概述

这是一个完整的微博搜索增量更新解决方案，可以自动定时获取最新的微博数据，避免重复爬取历史数据。

## 功能特点

- ✅ **增量更新**: 每次只获取最近时间段的数据
- ✅ **定时执行**: 支持crontab定时任务配置
- ✅ **日志管理**: 完整的日志记录和自动清理
- ✅ **配置灵活**: JSON配置文件，易于修改
- ✅ **错误处理**: 完善的异常处理和超时控制
- ✅ **自动化部署**: 一键配置crontab任务

## 文件结构

```
weibo-search/
├── incremental_update.py      # 主要的增量更新脚本
├── incremental_config.json    # 配置文件
├── run_incremental.sh         # 启动脚本
├── setup_crontab.sh          # 自动配置crontab脚本
├── CRONTAB_SETUP.md          # Crontab配置指南
├── logs/                     # 日志目录
│   ├── incremental_update_YYYYMMDD.log
│   └── crontab_execution.log
└── 结果文件/                  # 爬取结果目录
```

## 快速开始

### 1. 配置系统

```bash
# 1. 运行自动配置脚本
./setup_crontab.sh

# 2. 或者手动配置（可选）
crontab -e
# 添加: */30 * * * * /path/to/weibo-search/run_incremental.sh
```

### 2. 修改配置（可选）

编辑 `incremental_config.json` 文件：

```json
{
  "keywords": ["#你的关键词#"],
  "interval_minutes": 30,
  "weibo_type": 1,
  "limit_result": 1000
}
```

### 3. 测试运行

```bash
# 手动测试一次
./run_incremental.sh

# 或直接运行Python脚本
python3 incremental_update.py
```

## 配置说明

### 主要配置项

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `keywords` | 搜索关键词列表 | `["#黄霄云1222生日快乐#"]` |
| `interval_minutes` | 时间间隔（分钟） | `30` |
| `weibo_type` | 微博类型 | `1`（原创微博） |
| `contain_type` | 内容类型 | `0`（全部内容） |
| `limit_result` | 结果数量限制 | `0`（不限制） |

### 微博类型说明

- `0`: 全部微博
- `1`: 原创微博（推荐）
- `2`: 热门微博
- `3`: 关注人微博
- `4`: 认证用户微博
- `5`: 媒体微博
- `6`: 观点微博

## 定时任务配置

### 常用时间间隔

```bash
# 每15分钟
*/15 * * * * /path/to/run_incremental.sh

# 每30分钟（推荐）
*/30 * * * * /path/to/run_incremental.sh

# 每小时
0 * * * * /path/to/run_incremental.sh
```

### 管理命令

```bash
# 查看当前任务
crontab -l

# 编辑任务
crontab -e

# 删除所有任务
crontab -r
```

## 日志管理

### 日志文件

1. **应用日志**: `logs/incremental_update_YYYYMMDD.log`
   - 详细的执行过程
   - 错误信息和调试信息

2. **Crontab日志**: `logs/crontab_execution.log`
   - 定时任务的执行记录
   - 系统级别的错误信息

### 查看日志

```bash
# 实时查看应用日志
tail -f logs/incremental_update_$(date +%Y%m%d).log

# 实时查看crontab日志
tail -f logs/crontab_execution.log

# 查看错误信息
grep -i error logs/*.log
```

## 故障排除

### 常见问题

1. **脚本无法执行**
   ```bash
   chmod +x run_incremental.sh
   chmod +x setup_crontab.sh
   ```

2. **Python环境问题**
   ```bash
   # 检查虚拟环境
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **权限问题**
   ```bash
   # 确保有写入权限
   chmod 755 logs/
   chmod 755 结果文件/
   ```

4. **Crontab不执行**
   ```bash
   # 检查crontab服务
   # macOS
   sudo launchctl list | grep cron
   
   # Linux
   systemctl status cron
   ```

### 调试模式

```bash
# 手动运行并查看详细输出
python3 incremental_update.py

# 检查配置文件
cat incremental_config.json | python3 -m json.tool
```

## 性能优化

### 建议设置

1. **时间间隔**: 建议30分钟，避免过于频繁
2. **结果限制**: 设置合理的 `limit_result` 避免单次爬取过多
3. **错峰执行**: 避免在微博高峰时段执行
4. **日志清理**: 系统会自动清理7天前的日志

### 监控指标

- 执行时间
- 爬取数量
- 错误率
- 磁盘使用量

## 注意事项

1. **遵守robots.txt**: 请遵守微博的爬虫协议
2. **合理频率**: 不要设置过于频繁的执行间隔
3. **Cookie有效性**: 定期检查和更新Cookie
4. **磁盘空间**: 定期清理日志和结果文件
5. **网络稳定性**: 确保服务器网络连接稳定

## 扩展功能

### 数据库存储

可以启用数据库存储功能：

```json
{
  "enable_sqlite": true,
  "enable_mysql": true,
  "enable_mongo": true
}
```

### 自定义处理

可以修改 `incremental_update.py` 添加自定义的数据处理逻辑。

## 技术支持

如有问题，请检查：

1. 日志文件中的错误信息
2. 网络连接状态
3. Python环境和依赖包
4. 系统权限设置

---

**最后更新**: 2024年12月