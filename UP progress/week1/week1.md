# 高阶函数

## mapreduce

### map()
map()函数接收两个参数，一个是函数，一个是Iterable，map将传入的函数依次作用到序列的每个元素，并把结果作为新的Iterator

`r=map(f,[x for x in range(9)])         [0, 1, 4, 9, 16, 25, 36, 49, 64]`
`l=list(map(str,[1,2,3,4]))         ['1', '2', '3', '4']`


**map(f,v) 实际就是将 v 的值  ***逐个***  带入f进行计算**

### reduce()
函数必须接收两个参数，reduce把结果继续和序列的下一个元素做累积计算

`reduce(f, [x1, x2, x3, x4]) = f(f(f(x1, x2), x3), x4)`
