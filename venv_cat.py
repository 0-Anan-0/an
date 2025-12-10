import os
import sys
import subprocess
import platform
from pathlib import Path
from typing import List, Dict


def get_venv_paths() -> List[Path]:
    """
    查找系统中常见的虚拟环境路径
    优先查找用户目录下的虚拟环境，支持 venv/virtualenv/conda 格式
    """
    venv_paths = []
    user_home = Path.home()

    # 常见的虚拟环境存放目录
    common_venv_dirs = [
        user_home / "venvs",  # 手动创建的 venv 目录
        user_home / ".virtualenvs",  # virtualenvwrapper 默认目录
        user_home / "anaconda3" / "envs",  # conda 默认环境目录
        user_home / "miniconda3" / "envs",  # miniconda 环境目录
    ]

    # 遍历常见目录查找虚拟环境
    for dir_path in common_venv_dirs:
        if dir_path.exists() and dir_path.is_dir():
            for subdir in dir_path.iterdir():
                # 判断是否为虚拟环境目录（通过标志性文件/目录）
                if (subdir / "bin" / "python").exists() or \
                        (subdir / "Scripts" / "python.exe").exists() or \
                        (subdir / "lib" / "python*").exists():
                    venv_paths.append(subdir)

    # 额外查找当前目录下的 venv 目录
    current_venv = Path.cwd() / "venv"
    if current_venv.exists():
        venv_paths.append(current_venv)

    # 去重并排序
    venv_paths = list(dict.fromkeys(venv_paths))
    venv_paths.sort()

    return venv_paths


def get_conda_envs() -> List[Dict[str, str]]:
    """
    通过 conda 命令获取 conda 虚拟环境列表
    """
    conda_envs = []
    try:
        # 执行 conda info --envs 命令
        result = subprocess.run(
            ["conda", "info", "--envs"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            # 跳过表头，解析环境信息
            for line in lines[2:]:
                if line.strip() and not line.startswith("#"):
                    parts = line.split()
                    if len(parts) >= 2:
                        env_name = parts[0].strip()
                        env_path = " ".join(parts[1:]).strip()
                        conda_envs.append({"name": env_name, "path": env_path})
    except (FileNotFoundError, subprocess.CalledProcessError):
        # 未安装 conda 或命令执行失败
        pass

    return conda_envs


def get_venv_packages(venv_path: Path) -> List[str]:
    """
    获取指定虚拟环境中安装的库列表
    """
    packages = []
    # 确定 python 可执行文件路径
    if platform.system() == "Windows":
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        python_exe = venv_path / "bin" / "python"

    if not python_exe.exists():
        return packages

    try:
        # 执行 pip list 命令获取已安装包
        result = subprocess.run(
            [str(python_exe), "-m", "pip", "list", "--format=freeze"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
        if result.returncode == 0:
            packages = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]
    except Exception as e:
        print(f"⚠️  获取 {venv_path.name} 包列表失败: {e}")

    return packages


def main():
    print("=" * 60)
    print("🎯 Python 虚拟环境检测工具")
    print(f"🖥️  系统: {platform.system()} {platform.release()}")
    print(f"🐍 当前 Python: {sys.version.split()[0]}")
    print("=" * 60)

    # 1. 获取 venv/virtualenv 环境
    venv_paths = get_venv_paths()
    # 2. 获取 conda 环境
    conda_envs = get_conda_envs()

    # 打印 venv/virtualenv 环境信息
    if venv_paths:
        print("\n📦 检测到 venv/virtualenv 虚拟环境:")
        print("-" * 60)
        for idx, venv_path in enumerate(venv_paths, 1):
            print(f"\n[{idx}] 环境名称: {venv_path.name}")
            print(f"   路径: {venv_path.absolute()}")

            # 获取包列表
            packages = get_venv_packages(venv_path)
            if packages:
                print(f"   已安装库 ({len(packages)} 个):")
                # 按列展示包列表（每行显示3个）
                for i in range(0, len(packages), 3):
                    line_pkgs = packages[i:i + 3]
                    print(f"     {' | '.join(line_pkgs)}")
            else:
                print(f"   已安装库: 无 / 获取失败")
    else:
        print("\n⚠️  未检测到 venv/virtualenv 虚拟环境")

    # 打印 conda 环境信息
    if conda_envs:
        print("\n📦 检测到 Conda 虚拟环境:")
        print("-" * 60)
        for idx, env in enumerate(conda_envs, 1):
            print(f"\n[{idx}] 环境名称: {env['name']}")
            print(f"   路径: {env['path']}")

            # 获取 conda 环境的包列表
            try:
                result = subprocess.run(
                    ["conda", "list", "-n", env['name'], "--export"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="ignore"
                )
                if result.returncode == 0:
                    packages = [line.strip() for line in result.stdout.strip().split("\n") if
                                line.strip() and not line.startswith("#")]
                    print(f"   已安装库 ({len(packages)} 个):")
                    for i in range(0, len(packages), 3):
                        line_pkgs = packages[i:i + 3]
                        print(f"     {' | '.join(line_pkgs)}")
                else:
                    print(f"   已安装库: 获取失败 (conda list 执行失败)")
            except Exception as e:
                print(f"   已安装库: 获取失败 - {e}")
    else:
        print("\n⚠️  未检测到 Conda 虚拟环境 (未安装/未配置环境变量)")

    print("\n" + "=" * 60)
    print("✅ 检测完成")


if __name__ == "__main__":
    main()