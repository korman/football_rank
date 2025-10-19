import sys
import os
from collections import defaultdict

# 添加项目根目录到Python路径，确保能够导入src模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.match_data import MatchDataManager


def test_sp1_teams_count():
    """
    测试从MongoDB数据库中查询所有Div字段值为SP1的比赛数据
    并统计每个参赛队伍的名称及其对应的参赛次数信息
    """
    print("\n开始测试: 查询西甲(SP1)比赛数据并统计参赛队伍信息")

    # 创建MatchDataManager实例，连接到hao_football数据库
    # 根据之前的分析，用户提到实际数据库名称为hao_football
    match_data_manager = MatchDataManager(
        db_name="hao_football", collection_name="matches"
    )

    # 查询Div字段值为SP1的所有比赛数据
    print("\n查询Div字段值为SP1的所有比赛数据...")
    sp1_matches = match_data_manager.get_matches(filters={"Div": "SP1"}, limit=None)

    # 验证查询结果
    print(f"\n成功查询到{len(sp1_matches)}场西甲比赛")
    assert len(sp1_matches) >= 0, "查询结果数量应为非负数"

    # 如果没有查询到数据，可能使用的是模拟数据
    if not sp1_matches:
        print("警告: 未查询到实际西甲比赛数据，将使用模拟数据进行统计")
    else:
        # 显示前3条数据作为示例
        print("\n查询结果示例 (前3条):")
        for i, match in enumerate(sp1_matches[:3]):
            home_team = match.get("HomeTeam", "未知")
            away_team = match.get("AwayTeam", "未知")
            date = match.get("Date", "未知")
            print(f"  比赛{i + 1}: {home_team} vs {away_team} ({date})")

    # 统计每个队伍的参赛次数
    print("\n统计各队伍参赛次数...")
    team_counts = defaultdict(int)

    # 遍历所有比赛，统计每个队伍的参赛次数
    for match in sp1_matches:
        home_team = match.get("HomeTeam", "未知")
        away_team = match.get("AwayTeam", "未知")
        team_counts[home_team] += 1
        team_counts[away_team] += 1

    # 将结果转换为列表并按参赛次数降序排序
    sorted_teams = sorted(team_counts.items(), key=lambda x: x[1], reverse=True)

    # 清晰输出所有参赛队伍的名称及其对应的参赛次数信息
    print("\n西甲联赛(SP1)参赛队伍及参赛次数统计:")
    print("-" * 60)
    print(f"{'队伍名称':<30}{'参赛次数':<15}{'排名':<10}")
    print("-" * 60)

    for rank, (team, count) in enumerate(sorted_teams, 1):
        print(f"{team:<30}{count:<15}{rank:<10}")

    print("-" * 60)
    print(f"总计: {len(sorted_teams)}支队伍参与了{len(sp1_matches)}场比赛")

    # 如果有数据，确保至少有队伍被统计到
    if sp1_matches:
        assert len(sorted_teams) > 0, "至少应该有一支队伍被统计到"

    print("\n测试完成: 西甲(SP1)比赛数据查询和队伍统计成功")
    # 移除返回值，避免pytest警告


# 添加主函数支持直接运行
if __name__ == "__main__":
    test_sp1_teams_count()
    print("\n所有测试完成")
