# 通过集成pydantic中的BaseModel抽象类来定义状态State, 定义后的状态可以对键值对属性进行自动校验
from pydantic import BaseModel

class Mystate(BaseModel):
    x:int
    y:str='defaylt'

#自动校验
state =Mystate(x=1)
print(state.x)
print(state.y)
state1=Mystate(x='!')