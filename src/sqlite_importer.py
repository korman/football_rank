import sqlite3
import os
import csv
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SQLiteImporter:
    """
    SQLite数据导入器单例类
    负责将CSV文件数据导入到SQLite数据库中
    实现数据重复性检查，确保不插入重复数据
    """

    _instance: Optional["SQLiteImporter"] = None

    def __new__(cls, *args, **kwargs):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(SQLiteImporter, cls).__new__(cls)
        return cls._instance

    def __init__(self, db_path: str = "match_data.db"):
        """
        初始化SQLite导入器

        Args:
            db_path (str): SQLite数据库文件路径
        """
        # 防止重复初始化
        if not hasattr(self, "_initialized"):
            self.db_path = db_path
            self.conn = None
            self.cursor = None
            self._initialized = True
            # 初始化数据库连接
            self._init_db()

    def _init_db(self):
        """
        初始化数据库：检查数据库文件和表是否存在，不存在则创建
        """
        try:
            # 检查数据库文件是否存在，如果不存在会自动创建
            db_exists = os.path.exists(self.db_path)

            # 建立数据库连接
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()

            if not db_exists:
                logger.info(f"创建新的SQLite数据库: {self.db_path}")
            else:
                logger.info(f"连接到现有SQLite数据库: {self.db_path}")

            # 检查并创建matches表
            self._create_matches_table()

        except Exception as e:
            logger.error(f"初始化数据库时出错: {str(e)}")
            # 确保连接被正确关闭
            if self.conn:
                self.conn.close()
            self.conn = None
            self.cursor = None

    def _create_matches_table(self):
        """
        创建matches表（如果不存在）
        """
        try:
            # 检查表是否存在
            self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='matches'"
            )
            table_exists = self.cursor.fetchone() is not None

            if not table_exists:
                # 创建matches表
                create_table_sql = """
                CREATE TABLE matches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Div TEXT,
                    Date INTEGER,  -- 存储时间戳
                    HomeTeam TEXT,
                    AwayTeam TEXT,
                    FTHG TEXT,
                    FTAG TEXT,
                    FTR TEXT,
                    HTHG TEXT,
                    HTAG TEXT,
                    HTR TEXT,
                    Referee TEXT,
                    HS TEXT,
                    [AS] TEXT,  -- 使用方括号避免 SQL 关键字冲突
                    HST TEXT,
                    AST TEXT,
                    HF TEXT,
                    AF TEXT,
                    HC TEXT,
                    AC TEXT,
                    HY TEXT,
                    AY TEXT,
                    HR TEXT,
                    AR TEXT,
                    -- 添加唯一约束以防止重复数据
                    UNIQUE(Div, Date, HomeTeam, AwayTeam) ON CONFLICT IGNORE
                )
                """
                self.cursor.execute(create_table_sql)
                self.conn.commit()
                logger.info("成功创建matches表")
            else:
                logger.info("matches表已存在")

        except Exception as e:
            logger.error(f"创建matches表时出错: {str(e)}")
            if self.conn:
                self.conn.rollback()

    def import_csv(self, csv_file_path: str) -> Dict[str, Any]:
        """
        从CSV文件导入数据到matches表
        实现数据重复性检查，确保不插入重复数据

        Args:
            csv_file_path (str): CSV文件路径

        Returns:
            Dict[str, Any]: 导入结果统计信息
                - success: 是否成功
                - total_rows: CSV文件总行数
                - imported_rows: 成功导入的行数
                - skipped_rows: 因重复而跳过的行数
                - error: 错误信息（如果有）
        """
        result = {
            "success": False,
            "total_rows": 0,
            "imported_rows": 0,
            "skipped_rows": 0,
            "error": None,
        }

        try:
            # 检查数据库连接是否有效
            if not self.conn:
                self._init_db()
            else:
                # 尝试执行简单的SQL语句来测试连接是否仍然有效
                try:
                    self.cursor.execute("SELECT 1")
                except (sqlite3.OperationalError, AttributeError):
                    # 如果连接已关闭或cursor无效，重新初始化
                    self._init_db()

            # 检查CSV文件是否存在
            if not os.path.exists(csv_file_path):
                raise FileNotFoundError(f"CSV文件不存在: {csv_file_path}")

            logger.info(f"开始导入CSV文件: {csv_file_path}")

            # 读取CSV文件并导入数据
            with open(csv_file_path, "r", encoding="utf-8", newline="") as csvfile:
                csv_reader = csv.DictReader(csvfile)
                total_rows = 0
                imported_rows = 0
                skipped_rows = 0

                for row in csv_reader:
                    total_rows += 1

                    # 准备要插入的数据
                    # 只提取表中存在的字段

                    # 处理Date字段，转换为时间戳
                    date_str = row.get("Date", "")
                    timestamp = None

                    if date_str:
                        try:
                            # 尝试多种日期格式解析
                            # 首先尝试格式1: '21/08/2020,18:00'（包含逗号分隔的时间）
                            if "," in date_str:
                                date_parts = date_str.split(",")
                                date_part = date_parts[0].strip()
                                time_part = date_parts[1].strip()
                                # 检查date_part是否为简写年份格式
                                if len(date_part) == 8 and date_part.count("/") == 2:
                                    # 尝试简写年份格式 '14/08/10'
                                    try:
                                        dt = datetime.strptime(
                                            f"{date_part} {time_part}", "%d/%m/%y %H:%M"
                                        )
                                        timestamp = int(dt.timestamp())
                                    except ValueError:
                                        # 如果简写年份失败，尝试完整年份
                                        dt = datetime.strptime(
                                            f"{date_part} {time_part}", "%d/%m/%Y %H:%M"
                                        )
                                        timestamp = int(dt.timestamp())
                                else:
                                    # 默认使用完整年份格式
                                    dt = datetime.strptime(
                                        f"{date_part} {time_part}", "%d/%m/%Y %H:%M"
                                    )
                                    timestamp = int(dt.timestamp())
                            else:
                                # 尝试格式2: '12/08/2017'（不包含时间）
                                try:
                                    # 先尝试直接解析为日期
                                    if len(date_str) == 8 and date_str.count("/") == 2:
                                        # 尝试简写年份格式 '14/08/10'
                                        dt = datetime.strptime(date_str, "%d/%m/%y")
                                    else:
                                        # 默认使用完整年份格式
                                        dt = datetime.strptime(date_str, "%d/%m/%Y")
                                    # 补充18:00时间
                                    dt = dt.replace(hour=18, minute=0, second=0)
                                    timestamp = int(dt.timestamp())
                                except ValueError:
                                    # 尝试格式3: '21/08/2020 18:00'（空格分隔的时间）
                                    # 检查是否包含时间的简写年份格式
                                    if (
                                        len(date_str) > 8
                                        and date_str.count("/") == 2
                                        and " " in date_str
                                    ):
                                        try:
                                            dt = datetime.strptime(
                                                date_str, "%d/%m/%y %H:%M"
                                            )
                                            timestamp = int(dt.timestamp())
                                        except ValueError:
                                            dt = datetime.strptime(
                                                date_str, "%d/%m/%Y %H:%M"
                                            )
                                            timestamp = int(dt.timestamp())
                                    else:
                                        dt = datetime.strptime(
                                            date_str, "%d/%m/%Y %H:%M"
                                        )
                                        timestamp = int(dt.timestamp())
                        except ValueError:
                            # 如果所有格式都解析失败，记录警告
                            logger.warning(f"无法解析日期格式: {date_str}")
                            timestamp = None

                    data = {
                        "Div": row.get("Div", ""),
                        "Date": timestamp,
                        "HomeTeam": row.get("HomeTeam", ""),
                        "AwayTeam": row.get("AwayTeam", ""),
                        "FTHG": row.get("FTHG", ""),
                        "FTAG": row.get("FTAG", ""),
                        "FTR": row.get("FTR", ""),
                        "HTHG": row.get("HTHG", ""),
                        "HTAG": row.get("HTAG", ""),
                        "HTR": row.get("HTR", ""),
                        "Referee": row.get("Referee", ""),
                        "HS": row.get("HS", ""),
                        "AS": row.get("AS", ""),
                        "HST": row.get("HST", ""),
                        "AST": row.get("AST", ""),
                        "HF": row.get("HF", ""),
                        "AF": row.get("AF", ""),
                        "HC": row.get("HC", ""),
                        "AC": row.get("AC", ""),
                        "HY": row.get("HY", ""),
                        "AY": row.get("AY", ""),
                        "HR": row.get("HR", ""),
                        "AR": row.get("AR", ""),
                    }

                    # 构建插入语句，处理关键字字段
                    columns = []
                    for col in data.keys():
                        # 对AS关键字字段使用方括号
                        if col == "AS":
                            columns.append("[AS]")
                        else:
                            columns.append(col)
                    columns_str = ", ".join(columns)
                    placeholders = ", ".join(["?" for _ in data])
                    insert_sql = f"INSERT OR IGNORE INTO matches ({columns_str}) VALUES ({placeholders})"

                    # 执行插入
                    before_count = self.cursor.execute("SELECT changes()").fetchone()[0]
                    self.cursor.execute(insert_sql, list(data.values()))
                    after_count = self.cursor.execute("SELECT changes()").fetchone()[0]

                    if after_count > 0:
                        imported_rows += 1
                        # 每100行提交一次，避免内存占用过高
                        if imported_rows % 100 == 0:
                            self.conn.commit()
                            logger.info(f"已导入 {imported_rows} 行数据")
                    else:
                        skipped_rows += 1

                # 最终提交
                self.conn.commit()

                result.update(
                    {
                        "success": True,
                        "total_rows": total_rows,
                        "imported_rows": imported_rows,
                        "skipped_rows": skipped_rows,
                    }
                )

                logger.info(
                    f"CSV导入完成: "
                    f"总计{total_rows}行, "
                    f"成功导入{imported_rows}行, "
                    f"因重复跳过{skipped_rows}行"
                )

        except Exception as e:
            logger.error(f"导入CSV文件时出错: {str(e)}")
            result["error"] = str(e)
            if self.conn:
                self.conn.rollback()

        return result

    def close(self):
        """
        关闭数据库连接
        """
        if self.conn:
            try:
                self.conn.close()
                logger.info("SQLite数据库连接已关闭")
            except Exception:
                # 忽略关闭时的异常，确保连接被释放
                pass

    def __del__(self):
        """
        析构函数，确保连接被关闭
        """
        self.close()


# 提供一个便捷的全局访问实例
sqlite_importer = SQLiteImporter()
