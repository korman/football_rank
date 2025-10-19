#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试脚本：验证Team类的league属性和TeamManager的get_teams_by_league方法
"""

import os
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入必要的模块
from team_manager import TeamManager
from league_mapper import get_league_code


class TestLeagueTeams:
    """测试队伍联赛属性和按联赛获取队伍功能"""

    def __init__(self):
        # 初始化队伍管理器
        self.team_manager = TeamManager()
        print("初始化完成：TeamManager已创建")

    def test_league_property(self):
        """测试Team类的league属性"""
        print("\n开始测试Team类的league属性...")

        # 创建带联赛信息的队伍
        premier_league_code = get_league_code("英超")
        la_liga_code = get_league_code("西甲")

        print(f"英超联赛代码: {premier_league_code}")
        print(f"西甲联赛代码: {la_liga_code}")

        # 创建英超队伍
        man_utd, is_new1 = self.team_manager.create_team(
            "曼联", league=premier_league_code
        )
        liverpool, is_new2 = self.team_manager.create_team(
            "利物浦", league=premier_league_code
        )

        # 创建西甲队伍
        barcelona, is_new3 = self.team_manager.create_team(
            "巴塞罗那", league=la_liga_code
        )
        real_madrid, is_new4 = self.team_manager.create_team(
            "皇家马德里", league=la_liga_code
        )

        # 创建没有联赛信息的队伍
        bayern, is_new5 = self.team_manager.create_team("拜仁慕尼黑")

        print(f"曼联 - 联赛: {man_utd.league}")
        print(f"利物浦 - 联赛: {liverpool.league}")
        print(f"巴塞罗那 - 联赛: {barcelona.league}")
        print(f"皇家马德里 - 联赛: {real_madrid.league}")
        print(f"拜仁慕尼黑 - 联赛: {bayern.league}")

        # 测试更新已有队伍的联赛信息
        print("\n测试更新已有队伍的联赛信息...")
        self.team_manager.create_team("拜仁慕尼黑", league="B1")  # 模拟德甲代码
        updated_bayern = self.team_manager.get_team("拜仁慕尼黑")
        print(f"拜仁慕尼黑(更新后) - 联赛: {updated_bayern.league}")

    def test_get_teams_by_league(self):
        """测试TeamManager的get_teams_by_league方法"""
        print("\n开始测试get_teams_by_league方法...")

        # 获取英超队伍
        premier_league_teams = self.team_manager.get_teams_by_league("英超")
        print(f"\n英超队伍 ({len(premier_league_teams)}支):")
        for team in premier_league_teams:
            print(f"  - {team.name} (联赛: {team.league})")

        # 获取西甲队伍
        la_liga_teams = self.team_manager.get_teams_by_league("西甲")
        print(f"\n西甲队伍 ({len(la_liga_teams)}支):")
        for team in la_liga_teams:
            print(f"  - {team.name} (联赛: {team.league})")

        # 测试不存在的联赛
        invalid_teams = self.team_manager.get_teams_by_league("德甲")
        print(f"\n不存在的联赛队伍数量: {len(invalid_teams)}")

    def run_all_tests(self):
        """运行所有测试"""
        self.test_league_property()
        self.test_get_teams_by_league()
        print("\n所有测试完成！")


if __name__ == "__main__":
    # 创建测试实例并运行测试
    test = TestLeagueTeams()
    test.run_all_tests()
