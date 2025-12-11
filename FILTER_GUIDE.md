# 微博数据过滤功能说明

## 功能概述

已成功为微博搜索脚本添加了数据过滤功能，可以过滤掉话题标签、图片链接、视频链接和@信息，只保留用户头像、用户ID和纯净的祝福消息，并以JSON格式输出。

## 过滤规则

### 自动过滤的内容
- ✅ **话题标签**: `#话题内容#` → 完全移除
- ✅ **@用户信息**: `@用户名` → 完全移除  
- ✅ **图片链接**: 不包含在输出中
- ✅ **视频链接**: 不包含在输出中
- ✅ **多余空格**: 自动清理和规范化

### 保留的内容
- ✅ **用户ID**: 微博用户的唯一标识
- ✅ **用户头像**: 高清头像图片URL (180x180)
- ✅ **祝福消息**: 过滤后的纯文本内容
- ✅ **发布时间**: 微博发布的时间
- ✅ **关键词**: 搜索使用的关键词

## 输出格式

### JSON文件结构
```json
[
  {
    "user_id": "123456789",
    "user_avatar": "https://tva1.sinaimg.cn/crop.0.0.180.180.180/123456789.jpg",
    "blessing_message": "祝福黄霄云生日快乐！希望你越来越好！",
    "created_at": "2024-12-22 15:30:00",
    "keyword": "#黄霄云1222生日快乐#"
  }
]
```

### 字段说明
| 字段 | 类型 | 说明 |
|------|------|------|
| `user_id` | String | 微博用户ID |
| `user_avatar` | String | 用户头像URL（高清版本） |
| `blessing_message` | String | 过滤后的祝福消息 |
| `created_at` | String | 发布时间 |
| `keyword` | String | 搜索关键词 |

## 文件输出位置

### 过滤后的JSON文件
- **路径**: `过滤结果/关键词/关键词_filtered.json`
- **格式**: JSON数组，包含所有过滤后的数据
- **编码**: UTF-8
- **更新方式**: 追加模式，新数据会添加到现有文件中

### 原始CSV文件（保持不变）
- **路径**: `结果文件/关键词/关键词.csv`
- **格式**: CSV格式，包含完整的原始数据
- **用途**: 备份和详细分析

## 使用方法

### 1. 运行爬虫
```bash
# 普通运行
scrapy crawl search

# 增量更新运行
./run_incremental.sh

# 或使用Python脚本
python3 incremental_update.py
```

### 2. 查看结果
```bash
# 查看过滤后的JSON数据
cat "过滤结果/#黄霄云1222生日快乐#/#黄霄云1222生日快乐#_filtered.json"

# 使用jq工具美化显示（如果已安装）
cat "过滤结果/#黄霄云1222生日快乐#/#黄霄云1222生日快乐#_filtered.json" | jq '.'
```

### 3. 数据处理示例
```python
import json

# 读取过滤后的数据
with open('过滤结果/#黄霄云1222生日快乐#/#黄霄云1222生日快乐#_filtered.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 统计祝福消息数量
print(f"共收集到 {len(data)} 条祝福消息")

# 查看最新的祝福
for item in data[-5:]:  # 显示最新5条
    print(f"用户: {item['user_id']}")
    print(f"消息: {item['blessing_message']}")
    print(f"时间: {item['created_at']}")
    print("-" * 40)
```

## 过滤示例

### 原始微博内容
```
#黄霄云1222生日快乐# 祝福黄霄云生日快乐！@某用户 希望你越来越好！🎂🎉
```

### 过滤后内容
```
祝福黄霄云生日快乐！ 希望你越来越好！
```

## 配置管理

### Pipeline配置
在 `weibo/settings.py` 中已启用：
```python
ITEM_PIPELINES = {
    'weibo.pipelines.DuplicatesPipeline': 300,
    'weibo.pipelines.FilteredJsonPipeline': 301,  # 过滤JSON管道
    'weibo.pipelines.CsvPipeline': 302,
}
```

### 自定义过滤规则
如需修改过滤规则，编辑 `weibo/pipelines.py` 中的 `FilteredJsonPipeline` 类：

```python
def filter_text(self, text):
    """自定义过滤逻辑"""
    # 添加更多过滤规则
    text = re.sub(r'特定模式', '', text)
    return text
```

## 测试功能

运行测试脚本验证过滤功能：
```bash
python3 test_filter.py
```

测试包括：
- ✅ 文本过滤功能测试
- ✅ JSON输出格式测试  
- ✅ Pipeline配置检查

## 注意事项

1. **数据完整性**: 原始CSV数据仍会保存，JSON是额外的过滤输出
2. **编码问题**: 所有文件使用UTF-8编码，支持中文和emoji
3. **空消息**: 如果过滤后消息为空，该条记录不会保存到JSON文件
4. **头像质量**: 自动将小头像(50x50)转换为高清头像(180x180)
5. **增量更新**: 新数据会追加到现有JSON文件中，不会覆盖

## 故障排除

### 常见问题
1. **JSON文件为空**: 检查是否有有效的祝福消息（过滤后不为空）
2. **头像链接无效**: 某些用户可能没有设置头像
3. **编码错误**: 确保系统支持UTF-8编码

### 调试方法
```bash
# 查看详细日志
tail -f logs/incremental_update_$(date +%Y%m%d).log

# 检查Pipeline是否正常工作
grep "FilteredJsonPipeline" logs/*.log
```