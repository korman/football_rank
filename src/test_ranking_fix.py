#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的排名加载功能
"""

import sys
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from match_ranking import MatchRankingSystem
from team_manager import TeamManager
from league_mapper import get_league_code


def test_ranking_methods():
    """测试排名系统的方法"""
    print("开始测试排名系统方法...")

    # 创建排名系统实例
    ranking_system = MatchRankingSystem()

    # 打印可用的方法
    print("\nMatchRankingSystem可用的方法:")
    methods = [method for method in dir(ranking_system) if not method.startswith("_")]
    for method in methods:
        print(f"- {method}")

    # 处理一场测试比赛
    print("\n处理测试比赛...")
    home_team = "曼联"
    away_team = "利物浦"
    home_score = 2
    away_score = 1

    ranking_system.elo_algorithm.process_match(
        home_team, away_team, home_score, away_score
    )
    ranking_system.openskill_algorithm.process_match(
        home_team, away_team, home_score, away_score
    )

    # 获取排名并构建字典
    print("\n获取Elo排名并构建字典:")
    elo_rankings = ranking_system.get_elo_rankings()
    print(f"原始Elo排名: {elo_rankings}")

    elo_dict = dict(elo_rankings)
    print(f"转换为字典后: {elo_dict}")

    # 测试从字典获取评分
    for team in [home_team, away_team, "不存在的队伍"]:
        rating = elo_dict.get(team, 1500)  # 不存在时使用默认值1500
        print(f"队伍 '{team}' 的Elo评分: {rating}")

    print("\n获取OpenSkill排名并构建字典:")
    openskill_rankings = ranking_system.get_openskill_rankings()
    print(f"原始OpenSkill排名(前20个字符): {str(openskill_rankings)[:20]}...")

    openskill_dict = dict(openskill_rankings)
    print(f"转换为字典后(键): {list(openskill_dict.keys())}")

    # 测试从字典获取评分
    for team in [home_team, away_team, "不存在的队伍"]:
        rating = openskill_dict.get(team)
        if rating:
            print(
                f"队伍 '{team}' 的OpenSkill评分: mu={rating[0].mu:.2f}, sigma={rating[0].sigma:.2f}"
            )
        else:
            print(f"队伍 '{team}' 没有OpenSkill评分")

    print("\n排名系统方法测试完成！")


def test_team_manager_league_teams():
    """测试TeamManager的get_teams_by_league方法"""
    print("\n开始测试TeamManager的联赛队伍功能...")

    # 创建队伍管理器实例
    team_manager = TeamManager()

    # 添加测试队伍
    league_code_e0 = get_league_code("英超")
    league_code_sp1 = get_league_code("西甲")

    print(f"\n添加测试队伍到不同联赛:")
    team_manager.create_team("曼联", league=league_code_e0)
    team_manager.create_team("利物浦", league=league_code_e0)
    team_manager.create_team("巴塞罗那", league=league_code_sp1)
    team_manager.create_team("皇家马德里", league=league_code_sp1)

    # 测试get_teams_by_league方法
    print(f"\n通过中文联赛名获取队伍:")

    # 获取英超队伍
    epl_teams = team_manager.get_teams_by_league("英超")
    print(f"英超队伍 ({len(epl_teams)}):")
    for team in epl_teams:
        print(f"- {team.name} (联赛: {team.league})")

    # 获取西甲队伍
    la_liga_teams = team_manager.get_teams_by_league("西甲")
    print(f"西甲队伍 ({len(la_liga_teams)}):")
    for team in la_liga_teams:
        print(f"- {team.name} (联赛: {team.league})")

    # 测试不存在的联赛
    nonexistent_teams = team_manager.get_teams_by_league("不存在的联赛")
    print(f"不存在的联赛队伍数量: {len(nonexistent_teams)}")

    print("\nTeamManager联赛队伍功能测试完成！")


def simulate_main_window_logic():
    """模拟主窗口的排名加载逻辑"""
    print("\n开始模拟主窗口排名加载逻辑...")

    # 创建实例
    ranking_system = MatchRankingSystem()
    team_manager = TeamManager()

    # 设置当前联赛
    current_league = "英超"
    league_code = get_league_code(current_league)

    # 添加测试队伍
    team_manager.create_team("曼联", league=league_code)
    team_manager.create_team("利物浦", league=league_code)
    team_manager.create_team("切尔西", league=league_code)

    # 处理一些测试比赛
    ranking_system.elo_algorithm.process_match("曼联", "利物浦", 2, 1)
    ranking_system.elo_algorithm.process_match("切尔西", "曼联", 0, 0)

    ranking_system.openskill_algorithm.process_match("曼联", "利物浦", 2, 1)
    ranking_system.openskill_algorithm.process_match("切尔西", "曼联", 0, 0)

    # 模拟load_elo_rankings方法
    print(f"\n模拟load_elo_rankings方法:")

    # 获取联赛队伍
    league_teams = team_manager.get_teams_by_league(current_league)

    # 构建排名字典
    all_elo_rankings = dict(ranking_system.get_elo_rankings())

    # 处理排名
    processed_rankings = []
    for team in league_teams:
        elo_rating = all_elo_rankings.get(team.name, team.elo)
        processed_rankings.append((team.name, elo_rating, 1.0, team.match_count))

    # 排序
    processed_rankings.sort(key=lambda x: x[1], reverse=True)

    # 显示结果
    print(f"处理后的Elo排名:")
    for team_name, rating, stability, matches in processed_rankings:
        print(
            f"- {team_name}: 评分={rating:.2f}, 稳定度={stability:.2f}, 场次={matches}"
        )

    # 模拟load_openskill_rankings方法
    print(f"\n模拟load_openskill_rankings方法:")

    # 构建排名字典
    all_openskill_rankings = dict(ranking_system.get_openskill_rankings())
    min_sigma = 1.5

    # 处理排名
    processed_rankings = []
    for team in league_teams:
        openskill_rating = all_openskill_rankings.get(team.name)

        if openskill_rating:
            mu_value = openskill_rating[0].mu
            sigma_value = openskill_rating[0].sigma
        else:
            mu_value = team.mu
            sigma_value = team.sigma

        score = int(mu_value * 25)
        stability_value = (1 / sigma_value) / (1 / min_sigma) * 100
        stability = f"{round(stability_value)}%"

        processed_rankings.append((team.name, score, stability, team.match_count))

    # 排序
    processed_rankings.sort(key=lambda x: x[1], reverse=True)

    # 显示结果
    print(f"处理后的OpenSkill排名:")
    for team_name, score, stability, matches in processed_rankings:
        print(f"- {team_name}: 积分={score}, 稳定度={stability}, 场次={matches}")

    print("\n主窗口排名加载逻辑模拟完成！")


def main():
    """主测试函数"""
    print("=== 开始测试修复后的排名加载功能 ===")

    try:
        # 运行各项测试
        test_ranking_methods()
        test_team_manager_league_teams()
        simulate_main_window_logic()

        print("\n=== 所有测试通过！ ===")
        return 0
    except Exception as e:
        print(f"\n=== 测试失败！错误信息: {e} ===")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
