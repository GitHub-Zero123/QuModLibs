# -*- coding: utf-8 -*-
lambda: "By Zero123"

_DEFAULT = "default"

class SharedBox:
    """ 共享盒子 引用计数 """
    def __init__(self, load = lambda: None, unload = lambda: None):
        """
            @load 绑定存在引用的执行对象
            @unload 绑定无引用的执行对象
        """
        self._load = load
        self._unload = unload
        self._referenceCount = 0
        self._keySet = set()
    
    def increaseRefCount(self):
        """ 增加引用次数 """
        if self._referenceCount <= 0:
            self._load()
        self._referenceCount += 1
    
    def increaseRefCountWithKey(self, key = _DEFAULT):
        """ 基于Key值的引用计数追加 """
        if key in self._keySet:
            return
        self._keySet.add(key)
        self.increaseRefCount()
    
    def decreaseRefCount(self):
        """ 减少引用次数 """
        self._referenceCount -= 1
        if self._referenceCount == 0:
            self._unload()
        elif self._referenceCount < 0:
            self._referenceCount = 0
            raise Exception("引用次数不能为负数, 请检查是否存在逻辑问题")
    
    def decreaseRefCountWithKey(self, key = _DEFAULT):
        """ 基于Key值的引用计数减少 """
        if not key in self._keySet:
            return
        self._keySet.remove(key)
        self.decreaseRefCount()
    
    def free(self):
        self._load = lambda: None
        self._unload = lambda: None