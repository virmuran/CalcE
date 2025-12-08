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

# 导入 Qt 相关 - 修复：使用 Signal 而不是 pyqtSignal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QDoubleSpinBox, QComboBox, QTextEdit, QGroupBox,
    QCheckBox, QFileDialog, QProgressDialog, QSplitter, QTabWidget,
    QMenu, QApplication, QFrame, QToolBar, QSizePolicy
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
    from ..process_design_data import MaterialProperty
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
    """物料数据库标签页 - 增强版"""
    
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
    
    def setup_ui(self):
        """设置UI"""
        main_layout = QVBoxLayout(self)
        
        # 工具栏
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(16, 16))
        
        # 工具栏动作
        self.add_action = QAction("添加", self)
        self.add_action.triggered.connect(self.add_material)
        toolbar.addAction(self.add_action)
        
        self.edit_action = QAction("编辑", self)
        self.edit_action.triggered.connect(self.edit_material)
        toolbar.addAction(self.edit_action)
        
        self.delete_action = QAction("删除", self)
        self.delete_action.triggered.connect(self.delete_material)
        toolbar.addAction(self.delete_action)
        
        toolbar.addSeparator()
        
        self.import_action = QAction("导入", self)
        self.import_action.triggered.connect(self.import_materials)
        toolbar.addAction(self.import_action)
        
        self.export_action = QAction("导出", self)
        self.export_action.triggered.connect(self.export_materials)
        toolbar.addAction(self.export_action)
        
        toolbar.addSeparator()
        
        self.copy_action = QAction("复制", self)
        self.copy_action.triggered.connect(self.copy_selected)
        toolbar.addAction(self.copy_action)
        
        self.paste_action = QAction("粘贴", self)
        self.paste_action.triggered.connect(self.paste_material)
        toolbar.addAction(self.paste_action)
        
        toolbar.addSeparator()
        
        self.batch_toggle_action = QAction("批量模式", self)
        self.batch_toggle_action.setCheckable(True)
        self.batch_toggle_action.toggled.connect(self.toggle_batch_mode)
        toolbar.addAction(self.batch_toggle_action)
        
        main_layout.addWidget(toolbar)
        
        # 搜索和过滤区域
        filter_frame = QFrame()
        filter_frame.setFrameStyle(QFrame.StyledPanel)
        filter_layout = QHBoxLayout(filter_frame)
        
        # 搜索框
        search_layout = QHBoxLayout()
        search_label = QLabel("搜索:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("物料名称、CAS号或分子式...")
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
        
        # 相态过滤器
        self.phase_filter = QComboBox()
        self.phase_filter.addItem("所有相态")
        self.phase_filter.addItems(["liquid", "solid", "gas"])
        self.phase_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(QLabel("相态:"))
        filter_layout.addWidget(self.phase_filter)
        
        # 危险类别过滤器
        self.hazard_filter = QComboBox()
        self.hazard_filter.addItem("所有类别")
        self.hazard_filter.addItems(["易燃", "有毒", "腐蚀性", "爆炸性", "氧化剂", "无"])
        self.hazard_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(QLabel("危险类别:"))
        filter_layout.addWidget(self.hazard_filter)
        
        main_layout.addWidget(filter_frame)
        
        # 分割器：左侧表格，右侧详情
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：物料表格
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        
        # 表格上方信息栏
        info_layout = QHBoxLayout()
        self.info_label = QLabel("总计: 0 个物料")
        info_layout.addWidget(self.info_label)
        info_layout.addStretch()
        
        self.selected_label = QLabel("已选择: 0 个")
        info_layout.addWidget(self.selected_label)
        table_layout.addLayout(info_layout)
        
        # 物料表格
        self.material_table = QTableWidget()
        self.material_table.setColumnCount(11)  # 增加列数
        self.material_table.setHorizontalHeaderLabels([
            "",  # 选择框
            "物料ID", "名称", "CAS号", "分子式", "分子量", 
            "相态", "密度", "沸点", "熔点", "危险类别"
        ])
        
        # 设置表头
        header = self.material_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # 选择列固定宽度
        header.resizeSection(0, 30)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # ID列自适应
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # 名称列拉伸
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # CAS号
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 分子式
        
        # 启用排序
        self.material_table.setSortingEnabled(True)
        
        # 设置选择模式
        self.material_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.material_table.setSelectionMode(QTableWidget.ExtendedSelection)
        
        # 连接信号
        self.material_table.itemDoubleClicked.connect(self.on_material_double_clicked)
        self.material_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        table_layout.addWidget(self.material_table)
        
        splitter.addWidget(table_widget)
        
        # 右侧：物料详情
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        
        # 详情标签
        detail_label = QLabel("物料详情")
        detail_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        detail_layout.addWidget(detail_label)
        
        # 详情显示区域
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        self.detail_text.setMaximumHeight(300)
        detail_layout.addWidget(self.detail_text)
        
        # 物性标签
        property_label = QLabel("物理化学性质")
        property_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        detail_layout.addWidget(property_label)
        
        # 物性表格
        self.property_table = QTableWidget()
        self.property_table.setColumnCount(2)
        self.property_table.setHorizontalHeaderLabels(["属性", "值"])
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
        self.batch_edit_btn.clicked.connect(self.batch_edit_materials)
        batch_layout.addWidget(self.batch_edit_btn)
        
        self.batch_export_btn = QPushButton("批量导出")
        self.batch_export_btn.clicked.connect(self.batch_export_materials)
        batch_layout.addWidget(self.batch_export_btn)
        
        self.batch_delete_btn = QPushButton("批量删除")
        self.batch_delete_btn.clicked.connect(self.batch_delete_materials)
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
        self.copy_action.setShortcut(QKeySequence.Copy)
        self.copy_action.setShortcutContext(Qt.WidgetShortcut)
        
        # 粘贴快捷键
        self.paste_action.setShortcut(QKeySequence.Paste)
        self.paste_action.setShortcutContext(Qt.WidgetShortcut)
        
        # 删除快捷键
        self.delete_action.setShortcut(QKeySequence.Delete)
        self.delete_action.setShortcutContext(Qt.WidgetShortcut)
        
        # 刷新快捷键
        self.refresh_action = QAction("刷新", self)
        self.refresh_action.setShortcut(QKeySequence.Refresh)
        self.refresh_action.triggered.connect(self.load_materials)
        self.addAction(self.refresh_action)
    
    def load_materials(self):
        """加载物料数据"""
        if not self.process_manager:
            self.status_bar.setText("错误: 数据管理器未初始化")
            return
        
        try:
            self.current_materials = self.process_manager.get_all_materials()
            self.populate_table(self.current_materials)
            self.update_info_label()
            self.status_bar.setText(f"数据加载完成: {len(self.current_materials)} 条记录")
        except Exception as e:
            self.status_bar.setText(f"加载失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"加载物料数据时发生错误:\n{str(e)}")
    
    def populate_table(self, materials):
        """填充表格数据"""
        self.material_table.setRowCount(len(materials))
        
        for i, material in enumerate(materials):
            # 选择框
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            checkbox_item.setCheckState(Qt.Unchecked)
            self.material_table.setItem(i, 0, checkbox_item)
            
            # 物料数据
            self.material_table.setItem(i, 1, QTableWidgetItem(material.material_id))
            self.material_table.setItem(i, 2, QTableWidgetItem(material.name))
            self.material_table.setItem(i, 3, QTableWidgetItem(material.cas_number))
            self.material_table.setItem(i, 4, QTableWidgetItem(material.molecular_formula))
            self.material_table.setItem(i, 5, QTableWidgetItem(f"{material.molecular_weight:.2f}" if material.molecular_weight else ""))
            self.material_table.setItem(i, 6, QTableWidgetItem(material.phase))
            self.material_table.setItem(i, 7, QTableWidgetItem(f"{material.density:.2f}" if material.density else ""))
            self.material_table.setItem(i, 8, QTableWidgetItem(f"{material.boiling_point:.1f}" if material.boiling_point else ""))
            self.material_table.setItem(i, 9, QTableWidgetItem(f"{material.melting_point:.1f}" if material.melting_point else ""))
            self.material_table.setItem(i, 10, QTableWidgetItem(material.hazard_class))
        
        self.update_info_label()
    
    def update_info_label(self):
        """更新信息标签"""
        total = self.material_table.rowCount()
        selected = len([i for i in range(total) 
                       if self.material_table.item(i, 0).checkState() == Qt.Checked])
        self.info_label.setText(f"总计: {total} 个物料")
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
                materials = self.process_manager.get_all_materials()
            else:
                materials = self.process_manager.search_materials(search_term)
            
            self.current_materials = materials
            self.apply_filters()  # 应用当前过滤器
            self.status_bar.setText(f"搜索到 {len(materials)} 条记录")
        except Exception as e:
            self.status_bar.setText(f"搜索失败: {str(e)}")
    
    def apply_filters(self):
        """应用过滤器"""
        phase_filter = self.phase_filter.currentText()
        hazard_filter = self.hazard_filter.currentText()
        
        filtered_materials = self.current_materials.copy()
        
        # 应用相态过滤
        if phase_filter != "所有相态":
            filtered_materials = [m for m in filtered_materials if m.phase == phase_filter]
        
        # 应用危险类别过滤
        if hazard_filter != "所有类别":
            filtered_materials = [m for m in filtered_materials if hazard_filter in m.hazard_class]
        
        self.populate_table(filtered_materials)
    
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
            materials = self.process_manager.advanced_search_materials(criteria)
            self.current_materials = materials
            self.populate_table(materials)
            self.status_bar.setText(f"高级搜索找到 {len(materials)} 条记录")
        except Exception as e:
            self.status_bar.setText(f"高级搜索失败: {str(e)}")
            QMessageBox.warning(self, "搜索失败", str(e))
    
    def on_material_double_clicked(self, item):
        """物料双击事件"""
        if item.column() == 0:  # 点击选择框时不触发
            return
        
        row = item.row()
        material_id = self.material_table.item(row, 1).text()
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
    
    def on_selection_changed(self):
        """选择变化事件"""
        selected_rows = self.material_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            material_id = self.material_table.item(row, 1).text()
            self.show_material_details(material_id)
    
    def toggle_batch_mode(self, enabled):
        """切换批量操作模式"""
        self.batch_mode = enabled
        self.batch_panel.setVisible(enabled)
        
        if enabled:
            self.material_table.setSelectionMode(QTableWidget.NoSelection)
            for i in range(self.material_table.rowCount()):
                item = self.material_table.item(i, 0)
                item.setFlags(item.flags() | Qt.ItemIsEnabled)
        else:
            self.material_table.setSelectionMode(QTableWidget.ExtendedSelection)
            self.clear_batch_selection()
    
    def clear_batch_selection(self):
        """清除批量选择"""
        for i in range(self.material_table.rowCount()):
            self.material_table.item(i, 0).setCheckState(Qt.Unchecked)
        self.update_info_label()
    
    def get_selected_materials(self):
        """获取选中的物料ID列表"""
        selected = []
        for i in range(self.material_table.rowCount()):
            if self.material_table.item(i, 0).checkState() == Qt.Checked:
                material_id = self.material_table.item(i, 1).text()
                selected.append(material_id)
        return selected
    
    # ==================== 新增功能方法 ====================
    
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
                selected_ids = self.get_selected_materials()
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
                if col == 0:  # 跳过选择框列
                    continue
                item = self.material_table.item(row, col)
                row_data.append(item.text() if item else "")
            text += "\t".join(row_data) + "\n"
        
        clipboard = QApplication.clipboard()
        clipboard.setText(text.strip())
        
        self.status_bar.setText(f"已复制 {len(rows)} 行数据")
    
    def paste_material(self):
        """从剪贴板粘贴物料数据"""
        clipboard = QApplication.clipboard()
        text = clipboard.text().strip()
        
        if not text:
            return
        
        try:
            # 解析TSV格式数据
            rows = text.split('\n')
            materials = []
            
            for row in rows:
                parts = row.split('\t')
                if len(parts) >= 3:  # 至少需要ID、名称、CAS号
                    from ..process_design_data import MaterialProperty
                    
                    material = MaterialProperty(
                        material_id=parts[0],
                        name=parts[1],
                        cas_number=parts[2] if len(parts) > 2 else "",
                        molecular_formula=parts[3] if len(parts) > 3 else "",
                        molecular_weight=float(parts[4]) if len(parts) > 4 and parts[4] else 0,
                        phase=parts[5] if len(parts) > 5 else "liquid",
                        density=float(parts[6]) if len(parts) > 6 and parts[6] else None,
                        hazard_class=parts[7] if len(parts) > 7 else ""
                    )
                    materials.append(material)
            
            if materials:
                dialog = PasteConfirmDialog(materials, self)
                if dialog.exec() == QDialog.Accepted:
                    self.batch_add_materials(materials)
            
        except Exception as e:
            QMessageBox.warning(self, "粘贴失败", f"无法解析剪贴板数据:\n{str(e)}")
    
    def batch_add_materials(self, materials):
        """批量添加物料"""
        if not self.process_manager:
            return
        
        success_count = 0
        fail_count = 0
        
        for material in materials:
            try:
                if self.process_manager.add_material(material):
                    success_count += 1
                else:
                    fail_count += 1
            except Exception:
                fail_count += 1
        
        self.load_materials()
        
        if fail_count == 0:
            QMessageBox.information(self, "批量添加完成", f"成功添加 {success_count} 个物料")
        else:
            QMessageBox.warning(self, "批量添加完成", 
                              f"添加完成:\n成功: {success_count}\n失败: {fail_count}")
    
    def batch_edit_materials(self):
        """批量编辑物料"""
        selected_ids = self.get_selected_materials()
        if not selected_ids:
            QMessageBox.warning(self, "警告", "请先选择要编辑的物料")
            return
        
        dialog = BatchEditDialog(selected_ids, self.process_manager, self)
        if dialog.exec() == QDialog.Accepted:
            self.load_materials()
    
    def batch_export_materials(self):
        """批量导出选中的物料"""
        selected_ids = self.get_selected_materials()
        if not selected_ids:
            QMessageBox.warning(self, "警告", "请先选择要导出的物料")
            return
        
        self.export_selected_materials(selected_ids)
    
    def batch_delete_materials(self):
        """批量删除物料"""
        selected_ids = self.get_selected_materials()
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
    
    # ==================== 原有方法（保持兼容） ====================
    
    def add_material(self):
        """添加物料"""
        dialog = MaterialDialog(self)
        if dialog.exec() == QDialog.Accepted:
            material = dialog.get_material()
            if material and self.process_manager:
                try:
                    if self.process_manager.add_material(material):
                        self.load_materials()
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
        
        material_id = self.material_table.item(selected_row, 1).text()
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
                if self.process_manager.update_material(updated_material):
                    self.load_materials()
                    self.material_list_updated.emit()
                    self.status_bar.setText(f"物料 '{updated_material.name}' 更新成功")
                else:
                    QMessageBox.warning(self, "错误", "物料更新失败")
    
    def delete_material(self):
        """删除物料"""
        selected_row = self.material_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要删除的物料")
            return
        
        material_id = self.material_table.item(selected_row, 1).text()
        material_name = self.material_table.item(selected_row, 2).text()
        
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除物料 '{material_name}' 吗？\n此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes and self.process_manager:
            if self.process_manager.delete_material(material_id):
                self.load_materials()
                self.material_list_updated.emit()
                self.status_bar.setText(f"物料 '{material_name}' 删除成功")
            else:
                QMessageBox.warning(self, "错误", "物料删除失败")


# ==================== 新增对话框类 ====================

class AdvancedSearchDialog(QDialog):
    """高级搜索对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("高级搜索")
        self.setMinimumWidth(400)
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # 分子量范围
        mol_weight_layout = QHBoxLayout()
        self.min_mw = QDoubleSpinBox()
        self.min_mw.setRange(0, 10000)
        self.min_mw.setSpecialValueText("最小值")
        self.max_mw = QDoubleSpinBox()
        self.max_mw.setRange(0, 10000)
        self.max_mw.setSpecialValueText("最大值")
        mol_weight_layout.addWidget(self.min_mw)
        mol_weight_layout.addWidget(QLabel(" - "))
        mol_weight_layout.addWidget(self.max_mw)
        form_layout.addRow("分子量范围:", mol_weight_layout)
        
        # 密度范围
        density_layout = QHBoxLayout()
        self.min_density = QDoubleSpinBox()
        self.min_density.setRange(0, 10000)
        self.min_density.setSpecialValueText("最小值")
        self.max_density = QDoubleSpinBox()
        self.max_density.setRange(0, 10000)
        self.max_density.setSpecialValueText("最大值")
        density_layout.addWidget(self.min_density)
        density_layout.addWidget(QLabel(" - "))
        density_layout.addWidget(self.max_density)
        form_layout.addRow("密度范围:", density_layout)
        
        # 沸点范围
        bp_layout = QHBoxLayout()
        self.min_bp = QDoubleSpinBox()
        self.min_bp.setRange(-273, 10000)
        self.min_bp.setSpecialValueText("最小值")
        self.max_bp = QDoubleSpinBox()
        self.max_bp.setRange(-273, 10000)
        self.max_bp.setSpecialValueText("最大值")
        bp_layout.addWidget(self.min_bp)
        bp_layout.addWidget(QLabel(" - "))
        bp_layout.addWidget(self.max_bp)
        form_layout.addRow("沸点范围:", bp_layout)
        
        # 危险类别多选
        self.hazard_checkboxes = []
        hazard_layout = QHBoxLayout()
        for hazard in ["易燃", "有毒", "腐蚀性", "爆炸性", "氧化剂"]:
            checkbox = QCheckBox(hazard)
            self.hazard_checkboxes.append(checkbox)
            hazard_layout.addWidget(checkbox)
        form_layout.addRow("危险类别:", hazard_layout)
        
        layout.addLayout(form_layout)
        
        # 按钮
        from PySide6.QtWidgets import QDialogButtonBox
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_search_criteria(self):
        """获取搜索条件"""
        criteria = {}
        
        # 分子量
        if not self.min_mw.text().startswith("最小"):
            criteria['min_molecular_weight'] = self.min_mw.value()
        if not self.max_mw.text().startswith("最大"):
            criteria['max_molecular_weight'] = self.max_mw.value()
        
        # 密度
        if not self.min_density.text().startswith("最小"):
            criteria['min_density'] = self.min_density.value()
        if not self.max_density.text().startswith("最大"):
            criteria['max_density'] = self.max_density.value()
        
        # 沸点
        if not self.min_bp.text().startswith("最小"):
            criteria['min_boiling_point'] = self.min_bp.value()
        if not self.max_bp.text().startswith("最大"):
            criteria['max_boiling_point'] = self.max_bp.value()
        
        # 危险类别
        selected_hazards = []
        for checkbox in self.hazard_checkboxes:
            if checkbox.isChecked():
                selected_hazards.append(checkbox.text())
        if selected_hazards:
            criteria['hazard_classes'] = selected_hazards
        
        return criteria


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
        from PySide6.QtWidgets import QDialogButtonBox
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
        from PySide6.QtWidgets import QDialogButtonBox
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


class PasteConfirmDialog(QDialog):
    """粘贴确认对话框"""
    
    def __init__(self, materials, parent=None):
        super().__init__(parent)
        self.materials = materials
        self.setWindowTitle("确认粘贴")
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel(f"发现 {len(self.materials)} 个物料:"))
        
        # 预览表格
        preview_table = QTableWidget()
        preview_table.setColumnCount(4)
        preview_table.setHorizontalHeaderLabels(["物料ID", "名称", "CAS号", "分子式"])
        preview_table.setRowCount(min(5, len(self.materials)))  # 最多显示5行
        
        for i in range(min(5, len(self.materials))):
            material = self.materials[i]
            preview_table.setItem(i, 0, QTableWidgetItem(material.material_id))
            preview_table.setItem(i, 1, QTableWidgetItem(material.name))
            preview_table.setItem(i, 2, QTableWidgetItem(material.cas_number))
            preview_table.setItem(i, 3, QTableWidgetItem(material.molecular_formula))
        
        preview_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(preview_table)
        
        if len(self.materials) > 5:
            layout.addWidget(QLabel(f"... 还有 {len(self.materials)-5} 个物料"))
        
        layout.addWidget(QLabel("确认要添加这些物料吗？"))
        
        # 按钮
        from PySide6.QtWidgets import QDialogButtonBox
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)


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
        from PySide6.QtWidgets import QDialogButtonBox
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
            from ..process_design_data import MaterialProperty
            
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


# ==================== 原有MaterialDialog类（保持兼容） ====================

class MaterialDialog(QDialog):
    """物料对话框 - 增强版"""
    
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
        from PySide6.QtWidgets import QDialogButtonBox
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
        from ..process_design_data import MaterialProperty
        
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