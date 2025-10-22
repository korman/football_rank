import sys
import logging
from datetime import datetime, timedelta
from typing import Optional
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
    QFrame,
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from .team_info_dialog import TeamInfoDialog
from .sqlite_importer import sqlite_importer
from .match_ranking import MatchRankingSystem
from .team_name_mapper import TeamNameMapper
from .league_mapper import get_all_leagues, get_league_code
from .match_data import MatchDataManager
from .team_manager import TeamManager
from .match_info import MatchInfo
from .football_data_fetcher import FootballDataFetcher
from .match_parser import MatchParser


class BatchProcessingThread(QThread):
    """批处理线程，在独立线程中执行数据获取和处理"""

    progress_update = pyqtSignal(str, str)  # 进度更新信号
    batch_completed = pyqtSignal(int, int)  # 批次完成信号
    all_completed = pyqtSignal()  # 全部完成信号
    error_occurred = pyqtSignal(str)  # 错误信号

    def __init__(self, match_data_manager, match_parser):
        super().__init__()
        self.match_data_manager = match_data_manager
        self.match_parser = match_parser
        self.football_fetcher = None
        self.running = True

        # 初始化数据获取器
        self.init_fetcher()

    def init_fetcher(self):
        """初始化足球数据获取器"""
        try:
            api_key = "925538c2d157429ca8cd7f73a97cd974"
            self.football_fetcher = FootballDataFetcher(api_key)

            # 连接信号和槽
            self.football_fetcher.dataFetched.connect(self.on_data_fetched)
            self.football_fetcher.errorOccurred.connect(self.on_fetch_error)

            self.progress_update.emit("初始化", "数据获取器初始化完成")
        except Exception as e:
            self.error_occurred.emit(f"初始化数据获取器失败: {str(e)}")

    def run(self):
        """线程主函数，执行批处理任务"""
        try:
            # 设置日期范围
            a_date = datetime(2025, 7, 1)
            b_date = datetime.now()
            batch_size = 7

            # 初始化变量
            batch_start_date = a_date
            batch_count = 1
            league_codes = ["PL", "BL1", "SA", "PD", "FL1", "CL"]

            # 计算总批次数
            total_days = (b_date - a_date).days + 1
            total_batches = (total_days + batch_size - 1) // batch_size

            self.progress_update.emit(
                "配置",
                f"日期范围: {a_date.strftime('%Y-%m-%d')} 到 {b_date.strftime('%Y-%m-%d')} ({total_days}天)",
            )
            self.progress_update.emit(
                "配置", f"批次设置: 每次 {batch_size} 天，共 {total_batches} 个批次"
            )

            # 主批次处理循环
            while self.running and batch_start_date <= b_date:
                # 计算当前批次的结束日期
                batch_end_date = min(
                    batch_start_date + timedelta(days=batch_size - 1), b_date
                )
                batch_start_str = batch_start_date.strftime("%Y-%m-%d")
                batch_end_str = batch_end_date.strftime("%Y-%m-%d")

                self.progress_update.emit(
                    "处理",
                    f"[批次 {batch_count}/{total_batches}] 处理日期范围: {batch_start_str} 到 {batch_end_str}",
                )

                # 处理当前批次的所有联赛
                success = self.process_batch(
                    league_codes, batch_start_str, batch_end_str
                )

                if success:
                    self.batch_completed.emit(batch_count, total_batches)

                # 准备下一个批次
                batch_start_date += timedelta(days=batch_size)
                batch_count += 1

            self.all_completed.emit()
        except Exception as e:
            self.error_occurred.emit(f"批处理线程错误: {str(e)}")

    def process_batch(self, league_codes, batch_start_str, batch_end_str):
        """处理单个批次的所有联赛"""
        try:
            # 使用队列和事件来同步异步操作
            from PyQt6.QtCore import QEventLoop, QTimer

            for league_code in league_codes:
                if not self.running:
                    break

                self.progress_update.emit("获取", f"正在获取联赛 {league_code} 的数据")

                # 创建事件循环和定时器用于等待响应
                loop = QEventLoop()
                timer = QTimer()
                timer.setSingleShot(True)
                timer.timeout.connect(loop.quit)

                # 创建完成标志
                self.current_league = league_code
                self.league_complete = False

                # 发送请求
                self.football_fetcher.fetch_matches(
                    league_code, batch_start_str, batch_end_str
                )

                # 设置超时为45秒
                timer.start(45000)

                # 运行事件循环，等待完成或超时
                while not self.league_complete and timer.isActive() and self.running:
                    loop.processEvents(QEventLoop.ProcessEventsFlag.WaitForMoreEvents)

                # 清理定时器和循环
                timer.stop()
                loop.quit()

                if not self.league_complete:
                    self.progress_update.emit(
                        "超时", f"获取联赛 {league_code} 数据超时"
                    )

                # 添加短暂延迟，避免API请求过于频繁
                if self.running:
                    import time

                    time.sleep(1)  # 1秒延迟

            return True
        except Exception as e:
            self.error_occurred.emit(f"处理批次时出错: {str(e)}")
            return False

    def on_data_fetched(self, league_code, data):
        """处理获取到的数据"""
        try:
            # 只处理当前请求的联赛数据
            if hasattr(self, "current_league") and league_code == self.current_league:
                self.progress_update.emit("处理", f"成功获取联赛 {league_code} 数据")
                match_count = len(data.get("matches", []))
                self.progress_update.emit("处理", f"发现 {match_count} 场比赛")

                # 存储数据
                if match_count > 0:
                    import json

                    json_str = json.dumps(data)
                    inserted_count = self.match_parser.parse_and_store(json_str)
                    self.progress_update.emit(
                        "存储", f"成功存储 {inserted_count} 条记录"
                    )

                self.league_complete = True
        except Exception as e:
            self.error_occurred.emit(f"处理数据时出错: {str(e)}")
            if hasattr(self, "current_league") and league_code == self.current_league:
                self.league_complete = True  # 标记为已完成，避免无限等待

    def on_fetch_error(self, league_code, error_msg):
        """处理获取数据时的错误"""
        # 特别处理权限和速率限制错误
        if "403" in error_msg:
            self.progress_update.emit("重要错误", f"API权限不足: {error_msg}")
            self.progress_update.emit("建议", "请检查您的API密钥权限或考虑升级订阅等级")
        elif "429" in error_msg:
            self.progress_update.emit("速率限制", f"API请求过于频繁: {error_msg}")
            self.progress_update.emit("建议", "请减少请求频率或等待计数器重置")
        else:
            self.progress_update.emit(
                "错误", f"获取联赛 {league_code} 数据失败: {error_msg}"
            )

        # 标记为已完成，以便继续处理下一个联赛
        if hasattr(self, "current_league") and league_code == self.current_league:
            self.league_complete = True

    def stop(self):
        """停止批处理线程"""
        self.running = False
        self.wait()


