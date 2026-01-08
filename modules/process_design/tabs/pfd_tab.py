# modules/process_design/tabs/pfd_tab.py

import sys
import os
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from typing import Dict, List, Any, Optional
from datetime import datetime

from .pfd_constants import EQUIPMENT_TYPE_DETAILED_MAPPING, EQUIPMENT_TYPES
from .pfd_flow_diagram import ProcessFlowDiagram
from .pfd_equipment_node import EquipmentNode
from .pfd_material_connection import MaterialConnection
from .pfd_equipment_button import EquipmentButton
from .pfd_data_sync import EquipmentDataSync

try:
    from .equipment_dialogs import EquipmentDialog, EquipmentIDGenerator
except ImportError:
    from ..tabs.equipment_dialogs import EquipmentDialog, EquipmentIDGenerator

# 物料类型定义
MATERIAL_TYPES = {
    "liquid": {"name": "液体", "color": QColor(0, 100, 200)},
    "gas": {"name": "气体", "color": QColor(200, 100, 0)},
    "solid": {"name": "固体", "color": QColor(150, 100, 50)},
    "slurry": {"name": "浆料", "color": QColor(100, 100, 150)}
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
        
        # 数据同步管理器
        self.data_sync = EquipmentDataSync(data_manager)
        
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
    
    # 由于代码较长，这里只列出类的结构，具体方法实现请参考原文件
    # 以下为原 ProcessFlowDiagramTab 类中的主要方法，需要完整实现
    
    def setup_ui(self):
        """设置UI - 左侧竖排设备库，中间画布，右侧属性面板"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 左侧：设备库（竖排方形按钮）
        left_panel = QWidget()
        left_panel.setFixedWidth(100)  # 固定宽度
        left_panel.setStyleSheet("background-color: #f0f0f0;")
        
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.setSpacing(5)
        
        # 设备库标题
        equipment_label = QLabel("设备库")
        equipment_label.setAlignment(Qt.AlignCenter)
        equipment_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 12px;
                color: #333;
                padding: 5px;
                border-bottom: 1px solid #ccc;
            }
        """)
        left_layout.addWidget(equipment_label)
        
        # 设备按钮列表（竖排）
        self.equipment_buttons = []
        for equipment_type, equipment_info in EQUIPMENT_TYPES.items():
            btn = EquipmentButton(equipment_type, equipment_info)
            btn.clicked.connect(lambda checked, et=equipment_type: self.add_equipment_from_library(et))
            left_layout.addWidget(btn)
            self.equipment_buttons.append(btn)
        
        # 添加弹簧，使设备按钮靠上显示
        left_layout.addStretch()
        
        # 中间：流程图编辑器
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)
        
        # 创建自定义工具栏（在流程图编辑器的工具栏上方）
        custom_toolbar = QToolBar()
        custom_toolbar.setFixedHeight(40)
        
        # 添加保存到数据库按钮
        save_to_db_action = QAction("💾 保存到数据库", self)
        save_to_db_action.setToolTip("将当前流程图保存到应用程序数据库")
        save_to_db_action.triggered.connect(self.on_save_button_clicked)
        custom_toolbar.addAction(save_to_db_action)
        
        # 添加同步按钮
        sync_action = QAction("🔄 同步设备清单", self)
        sync_action.setToolTip("同步流程图和设备清单之间的设备数据")
        sync_action.triggered.connect(self.sync_with_inventory)
        custom_toolbar.addAction(sync_action)
        
        # 添加刷新按钮
        refresh_action = QAction("🔄 刷新", self)
        refresh_action.setToolTip("刷新设备列表和视图")
        refresh_action.triggered.connect(self.refresh_view)
        custom_toolbar.addAction(refresh_action)
        
        custom_toolbar.addSeparator()
        
        # 添加流程图信息标签
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet("color: #666; font-size: 12px; padding: 5px;")
        custom_toolbar.addWidget(self.status_label)
        
        # 添加伸展部件来占位（替代 addStretch）
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        custom_toolbar.addWidget(spacer)
        
        # 添加到中心布局
        center_layout.addWidget(custom_toolbar)
        
        # 添加流程图编辑器的工具栏
        center_layout.addWidget(self.flow_diagram.toolbar)
        
        # 添加流程图编辑器
        center_layout.addWidget(self.flow_diagram)
        
        # 右侧：属性面板
        right_panel = QWidget()
        right_panel.setFixedWidth(250)  # 固定宽度
        right_panel.setStyleSheet("background-color: #f8f8f8;")
        
        # 创建右侧垂直布局，用于3:2比例分配
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 5, 5)
        right_layout.setSpacing(5)
        
        # 当前设备列表（占3份）
        current_equipment_group = QGroupBox("当前设备")
        current_equipment_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        current_equipment_layout = QVBoxLayout(current_equipment_group)
        
        self.current_equipment_table = QTableWidget()
        self.current_equipment_table.setColumnCount(2)
        self.current_equipment_table.setHorizontalHeaderLabels(["名称", "类型"])
        self.current_equipment_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.current_equipment_table.setAlternatingRowColors(True)
        self.current_equipment_table.horizontalHeader().setStretchLastSection(True)
        self.current_equipment_table.doubleClicked.connect(self.on_table_device_double_clicked)
        
        # 设置表格样式
        self.current_equipment_table.setStyleSheet("""
            QTableWidget {
                font-size: 10px;
                selection-background-color: #b0d0ff;
                selection-color: black;
            }
            QHeaderView::section {
                background-color: #e0e0e0;
                padding: 4px;
                border: 1px solid #ccc;
                font-weight: bold;
            }
        """)
        
        current_equipment_layout.addWidget(self.current_equipment_table)
        
        # 属性面板（占2份）
        properties_group = QGroupBox("属性详情")
        properties_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        properties_layout = QVBoxLayout(properties_group)
        
        self.properties_browser = QTextBrowser()
        self.properties_browser.setStyleSheet("""
            QTextBrowser {
                font-size: 11px;
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        properties_layout.addWidget(self.properties_browser)
        
        # 将两个组件添加到右侧布局，使用3:2的比例
        right_layout.addWidget(current_equipment_group, 3)  # 设备列表占3份
        right_layout.addWidget(properties_group, 2)  # 属性详情占2份
        
        # 将三个部分添加到主布局
        layout.addWidget(left_panel)
        layout.addWidget(center_widget)
        layout.addWidget(right_panel)
        
        # 设置布局比例
        layout.setStretch(0, 0)  # 左侧设备库固定宽度
        layout.setStretch(1, 1)  # 中间画布自适应
        layout.setStretch(2, 0)  # 右侧属性面板固定宽度
    
    def connect_signals(self):
        """连接信号"""
        # 设备添加信号
        self.flow_diagram.equipment_added.connect(self.on_equipment_added)
        self.flow_diagram.equipment_updated.connect(self.on_equipment_updated)
        self.flow_diagram.equipment_deleted.connect(self.on_equipment_deleted)
        
        # 选择变化
        self.flow_diagram.scene.selectionChanged.connect(self.on_selection_changed)
    
    def setup_scene_monitor(self):
        """设置场景变化监控"""
        # 监听场景变化
        self.flow_diagram.scene.changed.connect(self.on_scene_changed)
        
        # 设置修改标志
        self._modified = False
    
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
                    # 使用 get_inventory_equipment_type 方法来获取正确的设备清单类型
                    equipment_type = self.get_inventory_equipment_type(equipment.equipment_type)
                    
                    # 导入设备ID生成器
                    try:
                        from .equipment_id_generator import EquipmentIDGenerator
                        unique_code = EquipmentIDGenerator.generate_equipment_id(
                            equipment_type,
                            custom_seed=equipment.name
                        )
                    except ImportError:
                        # 如果导入失败，使用简单方法生成唯一编码
                        import uuid
                        unique_code = f"{equipment_type}_{str(uuid.uuid4())[:8].upper()}"
                    
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
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "错误", f"同步失败: {str(e)}")
    
    def add_equipment_from_inventory(self, equipment_data: dict):
        """从设备清单添加设备到流程图"""
        try:
            from ..utils import safe_float, safe_int, safe_str
            
            # 安全获取设备ID和名称
            equipment_id = safe_str(equipment_data.get("equipment_id", ""))
            if not equipment_id:
                print("❌ 设备ID为空，无法添加到流程图")
                return None
            
            equipment_name = safe_str(equipment_data.get("name", "设备"))
            unique_code = safe_str(equipment_data.get("unique_code", ""))
            
            # 使用类方法获取设备类型映射
            inventory_type = safe_str(equipment_data.get("type", "其他"))
            equipment_type = self.get_pfd_equipment_type(inventory_type)
            
            # 创建位置
            view_rect = self.flow_diagram.viewport().rect()
            center = self.flow_diagram.mapToScene(view_rect.center())
            
            # 获取设备位置（如果有）
            pos_x = safe_float(equipment_data.get("pfd_position_x", center.x()))
            pos_y = safe_float(equipment_data.get("pfd_position_y", center.y()))
            
            # 创建设备节点
            equipment = EquipmentNode(
                equipment_id,
                equipment_type,
                equipment_name,
                pos_x, pos_y
            )
            
            # 存储完整设备数据到节点
            equipment.full_data = equipment_data
            equipment.unique_code = unique_code
            equipment.inventory_type = inventory_type
            
            # 设置设备属性
            operating_temperature = equipment_data.get("operating_temperature")
            operating_pressure = equipment_data.get("operating_pressure")
            
            equipment.properties.update({
                "temperature": safe_float(operating_temperature, 25.0),
                "pressure": safe_float(operating_pressure, 101.325),
                "flow_rate": 0.0,
                "material": safe_str(equipment_data.get("material", "")),
                "status": safe_str(equipment_data.get("status", "normal"))
            })
            
            # 添加设计参数
            design_temperature = equipment_data.get("design_temperature")
            design_pressure = equipment_data.get("design_pressure")
            
            if design_temperature is not None:
                equipment.properties["design_temperature"] = safe_float(design_temperature)
            
            if design_pressure is not None:
                equipment.properties["design_pressure"] = safe_float(design_pressure)
            
            # 添加到场景
            self.flow_diagram.scene.addItem(equipment)
            self.flow_diagram.equipment_nodes[equipment_id] = equipment
            
            # 更新设备表格
            self.update_equipment_table()
            
            print(f"✅ 从设备清单添加设备到流程图成功: {equipment_name} ({equipment_id}, {unique_code})")
            return equipment
            
        except Exception as e:
            print(f"❌ 从设备清单添加设备到流程图时出错: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def on_save_button_clicked(self):
        """保存按钮点击事件"""
        try:
            if self.save_diagram_to_manager():
                self.status_label.setText("💾 已保存到数据库")
                QTimer.singleShot(3000, lambda: self.status_label.setText("就绪"))
                QMessageBox.information(self, "保存成功", "流程图已保存到数据库")
            else:
                self.status_label.setText("❌ 保存失败")
                QTimer.singleShot(3000, lambda: self.status_label.setText("就绪"))
        except Exception as e:
            print(f"❌ 保存流程图时出错: {e}")
            self.status_label.setText("❌ 保存出错")
            QTimer.singleShot(3000, lambda: self.status_label.setText("就绪"))
    
    def refresh_view(self):
        """刷新视图"""
        try:
            # 刷新设备表格
            self.update_equipment_table()
            
            # 刷新状态标签
            node_count = len(self.flow_diagram.equipment_nodes)
            connection_count = len(self.flow_diagram.material_connections)
            self.status_label.setText(f"✅ 刷新完成: {node_count} 设备, {connection_count} 连接")
            
            # 3秒后恢复状态
            QTimer.singleShot(3000, lambda: self.status_label.setText("就绪"))
            
        except Exception as e:
            print(f"❌ 刷新视图时出错: {e}")
            self.status_label.setText("❌ 刷新出错")
            QTimer.singleShot(3000, lambda: self.status_label.setText("就绪"))
    
    def add_equipment_from_library(self, equipment_type: str, position: QPointF = None):
        """从设备库添加设备到画布 - 同时创建设备清单数据"""
        try:
            # 获取设备信息
            equipment_info = EQUIPMENT_TYPE_DETAILED_MAPPING.get(equipment_type, {})
            
            # 获取设备清单类型
            inventory_type = equipment_info.get("inventory_type", "其他")
            
            # 打开设备对话框，让用户输入基本信息
            dialog = EquipmentDialog(self.parent_window)
            if dialog.exec() == QDialog.Accepted:
                # 获取设备对象
                equipment_item = dialog.get_equipment()
                
                # 设置设备类型（使用设备清单的类型）
                equipment_item.type = inventory_type
                
                # 设置一些默认值
                equipment_item.equipment_type = inventory_type
                equipment_item.dynamic = equipment_info.get("default_properties", {}).get("dynamic", "静设备")
                equipment_item.material = equipment_info.get("default_properties", {}).get("material", "")
                
                # 如果有默认功率，设置之
                if "single_power" in equipment_info.get("default_properties", {}):
                    equipment_item.single_power = equipment_info["default_properties"]["single_power"]
                    equipment_item.total_power = equipment_info["default_properties"]["total_power"]
                
                # 保存到数据管理器
                if self.data_manager:
                    success = self.data_manager.add_equipment(equipment_item.to_dict())
                    if not success:
                        QMessageBox.warning(self, "错误", "保存设备到数据库失败")
                        return
                        
                # 在流程图中创建节点
                if position is None:
                    view_rect = self.flow_diagram.viewport().rect()
                    center = self.flow_diagram.mapToScene(view_rect.center())
                    pos = center
                else:
                    pos = position
                
                # 创建设备节点
                equipment_node = EquipmentNode(
                    equipment_item.equipment_id,
                    equipment_type,
                    equipment_item.name,
                    pos.x(), pos.y()
                )
                
                # 存储完整设备数据到节点
                equipment_node.full_data = equipment_item.to_dict()
                equipment_node.unique_code = equipment_item.unique_code
                equipment_node.inventory_type = inventory_type
                
                # 设置设备属性
                equipment_node.properties.update({
                    "temperature": float(equipment_item.operating_temperature or 25),
                    "pressure": float(equipment_item.operating_pressure or 101.325),
                    "flow_rate": 0.0,
                    "material": equipment_item.material,
                    "status": "normal"
                })
                
                # 添加到场景
                self.flow_diagram.scene.addItem(equipment_node)
                self.flow_diagram.equipment_nodes[equipment_item.equipment_id] = equipment_node
                
                # 发送信号
                self.flow_diagram.equipment_added.emit({
                    "equipment_id": equipment_item.equipment_id,
                    "unique_code": equipment_item.unique_code,
                    "equipment_type": equipment_type,
                    "inventory_type": inventory_type,
                    "name": equipment_item.name,
                    "position": {"x": pos.x(), "y": pos.y()},
                    "properties": equipment_node.properties
                })
                
                # 更新设备表格
                self.update_equipment_table()
                
                QMessageBox.information(self, "成功", f"设备 '{equipment_item.name}' 已添加到流程图和设备清单")
        except Exception as e:
            print(f"❌ 从设备库添加设备时出错: {e}")
            import traceback
            traceback.print_exc()
    
    def on_table_device_double_clicked(self, index):
        """表格中设备双击事件 - 选中流程图中对应的设备"""
        if index.isValid():
            row = index.row()
            if row < self.current_equipment_table.rowCount():
                equipment_name = self.current_equipment_table.item(row, 0).text()
                
                # 查找对应的设备节点
                for eq_id, equipment in self.flow_diagram.equipment_nodes.items():
                    if equipment.name == equipment_name:
                        # 清除之前的选择
                        self.flow_diagram.scene.clearSelection()
                        
                        # 选中该设备
                        equipment.setSelected(True)
                        
                        # 滚动到该设备
                        self.flow_diagram.centerOn(equipment)
                        
                        # 更新属性显示
                        self.on_selection_changed()
                        break
    
    def on_equipment_added(self, equipment_data: dict):
        """设备添加事件"""
        self.update_equipment_table()
        
        # 如果需要，可以在这里同步到设备清单模块
        print(f"设备添加: {equipment_data}")
    
    def on_equipment_updated(self, equipment_data: dict):
        """设备更新事件"""
        self.update_equipment_table()
        
        # 同步到设备清单模块
        print(f"设备更新: {equipment_data}")
    
    def on_equipment_deleted(self, equipment_id: str):
        """设备删除事件"""
        self.update_equipment_table()
        
        # 同步到设备清单模块
        print(f"设备删除: {equipment_id}")
    
    def on_selection_changed(self):
        """选择变化事件"""
        selected_items = self.flow_diagram.scene.selectedItems()
        
        if not selected_items:
            self.properties_browser.clear()
            return
        
        item = selected_items[0]
        
        if isinstance(item, EquipmentNode):
            # 显示设备属性
            html = f"""
            <div style="font-family: Arial, sans-serif;">
                <h3 style="color: #2c3e50; margin-bottom: 10px;">{item.name}</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 4px; border-bottom: 1px solid #eee;"><b>设备ID:</b></td>
                        <td style="padding: 4px; border-bottom: 1px solid #eee;">{item.equipment_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px; border-bottom: 1px solid #eee;"><b>类型:</b></td>
                        <td style="padding: 4px; border-bottom: 1px solid #eee;">{EQUIPMENT_TYPES.get(item.equipment_type, {}).get('name', '未知')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px; border-bottom: 1px solid #eee;"><b>温度:</b></td>
                        <td style="padding: 4px; border-bottom: 1px solid #eee;">{item.properties.get('temperature', 0)} °C</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px; border-bottom: 1px solid #eee;"><b>压力:</b></td>
                        <td style="padding: 4px; border-bottom: 1px solid #eee;">{item.properties.get('pressure', 0)} kPa</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px; border-bottom: 1px solid #eee;"><b>体积:</b></td>
                        <td style="padding: 4px; border-bottom: 1px solid #eee;">{item.properties.get('volume', 0)} m³</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px; border-bottom: 1px solid #eee;"><b>流量:</b></td>
                        <td style="padding: 4px; border-bottom: 1px solid #eee;">{item.properties.get('flow_rate', 0)} kg/h</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px; border-bottom: 1px solid #eee;"><b>物料:</b></td>
                        <td style="padding: 4px; border-bottom: 1px solid #eee;">{item.properties.get('material', '未指定')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px;"><b>状态:</b></td>
                        <td style="padding: 4px;">{item.properties.get('status', 'normal')}</td>
                    </tr>
                </table>
            </div>
            """
            self.properties_browser.setHtml(html)
        
        elif isinstance(item, MaterialConnection):
            # 显示连接属性
            html = f"""
            <div style="font-family: Arial, sans-serif;">
                <h3 style="color: #2c3e50; margin-bottom: 10px;">物料连接</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 4px; border-bottom: 1px solid #eee;"><b>从:</b></td>
                        <td style="padding: 4px; border-bottom: 1px solid #eee;">{item.source.name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px; border-bottom: 1px solid #eee;"><b>到:</b></td>
                        <td style="padding: 4px; border-bottom: 1px solid #eee;">{item.target.name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px; border-bottom: 1px solid #eee;"><b>物料:</b></td>
                        <td style="padding: 4px; border-bottom: 1px solid #eee;">{item.material_name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px; border-bottom: 1px solid #eee;"><b>类型:</b></td>
                        <td style="padding: 4px; border-bottom: 1px solid #eee;">{MATERIAL_TYPES.get(item.material_type, {}).get('name', '未知')}</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px; border-bottom: 1px solid #eee;"><b>流量:</b></td>
                        <td style="padding: 4px; border-bottom: 1px solid #eee;">{item.properties.get('flow_rate', 0)} kg/h</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px; border-bottom: 1px solid #eee;"><b>温度:</b></td>
                        <td style="padding: 4px; border-bottom: 1px solid #eee;">{item.properties.get('temperature', 0)} °C</td>
                    </tr>
                    <tr>
                        <td style="padding: 4px;"><b>压力:</b></td>
                        <td style="padding: 4px;">{item.properties.get('pressure', 0)} kPa</td>
                    </tr>
                </table>
            </div>
            """
            self.properties_browser.setHtml(html)
    
    def update_equipment_table(self):
        """更新设备表格"""
        self.current_equipment_table.setRowCount(len(self.flow_diagram.equipment_nodes))
        
        for i, (eq_id, equipment) in enumerate(self.flow_diagram.equipment_nodes.items()):
            self.current_equipment_table.setItem(i, 0, QTableWidgetItem(equipment.name))
            
            type_name = EQUIPMENT_TYPES.get(equipment.equipment_type, {}).get("name", "未知")
            self.current_equipment_table.setItem(i, 1, QTableWidgetItem(type_name))
            
            # 显示唯一编码
            unique_code = getattr(equipment, 'unique_code', '')
            self.current_equipment_table.setItem(i, 2, QTableWidgetItem(unique_code))
        
        # 设置表格头
        self.current_equipment_table.setHorizontalHeaderLabels(["设备名称", "PFD类型", "唯一编码"])
        
        # 调整表格列宽
        self.current_equipment_table.horizontalHeader().setStretchLastSection(True)
        for i in range(self.current_equipment_table.columnCount()):
            self.current_equipment_table.resizeColumnToContents(i)
        
        # 调整表格行高
        for i in range(self.current_equipment_table.rowCount()):
            self.current_equipment_table.setRowHeight(i, 24)
    
    def setup_auto_save(self):
        """设置自动保存"""
        # 创建自动保存定时器
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self.auto_save_diagram)
        self.auto_save_timer.start(30000)  # 每30秒自动保存一次
        
        # 连接场景变化信号
        self.flow_diagram.scene.changed.connect(self.on_scene_changed)
    
    def on_scene_changed(self):
        """场景变化时标记为已修改"""
        self._modified = True
    
    def auto_save_diagram(self):
        """自动保存流程图"""
        if self.needs_save:
            self.save_diagram_to_manager()
            self.needs_save = False
            print("🔄 流程图已自动保存")
    
    def save_diagram_to_manager(self) -> bool:
        """保存流程图到数据管理器"""
        if not self.data_manager:
            print("❌ 数据管理器未初始化")
            return False
            
        try:
            # 获取当前流程图数据
            diagram_data = self.get_current_diagram_data()
            
            # 从数据管理器获取 ProcessDesignManager
            if hasattr(self.data_manager, 'process_design_manager'):
                process_manager = self.data_manager.process_design_manager
            else:
                # 尝试创建 ProcessDesignManager
                from process_design.process_design_manager import ProcessDesignManager
                process_manager = ProcessDesignManager(self.data_manager)
                self.data_manager.process_design_manager = process_manager
            
            # 保存到数据管理器
            if process_manager.save_flow_diagram(diagram_data):
                print("✅ 流程图数据已保存到管理器")
                return True
            else:
                print("❌ 流程图数据保存失败")
                return False
                
        except Exception as e:
            print(f"❌ 保存流程图数据时出错: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_current_diagram_data(self) -> Dict[str, Any]:
        """获取当前流程图的数据"""
        try:
            diagram_data = {
                "nodes": [],
                "connections": [],
                "metadata": {
                    "saved_at": datetime.now().isoformat(),
                    "node_count": len(self.flow_diagram.equipment_nodes),
                    "connection_count": len(self.flow_diagram.material_connections),
                    "version": "1.0"
                }
            }
            
            # 保存设备节点
            for equipment_id, equipment in self.flow_diagram.equipment_nodes.items():
                node_data = {
                    "id": equipment_id,
                    "type": equipment.equipment_type,
                    "name": equipment.name,
                    "position": {
                        "x": float(equipment.pos().x()),
                        "y": float(equipment.pos().y())
                    },
                    "properties": equipment.properties,
                    "inventory_data": getattr(equipment, 'full_data', {})
                }
                diagram_data["nodes"].append(node_data)
            
            # 保存连接线
            for connection in self.flow_diagram.material_connections:
                conn_data = {
                    "source": connection.source.equipment_id,
                    "source_point": connection.source_point,
                    "target": connection.target.equipment_id,
                    "target_point": connection.target_point,
                    "material_type": connection.material_type,
                    "material_name": connection.material_name,
                    "properties": connection.properties
                }
                diagram_data["connections"].append(conn_data)
            
            return diagram_data
            
        except Exception as e:
            print(f"❌ 获取流程图数据时出错: {e}")
            return {"nodes": [], "connections": [], "metadata": {}}
    
    def load_data(self):
        """加载数据（供主窗口调用）"""
        try:
            if not self.data_manager:
                print("❌ 数据管理器未初始化，无法加载流程图数据")
                return False
            
            # 从数据管理器加载
            self.load_from_data_manager()
            return True
            
        except Exception as e:
            print(f"❌ 加载流程图数据时出错: {e}")
            return False
    
    def load_from_data_manager(self):
        """从数据管理器加载数据"""
        try:
            # 清空当前场景
            self.flow_diagram.clear_diagram()
            
            # 获取ProcessDesignManager
            if not hasattr(self.data_manager, 'process_design_manager'):
                from process_design.process_design_manager import ProcessDesignManager
                self.data_manager.process_design_manager = ProcessDesignManager(self.data_manager)
            
            # 加载流程图数据
            diagram_data = self.data_manager.process_design_manager.load_flow_diagram()
            
            if not diagram_data:
                print("📝 没有找到保存的流程图数据")
                return
            
            # 加载节点
            for node_data in diagram_data.get("nodes", []):
                try:
                    node_id = node_data.get("id")
                    node_type = node_data.get("type", "vessel")
                    node_name = node_data.get("name", "设备")
                    position = node_data.get("position", {"x": 0, "y": 0})
                    
                    # 创建设备节点
                    equipment = EquipmentNode(
                        node_id, node_type, node_name,
                        position.get("x", 0), position.get("y", 0)
                    )
                    
                    # 设置属性
                    equipment.properties = node_data.get("properties", {})
                    
                    # 如果有库存数据，保存起来
                    inventory_data = node_data.get("inventory_data", {})
                    if inventory_data:
                        equipment.full_data = inventory_data
                        equipment.unique_code = inventory_data.get("unique_code", "")
                        equipment.inventory_type = inventory_data.get("type", "")
                    
                    # 添加到场景
                    self.flow_diagram.scene.addItem(equipment)
                    self.flow_diagram.equipment_nodes[node_id] = equipment
                    
                except Exception as e:
                    print(f"⚠️ 加载节点 {node_data.get('id', '未知')} 失败: {e}")
                    continue
            
            # 加载连接线
            for conn_data in diagram_data.get("connections", []):
                try:
                    source = self.flow_diagram.equipment_nodes.get(conn_data.get("source"))
                    target = self.flow_diagram.equipment_nodes.get(conn_data.get("target"))
                    
                    if source and target:
                        connection = MaterialConnection(
                            source, conn_data.get("source_point", "outlet"),
                            target, conn_data.get("target_point", "inlet"),
                            conn_data.get("material_type", "liquid"),
                            conn_data.get("material_name", "")
                        )
                        connection.properties = conn_data.get("properties", {})
                        
                        self.flow_diagram.scene.addItem(connection)
                        self.flow_diagram.material_connections.append(connection)
                        
                except Exception as e:
                    print(f"⚠️ 加载连接线失败: {e}")
                    continue
            
            # 更新设备表格
            self.update_equipment_table()
            
            print(f"✅ 流程图加载完成: {len(diagram_data.get('nodes', []))} 个节点, "
                f"{len(diagram_data.get('connections', []))} 条连接")
            
        except Exception as e:
            print(f"❌ 从数据管理器加载数据失败: {e}")
    
    def load_saved_diagram(self):
        """加载保存的流程图"""
        if not self.data_manager:
            print("❌ 数据管理器未初始化")
            return
        
        try:
            # 从数据管理器获取 ProcessDesignManager
            if hasattr(self.data_manager, 'process_design_manager'):
                process_manager = self.data_manager.process_design_manager
            else:
                from process_design.process_design_manager import ProcessDesignManager
                process_manager = ProcessDesignManager(self.data_manager)
                self.data_manager.process_design_manager = process_manager
            
            # 加载数据
            diagram_data = process_manager.load_flow_diagram()
            
            if not diagram_data or "nodes" not in diagram_data:
                print("📝 没有找到保存的流程图数据，开始新的流程图")
                return
            
            print(f"📂 加载保存的流程图数据: {len(diagram_data.get('nodes', []))} 个节点")
            
            # 清空当前场景
            self.flow_diagram.clear_diagram()
            
            # 加载节点
            for node_data in diagram_data.get("nodes", []):
                try:
                    node_id = node_data.get("id")
                    node_type = node_data.get("type", "vessel")
                    node_name = node_data.get("name", "设备")
                    position = node_data.get("position", {"x": 0, "y": 0})
                    
                    # 创建设备节点
                    equipment = EquipmentNode(
                        node_id, node_type, node_name,
                        position.get("x", 0), position.get("y", 0)
                    )
                    
                    # 设置属性
                    equipment.properties = node_data.get("properties", {})
                    
                    # 添加到场景
                    self.flow_diagram.scene.addItem(equipment)
                    self.flow_diagram.equipment_nodes[node_id] = equipment
                    
                except Exception as e:
                    print(f"⚠️ 加载节点 {node_data.get('id', '未知')} 失败: {e}")
                    continue
            
            # 加载连接线
            for conn_data in diagram_data.get("connections", []):
                try:
                    source = self.flow_diagram.equipment_nodes.get(conn_data.get("source"))
                    target = self.flow_diagram.equipment_nodes.get(conn_data.get("target"))
                    
                    if source and target:
                        connection = MaterialConnection(
                            source, conn_data.get("source_point", "outlet"),
                            target, conn_data.get("target_point", "inlet"),
                            conn_data.get("material_type", "liquid"),
                            conn_data.get("material_name", "")
                        )
                        connection.properties = conn_data.get("properties", {})
                        
                        self.flow_diagram.scene.addItem(connection)
                        self.flow_diagram.material_connections.append(connection)
                        
                except Exception as e:
                    print(f"⚠️ 加载连接线失败: {e}")
                    continue
            
            # 恢复视口设置
            viewport = diagram_data.get("viewport", {})
            if viewport:
                try:
                    center_x = viewport.get("center_x", 0)
                    center_y = viewport.get("center_y", 0)
                    scale = viewport.get("scale", 1.0)
                    
                    # 设置缩放
                    self.flow_diagram.resetTransform()
                    self.flow_diagram.scale(scale, scale)
                    
                    # 居中显示
                    self.flow_diagram.centerOn(center_x, center_y)
                    
                except Exception as e:
                    print(f"⚠️ 恢复视口设置失败: {e}")
            
            # 更新设备表格
            self.update_equipment_table()
            
            print(f"✅ 流程图加载完成: {len(diagram_data.get('nodes', []))} 个节点, "
                f"{len(diagram_data.get('connections', []))} 条连接")
            
        except Exception as e:
            print(f"❌ 加载流程图数据失败: {e}")
            import traceback
            traceback.print_exc()
    
    def save_data(self):
        """保存数据（供主窗口调用）"""
        try:
            if not self.data_manager:
                print("❌ 数据管理器未初始化，无法保存流程图数据")
                return False
            
            # 获取当前流程图数据
            diagram_data = self.get_current_diagram_data()
            
            # 保存到数据管理器
            success = self.save_to_data_manager(diagram_data)
            
            if success:
                self._modified = False
                print("✅ 流程图数据保存成功")
                return True
            else:
                print("❌ 流程图数据保存失败")
                return False
                
        except Exception as e:
            print(f"❌ 保存流程图数据时出错: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def save_to_data_manager(self, diagram_data):
        """保存数据到数据管理器"""
        try:
            # 获取或创建ProcessDesignManager
            if not hasattr(self.data_manager, 'process_design_manager'):
                from process_design.process_design_manager import ProcessDesignManager
                self.data_manager.process_design_manager = ProcessDesignManager(self.data_manager)
            
            # 保存数据
            return self.data_manager.process_design_manager.save_flow_diagram(diagram_data)
        except Exception as e:
            print(f"❌ 保存到数据管理器失败: {e}")
            return False
    
    def on_activate(self):
        """模块激活时调用"""
        print("🔄 工艺流程图模块已激活")
        
        # 刷新设备表格
        self.update_equipment_table()
    
    def sync_equipment_to_inventory(self, equipment_node: EquipmentNode):
        """将流程图中的设备同步到设备清单"""
        if not self.data_manager or not equipment_node.unique_code:
            return
        
        try:
            # 获取设备数据
            equipment_data = {
                "equipment_id": equipment_node.equipment_id,
                "unique_code": equipment_node.unique_code,
                "name": equipment_node.name,
                "type": equipment_node.inventory_type,
                "pfd_position_x": equipment_node.x(),
                "pfd_position_y": equipment_node.y(),
                "status": equipment_node.properties.get("status", "active")
            }
            
            # 添加其他属性
            for key in ["temperature", "pressure", "flow_rate", "material"]:
                if key in equipment_node.properties:
                    equipment_data[key] = equipment_node.properties[key]
            
            # 检查设备是否已存在
            existing_data = self.data_manager.get_equipment_by_unique_code(equipment_node.unique_code)
            if existing_data:
                # 更新现有设备
                existing_data.update(equipment_data)
                self.data_manager.update_equipment(equipment_node.equipment_id, existing_data)
            else:
                # 添加新设备
                self.data_manager.add_equipment(equipment_data)
                
        except Exception as e:
            print(f"❌ 同步设备到设备清单时出错: {e}")
    
    def sync_inventory_to_flow_diagram(self, equipment_data: dict):
        """将设备清单的设备同步到流程图"""
        try:
            equipment_id = equipment_data.get("equipment_id")
            if not equipment_id:
                return
            
            # 检查设备是否已在流程图中
            if equipment_id in self.flow_diagram.equipment_nodes:
                # 更新现有设备
                equipment_node = self.flow_diagram.equipment_nodes[equipment_id]
                equipment_node.name = equipment_data.get("name", equipment_node.name)
                
                # 更新属性
                if "temperature" in equipment_data:
                    equipment_node.properties["temperature"] = float(equipment_data["temperature"])
                if "pressure" in equipment_data:
                    equipment_node.properties["pressure"] = float(equipment_data["pressure"])
                
                equipment_node.update()
            else:
                # 添加新设备
                self.add_equipment_from_inventory(equipment_data)
                
        except Exception as e:
            print(f"❌ 同步设备清单到流程图时出错: {e}")