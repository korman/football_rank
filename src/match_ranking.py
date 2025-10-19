import glob
import os
import pandas as pd
from openskill.models import PlackettLuce


class EloAlgorithm:
    """Elo评级算法实现"""

    def __init__(self, initial_rating=1500, k_factor=30):
        self.initial_rating = initial_rating
        self.k_factor = k_factor
        self.teams = {}

    def expected_result(self, rating_a, rating_b):
        """计算预期结果概率"""
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

    def update_elo(self, rating, expected, actual):
        """更新Elo评分"""
        return rating + self.k_factor * (actual - expected)

    def get_team_rating(self, team_name):
        """获取或初始化队伍评分"""
        if team_name not in self.teams:
            self.teams[team_name] = self.initial_rating
        return self.teams[team_name]

    def process_match(self, home_team, away_team, home_score, away_score):
        """处理单场比赛结果并更新评分"""
        # 获取当前评分
        home_rating = self.get_team_rating(home_team)
        away_rating = self.get_team_rating(away_team)

        # 计算预期结果
        exp_home = self.expected_result(home_rating, away_rating)
        exp_away = 1 - exp_home

        # 确定实际结果
        if home_score > away_score:
            actual_home, actual_away = 1, 0
        elif home_score < away_score:
            actual_home, actual_away = 0, 1
        else:
            actual_home, actual_away = 0.5, 0.5

        # 更新评分
        new_home_rating = self.update_elo(home_rating, exp_home, actual_home)
        new_away_rating = self.update_elo(away_rating, exp_away, actual_away)

        # 保存更新后的评分
        self.teams[home_team] = new_home_rating
        self.teams[away_team] = new_away_rating

    def get_rankings(self):
        """获取排序后的排名"""
        return sorted(self.teams.items(), key=lambda x: x[1], reverse=True)


class OpenSkillAlgorithm:
    """OpenSkill评级算法实现"""

    def __init__(self):
        self.model = PlackettLuce()
        self.teams = {}

    def get_team_rating(self, team_name):
        """获取或初始化队伍评分"""
        if team_name not in self.teams:
            self.teams[team_name] = [self.model.rating()]  # 创建默认评分
        return self.teams[team_name]

    def process_match(self, home_team, away_team, home_score, away_score):
        """处理单场比赛结果并更新评分"""
        # 获取当前评分
        home_rating = self.get_team_rating(home_team)
        away_rating = self.get_team_rating(away_team)

        # 确定排名
        if home_score > away_score:
            ranks = [1, 2]
        elif home_score < away_score:
            ranks = [2, 1]
        else:
            ranks = [1, 1]

        # 更新评分
        updated_ratings = self.model.rate([home_rating, away_rating], ranks=ranks)

        # 保存更新后的评分
        self.teams[home_team] = updated_ratings[0]
        self.teams[away_team] = updated_ratings[1]

    def get_rankings(self):
        """获取排序后的排名"""
        return sorted(self.teams.items(), key=lambda x: x[1][0].mu, reverse=True)


class MatchRankingSystem:
    """比赛排名统计系统主类"""

    def __init__(self, data_dir=None):
        # 使用绝对路径确保正确访问数据
        if data_dir is None:
            # 数据目录在项目根目录的football_data/epl子目录
            self.data_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "football_data",
                "epl",
            )
        else:
            self.data_dir = data_dir
        self.elo_algorithm = EloAlgorithm()
        self.openskill_algorithm = OpenSkillAlgorithm()
        self.all_data = None

    def _extract_year(self, filename):
        """从文件名提取起始年份"""
        base = os.path.basename(filename)
        year_str = base.split(" ")[1].split("-")[0]
        if len(year_str) == 2:
            return int("20" + year_str)
        return int(year_str)

    def load_data(self):
        """加载并预处理比赛数据"""
        # 查找所有CSV文件
        files = glob.glob(os.path.join(self.data_dir, "E0 *.csv"))

        # 按年份排序文件
        sorted_files = sorted(files, key=self._extract_year)

        # 初始化并连接所有数据
        self.all_data = pd.DataFrame()
        for file in sorted_files:
            df_temp = pd.read_csv(file)
            self.all_data = pd.concat([self.all_data, df_temp], ignore_index=True)

        # 转换日期并排序
        self.all_data["Date"] = pd.to_datetime(
            self.all_data["Date"], format="%d/%m/%Y", dayfirst=True, errors="coerce"
        )
        self.all_data = self.all_data.sort_values("Date").reset_index(drop=True)

        # 删除无效数据
        self.all_data = self.all_data.dropna(
            subset=["Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG"]
        )

        return self.all_data

    def process_all_matches(self):
        """处理所有比赛数据"""
        if self.all_data is None:
            self.load_data()

        for _, row in self.all_data.iterrows():
            home = row["HomeTeam"]
            away = row["AwayTeam"]
            home_score = int(row["FTHG"])
            away_score = int(row["FTAG"])

            # 使用两种算法处理同一场比赛
            self.elo_algorithm.process_match(home, away, home_score, away_score)
            self.openskill_algorithm.process_match(home, away, home_score, away_score)

    def get_elo_rankings(self):
        """获取Elo排名"""
        return self.elo_algorithm.get_rankings()

    def get_openskill_rankings(self):
        """获取OpenSkill排名"""
        return self.openskill_algorithm.get_rankings()

    def print_rankings(self):
        """打印所有排名结果"""
        # 打印OpenSkill排名
        print("OpenSkill Rankings (by mu descending):")
        for rank, (team, rating) in enumerate(self.get_openskill_rankings(), start=1):
            print(f"{rank}. {team}: mu={rating[0].mu:.2f}, sigma={rating[0].sigma:.2f}")

        # 打印Elo排名
        print("\nElo Rankings (by rating descending):")
        for rank, (team, rating) in enumerate(self.get_elo_rankings(), start=1):
            print(f"{rank}. {team}: elo={rating:.2f}")
