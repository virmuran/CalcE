# modules/process_design/tabs/process_flow_diagram_tab.py

import sys
import os
import math
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from ..data.data_models import UnifiedEquipment
from .equipment_id_generator import EquipmentIDGenerator

try:
    from .equipment_dialogs import EquipmentDialog, EquipmentIDGenerator
except ImportError:
    from ..tabs.equipment_dialogs import EquipmentDialog, EquipmentIDGenerator

# 设备类型定义
EQUIPMENT_TYPE_DETAILED_MAPPING = {
    "vessel": {
        "pfd_type": "vessel",
        "inventory_type": "T 储罐",
        "icon": "📦",
        "color": QColor(100, 150, 200),
        "default_properties": {
            "capacity": "储罐",
            "material": "碳钢",
            "dynamic": "静设备"
        }
    },
    "pump": {
        "pfd_type": "pump", 
        "inventory_type": "P 泵类",
        "icon": "🔧",
        "color": QColor(150, 100, 200),
        "default_properties": {
            "capacity": "输送",
            "material": "不锈钢",
            "dynamic": "动设备",
            "single_power": 7.5,
            "total_power": 7.5
        }
    },
    "reactor": {
        "pfd_type": "reactor",
        "inventory_type": "R 反应器",
        "icon": "⚗️",
        "color": QColor(200, 100, 100),
        "default_properties": {
            "capacity": "反应",
            "material": "不锈钢",
            "dynamic": "静设备"
        }
    },
    "heat_exchanger": {
        "pfd_type": "heat_exchanger",
        "inventory_type": "E 换热设备类",
        "icon": "🔥",
        "color": QColor(200, 150, 50),
        "default_properties": {
            "capacity": "换热",
            "material": "不锈钢",
            "dynamic": "静设备"
        }
    },
    "column": {
        "pfd_type": "column",
        "inventory_type": "C 塔器",
        "icon": "🗼",
        "color": QColor(100, 200, 150),
        "default_properties": {
            "capacity": "分离",
            "material": "不锈钢",
            "dynamic": "静设备"
        }
    },
    "valve": {
        "pfd_type": "valve",
        "inventory_type": "其他",
        "icon": "🚰",
        "color": QColor(150, 200, 100),
        "default_properties": {
            "capacity": "控制",
            "material": "铸钢",
            "dynamic": "静设备"
        }
    },
    "filter": {
        "pfd_type": "filter",
        "inventory_type": "S 分离设备类",
        "icon": "🧹",
        "color": QColor(100, 200, 200),
        "default_properties": {
            "capacity": "过滤",
            "material": "不锈钢",
            "dynamic": "静设备"
        }
    },
    "mixer": {
        "pfd_type": "mixer",
        "inventory_type": "A 搅拌设备类",
        "icon": "🌀",
        "color": QColor(200, 100, 150),
        "default_properties": {
            "capacity": "混合",
            "material": "不锈钢",
            "dynamic": "动设备",
            "single_power": 5.5,
            "total_power": 5.5
        }
    },
    "separator": {
        "pfd_type": "separator",
        "inventory_type": "S 分离设备类",
        "icon": "⚖️",
        "color": QColor(150, 150, 200),
        "default_properties": {
            "capacity": "分离",
            "material": "碳钢",
            "dynamic": "静设备"
        }
    }
}

EQUIPMENT_TYPES = {}
for key, info in EQUIPMENT_TYPE_DETAILED_MAPPING.items():
    EQUIPMENT_TYPES[key] = {
        "name": info["default_properties"]["capacity"],
        "icon": info["icon"],
        "color": info["color"]
    }

