# 匿名函数 lambda
# 关键字lambda表示匿名函数，冒号前面的x表示函数参数
def f(x):
    return x * x

f1=lambda x:x*x
print(f(5))
print(f)
print(f1(5))

# test
def is_odd(n):
    return n % 2 == 1

odd=lambda n:n%2==1

L = list(filter(is_odd, range(1, 20)))
l = list(filter(odd,range(1,20)))
print(L,l)

