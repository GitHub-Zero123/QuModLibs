# -*- coding: utf-8 -*-
import math
from .Util import Math
lambda: "By Zero123"

class Vec3(object):
    """ QuMod Vec3向量类 用于描述坐标/向量
        PS: Vec3的方法大多是自我操作并返回self的链式设计 如需产生新的对象请使用克隆方法
    """
    def __init__(self, x = 0.0, y = 0.0, z = 0.0):
        self._tuple = None      # type: tuple[float, float, float] | None
        self._needUpdate = True
        self.mX = float(x)
        self.mY = float(y)
        self.mZ = float(z)

    @property
    def x(self):
        return self.mX

    @x.setter
    def x(self, value):
        self._needUpdate = True
        self.mX = float(value)

    @property
    def y(self):
        return self.mY

    @y.setter
    def y(self, value):
        self._needUpdate = True
        self.mY = float(value)
    
    @property
    def z(self):
        return self.mZ

    @z.setter
    def z(self, value):
        self._needUpdate = True
        self.mZ = float(value)

    def getTuple(self):
        # type: () -> tuple[float, float, float]
        """ 获取元组 """
        if self._needUpdate:
            self._needUpdate = False
            self._upDate()
        return self._tuple

    def _upDate(self):
        """ 更新内部Tuple资源 """
        self._tuple = (self.x, self.y, self.z)
    
    def __getitem__(self, index):
        # type: (int) -> float
        return self.getTuple()[index]

    def __setitem__(self, index, value):
        if index >= len(self):
            raise IndexError("索引错误 {} 无效的坐标系".format(index))
        setattr(self, "xyz"[index], value)
    
    def __add__(self, other):
        if not isinstance(other, Vec3):
            raise TypeError("不支持的类型 {} 进行加法运算".format(type(other)))
        return self.copy().addVec(other)

    def __radd__(self, other):
        return self + other
    
    def __sub__(self, other):
        if not isinstance(other, Vec3):
            raise TypeError("不支持的类型 {} 进行减法运算".format(type(other)))
        return self.copy().vectorSubtraction(other)

    def __rsub__(self, other):
        return -self + other

    def __neg__(self):
        return self.copy().multiplyOf(-1.0)

    def __eq__(self, value):
        if not isinstance(value, Vec3):
            return False
        return value.getTuple() == self.getTuple()

    def __len__(self):
        return 3

    def __str__(self):
        return "<{} {}>".format(self.__class__.__name__, self.getTuple().__str__())
    
    @staticmethod
    def tupleToVec(tuple):
        # type: (tuple[float | int]) -> Vec3
        """ 将元组转换到Vec """
        return Vec3(*tuple)

    def copy(self):
        # type: () -> Vec3
        """ 拷贝一份新的Vec3对象 """
        return Vec3(self.x, self.y, self.z)
    
    def getLength(self):
        # type: () -> float
        """ 获取向量的长度 """
        return (self.x ** 2 + self.y ** 2 + self.z ** 2) ** 0.5
    
    def convertToUnitVector(self):
        # type: () -> Vec3
        """ 转换为单位向量 返回self """
        length = self.getLength()
        self.x = self.x / length
        self.y = self.y / length
        self.z = self.z / length
        return self
    
    def safeConvertToUnitVector(self):
        # type: () -> Vec3
        """ 安全转换为单位向量 返回self """
        if self.getLength() <= 0.0001:
            return self
        return self.convertToUnitVector()

    def addVec(self, nextVec3):
        # type: (Vec3) -> Vec3
        """ 向量加法运算 返回self """
        self.x += nextVec3.x
        self.y += nextVec3.y
        self.z += nextVec3.z
        return self
    
    def vectorSubtraction(self, nextVec3):
        # type: (Vec3) -> Vec3
        """ 向量减法运算 返回self """
        self.x -= nextVec3.x
        self.y -= nextVec3.y
        self.z -= nextVec3.z
        return self
    
    def addTuple(self, nextTuple):
        # type: (tuple[float, float, float]) -> Vec3
        """ 向量加法运算 使用元组 """
        return self.addVec(Vec3.tupleToVec(nextTuple))

    def multiplyOf(self, mutNumber):
        # type: (int | float) -> Vec3
        """ 向量乘法运算 返回self """
        self.x *= mutNumber
        self.y *= mutNumber
        self.z *= mutNumber
        return self

    def rotateVector(self, axis, angle):
        # type: (Vec3, float) -> Vec3
        """ 向量旋转（罗德里格斯旋转公式）
            @axis: 旋转轴(单位向量)
            @angle: 旋转角度(欧拉角，正方向与 MC yaw 旋转方向一致：绕Y轴正角度 = 面朝Z+时向左转）
            @return: self
        """
        angleRad = math.radians(angle)
        cosTheta = math.cos(angleRad)
        sin_theta = math.sin(angleRad)
        ux, uy, uz = axis.copy().convertToUnitVector()
        # 保存原始分量，避免 in-place 赋值污染（旧版 vector=self 无拷贝的 bug 修复）
        ox, oy, oz = self.x, self.y, self.z
        # 标准罗德里格斯旋转矩阵（列向量乘法 R*v），旋转方向与 MC yaw 坐标系保持一致
        self.x = (cosTheta + (1 - cosTheta) * ux * ux) * ox + ((1 - cosTheta) * ux * uy + sin_theta * uz) * oy + ((1 - cosTheta) * ux * uz - sin_theta * uy) * oz
        self.y = ((1 - cosTheta) * ux * uy - sin_theta * uz) * ox + (cosTheta + (1 - cosTheta) * uy * uy) * oy + ((1 - cosTheta) * uy * uz + sin_theta * ux) * oz
        self.z = ((1 - cosTheta) * ux * uz + sin_theta * uy) * ox + ((1 - cosTheta) * uy * uz - sin_theta * ux) * oy + (cosTheta + (1 - cosTheta) * uz * uz) * oz
        return self

    @staticmethod
    def dot(vc1, vc2):
        # type: (Vec3, Vec3) -> float
        """ 点积运算 """
        t1 = vc1.getTuple()
        t2 = vc2.getTuple()
        return sum(t1[i] * t2[i] for i in range(len(t1)))

    def vecAngle(self, otherVec):
        # type: (Vec3) -> float
        """ 向量夹角运算 计算两个向量之间的夹角 """
        dotValue = Vec3.dot(self, otherVec)
        length = self.getLength() * otherVec.getLength()
        if length <= 0.0001:
            # 未定义行为
            length = 1.0
        cosValue = max(min(dotValue / length, 1.0), -1.0)  # 避免浮点误差
        return math.degrees(math.acos(cosValue))

    def scale(self, scalar):  
        # type: (float) -> Vec3
        """ 向量缩放 在当前向量所有轴上乘以一个对应的标量 """
        self.x *= scalar
        self.y *= scalar
        self.z *= scalar
        return self

    @staticmethod
    def projectOn(withVec, otherVec):
        # type: (Vec3, Vec3) -> Vec3
        """ 计算投影向量 返回新的Vec3 """
        projLength = Vec3.dot(withVec, otherVec) / otherVec.getLength() ** 2
        return otherVec.copy().convertToUnitVector().scale(projLength)

    @staticmethod
    def cross(vc1, vc2):
        # type: (Vec3, Vec3) -> Vec3
        """ 计算叉积 返回新的 Vec3 向量 """
        x = vc1.y * vc2.z - vc1.z * vc2.y
        y = vc1.z * vc2.x - vc1.x * vc2.z
        z = vc1.x * vc2.y - vc1.y * vc2.x
        return Vec3(x, y, z)

