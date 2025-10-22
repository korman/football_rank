from PyQt6.QtCore import QObject, pyqtSignal, QThread
from datetime import datetime
import requests
import sys
import json
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class FetchWorker(QObject):
    finished = pyqtSignal()
    data_ready = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    progress_update = pyqtSignal(str)  # 添加进度更新信号

    def __init__(self, url, params, headers):
        super().__init__()
        self.url = url
        self.params = params
        self.headers = headers
        self.session = requests.Session()  # 使用会话以保持连接

        # 配置会话参数
        self.session.timeout = 30  # 增加超时时间
        self.session.max_redirects = 5

        # 添加重试逻辑
        retry_strategy = Retry(
            total=3,  # 最大重试次数
            status_forcelist=[429, 500, 502, 503, 504],  # 需要重试的状态码
            allowed_methods=["GET"],  # 允许重试的HTTP方法
            backoff_factor=1,  # 重试间隔时间因子
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        print("FetchWorker初始化完成，已配置重试机制和会话")

    def run(self):
        start_time = time.time()
        print(f"[{time.strftime('%H:%M:%S')}] 开始执行API请求...")
        try:
            self.progress_update.emit("准备请求...")
            print(f"请求URL: {self.url}")
            print(f"请求参数: {self.params}")
            # 只打印部分请求头，避免暴露敏感信息
            masked_headers = {
                k: "***" if "token" in k.lower() else v for k, v in self.headers.items()
            }
            print(f"请求头: {masked_headers}")

            # 发送请求，设置更详细的超时参数
            self.progress_update.emit("发送请求...")
            response = self.session.get(
                self.url, params=self.params, headers=self.headers, timeout=(5, 30)
            )

            elapsed_time = time.time() - start_time
            print(
                f"[{time.strftime('%H:%M:%S')}] 获取响应，状态码: {response.status_code}"
            )
            print(f"[{time.strftime('%H:%M:%S')}] 请求耗时: {elapsed_time:.2f}秒")
            print(f"响应内容长度: {len(response.content)} 字节")

            # 特别处理403和429错误
            if response.status_code == 403:
                error_msg = "权限错误(403): API密钥没有足够权限访问此资源"
                print(f"[{time.strftime('%H:%M:%S')}] {error_msg}")
                if hasattr(response, "text"):
                    print(
                        f"[{time.strftime('%H:%M:%S')}] 响应内容: {response.text[:200]}..."
                    )
                self.error_signal.emit(error_msg)
                return
            elif response.status_code == 429:
                remaining_requests = response.headers.get(
                    "X-Requests-Available-Minute", "未知"
                )
                reset_time = response.headers.get("X-RequestCounter-Reset", "未知")
                error_msg = f"请求频率限制(429): 剩余请求: {remaining_requests}/分钟，重置时间: {reset_time}秒"
                print(f"[{time.strftime('%H:%M:%S')}] {error_msg}")
                self.error_signal.emit(error_msg)
                return

            response.raise_for_status()  # 自动抛出其他HTTP错误

            self.progress_update.emit("解析响应...")
            print("响应成功，解析JSON数据...")
            data = response.json()
            print(f"成功解析JSON，数据类型: {type(data)}")

            # 输出部分数据以验证
            if isinstance(data, dict) and "matches" in data and data["matches"]:
                print(f"成功获取数据，匹配数量: {len(data.get('matches', []))}")
                first_match = data["matches"][0]
                if isinstance(first_match, dict):
                    match_date = first_match.get("utcDate", "N/A")
                    print(f"第一个匹配日期: {match_date}")

            self.data_ready.emit(data)

        except requests.Timeout as e:
            elapsed_time = time.time() - start_time
            error_msg = f"请求超时 ({elapsed_time:.2f}秒): {str(e)}"
            print(f"[{time.strftime('%H:%M:%S')}] {error_msg}")
            self.error_signal.emit(error_msg)
        except requests.ConnectionError as e:
            error_msg = f"连接错误: {str(e)}"
            print(f"[{time.strftime('%H:%M:%S')}] {error_msg}")
            self.error_signal.emit(error_msg)
        except requests.HTTPError as e:
            error_msg = f"HTTP错误: {str(e)}"
            print(f"[{time.strftime('%H:%M:%S')}] {error_msg}")
            # 尝试获取响应内容以获取更多信息
            if hasattr(e.response, "text"):
                print(
                    f"[{time.strftime('%H:%M:%S')}] 响应内容: {e.response.text[:200]}..."
                )  # 只打印前200个字符
            self.error_signal.emit(error_msg)
        except json.JSONDecodeError as e:
            error_msg = f"JSON解析错误: {str(e)}"
            print(f"[{time.strftime('%H:%M:%S')}] {error_msg}")
            self.error_signal.emit(error_msg)
        except requests.RequestException as e:
            error_msg = f"请求异常: {str(e)}"
            print(f"[{time.strftime('%H:%M:%S')}] {error_msg}")
            self.error_signal.emit(f"请求失败: {str(e)}")
        except Exception as e:
            error_msg = f"未知异常: {str(e)}"
            print(f"[{time.strftime('%H:%M:%S')}] 错误类型: {type(e).__name__}")
            print(f"[{time.strftime('%H:%M:%S')}] {error_msg}")
            import traceback

            traceback.print_exc()
            self.error_signal.emit(f"未知错误: {str(e)}")
        finally:
            elapsed_time = time.time() - start_time
            print(
                f"[{time.strftime('%H:%M:%S')}] 请求完成，总耗时: {elapsed_time:.2f}秒，发出finished信号"
            )
            self.finished.emit()
            # 清理会话
            self.session.close()
