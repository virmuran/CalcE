# modules/process_design/tabs/equipment_list_tab.py
import datetime
import re
import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from PySide6.QtCore import Qt, Signal, QTimer, QPoint, QRect, QSize, QEvent
from PySide6.QtGui import QAction, QKeySequence, QClipboard
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QHeaderView, QMessageBox, QDialog,
    QFormLayout, QDoubleSpinBox, QComboBox, QTextEdit, QGroupBox,
    QCheckBox, QFileDialog, QSplitter, QTabWidget,
    QMenu, QApplication, QFrame, QToolBar, QDialogButtonBox,
    QSpinBox, QScrollArea,
    QListWidget, QListWidgetItem
)

# 导入拆分后的模块
from .equipment_id_generator import EquipmentIDGenerator
from .equipment_id_table_item import EquipmentIDTableWidgetItem
from .equipment_properties import EquipmentPropertiesExtractor
from .equipment_templates import EquipmentTemplateCreator, EquipmentTemplateFiller
from .equipment_dialogs import (
    EquipmentDialog, BatchEditDialog, TemplateImportPreviewDialog,
    ProjectInfoDialog, TemplateTypeDialog
)
from .equipment_import_export import EquipmentImportExport

# 设置模块路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)

paths_to_add = [current_dir, parent_dir, grandparent_dir]
for path in paths_to_add:
    if path not in sys.path:
        sys.path.insert(0, path)

# 尝试导入工艺设计相关模块
try:
    from ..data.unified_data_manager import UnifiedDataManager as ProcessDesignManager
    from ..data.data_models import UnifiedEquipment
except ImportError:
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
    
    class UnifiedEquipment:
        def __init__(self, **kwargs):
            # 必需字段
            self.unique_code = kwargs.get('unique_code', '')
            self.equipment_id = kwargs.get('equipment_id', '')
            self.name = kwargs.get('name', '')
            self.type = kwargs.get('type', kwargs.get('equipment_type', '其他'))
            
            # 技术参数
            self.specification = kwargs.get('specification', '')
            self.model = kwargs.get('model', '')
            self.manufacturer = kwargs.get('manufacturer', '')
            
            # 设计操作参数
            self.design_pressure = kwargs.get('design_pressure', '')
            self.design_temperature = kwargs.get('design_temperature', '')
            self.operating_pressure = kwargs.get('operating_pressure', '')
            self.operating_temperature = kwargs.get('operating_temperature', '')
            
            # 导出相关
            self.quantity = kwargs.get('quantity', 1)
            self.unit_price = kwargs.get('unit_price', 0)
            self.total_price = kwargs.get('total_price', 0)
            self.material = kwargs.get('material', '')
            self.insulation = kwargs.get('insulation', '')
            self.weight_estimate = kwargs.get('weight_estimate', '')
            self.dynamic = kwargs.get('dynamic', '')
            self.notes = kwargs.get('notes', '')
            
            # 英文描述
            self.description_en = kwargs.get('description_en', kwargs.get('Description', ''))
            
            # P&ID图号
            self.pid_dwg_no = kwargs.get('pid_dwg_no', '')
            
            # 功率相关
            self.single_power = kwargs.get('single_power', 0)
            self.operating_power = kwargs.get('operating_power', 0)
            self.total_power = kwargs.get('total_power', 0)
            
            # 其他
            self.commission_date = kwargs.get('commission_date', None)

