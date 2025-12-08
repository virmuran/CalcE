# modules/process_design/tabs/msds_manager_tab.py
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
    QMenu, QApplication, QFrame, QToolBar, QSizePolicy, QDateEdit,
    QScrollArea, QGridLayout, QListWidget, QListWidgetItem, QDialogButtonBox,
    QProgressBar
)
from PySide6.QtCore import Qt, Signal, QTimer, QThread, QSize, QDate, QUrl, QObject
from PySide6.QtGui import QAction, QKeySequence, QClipboard, QDesktopServices, QPixmap

# 导入其他库
import csv
import json
import pandas as pd
import re
from typing import List, Optional, Dict, Any
from datetime import datetime
import webbrowser
from pathlib import Path

# 尝试导入工艺设计相关模块
try:
    from ..process_design_manager import ProcessDesignManager
    from ..process_design_data import MSDSDocument, MaterialProperty
    print("✅ 成功导入 ProcessDesignManager 和 MSDSDocument")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    
    # 创建占位符类
    class ProcessDesignManager:
        def __init__(self, *args, **kwargs):
            pass
        def get_all_msds(self):
            return []
        def get_msds(self, msds_id):
            return None
        def add_msds(self, msds):
            return False
        def update_msds(self, msds):
            return False
        def delete_msds(self, msds_id):
            return False
        def search_msds(self, search_term):
            return []
        def advanced_search_msds(self, criteria):
            return []
        def get_all_materials(self):
            return []
        def get_material_by_cas(self, cas_number):
            return None
    
    class MSDSDocument:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)
    
    class MaterialProperty:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

