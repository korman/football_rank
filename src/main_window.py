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
    QPushButton,
    QFileDialog,
    QMessageBox,
)
from .sqlite_importer import sqlite_importer
from PyQt6.QtCore import Qt
from .match_ranking import MatchRankingSystem
from .team_name_mapper import TeamNameMapper
from .league_mapper import get_all_leagues, get_league_code
from .match_data import MatchDataManager
from .team_manager import TeamManager


class RankingSystemMainWindow(QMainWindow):
    """浩子比赛排名系统主窗口"""

    def __init__(self):
        super().__init__()
        # 初始化排名系统
        self.ranking_system = MatchRankingSystem()
        # 初始化队伍名映射器
        self.team_mapper = TeamNameMapper()
        # 初始化数据库连接 (SQLite版本)
        self.match_data_manager = MatchDataManager()
        # 初始化队伍管理器
        self.team_manager = TeamManager()
        # 当前选中的联赛
        self.current_league = None
        # 初始化界面
        self.init_ui()
        # 初始不加载数据，等待用户选择联赛

    def _load_and_process_data(self, league_name=None):
        """加载并处理指定联赛的比赛数据"""
        try:
            # 重置排名系统的算法实例
            self.ranking_system.elo_algorithm = (
                self.ranking_system.elo_algorithm.__class__()
            )
            self.ranking_system.openskill_algorithm = (
                self.ranking_system.openskill_algorithm.__class__()
            )

            if league_name:
                # 根据联赛名称获取联赛代码
                league_code = get_league_code(league_name)
                print(f"正在加载联赛: {league_name} ({league_code})")

                # 从match_data_manager获取指定联赛的数据，使用正确的过滤条件格式
                matches = self.match_data_manager.get_matches({"Div": league_code})
                print(f"成功获取 {len(matches)} 场比赛数据")

                # 处理比赛数据
                for match in matches:
                    if (
                        "HomeTeam" in match
                        and "AwayTeam" in match
                        and "FTHG" in match
                        and "FTAG" in match
                    ):
                        home = match["HomeTeam"]
                        away = match["AwayTeam"]
                        home_score = int(match["FTHG"])
                        away_score = int(match["FTAG"])

                        # 使用已经确定的联赛代码
                        league_code = get_league_code(league_name)

                        # 首先通过TeamManager创建或获取队伍，并设置联赛信息
                        self.team_manager.create_team(home, league=league_code)
                        self.team_manager.create_team(away, league=league_code)

                        # 更新队伍的比赛次数
                        self.team_manager.increment_match_count(home)
                        self.team_manager.increment_match_count(away)

                        # 使用两种算法处理同一场比赛
                        self.ranking_system.elo_algorithm.process_match(
                            home, away, home_score, away_score
                        )
                        self.ranking_system.openskill_algorithm.process_match(
                            home, away, home_score, away_score
                        )
            else:
                # 处理所有比赛
                self.ranking_system.process_all_matches()

            # 更新表格
            selected_algorithm = self.algorithm_combo.currentText()
            self.update_ranking_table(selected_algorithm)

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

        # 算法选择部分
        algorithm_label = QLabel("排名比赛算法:")
        self.algorithm_combo = QComboBox()
        self.algorithm_combo.addItems(["Open Skill", "Elo"])
        self.algorithm_combo.currentIndexChanged.connect(self.on_algorithm_changed)

        # 联赛选择部分
        league_label = QLabel("选择联赛:")
        self.league_combo = QComboBox()

        # 首先添加"选择联赛"作为默认选项
        self.league_combo.addItem("选择联赛")

        # 获取所有联赛并添加到下拉框
        leagues = get_all_leagues()
        league_names = list(leagues.keys())
        self.league_combo.addItems(league_names)

        # 添加选项改变事件的监听器
        self.league_combo.currentIndexChanged.connect(self.on_league_changed)

        # 添加导入数据按钮
        import_button = QPushButton("导入数据")
        import_button.clicked.connect(self.on_import_data)

        algorithm_layout.addWidget(algorithm_label)
        algorithm_layout.addWidget(self.algorithm_combo)
        algorithm_layout.addSpacing(20)  # 添加间距
        algorithm_layout.addWidget(league_label)
        algorithm_layout.addWidget(self.league_combo)
        algorithm_layout.addSpacing(20)  # 添加间距
        algorithm_layout.addWidget(import_button)
        algorithm_layout.addStretch()  # 添加拉伸空间
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

    def on_league_changed(self, index):
        """联赛选择改变事件处理函数"""
        selected_league = self.league_combo.currentText()

        # 如果选择的是默认选项"选择联赛"，则不加载数据
        if selected_league == "选择联赛":
            self.current_league = None
            # 清空表格
            self.ranking_table.setRowCount(0)
        else:
            # 记录当前选中的联赛
            self.current_league = selected_league
            # 加载并处理选中联赛的数据
            self._load_and_process_data(selected_league)

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
        """加载Elo排名数据，使用TeamManager获取指定联赛的队伍"""
        try:
            if not self.current_league:
                return []

            # 使用TeamManager获取当前联赛的所有队伍
            league_teams = self.team_manager.get_teams_by_league(self.current_league)

            # 获取所有队伍的Elo排名并构建字典
            all_elo_rankings = dict(self.ranking_system.get_elo_rankings())

            # 构建排名数据
            processed_rankings = []
            for team in league_teams:
                # 从排名字典中获取队伍的Elo评分，如果不存在则使用队伍默认值
                elo_rating = all_elo_rankings.get(team.name, team.elo)
                processed_rankings.append(
                    (team.name, elo_rating, 1.0, team.match_count)
                )

            # 按Elo评分降序排序
            processed_rankings.sort(key=lambda x: x[1], reverse=True)
            return processed_rankings
        except Exception as e:
            print(f"加载Elo排名出错: {e}")
            return []

    def load_openskill_rankings(self):
        """加载OpenSkill排名数据，使用TeamManager获取指定联赛的队伍"""
        try:
            if not self.current_league:
                return []

            # 使用TeamManager获取当前联赛的所有队伍
            league_teams = self.team_manager.get_teams_by_league(self.current_league)
            min_sigma = 1.5  # 最小sigma值用于稳定性计算

            # 获取所有队伍的OpenSkill排名并构建字典
            all_openskill_rankings = dict(self.ranking_system.get_openskill_rankings())

            # 构建排名数据
            processed_rankings = []
            for team in league_teams:
                # 从排名字典中获取队伍的OpenSkill评分，如果不存在则为None
                openskill_rating = all_openskill_rankings.get(team.name)

                if openskill_rating:
                    # 如果ranking_system中有评分，使用该评分
                    mu_value = openskill_rating[0].mu
                    sigma_value = openskill_rating[0].sigma
                else:
                    # 否则使用队伍对象中的默认值
                    mu_value = team.mu
                    sigma_value = team.sigma

                # 计算积分：mu值乘以25后取整
                score = int(mu_value * 25)

                # 计算稳定性：Stability = (1 / sigma) / (1 / min_sigma) × 100
                stability_value = (1 / sigma_value) / (1 / min_sigma) * 100
                # 四舍五入处理并添加%符号
                stability = f"{round(stability_value)}%"

                processed_rankings.append(
                    (team.name, score, stability, team.match_count)
                )

            # 按积分降序排序
            processed_rankings.sort(key=lambda x: x[1], reverse=True)
            return processed_rankings
        except Exception as e:
            print(f"加载OpenSkill排名出错: {e}")
            return []

    def on_import_data(self):
        """
        导入数据按钮点击事件处理函数
        打开文件选择对话框，支持多选CSV文件，并调用sqlite_importer处理选中的文件
        """
        # 打开文件选择对话框，设置多选和文件筛选
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, "选择CSV文件", "", "CSV文件 (*.csv);;所有文件 (*)"
        )

        # 如果用户选择了文件
        if file_paths:
            # 显示导入开始的消息
            QMessageBox.information(
                self, "导入开始", f"开始导入 {len(file_paths)} 个CSV文件..."
            )

            # 遍历所有选中的文件路径
            total_imported = 0
            total_skipped = 0

            for file_path in file_paths:
                try:
                    # 调用sqlite_importer进行数据处理
                    result = sqlite_importer.import_csv(file_path)

                    if result["success"]:
                        total_imported += result["imported_rows"]
                        total_skipped += result["skipped_rows"]
                        print(
                            f"文件 {file_path} 导入成功: {result['imported_rows']} 行导入, {result['skipped_rows']} 行跳过"
                        )
                    else:
                        error_msg = result.get("error", "未知错误")
                        print(f"文件 {file_path} 导入失败: {error_msg}")
                        QMessageBox.warning(
                            self, "导入失败", f"文件 {file_path} 导入失败: {error_msg}"
                        )
                except Exception as e:
                    print(f"处理文件 {file_path} 时出错: {str(e)}")
                    QMessageBox.warning(
                        self, "处理错误", f"处理文件 {file_path} 时出错: {str(e)}"
                    )

            # 显示导入完成的消息
            QMessageBox.information(
                self,
                "导入完成",
                f"所有文件导入完成!\n总计导入: {total_imported} 行\n跳过重复: {total_skipped} 行",
            )


# 主窗口类已定义，主函数已移至项目根目录的main.py文件中
