#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试脚本：验证TeamManager在主窗口中的集成
"""

import os
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入必要的模块（不包括PyQt6）
from match_data import MatchDataManager
from team_manager import TeamManager


class TestTeamIntegration:
    """测试TeamManager集成的类"""

    def __init__(self):
        # 初始化数据管理器和队伍管理器
        self.match_data_manager = MatchDataManager()
        self.team_manager = TeamManager()
        print("初始化完成：MatchDataManager和TeamManager已创建")

    def test_team_creation_and_update(self):
        """测试队伍创建和更新功能"""
        print("\n开始测试队伍创建和更新功能...")

        # 模拟比赛数据
        mock_matches = [
            {"HomeTeam": "曼联", "AwayTeam": "利物浦", "FTHG": 2, "FTAG": 1},
            {"HomeTeam": "切尔西", "AwayTeam": "阿森纳", "FTHG": 0, "FTAG": 0},
            {"HomeTeam": "曼联", "AwayTeam": "切尔西", "FTHG": 3, "FTAG": 1},
        ]

        # 模拟_load_and_process_data函数中的队伍处理逻辑
        for match in mock_matches:
            home = match["HomeTeam"]
            away = match["AwayTeam"]

            # 创建队伍
            self.team_manager.create_team(home)
            self.team_manager.create_team(away)

            # 更新比赛次数
            self.team_manager.increment_match_count(home)
            self.team_manager.increment_match_count(away)

            print(f"处理比赛: {home} {match['FTHG']}-{match['FTAG']} {away}")

        # 验证队伍创建和比赛次数
        print("\n验证队伍创建和比赛次数:")
        teams = self.team_manager.get_all_teams()

        for team in teams:
            print(f"队伍: {team.name}, Elo: {team.elo}, 比赛次数: {team.match_count}")

        # 验证队伍的唯一性
        print("\n验证队伍的唯一性（再次创建已存在的队伍）:")
        self.team_manager.create_team("曼联")  # 应该不会创建新的，而是返回已存在的
        team = self.team_manager.get_team("曼联")
        print(f"曼联 - 确认存在，比赛次数: {team.match_count}")  # 比赛次数应该还是2次

        # 再次增加比赛次数
        self.team_manager.increment_match_count("曼联")
        print(f"曼联 - 增加比赛次数后: {team.match_count}")  # 现在应该是3次

        print("\n测试完成！")


if __name__ == "__main__":
    # 创建测试实例并运行测试
    test = TestTeamIntegration()
    test.test_team_creation_and_update()
