# -*- coding: utf-8 -*-
from .Math import Vec3, Vec2, QBox3D
from .IN import ModDirName
import mod.server.extraServerApi as serverApi

TickEvent = "OnScriptTickServer"
levelId = serverApi.GetLevelId()
System = serverApi.GetSystem("Minecraft", "game")

def getOwnerPlayerId():
    # type: () -> str | None
    """ 获取房主玩家ID 如果存在(联机大厅/网络游戏中不存在房主玩家) """
    from .IN import RuntimeService
    return RuntimeService._envPlayerId

def regModLoadFinishHandler(func):
    """ 注册Mod加载完毕后触发的Handler """
    from .IN import RuntimeService
    RuntimeService._serverLoadFinish.append(func)
    return func

def DestroyEntity(entityId):
    """ 注销特定实体 """
    return System.DestroyEntity(entityId)

def getLoaderSystem():
    """ 获取加载器系统 """
    from .Systems.Loader.Server import LoaderSystem
    return LoaderSystem.getSystem()

_loaderSystem = getLoaderSystem()

def ListenForEvent(eventName, parentObject=None, func=lambda: None):
    # type: (str | object, object, object) -> object
    """ 动态事件监听 """
    eventName = eventName if isinstance(eventName, str) else eventName.__name__
    return _loaderSystem.nativeListen(eventName, parentObject, func)

def UnListenForEvent(eventName, parentObject=None, func=lambda: None):
    # type: (str | object, object, object) -> bool
    """ 动态事件监听销毁 """
    eventName = eventName if isinstance(eventName, str) else eventName.__name__
    return _loaderSystem.unNativeListen(eventName, parentObject, func)

def Listen(eventName=""):
    """  [装饰器] 游戏事件监听 """
    eventName = eventName if isinstance(eventName, str) else eventName.__name__
    from .Systems.Loader.Server import LoaderSystem
    def _Listen(funObj):
        LoaderSystem.REG_STATIC_LISTEN_FUNC(eventName, funObj)
        return funObj
    return _Listen

def DestroyFunc(func):
    """ [装饰器] 注册销毁回调函数 """
    from .Systems.Loader.Server import LoaderSystem
    LoaderSystem.REG_DESTROY_CALL_FUNC(func)
    return func

def Call(playerId, apiKey="", *args, **kwargs):
    # type: (str, str, object, object) -> None
    """ Call请求对立端API调用 当playerId为*时代表全体玩家 """
    return _loaderSystem.sendCall(playerId, apiKey, args, kwargs)

def MultiClientsCall(playerIdList=[], key="", *args, **kwargs):
    # type: (list[str], str, object, object) -> None
    """ 多玩家客户端合批Call请求 """
    return _loaderSystem.sendMultiClientsCall(playerIdList, key, args, kwargs)

def CallBackKey(key=""):
    """ (向下兼容 未来可能移除)[装饰器] 用于给指定函数标记任意key值 以便被Call匹配 """
    def _CallBackKey(fun):
        _loaderSystem.regCustomApi(key, fun)
        return fun
    return _CallBackKey

def AllowCall(func):
    """ 允许调用 同等于CallBackKey 自动以当前函数名字设置参数 """
    key = func.__name__
    key2 = "{}.{}".format(func.__module__, key)
    key3 = key2.split(ModDirName+".", 1)[1]
    _loaderSystem.regCustomApi(key, func)
    _loaderSystem.regCustomApi(key2, func)
    _loaderSystem.regCustomApi(key3, func)
    return func

def InjectRPCPlayerId(func):
    """ [装饰器] 注入玩家ID接收，可搭配@AllowCall使用（注意先后顺序） """
    def _wrapper(*args, **kwargs):
        return func(_loaderSystem.rpcPlayerId, *args, **kwargs)
    _wrapper.__name__ = func.__name__
    return _wrapper

def InjectHttpPlayerId(func):
    """ [向下兼容] 注入玩家ID接收 可搭配@AllowCall使用（注意先后顺序） """
    return InjectRPCPlayerId(func)

def LocalCall(funcName="", *args, **kwargs):
    """ 本地调用 执行当前端@AllowCall|@CallBackKey("...")的方法 """
    return _loaderSystem.localCall(funcName, *args, **kwargs)

