# modules/process_design/tabs/equipment_list_tab.py
import sys
import os

# 设置模块路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # 父目录 (process_design)
grandparent_dir = os.path.dirname(parent_dir)  # 祖父目录 (modules)

# 添加必要的路径到sys.path
paths_to_add = [
    current_dir,      # 当前目录
    parent_dir,       # 父目录（TofuApp\modules\process_design）
    grandparent_dir   # 祖父目录（TofuApp\modules）
]

for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)

# 导入 Qt 相关
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QDoubleSpinBox, QComboBox, QTextEdit, QGroupBox,
    QCheckBox, QFileDialog, QProgressDialog, QSplitter, QTabWidget,
    QMenu, QApplication, QFrame, QToolBar, QSizePolicy, QDialogButtonBox,
    QSpinBox
)
from PySide6.QtCore import Qt, Signal, QTimer, QThread, QSize
from PySide6.QtGui import QAction, QKeySequence, QClipboard

# 导入其他库
import csv
import json
import pandas as pd
import re
from typing import List, Optional, Dict, Any
from datetime import datetime

# 尝试导入工艺设计相关模块
try:
    from ..process_design_manager import ProcessDesignManager
    from ..process_design_data import EquipmentItem
    print("✅ 成功导入 ProcessDesignManager 和 EquipmentItem")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    
    # 创建占位符类
    class ProcessDesignManager:
        def __init__(self, *args, **kwargs):
            pass
        def get_all_equipment(self):
            return []
        def get_equipment(self, equipment_id):
            return None
        def add_equipment(self, equipment):
            return False
        def update_equipment(self, equipment):
            return False
        def delete_equipment(self, equipment_id):
            return False
        def search_equipment(self, search_term):
            return []
        def advanced_search_equipment(self, criteria):
            return []
    
    class EquipmentItem:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