class MSDSManagerTab(QWidget):
    """MSDS管理标签页"""
    
    msds_selected = Signal(str)  # MSDS选择信号
    msds_list_updated = Signal()  # MSDS列表更新信号
    
    def __init__(self, data_manager=None, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.process_manager = None
        self.current_msds_docs = []  # 当前显示的MSDS文档列表
        self.selected_rows = set()  # 选中的行
        self.batch_mode = False  # 批量操作模式
        self.msds_file_paths = {}  # 存储MSDS文件路径
        
        # 延迟初始化process_manager
        if data_manager:
            try:
                self.process_manager = ProcessDesignManager(data_manager)
                print("✅ MSDS管理: ProcessDesignManager 初始化成功")
            except Exception as e:
                print(f"❌ MSDS管理: ProcessDesignManager 初始化失败: {e}")
                self.process_manager = None
        
        self.setup_ui()
        self.load_msds_documents()
        self.setup_shortcuts()
    
    def setup_ui(self):
        """设置UI"""
        main_layout = QVBoxLayout(self)
        
        # 工具栏
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(16, 16))
        
        # 工具栏动作
        self.add_action = QAction("添加MSDS", self)
        self.add_action.triggered.connect(self.add_msds)
        toolbar.addAction(self.add_action)
        
        self.edit_action = QAction("编辑", self)
        self.edit_action.triggered.connect(self.edit_msds)
        toolbar.addAction(self.edit_action)
        
        self.delete_action = QAction("删除", self)
        self.delete_action.triggered.connect(self.delete_msds)
        toolbar.addAction(self.delete_action)
        
        toolbar.addSeparator()
        
        self.view_action = QAction("查看文件", self)
        self.view_action.triggered.connect(self.view_msds_file)
        toolbar.addAction(self.view_action)
        
        self.download_action = QAction("下载文件", self)
        self.download_action.triggered.connect(self.download_msds_file)
        toolbar.addAction(self.download_action)
        
        toolbar.addSeparator()
        
        self.import_action = QAction("导入", self)
        self.import_action.triggered.connect(self.import_msds)
        toolbar.addAction(self.import_action)
        
        self.export_action = QAction("导出", self)
        self.export_action.triggered.connect(self.export_msds)
        toolbar.addAction(self.export_action)
        
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
        self.search_input.setPlaceholderText("物料名称、CAS号或供应商...")
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
        
        # 危险类别过滤器
        self.hazard_filter = QComboBox()
        self.hazard_filter.addItem("所有类别")
        self.hazard_filter.addItems(["易燃", "有毒", "腐蚀性", "爆炸性", "氧化剂", "环境危害", "无"])
        self.hazard_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(QLabel("危险类别:"))
        filter_layout.addWidget(self.hazard_filter)
        
        # 状态过滤器
        self.status_filter = QComboBox()
        self.status_filter.addItem("所有状态")
        self.status_filter.addItems(["有效", "过期", "待审核"])
        self.status_filter.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(QLabel("状态:"))
        filter_layout.addWidget(self.status_filter)
        
        main_layout.addWidget(filter_frame)
        
        # 分割器：左侧表格，右侧详情
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：MSDS表格
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        
        # 表格上方信息栏
        info_layout = QHBoxLayout()
        self.info_label = QLabel("总计: 0 个MSDS")
        info_layout.addWidget(self.info_label)
        info_layout.addStretch()
        
        self.selected_label = QLabel("已选择: 0 个")
        info_layout.addWidget(self.selected_label)
        table_layout.addLayout(info_layout)
        
        # MSDS表格
        self.msds_table = QTableWidget()
        self.msds_table.setColumnCount(12)
        self.msds_table.setHorizontalHeaderLabels([
            "",  # 选择框
            "MSDS ID", "物料名称", "CAS号", "供应商", "版本", 
            "生效日期", "有效期", "危险类别", "状态", 
            "文件大小", "上次更新"
        ])
        
        # 设置表头
        header = self.msds_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # 选择列固定宽度
        header.resizeSection(0, 30)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # ID列自适应
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # 名称列拉伸
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # CAS号
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 供应商
        
        # 启用排序
        self.msds_table.setSortingEnabled(True)
        
        # 设置选择模式
        self.msds_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.msds_table.setSelectionMode(QTableWidget.ExtendedSelection)
        
        # 连接信号
        self.msds_table.itemDoubleClicked.connect(self.on_msds_double_clicked)
        self.msds_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        table_layout.addWidget(self.msds_table)
        
        splitter.addWidget(table_widget)
        
        # 右侧：MSDS详情
        detail_widget = QWidget()
        detail_layout = QVBoxLayout(detail_widget)
        
        # 详情标签页
        detail_tab = QTabWidget()
        
        # 基本信息标签页
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        
        # 基本信息显示区域
        self.basic_info_text = QTextEdit()
        self.basic_info_text.setReadOnly(True)
        self.basic_info_text.setMaximumHeight(200)
        basic_layout.addWidget(self.basic_info_text)
        
        detail_tab.addTab(basic_tab, "基本信息")
        
        # 危险信息标签页
        hazard_tab = QWidget()
        hazard_layout = QVBoxLayout(hazard_tab)
        
        self.hazard_info_text = QTextEdit()
        self.hazard_info_text.setReadOnly(True)
        hazard_layout.addWidget(self.hazard_info_text)
        
        detail_tab.addTab(hazard_tab, "危险信息")
        
        # 应急处理标签页
        emergency_tab = QWidget()
        emergency_layout = QVBoxLayout(emergency_tab)
        
        self.emergency_info_text = QTextEdit()
        self.emergency_info_text.setReadOnly(True)
        emergency_layout.addWidget(self.emergency_info_text)
        
        detail_tab.addTab(emergency_tab, "应急处理")
        
        # 存储运输标签页
        storage_tab = QWidget()
        storage_layout = QVBoxLayout(storage_tab)
        
        self.storage_info_text = QTextEdit()
        self.storage_info_text.setReadOnly(True)
        storage_layout.addWidget(self.storage_info_text)
        
        detail_tab.addTab(storage_tab, "存储运输")
        
        detail_layout.addWidget(detail_tab)
        
        # 文件信息区域
        file_frame = QGroupBox("文件信息")
        file_layout = QVBoxLayout(file_frame)
        
        self.file_info_text = QTextEdit()
        self.file_info_text.setReadOnly(True)
        self.file_info_text.setMaximumHeight(100)
        file_layout.addWidget(self.file_info_text)
        
        # 文件操作按钮
        file_btn_layout = QHBoxLayout()
        self.open_file_btn = QPushButton("打开文件")
        self.open_file_btn.clicked.connect(self.view_msds_file)
        self.open_file_btn.setEnabled(False)
        
        self.save_file_btn = QPushButton("另存为...")
        self.save_file_btn.clicked.connect(self.save_msds_file_as)
        self.save_file_btn.setEnabled(False)
        
        file_btn_layout.addWidget(self.open_file_btn)
        file_btn_layout.addWidget(self.save_file_btn)
        file_layout.addLayout(file_btn_layout)
        
        detail_layout.addWidget(file_frame)
        
        splitter.addWidget(detail_widget)
        splitter.setSizes([700, 300])  # 设置初始大小比例
        
        main_layout.addWidget(splitter)
        
        # 批量操作按钮（初始隐藏）
        self.batch_panel = QFrame()
        self.batch_panel.setFrameStyle(QFrame.StyledPanel)
        self.batch_panel.setVisible(False)
        batch_layout = QHBoxLayout(self.batch_panel)
        
        self.batch_edit_btn = QPushButton("批量编辑")
        self.batch_edit_btn.clicked.connect(self.batch_edit_msds)
        batch_layout.addWidget(self.batch_edit_btn)
        
        self.batch_export_btn = QPushButton("批量导出")
        self.batch_export_btn.clicked.connect(self.batch_export_msds)
        batch_layout.addWidget(self.batch_export_btn)
        
        self.batch_download_btn = QPushButton("批量下载")
        self.batch_download_btn.clicked.connect(self.batch_download_msds)
        batch_layout.addWidget(self.batch_download_btn)
        
        self.batch_delete_btn = QPushButton("批量删除")
        self.batch_delete_btn.clicked.connect(self.batch_delete_msds)
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
        self.refresh_action.triggered.connect(self.load_msds_documents)
        self.addAction(self.refresh_action)
    
    def load_msds_documents(self):
        """加载MSDS文档数据"""
        if not self.process_manager:
            self.status_bar.setText("错误: 数据管理器未初始化")
            return
        
        try:
            self.current_msds_docs = self.process_manager.get_all_msds()
            self.populate_table(self.current_msds_docs)
            self.update_info_label()
            self.status_bar.setText(f"数据加载完成: {len(self.current_msds_docs)} 条记录")
        except Exception as e:
            self.status_bar.setText(f"加载失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"加载MSDS数据时发生错误:\n{str(e)}")
    
    def populate_table(self, msds_docs):
        """填充表格数据"""
        self.msds_table.setRowCount(len(msds_docs))
        
        for i, msds in enumerate(msds_docs):
            # 选择框
            checkbox_item = QTableWidgetItem()
            checkbox_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            checkbox_item.setCheckState(Qt.Unchecked)
            self.msds_table.setItem(i, 0, checkbox_item)
            
            # MSDS数据
            self.msds_table.setItem(i, 1, QTableWidgetItem(msds.msds_id))
            self.msds_table.setItem(i, 2, QTableWidgetItem(msds.material_name))
            self.msds_table.setItem(i, 3, QTableWidgetItem(msds.cas_number))
            self.msds_table.setItem(i, 4, QTableWidgetItem(msds.supplier))
            self.msds_table.setItem(i, 5, QTableWidgetItem(msds.version))
            
            # 日期格式化
            effective_date = msds.effective_date.strftime("%Y-%m-%d") if hasattr(msds.effective_date, 'strftime') else str(msds.effective_date)
            expiry_date = msds.expiry_date.strftime("%Y-%m-%d") if hasattr(msds.expiry_date, 'strftime') else str(msds.expiry_date) if msds.expiry_date else ""
            
            self.msds_table.setItem(i, 6, QTableWidgetItem(effective_date))
            self.msds_table.setItem(i, 7, QTableWidgetItem(expiry_date))
            self.msds_table.setItem(i, 8, QTableWidgetItem(msds.hazard_class))
            self.msds_table.setItem(i, 9, QTableWidgetItem(msds.status))
            
            # 文件大小
            file_size = self.format_file_size(msds.file_size) if hasattr(msds, 'file_size') and msds.file_size else ""
            self.msds_table.setItem(i, 10, QTableWidgetItem(file_size))
            
            # 上次更新
            last_updated = msds.last_updated.strftime("%Y-%m-%d %H:%M") if hasattr(msds.last_updated, 'strftime') else str(msds.last_updated)
            self.msds_table.setItem(i, 11, QTableWidgetItem(last_updated))
            
            # 存储文件路径
            if hasattr(msds, 'file_path') and msds.file_path:
                self.msds_file_paths[msds.msds_id] = msds.file_path
        
        self.update_info_label()
    
    def format_file_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def update_info_label(self):
        """更新信息标签"""
        total = self.msds_table.rowCount()
        selected = len([i for i in range(total) 
                       if self.msds_table.item(i, 0).checkState() == Qt.Checked])
        self.info_label.setText(f"总计: {total} 个MSDS")
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
                msds_docs = self.process_manager.get_all_msds()
            else:
                msds_docs = self.process_manager.search_msds(search_term)
            
            self.current_msds_docs = msds_docs
            self.apply_filters()  # 应用当前过滤器
            self.status_bar.setText(f"搜索到 {len(msds_docs)} 条记录")
        except Exception as e:
            self.status_bar.setText(f"搜索失败: {str(e)}")
    
    def apply_filters(self):
        """应用过滤器"""
        hazard_filter = self.hazard_filter.currentText()
        status_filter = self.status_filter.currentText()
        
        filtered_msds = self.current_msds_docs.copy()
        
        # 应用危险类别过滤
        if hazard_filter != "所有类别":
            filtered_msds = [m for m in filtered_msds if hazard_filter in m.hazard_class]
        
        # 应用状态过滤
        if status_filter != "所有状态":
            filtered_msds = [m for m in filtered_msds if m.status == status_filter]
        
        self.populate_table(filtered_msds)
    
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
            msds_docs = self.process_manager.advanced_search_msds(criteria)
            self.current_msds_docs = msds_docs
            self.populate_table(msds_docs)
            self.status_bar.setText(f"高级搜索找到 {len(msds_docs)} 条记录")
        except Exception as e:
            self.status_bar.setText(f"高级搜索失败: {str(e)}")
            QMessageBox.warning(self, "搜索失败", str(e))
    
    def on_msds_double_clicked(self, item):
        """MSDS双击事件"""
        if item.column() == 0:  # 点击选择框时不触发
            return
        
        row = item.row()
        msds_id = self.msds_table.item(row, 1).text()
        self.show_msds_details(msds_id)
        self.msds_selected.emit(msds_id)
    
    def show_msds_details(self, msds_id):
        """显示MSDS详情"""
        if not self.process_manager:
            return
        
        msds = self.process_manager.get_msds(msds_id)
        if not msds:
            return
        
        # 显示基本信息
        basic_info = f"<h3>{msds.material_name} (MSDS: {msds.msds_id})</h3>"
        basic_info += f"<b>CAS号:</b> {msds.cas_number}<br>"
        basic_info += f"<b>供应商:</b> {msds.supplier}<br>"
        basic_info += f"<b>版本:</b> {msds.version}<br>"
        basic_info += f"<b>生效日期:</b> {msds.effective_date.strftime('%Y-%m-%d') if hasattr(msds.effective_date, 'strftime') else msds.effective_date}<br>"
        
        if msds.expiry_date:
            basic_info += f"<b>有效期:</b> {msds.expiry_date.strftime('%Y-%m-%d') if hasattr(msds.expiry_date, 'strftime') else msds.expiry_date}<br>"
        
        basic_info += f"<b>危险类别:</b> {msds.hazard_class}<br>"
        basic_info += f"<b>状态:</b> {msds.status}<br>"
        
        if msds.description:
            basic_info += f"<br><b>描述:</b><br>{msds.description}"
        
        self.basic_info_text.setHtml(basic_info)
        
        # 显示危险信息
        hazard_info = ""
        if hasattr(msds, 'hazard_statements') and msds.hazard_statements:
            hazard_info += f"<b>危险性说明:</b><br>{msds.hazard_statements}<br><br>"
        
        if hasattr(msds, 'precautionary_statements') and msds.precautionary_statements:
            hazard_info += f"<b>防范说明:</b><br>{msds.precautionary_statements}<br><br>"
        
        if hasattr(msds, 'symptoms') and msds.symptoms:
            hazard_info += f"<b>症状/危害:</b><br>{msds.symptoms}<br><br>"
        
        self.hazard_info_text.setHtml(hazard_info)
        
        # 显示应急处理信息
        emergency_info = ""
        if hasattr(msds, 'first_aid_measures') and msds.first_aid_measures:
            emergency_info += f"<b>急救措施:</b><br>{msds.first_aid_measures}<br><br>"
        
        if hasattr(msds, 'fire_fighting_measures') and msds.fire_fighting_measures:
            emergency_info += f"<b>消防措施:</b><br>{msds.fire_fighting_measures}<br><br>"
        
        if hasattr(msds, 'accidental_release_measures') and msds.accidental_release_measures:
            emergency_info += f"<b>泄漏应急处理:</b><br>{msds.accidental_release_measures}<br><br>"
        
        self.emergency_info_text.setHtml(emergency_info)
        
        # 显示存储运输信息
        storage_info = ""
        if hasattr(msds, 'handling_and_storage') and msds.handling_and_storage:
            storage_info += f"<b>操作处置与储存:</b><br>{msds.handling_and_storage}<br><br>"
        
        if hasattr(msds, 'exposure_controls') and msds.exposure_controls:
            storage_info += f"<b>接触控制/个体防护:</b><br>{msds.exposure_controls}<br><br>"
        
        if hasattr(msds, 'transport_information') and msds.transport_information:
            storage_info += f"<b>运输信息:</b><br>{msds.transport_information}<br><br>"
        
        self.storage_info_text.setHtml(storage_info)
        
        # 显示文件信息
        file_info = ""
        if hasattr(msds, 'file_name') and msds.file_name:
            file_info += f"<b>文件名:</b> {msds.file_name}<br>"
        
        if hasattr(msds, 'file_size') and msds.file_size:
            file_info += f"<b>文件大小:</b> {self.format_file_size(msds.file_size)}<br>"
        
        if hasattr(msds, 'file_type') and msds.file_type:
            file_info += f"<b>文件类型:</b> {msds.file_type}<br>"
        
        if hasattr(msds, 'file_path') and msds.file_path:
            file_info += f"<b>文件路径:</b> {msds.file_path}<br>"
            self.open_file_btn.setEnabled(True)
            self.save_file_btn.setEnabled(True)
        else:
            self.open_file_btn.setEnabled(False)
            self.save_file_btn.setEnabled(False)
        
        self.file_info_text.setHtml(file_info)
    
    def on_selection_changed(self):
        """选择变化事件"""
        selected_rows = self.msds_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            msds_id = self.msds_table.item(row, 1).text()
            self.show_msds_details(msds_id)
    
    def toggle_batch_mode(self, enabled):
        """切换批量操作模式"""
        self.batch_mode = enabled
        self.batch_panel.setVisible(enabled)
        
        if enabled:
            self.msds_table.setSelectionMode(QTableWidget.NoSelection)
            for i in range(self.msds_table.rowCount()):
                item = self.msds_table.item(i, 0)
                item.setFlags(item.flags() | Qt.ItemIsEnabled)
        else:
            self.msds_table.setSelectionMode(QTableWidget.ExtendedSelection)
            self.clear_batch_selection()
    
    def clear_batch_selection(self):
        """清除批量选择"""
        for i in range(self.msds_table.rowCount()):
            self.msds_table.item(i, 0).setCheckState(Qt.Unchecked)
        self.update_info_label()
    
    def get_selected_msds(self):
        """获取选中的MSDS ID列表"""
        selected = []
        for i in range(self.msds_table.rowCount()):
            if self.msds_table.item(i, 0).checkState() == Qt.Checked:
                msds_id = self.msds_table.item(i, 1).text()
                selected.append(msds_id)
        return selected
    
    def view_msds_file(self):
        """查看MSDS文件"""
        selected_row = self.msds_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要查看的MSDS")
            return
        
        msds_id = self.msds_table.item(selected_row, 1).text()
        if msds_id in self.msds_file_paths:
            file_path = self.msds_file_paths[msds_id]
            try:
                if os.path.exists(file_path):
                    QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
                else:
                    QMessageBox.warning(self, "文件不存在", f"文件不存在或已被移动:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "打开失败", f"无法打开文件:\n{str(e)}")
        else:
            QMessageBox.warning(self, "无文件", "该MSDS没有关联的文件")
    
    def download_msds_file(self):
        """下载MSDS文件"""
        selected_row = self.msds_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要下载的MSDS")
            return
        
        msds_id = self.msds_table.item(selected_row, 1).text()
        msds_name = self.msds_table.item(selected_row, 2).text()
        
        if msds_id in self.msds_file_paths:
            file_path = self.msds_file_paths[msds_id]
            if os.path.exists(file_path):
                save_path, _ = QFileDialog.getSaveFileName(
                    self, "保存MSDS文件", 
                    f"{msds_name}_MSDS{Path(file_path).suffix}",
                    f"所有文件 (*{Path(file_path).suffix});;所有文件 (*.*)"
                )
                
                if save_path:
                    try:
                        import shutil
                        shutil.copy2(file_path, save_path)
                        QMessageBox.information(self, "下载成功", f"文件已保存到:\n{save_path}")
                    except Exception as e:
                        QMessageBox.critical(self, "下载失败", f"保存文件时发生错误:\n{str(e)}")
            else:
                QMessageBox.warning(self, "文件不存在", f"文件不存在或已被移动:\n{file_path}")
        else:
            QMessageBox.warning(self, "无文件", "该MSDS没有关联的文件")
    
    def save_msds_file_as(self):
        """另存为MSDS文件"""
        selected_row = self.msds_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要另存为的MSDS")
            return
        
        msds_id = self.msds_table.item(selected_row, 1).text()
        msds_name = self.msds_table.item(selected_row, 2).text()
        
        if msds_id in self.msds_file_paths:
            file_path = self.msds_file_paths[msds_id]
            if os.path.exists(file_path):
                save_path, _ = QFileDialog.getSaveFileName(
                    self, "另存为MSDS文件", 
                    f"{msds_name}_MSDS{Path(file_path).suffix}",
                    f"所有文件 (*{Path(file_path).suffix});;所有文件 (*.*)"
                )
                
                if save_path:
                    try:
                        import shutil
                        shutil.copy2(file_path, save_path)
                        QMessageBox.information(self, "保存成功", f"文件已保存到:\n{save_path}")
                    except Exception as e:
                        QMessageBox.critical(self, "保存失败", f"保存文件时发生错误:\n{str(e)}")
            else:
                QMessageBox.warning(self, "文件不存在", f"文件不存在或已被移动:\n{file_path}")
        else:
            QMessageBox.warning(self, "无文件", "该MSDS没有关联的文件")
    
    def import_msds(self):
        """导入MSDS数据"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择导入文件", "", 
            "Excel文件 (*.xlsx *.xls);;CSV文件 (*.csv);;JSON文件 (*.json)"
        )
        
        if not file_path:
            return
        
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
            
            # 显示预览
            dialog = ImportPreviewDialog(df, self)
            if dialog.exec() == QDialog.Accepted:
                # 导入数据
                success_count = 0
                fail_count = 0
                
                for _, row in df.iterrows():
                    try:
                        msds = MSDSDocument(
                            msds_id=str(row.get('msds_id', '')).strip(),
                            material_name=str(row.get('material_name', '')).strip(),
                            cas_number=str(row.get('cas_number', '')).strip(),
                            supplier=str(row.get('supplier', '')).strip(),
                            version=str(row.get('version', '')).strip(),
                            effective_date=datetime.strptime(row['effective_date'], '%Y-%m-%d') if pd.notna(row.get('effective_date')) else datetime.now(),
                            expiry_date=datetime.strptime(row['expiry_date'], '%Y-%m-%d') if pd.notna(row.get('expiry_date')) else None,
                            hazard_class=str(row.get('hazard_class', '')).strip(),
                            status=str(row.get('status', '有效')).strip(),
                            description=str(row.get('description', '')).strip()
                        )
                        
                        if self.process_manager.add_msds(msds):
                            success_count += 1
                        else:
                            fail_count += 1
                    except Exception:
                        fail_count += 1
                
                self.load_msds_documents()
                
                if fail_count == 0:
                    QMessageBox.information(self, "导入完成", f"成功导入 {success_count} 个MSDS")
                else:
                    QMessageBox.warning(self, "导入完成", 
                                      f"导入完成:\n成功: {success_count}\n失败: {fail_count}")
        
        except Exception as e:
            QMessageBox.critical(self, "导入失败", f"导入文件时发生错误:\n{str(e)}")
    
    def validate_import_data(self, df):
        """验证导入数据"""
        required_columns = ['msds_id', 'material_name', 'cas_number']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            QMessageBox.warning(self, "数据验证失败", 
                               f"缺少必要列: {', '.join(missing_columns)}")
            return False
        
        # 检查重复ID
        duplicates = df[df.duplicated('msds_id', keep=False)]
        if not duplicates.empty:
            reply = QMessageBox.question(
                self, "发现重复ID",
                f"发现 {len(duplicates)} 条重复的MSDS ID。是否继续导入？",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return False
        
        return True
    
    def export_msds(self):
        """导出MSDS数据"""
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "选择导出文件", "msds_export.xlsx",
            "Excel文件 (*.xlsx);;CSV文件 (*.csv);;JSON文件 (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            # 获取所有MSDS数据
            msds_docs = self.process_manager.get_all_msds()
            
            # 转换为DataFrame
            rows = []
            for msds in msds_docs:
                row = {
                    'msds_id': msds.msds_id,
                    'material_name': msds.material_name,
                    'cas_number': msds.cas_number,
                    'supplier': msds.supplier,
                    'version': msds.version,
                    'effective_date': msds.effective_date.strftime('%Y-%m-%d') if hasattr(msds.effective_date, 'strftime') else msds.effective_date,
                    'expiry_date': msds.expiry_date.strftime('%Y-%m-%d') if msds.expiry_date and hasattr(msds.expiry_date, 'strftime') else "",
                    'hazard_class': msds.hazard_class,
                    'status': msds.status,
                    'description': msds.description,
                    'hazard_statements': msds.hazard_statements if hasattr(msds, 'hazard_statements') else "",
                    'precautionary_statements': msds.precautionary_statements if hasattr(msds, 'precautionary_statements') else "",
                    'first_aid_measures': msds.first_aid_measures if hasattr(msds, 'first_aid_measures') else "",
                    'fire_fighting_measures': msds.fire_fighting_measures if hasattr(msds, 'fire_fighting_measures') else ""
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
            
            self.status_bar.setText(f"导出完成: {len(msds_docs)} 条记录")
            QMessageBox.information(self, "导出成功", f"成功导出 {len(msds_docs)} 条记录到:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出文件时发生错误:\n{str(e)}")
    
    def copy_selected(self):
        """复制选中内容到剪贴板"""
        selected_items = self.msds_table.selectedItems()
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
                item = self.msds_table.item(row, col)
                row_data.append(item.text() if item else "")
            text += "\t".join(row_data) + "\n"
        
        clipboard = QApplication.clipboard()
        clipboard.setText(text.strip())
        
        self.status_bar.setText(f"已复制 {len(rows)} 行数据")
    
    def batch_edit_msds(self):
        """批量编辑MSDS"""
        selected_ids = self.get_selected_msds()
        if not selected_ids:
            QMessageBox.warning(self, "警告", "请先选择要编辑的MSDS")
            return
        
        dialog = BatchEditDialog(selected_ids, self.process_manager, self)
        if dialog.exec() == QDialog.Accepted:
            self.load_msds_documents()
    
    def batch_export_msds(self):
        """批量导出MSDS"""
        selected_ids = self.get_selected_msds()
        if not selected_ids:
            QMessageBox.warning(self, "警告", "请先选择要导出的MSDS")
            return
        
        self.export_selected_msds(selected_ids)
    
    def batch_download_msds(self):
        """批量下载MSDS文件"""
        selected_ids = self.get_selected_msds()
        if not selected_ids:
            QMessageBox.warning(self, "警告", "请先选择要下载的MSDS")
            return
        
        # 选择保存目录
        save_dir = QFileDialog.getExistingDirectory(self, "选择保存目录")
        if not save_dir:
            return
        
        success_count = 0
        fail_count = 0
        
        for msds_id in selected_ids:
            if msds_id in self.msds_file_paths:
                file_path = self.msds_file_paths[msds_id]
                if os.path.exists(file_path):
                    try:
                        import shutil
                        file_name = os.path.basename(file_path)
                        save_path = os.path.join(save_dir, file_name)
                        shutil.copy2(file_path, save_path)
                        success_count += 1
                    except Exception:
                        fail_count += 1
                else:
                    fail_count += 1
            else:
                fail_count += 1
        
        if fail_count == 0:
            QMessageBox.information(self, "下载完成", f"成功下载 {success_count} 个文件到:\n{save_dir}")
        else:
            QMessageBox.warning(self, "下载完成", 
                              f"下载完成:\n成功: {success_count}\n失败: {fail_count}")
    
    def batch_delete_msds(self):
        """批量删除MSDS"""
        selected_ids = self.get_selected_msds()
        if not selected_ids:
            QMessageBox.warning(self, "警告", "请先选择要删除的MSDS")
            return
        
        reply = QMessageBox.question(
            self, "确认批量删除",
            f"确定要删除选中的 {len(selected_ids)} 个MSDS吗？\n此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success_count = 0
            for msds_id in selected_ids:
                if self.process_manager.delete_msds(msds_id):
                    success_count += 1
            
            self.load_msds_documents()
            self.msds_list_updated.emit()
            
            QMessageBox.information(
                self, "删除完成",
                f"已删除 {success_count} 个MSDS"
            )
    
    def export_selected_msds(self, msds_ids):
        """导出选中的MSDS"""
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "导出选中MSDS", "selected_msds.xlsx",
            "Excel文件 (*.xlsx);;CSV文件 (*.csv);;JSON文件 (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            msds_docs = []
            for msds_id in msds_ids:
                msds = self.process_manager.get_msds(msds_id)
                if msds:
                    msds_docs.append(msds)
            
            # 转换为DataFrame
            rows = []
            for msds in msds_docs:
                row = {
                    'msds_id': msds.msds_id,
                    'material_name': msds.material_name,
                    'cas_number': msds.cas_number,
                    'supplier': msds.supplier,
                    'version': msds.version,
                    'effective_date': msds.effective_date.strftime('%Y-%m-%d') if hasattr(msds.effective_date, 'strftime') else msds.effective_date,
                    'expiry_date': msds.expiry_date.strftime('%Y-%m-%d') if msds.expiry_date and hasattr(msds.expiry_date, 'strftime') else "",
                    'hazard_class': msds.hazard_class,
                    'status': msds.status,
                    'description': msds.description
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
            
            QMessageBox.information(self, "导出成功", f"成功导出 {len(msds_docs)} 个MSDS")
            
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出文件时发生错误:\n{str(e)}")
    
    def add_msds(self):
        """添加MSDS"""
        dialog = MSDSDialog(self)
        if dialog.exec() == QDialog.Accepted:
            msds = dialog.get_msds()
            if msds and self.process_manager:
                try:
                    # 检查文件是否存在
                    if hasattr(msds, 'file_path') and msds.file_path:
                        if not os.path.exists(msds.file_path):
                            reply = QMessageBox.question(
                                self, "文件不存在",
                                f"指定的文件不存在:\n{msds.file_path}\n是否继续添加？",
                                QMessageBox.Yes | QMessageBox.No
                            )
                            if reply == QMessageBox.No:
                                return
                    
                    if self.process_manager.add_msds(msds):
                        self.load_msds_documents()
                        self.msds_list_updated.emit()
                        self.status_bar.setText(f"MSDS '{msds.material_name}' 添加成功")
                    else:
                        QMessageBox.warning(self, "错误", "MSDS添加失败，可能MSDS ID已存在。")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"添加MSDS时发生错误:\n{str(e)}")
    
    def edit_msds(self):
        """编辑MSDS"""
        selected_row = self.msds_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要编辑的MSDS")
            return
        
        msds_id = self.msds_table.item(selected_row, 1).text()
        if not self.process_manager:
            return
        
        msds = self.process_manager.get_msds(msds_id)
        if not msds:
            QMessageBox.warning(self, "错误", "MSDS未找到")
            return
        
        dialog = MSDSDialog(self, msds)
        if dialog.exec() == QDialog.Accepted:
            updated_msds = dialog.get_msds()
            if updated_msds and self.process_manager:
                if self.process_manager.update_msds(updated_msds):
                    self.load_msds_documents()
                    self.msds_list_updated.emit()
                    self.status_bar.setText(f"MSDS '{updated_msds.material_name}' 更新成功")
                else:
                    QMessageBox.warning(self, "错误", "MSDS更新失败")
    
    def delete_msds(self):
        """删除MSDS"""
        selected_row = self.msds_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要删除的MSDS")
            return
        
        msds_id = self.msds_table.item(selected_row, 1).text()
        msds_name = self.msds_table.item(selected_row, 2).text()
        
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除MSDS '{msds_name}' 吗？\n此操作不可恢复！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes and self.process_manager:
            if self.process_manager.delete_msds(msds_id):
                self.load_msds_documents()
                self.msds_list_updated.emit()
                self.status_bar.setText(f"MSDS '{msds_name}' 删除成功")
            else:
                QMessageBox.warning(self, "错误", "MSDS删除失败")


# ==================== 对话框类 ====================

class AdvancedSearchDialog(QDialog):
    """高级搜索对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("高级搜索MSDS")
        self.setMinimumWidth(400)
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # 供应商搜索
        self.supplier_input = QLineEdit()
        self.supplier_input.setPlaceholderText("供应商名称")
        form_layout.addRow("供应商:", self.supplier_input)
        
        # 版本搜索
        self.version_input = QLineEdit()
        self.version_input.setPlaceholderText("版本号")
        form_layout.addRow("版本:", self.version_input)
        
        # 生效日期范围
        date_layout = QHBoxLayout()
        self.start_date = QLineEdit()
        self.start_date.setPlaceholderText("YYYY-MM-DD")
        self.end_date = QLineEdit()
        self.end_date.setPlaceholderText("YYYY-MM-DD")
        date_layout.addWidget(self.start_date)
        date_layout.addWidget(QLabel("至"))
        date_layout.addWidget(self.end_date)
        form_layout.addRow("生效日期范围:", date_layout)
        
        layout.addLayout(form_layout)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_search_criteria(self):
        """获取搜索条件"""
        criteria = {}
        
        supplier = self.supplier_input.text().strip()
        if supplier:
            criteria['supplier'] = supplier
        
        version = self.version_input.text().strip()
        if version:
            criteria['version'] = version
        
        start_date = self.start_date.text().strip()
        if start_date:
            criteria['start_date'] = start_date
        
        end_date = self.end_date.text().strip()
        if end_date:
            criteria['end_date'] = end_date
        
        return criteria

class BatchEditDialog(QDialog):
    """批量编辑对话框"""
    
    def __init__(self, msds_ids, process_manager, parent=None):
        super().__init__(parent)
        self.msds_ids = msds_ids
        self.process_manager = process_manager
        self.setWindowTitle("批量编辑MSDS")
        self.setMinimumWidth(400)
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel(f"批量编辑 {len(self.msds_ids)} 个MSDS"))
        
        form_layout = QFormLayout()
        
        # 可批量编辑的字段
        self.status_combo = QComboBox()
        self.status_combo.addItems(["", "有效", "过期", "待审核"])
        self.status_combo.setCurrentIndex(0)
        form_layout.addRow("状态:", self.status_combo)
        
        self.supplier_input = QLineEdit()
        self.supplier_input.setPlaceholderText("留空则不修改")
        form_layout.addRow("供应商:", self.supplier_input)
        
        self.version_input = QLineEdit()
        self.version_input.setPlaceholderText("留空则不修改")
        form_layout.addRow("版本:", self.version_input)
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        self.notes_input.setPlaceholderText("备注信息...")
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
        
        supplier = self.supplier_input.text().strip()
        if supplier:
            changes['supplier'] = supplier
        
        version = self.version_input.text().strip()
        if version:
            changes['version'] = version
        
        notes = self.notes_input.toPlainText().strip()
        if notes:
            changes['notes'] = notes
        
        if not changes:
            QMessageBox.warning(self, "警告", "没有修改任何字段")
            return
        
        success_count = 0
        for msds_id in self.msds_ids:
            msds = self.process_manager.get_msds(msds_id)
            if msds:
                # 应用修改
                if 'status' in changes:
                    msds.status = changes['status']
                if 'supplier' in changes:
                    msds.supplier = changes['supplier']
                if 'version' in changes:
                    msds.version = changes['version']
                if 'notes' in changes:
                    if hasattr(msds, 'notes'):
                        msds.notes = changes['notes']
                    elif hasattr(msds, 'description'):
                        msds.description = changes['notes']
                
                if self.process_manager.update_msds(msds):
                    success_count += 1
        
        QMessageBox.information(self, "批量编辑完成", f"成功更新 {success_count} 个MSDS")
        self.accept()

class ImportPreviewDialog(QDialog):
    """导入预览对话框"""
    
    def __init__(self, df, parent=None):
        super().__init__(parent)
        self.df = df
        self.setWindowTitle("导入预览")
        self.setMinimumSize(600, 400)
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel(f"共 {len(self.df)} 条记录，前5行预览:"))
        
        # 预览表格
        preview_table = QTableWidget()
        preview_table.setColumnCount(min(10, len(self.df.columns)))
        preview_table.setRowCount(min(5, len(self.df)))
        
        # 设置表头
        columns = list(self.df.columns)[:10]
        preview_table.setHorizontalHeaderLabels(columns)
        
        # 填充数据
        for i in range(min(5, len(self.df))):
            for j, col in enumerate(columns):
                if j < len(columns):
                    value = self.df.iloc[i][col]
                    if pd.isna(value):
                        value = ""
                    preview_table.setItem(i, j, QTableWidgetItem(str(value)))
        
        preview_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(preview_table)
        
        layout.addWidget(QLabel("确认导入这些记录吗？"))
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

