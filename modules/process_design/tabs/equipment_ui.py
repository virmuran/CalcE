# modules/process_design/tabs/equipment_ui.py
import sys
import os
from datetime import datetime

from PySide6.QtCore import Qt, Signal, QTimer, QPoint, QRect, QSize, QEvent
from PySide6.QtGui import QAction, QKeySequence, QClipboard, QFont, QColor
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QDoubleSpinBox, QComboBox, QTextEdit, QGroupBox,
    QCheckBox, QFileDialog, QSplitter, QTabWidget,
    QMenu, QApplication, QFrame, QToolBar, QDialogButtonBox,
    QSpinBox, QScrollArea, QToolTip,
    QListWidget, QListWidgetItem
)

class EquipmentListUI:
    """设备列表UI管理类"""
    
    def setup_ui(self):
        """设置UI界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)  # 减少外边距
        main_layout.setSpacing(2)  # 减少控件间距
        
        # 工具栏 - 固定高度
        self.setup_toolbar(main_layout)
        
        # 搜索和过滤区域 - 固定高度
        self.setup_filter_area(main_layout)
        
        # 主要区域：使用分割器，占据剩余空间
        self.setup_main_area(main_layout)
        
        # 状态栏 - 固定高度
        self.setup_status_bar(main_layout)
        
        # 设置窗口的最小尺寸
        self.setMinimumSize(800, 600)
    
    def setup_toolbar(self, main_layout):
        """设置工具栏"""
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setFixedHeight(36)  # 固定工具栏高度
        
        # 添加按钮
        self.add_action = QAction("添加", self)
        self.add_action.triggered.connect(self.add_equipment)
        toolbar.addAction(self.add_action)
        
        self.edit_action = QAction("编辑", self)
        self.edit_action.triggered.connect(self.edit_equipment)
        toolbar.addAction(self.edit_action)
        
        self.batch_edit_action = QAction("批量编辑", self)
        self.batch_edit_action.triggered.connect(self.batch_edit_equipment)
        toolbar.addAction(self.batch_edit_action)
        
        self.delete_action = QAction("删除", self)
        self.delete_action.triggered.connect(self.delete_equipment)
        self.delete_action.setToolTip("删除选中的设备（支持批量删除）")
        toolbar.addAction(self.delete_action)
        
        toolbar.addSeparator()
        
        self.select_all_action = QAction("全选", self)
        self.select_all_action.triggered.connect(self.select_all_equipment)
        toolbar.addAction(self.select_all_action)
        
        self.clear_selection_action = QAction("清除选择", self)
        self.clear_selection_action.triggered.connect(self.clear_selection)
        toolbar.addAction(self.clear_selection_action)
        
        toolbar.addSeparator()
        
        self.mapping_action = QAction("对照表", self)
        self.mapping_action.triggered.connect(self.manage_name_mapping)
        toolbar.addAction(self.mapping_action)
        
        toolbar.addSeparator()
        
        self.template_create_action = QAction("创建模板", self)
        self.template_create_action.triggered.connect(self.create_template)
        toolbar.addAction(self.template_create_action)
        
        self.template_import_action = QAction("导入", self)
        self.template_import_action.triggered.connect(self.import_equipment_by_template)
        toolbar.addAction(self.template_import_action)
        
        self.template_export_action = QAction("导出", self)
        self.template_export_action.triggered.connect(self.export_equipment_with_template)
        toolbar.addAction(self.template_export_action)
        
        self.template_manage_action = QAction("模板管理", self)
        self.template_manage_action.triggered.connect(self.manage_templates)
        toolbar.addAction(self.template_manage_action)
        
        toolbar.addSeparator()
        
        self.repair_action = QAction("修复文件", self)
        self.repair_action.triggered.connect(self.repair_import_file)
        toolbar.addAction(self.repair_action)
        
        main_layout.addWidget(toolbar)
    
    def setup_filter_area(self, main_layout):
        """设置搜索和过滤区域"""
        filter_frame = QFrame()
        filter_frame.setFixedHeight(50)  # 固定搜索区域高度
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(8, 4, 8, 4)  # 紧凑的内边距
        filter_layout.setSpacing(8)
        
        # 搜索部分 - 简化版本
        search_layout = QHBoxLayout()
        search_layout.setSpacing(4)
        search_label = QLabel("搜索:")
        
        # 搜索字段选择器 - 单选版本
        self.search_field_combo = QComboBox()
        self.search_field_combo.addItem("全部字段", "all")
        self.search_field_combo.addItem("设备ID", "equipment_id")
        self.search_field_combo.addItem("设备名称", "name")
        self.search_field_combo.addItem("设备类型", "type")
        self.search_field_combo.addItem("制造商", "manufacturer")
        self.search_field_combo.addItem("安装位置", "location")
        self.search_field_combo.addItem("唯一编码", "unique_code")
        self.search_field_combo.addItem("规格摘要", "specification")
        self.search_field_combo.addItem("备注", "notes")
        self.search_field_combo.addItem("P&ID图号", "pid_dwg_no")
        self.search_field_combo.setFixedHeight(28)
        self.search_field_combo.setToolTip("选择要搜索的字段")
        self.search_field_combo.setCurrentIndex(0)  # 默认选择"全部字段"
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入搜索关键词... (可使用设备ID、名称、类型等)")
        self.search_input.setFixedHeight(28)
        self.search_input.textChanged.connect(self.on_search_changed)
        self.search_input.returnPressed.connect(self.perform_search)
        
        # 清空搜索按钮
        self.clear_search_btn = QPushButton("清空")
        self.clear_search_btn.setFixedHeight(28)
        self.clear_search_btn.clicked.connect(self.clear_search)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_field_combo)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.clear_search_btn)
        
        filter_layout.addLayout(search_layout)
        filter_layout.addStretch()
        
        main_layout.addWidget(filter_frame)
    
    def setup_main_area(self, main_layout):
        """设置主区域"""
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)  # 防止子部件被压缩消失
        
        # 左侧：表格区域 - 使用拉伸因子
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(2)
        
        # 表格上方的信息区域 - 固定高度
        info_frame = QFrame()
        info_frame.setFixedHeight(30)
        info_layout = QHBoxLayout(info_frame)
        info_layout.setContentsMargins(8, 4, 8, 4)
        
        self.info_label = QLabel("总计: 0 个设备")
        info_layout.addWidget(self.info_label)
        info_layout.addStretch()
        
        self.selected_label = QLabel("已选择: 0 个")
        info_layout.addWidget(self.selected_label)
        
        table_layout.addWidget(info_frame)
        
        # 表格 - 设置为可拉伸，占据剩余空间
        self.equipment_table = QTableWidget()
        self.setup_table_columns()
        
        table_layout.addWidget(self.equipment_table, 1)
        
        splitter.addWidget(table_container)
        
        # 右侧：详情区域 - 按比例分配高度
        detail_container = self.create_detail_container()
        splitter.addWidget(detail_container)
        
        # 设置分割器的初始大小比例
        splitter.setSizes([700, 300])
        
        # 将分割器添加到主布局，使用拉伸因子1，使其占据剩余空间
        main_layout.addWidget(splitter, 1)
    
    def setup_table_columns(self):
        """设置表格列"""
        self.equipment_table.setColumnCount(13)
        self.equipment_table.setHorizontalHeaderLabels([
            "设备ID", "设备名称", "设备类型", "规格摘要", 
            "制造商", "安装位置", "状态", "投用日期", 
            "设计压力", "设计温度", "操作压力", "操作温度",
            "备注"
        ])
        
        header = self.equipment_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 设备ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # 设备名称
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 设备类型
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 规格摘要
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 制造商
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # 安装位置
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # 状态
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # 投用日期
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # 设计压力
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)  # 设计温度
        header.setSectionResizeMode(10, QHeaderView.ResizeToContents) # 操作压力
        header.setSectionResizeMode(11, QHeaderView.ResizeToContents) # 操作温度
        header.setSectionResizeMode(12, QHeaderView.Stretch)          # 备注
        
        self.equipment_table.setSortingEnabled(True)
        self.equipment_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.equipment_table.setSelectionMode(QTableWidget.ExtendedSelection)
        
        self.equipment_table.itemDoubleClicked.connect(self.on_equipment_double_clicked)
        self.equipment_table.itemSelectionChanged.connect(self.on_selection_changed)
    
    def create_detail_container(self):
        """创建设备详情容器"""
        detail_container = QWidget()
        detail_container.setMinimumWidth(300)
        detail_container.setMaximumWidth(500)
        detail_layout = QVBoxLayout(detail_container)
        detail_layout.setContentsMargins(5, 0, 5, 0)
        detail_layout.setSpacing(2)

        detail_label = QLabel("设备详情")
        detail_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 5px 0;")
        detail_layout.addWidget(detail_label)

        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        detail_layout.addWidget(self.detail_text, 3)  # 设备详情占3/5

        property_label = QLabel("技术参数")
        property_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px 0 5px 0;")
        detail_layout.addWidget(property_label)

        self.property_table = QTableWidget()
        self.property_table.setColumnCount(2)
        self.property_table.setHorizontalHeaderLabels(["参数", "值"])
        self.property_table.horizontalHeader().setStretchLastSection(True)
        self.property_table.setEditTriggers(QTableWidget.NoEditTriggers)
        detail_layout.addWidget(self.property_table, 2)  # 技术参数占2/5
        
        # 在详情区域添加一个拉伸，防止控件过度拉伸
        detail_layout.addStretch()
        
        return detail_container
    
    def setup_status_bar(self, main_layout):
        """设置状态栏"""
        self.status_bar = QLabel()
        self.status_bar.setFixedHeight(25)  # 固定高度
        self.status_bar.setText("就绪")
        main_layout.addWidget(self.status_bar)
    
    def setup_shortcuts(self):
        """设置快捷键"""
        # 复制快捷键
        self.copy_action = QAction("复制", self)
        self.copy_action.setShortcut(QKeySequence.Copy)
        self.copy_action.triggered.connect(self.copy_selected)
        self.addAction(self.copy_action)
        
        # 刷新快捷键 - 连接到force_refresh
        self.refresh_action = QAction("刷新", self)
        self.refresh_action.setShortcut(QKeySequence.Refresh)
        self.refresh_action.triggered.connect(self.force_refresh)
        self.addAction(self.refresh_action)
        
        # 全选快捷键
        self.select_all_action = QAction("全选", self)
        self.select_all_action.setShortcut(QKeySequence.SelectAll)
        self.select_all_action.triggered.connect(self.select_all_equipment)
        self.addAction(self.select_all_action)
        
        # 删除快捷键
        self.delete_shortcut = QAction("删除", self)
        self.delete_shortcut.setShortcut(QKeySequence.Delete)
        self.delete_shortcut.triggered.connect(self.smart_delete)
        self.addAction(self.delete_shortcut)
    
    def get_color_map(self):
        """获取设备类型颜色映射"""
        return {
            "A 搅拌设备类": Qt.blue,
            "B 风机类": Qt.darkGreen,
            "C 塔器": Qt.darkCyan,
            "D 槽罐": Qt.darkMagenta,
            "E 换热设备类": Qt.darkYellow,
            "G 成粒成型设备类": Qt.darkRed,
            "H 贮斗、料斗类": Qt.darkGray,
            "J 喷射器类": Qt.magenta,
            "K 压缩机类": Qt.darkBlue,
            "L 起重、装卸、包装机械设备类": Qt.green,
            "M 磨碎设备类、混合器类": Qt.cyan,
            "P 泵类": Qt.red,
            "R 反应器": Qt.darkGreen,
            "S 分离设备类": Qt.darkRed,
            "T 储罐": Qt.blue,
            "U 公用辅助设备类": Qt.darkYellow,
            "V 固体输送类（刮板机、铰刀、提升机、皮带机）": Qt.darkMagenta,
            "W 称重类设备": Qt.darkCyan,
            "X 成套设备类": Qt.gray,
            "其他": Qt.black
        }