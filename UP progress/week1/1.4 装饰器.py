## 装饰器
import datetime
import time
def now():
    time1=datetime.time()
    print('现在时间是：',time1)

f=now
f1=now()
print(f.__name__)
# print(f1.__name__)


def log(func):
    def wrapper(*args, **kw):
        print('call %s():' % func.__name__)
        return func(*args, **kw)
    return wrapper

@log
def now():
    time1 = datetime.time()
    print('现在时间是：', time1)

print(now())

now1 = log(now)
print(now1)