class ProcessFlowDiagramTab(QWidget):
    """工艺流程图标签页"""
    
    def __init__(self, data_manager=None, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.parent_window = parent
        self.equipment_list_tab = None
        
        # 设备类型映射（PFD类型 ↔ 设备清单类型）
        self.pfd_to_inventory = {}  # PFD类型 → 设备清单类型
        self.inventory_to_pfd = {}  # 设备清单类型 → PFD类型
        self.init_equipment_type_mapping()
        
        # 流程图编辑器
        self.flow_diagram = ProcessFlowDiagram(self)
        
        # 设备列表（从数据管理器获取）
        self.equipment_list = []
        
        # 设置UI
        self.setup_ui()
        
        # 连接信号
        self.connect_signals()
        
        # 设置场景变化监听
        self.setup_scene_monitor()
        
        # 加载现有设备
        self.load_existing_equipment()
        
        print("✅ 工艺流程图标签页初始化完成")
    
    def init_equipment_type_mapping(self):
        """初始化设备类型映射"""
        # 从 EQUIPMENT_TYPE_DETAILED_MAPPING 创建双向映射
        for pfd_type, info in EQUIPMENT_TYPE_DETAILED_MAPPING.items():
            inventory_type = info.get("inventory_type", "其他")
            self.pfd_to_inventory[pfd_type] = inventory_type
            self.inventory_to_pfd[inventory_type] = pfd_type
    
    def get_inventory_equipment_type(self, pfd_type: str) -> str:
        """获取设备清单类型"""
        return self.pfd_to_inventory.get(pfd_type, "其他")
    
    def get_pfd_equipment_type(self, inventory_type: str) -> str:
        """获取PFD设备类型"""
        return self.inventory_to_pfd.get(inventory_type, "vessel")

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


class MaterialConnection(QGraphicsPathItem):
    """物料连接线"""
    
    def __init__(self, source: EquipmentNode, source_point: str,
                 target: EquipmentNode, target_point: str,
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


class ProcessFlowDiagram(QGraphicsView):
    """工艺流程图编辑器"""
    
    # 信号定义
    equipment_added = Signal(dict)  # 设备添加信号
    equipment_updated = Signal(dict)  # 设备更新信号
    equipment_deleted = Signal(str)  # 设备删除信号
    connection_added = Signal(dict)  # 连接添加信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 场景
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.scene.setSceneRect(-1000, -1000, 2000, 2000)
        
        # 设置视图
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        
        # 缩放和滚动
        self.scale_factor = 1.0
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        
        # 数据存储
        self.equipment_nodes = {}  # 设备节点字典
        self.material_connections = []  # 物料连接列表
        self.current_tool = "select"  # 当前工具
        
        # 临时连接线（用于绘制中的连接）
        self.temp_connection = None
        self.connection_source = None
        self.connection_source_point = None
        
        # 设置背景
        self.setBackgroundBrush(QBrush(QColor(240, 240, 240)))
        
        # 网格
        self.grid_size = 50
        self.show_grid = True
        
        # 初始化工具栏
        self.init_toolbar()
        
        # 启用拖放
        self.setAcceptDrops(True)
        
        # 拖放相关
        self.is_dragging_from_library = False
        self.dragging_equipment_type = None
    
    def init_toolbar(self):
        """初始化工具栏"""
        self.toolbar = QToolBar()
        self.select_tool = QAction("选择", self)
        self.select_tool.setCheckable(True)
        self.select_tool.setChecked(True)
        self.select_tool.triggered.connect(lambda: self.set_tool("select"))
        self.save_action = QAction("保存", self)
        self.save_action.triggered.connect(self.save_diagram_from_toolbar)
        self.load_action = QAction("加载", self)
        self.load_action.triggered.connect(self.load_diagram_from_toolbar)
        self.export_action = QAction("导出图片", self)
        self.export_action.triggered.connect(self.export_diagram_from_toolbar)
        self.help_action = QAction("帮助", self)
        self.help_action.triggered.connect(self.show_help_dialog)
        self.tool_group = QActionGroup(self)
        self.tool_group.addAction(self.select_tool)
        self.toolbar.addAction(self.select_tool)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.save_action)
        self.toolbar.addAction(self.load_action)
        self.toolbar.addAction(self.export_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.help_action)
        self.toolbar.addSeparator()
        self.zoom_in_action = QAction("放大", self)
        self.zoom_in_action.triggered.connect(lambda: self.scale(1.2, 1.2))
        self.toolbar.addAction(self.zoom_in_action)
        self.zoom_out_action = QAction("缩小", self)
        self.zoom_out_action.triggered.connect(lambda: self.scale(1/1.2, 1/1.2))
        self.toolbar.addAction(self.zoom_out_action)
        self.zoom_reset_action = QAction("重置缩放", self)
        self.zoom_reset_action.triggered.connect(self.reset_view)
        self.toolbar.addAction(self.zoom_reset_action)
    
    def show_help_dialog(self):
        """显示帮助对话框"""
        help_text = """
        <h2>工艺流程图编辑器使用说明</h2>
        
        <h3>基本操作：</h3>
        <p><b>1. 添加设备：</b>
            <ul>
                <li>方法一：点击左侧设备库中的设备图标，然后在画布上点击添加</li>
                <li>方法二：从左侧设备库拖动设备图标到画布中</li>
            </ul>
        </p>
        <p><b>2. 移动设备：</b>点击选中设备后，拖拽到目标位置</p>
        <p><b>3. 添加连接：</b>
            <ul>
                <li>方法一：右键点击源设备 → "添加连接到..." → 选择目标设备</li>
                <li>方法二：按住Ctrl键，依次点击两个设备 → 右键 → "创建连接"</li>
            </ul>
        </p>
        <p><b>4. 编辑属性：</b>右键点击设备或连接 → "编辑属性"</p>
        <p><b>5. 删除元素：</b>右键点击设备或连接 → "删除"</p>
        
        <h3>快捷操作：</h3>
        <p><b>• 缩放视图：</b>使用鼠标滚轮</p>
        <p><b>• 平移视图：</b>按住鼠标中键拖拽</p>
        <p><b>• 多选：</b>按住Ctrl键点击多个项目，或使用框选</p>
        <p><b>• 撤销/重做：</b>Ctrl+Z / Ctrl+Y</p>
        
        <h3>设备类型说明：</h3>
        <p><b>• 储罐 📦：</b>用于储存物料</p>
        <p><b>• 泵 🔧：</b>用于输送流体</p>
        <p><b>• 反应器 ⚗️：</b>用于化学反应</p>
        <p><b>• 换热器 🔥：</b>用于热量交换</p>
        <p><b>• 塔 🗼：</b>用于精馏、吸收等</p>
        <p><b>• 阀门 🚰：</b>用于控制流量</p>
        <p><b>• 过滤器 🧹：</b>用于分离固体</p>
        <p><b>• 混合器 🌀：</b>用于混合物料</p>
        <p><b>• 分离器 ⚖️：</b>用于分离不同相态</p>
        """
        
        dialog = QDialog(self)
        dialog.setWindowTitle("帮助 - 工艺流程图编辑器")
        dialog.setFixedSize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        # 创建文本框显示帮助内容
        text_browser = QTextBrowser()
        text_browser.setHtml(help_text)
        text_browser.setOpenExternalLinks(True)
        
        layout.addWidget(text_browser)
        
        # 添加关闭按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)
        
        dialog.exec()
    
    def set_tool(self, tool: str):
        """设置当前工具"""
        self.current_tool = tool
        if tool == "select":
            self.setDragMode(QGraphicsView.RubberBandDrag)
            self.setCursor(Qt.ArrowCursor)
    
    def mousePressEvent(self, event: QMouseEvent):
        """鼠标按下事件"""
        # 检查是否正在进行拖放操作
        if self.is_dragging_from_library and self.dragging_equipment_type:
            # 获取鼠标位置
            scene_pos = self.mapToScene(event.pos())
            
            # 添加设备
            self.add_equipment_at_position(self.dragging_equipment_type, scene_pos)
            
            # 重置拖放状态
            self.is_dragging_from_library = False
            self.dragging_equipment_type = None
            
            # 恢复光标
            self.unsetCursor()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """鼠标移动事件"""
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """鼠标释放事件"""
        super().mouseReleaseEvent(event)
    
    def wheelEvent(self, event: QWheelEvent):
        """滚轮事件 - 缩放"""
        factor = 1.2
        if event.angleDelta().y() < 0:
            factor = 1.0 / factor
        
        self.scale(factor, factor)
        self.scale_factor *= factor
    
    def dragEnterEvent(self, event):
        """拖拽进入事件"""
        # 检查是否有拖拽数据
        if event.mimeData().hasText() and event.mimeData().text().startswith("EQUIPMENT:"):
            event.acceptProposedAction()
            
            # 设置拖拽光标
            self.setCursor(Qt.DragMoveCursor)
            
            # 设置拖拽状态
            self.is_dragging_from_library = True
            
            # 获取设备类型
            self.dragging_equipment_type = event.mimeData().text().replace("EQUIPMENT:", "")
        else:
            event.ignore()
    
    def dragMoveEvent(self, event):
        """拖拽移动事件"""
        if self.is_dragging_from_library:
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """拖放事件"""
        if self.is_dragging_from_library and self.dragging_equipment_type:
            # 获取鼠标位置
            scene_pos = self.mapToScene(event.position().toPoint())
            
            # 添加设备
            self.add_equipment_at_position(self.dragging_equipment_type, scene_pos)
            
            event.acceptProposedAction()
        else:
            event.ignore()
        
        # 重置拖放状态
        self.is_dragging_from_library = False
        self.dragging_equipment_type = None
        
        # 恢复光标
        self.unsetCursor()
    
    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        # 重置拖放状态
        self.is_dragging_from_library = False
        self.dragging_equipment_type = None
        
        # 恢复光标
        self.unsetCursor()
        
        event.accept()
    
    def add_equipment_at_position(self, equipment_type: str, position: QPointF):
        """在指定位置添加设备"""
        equipment_info = EQUIPMENT_TYPES.get(equipment_type, {})
        equipment_name = equipment_info.get("name", "设备")
        
        # 生成唯一ID
        import uuid
        equipment_id = f"{equipment_type.upper()}_{str(uuid.uuid4())[:6].upper()}"
        
        # 创建设备
        equipment = EquipmentNode(
            equipment_id, equipment_type, equipment_name,
            position.x(), position.y()
        )
        
        # 添加到场景
        self.scene.addItem(equipment)
        self.equipment_nodes[equipment_id] = equipment
        
        # 发送信号
        self.equipment_added.emit({
            "equipment_id": equipment_id,
            "equipment_type": equipment_type,
            "name": equipment_name,
            "position": {"x": position.x(), "y": position.y()},
            "properties": equipment.properties
        })
    
    def contextMenuEvent(self, event: QContextMenuEvent):
        """右键菜单事件"""
        menu = QMenu(self)
        
        item = self.itemAt(event.pos())
        
        if isinstance(item, EquipmentNode):
            # 设备右键菜单
            edit_action = menu.addAction("编辑设备属性")
            delete_action = menu.addAction("删除设备")
            clone_action = menu.addAction("克隆设备")
            
            menu.addSeparator()
            
            # 同步选项
            sync_action = menu.addAction("💾 同步到设备清单")
            sync_action.triggered.connect(lambda: self.sync_equipment_to_inventory(item))
            
            # 查看设备清单信息
            if item.unique_code:
                info_action = menu.addAction(f"查看设备清单信息")
                info_action.triggered.connect(lambda: self.show_equipment_inventory_info(item))
            
            # 添加连接点菜单
            connection_menu = menu.addMenu("添加连接到...")
            
            edit_action.triggered.connect(lambda: self.edit_equipment_properties(item))
            delete_action.triggered.connect(lambda: self.delete_equipment(item))
            clone_action.triggered.connect(lambda: self.clone_equipment(item))
            
            # 显示其他设备作为连接目标
            for eq_id, eq_node in self.equipment_nodes.items():
                if eq_node != item:
                    target_action = connection_menu.addAction(f"→ {eq_node.name} ({eq_node.equipment_id})")
                    target_action.triggered.connect(
                        lambda checked=False, target=eq_node: self.add_connection_between(item, target)
                    )
        
        elif isinstance(item, MaterialConnection):
            # 连接线右键菜单
            pass
        
        else:
            # 空白区域右键菜单
            add_equipment_action = menu.addAction("添加设备")
            add_from_inventory_action = menu.addAction("📥 从设备清单添加")
            
            add_equipment_action.triggered.connect(
                lambda: self.show_add_equipment_dialog(self.mapToScene(event.pos()))
            )
            add_from_inventory_action.triggered.connect(self.show_add_from_inventory_dialog)
        
        menu.exec(event.globalPos())
    
    def show_equipment_inventory_info(self, equipment_node: EquipmentNode):
        """显示设备清单信息"""
        if not equipment_node.unique_code or not self.data_manager:
            return
        
        try:
            # 获取设备清单数据
            equipment_data = self.data_manager.get_equipment_by_unique_code(equipment_node.unique_code)
            if not equipment_data:
                QMessageBox.information(self, "提示", "未在设备清单中找到该设备")
                return
            
            # 创建信息对话框
            dialog = QDialog(self)
            dialog.setWindowTitle(f"设备清单信息 - {equipment_node.name}")
            dialog.setMinimumSize(500, 400)
            
            layout = QVBoxLayout(dialog)
            
            # 创建文本框显示信息
            text_browser = QTextBrowser()
            text_browser.setFont(QFont("Arial", 10))
            
            # 格式化显示信息
            html = f"""
            <h3>设备基本信息</h3>
            <table border="0" cellpadding="4">
                <tr><td><b>唯一编码:</b></td><td>{equipment_data.get('unique_code', '')}</td></tr>
                <tr><td><b>设备位号:</b></td><td>{equipment_data.get('equipment_id', '')}</td></tr>
                <tr><td><b>设备名称:</b></td><td>{equipment_data.get('name', '')}</td></tr>
                <tr><td><b>设备类型:</b></td><td>{equipment_data.get('type', '')}</td></tr>
                <tr><td><b>状态:</b></td><td>{equipment_data.get('status', 'active')}</td></tr>
            </table>
            
            <h3>设计参数</h3>
            <table border="0" cellpadding="4">
                <tr><td><b>设计压力:</b></td><td>{equipment_data.get('design_pressure', '')}</td></tr>
                <tr><td><b>设计温度:</b></td><td>{equipment_data.get('design_temperature', '')}</td></tr>
                <tr><td><b>操作压力:</b></td><td>{equipment_data.get('operating_pressure', '')}</td></tr>
                <tr><td><b>操作温度:</b></td><td>{equipment_data.get('operating_temperature', '')}</td></tr>
            </table>
            
            <h3>其他信息</h3>
            <table border="0" cellpadding="4">
                <tr><td><b>材质:</b></td><td>{equipment_data.get('material', '')}</td></tr>
                <tr><td><b>制造商:</b></td><td>{equipment_data.get('manufacturer', '')}</td></tr>
                <tr><td><b>型号:</b></td><td>{equipment_data.get('model', '')}</td></tr>
                <tr><td><b>备注:</b></td><td>{equipment_data.get('notes', '')}</td></tr>
            </table>
            """
            
            text_browser.setHtml(html)
            
            layout.addWidget(text_browser)
            
            button_box = QDialogButtonBox(QDialogButtonBox.Ok)
            button_box.accepted.connect(dialog.accept)
            layout.addWidget(button_box)
            
            dialog.exec()
            
        except Exception as e:
            print(f"❌ 显示设备清单信息时出错: {e}")
            QMessageBox.critical(self, "错误", f"获取设备信息失败: {str(e)}")
    
    def show_add_equipment_dialog(self, position: QPointF):
        """显示添加设备对话框"""
        self.add_equipment_dialog(position)

    def show_add_from_inventory_dialog(self):
        """显示从设备清单添加设备的对话框"""
        if not self.data_manager:
            QMessageBox.warning(self, "错误", "数据管理器未初始化")
            return
            
        try:
            # 获取所有设备
            equipment_data = self.data_manager.get_equipment_data()
            if not equipment_data:
                QMessageBox.information(self, "提示", "设备清单中没有设备")
                return
                
            # 创建选择对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("从设备清单选择设备")
            dialog.setMinimumSize(600, 400)
            
            layout = QVBoxLayout(dialog)
            
            # 搜索框
            search_layout = QHBoxLayout()
            search_label = QLabel("搜索:")
            search_input = QLineEdit()
            search_input.setPlaceholderText("输入设备名称、位号或唯一编码...")
            search_button = QPushButton("搜索")
            search_layout.addWidget(search_label)
            search_layout.addWidget(search_input)
            search_layout.addWidget(search_button)
            layout.addLayout(search_layout)
            
            # 创建表格显示设备
            table = QTableWidget()
            table.setColumnCount(6)
            table.setHorizontalHeaderLabels(["选择", "唯一编码", "设备位号", "设备名称", "类型", "状态"])
            table.setRowCount(len(equipment_data))
            
            checkboxes = []
            
            for i, eq in enumerate(equipment_data):
                # 添加复选框
                checkbox = QCheckBox()
                checkboxes.append(checkbox)
                
                # 创建包含复选框的widget
                checkbox_widget = QWidget()
                checkbox_layout = QHBoxLayout(checkbox_widget)
                checkbox_layout.addWidget(checkbox)
                checkbox_layout.setAlignment(Qt.AlignCenter)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                
                table.setCellWidget(i, 0, checkbox_widget)
                table.setItem(i, 1, QTableWidgetItem(eq.get("unique_code", "")))
                table.setItem(i, 2, QTableWidgetItem(eq.get("equipment_id", "")))
                table.setItem(i, 3, QTableWidgetItem(eq.get("name", "")))
                table.setItem(i, 4, QTableWidgetItem(eq.get("type", "")))
                table.setItem(i, 5, QTableWidgetItem(eq.get("status", "active")))
            
            table.horizontalHeader().setStretchLastSection(True)
            table.resizeColumnsToContents()
            layout.addWidget(table)
            
            # 搜索功能
            def filter_table():
                search_text = search_input.text().lower()
                for row in range(table.rowCount()):
                    visible = False
                    if search_text:
                        for col in [1, 2, 3, 4]:  # 搜索唯一编码、位号、名称、类型
                            item = table.item(row, col)
                            if item and search_text in item.text().lower():
                                visible = True
                                break
                    else:
                        visible = True
                    table.setRowHidden(row, not visible)
            
            search_input.textChanged.connect(filter_table)
            search_button.clicked.connect(filter_table)
            
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            
            if dialog.exec() == QDialog.Accepted:
                # 获取选中的设备
                selected_indices = []
                for i, checkbox in enumerate(checkboxes):
                    if checkbox.isChecked():
                        selected_indices.append(i)
                
                if not selected_indices:
                    return
                    
                # 在流程图中心位置添加选中的设备
                view_rect = self.flow_diagram.viewport().rect()
                center = self.flow_diagram.mapToScene(view_rect.center())
                
                for i, idx in enumerate(selected_indices):
                    eq_data = equipment_data[idx]
                    
                    # 检查设备是否已在流程图中
                    eq_id = eq_data.get("equipment_id")
                    if eq_id in self.flow_diagram.equipment_nodes:
                        reply = QMessageBox.question(
                            self, "设备已存在",
                            f"设备 '{eq_data.get('name')}' 已在流程图中，是否重新添加？",
                            QMessageBox.Yes | QMessageBox.No
                        )
                        if reply == QMessageBox.No:
                            continue
                        else:
                            # 删除现有设备
                            existing_eq = self.flow_diagram.equipment_nodes[eq_id]
                            self.flow_diagram.delete_equipment(existing_eq)
                    
                    # 稍微偏移位置，避免重叠
                    offset_x = (i % 3) * 150
                    offset_y = (i // 3) * 150
                    
                    # 添加设备到流程图
                    equipment_node = self.add_equipment_from_inventory(eq_data)
                    
                    if equipment_node:
                        # 设置位置
                        equipment_node.setPos(center.x() + offset_x, center.y() + offset_y)
                        
                        # 更新位置信息
                        eq_data["pfd_position_x"] = equipment_node.x()
                        eq_data["pfd_position_y"] = equipment_node.y()
                        
                        # 更新数据管理器中的设备数据
                        if self.data_manager:
                            self.data_manager.update_equipment(eq_data.get("equipment_id"), eq_data)
                            
                QMessageBox.information(self, "成功", f"已添加 {len(selected_indices)} 个设备到流程图")
                
        except Exception as e:
            print(f"❌ 显示设备清单对话框时出错: {e}")
            QMessageBox.critical(self, "错误", f"加载设备清单失败: {str(e)}")
    
    def start_connection_from_selected(self, equipment: EquipmentNode):
        """从选中的设备开始连接"""
        self.connection_source = equipment
        self.connection_source_point = "outlet"  # 默认使用出口
        
        # 创建临时连接线
        self.temp_connection = QGraphicsLineItem()
        self.temp_connection.setPen(QPen(QColor(0, 100, 200), 2, Qt.DashLine))
        self.scene.addItem(self.temp_connection)
        
        # 切换工具状态
        self.current_tool = "add_connection"
        self.setDragMode(QGraphicsView.NoDrag)
        self.setCursor(Qt.CrossCursor)
    
    def select_all_items(self):
        """选择所有项目"""
        for eq_id, equipment in self.equipment_nodes.items():
            equipment.setSelected(True)
        
        for connection in self.material_connections:
            connection.setSelected(True)
    
    def clone_equipment(self, equipment: EquipmentNode):
        """克隆设备"""
        # 创建新设备ID
        import uuid
        new_id = f"{equipment.equipment_id}_COPY_{str(uuid.uuid4())[:4].upper()}"
        
        # 创建新设备
        new_equipment = EquipmentNode(
            new_id,
            equipment.equipment_type,
            f"{equipment.name} (副本)",
            equipment.x() + 50,  # 向右偏移
            equipment.y() + 50   # 向下偏移
        )
        
        # 复制属性
        new_equipment.properties = equipment.properties.copy()
        
        # 添加到场景
        self.scene.addItem(new_equipment)
        self.equipment_nodes[new_id] = new_equipment
        
        # 发送信号
        self.equipment_added.emit({
            "equipment_id": new_id,
            "equipment_type": equipment.equipment_type,
            "name": f"{equipment.name} (副本)",
            "position": {"x": new_equipment.x(), "y": new_equipment.y()},
            "properties": new_equipment.properties
        })
    
    def add_equipment_dialog(self, position: QPointF):
        """添加设备对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("添加设备")
        dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # 设备类型选择
        type_layout = QHBoxLayout()
        type_label = QLabel("设备类型:")
        type_combo = QComboBox()
        
        for type_key, type_info in EQUIPMENT_TYPES.items():
            type_combo.addItem(f"{type_info['icon']} {type_info['name']}", type_key)
        
        type_layout.addWidget(type_label)
        type_layout.addWidget(type_combo)
        layout.addLayout(type_layout)
        
        # 设备名称
        name_layout = QHBoxLayout()
        name_label = QLabel("设备名称:")
        name_input = QLineEdit()
        name_input.setPlaceholderText("例如: 反应器R-101")
        name_layout.addWidget(name_label)
        name_layout.addWidget(name_input)
        layout.addLayout(name_layout)
        
        # 设备ID
        id_layout = QHBoxLayout()
        id_label = QLabel("设备ID:")
        id_input = QLineEdit()
        import uuid
        id_input.setText(f"EQ_{str(uuid.uuid4())[:8].upper()}")
        id_layout.addWidget(id_label)
        id_layout.addWidget(id_input)
        layout.addLayout(id_layout)
        
        # 基础属性
        form_layout = QFormLayout()
        
        temp_spin = QDoubleSpinBox()
        temp_spin.setRange(-273, 1000)
        temp_spin.setValue(25)
        temp_spin.setSuffix(" °C")
        form_layout.addRow("温度:", temp_spin)
        
        pressure_spin = QDoubleSpinBox()
        pressure_spin.setRange(0, 10000)
        pressure_spin.setValue(101.325)
        pressure_spin.setSuffix(" kPa")
        form_layout.addRow("压力:", pressure_spin)
        
        volume_spin = QDoubleSpinBox()
        volume_spin.setRange(0, 1000)
        volume_spin.setValue(1.0)
        volume_spin.setSuffix(" m³")
        form_layout.addRow("体积:", volume_spin)
        
        layout.addLayout(form_layout)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.Accepted:
            # 创建设备节点
            equipment_type = type_combo.currentData()
            equipment_name = name_input.text() or f"设备_{len(self.equipment_nodes)+1}"
            equipment_id = id_input.text()
            
            # 创建设备
            equipment = EquipmentNode(
                equipment_id, equipment_type, equipment_name,
                position.x(), position.y()
            )
            
            # 设置属性
            equipment.properties.update({
                "temperature": temp_spin.value(),
                "pressure": pressure_spin.value(),
                "volume": volume_spin.value()
            })
            
            # 添加到场景
            self.scene.addItem(equipment)
            self.equipment_nodes[equipment_id] = equipment
            
            # 发送信号
            self.equipment_added.emit({
                "equipment_id": equipment_id,
                "equipment_type": equipment_type,
                "name": equipment_name,
                "position": {"x": position.x(), "y": position.y()},
                "properties": equipment.properties
            })
    
    def edit_equipment_properties(self, equipment: EquipmentNode):
        """编辑设备属性"""
        dialog = QDialog(self)
        dialog.setWindowTitle(f"编辑设备属性 - {equipment.name}")
        dialog.setFixedSize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # 基本信息
        info_group = QGroupBox("基本信息")
        info_layout = QFormLayout(info_group)
        
        id_label = QLabel(equipment.equipment_id)
        name_input = QLineEdit(equipment.name)
        type_label = QLabel(EQUIPMENT_TYPES.get(equipment.equipment_type, {}).get("name", "未知"))
        
        info_layout.addRow("设备ID:", id_label)
        info_layout.addRow("设备名称:", name_input)
        info_layout.addRow("设备类型:", type_label)
        
        layout.addWidget(info_group)
        
        # 工艺参数
        params_group = QGroupBox("工艺参数")
        params_layout = QFormLayout(params_group)
        
        temp_spin = QDoubleSpinBox()
        temp_spin.setRange(-273, 1000)
        temp_spin.setValue(equipment.properties.get("temperature", 25))
        temp_spin.setSuffix(" °C")
        params_layout.addRow("温度:", temp_spin)
        
        pressure_spin = QDoubleSpinBox()
        pressure_spin.setRange(0, 10000)
        pressure_spin.setValue(equipment.properties.get("pressure", 101.325))
        pressure_spin.setSuffix(" kPa")
        params_layout.addRow("压力:", pressure_spin)
        
        flow_spin = QDoubleSpinBox()
        flow_spin.setRange(0, 10000)
        flow_spin.setValue(equipment.properties.get("flow_rate", 0))
        flow_spin.setSuffix(" kg/h")
        params_layout.addRow("流量:", flow_spin)
        
        material_input = QLineEdit(equipment.properties.get("material", ""))
        params_layout.addRow("物料:", material_input)
        
        status_combo = QComboBox()
        status_combo.addItems(["normal", "warning", "error", "maintenance"])
        status_combo.setCurrentText(equipment.properties.get("status", "normal"))
        params_layout.addRow("状态:", status_combo)
        
        layout.addWidget(params_group)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.Accepted:
            # 更新设备
            equipment.name = name_input.text()
            equipment.properties.update({
                "temperature": temp_spin.value(),
                "pressure": pressure_spin.value(),
                "flow_rate": flow_spin.value(),
                "material": material_input.text(),
                "status": status_combo.currentText()
            })
            
            equipment.update()
            
            # 发送更新信号
            self.equipment_updated.emit({
                "equipment_id": equipment.equipment_id,
                "name": equipment.name,
                "properties": equipment.properties
            })
    
    def delete_equipment(self, equipment: EquipmentNode):
        """删除设备"""
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除设备 '{equipment.name}' 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 删除相关连接
            connections_to_remove = []
            for connection in self.material_connections:
                if connection.source == equipment or connection.target == equipment:
                    connections_to_remove.append(connection)
            
            for connection in connections_to_remove:
                self.delete_connection(connection)
            
            # 删除设备
            self.scene.removeItem(equipment)
            
            # 从设备字典中移除
            if equipment.equipment_id in self.equipment_nodes:
                del self.equipment_nodes[equipment.equipment_id]
            
            # 发送删除信号
            self.equipment_deleted.emit(equipment.equipment_id)
    
    def add_connection_between(self, source: EquipmentNode, target: EquipmentNode):
        """在两个设备之间添加连接"""
        dialog = QDialog(self)
        dialog.setWindowTitle("添加物料连接")
        dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # 连接信息
        info_label = QLabel(f"从 {source.name} 连接到 {target.name}")
        layout.addWidget(info_label)
        
        # 物料信息
        form_layout = QFormLayout()
        
        material_input = QLineEdit()
        material_input.setPlaceholderText("例如: 甲醇、水、原料气")
        form_layout.addRow("物料名称:", material_input)
        
        material_combo = QComboBox()
        for type_key, type_info in MATERIAL_TYPES.items():
            material_combo.addItem(type_info["name"], type_key)
        form_layout.addRow("物料类型:", material_combo)
        
        flow_spin = QDoubleSpinBox()
        flow_spin.setRange(0, 10000)
        flow_spin.setValue(100)
        flow_spin.setSuffix(" kg/h")
        form_layout.addRow("流量:", flow_spin)
        
        temp_spin = QDoubleSpinBox()
        temp_spin.setRange(-273, 1000)
        temp_spin.setValue(25)
        temp_spin.setSuffix(" °C")
        form_layout.addRow("温度:", temp_spin)
        
        layout.addLayout(form_layout)
        
        # 连接点选择
        points_group = QGroupBox("连接点")
        points_layout = QHBoxLayout(points_group)
        
        source_combo = QComboBox()
        for point in ["inlet", "outlet", "top", "bottom"]:
            source_combo.addItem(point)
        points_layout.addWidget(QLabel("起点:"))
        points_layout.addWidget(source_combo)
        
        target_combo = QComboBox()
        for point in ["inlet", "outlet", "top", "bottom"]:
            target_combo.addItem(point)
        points_layout.addWidget(QLabel("终点:"))
        points_layout.addWidget(target_combo)
        
        layout.addWidget(points_group)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.Accepted:
            # 创建连接
            connection = MaterialConnection(
                source, source_combo.currentText(),
                target, target_combo.currentText(),
                material_type=material_combo.currentData(),
                material_name=material_input.text()
            )
            
            connection.properties.update({
                "flow_rate": flow_spin.value(),
                "temperature": temp_spin.value()
            })
            
            self.scene.addItem(connection)
            self.material_connections.append(connection)
            
            # 发送信号
            self.connection_added.emit({
                "source": source.equipment_id,
                "source_point": source_combo.currentText(),
                "target": target.equipment_id,
                "target_point": target_combo.currentText(),
                "material_name": material_input.text(),
                "material_type": material_combo.currentData(),
                "properties": connection.properties
            })
    
    def edit_connection_properties(self, connection: MaterialConnection):
        """编辑连接属性"""
        dialog = QDialog(self)
        dialog.setWindowTitle("编辑连接属性")
        dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        
        material_input = QLineEdit(connection.material_name)
        form_layout.addRow("物料名称:", material_input)
        
        flow_spin = QDoubleSpinBox()
        flow_spin.setRange(0, 10000)
        flow_spin.setValue(connection.properties.get("flow_rate", 0))
        flow_spin.setSuffix(" kg/h")
        form_layout.addRow("流量:", flow_spin)
        
        temp_spin = QDoubleSpinBox()
        temp_spin.setRange(-273, 1000)
        temp_spin.setValue(connection.properties.get("temperature", 25))
        temp_spin.setSuffix(" °C")
        form_layout.addRow("温度:", temp_spin)
        
        pressure_spin = QDoubleSpinBox()
        pressure_spin.setRange(0, 10000)
        pressure_spin.setValue(connection.properties.get("pressure", 101.325))
        pressure_spin.setSuffix(" kPa")
        form_layout.addRow("压力:", pressure_spin)
        
        layout.addLayout(form_layout)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.Accepted:
            # 更新连接
            connection.material_name = material_input.text()
            connection.properties.update({
                "flow_rate": flow_spin.value(),
                "temperature": temp_spin.value(),
                "pressure": pressure_spin.value()
            })
            
            connection.update()
    
    def delete_connection(self, connection: MaterialConnection):
        """删除连接"""
        # 从相关设备中注销连接线
        connection.unregister_from_equipment()
        
        # 从场景中移除连接线
        self.scene.removeItem(connection)
        
        # 从连接线列表中移除
        if connection in self.material_connections:
            self.material_connections.remove(connection)
    
    def get_nearest_connection_point(self, equipment: EquipmentNode, mouse_pos: QPoint) -> str:
        """获取最近的连接点"""
        scene_pos = self.mapToScene(mouse_pos)
        equipment_pos = equipment.pos()
        
        min_distance = float('inf')
        nearest_point = "outlet"
        
        for point_name, point in equipment.connection_points.items():
            global_point = equipment.mapToScene(point)
            distance = QLineF(scene_pos, global_point).length()
            
            if distance < min_distance:
                min_distance = distance
                nearest_point = point_name
        
        return nearest_point
    
    def reset_view(self):
        """重置视图"""
        self.resetTransform()
        self.centerOn(0, 0)
        self.scale_factor = 1.0
    
    def save_diagram(self, file_path: str):
        """保存流程图"""
        diagram_data = {
            "equipment": [],
            "connections": [],
            "metadata": {
                "created": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
        
        # 保存设备
        for equipment_id, equipment in self.equipment_nodes.items():
            diagram_data["equipment"].append({
                "id": equipment_id,
                "type": equipment.equipment_type,
                "name": equipment.name,
                "position": {
                    "x": equipment.pos().x(),
                    "y": equipment.pos().y()
                },
                "properties": equipment.properties
            })
        
        # 保存连接
        for connection in self.material_connections:
            diagram_data["connections"].append({
                "source": connection.source.equipment_id,
                "source_point": connection.source_point,
                "target": connection.target.equipment_id,
                "target_point": connection.target_point,
                "material_type": connection.material_type,
                "material_name": connection.material_name,
                "properties": connection.properties
            })
        
        # 保存为JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(diagram_data, f, ensure_ascii=False, indent=2)
    
    def load_diagram(self, file_path: str):
        """加载流程图"""
        with open(file_path, 'r', encoding='utf-8') as f:
            diagram_data = json.load(f)
        
        # 清空场景
        self.clear_diagram()
        
        # 加载设备
        for eq_data in diagram_data.get("equipment", []):
            equipment = EquipmentNode(
                eq_data["id"],
                eq_data["type"],
                eq_data["name"],
                eq_data["position"]["x"],
                eq_data["position"]["y"]
            )
            equipment.properties = eq_data.get("properties", {})
            
            self.scene.addItem(equipment)
            self.equipment_nodes[eq_data["id"]] = equipment
        
        # 加载连接
        for conn_data in diagram_data.get("connections", []):
            source = self.equipment_nodes.get(conn_data["source"])
            target = self.equipment_nodes.get(conn_data["target"])
            
            if source and target:
                connection = MaterialConnection(
                    source, conn_data["source_point"],
                    target, conn_data["target_point"],
                    conn_data.get("material_type", "liquid"),
                    conn_data.get("material_name", "")
                )
                connection.properties = conn_data.get("properties", {})
                
                self.scene.addItem(connection)
                self.material_connections.append(connection)
    
    def clear_diagram(self):
        """清空流程图"""
        self.scene.clear()
        self.equipment_nodes.clear()
        self.material_connections.clear()
    
    def export_as_image(self, file_path: str, format: str = "PNG"):
        """导出为图片"""
        # 获取场景边界
        rect = self.scene.itemsBoundingRect()
        
        # 创建图片
        image = QImage(rect.size().toSize(), QImage.Format_ARGB32)
        image.fill(Qt.white)
        
        # 创建画家
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 渲染场景
        self.scene.render(painter, QRectF(image.rect()), rect)
        painter.end()
        
        # 保存图片
        image.save(file_path, format)
    
    def save_diagram_from_toolbar(self):
        """从工具栏保存流程图"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存流程图",
            "process_flow_diagram.json",
            "JSON文件 (*.json)"
        )
        
        if file_path:
            self.save_diagram(file_path)
            QMessageBox.information(self, "保存成功", "流程图已保存")
    
    def load_diagram_from_toolbar(self):
        """从工具栏加载流程图"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "加载流程图",
            "", "JSON文件 (*.json)"
        )
        
        if file_path:
            self.load_diagram(file_path)
            QMessageBox.information(self, "加载成功", "流程图已加载")
    
    def export_diagram_from_toolbar(self):
        """从工具栏导出为图片"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出流程图",
            "process_flow_diagram.png",
            "PNG图片 (*.png);;JPEG图片 (*.jpg);;BMP图片 (*.bmp)"
        )
        
        if file_path:
            if file_path.endswith('.png'):
                format = "PNG"
            elif file_path.endswith('.jpg'):
                format = "JPG"
            elif file_path.endswith('.bmp'):
                format = "BMP"
            else:
                file_path += '.png'
                format = "PNG"
            
            self.export_as_image(file_path, format)
            QMessageBox.information(self, "导出成功", f"流程图已导出为: {file_path}")

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

