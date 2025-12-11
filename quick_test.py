#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本 - 运行爬虫并查看过滤效果
"""

import sys
import os
import signal
import time
from pathlib import Path

# 设置项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def signal_handler(signum, frame):
    print("\n收到中断信号，正在停止...")
    sys.exit(0)

def run_test():
    """运行测试爬虫"""
    print("=" * 60)
    print("开始运行微博搜索爬虫测试")
    print("=" * 60)
    
    # 设置信号处理
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # 设置环境变量
        os.environ['SCRAPY_SETTINGS_MODULE'] = 'weibo.settings'
        
        # 导入必要的模块
        from scrapy.crawler import CrawlerProcess
        from weibo.spiders.search import SearchSpider
        
        # 创建爬虫进程
        settings = {
            'LOG_LEVEL': 'INFO',
            'DOWNLOAD_DELAY': 2,
            'LIMIT_RESULT': 3,  # 限制只爬取3条数据用于测试
            'ROBOTSTXT_OBEY': False,
            'COOKIES_ENABLED': False,
            'TELNETCONSOLE_ENABLED': False,
            'ITEM_PIPELINES': {
                'weibo.pipelines.DuplicatesPipeline': 300,
                'weibo.pipelines.FilteredJsonPipeline': 301,
                'weibo.pipelines.CsvPipeline': 302,
            }
        }
        
        process = CrawlerProcess(settings)
        process.crawl(SearchSpider)
        
        print("开始爬取数据...")
        print("注意: 限制爬取3条数据用于测试")
        print("如需中断，请按 Ctrl+C")
        print("-" * 60)
        
        # 启动爬虫
        process.start()
        
    except KeyboardInterrupt:
        print("\n用户中断了爬虫执行")
    except Exception as e:
        print(f"爬虫执行出错: {e}")
        import traceback
        traceback.print_exc()

def check_results():
    """检查爬取结果"""
    print("\n" + "=" * 60)
    print("检查爬取结果")
    print("=" * 60)
    
    # 检查过滤结果目录
    filter_dir = Path("过滤结果")
    if filter_dir.exists():
        print(f"✅ 过滤结果目录存在: {filter_dir}")
        
        # 查找JSON文件
        json_files = list(filter_dir.rglob("*_filtered.json"))
        if json_files:
            print(f"✅ 找到 {len(json_files)} 个过滤结果文件:")
            for json_file in json_files:
                print(f"   📄 {json_file}")
                
                # 读取并显示内容
                try:
                    import json
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    print(f"   📊 包含 {len(data)} 条过滤后的数据")
                    
                    # 显示前2条数据作为示例
                    for i, item in enumerate(data[:2], 1):
                        print(f"\n   示例 {i}:")
                        print(f"     用户ID: {item.get('user_id', 'N/A')}")
                        print(f"     头像: {item.get('user_avatar', 'N/A')[:50]}...")
                        print(f"     祝福消息: {item.get('blessing_message', 'N/A')}")
                        print(f"     发布时间: {item.get('created_at', 'N/A')}")
                    
                    if len(data) > 2:
                        print(f"   ... 还有 {len(data) - 2} 条数据")
                        
                except Exception as e:
                    print(f"   ❌ 读取文件失败: {e}")
        else:
            print("❌ 未找到过滤结果文件")
    else:
        print("❌ 过滤结果目录不存在")
    
    # 检查原始结果目录
    result_dir = Path("结果文件")
    if result_dir.exists():
        print(f"\n✅ 原始结果目录存在: {result_dir}")
        
        # 查找CSV文件
        csv_files = list(result_dir.rglob("*.csv"))
        if csv_files:
            print(f"✅ 找到 {len(csv_files)} 个原始结果文件:")
            for csv_file in csv_files:
                print(f"   📄 {csv_file}")
                
                # 统计行数
                try:
                    with open(csv_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    print(f"   📊 包含 {len(lines)-1} 条原始数据（除去标题行）")
                except Exception as e:
                    print(f"   ❌ 读取文件失败: {e}")
        else:
            print("❌ 未找到原始结果文件")
    else:
        print("❌ 原始结果目录不存在")

def main():
    """主函数"""
    print("微博搜索爬虫测试脚本")
    print("此脚本将:")
    print("1. 运行爬虫获取少量测试数据")
    print("2. 检查过滤功能是否正常工作")
    print("3. 显示过滤前后的数据对比")
    
    try:
        # 运行爬虫测试
        run_test()
        
        # 等待一下让文件写入完成
        time.sleep(2)
        
        # 检查结果
        check_results()
        
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()