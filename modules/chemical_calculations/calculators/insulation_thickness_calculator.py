# [file name]: calculators/insulation_thickness_calculator.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                              QLabel, QLineEdit, QComboBox, QPushButton, 
                              QTextEdit, QTableWidget, QTableWidgetItem,
                              QHeaderView, QMessageBox, QTabWidget, QDoubleSpinBox,
                              QCheckBox, QRadioButton, QButtonGroup, QGridLayout,
                              QStackedWidget, QFrame, QScrollArea, QSizePolicy)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QDoubleValidator, QIntValidator
import math
from datetime import datetime

class InsulationThicknessCalculator(QWidget):
    """保温厚度计算器（紧凑四列布局版本）"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_material_properties()
    
    def setup_ui(self):
        """设置UI - 紧凑四列布局"""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 左侧：输入参数区域
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(15)
        
        # 1. 说明文本
        description = QLabel(
            "计算保温层厚度，支持四种计算方法。参数输入区采用四列布局以节省空间。"
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 5px;")
        left_layout.addWidget(description)
        
        # 2. 计算类型选择 - 改为点选按钮模式
        calc_type_group = QGroupBox("计算类型")
        calc_type_group.setStyleSheet("""
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
        """)
        calc_type_layout = QHBoxLayout(calc_type_group)
        
        # 创建按钮组
        self.calc_type_group = QButtonGroup(self)
        
        # 定义计算类型和对应的工具提示
        calc_types = [
            ("绝热层经济厚度", "基于经济性考虑计算最佳保温厚度"),
            ("表面温度法", "根据外表面温度要求计算保温厚度"),
            ("防结露", "防止表面结露的最小保温厚度"),
            ("热损失法", "根据允许热损失量计算保温厚度")
        ]
        
        for i, (text, tooltip) in enumerate(calc_types):
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setToolTip(tooltip)
            btn.setMinimumWidth(100)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #ecf0f1;
                    border: 1px solid #bdc3c7;
                    border-radius: 4px;
                    padding: 8px;
                    text-align: center;
                }
                QPushButton:checked {
                    background-color: #3498db;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #d5dbdb;
                }
            """)
            self.calc_type_group.addButton(btn, i)
            calc_type_layout.addWidget(btn)
        
        # 默认选择第一个按钮
        self.calc_type_group.buttons()[0].setChecked(True)
        self.calc_type_group.buttonClicked.connect(self.on_calc_type_changed)
        
        left_layout.addWidget(calc_type_group)
        
        # 3. 输入参数组 - 四列布局
        input_group = QGroupBox("输入参数")
        input_group.setStyleSheet("""
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
        """)
        
        # 使用GridLayout实现四列布局
        input_layout = QGridLayout(input_group)
        input_layout.setVerticalSpacing(10)
        input_layout.setHorizontalSpacing(8)
        
        # 标签样式 - 右对齐，紧凑
        label_style = """
            QLabel {
                font-weight: bold;
                font-size: 11px;
                padding-right: 5px;
            }
        """
        
        # 输入框样式 - 设置固定宽度
        input_style = """
            QLineEdit, QComboBox {
                min-width: 120px;
                max-width: 150px;
                font-size: 11px;
            }
        """
        
        row = 0
        
        # 第1行：设备型式和保温类型
        equipment_label = QLabel("设备型式:")
        equipment_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        equipment_label.setStyleSheet(label_style)
        input_layout.addWidget(equipment_label, row, 0)
        
        self.equipment_type_combo = QComboBox()
        self.equipment_type_combo.addItems(["管道或圆筒形设备", "平面形设备"])
        self.equipment_type_combo.setStyleSheet(input_style)
        self.equipment_type_combo.currentTextChanged.connect(self.on_equipment_type_changed)
        input_layout.addWidget(self.equipment_type_combo, row, 1)
        
        insulation_label = QLabel("保温类型:")
        insulation_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        insulation_label.setStyleSheet(label_style)
        input_layout.addWidget(insulation_label, row, 2)
        
        self.insulation_type_combo = QComboBox()
        self.insulation_type_combo.addItems(["保温", "保冷"])
        self.insulation_type_combo.setStyleSheet(input_style)
        self.insulation_type_combo.currentTextChanged.connect(self.on_insulation_type_changed)
        input_layout.addWidget(self.insulation_type_combo, row, 3)
        
        row += 1
        
        # 第2行：设备尺寸和保温材料
        size_label = QLabel("设备尺寸(mm):")
        size_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        size_label.setStyleSheet(label_style)
        input_layout.addWidget(size_label, row, 0)
        
        self.size_input = QLineEdit()
        self.size_input.setPlaceholderText("108")
        self.size_input.setValidator(QDoubleValidator(1.0, 5000.0, 2))
        self.size_input.setText("108")
        self.size_input.setStyleSheet(input_style)
        input_layout.addWidget(self.size_input, row, 1)
        
        material_label = QLabel("保温材料:")
        material_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        material_label.setStyleSheet(label_style)
        input_layout.addWidget(material_label, row, 2)
        
        self.material_combo = QComboBox()
        self.material_combo.addItems([
            "硅酸钙(170kg/m³)",
            "岩棉",
            "玻璃棉", 
            "硅酸铝纤维",
            "聚氨酯泡沫",
            "聚苯乙烯泡沫",
            "橡塑海绵",
            "气凝胶",
            "复合硅酸盐",
            "微孔硅酸钙",
            "珍珠岩",
            "自定义材料"
        ])
        self.material_combo.setStyleSheet(input_style)
        self.material_combo.currentTextChanged.connect(self.on_material_changed)
        input_layout.addWidget(self.material_combo, row, 3)
        
        row += 1
        
        # 第3行：导热系数和材料密度
        conductivity_label = QLabel("导热系数:")
        conductivity_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        conductivity_label.setStyleSheet(label_style)
        input_layout.addWidget(conductivity_label, row, 0)
        
        self.conductivity_input = QLineEdit()
        self.conductivity_input.setPlaceholderText("0.0512")
        self.conductivity_input.setValidator(QDoubleValidator(0.001, 1.0, 6))
        self.conductivity_input.setText("0.0512")
        self.conductivity_input.setStyleSheet(input_style)
        input_layout.addWidget(self.conductivity_input, row, 1)
        
        density_label = QLabel("密度(kg/m³):")
        density_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        density_label.setStyleSheet(label_style)
        input_layout.addWidget(density_label, row, 2)
        
        self.density_input = QLineEdit()
        self.density_input.setPlaceholderText("170")
        self.density_input.setValidator(QDoubleValidator(10, 500, 2))
        self.density_input.setText("170")
        self.density_input.setStyleSheet(input_style)
        input_layout.addWidget(self.density_input, row, 3)
        
        row += 1
        
        # 第4行：环境温度和风速
        ambient_label = QLabel("环境温度(°C):")
        ambient_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        ambient_label.setStyleSheet(label_style)
        input_layout.addWidget(ambient_label, row, 0)
        
        self.ambient_temp_input = QLineEdit()
        self.ambient_temp_input.setPlaceholderText("20")
        self.ambient_temp_input.setValidator(QDoubleValidator(-50, 60, 2))
        self.ambient_temp_input.setText("20")
        self.ambient_temp_input.setStyleSheet(input_style)
        input_layout.addWidget(self.ambient_temp_input, row, 1)
        
        wind_label = QLabel("风速(m/s):")
        wind_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        wind_label.setStyleSheet(label_style)
        input_layout.addWidget(wind_label, row, 2)
        
        self.wind_speed_input = QLineEdit()
        self.wind_speed_input.setPlaceholderText("3")
        self.wind_speed_input.setValidator(QDoubleValidator(0, 20, 2))
        self.wind_speed_input.setText("3")
        self.wind_speed_input.setStyleSheet(input_style)
        input_layout.addWidget(self.wind_speed_input, row, 3)
        
        row += 1
        
        # 第5行：露点温度和设备温度
        dew_point_label = QLabel("露点温度(°C):")
        dew_point_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        dew_point_label.setStyleSheet(label_style)
        input_layout.addWidget(dew_point_label, row, 0)
        
        self.dew_point_input = QLineEdit()
        self.dew_point_input.setPlaceholderText("22")
        self.dew_point_input.setValidator(QDoubleValidator(-50, 60, 2))
        self.dew_point_input.setText("22")
        self.dew_point_input.setStyleSheet(input_style)
        input_layout.addWidget(self.dew_point_input, row, 1)
        
        equipment_temp_label = QLabel("设备温度(°C):")
        equipment_temp_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        equipment_temp_label.setStyleSheet(label_style)
        input_layout.addWidget(equipment_temp_label, row, 2)
        
        self.equipment_temp_input = QLineEdit()
        self.equipment_temp_input.setPlaceholderText("200")
        self.equipment_temp_input.setValidator(QDoubleValidator(-200, 1000, 2))
        self.equipment_temp_input.setText("200")
        self.equipment_temp_input.setStyleSheet(input_style)
        input_layout.addWidget(self.equipment_temp_input, row, 3)
        
        row += 1
        
        # 动态参数区域 - 不同计算方法的特定参数
        self.dynamic_params_widget = QWidget()
        self.dynamic_params_layout = QGridLayout(self.dynamic_params_widget)
        self.dynamic_params_layout.setVerticalSpacing(10)
        self.dynamic_params_layout.setHorizontalSpacing(8)
        
        # 创建不同计算方法的动态参数
        self.setup_dynamic_parameters()
        
        # 将动态参数区域添加到主布局，跨4列
        input_layout.addWidget(self.dynamic_params_widget, row, 0, 1, 4)
        
        left_layout.addWidget(input_group)
        
        # 4. 按钮布局
        button_layout = QHBoxLayout()
        
        self.calculate_btn = QPushButton("🧮 计算保温厚度")
        self.calculate_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.calculate_btn.clicked.connect(self.calculate)
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
        button_layout.addWidget(self.calculate_btn)
        
        left_layout.addLayout(button_layout)
        
        # 5. 下载按钮布局
        download_layout = QHBoxLayout()
        
        download_txt_btn = QPushButton("📄 下载计算书(TXT)")
        download_txt_btn.clicked.connect(self.download_txt_report)
        download_txt_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        download_txt_btn.setStyleSheet("""
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
        
        download_pdf_btn = QPushButton("📊 下载计算书(PDF)")
        download_pdf_btn.clicked.connect(self.generate_pdf_report)
        download_pdf_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        download_pdf_btn.setStyleSheet("""
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
        
        download_layout.addWidget(download_txt_btn)
        download_layout.addWidget(download_pdf_btn)
        left_layout.addLayout(download_layout)
        
        # 6. 清空按钮
        clear_btn = QPushButton("🗑️ 清空输入")
        clear_btn.clicked.connect(self.clear_inputs)
        clear_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        left_layout.addWidget(clear_btn)
        
        # 添加弹性空间
        left_layout.addStretch()
        
        # 右侧：结果显示区域
        right_widget = QWidget()
        right_widget.setMinimumWidth(300)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)
        
        # 结果显示
        self.result_group = QGroupBox("计算结果")
        self.result_group.setStyleSheet("""
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
        """)
        result_layout = QVBoxLayout(self.result_group)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.result_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ecf0f1;
                border-radius: 6px;
                padding: 8px;
                background-color: #f8f9fa;
                min-height: 500px;
            }
        """)
        result_layout.addWidget(self.result_text)
        
        right_layout.addWidget(self.result_group)
        
        # 将左右两部分添加到主布局
        main_layout.addWidget(left_widget, 2)  # 左侧占2/3权重
        main_layout.addWidget(right_widget, 1)  # 右侧占1/3权重
        
        # 初始化显示状态
        self.update_ui_visibility()
    
    def setup_dynamic_parameters(self):
        """设置不同计算方法的动态参数"""
        # 清空现有布局
        while self.dynamic_params_layout.count():
            child = self.dynamic_params_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # 获取当前计算方法
        calc_type = self.get_current_calc_type()
        
        # 设置标签样式
        label_style = """
            QLabel {
                font-weight: bold;
                font-size: 11px;
                padding-right: 5px;
            }
        """
        
        # 设置输入框样式
        input_style = """
            QLineEdit {
                min-width: 120px;
                max-width: 150px;
                font-size: 11px;
            }
        """
        
        row = 0
        
        if calc_type == "绝热层经济厚度":
            # 经济厚度法参数 - 两行四列
            energy_price_label = QLabel("能量价格(元/GJ):")
            energy_price_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            energy_price_label.setStyleSheet(label_style)
            self.dynamic_params_layout.addWidget(energy_price_label, row, 0)
            
            self.energy_price_input = QLineEdit()
            self.energy_price_input.setPlaceholderText("3.6")
            self.energy_price_input.setValidator(QDoubleValidator(0.1, 100, 2))
            self.energy_price_input.setText("3.6")
            self.energy_price_input.setStyleSheet(input_style)
            self.dynamic_params_layout.addWidget(self.energy_price_input, row, 1)
            
            insulation_cost_label = QLabel("绝热造价(元/m³):")
            insulation_cost_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            insulation_cost_label.setStyleSheet(label_style)
            self.dynamic_params_layout.addWidget(insulation_cost_label, row, 2)
            
            self.insulation_cost_input = QLineEdit()
            self.insulation_cost_input.setPlaceholderText("640")
            self.insulation_cost_input.setValidator(QDoubleValidator(100, 5000, 2))
            self.insulation_cost_input.setText("640")
            self.insulation_cost_input.setStyleSheet(input_style)
            self.dynamic_params_layout.addWidget(self.insulation_cost_input, row, 3)
            
            row += 1
            
            operation_time_label = QLabel("年运行时间(小时):")
            operation_time_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            operation_time_label.setStyleSheet(label_style)
            self.dynamic_params_layout.addWidget(operation_time_label, row, 0)
            
            self.operation_time_input = QLineEdit()
            self.operation_time_input.setPlaceholderText("8000")
            self.operation_time_input.setValidator(QDoubleValidator(1, 8760, 2))
            self.operation_time_input.setText("8000")
            self.operation_time_input.setStyleSheet(input_style)
            self.dynamic_params_layout.addWidget(self.operation_time_input, row, 1)
            
            interest_rate_label = QLabel("年利率(%):")
            interest_rate_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            interest_rate_label.setStyleSheet(label_style)
            self.dynamic_params_layout.addWidget(interest_rate_label, row, 2)
            
            self.interest_rate_input = QLineEdit()
            self.interest_rate_input.setPlaceholderText("10")
            self.interest_rate_input.setValidator(QDoubleValidator(0.1, 50, 2))
            self.interest_rate_input.setText("10")
            self.interest_rate_input.setStyleSheet(input_style)
            self.dynamic_params_layout.addWidget(self.interest_rate_input, row, 3)
            
            row += 1
            
            years_label = QLabel("计息年限(年):")
            years_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            years_label.setStyleSheet(label_style)
            self.dynamic_params_layout.addWidget(years_label, row, 0)
            
            self.years_input = QLineEdit()
            self.years_input.setPlaceholderText("5")
            self.years_input.setValidator(QDoubleValidator(1, 30, 2))
            self.years_input.setText("5")
            self.years_input.setStyleSheet(input_style)
            self.dynamic_params_layout.addWidget(self.years_input, row, 1)
            
        elif calc_type == "表面温度法":
            # 表面温度法参数
            surface_temp_label = QLabel("外表面温度(°C):")
            surface_temp_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            surface_temp_label.setStyleSheet(label_style)
            self.dynamic_params_layout.addWidget(surface_temp_label, row, 0)
            
            self.surface_temp_input = QLineEdit()
            self.surface_temp_input.setPlaceholderText("26")
            self.surface_temp_input.setValidator(QDoubleValidator(-50, 200, 2))
            self.surface_temp_input.setText("26")
            self.surface_temp_input.setStyleSheet(input_style)
            self.dynamic_params_layout.addWidget(self.surface_temp_input, row, 1)
            
            # 留空第2、3列保持布局对齐
            # 或者添加一个占位符
            placeholder = QLabel("")
            self.dynamic_params_layout.addWidget(placeholder, row, 2)
            
            placeholder2 = QLabel("")
            self.dynamic_params_layout.addWidget(placeholder2, row, 3)

        elif calc_type == "热损失法":
            # 热损失法参数
            heat_loss_label = QLabel("允许热损失(W/m²):")
            heat_loss_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            heat_loss_label.setStyleSheet(label_style)
            self.dynamic_params_layout.addWidget(heat_loss_label, row, 0)
            
            self.heat_loss_limit_input = QLineEdit()
            self.heat_loss_limit_input.setPlaceholderText("160")
            self.heat_loss_limit_input.setValidator(QDoubleValidator(10, 1000, 2))
            self.heat_loss_limit_input.setText("160")
            self.heat_loss_limit_input.setStyleSheet(input_style)
            self.dynamic_params_layout.addWidget(self.heat_loss_limit_input, row, 1)

    def get_current_calc_type(self):
        """获取当前选择的计算类型"""
        checked_button = self.calc_type_group.checkedButton()
        if checked_button:
            return checked_button.text()
        return "绝热层经济厚度"  # 默认值
    
    def on_calc_type_changed(self, button):
        """计算类型改变事件"""
        self.setup_dynamic_parameters()
    
    def setup_material_properties(self):
        """设置保温材料属性"""
        self.material_properties = {
            "硅酸钙(170kg/m³)": {"conductivity": 0.0512, "density": 170},
            "岩棉": {"conductivity": 0.040, "density": 120},
            "玻璃棉": {"conductivity": 0.042, "density": 64},
            "硅酸铝纤维": {"conductivity": 0.120, "density": 200},
            "聚氨酯泡沫": {"conductivity": 0.025, "density": 40},
            "聚苯乙烯泡沫": {"conductivity": 0.038, "density": 30},
            "橡塑海绵": {"conductivity": 0.038, "density": 80},
            "气凝胶": {"conductivity": 0.018, "density": 180},
            "复合硅酸盐": {"conductivity": 0.048, "density": 180},
            "微孔硅酸钙": {"conductivity": 0.055, "density": 220},
            "珍珠岩": {"conductivity": 0.065, "density": 80}
        }
    
    def on_equipment_type_changed(self, equipment_type):
        """设备类型改变事件"""
        pass
    
    def on_insulation_type_changed(self, insulation_type):
        """保温类型改变事件"""
        self.update_ui_visibility()
    
    def on_material_changed(self, material_name):
        """保温材料改变事件"""
        if material_name in self.material_properties:
            props = self.material_properties[material_name]
            self.conductivity_input.setText(f"{props['conductivity']}")
            self.density_input.setText(f"{props['density']}")
    
    def update_ui_visibility(self):
        """更新UI元素可见性"""
        insulation_type = self.insulation_type_combo.currentText()
        
        # 保冷时显示露点温度，保温时隐藏
        if insulation_type == "保冷":
            self.dew_point_input.setEnabled(True)
            # 查找露点温度标签并启用
            for i in range(self.dynamic_params_widget.layout().count()):
                widget = self.dynamic_params_widget.layout().itemAt(i).widget()
                if isinstance(widget, QLabel) and "露点温度" in widget.text():
                    widget.setEnabled(True)
        else:
            self.dew_point_input.setEnabled(False)
            # 查找露点温度标签并禁用
            for i in range(self.dynamic_params_widget.layout().count()):
                widget = self.dynamic_params_widget.layout().itemAt(i).widget()
                if isinstance(widget, QLabel) and "露点温度" in widget.text():
                    widget.setEnabled(False)
    
    def calculate(self):
        """执行计算"""
        try:
            # 获取通用参数
            calc_type = self.get_current_calc_type()
            equipment_type = self.equipment_type_combo.currentText()
            insulation_type = self.insulation_type_combo.currentText()
            size = float(self.size_input.text() or 108) / 1000.0  # 转换为米
            conductivity = float(self.conductivity_input.text() or 0.0512)
            ambient_temp = float(self.ambient_temp_input.text() or 20)
            wind_speed = float(self.wind_speed_input.text() or 3)
            equipment_temp = float(self.equipment_temp_input.text() or 200)
            
            # 根据计算类型执行不同的计算
            if calc_type == "绝热层经济厚度":
                thickness = self.calculate_economic_thickness(
                    equipment_type, size, insulation_type,
                    float(self.energy_price_input.text() or 3.6),
                    float(self.insulation_cost_input.text() or 640),
                    ambient_temp, equipment_temp, conductivity,
                    wind_speed,
                    float(self.operation_time_input.text() or 8000),
                    float(self.interest_rate_input.text() or 10) / 100.0,
                    float(self.years_input.text() or 5)
                )
                method_name = "绝热层经济厚度法"
                
            elif calc_type == "表面温度法":
                thickness = self.calculate_by_surface_temp(
                    equipment_type, size, insulation_type,
                    ambient_temp, float(self.surface_temp_input.text() or 26),
                    equipment_temp, conductivity, wind_speed
                )
                method_name = "表面温度法"
                
            elif calc_type == "防结露":
                thickness = self.calculate_anti_condensation(
                    equipment_type, size,
                    ambient_temp, float(self.dew_point_input.text() or 22),
                    equipment_temp, conductivity
                )
                method_name = "防结露法"
                
            elif calc_type == "热损失法":
                thickness = self.calculate_by_heat_loss(
                    equipment_type, size, insulation_type,
                    ambient_temp, equipment_temp,
                    float(self.heat_loss_limit_input.text() or 160),
                    conductivity, wind_speed
                )
                method_name = "最大允许热损失法"
            else:
                raise ValueError(f"未知的计算类型: {calc_type}")
            
            # 显示结果
            self.display_results(calc_type, thickness, method_name)
            
        except Exception as e:
            QMessageBox.critical(self, "计算错误", f"计算过程中发生错误:\n{str(e)}")
    
    def calculate_economic_thickness(self, equipment_type, size, insulation_type,
                                   energy_price, insulation_cost,
                                   ambient_temp, equipment_temp, conductivity,
                                   wind_speed, operation_time, interest_rate, years):
        """计算经济厚度"""
        # 计算表面传热系数
        h = self.calculate_surface_heat_transfer_coefficient(wind_speed)
        
        # 将能量价格从元/GJ转换为元/J
        energy_price_j = energy_price / 1e9
        
        # 年运行时间转换为秒
        operation_time_s = operation_time * 3600
        
        # 温差
        delta_t = abs(equipment_temp - ambient_temp)
        
        if equipment_type == "管道或圆筒形设备":
            # 圆筒形设备经济厚度计算
            thickness = 0.01  # 从10mm开始
            best_thickness = thickness
            min_cost = float('inf')
            
            # 迭代范围：1mm 到 300mm
            for t in range(1, 301):
                thickness = t / 1000.0  # 转换为米
                
                # 计算热损失
                d1 = size  # 管道外径
                d2 = d1 + 2 * thickness  # 保温外径
                
                if d2 <= d1:
                    continue
                
                # 热阻计算
                r_insulation = math.log(d2 / d1) / (2 * math.pi * conductivity)
                r_surface = 1 / (h * math.pi * d2)
                total_r = r_insulation + r_surface
                
                # 热损失
                heat_loss = delta_t / total_r  # W/m
                
                # 年热损失费用
                annual_heat_loss_cost = heat_loss * operation_time_s * energy_price_j
                
                # 保温材料体积
                volume_per_meter = math.pi * (d2**2 - d1**2) / 4
                
                # 保温材料投资
                insulation_investment = volume_per_meter * insulation_cost
                
                # 等额分付资本回收系数
                capital_recovery_factor = (interest_rate * (1 + interest_rate)**years) / ((1 + interest_rate)**years - 1)
                
                # 年投资成本
                annual_investment_cost = insulation_investment * capital_recovery_factor
                
                # 年总费用
                total_annual_cost = annual_heat_loss_cost + annual_investment_cost
                
                if total_annual_cost < min_cost:
                    min_cost = total_annual_cost
                    best_thickness = thickness
            
            return best_thickness * 1000  # 返回毫米
            
        else:  # 平面形设备
            # 平面设备经济厚度计算
            # 简化公式：经济厚度 = sqrt(λ * ΔT * τ * P_E / (P_T * i)) - λ/h
            numerator = conductivity * delta_t * operation_time_s * energy_price_j
            denominator = insulation_cost * interest_rate
            economic_thickness = math.sqrt(numerator / denominator) - conductivity / h
            
            # 确保厚度非负
            economic_thickness = max(economic_thickness, 0)
            
            return economic_thickness * 1000  # 返回毫米
    
    def calculate_by_surface_temp(self, equipment_type, size, insulation_type,
                                ambient_temp, surface_temp, equipment_temp,
                                conductivity, wind_speed):
        """根据表面温度计算厚度"""
        # 计算表面传热系数
        h = self.calculate_surface_heat_transfer_coefficient(wind_speed)
        
        if equipment_type == "管道或圆筒形设备":
            # 圆筒形设备
            d1 = size  # 管道外径
            
            # 使用迭代法求解厚度
            thickness = 0.01  # 从10mm开始
            
            for _ in range(50):  # 最多迭代50次
                d2 = d1 + 2 * thickness
                
                # 计算当前厚度下的表面温度
                r_insulation = math.log(d2 / d1) / (2 * math.pi * conductivity)
                heat_loss = (equipment_temp - ambient_temp) / (r_insulation + 1/(h * math.pi * d2))
                calculated_surface_temp = ambient_temp + heat_loss * (1/(h * math.pi * d2))
                
                # 检查是否收敛
                if abs(calculated_surface_temp - surface_temp) < 0.1:
                    break
                
                # 调整厚度
                if calculated_surface_temp > surface_temp:
                    thickness += 0.001  # 增加厚度
                else:
                    thickness -= 0.001  # 减少厚度
                
                # 确保厚度在合理范围内
                thickness = max(thickness, 0.001)
            
            return thickness * 1000  # 返回毫米
            
        else:  # 平面形设备
            # 平面设备
            # 从表面温度计算热损失
            heat_loss = h * (surface_temp - ambient_temp)
            
            # 计算保温层热阻
            r_insulation = (equipment_temp - surface_temp) / heat_loss - 1/h
            
            # 计算厚度
            thickness = r_insulation * conductivity
            
            # 确保厚度非负
            thickness = max(thickness, 0)
            
            return thickness * 1000  # 返回毫米
    
    def calculate_anti_condensation(self, equipment_type, size,
                                  ambient_temp, dew_point, equipment_temp, conductivity):
        """防结露计算"""
        # 确保表面温度高于露点温度
        # 设置表面温度为露点温度 + 安全裕度（通常2-3°C）
        surface_temp = dew_point + 2.0
        
        # 假设风速为0.5m/s（室内环境）
        h = self.calculate_surface_heat_transfer_coefficient(0.5)
        
        if equipment_type == "管道或圆筒形设备":
            # 圆筒形设备
            d1 = size  # 管道外径
            
            # 使用迭代法求解厚度
            thickness = 0.01  # 从10mm开始
            
            for _ in range(50):
                d2 = d1 + 2 * thickness
                
                # 计算当前厚度下的表面温度
                r_insulation = math.log(d2 / d1) / (2 * math.pi * conductivity)
                heat_loss = (equipment_temp - ambient_temp) / (r_insulation + 1/(h * math.pi * d2))
                calculated_surface_temp = ambient_temp + heat_loss * (1/(h * math.pi * d2))
                
                # 检查是否收敛
                if abs(calculated_surface_temp - surface_temp) < 0.1:
                    break
                
                # 调整厚度
                if calculated_surface_temp > surface_temp:
                    thickness += 0.001
                else:
                    thickness -= 0.001
                
                thickness = max(thickness, 0.001)
            
            return thickness * 1000
            
        else:  # 平面形设备
            # 平面设备
            # 从表面温度计算热损失
            heat_loss = h * (surface_temp - ambient_temp)
            
            # 计算保温层热阻
            r_insulation = (equipment_temp - surface_temp) / heat_loss - 1/h
            
            # 计算厚度
            thickness = r_insulation * conductivity
            
            # 确保厚度非负
            thickness = max(thickness, 0)
            
            return thickness * 1000
    
    def calculate_by_heat_loss(self, equipment_type, size, insulation_type,
                             ambient_temp, equipment_temp, heat_loss_limit,
                             conductivity, wind_speed):
        """根据最大允许热损失计算厚度"""
        # 计算表面传热系数
        h = self.calculate_surface_heat_transfer_coefficient(wind_speed)
        
        # 温差
        delta_t = abs(equipment_temp - ambient_temp)
        
        if equipment_type == "管道或圆筒形设备":
            # 圆筒形设备
            d1 = size  # 管道外径
            
            # 使用迭代法求解厚度
            thickness = 0.01  # 从10mm开始
            
            for _ in range(50):
                d2 = d1 + 2 * thickness
                
                # 计算当前厚度下的热损失
                r_insulation = math.log(d2 / d1) / (2 * math.pi * conductivity)
                r_surface = 1 / (h * math.pi * d2)
                total_r = r_insulation + r_surface
                
                heat_loss_per_meter = delta_t / total_r  # W/m
                
                # 转换为单位面积热损失 (W/m²)
                heat_loss_per_area = heat_loss_per_meter / (math.pi * d2)
                
                # 检查是否收敛
                if abs(heat_loss_per_area - heat_loss_limit) < 0.1:
                    break
                
                # 调整厚度
                if heat_loss_per_area > heat_loss_limit:
                    thickness += 0.001  # 增加厚度
                else:
                    thickness -= 0.001  # 减少厚度
                
                thickness = max(thickness, 0.001)
            
            return thickness * 1000
            
        else:  # 平面形设备
            # 平面设备
            # 从热损失计算总热阻
            total_r = delta_t / heat_loss_limit
            
            # 计算保温层热阻
            r_insulation = total_r - 1/h
            
            # 计算厚度
            thickness = r_insulation * conductivity
            
            # 确保厚度非负
            thickness = max(thickness, 0)
            
            return thickness * 1000
    
    def calculate_surface_heat_transfer_coefficient(self, wind_speed):
        """计算表面传热系数"""
        # 简化公式：h = 9.4 + 0.052 * ΔT + 3.6 * √v
        # 假设ΔT为20°C进行估算
        estimated_delta_t = 20
        h = 9.4 + 0.052 * estimated_delta_t + 3.6 * math.sqrt(wind_speed)
        return h
    
    def display_results(self, calc_type, thickness, method_name):
        """显示计算结果"""
        # 获取输入参数
        equipment_type = self.equipment_type_combo.currentText()
        insulation_type = self.insulation_type_combo.currentText()
        size = self.size_input.text()
        ambient_temp = self.ambient_temp_input.text()
        equipment_temp = self.equipment_temp_input.text()
        conductivity = self.conductivity_input.text()
        
        # 根据计算类型获取特定参数
        specific_params = ""
        if calc_type == "绝热层经济厚度":
            specific_params = f"""
                    <tr>
                        <td style="padding: 6px;">能量价格:</td>
                        <td style="padding: 6px; color: #2c3e50;">{self.energy_price_input.text()} 元/GJ</td>
                        <td style="padding: 6px;">绝热造价:</td>
                        <td style="padding: 6px; color: #2c3e50;">{self.insulation_cost_input.text()} 元/m³</td>
                    </tr>
                    <tr style="background-color: #f1f1f1;">
                        <td style="padding: 6px;">年运行时间:</td>
                        <td style="padding: 6px; color: #2c3e50;">{self.operation_time_input.text()} 小时</td>
                        <td style="padding: 6px;">年利率:</td>
                        <td style="padding: 6px; color: #2c3e50;">{self.interest_rate_input.text()} %</td>
                    </tr>
                    <tr>
                        <td style="padding: 6px;">计息年限:</td>
                        <td style="padding: 6px; color: #2c3e50;">{self.years_input.text()} 年</td>
                        <td colspan="2"></td>
                    </tr>
            """
        elif calc_type == "表面温度法":
            specific_params = f"""
                    <tr>
                        <td style="padding: 6px;">外表面温度:</td>
                        <td style="padding: 6px; color: #2c3e50;" colspan="3">{self.surface_temp_input.text()} °C</td>
                    </tr>
            """
        elif calc_type == "防结露":
            specific_params = f"""
                    <tr>
                        <td style="padding: 6px;">露点温度:</td>
                        <td style="padding: 6px; color: #2c3e50;" colspan="3">{self.dew_point_input.text()} °C</td>
                    </tr>
            """
        elif calc_type == "热损失法":
            specific_params = f"""
                    <tr>
                        <td style="padding: 6px;">允许热损失量:</td>
                        <td style="padding: 6px; color: #2c3e50;" colspan="3">{self.heat_loss_limit_input.text()} W/m²</td>
                    </tr>
            """
        
        result_html = f"""
        <div style="font-family: 'Segoe UI', Arial, sans-serif;">
            <h2 style="color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px;">
                保温厚度计算结果
            </h2>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                <h3 style="color: #16a085; margin-top: 0;">计算信息</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px; width: 30%; font-weight: bold;">计算类型:</td>
                        <td style="padding: 8px; color: #2c3e50;">{calc_type}</td>
                        <td style="padding: 8px; width: 30%; font-weight: bold;">计算方法:</td>
                        <td style="padding: 8px; color: #2c3e50;">{method_name}</td>
                    </tr>
                    <tr style="background-color: #f1f1f1;">
                        <td style="padding: 8px; font-weight: bold;">设备型式:</td>
                        <td style="padding: 8px; color: #2c3e50;">{equipment_type}</td>
                        <td style="padding: 8px; font-weight: bold;">保温类型:</td>
                        <td style="padding: 8px; color: #2c3e50;">{insulation_type}</td>
                    </tr>
                </table>
            </div>
            
            <div style="background-color: #e8f4fc; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
                <h3 style="color: #3498db; margin-top: 0;">计算结果</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 10px; font-weight: bold; width: 70%;">推荐保温厚度:</td>
                        <td style="padding: 10px;">
                            <span style="font-size: 24px; color: #e74c3c; font-weight: bold;">
                                {thickness:.1f} mm
                            </span>
                        </td>
                    </tr>
                </table>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px;">
                <h3 style="color: #27ae60; margin-top: 0;">输入参数</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 6px; width: 25%;">设备尺寸:</td>
                        <td style="padding: 6px; color: #2c3e50;">{size} mm</td>
                        <td style="padding: 6px; width: 25%;">环境温度:</td>
                        <td style="padding: 6px; color: #2c3e50;">{ambient_temp} °C</td>
                    </tr>
                    <tr style="background-color: #f1f1f1;">
                        <td style="padding: 6px;">设备温度:</td>
                        <td style="padding: 6px; color: #2c3e50;">{equipment_temp} °C</td>
                        <td style="padding: 6px;">导热系数:</td>
                        <td style="padding: 6px; color: #2c3e50;">{conductivity} W/(m·K)</td>
                    </tr>
                    <tr>
                        <td style="padding: 6px;">材料密度:</td>
                        <td style="padding: 6px; color: #2c3e50;">{self.density_input.text()} kg/m³</td>
                        <td style="padding: 6px;">风速:</td>
                        <td style="padding: 6px; color: #2c3e50;">{self.wind_speed_input.text()} m/s</td>
                    </tr>
                    {specific_params}
                </table>
            </div>
            
            <div style="margin-top: 20px; padding: 10px; background-color: #fff3cd; border-left: 4px solid #ffc107; border-radius: 3px;">
                <p style="margin: 0; color: #856404;">
                    <strong>说明:</strong> 计算结果仅供参考，实际工程中应结合具体工况、施工条件和安全系数进行最终设计。
                    建议咨询专业工程师进行审核确认。
                </p>
            </div>
        </div>
        """
        
        self.result_text.setHtml(result_html)
    
    def clear_inputs(self):
        """清空输入"""
        # 重置通用参数
        self.size_input.setText("108")
        self.material_combo.setCurrentIndex(0)
        self.conductivity_input.setText("0.0512")
        self.density_input.setText("170")
        self.ambient_temp_input.setText("20")
        self.wind_speed_input.setText("3")
        self.dew_point_input.setText("22")
        self.equipment_temp_input.setText("200")
        
        # 重置动态参数
        self.setup_dynamic_parameters()
        
        # 清空结果
        self.result_text.clear()
    
    def download_txt_report(self):
        """下载TXT格式计算书"""
        try:
            from PySide6.QtWidgets import QFileDialog
            
            # 检查是否有计算结果
            if not self.result_text.toPlainText().strip():
                QMessageBox.warning(self, "生成失败", "请先进行计算再生成计算书")
                return
            
            # 获取当前结果
            result_text = self.result_text.toPlainText()
            
            # 创建报告内容
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report = f"""工程计算书 - 保温厚度计算
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
计算工具: CalcE 工程计算模块
========================================

