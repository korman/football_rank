from match_ranking import MatchRankingSystem


def main():
    # 创建排名系统实例
    ranking_system = MatchRankingSystem()

    # 处理所有比赛并计算排名
    ranking_system.process_all_matches()

    # 打印排名结果
    ranking_system.print_rankings()


if __name__ == "__main__":
    main()
