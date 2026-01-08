# modules/process_design/tabs/pfd_material_connection.py

import math
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from .pfd_constants import MATERIAL_TYPES

class MaterialConnection(QGraphicsPathItem):
    """物料连接线"""
    
    def __init__(self, source, source_point: str,
                 target, target_point: str,
                 material_type: str = "liquid", material_name: str = ""):
        super().__init__()
        
        self.source = source
        self.source_point = source_point
        self.target = target
        self.target_point = target_point
        self.material_type = material_type
        self.material_name = material_name
        
        # 设置为可选
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # 注册连接线到设备
        self.register_to_equipment()
        
        # 设置初始路径
        self.update_path()
        
        # 设置样式
        material_color = MATERIAL_TYPES.get(material_type, {}).get("color", QColor(100, 100, 100))
        self.normal_pen = QPen(material_color, 3)
        self.selected_pen = QPen(QColor(255, 100, 0), 4)  # 选中时的橙色粗线
        
        self.setPen(self.normal_pen)
        self.setZValue(-1)  # 放在设备下面
        
        # 物料属性
        self.properties = {
            "flow_rate": 0.0,  # kg/h
            "temperature": 25.0,  # °C
            "pressure": 101.325,  # kPa
            "composition": {}  # 组成
        }
        
        # 箭头
        self.arrow_size = 10
    
    def register_to_equipment(self):
        """将连接线注册到相关设备"""
        # 添加到源设备的出口连接线列表
        self.source.add_outgoing_connection(self)
        
        # 添加到目标设备的入口连接线列表
        self.target.add_incoming_connection(self)
    
    def unregister_from_equipment(self):
        """从相关设备中注销连接线"""
        # 从源设备的出口连接线列表中移除
        if hasattr(self.source, 'remove_connection'):
            self.source.remove_connection(self)
        
        # 从目标设备的入口连接线列表中移除
        if hasattr(self.target, 'remove_connection'):
            self.target.remove_connection(self)
    
    def update_path(self):
        """更新路径"""
        path = QPainterPath()
        
        # 起点和终点
        start_point = self.source.get_connection_point(self.source_point)
        end_point = self.target.get_connection_point(self.target_point)
        
        # 创建曲线路径
        path.moveTo(start_point)
        
        # 计算控制点
        dx = end_point.x() - start_point.x()
        dy = end_point.y() - start_point.y()
        
        # 创建带控制点的曲线
        ctrl1 = QPointF(start_point.x() + dx * 0.3, start_point.y())
        ctrl2 = QPointF(end_point.x() - dx * 0.3, end_point.y())
        
        path.cubicTo(ctrl1, ctrl2, end_point)
        
        self.setPath(path)
    
    def paint(self, painter: QPainter, option, widget):
        """绘制连接线"""
        # 根据是否被选中使用不同的画笔
        if self.isSelected():
            painter.setPen(self.selected_pen)
        else:
            painter.setPen(self.normal_pen)
            
        painter.drawPath(self.path())
        
        # 绘制箭头
        path = self.path()
        length = path.length()
        if length > 0:
            # 在路径的90%处绘制箭头
            percent = 0.9
            point = path.pointAtPercent(percent)
            
            # 计算切线方向
            if percent > 0.01:
                prev_point = path.pointAtPercent(percent - 0.01)
                dx = point.x() - prev_point.x()
                dy = point.y() - prev_point.y()
            else:
                next_point = path.pointAtPercent(percent + 0.01)
                dx = next_point.x() - point.x()
                dy = next_point.y() - point.y()
            
            # 归一化方向向量
            length_dir = math.sqrt(dx*dx + dy*dy)
            if length_dir > 0:
                dx /= length_dir
                dy /= length_dir
                
                # 箭头两个侧边的方向
                left_dx = -dy
                left_dy = dx
                right_dx = dy
                right_dy = -dx
                
                # 计算箭头点
                arrow_tip = QPointF(
                    point.x() - self.arrow_size * dx,
                    point.y() - self.arrow_size * dy
                )
                arrow_left = QPointF(
                    arrow_tip.x() + self.arrow_size * 0.5 * left_dx,
                    arrow_tip.y() + self.arrow_size * 0.5 * left_dy
                )
                arrow_right = QPointF(
                    arrow_tip.x() + self.arrow_size * 0.5 * right_dx,
                    arrow_tip.y() + self.arrow_size * 0.5 * right_dy
                )
                
                # 绘制箭头多边形
                if self.isSelected():
                    painter.setBrush(QColor(255, 100, 0))  # 选中时橙色填充
                else:
                    painter.setBrush(self.normal_pen.color())
                    
                painter.drawPolygon(QPolygonF([point, arrow_left, arrow_right]))
        
        # 绘制物料名称
        if self.material_name:
            point = path.pointAtPercent(0.5)
            painter.setPen(QPen(QColor(0, 0, 0)))
            painter.setFont(QFont("Arial", 8))
            painter.drawText(point, self.material_name)
    
    def mousePressEvent(self, event):
        """鼠标按下事件 - 确保连接线可以被选中"""
        # 设置选中状态
        self.setSelected(True)
        super().mousePressEvent(event)