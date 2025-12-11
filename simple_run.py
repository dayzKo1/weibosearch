#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微博搜索简单执行脚本
直接运行scrapy爬虫，不包含增量更新逻辑
"""

import os
import sys
import json
import logging
import subprocess
from datetime import datetime
from pathlib import Path

# 配置日志
def setup_logging():
    """设置日志配置"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    log_file = log_dir / f"weibo_search_{datetime.now().strftime('%Y%m%d_%H%M')}.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

class SimpleWeiboRunner:
    def __init__(self, config_file="simple_config.json"):
        self.logger = setup_logging()
        self.config_file = config_file
        self.config = self.load_config()
        self.project_root = Path(__file__).parent
        
    def load_config(self):
        """加载配置文件"""
        default_config = {
            "keywords": ["#黄霄云1222生日快乐#", "#黄霄雲1222生日快乐"],
            "weibo_type": 1,
            "contain_type": 0,
            "region": ["全部"],
            "further_threshold": 46,
            "limit_result": 0,
            "output_dir": "结果文件",
            "enable_sqlite": False,
            "enable_mysql": False,
            "enable_mongo": False
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    default_config.update(config)
                    return default_config
            except Exception as e:
                self.logger.error(f"加载配置文件失败: {e}")
                return default_config
        else:
            self.logger.warning(f"配置文件 {self.config_file} 不存在，使用默认配置")
            return default_config
    
    def update_settings(self):
        """更新settings.py文件中的配置"""
        settings_file = self.project_root / "weibo" / "settings.py"
        
        try:
            # 读取当前settings.py
            with open(settings_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 更新关键词列表
            keywords_str = str(self.config['keywords']).replace("'", "'")
            content = self.replace_setting(content, 'KEYWORD_LIST', keywords_str)
            
            # 更新其他配置
            content = self.replace_setting(content, 'WEIBO_TYPE', str(self.config['weibo_type']))
            content = self.replace_setting(content, 'CONTAIN_TYPE', str(self.config['contain_type']))
            content = self.replace_setting(content, 'REGION', str(self.config['region']))
            content = self.replace_setting(content, 'FURTHER_THRESHOLD', str(self.config['further_threshold']))
            content = self.replace_setting(content, 'LIMIT_RESULT', str(self.config['limit_result']))
            
            # 写回文件
            with open(settings_file, 'w', encoding='utf-8') as f:
                f.write(content)
                
            self.logger.info("已更新settings.py配置")
            return True
            
        except Exception as e:
            self.logger.error(f"更新settings.py失败: {e}")
            return False
    
    def replace_setting(self, content, setting_name, new_value):
        """替换settings.py中的配置项"""
        import re
        pattern = rf'^{setting_name}\s*=.*$'
        replacement = f'{setting_name} = {new_value}'
        return re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    def run_scrapy(self):
        """运行scrapy爬虫"""
        try:
            # 切换到项目目录
            os.chdir(self.project_root)
            
            # 构建scrapy命令
            cmd = [sys.executable, "-m", "scrapy", "crawl", "search"]
            
            self.logger.info(f"开始执行爬虫: {' '.join(cmd)}")
            
            # 执行命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=3600  # 60分钟超时
            )
            
            if result.returncode == 0:
                self.logger.info("爬虫执行成功")
                if result.stdout:
                    self.logger.info(f"输出: {result.stdout}")
                return True
            else:
                self.logger.error(f"爬虫执行失败，返回码: {result.returncode}")
                if result.stderr:
                    self.logger.error(f"错误输出: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("爬虫执行超时")
            return False
        except Exception as e:
            self.logger.error(f"执行爬虫时发生错误: {e}")
            return False
    
    def run(self):
        """执行爬虫"""
        self.logger.info("=" * 50)
        self.logger.info("开始执行微博搜索爬虫")
        
        try:
            # 更新配置
            if not self.update_settings():
                return False
            
            # 运行爬虫
            success = self.run_scrapy()
            
            if success:
                self.logger.info("爬虫执行完成")
            else:
                self.logger.error("爬虫执行失败")
                
            return success
            
        except Exception as e:
            self.logger.error(f"执行过程中发生错误: {e}")
            return False
        finally:
            self.logger.info("=" * 50)

def main():
    """主函数"""
    runner = SimpleWeiboRunner()
    success = runner.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()