# modules/process_design/tabs/material_database_tab.py
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
    QMenu, QApplication, QFrame, QToolBar, QDialogButtonBox,
    QSpinBox, QScrollArea, QListWidget, QListWidgetItem,
    QSizePolicy, QGridLayout
)
from PySide6.QtCore import Qt, Signal, QTimer, QThread, QSize, QEvent
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
    from ..data.data_models import MaterialProperty
    print("✅ 成功导入 ProcessDesignManager 和 MaterialProperty")
except ImportError as e:
    print(f"❌ 导入失败: {e}")

    # 创建占位符类
    class ProcessDesignManager:
        def __init__(self, *args, **kwargs):
            pass
        def get_all_materials(self):
            return []
        def get_material(self, material_id):
            return None
        def add_material(self, material):
            return False
        def update_material(self, material):
            return False
        def delete_material(self, material_id):
            return False
        def search_materials(self, search_term):
            return []
        def advanced_search_materials(self, criteria):
            return []
    
    class MaterialProperty:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

class MaterialDatabaseTab(QWidget):
    """物料数据库标签页 - 优化布局，主要区域最大化"""
    
    material_selected = Signal(str)  # 物料选择信号
    material_list_updated = Signal()  # 物料列表更新信号
    import_progress = Signal(int)  # 导入进度信号
    
    def __init__(self, data_manager=None, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.process_manager = None
        self.current_materials = []  # 当前显示的材料列表
        self.selected_rows = set()  # 选中的行
        self.batch_mode = False  # 批量操作模式
        
        # 延迟初始化process_manager
        if data_manager:
            try:
                self.process_manager = ProcessDesignManager(data_manager)
                print("✅ 物料数据库: ProcessDesignManager 初始化成功")
            except Exception as e:
                print(f"❌ 物料数据库: ProcessDesignManager 初始化失败: {e}")
                self.process_manager = None
        
        self.setup_ui()
        self.load_materials()
        self.setup_shortcuts()
        
        # 添加延迟初始化，确保UI完全加载
        QTimer.singleShot(100, self.finalize_initialization)

    def finalize_initialization(self):
        """完成初始化，确保表格正确显示"""
        # 确保表格正确排序
        self.material_table.sortItems(1, Qt.AscendingOrder)  # 按物料ID排序
        # 强制重绘
        self.material_table.viewport().update()
        self.status_bar.setText("就绪 - 初始化完成")
    
    def setup_ui(self):
        """设置UI - 优化布局，主要区域最大化"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)  # 减少外边距
        main_layout.setSpacing(2)  # 减少控件间距
        
        # ========== 工具栏 - 固定高度 ==========
        self.setup_toolbar()
        main_layout.addWidget(self.toolbar)
        
        # ========== 搜索和过滤区域 - 固定高度 ==========
        filter_frame = QFrame()
        filter_frame.setFixedHeight(50)  # 固定搜索区域高度
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(8, 4, 8, 4)  # 紧凑的内边距
        filter_layout.setSpacing(8)
        
        # 搜索部分 - 简化版本
        search_layout = QHBoxLayout()
        search_layout.setSpacing(4)
        search_label = QLabel("搜索:")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入物料名称、CAS号或分子式...")
        self.search_input.setFixedHeight(28)
        self.search_input.textChanged.connect(self.on_search_changed)
        self.search_input.returnPressed.connect(self.perform_search)
        
        # 清空搜索按钮
        self.clear_search_btn = QPushButton("清空")
        self.clear_search_btn.setFixedHeight(28)
        self.clear_search_btn.clicked.connect(self.clear_search)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.clear_search_btn)
        
        filter_layout.addLayout(search_layout)
        filter_layout.addStretch()
        
        # 快速过滤器
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["全部物料", "液体物料", "固体物料", "气体物料", "危险物料"])
        self.filter_combo.setFixedHeight(28)
        self.filter_combo.currentIndexChanged.connect(self.apply_quick_filter)
        filter_layout.addWidget(QLabel("筛选:"))
        filter_layout.addWidget(self.filter_combo)
        
        main_layout.addWidget(filter_frame)
        
        # ========== 主要区域：使用分割器，占据剩余空间 ==========
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)  # 防止子部件被压缩消失
        
        # ========== 左侧：表格区域 - 使用拉伸因子 ==========
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(2)
        
        # 表格上方的信息区域 - 固定高度
        info_frame = QFrame()
        info_frame.setFixedHeight(30)
        info_layout = QHBoxLayout(info_frame)
        info_layout.setContentsMargins(8, 4, 8, 4)
        
        self.info_label = QLabel("总计: 0 个物料")
        info_layout.addWidget(self.info_label)
        info_layout.addStretch()
        
        self.selected_label = QLabel("已选择: 0 个")
        info_layout.addWidget(self.selected_label)
        
        # 批量模式切换按钮
        self.batch_toggle_btn = QPushButton("批量模式")
        self.batch_toggle_btn.setCheckable(True)
        self.batch_toggle_btn.setFixedHeight(24)
        self.batch_toggle_btn.toggled.connect(self.toggle_batch_mode)
        info_layout.addWidget(self.batch_toggle_btn)
        
        table_layout.addWidget(info_frame)
        
        # ========== 物料表格 - 设置为可拉伸，占据剩余空间 ==========
        self.material_table = QTableWidget()
        self.material_table.setColumnCount(10)  # 优化列数，移除选择框列
        self.material_table.setHorizontalHeaderLabels([
            "物料ID", "名称", "CAS号", "分子式", "分子量", 
            "相态", "密度", "沸点", "熔点", "危险类别"
        ])
        
        # 设置表头
        header = self.material_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 物料ID列自适应
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # 名称列拉伸
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # CAS号
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 分子式
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 分子量
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # 相态
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # 密度
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # 沸点
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # 熔点
        header.setSectionResizeMode(9, QHeaderView.Stretch)          # 危险类别
        
        # 启用排序
        self.material_table.setSortingEnabled(True)
        
        # 设置选择模式
        self.material_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.material_table.setSelectionMode(QTableWidget.ExtendedSelection)
        
        # 连接信号
        self.material_table.itemDoubleClicked.connect(self.on_material_double_clicked)
        self.material_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        # 表格添加到布局，使用拉伸因子1，使其占据剩余空间
        table_layout.addWidget(self.material_table, 1)
        
        splitter.addWidget(table_container)
        
        # ========== 右侧：详情区域 - 按比例分配高度 ==========
        detail_container = QWidget()
        detail_container.setMinimumWidth(300)
        detail_container.setMaximumWidth(500)
        detail_layout = QVBoxLayout(detail_container)
        detail_layout.setContentsMargins(5, 0, 5, 0)
        detail_layout.setSpacing(2)

        # 物料详情区域
        detail_label = QLabel("物料详情")
        detail_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 5px 0;")
        detail_layout.addWidget(detail_label)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMinimumHeight(150)
        detail_layout.addWidget(self.detail_text, 3)  # 物料详情占3/5

        # 物性参数区域
        property_label = QLabel("物理化学性质")
        property_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px 0 5px 0;")
        detail_layout.addWidget(property_label)

        self.property_table = QTableWidget()
        self.property_table.setColumnCount(2)
        self.property_table.setHorizontalHeaderLabels(["属性", "值"])
        self.property_table.horizontalHeader().setStretchLastSection(True)
        self.property_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.property_table.setMinimumHeight(120)
        detail_layout.addWidget(self.property_table, 2)  # 物性参数占2/5
        
        # 在详情区域添加一个拉伸，防止控件过度拉伸
        detail_layout.addStretch()
        
        splitter.addWidget(detail_container)
        
        # 设置分割器的初始大小比例
        splitter.setSizes([700, 300])
        
        # 将分割器添加到主布局，使用拉伸因子1，使其占据剩余空间
        main_layout.addWidget(splitter, 1)
        
        # ========== 批量操作面板 - 初始隐藏 ==========
        self.batch_panel = QFrame()
        self.batch_panel.setFrameStyle(QFrame.StyledPanel)
        self.batch_panel.setVisible(False)
        batch_layout = QHBoxLayout(self.batch_panel)
        batch_layout.setContentsMargins(5, 5, 5, 5)
        
        self.batch_edit_btn = QPushButton("批量编辑")
        self.batch_edit_btn.clicked.connect(self.batch_edit_materials)
        self.batch_edit_btn.setFixedHeight(30)
        batch_layout.addWidget(self.batch_edit_btn)
        
        self.batch_export_btn = QPushButton("批量导出")
        self.batch_export_btn.clicked.connect(self.batch_export_materials)
        self.batch_export_btn.setFixedHeight(30)
        batch_layout.addWidget(self.batch_export_btn)
        
        self.batch_delete_btn = QPushButton("批量删除")
        self.batch_delete_btn.clicked.connect(self.batch_delete_materials)
        self.batch_delete_btn.setFixedHeight(30)
        batch_layout.addWidget(self.batch_delete_btn)
        
        batch_layout.addStretch()
        
        self.clear_batch_btn = QPushButton("清除选择")
        self.clear_batch_btn.clicked.connect(self.clear_batch_selection)
        self.clear_batch_btn.setFixedHeight(30)
        batch_layout.addWidget(self.clear_batch_btn)
        
        main_layout.addWidget(self.batch_panel)
        
        # ========== 状态栏 - 固定高度 ==========
        self.status_bar = QLabel()
        self.status_bar.setFixedHeight(25)
        self.status_bar.setText("就绪")
        main_layout.addWidget(self.status_bar)
        
        # 设置窗口的最小尺寸
        self.setMinimumSize(800, 600)

    def setup_toolbar(self):
        """设置工具栏"""
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.setFixedHeight(36)  # 固定工具栏高度
        
        # 工具栏动作
        self.add_action = QAction("添加", self)
        self.add_action.triggered.connect(self.add_material)
        self.toolbar.addAction(self.add_action)
        
        self.edit_action = QAction("编辑", self)
        self.edit_action.triggered.connect(self.edit_material)
        self.toolbar.addAction(self.edit_action)
        
        self.delete_action = QAction("删除", self)
        self.delete_action.triggered.connect(self.delete_material)
        self.toolbar.addAction(self.delete_action)
        
        self.toolbar.addSeparator()
        
        self.import_action = QAction("导入", self)
        self.import_action.triggered.connect(self.import_materials)
        self.toolbar.addAction(self.import_action)
        
        self.export_action = QAction("导出", self)
        self.export_action.triggered.connect(self.export_materials)
        self.toolbar.addAction(self.export_action)
        
        self.toolbar.addSeparator()
        
        self.copy_action = QAction("复制", self)
        self.copy_action.triggered.connect(self.copy_selected)
        self.toolbar.addAction(self.copy_action)
        
        self.toolbar.addSeparator()
        
        self.select_all_action = QAction("全选", self)
        self.select_all_action.triggered.connect(self.select_all_materials)
        self.toolbar.addAction(self.select_all_action)
        
        self.clear_selection_action = QAction("清除选择", self)
        self.clear_selection_action.triggered.connect(self.clear_selection)
        self.toolbar.addAction(self.clear_selection_action)
        
        self.toolbar.addSeparator()
        
        self.refresh_action = QAction("刷新", self)
        self.refresh_action.triggered.connect(self.force_refresh)
        self.toolbar.addAction(self.refresh_action)
        
        self.toolbar.addSeparator()
        
        self.help_action = QAction("帮助", self)
        self.help_action.triggered.connect(self.show_help)
        self.toolbar.addAction(self.help_action)
    
    def setup_shortcuts(self):
        """设置快捷键"""
        # 复制快捷键
        self.copy_action.setShortcut(QKeySequence.Copy)
        self.copy_action.setShortcutContext(Qt.WidgetShortcut)
        
        # 删除快捷键
        self.delete_action.setShortcut(QKeySequence.Delete)
        self.delete_action.setShortcutContext(Qt.WidgetShortcut)
        
        # 刷新快捷键
        self.refresh_action.setShortcut(QKeySequence.Refresh)
        self.refresh_action.setShortcutContext(Qt.WidgetShortcut)
        
        # 全选快捷键
        self.select_all_action.setShortcut(QKeySequence.SelectAll)
        self.select_all_action.setShortcutContext(Qt.WidgetShortcut)
        
        # 导出快捷键
        self.export_action.setShortcut("Ctrl+E")
        self.export_action.setShortcutContext(Qt.WidgetShortcut)
    
    def force_refresh(self):
        """强制刷新物料列表"""
        self.status_bar.setText("正在刷新...")
        QApplication.processEvents()  # 处理挂起的事件
        
        try:
            # 保存当前选中的行
            selected_rows = self.material_table.selectionModel().selectedRows()
            selected_ids = [self.material_table.item(row.row(), 0).text() 
                          for row in selected_rows if self.material_table.item(row.row(), 0)]
            
            # 执行刷新
            self.load_materials()
            
            # 尝试恢复选择
            if selected_ids:
                self.select_materials_by_ids(selected_ids)
            
            self.status_bar.setText("刷新完成")
            
        except Exception as e:
            self.status_bar.setText(f"刷新失败: {str(e)}")
            QMessageBox.warning(self, "刷新错误", f"刷新过程中发生错误:\n{str(e)}")
    
    def select_materials_by_ids(self, material_ids):
        """根据物料ID选择行"""
        self.material_table.clearSelection()
        
        for row in range(self.material_table.rowCount()):
            item = self.material_table.item(row, 0)
            if item and item.text() in material_ids:
                self.material_table.selectRow(row)
    
    def clear_search(self):
        """清空搜索"""
        self.search_input.clear()
        self.filter_combo.setCurrentIndex(0)  # 设置为"全部物料"
        self.load_materials()
    
    def apply_quick_filter(self):
        """应用快速筛选"""
        filter_text = self.filter_combo.currentText()
        
        if filter_text == "全部物料":
            self.populate_table(self.current_materials)
        elif filter_text == "液体物料":
            filtered = [m for m in self.current_materials if m.phase == "liquid"]
            self.populate_table(filtered)
        elif filter_text == "固体物料":
            filtered = [m for m in self.current_materials if m.phase == "solid"]
            self.populate_table(filtered)
        elif filter_text == "气体物料":
            filtered = [m for m in self.current_materials if m.phase == "gas"]
            self.populate_table(filtered)
        elif filter_text == "危险物料":
            filtered = [m for m in self.current_materials if m.hazard_class and m.hazard_class != "无"]
            self.populate_table(filtered)
    
    def load_materials(self):
        """加载物料数据"""
        if not self.process_manager:
            self.status_bar.setText("错误: 数据管理器未初始化")
            return
        
        try:
            # 临时禁用表格更新，避免闪烁
            self.material_table.setUpdatesEnabled(False)
            
            # 从数据管理器获取所有物料
            self.current_materials = self.process_manager.get_all_materials()
            
            # 将数据显示在表格中
            self.populate_table(self.current_materials)
            
            # 重新启用表格更新
            self.material_table.setUpdatesEnabled(True)
            
            # 强制重绘
            self.material_table.viewport().update()
            
            # 更新界面状态
            self.update_info_label()
            self.status_bar.setText(f"数据加载完成: {len(self.current_materials)} 条记录")
            
        except Exception as e:
            # 确保表格更新被重新启用
            self.material_table.setUpdatesEnabled(True)
            self.status_bar.setText(f"加载失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"加载物料数据时发生错误:\n{str(e)}")
    
    def populate_table(self, materials):
        """安全地填充表格，避免item所有权冲突"""
        # 停止所有信号，防止排序干扰
        self.material_table.blockSignals(True)
        self.material_table.setSortingEnabled(False)
        
        try:
            # 完全清空表格
            self.material_table.clearContents()
            self.material_table.setRowCount(0)
            
            # 设置新的行数
            self.material_table.setRowCount(len(materials))
            
            for i, material in enumerate(materials):
                # 物料数据
                self.material_table.setItem(i, 0, QTableWidgetItem(material.material_id))
                self.material_table.setItem(i, 1, QTableWidgetItem(material.name))
                self.material_table.setItem(i, 2, QTableWidgetItem(material.cas_number))
                self.material_table.setItem(i, 3, QTableWidgetItem(material.molecular_formula))
                self.material_table.setItem(i, 4, QTableWidgetItem(f"{material.molecular_weight:.2f}" if material.molecular_weight else ""))
                self.material_table.setItem(i, 5, QTableWidgetItem(material.phase))
                self.material_table.setItem(i, 6, QTableWidgetItem(f"{material.density:.2f}" if material.density else ""))
                self.material_table.setItem(i, 7, QTableWidgetItem(f"{material.boiling_point:.1f}" if material.boiling_point else ""))
                self.material_table.setItem(i, 8, QTableWidgetItem(f"{material.melting_point:.1f}" if material.melting_point else ""))
                self.material_table.setItem(i, 9, QTableWidgetItem(material.hazard_class))
            
            # 重新启用排序
            self.material_table.setSortingEnabled(True)
            self.material_table.sortItems(0, Qt.AscendingOrder)
            
        finally:
            # 恢复信号
            self.material_table.blockSignals(False)
        
        self.update_info_label()
    
    def update_info_label(self):
        """更新信息标签"""
        total = self.material_table.rowCount()
        selected = len(self.material_table.selectionModel().selectedRows())
        
        self.info_label.setText(f"总计: {total} 个物料")
        self.selected_label.setText(f"已选择: {selected} 个")
        
        # 更新状态栏
        search_term = self.search_input.text().strip()
        filter_text = self.filter_combo.currentText()
        
        if search_term:
            self.status_bar.setText(f"搜索 '{search_term}'，找到 {total} 个物料")
        elif filter_text != "全部物料":
            self.status_bar.setText(f"筛选 '{filter_text}'，显示 {total} 个物料")
        else:
            self.status_bar.setText(f"总计 {total} 个物料")
    
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
                materials = self.process_manager.get_all_materials()
            else:
                materials = self.process_manager.search_materials(search_term)
            
            self.current_materials = materials
            self.apply_quick_filter()  # 应用当前过滤器
            self.status_bar.setText(f"搜索到 {len(materials)} 条记录")
        except Exception as e:
            self.status_bar.setText(f"搜索失败: {str(e)}")
    
    def on_material_double_clicked(self, item):
        """物料双击事件"""
        row = item.row()
        material_id = self.material_table.item(row, 0).text()
        self.show_material_details(material_id)
        self.material_selected.emit(material_id)
    
    def show_material_details(self, material_id):
        """显示物料详情"""
        if not self.process_manager:
            return
        
        material = self.process_manager.get_material(material_id)
        if not material:
            return
        
        # 显示基本信息
        details = f"<h3>{material.name} ({material.material_id})</h3>"
        details += f"<b>CAS号:</b> {material.cas_number}<br>"
        details += f"<b>分子式:</b> {material.molecular_formula}<br>"
        details += f"<b>分子量:</b> {material.molecular_weight:.2f} g/mol<br>"
        details += f"<b>相态:</b> {material.phase}<br>"
        
        if material.notes:
            details += f"<br><b>备注:</b><br>{material.notes}"
        
        self.detail_text.setHtml(details)
        
        # 显示物理化学性质表格
        properties = [
            ("密度", f"{material.density:.2f} kg/m³" if material.density else "未知"),
            ("沸点", f"{material.boiling_point:.1f} °C" if material.boiling_point else "未知"),
            ("熔点", f"{material.melting_point:.1f} °C" if material.melting_point else "未知"),
            ("闪点", f"{material.flash_point:.1f} °C" if material.flash_point else "未知"),
            ("危险类别", material.hazard_class or "无"),
            ("蒸汽压", f"{material.vapor_pressure} Pa" if hasattr(material, 'vapor_pressure') and material.vapor_pressure else "未知"),
            ("粘度", f"{material.viscosity} Pa·s" if hasattr(material, 'viscosity') and material.viscosity else "未知"),
            ("热容", f"{material.heat_capacity} J/(mol·K)" if hasattr(material, 'heat_capacity') and material.heat_capacity else "未知"),
        ]
        
        self.property_table.setRowCount(len(properties))
        for i, (prop, value) in enumerate(properties):
            self.property_table.setItem(i, 0, QTableWidgetItem(prop))
            self.property_table.setItem(i, 1, QTableWidgetItem(value))
        
        # 设置表格自适应
        self.property_table.resizeRowsToContents()
    
    def on_selection_changed(self):
        """选择变化事件"""
        selected_rows = self.material_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            material_id = self.material_table.item(row, 0).text()
            self.show_material_details(material_id)
    
    def toggle_batch_mode(self, enabled):
        """切换批量操作模式"""
        self.batch_mode = enabled
        self.batch_panel.setVisible(enabled)
        
        if enabled:
            self.material_table.setSelectionMode(QTableWidget.MultiSelection)
        else:
            self.material_table.setSelectionMode(QTableWidget.ExtendedSelection)
            self.clear_batch_selection()
    
    def clear_batch_selection(self):
        """清除批量选择"""
        self.material_table.clearSelection()
        self.update_info_label()
    
    def get_selected_material_ids(self):
        """获取选中的物料ID列表"""
        selected_rows = self.material_table.selectionModel().selectedRows()
        selected_ids = []
        
        for row in selected_rows:
            material_id_item = self.material_table.item(row.row(), 0)
            if material_id_item:
                selected_ids.append(material_id_item.text())
        
        return selected_ids
    
    def select_all_materials(self):
        """全选所有物料"""
        self.material_table.selectAll()
        self.update_info_label()
    
    def clear_selection(self):
        """清除选择"""
        self.material_table.clearSelection()
        self.update_info_label()
    
    def copy_selected(self):
        """复制选中内容到剪贴板"""
        selected_items = self.material_table.selectedItems()
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
                item = self.material_table.item(row, col)
                row_data.append(item.text() if item else "")
            text += "\t".join(row_data) + "\n"
        
        clipboard = QApplication.clipboard()
        clipboard.setText(text.strip())
        
        self.status_bar.setText(f"已复制 {len(rows)} 行数据")
    
    # ==================== 核心功能方法 ====================
    
    def add_material(self):
        """添加物料"""
        dialog = MaterialDialog(self)
        if dialog.exec() == QDialog.Accepted:
            material = dialog.get_material()
            if material and self.process_manager:
                try:
                    if self.process_manager.add_material(material):
                        # 延迟一小段时间再刷新，确保UI完全处理完
                        QTimer.singleShot(50, self.load_materials)
                        self.material_list_updated.emit()
                        self.status_bar.setText(f"物料 '{material.name}' 添加成功")
                    else:
                        QMessageBox.warning(self, "错误", "物料添加失败，可能物料ID已存在。")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"添加物料时发生错误:\n{str(e)}")
    
    def edit_material(self):
        """编辑物料"""
        selected_row = self.material_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要编辑的物料")
            return
        
        material_id = self.material_table.item(selected_row, 0).text()
        if not self.process_manager:
            return
        
        material = self.process_manager.get_material(material_id)
        if not material:
            QMessageBox.warning(self, "错误", "物料未找到")
            return
        
        dialog = MaterialDialog(self, material)
        if dialog.exec() == QDialog.Accepted:
            updated_material = dialog.get_material()
            if updated_material and self.process_manager:
                try:
                    if self.process_manager.update_material(updated_material):
                        QTimer.singleShot(50, self.load_materials)
                        self.material_list_updated.emit()
                        self.status_bar.setText(f"物料 '{updated_material.name}' 更新成功")
                    else:
                        QMessageBox.warning(self, "错误", "物料更新失败")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"更新物料时发生错误:\n{str(e)}")
    
    def delete_material(self):
        """删除物料 - 支持单个和批量删除"""
        selected_ids = self.get_selected_material_ids()
        if not selected_ids:
            QMessageBox.warning(self, "警告", "请先选择要删除的物料")
            return
        
        # 获取选中的第一个物料（用于单个删除时的确认信息）
        material = None
        if selected_ids:
            material = self.process_manager.get_material(selected_ids[0])
        
        # 确认删除
        confirmed = False
        
        if len(selected_ids) == 1 and material:
            # 单个物料删除确认
            reply = QMessageBox.question(
                self, "确认删除",
                f"确定要删除物料 '{material.name}' 吗？\n此操作不可恢复！",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            confirmed = (reply == QMessageBox.Yes)
        else:
            # 批量删除确认
            confirmed = self.confirm_batch_delete(selected_ids)
        
        # 如果用户确认删除，执行删除操作
        if confirmed:
            success_count = 0
            failed_count = 0
            
            for material_id in selected_ids:
                if self.process_manager.delete_material(material_id):
                    success_count += 1
                else:
                    failed_count += 1
            
            # 重新加载数据
            QTimer.singleShot(50, self.load_materials)
            self.material_list_updated.emit()
            
            # 显示操作结果
            if len(selected_ids) == 1:
                if success_count == 1:
                    self.status_bar.setText(f"物料 '{material.name}' 删除成功")
                else:
                    self.status_bar.setText(f"物料 '{material.name}' 删除失败")
            else:
                message = f"批量删除完成: 成功 {success_count} 个"
                if failed_count > 0:
                    message += f", 失败 {failed_count} 个"
                
                QMessageBox.information(self, "删除完成", message)
                self.status_bar.setText(f"批量删除完成: {success_count}/{len(selected_ids)} 个成功")
    
    def confirm_batch_delete(self, selected_ids):
        """批量删除确认对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle("批量删除确认")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # 显示选中物料数量
        layout.addWidget(QLabel(f"将要删除 {len(selected_ids)} 个物料"))
        
        # 显示部分物料名称（最多显示5个）
        material_names = []
        for material_id in selected_ids[:5]:  # 只显示前5个
            material = self.process_manager.get_material(material_id)
            if material:
                material_names.append(f"• {material.name}")
        
        if material_names:
            names_text = "\n".join(material_names)
            if len(selected_ids) > 5:
                names_text += f"\n...等 {len(selected_ids)} 个物料"
            
            names_label = QLabel(names_text)
            layout.addWidget(names_label)
        
        # 警告信息
        warning_label = QLabel("⚠️ 此操作不可恢复！请确认")
        warning_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(warning_label)
        
        # 确认复选框（防止误操作）
        confirm_checkbox = QCheckBox("我确认要删除这些物料")
        layout.addWidget(confirm_checkbox)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).setEnabled(False)  # 初始禁用
        
        # 只有当用户勾选确认框时才启用确定按钮
        def update_button_state(checked):
            button_box.button(QDialogButtonBox.Ok).setEnabled(checked)
        
        confirm_checkbox.stateChanged.connect(update_button_state)
        
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        layout.addWidget(button_box)
        
        return dialog.exec() == QDialog.Accepted
    
    def import_materials(self):
        """导入物料数据"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择导入文件", "", 
            "Excel文件 (*.xlsx *.xls);;CSV文件 (*.csv);;JSON文件 (*.json)"
        )
        
        if not file_path:
            return
        
        # 选择导入模式
        dialog = ImportDialog(self)
        if dialog.exec() != QDialog.Accepted:
            return
        
        import_mode = dialog.get_import_mode()
        
        try:
            if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                df = pd.read_excel(file_path)
            elif file_path.endswith('.csv'):
                df = pd.read_csv(file_path, encoding='utf-8')
            elif file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                df = pd.DataFrame(data)
            else:
                raise ValueError("不支持的文件格式")
            
            # 验证数据
            if not self.validate_import_data(df):
                return
            
            # 创建导入工作线程
            self.import_thread = ImportThread(df, import_mode, self.process_manager)
            self.import_thread.progress.connect(self.on_import_progress)
            self.import_thread.finished.connect(self.on_import_finished)
            self.import_thread.error.connect(self.on_import_error)
            
            # 显示进度对话框
            self.progress_dialog = QProgressDialog("导入中...", "取消", 0, len(df), self)
            self.progress_dialog.setWindowTitle("导入物料")
            self.progress_dialog.setWindowModality(Qt.WindowModal)
            self.progress_dialog.canceled.connect(self.import_thread.cancel)
            self.progress_dialog.show()
            
            self.import_thread.start()
            
        except Exception as e:
            QMessageBox.critical(self, "导入失败", f"导入文件时发生错误:\n{str(e)}")
    
    def validate_import_data(self, df):
        """验证导入数据"""
        required_columns = ['material_id', 'name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            QMessageBox.warning(self, "数据验证失败", 
                               f"缺少必要列: {', '.join(missing_columns)}")
            return False
        
        # 检查重复ID
        duplicates = df[df.duplicated('material_id', keep=False)]
        if not duplicates.empty:
            reply = QMessageBox.question(
                self, "发现重复ID",
                f"发现 {len(duplicates)} 条重复的物料ID。是否继续导入？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return False
        
        return True
    
    def on_import_progress(self, value):
        """导入进度更新"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.setValue(value)
    
    def on_import_finished(self, stats):
        """导入完成"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        
        self.load_materials()
        QMessageBox.information(
            self, "导入完成",
            f"导入统计:\n成功: {stats['success']}\n失败: {stats['failed']}\n跳过: {stats['skipped']}"
        )
    
    def on_import_error(self, error_msg):
        """导入错误"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        
        QMessageBox.critical(self, "导入错误", error_msg)
    
    def export_materials(self):
        """导出物料数据"""
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "选择导出文件", "materials_export.xlsx",
            "Excel文件 (*.xlsx);;CSV文件 (*.csv);;JSON文件 (*.json)"
        )
        
        if not file_path:
            return
        
        # 选择导出范围
        dialog = ExportDialog(self, len(self.current_materials))
        if dialog.exec() != QDialog.Accepted:
            return
        
        export_mode, include_all = dialog.get_export_options()
        
        try:
            if export_mode == 'current':
                data = self.current_materials
            elif export_mode == 'selected':
                selected_ids = self.get_selected_material_ids()
                if not selected_ids:
                    QMessageBox.warning(self, "警告", "请先选择要导出的物料")
                    return
                data = [m for m in self.current_materials if m.material_id in selected_ids]
            else:  # 'all'
                data = self.process_manager.get_all_materials()
            
            # 转换为DataFrame
            rows = []
            for material in data:
                row = {
                    'material_id': material.material_id,
                    'name': material.name,
                    'cas_number': material.cas_number,
                    'molecular_formula': material.molecular_formula,
                    'molecular_weight': material.molecular_weight,
                    'phase': material.phase,
                    'density': material.density,
                    'boiling_point': material.boiling_point,
                    'melting_point': material.melting_point,
                    'flash_point': material.flash_point,
                    'hazard_class': material.hazard_class,
                    'notes': material.notes
                }
                rows.append(row)
            
            df = pd.DataFrame(rows)
            
            # 根据文件类型保存
            if file_path.endswith('.xlsx'):
                df.to_excel(file_path, index=False)
            elif file_path.endswith('.csv'):
                df.to_csv(file_path, index=False, encoding='utf-8')
            elif file_path.endswith('.json'):
                df.to_json(file_path, orient='records', force_ascii=False, indent=2)
            
            self.status_bar.setText(f"导出完成: {len(data)} 条记录")
            QMessageBox.information(self, "导出成功", f"成功导出 {len(data)} 条记录到:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出文件时发生错误:\n{str(e)}")
    
    def batch_edit_materials(self):
        """批量编辑物料"""
        selected_ids = self.get_selected_material_ids()
        if not selected_ids:
            QMessageBox.warning(self, "警告", "请先选择要编辑的物料")
            return
        
        dialog = BatchEditDialog(selected_ids, self.process_manager, self)
        if dialog.exec() == QDialog.Accepted:
            self.load_materials()
    
    def batch_export_materials(self):
        """批量导出选中的物料"""
        selected_ids = self.get_selected_material_ids()
        if not selected_ids:
            QMessageBox.warning(self, "警告", "请先选择要导出的物料")
            return
        
        self.export_selected_materials(selected_ids)
    
    def batch_delete_materials(self):
        """批量删除物料"""
        selected_ids = self.get_selected_material_ids()
        if not selected_ids:
            QMessageBox.warning(self, "警告", "请先选择要删除的物料")
            return
        
        reply = QMessageBox.question(
            self, "确认批量删除",
            f"确定要删除选中的 {len(selected_ids)} 个物料吗？\n此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success_count = 0
            for material_id in selected_ids:
                if self.process_manager.delete_material(material_id):
                    success_count += 1
            
            self.load_materials()
            self.material_list_updated.emit()
            
            QMessageBox.information(
                self, "删除完成",
                f"已删除 {success_count} 个物料"
            )
    
    def export_selected_materials(self, material_ids):
        """导出选中的物料"""
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "导出选中物料", "selected_materials.xlsx",
            "Excel文件 (*.xlsx);;CSV文件 (*.csv);;JSON文件 (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            materials = []
            for material_id in material_ids:
                material = self.process_manager.get_material(material_id)
                if material:
                    materials.append(material)
            
            # 转换为DataFrame
            rows = []
            for material in materials:
                row = {
                    'material_id': material.material_id,
                    'name': material.name,
                    'cas_number': material.cas_number,
                    'molecular_formula': material.molecular_formula,
                    'molecular_weight': material.molecular_weight,
                    'phase': material.phase,
                    'density': material.density,
                    'boiling_point': material.boiling_point,
                    'melting_point': material.melting_point,
                    'flash_point': material.flash_point,
                    'hazard_class': material.hazard_class,
                    'notes': material.notes
                }
                rows.append(row)
            
            df = pd.DataFrame(rows)
            
            # 根据文件类型保存
            if file_path.endswith('.xlsx'):
                df.to_excel(file_path, index=False)
            elif file_path.endswith('.csv'):
                df.to_csv(file_path, index=False, encoding='utf-8')
            elif file_path.endswith('.json'):
                df.to_json(file_path, orient='records', force_ascii=False, indent=2)
            
            QMessageBox.information(self, "导出成功", f"成功导出 {len(materials)} 个物料")
            
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出文件时发生错误:\n{str(e)}")
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
        <h3>物料数据库使用说明</h3>
        
        <h4>主要功能：</h4>
        <ul>
            <li><b>添加物料</b>: 点击工具栏的"添加"按钮</li>
            <li><b>编辑物料</b>: 选择物料后点击"编辑"按钮或双击物料行</li>
            <li><b>删除物料</b>: 选择物料后点击"删除"按钮</li>
            <li><b>批量操作</b>: 开启批量模式后可进行批量编辑、导出、删除</li>
        </ul>
        
        <h4>搜索功能：</h4>
        <ul>
            <li>支持按物料名称、CAS号、分子式搜索</li>
            <li>使用快速筛选功能按物料类型过滤</li>
        </ul>
        
        <h4>快捷键：</h4>
        <ul>
            <li><b>Ctrl+C</b>: 复制选中内容</li>
            <li><b>Ctrl+E</b>: 导出物料数据</li>
            <li><b>Delete</b>: 删除选中物料</li>
            <li><b>F5</b>: 刷新物料列表</li>
            <li><b>Ctrl+A</b>: 全选</li>
        </ul>
        """
        
        QMessageBox.information(self, "物料数据库帮助", help_text)


# ==================== 对话框类 ====================

class ImportDialog(QDialog):
    """导入选项对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("导入选项")
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        # 导入模式选择
        mode_group = QGroupBox("导入模式")
        mode_layout = QVBoxLayout()
        
        self.replace_radio = QCheckBox("替换现有数据（清空后导入）")
        self.update_radio = QCheckBox("更新现有数据（ID存在则更新）")
        self.append_radio = QCheckBox("追加新数据（ID存在则跳过）")
        self.append_radio.setChecked(True)
        
        mode_layout.addWidget(self.replace_radio)
        mode_layout.addWidget(self.update_radio)
        mode_layout.addWidget(self.append_radio)
        mode_group.setLayout(mode_layout)
        
        layout.addWidget(mode_group)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_import_mode(self):
        """获取导入模式"""
        if self.replace_radio.isChecked():
            return 'replace'
        elif self.update_radio.isChecked():
            return 'update'
        else:
            return 'append'


class ExportDialog(QDialog):
    """导出选项对话框"""
    
    def __init__(self, parent=None, current_count=0):
        super().__init__(parent)
        self.current_count = current_count
        self.setWindowTitle("导出选项")
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        # 导出范围选择
        range_group = QGroupBox("导出范围")
        range_layout = QVBoxLayout()
        
        self.current_radio = QCheckBox(f"当前视图 ({self.current_count} 个物料)")
        self.current_radio.setChecked(True)
        self.selected_radio = QCheckBox("选中的物料")
        self.all_radio = QCheckBox("所有物料")
        
        range_layout.addWidget(self.current_radio)
        range_layout.addWidget(self.selected_radio)
        range_layout.addWidget(self.all_radio)
        range_group.setLayout(range_layout)
        
        layout.addWidget(range_group)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_export_options(self):
        """获取导出选项"""
        if self.current_radio.isChecked():
            return 'current', False
        elif self.selected_radio.isChecked():
            return 'selected', False
        else:
            return 'all', True


class BatchEditDialog(QDialog):
    """批量编辑对话框"""
    
    def __init__(self, material_ids, process_manager, parent=None):
        super().__init__(parent)
        self.material_ids = material_ids
        self.process_manager = process_manager
        self.setWindowTitle("批量编辑")
        self.setMinimumWidth(400)
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel(f"批量编辑 {len(self.material_ids)} 个物料"))
        
        form_layout = QFormLayout()
        
        # 可批量编辑的字段
        self.phase_combo = QComboBox()
        self.phase_combo.addItems(["", "liquid", "solid", "gas"])
        self.phase_combo.setCurrentIndex(0)
        form_layout.addRow("相态:", self.phase_combo)
        
        self.hazard_input = QLineEdit()
        self.hazard_input.setPlaceholderText("留空则不修改")
        form_layout.addRow("危险类别:", self.hazard_input)
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        self.notes_input.setPlaceholderText("留空则不修改")
        form_layout.addRow("备注:", self.notes_input)
        
        layout.addLayout(form_layout)
        
        # 操作选项
        self.append_notes = QCheckBox("追加备注（而不是替换）")
        layout.addWidget(self.append_notes)
        
        layout.addWidget(QLabel("注意：空字段不会修改原有值"))
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.apply_changes)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def apply_changes(self):
        """应用批量修改"""
        changes = {}
        
        phase = self.phase_combo.currentText()
        if phase:
            changes['phase'] = phase
        
        hazard = self.hazard_input.text().strip()
        if hazard:
            changes['hazard_class'] = hazard
        
        notes = self.notes_input.toPlainText().strip()
        if notes:
            changes['notes'] = notes
            changes['append_notes'] = self.append_notes.isChecked()
        
        if not changes:
            QMessageBox.warning(self, "警告", "没有修改任何字段")
            return
        
        success_count = 0
        for material_id in self.material_ids:
            material = self.process_manager.get_material(material_id)
            if material:
                # 应用修改
                if 'phase' in changes:
                    material.phase = changes['phase']
                if 'hazard_class' in changes:
                    material.hazard_class = changes['hazard_class']
                if 'notes' in changes:
                    if changes.get('append_notes'):
                        material.notes = (material.notes + "\n" + changes['notes']).strip()
                    else:
                        material.notes = changes['notes']
                
                if self.process_manager.update_material(material):
                    success_count += 1
        
        QMessageBox.information(self, "批量编辑完成", f"成功更新 {success_count} 个物料")
        self.accept()


