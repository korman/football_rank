import logging
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from datetime import datetime, timedelta
from .fetch_worker import FetchWorker
import json


class FootballDataFetcher(QObject):
    dataFetched = pyqtSignal(str, dict)  # 信号：联赛代码, 成功获取 JSON 数据
    errorOccurred = pyqtSignal(str, str)  # 信号：联赛代码, 错误消息
    progressUpdate = pyqtSignal(str, str)  # 进度更新信号

    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.base_url = "https://api.football-data.org/v4/competitions/{code}/matches"
        self.active_threads = []  # 存储活动线程的引用，防止垃圾回收
        self.current_league = None
        self.current_date_range = None

        print(
            f"FootballDataFetcher初始化完成，API Key: {'*' * len(self.api_key[:-4]) + self.api_key[-4:]}"
        )

    def fetch_matches(self, league_code, date_from, date_to):
        """请求比赛数据：联赛代码、起始日期 (YYYY-MM-DD)、结束日期 (YYYY-MM-DD)"""
        print(
            f"fetch_matches被调用: 联赛={league_code}, 日期范围={date_from} 到 {date_to}"
        )

        # 保存当前请求的信息
        self.current_league = league_code
        self.current_date_range = f"{date_from} 到 {date_to}"

        # 参数验证
        try:
            datetime.strptime(date_from, "%Y-%m-%d")
            datetime.strptime(date_to, "%Y-%m-%d")
        except ValueError:
            self.errorOccurred.emit(league_code, "日期格式无效，应为 YYYY-MM-DD")
            return

        # 构建 URL 和参数
        url = self.base_url.format(code=league_code.upper())
        params = {"dateFrom": date_from, "dateTo": date_to}
        headers = {"X-Auth-Token": self.api_key, "Content-Type": "application/json"}

        print(f"请求 URL: {url}")
        print(f"请求参数: {params}")
        print(f"请求头: {headers}")

        # 创建新线程和工作对象
        thread = QThread()
        worker = FetchWorker(url, headers, params)  # 注意参数顺序已调整

        # 将工作对象移到线程中
        worker.moveToThread(thread)

        # 连接信号和槽
        thread.started.connect(worker.run)
        worker.data_ready.connect(
            lambda data, code=league_code: self.on_data_ready(code, data)
        )
        worker.error_signal.connect(
            lambda error, code=league_code: self.on_error(code, error)
        )
        worker.progress_update.connect(
            lambda msg, code=league_code: self.on_progress_update(code, msg)
        )
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)

        # 保存线程引用，防止垃圾回收
        self.active_threads.append(thread)
        thread.finished.connect(lambda thread=thread: self._cleanup_thread(thread))

        # 启动线程
        thread.start()
        print("已在线程中启动API请求")
        self.progressUpdate.emit(league_code, "请求已启动")

    def _cleanup_thread(self, thread):
        """清理完成的线程引用"""
        if thread in self.active_threads:
            self.active_threads.remove(thread)
            print(f"线程已清理，剩余活动线程数: {len(self.active_threads)}")

    def on_data_ready(self, league_code, data):
        """处理成功数据"""
        print(f"[调试] 数据获取成功，联赛: {league_code}")
        print(f"数据类型: {type(data)}, 包含匹配: {len(data.get('matches', []))}")
        self.dataFetched.emit(league_code, data)

    def on_error(self, league_code, error_msg):
        """处理错误"""
        print(f"[调试] 数据获取失败，联赛: {league_code}, 错误: {error_msg}")
        self.errorOccurred.emit(league_code, error_msg)

    def on_progress_update(self, league_code, progress_msg):
        """处理进度更新"""
        self.progressUpdate.emit(league_code, progress_msg)
