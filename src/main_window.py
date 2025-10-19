import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PyQt6.QtCore import Qt
from .match_ranking import MatchRankingSystem
from .team_name_mapper import TeamNameMapper


class RankingSystemMainWindow(QMainWindow):
    """浩子比赛排名系统主窗口"""

    def __init__(self):
        super().__init__()
        # 初始化排名系统
        self.ranking_system = MatchRankingSystem()
        # 初始化队伍名映射器
        self.team_mapper = TeamNameMapper()
        # 加载并处理数据
        self._load_and_process_data()
        # 初始化界面
        self.init_ui()

    def _load_and_process_data(self):
        """加载并处理比赛数据"""
        try:
            # 处理所有比赛并计算排名
            self.ranking_system.process_all_matches()
        except Exception as e:
            print(f"加载数据时出错: {e}")

    def init_ui(self):
        # 设置窗口标题和大小
        self.setWindowTitle("浩子比赛排名系统")
        self.setGeometry(100, 100, 800, 600)

        # 创建中心部件和主布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 创建标题标签
        title_label = QLabel("浩子比赛排名系统")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = title_label.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)

        # 创建算法选择区域
        algorithm_layout = QHBoxLayout()
        algorithm_label = QLabel("排名比赛算法:")
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["Open Skill", "Elo"])
        self.algorithm_combo.currentIndexChanged.connect(self.on_algorithm_changed)

        algorithm_layout.addWidget(algorithm_label)
        algorithm_layout.addWidget(self.algorithm_combo)
        algorithm_layout.addStretch()  # 添加拉伸空间使其靠左
        main_layout.addLayout(algorithm_layout)

        # 创建排名表格
        table_container = QWidget()
        table_container.setStyleSheet("border: 1px solid black;")
        table_layout = QVBoxLayout(table_container)

        # 创建表格标题
        table_title = QLabel("队伍排名表")
        table_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        table_title_font = table_title.font()
        table_title_font.setPointSize(14)
        table_title_font.setBold(True)
        table_title.setFont(table_title_font)
        table_layout.addWidget(table_title)

        # 创建表格
        self.ranking_table = QTableWidget()
        self.ranking_table.setColumnCount(4)
        self.ranking_table.setHorizontalHeaderLabels(
            ["队伍名", "积分", "稳定度", "比赛场次"]
        )

        # 设置表格样式和布局
        header = self.ranking_table.horizontalHeader()
        header.setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )  # 队伍名列自动拉伸
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

        # 初始加载OpenSkill排名数据
        self.update_ranking_table("Open Skill")

        # 禁用编辑
        self.ranking_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # 添加表格到布局
        table_layout.addWidget(self.ranking_table)

        # 添加表格容器到主布局
        main_layout.addWidget(table_container, 1)  # 设置伸展因子为1，使其占据大部分空间

    def on_algorithm_changed(self, index):
        """算法选择改变事件处理函数"""
        selected_algorithm = self.algorithm_combo.currentText()
        self.update_ranking_table(selected_algorithm)

    def update_ranking_table(self, algorithm_type):
        """更新排名表格数据"""
        # 清空表格
        self.ranking_table.setRowCount(0)

        if algorithm_type == "Open Skill":
            rankings = self.load_openskill_rankings()
        elif algorithm_type == "Elo":
            rankings = self.load_elo_rankings()
        else:
            return

        # 填充表格数据
        for i, (team_name, score, stability, matches) in enumerate(rankings):
            self.ranking_table.insertRow(i)

            # 添加队伍名（使用中文名称）
            chinese_name = self.team_mapper.get_chinese_name(team_name)
            self.ranking_table.setItem(i, 0, QTableWidgetItem(chinese_name))

            # 添加积分（对于OpenSkill已取整，Elo保留两位小数）
            if isinstance(score, int):
                self.ranking_table.setItem(i, 1, QTableWidgetItem(str(score)))
            else:
                self.ranking_table.setItem(i, 1, QTableWidgetItem(f"{score:.2f}"))

            # 添加稳定度：如果是字符串直接显示（已包含%符号），否则保留两位小数
            if isinstance(stability, str):
                self.ranking_table.setItem(i, 2, QTableWidgetItem(stability))
            else:
                self.ranking_table.setItem(i, 2, QTableWidgetItem(f"{stability:.2f}"))

            # 添加比赛场次
            self.ranking_table.setItem(i, 3, QTableWidgetItem(str(matches)))

    def load_elo_rankings(self):
        """加载Elo排名数据"""
        try:
            elo_rankings = self.ranking_system.get_elo_rankings()
            # 对于Elo算法，假设稳定性是固定值，比赛场次暂时设为100
            processed_rankings = [
                (team, rating, 1.0, 100) for team, rating in elo_rankings
            ]
            return processed_rankings
        except Exception as e:
            print(f"加载Elo排名出错: {e}")
            return []

    def load_openskill_rankings(self):
        """加载OpenSkill排名数据"""
        try:
            openskill_rankings = self.ranking_system.get_openskill_rankings()
            min_sigma = 1.5  # 最小sigma值用于稳定性计算
            # OpenSkill算法中，将mu值乘以25后取整作为积分，使用新公式计算稳定性
            processed_rankings = []
            for team, rating in openskill_rankings:
                mu_value = rating[0].mu
                sigma_value = rating[0].sigma

                # 计算积分：mu值乘以25后取整
                score = int(mu_value * 25)

                # 计算稳定性：Stability = (1 / sigma) / (1 / min_sigma) × 100
                stability_value = (1 / sigma_value) / (1 / min_sigma) * 100
                # 四舍五入处理并添加%符号
                stability = f"{round(stability_value)}%"

                processed_rankings.append((team, score, stability, 100))

            return processed_rankings
        except Exception as e:
            print(f"加载OpenSkill排名出错: {e}")
            return []


# 主窗口类已定义，主函数已移至项目根目录的main.py文件中
