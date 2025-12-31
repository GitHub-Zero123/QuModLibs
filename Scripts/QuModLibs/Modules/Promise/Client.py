# -*- coding: utf-8 -*-
# import mod.client.extraClientApi as clientApi
from ...Client import compFactory, levelId
from ..EventsPool.Client import POOL_ListenForEvent, POOL_UnListenForEvent
from .Core import *
lambda: "By Tohru"

__all__ = [
    "sleepAsync",
    "waitEvent",
    "Promise",
    "asyncRunner",
]

def sleepAsync(duration):
    def executor(resolve, reject):
        comp = compFactory.CreateGame(levelId)
        comp.AddTimer(duration, resolve)
    return Promise(executor)

def requestEvent(name, callBack):
    def _callBack(data):
        return callBack(data)

    def destroy():
        POOL_UnListenForEvent(name, _callBack)

    POOL_ListenForEvent(name, _callBack)
    return destroy

def waitEvent(name, callBack, time=5.0):
    """
        等待事件触发，支持超时自动取消。
        name: 事件名
        callBack: 事件回调函数，返回True表示处理完成，返回False表示继续等待
        time: 超时时间，单位秒
        return: Promise对象
    """
    def executor(resolve, reject):
        funcRef = PromiseRef(lambda: None)

        def eventCallBack(args):
            if callBack(args):
                funcRef.value()
                resolve(args)

        def rejectHandler():
            funcRef.value()
            reject()

        funcRef.value = requestEvent(name, eventCallBack)
        comp = compFactory.CreateGame(levelId)
        comp.AddTimer(time, rejectHandler)

    return Promise(executor)