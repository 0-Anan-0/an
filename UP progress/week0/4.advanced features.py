
# 切片
import var

l = var.L
print(l[1:50:10])
print(l[5::-1])

#迭代

d =var.dict1
# 默认迭代的是key  如果想迭代值 则 迭代对象为 d.values()
for key in d:
    print(key)
for values in d.values():
    print(values)

for key,value in d.items():
    print(key,'+',value)

# 方法是通过collections.abc模块的Iterable类型判断
from collections.abc import Iterable
print(isinstance('abc', Iterable))

# 加下标 list  使用enumerate
for i, value in enumerate(['A', 'B', 'C']):
    print(i, value)

## 生成器
# 创建一个generator，有很多种方法。第一种方法很简单，只要把一个列表生成式的[]改成()，就创建了一个generato
l1 = [x * x for x in range(10)]
l2 =(x * x for x in range(10))  #可使用next() 查看下个生成的内容 正常使用for 看

for n in (x * x for x in range(10)):
    print(n)
print(l1,l2)