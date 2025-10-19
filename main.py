import sys
from src.main_window import RankingSystemMainWindow
from PyQt6.QtWidgets import QApplication


def main():
    """主函数，启动浩子比赛排名系统界面"""
    # 创建Qt应用程序实例
    app = QApplication(sys.argv)

    # 创建并显示主窗口
    window = RankingSystemMainWindow()
    window.show()

    # 运行应用程序事件循环
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
