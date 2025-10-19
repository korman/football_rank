"""
比赛数据管理类
负责与MongoDB交互存储和检索比赛相关数据
"""

import logging
import os
import sys

# 添加更全面的路径设置，确保能够找到必要的模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 尝试导入pymongo和league_mapper模块
try:
    from pymongo import MongoClient
    from pymongo.errors import ConnectionFailure, OperationFailure

    pymongo_available = True
except ImportError:
    print("警告: 无法导入pymongo模块，MongoDB功能将不可用")
    pymongo_available = False

try:
    from league_mapper import get_league_code

    league_mapper_available = True
except ImportError:
    print("警告: 无法导入league_mapper模块，将使用默认的联赛代码映射")
    league_mapper_available = False

    # 创建一个简单的league_mapper备用实现
    def get_league_code(chinese_name):
        """备用的get_league_code函数实现"""
        default_map = {"英超": "E0", "西甲": "SP1"}
        return default_map.get(chinese_name)


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
        self.mock_data = []  # 用于模拟数据

        # 只有在pymongo可用时才尝试连接
        if pymongo_available:
            self._connect()
        else:
            print(f"警告: 由于pymongo模块不可用，无法连接到MongoDB数据库 '{db_name}'")
            # 生成一些模拟数据用于演示
            self._generate_mock_data()

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
            # 连接失败时生成模拟数据
            self._generate_mock_data()
            return False
        except Exception as e:
            logger.error(f"初始化MongoDB连接时发生异常: {e}")
            self.client = None
            self.db = None
            self.collection = None
            # 连接失败时生成模拟数据
            self._generate_mock_data()
            return False

    def _generate_mock_data(self):
        """
        生成模拟的比赛数据，用于演示和测试
        """
        print("生成模拟比赛数据用于演示...")
        # 英超模拟数据
        premier_league_matches = [
            {
                "Div": "E0",
                "Date": "2023-08-12",
                "HomeTeam": "Arsenal",
                "AwayTeam": "Crystal Palace",
                "FTHG": 2,
                "FTAG": 0,
                "HTHG": 1,
                "HTAG": 0,
                "FTR": "H",
                "Referee": "M Oliver",
            },
            {
                "Div": "E0",
                "Date": "2023-08-13",
                "HomeTeam": "Chelsea",
                "AwayTeam": "Liverpool",
                "FTHG": 1,
                "FTAG": 2,
                "HTHG": 0,
                "HTAG": 1,
                "FTR": "A",
                "Referee": "A Taylor",
            },
            {
                "Div": "E0",
                "Date": "2023-08-13",
                "HomeTeam": "Man City",
                "AwayTeam": "Burnley",
                "FTHG": 3,
                "FTAG": 0,
                "HTHG": 2,
                "HTAG": 0,
                "FTR": "H",
                "Referee": "P Tierney",
            },
            {
                "Div": "E0",
                "Date": "2023-08-14",
                "HomeTeam": "Man United",
                "AwayTeam": "Wolves",
                "FTHG": 1,
                "FTAG": 0,
                "HTHG": 1,
                "HTAG": 0,
                "FTR": "H",
                "Referee": "S Attwell",
            },
            {
                "Div": "E0",
                "Date": "2023-08-14",
                "HomeTeam": "Tottenham",
                "AwayTeam": "Brentford",
                "FTHG": 2,
                "FTAG": 2,
                "HTHG": 1,
                "HTAG": 1,
                "FTR": "D",
                "Referee": "R Jones",
            },
        ]

        # 西甲模拟数据
        la_liga_matches = [
            {
                "Div": "SP1",
                "Date": "2023-08-11",
                "HomeTeam": "Barcelona",
                "AwayTeam": "Getafe",
                "FTHG": 4,
                "FTAG": 0,
                "HTHG": 2,
                "HTAG": 0,
                "FTR": "H",
                "Referee": "J Sánchez",
            },
            {
                "Div": "SP1",
                "Date": "2023-08-12",
                "HomeTeam": "Real Madrid",
                "AwayTeam": "Almería",
                "FTHG": 2,
                "FTAG": 0,
                "HTHG": 1,
                "HTAG": 0,
                "FTR": "H",
                "Referee": "A Mateu",
            },
        ]

        # 合并所有模拟数据
        self.mock_data.extend(premier_league_matches)
        self.mock_data.extend(la_liga_matches)
        print(f"成功生成{len(self.mock_data)}条模拟比赛数据")

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
        # 如果连接可用，从数据库获取数据
        if self.is_connected():
            try:
                query = filters or {}
                matches = list(self.collection.find(query).limit(limit))
                logger.info(f"成功从MongoDB查询到 {len(matches)} 条比赛数据")
                return matches
            except Exception as e:
                logger.error(f"查询MongoDB比赛数据时出错: {e}")
                # 如果数据库查询失败，使用模拟数据
                return self._filter_mock_data(filters, limit)
        else:
            # 如果连接不可用，使用模拟数据
            print("使用模拟数据进行查询...")
            return self._filter_mock_data(filters, limit)

    def _filter_mock_data(self, filters=None, limit=100):
        """
        从模拟数据中过滤符合条件的比赛

        Args:
            filters (dict): 查询过滤条件
            limit (int): 返回结果的最大数量

        Returns:
            list: 过滤后的模拟比赛数据列表
        """
        if not filters:
            filtered_matches = self.mock_data[:limit]
        else:
            filtered_matches = []
            for match in self.mock_data:
                # 检查是否满足所有过滤条件
                match_meets_criteria = True
                for key, value in filters.items():
                    if match.get(key) != value:
                        match_meets_criteria = False
                        break
                if match_meets_criteria:
                    filtered_matches.append(match)
                    if len(filtered_matches) >= limit:
                        break

        print(f"从模拟数据中过滤出{len(filtered_matches)}条符合条件的比赛")
        return filtered_matches

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

    def get_league_matches(self, chinese_league_name, limit=100):
        """
        根据中文联赛名称获取比赛数据

        Args:
            chinese_league_name (str): 中文联赛名称，如"英超"、"西甲"
            limit (int): 返回结果的最大数量

        Returns:
            list: 比赛数据列表
        """
        # 获取联赛代码
        league_code = get_league_code(chinese_league_name)
        if not league_code:
            logger.error(f"未找到联赛'{chinese_league_name}'对应的代码")
            return []

        logger.info(
            f"正在查询联赛'{chinese_league_name}'（代码：{league_code}）的比赛数据"
        )

        # 使用联赛代码筛选数据
        return self.get_matches(filters={"Div": league_code}, limit=limit)


