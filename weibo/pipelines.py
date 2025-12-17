# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import copy
import csv
import os

import scrapy
from scrapy.exceptions import DropItem
from scrapy.pipelines.files import FilesPipeline
from scrapy.pipelines.images import ImagesPipeline
from scrapy.utils.project import get_project_settings

settings = get_project_settings()


class CsvPipeline(object):
    def process_item(self, item, spider):
        base_dir = '结果文件' + os.sep + item['keyword']
        if not os.path.isdir(base_dir):
            os.makedirs(base_dir)
        file_path = base_dir + os.sep + item['keyword'] + '.csv'
        if not os.path.isfile(file_path):
            is_first_write = 1
        else:
            is_first_write = 0

        if item:
            with open(file_path, 'a', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f)
                if is_first_write:
                    header = [
                        'id', 'bid', 'user_id', '用户昵称', '微博正文', '头条文章url',
                        '发布位置', '艾特用户', '话题', '转发数', '评论数', '点赞数', '发布时间',
                        '发布工具', '微博图片url', '微博视频url', 'retweet_id', 'ip', 'user_authentication',
                        '会员类型', '会员等级'
                    ]
                    writer.writerow(header)

                writer.writerow([
                    item['weibo'].get('id', ''),
                    item['weibo'].get('bid', ''),
                    item['weibo'].get('user_id', ''),
                    item['weibo'].get('screen_name', ''),
                    item['weibo'].get('text', ''),
                    item['weibo'].get('article_url', ''),
                    item['weibo'].get('location', ''),
                    item['weibo'].get('at_users', ''),
                    item['weibo'].get('topics', ''),
                    item['weibo'].get('reposts_count', ''),
                    item['weibo'].get('comments_count', ''),
                    item['weibo'].get('attitudes_count', ''),
                    item['weibo'].get('created_at', ''),
                    item['weibo'].get('source', ''),
                    ','.join(item['weibo'].get('pics', [])),
                    item['weibo'].get('video_url', ''),
                    item['weibo'].get('retweet_id', ''),
                    item['weibo'].get('ip', ''),
                    item['weibo'].get('user_authentication', ''),
                    item['weibo'].get('vip_type', ''),
                    item['weibo'].get('vip_level', 0)
                ])
        return item

class SQLitePipeline(object):
    def open_spider(self, spider):
        try:
            import sqlite3
            # 在结果文件目录下创建SQLite数据库
            base_dir = '结果文件'
            if not os.path.isdir(base_dir):
                os.makedirs(base_dir)
            db_name = settings.get('SQLITE_DATABASE', 'weibo.db')
            self.conn = sqlite3.connect(os.path.join(base_dir, db_name))
            self.cursor = self.conn.cursor()
            # 创建表
            sql = """
            CREATE TABLE IF NOT EXISTS weibo (
                id varchar(20) NOT NULL PRIMARY KEY,
                bid varchar(12) NOT NULL,
                user_id varchar(20),
                screen_name varchar(30),
                text varchar(2000),
                article_url varchar(100),
                topics varchar(200),
                at_users varchar(1000),
                pics varchar(3000),
                video_url varchar(1000),
                location varchar(100),
                created_at DATETIME,
                source varchar(30),
                attitudes_count INTEGER,
                comments_count INTEGER,
                reposts_count INTEGER,
                retweet_id varchar(20),
                ip varchar(100),
                user_authentication varchar(100),
                vip_type varchar(50),
                vip_level INTEGER
            )"""
            self.cursor.execute(sql)
            self.conn.commit()
        except Exception as e:
            print(f"SQLite数据库创建失败: {e}")
            spider.sqlite_error = True


    def process_item(self, item, spider):
        data = dict(item['weibo'])
        data['pics'] = ','.join(data['pics'])
        keys = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        sql = f"""INSERT OR REPLACE INTO weibo ({keys}) 
                 VALUES ({placeholders})"""
        try:
            self.cursor.execute(sql, tuple(data.values()))
            self.conn.commit()
        except Exception as e:
            print(f"SQLite保存出错: {e}")
            spider.sqlite_error = True
            self.conn.rollback()

    def close_spider(self, spider):
        self.conn.close()

class MyImagesPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if len(item['weibo']['pics']) == 1:
            yield scrapy.Request(item['weibo']['pics'][0],
                                 meta={
                                     'item': item,
                                     'sign': ''
                                 })
        else:
            sign = 0
            for image_url in item['weibo']['pics']:
                yield scrapy.Request(image_url,
                                     meta={
                                         'item': item,
                                         'sign': '-' + str(sign)
                                     })
                sign += 1

    def file_path(self, request, response=None, info=None):
        image_url = request.url
        item = request.meta['item']
        sign = request.meta['sign']
        base_dir = '结果文件' + os.sep + item['keyword'] + os.sep + 'images'
        if not os.path.isdir(base_dir):
            os.makedirs(base_dir)
        image_suffix = image_url[image_url.rfind('.'):]
        file_path = base_dir + os.sep + item['weibo'][
            'id'] + sign + image_suffix
        return file_path


