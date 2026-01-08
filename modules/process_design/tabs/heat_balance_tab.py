# modules/process_design/tabs/heat_balance_tab.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QFormLayout, QLineEdit, QTextEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QDoubleSpinBox, QSpinBox, QCheckBox, QSplitter, QFrame,
    QToolBar, QTabWidget, QDialog, QDialogButtonBox, QProgressDialog,
    QFileDialog, QToolButton, QMenu, QApplication,
    QScrollArea, QProgressBar, QListWidget, QListWidgetItem  # 添加所有需要的控件
)
from PySide6.QtCore import Qt, Signal, QSize, QTimer
from PySide6.QtGui import QAction, QKeySequence, QClipboard
import math
import pandas as pd
import json
import os

class HeatBalanceTab(QWidget):
    """热平衡计算标签页 - 现代化紧凑风格"""
    
    # 定义信号
    calculation_completed = Signal(dict)
    export_requested = Signal(str)
    
    def __init__(self, data_manager=None):
        super().__init__()
        self.data_manager = data_manager
        self.results = {}
        self.history = []  # 计算历史记录
        self.current_calc_index = -1
        
        self.setup_ui()
        self.setup_shortcuts()
    
    def setup_ui(self):
        """设置UI - 紧凑现代化风格"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)  # 减少外边距
        main_layout.setSpacing(2)  # 减少控件间距
        
        # 1. 工具栏 - 固定高度
        self.setup_toolbar()
        self.toolbar.setFixedHeight(36)  # 固定工具栏高度
        main_layout.addWidget(self.toolbar)
        
        # 2. 主内容区域 - 使用分割器，占据最大空间
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setChildrenCollapsible(False)  # 防止子部件被压缩消失
        
        # 左侧：输入参数区域（固定宽度，自适应高度）
        input_widget = QWidget()
        input_widget.setMinimumWidth(350)  # 最小宽度
        input_widget.setMaximumWidth(500)  # 最大宽度
        input_layout = QVBoxLayout(input_widget)
        input_layout.setContentsMargins(5, 5, 5, 5)
        input_layout.setSpacing(8)
        
        # 参数输入标题
        input_title = QLabel("热平衡计算参数")
        input_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2C3E50; margin: 5px 0;")
        input_layout.addWidget(input_title)
        
        # 参数输入表单（使用拉伸因子，填满剩余空间）
        self.setup_parameter_form()
        input_layout.addWidget(self.parameter_form, 1)  # 拉伸因子为1，占据剩余空间
        
        main_splitter.addWidget(input_widget)
        
        # 右侧：结果区域（可拉伸，占据最大空间）
        result_widget = QWidget()
        result_layout = QVBoxLayout(result_widget)
        result_layout.setContentsMargins(5, 5, 5, 5)
        result_layout.setSpacing(8)
        
        # 结果区域标题
        result_title = QLabel("热平衡计算结果")
        result_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #2C3E50; margin: 5px 0;")
        result_layout.addWidget(result_title)
        
        # 上部：关键指标卡片（固定高度）
        self.setup_key_metrics(result_layout)
        
        # 中部：详细结果表格（可拉伸，占据最大空间）
        table_group = QGroupBox("详细计算结果")
        table_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #34495E;
            }
        """)
        table_layout = QVBoxLayout(table_group)
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(4)
        self.result_table.setHorizontalHeaderLabels(["项目", "数值", "单位", "说明"])
        self.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.result_table.horizontalHeader().setStretchLastSection(True)
        self.result_table.setAlternatingRowColors(True)
        
        # 设置列宽
        self.result_table.setColumnWidth(0, 120)
        self.result_table.setColumnWidth(1, 100)
        self.result_table.setColumnWidth(2, 80)
        
        table_layout.addWidget(self.result_table)
        result_layout.addWidget(table_group, 1)  # 拉伸因子为1，占据剩余空间
        
        # 下部：效率分析和历史记录（固定高度）
        bottom_splitter = QSplitter(Qt.Horizontal)
        bottom_splitter.setChildrenCollapsible(False)
        
        # 效率分析面板
        efficiency_widget = self.create_efficiency_panel()
        bottom_splitter.addWidget(efficiency_widget)
        
        # 历史记录面板
        history_widget = self.create_history_panel()
        bottom_splitter.addWidget(history_widget)
        
        # 设置底部面板高度
        bottom_splitter.setMaximumHeight(180)
        result_layout.addWidget(bottom_splitter)
        
        main_splitter.addWidget(result_widget)
        
        # 设置分割器初始比例
        main_splitter.setSizes([350, 650])  # 输入区域350，结果区域650
        
        main_layout.addWidget(main_splitter, 1)  # 主分割器占据最大空间
        
        # 3. 状态栏 - 固定高度
        self.status_bar = QLabel("就绪")
        self.status_bar.setFixedHeight(24)
        self.status_bar.setStyleSheet("""
            QLabel {
                background-color: #ECF0F1;
                color: #7F8C8D;
                padding: 2px 10px;
                border-top: 1px solid #BDC3C7;
                font-size: 11px;
            }
        """)
        main_layout.addWidget(self.status_bar)
    
    def setup_toolbar(self):
        """设置工具栏 - 紧凑版本"""
        self.toolbar = QToolBar()
        self.toolbar.setIconSize(QSize(16, 16))
        
        # 计算按钮组
        self.calc_action = QAction("计算 (F5)", self)
        self.calc_action.triggered.connect(self.calculate_heat_balance)
        self.toolbar.addAction(self.calc_action)
        
        self.toolbar.addSeparator()
        
        # 数据操作组
        self.save_action = QAction("保存 (Ctrl+S)", self)
        self.save_action.triggered.connect(self.save_calculation)
        self.toolbar.addAction(self.save_action)
        
        self.load_action = QAction("加载", self)
        self.load_action.triggered.connect(self.load_calculation)
        self.toolbar.addAction(self.load_action)
        
        self.export_action = QAction("导出", self)
        self.export_action.triggered.connect(self.export_results)
        self.toolbar.addAction(self.export_action)
        
        self.toolbar.addSeparator()
        
        # 操作组
        self.reset_action = QAction("重置 (Ctrl+R)", self)
        self.reset_action.triggered.connect(self.reset_inputs)
        self.toolbar.addAction(self.reset_action)
        
        self.copy_action = QAction("复制 (Ctrl+C)", self)
        self.copy_action.triggered.connect(self.copy_results)
        self.toolbar.addAction(self.copy_action)
        
        self.toolbar.addSeparator()
        
        # 历史导航
        self.prev_action = QAction("上一个", self)
        self.prev_action.triggered.connect(self.prev_calculation)
        self.toolbar.addAction(self.prev_action)
        
        self.next_action = QAction("下一个", self)
        self.next_action.triggered.connect(self.next_calculation)
        self.toolbar.addAction(self.next_action)
        
        self.toolbar.addSeparator()
        
        # 帮助
        self.help_action = QAction("帮助", self)
        self.help_action.triggered.connect(self.show_help)
        self.toolbar.addAction(self.help_action)
    
    def setup_parameter_form(self):
        """设置参数输入表单 - 自适应高度版本"""
        self.parameter_form = QWidget()
        form_layout = QVBoxLayout(self.parameter_form)
        form_layout.setContentsMargins(0, 0, 0, 0)  # 移除内边距
        form_layout.setSpacing(0)
        
        # 使用滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 禁用水平滚动条
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
        """)
        
        scroll_content = QWidget()
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(8, 8, 8, 8)  # 内容的内边距
        content_layout.setSpacing(10)
        
        # 1. 基本信息组
        basic_group = QGroupBox("基本信息")
        basic_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
                margin-top: 0px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #34495E;
            }
        """)
        basic_layout = QFormLayout(basic_group)
        basic_layout.setSpacing(8)
        basic_layout.setContentsMargins(10, 15, 10, 10)  # 减少内边距
        
        self.system_name = QLineEdit("反应器 R-101")
        self.system_name.setPlaceholderText("系统名称")
        basic_layout.addRow("系统名称:", self.system_name)
        
        self.system_type = QComboBox()
        self.system_type.addItems(["反应系统", "换热系统", "蒸馏系统", "冷却系统"])
        basic_layout.addRow("系统类型:", self.system_type)
        
        content_layout.addWidget(basic_group)
        
        # 2. 温度参数组
        temp_group = QGroupBox("温度参数 (°C)")
        temp_group.setStyleSheet(basic_group.styleSheet())
        temp_layout = QFormLayout(temp_group)
        temp_layout.setSpacing(8)
        temp_layout.setContentsMargins(10, 15, 10, 10)
        
        self.temp_in = QDoubleSpinBox()
        self.temp_in.setRange(-273.15, 2000)
        self.temp_in.setValue(25.0)
        self.temp_in.setSingleStep(5.0)
        temp_layout.addRow("入口温度:", self.temp_in)
        
        self.temp_out = QDoubleSpinBox()
        self.temp_out.setRange(-273.15, 2000)
        self.temp_out.setValue(150.0)
        self.temp_out.setSingleStep(5.0)
        temp_layout.addRow("出口温度:", self.temp_out)
        
        # 温差显示
        self.temp_diff_label = QLabel("0.0 °C")
        temp_layout.addRow("温差:", self.temp_diff_label)
        
        # 连接温度变化信号
        self.temp_in.valueChanged.connect(self.update_temp_diff)
        self.temp_out.valueChanged.connect(self.update_temp_diff)
        
        content_layout.addWidget(temp_group)
        
        # 3. 物料参数组
        material_group = QGroupBox("物料参数")
        material_group.setStyleSheet(basic_group.styleSheet())
        material_layout = QFormLayout(material_group)
        material_layout.setSpacing(8)
        material_layout.setContentsMargins(10, 15, 10, 10)
        
        self.mass_flow = QDoubleSpinBox()
        self.mass_flow.setRange(0, 1000000)
        self.mass_flow.setValue(1000.0)
        self.mass_flow.setSuffix(" kg/h")
        self.mass_flow.setSingleStep(100.0)
        material_layout.addRow("质量流量:", self.mass_flow)
        
        self.heat_capacity = QDoubleSpinBox()
        self.heat_capacity.setRange(0, 100)
        self.heat_capacity.setValue(4.18)
        self.heat_capacity.setSuffix(" kJ/(kg·K)")
        self.heat_capacity.setSingleStep(0.1)
        material_layout.addRow("比热容:", self.heat_capacity)
        
        content_layout.addWidget(material_group)
        
        # 4. 热损失参数组
        loss_group = QGroupBox("热损失参数")
        loss_group.setStyleSheet(basic_group.styleSheet())
        loss_layout = QFormLayout(loss_group)
        loss_layout.setSpacing(8)
        loss_layout.setContentsMargins(10, 15, 10, 10)
        
        self.heat_loss_percent = QDoubleSpinBox()
        self.heat_loss_percent.setRange(0, 100)
        self.heat_loss_percent.setValue(5.0)
        self.heat_loss_percent.setSuffix(" %")
        self.heat_loss_percent.setSingleStep(0.5)
        loss_layout.addRow("热损失:", self.heat_loss_percent)
        
        content_layout.addWidget(loss_group)
        
        # 5. 高级选项组（可折叠）
        self.advanced_group = QGroupBox("高级选项")
        self.advanced_group.setCheckable(True)
        self.advanced_group.setChecked(False)
        self.advanced_group.setStyleSheet(basic_group.styleSheet())
        advanced_layout = QFormLayout(self.advanced_group)
        advanced_layout.setSpacing(8)
        advanced_layout.setContentsMargins(10, 15, 10, 10)
        
        self.auto_calc_check = QCheckBox("自动计算")
        self.auto_calc_check.setChecked(False)
        self.auto_calc_check.stateChanged.connect(self.on_auto_calc_changed)
        advanced_layout.addRow("", self.auto_calc_check)
        
        self.heat_type = QComboBox()
        self.heat_type.addItems(["显热", "潜热", "反应热"])
        advanced_layout.addRow("热流类型:", self.heat_type)
        
        # 添加更多高级选项
        self.ambient_temp = QDoubleSpinBox()
        self.ambient_temp.setRange(-50, 100)
        self.ambient_temp.setValue(25.0)
        self.ambient_temp.setSuffix(" °C")
        advanced_layout.addRow("环境温度:", self.ambient_temp)
        
        self.pressure = QDoubleSpinBox()
        self.pressure.setRange(0.1, 10.0)
        self.pressure.setValue(1.0)
        self.pressure.setSuffix(" atm")
        advanced_layout.addRow("系统压力:", self.pressure)
        
        content_layout.addWidget(self.advanced_group)
        
        # 添加一个拉伸弹簧，让内容填满空间
        content_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        form_layout.addWidget(scroll_area)
    
    def setup_key_metrics(self, layout):
        """设置关键指标显示区域"""
        metrics_widget = QWidget()
        metrics_layout = QHBoxLayout(metrics_widget)
        metrics_layout.setSpacing(10)
        
        # 效率指标卡片
        efficiency_card = self.create_metric_card("热效率", "0%", "#27AE60", "系统热效率")
        metrics_layout.addWidget(efficiency_card)
        
        # 输入热量卡片
        input_card = self.create_metric_card("输入热量", "0 kW", "#3498DB", "总输入热量")
        metrics_layout.addWidget(input_card)
        
        # 输出热量卡片
        output_card = self.create_metric_card("输出热量", "0 kW", "#E74C3C", "有效输出热量")
        metrics_layout.addWidget(output_card)
        
        # 热损失卡片
        loss_card = self.create_metric_card("热损失", "0 kW", "#F39C12", "系统热损失")
        metrics_layout.addWidget(loss_card)
        
        layout.addWidget(metrics_widget)
    
    def create_metric_card(self, title, value, color, tooltip):
        """创建指标卡片"""
        card = QFrame()
        card.setFrameStyle(QFrame.Box | QFrame.Raised)
        card.setLineWidth(1)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #BDC3C7;
                border-radius: 6px;
                padding: 8px;
            }}
        """)
        card.setToolTip(tooltip)
        
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(4)
        
        # 标题
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; color: #7F8C8D; font-size: 12px;")
        title_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title_label)
        
        # 值
        value_label = QLabel(value)
        value_label.setStyleSheet(f"font-weight: bold; color: {color}; font-size: 18px;")
        value_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(value_label)
        
        return card
    
    def create_efficiency_panel(self):
        """创建效率分析面板"""
        panel = QGroupBox("效率分析")
        panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #34495E;
            }
        """)
        layout = QVBoxLayout(panel)
        
        # 效率显示
        efficiency_display = QHBoxLayout()
        
        self.efficiency_gauge = QLabel("0%")
        self.efficiency_gauge.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #7F8C8D;
                min-width: 80px;
                text-align: center;
            }
        """)
        efficiency_display.addWidget(self.efficiency_gauge)
        
        # 效率等级
        level_layout = QVBoxLayout()
        self.efficiency_level = QLabel("未计算")
        self.efficiency_level.setStyleSheet("font-weight: bold; font-size: 14px;")
        level_layout.addWidget(self.efficiency_level)
        
        self.distribution_text = QLabel("热量分布: 未计算")
        self.distribution_text.setStyleSheet("font-size: 11px; color: #7F8C8D;")
        level_layout.addWidget(self.distribution_text)
        
        efficiency_display.addLayout(level_layout)
        layout.addLayout(efficiency_display)
        
        # 效率指示条
        self.efficiency_indicator = QProgressBar()
        self.efficiency_indicator.setRange(0, 100)
        self.efficiency_indicator.setValue(0)
        self.efficiency_indicator.setTextVisible(True)
        self.efficiency_indicator.setStyleSheet("""
            QProgressBar {
                border: 1px solid #BDC3C7;
                border-radius: 3px;
                text-align: center;
                height: 16px;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 #E74C3C, stop:0.5 #F1C40F, stop:1 #27AE60
                );
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.efficiency_indicator)
        
        return panel
    
    def create_history_panel(self):
        """创建历史记录面板"""
        panel = QGroupBox("计算历史")
        panel.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #BDC3C7;
                border-radius: 4px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #34495E;
            }
        """)
        layout = QVBoxLayout(panel)
        
        self.history_list = QListWidget()
        self.history_list.setMaximumHeight(120)
        self.history_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #BDC3C7;
                border-radius: 3px;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.history_list)
        
        # 历史操作按钮
        history_btns = QHBoxLayout()
        prev_btn = QPushButton("上一个")
        prev_btn.clicked.connect(self.prev_calculation)
        prev_btn.setMaximumWidth(80)
        history_btns.addWidget(prev_btn)
        
        next_btn = QPushButton("下一个")
        next_btn.clicked.connect(self.next_calculation)
        next_btn.setMaximumWidth(80)
        history_btns.addWidget(next_btn)
        
        history_btns.addStretch()
        layout.addLayout(history_btns)
        
        return panel
    
    def setup_shortcuts(self):
        """设置快捷键"""
        # 计算快捷键
        self.calc_action.setShortcut(QKeySequence("F5"))
        
        # 复制快捷键
        self.copy_action.setShortcut(QKeySequence.Copy)
        
        # 保存快捷键
        self.save_action.setShortcut(QKeySequence.Save)
        
        # 重置快捷键
        self.reset_action.setShortcut("Ctrl+R")
        
        # 历史导航快捷键
        self.prev_action.setShortcut("Ctrl+Left")
        self.next_action.setShortcut("Ctrl+Right")
    
    def update_temp_diff(self):
        """更新温差显示"""
        temp_diff = self.temp_out.value() - self.temp_in.value()
        self.temp_diff_label.setText(f"{temp_diff:.1f} °C")
        
        # 自动计算（如果启用）
        if self.auto_calc_check.isChecked():
            self.auto_calculate()
    
    def auto_calculate(self):
        """自动计算（防抖处理）"""
        if hasattr(self, '_calc_timer'):
            self._calc_timer.stop()
        
        self._calc_timer = QTimer()
        self._calc_timer.setSingleShot(True)
        self._calc_timer.timeout.connect(self.calculate_heat_balance)
        self._calc_timer.start(500)  # 500ms防抖
    
    def on_auto_calc_changed(self, state):
        """自动计算选项变化"""
        if state == Qt.Checked:
            # 连接所有输入控件的值变化信号
            self.temp_in.valueChanged.connect(self.auto_calculate)
            self.temp_out.valueChanged.connect(self.auto_calculate)
            self.mass_flow.valueChanged.connect(self.auto_calculate)
            self.heat_capacity.valueChanged.connect(self.auto_calculate)
            self.heat_loss_percent.valueChanged.connect(self.auto_calculate)
        else:
            # 断开信号
            try:
                self.temp_in.valueChanged.disconnect(self.auto_calculate)
                self.temp_out.valueChanged.disconnect(self.auto_calculate)
                self.mass_flow.valueChanged.disconnect(self.auto_calculate)
                self.heat_capacity.valueChanged.disconnect(self.auto_calculate)
                self.heat_loss_percent.valueChanged.disconnect(self.auto_calculate)
            except:
                pass
    
    def calculate_heat_balance(self):
        """计算热平衡"""
        try:
            # 获取输入参数
            temp_diff = self.temp_out.value() - self.temp_in.value()
            mass_flow = self.mass_flow.value()
            cp = self.heat_capacity.value()
            
            # 计算显热
            sensible_heat = mass_flow * cp * temp_diff / 3600  # kW
            
            # 总输入热量
            total_heat_input = sensible_heat
            
            # 计算热损失
            heat_loss_percent = self.heat_loss_percent.value() / 100
            heat_loss = total_heat_input * heat_loss_percent
            
            # 输出热量
            total_heat_output = total_heat_input - heat_loss
            
            # 热效率
            if total_heat_input > 0:
                efficiency = (total_heat_output / total_heat_input) * 100
            else:
                efficiency = 0
            
            # 存储结果
            self.results = {
                'system_name': self.system_name.text(),
                'system_type': self.system_type.currentText(),
                'heat_input': total_heat_input,
                'heat_output': total_heat_output,
                'heat_loss': heat_loss,
                'efficiency': efficiency,
                'sensible_heat': sensible_heat,
                'temp_in': self.temp_in.value(),
                'temp_out': self.temp_out.value(),
                'temp_diff': temp_diff,
                'mass_flow': mass_flow,
                'heat_capacity': cp,
                'timestamp': pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # 保存到历史记录
            self.history.append(self.results.copy())
            self.current_calc_index = len(self.history) - 1
            self.update_history_display()
            
            # 更新UI
            self.update_results_display()
            
            # 发出信号
            self.calculation_completed.emit(self.results)
            
            self.status_bar.setText(f"计算完成 - 效率: {efficiency:.1f}%")
            
        except Exception as e:
            QMessageBox.critical(self, "计算错误", f"计算过程中发生错误:\n{str(e)}")
            self.status_bar.setText("计算错误")
    
    def update_results_display(self):
        """更新结果显示"""
        if not self.results:
            return
        
        # 更新效率仪表盘
        efficiency = self.results['efficiency']
        self.efficiency_gauge.setText(f"{efficiency:.1f}%")
        self.efficiency_indicator.setValue(int(efficiency))
        
        # 设置效率颜色和等级
        if efficiency >= 80:
            color = "#27AE60"
            level = "优秀"
        elif efficiency >= 60:
            color = "#F39C12"
            level = "良好"
        else:
            color = "#E74C3C"
            level = "待改进"
        
        self.efficiency_gauge.setStyleSheet(f"""
            QLabel {{
                font-size: 28px;
                font-weight: bold;
                color: {color};
                min-width: 80px;
                text-align: center;
            }}
        """)
        self.efficiency_level.setText(level)
        self.efficiency_level.setStyleSheet(f"font-weight: bold; font-size: 14px; color: {color};")
        
        # 更新热量分布
        if self.results['heat_input'] > 0:
            input_pct = 100
            output_pct = (self.results['heat_output'] / self.results['heat_input']) * 100
            loss_pct = (self.results['heat_loss'] / self.results['heat_input']) * 100
            
            self.distribution_text.setText(
                f"输入: {input_pct:.0f}% | 输出: {output_pct:.1f}% | 损失: {loss_pct:.1f}%"
            )
        
        # 更新详细表格
        self.result_table.setRowCount(8)
        
        items = [
            ("系统名称", self.results['system_name'], "", "系统标识"),
            ("系统类型", self.results['system_type'], "", "系统分类"),
            ("显热", f"{self.results['sensible_heat']:.2f}", "kW", "温度变化引起的热量"),
            ("总输入热量", f"{self.results['heat_input']:.2f}", "kW", "输入系统的总热量"),
            ("热损失", f"{self.results['heat_loss']:.2f}", "kW", "散失到环境的热量"),
            ("有效输出热量", f"{self.results['heat_output']:.2f}", "kW", "系统输出的可用热量"),
            ("温差", f"{self.results['temp_diff']:.1f}", "°C", "温度变化"),
            ("热效率", f"{self.results['efficiency']:.2f}", "%", "系统热效率")
        ]
        
        for i, (item, value, unit, note) in enumerate(items):
            self.result_table.setItem(i, 0, QTableWidgetItem(item))
            self.result_table.setItem(i, 1, QTableWidgetItem(value))
            self.result_table.setItem(i, 2, QTableWidgetItem(unit))
            self.result_table.setItem(i, 3, QTableWidgetItem(note))
        
        # 调整列宽
        self.result_table.resizeColumnsToContents()
    
    def update_history_display(self):
        """更新历史记录显示"""
        self.history_list.clear()
        
        if not self.history:
            return
        
        for i, calc in enumerate(self.history[-10:]):  # 显示最近10条记录
            idx = len(self.history) - 10 + i if len(self.history) > 10 else i
            calc_data = self.history[idx]
            
            timestamp = calc_data.get('timestamp', '')[-8:]  # 只显示时间部分
            item_text = f"[{timestamp}] {calc_data['system_name']}: {calc_data['efficiency']:.1f}%"
            
            item = QListWidgetItem(item_text)
            if idx == self.current_calc_index:
                item.setBackground(Qt.lightGray)
            self.history_list.addItem(item)
    
    def prev_calculation(self):
        """上一个计算"""
        if self.current_calc_index > 0:
            self.current_calc_index -= 1
            self.results = self.history[self.current_calc_index].copy()
            self.update_results_display()
            self.update_history_display()
            self.status_bar.setText(f"加载历史记录 {self.current_calc_index + 1}/{len(self.history)}")
    
    def next_calculation(self):
        """下一个计算"""
        if self.current_calc_index < len(self.history) - 1:
            self.current_calc_index += 1
            self.results = self.history[self.current_calc_index].copy()
            self.update_results_display()
            self.update_history_display()
            self.status_bar.setText(f"加载历史记录 {self.current_calc_index + 1}/{len(self.history)}")
    
    def reset_inputs(self):
        """重置输入"""
        # 重置所有输入控件
        self.system_name.setText("反应器 R-101")
        self.system_type.setCurrentIndex(0)
        
        self.temp_in.setValue(25.0)
        self.temp_out.setValue(150.0)
        self.mass_flow.setValue(1000.0)
        self.heat_capacity.setValue(4.18)
        self.heat_loss_percent.setValue(5.0)
        
        self.auto_calc_check.setChecked(False)
        self.heat_type.setCurrentIndex(0)
        
        # 清除结果
        self.results = {}
        self.result_table.setRowCount(0)
        
        # 重置效率显示
        self.efficiency_gauge.setText("0%")
        self.efficiency_gauge.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #7F8C8D;
                min-width: 80px;
                text-align: center;
            }
        """)
        self.efficiency_level.setText("未计算")
        self.efficiency_level.setStyleSheet("font-weight: bold; font-size: 14px; color: #7F8C8D;")
        self.distribution_text.setText("热量分布: 未计算")
        self.efficiency_indicator.setValue(0)
        
        # 清空历史列表
        self.history_list.clear()
        
        self.status_bar.setText("已重置所有输入")
    
    def save_calculation(self):
        """保存计算结果"""
        if not self.results:
            QMessageBox.warning(self, "无法保存", "请先进行计算")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存计算结果", 
            f"heat_balance_{self.results['system_name'].replace(' ', '_')}.json",
            "JSON文件 (*.json);;文本文件 (*.txt);;Excel文件 (*.xlsx)"
        )
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.results, f, indent=2, ensure_ascii=False)
            elif file_path.endswith('.txt'):
                with open(file_path, 'w', encoding='utf-8') as f:
                    for key, value in self.results.items():
                        f.write(f"{key}: {value}\n")
            elif file_path.endswith('.xlsx'):
                df = pd.DataFrame([self.results])
                df.to_excel(file_path, index=False)
            
            self.status_bar.setText(f"结果已保存到: {os.path.basename(file_path)}")
            
        except Exception as e:
            QMessageBox.critical(self, "保存失败", f"保存结果时发生错误:\n{str(e)}")
            self.status_bar.setText("保存失败")
    
    def load_calculation(self):
        """加载计算结果"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "加载计算结果", 
            "", "JSON文件 (*.json);;Excel文件 (*.xlsx)"
        )
        
        if not file_path:
            return
        
        try:
            if file_path.endswith('.json'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    self.results = json.load(f)
            elif file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path)
                self.results = df.iloc[0].to_dict()
            
            # 更新UI
            self.update_results_display()
            self.status_bar.setText(f"已加载: {os.path.basename(file_path)}")
            
        except Exception as e:
            QMessageBox.critical(self, "加载失败", f"加载结果时发生错误:\n{str(e)}")
            self.status_bar.setText("加载失败")
    
    def export_results(self):
        """导出结果"""
        if not self.results:
            QMessageBox.warning(self, "无法导出", "请先进行计算")
            return
        
        # 导出选项对话框
        dialog = ExportDialog(self)
        if dialog.exec() == QDialog.Accepted:
            options = dialog.get_export_options()
            format_type = options['format']
            
            # 构建导出数据
            export_data = {
                'summary': {
                    '系统名称': self.results['system_name'],
                    '系统类型': self.results['system_type'],
                    '总输入热量': f"{self.results['heat_input']:.2f} kW",
                    '总输出热量': f"{self.results['heat_output']:.2f} kW",
                    '热损失': f"{self.results['heat_loss']:.2f} kW",
                    '热效率': f"{self.results['efficiency']:.2f} %",
                    '计算时间': self.results.get('timestamp', '')
                },
                'details': self.results
            }
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, "导出结果", 
                f"heat_balance_export.{format_type}",
                f"{format_type.upper()}文件 (*.{format_type})"
            )
            
            if not file_path:
                return
            
            try:
                if format_type == 'json':
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, indent=2, ensure_ascii=False)
                elif format_type == 'xlsx':
                    with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                        summary_df = pd.DataFrame([export_data['summary']])
                        summary_df.to_excel(writer, sheet_name='摘要', index=False)
                        
                        details_df = pd.DataFrame([export_data['details']])
                        details_df.to_excel(writer, sheet_name='详细数据', index=False)
                elif format_type == 'csv':
                    df = pd.DataFrame([export_data['summary']])
                    df.to_csv(file_path, index=False, encoding='utf-8')
                
                self.status_bar.setText(f"结果已导出: {os.path.basename(file_path)}")
                
            except Exception as e:
                QMessageBox.critical(self, "导出失败", f"导出结果时发生错误:\n{str(e)}")
    
    def copy_results(self):
        """复制结果到剪贴板"""
        if not self.results:
            return
        
        # 构建复制文本
        text = f"热平衡计算结果\n{'='*40}\n"
        text += f"系统名称: {self.results['system_name']}\n"
        text += f"系统类型: {self.results['system_type']}\n"
        text += f"总输入热量: {self.results['heat_input']:.2f} kW\n"
        text += f"总输出热量: {self.results['heat_output']:.2f} kW\n"
        text += f"热损失: {self.results['heat_loss']:.2f} kW\n"
        text += f"热效率: {self.results['efficiency']:.2f} %\n"
        text += f"计算时间: {self.results.get('timestamp', '')}\n"
        
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        self.status_bar.setText("结果已复制到剪贴板")
    
    def show_help(self):
        """显示帮助信息"""
        QMessageBox.information(self, "热平衡计算帮助", 
            "热平衡计算说明：\n\n"
            "1. 输入基本参数：系统名称、类型、温度、流量等\n"
            "2. 点击'计算'按钮或按F5进行计算\n"
            "3. 查看右侧的结果表格和效率分析\n"
            "4. 可使用历史记录查看之前的计算结果\n\n"
            "快捷键：\n"
            "• F5: 计算\n"
            "• Ctrl+S: 保存\n"
            "• Ctrl+C: 复制结果\n"
            "• Ctrl+R: 重置输入\n"
            "• Ctrl+Left/Right: 历史导航")


class ExportDialog(QDialog):
    """导出选项对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("导出选项")
        self.setMinimumWidth(300)
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        # 导出格式
        self.format_combo = QComboBox()
        self.format_combo.addItems(["json", "xlsx", "csv"])
        form_layout.addRow("导出格式:", self.format_combo)
        
        layout.addLayout(form_layout)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_export_options(self):
        """获取导出选项"""
        return {
            'format': self.format_combo.currentText()
        }