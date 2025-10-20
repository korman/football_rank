import sys
import os
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFrame,
    QWidget,
)
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt
from PyQt6.QtCharts import (
    QChart,
    QChartView,
    QLineSeries,
    QValueAxis,
    QDateTimeAxis,
    QLegend,
)
from datetime import datetime, timedelta
from typing import List, Optional
from .team import Team
from .match_info import MatchInfo


class TeamInfoDialog(QDialog):
    """
    队伍信息对话框，用于展示队伍的详细信息、积分历史和比赛记录
    """

    def __init__(self, team: Team, parent: Optional[QWidget] = None):
        """
        初始化队伍信息对话框

        参数:
            team: Team类实例，包含队伍的所有信息
            parent: 父窗口组件
        """
        super().__init__(parent)
        self.team = team
        self._init_ui()

    def _init_ui(self):
        """
        初始化对话框UI组件
        """
        self.setWindowTitle(f"{self.team.name} - 队伍信息")
        self.setMinimumSize(800, 600)

        # 创建主布局
        main_layout = QVBoxLayout(self)

        # 1. 创建队伍基本信息区域
        self._create_team_info_section(main_layout)

        # 2. 创建积分历史折线图区域
        self._create_ranking_history_chart(main_layout)

        # 3. 创建历史比赛表格区域
        self._create_match_history_table(main_layout)

    def _create_team_info_section(self, parent_layout: QVBoxLayout):
        """
        创建队伍基本信息区域，包含队标和基本数据
        """
        # 创建水平布局
        info_layout = QHBoxLayout()

        # 队标区域
        logo_frame = QFrame()
        logo_frame.setFixedSize(100, 100)
        logo_frame.setFrameShape(QFrame.Shape.StyledPanel)
        logo_frame.setFrameShadow(QFrame.Shadow.Raised)

        # 加载默认队标图片
        logo_label = QLabel(logo_frame)
        logo_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "assets",
            "team_logo",
            "default.png",
        )

        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(
                80,
                80,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo_label.setPixmap(pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_layout = QVBoxLayout(logo_frame)
        logo_layout.addWidget(logo_label)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 队伍信息区域
        info_container = QWidget()
        info_v_layout = QVBoxLayout(info_container)

        # 队伍名称
        team_name_label = QLabel(self.team.name)
        team_name_font = QFont("SimHei", 24, QFont.Weight.Bold)
        team_name_label.setFont(team_name_font)
        team_name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # 队伍积分信息
        ranking_info_text = (
            f"Elo积分: {self.team.elo:.0f}  "
            f"Truskill积分: {self.team.mu:.0f}  "
            f"稳定度: {self._calculate_stability():.1f}%"
        )
        ranking_info_label = QLabel(ranking_info_text)
        ranking_info_label.setFont(QFont("SimHei", 12))

        # 添加到垂直布局
        info_v_layout.addWidget(team_name_label)
        info_v_layout.addWidget(ranking_info_label)
        info_v_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 将队标和信息区域添加到水平布局
        info_layout.addWidget(logo_frame)
        info_layout.addWidget(info_container)
        info_layout.addStretch()

        # 添加到主布局
        parent_layout.addLayout(info_layout)
        parent_layout.addSpacing(20)

    def _calculate_stability(self) -> float:
        """
        计算队伍评分的稳定度
        稳定度 = (1 - sigma/mu) * 100%，但确保结果在0-100之间
        """
        if self.team.mu <= 0:
            return 0.0
        stability = (1 - self.team.sigma / self.team.mu) * 100
        return max(0.0, min(100.0, stability))

    def _create_ranking_history_chart(self, parent_layout: QVBoxLayout):
        """
        创建积分历史折线图区域
        """
        # 添加标题
        chart_title_label = QLabel("积分历史:")
        chart_title_label.setFont(QFont("SimHei", 14, QFont.Weight.Bold))
        parent_layout.addWidget(chart_title_label)

        # 创建图表容器
        chart_frame = QFrame()
        chart_frame.setFrameShape(QFrame.Shape.StyledPanel)
        chart_frame.setFrameShadow(QFrame.Shadow.Raised)
        chart_frame.setMinimumHeight(300)

        # 创建图表
        chart = QChart()
        chart.setTitle(f"{self.team.name} 积分变化趋势")
        chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)

        # 创建坐标轴
        axis_x = QDateTimeAxis()
        axis_x.setTickCount(6)
        axis_x.setFormat("yyyy-MM-dd")
        axis_x.setTitleText("日期")

        axis_y = QValueAxis()
        axis_y.setLabelFormat("%.0f")
        axis_y.setTitleText("积分值")

        # 创建并添加模拟数据系列
        elo_series = self._create_elo_series()
        trueskill_series = self._create_trueskill_series()

        chart.addSeries(elo_series)
        chart.addSeries(trueskill_series)
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)

        elo_series.attachAxis(axis_x)
        elo_series.attachAxis(axis_y)
        trueskill_series.attachAxis(axis_x)
        trueskill_series.attachAxis(axis_y)

        # 创建图表视图
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QChartView.RenderHint.Antialiasing)

        # 将图表视图添加到容器
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.addWidget(chart_view)

        # 添加到主布局
        parent_layout.addWidget(chart_frame)
        parent_layout.addSpacing(20)

    def _create_elo_series(self) -> QLineSeries:
        """
        创建Elo积分历史系列
        """
        series = QLineSeries()
        series.setName("Elo积分")

        # 生成模拟数据
        today = datetime.now()
        base_elo = self.team.elo

        # 生成过去30天的模拟数据
        for i in range(30):
            date = today - timedelta(days=30 - i)
            # 添加一些随机波动
            variation = (i % 5 - 2) * 10  # 简单波动模式
            elo_value = base_elo + variation
            series.append(date.timestamp() * 1000, elo_value)

        # 添加当前值
        series.append(today.timestamp() * 1000, self.team.elo)

        return series

    def _create_trueskill_series(self) -> QLineSeries:
        """
        创建TrueSkill积分历史系列
        """
        series = QLineSeries()
        series.setName("TrueSkill积分")

        # 生成模拟数据
        today = datetime.now()
        base_mu = self.team.mu

        # 生成过去30天的模拟数据
        for i in range(30):
            date = today - timedelta(days=30 - i)
            # 添加一些随机波动
            variation = (i % 7 - 3) * 5  # 不同的波动模式
            mu_value = base_mu + variation
            series.append(date.timestamp() * 1000, mu_value)

        # 添加当前值
        series.append(today.timestamp() * 1000, self.team.mu)

        return series

    def _create_match_history_table(self, parent_layout: QVBoxLayout):
        """
        创建历史比赛表格区域
        """
        # 添加标题
        table_title_label = QLabel("历史比赛:")
        table_title_label.setFont(QFont("SimHei", 14, QFont.Weight.Bold))
        parent_layout.addWidget(table_title_label)

        # 创建表格容器
        table_frame = QFrame()
        table_frame.setFrameShape(QFrame.Shape.StyledPanel)
        table_frame.setFrameShadow(QFrame.Shadow.Raised)
        table_frame.setMinimumHeight(200)

        # 创建表格
        self.match_table = QTableWidget()
        self.match_table.setColumnCount(5)
        self.match_table.setHorizontalHeaderLabels(
            ["比赛日期", "对手", "比分", "比赛ID", "比赛类型"]
        )

        # 设置表格列宽自适应
        header = self.match_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # 当前表格为空，后续可以通过队伍的match_info填充

        # 将表格添加到容器
        table_layout = QVBoxLayout(table_frame)
        table_layout.addWidget(self.match_table)

        # 添加到主布局
        parent_layout.addWidget(table_frame)

    def update_match_history(self):
        """
        更新历史比赛表格数据
        从team.match_info中获取数据并填充表格
        """
        # 清空现有数据
        self.match_table.setRowCount(0)

        # 获取队伍的比赛历史记录
        match_infos = self.team.get_match_info()

        # 按照日期排序
        sorted_matches = sorted(match_infos, key=lambda x: x.match_date, reverse=True)

        # 填充表格
        for match_info in sorted_matches:
            row_position = self.match_table.rowCount()
            self.match_table.insertRow(row_position)

            # 填充数据（注意：这里只有比赛ID和日期信息，对手和比分需要额外获取）
            self.match_table.setItem(
                row_position,
                0,
                QTableWidgetItem(match_info.match_date.strftime("%Y-%m-%d")),
            )
            self.match_table.setItem(
                row_position,
                1,
                QTableWidgetItem("未知对手"),  # 需要额外数据支持
            )
            self.match_table.setItem(
                row_position,
                2,
                QTableWidgetItem("未知比分"),  # 需要额外数据支持
            )
            self.match_table.setItem(
                row_position, 3, QTableWidgetItem(str(match_info.match_id))
            )
            self.match_table.setItem(
                row_position,
                4,
                QTableWidgetItem("联赛"),  # 默认类型
            )


if __name__ == "__main__":
    # 简单测试代码
    app = QApplication(sys.argv)

    # 创建一个测试用的Team实例
    test_team = Team("皇家马德里")
    test_team.elo = 1855
    test_team.mu = 1566
    test_team.sigma = 10

    # 创建并显示对话框
    dialog = TeamInfoDialog(test_team)
    dialog.exec()

    sys.exit(app.exec())
