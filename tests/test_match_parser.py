import os
import json
import sqlite3
import pytest

# 添加项目根目录到Python路径，使src模块可以被导入
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.match_parser import MatchParser


class TestMatchParser:
    """测试MatchParser类的功能"""

    @pytest.fixture
    def test_data(self):
        """加载测试数据"""
        test_file_path = os.path.join(
            os.path.dirname(__file__), "..", "temp_files", "temp_response.json"
        )
        with open(test_file_path, "r", encoding="utf-8") as f:
            return json.dumps(json.load(f))  # 返回JSON字符串

    @pytest.fixture
    def temp_db_path(self, tmp_path):
        """创建临时数据库路径"""
        return str(tmp_path / "test_football.db")

    @pytest.fixture
    def parser(self, temp_db_path):
        """创建并连接MatchParser实例"""
        parser = MatchParser(db_path=temp_db_path)
        parser.connect()
        yield parser
        parser.close()

    def test_connect_creates_table(self, temp_db_path):
        """测试connect方法是否正确创建表"""
        parser = MatchParser(db_path=temp_db_path)
        parser.connect()

        # 检查表是否存在
        cursor = parser.conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='matches'"
        )
        table_exists = cursor.fetchone() is not None

        assert table_exists, "matches表应该被创建"

        # 检查表结构
        cursor.execute("PRAGMA table_info(matches)")
        columns = [row[1] for row in cursor.fetchall()]

        assert "api_id" in columns, "表应该包含api_id列"
        assert "utc_date" in columns, "表应该包含utc_date列"
        assert "json_data" in columns, "表应该包含json_data列"

        parser.close()

    def test_parse_and_store(self, parser, test_data):
        """测试parse_and_store方法是否正确解析和存储数据"""
        # 解析并存储数据
        inserted_count = parser.parse_and_store(test_data)

        # 验证插入的记录数
        cursor = parser.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM matches")
        total_count = cursor.fetchone()[0]

        assert inserted_count > 0, "应该插入至少一条记录"
        assert total_count == inserted_count, "插入的记录数应该等于数据库中的记录数"

        # 验证数据完整性
        cursor.execute("SELECT api_id, utc_date FROM matches LIMIT 1")
        row = cursor.fetchone()
        assert row is not None, "数据库中应该有记录"
        assert row[0] is not None, "api_id不应该为None"
        assert row[1] is not None, "utc_date不应该为None"

    def test_parse_and_store_duplicate(self, parser, test_data):
        """测试parse_and_store方法对重复数据的处理"""
        # 第一次插入
        first_count = parser.parse_and_store(test_data)

        # 第二次插入相同数据
        second_count = parser.parse_and_store(test_data)

        # 验证第二次插入的记录数为0（去重）
        assert second_count == 0, "重复数据不应该被插入"

        cursor = parser.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM matches")
        total_count = cursor.fetchone()[0]

        assert total_count == first_count, "总记录数应该等于第一次插入的数量"

    def test_query_by_date(self, parser, test_data):
        """测试query_by_date方法是否正确查询数据"""
        # 先存储数据
        parser.parse_and_store(test_data)

        # 解析测试数据，获取第一个比赛的日期
        data = json.loads(test_data)
        first_match = data.get("matches", [])[0] if data.get("matches") else None
        if first_match:
            match_date = first_match.get("utcDate", "")[:10]  # 获取YYYY-MM-DD格式

            # 按日期查询
            results = parser.query_by_date(match_date)

            assert len(results) > 0, f"应该能查询到{match_date}的比赛"

            # 验证查询结果
            for result in results:
                assert len(result) == 3, "查询结果应该包含3个字段"
                assert isinstance(result[0], int), "api_id应该是整数"
                assert result[1].startswith(match_date), "日期应该匹配"

    def test_error_handling(self, parser, temp_db_path):
        """测试错误处理"""
        # 测试未连接时调用方法
        unconnected_parser = MatchParser(db_path=temp_db_path)
        with pytest.raises(ValueError, match="请先调用 connect()"):
            unconnected_parser.parse_and_store("{}")

        # 测试无效JSON
        with pytest.raises(ValueError, match="JSON解析失败"):
            parser.parse_and_store("invalid json")

        # 测试缺少matches字段的JSON（实际行为是返回0条记录，不抛出异常）
        # 这与match_parser.py中的实现一致：matches = data.get("matches", [])
        count = parser.parse_and_store("{}")
        assert count == 0, "对于缺少matches字段的JSON，应该返回0条插入记录"

    def test_close_connection(self, temp_db_path):
        """测试close方法是否正确关闭连接"""
        parser = MatchParser(db_path=temp_db_path)
        parser.connect()

        # 验证连接已建立
        assert parser.conn is not None

        # 关闭连接
        parser.close()

        # 验证连接已关闭
        assert parser.conn is None

        # 尝试使用已关闭的连接
        with pytest.raises(ValueError, match="请先调用 connect()"):
            parser.parse_and_store("{}")


if __name__ == "__main__":
    pytest.main([__file__, "-s"])
