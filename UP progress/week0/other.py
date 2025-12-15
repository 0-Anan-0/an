import traceback
traceback.print_stack()          # 直接打印到控制台
# 或者
stack = traceback.format_stack() # 返回字符串列表，可自己写日志
print(''.join(stack))

import inspect
frame = inspect.currentframe()   # 当前帧
for finfo in inspect.getouterframes(frame):
    print(finfo.filename, finfo.lineno, finfo.function)