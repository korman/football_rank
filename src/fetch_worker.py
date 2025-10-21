from PyQt6.QtCore import QObject, pyqtSignal, QThread
from datetime import datetime
import requests
import sys


class FetchWorker(QObject):
    finished = pyqtSignal()
    data_ready = pyqtSignal(dict)
    error_signal = pyqtSignal(str)

    def __init__(self, url, params, headers):
        super().__init__()
        self.url = url
        self.params = params
        self.headers = headers
        print("FetchWorker初始化完成")

    def run(self):
        print("开始执行API请求...")
        try:
            print(f"请求URL: {self.url}")
            print(f"请求参数: {self.params}")
            print(f"请求头: {self.headers}")

            response = requests.get(
                self.url, params=self.params, headers=self.headers, timeout=9
            )

            print(f"获取响应，状态码: {response.status_code}")

            if response.status_code == 200:
                print("响应成功，解析JSON数据...")
                data = response.json()
                print(f"成功解析JSON，数据类型: {type(data)}")
                self.data_ready.emit(data)
            else:
                print(f"响应失败，状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
                self.error_signal.emit(
                    f"HTTP错误: {response.status_code} - {response.reason}"
                )

        except requests.Timeout:
            print("请求超时")
            self.error_signal.emit("请求超时，请检查网络")
        except requests.RequestException as e:
            print(f"请求异常: {str(e)}")
            self.error_signal.emit(f"请求失败: {str(e)}")
        except Exception as e:
            print(f"未知异常: {str(e)}")
            self.error_signal.emit(f"未知错误: {str(e)}")
        finally:
            print("请求完成，发出finished信号")
            self.finished.emit()
