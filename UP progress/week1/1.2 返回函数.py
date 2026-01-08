# 高阶函数除了可以接受函数作为参数外，还可以把函数作为结果值返回。

def clac_sum(*args):
    ax=0
    for n in args:
        ax=ax+n
    return ax

print(clac_sum(1,7,65))

# 不返回求和的结果，而是返回求和的函数sum ：若返回的是sum()则是执行了的
def lazy_sum(*args):
    def sum():
        ax=0
        for n in args:
            ax = ax + n
        return ax
    return sum

print(lazy_sum(1,7,65))
print(lazy_sum(1,7,65)())

# 闭包
# 返回的函数在其定义内部引用了局部变量args，所以，当一个函数返回了一个函数后，其内部的局部变量还被新函数引用，所以，闭包用起来简单，实现起来可不容易。
#错误示范
def count():
    fs = []
    for i in range(1, 4):
        def f():
             return i*i
        fs.append(f)
    return fs

f1, f2, f3 = count()
#f1(),f2(),f3() 9，9，9
# !!! 返回闭包时牢记一点：返回函数不要引用任何循环变量，或者后续会发生变化的变量。
def count():
    def f(j):
        def g():
            return j*j
        return g   # g()
    fs = []
    for i in range(1, 4):
        fs.append(f(i)) # f(i)立刻被执行，因此i的当前值被传入f()
    return fs

# 使用闭包时，对外层变量赋值前，需要先使用nonlocal声明该变量不是当前函数的局部变量。

def inc():
    x = 0
    def fn():
        # 仅读取x的值:
        return x + 1
    return fn

f = inc()
print(f()) # 1
print(f()) # 1

def inc():
    x = 0
    def fn():
        nonlocal x
        x = x + 1
        return x
    return fn

f = inc()
print(f()) # 1
print(f()) # 2
print(f()) #3