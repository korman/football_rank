from datetime import datetime
from typing import Optional


class MatchInfo:
    """
    比赛信息类，用于存储比赛相关的详细数据

    属性:
        match_id: int 比赛数据库中的id值
        mu: float 比赛之后的mu值
        elo: float 比赛之后的elo值
        sigma: float 比赛之后的sigma值
        match_date: datetime 比赛日期
    """

    def __init__(
        self, match_id: int, mu: float, elo: float, sigma: float, match_date: datetime
    ):
        """
        初始化MatchInfo对象

        参数:
            match_id: 比赛数据库中的id值
            mu: 比赛之后的mu值
            elo: 比赛之后的elo值
            sigma: 比赛之后的sigma值
            match_date: 比赛日期
        """
        self.match_id = match_id
        self.mu = mu
        self.elo = elo
        self.sigma = sigma
        self.match_date = match_date

    def __str__(self) -> str:
        """返回对象的字符串表示"""
        return f"MatchInfo(id={self.match_id}, date={self.match_date}, mu={self.mu:.2f}, elo={self.elo:.2f}, sigma={self.sigma:.2f})"

    def __repr__(self) -> str:
        """返回对象的正式字符串表示"""
        return self.__str__()

    def to_dict(self) -> dict:
        """
        将对象转换为字典格式

        返回:
            dict: 包含所有属性的字典
        """
        return {
            "match_id": self.match_id,
            "mu": self.mu,
            "elo": self.elo,
            "sigma": self.sigma,
            "match_date": self.match_date.isoformat() if self.match_date else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MatchInfo":
        """
        从字典创建MatchInfo对象

        参数:
            data: 包含必要属性的字典

        返回:
            MatchInfo: 创建的MatchInfo对象
        """
        # 确保日期字符串转换为datetime对象
        match_date = data.get("match_date")
        if isinstance(match_date, str):
            match_date = datetime.fromisoformat(match_date)

        return cls(
            match_id=data["match_id"],
            mu=data["mu"],
            elo=data["elo"],
            sigma=data["sigma"],
            match_date=match_date,
        )
