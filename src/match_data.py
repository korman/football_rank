"""
比赛数据管理类
负责与SQLite交互存储和检索比赛相关数据
"""

import logging
import os
import sys
import sqlite3

# 添加更全面的路径设置，确保能够找到必要的模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 尝试导入league_mapper模块
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
    通过SQLite存储和检索比赛数据
    """

    def __init__(self, db_name=None, collection_name=None):
        """
        初始化比赛数据管理器

        Args:
            db_name (str): 数据库名称 (兼容MongoDB接口，实际忽略)
            collection_name (str): 集合名称 (兼容MongoDB接口，实际忽略)
        """
        # 项目根目录下的match_data.db文件
        self.db_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "match_data.db")
        )
        self.conn = None
        self.cursor = None
        self.mock_data = []  # 用于模拟数据（保留兼容性）
        self._connect()

    def _connect(self):
        """
        建立SQLite连接

        Returns:
            bool: 连接是否成功
        """
        try:
            # 检查数据库文件是否存在
            db_exists = os.path.exists(self.db_path)

            # 建立SQLite连接
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()

            if not db_exists:
                logger.info(f"创建新的SQLite数据库: {self.db_path}")
            else:
                logger.info(f"连接到现有SQLite数据库: {self.db_path}")

            # 检查matches表是否存在，如果不存在，创建一个基础结构
            self._check_table_exists()

            # 保留生成模拟数据的逻辑以确保兼容性
            self._generate_mock_data()

            return True
        except Exception as e:
            logger.error(f"初始化SQLite连接时出错: {e}")
            self.conn = None
            self.cursor = None
            # 连接失败时生成模拟数据
            self._generate_mock_data()
            return False

    def _check_table_exists(self):
        """
        检查matches表是否存在，如果不存在则创建基础结构
        """
        try:
            # 检查表是否存在
            self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='matches'"
            )
            table_exists = self.cursor.fetchone() is not None

            if not table_exists:
                logger.warning("matches表不存在，生成的查询将返回空结果")
        except Exception as e:
            logger.error(f"检查matches表时出错: {e}")

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
        检查是否已连接到SQLite

        Returns:
            bool: 是否已连接
        """
        return self.conn is not None

    def save_match(self, match_data):
        """
        保存一场比赛数据

        Args:
            match_data (dict): 比赛数据字典

        Returns:
            str: 保存的记录ID，如果失败返回None
        """
        if not self.is_connected():
            if not self._connect():
                return None

        try:
            # 提取数据字段和值
            keys = []
            values = []
            placeholders = []

            for key, value in match_data.items():
                # 处理关键字字段AS
                col_name = "[AS]" if key == "AS" else key
                keys.append(col_name)
                values.append(value)
                placeholders.append("?")

            # 构建SQL语句
            sql = f"INSERT INTO matches ({', '.join(keys)}) VALUES ({', '.join(placeholders)})"

            # 执行插入
            self.cursor.execute(sql, values)
            self.conn.commit()

            # 获取插入的ID
            inserted_id = self.cursor.lastrowid
            logger.info(f"成功保存比赛数据，记录ID: {inserted_id}")
            return str(inserted_id)
        except Exception as e:
            logger.error(f"保存比赛数据时出错: {e}")
            if self.conn:
                self.conn.rollback()
            return None

    def save_matches(self, matches_data):
        """
        批量保存比赛数据

        Args:
            matches_data (list): 比赛数据字典列表

        Returns:
            list: 保存的记录ID列表，如果失败返回None
        """
        if not self.is_connected():
            if not self._connect():
                return None

        try:
            inserted_ids = []

            # 逐条插入，SQLite的executemany对于不同结构的字典支持有限
            for match_data in matches_data:
                # 提取数据字段和值
                keys = []
                values = []
                placeholders = []

                for key, value in match_data.items():
                    # 处理关键字字段AS
                    col_name = "[AS]" if key == "AS" else key
                    keys.append(col_name)
                    values.append(value)
                    placeholders.append("?")

                # 构建SQL语句
                sql = f"INSERT INTO matches ({', '.join(keys)}) VALUES ({', '.join(placeholders)})"

                # 执行插入
                self.cursor.execute(sql, values)
                inserted_ids.append(str(self.cursor.lastrowid))

            # 提交事务
            self.conn.commit()
            logger.info(f"成功批量保存 {len(inserted_ids)} 条比赛数据")
            return inserted_ids
        except Exception as e:
            logger.error(f"批量保存比赛数据时出错: {e}")
            if self.conn:
                self.conn.rollback()
            return None

    def get_matches(self, filters=None, limit=None):
        """
        获取比赛数据

        Args:
            filters (dict): 查询过滤条件
            limit (int, None): 返回结果的最大数量，设为None时不限制数量

        Returns:
            list: 比赛数据列表
        """
        # 如果连接可用，从数据库获取数据
        if self.is_connected():
            try:
                # 输出检索命令到控制台
                print(
                    f"执行SQLite查询: 数据库='{self.db_path}', 查询条件={filters}, 限制={limit if limit is not None else '无限制'}"
                )

                # 构建SQL查询
                query = "SELECT * FROM matches"
                params = []

                # 处理过滤条件
                if filters:
                    where_clauses = []
                    for key, value in filters.items():
                        # 处理关键字字段AS
                        if key == "AS":
                            key = "[AS]"
                        where_clauses.append(f"{key} = ?")
                        params.append(value)

                    if where_clauses:
                        query += " WHERE " + " AND ".join(where_clauses)

                # 添加排序：按日期从早到晚排序
                query += " ORDER BY Date ASC"

                # 添加限制
                if limit is not None:
                    query += f" LIMIT {limit}"

                # 执行查询
                self.cursor.execute(query, params)

                # 获取列名
                columns = [desc[0] for desc in self.cursor.description]

                # 转换结果为字典列表
                matches = []
                for row in self.cursor.fetchall():
                    match_dict = {}
                    for i, col in enumerate(columns):
                        # 移除方括号（如果有的话）
                        if col.startswith("[") and col.endswith("]"):
                            col = col[1:-1]
                        match_dict[col] = row[i]
                    matches.append(match_dict)

                print(f"SQLite查询结果: 找到{len(matches)}条数据")
                logger.info(f"成功从SQLite查询到 {len(matches)} 条比赛数据")

                # 如果数据库查询成功但没有找到数据，也使用模拟数据
                if not matches:
                    print("SQLite查询返回空结果，使用模拟数据...")
                    return self._filter_mock_data(filters, limit)

                # 确保返回的数据按日期从早到晚排序
                matches.sort(key=lambda x: x.get("Date", ""))

                # 输出前3条数据的简要信息作为示例
                if matches:
                    print(f"查询结果示例 (前{min(3, len(matches))}条):")
                    for i, match in enumerate(matches[:3]):
                        div = match.get("Div", "N/A")
                        date = match.get("Date", "N/A")
                        home_team = match.get("HomeTeam", "N/A")
                        away_team = match.get("AwayTeam", "N/A")
                        print(
                            f"  数据{i + 1}: 联赛={div}, 日期={date}, 主队={home_team}, 客队={away_team}"
                        )

                return matches
            except Exception as e:
                logger.error(f"查询SQLite比赛数据时出错: {e}")
                print(f"SQLite查询出错: {e}")
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

        # 按日期从早到晚排序模拟数据
        filtered_matches.sort(key=lambda x: x.get("Date", ""))

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
            # 构建更新字段
            update_fields = []
            params = []

            for key, value in update_data.items():
                # 处理关键字字段AS
                col_name = "[AS]" if key == "AS" else key
                update_fields.append(f"{col_name} = ?")
                params.append(value)

            # 添加ID参数
            params.append(match_id)

            # 构建SQL语句
            sql = f"UPDATE matches SET {', '.join(update_fields)} WHERE id = ?"

            # 执行更新
            self.cursor.execute(sql, params)
            self.conn.commit()

            # 检查是否有更新
            modified_count = self.cursor.rowcount
            logger.info(f"更新比赛数据，修改了 {modified_count} 条记录")
            return modified_count > 0
        except Exception as e:
            logger.error(f"更新比赛数据时出错: {e}")
            if self.conn:
                self.conn.rollback()
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
            # 执行删除
            self.cursor.execute("DELETE FROM matches WHERE id = ?", (match_id,))
            self.conn.commit()

            # 检查是否有删除
            deleted_count = self.cursor.rowcount
            logger.info(f"删除比赛数据，匹配到并删除了 {deleted_count} 条记录")
            return deleted_count > 0
        except Exception as e:
            logger.error(f"删除比赛数据时出错: {e}")
            if self.conn:
                self.conn.rollback()
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
            # 转换键格式为SQLite索引格式
            if isinstance(keys, dict):
                # 处理MongoDB格式的索引定义 {"field": 1}
                index_fields = []
                for field, order in keys.items():
                    # 处理关键字字段AS
                    col_name = "[AS]" if field == "AS" else field
                    index_fields.append(f"{col_name} {'ASC' if order > 0 else 'DESC'}")
                index_sql = f"CREATE {'UNIQUE' if unique else ''} INDEX idx_{'_'.join(keys.keys())} ON matches ({', '.join(index_fields)})"
            elif isinstance(keys, list):
                # 处理字段列表格式
                index_fields = []
                for field in keys:
                    # 处理关键字字段AS
                    if isinstance(field, tuple):  # 支持 (field, order) 格式
                        field_name, order = field
                        col_name = "[AS]" if field_name == "AS" else field_name
                        index_fields.append(
                            f"{col_name} {'ASC' if order > 0 else 'DESC'}"
                        )
                    else:  # 简单字段名
                        col_name = "[AS]" if field == "AS" else field
                        index_fields.append(col_name)
                index_sql = f"CREATE {'UNIQUE' if unique else ''} INDEX idx_{'_'.join([f[0] if isinstance(f, tuple) else f for f in keys])} ON matches ({', '.join(index_fields)})"
            else:
                # 单个字段
                field = keys
                col_name = "[AS]" if field == "AS" else field
                index_sql = f"CREATE {'UNIQUE' if unique else ''} INDEX idx_{field} ON matches ({col_name})"

            # 执行索引创建
            self.cursor.execute(index_sql)
            self.conn.commit()
            logger.info(f"成功创建SQLite索引: {keys}, 唯一: {unique}")
            return True
        except Exception as e:
            logger.error(f"创建索引时出错: {e}")
            if self.conn:
                self.conn.rollback()
            return False

    def close(self):
        """
        关闭SQLite连接
        """
        if self.conn:
            try:
                self.conn.close()
                logger.info("SQLite连接已关闭")
            except Exception as e:
                logger.error(f"关闭SQLite连接时出错: {e}")
            finally:
                self.conn = None
                self.cursor = None

    def __del__(self):
        """
        析构函数，确保连接被关闭
        """
        self.close()

    def get_league_matches(self, league_name, season=None, limit=None):
        """
        获取指定联赛的比赛数据

        Args:
            league_name (str): 联赛中文名称
            season (str, optional): 赛季，格式如 "2023-24"
            limit (int, optional): 返回结果数量限制

        Returns:
            list: 比赛数据列表
        """
        # 转换联赛中文名称为英文代码
        league_code = get_league_code(league_name)
        if not league_code:
            logger.warning(f"未找到联赛: {league_name}")
            return []

        logger.info(f"正在查询联赛'{league_name}'（代码：{league_code}）的比赛数据")

        # 构建查询条件字典
        query = {"Div": league_code}
        if season:
            query["Season"] = season

        # 获取数据 - 直接传递查询字典给get_matches
        return self.get_matches(query, limit=limit)