class EquipmentListTab(QWidget):
    """设备列表标签页"""
    equipment_selected = Signal(str)
    equipment_list_updated = Signal()
    
    def __init__(self, data_manager=None, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.process_manager = None
        self.current_equipment = []
        
        if data_manager:
            try:
                self.process_manager = ProcessDesignManager(data_manager)
            except Exception:
                self.process_manager = None
        
        # 初始化工具类
        self.properties_extractor = EquipmentPropertiesExtractor()
        self.template_creator = EquipmentTemplateCreator()
        self.template_filler = EquipmentTemplateFiller()
        self.import_export = EquipmentImportExport(self)
        
        # 初始化UI之前先创建equipment_table属性，避免后续访问错误
        self.equipment_table = None
        
        self.setup_ui()
        self.load_equipment()
        self.setup_shortcuts()
        
        # 添加延迟初始化，确保UI完全加载
        QTimer.singleShot(100, self.finalize_initialization)

    def finalize_initialization(self):
        """完成初始化，确保表格正确显示"""
        if self.equipment_table:
            # 确保表格正确排序
            self.equipment_table.sortItems(0, Qt.AscendingOrder)
            # 强制重绘
            self.equipment_table.viewport().update()
        self.status_bar.setText("就绪 - 初始化完成")
    
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)  # 减少外边距
        main_layout.setSpacing(2)  # 减少控件间距
        
        # 工具栏 - 固定高度
        toolbar = QToolBar()
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setFixedHeight(36)  # 固定工具栏高度
        
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
        
        import_from_pfd_action = QAction("📥 从流程图导入", self)
        import_from_pfd_action.triggered.connect(self.import_from_flow_diagram)
        toolbar.addAction(import_from_pfd_action)
        
        main_layout.addWidget(toolbar)
        
        # 搜索和过滤区域 - 固定高度
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
        # 移除安装位置选项
        # self.search_field_combo.addItem("安装位置", "location")
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
        
        # 主要区域：使用分割器，占据剩余空间
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
        self.equipment_table.setColumnCount(11)
        self.equipment_table.setHorizontalHeaderLabels([
            "设备ID", "设备名称", "设备类型", "规格摘要", "制造商", 
            "投用日期", "设计压力", "设计温度", "操作压力", "操作温度",
            "备注"
        ])
        
        header = self.equipment_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 设备ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # 设备名称
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 设备类型
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 规格摘要
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 制造商
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # 投用日期
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # 设计压力
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # 设计温度
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # 操作压力
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents)  # 操作温度
        header.setSectionResizeMode(10, QHeaderView.Stretch)          # 备注
        
        self.equipment_table.setSortingEnabled(True)
        self.equipment_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.equipment_table.setSelectionMode(QTableWidget.ExtendedSelection)
        
        self.equipment_table.itemDoubleClicked.connect(self.on_equipment_double_clicked)
        self.equipment_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        # 表格添加到布局，使用拉伸因子1，使其占据剩余空间
        table_layout.addWidget(self.equipment_table, 1)
        
        splitter.addWidget(table_container)
        
        # 右侧：详情区域 - 按比例分配高度
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
        
        splitter.addWidget(detail_container)
        
        # 设置分割器的初始大小比例
        splitter.setSizes([700, 300])
        
        # 将分割器添加到主布局，使用拉伸因子1，使其占据剩余空间
        main_layout.addWidget(splitter, 1)  # 注意：这里只添加一次！
        
        # 状态栏 - 固定高度
        self.status_bar = QLabel()
        self.status_bar.setFixedHeight(25)  # 固定高度
        self.status_bar.setText("就绪")
        main_layout.addWidget(self.status_bar)
        
        # 设置窗口的最小尺寸
        self.setMinimumSize(800, 600)

    def setup_shortcuts(self):
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
        
    def smart_delete(self):
        """智能删除：根据选择数量调用统一的删除功能"""
        selected_ids = self.get_selected_equipment_ids()
        
        if not selected_ids:
            QMessageBox.warning(self, "警告", "请先选择要删除的设备")
            return
        
        # 直接调用统一的删除函数
        self.delete_equipment()
        
    def force_refresh(self):
        """强制刷新设备列表"""
        self.status_bar.setText("正在刷新...")
        QApplication.processEvents()  # 处理挂起的事件
        
        try:
            # 保存当前选中的行
            selected_rows = self.equipment_table.selectionModel().selectedRows()
            selected_ids = [self.equipment_table.item(row.row(), 0).text() for row in selected_rows if self.equipment_table.item(row.row(), 0)]
            
            # 执行刷新
            self.load_equipment()
            
            # 尝试恢复选择
            if selected_ids:
                self.select_equipment_by_ids(selected_ids)
            
            self.status_bar.setText("刷新完成")
            
        except Exception as e:
            self.status_bar.setText(f"刷新失败: {str(e)}")
            QMessageBox.warning(self, "刷新错误", f"刷新过程中发生错误:\n{str(e)}")

    def select_equipment_by_ids(self, equipment_ids):
        """根据设备ID选择行"""
        if not self.equipment_table:
            return
            
        self.equipment_table.clearSelection()
        
        for row in range(self.equipment_table.rowCount()):
            item = self.equipment_table.item(row, 0)
            if item and item.text() in equipment_ids:
                self.equipment_table.selectRow(row)
        
    def eventFilter(self, source, event):
        """事件过滤器，处理键盘事件"""
        if source == self.equipment_table and event.type() == QEvent.KeyPress:
            pass
        
        return super().eventFilter(source, event)
    
    def get_properties_by_equipment_type(self, equipment_type, equipment):
        """根据新设备类型返回要显示的技术参数列表"""
        return self.properties_extractor.get_properties_by_equipment_type(equipment_type, equipment)
    
    def import_from_flow_diagram(self):
        """从工艺流程图导入设备"""
        try:
            if not self.process_manager:
                QMessageBox.warning(self, "警告", "数据管理器未初始化，无法导入设备")
                return
                
            # 这里应该调用工艺流程图模块的接口来获取设备列表
            # 由于这是一个占位实现，我们先显示一个提示
            QMessageBox.information(
                self, 
                "从流程图导入", 
                "从流程图导入设备的功能正在开发中...\n\n"
                "这个功能将从当前的工艺流程图页面获取设备数据，"
                "并将其添加到设备列表中。"
            )
            
            # TODO: 实现从流程图页面获取设备数据的逻辑
            # 应该调用流程图标签页的方法来获取当前流程图中的设备
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"从流程图导入设备时发生错误:\n{str(e)}")
    
    # ==================== 模板相关方法 ====================
    
    def export_equipment_with_template(self):
        """统一的设备导出功能 - 支持模板导出和批量导出"""
        try:
            # 检查是否有选中设备
            selected_ids = self.get_selected_equipment_ids()
            
            # 确定导出范围
            if selected_ids:
                # 有选中设备，询问用户导出范围
                scope = self._ask_export_scope(len(selected_ids))
                if scope == "cancel":
                    return
                
                if scope == "selected":
                    # 导出选中设备
                    equipment_list = []
                    for equipment_id in selected_ids:
                        equipment = self.process_manager.get_equipment(equipment_id)
                        if equipment:
                            equipment_list.append(equipment)
                    export_scope = f"选中设备 ({len(selected_ids)}个)"
                else:  # all
                    # 导出全部设备
                    equipment_list = self.process_manager.get_all_equipment()
                    export_scope = "全部设备"
            else:
                # 没有选中设备，直接导出全部
                equipment_list = self.process_manager.get_all_equipment()
                export_scope = "全部设备"
            
            if not equipment_list:
                QMessageBox.warning(self, "警告", "没有设备可导出")
                return
            
            # 选择模板文件
            template_path, _ = QFileDialog.getOpenFileName(
                self, f"选择模板文件 - {export_scope}", "",
                "Excel模板文件 (*.xlsx);;所有文件 (*)"
            )
            
            if not template_path:
                return
            
            # 选择保存位置
            default_name = f"设备清单_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            output_path, _ = QFileDialog.getSaveFileName(
                self, f"保存设备清单 - {export_scope}", default_name,
                "Excel文件 (*.xlsx)"
            )
            
            if not output_path:
                return
            
            template_filler = EquipmentTemplateFiller()
            
            # 获取项目信息
            project_info = self.get_project_info_from_dialog()
            if project_info is None:
                return
            
            # 填充模板
            success = template_filler.fill_template(
                template_path, output_path, equipment_list, project_info
            )
            
            if success:
                QMessageBox.information(
                    self, "导出成功",
                    f"已成功导出 {len(equipment_list)} 个设备 ({export_scope})\n文件已保存到:\n{output_path}"
                )
                
                # 询问是否打开文件
                reply = QMessageBox.question(
                    self, "打开文件",
                    "是否立即打开导出的文件？",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    self.open_file(output_path)
            else:
                QMessageBox.warning(self, "导出失败", "模板填充失败，请检查模板格式")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出过程中发生错误:\n{str(e)}")

    def _ask_export_scope(self, selected_count):
        """询问导出范围"""
        dialog = QDialog(self)
        dialog.setWindowTitle("选择导出范围")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel(f"当前选中 {selected_count} 个设备"))
        layout.addWidget(QLabel("请选择要导出的范围:"))
        
        btn_layout = QVBoxLayout()
        
        selected_btn = QPushButton(f"导出选中设备 ({selected_count}个)")
        selected_btn.clicked.connect(lambda: self._set_scope_result(dialog, "selected"))
        btn_layout.addWidget(selected_btn)
        
        all_btn = QPushButton("导出全部设备")
        all_btn.clicked.connect(lambda: self._set_scope_result(dialog, "all"))
        btn_layout.addWidget(all_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(lambda: self._set_scope_result(dialog, "cancel"))
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        dialog.scope_result = None
        dialog.exec()
        
        return getattr(dialog, 'scope_result', 'cancel')

    def _set_scope_result(self, dialog, result):
        """设置导出范围结果"""
        dialog.scope_result = result
        dialog.accept()

    def _on_export_scope_selected(self, dialog, selected_ids, scope_type):
        """处理用户选择的导出范围"""
        dialog.accept()
        
        if scope_type == "selected":
            self._export_with_template_confirm(selected_ids, "选中设备")
        else:  # all
            self._export_with_template_confirm(None, "全部设备")

    def _export_with_template_confirm(self, selected_ids, scope_text):
        """执行模板导出"""
        try:
            template_path, _ = QFileDialog.getOpenFileName(
                self, f"选择模板文件 - {scope_text}", "",
                "Excel模板文件 (*.xlsx);;所有文件 (*)"
            )
            
            if not template_path:
                return
            
            default_name = f"设备清单_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            output_path, _ = QFileDialog.getSaveFileName(
                self, f"保存设备清单 - {scope_text}", default_name,
                "Excel文件 (*.xlsx)"
            )
            
            if not output_path:
                return
            
            template_filler = EquipmentTemplateFiller()
            
            # 根据范围获取设备列表
            if selected_ids:
                equipment_list = []
                for equipment_id in selected_ids:
                    equipment = self.process_manager.get_equipment(equipment_id)
                    if equipment:
                        equipment_list.append(equipment)
            else:
                equipment_list = self.process_manager.get_all_equipment()
            
            if not equipment_list:
                QMessageBox.warning(self, "警告", "没有设备可导出")
                return
            
            project_info = self.get_project_info_from_dialog()
            if project_info is None:
                return
            
            success = template_filler.fill_template(
                template_path, output_path, equipment_list, project_info
            )
            
            if success:
                QMessageBox.information(
                    self, "导出成功",
                    f"已成功导出 {len(equipment_list)} 个设备 ({scope_text})\n文件已保存到:\n{output_path}"
                )
                
                reply = QMessageBox.question(
                    self, "打开文件",
                    "是否立即打开导出的文件？",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    self.open_file(output_path)
            else:
                QMessageBox.warning(self, "导出失败", "模板填充失败，请检查模板格式")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出过程中发生错误:\n{str(e)}")
    
    def get_equipment_to_export(self):
        if self.batch_mode:
            selected_ids = self.get_selected_equipment()
            equipment_list = []
            for equipment_id in selected_ids:
                equipment = self.process_manager.get_equipment(equipment_id)
                if equipment:
                    equipment_list.append(equipment)
            return equipment_list
        else:
            return self.process_manager.get_all_equipment()
    
    def get_project_info_from_dialog(self):
        dialog = ProjectInfoDialog(self)
        if dialog.exec() == QDialog.Accepted:
            return dialog.get_project_info()
        return None
    
    def open_file(self, file_path):
        try:
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", file_path])
            else:
                subprocess.run(["xdg-open", file_path])
        except Exception:
            pass
    
    def create_template(self):
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存模板文件", "设备清单模板.xlsx",
                "Excel文件 (*.xlsx)"
            )
            
            if not file_path:
                return
            
            creator = EquipmentTemplateCreator()
            dialog = TemplateTypeDialog(self)
            
            if dialog.exec() == QDialog.Accepted:
                template_type = dialog.get_template_type()
                template_path = creator.create_template(template_type, file_path)
                config_path = creator.create_template_config(template_type)
                
                QMessageBox.information(
                    self, "模板创建成功",
                    f"模板已创建:\n{template_path}\n\n配置文件:\n{config_path}"
                )
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"创建模板失败:\n{str(e)}")
    
    # ==================== 核心功能方法 ====================
    
    def load_equipment(self):
        """加载设备列表 - 修复版本"""
        if not self.process_manager:
            self.status_bar.setText("错误: 数据管理器未初始化")
            return
        
        try:
            # 临时禁用表格更新，避免闪烁
            if self.equipment_table:
                self.equipment_table.setUpdatesEnabled(False)
            
            # 从数据管理器获取所有设备
            self.current_equipment = self.process_manager.get_all_equipment()
            
            # 将数据显示在表格中
            self.populate_table(self.current_equipment)
            
            # 重新启用表格更新
            if self.equipment_table:
                self.equipment_table.setUpdatesEnabled(True)
                # 强制重绘
                self.equipment_table.viewport().update()
            
            # 更新界面状态
            self.update_info_label()
            self.status_bar.setText(f"数据加载完成: {len(self.current_equipment)} 条记录")
            
        except Exception as e:
            # 确保表格更新被重新启用
            if self.equipment_table:
                self.equipment_table.setUpdatesEnabled(True)
            self.status_bar.setText(f"加载失败: {str(e)}")
            QMessageBox.critical(self, "错误", f"加载设备数据时发生错误:\n{str(e)}")
    
    def populate_table(self, equipment_list):
        """安全地填充表格，避免item所有权冲突"""
        if not self.equipment_table:
            return
            
        # 停止所有信号，防止排序干扰
        self.equipment_table.blockSignals(True)
        self.equipment_table.setSortingEnabled(False)
        
        try:
            # 完全清空表格
            self.equipment_table.clearContents()
            self.equipment_table.setRowCount(0)
            
            # 设置新的行数
            self.equipment_table.setRowCount(len(equipment_list))
            
            for i, equipment in enumerate(equipment_list):
                # 设备ID - 使用自定义排序项
                equipment_id = equipment.equipment_id if hasattr(equipment, 'equipment_id') else ""
                id_item = EquipmentIDTableWidgetItem(equipment_id)
                self.equipment_table.setItem(i, 0, id_item)
                
                # 设备名称 - 根据设备类型代码添加颜色提示
                name_item = QTableWidgetItem(equipment.name if hasattr(equipment, 'name') else "")
                
                color_map = {
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

                # 获取设备类型
                equipment_type = equipment.equipment_type if hasattr(equipment, 'equipment_type') else equipment.type if hasattr(equipment, 'type') else ""
                
                if equipment_type in color_map:
                    name_item.setForeground(color_map[equipment_type])
                
                self.equipment_table.setItem(i, 1, name_item)
                
                # 设备类型 - 第2列
                equipment_type = equipment.equipment_type if hasattr(equipment, 'equipment_type') else equipment.type if hasattr(equipment, 'type') else ""
                self.equipment_table.setItem(i, 2, QTableWidgetItem(equipment_type))
                
                # 规格摘要 - 第3列
                spec_summary = self._extract_spec_summary(equipment_type, equipment.specification if hasattr(equipment, 'specification') else "")
                spec_item = QTableWidgetItem(spec_summary)
                if hasattr(equipment, 'specification') and equipment.specification:
                    spec_item.setToolTip(f"完整规格:\n{equipment.specification}")
                self.equipment_table.setItem(i, 3, spec_item)
                
                # 制造商 - 第4列
                self.equipment_table.setItem(i, 4, QTableWidgetItem(equipment.manufacturer if hasattr(equipment, 'manufacturer') else ""))
                
                # 投用日期 - 第5列
                date_str = ""
                if hasattr(equipment, 'commission_date') and equipment.commission_date:
                    if hasattr(equipment.commission_date, 'strftime'):
                        date_str = equipment.commission_date.strftime("%Y-%m-%d")
                    else:
                        date_str = str(equipment.commission_date)
                self.equipment_table.setItem(i, 5, QTableWidgetItem(date_str))
                
                # 设计压力 - 第6列
                pressure_str = ""
                if hasattr(equipment, 'design_pressure') and equipment.design_pressure:
                    if isinstance(equipment.design_pressure, (int, float)):
                        pressure_str = f"{equipment.design_pressure:.2f}"
                    else:
                        pressure_str = str(equipment.design_pressure)
                self.equipment_table.setItem(i, 6, QTableWidgetItem(pressure_str))
                
                # 设计温度 - 第7列
                temp_str = ""
                if hasattr(equipment, 'design_temperature') and equipment.design_temperature:
                    if isinstance(equipment.design_temperature, (int, float)):
                        temp_str = f"{equipment.design_temperature:.1f}"
                    else:
                        temp_str = str(equipment.design_temperature)
                self.equipment_table.setItem(i, 7, QTableWidgetItem(temp_str))
                
                # 操作压力 - 第8列
                op_pressure_str = ""
                if hasattr(equipment, 'operating_pressure') and equipment.operating_pressure:
                    if isinstance(equipment.operating_pressure, (int, float)):
                        op_pressure_str = f"{equipment.operating_pressure:.2f}"
                    else:
                        op_pressure_str = str(equipment.operating_pressure)
                self.equipment_table.setItem(i, 8, QTableWidgetItem(op_pressure_str))
                
                # 操作温度 - 第9列
                op_temp_str = ""
                if hasattr(equipment, 'operating_temperature') and equipment.operating_temperature:
                    if isinstance(equipment.operating_temperature, (int, float)):
                        op_temp_str = f"{equipment.operating_temperature:.1f}"
                    else:
                        op_temp_str = str(equipment.operating_temperature)
                self.equipment_table.setItem(i, 9, QTableWidgetItem(op_temp_str))
                
                # 备注 - 第10列
                notes = equipment.notes if hasattr(equipment, 'notes') else ""
                notes_item = QTableWidgetItem(notes or "")
                if notes and len(notes) > 20:
                    notes_item.setToolTip(notes)
                self.equipment_table.setItem(i, 10, notes_item)
            
            # 重新启用排序
            self.equipment_table.setSortingEnabled(True)
            self.equipment_table.sortItems(0, Qt.AscendingOrder)
            
        finally:
            # 恢复信号
            self.equipment_table.blockSignals(False)
        
        self.update_info_label()

    def _extract_spec_summary(self, equipment_type, specification):
        """从完整规格中提取摘要信息"""
        if not specification:
            return ""
        
        # 根据设备类型提取关键信息
        if equipment_type == "反应器":
            # 提取容积
            volume_match = re.search(r'体积[:：]\s*([\d\.]+)\s*m³', specification)
            if volume_match:
                return f"{volume_match.group(1)}m³反应器"
        elif equipment_type == "泵":
            # 提取流量和扬程
            flow_match = re.search(r'流量[:：]\s*([\d\.]+)\s*m³/h', specification)
            head_match = re.search(r'扬程[:：]\s*([\d\.]+)\s*m', specification)
            if flow_match and head_match:
                return f"{flow_match.group(1)}m³/h, {head_match.group(1)}m"
        elif equipment_type == "储罐":
            # 提取容积
            volume_match = re.search(r'体积[:：]\s*([\d\.]+)\s*m³', specification)
            if volume_match:
                return f"{volume_match.group(1)}m³储罐"
        elif equipment_type == "换热器":
            # 提取换热面积
            area_match = re.search(r'换热面积[:：]\s*([\d\.]+)\s*m²', specification)
            if area_match:
                return f"{area_match.group(1)}m²换热器"
        
        # 通用情况：返回前50个字符
        return specification[:50] + ("..." if len(specification) > 50 else "")
    
    def on_search_changed(self):
        """搜索框文本变化时的处理 - 延迟搜索"""
        if hasattr(self, '_search_timer'):
            self._search_timer.stop()
        
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self.perform_search)
        self._search_timer.start(500)  # 500毫秒延迟
    
    def perform_search(self):
        """优化的搜索方法 - 精确匹配"""
        search_term = self.search_input.text().strip()
        
        # 获取选中的搜索字段
        selected_field = self.search_field_combo.currentData()
        
        # 如果搜索词相同、字段选择相同且结果已缓存，直接使用缓存
        cache_key = f"{search_term}:{selected_field}"
        if hasattr(self, '_last_search_cache_key') and self._last_search_cache_key == cache_key:
            if hasattr(self, '_cached_search_results'):
                self.current_equipment = self._cached_search_results
                self.apply_filters()
                return
        
        # 执行搜索
        try:
            equipment_list = self._exact_search_equipment(search_term, selected_field)
            
            # 缓存结果
            self._last_search_cache_key = cache_key
            self._cached_search_results = equipment_list
            
            self.current_equipment = equipment_list
            self.apply_filters()
            
            self.status_bar.setText(f"搜索到 {len(equipment_list)} 条记录")
            
        except Exception as e:
            self.status_bar.setText(f"搜索失败: {str(e)}")

    def _exact_search_equipment(self, search_term, selected_field):
        """
        精确搜索设备 - 在指定字段中进行子字符串精确匹配
        
        参数:
            search_term: 搜索关键词
            selected_field: 要搜索的字段，"all"表示搜索所有字段
        
        返回:
            匹配的设备列表
        """
        if not search_term or not self.process_manager:
            return self.process_manager.get_all_equipment() if self.process_manager else []
        
        search_term = search_term.lower().strip()
        
        try:
            all_equipment = self.process_manager.get_all_equipment()
            results = []
            
            # 字段映射：数据库字段 -> 显示名称
            field_mapping = {
                'equipment_id': lambda e: getattr(e, 'equipment_id', ''),
                'name': lambda e: getattr(e, 'name', ''),
                'type': lambda e: getattr(e, 'type', getattr(e, 'equipment_type', '')),
                'manufacturer': lambda e: getattr(e, 'manufacturer', ''),
                # 移除安装位置和状态字段
                # 'location': lambda e: getattr(e, 'location', ''),
                'unique_code': lambda e: getattr(e, 'unique_code', ''),
                'specification': lambda e: getattr(e, 'specification', ''),
                'notes': lambda e: getattr(e, 'notes', ''),
                'pid_dwg_no': lambda e: getattr(e, 'pid_dwg_no', ''),
                'model': lambda e: getattr(e, 'model', ''),
                # 'status': lambda e: getattr(e, 'status', ''),
                'material': lambda e: getattr(e, 'material', ''),
                'insulation': lambda e: getattr(e, 'insulation', ''),
                'description_en': lambda e: getattr(e, 'description_en', ''),
            }
            
            # 确定要搜索的字段列表
            if selected_field == "all":
                search_fields = list(field_mapping.keys())
            else:
                search_fields = [selected_field]
            
            for equipment in all_equipment:
                found = False
                
                for field in search_fields:
                    if field in field_mapping:
                        field_value = field_mapping[field](equipment)
                        
                        # 转换为字符串并进行搜索
                        if field_value and search_term in str(field_value).lower():
                            found = True
                            break
                
                if found:
                    results.append(equipment)
            
            return results
            
        except Exception as e:
            print(f"精确搜索出错: {e}")
            return []
    
    def clear_search(self):
        """清空搜索"""
        self.search_input.clear()
        self.search_field_combo.setCurrentIndex(0)  # 设置为"全部字段"
        self.load_equipment()
    
    def apply_filters(self):
        """应用过滤条件 - 现在只有搜索过滤"""
        self.populate_table(self.current_equipment)
    
    def on_equipment_double_clicked(self, item):
        """双击设备行显示详情"""
        if not self.equipment_table:
            return
            
        if item.column() == 0:
            return
        
        row = item.row()
        
        # 从第0列获取设备ID
        equipment_id_item = self.equipment_table.item(row, 0)
        if not equipment_id_item:
            return
        
        equipment_id = equipment_id_item.text()
        self.show_equipment_details(equipment_id)
        self.equipment_selected.emit(equipment_id)
    
    def show_equipment_details(self, equipment_id):
        """显示设备详情 - 动态显示技术参数"""
        if not self.process_manager:
            return
        
        equipment = self.process_manager.get_equipment(equipment_id)
        if not equipment:
            self.status_bar.setText(f"设备未找到: {equipment_id}")
            return
        
        # 获取设备类型
        equipment_type = getattr(equipment, 'equipment_type', getattr(equipment, 'type', '未知'))
        
        # 1. 设备详情区域显示
        details = self._get_equipment_details_html(equipment, equipment_type)
        self.detail_text.setHtml(details)
        
        # 2. 技术参数区域动态显示
        properties = self.get_properties_by_equipment_type(equipment_type, equipment)
        self._populate_property_table(properties)

    def _get_equipment_details_html(self, equipment, equipment_type):
        """生成设备详情的HTML内容"""
        details = f"<h3>{equipment.name} ({equipment.equipment_id})</h3>"
        details += f"<b>唯一编码:</b> {getattr(equipment, 'unique_code', '未设置')}<br>"
        details += f"<b>设备类型:</b> {equipment_type}<br>"
        details += f"<b>型号:</b> {getattr(equipment, 'model', '')}<br>"
        details += f"<b>制造商:</b> {getattr(equipment, 'manufacturer', '')}<br>"
        
        if hasattr(equipment, 'commission_date') and equipment.commission_date:
            date_str = equipment.commission_date.strftime('%Y-%m-%d') if hasattr(equipment.commission_date, 'strftime') else str(equipment.commission_date)
            details += f"<b>投用日期:</b> {date_str}<br>"
        
        # 显示P&ID图号
        pid_dwg_no = getattr(equipment, 'pid_dwg_no', '')
        if pid_dwg_no:
            details += f"<b>P&ID图号:</b> {pid_dwg_no}<br>"
        
        # 显示英文描述
        description_en = getattr(equipment, 'description_en', '')
        if description_en:
            details += f"<b>英文描述:</b> {description_en}<br>"
        
        # 显示完整规格
        specification = getattr(equipment, 'specification', '')
        if specification:
            details += f"<br><b>完整规格:</b><br>{specification}"
        
        # 显示备注
        notes = getattr(equipment, 'notes', '')
        if notes:
            details += f"<br><br><b>备注:</b><br>{notes}"
        
        return details

    def _populate_property_table(self, properties):
        """填充技术参数表格"""
        self.property_table.setRowCount(len(properties))
        
        for i, (prop, value) in enumerate(properties):
            self.property_table.setItem(i, 0, QTableWidgetItem(prop))
            self.property_table.setItem(i, 1, QTableWidgetItem(value))
        
        # 设置表格自适应
        self.property_table.resizeRowsToContents()
            
    def _format_parameter(self, value, unit, decimals):
        if value is None or value == '':
            return "未知"
        
        if isinstance(value, str):
            value = value.strip()
            if value.upper() == 'NT' or value.upper() == 'NP':
                return value.upper()
        
        if isinstance(value, (int, float)):
            if decimals == 1:
                return f"{value:.1f} {unit}"
            elif decimals == 2:
                return f"{value:.2f} {unit}"
            else:
                return f"{value} {unit}"
        else:
            return f"{value} {unit}"

    def get_selected_equipment_ids(self):
        """获取选中的设备ID列表"""
        if not self.equipment_table:
            return []
            
        selected_rows = self.equipment_table.selectionModel().selectedRows()
        selected_ids = []
        
        for row in selected_rows:
            # 设备ID在第0列
            equipment_id_item = self.equipment_table.item(row.row(), 0)
            if equipment_id_item:
                selected_ids.append(equipment_id_item.text())
        
        return selected_ids

    def select_all_equipment(self):
        """全选所有设备"""
        if self.equipment_table:
            self.equipment_table.selectAll()
            self.update_info_label()

    def clear_selection(self):
        """清除选择"""
        if self.equipment_table:
            self.equipment_table.clearSelection()
            self.update_info_label()

    def on_selection_changed(self):
        """选择变化时更新显示"""
        if not self.equipment_table:
            return
            
        selected_rows = self.equipment_table.selectionModel().selectedRows()
        
        # 如果选择了设备，显示第一个设备的详情
        if selected_rows:
            row = selected_rows[0].row()
            equipment_id = self.equipment_table.item(row, 0).text()
            self.show_equipment_details(equipment_id)
        
        # 更新选中数量显示
        self.update_info_label()

    def update_info_label(self):
        """更新信息标签"""
        total = self.equipment_table.rowCount() if self.equipment_table else 0
        selected = len(self.equipment_table.selectionModel().selectedRows()) if self.equipment_table else 0
        
        self.info_label.setText(f"总计: {total} 个设备")
        self.selected_label.setText(f"已选择: {selected} 个")
        
        # 在状态栏显示搜索信息
        search_term = self.search_input.text().strip()
        if search_term:
            selected_field = self.search_field_combo.currentText()
            self.status_bar.setText(f"在'{selected_field}'中搜索 '{search_term}'，找到 {total} 个设备")
        else:
            self.status_bar.setText(f"总计 {total} 个设备")
    
    def import_equipment(self):
        """导入设备数据"""
        return self.import_export.import_equipment()
    
    def export_equipment(self):
        """导出设备数据（按照设备清单模板格式）"""
        return self.import_export.export_equipment()
    
    def repair_import_file(self):
        """修复导入文件格式 - 主要修复唯一编码和设备位号"""
        return self.import_export.repair_import_file()
    
    def copy_selected(self):
        if not self.equipment_table:
            return
            
        selected_items = self.equipment_table.selectedItems()
        if not selected_items:
            return
        
        rows = sorted(set(item.row() for item in selected_items))
        cols = sorted(set(item.column() for item in selected_items))
        
        text = ""
        for row in rows:
            row_data = []
            for col in cols:
                if col == 0:
                    continue
                item = self.equipment_table.item(row, col)
                row_data.append(item.text() if item else "")
            text += "\t".join(row_data) + "\n"
        
        clipboard = QApplication.clipboard()
        clipboard.setText(text.strip())
        
        self.status_bar.setText(f"已复制 {len(rows)} 行数据")
    
    def batch_edit_equipment(self):
        """批量编辑设备"""
        selected_ids = self.get_selected_equipment_ids()
        if not selected_ids:
            QMessageBox.warning(self, "警告", "请先选择要编辑的设备")
            return
        
        dialog = BatchEditDialog(selected_ids, self.process_manager, self)
        if dialog.exec() == QDialog.Accepted:
            self.load_equipment()

    def delete_equipment(self):
        """删除设备 - 支持单个和批量删除"""
        selected_ids = self.get_selected_equipment_ids()
        if not selected_ids:
            QMessageBox.warning(self, "警告", "请先选择要删除的设备")
            return
        
        # 获取选中的第一个设备（用于单个删除时的确认信息）
        equipment = None
        if selected_ids:
            equipment = self.process_manager.get_equipment(selected_ids[0])
        
        # 确认删除
        confirmed = False
        
        if len(selected_ids) == 1 and equipment:
            # 单个设备删除确认
            reply = QMessageBox.question(
                self, "确认删除",
                f"确定要删除设备 '{equipment.name}' 吗？\n此操作不可恢复！",
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
            
            for equipment_id in selected_ids:
                if self.process_manager.delete_equipment(equipment_id):
                    success_count += 1
                else:
                    failed_count += 1
            
            # 重新加载数据
            self.load_equipment()
            self.equipment_list_updated.emit()
            
            # 显示操作结果
            if len(selected_ids) == 1:
                if success_count == 1:
                    self.status_bar.setText(f"设备 '{equipment.name}' 删除成功")
                else:
                    self.status_bar.setText(f"设备 '{equipment.name}' 删除失败")
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
        
        # 显示选中设备数量
        layout.addWidget(QLabel(f"将要删除 {len(selected_ids)} 个设备"))
        
        # 显示部分设备名称（最多显示5个）
        equipment_names = []
        for equipment_id in selected_ids[:5]:  # 只显示前5个
            equipment = self.process_manager.get_equipment(equipment_id)
            if equipment:
                equipment_names.append(f"• {equipment.name}")
        
        if equipment_names:
            names_text = "\n".join(equipment_names)
            if len(selected_ids) > 5:
                names_text += f"\n...等 {len(selected_ids)} 个设备"
            
            names_label = QLabel(names_text)
            layout.addWidget(names_label)
        
        # 警告信息
        warning_label = QLabel("⚠️ 此操作不可恢复！请确认")
        warning_label.setStyleSheet("color: red; font-weight: bold;")
        layout.addWidget(warning_label)
        
        # 确认复选框（防止误操作）
        confirm_checkbox = QCheckBox("我确认要删除这些设备")
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
    
    def add_equipment(self):
        dialog = EquipmentDialog(self)
        if dialog.exec() == QDialog.Accepted:
            equipment = dialog.get_equipment()
            if equipment and self.process_manager:
                try:
                    # 检查设备ID是否已存在
                    existing = self.process_manager.get_equipment(equipment.equipment_id)
                    if existing:
                        QMessageBox.warning(self, "警告", f"设备位号 '{equipment.equipment_id}' 已存在，请使用其他设备位号。")
                        return
                    
                    if self.process_manager.add_equipment(equipment):
                        # 延迟一小段时间再刷新，确保UI完全处理完
                        QTimer.singleShot(50, self.load_equipment)
                        self.equipment_list_updated.emit()
                        self.status_bar.setText(f"设备 '{equipment.name}' 添加成功")
                    else:
                        QMessageBox.warning(self, "错误", "设备添加失败")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"添加设备时发生错误:\n{str(e)}")

    def edit_equipment(self):
        """编辑设备"""
        if not self.equipment_table:
            return
            
        selected_row = self.equipment_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要编辑的设备")
            return
        
        # 设备ID在第0列
        equipment_id_item = self.equipment_table.item(selected_row, 0)
        if not equipment_id_item:
            QMessageBox.warning(self, "错误", "无法获取设备ID")
            return
        
        equipment_id = equipment_id_item.text()
        
        if not self.process_manager:
            return
        
        equipment = self.process_manager.get_equipment(equipment_id)
        if not equipment:
            QMessageBox.warning(self, "错误", f"设备未找到: {equipment_id}")
            return
        
        dialog = EquipmentDialog(self, equipment)
        if dialog.exec() == QDialog.Accepted:
            updated_equipment = dialog.get_equipment()
            if updated_equipment and self.process_manager:
                try:
                    # 检查设备ID是否被修改且是否已存在
                    if updated_equipment.equipment_id != equipment_id:
                        existing = self.process_manager.get_equipment(updated_equipment.equipment_id)
                        if existing:
                            QMessageBox.warning(self, "警告", f"设备位号 '{updated_equipment.equipment_id}' 已存在，请使用其他设备位号。")
                            return
                    
                    if self.process_manager.update_equipment(updated_equipment):
                        # 延迟刷新
                        QTimer.singleShot(50, self.load_equipment)
                        self.equipment_list_updated.emit()
                        self.status_bar.setText(f"设备 '{updated_equipment.name}' 更新成功")
                    else:
                        QMessageBox.warning(self, "错误", "设备更新失败")
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"更新设备时发生错误:\n{str(e)}")
                    
    def fix_table_display(self):
        """修复表格显示问题"""
        # 检查equipment_table是否存在
        if not hasattr(self, 'equipment_table') or self.equipment_table is None:
            return
            
        try:
            # 停止所有可能影响UI的操作
            self.equipment_table.setUpdatesEnabled(False)
            self.equipment_table.setSortingEnabled(False)
            
            # 强制清除和重置
            self.equipment_table.clearContents()
            self.equipment_table.setRowCount(0)
            
            # 如果有数据，重新填充
            if hasattr(self, 'current_equipment') and self.current_equipment:
                self.populate_table(self.current_equipment)
            
            # 重新启用
            self.equipment_table.setSortingEnabled(True)
            self.equipment_table.setUpdatesEnabled(True)
            
            # 强制重绘
            self.equipment_table.viewport().update()
            self.repaint()
            
            print("表格显示已修复")
            
        except Exception as e:
            print(f"修复表格显示时出错: {e}")
        
    def showEvent(self, event):
        """窗口显示事件"""
        super().showEvent(event)
        # 延迟一小段时间修复显示
        QTimer.singleShot(50, self.fix_table_display)
    
    def manage_name_mapping(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("设备名称对照表管理")
        dialog.setMinimumSize(800, 500)
        
        layout = QVBoxLayout(dialog)
        
        # 添加/修改区域
        add_layout = QHBoxLayout()
        add_layout.addWidget(QLabel("中文名称:"))
        chinese_input = QLineEdit()
        chinese_input.setPlaceholderText("输入中文名称")
        add_layout.addWidget(chinese_input)
        
        add_layout.addWidget(QLabel("英文名称:"))
        english_input = QLineEdit()
        english_input.setPlaceholderText("输入英文名称")
        add_layout.addWidget(english_input)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton("添加")
        add_btn.setToolTip("添加新的对照关系")
        
        update_btn = QPushButton("更新")
        update_btn.setToolTip("更新选中的对照关系")
        update_btn.setEnabled(False)
        
        clear_btn = QPushButton("清空")
        clear_btn.setToolTip("清空输入框")
        
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(update_btn)
        btn_layout.addWidget(clear_btn)
        btn_layout.addStretch()
        
        add_layout.addLayout(btn_layout)
        layout.addLayout(add_layout)
        
        # 对照表列表
        mapping_table = QTableWidget()
        mapping_table.setColumnCount(3)
        mapping_table.setHorizontalHeaderLabels(["ID", "中文名称", "英文名称"])
        mapping_table.horizontalHeader().setStretchLastSection(True)
        mapping_table.setSelectionBehavior(QTableWidget.SelectRows)
        mapping_table.setSelectionMode(QTableWidget.SingleSelection)
        mapping_table.setEditTriggers(QTableWidget.NoEditTriggers)  # 不允许直接编辑单元格
        
        # 设置列宽
        mapping_table.setColumnWidth(0, 50)
        mapping_table.setColumnWidth(1, 250)
        
        layout.addWidget(mapping_table)
        
        # 底部按钮
        bottom_btn_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("刷新")
        refresh_btn.setToolTip("刷新对照表")
        
        delete_btn = QPushButton("删除选中")
        delete_btn.setToolTip("删除选中的对照关系")
        delete_btn.setEnabled(False)
        
        import_btn = QPushButton("导入")
        import_btn.setToolTip("从文件导入对照表")
        
        export_btn = QPushButton("导出")
        export_btn.setToolTip("导出对照表到文件")
        
        bottom_btn_layout.addWidget(refresh_btn)
        bottom_btn_layout.addWidget(delete_btn)
        bottom_btn_layout.addStretch()
        bottom_btn_layout.addWidget(import_btn)
        bottom_btn_layout.addWidget(export_btn)
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.accept)
        bottom_btn_layout.addWidget(close_btn)
        
        layout.addLayout(bottom_btn_layout)
        
        # 加载对照表数据
        def load_mapping_table():
            try:
                if hasattr(self.data_manager, 'get_equipment_name_mapping'):
                    mapping = self.data_manager.get_equipment_name_mapping()
                else:
                    # 如果数据管理器没有该方法，使用模拟数据
                    mapping = {
                        "泵": "Pump",
                        "储罐": "Storage Tank",
                        "反应器": "Reactor",
                        "换热器": "Heat Exchanger",
                        "压缩机": "Compressor"
                    }
                
                mapping_table.setRowCount(len(mapping))
                
                sorted_items = sorted(mapping.items(), key=lambda x: x[0])  # 按中文名称排序
                
                for i, (chinese, english) in enumerate(sorted_items):
                    # ID列
                    mapping_table.setItem(i, 0, QTableWidgetItem(str(i+1)))
                    # 中文名称列
                    mapping_table.setItem(i, 1, QTableWidgetItem(chinese))
                    # 英文名称列
                    mapping_table.setItem(i, 2, QTableWidgetItem(english))
            except Exception as e:
                QMessageBox.warning(dialog, "加载错误", f"加载对照表时发生错误:\n{str(e)}")
        
        # 表格选择变化事件
        def on_table_selection_changed():
            selected_rows = set(index.row() for index in mapping_table.selectedIndexes())
            
            if len(selected_rows) == 1:
                # 选中一行，允许修改和删除
                row = list(selected_rows)[0]
                chinese_name = mapping_table.item(row, 1).text()
                english_name = mapping_table.item(row, 2).text()
                
                chinese_input.setText(chinese_name)
                english_input.setText(english_name)
                
                update_btn.setEnabled(True)
                delete_btn.setEnabled(True)
            else:
                # 未选中或选中多行，清空输入框并禁用更新按钮
                chinese_input.clear()
                english_input.clear()
                update_btn.setEnabled(False)
                delete_btn.setEnabled(False)
        
        # 添加对照关系
        def add_mapping():
            chinese = chinese_input.text().strip()
            english = english_input.text().strip()
            
            if not chinese:
                QMessageBox.warning(dialog, "输入错误", "中文名称不能为空")
                return
            
            if not english:
                QMessageBox.warning(dialog, "输入错误", "英文名称不能为空")
                return
            
            try:
                if hasattr(self.data_manager, 'add_equipment_name_mapping'):
                    # 检查是否已存在
                    existing_mapping = self.data_manager.get_equipment_name_mapping()
                    if chinese in existing_mapping:
                        reply = QMessageBox.question(
                            dialog, "确认覆盖",
                            f"中文名称 '{chinese}' 已存在，是否覆盖原有对照关系？",
                            QMessageBox.Yes | QMessageBox.No,
                            QMessageBox.No
                        )
                        if reply == QMessageBox.No:
                            return
                    
                    self.data_manager.add_equipment_name_mapping(chinese, english)
                    QMessageBox.information(dialog, "添加成功", "对照关系添加成功")
                else:
                    QMessageBox.warning(dialog, "功能不可用", "数据管理器不支持对照表管理")
                
                # 清空输入框并刷新表格
                chinese_input.clear()
                english_input.clear()
                load_mapping_table()
                
            except Exception as e:
                QMessageBox.critical(dialog, "添加失败", f"添加对照关系时发生错误:\n{str(e)}")
        
        # 更新对照关系
        def update_mapping():
            selected_rows = set(index.row() for index in mapping_table.selectedIndexes())
            
            if len(selected_rows) != 1:
                QMessageBox.warning(dialog, "选择错误", "请选择一行进行更新")
                return
            
            old_chinese = mapping_table.item(list(selected_rows)[0], 1).text()
            new_chinese = chinese_input.text().strip()
            new_english = english_input.text().strip()
            
            if not new_chinese:
                QMessageBox.warning(dialog, "输入错误", "中文名称不能为空")
                return
            
            if not new_english:
                QMessageBox.warning(dialog, "输入错误", "英文名称不能为空")
                return
            
            try:
                if hasattr(self.data_manager, 'add_equipment_name_mapping'):
                    # 先删除旧的，再添加新的
                    if hasattr(self.data_manager, 'remove_equipment_name_mapping'):
                        self.data_manager.remove_equipment_name_mapping(old_chinese)
                    
                    self.data_manager.add_equipment_name_mapping(new_chinese, new_english)
                    QMessageBox.information(dialog, "更新成功", "对照关系更新成功")
                else:
                    QMessageBox.warning(dialog, "功能不可用", "数据管理器不支持对照表管理")
                
                # 清空输入框并刷新表格
                chinese_input.clear()
                english_input.clear()
                update_btn.setEnabled(False)
                load_mapping_table()
                
            except Exception as e:
                QMessageBox.critical(dialog, "更新失败", f"更新对照关系时发生错误:\n{str(e)}")
        
        # 删除选中的对照关系
        def delete_selected_mapping():
            selected_rows = set(index.row() for index in mapping_table.selectedIndexes())
            
            if not selected_rows:
                QMessageBox.warning(dialog, "选择错误", "请先选择要删除的行")
                return
            
            # 确认删除
            row_count = len(selected_rows)
            reply = QMessageBox.question(
                dialog, "确认删除",
                f"确定要删除选中的 {row_count} 个对照关系吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                return
            
            try:
                if hasattr(self.data_manager, 'remove_equipment_name_mapping'):
                    # 从后往前删除，避免索引变化
                    for row in sorted(selected_rows, reverse=True):
                        chinese_name = mapping_table.item(row, 1).text()
                        self.data_manager.remove_equipment_name_mapping(chinese_name)
                    
                    QMessageBox.information(dialog, "删除成功", f"已成功删除 {row_count} 个对照关系")
                else:
                    QMessageBox.warning(dialog, "功能不可用", "数据管理器不支持对照表管理")
                
                # 清空输入框并刷新表格
                chinese_input.clear()
                english_input.clear()
                update_btn.setEnabled(False)
                delete_btn.setEnabled(False)
                load_mapping_table()
                
            except Exception as e:
                QMessageBox.critical(dialog, "删除失败", f"删除对照关系时发生错误:\n{str(e)}")
        
        # 清空输入框
        def clear_inputs():
            chinese_input.clear()
            english_input.clear()
            mapping_table.clearSelection()
            update_btn.setEnabled(False)
            delete_btn.setEnabled(False)
        
        # 从文件导入
        def import_mapping():
            file_path, _ = QFileDialog.getOpenFileName(
                dialog, "选择导入文件", "",
                "CSV文件 (*.csv);;文本文件 (*.txt);;所有文件 (*)"
            )
            
            if not file_path:
                return
            
            try:
                import_count = 0
                skip_count = 0
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        
                        parts = line.split(',')
                        if len(parts) >= 2:
                            chinese = parts[0].strip()
                            english = parts[1].strip()
                            
                            if chinese and english:
                                if hasattr(self.data_manager, 'add_equipment_name_mapping'):
                                    # 检查是否已存在
                                    existing_mapping = self.data_manager.get_equipment_name_mapping()
                                    if chinese not in existing_mapping:
                                        self.data_manager.add_equipment_name_mapping(chinese, english)
                                        import_count += 1
                                    else:
                                        skip_count += 1
                
                QMessageBox.information(
                    dialog, "导入完成",
                    f"导入完成！\n成功导入: {import_count} 条\n跳过重复: {skip_count} 条"
                )
                
                load_mapping_table()
                
            except Exception as e:
                QMessageBox.critical(dialog, "导入失败", f"导入对照表时发生错误:\n{str(e)}")
        
        # 导出到文件
        def export_mapping():
            file_path, _ = QFileDialog.getSaveFileName(
                dialog, "选择保存位置", "设备名称对照表.csv",
                "CSV文件 (*.csv);;文本文件 (*.txt);;所有文件 (*)"
            )
            
            if not file_path:
                return
            
            try:
                mapping = self.data_manager.get_equipment_name_mapping()
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("# 设备名称对照表\n")
                    f.write("# 格式: 中文名称,英文名称\n")
                    f.write("# 生成时间: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n\n")
                    
                    for chinese, english in sorted(mapping.items()):
                        f.write(f"{chinese},{english}\n")
                
                QMessageBox.information(
                    dialog, "导出成功",
                    f"对照表已成功导出到:\n{file_path}"
                )
                
            except Exception as e:
                QMessageBox.critical(dialog, "导出失败", f"导出对照表时发生错误:\n{str(e)}")
        
        # 表格双击事件
        def on_table_double_clicked(row, column):
            if column in [1, 2]:  # 双击中文或英文列
                chinese_name = mapping_table.item(row, 1).text()
                english_name = mapping_table.item(row, 2).text()
                
                chinese_input.setText(chinese_name)
                english_input.setText(english_name)
                
                update_btn.setEnabled(True)
                delete_btn.setEnabled(True)
        
        # 连接信号
        add_btn.clicked.connect(add_mapping)
        update_btn.clicked.connect(update_mapping)
        clear_btn.clicked.connect(clear_inputs)
        refresh_btn.clicked.connect(load_mapping_table)
        delete_btn.clicked.connect(delete_selected_mapping)
        import_btn.clicked.connect(import_mapping)
        export_btn.clicked.connect(export_mapping)
        
        mapping_table.itemSelectionChanged.connect(on_table_selection_changed)
        mapping_table.cellDoubleClicked.connect(on_table_double_clicked)
        
        # 初始加载数据
        load_mapping_table()
        
        dialog.exec()
        
    def import_equipment_by_template(self):
        """模板导入：导入符合模板格式的Excel文件"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择模板文件导入", "",
                "Excel模板文件 (*.xlsx);;所有文件 (*)"
            )
            
            if not file_path:
                return
            
            # 询问是否导入项目信息
            reply = QMessageBox.question(
                self, "导入项目信息",
                "是否同时导入文件中的项目信息？\n"
                "（项目名称、子项名称、文件编号等）",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Cancel:
                return
            
            import_project_info = (reply == QMessageBox.Yes)
            
            # 解析模板文件
            result = self.parse_template_file(file_path, import_project_info)
            
            if not result:
                QMessageBox.warning(self, "导入失败", "文件解析失败，请检查文件格式")
                return
            
            project_info, equipment_list = result
            
            if not equipment_list:
                QMessageBox.warning(self, "警告", "文件中没有找到设备数据")
                return
            
            # 显示预览对话框
            dialog = TemplateImportPreviewDialog(project_info, equipment_list, self)
            
            if dialog.exec() == QDialog.Accepted:
                # 获取用户选择的导入选项
                import_options = dialog.get_import_options()
                
                # 执行导入
                success_count = self.execute_template_import(
                    equipment_list, 
                    import_options
                )
                
                if success_count > 0:
                    QMessageBox.information(
                        self, "导入成功",
                        f"成功导入 {success_count} 个设备"
                    )
                    self.load_equipment()
                    self.equipment_list_updated.emit()
                else:
                    QMessageBox.warning(self, "导入失败", "没有设备被导入")
            
        except Exception as e:
            QMessageBox.critical(self, "导入错误", f"导入过程中发生错误:\n{str(e)}")
            import traceback
            traceback.print_exc()

    def parse_template_file(self, file_path, import_project_info=True):
        """解析模板格式的Excel文件"""
        return self.import_export.parse_template_file(file_path, import_project_info)

    def parse_project_info_from_sheet(self, ws):
        """从工作表中解析项目信息"""
        return self.import_export.parse_project_info_from_sheet(ws)

    def _normalize_header(self, header_text):
        """规范化表头文本"""
        return self.import_export._normalize_header(header_text)

    def _get_cell_value(self, ws, row, column_mapping, field_name, default=''):
        """获取单元格值"""
        return self.import_export._get_cell_value(ws, row, column_mapping, field_name, default)

    def _parse_number(self, value):
        """解析数值"""
        return self.import_export._parse_number(value)

    def _parse_temperature(self, value):
        """解析温度值"""
        return self.import_export._parse_temperature(value)

    def _parse_pressure(self, value):
        """解析压力值"""
        return self.import_export._parse_pressure(value)

    def execute_template_import(self, equipment_list, import_options):
        """执行模板导入"""
        return self.import_export.execute_template_import(equipment_list, import_options)

    def manage_templates(self):
        """管理模板"""
        dialog = QDialog(self)
        dialog.setWindowTitle("模板管理")
        dialog.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # 模板列表
        template_list = QListWidget()
        template_list.addItems([
            "ACME标准设备清单模板",
            "简化设备清单模板",
            "自定义模板1"
        ])
        
        layout.addWidget(QLabel("可用模板:"))
        layout.addWidget(template_list)
        
        # 模板信息
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setMaximumHeight(150)
        info_text.setPlainText(
            "ACME标准设备清单模板:\n"
            "- 包含完整的项目信息\n"
            "- 标准化的表头格式\n"
            "- 支持所有字段导入导出\n\n"
            "使用说明:\n"
            "1. 使用'模板导入'导入符合格式的文件\n"
            "2. 使用'模板导出'生成标准化文件\n"
            "3. 使用'创建模板'生成空白模板"
        )
        
        layout.addWidget(QLabel("模板说明:"))
        layout.addWidget(info_text)
        
        # 按钮
        btn_layout = QHBoxLayout()
        
        open_template_btn = QPushButton("打开模板文件夹")
        open_template_btn.clicked.connect(self.open_template_folder)
        btn_layout.addWidget(open_template_btn)
        
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(dialog.accept)  # 暂时简单处理
        btn_layout.addWidget(refresh_btn)
        
        btn_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        
        dialog.exec()

    def open_template_folder(self):
        """打开模板文件夹"""
        try:
            templates_dir = "templates"
            if not os.path.exists(templates_dir):
                os.makedirs(templates_dir)
            
            if sys.platform == "win32":
                os.startfile(templates_dir)
            elif sys.platform == "darwin":
                subprocess.run(["open", templates_dir])
            else:
                subprocess.run(["xdg-open", templates_dir])
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法打开模板文件夹:\n{str(e)}")

    def _local_search_equipment(self, search_term):
        """
        本地搜索设备 - 在本地内存中搜索设备数据
        不依赖 ProcessDesignManager 的搜索方法
        
        参数:
            search_term: 搜索关键词
        
        返回:
            匹配的设备列表
        """
        if not search_term or not self.process_manager:
            # 如果没有搜索词或没有数据管理器，返回所有设备
            return self.process_manager.get_all_equipment() if self.process_manager else []
        
        search_term = search_term.lower().strip()
        
        try:
            # 获取所有设备进行本地搜索
            all_equipment = self.process_manager.get_all_equipment()
            results = []
            
            for equipment in all_equipment:
                # 定义要搜索的字段列表
                search_fields = [
                    getattr(equipment, 'equipment_id', ''),      # 设备ID
                    getattr(equipment, 'name', ''),              # 设备名称
                    getattr(equipment, 'model', ''),             # 型号
                    getattr(equipment, 'manufacturer', ''),      # 制造商
                    getattr(equipment, 'specification', ''),     # 规格
                    getattr(equipment, 'location', ''),          # 安装位置
                    getattr(equipment, 'notes', ''),             # 备注
                    getattr(equipment, 'description_en', ''),    # 英文描述
                    getattr(equipment, 'unique_code', ''),       # 唯一编码
                    getattr(equipment, 'pid_dwg_no', ''),        # P&ID图号
                    getattr(equipment, 'material', ''),          # 材质
                    getattr(equipment, 'type', ''),              # 设备类型
                    getattr(equipment, 'status', ''),            # 状态
                ]
                
                # 检查是否有任何字段包含搜索词
                found = False
                for field in search_fields:
                    if field and search_term in str(field).lower():
                        found = True
                        break
                
                if found:
                    results.append(equipment)
            
            return results
            
        except Exception as e:
            print(f"本地搜索出错: {e}")
            return []

    def _exact_search(self, equipment_list, search_term):
        """精确搜索：搜索词完全包含在字段中"""
        results = []
        
        for equipment in equipment_list:
            # 检查关键字段
            key_fields = [
                getattr(equipment, 'equipment_id', ''),
                getattr(equipment, 'name', ''),
                getattr(equipment, 'model', ''),
                getattr(equipment, 'unique_code', ''),
            ]
            
            for field in key_fields:
                if field and search_term in str(field).lower():
                    results.append(equipment)
                    break
            
            # 如果关键字段没找到，检查其他字段
            if equipment not in results:
                other_fields = [
                    getattr(equipment, 'manufacturer', ''),
                    getattr(equipment, 'specification', ''),
                    getattr(equipment, 'location', ''),
                    getattr(equipment, 'description_en', ''),
                ]
                
                for field in other_fields:
                    if field and search_term in str(field).lower():
                        results.append(equipment)
                        break
        
        return results

    def _fuzzy_search(self, equipment_list, search_term):
        """模糊搜索：支持部分匹配和权重计算"""
        import difflib
        
        results = []
        
        for equipment in equipment_list:
            score = 0
            max_score = 0
            
            # 定义字段及其权重
            field_weights = [
                (getattr(equipment, 'equipment_id', ''), 3.0),      # 设备ID权重最高
                (getattr(equipment, 'name', ''), 2.5),              # 设备名称权重高
                (getattr(equipment, 'unique_code', ''), 2.5),       # 唯一编码权重高
                (getattr(equipment, 'model', ''), 2.0),             # 型号权重中等
                (getattr(equipment, 'description_en', ''), 1.5),    # 英文描述权重中等
                (getattr(equipment, 'manufacturer', ''), 1.0),      # 制造商权重低
                (getattr(equipment, 'specification', ''), 0.5),     # 规格权重低
            ]
            
            for field, weight in field_weights:
                if field:
                    field_str = str(field).lower()
                    # 计算相似度
                    similarity = difflib.SequenceMatcher(None, search_term, field_str).ratio()
                    # 部分匹配（搜索词包含在字段中）
                    contains = search_term in field_str
                    
                    # 计算得分
                    field_score = similarity * weight
                    if contains:
                        field_score *= 1.5  # 包含搜索词有加分
                    
                    max_score = max(max_score, field_score)
            
            # 如果得分超过阈值，加入结果
            if max_score > 0.3:  # 阈值可以调整
                results.append((equipment, max_score))
        
        # 按得分排序
        results.sort(key=lambda x: x[1], reverse=True)
        return [item[0] for item in results]
    
    def add_equipment_from_pfd(self, equipment_item):
        """从工艺流程图添加设备"""
        if not self.process_manager:
            return False
        
        try:
            # 检查设备是否已存在
            existing = self.process_manager.get_equipment(equipment_item.equipment_id)
            if existing:
                QMessageBox.warning(self, "警告", f"设备位号 '{equipment_item.equipment_id}' 已存在")
                return False
            
            # 添加设备
            if self.process_manager.add_equipment(equipment_item):
                # 延迟刷新
                QTimer.singleShot(50, self.load_equipment)
                self.equipment_list_updated.emit()
                self.status_bar.setText(f"设备 '{equipment_item.name}' 添加成功")
                return True
            else:
                return False
        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加设备时发生错误:\n{str(e)}")
            return False

    def refresh_equipment_list(self):
        """强制刷新设备列表（供外部模块调用）"""
        self.load_equipment()