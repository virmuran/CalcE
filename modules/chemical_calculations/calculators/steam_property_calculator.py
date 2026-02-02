from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGroupBox, QTextEdit, QComboBox, QMessageBox, QFrame,
    QScrollArea, QDialog, QSpinBox, QButtonGroup, QGridLayout,
    QFileDialog, QDialogButtonBox, QSizePolicy, QRadioButton, QStackedWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QDoubleValidator
import math
import re
from datetime import datetime


class SteamPropertyCalculator(QWidget):
    """水蒸气性质查询（与压降计算模块保持相同UI风格）"""
    
    # 信号：用于传递计算结果
    calculation_completed = Signal(dict)
    
    def __init__(self, parent=None, data_manager=None):
        super().__init__(parent)
        
        # 使用传入的数据管理器或创建新的
        if data_manager is not None:
            self.data_manager = data_manager
        else:
            self.init_data_manager()
        
        # 初始化状态变量
        self.current_mode = "saturation"  # 默认饱和状态
        self.parameter1_type = "pressure"  # 参数1类型
        self.parameter2_type = "temperature"  # 参数2类型
        
        # 初始化单位
        self.pressure_unit = "MPa"
        self.temperature_unit = "°C"
        self.density_unit = "kg/m³"
        self.enthalpy_unit = "kJ/kg"
        self.entropy_unit = "kJ/(kg·K)"
        
        self.setup_ui()
        self.setup_mode_dependencies()
        self.initialize_values()
        self.setup_connections()
    
    def init_data_manager(self):
        """初始化数据管理器"""
        try:
            from data_manager import DataManager
            self.data_manager = DataManager.get_instance()
            print("使用共享的数据管理器实例")
        except Exception as e:
            print(f"数据管理器初始化失败: {e}")
            self.data_manager = None
    
    def setup_ui(self):
        """设置UI界面 - 保持与压降计算模块完全相同的风格"""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # ==================== 左侧：输入参数区域 ====================
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(15)
        
        # 1. 说明文本
        description = QLabel(
            "查询水蒸气在不同状态下的热力学性质，包括密度、比焓、比熵等。支持饱和状态和其他状态查询。"
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 5px;")
        left_layout.addWidget(description)
        
        # 2. 查询模式选择
        mode_group = QGroupBox("查询模式")
        mode_group.setStyleSheet(self.get_groupbox_style())
        mode_layout = QHBoxLayout(mode_group)
        
        self.mode_button_group = QButtonGroup(self)
        self.mode_buttons = {}
        
        modes = [
            ("饱和状态", "查询饱和状态下的水蒸气性质"),
            ("其他状态", "查询已知两个参数的水蒸气性质")
        ]
        
        for i, (mode_name, tooltip) in enumerate(modes):
            btn = QPushButton(mode_name)
            btn.setCheckable(True)
            btn.setToolTip(tooltip)
            btn.setMinimumWidth(120)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #ecf0f1;
                    border: 1px solid #bdc3c7;
                    border-radius: 4px;
                    padding: 8px;
                    text-align: center;
                    color: black;
                }
                QPushButton:checked {
                    background-color: #3498db;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #d5dbdb;
                    color: green;
                }
            """)
            self.mode_button_group.addButton(btn, i)
            mode_layout.addWidget(btn)
            self.mode_buttons[mode_name] = btn
        
        # 默认选择第一个
        self.mode_buttons["饱和状态"].setChecked(True)
        self.mode_button_group.buttonClicked.connect(self.on_mode_button_clicked)
        
        mode_layout.addStretch()
        left_layout.addWidget(mode_group)
        
        # 3. 参数输入区域 - 使用堆栈窗口切换不同模式
        self.input_stack = QStackedWidget()
        
        # 饱和状态页面
        self.saturation_page = self.create_saturation_page()
        
        # 其他状态页面
        self.other_page = self.create_other_page()
        
        self.input_stack.addWidget(self.saturation_page)
        self.input_stack.addWidget(self.other_page)
        
        left_layout.addWidget(self.input_stack)
        
        # 4. 计算按钮
        self.calculate_btn = QPushButton("🧮 查询水蒸气性质")
        self.calculate_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.calculate_btn.clicked.connect(self.calculate_steam_properties)
        self.calculate_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.calculate_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219955;
            }
        """)
        self.calculate_btn.setMinimumHeight(50)
        left_layout.addWidget(self.calculate_btn)
        
        # 5. 下载按钮布局
        download_layout = QHBoxLayout()
        
        self.download_txt_btn = QPushButton("📄 下载计算书(TXT)")
        self.download_txt_btn.clicked.connect(self.download_txt_report)
        self.download_txt_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.download_txt_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219653;
            }
        """)
        
        self.download_pdf_btn = QPushButton("📊 下载计算书(PDF)")
        self.download_pdf_btn.clicked.connect(self.download_pdf_report)
        self.download_pdf_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.download_pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        download_layout.addWidget(self.download_txt_btn)
        download_layout.addWidget(self.download_pdf_btn)
        left_layout.addLayout(download_layout)
        
        # 6. 在底部添加拉伸因子
        left_layout.addStretch()
        
        # ==================== 右侧：结果显示区域 ====================
        right_widget = QWidget()
        right_widget.setMinimumWidth(300)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)
        
        # 结果显示
        self.result_group = QGroupBox("📤 计算结果")
        self.result_group.setStyleSheet(self.get_groupbox_style())
        result_layout = QVBoxLayout(self.result_group)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.result_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ecf0f1;
                border-radius: 6px;
                padding: 12px;
                background-color: #f8f9fa;
                min-height: 600px;
                font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif;
                font-size: 12px;
                line-height: 1.4;
            }
        """)
        result_layout.addWidget(self.result_text)
        
        right_layout.addWidget(self.result_group)
        
        # ==================== 添加左右布局 ====================
        main_layout.addWidget(left_widget, 2)  # 左侧占2/3权重
        main_layout.addWidget(right_widget, 1)  # 右侧占1/3权重
    
    def create_saturation_page(self):
        """创建饱和状态输入页面 - 简化布局，去掉双层框"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        
        # 输入组 - 不再使用GroupBox，直接使用GridLayout
        input_widget = QWidget()
        input_layout = QGridLayout(input_widget)
        input_layout.setVerticalSpacing(12)
        input_layout.setHorizontalSpacing(10)
        
        # 设置列宽比例
        input_layout.setColumnStretch(0, 1)  # 标签列
        input_layout.setColumnStretch(1, 2)  # 输入框列
        input_layout.setColumnStretch(2, 2)  # 下拉菜单列
        
        # 标签样式
        label_style = "QLabel { font-weight: bold; padding-right: 10px; }"
        
        row = 0
        
        # 已知参数选择 - 改为按钮组
        known_label = QLabel("已知参数:")
        known_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        known_label.setStyleSheet(label_style)
        input_layout.addWidget(known_label, row, 0)
        
        # 创建按钮组
        known_widget = QWidget()
        known_btn_layout = QHBoxLayout(known_widget)
        known_btn_layout.setSpacing(5)
        known_btn_layout.setContentsMargins(0, 0, 0, 0)
        
        self.sat_known_button_group = QButtonGroup(self)
        self.sat_known_buttons = {}
        
        known_options = ["压力 P", "温度 T"]
        
        for i, option in enumerate(known_options):
            btn = QPushButton(option)
            btn.setCheckable(True)
            btn.setMinimumWidth(80)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #ecf0f1;
                    border: 1px solid #bdc3c7;
                    border-radius: 4px;
                    padding: 6px;
                    text-align: center;
                    color: black;
                }
                QPushButton:checked {
                    background-color: #3498db;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #d5dbdb;
                }
            """)
            self.sat_known_button_group.addButton(btn, i)
            known_btn_layout.addWidget(btn)
            self.sat_known_buttons[option] = btn
        
        # 默认选择第一个
        self.sat_known_buttons["压力 P"].setChecked(True)
        self.sat_known_button_group.buttonClicked.connect(self.on_sat_known_button_clicked)
        
        known_btn_layout.addStretch()
        input_layout.addWidget(known_widget, row, 1, 1, 2)
        
        row += 1
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #bdc3c7;")
        input_layout.addWidget(separator, row, 0, 1, 3)
        
        row += 1
        
        # 参数输入
        self.sat_param1_label = QLabel("压力 (MPa):")
        self.sat_param1_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.sat_param1_label.setStyleSheet(label_style)
        input_layout.addWidget(self.sat_param1_label, row, 0)
        
        self.sat_param1_input = QLineEdit()
        self.sat_param1_input.setPlaceholderText("例如: 0.6")
        self.sat_param1_input.setValidator(QDoubleValidator(0.001, 30.0, 6))
        self.sat_param1_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        input_layout.addWidget(self.sat_param1_input, row, 1)
        
        self.sat_param1_combo = QComboBox()
        self.setup_pressure_options(self.sat_param1_combo)
        self.sat_param1_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.sat_param1_combo.currentTextChanged.connect(
            lambda text: self.on_param_combo_changed(text, self.sat_param1_input)
        )
        input_layout.addWidget(self.sat_param1_combo, row, 2)
        
        row += 1
        
        # 干度输入
        dryness_label = QLabel("干度 (0-1):")
        dryness_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        dryness_label.setStyleSheet(label_style)
        input_layout.addWidget(dryness_label, row, 0)
        
        self.dryness_input = QLineEdit()
        self.dryness_input.setPlaceholderText("例如: 0.9")
        self.dryness_input.setValidator(QDoubleValidator(0.0, 1.0, 3))
        self.dryness_input.setText("1.0")  # 默认干饱和蒸汽
        self.dryness_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        input_layout.addWidget(self.dryness_input, row, 1)
        
        # 干度说明
        self.dryness_hint = QLabel("干度=0:饱和水，干度=1:干饱和蒸汽")
        self.dryness_hint.setStyleSheet("color: #7f8c8d; font-style: italic;")
        self.dryness_hint.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        input_layout.addWidget(self.dryness_hint, row, 2)
        
        layout.addWidget(input_widget)
        layout.addStretch()
        
        return widget
    
    def create_other_page(self):
        """创建其他状态输入页面 - 简化布局，去掉双层框"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)
        
        # 输入组 - 不再使用GroupBox，直接使用GridLayout
        input_widget = QWidget()
        input_layout = QGridLayout(input_widget)
        input_layout.setVerticalSpacing(12)
        input_layout.setHorizontalSpacing(10)
        
        # 设置列宽比例
        input_layout.setColumnStretch(0, 1)  # 标签列
        input_layout.setColumnStretch(1, 2)  # 输入框列
        input_layout.setColumnStretch(2, 2)  # 下拉菜单列
        
        # 标签样式
        label_style = "QLabel { font-weight: bold; padding-right: 10px; }"
        
        row = 0
        
        # 已知参数组合选择 - 改为按钮组
        known_label = QLabel("已知参数组合:")
        known_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        known_label.setStyleSheet(label_style)
        input_layout.addWidget(known_label, row, 0)
        
        # 创建按钮组
        known_widget = QWidget()
        known_btn_layout = QVBoxLayout(known_widget)
        known_btn_layout.setSpacing(5)
        known_btn_layout.setContentsMargins(0, 0, 0, 0)
        
        self.other_known_button_group = QButtonGroup(self)
        self.other_known_buttons = {}
        
        known_options = [
            "压力 P 和温度 T",
            "压力 P 和比焓 H",
            "压力 P 和比熵 S"
        ]
        
        for i, option in enumerate(known_options):
            btn = QPushButton(option)
            btn.setCheckable(True)
            btn.setMinimumHeight(30)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #ecf0f1;
                    border: 1px solid #bdc3c7;
                    border-radius: 4px;
                    padding: 6px;
                    text-align: left;
                    color: black;
                }
                QPushButton:checked {
                    background-color: #3498db;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #d5dbdb;
                }
            """)
            self.other_known_button_group.addButton(btn, i)
            known_btn_layout.addWidget(btn)
            self.other_known_buttons[option] = btn
        
        # 默认选择第一个
        self.other_known_buttons["压力 P 和温度 T"].setChecked(True)
        self.other_known_button_group.buttonClicked.connect(self.on_other_known_button_clicked)
        
        input_layout.addWidget(known_widget, row, 1, 1, 2)
        
        row += 1
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #bdc3c7;")
        input_layout.addWidget(separator, row, 0, 1, 3)
        
        row += 1
        
        # 参数1输入
        self.other_param1_label = QLabel("压力 (MPa):")
        self.other_param1_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.other_param1_label.setStyleSheet(label_style)
        input_layout.addWidget(self.other_param1_label, row, 0)
        
        self.other_param1_input = QLineEdit()
        self.other_param1_input.setPlaceholderText("例如: 0.6")
        self.other_param1_input.setValidator(QDoubleValidator(0.001, 30.0, 6))
        self.other_param1_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        input_layout.addWidget(self.other_param1_input, row, 1)
        
        self.other_param1_combo = QComboBox()
        self.setup_pressure_options(self.other_param1_combo)
        self.other_param1_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.other_param1_combo.currentTextChanged.connect(
            lambda text: self.on_param_combo_changed(text, self.other_param1_input)
        )
        input_layout.addWidget(self.other_param1_combo, row, 2)
        
        row += 1
        
        # 参数2输入
        self.other_param2_label = QLabel("温度 (°C):")
        self.other_param2_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.other_param2_label.setStyleSheet(label_style)
        input_layout.addWidget(self.other_param2_label, row, 0)
        
        self.other_param2_input = QLineEdit()
        self.other_param2_input.setPlaceholderText("例如: 165")
        self.other_param2_input.setValidator(QDoubleValidator(0.01, 800.0, 6))
        self.other_param2_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        input_layout.addWidget(self.other_param2_input, row, 1)
        
        self.other_param2_combo = QComboBox()
        self.setup_temperature_options(self.other_param2_combo)
        self.other_param2_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.other_param2_combo.currentTextChanged.connect(
            lambda text: self.on_param_combo_changed(text, self.other_param2_input)
        )
        input_layout.addWidget(self.other_param2_combo, row, 2)
        
        layout.addWidget(input_widget)
        layout.addStretch()
        
        return widget
    
    def setup_mode_dependencies(self):
        """设置计算模式的依赖关系"""
        # 初始状态 - 饱和状态
        self.on_mode_changed("饱和状态")
    
    def setup_connections(self):
        """设置信号连接"""
        # 计算按钮连接已在setup_ui中设置
        pass
    
    def initialize_values(self):
        """初始化值"""
        # 饱和状态默认值
        self.sat_param1_input.setText("0.6")
        self.dryness_input.setText("0.9")
        
        # 其他状态默认值
        self.other_param1_input.setText("0.6")
        self.other_param2_input.setText("165")
    
    def get_groupbox_style(self):
        """获取GroupBox样式 - 与压降计算模块完全一致"""
        return """
            QGroupBox {
                font-weight: bold;
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """
    
    def setup_pressure_options(self, combo_box):
        """设置压力选项"""
        options = [
            "- 请选择压力 -",
            "0.1013 MPa - 常压",
            "0.1 MPa - 低压蒸汽",
            "0.3 MPa - 低压蒸汽",
            "0.6 MPa - 中压蒸汽",
            "1.0 MPa - 中压蒸汽",
            "1.6 MPa - 高压蒸汽",
            "2.5 MPa - 高压蒸汽",
            "4.0 MPa - 超高压蒸汽",
            "10.0 MPa - 超高压蒸汽",
            "自定义压力"
        ]
        combo_box.addItems(options)
        combo_box.setCurrentIndex(0)
    
    def setup_temperature_options(self, combo_box):
        """设置温度选项"""
        options = [
            "- 请选择温度 -",
            "100 °C - 饱和蒸汽",
            "120 °C - 饱和蒸汽",
            "150 °C - 饱和蒸汽",
            "165 °C - 饱和蒸汽",
            "180 °C - 饱和蒸汽",
            "200 °C - 过热蒸汽",
            "250 °C - 过热蒸汽",
            "300 °C - 过热蒸汽",
            "400 °C - 高温蒸汽",
            "500 °C - 高温蒸汽",
            "600 °C - 超高温蒸汽",
            "自定义温度"
        ]
        combo_box.addItems(options)
        combo_box.setCurrentIndex(0)
    
    def on_mode_button_clicked(self, button):
        """处理计算模式按钮点击"""
        mode_text = button.text()
        self.on_mode_changed(mode_text)
    
    def on_sat_known_button_clicked(self, button):
        """处理饱和状态已知参数按钮点击"""
        param_type = button.text()
        self.update_sat_known_ui(param_type)
    
    def on_other_known_button_clicked(self, button):
        """处理其他状态已知参数组合按钮点击"""
        param_combo = button.text()
        self.update_other_known_ui(param_combo)
    
    def get_current_mode(self):
        """获取当前选择的计算模式"""
        checked_button = self.mode_button_group.checkedButton()
        if checked_button:
            return checked_button.text()
        return "饱和状态"  # 默认值
    
    def on_mode_changed(self, mode):
        """处理计算模式变化"""
        self.current_mode = mode
        
        if mode == "饱和状态":
            self.input_stack.setCurrentWidget(self.saturation_page)
        else:  # 其他状态
            self.input_stack.setCurrentWidget(self.other_page)
    
    def update_sat_known_ui(self, param_type):
        """更新饱和状态已知参数UI"""
        if "压力" in param_type:
            self.sat_param1_label.setText("压力 (MPa):")
            self.sat_param1_combo.clear()
            self.setup_pressure_options(self.sat_param1_combo)
            self.sat_param1_input.setValidator(QDoubleValidator(0.001, 30.0, 6))
            self.sat_param1_input.setPlaceholderText("例如: 0.6")
            self.sat_param1_input.setText("0.6")
        else:  # 温度
            self.sat_param1_label.setText("温度 (°C):")
            self.sat_param1_combo.clear()
            self.setup_temperature_options(self.sat_param1_combo)
            self.sat_param1_input.setValidator(QDoubleValidator(0.01, 800.0, 6))
            self.sat_param1_input.setPlaceholderText("例如: 165")
            self.sat_param1_input.setText("165")
    
    def update_other_known_ui(self, param_combo):
        """更新其他状态已知参数组合UI"""
        # 根据选择的参数组合更新标签
        if "压力 P 和温度 T" in param_combo:
            self.other_param1_label.setText("压力 (MPa):")
            self.other_param2_label.setText("温度 (°C):")
            
            self.other_param1_combo.clear()
            self.setup_pressure_options(self.other_param1_combo)
            self.other_param1_input.setValidator(QDoubleValidator(0.001, 30.0, 6))
            self.other_param1_input.setPlaceholderText("例如: 0.6")
            
            self.other_param2_combo.clear()
            self.setup_temperature_options(self.other_param2_combo)
            self.other_param2_input.setValidator(QDoubleValidator(0.01, 800.0, 6))
            self.other_param2_input.setPlaceholderText("例如: 165")
            
        elif "压力 P 和比焓 H" in param_combo:
            self.other_param1_label.setText("压力 (MPa):")
            self.other_param2_label.setText("比焓 (kJ/kg):")
            
            self.other_param1_combo.clear()
            self.setup_pressure_options(self.other_param1_combo)
            self.other_param1_input.setValidator(QDoubleValidator(0.001, 30.0, 6))
            self.other_param1_input.setPlaceholderText("例如: 0.6")
            
            self.other_param2_combo.clear()
            enthalpy_options = [
                "- 请选择比焓 -",
                "500 kJ/kg - 过冷水",
                "1000 kJ/kg - 湿蒸汽",
                "2000 kJ/kg - 湿蒸汽",
                "2675 kJ/kg - 饱和蒸汽",
                "2800 kJ/kg - 过热蒸汽",
                "3000 kJ/kg - 过热蒸汽",
                "3500 kJ/kg - 高温蒸汽",
                "自定义比焓"
            ]
            self.other_param2_combo.addItems(enthalpy_options)
            self.other_param2_input.setValidator(QDoubleValidator(0.1, 5000.0, 6))
            self.other_param2_input.setPlaceholderText("例如: 2800")
            
        elif "压力 P 和比熵 S" in param_combo:
            self.other_param1_label.setText("压力 (MPa):")
            self.other_param2_label.setText("比熵 (kJ/(kg·K)):")
            
            self.other_param1_combo.clear()
            self.setup_pressure_options(self.other_param1_combo)
            self.other_param1_input.setValidator(QDoubleValidator(0.001, 30.0, 6))
            self.other_param1_input.setPlaceholderText("例如: 0.6")
            
            self.other_param2_combo.clear()
            entropy_options = [
                "- 请选择比熵 -",
                "1.0 kJ/(kg·K) - 过冷水",
                "3.0 kJ/(kg·K) - 湿蒸汽",
                "5.0 kJ/(kg·K) - 湿蒸汽",
                "6.5 kJ/(kg·K) - 饱和蒸汽",
                "7.0 kJ/(kg·K) - 过热蒸汽",
                "8.0 kJ/(kg·K) - 过热蒸汽",
                "自定义比熵"
            ]
            self.other_param2_combo.addItems(entropy_options)
            self.other_param2_input.setValidator(QDoubleValidator(0.1, 10.0, 6))
            self.other_param2_input.setPlaceholderText("例如: 7.0")
    
    def on_param_combo_changed(self, text, input_widget):
        """处理参数下拉菜单变化"""
        # 检查是否为空值选项
        if text.startswith("-") or not text.strip():
            input_widget.clear()
            input_widget.setReadOnly(False)
            return
        
        if "自定义" in text:
            input_widget.setReadOnly(False)
            input_widget.setPlaceholderText("输入自定义值")
            input_widget.clear()
        else:
            input_widget.setReadOnly(True)
            try:
                # 从文本中提取数字
                match = re.search(r'(\d+\.?\d*)', text)
                if match:
                    value = float(match.group(1))
                    # 根据单位确定显示格式
                    if "MPa" in text:
                        input_widget.setText(f"{value:.4f}")
                    elif "°C" in text:
                        input_widget.setText(f"{value:.0f}")
                    elif "kJ/kg" in text:
                        input_widget.setText(f"{value:.1f}")
                    elif "kJ/(kg·K)" in text:
                        input_widget.setText(f"{value:.3f}")
                    else:
                        input_widget.setText(f"{value}")
            except:
                pass
    
    # ==================== 计算函数 ====================
    
    def calculate_steam_properties(self):
        """计算水蒸气性质"""
        try:
            if self.current_mode == "饱和状态":
                self.calculate_saturation_properties()
            else:
                self.calculate_other_properties()
                
        except ValueError as e:
            QMessageBox.critical(self, "输入错误", f"参数输入格式错误: {str(e)}")
        except ZeroDivisionError:
            QMessageBox.critical(self, "计算错误", "计算过程中出现除零错误")
        except Exception as e:
            QMessageBox.critical(self, "计算错误", f"计算过程中发生错误: {str(e)}")
    
    def calculate_saturation_properties(self):
        """计算饱和状态水蒸气性质"""
        # 获取输入值
        # 获取当前选中的已知参数按钮
        checked_button = self.sat_known_button_group.checkedButton()
        if checked_button:
            param_type = checked_button.text()
        else:
            param_type = "压力 P"  # 默认值
        
        param_value = float(self.sat_param1_input.text() or 0)
        dryness = float(self.dryness_input.text() or 0)
        
        # 验证输入
        if not param_value:
            QMessageBox.warning(self, "输入错误", "请输入参数值")
            return
        
        if dryness < 0 or dryness > 1:
            QMessageBox.warning(self, "输入错误", "干度必须在0~1之间")
            return
        
        # 计算饱和性质
        if "压力" in param_type:
            pressure_mpa = param_value
            saturation_temp = self.calculate_saturation_temperature(pressure_mpa)
        else:  # 温度
            temperature_c = param_value
            pressure_mpa = self.calculate_saturation_pressure(temperature_c)
            saturation_temp = temperature_c
        
        # 计算物性
        density = self.calculate_steam_density(pressure_mpa, saturation_temp, dryness)
        enthalpy = self.calculate_enthalpy(pressure_mpa, saturation_temp, dryness)
        entropy = self.calculate_entropy(pressure_mpa, saturation_temp, dryness)
        specific_volume = 1 / density if density > 0 else 0
        
        # 判断蒸汽状态
        if dryness == 0:
            state = "饱和水"
            state_icon = "💧"
        elif dryness == 1:
            state = "干饱和蒸汽"
            state_icon = "🔥"
        else:
            state = f"湿蒸汽 (干度={dryness:.3f})"
            state_icon = "💧🔥"
        
        # 格式化结果
        result = self.format_saturation_result(
            param_type, param_value, dryness, pressure_mpa, saturation_temp,
            state, state_icon, density, specific_volume, enthalpy, entropy
        )
        
        self.result_text.setText(result)
        
        # 发射信号
        if hasattr(self, 'calculation_completed'):
            self.calculation_completed.emit({
                'mode': 'saturation',
                'pressure': pressure_mpa,
                'temperature': saturation_temp,
                'dryness': dryness,
                'state': state,
                'density': density,
                'enthalpy': enthalpy,
                'entropy': entropy
            })
    
    def calculate_other_properties(self):
        """计算其他状态水蒸气性质"""
        # 获取输入值
        # 获取当前选中的已知参数组合按钮
        checked_button = self.other_known_button_group.checkedButton()
        if checked_button:
            param_combo = checked_button.text()
        else:
            param_combo = "压力 P 和温度 T"  # 默认值
        
        param1_value = float(self.other_param1_input.text() or 0)
        param2_value = float(self.other_param2_input.text() or 0)
        
        # 验证输入
        if not param1_value or not param2_value:
            QMessageBox.warning(self, "输入错误", "请输入所有参数值")
            return
        
        # 根据参数组合计算
        if "压力 P 和温度 T" in param_combo:
            pressure_mpa = param1_value
            temperature_c = param2_value
            
            # 判断状态
            saturation_temp = self.calculate_saturation_temperature(pressure_mpa)
            
            if temperature_c < saturation_temp - 0.1:
                state = "过冷水"
                state_icon = "💧"
                dryness = 0
            elif abs(temperature_c - saturation_temp) < 0.1:
                state = "饱和状态"
                state_icon = "💧🔥"
                dryness = 1  # 默认干饱和蒸汽
            else:
                state = "过热蒸汽"
                state_icon = "🔥"
                dryness = 1
        
        elif "压力 P 和比焓 H" in param_combo:
            pressure_mpa = param1_value
            enthalpy_kjkg = param2_value
            
            # 计算饱和性质
            saturation_temp = self.calculate_saturation_temperature(pressure_mpa)
            h_f = self.calculate_enthalpy(pressure_mpa, saturation_temp, 0)  # 饱和水焓
            h_g = self.calculate_enthalpy(pressure_mpa, saturation_temp, 1)  # 饱和蒸汽焓
            
            if enthalpy_kjkg <= h_f:
                state = "过冷水"
                state_icon = "💧"
                temperature_c = enthalpy_kjkg / 4.18  # 简化计算
                dryness = 0
            elif h_f < enthalpy_kjkg < h_g:
                state = "湿蒸汽"
                state_icon = "💧🔥"
                dryness = (enthalpy_kjkg - h_f) / (h_g - h_f)
                temperature_c = saturation_temp
            else:
                state = "过热蒸汽"
                state_icon = "🔥"
                dryness = 1
                # 简化计算过热蒸汽温度
                temperature_c = saturation_temp + (enthalpy_kjkg - h_g) / 2.0
        
        else:  # 压力 P 和比熵 S
            pressure_mpa = param1_value
            entropy_kjkgk = param2_value
            
            # 简化计算
            saturation_temp = self.calculate_saturation_temperature(pressure_mpa)
            s_f = self.calculate_entropy(pressure_mpa, saturation_temp, 0)  # 饱和水熵
            s_g = self.calculate_entropy(pressure_mpa, saturation_temp, 1)  # 饱和蒸汽熵
            
            if entropy_kjkgk <= s_f:
                state = "过冷水"
                state_icon = "💧"
                temperature_c = saturation_temp - 5  # 简化
                dryness = 0
            elif s_f < entropy_kjkgk < s_g:
                state = "湿蒸汽"
                state_icon = "💧🔥"
                dryness = (entropy_kjkgk - s_f) / (s_g - s_f)
                temperature_c = saturation_temp
            else:
                state = "过热蒸汽"
                state_icon = "🔥"
                dryness = 1
                temperature_c = saturation_temp + 50  # 简化
        
        # 计算物性
        density = self.calculate_steam_density(pressure_mpa, temperature_c, dryness)
        enthalpy = self.calculate_enthalpy(pressure_mpa, temperature_c, dryness)
        entropy = self.calculate_entropy(pressure_mpa, temperature_c, dryness)
        specific_volume = 1 / density if density > 0 else 0
        
        # 计算过热度（如果是过热蒸汽）
        superheat = temperature_c - saturation_temp if temperature_c > saturation_temp else 0
        
        # 格式化结果
        result = self.format_other_result(
            param_combo, pressure_mpa, param2_value, temperature_c, saturation_temp,
            state, state_icon, dryness, density, specific_volume, enthalpy, entropy, superheat
        )
        
        self.result_text.setText(result)
        
        # 发射信号
        if hasattr(self, 'calculation_completed'):
            self.calculation_completed.emit({
                'mode': 'other',
                'param_combo': param_combo,
                'pressure': pressure_mpa,
                'param2': param2_value,
                'temperature': temperature_c,
                'dryness': dryness,
                'state': state,
                'density': density,
                'enthalpy': enthalpy,
                'entropy': entropy
            })
    
    def calculate_saturation_temperature(self, pressure_mpa):
        """计算饱和温度"""
        # IAPWS-IF97 简化公式（0.001~22.064 MPa）
        pressure_bar = pressure_mpa * 10
        
        # 使用IAPWS近似公式
        if pressure_bar <= 0.1:
            return 45.8
        elif pressure_bar <= 1:
            return 99.6 + (pressure_bar - 0.1) * 30
        elif pressure_bar <= 10:
            return 179.9 + (pressure_bar - 1) * 12
        elif pressure_bar <= 50:
            return 263.9 + (pressure_bar - 10) * 3.5
        elif pressure_bar <= 100:
            return 311.0 + (pressure_bar - 50) * 1.5
        elif pressure_bar <= 200:
            return 365.8 + (pressure_bar - 100) * 1.1
        else:
            return 374.1  # 临界温度
    
    def calculate_saturation_pressure(self, temperature_c):
        """计算饱和压力"""
        # IAPWS-IF97 简化公式（0.01~374 °C）
        if temperature_c <= 100:
            return 0.1013 * (temperature_c / 100) ** 4
        elif temperature_c <= 200:
            return 0.1013 * (temperature_c / 100) ** 3
        elif temperature_c <= 300:
            return 0.1013 * (temperature_c / 100) ** 2.5
        elif temperature_c <= 374:
            return 22.064 * ((temperature_c - 300) / 74) ** 2
        else:
            return 22.064  # 临界压力
    
    def calculate_steam_density(self, pressure_mpa, temperature_c, dryness=1):
        """计算蒸汽密度"""
        pressure_bar = pressure_mpa * 10
        
        if dryness < 1:  # 湿蒸汽
            # 饱和水密度
            rho_f = 1000 - (temperature_c - 100) * 1.5
            # 饱和蒸汽密度
            if temperature_c < 200:
                rho_g = 0.6 * pressure_bar / (temperature_c + 100)
            else:
                rho_g = 0.5 * pressure_bar / (temperature_c + 150)
            
            # 混合密度
            v_f = 1 / rho_f if rho_f > 0 else 0
            v_g = 1 / rho_g if rho_g > 0 else 0
            v = (1 - dryness) * v_f + dryness * v_g
            return 1 / v if v > 0 else 0
        else:  # 单相
            if temperature_c < 200:
                density = 0.6 * pressure_bar / (temperature_c + 100)
            else:
                density = 0.5 * pressure_bar / (temperature_c + 150)
            
            return max(density, 0.1)
    
    def calculate_enthalpy(self, pressure_mpa, temperature_c, dryness=1):
        """计算比焓"""
        saturation_temp = self.calculate_saturation_temperature(pressure_mpa)
        
        if dryness < 1:  # 湿蒸汽
            # 饱和水焓
            h_f = 4.18 * saturation_temp
            # 饱和蒸汽焓
            h_g = 2675 + pressure_mpa * 10
            
            return (1 - dryness) * h_f + dryness * h_g
        else:  # 单相
            if temperature_c < saturation_temp - 0.1:
                return 4.18 * temperature_c  # 过冷水
            elif abs(temperature_c - saturation_temp) < 0.1:
                return 2675 + pressure_mpa * 10  # 饱和蒸汽
            else:
                # 过热蒸汽
                h_sat = 2675 + pressure_mpa * 10
                return h_sat + (temperature_c - saturation_temp) * 2.0
    
    def calculate_entropy(self, pressure_mpa, temperature_c, dryness=1):
        """计算比熵"""
        saturation_temp = self.calculate_saturation_temperature(pressure_mpa)
        
        if dryness < 1:  # 湿蒸汽
            # 饱和水熵
            s_f = 0.5 + 0.01 * saturation_temp
            # 饱和蒸汽熵
            s_g = 6.5 + pressure_mpa * 0.1
            
            return (1 - dryness) * s_f + dryness * s_g
        else:  # 单相
            if temperature_c < saturation_temp - 0.1:
                return 0.5 + 0.01 * temperature_c  # 过冷水
            elif abs(temperature_c - saturation_temp) < 0.1:
                return 6.5 + pressure_mpa * 0.1  # 饱和蒸汽
            else:
                # 过热蒸汽
                s_sat = 6.5 + pressure_mpa * 0.1
                return s_sat + (temperature_c - saturation_temp) * 0.005
    
    # ==================== 结果格式化函数 ====================
    
    def format_saturation_result(self, param_type, param_value, dryness, pressure, temperature,
                                state, state_icon, density, specific_volume, enthalpy, entropy):
        """格式化饱和状态结果"""
        return f"""═══════════════════════════════════════════════════
                        📋 输入参数
═══════════════════════════════════════════════════

• 查询模式: 饱和状态
• 已知参数: {param_type}
• 参数值: {param_value:.4f} {param_type.split()[-1]}
• 干度: {dryness:.3f}

═══════════════════════════════════════════════════
                        📊 计算结果
═══════════════════════════════════════════════════

• 压力: {pressure:.4f} MPa
• 温度: {temperature:.2f} °C
• 状态: {state_icon} {state}

物性参数:
• 密度: {density:.4f} kg/m³
• 比容: {specific_volume:.6f} m³/kg
• 比焓: {enthalpy:.2f} kJ/kg
• 比熵: {entropy:.4f} kJ/(kg·K)

饱和参数对比:
• 饱和压力: {pressure:.4f} MPa
• 饱和温度: {temperature:.2f} °C
• 汽化潜热: {self.calculate_enthalpy(pressure, temperature, 1) - self.calculate_enthalpy(pressure, temperature, 0):.1f} kJ/kg

═══════════════════════════════════════════════════
                        💡 状态说明
═══════════════════════════════════════════════════

{state_icon} {state}

{f"• 干度 {dryness:.3f} 表示蒸汽中含有 {dryness*100:.1f}% 的饱和蒸汽" if 0 < dryness < 1 else ""}
{f"• 饱和水状态，可用于加热或传热计算" if dryness == 0 else ""}
{f"• 干饱和蒸汽，可用于动力或工艺过程" if dryness == 1 else ""}

═══════════════════════════════════════════════════
                        🎯 应用建议
═══════════════════════════════════════════════════

• 以上数据为工程近似值
• 实际应用请参考IAPWS-IF97标准
• 对于精确计算，建议使用专业物性软件
• 在临界点附近物性变化剧烈，需要特别注意"""
    
    def format_other_result(self, param_combo, pressure, param2_value, temperature, saturation_temp,
                           state, state_icon, dryness, density, specific_volume, enthalpy, entropy, superheat):
        """格式化其他状态结果"""
        return f"""═══════════════════════════════════════════════════
                        📋 输入参数
═══════════════════════════════════════════════════

• 查询模式: 其他状态
• 已知参数: {param_combo}
• 压力 P: {pressure:.4f} MPa
• {param_combo.split("和")[1].strip()}: {param2_value:.4f}

═══════════════════════════════════════════════════
                        📊 计算结果
═══════════════════════════════════════════════════

• 压力: {pressure:.4f} MPa
• 温度: {temperature:.2f} °C
• 状态: {state_icon} {state}
{f"• 干度: {dryness:.3f}" if 0 < dryness < 1 else ""}
{f"• 过热度: {superheat:.2f} °C" if superheat > 0 else ""}

物性参数:
• 密度: {density:.4f} kg/m³
• 比容: {specific_volume:.6f} m³/kg
• 比焓: {enthalpy:.2f} kJ/kg
• 比熵: {entropy:.4f} kJ/(kg·K)

参考数据:
• 饱和温度: {saturation_temp:.2f} °C
• 当前温度: {temperature:.2f} °C
{f"• 过热度: {superheat:.2f} °C" if superheat > 0 else f"• 过冷度: {saturation_temp - temperature:.2f} °C" if temperature < saturation_temp else ""}

═══════════════════════════════════════════════════
                        💡 状态说明
═══════════════════════════════════════════════════

{state_icon} {state}

{f"• 过热度 {superheat:.1f}°C，属于中等过热蒸汽" if 10 < superheat <= 50 else ""}
{f"• 过热度 {superheat:.1f}°C，属于高度过热蒸汽" if superheat > 50 else ""}
{f"• 接近饱和状态，需要注意汽水分离" if abs(temperature - saturation_temp) < 5 and temperature >= saturation_temp else ""}
{f"• 处于过冷水状态，需要加热才能产生蒸汽" if temperature < saturation_temp - 0.1 else ""}

═══════════════════════════════════════════════════
                        🎯 应用建议
═══════════════════════════════════════════════════

• 以上数据为工程近似值
• 实际应用请参考IAPWS-IF97标准
• 对于精确计算，建议使用专业物性软件
• 在临界点附近物性变化剧烈，需要特别注意"""
    
    # ==================== 报告生成函数 ====================
    
    def download_txt_report(self):
        """下载TXT格式计算书"""
        try:
            # 获取当前结果文本
            result_text = self.result_text.toPlainText()
            
            if not result_text or "计算结果" not in result_text:
                QMessageBox.warning(self, "生成失败", "请先进行计算再生成计算书")
                return
            
            # 选择保存路径
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"水蒸气性质计算书_{timestamp}.txt"
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存计算书", default_name, "Text Files (*.txt)"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(result_text)
                QMessageBox.information(self, "下载成功", f"计算书已保存到:\n{file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "下载失败", f"保存计算书时发生错误: {str(e)}")
    
    def download_pdf_report(self):
        """下载PDF格式计算书"""
        try:
            # 获取当前结果文本
            result_text = self.result_text.toPlainText()
            
            if not result_text or "计算结果" not in result_text:
                QMessageBox.warning(self, "生成失败", "请先进行计算再生成计算书")
                return
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"水蒸气性质计算书_{timestamp}.pdf"
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存PDF计算书", default_name, "PDF Files (*.pdf)"
            )
            
            if not file_path:
                return
            
            # 尝试导入reportlab
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.pdfgen import canvas
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
                from reportlab.lib.units import inch
                from reportlab.pdfbase import pdfmetrics
                from reportlab.pdfbase.ttfonts import TTFont
                import os
                
                # 注册中文字体
                try:
                    font_paths = [
                        "C:/Windows/Fonts/simhei.ttf",
                        "C:/Windows/Fonts/simsun.ttc",
                        "C:/Windows/Fonts/msyh.ttc",
                        "/Library/Fonts/Arial Unicode.ttf",
                        "/System/Library/Fonts/Arial.ttf",
                    ]
                    
                    chinese_font_registered = False
                    for font_path in font_paths:
                        if os.path.exists(font_path):
                            try:
                                pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                                chinese_font_registered = True
                                break
                            except:
                                continue
                    
                    if not chinese_font_registered:
                        pdfmetrics.registerFont(TTFont('ChineseFont', 'Helvetica'))
                except:
                    pass
                
                # 创建PDF文档
                doc = SimpleDocTemplate(file_path, pagesize=A4)
                styles = getSampleStyleSheet()
                
                # 创建支持中文的样式
                chinese_style_normal = ParagraphStyle(
                    'ChineseNormal',
                    parent=styles['Normal'],
                    fontName='ChineseFont',
                    fontSize=10,
                    leading=14,
                )
                
                chinese_style_heading = ParagraphStyle(
                    'ChineseHeading',
                    parent=styles['Heading1'],
                    fontName='ChineseFont',
                    fontSize=16,
                    leading=20,
                    spaceAfter=12,
                )
                
                story = []
                
                # 添加标题
                title = Paragraph("工程计算书 - 水蒸气性质查询", chinese_style_heading)
                story.append(title)
                story.append(Spacer(1, 0.2*inch))
                
                # 处理报告内容
                processed_content = self.process_content_for_pdf(result_text)
                
                # 添加内容
                for line in processed_content.split('\n'):
                    if line.strip():
                        line = line.replace(' ', '&nbsp;')
                        line = line.replace('═', '=').replace('─', '-')
                        para = Paragraph(line, chinese_style_normal)
                        story.append(para)
                        story.append(Spacer(1, 0.05*inch))
                
                # 生成PDF
                doc.build(story)
                QMessageBox.information(self, "生成成功", f"PDF计算书已保存到:\n{file_path}")
                return True
                
            except ImportError:
                QMessageBox.warning(
                    self, 
                    "功能不可用", 
                    "PDF生成功能需要安装reportlab库\n\n请运行: pip install reportlab"
                )
                return False
                
        except Exception as e:
            QMessageBox.critical(self, "生成失败", f"生成PDF时发生错误: {str(e)}")
            return False
    
    def process_content_for_pdf(self, content):
        """处理内容，使其适合PDF显示"""
        # 替换表情图标为文字描述
        replacements = {
            "📋": "",
            "📊": "", 
            "🧮": "",
            "💡": "",
            "📤": "",
            "📥": "",
            "⚠️": "",
            "🔬": "",
            "💧": "",
            "🔥": "",
            "💧🔥": "(湿蒸汽)",
            "🎯": ""
        }
        
        # 替换表情图标
        for emoji, text in replacements.items():
            content = content.replace(emoji, text)
        
        # 替换单位符号
        content = content.replace("m³", "m3")
        content = content.replace("kg/m³", "kg/m3")
        content = content.replace("kJ/(kg·K)", "kJ/(kg.K)")
        
        return content


# ==================== 测试代码 ====================
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    calculator = SteamPropertyCalculator()
    calculator.resize(1200, 800)
    calculator.show()
    
    sys.exit(app.exec())