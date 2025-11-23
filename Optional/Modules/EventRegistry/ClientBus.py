# -*- coding: utf-8 -*-
from functools import wraps
from ...Systems.Loader.Client import LoaderSystem as _LoaderSystem

def _parseEventClass(func):
    return getattr(func, "func_defaults")[0].__class__

def SubscribeEvent(func):
    """ 面向对象事件监听装饰器 """
    eventCls = _parseEventClass(func)
    @wraps(func)
    def _wrapperFunc(args=None):
        return func(eventCls(args))
    _LoaderSystem.REG_STATIC_LISTEN_FUNC(eventCls.__name__, _wrapperFunc)
    return _wrapperFunc