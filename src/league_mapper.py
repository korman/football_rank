"""
联赛名称映射模块
提供中文联赛名称到英文代码的映射功能
全局可用，无需实例化
"""

# 联赛名称映射字典
LEAGUE_MAP = {"英超": "E0", "西甲": "SP1", "德甲": "D1"}


def get_league_code(chinese_name):
    """
    根据中文联赛名称获取对应的英文代码

    Args:
        chinese_name (str): 中文联赛名称，如"英超"、"西甲"

    Returns:
        str: 对应的英文联赛代码，如"E0"、"SP1"；如果未找到映射，返回None
    """
    return LEAGUE_MAP.get(chinese_name)


def add_league_mapping(chinese_name, league_code):
    """
    添加新的联赛映射关系

    Args:
        chinese_name (str): 中文联赛名称
        league_code (str): 对应的英文联赛代码
    """
    LEAGUE_MAP[chinese_name] = league_code


def get_all_leagues():
    """
    获取所有已映射的联赛名称和代码

    Returns:
        dict: 包含所有联赛映射关系的字典
    """
    return LEAGUE_MAP.copy()


def is_valid_league(chinese_name):
    """
    检查给定的中文联赛名称是否有对应的映射

    Args:
        chinese_name (str): 中文联赛名称

    Returns:
        bool: 如果存在映射返回True，否则返回False
    """
    return chinese_name in LEAGUE_MAP
