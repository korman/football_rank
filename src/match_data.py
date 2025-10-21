"""
比赛数据管理类
负责与SQLite交互存储和检索比赛相关数据
"""

import logging
import os
import sys
import sqlite3
from datetime import datetime

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

    def __init__(self):
        """
        初始化比赛数据管理器
        连接到SQLite数据库，用于存储和检索比赛数据
        """
        # 项目根目录下的match_data.db文件
        self.db_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "match_data.db")
        )
        self.conn = None
        self.cursor = None
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

            return True
        except Exception as e:
            logger.error(f"初始化SQLite连接时出错: {e}")
            self.conn = None
            self.cursor = None
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

                        # 处理Date字段，确保它是时间戳格式
                        if col == "Date" and row[i] is not None:
                            # 如果已经是整数类型，直接保留（时间戳格式）
                            if isinstance(row[i], int):
                                match_dict[col] = row[i]
                            else:
                                # 如果是字符串，尝试转换为时间戳
                                try:
                                    # 尝试将字符串转换为时间戳
                                    # 注意：这里根据实际存储格式可能需要调整
                                    timestamp = int(row[i])
                                    match_dict[col] = timestamp
                                except (ValueError, TypeError):
                                    # 如果无法转换，记录警告并保持原样
                                    logger.warning(
                                        f"无法将日期值'{row[i]}'转换为时间戳"
                                    )
                                    match_dict[col] = row[i]
                        else:
                            match_dict[col] = row[i]
                    matches.append(match_dict)

                print(f"SQLite查询结果: 找到{len(matches)}条数据")
                logger.info(f"成功从SQLite查询到 {len(matches)} 条比赛数据")

                # 如果数据库查询成功但没有找到数据，返回空列表
                if not matches:
                    print("SQLite查询返回空结果")
                    return []

                # 确保返回的数据按日期从早到晚排序
                # 对于时间戳，我们需要特殊处理排序逻辑
                matches.sort(
                    key=lambda x: (
                        x.get("Date", 0) if isinstance(x.get("Date"), int) else 0
                    )
                )

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
                return []
        else:
            # 如果连接不可用，返回空列表
            print("数据库连接不可用")
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

    def create_index(self, field_name, unique=False):
        """
        创建SQLite索引以提高查询性能

        Args:
            field_name (str): 要索引的字段名
            unique (bool): 是否为唯一索引

        Returns:
            bool: 创建是否成功
        """
        if not self.is_connected():
            if not self._connect():
                return False

        try:
            # 处理关键字字段AS
            col_name = "[AS]" if field_name == "AS" else field_name
            index_name = f"idx_{col_name}"

            # 检查索引是否已存在
            self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name=?",
                (index_name,),
            )
            if self.cursor.fetchone():
                logger.info(f"索引 {index_name} 已存在")
                return True

            # 创建索引
            index_sql = f"CREATE {'UNIQUE' if unique else ''} INDEX {index_name} ON matches ({col_name})"
            self.cursor.execute(index_sql)
            self.conn.commit()
            logger.info(f"成功创建索引: {index_name} on {col_name}")
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
