import sys
sys.path.insert(0, ".")

from funboost import boost

# 你的任务
@boost("test_queue")
def add(a, b):
    res = a + b
    print(f"{a} + {b} = {res}")
    return res


# 👇 下面是固定写法，适配你版本的 启动消费 + 启动Web
if __name__ == '__main__':
    # 发布任务
    add.push(1, 2)
    add.push(3, 4)
    add.push(5, 6)

    # 直接运行，自动启动 Web + 消费
    add.consume()