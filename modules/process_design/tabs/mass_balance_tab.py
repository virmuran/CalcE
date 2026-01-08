# modules/process_design/tabs/mass_balance_tab.py
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
    QSizePolicy, QGridLayout, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt, Signal, QTimer, QThread, QSize
from PySide6.QtGui import QAction, QKeySequence, QClipboard, QFont

# 导入其他库
import csv
import json
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime


class MassBalanceTab(QWidget):
    """质量平衡计算标签页 - 优化布局，主要区域最大化"""
    
    calculation_completed = Signal(dict)  # 计算完成信号
    data_updated = Signal()  # 数据更新信号
    
    def __init__(self, data_manager=None, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.current_calculations = []  # 当前计算列表
        self.current_streams = []  # 当前流股数据
        self.current_results = {}  # 当前计算结果
        
        self.setup_ui()
        self.load_example_data()
        self.setup_shortcuts()
        
        # 添加延迟初始化
        QTimer.singleShot(100, self.finalize_initialization)
    
    def finalize_initialization(self):
        """完成初始化"""
        self.status_bar.setText("就绪 - 初始化完成")
    
    def setup_ui(self):
        """设置UI - 优化布局，主要区域最大化"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)
        
        # ========== 工具栏 - 固定高度 ==========
        self.setup_toolbar()
        main_layout.addWidget(self.toolbar)
        
        # ========== 计算选项区域 - 固定高度 ==========
        options_frame = QFrame()
        options_frame.setFixedHeight(60)
        options_layout = QHBoxLayout(options_frame)
        options_layout.setContentsMargins(8, 4, 8, 4)
        options_layout.setSpacing(10)
        
        # 计算类型选择
        calc_type_label = QLabel("计算类型:")
        self.calc_type_combo = QComboBox()
        self.calc_type_combo.addItems([
            "全流程质量平衡",
            "单元操作质量平衡", 
            "组分质量平衡",
            "反应器质量平衡",
            "分离器质量平衡"
        ])
        self.calc_type_combo.setFixedHeight(28)
        options_layout.addWidget(calc_type_label)
        options_layout.addWidget(self.calc_type_combo)
        
        # 基准选择
        basis_label = QLabel("基准:")
        self.basis_combo = QComboBox()
        self.basis_combo.addItems(["kg/h", "t/h", "lb/h", "mol/h"])
        self.basis_combo.setFixedHeight(28)
        options_layout.addWidget(basis_label)
        options_layout.addWidget(self.basis_combo)
        
        # 计算按钮
        self.calc_btn = QPushButton("⚡ 执行计算")
        self.calc_btn.setFixedHeight(28)
        self.calc_btn.setStyleSheet("font-weight: bold; background-color: #4CAF50; color: white;")
        self.calc_btn.clicked.connect(self.perform_calculation)
        options_layout.addWidget(self.calc_btn)
        
        # 重置按钮
        self.reset_btn = QPushButton("🔄 重置")
        self.reset_btn.setFixedHeight(28)
        self.reset_btn.clicked.connect(self.reset_calculation)
        options_layout.addWidget(self.reset_btn)
        
        options_layout.addStretch()
        
        main_layout.addWidget(options_frame)
        
        # ========== 主要区域：使用分割器，占据剩余空间 ==========
        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        
        # ========== 左侧：流股数据表格区域 - 使用拉伸因子 ==========
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(2)
        
        # 流股数据标题
        streams_label = QLabel("📊 流股数据")
        streams_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 5px 0;")
        left_layout.addWidget(streams_label)
        
        # 流股表格
        self.streams_table = QTableWidget()
        self.streams_table.setColumnCount(8)
        self.streams_table.setHorizontalHeaderLabels([
            "流股号", "名称", "类型", "温度(°C)", "压力(bar)", 
            "总流量", "组成", "备注"
        ])
        
        # 设置表头
        header = self.streams_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 流股号
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # 名称
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # 类型
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 温度
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # 压力
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # 总流量
        header.setSectionResizeMode(6, QHeaderView.Stretch)          # 组成
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # 备注
        
        # 启用排序
        self.streams_table.setSortingEnabled(True)
        self.streams_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        # 连接信号
        self.streams_table.itemChanged.connect(self.on_stream_data_changed)
        
        left_layout.addWidget(self.streams_table, 1)
        
        # 流股操作按钮区域
        stream_buttons_layout = QHBoxLayout()
        
        self.add_stream_btn = QPushButton("➕ 添加流股")
        self.add_stream_btn.setFixedHeight(30)
        self.add_stream_btn.clicked.connect(self.add_stream)
        stream_buttons_layout.addWidget(self.add_stream_btn)
        
        self.delete_stream_btn = QPushButton("🗑️ 删除流股")
        self.delete_stream_btn.setFixedHeight(30)
        self.delete_stream_btn.clicked.connect(self.delete_stream)
        stream_buttons_layout.addWidget(self.delete_stream_btn)
        
        self.import_streams_btn = QPushButton("📥 导入流股")
        self.import_streams_btn.setFixedHeight(30)
        self.import_streams_btn.clicked.connect(self.import_streams)
        stream_buttons_layout.addWidget(self.import_streams_btn)
        
        stream_buttons_layout.addStretch()
        
        left_layout.addLayout(stream_buttons_layout)
        
        splitter.addWidget(left_container)
        
        # ========== 右侧：计算结果显示区域 ==========
        right_container = QWidget()
        right_container.setMinimumWidth(350)
        right_container.setMaximumWidth(600)
        right_layout = QVBoxLayout(right_container)
        right_layout.setContentsMargins(5, 0, 5, 0)
        right_layout.setSpacing(2)
        
        # 计算结果标题
        results_label = QLabel("📈 计算结果")
        results_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 5px 0;")
        right_layout.addWidget(results_label)
        
        # 汇总信息框
        self.summary_group = QGroupBox("平衡汇总")
        self.summary_group.setMinimumHeight(120)
        summary_layout = QVBoxLayout(self.summary_group)
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(100)
        summary_layout.addWidget(self.summary_text)
        
        right_layout.addWidget(self.summary_group)
        
        # 详细结果表格
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels([
            "流股", "输入(kg/h)", "输出(kg/h)", "平衡误差(%)"
        ])
        
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setMinimumHeight(150)
        
        right_layout.addWidget(self.results_table, 1)
        
        # 图表显示区域
        chart_group = QGroupBox("可视化")
        chart_group.setMaximumHeight(180)
        chart_layout = QVBoxLayout(chart_group)
        
        self.chart_label = QLabel("📊 质量平衡图")
        self.chart_label.setAlignment(Qt.AlignCenter)
        self.chart_label.setStyleSheet("""
            QLabel {
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: #f9f9f9;
                padding: 20px;
            }
        """)
        chart_layout.addWidget(self.chart_label)
        
        # 图表类型选择
        chart_type_layout = QHBoxLayout()
        chart_type_layout.addWidget(QLabel("图表类型:"))
        
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["柱状图", "饼图", "桑基图", "趋势图"])
        self.chart_type_combo.setFixedHeight(24)
        chart_type_layout.addWidget(self.chart_type_combo)
        
        self.generate_chart_btn = QPushButton("生成图表")
        self.generate_chart_btn.setFixedHeight(24)
        self.generate_chart_btn.clicked.connect(self.generate_chart)
        chart_type_layout.addWidget(self.generate_chart_btn)
        
        chart_type_layout.addStretch()
        chart_layout.addLayout(chart_type_layout)
        
        right_layout.addWidget(chart_group)
        
        splitter.addWidget(right_container)
        
        # 设置分割器的初始大小比例
        splitter.setSizes([700, 300])
        
        # 将分割器添加到主布局，使用拉伸因子1，使其占据剩余空间
        main_layout.addWidget(splitter, 1)
        
        # ========== 底部：计算日志区域 - 固定高度 ==========
        log_frame = QFrame()
        log_frame.setFixedHeight(120)
        log_frame.setFrameStyle(QFrame.StyledPanel)
        log_layout = QVBoxLayout(log_frame)
        
        log_label = QLabel("📝 计算日志")
        log_label.setStyleSheet("font-weight: bold;")
        log_layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(80)
        log_layout.addWidget(self.log_text)
        
        main_layout.addWidget(log_frame)
        
        # ========== 状态栏 - 固定高度 ==========
        self.status_bar = QLabel()
        self.status_bar.setFixedHeight(25)
        self.status_bar.setText("就绪")
        main_layout.addWidget(self.status_bar)
        
        # 设置窗口的最小尺寸
        self.setMinimumSize(900, 700)
    
    def setup_toolbar(self):
        """设置工具栏"""
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(16, 16))
        self.toolbar.setFixedHeight(36)
        
        # 工具栏动作
        self.new_calc_action = QAction("新建计算", self)
        self.new_calc_action.triggered.connect(self.new_calculation)
        self.toolbar.addAction(self.new_calc_action)
        
        self.save_action = QAction("保存", self)
        self.save_action.triggered.connect(self.save_calculation)
        self.toolbar.addAction(self.save_action)
        
        self.load_action = QAction("加载", self)
        self.load_action.triggered.connect(self.load_calculation)
        self.toolbar.addAction(self.load_action)
        
        self.toolbar.addSeparator()
        
        self.export_action = QAction("导出", self)
        self.export_action.triggered.connect(self.export_results)
        self.toolbar.addAction(self.export_action)
        
        self.print_action = QAction("打印", self)
        self.print_action.triggered.connect(self.print_report)
        self.toolbar.addAction(self.print_action)
        
        self.toolbar.addSeparator()
        
        self.validate_action = QAction("验证", self)
        self.validate_action.triggered.connect(self.validate_data)
        self.toolbar.addAction(self.validate_action)
        
        self.optimize_action = QAction("优化", self)
        self.optimize_action.triggered.connect(self.optimize_balance)
        self.toolbar.addAction(self.optimize_action)
        
        self.toolbar.addSeparator()
        
        self.help_action = QAction("帮助", self)
        self.help_action.triggered.connect(self.show_help)
        self.toolbar.addAction(self.help_action)
    
    def setup_shortcuts(self):
        """设置快捷键"""
        # 计算快捷键
        self.calc_btn.setShortcut("F5")
        
        # 新建快捷键
        self.new_calc_action.setShortcut("Ctrl+N")
        
        # 保存快捷键
        self.save_action.setShortcut("Ctrl+S")
        
        # 导出快捷键
        self.export_action.setShortcut("Ctrl+E")
    
    def load_example_data(self):
        """加载示例数据"""
        # 示例流股数据
        self.current_streams = [
            {
                'id': 'S1', 'name': '原料进料', 'type': '输入', 
                'temp': 25.0, 'pressure': 1.0, 'flow': 1000.0,
                'composition': '甲醇:70%, 水:30%', 'notes': '新鲜原料'
            },
            {
                'id': 'S2', 'name': '反应器进料', 'type': '中间', 
                'temp': 150.0, 'pressure': 5.0, 'flow': 1000.0,
                'composition': '甲醇:70%, 水:30%', 'notes': ''
            },
            {
                'id': 'S3', 'name': '反应器出料', 'type': '中间', 
                'temp': 200.0, 'pressure': 4.5, 'flow': 950.0,
                'composition': '甲醇:50%, 水:25%, 产品:25%', 'notes': ''
            },
            {
                'id': 'S4', 'name': '产品流股', 'type': '输出', 
                'temp': 50.0, 'pressure': 1.0, 'flow': 237.5,
                'composition': '产品:100%', 'notes': '主产品'
            },
            {
                'id': 'S5', 'name': '废水流股', 'type': '输出', 
                'temp': 40.0, 'pressure': 1.0, 'flow': 712.5,
                'composition': '水:95%, 甲醇:5%', 'notes': '废水处理'
            }
        ]
        
        self.populate_streams_table()
    
    def populate_streams_table(self):
        """填充流股表格"""
        self.streams_table.blockSignals(True)
        self.streams_table.setSortingEnabled(False)
        
        try:
            self.streams_table.clearContents()
            self.streams_table.setRowCount(len(self.current_streams))
            
            for i, stream in enumerate(self.current_streams):
                self.streams_table.setItem(i, 0, QTableWidgetItem(stream['id']))
                self.streams_table.setItem(i, 1, QTableWidgetItem(stream['name']))
                self.streams_table.setItem(i, 2, QTableWidgetItem(stream['type']))
                self.streams_table.setItem(i, 3, QTableWidgetItem(f"{stream['temp']:.1f}"))
                self.streams_table.setItem(i, 4, QTableWidgetItem(f"{stream['pressure']:.2f}"))
                self.streams_table.setItem(i, 5, QTableWidgetItem(f"{stream['flow']:.2f}"))
                self.streams_table.setItem(i, 6, QTableWidgetItem(stream['composition']))
                self.streams_table.setItem(i, 7, QTableWidgetItem(stream['notes']))
            
            self.streams_table.setSortingEnabled(True)
            
        finally:
            self.streams_table.blockSignals(False)
        
        self.update_status("流股数据加载完成")
    
    def on_stream_data_changed(self, item):
        """流股数据变化事件"""
        row = item.row()
        col = item.column()
        
        if row < len(self.current_streams):
            value = item.text()
            
            if col == 0:
                self.current_streams[row]['id'] = value
            elif col == 1:
                self.current_streams[row]['name'] = value
            elif col == 2:
                self.current_streams[row]['type'] = value
            elif col == 3:
                try:
                    self.current_streams[row]['temp'] = float(value)
                except:
                    pass
            elif col == 4:
                try:
                    self.current_streams[row]['pressure'] = float(value)
                except:
                    pass
            elif col == 5:
                try:
                    self.current_streams[row]['flow'] = float(value)
                except:
                    pass
            elif col == 6:
                self.current_streams[row]['composition'] = value
            elif col == 7:
                self.current_streams[row]['notes'] = value
            
            self.add_log(f"流股 {self.current_streams[row]['id']} 数据已更新")
    
    def add_stream(self):
        """添加新流股"""
        stream_id = f"S{len(self.current_streams) + 1}"
        new_stream = {
            'id': stream_id,
            'name': f'新流股{len(self.current_streams) + 1}',
            'type': '中间',
            'temp': 25.0,
            'pressure': 1.0,
            'flow': 0.0,
            'composition': '',
            'notes': ''
        }
        
        self.current_streams.append(new_stream)
        self.populate_streams_table()
        self.add_log(f"添加新流股: {stream_id}")
    
    def delete_stream(self):
        """删除选中的流股"""
        selected_rows = self.streams_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "警告", "请先选择要删除的流股")
            return
        
        # 获取选中的流股ID
        stream_ids = []
        for row in selected_rows:
            item = self.streams_table.item(row.row(), 0)
            if item:
                stream_ids.append(item.text())
        
        # 确认删除
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除 {len(stream_ids)} 个流股吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 从后往前删除，避免索引问题
            for stream_id in stream_ids:
                for i, stream in enumerate(self.current_streams):
                    if stream['id'] == stream_id:
                        del self.current_streams[i]
                        self.add_log(f"删除流股: {stream_id}")
                        break
            
            self.populate_streams_table()
    
    def import_streams(self):
        """导入流股数据"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择导入文件", "",
            "Excel文件 (*.xlsx *.xls);;CSV文件 (*.csv);;JSON文件 (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            if file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            elif file_path.endswith('.csv'):
                df = pd.read_csv(file_path, encoding='utf-8')
            elif file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                df = pd.DataFrame(data)
            else:
                raise ValueError("不支持的文件格式")
            
            # 转换为流股数据格式
            streams = []
            for _, row in df.iterrows():
                stream = {
                    'id': str(row.get('id', f'S{len(streams)+1}')),
                    'name': str(row.get('name', '')),
                    'type': str(row.get('type', '中间')),
                    'temp': float(row.get('temp', 25.0)),
                    'pressure': float(row.get('pressure', 1.0)),
                    'flow': float(row.get('flow', 0.0)),
                    'composition': str(row.get('composition', '')),
                    'notes': str(row.get('notes', ''))
                }
                streams.append(stream)
            
            self.current_streams = streams
            self.populate_streams_table()
            self.add_log(f"从 {os.path.basename(file_path)} 导入 {len(streams)} 个流股")
            
        except Exception as e:
            QMessageBox.critical(self, "导入失败", f"导入文件时发生错误:\n{str(e)}")
    
    def perform_calculation(self):
        """执行质量平衡计算"""
        self.status_bar.setText("正在计算...")
        self.log_text.clear()
        
        try:
            # 解析流股数据
            input_streams = []
            output_streams = []
            internal_streams = []
            
            for stream in self.current_streams:
                if stream['type'] == '输入':
                    input_streams.append(stream)
                elif stream['type'] == '输出':
                    output_streams.append(stream)
                else:
                    internal_streams.append(stream)
            
            # 计算总输入和输出
            total_input = sum(stream['flow'] for stream in input_streams)
            total_output = sum(stream['flow'] for stream in output_streams)
            
            # 计算平衡误差
            if total_input > 0:
                error_percent = abs((total_output - total_input) / total_input) * 100
            else:
                error_percent = 0.0
            
            # 更新计算结果
            self.current_results = {
                'total_input': total_input,
                'total_output': total_output,
                'error_percent': error_percent,
                'input_streams': input_streams,
                'output_streams': output_streams,
                'internal_streams': internal_streams,
                'is_balanced': error_percent < 1.0  # 误差小于1%认为平衡
            }
            
            # 更新结果显示
            self.update_results_display()
            
            # 添加日志
            self.add_log(f"质量平衡计算完成")
            self.add_log(f"总输入: {total_input:.2f} kg/h")
            self.add_log(f"总输出: {total_output:.2f} kg/h")
            self.add_log(f"平衡误差: {error_percent:.4f}%")
            
            if self.current_results['is_balanced']:
                self.add_log("✅ 质量平衡良好")
                self.status_bar.setText("计算完成 - 质量平衡良好")
            else:
                self.add_log("⚠️ 质量不平衡，请检查流股数据")
                self.status_bar.setText("计算完成 - 质量不平衡")
            
            # 发出计算完成信号
            self.calculation_completed.emit(self.current_results)
            
        except Exception as e:
            self.status_bar.setText(f"计算失败: {str(e)}")
            QMessageBox.critical(self, "计算错误", f"计算过程中发生错误:\n{str(e)}")
    
    def update_results_display(self):
        """更新结果显示"""
        # 更新汇总信息
        summary = f"""
        <div style="font-size: 12pt; line-height: 1.6;">
        <b>质量平衡计算结果</b><br>
        <hr style="margin: 5px 0;">
        <table width="100%">
        <tr><td><b>总输入:</b></td><td align="right">{self.current_results['total_input']:.2f} kg/h</td></tr>
        <tr><td><b>总输出:</b></td><td align="right">{self.current_results['total_output']:.2f} kg/h</td></tr>
        <tr><td><b>平衡误差:</b></td><td align="right" style="color: {'green' if self.current_results['is_balanced'] else 'red'}">
            {self.current_results['error_percent']:.4f}%
        </td></tr>
        <tr><td><b>平衡状态:</b></td><td align="right">
            <span style="color: {'green' if self.current_results['is_balanced'] else 'red'}; font-weight: bold;">
            {'✅ 平衡' if self.current_results['is_balanced'] else '⚠️ 不平衡'}
            </span>
        </td></tr>
        </table>
        </div>
        """
        
        self.summary_text.setHtml(summary)
        
        # 更新详细结果表格
        self.results_table.blockSignals(True)
        
        try:
            self.results_table.clearContents()
            
            # 添加输入流股
            rows = []
            for stream in self.current_results['input_streams']:
                rows.append({
                    'stream': f"{stream['id']} - {stream['name']}",
                    'input': stream['flow'],
                    'output': 0.0,
                    'error': 0.0
                })
            
            # 添加输出流股
            for stream in self.current_results['output_streams']:
                rows.append({
                    'stream': f"{stream['id']} - {stream['name']}",
                    'input': 0.0,
                    'output': stream['flow'],
                    'error': 0.0
                })
            
            # 添加汇总行
            rows.append({
                'stream': '<b>总计</b>',
                'input': self.current_results['total_input'],
                'output': self.current_results['total_output'],
                'error': self.current_results['error_percent']
            })
            
            self.results_table.setRowCount(len(rows))
            
            for i, row_data in enumerate(rows):
                # 流股名称
                item = QTableWidgetItem()
                if i == len(rows) - 1:  # 最后一行是总计
                    item.setText(row_data['stream'])
                    font = QFont()
                    font.setBold(True)
                    item.setFont(font)
                else:
                    item.setText(row_data['stream'])
                self.results_table.setItem(i, 0, item)
                
                # 输入值
                if row_data['input'] > 0:
                    item = QTableWidgetItem(f"{row_data['input']:.2f}")
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.results_table.setItem(i, 1, item)
                
                # 输出值
                if row_data['output'] > 0:
                    item = QTableWidgetItem(f"{row_data['output']:.2f}")
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    self.results_table.setItem(i, 2, item)
                
                # 误差
                if i == len(rows) - 1:  # 只有总计行显示误差
                    item = QTableWidgetItem(f"{row_data['error']:.4f}")
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    
                    # 根据误差值设置颜色
                    if self.current_results['is_balanced']:
                        item.setForeground(Qt.green)
                    else:
                        item.setForeground(Qt.red)
                    
                    self.results_table.setItem(i, 3, item)
            
            # 设置表格自适应
            self.results_table.resizeRowsToContents()
            
        finally:
            self.results_table.blockSignals(False)
    
    def generate_chart(self):
        """生成图表（模拟）"""
        chart_type = self.chart_type_combo.currentText()
        
        # 模拟生成图表
        chart_html = f"""
        <div style="text-align: center;">
        <h4>{chart_type} - 质量平衡可视化</h4>
        <p style="color: #666; font-style: italic;">
        图表功能正在开发中...<br>
        当前显示模拟图表
        </p>
        <div style="background: linear-gradient(45deg, #4CAF50, #2196F3); 
                    height: 80px; border-radius: 5px; margin: 10px; 
                    display: flex; align-items: center; justify-content: center;">
        <span style="color: white; font-weight: bold; font-size: 16px;">
        输入: {self.current_results.get('total_input', 0):.1f} kg/h<br>
        输出: {self.current_results.get('total_output', 0):.1f} kg/h
        </span>
        </div>
        </div>
        """
        
        self.chart_label.setText(chart_html)
        self.add_log(f"生成 {chart_type} 图表")
    
    def reset_calculation(self):
        """重置计算"""
        reply = QMessageBox.question(
            self, "确认重置",
            "确定要重置所有流股数据吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.current_streams = []
            self.current_results = {}
            self.streams_table.clearContents()
            self.streams_table.setRowCount(0)
            self.summary_text.clear()
            self.results_table.clearContents()
            self.results_table.setRowCount(0)
            self.log_text.clear()
            self.status_bar.setText("已重置")
            self.add_log("系统已重置")
    
    def new_calculation(self):
        """新建计算"""
        self.reset_calculation()
        self.load_example_data()
        self.add_log("新建质量平衡计算")
    
    def save_calculation(self):
        """保存计算"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存计算", "mass_balance.json",
            "JSON文件 (*.json);;Excel文件 (*.xlsx)"
        )
        
        if not file_path:
            return
        
        try:
            data = {
                'streams': self.current_streams,
                'results': self.current_results,
                'timestamp': datetime.now().isoformat(),
                'calc_type': self.calc_type_combo.currentText(),
                'basis': self.basis_combo.currentText()
            }
            
            if file_path.endswith('.json'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            elif file_path.endswith('.xlsx'):
                # 保存流股数据到Excel
                df = pd.DataFrame(self.current_streams)
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Streams', index=False)
                    
                    # 保存结果数据
                    results_data = {
                        'Parameter': ['总输入', '总输出', '平衡误差', '平衡状态'],
                        'Value': [
                            f"{self.current_results.get('total_input', 0):.2f}",
                            f"{self.current_results.get('total_output', 0):.2f}",
                            f"{self.current_results.get('error_percent', 0):.4f}%",
                            '平衡' if self.current_results.get('is_balanced', False) else '不平衡'
                        ]
                    }
                    pd.DataFrame(results_data).to_excel(writer, sheet_name='Results', index=False)
            
            self.add_log(f"计算已保存到: {os.path.basename(file_path)}")
            self.status_bar.setText("计算已保存")
            
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"保存文件时发生错误:\n{str(e)}")
    
    def load_calculation(self):
        """加载计算"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "加载计算", "",
            "JSON文件 (*.json);;Excel文件 (*.xlsx)"
        )
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.current_streams = data.get('streams', [])
                self.current_results = data.get('results', {})
                
            elif file_path.endswith('.xlsx'):
                # 从Excel加载流股数据
                df = pd.read_excel(file_path, sheet_name='Streams')
                
                streams = []
                for _, row in df.iterrows():
                    stream = {
                        'id': str(row.get('id', '')),
                        'name': str(row.get('name', '')),
                        'type': str(row.get('type', '中间')),
                        'temp': float(row.get('temp', 25.0)),
                        'pressure': float(row.get('pressure', 1.0)),
                        'flow': float(row.get('flow', 0.0)),
                        'composition': str(row.get('composition', '')),
                        'notes': str(row.get('notes', ''))
                    }
                    streams.append(stream)
                
                self.current_streams = streams
                self.current_results = {}
            
            self.populate_streams_table()
            self.update_results_display()
            self.add_log(f"从 {os.path.basename(file_path)} 加载计算")
            
        except Exception as e:
            QMessageBox.critical(self, "加载失败", f"加载文件时发生错误:\n{str(e)}")
    
    def export_results(self):
        """导出结果"""
        if not self.current_results:
            QMessageBox.warning(self, "警告", "请先执行计算再导出结果")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出结果", "mass_balance_results.xlsx",
            "Excel文件 (*.xlsx);;CSV文件 (*.csv);;PDF文件 (*.pdf)"
        )
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.xlsx'):
                # 创建Excel文件
                with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                    # 写入流股数据
                    streams_df = pd.DataFrame(self.current_streams)
                    streams_df.to_excel(writer, sheet_name='流股数据', index=False)
                    
                    # 写入计算结果
                    results_data = []
                    for stream in self.current_results.get('input_streams', []):
                        results_data.append({
                            '流股': f"{stream['id']} - {stream['name']}",
                            '类型': '输入',
                            '流量(kg/h)': stream['flow'],
                            '温度(°C)': stream['temp'],
                            '压力(bar)': stream['pressure']
                        })
                    
                    for stream in self.current_results.get('output_streams', []):
                        results_data.append({
                            '流股': f"{stream['id']} - {stream['name']}",
                            '类型': '输出',
                            '流量(kg/h)': stream['flow'],
                            '温度(°C)': stream['temp'],
                            '压力(bar)': stream['pressure']
                        })
                    
                    results_df = pd.DataFrame(results_data)
                    results_df.to_excel(writer, sheet_name='计算结果', index=False)
                    
                    # 写入汇总信息
                    summary_data = {
                        '项目': ['总输入', '总输出', '平衡误差', '平衡状态'],
                        '数值': [
                            f"{self.current_results.get('total_input', 0):.2f} kg/h",
                            f"{self.current_results.get('total_output', 0):.2f} kg/h",
                            f"{self.current_results.get('error_percent', 0):.4f}%",
                            '平衡' if self.current_results.get('is_balanced', False) else '不平衡'
                        ]
                    }
                    summary_df = pd.DataFrame(summary_data)
                    summary_df.to_excel(writer, sheet_name='汇总', index=False)
                
                self.add_log(f"结果已导出到: {os.path.basename(file_path)}")
                
            elif file_path.endswith('.csv'):
                # 导出为CSV
                results_data = []
                for stream in self.current_streams:
                    results_data.append({
                        'Stream_ID': stream['id'],
                        'Name': stream['name'],
                        'Type': stream['type'],
                        'Flow_kg_h': stream['flow'],
                        'Temp_C': stream['temp'],
                        'Pressure_bar': stream['pressure'],
                        'Composition': stream['composition'],
                        'Notes': stream['notes']
                    })
                
                df = pd.DataFrame(results_data)
                df.to_csv(file_path, index=False, encoding='utf-8')
                
                self.add_log(f"结果已导出到CSV文件")
            
            elif file_path.endswith('.pdf'):
                # PDF导出（模拟）
                QMessageBox.information(
                    self, "PDF导出",
                    "PDF导出功能正在开发中。\n请先导出为Excel或CSV格式。"
                )
                return
            
            self.status_bar.setText("结果已导出")
            QMessageBox.information(self, "导出成功", f"结果已成功导出到:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出文件时发生错误:\n{str(e)}")
    
    def print_report(self):
        """打印报告"""
        if not self.current_results:
            QMessageBox.warning(self, "警告", "请先执行计算再打印报告")
            return
        
        # 创建报告内容
        report_html = f"""
        <html>
        <head>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
            h2 {{ color: #34495e; margin-top: 20px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 10px 0; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .summary {{ background-color: #f9f9f9; padding: 15px; border-radius: 5px; }}
            .balanced {{ color: green; font-weight: bold; }}
            .unbalanced {{ color: red; font-weight: bold; }}
        </style>
        </head>
        <body>
        <h1>质量平衡计算报告</h1>
        <p><b>计算时间:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><b>计算类型:</b> {self.calc_type_combo.currentText()}</p>
        <p><b>基准单位:</b> {self.basis_combo.currentText()}</p>
        
        <h2>平衡汇总</h2>
        <div class="summary">
        <p><b>总输入:</b> {self.current_results.get('total_input', 0):.2f} kg/h</p>
        <p><b>总输出:</b> {self.current_results.get('total_output', 0):.2f} kg/h</p>
        <p><b>平衡误差:</b> {self.current_results.get('error_percent', 0):.4f}%</p>
        <p><b>平衡状态:</b> 
            <span class="{'balanced' if self.current_results.get('is_balanced', False) else 'unbalanced'}">
            {'✅ 平衡' if self.current_results.get('is_balanced', False) else '⚠️ 不平衡'}
            </span>
        </p>
        </div>
        
        <h2>流股数据</h2>
        <table>
        <tr>
            <th>流股号</th><th>名称</th><th>类型</th><th>温度(°C)</th>
            <th>压力(bar)</th><th>流量(kg/h)</th><th>组成</th>
        </tr>
        """
        
        # 添加流股数据行
        for stream in self.current_streams:
            report_html += f"""
            <tr>
                <td>{stream['id']}</td>
                <td>{stream['name']}</td>
                <td>{stream['type']}</td>
                <td>{stream['temp']:.1f}</td>
                <td>{stream['pressure']:.2f}</td>
                <td>{stream['flow']:.2f}</td>
                <td>{stream['composition']}</td>
            </tr>
            """
        
        report_html += """
        </table>
        
        <h2>计算结果</h2>
        <table>
        <tr><th>流股</th><th>输入(kg/h)</th><th>输出(kg/h)</th></tr>
        """
        
        # 添加计算结果行
        total_input = 0
        total_output = 0
        
        for stream in self.current_results.get('input_streams', []):
            report_html += f"""
            <tr>
                <td>{stream['id']} - {stream['name']}</td>
                <td>{stream['flow']:.2f}</td>
                <td></td>
            </tr>
            """
            total_input += stream['flow']
        
        for stream in self.current_results.get('output_streams', []):
            report_html += f"""
            <tr>
                <td>{stream['id']} - {stream['name']}</td>
                <td></td>
                <td>{stream['flow']:.2f}</td>
            </tr>
            """
            total_output += stream['flow']
        
        # 添加总计行
        report_html += f"""
        <tr style="font-weight: bold; background-color: #f2f2f2;">
            <td>总计</td>
            <td>{total_input:.2f}</td>
            <td>{total_output:.2f}</td>
        </tr>
        </table>
        
        <p style="margin-top: 30px; font-size: 10px; color: #777;">
        报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
        TofuApp - 工艺设计系统
        </p>
        </body>
        </html>
        """
        
        # 显示打印预览对话框
        from PySide6.QtPrintSupport import QPrintDialog, QPrinter
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec() == QDialog.Accepted:
            # 这里可以添加实际的打印逻辑
            QMessageBox.information(self, "打印", "打印功能正在开发中，请使用导出功能。")
    
    def validate_data(self):
        """验证数据"""
        errors = []
        warnings = []
        
        # 检查流股数据
        for i, stream in enumerate(self.current_streams):
            if not stream['id']:
                errors.append(f"流股 {i+1}: 流股号不能为空")
            
            if stream['flow'] < 0:
                errors.append(f"流股 {stream['id']}: 流量不能为负数")
            
            if stream['temp'] < -273.15:
                errors.append(f"流股 {stream['id']}: 温度不能低于绝对零度")
        
        # 检查输入输出流股
        input_streams = [s for s in self.current_streams if s['type'] == '输入']
        output_streams = [s for s in self.current_streams if s['type'] == '输出']
        
        if not input_streams:
            warnings.append("没有输入流股")
        if not output_streams:
            warnings.append("没有输出流股")
        
        # 显示验证结果
        if errors or warnings:
            message = ""
            if errors:
                message += "<b>错误:</b><br>" + "<br>".join(f"❌ {e}" for e in errors) + "<br><br>"
            if warnings:
                message += "<b>警告:</b><br>" + "<br>".join(f"⚠️ {w}" for w in warnings)
            
            QMessageBox.warning(self, "数据验证", message)
        else:
            QMessageBox.information(self, "数据验证", "✅ 所有数据验证通过")
    
    def optimize_balance(self):
        """优化质量平衡"""
        if not self.current_results:
            QMessageBox.warning(self, "警告", "请先执行计算再优化")
            return
        
        # 简单的平衡优化算法
        total_input = self.current_results['total_input']
        total_output = self.current_results['total_output']
        
        if abs(total_input - total_output) > 0.01:
            # 计算调整因子
            if total_input > 0:
                adjustment_factor = total_output / total_input
                
                # 调整所有流股
                for stream in self.current_streams:
                    if stream['type'] == '输入':
                        stream['flow'] *= adjustment_factor
                
                self.populate_streams_table()
                self.perform_calculation()
                self.add_log(f"平衡优化完成，调整因子: {adjustment_factor:.4f}")
                
                QMessageBox.information(
                    self, "优化完成",
                    f"已自动调整输入流股以达到质量平衡\n"
                    f"调整因子: {adjustment_factor:.4f}"
                )
            else:
                QMessageBox.warning(self, "优化失败", "总输入为零，无法优化")
        else:
            QMessageBox.information(self, "优化", "质量已经平衡，无需优化")
    
    def add_log(self, message):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        # 限制日志行数
        lines = self.log_text.toPlainText().split('\n')
        if len(lines) > 100:
            self.log_text.setPlainText('\n'.join(lines[-100:]))
    
    def update_status(self, message):
        """更新状态栏"""
        self.status_bar.setText(message)
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """
        <h3>质量平衡计算使用说明</h3>
        
        <h4>主要功能：</h4>
        <ul>
            <li><b>添加流股</b>: 点击"添加流股"按钮，填写流股数据</li>
            <li><b>编辑流股</b>: 直接在表格中编辑流股数据</li>
            <li><b>执行计算</b>: 点击"执行计算"按钮进行质量平衡计算</li>
            <li><b>优化平衡</b>: 使用优化功能自动调整流股以达到质量平衡</li>
        </ul>
        
        <h4>流股类型说明：</h4>
        <ul>
            <li><b>输入</b>: 进入系统的物料流股</li>
            <li><b>输出</b>: 离开系统的物料流股</li>
            <li><b>中间</b>: 系统内部的流股，不参与总平衡计算</li>
        </ul>
        
        <h4>计算原理：</h4>
        <p>质量平衡基于质量守恒定律：<br>
        <b>总输入 = 总输出 + 积累</b><br>
        对于稳态过程，积累为零，因此总输入应等于总输出。</p>
        
        <h4>快捷键：</h4>
        <ul>
            <li><b>F5</b>: 执行计算</li>
            <li><b>Ctrl+N</b>: 新建计算</li>
            <li><b>Ctrl+S</b>: 保存计算</li>
            <li><b>Ctrl+E</b>: 导出结果</li>
        </ul>
        
        <h4>平衡标准：</h4>
        <p>当平衡误差小于1%时，系统认为质量平衡良好。</p>
        """
        
        QMessageBox.information(self, "质量平衡计算帮助", help_text)


# 导出函数，用于动态导入
def import_mass_balance_tab():
    """导入MassBalanceTab类"""
    return MassBalanceTab