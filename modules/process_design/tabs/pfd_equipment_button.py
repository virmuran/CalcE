# modules/process_design/tabs/pfd_equipment_button.py

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

class EquipmentButton(QPushButton):
    """自定义设备按钮，支持拖放"""
    
    equipment_dragged = Signal(str)  # 设备拖拽信号
    
    def __init__(self, equipment_type: str, equipment_info: dict, parent=None):
        super().__init__(parent)
        
        self.equipment_type = equipment_type
        self.equipment_info = equipment_info
        
        # 设置按钮大小
        self.setFixedSize(70, 70)
        
        # 设置按钮文本（显示图标和名称）
        self.setText(f"{equipment_info['icon']}\n{equipment_info['name']}")
        
        # 设置样式
        self.setToolTip(f"{equipment_info['name']} - 点击或拖拽到画布")
        
        # 设置颜色
        color = equipment_info['color']
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {color.lighter(120).name()}, stop:1 {color.name()});
                border: 2px solid {color.darker(150).name()};
                border-radius: 10px;
                font-size: 11px;
                font-weight: bold;
                color: white;
                padding: 2px;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {color.lighter(140).name()}, stop:1 {color.lighter(120).name()});
                border: 2px solid {color.lighter(200).name()};
            }}
            QPushButton:pressed {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {color.darker(120).name()}, stop:1 {color.darker(140).name()});
                border: 2px solid {color.darker(200).name()};
            }}
        """)
        
        # 设置拖拽支持
        self.setAcceptDrops(False)  # 按钮本身不接受拖放，只作为拖放源
        self.drag_start_position = None
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.position().toPoint()
        
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 开始拖拽"""
        if not (event.buttons() & Qt.LeftButton):
            return
        
        if self.drag_start_position is None:
            return
        
        # 检查是否移动了足够距离才开始拖拽
        if (event.position().toPoint() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return
        
        # 开始拖拽
        drag = QDrag(self)
        mime_data = QMimeData()
        
        # 设置拖拽数据
        mime_data.setText(f"EQUIPMENT:{self.equipment_type}")
        
        # 创建拖拽图标
        pixmap = QPixmap(70, 70)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 绘制按钮外观到拖拽图标
        color = self.equipment_info['color']
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(color.darker(150), 2))
        painter.drawRoundedRect(5, 5, 60, 60, 10, 10)
        
        # 绘制图标
        painter.setFont(QFont("Arial", 20))
        painter.drawText(QRectF(0, 10, 70, 30), Qt.AlignCenter, self.equipment_info['icon'])
        
        # 绘制名称
        painter.setFont(QFont("Arial", 9, QFont.Bold))
        painter.drawText(QRectF(0, 40, 70, 20), Qt.AlignCenter, self.equipment_info['name'])
        
        painter.end()
        
        drag.setMimeData(mime_data)
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(35, 35))  # 图标中心
        
        # 开始拖拽
        drag.exec(Qt.CopyAction | Qt.MoveAction)