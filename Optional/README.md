# QuModLibs 可选扩展
本目录包含QuModLibs的可选扩展模块，可以根据需要选择性地合并到项目中使用。 

## EventRegistry 模块
EventRegistry模块提供了一套适用于Py2面向对象的事件注册解决方案。

```python
# -*- coding: utf-8 -*-
from .QuModLibs.Client import *
from .QuModLibs.Modules.EventRegistry.ClientBus import SubscribeEvent, GameEvents

@SubscribeEvent
def onTick(event=GameEvents.OnScriptTickClient()):
    print("Tick event received!")

@SubscribeEvent
def onJump(event=GameEvents.ClientJumpButtonPressDownEvent()):
    event.continueJump = False
    print("Jump event received!")
```
由于Py2中并不支持类型注解，作为替代，事件类型需要通过默认参数的方式进行指定。