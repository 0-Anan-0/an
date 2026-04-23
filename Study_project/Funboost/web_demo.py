import sys
sys.path.insert(0, r"E:\Ending of study\py_workspace\Study_project\Funboost")
from funboost import boost
import logging
logging.basicConfig(level=logging.INFO)  # 仅显示 INFO 及以上级别日志

from funboost import boost
from funboost import run_consumer  # 导入启动器
from funboost.web.web_monkey_patch import start_flask_web  # 导入Web后台

# 定义任务
@boost('test_queue', qps=10)
def add(a, b):
    print(f"{a} + {b} = {a + b}")
    return a + b

# 启动 Web 监控后台（默认端口 6666）
start_flask_web()

# 发布任务
if __name__ == '__main__':
    add.push(1, 2)
    add.push(3, 4)
    add.push(5, 6)
    
    # 启动消费者（必须启动才能消费任务）
    run_consumer(['test_queue'])