class ImportThread(QThread):
    """导入工作线程"""
    
    progress = Signal(int)
    finished = Signal(dict)
    error = Signal(str)
    
    def __init__(self, df, import_mode, process_manager):
        super().__init__()
        self.df = df
        self.import_mode = import_mode
        self.process_manager = process_manager
        self._is_cancelled = False
    
    def run(self):
        """执行导入"""
        try:
            stats = {'success': 0, 'failed': 0, 'skipped': 0}
            
            # 如果是替换模式，先清空所有物料
            if self.import_mode == 'replace':
                all_materials = self.process_manager.get_all_materials()
                for material in all_materials:
                    self.process_manager.delete_material(material.material_id)
            
            # 导入数据
            from ..data.data_models import MaterialProperty
            
            for i, row in self.df.iterrows():
                if self._is_cancelled:
                    break
                
                try:
                    # 创建物料对象
                    material = MaterialProperty(
                        material_id=str(row.get('material_id', '')).strip(),
                        name=str(row.get('name', '')).strip(),
                        cas_number=str(row.get('cas_number', '')).strip(),
                        molecular_formula=str(row.get('molecular_formula', '')).strip(),
                        molecular_weight=float(row['molecular_weight']) if pd.notna(row.get('molecular_weight')) else 0,
                        phase=str(row.get('phase', 'liquid')).strip(),
                        density=float(row['density']) if pd.notna(row.get('density')) else None,
                        boiling_point=float(row['boiling_point']) if pd.notna(row.get('boiling_point')) else None,
                        melting_point=float(row['melting_point']) if pd.notna(row.get('melting_point')) else None,
                        flash_point=float(row['flash_point']) if pd.notna(row.get('flash_point')) else None,
                        hazard_class=str(row.get('hazard_class', '')).strip(),
                        notes=str(row.get('notes', '')).strip()
                    )
                    
                    # 检查物料ID是否已存在
                    existing = self.process_manager.get_material(material.material_id)
                    
                    if existing:
                        if self.import_mode == 'update':
                            # 更新现有物料
                            if self.process_manager.update_material(material):
                                stats['success'] += 1
                            else:
                                stats['failed'] += 1
                        else:  # append模式，跳过
                            stats['skipped'] += 1
                    else:
                        # 添加新物料
                        if self.process_manager.add_material(material):
                            stats['success'] += 1
                        else:
                            stats['failed'] += 1
                    
                except Exception as e:
                    stats['failed'] += 1
                
                # 更新进度
                self.progress.emit(i + 1)
            
            self.finished.emit(stats)
            
        except Exception as e:
            self.error.emit(str(e))
    
    def cancel(self):
        """取消导入"""
        self._is_cancelled = True