{result_text}

---
生成于 CalcE 工程计算模块
"""
            
            # 选择保存路径
            default_name = f"保温厚度计算书_{timestamp}.txt"
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存计算书", default_name, "Text Files (*.txt)"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report)
                QMessageBox.information(self, "下载成功", f"计算书已保存到:\n{file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "下载失败", f"保存计算书时发生错误: {str(e)}")
    
    def generate_pdf_report(self):
        """生成PDF格式计算书"""
        try:
            from PySide6.QtWidgets import QFileDialog
            
            # 检查是否有计算结果
            if not self.result_text.toPlainText().strip():
                QMessageBox.warning(self, "生成失败", "请先进行计算再生成计算书")
                return False
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"保温厚度计算书_{timestamp}.pdf"
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存PDF计算书", default_name, "PDF Files (*.pdf)"
            )
            
            if not file_path:
                return False
            
            # 尝试生成PDF
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
                title = Paragraph("工程计算书 - 保温厚度计算", chinese_style_heading)
                story.append(title)
                story.append(Spacer(1, 0.2*inch))
                
                # 处理结果文本
                result_text = self.result_text.toPlainText()
                processed_content = self.process_content_for_pdf(result_text)
                
                # 添加内容
                for line in processed_content.split('\n'):
                    if line.strip():
                        line = line.replace(' ', '&nbsp;')
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
            "🧊": "",
            "📋": "",
            "📊": "", 
            "🧮": "",
            "💡": "",
            "📤": "",
            "📥": "",
            "🏭": "",
            "🧱": "",
            "🌍": "",
            "📈": "",
            "🚀": "",
            "🗑️": "",
            "📄": "",
            "📊": ""
        }
        
        for emoji, text in replacements.items():
            content = content.replace(emoji, text)
        
        # 替换单位符号
        content = content.replace("m³", "m3")
        content = content.replace("kg/m³", "kg/m3")
        content = content.replace("W/(m·K)", "W/(m.K)")
        
        return content

if __name__ == "__main__":
    # 测试代码
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    widget = InsulationThicknessCalculator()
    widget.resize(1200, 800)
    widget.setWindowTitle("保温厚度计算器 - 紧凑四列布局")
    widget.show()
    
    sys.exit(app.exec())