class EquipmentListTab(QWidget):
    """设备列表标签页"""
    
    equipment_selected = Signal(str)  # 设备选择信号
    equipment_list_updated = Signal()  # 设备列表更新信号
    import_progress = Signal(int)  # 导入进度信号
    
    def __init__(self, data_manager=None, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.process_manager = None
        self.current_equipment = []  # 当前显示的设备列表
        self.selected_rows = set()  # 选中的行
        self.batch_mode = False  # 批量操作模式
        
        # 延迟初始化process_manager
        if data_manager:
            try:
                self.process_manager = ProcessDesignManager(data_manager)
                print("✅ 设备列表: ProcessDesignManager 初始化成功")
            except Exception as e:
                print(f"❌ 设备列表: ProcessDesignManager 初始化失败: {e}")
                self.process_manager = None
        
        self.setup_ui()
        self.load_equipment()
        self.setup_shortcuts()
    
    def setup_ui(self):
        """设置UI"""
        main_layout = QVBoxLayout(self)
        
        # 工具栏
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(16, 16))
        
        # 工具栏动作
        self.add_action = QAction("添加", self)
        self.add_action.triggered.connect(self.add_equipment)
        toolbar.addAction(self.add_action)
        
        self.edit_action = QAction("编辑", self)
        self.edit_action.triggered.connect(self.edit_equipment)
        toolbar.addAction(self.edit_action)
        
        self.delete_action = QAction("删除", self)
        self.delete_action.triggered.connect(self.delete_equipment)
        toolbar.addAction(self.delete_action)
        
        toolbar.addSeparator()
        
        self.import_action = QAction("导入", self)
        self.import_action.triggered.connect(self.import_equipment)
        toolbar.addAction(self.import_action)
        
        self.export_action = QAction("导出", self)
        self.export_action.triggered.connect(self.export_equipment)
        toolbar.addAction(self.export_action)
        
        toolbar.addSeparator()
        
        self.batch_toggle_action = QAction("批量模式", self)
        self.batch_toggle_action.setCheckable(True)
        self.batch_toggle_action.toggled.connect(self.toggle_batch_mode)
        toolbar.addAction(self.batch_toggle_action)
        
        toolbar.addSeparator()
        
        self.mapping_action = QAction("对照表", self)
        self.mapping_action.triggered.connect(self.manage_name_mapping)
        toolbar.addAction(self.mapping_action)
        
        main_layout.addWidget(toolbar)
        
        # 搜索和过滤区域
        filter_frame = QFrame()
        filter_frame.setFrameStyle(QFrame.StyledPanel)
        filter_layout = QHBoxLayout(filter_frame)
        
        # 搜索框
        search_layout = QHBoxLayout()
        search_label = QLabel("搜索:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("设备名称、型号或编号...")
        self.search_input.textChanged.connect(self.on_search_changed)
        self.search_input.returnPressed.connect(self.perform_search)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        
        # 高级搜索按钮
        self.advanced_search_btn = QPushButton("高级搜索")
        self.advanced_search_btn.clicked.connect(self.open_advanced_search)
        search_layout.addWidget(self.advanced_search_btn)
        
        filter_layout.addLayout(search_layout)
        
        # 过滤器
        filter_layout.addStretch()
        
        # 设备类型过滤器
        self.type_filter = QComboBox()
        self.type_filter.addItem("所有类型")
        self.type_filter.addItems(["反应器", "分离器", "换热器", "泵", "压缩机", "储罐", "阀门", "管道", "其他"])
        self.type_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(QLabel("设备类型:"))
        filter_layout.addWidget(self.type_filter)
        
        # 状态过滤器
        self.status_filter = QComboBox()
        self.status_filter.addItem("所有状态")
        self.status_filter.addItems(["运行中", "停机", "维修中", "备用"])
        self.status_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(QLabel("状态:"))
        filter_layout.addWidget(self.status_filter)
        
        main_layout.addWidget(filter_frame)
        
        # 分割器：左侧表格，右侧详情
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：设备表格
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        
        # 表格上方信息栏
        info_layout = QHBoxLayout()
        self.info_label = QLabel("总计: 0 个设备")
        info_layout.addWidget(self.info_label)
        info_layout.addStretch()
        
        self.selected_label = QLabel("已选择: 0 个")
        info_layout.addWidget(self.selected_label)
        table_layout.addLayout(info_layout)
        
        # 设备表格
        self.equipment_table = QTableWidget()
        self.equipment_table.setColumnCount(13)
        self.equipment_table.setHorizontalHeaderLabels([
            "",  # 选择框
            "设备ID", "设备名称", "设备类型", "型号", "规格", 
            "制造商", "安装位置", "状态", "投用日期", 
            "设计压力", "设计温度", "备注"
        ])
        
        # 设置表头
        header = self.equipment_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # 选择列固定宽度
        header.resizeSection(0, 30)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # ID列自适应
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # 名称列拉伸
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 类型
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 型号
        
        # 启用排序
        self.equipment_table.setSortingEnabled(True)
        
        # 设置选择模式
        self.equipment_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.equipment_table.setSelectionMode(QTableWidget.ExtendedSelection)
        
        # 连接信号
        self.equipment_table.itemDoubleClicked.connect(self.on_equipment_double_clicked)
        self.equipment_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        table_layout.addWidget(self.equipment_table)
        
        splitter.addWidget(table_widget)
        
        # 右侧：设备详情
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        
        # 详情标签
        detail_label = QLabel("设备详情")
        detail_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        detail_layout.addWidget(detail_label)
        
        # 详情显示区域
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMaximumHeight(300)
        detail_layout.addWidget(self.detail_text)
        
        # 技术参数标签
        property_label = QLabel("技术参数")
        property_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        detail_layout.addWidget(property_label)
        
        # 技术参数表格
        self.property_table = QTableWidget()
        self.property_table.setColumnCount(2)
        self.property_table.setHorizontalHeaderLabels(["参数", "值"])
        self.property_table.horizontalHeader().setStretchLastSection(True)
        self.property_table.setEditTriggers(QTableWidget.NoEditTriggers)
        detail_layout.addWidget(self.property_table)
        
        splitter.addWidget(detail_widget)
        splitter.setSizes([700, 300])  # 设置初始大小比例
        
        main_layout.addWidget(splitter)
        
        # 批量操作按钮（初始隐藏）
        self.batch_panel = QFrame()
        self.batch_panel.setFrameStyle(QFrame.StyledPanel)
        self.batch_panel.setVisible(False)
        batch_layout = QHBoxLayout(self.batch_panel)
        
        self.batch_edit_btn = QPushButton("批量编辑")
        self.batch_edit_btn.clicked.connect(self.batch_edit_equipment)
        batch_layout.addWidget(self.batch_edit_btn)
        
        self.batch_export_btn = QPushButton("批量导出")
        self.batch_export_btn.clicked.connect(self.batch_export_equipment)
        batch_layout.addWidget(self.batch_export_btn)
        
        self.batch_delete_btn = QPushButton("批量删除")
        self.batch_delete_btn.clicked.connect(self.batch_delete_equipment)
        batch_layout.addWidget(self.batch_delete_btn)
        
        batch_layout.addStretch()
        
        self.clear_batch_btn = QPushButton("清除选择")
        self.clear_batch_btn.clicked.connect(self.clear_batch_selection)
        batch_layout.addWidget(self.clear_batch_btn)
        
        main_layout.addWidget(self.batch_panel)
        
        # 状态栏
        self.status_bar = QLabel()
        self.status_bar.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        main_layout.addWidget(self.status_bar)
    
    def setup_shortcuts(self):
        """设置快捷键"""
        # 复制快捷键
        self.copy_action = QAction("复制", self)
        self.copy_action.setShortcut(QKeySequence.Copy)
        self.copy_action.triggered.connect(self.copy_selected)
        self.addAction(self.copy_action)
        
        # 刷新快捷键
        self.refresh_action = QAction("刷新", self)
        self.refresh_action.setShortcut(QKeySequence.Refresh)
        self.refresh_action.triggered.connect(self.load_equipment)
        self.addAction(self.refresh_action)
    
    def load_equipment(self):
        """加载设备数据"""
        if not self.process_manager:
            self.status_bar.setText("错误: 数据管理器未初始化")
            return
        
        try:
            self.current_equipment = self.process_manager.get_all_equipment()
            self.populate_table(self.current_equipment)
            self.update_info_label()
            self.status_bar.setText(f"数据加载完成: {len(self.current_equipment)} 条记录")
        except Exception as e:
            self.status_bar.setText(f"加载失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"加载设备数据时发生错误:\n{str(e)}")
    
    def populate_table(self, equipment_list):
        """填充表格数据"""
        self.equipment_table.setRowCount(len(equipment_list))
        
        for i, equipment in enumerate(equipment_list):
            # 选择框
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            checkbox_item.setCheckState(Qt.Unchecked)
            self.equipment_table.setItem(i, 0, checkbox_item)
            
            # 设备数据
            self.equipment_table.setItem(i, 1, QTableWidgetItem(equipment.equipment_id))
            self.equipment_table.setItem(i, 2, QTableWidgetItem(equipment.name))
            self.equipment_table.setItem(i, 3, QTableWidgetItem(equipment.equipment_type if hasattr(equipment, 'equipment_type') else equipment.type))
            self.equipment_table.setItem(i, 4, QTableWidgetItem(equipment.model))
            self.equipment_table.setItem(i, 5, QTableWidgetItem(equipment.specification))
            self.equipment_table.setItem(i, 6, QTableWidgetItem(equipment.manufacturer))
            self.equipment_table.setItem(i, 7, QTableWidgetItem(equipment.location))
            self.equipment_table.setItem(i, 8, QTableWidgetItem(equipment.status))
            
            # 日期格式化
            if hasattr(equipment, 'commission_date') and equipment.commission_date:
                date_str = equipment.commission_date.strftime("%Y-%m-%d") if hasattr(equipment.commission_date, 'strftime') else str(equipment.commission_date)
            else:
                date_str = ""
            self.equipment_table.setItem(i, 9, QTableWidgetItem(date_str))
            
            # 设计参数
            self.equipment_table.setItem(i, 10, QTableWidgetItem(
                f"{equipment.design_pressure:.2f}" if hasattr(equipment, 'design_pressure') and equipment.design_pressure else ""
            ))
            self.equipment_table.setItem(i, 11, QTableWidgetItem(
                f"{equipment.design_temperature:.1f}" if hasattr(equipment, 'design_temperature') and equipment.design_temperature else ""
            ))
            self.equipment_table.setItem(i, 12, QTableWidgetItem(equipment.notes or ""))
        
        self.update_info_label()
    
    def update_info_label(self):
        """更新信息标签"""
        total = self.equipment_table.rowCount()
        selected = len([i for i in range(total) 
                       if self.equipment_table.item(i, 0).checkState() == Qt.Checked])
        self.info_label.setText(f"总计: {total} 个设备")
        self.selected_label.setText(f"已选择: {selected} 个")
    
    def on_search_changed(self):
        """搜索内容变化 - 防抖处理"""
        if hasattr(self, '_search_timer'):
            self._search_timer.stop()
        
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self.perform_search)
        self._search_timer.start(500)  # 500ms防抖
    
    def perform_search(self):
        """执行搜索"""
        search_term = self.search_input.text().strip()
        if not self.process_manager:
            return
        
        try:
            if not search_term:
                equipment_list = self.process_manager.get_all_equipment()
            else:
                equipment_list = self.process_manager.search_equipment(search_term)
            
            self.current_equipment = equipment_list
            self.apply_filters()  # 应用当前过滤器
            self.status_bar.setText(f"搜索到 {len(equipment_list)} 条记录")
        except Exception as e:
            self.status_bar.setText(f"搜索失败: {str(e)}")
    
    def apply_filters(self):
        """应用过滤器"""
        type_filter = self.type_filter.currentText()
        status_filter = self.status_filter.currentText()
        
        filtered_equipment = self.current_equipment.copy()
        
        # 应用设备类型过滤
        if type_filter != "所有类型":
            filtered_equipment = [e for e in filtered_equipment if e.equipment_type == type_filter]
        
        # 应用状态过滤
        if status_filter != "所有状态":
            filtered_equipment = [e for e in filtered_equipment if e.status == status_filter]
        
        self.populate_table(filtered_equipment)
    
    def open_advanced_search(self):
        """打开高级搜索对话框"""
        dialog = AdvancedSearchDialog(self)
        if dialog.exec() == QDialog.Accepted:
            criteria = dialog.get_search_criteria()
            self.perform_advanced_search(criteria)
    
    def perform_advanced_search(self, criteria):
        """执行高级搜索"""
        if not self.process_manager:
            return
        
        try:
            equipment_list = self.process_manager.advanced_search_equipment(criteria)
            self.current_equipment = equipment_list
            self.populate_table(equipment_list)
            self.status_bar.setText(f"高级搜索找到 {len(equipment_list)} 条记录")
        except Exception as e:
            self.status_bar.setText(f"高级搜索失败: {str(e)}")
            QMessageBox.warning(self, "搜索失败", str(e))
    
    def on_equipment_double_clicked(self, item):
        """设备双击事件"""
        if item.column() == 0:  # 点击选择框时不触发
            return
        
        row = item.row()
        equipment_id = self.equipment_table.item(row, 1).text()
        self.show_equipment_details(equipment_id)
        self.equipment_selected.emit(equipment_id)
    
    def show_equipment_details(self, equipment_id):
        """显示设备详情"""
        if not self.process_manager:
            return
        
        equipment = self.process_manager.get_equipment(equipment_id)
        if not equipment:
            return
        
        # 显示基本信息
        details = f"<h3>{equipment.name} ({equipment.equipment_id})</h3>"
        details += f"<b>设备类型:</b> {equipment.equipment_type if hasattr(equipment, 'equipment_type') else equipment.type}<br>"
        details += f"<b>型号:</b> {equipment.model}<br>"
        details += f"<b>规格:</b> {equipment.specification}<br>"
        details += f"<b>制造商:</b> {equipment.manufacturer}<br>"
        details += f"<b>安装位置:</b> {equipment.location}<br>"
        details += f"<b>状态:</b> {equipment.status}<br>"
        
        if hasattr(equipment, 'commission_date') and equipment.commission_date:
            details += f"<b>投用日期:</b> {equipment.commission_date.strftime('%Y-%m-%d') if hasattr(equipment.commission_date, 'strftime') else equipment.commission_date}<br>"
        
        if equipment.notes:
            details += f"<br><b>备注:</b><br>{equipment.notes}"
        
        self.detail_text.setHtml(details)
        
        # 显示技术参数表格
        properties = [
            ("设计压力", f"{equipment.design_pressure:.2f} MPa" if hasattr(equipment, 'design_pressure') and equipment.design_pressure else "未知"),
            ("设计温度", f"{equipment.design_temperature:.1f} °C" if hasattr(equipment, 'design_temperature') and equipment.design_temperature else "未知"),
            ("操作压力", f"{equipment.operating_pressure:.2f} MPa" if hasattr(equipment, 'operating_pressure') and equipment.operating_pressure else "未知"),
            ("操作温度", f"{equipment.operating_temperature:.1f} °C" if hasattr(equipment, 'operating_temperature') and equipment.operating_temperature else "未知"),
            ("容积", f"{equipment.volume:.2f} m³" if hasattr(equipment, 'volume') and equipment.volume else "未知"),
            ("材质", equipment.material if hasattr(equipment, 'material') and equipment.material else "未知"),
            ("功率", f"{equipment.power:.1f} kW" if hasattr(equipment, 'power') and equipment.power else "未知"),
        ]
        
        self.property_table.setRowCount(len(properties))
        for i, (prop, value) in enumerate(properties):
            self.property_table.setItem(i, 0, QTableWidgetItem(prop))
            self.property_table.setItem(i, 1, QTableWidgetItem(value))
    
    def on_selection_changed(self):
        """选择变化事件"""
        selected_rows = self.equipment_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            equipment_id = self.equipment_table.item(row, 1).text()
            self.show_equipment_details(equipment_id)
    
    def toggle_batch_mode(self, enabled):
        """切换批量操作模式"""
        self.batch_mode = enabled
        self.batch_panel.setVisible(enabled)
        
        if enabled:
            self.equipment_table.setSelectionMode(QTableWidget.NoSelection)
            for i in range(self.equipment_table.rowCount()):
                item = self.equipment_table.item(i, 0)
                item.setFlags(item.flags() | Qt.ItemIsEnabled)
        else:
            self.equipment_table.setSelectionMode(QTableWidget.ExtendedSelection)
            self.clear_batch_selection()
    
    def clear_batch_selection(self):
        """清除批量选择"""
        for i in range(self.equipment_table.rowCount()):
            self.equipment_table.item(i, 0).setCheckState(Qt.Unchecked)
        self.update_info_label()
    
    def get_selected_equipment(self):
        """获取选中的设备ID列表"""
        selected = []
        for i in range(self.equipment_table.rowCount()):
            if self.equipment_table.item(i, 0).checkState() == Qt.Checked:
                equipment_id = self.equipment_table.item(i, 1).text()
                selected.append(equipment_id)
        return selected
    
    def import_equipment(self):
        """导入设备数据"""
        file_path, selected_filter = QFileDialog.getOpenFileName(
            self, "导入设备数据", "", 
            "Excel文件 (*.xlsx *.xls);;CSV文件 (*.csv);;JSON文件 (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            imported_count = 0
            
            if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                # 读取Excel文件
                df = pd.read_excel(file_path, dtype=str)
                
                # 处理列名映射
                column_mapping = {
                    'Tag num.': 'equipment_id',
                    'Description': 'description_en',
                    '设备名称': 'name',
                    'Technical specifications': 'specification',
                    'Design tem.℃': 'design_temperature',
                    'Design pressure MPa·G': 'design_pressure',
                    'Operating tem.℃': 'operating_temperature',
                    'Operating pressure MPa·G': 'operating_pressure',
                    'Estimated power(kW)': 'estimated_power',
                    'Material': 'material',
                    'Insulation': 'insulation',
                    'Weight estimate(t)': 'weight_estimate',
                    'Remark': 'notes'
                }
                
                # 重命名列
                df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns}, inplace=True)
                
                for _, row in df.iterrows():
                    # 创建设备对象
                    equipment_data = {}
                    for col in df.columns:
                        if col in ['equipment_id', 'name', 'description_en']:
                            equipment_data[col] = str(row[col]) if pd.notna(row[col]) else ""
                        elif col in ['design_temperature', 'design_pressure', 'operating_temperature', 
                                    'operating_pressure', 'estimated_power', 'weight_estimate']:
                            try:
                                equipment_data[col] = float(row[col]) if pd.notna(row[col]) else None
                            except:
                                equipment_data[col] = None
                        else:
                            equipment_data[col] = str(row[col]) if pd.notna(row[col]) else ""
                    
                    # 设置默认值
                    if 'type' not in equipment_data:
                        equipment_data['type'] = '其他'
                    if 'status' not in equipment_data:
                        equipment_data['status'] = '运行中'
                    
                    # 添加或更新对照表
                    if equipment_data.get('name') and equipment_data.get('description_en'):
                        self.data_manager.add_equipment_name_mapping(
                            equipment_data['name'], 
                            equipment_data['description_en']
                        )
                    
                    # 创建设备对象并保存
                    from ..process_design_data import EquipmentItem
                    equipment = EquipmentItem(**equipment_data)
                    
                    if self.process_manager.add_equipment(equipment):
                        imported_count += 1
            
            elif file_path.endswith('.csv'):
                df = pd.read_csv(file_path, encoding='utf-8', dtype=str)
                # 处理逻辑与Excel类似
                column_mapping = {
                    'Tag num.': 'equipment_id',
                    'Description': 'description_en',
                    '设备名称': 'name',
                    'Technical specifications': 'specification',
                    'Design tem.℃': 'design_temperature',
                    'Design pressure MPa·G': 'design_pressure',
                    'Operating tem.℃': 'operating_temperature',
                    'Operating pressure MPa·G': 'operating_pressure',
                    'Estimated power(kW)': 'estimated_power',
                    'Material': 'material',
                    'Insulation': 'insulation',
                    'Weight estimate(t)': 'weight_estimate',
                    'Remark': 'notes'
                }
                
                df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns}, inplace=True)
                
                for _, row in df.iterrows():
                    equipment_data = {}
                    for col in df.columns:
                        if col in ['equipment_id', 'name', 'description_en']:
                            equipment_data[col] = str(row[col]) if pd.notna(row[col]) else ""
                        elif col in ['design_temperature', 'design_pressure', 'operating_temperature', 
                                    'operating_pressure', 'estimated_power', 'weight_estimate']:
                            try:
                                equipment_data[col] = float(row[col]) if pd.notna(row[col]) else None
                            except:
                                equipment_data[col] = None
                        else:
                            equipment_data[col] = str(row[col]) if pd.notna(row[col]) else ""
                    
                    if 'type' not in equipment_data:
                        equipment_data['type'] = '其他'
                    if 'status' not in equipment_data:
                        equipment_data['status'] = '运行中'
                    
                    if equipment_data.get('name') and equipment_data.get('description_en'):
                        self.data_manager.add_equipment_name_mapping(
                            equipment_data['name'], 
                            equipment_data['description_en']
                        )
                    
                    from ..process_design_data import EquipmentItem
                    equipment = EquipmentItem(**equipment_data)
                    
                    if self.process_manager.add_equipment(equipment):
                        imported_count += 1
            
            elif file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for item in data:
                    from ..process_design_data import EquipmentItem
                    equipment = EquipmentItem.from_dict(item)
                    
                    # 添加对照表
                    if equipment.name and equipment.description_en:
                        self.data_manager.add_equipment_name_mapping(
                            equipment.name, 
                            equipment.description_en
                        )
                    
                    if self.process_manager.add_equipment(equipment):
                        imported_count += 1
            
            self.load_equipment()
            self.equipment_list_updated.emit()
            
            QMessageBox.information(self, "导入成功", f"成功导入 {imported_count} 个设备")
            
        except Exception as e:
            QMessageBox.critical(self, "导入失败", f"导入文件时发生错误:\n{str(e)}")
    
    def export_equipment(self):
        """导出设备数据（按照设备清单模板格式）"""
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "导出设备清单", "设备清单.xlsx",
            "Excel文件 (*.xlsx);;CSV文件 (*.csv);;JSON文件 (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            # 获取所有设备
            equipment_list = self.process_manager.get_all_equipment()
            
            # 按照模板格式构建数据
            rows = []
            for i, equipment in enumerate(equipment_list, 1):
                # 获取英文描述
                description_en = ""
                if hasattr(equipment, 'description_en') and equipment.description_en:
                    description_en = equipment.description_en
                elif equipment.name:
                    # 尝试从对照表获取
                    description_en = self.data_manager.get_english_name(equipment.name)
                
                row = {
                    'Item': i,
                    'Tag num.': equipment.equipment_id,
                    'Description': description_en,
                    '设备名称': equipment.name,
                    'P&ID DWG. NO.': equipment.pid_dwg_no if hasattr(equipment, 'pid_dwg_no') else '',
                    'Technical specifications': equipment.specification,
                    'QTY.': equipment.quantity if hasattr(equipment, 'quantity') else 1,
                    '单价\nPrice': equipment.unit_price if hasattr(equipment, 'unit_price') else '',
                    '总价\nTotal': equipment.total_price if hasattr(equipment, 'total_price') else '',
                    'Design tem.<br>℃': equipment.design_temperature,
                    'Design pressure<br>MPa·G': equipment.design_pressure,
                    'Operating tem.<br>℃': equipment.operating_temperature if hasattr(equipment, 'operating_temperature') else '',
                    'Operating pressure<br>MPa·G': equipment.operating_pressure if hasattr(equipment, 'operating_pressure') else '',
                    'Estimated power(kW)': equipment.estimated_power if hasattr(equipment, 'estimated_power') else '',
                    'Material': equipment.material if hasattr(equipment, 'material') else '',
                    'Insulation': equipment.insulation if hasattr(equipment, 'insulation') else '',
                    'Weight estimate(t)': equipment.weight_estimate if hasattr(equipment, 'weight_estimate') else '',
                    'Dynamic': equipment.dynamic if hasattr(equipment, 'dynamic') else '',
                    'Remark': equipment.notes
                }
                rows.append(row)
            
            df = pd.DataFrame(rows)
            
            # 设置列顺序（按照模板顺序）
            columns = [
                'Item', 'Tag num.', 'Description', '设备名称', 'P&ID DWG. NO.', 
                'Technical specifications', 'QTY.', '单价\nPrice', '总价\nTotal',
                'Design tem.<br>℃', 'Design pressure<br>MPa·G', 'Operating tem.<br>℃', 
                'Operating pressure<br>MPa·G', 'Estimated power(kW)', 
                'Material', 'Insulation', 'Weight estimate(t)', 
                'Dynamic', 'Remark'
            ]
            
            # 重新排列列顺序
            df = df.reindex(columns=[col for col in columns if col in df.columns])
            
            # 根据文件类型保存
            if file_path.endswith('.xlsx'):
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Sheet1')
                    
                    # 设置列宽（可选）
                    worksheet = writer.sheets['Sheet1']
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 30)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
                        
            elif file_path.endswith('.csv'):
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
            elif file_path.endswith('.json'):
                df.to_json(file_path, orient='records', force_ascii=False, indent=2)
            
            QMessageBox.information(self, "导出成功", f"成功导出 {len(equipment_list)} 个设备")
            
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出文件时发生错误:\n{str(e)}")
    
    def copy_selected(self):
        """复制选中内容到剪贴板"""
        selected_items = self.equipment_table.selectedItems()
        if not selected_items:
            return
        
        # 获取选中的行和列
        rows = sorted(set(item.row() for item in selected_items))
        cols = sorted(set(item.column() for item in selected_items))
        
        # 构建表格文本
        text = ""
        for row in rows:
            row_data = []
            for col in cols:
                if col == 0:  # 跳过选择框列
                    continue
                item = self.equipment_table.item(row, col)
                row_data.append(item.text() if item else "")
            text += "\t".join(row_data) + "\n"
        
        clipboard = QApplication.clipboard()
        clipboard.setText(text.strip())
        
        self.status_bar.setText(f"已复制 {len(rows)} 行数据")
    
    def batch_edit_equipment(self):
        """批量编辑设备"""
        selected_ids = self.get_selected_equipment()
        if not selected_ids:
            QMessageBox.warning(self, "警告", "请先选择要编辑的设备")
            return
        
        dialog = BatchEditDialog(selected_ids, self.process_manager, self)
        if dialog.exec() == QDialog.Accepted:
            self.load_equipment()
    
    def batch_export_equipment(self):
        """批量导出设备"""
        selected_ids = self.get_selected_equipment()
        if not selected_ids:
            QMessageBox.warning(self, "警告", "请先选择要导出的设备")
            return
        
        self.export_selected_equipment(selected_ids)
    
    def batch_delete_equipment(self):
        """批量删除设备"""
        selected_ids = self.get_selected_equipment()
        if not selected_ids:
            QMessageBox.warning(self, "警告", "请先选择要删除的设备")
            return
        
        reply = QMessageBox.question(
            self, "确认批量删除",
            f"确定要删除选中的 {len(selected_ids)} 个设备吗？\n此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success_count = 0
            for equipment_id in selected_ids:
                if self.process_manager.delete_equipment(equipment_id):
                    success_count += 1
            
            self.load_equipment()
            self.equipment_list_updated.emit()
            
            QMessageBox.information(
                self, "删除完成",
                f"已删除 {success_count} 个设备"
            )
    
    def export_selected_equipment(self, equipment_ids):
        """导出选中的设备"""
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "导出选中设备", "selected_equipment.xlsx",
            "Excel文件 (*.xlsx);;CSV文件 (*.csv);;JSON文件 (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            equipment_list = []
            for equipment_id in equipment_ids:
                equipment = self.process_manager.get_equipment(equipment_id)
                if equipment:
                    equipment_list.append(equipment)
            
            # 按照模板格式构建数据
            rows = []
            for i, equipment in enumerate(equipment_list, 1):
                # 获取英文描述
                description_en = ""
                if hasattr(equipment, 'description_en') and equipment.description_en:
                    description_en = equipment.description_en
                elif equipment.name:
                    description_en = self.data_manager.get_english_name(equipment.name)
                
                row = {
                    'Item': i,
                    'Tag num.': equipment.equipment_id,
                    'Description': description_en,
                    '设备名称': equipment.name,
                    'P&ID DWG. NO.': equipment.pid_dwg_no if hasattr(equipment, 'pid_dwg_no') else '',
                    'Technical specifications': equipment.specification,
                    'QTY.': equipment.quantity if hasattr(equipment, 'quantity') else 1,
                    '单价\nPrice': equipment.unit_price if hasattr(equipment, 'unit_price') else '',
                    '总价\nTotal': equipment.total_price if hasattr(equipment, 'total_price') else '',
                    'Design tem.<br>℃': equipment.design_temperature,
                    'Design pressure<br>MPa·G': equipment.design_pressure,
                    'Operating tem.<br>℃': equipment.operating_temperature if hasattr(equipment, 'operating_temperature') else '',
                    'Operating pressure<br>MPa·G': equipment.operating_pressure if hasattr(equipment, 'operating_pressure') else '',
                    'Estimated power(kW)': equipment.estimated_power if hasattr(equipment, 'estimated_power') else '',
                    'Material': equipment.material if hasattr(equipment, 'material') else '',
                    'Insulation': equipment.insulation if hasattr(equipment, 'insulation') else '',
                    'Weight estimate(t)': equipment.weight_estimate if hasattr(equipment, 'weight_estimate') else '',
                    'Dynamic': equipment.dynamic if hasattr(equipment, 'dynamic') else '',
                    'Remark': equipment.notes
                }
                rows.append(row)
            
            df = pd.DataFrame(rows)
            
            # 设置列顺序
            columns = [
                'Item', 'Tag num.', 'Description', '设备名称', 'P&ID DWG. NO.', 
                'Technical specifications', 'QTY.', '单价\nPrice', '总价\nTotal',
                'Design tem.<br>℃', 'Design pressure<br>MPa·G', 'Operating tem.<br>℃', 
                'Operating pressure<br>MPa·G', 'Estimated power(kW)', 
                'Material', 'Insulation', 'Weight estimate(t)', 
                'Dynamic', 'Remark'
            ]
            
            df = df.reindex(columns=[col for col in columns if col in df.columns])
            
            # 保存文件
            if file_path.endswith('.xlsx'):
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Sheet1')
            elif file_path.endswith('.csv'):
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
            elif file_path.endswith('.json'):
                df.to_json(file_path, orient='records', force_ascii=False, indent=2)
            
            QMessageBox.information(self, "导出成功", f"成功导出 {len(equipment_list)} 个设备")
            
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出文件时发生错误:\n{str(e)}")
    
    def add_equipment(self):
        """添加设备"""
        dialog = EquipmentDialog(self)
        if dialog.exec() == QDialog.Accepted:
            equipment = dialog.get_equipment()
            if equipment and self.process_manager:
                try:
                    if self.process_manager.add_equipment(equipment):
                        self.load_equipment()
                        self.equipment_list_updated.emit()
                        self.status_bar.setText(f"设备 '{equipment.name}' 添加成功")
                    else:
                        QMessageBox.warning(self, "错误", "设备添加失败，可能设备ID已存在。")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"添加设备时发生错误:\n{str(e)}")
    
    def edit_equipment(self):
        """编辑设备"""
        selected_row = self.equipment_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要编辑的设备")
            return
        
        equipment_id = self.equipment_table.item(selected_row, 1).text()
        if not self.process_manager:
            return
        
        equipment = self.process_manager.get_equipment(equipment_id)
        if not equipment:
            QMessageBox.warning(self, "错误", "设备未找到")
            return
        
        dialog = EquipmentDialog(self, equipment)
        if dialog.exec() == QDialog.Accepted:
            updated_equipment = dialog.get_equipment()
            if updated_equipment and self.process_manager:
                if self.process_manager.update_equipment(updated_equipment):
                    self.load_equipment()
                    self.equipment_list_updated.emit()
                    self.status_bar.setText(f"设备 '{updated_equipment.name}' 更新成功")
                else:
                    QMessageBox.warning(self, "错误", "设备更新失败")
    
    def delete_equipment(self):
        """删除设备"""
        selected_row = self.equipment_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要删除的设备")
            return
        
        equipment_id = self.equipment_table.item(selected_row, 1).text()
        equipment_name = self.equipment_table.item(selected_row, 2).text()
        
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除设备 '{equipment_name}' 吗？\n此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes and self.process_manager:
            if self.process_manager.delete_equipment(equipment_id):
                self.load_equipment()
                self.equipment_list_updated.emit()
                self.status_bar.setText(f"设备 '{equipment_name}' 删除成功")
            else:
                QMessageBox.warning(self, "错误", "设备删除失败")
    
    def manage_name_mapping(self):
        """管理设备名称对照表"""
        dialog = QDialog(self)
        dialog.setWindowTitle("设备名称对照表管理")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # 添加新的对照
        add_layout = QHBoxLayout()
        add_layout.addWidget(QLabel("中文名称:"))
        chinese_input = QLineEdit()
        add_layout.addWidget(chinese_input)
        
        add_layout.addWidget(QLabel("英文名称:"))
        english_input = QLineEdit()
        add_layout.addWidget(english_input)
        
        add_btn = QPushButton("添加")
        
        def add_mapping():
            chinese = chinese_input.text().strip()
            english = english_input.text().strip()
            if chinese and english:
                self.data_manager.add_equipment_name_mapping(chinese, english)
                chinese_input.clear()
                english_input.clear()
                load_mapping_table()
        
        add_btn.clicked.connect(add_mapping)
        add_layout.addWidget(add_btn)
        
        layout.addLayout(add_layout)
        
        # 对照表表格
        mapping_table = QTableWidget()
        mapping_table.setColumnCount(2)
        mapping_table.setHorizontalHeaderLabels(["中文名称", "英文名称"])
        mapping_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(mapping_table)
        
        def load_mapping_table():
            """加载对照表到表格"""
            mapping = self.data_manager.get_equipment_name_mapping()
            mapping_table.setRowCount(len(mapping))
            
            for i, (chinese, english) in enumerate(mapping.items()):
                mapping_table.setItem(i, 0, QTableWidgetItem(chinese))
                mapping_table.setItem(i, 1, QTableWidgetItem(english))
        
        # 按钮
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(load_mapping_table)
        btn_layout.addWidget(refresh_btn)
        
        delete_btn = QPushButton("删除选中")
        
        def delete_selected_mapping():
            """删除选中的对照表条目"""
            selected_rows = set(index.row() for index in mapping_table.selectedIndexes())
            
            for row in sorted(selected_rows, reverse=True):
                chinese_name = mapping_table.item(row, 0).text()
                self.data_manager.remove_equipment_name_mapping(chinese_name)
            
            load_mapping_table()
        
        delete_btn.clicked.connect(delete_selected_mapping)
        btn_layout.addWidget(delete_btn)
        
        btn_layout.addStretch()
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        # 加载数据
        load_mapping_table()
        
        dialog.exec()

