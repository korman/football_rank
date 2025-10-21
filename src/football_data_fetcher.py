from PyQt6.QtCore import QObject, pyqtSignal, QThread
from datetime import datetime, timedelta
from .fetch_worker import FetchWorker
import json


class FootballDataFetcher(QObject):
    dataFetched = pyqtSignal(dict)  # 信号：成功获取 JSON 数据
    errorOccurred = pyqtSignal(str)  # 信号：错误消息

    def __init__(self, api_key):
        super().__init__()
        self.api_key = api_key
        self.base_url = "https://api.football-data.org/v4/competitions/{code}/matches"
        self.active_threads = []  # 存储活动线程的引用，防止垃圾回收

    def fetch_matches(self, league_code, date_from, date_to):
        """请求比赛数据：联赛代码、起始日期 (YYYY-MM-DD)、结束日期 (YYYY-MM-DD)"""
        # 参数验证
        try:
            datetime.strptime(date_from, "%Y-%m-%d")
            datetime.strptime(date_to, "%Y-%m-%d")
        except ValueError:
            self.errorOccurred.emit("日期格式无效，应为 YYYY-MM-DD")
            return

        # 构建 URL 和参数
        url = self.base_url.format(code=league_code.upper())
        params = {"dateFrom": date_from, "dateTo": date_to}
        headers = {"X-Auth-Token": self.api_key}

        print(f"请求 URL: {url}")
        print(f"请求参数: {params}")
        print(f"请求头: {headers}")

        # 直接在主线程中执行请求，以排除线程相关问题
        print("直接在主线程中执行API请求")
        try:
            import requests

            response = requests.get(url, params=params, headers=headers, timeout=9)
            print(f"获取响应，状态码: {response.status_code}")

            if response.status_code == 200:
                print("响应成功，解析JSON数据...")
                data = response.json()
                print(f"成功解析JSON，数据类型: {type(data)}")
                self.on_data_ready(data)
            else:
                print(f"响应失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
                self.on_error(f"HTTP错误: {response.status_code} - {response.reason}")

        except requests.Timeout:
            print("请求超时")
            self.on_error("请求超时，请检查网络")
        except requests.RequestException as e:
            print(f"请求异常: {str(e)}")
            self.on_error(f"请求失败: {str(e)}")
        except Exception as e:
            print(f"未知异常: {str(e)}")
            self.on_error(f"未知错误: {str(e)}")

    def on_data_ready(self, data):
        """处理成功数据"""
        print("数据获取成功")
        self.dataFetched.emit(data)

    def on_error(self, error_msg):
        """处理错误"""
        print("数据获取失败:", error_msg)
        self.errorOccurred.emit(error_msg)


# 使用示例（在 PyQt6 应用中）
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import QTimer, QCoreApplication

    print("创建QApplication实例")
    app = QApplication([])

    # 设置应用程序信息
    QCoreApplication.setApplicationName("FootballDataFetcher")

    print("创建FootballDataFetcher实例")
    api_key = "925538c2d157429ca8cd7f73a97cd974"
    fetcher = FootballDataFetcher(api_key)

    # 创建一个简单的类来跟踪状态
    class ResponseTracker:
        def __init__(self):
            self.received = False

    print("创建响应跟踪器")
    tracker = ResponseTracker()

    # 连接信号
    print("连接信号和槽函数")

    def on_data_received(data):
        print("接收到数据信号！")
        # 输出完整的JSON数据
        import json

        print("完整数据内容:")
        print(json.dumps(data, indent=4, ensure_ascii=False))
        tracker.received = True
        print("设置响应标志为True")
        # 收到响应后1秒退出应用
        print("设置1秒后退出应用")
        QTimer.singleShot(1000, app.quit)

    def on_error_received(msg):
        print(f"接收到错误信号: {msg}")
        tracker.received = True
        print("设置响应标志为True")
        # 收到错误后1秒退出应用
        print("设置1秒后退出应用")
        QTimer.singleShot(1000, app.quit)

    fetcher.dataFetched.connect(on_data_received)
    fetcher.errorOccurred.connect(on_error_received)

    # 请求示例：最近10天英超
    print("准备日期参数")
    today = datetime.now().strftime("%Y-%m-%d")
    from_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
    print(f"日期范围: {from_date} 到 {today}")

    print("调用fetch_matches方法")
    fetcher.fetch_matches("PL", from_date, today)

    # 设置一个超时，以防请求永远不返回
    print("设置60秒超时")
    QTimer.singleShot(
        60000, lambda: not tracker.received and (print("超时，退出应用"), app.quit())
    )

    print("启动应用程序事件循环")
    sys.exit(app.exec())