class MSDSDialog(QDialog):
    """MSDS对话框"""
    
    def __init__(self, parent=None, msds=None):
        super().__init__(parent)
        self.msds = msds
        self.setWindowTitle("添加MSDS" if not msds else "编辑MSDS")
        self.setMinimumWidth(700)
        
        self.setup_ui()
        if msds:
            self.load_msds_data()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        # 使用标签页组织内容
        tab_widget = QTabWidget()
        
        # 基本信息标签页
        basic_tab = QWidget()
        basic_layout = QFormLayout(basic_tab)
        
        self.msds_id_input = QLineEdit()
        self.material_name_input = QLineEdit()
        self.cas_input = QLineEdit()
        self.supplier_input = QLineEdit()
        self.version_input = QLineEdit()
        
        self.effective_date = QDateEdit()
        self.effective_date.setCalendarPopup(True)
        self.effective_date.setDate(QDate.currentDate())
        
        self.expiry_date = QDateEdit()
        self.expiry_date.setCalendarPopup(True)
        self.expiry_date.setDate(QDate.currentDate().addYears(1))
        self.expiry_date.setSpecialValueText("无")
        
        self.hazard_class_input = QLineEdit()
        self.hazard_class_input.setPlaceholderText("用逗号分隔，如：易燃,有毒")
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(["有效", "过期", "待审核"])
        
        basic_layout.addRow("MSDS ID*:", self.msds_id_input)
        basic_layout.addRow("物料名称*:", self.material_name_input)
        basic_layout.addRow("CAS号*:", self.cas_input)
        basic_layout.addRow("供应商:", self.supplier_input)
        basic_layout.addRow("版本:", self.version_input)
        basic_layout.addRow("生效日期:", self.effective_date)
        basic_layout.addRow("有效期:", self.expiry_date)
        basic_layout.addRow("危险类别:", self.hazard_class_input)
        basic_layout.addRow("状态:", self.status_combo)
        
        tab_widget.addTab(basic_tab, "基本信息")
        
        # 文件信息标签页
        file_tab = QWidget()
        file_layout = QVBoxLayout(file_tab)
        
        # 文件路径选择
        file_path_layout = QHBoxLayout()
        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("MSDS文件路径")
        browse_btn = QPushButton("浏览...")
        browse_btn.clicked.connect(self.browse_file)
        
        file_path_layout.addWidget(self.file_path_input)
        file_path_layout.addWidget(browse_btn)
        
        file_layout.addWidget(QLabel("文件路径:"))
        file_layout.addLayout(file_path_layout)
        
        # 文件信息显示
        self.file_info_label = QLabel("未选择文件")
        self.file_info_label.setWordWrap(True)
        file_layout.addWidget(self.file_info_label)
        
        tab_widget.addTab(file_tab, "文件信息")
        
        # 危险信息标签页
        hazard_tab = QWidget()
        hazard_layout = QVBoxLayout(hazard_tab)
        
        self.hazard_statements_input = QTextEdit()
        self.hazard_statements_input.setPlaceholderText("危险性说明...")
        
        self.precautionary_statements_input = QTextEdit()
        self.precautionary_statements_input.setPlaceholderText("防范说明...")
        
        hazard_layout.addWidget(QLabel("危险性说明:"))
        hazard_layout.addWidget(self.hazard_statements_input)
        hazard_layout.addWidget(QLabel("防范说明:"))
        hazard_layout.addWidget(self.precautionary_statements_input)
        
        tab_widget.addTab(hazard_tab, "危险信息")
        
        # 应急处理标签页
        emergency_tab = QWidget()
        emergency_layout = QVBoxLayout(emergency_tab)
        
        self.first_aid_measures_input = QTextEdit()
        self.first_aid_measures_input.setPlaceholderText("急救措施...")
        
        self.fire_fighting_measures_input = QTextEdit()
        self.fire_fighting_measures_input.setPlaceholderText("消防措施...")
        
        emergency_layout.addWidget(QLabel("急救措施:"))
        emergency_layout.addWidget(self.first_aid_measures_input)
        emergency_layout.addWidget(QLabel("消防措施:"))
        emergency_layout.addWidget(self.fire_fighting_measures_input)
        
        tab_widget.addTab(emergency_tab, "应急处理")
        
        # 其他信息标签页
        other_tab = QWidget()
        other_layout = QVBoxLayout(other_tab)
        
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("描述信息...")
        
        other_layout.addWidget(QLabel("描述:"))
        other_layout.addWidget(self.description_input)
        
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
    
    def browse_file(self):
        """浏览文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择MSDS文件", "",
            "PDF文件 (*.pdf);;Word文件 (*.doc *.docx);;所有文件 (*.*)"
        )
        
        if file_path:
            self.file_path_input.setText(file_path)
            file_size = os.path.getsize(file_path)
            file_info = f"文件: {os.path.basename(file_path)}\n大小: {self.format_file_size(file_size)}"
            self.file_info_label.setText(file_info)
    
    def format_file_size(self, size_bytes):
        """格式化文件大小"""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def validate_and_accept(self):
        """验证并接受"""
        msds_id = self.msds_id_input.text().strip()
        material_name = self.material_name_input.text().strip()
        cas_number = self.cas_input.text().strip()
        
        errors = []
        
        if not msds_id:
            errors.append("MSDS ID不能为空")
        if not material_name:
            errors.append("物料名称不能为空")
        if not cas_number:
            errors.append("CAS号不能为空")
        
        # 验证CAS号格式
        if cas_number and not self.validate_cas(cas_number):
            errors.append("CAS号格式不正确 (格式: XXXXXXX-XX-X)")
        
        if errors:
            self.validation_label.setText("错误: " + "; ".join(errors))
            return
        
        self.validation_label.setText("")
        self.accept()
    
    def validate_cas(self, cas_number):
        """验证CAS号格式"""
        pattern = r'^\d{1,7}-\d{2}-\d$'
        return re.match(pattern, cas_number) is not None
    
    def load_msds_data(self):
        """加载MSDS数据"""
        if not self.msds:
            return
        
        self.msds_id_input.setText(self.msds.msds_id)
        self.material_name_input.setText(self.msds.material_name)
        self.cas_input.setText(self.msds.cas_number)
        self.supplier_input.setText(self.msds.supplier or "")
        self.version_input.setText(self.msds.version or "")
        
        if hasattr(self.msds, 'effective_date') and self.msds.effective_date:
            if hasattr(self.msds.effective_date, 'year'):
                self.effective_date.setDate(QDate(
                    self.msds.effective_date.year,
                    self.msds.effective_date.month,
                    self.msds.effective_date.day
                ))
        
        if hasattr(self.msds, 'expiry_date') and self.msds.expiry_date:
            if hasattr(self.msds.expiry_date, 'year'):
                self.expiry_date.setDate(QDate(
                    self.msds.expiry_date.year,
                    self.msds.expiry_date.month,
                    self.msds.expiry_date.day
                ))
        
        self.hazard_class_input.setText(self.msds.hazard_class or "")
        
        index = self.status_combo.findText(self.msds.status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        
        if hasattr(self.msds, 'file_path') and self.msds.file_path:
            self.file_path_input.setText(self.msds.file_path)
            if os.path.exists(self.msds.file_path):
                file_size = os.path.getsize(self.msds.file_path)
                file_info = f"文件: {os.path.basename(self.msds.file_path)}\n大小: {self.format_file_size(file_size)}"
                self.file_info_label.setText(file_info)
        
        if hasattr(self.msds, 'hazard_statements') and self.msds.hazard_statements:
            self.hazard_statements_input.setText(self.msds.hazard_statements)
        
        if hasattr(self.msds, 'precautionary_statements') and self.msds.precautionary_statements:
            self.precautionary_statements_input.setText(self.msds.precautionary_statements)
        
        if hasattr(self.msds, 'first_aid_measures') and self.msds.first_aid_measures:
            self.first_aid_measures_input.setText(self.msds.first_aid_measures)
        
        if hasattr(self.msds, 'fire_fighting_measures') and self.msds.fire_fighting_measures:
            self.fire_fighting_measures_input.setText(self.msds.fire_fighting_measures)
        
        self.description_input.setText(self.msds.description or "")
    
    def get_msds(self):
        """获取MSDS对象"""
        from ..process_design_data import MSDSDocument
        
        msds_id = self.msds_id_input.text().strip()
        material_name = self.material_name_input.text().strip()
        cas_number = self.cas_input.text().strip()
        
        # 创建基本MSDS对象
        msds = MSDSDocument(
            msds_id=msds_id,
            material_name=material_name,
            cas_number=cas_number,
            supplier=self.supplier_input.text().strip(),
            version=self.version_input.text().strip(),
            effective_date=self.effective_date.date().toPython(),
            expiry_date=self.expiry_date.date().toPython() if not self.expiry_date.date().isNull() else None,
            hazard_class=self.hazard_class_input.text().strip(),
            status=self.status_combo.currentText(),
            description=self.description_input.toPlainText().strip(),
            last_updated=datetime.now()
        )
        
        # 添加文件信息
        file_path = self.file_path_input.text().strip()
        if file_path:
            msds.file_path = file_path
            msds.file_name = os.path.basename(file_path)
            if os.path.exists(file_path):
                msds.file_size = os.path.getsize(file_path)
                msds.file_type = os.path.splitext(file_path)[1].lower()
        
        # 添加危险信息
        hazard_statements = self.hazard_statements_input.toPlainText().strip()
        if hazard_statements:
            msds.hazard_statements = hazard_statements
        
        precautionary_statements = self.precautionary_statements_input.toPlainText().strip()
        if precautionary_statements:
            msds.precautionary_statements = precautionary_statements
        
        # 添加应急处理信息
        first_aid_measures = self.first_aid_measures_input.toPlainText().strip()
        if first_aid_measures:
            msds.first_aid_measures = first_aid_measures
        
        fire_fighting_measures = self.fire_fighting_measures_input.toPlainText().strip()
        if fire_fighting_measures:
            msds.fire_fighting_measures = fire_fighting_measures
        
        return msds