class Entity(object):
    __slots__ = ("entityId","PropertySettingsDic",)
    ErrorSet = "[Error] 不支持的属性设置"

    class Type:
        PLAYER = "minecraft:player"

    class HealthComp(object):
        """ 生命值组件 """
        def __init__(self,entityId):
            # type: (str) -> None
            self.entityId = entityId
            self.PropertySettingsDic = {
                "Value":self.SetValue,
                "Max":self.SetMax
            }

        def __setattr__(self, Name, Value):
            """ 属性设置处理 """
            if Name in Entity.__slots__:
                return object.__setattr__(self, Name, Value)
            elif Name in self.PropertySettingsDic:
                Fun = self.PropertySettingsDic[Name]
                return Fun(Value)
            else:
                print(Entity.ErrorSet)
                return None

        def SetValue(self,Value):
            """ 设置Value值 """
            comp = serverApi.GetEngineCompFactory().CreateAttr(self.entityId)
            return comp.SetAttrValue(0,Value)

        def SetMax(self,Value):
            """ 设置Max值 """
            comp = serverApi.GetEngineCompFactory().CreateAttr(self.entityId)
            return comp.SetAttrMaxValue(0,Value)

        @property
        def Value(self):
            # type: () -> int
            comp = serverApi.GetEngineCompFactory().CreateAttr(self.entityId)
            return comp.GetAttrValue(0)

        @property
        def Max(self):
            # type: () -> int
            comp = serverApi.GetEngineCompFactory().CreateAttr(self.entityId)
            return comp.GetAttrMaxValue(0)
    
    @staticmethod
    def CreateEngineEntityByTypeStr(engineTypeStr, pos, rot, dimensionId = 0, isNpc = False):
        # type: (str, tuple[float], tuple[float], int, bool) -> str
        """ 服务端系统接口 创建微软生物 """
        return System.CreateEngineEntityByTypeStr(engineTypeStr, pos, rot, dimensionId, isNpc)
    
    def __init__(self, __entityId):
        # type: (str) -> None
        self.entityId = __entityId
        self.PropertySettingsDic = {
            "Pos":self.__SetPos,
            "FootPos":self.__SetPos,
            "Rot":self.__SetRot,
        }

    def __setattr__(self, Name, Value):
        """ 属性设置处理 """
        if Name in Entity.__slots__:
            return object.__setattr__(self, Name, Value)
        elif Name in self.PropertySettingsDic:
            Fun = self.PropertySettingsDic[Name]
            return Fun(Value)
        else:
            print(Entity.ErrorSet)
            return None

    def EntityPointDistance(self, otherEntity="", errorValue=0.0):
        # type: (str, float) -> float
        """ 获取与另外一个实体对应的脚部中心点距离(若实体异常将返回errorValue) """
        myPos = serverApi.GetEngineCompFactory().CreatePos(self.entityId).GetPos()
        otherPos = serverApi.GetEngineCompFactory().CreatePos(otherEntity).GetPos()
        if myPos is None or otherPos is None:
            return errorValue
        return Vec3.tupleToVec(myPos).vectorSubtraction(Vec3.tupleToVec(otherPos)).getLength()

    def EntityCenterPointDistance(self, otherEntity="", errorValue=0.0):
        # type: (str, float) -> float
        """ 获取与另外一个实体的中心点距离(若实体异常将返回errorValue) """
        myPos = serverApi.GetEngineCompFactory().CreatePos(self.entityId).GetPos()
        otherPos = serverApi.GetEngineCompFactory().CreatePos(otherEntity).GetPos()
        if myPos is None or otherPos is None:
            return errorValue
        myVec = Vec3.tupleToVec(myPos)
        otherVec = Vec3.tupleToVec(otherPos)
        comp = serverApi.GetEngineCompFactory().CreateCollisionBox(self.entityId)
        mySize = comp.GetSize()
        comp = serverApi.GetEngineCompFactory().CreateCollisionBox(otherEntity)
        otherSize = comp.GetSize()
        myVec.y -= mySize[1] * 0.5
        otherVec.y -= otherSize[1] * 0.5
        return myVec.vectorSubtraction(otherVec).getLength()

    def LookAt(self, otherPos=(0, 0, 0), minTime=2.0, maxTime=3.0, reject=True):
        comp = serverApi.GetEngineCompFactory().CreateRot(self.entityId)
        comp.SetEntityLookAtPos(otherPos, minTime, maxTime, reject)

    def getBox3D(self, useBodyRot=False):
        # type: (bool) -> QBox3D
        """ 获取该实体的三维空间盒对象 """
        footPos = self.FootPos
        if not footPos:
            return QBox3D.createNullBox3D()
        comp = serverApi.GetEngineCompFactory().CreateCollisionBox(self.entityId)
        sx, sy = comp.GetSize()
        x, y, z = footPos
        return QBox3D(Vec3(sx, sy, sx), Vec3(x, y + sy * 0.5, z), None, rotationAngle = 0 if not useBodyRot else self.Rot[1])

    def callEvent(self, eventName):
        # type: (str) -> bool
        """ 触发JSON中特定的事件定义 """
        comp = serverApi.GetEngineCompFactory().CreateEntityEvent(self.entityId)
        return comp.TriggerCustomEvent(self.entityId, eventName)

    def getComponents(self):
        # type: () -> dict[str, object]
        """ 获取实体持有的运行时JSON组件 """
        comp = serverApi.GetEngineCompFactory().CreateEntityEvent(self.entityId)
        return comp.GetComponents()

    def removeComponent(self, compName):
        # type: (str) -> bool
        """ 移除特定的JSON组件 """
        comp = serverApi.GetEngineCompFactory().CreateEntityEvent(self.entityId)
        return comp.RemoveActorComponent(compName)

    def addComponent(self, compName, data):
        # type: (str, str | dict) -> bool
        """ 添加特定的JSON组件及参数 """
        if isinstance(data, dict):
            from json import dumps
            data = dumps(data)
        comp = serverApi.GetEngineCompFactory().CreateEntityEvent(self.entityId)
        return comp.AddActorComponent(compName, data)

    def getBlockControlAi(self):
        # type: () -> bool
        """ 获取生物AI是否被屏蔽 """
        comp = serverApi.GetEngineCompFactory().CreateControlAi(self.entityId)
        return comp.GetBlockControlAi()

    def setBlockControlAi(self, isBlock, freezeAnim=False):
        # type: (bool, bool) -> bool
        """ 设置生物AI是否被屏蔽 """
        comp = serverApi.GetEngineCompFactory().CreateControlAi(self.entityId)
        return comp.SetBlockControlAi(isBlock, freezeAnim)

    def SetMarkVariant(self, value=1):
        # type: (int | float) -> bool
        """ 设置对应JSON组件的MarkVariant值 对应query.mark_variant(底层同步) """
        comp = serverApi.GetEngineCompFactory().CreateEntityDefinitions(self.entityId)
        return comp.SetMarkVariant(value)

    def SetVariant(self, value=1):
        # type: (int | float) -> bool
        """ 设置对应JSON组件的Variant值 对应query.variant(底层同步) """
        comp = serverApi.GetEngineCompFactory().CreateEntityDefinitions(self.entityId)
        return comp.SetVariant(value)

    def GetAttackTarget(self):
        # type: () -> str
        """ 获取攻击目标 """
        comp = serverApi.GetEngineCompFactory().CreateAction(self.entityId)
        return comp.GetAttackTarget()

    def SetAttackTarget(self, targetId=None, autoResetAttackTarget=True):
        # type: (str | None, bool) -> bool
        """ 设置攻击目标 """
        comp = serverApi.GetEngineCompFactory().CreateAction(self.entityId)
        if autoResetAttackTarget and self.GetAttackTarget() != targetId:
            self.ResetAttackTarget()
        if targetId:
            return comp.SetAttackTarget(targetId)

    def ResetAttackTarget(self):
        # type: () -> bool
        """ 重置攻击目标 """
        comp = serverApi.GetEngineCompFactory().CreateAction(self.entityId)
        return comp.ResetAttackTarget()

    def GetMotionComp(self):
        """ 获取移动向量管理组件 """
        return serverApi.GetEngineCompFactory().CreateActorMotion(self.entityId)

    def SetRuntimeAttr(self, attrName, value):
        """ 设置运行时属性数据(根据MOD隔离并同步客户端) """
        comp = serverApi.GetEngineCompFactory().CreateModAttr(self.entityId)
        return comp.SetAttr("{}_{}".format(ModDirName, attrName), value)

    def GetRuntimeAttr(self, attrName, nullValue=None):
        """ 获取运行时属性数据(根据MOD隔离) """
        comp = serverApi.GetEngineCompFactory().CreateModAttr(self.entityId)
        return comp.GetAttr("{}_{}".format(ModDirName, attrName), nullValue)

    def checkSubstantive(self):
        # type: () -> bool
        """ 检查实体是否具有实质性(非物品/抛掷物) """
        entityTypeEnum = serverApi.GetMinecraftEnum().EntityType
        comp = serverApi.GetEngineCompFactory().CreateEngineType(self.entityId)
        entityType = comp.GetEngineType()
        if entityType & entityTypeEnum.Projectile == entityTypeEnum.Projectile or entityType & entityTypeEnum.ItemEntity == entityTypeEnum.ItemEntity:
            return False
        return True

    def getBodyDirVec3(self):
        # type: () -> Vec3
        """ 获取基于Body方向的单位向量 """
        vc = self.Vec3DirFromRot
        vc.y = 0.0
        if vc.getLength() > 0.0:
            vc.convertToUnitVector()
        return vc

    def convertToWorldVec3(self, absVec):
        # type: (Vec3) -> Vec3
        """ 基于当前实体转换一个相对向量到世界向量 """
        axis = Vec3(0, 1, 0)
        f = self.getBodyDirVec3()
        l = f.copy().rotateVector(axis, -90)
        worldVec3 = f.multiplyOf(absVec.z).addVec(l.multiplyOf(absVec.x))
        if worldVec3.getLength() > 0.0:
            worldVec3.convertToUnitVector()
            worldVec3.multiplyOf(Vec3(absVec.x, 0.0, absVec.z).getLength())
        worldVec3.y = absVec.y
        return worldVec3

    @property
    def Health(self):
        # type: () -> Entity.HealthComp
        """ 实体生命值属性 """
        return self.__class__.HealthComp(self.entityId)
    
    @property
    def Pos(self):
        # type: () -> tuple[float,float,float]  | None
        return serverApi.GetEngineCompFactory().CreatePos(self.entityId).GetPos()

    @property
    def Vec3Pos(self):
        # type: () -> Vec3 | None
        """ 获取Vec3坐标 失败则返回None """
        pos = self.Pos
        if pos is None:
            return None
        return Vec3.tupleToVec(pos)

    @property
    def IsPlayer(self):
        # type: () -> bool
        """ 判断目标是不是玩家单位 """
        return self.Identifier == "minecraft:player"

    @property
    def Vec3FootPos(self):
        # type: () -> Vec3 | None
        """ 获取Vec3脚下坐标 失败则返回None """
        pos = self.FootPos
        if pos is None:
            return None
        return Vec3.tupleToVec(pos)

    @property
    def FootPos(self):
        # type: () -> tuple[float,float,float]  | None
        return serverApi.GetEngineCompFactory().CreatePos(self.entityId).GetFootPos()

    @property
    def Rot(self):
        # type: () -> tuple[float,float]  | None
        return serverApi.GetEngineCompFactory().CreateRot(self.entityId).GetRot()

    @property
    def Vec2Rot(self):
        # type: () -> Vec2 | None
        """ 获取Vec2旋转角度 失败则返回None """
        rot = self.Rot
        if rot is None:
            return None
        return Vec2.tupleToVec(rot)

    @property
    def Identifier(self):
        # type: () -> str
        return serverApi.GetEngineCompFactory().CreateEngineType(self.entityId).GetEngineTypeStr()

    @property
    def Dm(self):
        # type: () -> int
        return serverApi.GetEngineCompFactory().CreateDimension(self.entityId).GetEntityDimensionId()
    
    @property
    def DirFromRot(self):
        # type: () -> tuple[float,float,float]  | None
        return serverApi.GetDirFromRot(self.Rot)

    @property
    def Vec3DirFromRot(self):
        # type: () -> Vec3 | None
        rot = self.DirFromRot
        if rot is None:
            return None
        return Vec3.tupleToVec(rot)
    
    @property
    def DimensionId(self):
        # type: () -> int
        return self.Dm
    
    def __SetPos(self,Value):
        # type: (tuple[float, float, float] | Vec3) -> bool
        if Value and isinstance(Value, Vec3):
            Value = Value.getTuple()
        return serverApi.GetEngineCompFactory().CreatePos(self.entityId).SetPos(Value)

    def __SetRot(self,Value):
        # type: (tuple[float, float] | Vec2) -> bool
        if Value and isinstance(Value, Vec2):
            Value = Value.getTuple()
        return serverApi.GetEngineCompFactory().CreateRot(self.entityId).SetRot(Value)
    
    def Destroy(self):
        """ 注销 销毁实体 """
        return DestroyEntity(self.entityId)
    
    def Kill(self):
        """ 杀死实体 """
        return serverApi.GetEngineCompFactory().CreateGame(levelId).KillEntity(self.entityId)
    
    def exeCmd(self, cmd):
        # type: (str) -> bool
        """ 使实体执行命令 """
        return serverApi.GetEngineCompFactory().CreateCommand(levelId).SetCommand(cmd, self.entityId)

    def getNearPlayer(self):
        # type: () -> str | None
        """ 获取任意一个最近的玩家单位(渲染范围内) 可能为None """
        playerList = serverApi.GetEngineCompFactory().CreatePlayer(self.entityId).GetRelevantPlayer([])
        if playerList:
            return playerList[0]
        return None