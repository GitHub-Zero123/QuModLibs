# -*- coding: utf-8 -*-
import threading
import Queue

class QThreadPool:
    def __init__(self, maxThreadCount=2, daemon=None):
        # type: (int, bool | None) -> None
        self.maxThreadCount = maxThreadCount
        self.daemon = daemon
        self._taskQueue = Queue.Queue(maxsize=0)
        self._threadList = []   # type: list[threading.Thread]
        self._closed = False

    def start(self):
        """ 启用线程并返回自己的实例 """
        if len(self._threadList) <= 0:
            self._createThread(self.maxThreadCount)
        return self

    def _createThread(self, count=1):
        for _ in range(count):
            thread = threading.Thread(target=self._threadLoop)
            if self.daemon:
                thread.daemon = True
            self._threadList.append(thread)
            thread.start()

    def _threadLoop(self):
        while 1:
            item = self._taskQueue.get()
            if item is None:
                break
            elif self._closed:
                break
            try:
                item()
            except Exception:
                import traceback
                traceback.print_exc()

    def addTask(self, func=lambda: None):
        """ 添加执行任务 """
        if func is None:
            raise ValueError("func 不能为 None")
        self._taskQueue.put(func)

    def free(self, autoJoin=False):
        """ 释放线程池，请勿重复使用已经释放的线程池 """
        if self._closed:
            return
        threadCount = len(self._threadList)
        self._closed = True
        for _ in range(threadCount):
            self._taskQueue.put(None)
        if autoJoin:
            self.join()

    def join(self):
        """ 等待所有线程结束 """
        for thread in self._threadList:
            thread.join()