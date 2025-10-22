import sqlite3
import json
from typing import Optional


class MatchParser:
    """
    足球比赛JSON解析器：拆分关键字段，存储到SQLite。
    - 提取：api_id (唯一ID), utc_date (ISO-8601 TEXT)。
    - 存储：完整JSON blob + 提取字段，支持去重。
    - 数据库：新建football.db，表matches。
    """

    def __init__(self, db_path: str = "football.db"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self) -> None:
        """连接数据库，创建表（若不存在）。"""
        self.conn = sqlite3.connect(self.db_path)
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                api_id INTEGER PRIMARY KEY,
                utc_date TEXT NOT NULL,
                json_data TEXT NOT NULL
            )
        """)
        # 索引加速日期查询
        cur.execute("CREATE INDEX IF NOT EXISTS idx_utc_date ON matches(utc_date)")
        self.conn.commit()

    def parse_and_store(self, json_str: str) -> int:
        """
        解析JSON字符串，存储比赛数据。
        :param json_str: JSON字符串 (e.g., {"matches": [...]})
        :return: 插入/更新记录数
        """
        if not self.conn:
            raise ValueError("请先调用 connect()")

        try:
            data = json.loads(json_str)
            matches = data.get("matches", [])
            if not isinstance(matches, list):
                raise ValueError("JSON必须包含 'matches' 数组")

            cur = self.conn.cursor()
            inserted = 0
            for match in matches:
                api_id = match.get("id")
                if not api_id:
                    print(
                        f"警告: 跳过无ID的比赛 {match.get('homeTeam', {}).get('name', 'Unknown')}"
                    )
                    continue

                utc_date = match.get("utcDate", "")  # ISO-8601 直接存储
                if not utc_date:
                    print(f"警告: 跳过无日期的比赛 ID {api_id}")
                    continue

                json_data = json.dumps(match)

                # 去重插入
                cur.execute(
                    """
                    INSERT OR IGNORE INTO matches (api_id, utc_date, json_data)
                    VALUES (?, ?, ?)
                """,
                    (api_id, utc_date, json_data),
                )
                if cur.rowcount > 0:
                    inserted += 1
                    print(f"插入: ID {api_id} ({utc_date[:10]})")

            self.conn.commit()
            return inserted
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON解析失败: {e}")

    def query_by_date(self, date_str: str) -> list:
        """示例查询：按日期过滤比赛（YYYY-MM-DD）。"""
        if not self.conn:
            raise ValueError("请先调用 connect()")
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT api_id, utc_date, json_extract(json_data, '$.score.fullTime.home') as home_goals
            FROM matches WHERE date(utc_date) = ?
        """,
            (date_str,),
        )
        return cur.fetchall()

    def close(self) -> None:
        """关闭连接。"""
        if self.conn:
            self.conn.close()
            self.conn = None


# 使用示例
if __name__ == "__main__":
    # 模拟JSON (替换为您的temp_response.json内容)
    sample_json = """
    {
        "matches": [
            {
                "id": 537862,
                "utcDate": "2025-10-18T11:30:00Z",
                "homeTeam": {"id": 351, "name": "Nottingham Forest FC"},
                "awayTeam": {"id": 61, "name": "Chelsea FC"},
                "score": {"fullTime": {"home": 0, "away": 3}}
            }
        ]
    }
    """

    parser = MatchParser()
    parser.connect()
    count = parser.parse_and_store(sample_json)
    print(f"总插入 {count} 场")

    # 测试查询
    results = parser.query_by_date("2025-10-18")
    print("查询结果:", results)

    parser.close()