class QBox3D:
    """ 表示一个支持旋转的简易三维盒子 用于简单的碰撞测量计算 实现便捷索敌/物理计算 """
    def __init__(self, boxSize, centerPos, rotationAxis=None, rotationAngle=0):
        # type: (Vec3, Vec3, Vec3 | None, float) -> None
        """
            @boxSize: Vec3 - 描述盒子的xyz大小
            @centerPos: Vec3 - 描述盒子的中心点位置
            @rotationAxis: Vec3 | None - 描述旋转轴心 默认为y轴
            @rotationAngle: float - 描述旋转角度(自动换算弧度)
        """
        self.center = centerPos
        self.width = boxSize.x
        self.height = boxSize.y
        self.depth = boxSize.z
        self.rotationAxis = rotationAxis or Vec3(0, 1, 0)  # 默认为绕y轴旋转
        self.rotationAngle = rotationAngle
        # 旋转之前的盒子角点
        self.corners = self.getLocalCorners()

    def posMove(self, moveVc):
        # type: (Vec3) -> QBox3D
        self.center.addVec(moveVc)
        return self

    def getScaleXYZ(self):
        # type: () -> Vec3
        """ 获取XYZ大小 """
        return Vec3(self.width, self.height, self.depth)

    def setScaleXYZ(self, newXYZ=Vec3(0, 0, 0)):
        # type: (Vec3) -> None
        """ 设置XYZ大小 """
        self.width = newXYZ.x
        self.height = newXYZ.y
        self.depth = newXYZ.z

    def setCenterPos(self, newXYZ=Vec3(0, 0, 0)):
        # type: (Vec3) -> None
        """ 设置中心位置 """
        self.center = newXYZ

    def getCenterPosRef(self):
        # type: () -> Vec3
        """ 获取中心位置的引用 """
        return self.center

    def setRot(self, rotationAngle=0, axis=None):
        # type: (float, Vec3 | None) -> None
        """ 设置旋转 当axis为None时保留当前旋转轴 """
        if axis:
            self.rotationAxis = axis
        self.rotationAngle = rotationAngle
        self.corners = self.getLocalCorners()

    def xyzMaxLength(self):
        # type: () -> float
        """ 获取盒状XYZ轴最大长度轴的值 """
        return max(self.width, self.height, self.depth)

    @staticmethod
    def createNullBox3D():
        # type: () -> QBox3D
        """ 创建空3D盒子对象 """
        return QBox3D(Vec3(0.0, 0.0, 0.0), Vec3(0.0, 0.0, 0.0))

    def getLocalCorners(self):
        """ 获取盒子的8个角点（未旋转前）"""
        halfWidth, halfHeight, halfDepth = self.width / 2.0, self.height / 2.0, self.depth / 2.0
        corners = [
            Vec3(halfWidth, halfHeight, halfDepth), Vec3(-halfWidth, halfHeight, halfDepth), 
            Vec3(-halfWidth, -halfHeight, halfDepth), Vec3(halfWidth, -halfHeight, halfDepth),
            Vec3(halfWidth, halfHeight, -halfDepth), Vec3(-halfWidth, halfHeight, -halfDepth),
            Vec3(-halfWidth, -halfHeight, -halfDepth), Vec3(halfWidth, -halfHeight, -halfDepth)
        ]
        return corners

    def getWorldCorners(self):
        # type: () -> list[Vec3]
        """ 获取盒子在世界坐标系中的8个角点(旋转后) """
        worldCorners = []
        for corner in self.corners:
            rotatedCorner = corner.copy().rotateVector(self.rotationAxis, self.rotationAngle)
            # rotatedCorner = corner.rotate(self.rotationAxis, self.rotationAngle)
            worldCorner = Vec3(self.center.x + rotatedCorner.x, self.center.y + rotatedCorner.y, self.center.z + rotatedCorner.z)
            worldCorners.append(worldCorner)
        return worldCorners

    def overlapsAABB(self, otherBox):
        # type: (QBox3D) -> bool
        """ 基于AABB算法检测两个Box3D是否重叠(不支持旋转) """
        aMin = Vec3(self.center.x - self.width / 2.0, self.center.y - self.height / 2.0, self.center.z - self.depth / 2.0)
        aMax = Vec3(self.center.x + self.width / 2.0, self.center.y + self.height / 2.0, self.center.z + self.depth / 2.0)

        bMin = Vec3(otherBox.center.x - otherBox.width / 2.0, otherBox.center.y - otherBox.height / 2.0, otherBox.center.z - otherBox.depth / 2.0)
        bMax = Vec3(otherBox.center.x + otherBox.width / 2.0, otherBox.center.y + otherBox.height / 2.0, otherBox.center.z + otherBox.depth / 2.0)
        # 检查在三个轴上的投影是否重叠
        return (aMin.x <= bMax.x and aMax.x >= bMin.x and aMin.y <= bMax.y and aMax.y >= bMin.y and aMin.z <= bMax.z and aMax.z >= bMin.z)

    def overlapsSAT(self, otherBox):
        # type: (QBox3D) -> bool
        """ 使用分离轴定理 (SAT) 进行碰撞检测，检测两个旋转后的Box3D是否重叠 """
        # 获取两个盒子的8个角点
        aCorners = self.getWorldCorners()
        bCorners = otherBox.getWorldCorners()
        # 定义需要投影的分离轴，分别是两个盒子的三个轴的法向量
        axes = [
            Vec3(1, 0, 0), Vec3(0, 1, 0), Vec3(0, 0, 1),  # self 盒子的轴
            otherBox.rotationAxis  # 可以添加更多分离轴，基于旋转的法向量
        ]
        # 对每一个轴进行投影
        for axis in axes:
            # 投影 self 的角点
            aProjections = [Vec3.dot(corner, axis) for corner in aCorners]
            aMinProj, aMaxProj = min(aProjections), max(aProjections)
            # 投影 otherBox 的角点
            bProjections = [Vec3.dot(corner, axis) for corner in bCorners]
            bMinProj, bMaxProj = min(bProjections), max(bProjections)
            # 如果在这个轴上没有重叠，则盒子不相交
            if aMaxProj < bMinProj or bMaxProj < aMinProj:
                return False  # 找到一个分离轴，说明盒子不重叠
        # 所有轴都没有找到分离轴，盒子重叠
        return True

class Vec2(Vec3):
    """ [不推荐] Vec2向量类 用于描述2D向量 继承于Vec3并抹除特定坐标轴 """
    def __init__(self, x = 0, y = 0):
        Vec3.__init__(self, x, y, 0)

    def __len__(self):
        return 2

    def _upDate(self):
        """ 更新tuple资源 """
        self._tuple = (self.x, self.y)

    @staticmethod
    def tupleToVec(tuple):
        # type: (tuple[float | int]) -> Vec2
        """ 将元组转换到Vec """
        return Vec2(*tuple)

    def copy(self):
        # type: () -> Vec2
        """ 拷贝一份新的Vec2对象 """
        return Vec2(self.x, self.y)