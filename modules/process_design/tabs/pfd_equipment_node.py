# modules/process_design/tabs/pfd_equipment_node.py

from typing import Any, Dict
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from .pfd_constants import EQUIPMENT_TYPES

class EquipmentNode(QGraphicsRectItem):
    """设备节点"""
    
    def __init__(self, equipment_id: str, equipment_type: str, name: str, 
                 x: float = 0, y: float = 0, parent=None):
        super().__init__(parent)
        
        self.equipment_id = equipment_id
        self.equipment_type = equipment_type
        self.name = name
        
        # 设置尺寸和位置
        self.setRect(0, 0, 120, 80)
        self.setPos(x, y)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # 设备属性
        self.properties = {
            "temperature": 25.0,  # °C
            "pressure": 101.325,  # kPa
            "volume": 1.0,  # m³
            "material": "",
            "flow_rate": 0.0,  # kg/h
            "status": "normal"
        }
        
        # 连接点
        self.connection_points = {
            "inlet": QPointF(0, 40),   # 左中
            "outlet": QPointF(120, 40),  # 右中
            "top": QPointF(60, 0),     # 上中
            "bottom": QPointF(60, 80)  # 下中
        }
        
        # 设置样式
        self.setBrush(QBrush(EQUIPMENT_TYPES.get(equipment_type, {}).get("color", QColor(200, 200, 200))))
        self.setPen(QPen(QColor(50, 50, 50), 2))
        
        # 设备图标和名称
        self.icon_text = EQUIPMENT_TYPES.get(equipment_type, {}).get("icon", "📦")
        
        # 连接线管理
        self.incoming_connections = []  # 进入该设备的连接线
        self.outgoing_connections = []  # 从该设备出发的连接线
    
    def itemChange(self, change, value):
        """处理设备变化事件"""
        if change == QGraphicsItem.ItemPositionHasChanged:
            # 设备位置改变时，更新所有相关的连接线
            self.update_connected_lines()
        
        return super().itemChange(change, value)
    
    def update_connected_lines(self):
        """更新所有与该设备相关的连接线"""
        # 更新进入该设备的连接线
        for connection in self.incoming_connections:
            if hasattr(connection, 'update_path'):
                connection.update_path()
        
        # 更新从该设备出发的连接线
        for connection in self.outgoing_connections:
            if hasattr(connection, 'update_path'):
                connection.update_path()
    
    def add_incoming_connection(self, connection):
        """添加入口连接线"""
        if connection not in self.incoming_connections:
            self.incoming_connections.append(connection)
    
    def add_outgoing_connection(self, connection):
        """添加出口连接线"""
        if connection not in self.outgoing_connections:
            self.outgoing_connections.append(connection)
    
    def remove_connection(self, connection):
        """移除连接线"""
        if connection in self.incoming_connections:
            self.incoming_connections.remove(connection)
        if connection in self.outgoing_connections:
            self.outgoing_connections.remove(connection)
    
    def boundingRect(self):
        """返回边界矩形（包含名称区域）"""
        rect = super().boundingRect()
        return rect.adjusted(0, 0, 0, 20)  # 为名称预留空间
    
    def paint(self, painter: QPainter, option, widget):
        """绘制设备"""
        # 如果被选中，绘制选中背景
        if self.isSelected():
            painter.setBrush(QBrush(QColor(200, 230, 255, 100)))
            painter.setPen(QPen(QColor(0, 100, 200), 2, Qt.DashLine))
            painter.drawRoundedRect(self.rect().adjusted(-5, -5, 5, 25), 15, 15)
        
        # 绘制设备背景
        painter.setBrush(self.brush())
        painter.setPen(self.pen())
        painter.drawRoundedRect(self.rect(), 10, 10)
        
        # 绘制设备图标
        painter.setFont(QFont("Arial", 20))
        painter.drawText(self.rect().center() - QPointF(10, 10), self.icon_text)
        
        # 绘制设备名称
        painter.setFont(QFont("Arial", 9, QFont.Bold))
        painter.setPen(QPen(QColor(0, 0, 0)))
        painter.drawText(QRectF(0, 60, 120, 20), Qt.AlignCenter, self.name)
        
        # 绘制连接点
        painter.setBrush(QBrush(QColor(0, 200, 0)))
        painter.setPen(QPen(QColor(0, 150, 0), 1))
        for point_name, point in self.connection_points.items():
            painter.drawEllipse(point, 4, 4)
    
    def get_connection_point(self, point_name: str) -> QPointF:
        """获取连接点位置（场景坐标）"""
        return self.mapToScene(self.connection_points[point_name])
    
    def update_properties(self, properties: Dict[str, Any]):
        """更新设备属性"""
        self.properties.update(properties)
        self.update()