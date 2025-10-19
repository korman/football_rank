import sys
import os

# 添加项目根目录到Python路径，确保能够导入src模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def test_python_environment():
    """测试Python环境"""
    print(f"\nPython版本: {sys.version}")
    print(f"Python路径: {sys.path}")
    assert sys.version_info >= (3, 7), "Python版本需要3.7或更高"


def test_pymongo_import():
    """测试pymongo模块导入"""
    try:
        import pymongo

        print(f"\npymongo版本: {pymongo.__version__}")
        assert pymongo.__version__, "pymongo版本信息为空"
    except ImportError:
        print("\n警告: 无法导入pymongo模块")
        # 这里不使用assert失败，因为测试环境可能没有安装pymongo


def test_league_mapper_import():
    """测试league_mapper模块导入"""
    try:
        from src.league_mapper import get_league_code

        print("\n成功导入league_mapper模块")

        # 测试get_league_code函数
        code = get_league_code("英超")
        print(f"英超对应的联赛代码: {code}")
        assert code == "E0", f"预期英超对应的联赛代码是'E0'，但实际是'{code}'"

        # 测试另一个联赛
        code = get_league_code("西甲")
        print(f"西甲对应的联赛代码: {code}")
        assert code == "SP1", f"预期西甲对应的联赛代码是'SP1'，但实际是'{code}'"

    except ImportError:
        print("\n错误: 无法导入league_mapper模块")
        # 这里使用assert失败，因为league_mapper应该是项目的核心模块
        assert False, "无法导入league_mapper模块"


# 添加主函数支持直接运行
if __name__ == "__main__":
    test_python_environment()
    test_pymongo_import()
    test_league_mapper_import()
    print("\n所有测试完成")
