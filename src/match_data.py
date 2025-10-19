"""
比赛数据管理类
负责与MongoDB交互存储和检索比赛相关数据
"""

import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

logger = logging.getLogger(__name__)


class MatchDataManager:
    """
    比赛数据管理类，负责管理和操作比赛相关数据
    通过MongoDB存储和检索比赛数据
    """

    def __init__(
        self, db_name, collection_name, mongo_uri="mongodb://localhost:27017/"
    ):
        """
        初始化比赛数据管理器

        Args:
            db_name (str): 数据库名称
            collection_name (str): 集合名称
            mongo_uri (str): MongoDB连接URI
        """
        self.db_name = db_name
        self.collection_name = collection_name
        self.mongo_uri = mongo_uri
        self.client = None
        self.db = None
        self.collection = None
        self._connect()

    def _connect(self):
        """
        建立MongoDB连接

        Returns:
            bool: 连接是否成功
        """
        try:
            self.client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=5000)
            self.client.server_info()  # 验证连接
            self.db = self.client[self.db_name]
            self.collection = self.db[self.collection_name]
            logger.info(
                f"成功连接到MongoDB数据库 '{self.db_name}' 的集合 '{self.collection_name}'"
            )
            return True
        except ConnectionFailure as e:
            logger.error(f"连接到MongoDB失败: {e}")
            self.client = None
            self.db = None
            self.collection = None
            return False
        except Exception as e:
            logger.error(f"初始化MongoDB连接时发生异常: {e}")
            self.client = None
            self.db = None
            self.collection = None
            return False

    def is_connected(self):
        """
        检查是否已连接到MongoDB

        Returns:
            bool: 是否已连接
        """
        return self.client is not None

    def save_match(self, match_data):
        """
        保存一场比赛数据

        Args:
            match_data (dict): 比赛数据字典

        Returns:
            str: 保存的文档ID，如果失败返回None
        """
        if not self.is_connected():
            if not self._connect():
                return None

        try:
            result = self.collection.insert_one(match_data)
            logger.info(f"成功保存比赛数据，文档ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"保存比赛数据时出错: {e}")
            return None

    def save_matches(self, matches_data):
        """
        批量保存比赛数据

        Args:
            matches_data (list): 比赛数据字典列表

        Returns:
            list: 保存的文档ID列表，如果失败返回None
        """
        if not self.is_connected():
            if not self._connect():
                return None

        try:
            result = self.collection.insert_many(matches_data)
            logger.info(f"成功批量保存 {len(result.inserted_ids)} 条比赛数据")
            return [str(id) for id in result.inserted_ids]
        except Exception as e:
            logger.error(f"批量保存比赛数据时出错: {e}")
            return None

    def get_matches(self, filters=None, limit=100):
        """
        获取比赛数据

        Args:
            filters (dict): 查询过滤条件
            limit (int): 返回结果的最大数量

        Returns:
            list: 比赛数据列表
        """
        if not self.is_connected():
            if not self._connect():
                return []

        try:
            query = filters or {}
            matches = list(self.collection.find(query).limit(limit))
            logger.info(f"成功查询到 {len(matches)} 条比赛数据")
            return matches
        except Exception as e:
            logger.error(f"查询比赛数据时出错: {e}")
            return []

    def update_match(self, match_id, update_data):
        """
        更新比赛数据

        Args:
            match_id (str): 比赛ID
            update_data (dict): 更新数据

        Returns:
            bool: 更新是否成功
        """
        if not self.is_connected():
            if not self._connect():
                return False

        try:
            result = self.collection.update_one(
                {"_id": match_id}, {"$set": update_data}
            )
            logger.info(
                f"更新比赛数据，匹配到 {result.matched_count} 条，修改了 {result.modified_count} 条"
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"更新比赛数据时出错: {e}")
            return False

    def delete_match(self, match_id):
        """
        删除比赛数据

        Args:
            match_id (str): 比赛ID

        Returns:
            bool: 删除是否成功
        """
        if not self.is_connected():
            if not self._connect():
                return False

        try:
            result = self.collection.delete_one({"_id": match_id})
            logger.info(f"删除比赛数据，匹配到并删除了 {result.deleted_count} 条")
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"删除比赛数据时出错: {e}")
            return False

    def create_index(self, keys, unique=False):
        """
        创建索引以提高查询性能

        Args:
            keys (dict or list): 索引键
            unique (bool): 是否为唯一索引

        Returns:
            bool: 创建是否成功
        """
        if not self.is_connected():
            if not self._connect():
                return False

        try:
            self.collection.create_index(keys, unique=unique)
            logger.info(f"成功创建索引: {keys}, 唯一: {unique}")
            return True
        except Exception as e:
            logger.error(f"创建索引时出错: {e}")
            return False

    def close(self):
        """
        关闭MongoDB连接
        """
        if self.client:
            try:
                self.client.close()
                logger.info("MongoDB连接已关闭")
            except Exception as e:
                logger.error(f"关闭MongoDB连接时出错: {e}")
            finally:
                self.client = None
                self.db = None
                self.collection = None

    def __del__(self):
        """
        析构函数，确保连接被关闭
        """
        self.close()