class RankingSystemMainWindow(QMainWindow):
    """浩子比赛排名系统主窗口"""

    def __init__(self):
        super().__init__()
        # 初始化排名系统
        self.ranking_system = MatchRankingSystem()
        # 初始化队伍名映射器
        self.team_mapper = TeamNameMapper()
        # 初始化SQLite数据库连接
        self.match_data_manager = MatchDataManager()
        # 初始化队伍管理器
        self.team_manager = TeamManager()
        # 当前选中的联赛
        self.current_league = None

        # 初始化界面
        self.init_ui()
        # 添加API状态警告横幅
        self._add_api_status_warning()
        # 初始化足球数据获取器和解析器
        self.init_data_fetcher()

        # 初始不加载数据，等待用户选择联赛

        # 启动数据获取（延迟执行，确保界面已加载完成）
        QTimer.singleShot(1000, self.start_data_fetching)  # 只执行一次

    def _add_api_status_warning(self):
        """添加API状态警告横幅"""
        warning_layout = QVBoxLayout(self.api_warning_frame)

        # 创建警告标签
        warning_label = QLabel()
        warning_label.setStyleSheet("""
            background-color: #ffcccc;
            color: #cc0000;
            padding: 10px;
            border: 2px solid #cc0000;
            border-radius: 5px;
            font-weight: bold;
        """)

        warning_text = """
        <h3>⚠️ API权限警告 ⚠️</h3>
        <p>当前使用的API密钥没有足够权限访问历史比赛数据。</p>
        <p><b>需要操作：</b></p>
        <ul>
            <li>从football-data.org获取有效的付费订阅API密钥</li>
            <li>确保订阅计划包含访问历史比赛数据的权限</li>
            <li>应用程序将继续尝试获取数据，但可能会显示超时或错误</li>
        </ul>
        """

        warning_label.setText(warning_text)
        warning_label.setWordWrap(True)
        warning_layout.addWidget(warning_label)

        # 显示警告横幅
        self.api_warning_frame.setMinimumHeight(200)
        self.api_warning_frame.setMaximumHeight(500)
        self.api_warning_frame.show()

    def init_data_fetcher(self):
        """初始化足球数据获取器和解析器"""
        print("开始初始化数据获取器...")
        # 初始化MatchParser
        print("正在初始化MatchParser...")
        self.match_parser = MatchParser()
        try:
            self.match_parser.connect()
            print("成功连接到match_parser数据库")
        except Exception as e:
            print(f"连接到match_parser数据库失败: {str(e)}")

    def init_ui(self):
        """初始化用户界面"""
        # 设置窗口标题和大小
        self.setWindowTitle("浩子比赛排名系统")
        self.resize(800, 600)

        # 创建中央部件和主布局
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # 保留位置用于API状态警告横幅
        self.api_warning_frame = QFrame()
        self.api_warning_frame.setMinimumHeight(0)
        self.api_warning_frame.setMaximumHeight(0)  # 默认隐藏
        main_layout.addWidget(self.api_warning_frame)

        # 创建顶部控制区域
        control_layout = QHBoxLayout()

        # 添加联赛选择下拉框
        self.league_combo = QComboBox()
        self.league_combo.addItem("请选择联赛")
        for league in get_all_leagues():
            self.league_combo.addItem(league, get_league_code(league))

        control_layout.addWidget(QLabel("联赛:"))
        control_layout.addWidget(self.league_combo)
        control_layout.addStretch()

        # 创建排名表格
        self.ranking_table = QTableWidget()
        self.ranking_table.setColumnCount(6)
        self.ranking_table.setHorizontalHeaderLabels(
            ["排名", "队伍", "比赛场次", "胜率", "评分", "详细信息"]
        )
        self.ranking_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        # 将控件添加到主布局
        main_layout.addLayout(control_layout)
        main_layout.addWidget(self.ranking_table)

        # 设置中央部件
        self.setCentralWidget(central_widget)

    def start_data_fetching(self):
        """开始获取比赛数据，在独立线程中执行"""
        print("===== 开始获取历史比赛数据 =====")

        # 直接开始批处理流程

        # 1. 初始化数据库连接
        # 设置match_data_manager的批处理模式
        if hasattr(self, "match_data_manager") and hasattr(
            self.match_data_manager, "set_batch_processing"
        ):
            self.match_data_manager.set_batch_processing(True)
            print("已为match_data_manager启用批处理模式")

        # 设置match_parser的批处理模式
        if hasattr(self, "match_parser"):
            try:
                if not self.match_parser.conn:
                    self.match_parser.connect()
                print("数据库连接已建立")
                # 设置批处理模式，防止连接被过早关闭
                if hasattr(self.match_parser, "set_batch_processing"):
                    self.match_parser.set_batch_processing(True)
                    print("已为match_parser启用批处理模式")
            except Exception as e:
                print(f"数据库连接错误: {str(e)}")
                return
        else:
            print("未找到MatchParser实例")
            return

        # 2. 创建并启动批处理线程
        print("创建批处理线程...")
        self.batch_thread = BatchProcessingThread(
            self.match_data_manager, self.match_parser
        )

        # 连接线程信号
        self.batch_thread.progress_update.connect(self.on_batch_progress)
        self.batch_thread.batch_completed.connect(self.on_batch_completed)
        self.batch_thread.all_completed.connect(self.on_all_batches_completed)
        self.batch_thread.error_occurred.connect(self.on_batch_error)

        # 启动线程
        print("启动批处理线程...")
        self.batch_thread.start()
        print("批处理线程已启动")

    def on_batch_progress(self, stage, message):
        """处理批处理进度更新"""
        print(f"[{stage}] {message}")

    def on_batch_completed(self, batch_count, total_batches):
        """处理批次完成"""
        print(f"[批次完成] 已完成批次 {batch_count}/{total_batches}")

    def on_all_batches_completed(self):
        """处理所有批次完成"""
        print("\n[全部完成] 所有批次数据获取已完成！")

        # 关闭数据库连接
        # 取消match_data_manager的批处理模式
        if hasattr(self, "match_data_manager") and hasattr(
            self.match_data_manager, "set_batch_processing"
        ):
            self.match_data_manager.set_batch_processing(False)
            print("已为match_data_manager禁用批处理模式")
            if hasattr(self.match_data_manager, "close"):
                self.match_data_manager.close()
                print("已关闭match_data_manager连接")

        # 取消match_parser的批处理模式
        if hasattr(self, "match_parser"):
            # 取消批处理模式
            if hasattr(self.match_parser, "set_batch_processing"):
                self.match_parser.set_batch_processing(False)
                print("已为match_parser禁用批处理模式")
            # 关闭连接
            if hasattr(self.match_parser, "close"):
                self.match_parser.close()
                print("已关闭match_parser连接")

    def on_batch_error(self, error_message):
        """处理批处理错误"""
        print(f"[错误] {error_message}")

    def closeEvent(self, event):
        """窗口关闭时释放资源"""
        # 停止批处理线程（如果存在）
        if hasattr(self, "batch_thread") and self.batch_thread.isRunning():
            print("停止批处理线程...")
            self.batch_thread.stop()
            print("批处理线程已停止")

        # 关闭match_parser的数据库连接
        if hasattr(self, "match_parser") and self.match_parser:
            self.match_parser.close()

        # 调用父类的closeEvent方法
        super().closeEvent(event)
