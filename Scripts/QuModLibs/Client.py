# -*- coding: utf-8 -*-
# 客户端端基本功能模块 为减缓IO开销 常用的功能均放置在该文件 其他功能按需导入使用
from .Math import Vec3, Vec2, QBox3D
from .Util import Unknown, InitOperation, errorPrint, _eventsRedirect, \
    ObjectConversion as __ObjectConversion
from .Systems.Loader.Client import LoaderSystem as _LoaderSystem, CustomEngineEvent
if 1 > 2:
    # 阻止补全库被真正import降低运行时开销（可通过自动化剔除工具移除）
    from .QuClientApi import extraClientApi
    from .QuClientApi.Events import Events as _EventsPrompt
import mod.client.extraClientApi as __extraClientApi
from . import IN as __IN
from .IN import ModDirName
IsServerUser = __IN.IsServerUser
""" 客户端常量_是否为房主 """
clientApi = __extraClientApi                        # type: extraClientApi
TickEvent = "OnScriptTickClient"
System = clientApi.GetSystem("Minecraft", "game")    # type: extraClientApi
compFactory = clientApi.GetEngineCompFactory()
levelId = clientApi.GetLevelId()
playerId = clientApi.GetLocalPlayerId() 
Events = _eventsRedirect                            # type: type[_EventsPrompt]

def regModLoadFinishHandler(func):
    """ 注册Mod加载完毕后触发的Handler """
    from .IN import RuntimeService
    RuntimeService._clientLoadFinish.append(func)
    return func

def creatTemporaryContainer():
    return type("TemporaryContainer",(object,),{})()

def getLoaderSystem():
    """ 获取加载器系统 """
    return _LoaderSystem.getSystem()

_loaderSystem = getLoaderSystem()

def _FORMAT_EVENET_INFO(event):
    if isinstance(event, CustomEngineEvent):
        return event
    return event if isinstance(event, str) else event.__name__

def Request(key, args=tuple(), kwargs={}, onResponse=lambda *_: None):
    # type: (str, tuple, dict, object) -> bool
    """ Request 向服务端发送请求, 与Call不同的是, 这是双向的, 可以取得返回值 """
    from .Util import RandomUid
    backKey = RandomUid()
    def _backFun(*_args, **_kwargs):
        _loaderSystem.removeCustomApi(backKey)
        return onResponse(*_args, **_kwargs)
    _loaderSystem.regCustomApi(backKey, _backFun)
    Call("__Client.Request__", playerId, key, args, kwargs, backKey)
    return True

def CallOTClient(playerId="", key="", *Args, **Kwargs):
    # type: (str, str, object, object) -> bool
    """ Call其他玩家的客户端 如: 发起组队申请 """
    Call("__CALL.CLIENT__", playerId, key, Args, Kwargs)
    return True

def ListenForEvent(eventName, parentObject=None, func=lambda: None):
    # type: (str, object, object) -> object
    return _loaderSystem.nativeListen(_FORMAT_EVENET_INFO(eventName), parentObject, func)

def UnListenForEvent(eventName, parentObject=None, func=lambda: None):
    # type: (str, object, object) -> bool
    return _loaderSystem.unNativeListen(_FORMAT_EVENET_INFO(eventName), parentObject, func)

def Listen(eventName):
    """  [装饰器] 游戏事件监听 """
    def _Listen(funObj):
        _LoaderSystem.REG_STATIC_LISTEN_FUNC(_FORMAT_EVENET_INFO(eventName), funObj)
        return funObj
    return _Listen

def DestroyFunc(func):
    """ [装饰器] 注册销毁回调函数 """
    _LoaderSystem.REG_DESTROY_CALL_FUNC(func)
    return func

def Call(apiKey="", *args, **kwargs):
    # type: (str, object, object) -> None
    """ Call请求服务端API调用 """
    return _loaderSystem.sendCall(apiKey, args, kwargs)

def CallBackKey(key=""):
    """ (向下兼容 未来可能移除)[装饰器] 用于给指定函数标记任意key值 以便被Call匹配 """
    def _CallBackKey(fun):
        _loaderSystem.regCustomApi(key, fun)
        return fun
    return _CallBackKey

def AllowCall(func):
    """ 允许调用 同等于CallBackKey 自动以当前函数名字设置参数 """
    key = func.__name__
    # key2 = "{}.{}".format(func.__module__, key)
    key2 = func.__module__ + "." + key
    key3 = key2.split(ModDirName+".", 1)[1]
    _loaderSystem.regCustomApi(key, func)
    _loaderSystem.regCustomApi(key2, func)
    _loaderSystem.regCustomApi(key3, func)
    return func