class MyVideoPipeline(FilesPipeline):
    def get_media_requests(self, item, info):
        if item['weibo']['video_url']:
            yield scrapy.Request(item['weibo']['video_url'],
                                 meta={'item': item})

    def file_path(self, request, response=None, info=None):
        item = request.meta['item']
        base_dir = '结果文件' + os.sep + item['keyword'] + os.sep + 'videos'
        if not os.path.isdir(base_dir):
            os.makedirs(base_dir)
        file_path = base_dir + os.sep + item['weibo']['id'] + '.mp4'
        return file_path


class MongoPipeline(object):
    def open_spider(self, spider):
        try:
            from pymongo import MongoClient
            self.client = MongoClient(settings.get('MONGO_URI'))
            self.db = self.client['weibo']
            self.collection = self.db['weibo']
        except ModuleNotFoundError:
            spider.pymongo_error = True

    def process_item(self, item, spider):
        try:
            import pymongo

            new_item = copy.deepcopy(item)
            if not self.collection.find_one({'id': new_item['weibo']['id']}):
                self.collection.insert_one(dict(new_item['weibo']))
            else:
                self.collection.update_one({'id': new_item['weibo']['id']},
                                           {'$set': dict(new_item['weibo'])})
        except pymongo.errors.ServerSelectionTimeoutError:
            spider.mongo_error = True

    def close_spider(self, spider):
        try:
            self.client.close()
        except AttributeError:
            pass


class MysqlPipeline(object):
    def create_database(self, mysql_config):
        """创建MySQL数据库"""
        import pymysql
        sql = """CREATE DATABASE IF NOT EXISTS %s DEFAULT
            CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci""" % settings.get(
            'MYSQL_DATABASE', 'weibo')
        db = pymysql.connect(**mysql_config)
        cursor = db.cursor()
        cursor.execute(sql)
        db.close()

    def create_table(self):
        """创建MySQL表"""
        sql = """
                CREATE TABLE IF NOT EXISTS weibo (
                id varchar(20) NOT NULL,
                bid varchar(12) NOT NULL,
                user_id varchar(20),
                screen_name varchar(30),
                text varchar(2000),
                article_url varchar(100),
                topics varchar(200),
                at_users varchar(1000),
                pics varchar(3000),
                video_url varchar(1000),
                location varchar(100),
                created_at DATETIME,
                source varchar(30),
                attitudes_count INT,
                comments_count INT,
                reposts_count INT,
                retweet_id varchar(20),
                PRIMARY KEY (id),
                ip varchar(100),
                user_authentication varchar(100),
                vip_type varchar(50),
                vip_level INT
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"""
        self.cursor.execute(sql)

    def open_spider(self, spider):
        try:
            import pymysql
            mysql_config = {
                'host': settings.get('MYSQL_HOST', 'localhost'),
                'port': settings.get('MYSQL_PORT', 3306),
                'user': settings.get('MYSQL_USER', 'root'),
                'password': settings.get('MYSQL_PASSWORD', '123456'),
                'charset': 'utf8mb4'
            }
            self.create_database(mysql_config)
            mysql_config['db'] = settings.get('MYSQL_DATABASE', 'weibo')
            self.db = pymysql.connect(**mysql_config)
            self.cursor = self.db.cursor()
            self.create_table()
        except ImportError:
            spider.pymysql_error = True
        except pymysql.OperationalError:
            spider.mysql_error = True

    def process_item(self, item, spider):
        data = dict(item['weibo'])
        data['pics'] = ','.join(data['pics'])
        keys = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql = """INSERT INTO {table}({keys}) VALUES ({values}) ON
                     DUPLICATE KEY UPDATE""".format(table='weibo',
                                                    keys=keys,
                                                    values=values)
        update = ','.join([" {key} = {key}".format(key=key) for key in data])
        sql += update
        try:
            self.cursor.execute(sql, tuple(data.values()))
            self.db.commit()
        except Exception:
            self.db.rollback()
        return item

    def close_spider(self, spider):
        try:
            self.db.close()
        except Exception:
            pass


class DuplicatesPipeline(object):
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['weibo']['id'] in self.ids_seen:
            raise DropItem("过滤重复微博: %s" % item)
        else:
            self.ids_seen.add(item['weibo']['id'])
            return item