# ==================== MaterialDialog类 ====================

class MaterialDialog(QDialog):
    """物料对话框"""
    
    def __init__(self, parent=None, material=None):
        super().__init__(parent)
        self.material = material
        self.setWindowTitle("添加物料" if not material else "编辑物料")
        self.setMinimumWidth(600)
        
        self.setup_ui()
        if material:
            self.load_material_data()
        
        # 连接验证信号
        self.cas_input.textChanged.connect(self.validate_cas)
        self.formula_input.textChanged.connect(self.validate_formula)
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        # 使用标签页组织内容
        tab_widget = QTabWidget()
        
        # 基本信息标签页
        basic_tab = QWidget()
        basic_layout = QFormLayout(basic_tab)
        
        self.material_id_input = QLineEdit()
        self.name_input = QLineEdit()
        self.cas_input = QLineEdit()
        self.cas_status = QLabel()
        self.cas_status.setStyleSheet("color: gray;")
        
        self.formula_input = QLineEdit()
        self.formula_status = QLabel()
        self.formula_status.setStyleSheet("color: gray;")
        
        self.mw_input = QDoubleSpinBox()
        self.mw_input.setRange(0, 10000)
        self.mw_input.setDecimals(2)
        self.mw_input.setSuffix(" g/mol")
        
        basic_layout.addRow("物料ID*:", self.material_id_input)
        basic_layout.addRow("物料名称*:", self.name_input)
        basic_layout.addRow("CAS号:", self.cas_input)
        basic_layout.addRow("", self.cas_status)
        basic_layout.addRow("分子式:", self.formula_input)
        basic_layout.addRow("", self.formula_status)
        basic_layout.addRow("分子量:", self.mw_input)
        
        tab_widget.addTab(basic_tab, "基本信息")
        
        # 物理性质标签页
        property_tab = QWidget()
        property_layout = QFormLayout(property_tab)
        
        self.density_input = QDoubleSpinBox()
        self.density_input.setRange(0, 10000)
        self.density_input.setDecimals(2)
        self.density_input.setSuffix(" kg/m³")
        
        self.phase_combo = QComboBox()
        self.phase_combo.addItems(["liquid", "solid", "gas"])
        
        self.boiling_point_input = QDoubleSpinBox()
        self.boiling_point_input.setRange(-273, 10000)
        self.boiling_point_input.setDecimals(1)
        self.boiling_point_input.setSuffix(" °C")
        
        self.melting_point_input = QDoubleSpinBox()
        self.melting_point_input.setRange(-273, 10000)
        self.melting_point_input.setDecimals(1)
        self.melting_point_input.setSuffix(" °C")
        
        property_layout.addRow("密度:", self.density_input)
        property_layout.addRow("相态:", self.phase_combo)
        property_layout.addRow("沸点:", self.boiling_point_input)
        property_layout.addRow("熔点:", self.melting_point_input)
        
        tab_widget.addTab(property_tab, "物理性质")
        
        # 安全信息标签页
        safety_tab = QWidget()
        safety_layout = QFormLayout(safety_tab)
        
        self.hazard_class_input = QLineEdit()
        self.flash_point_input = QDoubleSpinBox()
        self.flash_point_input.setRange(-273, 10000)
        self.flash_point_input.setDecimals(1)
        self.flash_point_input.setSuffix(" °C")
        
        safety_layout.addRow("危险类别:", self.hazard_class_input)
        safety_layout.addRow("闪点:", self.flash_point_input)
        
        tab_widget.addTab(safety_tab, "安全信息")
        
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
    
    def validate_cas(self, text):
        """验证CAS号格式"""
        text = text.strip()
        if not text:
            self.cas_status.setText("")
            return True
        
        # CAS号格式: 000000-00-0
        pattern = r'^\d{1,7}-\d{2}-\d$'
        if re.match(pattern, text):
            self.cas_status.setText("✓ 格式正确")
            self.cas_status.setStyleSheet("color: green;")
            return True
        else:
            self.cas_status.setText("⚠ 格式应为: XXXXXXX-XX-X")
            self.cas_status.setStyleSheet("color: orange;")
            return False
    
    def validate_formula(self, text):
        """验证分子式格式"""
        text = text.strip()
        if not text:
            self.formula_status.setText("")
            return True
        
        # 简单的分子式验证（可扩展）
        if re.match(r'^[A-Z][a-z]?\d*([A-Z][a-z]?\d*)*$', text):
            self.formula_status.setText("✓ 格式正确")
            self.formula_status.setStyleSheet("color: green;")
            return True
        else:
            self.formula_status.setText("⚠ 检查格式（如: H2O, C6H12O6）")
            self.formula_status.setStyleSheet("color: orange;")
            return False
    
    def validate_and_accept(self):
        """验证并接受"""
        material_id = self.material_id_input.text().strip()
        name = self.name_input.text().strip()
        
        errors = []
        
        if not material_id:
            errors.append("物料ID不能为空")
        if not name:
            errors.append("物料名称不能为空")
        
        # 验证CAS号
        if self.cas_input.text().strip() and not self.validate_cas(self.cas_input.text()):
            errors.append("CAS号格式不正确")
        
        if errors:
            self.validation_label.setText("错误: " + "; ".join(errors))
            return
        
        self.validation_label.setText("")
        self.accept()
    
    def load_material_data(self):
        """加载物料数据"""
        if not self.material:
            return
        
        self.material_id_input.setText(self.material.material_id)
        self.name_input.setText(self.material.name)
        self.cas_input.setText(self.material.cas_number)
        self.formula_input.setText(self.material.molecular_formula)
        self.mw_input.setValue(self.material.molecular_weight)
        
        if self.material.density:
            self.density_input.setValue(self.material.density)
        
        index = self.phase_combo.findText(self.material.phase)
        if index >= 0:
            self.phase_combo.setCurrentIndex(index)
        
        if self.material.boiling_point:
            self.boiling_point_input.setValue(self.material.boiling_point)
        
        if self.material.melting_point:
            self.melting_point_input.setValue(self.material.melting_point)
        
        self.hazard_class_input.setText(self.material.hazard_class)
        
        if self.material.flash_point:
            self.flash_point_input.setValue(self.material.flash_point)
        
        self.notes_input.setText(self.material.notes)
        
        # 触发验证
        self.validate_cas(self.material.cas_number)
        self.validate_formula(self.material.molecular_formula)
    
    def get_material(self):
        """获取物料对象"""
        from ..data.data_models import MaterialProperty
        
        material_id = self.material_id_input.text().strip()
        name = self.name_input.text().strip()
        
        material = MaterialProperty(
            material_id=material_id,
            name=name,
            cas_number=self.cas_input.text().strip(),
            molecular_formula=self.formula_input.text().strip(),
            molecular_weight=self.mw_input.value(),
            density=self.density_input.value() if self.density_input.value() > 0 else None,
            phase=self.phase_combo.currentText(),
            boiling_point=self.boiling_point_input.value() if self.boiling_point_input.value() > -273 else None,
            melting_point=self.melting_point_input.value() if self.melting_point_input.value() > -273 else None,
            flash_point=self.flash_point_input.value() if self.flash_point_input.value() > -273 else None,
            hazard_class=self.hazard_class_input.text().strip(),
            notes=self.notes_input.toPlainText().strip()
        )
        
        return material