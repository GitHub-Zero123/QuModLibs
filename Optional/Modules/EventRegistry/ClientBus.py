# -*- coding: utf-8 -*-
from functools import wraps
from ...Systems.Loader.Client import LoaderSystem as _LoaderSystem
if 1 > 2:
    from . import Events as _EventsIMP

__all__ = ["SubscribeEvent", "GameEvents"]

class _EVENT_JMP(object):
    def __init__(self, args=None):
        self.mArgs = args or dict()

    def __getattr__(self, name):
        return self.mArgs.get(name, None)

    def __setattr__(self, key, value):
        if key == "mArgs":
            object.__setattr__(self, key, value)
            return
        self.mArgs[key] = value

class _ENGINE_ATTR_JMP(object):
    def __getattr__(cls, item):
        newType = type(item, (_EVENT_JMP,), {})
        newType.__module__ = cls.__module__
        newType.__name__ = item
        return newType

GameEvents = _ENGINE_ATTR_JMP()    # type: _EventsIMP

def _parseEventClass(func):
    return getattr(func, "func_defaults")[0].__class__

def SubscribeEvent(func):
    """ 面向对象事件监听装饰器 """
    eventCls = _parseEventClass(func)
    @wraps(func)
    def _wrapperFunc(args=None):
        return func(eventCls(args))
    _LoaderSystem.REG_STATIC_LISTEN_FUNC(eventCls.__name__, _wrapperFunc)
    return func