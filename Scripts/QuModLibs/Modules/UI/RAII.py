# -*- coding: utf-8 -*-
from ...Client import *
from ...Util import QRAIIDelayed
from .EnhancedUI import (
    QEControlFuntion,
    ScreenNodeWrapper,
    LifecycleBind,
    ContextNode,
)
import weakref

class TouchPaperDoll(QEControlFuntion):
    """ 触摸纸娃娃功能封装类
        @uiNode: UI节点, 必须是ScreenNodeWrapper实例
        @parentPath: 纸娃娃所在路径
        @defaultParams: 纸娃娃默认参数, 包含初始旋转角度等(同原版接口参数)
        @touchButton: 触摸按钮路径, 默认为父节点下的touchHandler
    """
    def __init__(self, uiNode, parentPath="", defaultParams={}, touchButton=""):
        QEControlFuntion.__init__(self, uiNode, parentPath)
        self.defaultParams = defaultParams  # type: dict
        self.touchButton = touchButton
        self.lastTouchPosX = 0.0
        self.bindPcMosStartPos = None

    def getRotY(self):
        return self.defaultParams.get("init_rot_y", 0)

    def setRotY(self, rotY=0, autoUpdate=False):
        self.defaultParams["init_rot_y"] = rotY
        if autoUpdate:
            self.updateRender()

    def updateRender(self):
        self.getBaseUIControl().asNeteasePaperDoll().RenderEntity(self.defaultParams)
    
    def onCreate(self):
        QEControlFuntion.onCreate(self)
        self.updateRender()
        uiNode = self.getUiNode()
        if not self.touchButton:
            # 尝试搜索内部button
            self.touchButton = self._parentPath + "/touchHandler"
        baseUIControl = uiNode.GetBaseUIControl(self.touchButton)
        if not baseUIControl:
            return
        baseUIControl.SetTouchEnable(True)
        buttonUIControl = baseUIControl.asButton()
        buttonUIControl.AddTouchEventParams({"isSwallow":True})
        funcObject = self.touchHandler
        buttonUIControl.SetButtonTouchDownCallback(funcObject)
        buttonUIControl.SetButtonTouchUpCallback(funcObject)
        buttonUIControl.SetButtonTouchCancelCallback(funcObject)
        buttonUIControl.SetButtonTouchMoveCallback(funcObject)
        buttonUIControl.SetButtonTouchMoveInCallback(funcObject)
        buttonUIControl.SetButtonTouchMoveOutCallback(funcObject)
        buttonUIControl.SetButtonScreenExitCallback(funcObject)

    @QEControlFuntion.Listen("OnScriptTickClient")
    def pcUpdate(self):
        if not self.bindPcMosStartPos:
            return
        mPos = self.getMPos()
        if not mPos:
            return
        x = mPos[0]
        moveX = x - self.bindPcMosStartPos[0]
        if abs(moveX) <= 0.05:
            return
        self.setRotY(self.getRotY() + moveX * 1.3)
        self.bindPcMosStartPos = mPos
        self.updateRender()
    
    def getMPos(self):
        comp = compFactory.CreateActorMotion(playerId)
        return comp.GetMousePosition()

    def touchHandler(self, args={}):
        """ 水平滚动触摸处理 """
        touchEvent = args["TouchEvent"]
        if touchEvent in (0, 7, 3):
            self.bindPcMosStartPos = None
        if touchEvent in (1,):
            # 清空记录
            self.lastTouchPosX = None
            self.bindPcMosStartPos = self.getMPos()
        elif touchEvent == 4:
            # 移动面板
            newX = args["TouchPosX"]
            if self.lastTouchPosX:
                # 移动处理
                moveX = newX - self.lastTouchPosX
                self.setRotY(self.getRotY() + moveX * 1.3)
                self.updateRender()
            self.lastTouchPosX = newX
            return

class RAIIWindowESC(QRAIIDelayed):
    """ RAII窗口ESC退出绑定(适用于PUSH界面) """
    class _Binder(LifecycleBind):
        def onLoad(self, nodeSelf):
            # type: (ContextNode) -> None
            RAIIWindowESC(nodeSelf.contextNode, bindCloseFunc=nodeSelf.funObj)

    def __init__(self, uiNode, bindCloseFunc=None):
        self.bindCloseFunc = bindCloseFunc
        if not isinstance(uiNode, ScreenNodeWrapper):
            raise TypeError("uiNode must be a ScreenNodeWrapper instance")
        self.uiNodeRef = weakref.ref(uiNode)
        uiNode.addRAIIRes(self)

    @staticmethod
    def Bind():
        """ [注解] ESC按键绑定 """
        return RAIIWindowESC._Binder.creatAnnotationObj()

    def _loadResource(self):
        ListenForEvent("OnKeyPressInGame", self, self.OnKeyPressInGame)

    def _cleanup(self):
        UnListenForEvent("OnKeyPressInGame", self, self.OnKeyPressInGame)

    def OnKeyPressInGame(self, args={}):
        uiNode = self.uiNodeRef()
        if args["isDown"] != "1" or clientApi.GetTopScreen() != uiNode:
            return
        if args["key"] == "27":
            if self.bindCloseFunc:
                return self.bindCloseFunc()
            uiNode.SetRemove()