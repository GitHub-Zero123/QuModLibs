# -*- coding: utf-8 -*-
from mod.client.ui.screenNode import ScreenNode
import mod.client.extraClientApi as clientApi
from .Util import (
    ModDirName,
    RandomUid,
    ExceptionHandling,
    getObjectPathName,
    TRY_EXEC_FUN,
    QDRAIIEnv
)
from .Client import ListenForEvent
lambda: "By Zero123"

__all__ = [
    "ScreenNodeWrapper"
]

_BASE_SCREEN_NODE_CLS = ScreenNode

class ScreenNodeWrapper(_BASE_SCREEN_NODE_CLS, QDRAIIEnv):
    """ 封装界面节点类 按类隔离命名空间与Key名 """
    _AUTO_REGISTER_UI_MAP = {}
    _INIT_UI_LOAD_FINISH = False

    def __init__(self, namespace, name, param):
        _BASE_SCREEN_NODE_CLS.__init__(self, namespace, name, param)
        QDRAIIEnv.__init__(self)
        self._raiiCleanState = False

    @staticmethod
    def _AUTO_REGISTER_UI_FINISH_EVENT(_={}):
        ScreenNodeWrapper._INIT_UI_LOAD_FINISH = True
        for func in ScreenNodeWrapper._AUTO_REGISTER_UI_MAP.values():
            TRY_EXEC_FUN(func)

    @staticmethod
    def autoRegister(uiScreenDef):
        """ 自动注册装饰器 """
        def _autoRegister(cls):
            uiCls = cls # type: type[ScreenNodeWrapper]
            key = uiCls._createUiKey()
            if not ScreenNodeWrapper._AUTO_REGISTER_UI_MAP:
                # 初始化内部监听管理
                ListenForEvent("UiInitFinished", ScreenNodeWrapper, ScreenNodeWrapper._AUTO_REGISTER_UI_FINISH_EVENT)
            if not key in ScreenNodeWrapper._AUTO_REGISTER_UI_MAP:
                ScreenNodeWrapper._AUTO_REGISTER_UI_MAP[key] = lambda: uiCls.registerUI(uiScreenDef=uiScreenDef)
            return cls
        return _autoRegister

    @classmethod
    def createUI(cls, uiKey="", createParams=None, isHud=1):
        """ 创建HUD_UI """
        if 1 > 2:
            return cls.getUiNode()
        if not isHud is None:
            createParams = createParams or dict()
            createParams["isHud"] = isHud
        return clientApi.CreateUI(ModDirName, cls._createUiKey(uiKey), createParams)

    @classmethod
    def pushScreen(cls, uiKey="", createParams=None):
        """ 使用栈管理的方式创建UI """
        if 1 > 2:
            return cls.getUiNode()
        return clientApi.PushScreen(ModDirName, cls._createUiKey(uiKey), createParams)

    @staticmethod
    def popScreen():
        """ 关闭POP界面(栈顶) """
        return clientApi.PopScreen()

    @staticmethod
    def nativePopTopUI():
        """ 弹出UI栈顶的UI """
        return clientApi.PopTopUI()

    @classmethod
    def removeClsUI(cls, uiKey=""):
        """ 删除用户的当前UI实例 """
        uiNode = cls.getUiNode(uiKey)
        if uiNode:
            uiNode.SetRemove()
            return True
        return False

    @classmethod
    def registerUI(cls, uiKey="", uiScreenDef=None):
        return clientApi.RegisterUI(ModDirName, cls._createUiKey(uiKey), getObjectPathName(cls), uiScreenDef)

    @classmethod
    def getUiNode(cls, uiKey=""):
        if 1 > 2:
            return cls("none", "none", {})
        uiNode = clientApi.GetUI(ModDirName, cls._createUiKey(uiKey))
        if uiNode:
            return uiNode
        return None

    @classmethod
    def _createUiKey(cls, uiKey=""):
        return "{}_{}_{}".format(cls.__name__, hash(getObjectPathName(cls)), uiKey)

    def setButtonClickHandler(self, buttonPath, onClick=lambda: None):
        """ 封装的设置按钮点击回调 """
        def creatFun(func):
            def _onClick(*_):
                return func()
            return _onClick
        baseUIControl = self.GetBaseUIControl(buttonPath)
        baseUIControl.SetTouchEnable(True)
        buttonUIControl = baseUIControl.asButton()
        buttonUIControl.AddTouchEventParams({"isSwallow":True})
        buttonUIControl.SetButtonTouchUpCallback(creatFun(onClick))
        return self

    def bindButtonClickHandler(self, buttonPath):
        """ 封装的装饰器绑定按钮函数调用 """
        def _wrapper(func):
            self.setButtonClickHandler(buttonPath, func)
            return func
        return _wrapper

    def Create(self):
        """ UI_CREATE方法 请确保重写后调用父级 """
        # RAII资源管理初始化
        self.setDRAIIEnvState(True)
        self.loadALLDRAIIRes()
    
    def Update(self):
        pass

    def Destroy(self):
        """ UI_DESTROY方法 请确保重写后调用父级 """
        # RAII资源管理析构
        if self._draiiEnvState:
            self.setDRAIIEnvState(False)
            self._raiiCleanState = True
            self.freeALLRAIIRes()
            self._raiiCleanState = False