def LocalCall(funcName="", *args, **kwargs):
    """ 本地调用 执行当前端@AllowCall|@CallBackKey("...")的方法 """
    return _loaderSystem.localCall(funcName, *args, **kwargs)

class Entity(object):
    class Type:
        PLAYER = "minecraft:player"

    class HealthComp(object):
        """ 生命值组件 """
        def __init__(self, entityId):
            # type: (str) -> None
            self.mEntityId = entityId
            self.mComp = compFactory.CreateAttr(entityId)

        @property
        def Value(self):
            # type: () -> int
            return self.mComp.GetAttrValue(0)

        @property
        def Max(self):
            # type: () -> int
            return self.mComp.GetAttrMaxValue(0)

    def __init__(self, entityId):
        # type: (str) -> None
        self.mEntityId = entityId
    
    @property
    def entityId(self):
        # type: () -> str
        return self.mEntityId

    @property
    def Health(self):
        # type: () -> Entity.HealthComp
        """ 实体生命值属性 """
        return self.__class__.HealthComp(self.mEntityId)

    @property
    def Pos(self):
        # type: () -> tuple[float, float, float] | None
        return compFactory.CreatePos(self.mEntityId).GetPos()

    @property
    def Vec3Pos(self):
        # type: () -> Vec3 | None
        pos = self.Pos
        if pos is None:
            return None
        return Vec3.tupleToVec(pos)

    @property
    def Vec3FootPos(self):
        # type: () -> Vec3 | None
        pos = self.FootPos
        if pos is None:
            return None
        return Vec3.tupleToVec(pos)

    @property
    def FootPos(self):
        # type: () -> tuple[float, float, float] | None
        return compFactory.CreatePos(self.mEntityId).GetFootPos()

    @property
    def Vec2Rot(self):
        # type: () -> Vec2 | None
        rot = self.Rot
        if rot is None:
            return None
        return Vec2.tupleToVec(rot)

    @property
    def Rot(self):
        # type: () -> tuple[float, float] | None
        return compFactory.CreateRot(self.mEntityId).GetRot()

    @property
    def DirFromRot(self):
        # type: () -> tuple[float, float, float] | None
        return clientApi.GetDirFromRot(self.Rot)

    @property
    def Vec3DirFromRot(self):
        # type: () -> Vec3 | None
        rot = self.DirFromRot
        if rot is None:
            return None
        return Vec3.tupleToVec(rot)

    def checkSubstantive(self):
        # type: () -> bool
        """ 检查实体是否具有实质性(非物品/抛掷物) """
        entityTypeEnum = clientApi.GetMinecraftEnum().EntityType
        comp = compFactory.CreateEngineType(self.mEntityId)
        entityType = comp.GetEngineType()
        if entityType & entityTypeEnum.Projectile == entityTypeEnum.Projectile or entityType & entityTypeEnum.ItemEntity == entityTypeEnum.ItemEntity:
            return False
        return True

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

    def getBodyDirVec3(self):
        # type: () -> Vec3
        """ 获取基于Body方向的单位向量 """
        vc = self.Vec3DirFromRot
        vc.y = 0.0
        if vc.getLength() > 0.0:
            vc.convertToUnitVector()
        return vc

    def EntityPointDistance(self, otherEntity="", errorValue=0.0):
        # type: (str, float) -> float
        """ 获取与另外一个实体对应的脚部中心点距离(若实体异常将返回errorValue) """
        myPos = compFactory.CreatePos(self.mEntityId).GetPos()
        otherPos = compFactory.CreatePos(otherEntity).GetPos()
        if myPos is None or otherPos is None:
            return errorValue
        return Vec3.tupleToVec(myPos).vectorSubtraction(Vec3.tupleToVec(otherPos)).getLength()

    def SetRuntimeAttr(self, attrName, value):
        """ 设置运行时属性数据(根据MOD隔离) """
        comp = compFactory.CreateModAttr(self.mEntityId)
        return comp.SetAttr("{}_{}".format(ModDirName, attrName), value)

    def GetRuntimeAttr(self, attrName, nullValue=None):
        """ 获取运行时属性数据(根据MOD隔离) """
        comp = compFactory.CreateModAttr(self.mEntityId)
        return comp.GetAttr("{}_{}".format(ModDirName, attrName), nullValue)

    def getBox3D(self, useBodyRot=False):
        # type: (bool) -> QBox3D
        """ 获取该实体的三维空间盒对象 """
        footPos = self.FootPos
        if not footPos:
            return QBox3D.createNullBox3D()
        comp = compFactory.CreateCollisionBox(self.mEntityId)
        sx, sy = comp.GetSize()
        x, y, z = footPos
        return QBox3D(Vec3(sx, sy, sx), Vec3(x, y + sy * 0.5, z), None, rotationAngle = 0 if not useBodyRot else self.Rot[1])

    @property
    def Identifier(self):
        # type: () -> str
        return compFactory.CreateEngineType(self.mEntityId).GetEngineTypeStr()
    
    def GetMoLang(self, query):
        # type: (str) -> float
        """ 获取 实体节点(仅支持原版Molang) """
        comp = compFactory.CreateQueryVariable(self.mEntityId)
        return comp.GetMolangValue(query)
    
    def GetQuery(self, query):
        # type: (str) -> float
        """ 获取实体Query节点 支持原版Molang和自定义Query """
        if query.lower().startswith("query.mod."):
            return compFactory.CreateQueryVariable(self.mEntityId).Get(query)
        else:
            return self.GetMoLang(query)
    
    def SetQuery(self, query, value):
        # type: (str,float) -> bool
        """ 设置实体Query节点 仅支持自定义Query """
        comp = compFactory.CreateQueryVariable(self.mEntityId)
        return comp.Set(query, value)

