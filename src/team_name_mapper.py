# 联赛映射模块
LEAGUE_MAP = {
    "英超": "E0",  # Premier League
    "西甲": "SP1",  # La Liga
    "德甲": "D1",  # Bundesliga
    "意甲": "I1",  # Serie A
    "法甲": "F1",  # Ligue 1
    # 可以根据需要添加更多联赛，如 "荷甲": "N1"
}


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


class TeamNameMapper:
    def __init__(self):
        # 中英文队名映射字典，基于您提供的英超、西甲、德甲、意甲、法甲列表
        self.mapping = {
            # 原有英超球队
            "Liverpool": "利物浦",
            "Man City": "曼城",
            "Arsenal": "阿森纳",
            "Chelsea": "切尔西",
            "Brighton": "布莱顿",
            "Aston Villa": "阿斯顿维拉",
            "Newcastle": "纽卡斯尔",
            "Crystal Palace": "水晶宫",
            "Nott'm Forest": "诺丁汉森林",
            "Brentford": "布伦特福德",
            "Everton": "埃弗顿",
            "Bournemouth": "伯恩茅斯",
            "Man United": "曼联",
            "Tottenham": "热刺",
            "Fulham": "富勒姆",
            "West Ham": "西汉姆",
            "Wolves": "狼队",
            "Leeds": "利兹联",
            "Leicester": "莱斯特城",
            "Burnley": "伯恩利",
            "Southampton": "南安普顿",
            "Ipswich": "伊普斯维奇",
            "Luton": "卢顿",
            "Sheffield United": "谢菲尔德联",
            "Watford": "沃特福德",
            "West Brom": "西布朗",
            "Stoke": "斯托克城",
            "Swansea": "斯旺西",
            "Norwich": "诺维奇",
            "Sunderland": "桑德兰",
            "Middlesbrough": "米德尔斯堡",
            "Huddersfield": "哈德斯菲尔德",
            "Hull": "赫尔城",
            "Cardiff": "卡迪夫城",
            "QPR": "女王公园巡游者",
            "Wigan": "维冈竞技",
            "Reading": "雷丁",
            "Bolton": "博尔顿",
            "Blackburn": "布莱克本",
            "Birmingham": "伯明翰",
            "Blackpool": "布莱克浦",
            # 原有西甲球队
            "Barcelona": "巴塞罗那",
            "Valencia": "瓦伦西亚",
            "Sociedad": "皇家社会",
            "Ath Bilbao": "毕尔巴鄂竞技",
            "Sevilla": "塞维利亚",
            "Ath Madrid": "马德里竞技",
            "Real Madrid": "皇家马德里",
            "Villarreal": "比利亚雷阿尔",
            "Getafe": "赫塔费",
            "Celta": "塞尔塔",
            "Espanol": "西班牙人",
            "Betis": "皇家贝蒂斯",
            "Levante": "莱万特",
            "Osasuna": "奥萨苏纳",
            "Vallecano": "巴列卡诺",
            "Granada": "格拉纳达",
            "Mallorca": "马洛卡",
            "Alaves": "阿拉维斯",
            "Malaga": "马拉加",
            "Valladolid": "巴拉多利德",
            "Eibar": "埃瓦尔",
            "La Coruna": "拉科鲁尼亚",
            "Girona": "赫罗纳",
            "Elche": "埃尔切",
            "Las Palmas": "拉斯帕尔马斯",
            "Leganes": "莱加内斯",
            "Almeria": "阿尔梅里亚",
            "Cadiz": "加的斯",
            "Sp Gijon": "希洪竞技",
            "Zaragoza": "萨拉戈萨",
            "Huesca": "韦斯卡",
            "Santander": "桑坦德竞技",
            "Cordoba": "科尔多巴",
            "Hercules": "赫库莱斯",
            "Oviedo": "奥维耶多",
            # 德甲球队（基于您提供的15年数据列表）
            "Werder Bremen": "云达不莱梅",
            "Hannover": "汉诺威96",
            "Augsburg": "奥格斯堡",
            "M'gladbach": "门兴格拉德巴赫",
            "Hoffenheim": "霍芬海姆",
            "Hamburg": "汉堡",
            "Leverkusen": "勒沃库森",
            "Stuttgart": "斯图加特",
            "Mainz": "美因茨",
            "Freiburg": "弗赖堡",
            "Schalke 04": "沙尔克04",
            "Wolfsburg": "沃尔夫斯堡",
            "Hertha": "赫塔柏林",
            "RB Leipzig": "红牛莱比锡",
            "Dortmund": "多特蒙德",
            "Union Berlin": "柏林联合",
            "Fortuna Dusseldorf": "杜塞尔多夫",
            "Ein Frankfurt": "法兰克福",
            "Bayern Munich": "拜仁慕尼黑",
            "Braunschweig": "不伦瑞克",
            "Nurnberg": "纽伦堡",
            "Paderborn": "帕德博恩",
            "Ingolstadt": "因戈尔施塔特",
            "FC Koln": "科隆",
            "St Pauli": "圣保利",
            "Darmstadt": "达姆施塔特",
            "Heidenheim": "海登海姆",
            "Greuther Furth": "格罗特赫恩富特",
            "Bochum": "波鸿",
            "Bielefeld": "比勒费尔德",
            "Kaiserslautern": "凯泽斯劳滕",
            # 意甲球队（基于您提供的15年数据列表）
            "Milan": "AC米兰",
            "Lazio": "拉齐奥",
            "Cagliari": "卡利亚里",
            "Roma": "罗马",
            "Inter": "国际米兰",
            "Palermo": "巴勒莫",
            "Napoli": "那不勒斯",
            "Cesena": "切塞纳",
            "Udinese": "乌迪内斯",
            "Lecce": "莱切",
            "Bologna": "博洛尼亚",
            "Fiorentina": "佛罗伦萨",
            "Torino": "都灵",
            "Atalanta": "亚特兰大",
            "Chievo": "基耶沃",
            "Parma": "帕尔马",
            "Verona": "维罗纳",
            "Sassuolo": "萨索洛",
            "Sampdoria": "桑普多利亚",
            "Juventus": "尤文图斯",
            "Pescara": "佩斯卡拉",
            "Brescia": "布雷西亚",
            "Empoli": "恩波利",
            "Genoa": "热那亚",
            "Novara": "诺瓦拉",
            "Siena": "锡耶纳",
            "Cremonese": "克雷莫内斯",
            "Salernitana": "萨勒尼塔纳",
            "Bari": "巴里",
            "Catania": "卡塔尼亚",
            "Carpi": "卡尔皮",
            "Frosinone": "弗罗西诺内",
            "Crotone": "克罗托内",
            "Benevento": "贝内文托",
            "Spezia": "斯佩齐亚",
            "Venezia": "威尼斯",
            "Spal": "斯帕尔",
            "Livorno": "利沃诺",
            "Monza": "蒙扎",
            # 新增法甲球队（基于您提供的15年数据列表）
            "Angers": "安热",
            "Lorient": "洛里昂",
            "Lens": "朗斯",
            "Paris SG": "巴黎圣日耳曼",
            "Lyon": "里昂",
            "Clermont": "克莱蒙",
            "Monaco": "摩纳哥",
            "Brest": "布雷斯特",
            "Nantes": "南特",
            "Auxerre": "欧塞尔",
            "Toulouse": "图卢兹",
            "Ajaccio": "阿雅克肖",
            "Bastia": "巴斯蒂亚",
            "Guingamp": "甘冈",
            "Evian Thonon Gaillard": "埃维昂温泉",
            "Reims": "兰斯",
            "Montpellier": "蒙彼利埃",
            "Sochaux": "索肖",
            "St Etienne": "圣埃蒂安",
            "Valenciennes": "瓦朗谢讷",
            "Bordeaux": "波尔多",
            "Caen": "卡昂",
            "Lille": "里尔",
            "Nice": "尼斯",
            "Amiens": "阿米恩",
            "Dijon": "第戎",
            "Nimes": "尼姆",
            "Strasbourg": "斯特拉斯堡",
            "Marseille": "马赛",
            "Rennes": "雷恩",
            "Troyes": "特鲁瓦",
            "Metz": "梅斯",
            "Nancy": "南锡",
            "Le Havre": "勒阿弗尔",
            "Arles": "阿莱斯",
            "Ajaccio GFCO": "阿雅克肖GFCO",
        }

    def get_chinese_name(self, english_name):
        # 返回中文名，如果不存在返回英文原名
        return self.mapping.get(english_name, english_name)


# 使用示例
if __name__ == "__main__":
    # 联赛映射示例
    print(get_league_code("英超"))  # 输出: E0
    print(get_league_code("法甲"))  # 输出: F1
    print(is_valid_league("法甲"))  # 输出: True
    print(
        get_all_leagues()
    )  # 输出: {'英超': 'E0', '西甲': 'SP1', '德甲': 'D1', '意甲': 'I1', '法甲': 'F1'}

    # 球队映射示例
    mapper = TeamNameMapper()
    print(mapper.get_chinese_name("Liverpool"))  # 输出: 利物浦
    print(mapper.get_chinese_name("Bayern Munich"))  # 输出: 拜仁慕尼黑
    print(mapper.get_chinese_name("Juventus"))  # 输出: 尤文图斯
    # 新增法甲示例
    print(mapper.get_chinese_name("Paris SG"))  # 输出: 巴黎圣日耳曼
    print(mapper.get_chinese_name("Marseille"))  # 输出: 马赛
    print(mapper.get_chinese_name("Lyon"))  # 输出: 里昂
