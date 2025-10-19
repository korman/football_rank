import subprocess
import time
import os
import logging
import socket
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import atexit

# 配置日志
logger = logging.getLogger(__name__)


class MongoDBManager:
    """
    MongoDB服务管理类，负责MongoDB服务的启动和关闭
    """

    def __init__(self):
        """
        初始化MongoDB管理器
        """
        self.mongo_proc = None
        self.db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db"
        )
        self.data_dir = os.path.join(self.db_path, "data")
        self.mongod_exe = os.path.join(self.db_path, "mongod.exe")
        self.log_file = os.path.join(self.db_path, "mongodb.log")

        # 注册程序退出时的清理函数
        atexit.register(self.stop_mongodb)

    def _check_port(self, host, port):
        """
        检查指定的端口是否可连接

        Args:
            host (str): 主机名
            port (int): 端口号

        Returns:
            bool: 端口是否可连接
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        try:
            result = sock.connect_ex((host, port))
            return result == 0
        except Exception as e:
            logger.error(f"检查端口连接性时出错: {e}")
            return False
        finally:
            sock.close()

    def start_mongodb(self):
        """
        启动MongoDB服务

        Returns:
            bool: MongoDB是否成功启动
        """
        try:
            # 确保数据目录存在
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
                logger.info(f"已创建MongoDB数据目录: {self.data_dir}")

            # 检查mongod.exe是否存在
            if not os.path.exists(self.mongod_exe):
                logger.error(f"MongoDB可执行文件不存在: {self.mongod_exe}")
                return False

            # 检查端口是否被占用
            if self._check_port("localhost", 27017):
                logger.warning("端口27017已被占用，可能有MongoDB实例正在运行")
                # 尝试连接现有实例
                try:
                    client = MongoClient(
                        "mongodb://localhost:27017/", serverSelectionTimeoutMS=3000
                    )
                    client.server_info()
                    logger.info("成功连接到已运行的MongoDB实例")
                    return True
                except Exception as e:
                    logger.warning(f"连接到已运行的MongoDB实例失败: {e}")
                    # 继续尝试启动新实例

            # 启动MongoDB，添加日志文件参数以便调试
            mongo_args = [
                self.mongod_exe,
                "--dbpath",
                self.data_dir,
                "--port",
                "27017",
                "--logpath",
                self.log_file,
                "--logappend",
            ]

            logger.info(f"尝试启动MongoDB: {mongo_args}")

            # 使用shell=True可以更好地处理Windows上的进程
            self.mongo_proc = subprocess.Popen(
                mongo_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False,
            )

            # 等待MongoDB启动，增加等待时间并添加重试逻辑
            max_retries = 5
            retry_interval = 2
            connected = False

            for attempt in range(max_retries):
                time.sleep(retry_interval)

                # 检查进程是否还在运行
                if self.mongo_proc.poll() is not None:
                    # 读取错误输出
                    stderr = self.mongo_proc.stderr.read()
                    logger.error(
                        f"MongoDB启动失败，退出代码: {self.mongo_proc.returncode}, 错误输出: {stderr}"
                    )
                    self.mongo_proc = None
                    return False

                # 检查端口是否可用
                if self._check_port("localhost", 27017):
                    logger.info(
                        f"MongoDB服务已启动并监听端口27017 (尝试 {attempt + 1}/{max_retries})"
                    )
                    # 尝试连接MongoDB
                    try:
                        client = MongoClient(
                            "mongodb://localhost:27017/", serverSelectionTimeoutMS=5000
                        )
                        client.server_info()  # 验证连接是否成功
                        logger.info("MongoDB启动成功并成功连接")
                        connected = True
                        break
                    except ConnectionFailure as e:
                        logger.warning(f"MongoDB连接尝试 {attempt + 1} 失败: {e}")
                else:
                    logger.info(
                        f"MongoDB尚未监听端口27017 (尝试 {attempt + 1}/{max_retries})"
                    )

            if not connected:
                logger.error("MongoDB启动后无法连接，达到最大重试次数")
                self.stop_mongodb()
                return False

            return True

        except Exception as e:
            logger.error(f"启动MongoDB时发生异常: {e}")
            self.stop_mongodb()
            return False

    def stop_mongodb(self):
        """
        停止MongoDB服务
        """
        if self.mongo_proc is None:
            return

        try:
            # 尝试通过MongoDB命令优雅关闭
            try:
                client = MongoClient("mongodb://localhost:27017/")
                logger.info("尝试优雅关闭MongoDB")
                client.admin.command("shutdown")
                # 等待进程结束
                self.mongo_proc.wait(timeout=10)
                logger.info("MongoDB已优雅关闭")
            except Exception as e:
                logger.warning(f"优雅关闭MongoDB失败: {e}")
                # 强制终止进程
                logger.info("强制终止MongoDB进程")
                self.mongo_proc.terminate()
                try:
                    self.mongo_proc.wait(timeout=10)
                    logger.info("MongoDB进程已成功终止")
                except subprocess.TimeoutExpired:
                    logger.warning("MongoDB进程终止超时，强制杀死")
                    self.mongo_proc.kill()
        except Exception as e:
            logger.error(f"停止MongoDB时发生异常: {e}")
        finally:
            self.mongo_proc = None

    def is_running(self):
        """
        检查MongoDB服务是否正在运行

        Returns:
            bool: MongoDB服务是否正在运行
        """
        # 检查进程是否存在且运行中
        if self.mongo_proc is not None:
            return self.mongo_proc.poll() is None

        # 检查端口是否开放
        return self._check_port("localhost", 27017)

    def create_match_data_manager(self, db_name, collection_name):
        """
        创建比赛数据管理实例
        注意：此方法需要在MongoDB服务启动后调用

        Args:
            db_name (str): 数据库名称
            collection_name (str): 集合名称

        Returns:
            MatchDataManager: 比赛数据管理实例，如果创建失败返回None
        """
        try:
            # 确保MongoDB服务已启动
            if not self.is_running():
                logger.warning("MongoDB服务未运行，尝试启动...")
                if not self.start_mongodb():
                    logger.error("MongoDB服务启动失败，无法创建MatchDataManager")
                    return None

            # 延迟导入以避免循环依赖
            from .match_data import MatchDataManager

            # 创建并返回MatchDataManager实例
            match_data_manager = MatchDataManager(db_name, collection_name)

            # 验证创建是否成功
            if match_data_manager.is_connected():
                logger.info(
                    f"成功创建MatchDataManager实例，数据库: {db_name}，集合: {collection_name}"
                )
                return match_data_manager
            else:
                logger.error("MatchDataManager创建成功但连接失败")
                return None

        except ImportError as e:
            logger.error(f"导入MatchDataManager失败: {e}")
            return None
        except Exception as e:
            logger.error(f"创建MatchDataManager实例时发生异常: {e}")
            return None
