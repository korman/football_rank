class TeamNameMapper:
    def __init__(self):
        # 中英文队名映射字典，基于您提供的列表
        self.mapping = {
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
        }

    def get_chinese_name(self, english_name):
        # 返回中文名，如果不存在返回英文原名
        return self.mapping.get(english_name, english_name)


# 使用示例
if __name__ == "__main__":
    mapper = TeamNameMapper()
    print(mapper.get_chinese_name("Liverpool"))  # 输出: 利物浦
    print(mapper.get_chinese_name("Man City"))  # 输出: 曼城
    print(mapper.get_chinese_name("Unknown"))  # 输出: Unknown (不存在时返回原名)