# ================================================
# 因历史原因 以下功能将在未来逐步废弃 不推荐继续使用
# 替代模块: Modules.DataStore.*
# ================================================

class QuObjectConversion(__ObjectConversion):
    @staticmethod
    def getClsWithPath(path):
        # type: (str) -> object
        lastPos = path.rfind(".")
        impObj = clientApi.ImportModule((path[:lastPos]))
        return getattr(impObj, path[lastPos+1:])

class QuDataStorage:
    """ Qu数据储存管理 """
    _versionKey = "__version__"
    _dataKey = "__data__"
    _isGlobal = "__isGlobal__"
    _autoMap = {}   # type: dict[type, dict]
    _init = False

    @staticmethod
    def formatStrType(typ):
        # type: (str) -> str
        """ 格式化字符串类型 """
        if typ in ("float", "int"):
            return "number"
        elif typ in ("str", "unicode"):
            return "baseString"
        return typ

    @staticmethod
    def loadData(clsObj, data):
        # type: (type, dict) -> None
        """ 加载数据 """
        for k, v in data.items():
            try:
                newObj = QuObjectConversion.loadDumpsObject(v)
                oldType = QuDataStorage.formatStrType(QuObjectConversion.getType(getattr(clsObj, k)))
                newType = QuDataStorage.formatStrType(QuObjectConversion.getType(newObj))
                if oldType != newType:
                    print("[QuDataStorage] 新旧数据类型不一已被放弃 ('{}' != '{}')".format(newType, oldType))
                    continue
                setattr(clsObj, k, newObj)
            except Exception as e:
                print(e)
    
    @staticmethod
    def dumpsData(clsObj):
        # type: (type) -> dict
        """ 获取序列化数据 """
        return {
            k : QuObjectConversion.dumpsObject(getattr(clsObj, k)) for k in dir(clsObj) if not k.startswith("__")
        }

    @staticmethod
    def AutoSave(version = 1, isGlobal = False):
        """ 自动保存装饰器
            @version 版本控制 当版本号不同时将会抛弃当前存档数据该用新版数据 一般用于大型数据变动
            @isGlobal 是否为全局配置 False视为仅当前存档
        """
        if not QuDataStorage._init:
            QuDataStorage._init = True
            _loaderSystem._onDestroyCall_LAST.append(QuDataStorage.saveData)
        def _autoSave(cls):
            path = QuObjectConversion.getClsPathWithClass(cls)
            comp = compFactory.CreateConfigClient(clientApi.GetLevelId())
            configDict = comp.GetConfigData(path, isGlobal)
            if configDict is None:
                configDict = {}
            if configDict.get(QuDataStorage._versionKey, version) == version:
                QuDataStorage.loadData(cls, configDict.get(QuDataStorage._dataKey, {}))
            configDict[QuDataStorage._versionKey] = version
            configDict[QuDataStorage._isGlobal] = isGlobal
            if not path in QuDataStorage._autoMap:
                QuDataStorage._autoMap[path] = configDict
            return cls
        return _autoSave
    
    @staticmethod
    def saveData():
        """ 保存存档数据 """
        levelcomp = compFactory.CreateConfigClient(levelId)
        for k, v in QuDataStorage._autoMap.items():
            try:
                cls = QuObjectConversion.getClsWithPath(k)
                v[QuDataStorage._dataKey] = QuDataStorage.dumpsData(cls)
                levelcomp.SetConfigData(k, v, v.get(QuDataStorage._isGlobal, False))
            except Exception as e:
                print(e)