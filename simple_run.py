#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单运行脚本 - 根据配置文件运行微博爬虫
"""

import sys
import os
import signal
import time
import json
from pathlib import Path

# 设置项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def signal_handler(signum, frame):
    print("\n收到中断信号，正在停止...")
    sys.exit(0)

def load_config():
    """加载配置文件"""
    config_file = Path("simple_config.json")
    if not config_file.exists():
        print("❌ 配置文件 simple_config.json 不存在")
        return None
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except Exception as e:
        print(f"❌ 读取配置文件失败: {e}")
        return None

def run_spider():
    """运行爬虫"""
    print("=" * 60)
    print("开始运行微博搜索爬虫")
    print("=" * 60)
    
    # 加载配置
    config = load_config()
    if not config:
        return
    
    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # 设置环境变量
        os.environ['SCRAPY_SETTINGS_MODULE'] = 'weibo.settings'
        
        # 导入必要的模块
        from scrapy.crawler import CrawlerProcess
        from weibo.spiders.search import SearchSpider
        
        # 创建爬虫进程配置
        settings = {
            'LOG_LEVEL': 'INFO',
            'DOWNLOAD_DELAY': config.get('download_delay', 10),
            'LIMIT_RESULT': config.get('limit_result', 0),
            'ROBOTSTXT_OBEY': False,
            'COOKIES_ENABLED': False,
            'TELNETCONSOLE_ENABLED': False,
            'ITEM_PIPELINES': {
                'weibo.pipelines.DuplicatesPipeline': 300,
                'weibo.pipelines.SupertopicFilterPipeline': 301,
                'weibo.pipelines.FilteredJsonPipeline': 302,
                'weibo.pipelines.CsvPipeline': 303,
            }
        }
        
        # 更新settings.py中的配置
        import weibo.settings as settings_module
        
        # 设置关键词
        settings_module.KEYWORD_LIST = config.get('keywords', [])
        
        # 设置时间范围
        settings_module.START_DATE = config.get('start_date', '2025-12-01')
        settings_module.END_DATE = config.get('end_date', '2025-12-17')
        
        # 设置其他参数
        settings_module.FURTHER_THRESHOLD = config.get('further_threshold', 46)
        settings_module.REGION = config.get('region', ['全部'])
        settings_module.WEIBO_TYPE = config.get('weibo_type', 1)
        settings_module.CONTAIN_TYPE = config.get('contain_type', 0)
        
        print(f"📋 关键词: {', '.join(settings_module.KEYWORD_LIST)}")
        print(f"📅 时间范围: {settings_module.START_DATE} 到 {settings_module.END_DATE}")
        print(f"⏱️  下载延迟: {settings_module.DOWNLOAD_DELAY}秒")
        print(f"🎯 结果限制: {'无限制' if settings_module.LIMIT_RESULT == 0 else settings_module.LIMIT_RESULT}")
        print("-" * 60)
        
        # 创建爬虫进程
        process = CrawlerProcess(settings)
        process.crawl(SearchSpider)
        
        print("🚀 开始爬取数据...")
        print("如需中断，请按 Ctrl+C")
        print("-" * 60)
        
        # 启动爬虫
        process.start()
        
    except KeyboardInterrupt:
        print("\n用户中断了爬虫执行")
    except Exception as e:
        print(f"❌ 爬虫执行出错: {e}")
        import traceback
        traceback.print_exc()

def main():
    """主函数"""
    print("微博搜索爬虫 - 简单运行脚本")
    print("此脚本将:")
    print("1. 读取 simple_config.json 配置文件")
    print("2. 运行爬虫获取指定关键词的数据")
    print("3. 将结果保存到指定目录")
    
    try:
        run_spider()
        
        print("\n" + "=" * 60)
        print("爬虫执行完成！")
        print("请检查 过滤结果 目录中的JSON文件")
        print("=" * 60)
        
    except Exception as e:
        print(f"执行过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()