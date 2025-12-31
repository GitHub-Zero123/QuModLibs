# -*- coding: utf-8 -*-
from .Core import BaseAutoStoreCls
from ...Server import compFactory, levelId
# import mod.server.extraServerApi as serverApi

class ServerAutoStoreCls(BaseAutoStoreCls):
    __IS_CLIENT__ = False

    # __VERSION__ = 1               # 数据版本(默认1), 与存档版本不符时会自动丢弃数据
    # __AUTO_SAVE_INTERVAL__ = 8.0  # 自动保存间隔(默认8秒)
    # __SAVED_FULL_NAME__ = ""      # 自定义完整Key(默认自动生成)
    # __SAVED_MOD_KEY_NAME__ = ""   # 自定义ModKey(自动添加mod名隔离)

    @classmethod
    def mLoadUserData(cls):
        extraData = compFactory.CreateExtraData(levelId)
        savedData = extraData.GetExtraData(cls.mGetSavedFullName())
        for k, v in cls.mUnpackClsDatas(savedData).items():
            type.__setattr__(cls, k, v)

    @classmethod
    def _mSaveUserData(cls):
        extraData = compFactory.CreateExtraData(levelId)
        extraData.SetExtraData(cls.mGetSavedFullName(), cls.mPackClsDatas())

    @classmethod
    def _updateOldDataCls(cls, oldDataKey):
        extraData = compFactory.CreateExtraData(levelId)
        data = extraData.GetExtraData(oldDataKey)
        if data:
            extraData.SetExtraData(oldDataKey, {}) # 清空旧数据
        if not data or not isinstance(data, dict):
            return
        savedData = data["__data__"]    # type: dict
        for k, v in savedData.items():
            setattr(cls, k, v)