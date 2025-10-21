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
    QCheckBox,
)
from PyQt6.QtGui import QPixmap, QFont, QPainter
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
from .team_name_mapper import TeamNameMapper
from .match_data import MatchDataManager


class TeamInfoDialog(QDialog):
    """
    队伍信息对话框，用于展示队伍的详细信息、积分历史和比赛记录
    """

    def __init__(
        self,
        team: Team,
        match_data_manager: MatchDataManager = None,
        parent: Optional[QWidget] = None,
    ):
        """
        初始化队伍信息对话框

        参数:
            team: Team类实例，包含队伍的所有信息
            match_data_manager: MatchDataManager实例，用于获取比赛详细数据
            parent: 父窗口组件
        """
        super().__init__(parent)
        self.team = team
        self.match_data_manager = match_data_manager or MatchDataManager()
        self.elo_series = None  # 保存对elo系列的引用
        self.trueskill_series = None  # 保存对trueskill系列的引用
        self._init_ui()
        # 初始化后更新比赛历史表格
        self.update_match_history()

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

        # 队伍名称 - 使用中文显示
        team_name_mapper = TeamNameMapper()
        chinese_team_name = team_name_mapper.get_chinese_name(self.team.name)
        team_name_label = QLabel(chinese_team_name)
        team_name_font = QFont("SimHei", 28, QFont.Weight.Bold)  # 字号从24调整到28
        team_name_label.setFont(team_name_font)
        team_name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # 队伍积分信息
        ranking_info_text = (
            f"Elo积分: {self.team.elo:.0f}  "
            f"Truskill积分: {self.team.mu * 25:.0f}  "
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
        注意：这里直接使用mu和sigma的原始值计算，因为稳定度是相对比率
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
        self.chart = QChart()
        # 使用中文队名作为图表标题
        team_name_mapper = TeamNameMapper()
        chinese_team_name = team_name_mapper.get_chinese_name(self.team.name)
        self.chart.setTitle(f"{chinese_team_name} 积分变化趋势")
        self.chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)

        # 创建坐标轴
        self.axis_x = QDateTimeAxis()
        self.axis_x.setTickCount(6)
        self.axis_x.setFormat("yyyy-MM-dd")
        self.axis_x.setTitleText("日期")

        self.axis_y = QValueAxis()
        self.axis_y.setLabelFormat("%.0f")
        self.axis_y.setTitleText("积分值")
        # 移除固定范围设置，让图表根据数据动态调整Y轴范围

        # 创建并添加数据系列
        # 根据要求，只保留TrueSkill积分曲线
        self.elo_series = self._create_elo_series()  # 保留方法调用但不添加到图表
        self.trueskill_series = self._create_trueskill_series()

        # 只添加TrueSkill系列到图表
        self.chart.addSeries(self.trueskill_series)
        self.chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignBottom)
        self.chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)

        # 只关联TrueSkill系列到坐标轴
        self.trueskill_series.attachAxis(self.axis_x)
        self.trueskill_series.attachAxis(self.axis_y)

        # 动态调整Y轴范围，添加适当边距
        self._adjust_y_axis_range()

        # 创建图表视图
        chart_view = QChartView(self.chart)
        chart_view.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 创建选择框布局
        checkbox_layout = QHBoxLayout()

        # 根据要求，只保留TrueSkill选择框
        # 创建TrueSkill选择框
        self.trueskill_checkbox = QCheckBox("trueskill")
        self.trueskill_checkbox.setChecked(True)  # 初始状态为勾选
        self.trueskill_checkbox.stateChanged.connect(
            self._on_trueskill_checkbox_changed
        )
        checkbox_layout.addWidget(self.trueskill_checkbox)

        checkbox_layout.addStretch()

        # 将图表视图和选择框添加到容器
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.addWidget(chart_view)
        chart_layout.addLayout(checkbox_layout)

        # 添加到主布局
        parent_layout.addWidget(chart_frame)
        parent_layout.addSpacing(20)

    def _on_elo_checkbox_changed(self, state):
        """
        处理Elo选择框状态变化
        """
        if self.elo_series:
            is_checked = state == Qt.CheckState.Checked
            self.elo_series.setVisible(is_checked)

            # 确保在图表中正确显示
            if is_checked and self.elo_series not in self.chart.series():
                self.chart.addSeries(self.elo_series)
                self.elo_series.attachAxis(self.axis_x)
                self.elo_series.attachAxis(self.axis_y)

    def _on_trueskill_checkbox_changed(self, state):
        """
        处理TrueSkill选择框状态变化
        """
        if self.trueskill_series:
            is_checked = state == Qt.CheckState.Checked
            self.trueskill_series.setVisible(is_checked)

            # 确保在图表中正确显示
            if is_checked and self.trueskill_series not in self.chart.series():
                self.chart.addSeries(self.trueskill_series)
                self.trueskill_series.attachAxis(self.axis_x)
                self.trueskill_series.attachAxis(self.axis_y)

    def _create_elo_series(self) -> QLineSeries:
        """
        创建Elo积分历史系列，使用队伍的实际比赛数据
        注意：根据要求，现在只显示最近30场比赛的数据
        """
        series = QLineSeries()
        series.setName("Elo积分")

        # 获取队伍的历史比赛信息
        match_infos = self.team.get_match_info()

        if match_infos:
            # 按日期排序
            sorted_matches = sorted(match_infos, key=lambda x: x.match_date)
            # 只保留最近30场比赛
            recent_matches = (
                sorted_matches[-30:] if len(sorted_matches) > 30 else sorted_matches
            )

            # 添加实际比赛数据
            for match_info in recent_matches:
                # 确保match_date是有效的datetime对象
                if isinstance(match_info.match_date, datetime):
                    timestamp = match_info.match_date.timestamp() * 1000
                    series.append(timestamp, match_info.elo)
        else:
            # 如果没有比赛数据，添加当前值作为参考
            today = datetime.now()
            series.append(today.timestamp() * 1000, self.team.elo)

        return series

    def _create_trueskill_series(self) -> QLineSeries:
        """
        创建TrueSkill积分历史系列，使用队伍的实际比赛数据
        注意：将mu值乘以25以避免因数值过低导致的显示问题
        注意：根据要求，现在只显示最近30场比赛的数据
        """
        series = QLineSeries()
        series.setName("TrueSkill积分")

        # 获取队伍的历史比赛信息
        match_infos = self.team.get_match_info()

        if match_infos:
            # 按日期排序
            sorted_matches = sorted(match_infos, key=lambda x: x.match_date)
            # 只保留最近30场比赛
            recent_matches = (
                sorted_matches[-30:] if len(sorted_matches) > 30 else sorted_matches
            )

            # 添加实际比赛数据，并将mu值乘以25
            for match_info in recent_matches:
                # 确保match_date是有效的datetime对象
                if isinstance(match_info.match_date, datetime):
                    timestamp = match_info.match_date.timestamp() * 1000
                    # 将mu值乘以25
                    scaled_mu = match_info.mu * 25
                    series.append(timestamp, scaled_mu)
        else:
            # 如果没有比赛数据，添加当前值作为参考，并将mu值乘以25
            today = datetime.now()
            scaled_mu = self.team.mu * 25
            series.append(today.timestamp() * 1000, scaled_mu)

        return series

    def _adjust_y_axis_range(self):
        """
        根据TrueSkill数据动态调整Y轴范围
        添加5%的边距确保数据点完全可见
        """
        if self.trueskill_series.count() == 0:
            return

        # 获取系列中的所有点
        points = self.trueskill_series.points()

        # 提取所有Y值
        y_values = [point.y() for point in points]

        # 计算最小和最大值
        min_y = min(y_values)
        max_y = max(y_values)

        # 计算范围和边距
        value_range = max_y - min_y
        margin = value_range * 0.05  # 添加5%的边距

        # 设置新的Y轴范围
        self.axis_y.setMin(min_y - margin)
        self.axis_y.setMax(max_y + margin)

        # 如果范围非常小（例如只有一个数据点），设置一个合理的默认范围
        if value_range < 1:
            self.axis_y.setMin(min_y - 10)
            self.axis_y.setMax(max_y + 10)

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
            ["比赛日期", "比赛对手", "比分", "积分", "积分变化"]
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
        从team.match_info中获取基本信息，并通过match_data_manager获取详细比赛数据
        """
        # 清空现有数据
        self.match_table.setRowCount(0)

        # 获取队伍的比赛历史记录
        match_infos = self.team.get_match_info()

        # 按照日期排序（升序）以便计算积分变化
        sorted_matches_asc = sorted(match_infos, key=lambda x: x.match_date)

        # 创建一个映射，便于按ID查找上一场比赛的mu值
        match_id_to_index = {
            info.match_id: i for i, info in enumerate(sorted_matches_asc)
        }

        # 按照日期降序排列显示
        sorted_matches_desc = sorted(
            match_infos, key=lambda x: x.match_date, reverse=True
        )

        # 填充表格
        for match_info in sorted_matches_desc:
            row_position = self.match_table.rowCount()
            self.match_table.insertRow(row_position)

            # 尝试通过match_data_manager获取详细比赛数据
            match_data = None
            if self.match_data_manager:
                try:
                    match_data = self.match_data_manager.get_match_by_id(
                        str(match_info.match_id)
                    )
                except Exception as e:
                    print(f"获取比赛ID {match_info.match_id} 的详细数据时出错: {e}")

            # 填充比赛日期
            self.match_table.setItem(
                row_position,
                0,
                QTableWidgetItem(match_info.match_date.strftime("%Y-%m-%d")),
            )

            # 填充对手信息
            opponent = "未知对手"
            if match_data:
                # 判断当前队伍是主队还是客队
                if match_data.get("HomeTeam") == self.team.name:
                    opponent = match_data.get("AwayTeam", "未知对手")
                else:
                    opponent = match_data.get("HomeTeam", "未知对手")

                # 使用TeamNameMapper将对手名称转换为中文
                team_name_mapper = TeamNameMapper()
                opponent = team_name_mapper.get_chinese_name(opponent)
            self.match_table.setItem(row_position, 1, QTableWidgetItem(opponent))

            # 填充比分信息
            score = "未知比分"
            if match_data:
                home_score = match_data.get("FTHG", "-")
                away_score = match_data.get("FTAG", "-")
                # 判断当前队伍是主队还是客队，调整比分显示顺序
                if match_data.get("HomeTeam") == self.team.name:
                    score = f"{home_score} - {away_score}"
                else:
                    score = f"{away_score} - {home_score}"
            self.match_table.setItem(row_position, 2, QTableWidgetItem(score))

            # 填充积分信息（TrueSkill积分，mu*25）
            current_mu = match_info.mu
            scaled_mu = current_mu * 25
            self.match_table.setItem(
                row_position, 3, QTableWidgetItem(f"{scaled_mu:.1f}")
            )

            # 计算并填充积分变化
            mu_change = 0.0
            if match_info.match_id in match_id_to_index:
                current_index = match_id_to_index[match_info.match_id]
                if current_index > 0:  # 不是第一场比赛
                    prev_match_info = sorted_matches_asc[current_index - 1]
                    mu_change = current_mu - prev_match_info.mu

            scaled_change = mu_change * 25
            # 根据变化值设置不同的样式
            change_item = QTableWidgetItem(f"{scaled_change:+.1f}")
            if scaled_change > 0:
                change_item.setForeground(Qt.GlobalColor.green)
            elif scaled_change < 0:
                change_item.setForeground(Qt.GlobalColor.red)

            self.match_table.setItem(row_position, 4, change_item)
