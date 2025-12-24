#高阶函数
from functools import reduce
# map()  reduce()

#
def f(x):
    return x*x

r=map(f,[x for x in range(9)])
print(r)            # 此时的r  是一个 map 迭代器
print(list(r))      #使用list（） 将整个序列计算返回

l=list(map(str,[1,2,3,4]))
print(l)

# reduce
# 函数必须接收两个参数，reduce把结果继续和序列的下一个元素做累积计算
import math
from functools import reduce
def add(x, y):
    return x + y

reduce(add, [1, 3, 5, 7, 9])

from functools import reduce

DIGITS = {'a': 0, 'b': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}

def char2num(s):
    return DIGITS[s]

def str2int(s):
    return reduce(lambda x, y: x * 10 + y, map(char2num, s))

print(str2int('a'))

## filter(fn,l)
# 和map()类似，filter()也接收一个函数和一个序列。和map()不同的是，filter()把传入的函数依次作用于每个元素，然后根据返回值是True还是False决定保留还是丢弃该元素
def is_odd(n):
    return n % 2 == 1

list(filter(is_odd, [1, 2, 4, 5, 6, 9, 10, 15]))
[1, 5, 9, 15]


# sorted(l,key=,reverse)