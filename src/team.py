class Team:
    """
    队伍类，包含队伍的基本信息和评级相关属性

    属性:
        name (str): 队伍名称
        elo (float): Elo评分
        mu (float): TrueSkill评级系统中的mu值（技能均值）
        sigma (float): TrueSkill评级系统中的sigma值（技能不确定性）
        match_count (int): 参与联赛的比赛次数
    """

    def __init__(self, name, elo=1500.0, mu=25.0, sigma=8.333):
        """
        初始化队伍对象

        参数:
            name (str): 队伍名称
            elo (float, optional): 初始Elo评分，默认为1500.0
            mu (float, optional): 初始TrueSkill mu值，默认为25.0
            sigma (float, optional): 初始TrueSkill sigma值，默认为8.333
        """
        self.name = name
        self.elo = elo
        self.mu = mu
        self.sigma = sigma
        self.match_count = 0

    def update_rating(self, new_elo=None, new_mu=None, new_sigma=None):
        """
        更新队伍评级

        参数:
            new_elo (float, optional): 新的Elo评分
            new_mu (float, optional): 新的TrueSkill mu值
            new_sigma (float, optional): 新的TrueSkill sigma值
        """
        if new_elo is not None:
            self.elo = new_elo
        if new_mu is not None:
            self.mu = new_mu
        if new_sigma is not None:
            self.sigma = new_sigma

    def increment_match_count(self):
        """
        增加队伍参与的比赛次数
        """
        self.match_count += 1

    def get_trueskill_rating(self):
        """
        获取TrueSkill评级（2*mu - 3*sigma）

        返回:
            float: TrueSkill评级
        """
        return 2 * self.mu - 3 * self.sigma

    def __str__(self):
        """
        返回队伍的字符串表示
        """
        return (
            f"Team(name='{self.name}', elo={self.elo:.2f}, "
            f"mu={self.mu:.2f}, sigma={self.sigma:.2f}, "
            f"match_count={self.match_count})"
        )

    def __repr__(self):
        """
        返回队伍的正式字符串表示
        """
        return self.__str__()

    def __eq__(self, other):
        """
        比较两个队伍是否相同（基于队伍名称）
        """
        if isinstance(other, Team):
            return self.name == other.name
        return False

    def __hash__(self):
        """
        计算队伍的哈希值，用于在集合中使用
        """
        return hash(self.name)
