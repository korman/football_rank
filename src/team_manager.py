import sys
import os

# 确保当前目录在Python路径中
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from team import Team
import logging

logger = logging.getLogger(__name__)


class TeamManager:
    """
    队伍管理器，负责队伍的创建、存储和管理，确保队伍的唯一性
    """

    def __init__(self):
        """
        初始化队伍管理器
        """
        # 使用字典存储队伍，键为队伍名称，值为Team对象
        self._teams = {}
        logger.info("队伍管理器已初始化")

    def create_team(self, name, elo=1500.0, mu=25.0, sigma=8.333):
        """
        创建新队伍，如果队伍已存在则返回现有队伍

        参数:
            name (str): 队伍名称
            elo (float, optional): 初始Elo评分
            mu (float, optional): 初始TrueSkill mu值
            sigma (float, optional): 初始TrueSkill sigma值

        返回:
            Team: 队伍对象
            bool: 是否是新创建的队伍（True表示新创建，False表示返回已有队伍）
        """
        # 检查队伍是否已存在
        if name in self._teams:
            logger.warning(f"队伍 '{name}' 已存在，返回现有队伍")
            return self._teams[name], False

        # 创建新队伍
        team = Team(name, elo, mu, sigma)
        self._teams[name] = team
        logger.info(f"成功创建新队伍: {name}")
        return team, True

    def get_team(self, name):
        """
        获取指定名称的队伍

        参数:
            name (str): 队伍名称

        返回:
            Team or None: 如果队伍存在返回Team对象，否则返回None
        """
        return self._teams.get(name)

    def get_all_teams(self):
        """
        获取所有队伍

        返回:
            list: 所有Team对象的列表
        """
        return list(self._teams.values())

    def get_team_names(self):
        """
        获取所有队伍名称

        返回:
            list: 所有队伍名称的列表
        """
        return list(self._teams.keys())

    def update_team_rating(self, name, new_elo=None, new_mu=None, new_sigma=None):
        """
        更新队伍评级

        参数:
            name (str): 队伍名称
            new_elo (float, optional): 新的Elo评分
            new_mu (float, optional): 新的TrueSkill mu值
            new_sigma (float, optional): 新的TrueSkill sigma值

        返回:
            bool: 更新是否成功
        """
        team = self.get_team(name)
        if team:
            team.update_rating(new_elo, new_mu, new_sigma)
            logger.info(
                f"更新队伍 '{name}' 的评级: Elo={new_elo}, mu={new_mu}, sigma={new_sigma}"
            )
            return True
        logger.warning(f"更新失败，队伍 '{name}' 不存在")
        return False

    def increment_match_count(self, name):
        """
        增加队伍参与的比赛次数

        参数:
            name (str): 队伍名称

        返回:
            bool: 操作是否成功
        """
        team = self.get_team(name)
        if team:
            team.increment_match_count()
            logger.info(f"增加队伍 '{name}' 的比赛次数至 {team.match_count}")
            return True
        logger.warning(f"操作失败，队伍 '{name}' 不存在")
        return False

    def delete_team(self, name):
        """
        删除队伍

        参数:
            name (str): 队伍名称

        返回:
            bool: 删除是否成功
        """
        if name in self._teams:
            del self._teams[name]
            logger.info(f"成功删除队伍: {name}")
            return True
        logger.warning(f"删除失败，队伍 '{name}' 不存在")
        return False

    def team_exists(self, name):
        """
        检查队伍是否存在

        参数:
            name (str): 队伍名称

        返回:
            bool: 队伍是否存在
        """
        return name in self._teams

    def get_team_count(self):
        """
        获取队伍总数

        返回:
            int: 队伍数量
        """
        return len(self._teams)

    def get_teams_sorted_by_elo(self, descending=True):
        """
        获取按Elo评分排序的队伍列表

        参数:
            descending (bool): 是否降序排列

        返回:
            list: 排序后的Team对象列表
        """
        return sorted(
            self._teams.values(), key=lambda team: team.elo, reverse=descending
        )

    def get_teams_sorted_by_trueskill(self, descending=True):
        """
        获取按TrueSkill评分排序的队伍列表

        参数:
            descending (bool): 是否降序排列

        返回:
            list: 排序后的Team对象列表
        """
        return sorted(
            self._teams.values(),
            key=lambda team: team.get_trueskill_rating(),
            reverse=descending,
        )

    def clear_all_teams(self):
        """
        清除所有队伍
        """
        self._teams.clear()
        logger.info("已清除所有队伍")

    def __str__(self):
        """
        返回队伍管理器的字符串表示
        """
        return f"TeamManager(队伍数量={self.get_team_count()})"

    def __repr__(self):
        """
        返回队伍管理器的正式字符串表示
        """
        return self.__str__()


# 测试代码
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # 创建队伍管理器
    manager = TeamManager()
    print(manager)

    # 创建队伍
    team1, is_new1 = manager.create_team("曼联")
    team2, is_new2 = manager.create_team("利物浦", elo=1600.0)
    team3, is_new3 = manager.create_team("切尔西", elo=1550.0)

    print(f"创建队伍结果: {team1}, 新队伍: {is_new1}")
    print(f"创建队伍结果: {team2}, 新队伍: {is_new2}")

    # 测试队伍唯一性
    team4, is_new4 = manager.create_team("曼联")
    print(f"再次创建曼联: {is_new4} (应为False)")

    # 测试获取队伍
    print(f"获取队伍曼联: {manager.get_team('曼联')}")
    print(f"获取不存在队伍: {manager.get_team('阿森纳')}")

    # 测试更新评级
    manager.update_team_rating("曼联", new_elo=1520.0)
    print(f"更新后曼联: {manager.get_team('曼联')}")

    # 测试增加比赛次数
    manager.increment_match_count("曼联")
    manager.increment_match_count("曼联")
    print(f"增加比赛次数后曼联: {manager.get_team('曼联')}")

    # 测试排序
    print("\n按Elo排序的队伍:")
    for team in manager.get_teams_sorted_by_elo():
        print(f"  {team.name}: {team.elo:.2f}")

    # 测试删除队伍
    manager.delete_team("利物浦")
    print(f"\n删除后队伍数量: {manager.get_team_count()}")
    print(f"所有队伍: {manager.get_team_names()}")
