
# list
# Python内置的一种数据类型是列表：list。list是一种有序的集合，可以随时添加和删除其中的元素。
list1 = ['yi','qw','er']
print(type(list1))
print(list1)

ll1=list1.insert(1,'insert')
ll2=list1.append('append')
ll3=list1.sort()
ll4=list1.pop(1)
ll5=list1.remove('yi')
print(ll3)
print(ll1,ll2,ll4,ll5,ll3)


l2=[['q','w','e'],['1','2','3'],['a1','b2','c3']]
print(l2[1])
# tuple
# 另一种有序列表叫元组：tuple。tuple和list非常类似，但是tuple一旦初始化就不能修改，比如同样是列出同学的名字：
tuple1=('1','2','3')
print(type(tuple1))
print(tuple1[1])