class ProcessFlowDiagramTab(QWidget):
    """工艺流程图标签页"""
    
    def __init__(self, data_manager=None, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.parent_window = parent
        self.equipment_list_tab = None
        
        # 流程图编辑器
        self.flow_diagram = ProcessFlowDiagram(self)
        
        # 设备列表（从数据管理器获取）
        self.equipment_list = []
        
        # 设置UI
        self.setup_ui()
        
        # 连接信号
        self.connect_signals()
        
        # 设置场景变化监听
        self.setup_scene_monitor()
        
        # 加载现有设备
        self.load_existing_equipment()
        
        print("✅ 工艺流程图标签页初始化完成")

    def get_pfd_equipment_type(self, inventory_type: str) -> str:
        """将设备清单类型映射到工艺流程图类型"""
        for pfd_type, mapping in EQUIPMENT_TYPE_DETAILED_MAPPING.items():
            if mapping["inventory_type"] == inventory_type:
                return pfd_type
                
        # 默认映射
        type_mapping = {
            "T 储罐": "vessel",
            "P 泵类": "pump", 
            "R 反应器": "reactor",
            "E 换热设备类": "heat_exchanger",
            "C 塔器": "column",
            "A 搅拌设备类": "mixer",
            "S 分离设备类": "separator",
            "其他": "vessel"
        }
        
        return type_mapping.get(inventory_type, "vessel")

    def sync_with_inventory(self):
        """同步流程图和设备清单之间的设备数据"""
        if not self.data_manager:
            QMessageBox.warning(self, "错误", "数据管理器未初始化")
            return
        
        try:
            # 获取设备清单中的所有设备
            inventory_equipment = self.data_manager.get_equipment_data()
            
            # 同步设备清单到流程图
            synced_count = 0
            for eq_data in inventory_equipment:
                eq_id = eq_data.get("equipment_id")
                if eq_id and eq_id not in self.flow_diagram.equipment_nodes:
                    # 设备不在流程图中，添加它
                    self.add_equipment_from_inventory(eq_data)
                    synced_count += 1
            
            # 同步流程图到设备清单
            for eq_id, equipment in self.flow_diagram.equipment_nodes.items():
                if not hasattr(equipment, 'unique_code') or not equipment.unique_code:
                    # 生成唯一编码（如果设备清单中没有）
                    equipment_type = self.get_inventory_equipment_type(equipment.equipment_type)
                    
                    # 使用设备清单模块的唯一编码生成器
                    from .equipment_id_generator import EquipmentIDGenerator
                    unique_code = EquipmentIDGenerator.generate_equipment_id(
                        equipment_type,
                        custom_seed=equipment.name
                    )
                    
                    equipment.unique_code = unique_code
                    equipment.inventory_type = equipment_type
                    
                    # 同步到设备清单
                    self.sync_equipment_to_inventory(equipment)
                    synced_count += 1
            
            # 更新设备表格
            self.update_equipment_table()
            
            if synced_count > 0:
                QMessageBox.information(self, "同步完成", f"成功同步 {synced_count} 个设备")
            else:
                QMessageBox.information(self, "同步完成", "设备和流程图已经是最新状态")
                
        except Exception as e:
            print(f"❌ 同步设备清单时出错: {e}")
            QMessageBox.critical(self, "错误", f"同步失败: {str(e)}")

    def load_existing_equipment(self):
        """加载数据管理器中的现有设备到流程图"""
        if not self.data_manager:
            return
            
        try:
            # 获取所有设备
            equipment_data = self.data_manager.get_equipment_data()
            if not equipment_data:
                return
                
            for eq_data in equipment_data:
                # 将设备清单的设备添加到流程图
                self.add_equipment_from_inventory(eq_data)
                
        except Exception as e:
            print(f"加载现有设备到流程图时出错: {e}")

    def get_pfd_equipment_type(self, inventory_type: str) -> str:
        """将设备清单类型映射到工艺流程图类型"""
        # 定义映射关系
        type_mapping = {
            "T 储罐": "vessel",
            "P 泵类": "pump", 
            "R 反应器": "reactor",
            "E 换热设备类": "heat_exchanger",
            "C 塔器": "column",
            "A 搅拌设备类": "mixer",
            "S 分离设备类": "separator",
            "其他": "vessel",
            "vessel": "vessel",
            "pump": "pump",
            "reactor": "reactor",
            "heat_exchanger": "heat_exchanger",
            "column": "column",
            "mixer": "mixer",
            "separator": "separator"
        }
        
        return type_mapping.get(inventory_type, "vessel")

class EquipmentDataSync:
    """设备数据同步管理器"""
    
    def __init__(self, data_manager):
        self.data_manager = data_manager
        self.equipment_cache = {}  # 设备缓存
        
    def sync_from_diagram(self, equipment_data: dict):
        """从流程图同步到设备清单"""
        # 这里实现与设备清单模块的同步逻辑
        # 1. 检查设备是否已存在
        # 2. 如果不存在，创建新设备
        # 3. 如果存在，更新设备属性
        
        equipment_id = equipment_data["equipment_id"]
        
        # 检查设备清单模块是否有对应方法
        if hasattr(self.data_manager, 'equipment_module'):
            equipment_module = self.data_manager.equipment_module
            
            # 检查设备是否存在
            existing_equipment = equipment_module.get_equipment(equipment_id)
            
            if existing_equipment:
                # 更新现有设备
                equipment_module.update_equipment(equipment_id, {
                    "name": equipment_data["name"],
                    "type": equipment_data["equipment_type"],
                    "properties": equipment_data["properties"]
                })
            else:
                # 创建新设备
                equipment_module.add_equipment({
                    "equipment_id": equipment_id,
                    "name": equipment_data["name"],
                    "type": equipment_data["equipment_type"],
                    "category": "process_equipment",
                    "properties": equipment_data["properties"],
                    "status": "active",
                    "create_time": datetime.now()
                })
    
    def sync_to_diagram(self, equipment_id: str):
        """从设备清单同步到流程图"""
        # 这里实现从设备清单模块获取数据并更新流程图
        pass