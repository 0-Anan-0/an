# 调用一个函数
a=abs(-100)

# 定义一个函数
def abc(x):
    if x>100:
        return x-9999
    else:
        return x**2

#空函数 ，无事发生 当占位符可运行
def nop(x):
    if x >999:
        pass

def my_abs(x):
    if not isinstance(x, (int, float)):
        raise TypeError('bad operand type这不是我要的数据类型')
    if x >= 0:
        return x
    else:
        return -x

# 返回多个参数
import math

def move(x, y, step, angle=0):
    nx = x + step * math.cos(angle)
    ny = y - step * math.sin(angle)
    return nx, ny


print(a,abc(100),nop(1),my_abs(1))
x,y=move(100, 100, 60, math.pi / 6)
print(x,y)
# print(my_abs('a'))


def quadratic(a,b,c):
    x1=b*b-4*a*c
    x21=(-b+math.sqrt(x1))/(2*a)
    x22=(-b-math.sqrt(x1))/(2*a)
    return x21,x22
# print(quadratic(2, 3, 1))

# 测试:

print('quadratic(2, 3, 1) =', quadratic(2, 3, 1))
print('quadratic(1, 3, -4) =', quadratic(1, 3, -4))

if quadratic(2, 3, 1) != (-0.5, -1.0):
    print('测试失败')
elif quadratic(1, 3, -4) != (1.0, -4.0):
    print('测试失败')
else:
    print('测试成功')

# 递归函数
def fact(n):
    if n==1:
        return 1
    return n * fact(n - 1)

print(fact(5))

def move(n,a,b,c):
    if n==1:
        print('move',a,'-->',c)
    else:
        move(n-1,a,c,b)
        move(1,a,b,c)
        move(n-1,b,a,c)
move(3, 'A', 'B', 'C')