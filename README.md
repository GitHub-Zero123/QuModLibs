# QuModLibs NX14（山头临时修复）
适用于网易MC_MOD开发的免费开源框架 (如需摘录部分源代码到其他同类别项目请署名原作者)。
> 该版本为临时修复分支（会在官方修复后删除），基于**QuModLibs-NX14**进行调整以适配网易山头服务器最新环境，可局部覆盖`LoaderSystem`包。

#### NX14变动内容(2025/09/13)
    - 移除过时的NX12兼容模块
    - 移除过时的CTRender扩展
    - 移除UIManager现推荐直接使用push界面管理
    - 移除不常用的Task功能
    - 移除IsThread装饰器，推荐使用线程池模块
    - getLoaderSystem函数公开访问权限
    - AutoSave列为废弃清单(未来将由其他模块替代)
    - EasyScreenNodeCls列为废弃清单(NX15中彻底删除)
    - ItemService现在是单独的模块(Items)不再是Services的子集
    - QAnimManager新增bindRAIINode 自适应绑定方案
    - 新增DataStore模块 全新的数据存储管理方案
    - 调整QuModLibs内部所有相对导入部分，更加标准化
    - Tools/QuModPurge.exe工具支持新版本同时兼容NX13
    - 摄像机运镜系统支持z轴，并调整了局部实现
    - 调整Vec3的实现，延迟评估不可变tuple的构造
    - Mini版本QuModLibs核心更新至v1.4.X
    - 合并Promise功能至当前版本
    - 其他若干小的调整和修复

## 创建项目
您可以通过以下步骤创建一个基于`QuModLibs`的网易MCMOD项目。
### 项目结构
推荐放置在 `Scripts/QuModLibs`目录下，但不是必须：
```
├── 行为包
│   └── 脚本目录
│       └── QuModLibs(库目录)
|           ├── __init__.py
|           └── ...
│       ├── __init__.py
│       ├── modMain.py
│       ├── Server.py
│       └── Client.py
```
```python
# modMain.py
# -*- coding: utf-8 -*-
from .QuModLibs.QuMod import * # 导入 QuModLibs.QuMod 的全部功能
myMod = EasyMod()              # 便捷的MOD构建类

# 服务端与客户端注册 将加载: 脚本目录/Server.py 和 脚本目录/Client.py
myMod.Server("Server")
myMod.Client("Client")
```

### 事件监听
通过`@Listen`装饰器注册事件监听。
```python
# Server/Client.py
from .QuModLibs.Server import *
# from .QuModLibs.Client import *

@Listen("OnScriptTickServer")
def OnScriptTickServer(_={}):
    print("game tick")

@Listen("OnCarriedNewItemChangedServerEvent")
def OnCarriedNewItemChangedServerEvent(args={}):
    # type: (dict) -> None
    playerId = args["playerId"] # 触发事件的玩家
    comp = serverApi.GetEngineCompFactory().CreateCommand(levelId)
    comp.SetCommand("/say 我切换了手持物品", playerId)

@DestroyFunc
def onGameClose():
    print("游戏端侧关闭时触发, 等价于Destroy")
```

### RPC通信
通过`@AllowCall`与`Call`实现服务端与客户端的通信。
#### 声明函数
所有需要远程调用的函数必须使用`@AllowCall`装饰器声明。
```python
# Client.py
@AllowCall
def testFunc():
    # 声明的函数将被登记到通信调用中，以便远程调用
    pass
```

#### 调用函数
QuMod提供了封装的`Call`函数用于跨端调用特定函数。
```python
# Server.py
# 服务端需要指定玩家Id调用特定客户端 其中 "*" 作为保留字段用于全体玩家广播
Call(playerId, "testFunc", ...args)
```

#### 批量调用
QuMod提供了封装的`MultiClientsCall`函数可用于批量发包调用。
```python
# MultiClientsCall为服务端独占功能 用于给多个玩家同时发包调用对立客户端函数
# 该方法相比for循环+Call的批量发包性能更好
MultiClientsCall([playerId1, playerId2, ...], "testFunc", ...args)
```

#### 数据包来源
通过使用`@InjectRPCPlayerId`装饰器可在被调用函数中捕获发起调用的玩家Id。
```python
# 服务端独占
from .QuModLibs.Server import *

@AllowCall
@InjectRPCPlayerId
def testFunc(playerId, ...args):
    # playerId为发起调用的玩家Id 会被InjectRPCPlayerId自动插入到第一个参数上
    pass
```
### IMP即初始化
QuMod推崇`import`即初始化的理念，推荐在功能模块加载时完成必要的初始化工作。

### Tools工具模块
`QuModLibs/Tools`提供了一组工具集，可帮助开发者快速实现某些功能，或进行项目优化。

## 更多功能
请参考`QuModLibs`官网文档、讨论群交流，或查看各模块的源代码注释。