import sys
from src.main_window import RankingSystemMainWindow
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """主函数，启动浩子比赛排名系统界面"""
    logger.info("启动浩子比赛排名系统")

    # 确保设置好正确的编码
    os.environ["QT_FONT_DPI"] = "96"
    os.environ["PYTHONUTF8"] = "1"

    # 创建Qt应用程序
    app = QApplication(sys.argv)
    # 设置应用程序图标
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.png")
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)

        # 对于Windows平台，确保任务栏图标正确显示
        if sys.platform == "win32":
            # 添加一个额外的图标设置，有助于Windows任务栏正确识别应用程序图标
            import ctypes

            try:
                # 设置应用程序ID，这有助于Windows任务栏正确显示图标
                app_id = "com.haozi.football_rank"
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
            except Exception as e:
                logger.warning(f"设置Windows应用程序ID时出错: {str(e)}")

    # 创建并显示主窗口
    window = RankingSystemMainWindow()
    window.show()

    # 运行应用程序事件循环
    print("启动应用程序事件循环...")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