class SupertopicFilterPipeline(object):
    """过滤超话内容的管道 - 只保留来自黄霄云超话的微博，并清理文本"""
    
    def __init__(self):
        self.filtered_count = 0
        self.passed_count = 0
        import re
        self.re = re
    
    def process_item(self, item, spider):
        weibo_data = item['weibo']
        
        # 只保留来源为"黄霄云超话"的微博，过滤掉其他来源
        source = weibo_data.get('source', '')
        if source != '黄霄云超话':
            self.filtered_count += 1
            raise DropItem("过滤非超话微博: %s" % item['weibo']['id'])
        
        # 检查微博正文
        text = weibo_data.get('text', '')
        if text:
            # 过滤包含Day1-Day9或day1-day9等日期打卡文案的微博
            if self.re.search(r'[Dd]ay\s*[0-9]+', text):
                self.filtered_count += 1
                raise DropItem("过滤日期打卡微博: %s" % item['weibo']['id'])
      
            # 清理微博正文中的"黄霄云超话"字段
            cleaned_text = text.replace('黄霄云超话', '').strip()
            weibo_data['text'] = cleaned_text
        else:
            # 如果没有正文，也过滤掉
            self.filtered_count += 1
            raise DropItem("过滤无正文微博: %s" % item['weibo']['id'])
        
        self.passed_count += 1
        # 检查是否达到爬取结果数量限制
        if spider.limit_result > 0 and self.passed_count >= spider.limit_result:
            print(f'已达到爬取结果数量限制：{spider.limit_result}条，停止爬取')
            from scrapy.exceptions import CloseSpider
            raise CloseSpider('已达到爬取结果数量限制')
        
        return item


class FilteredJsonPipeline(object):
    """过滤数据并输出为JSON格式，统一输出到blessData.json，相同user_id去重保留最新记录"""
    
    def __init__(self):
        import re
        import json
        import os
        from datetime import datetime
        self.re = re
        self.json = json
        self.os = os
        self.datetime = datetime
        self.bless_data_file = '过滤结果' + os.sep + 'blessData.json'
        self.data_cache = {}  # 用于缓存数据，key为user_id
        
    def process_item(self, item, spider):
        """处理数据项，过滤并格式化输出"""
        weibo_data = item['weibo']
        
        # 过滤微博文本内容
        filtered_text = self.filter_text(weibo_data.get('text', ''))
        
        # 构建过滤后的数据
        filtered_data = {
            'user_id': weibo_data.get('user_id', ''),
            'username': self.get_username(weibo_data),
            'blessing_message': filtered_text,
            'created_at': weibo_data.get('created_at', ''),
            'keyword': item.get('keyword', '')
        }
        
        # 只有当祝福消息不为空时才保存
        if filtered_data['blessing_message'].strip():
            self.save_filtered_data(filtered_data)
        
        return item
    
    def filter_text(self, text):
        """过滤文本内容，移除话题、@用户等信息"""
        if not text:
            return ''
        
        # 移除话题标签 #话题#
        text = self.re.sub(r'#[^#]*#', '', text)
        
        # 移除@用户信息
        text = self.re.sub(r'@[^\s]+', '', text)
        
        # 移除多余的空格和换行
        text = self.re.sub(r'\s+', ' ', text)
        
        # 移除首尾空格
        text = text.strip()
        
        return text
    
    def get_username(self, weibo_data):
        """获取用户名"""
        # 获取用户名信息
        return weibo_data.get('username', '')
    
    def parse_date(self, date_str):
        """解析日期字符串为datetime对象"""
        try:
            # 尝试解析 "2025-12-17 22:55" 格式
            return self.datetime.strptime(date_str, '%Y-%m-%d %H:%M')
        except ValueError:
            try:
                # 尝试解析 "2025-12-17" 格式
                return self.datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                # 如果都失败，返回一个很早的时间
                return self.datetime(1970, 1, 1)
    
    def save_filtered_data(self, data):
        """保存过滤后的数据为JSON格式，统一输出到blessData.json"""
        user_id = data['user_id']
        
        # 检查是否已有该用户的数据
        if user_id in self.data_cache:
            # 比较时间，保留最新的记录
            existing_date = self.parse_date(self.data_cache[user_id]['created_at'])
            new_date = self.parse_date(data['created_at'])
            
            if new_date > existing_date:
                self.data_cache[user_id] = data
        else:
            self.data_cache[user_id] = data
        
        # 每次处理完数据后都更新文件
        self.update_bless_data_file()
    
    def update_bless_data_file(self):
        """更新blessData.json文件"""
        # 创建输出目录
        base_dir = '过滤结果'
        if not self.os.path.isdir(base_dir):
            self.os.makedirs(base_dir)
        
        # 将缓存数据转换为列表
        data_list = list(self.data_cache.values())
        
        # 按创建时间排序（最新的在前）
        data_list.sort(key=lambda x: self.parse_date(x['created_at']), reverse=True)
        
        # 保存数据
        with open(self.bless_data_file, 'w', encoding='utf-8') as f:
            self.json.dump(data_list, f, ensure_ascii=False, indent=2)
    
    def open_spider(self, spider):
        """爬虫开始时加载现有数据"""
        if self.os.path.exists(self.bless_data_file):
            try:
                with open(self.bless_data_file, 'r', encoding='utf-8') as f:
                    existing_data = self.json.load(f)
                    # 将现有数据加载到缓存中
                    for item in existing_data:
                        user_id = item.get('user_id')
                        if user_id:
                            self.data_cache[user_id] = item
            except (self.json.JSONDecodeError, FileNotFoundError):
                self.data_cache = {}
    
    def close_spider(self, spider):
        """爬虫结束时最终保存数据"""
        self.update_bless_data_file()
        print(f"数据已保存到 {self.bless_data_file}，共 {len(self.data_cache)} 条记录")
