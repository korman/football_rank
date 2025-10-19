class TeamNameMapper:
    def __init__(self):
        # 中英文队名映射字典，基于您提供的英超和西甲列表
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
            # 新增德甲球队（基于您提供的15年数据列表）
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
        }

    def get_chinese_name(self, english_name):
        # 返回中文名，如果不存在返回英文原名
        return self.mapping.get(english_name, english_name)


# 使用示例
if __name__ == "__main__":
    mapper = TeamNameMapper()
    print(mapper.get_chinese_name("Liverpool"))  # 输出: 利物浦
    print(mapper.get_chinese_name("Man City"))  # 输出: 曼城
    print(mapper.get_chinese_name("Barcelona"))  # 输出: 巴塞罗那
    print(mapper.get_chinese_name("Real Madrid"))  # 输出: 皇家马德里
    print(mapper.get_chinese_name("Unknown"))  # 输出: Unknown (不存在时返回原名)
    # 新增德甲示例
    print(mapper.get_chinese_name("Bayern Munich"))  # 输出: 拜仁慕尼黑
    print(mapper.get_chinese_name("Dortmund"))  # 输出: 多特蒙德
    print(mapper.get_chinese_name("Schalke 04"))  # 输出: 沙尔克04
