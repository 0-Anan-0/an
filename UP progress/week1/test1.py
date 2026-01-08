#1. 利用map()函数，把用户输入的不规范的英文名字，变为首字母大写，其他小写的规范名字。输入：['adam', 'LISA', 'barT']，输出：['Adam', 'Lisa', 'Bart']：
def normalize(name):
    return name.capitalize()

# 测试:
L1 = ['adam', 'LISA', 'barT']
L2 = list(map(normalize, L1))
print(L2)

#2. Python提供的sum()函数可以接受一个list并求和，请编写一个prod()函数，可以接受一个list并利用reduce()求积：
from functools import reduce

def s(x,y):
    return x*y
def prod(L):
    return reduce(s,L)

print('3 * 5 * 7 * 9 =', prod([3, 5, 7, 9]))
if prod([3, 5, 7, 9]) == 945:
    print('测试成功!')
else:
    print('测试失败!')



# 利用map和reduce编写一个str2float函数，把字符串'123.456'转换成浮点数123.456：

from functools import reduce


def str2float(s):
    int_p,_,frac_p=s.partition('.')

    # 把字符串转成数字的辅助函数
    def char2num(c):
        return {'0': 0, '1': 1, '2': 2, '3': 3, '4': 4,
                '5': 5, '6': 6, '7': 7, '8': 8, '9': 9}[c]
    #整数
    int_v=reduce(lambda x,y:x*10+y,map(char2num,int_p))
    #小数
    frac_v=reduce(lambda x,y:x*10+y,map(char2num,frac_p)) / (10**len(frac_p))
    return int_v+frac_v

print('str2float(\'123.456\') =', str2float('123.456'))
if abs(str2float('123.456') - 123.456) < 0.00001:
    print('测试成功!')
else:
    print('测试失败!')



## sort()  key=abs    reserve=True
# name
L = [('Bob', 75), ('Adam', 92), ('Bart', 66), ('Lisa', 88)]

def by_name(t):
    return t[0]

    # l2 = sorted(l1,key=by_name,reverse=True)

L2 = sorted(L, key=by_name)
print(L2)
# Score
L = [('Bob', 75), ('Adam', 92), ('Bart', 66), ('Lisa', 88)]

def by_name(t):
    return -t[1]

L2 = sorted(L, key=by_name)#,reverse=True   有负号就已经反转了

print(L2)

# 返回函数
def createCounter():
    x=0
    def counter():
        nonlocal x
        x=x+1
        return x
    return counter

# 测试:
counterA = createCounter()
print(counterA(), counterA(), counterA(), counterA(), counterA()) # 1 2 3 4 5
counterB = createCounter()
if [counterB(), counterB(), counterB(), counterB()] == [1, 2, 3, 4]:
    print('测试通过!')
else:
    print('测试失败!')