# ==================== 对话框类 ====================

class AdvancedSearchDialog(QDialog):
    """高级搜索对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("高级搜索设备")
        self.setMinimumWidth(400)
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # 制造商搜索
        self.manufacturer_input = QLineEdit()
        self.manufacturer_input.setPlaceholderText("制造商名称")
        form_layout.addRow("制造商:", self.manufacturer_input)
        
        # 安装位置搜索
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("安装位置")
        form_layout.addRow("安装位置:", self.location_input)
        
        # 投用日期范围
        date_layout = QHBoxLayout()
        self.start_date = QLineEdit()
        self.start_date.setPlaceholderText("YYYY-MM-DD")
        self.end_date = QLineEdit()
        self.end_date.setPlaceholderText("YYYY-MM-DD")
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(QLabel("至"))
        date_layout.addWidget(self.end_date)
        form_layout.addRow("投用日期范围:", date_layout)
        
        layout.addLayout(form_layout)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_search_criteria(self):
        """获取搜索条件"""
        criteria = {}
        
        manufacturer = self.manufacturer_input.text().strip()
        if manufacturer:
            criteria['manufacturer'] = manufacturer
        
        location = self.location_input.text().strip()
        if location:
            criteria['location'] = location
        
        start_date = self.start_date.text().strip()
        if start_date:
            criteria['start_date'] = start_date
        
        end_date = self.end_date.text().strip()
        if end_date:
            criteria['end_date'] = end_date
        
        return criteria

class BatchEditDialog(QDialog):
    """批量编辑对话框"""
    
    def __init__(self, equipment_ids, process_manager, parent=None):
        super().__init__(parent)
        self.equipment_ids = equipment_ids
        self.process_manager = process_manager
        self.setWindowTitle("批量编辑设备")
        self.setMinimumWidth(400)
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel(f"批量编辑 {len(self.equipment_ids)} 个设备"))
        
        form_layout = QFormLayout()
        
        # 可批量编辑的字段
        self.status_combo = QComboBox()
        self.status_combo.addItems(["", "运行中", "停机", "维修中", "备用"])
        self.status_combo.setCurrentIndex(0)
        form_layout.addRow("状态:", self.status_combo)
        
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("留空则不修改")
        form_layout.addRow("安装位置:", self.location_input)
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        self.notes_input.setPlaceholderText("留空则不修改")
        form_layout.addRow("备注:", self.notes_input)
        
        layout.addLayout(form_layout)
        
        layout.addWidget(QLabel("注意：空字段不会修改原有值"))
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.apply_changes)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def apply_changes(self):
        """应用批量修改"""
        changes = {}
        
        status = self.status_combo.currentText()
        if status:
            changes['status'] = status
        
        location = self.location_input.text().strip()
        if location:
            changes['location'] = location
        
        notes = self.notes_input.toPlainText().strip()
        if notes:
            changes['notes'] = notes
        
        if not changes:
            QMessageBox.warning(self, "警告", "没有修改任何字段")
            return
        
        success_count = 0
        for equipment_id in self.equipment_ids:
            equipment = self.process_manager.get_equipment(equipment_id)
            if equipment:
                # 应用修改
                if 'status' in changes:
                    equipment.status = changes['status']
                if 'location' in changes:
                    equipment.location = changes['location']
                if 'notes' in changes:
                    equipment.notes = changes['notes']
                
                if self.process_manager.update_equipment(equipment):
                    success_count += 1
        
        QMessageBox.information(self, "批量编辑完成", f"成功更新 {success_count} 个设备")
        self.accept()

class EquipmentDialog(QDialog):
    """设备对话框"""
    
    def __init__(self, parent=None, equipment=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.equipment = equipment
        self.setWindowTitle("添加设备" if not equipment else "编辑设备")
        self.setMinimumWidth(600)
        
        self.setup_ui()
        if equipment:
            self.load_equipment_data()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        # 使用标签页组织内容
        tab_widget = QTabWidget()
        
        # 基本信息标签页
        basic_tab = QWidget()
        basic_layout = QFormLayout(basic_tab)
        
        self.equipment_id_input = QLineEdit()
        self.name_input = QLineEdit()
        
        # 添加英文描述输入框
        self.description_en_input = QLineEdit()
        self.description_en_input.setPlaceholderText("自动从对照表获取，可修改")
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["反应器", "分离器", "换热器", "泵", "压缩机", "储罐", "阀门", "管道", "其他"])
        
        self.model_input = QLineEdit()
        self.specification_input = QLineEdit()
        self.manufacturer_input = QLineEdit()
        self.location_input = QLineEdit()
        
        basic_layout.addRow("设备ID*:", self.equipment_id_input)
        basic_layout.addRow("设备名称(中文)*:", self.name_input)
        basic_layout.addRow("设备名称(英文):", self.description_en_input)
        basic_layout.addRow("设备类型:", self.type_combo)
        basic_layout.addRow("型号:", self.model_input)
        basic_layout.addRow("规格:", self.specification_input)
        basic_layout.addRow("制造商:", self.manufacturer_input)
        basic_layout.addRow("安装位置:", self.location_input)
        
        # 连接信号：当中文名称变化时，自动获取英文名称
        self.name_input.textChanged.connect(self.update_english_name)
        
        tab_widget.addTab(basic_tab, "基本信息")
        
        # 状态信息标签页
        status_tab = QWidget()
        status_layout = QFormLayout(status_tab)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["运行中", "停机", "维修中", "备用"])
        
        self.commission_date = QLineEdit()
        self.commission_date.setPlaceholderText("YYYY-MM-DD")
        
        status_layout.addRow("状态:", self.status_combo)
        status_layout.addRow("投用日期:", self.commission_date)
        
        tab_widget.addTab(status_tab, "状态信息")
        
        # 设计参数标签页
        design_tab = QWidget()
        design_layout = QFormLayout(design_tab)
        
        self.design_pressure_input = QDoubleSpinBox()
        self.design_pressure_input.setRange(0, 1000)
        self.design_pressure_input.setDecimals(2)
        self.design_pressure_input.setSuffix(" MPa")
        
        self.design_temperature_input = QDoubleSpinBox()
        self.design_temperature_input.setRange(-273, 1000)
        self.design_temperature_input.setDecimals(1)
        self.design_temperature_input.setSuffix(" °C")
        
        design_layout.addRow("设计压力:", self.design_pressure_input)
        design_layout.addRow("设计温度:", self.design_temperature_input)
        
        tab_widget.addTab(design_tab, "设计参数")
        
        # 导出相关参数标签页
        export_tab = QWidget()
        export_layout = QFormLayout(export_tab)
        
        self.pid_dwg_no_input = QLineEdit()
        self.pid_dwg_no_input.setPlaceholderText("P&ID图号")
        
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(1, 1000)
        self.quantity_input.setValue(1)
        
        self.unit_price_input = QDoubleSpinBox()
        self.unit_price_input.setRange(0, 10000000)
        self.unit_price_input.setDecimals(2)
        self.unit_price_input.setPrefix("¥ ")
        
        self.total_price_input = QDoubleSpinBox()
        self.total_price_input.setRange(0, 10000000)
        self.total_price_input.setDecimals(2)
        self.total_price_input.setPrefix("¥ ")
        
        self.operating_temperature_input = QDoubleSpinBox()
        self.operating_temperature_input.setRange(-273, 1000)
        self.operating_temperature_input.setDecimals(1)
        self.operating_temperature_input.setSuffix(" °C")
        
        self.operating_pressure_input = QDoubleSpinBox()
        self.operating_pressure_input.setRange(0, 1000)
        self.operating_pressure_input.setDecimals(2)
        self.operating_pressure_input.setSuffix(" MPa")
        
        self.estimated_power_input = QDoubleSpinBox()
        self.estimated_power_input.setRange(0, 10000)
        self.estimated_power_input.setDecimals(1)
        self.estimated_power_input.setSuffix(" kW")
        
        self.material_input = QLineEdit()
        self.material_input.setPlaceholderText("材质")
        
        self.insulation_input = QLineEdit()
        self.insulation_input.setPlaceholderText("保温")
        
        self.weight_estimate_input = QDoubleSpinBox()
        self.weight_estimate_input.setRange(0, 1000)
        self.weight_estimate_input.setDecimals(2)
        self.weight_estimate_input.setSuffix(" t")
        
        self.dynamic_input = QLineEdit()
        self.dynamic_input.setPlaceholderText("动态")
        
        export_layout.addRow("P&ID图号:", self.pid_dwg_no_input)
        export_layout.addRow("数量:", self.quantity_input)
        export_layout.addRow("单价:", self.unit_price_input)
        export_layout.addRow("总价:", self.total_price_input)
        export_layout.addRow("操作温度:", self.operating_temperature_input)
        export_layout.addRow("操作压力:", self.operating_pressure_input)
        export_layout.addRow("估计功率:", self.estimated_power_input)
        export_layout.addRow("材质:", self.material_input)
        export_layout.addRow("保温:", self.insulation_input)
        export_layout.addRow("重量估计:", self.weight_estimate_input)
        export_layout.addRow("动态:", self.dynamic_input)
        
        tab_widget.addTab(export_tab, "导出参数")
        
        # 其他信息标签页
        other_tab = QWidget()
        other_layout = QVBoxLayout(other_tab)
        
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("备注信息...")
        
        other_layout.addWidget(QLabel("备注:"))
        other_layout.addWidget(self.notes_input)
        
        tab_widget.addTab(other_tab, "其他")
        
        layout.addWidget(tab_widget)
        
        # 验证状态
        self.validation_label = QLabel()
        self.validation_label.setStyleSheet("color: red;")
        layout.addWidget(self.validation_label)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def update_english_name(self):
        """根据中文名称自动获取英文名称"""
        chinese_name = self.name_input.text().strip()
        if chinese_name and self.parent_widget and hasattr(self.parent_widget, 'data_manager'):
            # 尝试从对照表获取英文名称
            english_name = self.parent_widget.data_manager.get_english_name(chinese_name)
            if english_name:
                self.description_en_input.setText(english_name)
    
    def validate_and_accept(self):
        """验证并接受"""
        equipment_id = self.equipment_id_input.text().strip()
        name = self.name_input.text().strip()
        
        errors = []
        
        if not equipment_id:
            errors.append("设备ID不能为空")
        if not name:
            errors.append("设备名称不能为空")
        
        # 验证日期格式
        if self.commission_date.text().strip():
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', self.commission_date.text().strip()):
                errors.append("投用日期格式应为: YYYY-MM-DD")
        
        if errors:
            self.validation_label.setText("错误: " + "; ".join(errors))
            return
        
        self.validation_label.setText("")
        self.accept()
    
    def load_equipment_data(self):
        """加载设备数据"""
        if not self.equipment:
            return
        
        self.equipment_id_input.setText(self.equipment.equipment_id)
        self.name_input.setText(self.equipment.name)
        
        index = self.type_combo.findText(self.equipment.equipment_type if hasattr(self.equipment, 'equipment_type') else self.equipment.type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
        
        self.model_input.setText(self.equipment.model or "")
        self.specification_input.setText(self.equipment.specification or "")
        self.manufacturer_input.setText(self.equipment.manufacturer or "")
        self.location_input.setText(self.equipment.location or "")
        
        index = self.status_combo.findText(self.equipment.status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        
        if hasattr(self.equipment, 'commission_date') and self.equipment.commission_date:
            if hasattr(self.equipment.commission_date, 'strftime'):
                self.commission_date.setText(self.equipment.commission_date.strftime('%Y-%m-%d'))
            else:
                self.commission_date.setText(str(self.equipment.commission_date))
        
        if hasattr(self.equipment, 'design_pressure') and self.equipment.design_pressure:
            self.design_pressure_input.setValue(self.equipment.design_pressure)
        
        if hasattr(self.equipment, 'design_temperature') and self.equipment.design_temperature:
            self.design_temperature_input.setValue(self.equipment.design_temperature)
        
        # 加载英文描述
        if hasattr(self.equipment, 'description_en') and self.equipment.description_en:
            self.description_en_input.setText(self.equipment.description_en)
        else:
            # 尝试从对照表获取
            if self.parent_widget and hasattr(self.parent_widget, 'data_manager'):
                english_name = self.parent_widget.data_manager.get_english_name(self.equipment.name)
                if english_name:
                    self.description_en_input.setText(english_name)
        
        # 加载导出相关参数
        if hasattr(self.equipment, 'pid_dwg_no'):
            self.pid_dwg_no_input.setText(self.equipment.pid_dwg_no or "")
        
        if hasattr(self.equipment, 'quantity'):
            self.quantity_input.setValue(self.equipment.quantity or 1)
        
        if hasattr(self.equipment, 'unit_price') and self.equipment.unit_price:
            self.unit_price_input.setValue(self.equipment.unit_price)
        
        if hasattr(self.equipment, 'total_price') and self.equipment.total_price:
            self.total_price_input.setValue(self.equipment.total_price)
        
        if hasattr(self.equipment, 'operating_temperature') and self.equipment.operating_temperature:
            self.operating_temperature_input.setValue(self.equipment.operating_temperature)
        
        if hasattr(self.equipment, 'operating_pressure') and self.equipment.operating_pressure:
            self.operating_pressure_input.setValue(self.equipment.operating_pressure)
        
        if hasattr(self.equipment, 'estimated_power') and self.equipment.estimated_power:
            self.estimated_power_input.setValue(self.equipment.estimated_power)
        
        if hasattr(self.equipment, 'material'):
            self.material_input.setText(self.equipment.material or "")
        
        if hasattr(self.equipment, 'insulation'):
            self.insulation_input.setText(self.equipment.insulation or "")
        
        if hasattr(self.equipment, 'weight_estimate') and self.equipment.weight_estimate:
            self.weight_estimate_input.setValue(self.equipment.weight_estimate)
        
        if hasattr(self.equipment, 'dynamic'):
            self.dynamic_input.setText(self.equipment.dynamic or "")
        
        self.notes_input.setText(self.equipment.notes or "")
    
    def get_equipment(self):
        """获取设备对象"""
        from ..process_design_data import EquipmentItem
        
        equipment_id = self.equipment_id_input.text().strip()
        name = self.name_input.text().strip()
        description_en = self.description_en_input.text().strip()
        
        # 如果用户输入了英文描述，更新对照表
        if name and description_en and self.parent_widget and hasattr(self.parent_widget, 'data_manager'):
            self.parent_widget.data_manager.add_equipment_name_mapping(name, description_en)
        
        equipment = EquipmentItem(
            equipment_id=equipment_id,
            name=name,
            type=self.type_combo.currentText(),
            model=self.model_input.text().strip(),
            specification=self.specification_input.text().strip(),
            manufacturer=self.manufacturer_input.text().strip(),
            location=self.location_input.text().strip(),
            status=self.status_combo.currentText(),
            commission_date=self.commission_date.text().strip() or None,
            design_pressure=self.design_pressure_input.value() if self.design_pressure_input.value() > 0 else None,
            design_temperature=self.design_temperature_input.value() if self.design_temperature_input.value() > -273 else None,
            description=self.notes_input.toPlainText().strip(),
            description_en=description_en,
            pid_dwg_no=self.pid_dwg_no_input.text().strip(),
            quantity=self.quantity_input.value(),
            unit_price=self.unit_price_input.value() if self.unit_price_input.value() > 0 else None,
            total_price=self.total_price_input.value() if self.total_price_input.value() > 0 else None,
            operating_temperature=self.operating_temperature_input.value() if self.operating_temperature_input.value() > -273 else None,
            operating_pressure=self.operating_pressure_input.value() if self.operating_pressure_input.value() > 0 else None,
            estimated_power=self.estimated_power_input.value() if self.estimated_power_input.value() > 0 else None,
            material=self.material_input.text().strip(),
            insulation=self.insulation_input.text().strip(),
            weight_estimate=self.weight_estimate_input.value() if self.weight_estimate_input.value() > 0 else None,
            dynamic=self.dynamic_input.text().strip()
        )
        
        return equipment