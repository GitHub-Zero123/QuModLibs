# -*- coding: utf-8 -*-
from .Core import BaseAutoStoreCls
from ...Client import compFactory, levelId
# import mod.client.extraClientApi as clientApi

class ClientAutoStoreCls(BaseAutoStoreCls):
    __IS_CLIENT__ = True
    __GLOBAL_MODE__ = False         # 客户端全局数据(默认False, 即存档数据)

    # __VERSION__ = 1               # 数据版本(默认1), 与存档版本不符时会自动丢弃数据
    # __AUTO_SAVE_INTERVAL__ = 8.0  # 自动保存间隔(默认8秒)
    # __SAVED_FULL_NAME__ = ""      # 自定义完整Key(默认自动生成)
    # __SAVED_MOD_KEY_NAME__ = ""   # 自定义ModKey(自动添加mod名隔离)

    @classmethod
    def mLoadUserData(cls):
        configClient = compFactory.CreateConfigClient(levelId)
        savedData = configClient.GetConfigData(cls.mGetSavedFullName(), cls.__GLOBAL_MODE__)
        for k, v in cls.mUnpackClsDatas(savedData).items():
            type.__setattr__(cls, k, v)

    @classmethod
    def _mSaveUserData(cls):
        configClient = compFactory.CreateConfigClient(levelId)
        configClient.SetConfigData(cls.mGetSavedFullName(), cls.mPackClsDatas(), cls.__GLOBAL_MODE__)

    @classmethod
    def _updateOldDataCls(cls, oldDataKey):
        configClient = compFactory.CreateConfigClient(levelId)
        data = configClient.GetConfigData(oldDataKey, cls.__GLOBAL_MODE__)
        if data:
            configClient.SetConfigData(oldDataKey, {}, cls.__GLOBAL_MODE__) # 清空旧数据
        if not data or not isinstance(data, dict):
            return
        savedData = data["__data__"]    # type: dict
        for k, v in savedData.items():
            setattr(cls, k, v)