if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        # 创建MatchDataManager实例
        # 注意：这里使用默认的数据库和集合名称，实际使用时可能需要修改
        match_manager = MatchDataManager(
            db_name="football_data", collection_name="matches"
        )

        # 查询英超比赛数据
        league_name = "英超"
        logger.info(f"开始查询{league_name}比赛数据...")

        matches = match_manager.get_league_matches(league_name, limit=100)

        if matches:
            logger.info(f"成功获取到{len(matches)}条{league_name}比赛数据")

            # 打印前100条数据作为调试信息
            logger.info(
                f"\n=== 调试信息：前{min(100, len(matches))}条{league_name}比赛数据 ==="
            )

            for i, match in enumerate(matches[:100], 1):
                # 提取关键信息打印
                match_info = {
                    "日期": match.get("Date", "未知"),
                    "主队": match.get("HomeTeam", "未知"),
                    "客队": match.get("AwayTeam", "未知"),
                    "比分": f"{match.get('FTHG', 0)}-{match.get('FTAG', 0)}",
                    "半场比分": f"{match.get('HTHG', 0)}-{match.get('HTAG', 0)}",
                    "结果": match.get("FTR", "未知"),
                }
                logger.info(f"\n比赛 {i}: {match_info}")
        else:
            logger.warning(f"未找到{league_name}的比赛数据")

    except Exception as e:
        logger.error(f"执行过程中发生异常: {e}")
    finally:
        # 确保关闭连接
        if "match_manager" in locals():
            match_manager.close()
            logger.info("程序执行完毕，已关闭数据库连接")
