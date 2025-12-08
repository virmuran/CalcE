from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QLineEdit, QPushButton,
    QComboBox, QGridLayout, QTextEdit, QTabWidget, QMessageBox, QDialog, 
    QDialogButtonBox, QScrollArea, QDoubleSpinBox, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QDoubleValidator
import math
import random
import re
from datetime import datetime


class HeatExchangerAreaCalculator(QWidget):
    """换热器面积计算器 - 左右布局，与压降计算器保持一致"""
    
    def __init__(self, parent=None, data_manager=None):
        super().__init__(parent)
        
        # 使用传入的数据管理器或创建新的
        if data_manager is not None:
            self.data_manager = data_manager
            print("使用共享的数据管理器")
        else:
            self.init_data_manager()
        
        # 流体比热容数据
        self.specific_heat_data = self.setup_specific_heat_data()
        
        # 传热系数数据
        self.heat_transfer_coeff_data = self.setup_heat_transfer_coeff_data()
        
        # 换热器类型数据
        self.exchanger_types_data = self.setup_exchanger_types_data()
        
        # 初始化输入控件字典
        self.input_widgets = {}
        
        self.setup_ui()
        self.setup_calculation_mode(0)  # 默认第一种模式
    
    def init_data_manager(self):
        """初始化数据管理器 - 使用单例模式"""
        try:
            from data_manager import DataManager
            self.data_manager = DataManager.get_instance()
            print("使用共享的数据管理器实例")
        except Exception as e:
            print(f"数据管理器初始化失败: {e}")
            self.data_manager = None
    
    def setup_specific_heat_data(self):
        """设置流体比热容数据"""
        return {
            "水": 4.19,
            "乙醇": 2.4,
            "95%乙醇": 2.51,
            "90%乙醇": 2.72,
            "乙二醇": 2.35,
            "丙三醇": 2.46,
            "导热油": 2.9,
            "乙酸": 2.01,
            "10%乙酸": 4.02,
            "丙酮": 2.15,
            "蜂蜜": 1.42,
            "31%盐酸": 2.51,
            "10%盐酸": 3.14,
            "90%硫酸": 1.47,
            "60%硫酸": 2.18,
            "20%硫酸": 3.52,
            "蔗糖(60%糖浆)": 3.1,
            "蔗糖(40%糖浆)": 2.76,
            "汽油": 2.22,
            "空气": 1.0,
            "氨气": 2.26,
            "苯": 1.36,
            "丁烷": 1.91,
            "二氧化碳": 0.88,
            "一氧化碳": 1.07,
            "氯气": 0.5
        }
    
    def setup_heat_transfer_coeff_data(self):
        """设置传热系数数据"""
        data = []
        
        # 板式换热器数据
        data.append({"hot_fluid": "水", "cold_fluid": "水", "range": (4500.0, 6500.0), "exchanger": "板式换热器"})
        data.append({"hot_fluid": "油", "cold_fluid": "水", "range": (500.0, 700.0), "exchanger": "板式换热器"})
        
        # 螺旋板式换热器数据
        data.append({"hot_fluid": "水", "cold_fluid": "水", "range": (1750.0, 2210.0), "exchanger": "螺旋板式换热器"})
        data.append({"hot_fluid": "废液", "cold_fluid": "水", "range": (1400.0, 2100.0), "exchanger": "螺旋板式换热器"})
        data.append({"hot_fluid": "有机液", "cold_fluid": "有机液", "range": (350.0, 580.0), "exchanger": "螺旋板式换热器"})
        data.append({"hot_fluid": "中焦油", "cold_fluid": "中焦油", "range": (160.0, 200.0), "exchanger": "螺旋板式换热器"})
        data.append({"hot_fluid": "中焦油", "cold_fluid": "水", "range": (270.0, 310.0), "exchanger": "螺旋板式换热器"})
        data.append({"hot_fluid": "高粘度油", "cold_fluid": "水", "range": (230.0, 350.0), "exchanger": "螺旋板式换热器"})
        data.append({"hot_fluid": "油", "cold_fluid": "油", "range": (90.0, 140.0), "exchanger": "螺旋板式换热器"})
        data.append({"hot_fluid": "气体", "cold_fluid": "气体", "range": (30.0, 47.0), "exchanger": "螺旋板式换热器"})
        data.append({"hot_fluid": "变压器油", "cold_fluid": "水", "range": (327.0, 550.0), "exchanger": "螺旋板式换热器"})
        data.append({"hot_fluid": "电解液", "cold_fluid": "水", "range": (600.0, 1900.0), "exchanger": "螺旋板式换热器"})
        data.append({"hot_fluid": "浓碱液", "cold_fluid": "水", "range": (350.0, 650.0), "exchanger": "螺旋板式换热器"})
        
        # 管壳式换热器数据
        data.append({"hot_fluid": "水", "cold_fluid": "芳香族蒸气共沸物", "range": (250.0, 460.0), "exchanger": "管壳式换热器"})
        data.append({"hot_fluid": "空气", "cold_fluid": "水或盐水", "range": (57.0, 280.0), "exchanger": "管壳式换热器"})
        data.append({"hot_fluid": "水或盐水", "cold_fluid": "空气等（压缩）", "range": (110.0, 230.0), "exchanger": "管壳式换热器"})
        data.append({"hot_fluid": "水或盐水", "cold_fluid": "空气等（大气压）", "range": (30.0, 110.0), "exchanger": "管壳式换热器"})
        data.append({"hot_fluid": "道生油", "cold_fluid": "气体", "range": (20.0, 200.0), "exchanger": "管壳式换热器"})
        data.append({"hot_fluid": "水", "cold_fluid": "水", "range": (3000.0, 4500.0), "exchanger": "板翅式换热器"})
        data.append({"hot_fluid": "水", "cold_fluid": "油", "range": (400.0, 600.0), "exchanger": "板翅式换热器"})
        data.append({"hot_fluid": "油", "cold_fluid": "油", "range": (170.0, 350.0), "exchanger": "板翅式换热器"})
        data.append({"hot_fluid": "气体", "cold_fluid": "气体", "range": (70.0, 200.0), "exchanger": "板翅式换热器"})
        data.append({"hot_fluid": "空气", "cold_fluid": "水", "range": (80.0, 200.0), "exchanger": "板翅式换热器"})
        data.append({"hot_fluid": "硫酸", "cold_fluid": "水", "range": (870.0, 870.0), "exchanger": "石墨管壳式换热器-冷却器"})
        data.append({"hot_fluid": "氯气（除水）", "cold_fluid": "水", "range": (35.0, 170.0), "exchanger": "石墨管壳式换热器-冷却器"})
        data.append({"hot_fluid": "焙烧SO2气体", "cold_fluid": "水", "range": (350.0, 470.0), "exchanger": "石墨管壳式换热器-冷却器"})
        
        return data
    
    def setup_exchanger_types_data(self):
        """设置换热器类型数据"""
        return {
            "管壳式换热器": {
                "description": "最常见的换热器类型，适用于多种工况",
                "k_range": (300, 4500),
                "common_fluids": ["水-水", "蒸汽-水", "油-水"]
            },
            "板式换热器": {
                "description": "高效紧凑型换热器，传热系数高",
                "k_range": (4500, 6500),
                "common_fluids": ["水-水", "蒸汽-水"]
            },
            "螺旋板式换热器": {
                "description": "适用于高粘度流体和含有固体颗粒的流体",
                "k_range": (1750, 2210),
                "common_fluids": ["水-水", "废液-水", "油-水"]
            },
            "板翅式换热器": {
                "description": "紧凑型换热器，适用于气体和低粘度流体",
                "k_range": (3000, 4500),
                "common_fluids": ["气体-气体", "空气-水"]
            },
            "沉浸式换热器": {
                "description": "用于加热或冷却储罐中的液体",
                "k_range": (200, 600),
                "common_fluids": ["蒸汽-水", "蒸汽-油"]
            },
            "套管式换热器": {
                "description": "简单的换热器结构，适用于小流量",
                "k_range": (500, 1500),
                "common_fluids": ["水-水", "蒸汽-水"]
            }
        }
    
    def setup_ui(self):
        """设置左右布局的换热器面积计算UI"""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 左侧：输入参数区域 (占2/3宽度)
        left_widget = QWidget()
        left_widget.setMaximumWidth(900)  # 限制最大宽度
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("🔥 换热器面积计算器")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        left_layout.addWidget(title_label)
        
        # 说明文本
        desc_label = QLabel("换热器面积计算器 - 根据热负荷、传热系数和温差计算所需换热面积")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 5px;")
        left_layout.addWidget(desc_label)
        
        # 计算模式选择 - 下拉菜单
        mode_group = QGroupBox("计算模式")
        mode_group.setStyleSheet("""
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
        mode_layout = QHBoxLayout(mode_group)
        
        # 模式选择下拉菜单
        mode_label = QLabel("选择计算模式:")
        mode_label.setStyleSheet("font-weight: bold;")
        mode_layout.addWidget(mode_label)
        
        self.mode_combo = QComboBox()
        modes = [
            ("直接计算法", "已知热负荷、传热系数和温差，直接计算面积"),
            ("流体参数法", "根据流体进出口参数计算热负荷和温差，再计算面积"),
            ("蒸汽加热法", "使用蒸汽加热冷流体，计算所需换热面积")
        ]
        
        for mode_name, tooltip in modes:
            self.mode_combo.addItem(mode_name)
            # 设置tooltip为最后一项
            self.mode_combo.setItemData(self.mode_combo.count()-1, tooltip, Qt.ToolTipRole)
        
        self.mode_combo.setCurrentIndex(0)
        self.mode_combo.currentIndexChanged.connect(self.on_mode_changed)
        self.mode_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: white;
            }
            QComboBox:hover {
                border-color: #3498db;
            }
        """)
        self.mode_combo.setFixedWidth(350)
        
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()
        left_layout.addWidget(mode_group)
        
        # 输入参数组 - 使用GridLayout实现整齐的布局
        input_group = QGroupBox("📥 输入参数")
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
        
        # 使用GridLayout确保整齐排列
        self.input_layout = QGridLayout(input_group)
        self.input_layout.setVerticalSpacing(12)
        self.input_layout.setHorizontalSpacing(10)
        
        left_layout.addWidget(input_group)
        
        # 计算按钮
        calculate_btn = QPushButton("🧮 计算换热面积")
        calculate_btn.setFont(QFont("Arial", 12, QFont.Bold))
        calculate_btn.clicked.connect(self.calculate)
        calculate_btn.setStyleSheet("""
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
        calculate_btn.setMinimumHeight(50)
        left_layout.addWidget(calculate_btn)
        
        # 下载按钮布局
        download_layout = QHBoxLayout()
        download_txt_btn = QPushButton("📄 下载计算书(TXT)")
        download_txt_btn.clicked.connect(self.download_txt_report)
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

        clear_btn = QPushButton("🗑️ 清空")
        clear_btn.clicked.connect(self.clear_inputs)
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

        download_layout.addWidget(clear_btn)
        download_layout.addStretch()
        download_layout.addWidget(download_txt_btn)
        download_layout.addWidget(download_pdf_btn)
        left_layout.addLayout(download_layout)
        
        # 右侧：结果显示区域 (占1/3宽度)
        right_widget = QWidget()
        right_widget.setMinimumWidth(400)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)
        
        # 结果显示
        self.result_group = QGroupBox("📊 计算结果")
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
        main_layout.addWidget(left_widget, 2)  # 左侧占2/3
        main_layout.addWidget(right_widget, 1)  # 右侧占1/3
    
    def on_mode_changed(self, index):
        """处理计算模式变化"""
        self.setup_calculation_mode(index)
    
    def setup_calculation_mode(self, mode_index):
        """设置计算模式的输入界面"""
        # 清除现有输入控件
        for widget in self.input_widgets.values():
            widget.setParent(None)
        self.input_widgets.clear()
        
        # 清除布局中的所有项目
        while self.input_layout.count():
            item = self.input_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
        
        row = 0
        
        # 根据模式设置输入界面
        if mode_index == 0:  # 直接计算法
            self.setup_mode_0_inputs(row)
        elif mode_index == 1:  # 流体参数法
            self.setup_mode_1_inputs(row)
        elif mode_index == 2:  # 蒸汽加热法
            self.setup_mode_2_inputs(row)
    
    def add_input_field(self, row, label_text, widget_type="lineedit", default_value="", placeholder="", validator=None):
        """添加输入字段 - 与压降计算器保持一致的布局"""
        # 标签 - 右对齐，第0列
        label = QLabel(label_text)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label.setStyleSheet("QLabel { font-weight: bold; padding-right: 10px; }")
        label.setFixedWidth(200)  # 固定标签宽度
        self.input_layout.addWidget(label, row, 0)
        
        widget = None
        
        if widget_type == "lineedit":
            widget = QLineEdit()
            if default_value:
                widget.setText(str(default_value))
            if placeholder:
                widget.setPlaceholderText(placeholder)
            if validator:
                widget.setValidator(validator)
            widget.setFixedWidth(400)  # 固定输入框宽度
            self.input_layout.addWidget(widget, row, 1)
            
        elif widget_type == "combobox":
            widget = QComboBox()
            widget.setFixedWidth(250)  # 固定下拉框宽度
            self.input_layout.addWidget(widget, row, 2)  # 放在第2列
        
        # 存储控件引用
        key = label_text.replace(":", "").replace("(", "").replace(")", "").replace(" ", "_").replace("·", "").replace("/", "_").lower()
        self.input_widgets[key] = widget
        
        return widget
    
    def add_cp_input_field(self, row, label_text):
        """添加比热容输入字段 - 左侧输入框，右侧下拉菜单"""
        # 标签 - 右对齐，第0列
        label = QLabel(label_text)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label.setStyleSheet("QLabel { font-weight: bold; padding-right: 10px; }")
        label.setFixedWidth(200)  # 固定标签宽度
        self.input_layout.addWidget(label, row, 0)
        
        # 输入框 - 第1列
        lineedit = QLineEdit()
        lineedit.setPlaceholderText("输入或选择后自动填充")
        lineedit.setValidator(QDoubleValidator(0.1, 100.0, 2))
        lineedit.setFixedWidth(400)
        self.input_layout.addWidget(lineedit, row, 1)
        
        # 下拉菜单 - 第2列
        combobox = QComboBox()
        combobox.addItem("- 请选择流体比热容 -")
        for fluid in self.specific_heat_data.keys():
            combobox.addItem(fluid)
        combobox.setFixedWidth(250)
        combobox.currentTextChanged.connect(lambda text, le=lineedit: self.on_cp_selected(text, le))
        self.input_layout.addWidget(combobox, row, 2)
        
        # 存储控件引用
        key = label_text.replace(":", "").replace("(", "").replace(")", "").replace(" ", "_").replace("·", "").replace("/", "_").lower()
        self.input_widgets[key] = lineedit
        self.input_widgets[f"{key}_combo"] = combobox
        
        return lineedit, combobox
    
    def on_cp_selected(self, text, lineedit):
        """处理比热容选择"""
        if text.startswith("-") or not text.strip():
            return
        
        if text in self.specific_heat_data:
            cp_value = self.specific_heat_data[text]
            lineedit.setText(f"{cp_value:.2f}")
    
    def setup_mode_0_inputs(self, row):
        """模式0：直接计算法"""
        # 热负荷 Q (kW)
        self.add_input_field(row, "热负荷 Q (kW):", "lineedit", "1000", "例如：1000", QDoubleValidator(0.1, 1000000, 1))
        row += 1
        
        # 换热器类型选择
        self.add_input_field(row, "换热器类型:", "combobox")
        exchanger_type_combo = self.input_widgets["换热器类型"]
        exchanger_type_combo.addItem("- 请选择换热器类型 -")
        for exchanger_type in self.exchanger_types_data.keys():
            exchanger_type_combo.addItem(exchanger_type)
        exchanger_type_combo.currentTextChanged.connect(self.on_exchanger_type_selected)
        row += 1
        
        # 总传热系数K W/K.㎡
        self.setup_heat_transfer_coeff_combo(row)
        row += 1
        
        # 热流体进口温度 T1 (°C)
        self.add_input_field(row, "热流体进口T1 (°C):", "lineedit", "90", "例如：90", QDoubleValidator(-273, 1000, 1))
        row += 1
        
        # 热流体出口温度 T2 (°C)
        self.add_input_field(row, "热流体出口T2 (°C):", "lineedit", "60", "例如：60", QDoubleValidator(-273, 1000, 1))
        row += 1
        
        # 冷流体进口温度 t1 (°C)
        self.add_input_field(row, "冷流体进口t1 (°C):", "lineedit", "20", "例如：20", QDoubleValidator(-273, 1000, 1))
        row += 1
        
        # 冷流体出口温度 t2 (°C)
        self.add_input_field(row, "冷流体出口t2 (°C):", "lineedit", "50", "例如：50", QDoubleValidator(-273, 1000, 1))
        row += 1
        
        # 安全系数
        self.add_input_field(row, "安全系数:", "lineedit", "1.15", "例如：1.15", QDoubleValidator(1.0, 2.0, 2))
        row += 1
    
    def setup_mode_1_inputs(self, row):
        """模式1：流体参数法"""
        # 热流体流量 W1 (kg/h)
        self.add_input_field(row, "热流体流量W1 (kg/h):", "lineedit", "5000", "例如：5000", QDoubleValidator(1, 1000000, 1))
        row += 1
        
        # 热流体比热容 Cp1 (kJ/kg·K)
        self.add_cp_input_field(row, "热流体Cp1 (kJ/kg·K):")
        row += 1
        
        # 热流体进口温度 T1 (°C)
        self.add_input_field(row, "热流体进口T1 (°C):", "lineedit", "90", "例如：90", QDoubleValidator(-273, 1000, 1))
        row += 1
        
        # 热流体出口温度 T2 (°C)
        self.add_input_field(row, "热流体出口T2 (°C):", "lineedit", "60", "例如：60", QDoubleValidator(-273, 1000, 1))
        row += 1
        
        # 冷流体流量 W2 (kg/h)
        self.add_input_field(row, "冷流体流量W2 (kg/h):", "lineedit", "10000", "例如：10000", QDoubleValidator(1, 1000000, 1))
        row += 1
        
        # 冷流体比热容 Cp2 (kJ/kg·K)
        self.add_cp_input_field(row, "冷流体Cp2 (kJ/kg·K):")
        row += 1
        
        # 冷流体进口温度 t1 (°C)
        self.add_input_field(row, "冷流体进口t1 (°C):", "lineedit", "20", "例如：20", QDoubleValidator(-273, 1000, 1))
        row += 1
        
        # 冷流体出口温度 t2 (°C)
        self.add_input_field(row, "冷流体出口t2 (°C):", "lineedit", "50", "例如：50", QDoubleValidator(-273, 1000, 1))
        row += 1
        
        # 换热器类型选择
        self.add_input_field(row, "换热器类型:", "combobox")
        exchanger_type_combo = self.input_widgets["换热器类型"]
        exchanger_type_combo.addItem("- 请选择换热器类型 -")
        for exchanger_type in self.exchanger_types_data.keys():
            exchanger_type_combo.addItem(exchanger_type)
        exchanger_type_combo.currentTextChanged.connect(self.on_exchanger_type_selected)
        row += 1
        
        # 总传热系数K W/K.㎡
        self.setup_heat_transfer_coeff_combo(row)
        row += 1
        
        # 安全系数
        self.add_input_field(row, "安全系数:", "lineedit", "1.15", "例如：1.15", QDoubleValidator(1.0, 2.0, 2))
        row += 1
    
    def setup_mode_2_inputs(self, row):
        """模式2：蒸汽加热法"""
        # 蒸汽压力(G) MPa
        self.add_input_field(row, "蒸汽压力(G) MPa:", "lineedit", "0.5", "例如：0.5", QDoubleValidator(0.01, 10.0, 2))
        row += 1
        
        # 蒸汽流量 (kg/h)
        self.add_input_field(row, "蒸汽流量 (kg/h):", "lineedit", "1000", "例如：1000", QDoubleValidator(1, 1000000, 1))
        row += 1
        
        # 冷流体流量 W2 (kg/h)
        self.add_input_field(row, "冷流体流量W2 (kg/h):", "lineedit", "10000", "例如：10000", QDoubleValidator(1, 1000000, 1))
        row += 1
        
        # 冷流体比热容 Cp2 (kJ/kg·K)
        self.add_cp_input_field(row, "冷流体Cp2 (kJ/kg·K):")
        row += 1
        
        # 冷流体进口温度 t1 (°C)
        self.add_input_field(row, "冷流体进口t1 (°C):", "lineedit", "20", "例如：20", QDoubleValidator(-273, 1000, 1))
        row += 1
        
        # 冷流体出口温度 t2 (°C)
        self.add_input_field(row, "冷流体出口t2 (°C):", "lineedit", "60", "例如：60", QDoubleValidator(-273, 1000, 1))
        row += 1
        
        # 换热器类型选择
        self.add_input_field(row, "换热器类型:", "combobox")
        exchanger_type_combo = self.input_widgets["换热器类型"]
        exchanger_type_combo.addItem("- 请选择换热器类型 -")
        for exchanger_type in self.exchanger_types_data.keys():
            exchanger_type_combo.addItem(exchanger_type)
        exchanger_type_combo.currentTextChanged.connect(self.on_exchanger_type_selected)
        row += 1
        
        # 总传热系数K W/K.㎡
        self.setup_heat_transfer_coeff_combo(row)
        row += 1
        
        # 安全系数
        self.add_input_field(row, "安全系数:", "lineedit", "1.15", "例如：1.15", QDoubleValidator(1.0, 2.0, 2))
        row += 1
    
    def on_exchanger_type_selected(self, text):
        """处理换热器类型选择"""
        if text.startswith("-") or not text.strip():
            return
        
        if text in self.exchanger_types_data:
            exchanger_data = self.exchanger_types_data[text]
            k_min, k_max = exchanger_data["k_range"]
            
            # 生成范围内的推荐K值
            recommended_k = (k_min + k_max) / 2
            
            # 如果存在手动输入框，填充推荐值
            if "k_manual" in self.input_widgets:
                self.input_widgets["k_manual"].setText(f"{recommended_k:.1f}")
    
    def setup_heat_transfer_coeff_combo(self, row):
        """设置传热系数下拉菜单"""
        # 标签
        label = QLabel("总传热系数K (W/m²·K):")
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label.setStyleSheet("QLabel { font-weight: bold; padding-right: 10px; }")
        label.setFixedWidth(200)
        self.input_layout.addWidget(label, row, 0)
        
        # 输入框
        manual_input = QLineEdit()
        manual_input.setPlaceholderText("输入或选择后自动填充")
        manual_input.setValidator(QDoubleValidator(1, 10000, 1))
        manual_input.setFixedWidth(400)
        self.input_layout.addWidget(manual_input, row, 1)
        self.input_widgets["k_manual"] = manual_input
        
        # 下拉框
        combo = QComboBox()
        combo.addItem("- 请选择流体组合 -")
        
        # 添加传热系数选项
        for item in self.heat_transfer_coeff_data:
            hot_fluid = item["hot_fluid"]
            cold_fluid = item["cold_fluid"]
            min_val = item["range"][0]
            max_val = item["range"][1]
            exchanger = item["exchanger"]
            
            option_text = f"{hot_fluid} → {cold_fluid} | {min_val:.1f}~{max_val:.1f} W/m²·K | {exchanger}"
            combo.addItem(option_text)
        
        combo.setFixedWidth(250)
        combo.currentTextChanged.connect(self.on_heat_transfer_coeff_selected)
        self.input_layout.addWidget(combo, row, 2)
        self.input_widgets["k_combo"] = combo
        
        return combo
    
    def on_heat_transfer_coeff_selected(self, text):
        """处理传热系数选择"""
        if text.startswith("-") or not text.strip():
            return
        
        # 从选项文本中提取范围
        try:
            # 查找范围部分
            match = re.search(r'(\d+\.?\d*)~(\d+\.?\d*)', text)
            if match:
                min_val = float(match.group(1))
                max_val = float(match.group(2))
                
                # 生成范围内的随机数
                random_k = random.uniform(min_val, max_val)
                
                # 如果存在手动输入框，填充随机值
                if "k_manual" in self.input_widgets:
                    self.input_widgets["k_manual"].setText(f"{random_k:.1f}")
        except Exception as e:
            print(f"解析传热系数范围失败: {e}")
    
    def get_steam_latent_heat(self, pressure_mpa):
        """根据蒸汽压力获取汽化潜热"""
        # 简化计算：压力(MPa)对应的汽化潜热(kJ/kg)
        if pressure_mpa <= 0.1:
            return 2257.0
        elif pressure_mpa <= 0.2:
            return 2202.0
        elif pressure_mpa <= 0.3:
            return 2164.0
        elif pressure_mpa <= 0.4:
            return 2133.0
        elif pressure_mpa <= 0.5:
            return 2108.0
        elif pressure_mpa <= 0.6:
            return 2085.0
        elif pressure_mpa <= 0.7:
            return 2065.0
        elif pressure_mpa <= 0.8:
            return 2047.0
        elif pressure_mpa <= 0.9:
            return 2030.0
        else:  # 1.0 MPa
            return 2015.0
    
    def get_input_value(self, key, default=0.0):
        """获取输入值"""
        if key in self.input_widgets:
            widget = self.input_widgets[key]
            if isinstance(widget, QLineEdit):
                text = widget.text().strip()
                if text:
                    try:
                        return float(text)
                    except:
                        return default
            elif isinstance(widget, QComboBox):
                text = widget.currentText()
                if text in self.specific_heat_data:
                    return self.specific_heat_data[text]
        return default
    
    def calculate(self):
        """执行计算"""
        try:
            # 获取当前选中的模式索引
            mode = self.mode_combo.currentIndex()
            
            if mode == 0:  # 直接计算法
                self.calculate_mode_0()
            elif mode == 1:  # 流体参数法
                self.calculate_mode_1()
            elif mode == 2:  # 蒸汽加热法
                self.calculate_mode_2()
            else:
                QMessageBox.warning(self, "计算错误", "请选择计算模式")
                
        except ValueError as e:
            QMessageBox.critical(self, "输入错误", f"参数输入格式错误: {str(e)}")
        except ZeroDivisionError:
            QMessageBox.critical(self, "计算错误", "参数不能为零")
        except Exception as e:
            QMessageBox.critical(self, "计算错误", f"计算过程中发生错误: {str(e)}")
    
    def calculate_mode_0(self):
        """模式0：直接计算法"""
        # 获取输入值
        Q_heat = self.get_input_value("热负荷_q_kw", 1000)
        T1 = self.get_input_value("热流体进口t1_°c", 90)
        T2 = self.get_input_value("热流体出口t2_°c", 60)
        t1 = self.get_input_value("冷流体进口t1_°c", 20)
        t2 = self.get_input_value("冷流体出口t2_°c", 50)
        K = self.get_input_value("k_manual", 1000)
        safety_factor = self.get_input_value("安全系数", 1.15)
        
        # 验证输入
        if T2 >= T1:
            QMessageBox.warning(self, "输入错误", "热流体出口温度必须小于进口温度")
            return
        
        if t2 <= t1:
            QMessageBox.warning(self, "输入错误", "冷流体出口温度必须大于进口温度")
            return
        
        # 计算对数平均温差
        delta_T1 = T1 - t2
        delta_T2 = T2 - t1
        
        if delta_T1 <= 0 or delta_T2 <= 0:
            QMessageBox.warning(self, "输入错误", "温差计算出现负值，请检查温度参数")
            return
        
        if abs(delta_T1 - delta_T2) < 1e-6:
            LMTD = delta_T1
        else:
            LMTD = (delta_T1 - delta_T2) / math.log(delta_T1 / delta_T2)
        
        # 计算换热面积 (m²)
        # 公式: A = Q * 1000 / (K * ΔTm)   [Q从kW转为W]
        A_theoretical = Q_heat * 1000 / (K * LMTD)
        
        # 考虑安全系数
        A_actual = A_theoretical * safety_factor
        
        # 显示结果
        result = f"""
═══════════════════════════════════════════════════
📋 输入参数
═══════════════════════════════════════════════════

计算模式: {self.mode_combo.currentText()}
热负荷: {Q_heat:.1f} kW
总传热系数: {K:.1f} W/(m²·K)
热流体进口温度: {T1:.1f} °C
热流体出口温度: {T2:.1f} °C
冷流体进口温度: {t1:.1f} °C
冷流体出口温度: {t2:.1f} °C
安全系数: {safety_factor:.2f}

═══════════════════════════════════════════════════
📊 计算结果
═══════════════════════════════════════════════════

热负荷: {Q_heat:.1f} kW
对数平均温差(LMTD): {LMTD:.1f} °C
理论换热面积: {A_theoretical:.2f} m²
考虑安全系数的实际面积: {A_actual:.2f} m²
面积裕量: {(A_actual - A_theoretical):.2f} m²

═══════════════════════════════════════════════════
💡 计算说明
═══════════════════════════════════════════════════

计算公式:
1. 对数平均温差: ΔTm = (ΔT1 - ΔT2) / ln(ΔT1/ΔT2)
   其中: ΔT1 = T1 - t2, ΔT2 = T2 - t1
2. 换热面积: A = Q × 1000 / (K × ΔTm) [m²]
   其中: Q - 热负荷(kW), K - 总传热系数(W/m²·K)
3. 实际面积: A_actual = A × 安全系数

工程建议:
• 安全系数通常取1.1~1.25，根据流体腐蚀性、污垢情况调整
• 实际设计中还需考虑管径、管长、管间距等结构参数
• 重要工程应进行详细的热力计算和结构设计"""
        
        self.result_text.setText(result)
    
    def calculate_mode_1(self):
        """模式1：流体参数法"""
        # 获取输入值
        W1 = self.get_input_value("热流体流量w1_kg/h", 5000)
        Cp1 = self.get_input_value("热流体cp1_kj/kg·k", 4.19)
        T1 = self.get_input_value("热流体进口t1_°c", 90)
        T2 = self.get_input_value("热流体出口t2_°c", 60)
        W2 = self.get_input_value("冷流体流量w2_kg/h", 10000)
        Cp2 = self.get_input_value("冷流体cp2_kj/kg·k", 4.19)
        t1 = self.get_input_value("冷流体进口t1_°c", 20)
        t2 = self.get_input_value("冷流体出口t2_°c", 50)
        K = self.get_input_value("k_manual", 1000)
        safety_factor = self.get_input_value("安全系数", 1.15)
        
        # 验证输入
        if T2 >= T1:
            QMessageBox.warning(self, "输入错误", "热流体出口温度必须小于进口温度")
            return
        
        if t2 <= t1:
            QMessageBox.warning(self, "输入错误", "冷流体出口温度必须大于进口温度")
            return
        
        # 计算热负荷 (kW)
        # Q = W * Cp * ΔT / 3600  [kg/h * kJ/kg·K * °C / 3600 = kW]
        Q_hot = W1 * Cp1 * (T1 - T2) / 3600
        Q_cold = W2 * Cp2 * (t2 - t1) / 3600
        
        # 检查热平衡（理论上应相等，实际可能有误差）
        Q_heat = (Q_hot + Q_cold) / 2  # 取平均值
        
        # 计算对数平均温差
        delta_T1 = T1 - t2
        delta_T2 = T2 - t1
        
        if delta_T1 <= 0 or delta_T2 <= 0:
            QMessageBox.warning(self, "输入错误", "温差计算出现负值，请检查温度参数")
            return
        
        if abs(delta_T1 - delta_T2) < 1e-6:
            LMTD = delta_T1
        else:
            LMTD = (delta_T1 - delta_T2) / math.log(delta_T1 / delta_T2)
        
        # 计算换热面积 (m²)
        A_theoretical = Q_heat * 1000 / (K * LMTD)
        
        # 考虑安全系数
        A_actual = A_theoretical * safety_factor
        
        # 计算热效率
        efficiency = (t2 - t1) / (T1 - t1) * 100
        
        # 显示结果
        result = f"""
═══════════════════════════════════════════════════
📋 输入参数
═══════════════════════════════════════════════════

计算模式: {self.mode_combo.currentText()}
热流体流量: {W1:.0f} kg/h
热流体比热容: {Cp1:.2f} kJ/(kg·K)
热流体进口温度: {T1:.1f} °C
热流体出口温度: {T2:.1f} °C
冷流体流量: {W2:.0f} kg/h
冷流体比热容: {Cp2:.2f} kJ/(kg·K)
冷流体进口温度: {t1:.1f} °C
冷流体出口温度: {t2:.1f} °C
总传热系数: {K:.1f} W/(m²·K)
安全系数: {safety_factor:.2f}

═══════════════════════════════════════════════════
📊 计算结果
═══════════════════════════════════════════════════

热负荷分析:
• 热流体放热量: {Q_hot:.1f} kW
• 冷流体吸热量: {Q_cold:.1f} kW
• 平均热负荷: {Q_heat:.1f} kW
• 热平衡误差: {abs(Q_hot - Q_cold)/Q_heat*100:.1f} %

温差分析:
• 热流体温降: {T1 - T2:.1f} °C
• 冷流体温升: {t2 - t1:.1f} °C
• 对数平均温差(LMTD): {LMTD:.1f} °C

面积计算:
• 理论换热面积: {A_theoretical:.2f} m²
• 考虑安全系数的实际面积: {A_actual:.2f} m²
• 面积裕量: {(A_actual - A_theoretical):.2f} m²

性能指标:
• 换热效率: {efficiency:.1f} %
• 单位面积热负荷: {Q_heat/A_theoretical:.1f} kW/m²

═══════════════════════════════════════════════════
💡 计算说明
═══════════════════════════════════════════════════

计算公式:
1. 热负荷: Q = W × Cp × ΔT / 3600 [kW]
2. 对数平均温差: ΔTm = (ΔT1 - ΔT2) / ln(ΔT1/ΔT2)
3. 换热面积: A = Q × 1000 / (K × ΔTm) [m²]
4. 热效率: η = (t2 - t1) / (T1 - t1) × 100%

工程建议:
• 热平衡误差应小于5%，否则需检查输入参数
• 换热效率一般在60%~90%之间
• 根据流体性质选择合适的传热系数和安全系数"""
        
        self.result_text.setText(result)
    
    def calculate_mode_2(self):
        """模式2：蒸汽加热法"""
        # 获取输入值
        steam_pressure = self.get_input_value("蒸汽压力g_mpa", 0.5)
        steam_flow = self.get_input_value("蒸汽流量_kg/h", 1000)
        W2 = self.get_input_value("冷流体流量w2_kg/h", 10000)
        Cp2 = self.get_input_value("冷流体cp2_kj/kg·k", 4.19)
        t1 = self.get_input_value("冷流体进口t1_°c", 20)
        t2 = self.get_input_value("冷流体出口t2_°c", 60)
        K = self.get_input_value("k_manual", 2000)
        safety_factor = self.get_input_value("安全系数", 1.15)
        
        # 验证输入
        if t2 <= t1:
            QMessageBox.warning(self, "输入错误", "冷流体出口温度必须大于进口温度")
            return
        
        # 获取蒸汽汽化潜热
        latent_heat = self.get_steam_latent_heat(steam_pressure)
        
        # 计算热负荷 (kW)
        # 蒸汽放热量 = 蒸汽流量 × 汽化潜热 / 3600
        Q_steam = steam_flow * latent_heat / 3600
        
        # 冷流体吸热量
        Q_cold = W2 * Cp2 * (t2 - t1) / 3600
        
        # 取较小值作为设计热负荷（保守设计）
        Q_heat = min(Q_steam, Q_cold)
        
        # 蒸汽温度（假设为饱和温度，简化计算）
        # 蒸汽饱和温度与压力的关系：简化计算，实际应查蒸汽表
        if steam_pressure <= 0.1:
            T_steam = 100
        elif steam_pressure <= 0.2:
            T_steam = 120
        elif steam_pressure <= 0.3:
            T_steam = 133
        elif steam_pressure <= 0.4:
            T_steam = 144
        elif steam_pressure <= 0.5:
            T_steam = 152
        elif steam_pressure <= 0.6:
            T_steam = 159
        elif steam_pressure <= 0.7:
            T_steam = 165
        elif steam_pressure <= 0.8:
            T_steam = 170
        elif steam_pressure <= 0.9:
            T_steam = 175
        else:  # 1.0 MPa
            T_steam = 180
        
        # 对数平均温差（蒸汽冷凝温度近似不变）
        delta_T1 = T_steam - t1
        delta_T2 = T_steam - t2
        
        if abs(delta_T1 - delta_T2) < 1e-6:
            LMTD = delta_T1
        else:
            LMTD = (delta_T1 - delta_T2) / math.log(delta_T1 / delta_T2)
        
        # 计算换热面积 (m²)
        A_theoretical = Q_heat * 1000 / (K * LMTD)
        
        # 考虑安全系数
        A_actual = A_theoretical * safety_factor
        
        # 计算蒸汽消耗率
        steam_consumption = Q_heat * 3600 / latent_heat
        
        # 显示结果
        result = f"""
═══════════════════════════════════════════════════
📋 输入参数
═══════════════════════════════════════════════════

计算模式: {self.mode_combo.currentText()}
蒸汽压力: {steam_pressure:.2f} MPa
蒸汽流量: {steam_flow:.0f} kg/h
冷流体流量: {W2:.0f} kg/h
冷流体比热容: {Cp2:.2f} kJ/(kg·K)
冷流体进口温度: {t1:.1f} °C
冷流体出口温度: {t2:.1f} °C
总传热系数: {K:.1f} W/(m²·K)
安全系数: {safety_factor:.2f}

═══════════════════════════════════════════════════
📊 计算结果
═══════════════════════════════════════════════════

蒸汽参数:
• 蒸汽饱和温度: {T_steam:.1f} °C
• 蒸汽汽化潜热: {latent_heat:.1f} kJ/kg
• 蒸汽放热量: {Q_steam:.1f} kW

热负荷分析:
• 冷流体吸热量: {Q_cold:.1f} kW
• 设计热负荷: {Q_heat:.1f} kW
• 蒸汽消耗率: {steam_consumption:.1f} kg/h

温差分析:
• 蒸汽-冷流体温差: {T_steam - t1:.1f} ~ {T_steam - t2:.1f} °C
• 对数平均温差(LMTD): {LMTD:.1f} °C

面积计算:
• 理论换热面积: {A_theoretical:.2f} m²
• 考虑安全系数的实际面积: {A_actual:.2f} m²
• 面积裕量: {(A_actual - A_theoretical):.2f} m²

性能指标:
• 单位面积热负荷: {Q_heat/A_theoretical:.1f} kW/m²
• 蒸汽利用率: {Q_heat/Q_steam*100:.1f} %

═══════════════════════════════════════════════════
💡 计算说明
═══════════════════════════════════════════════════

计算公式:
1. 蒸汽放热量: Q_steam = W_steam × r / 3600 [kW]
2. 冷流体吸热量: Q_cold = W_cold × Cp_cold × (t2 - t1) / 3600 [kW]
3. 设计热负荷: Q = min(Q_steam, Q_cold) [kW]
4. 对数平均温差: ΔTm = (ΔT1 - ΔT2) / ln(ΔT1/ΔT2)
5. 换热面积: A = Q × 1000 / (K × ΔTm) [m²]

工程建议:
• 蒸汽加热器通常采用管壳式或板式换热器
• 蒸汽侧应考虑冷凝水排出和空气排除
• 对于腐蚀性流体，应选用耐腐蚀材料
• 蒸汽压力较高时，需考虑设备承压能力"""
        
        self.result_text.setText(result)
    
    def clear_inputs(self):
        """清空输入"""
        for widget in self.input_widgets.values():
            if isinstance(widget, QLineEdit):
                widget.clear()
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
            elif isinstance(widget, QDoubleSpinBox):
                widget.setValue(0.0)
        
        self.result_text.clear()
    
    def get_project_info(self):
        """获取工程信息"""
        try:
            class ProjectInfoDialog(QDialog):
                def __init__(self, parent=None, default_info=None, report_number=""):
                    super().__init__(parent)
                    self.default_info = default_info or {}
                    self.report_number = report_number
                    self.setWindowTitle("工程信息")
                    self.setFixedSize(400, 350)
                    self.setup_ui()
                    
                def setup_ui(self):
                    layout = QVBoxLayout(self)
                    
                    # 标题
                    title_label = QLabel("请输入工程信息")
                    title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px;")
                    layout.addWidget(title_label)
                    
                    # 公司名称
                    company_layout = QHBoxLayout()
                    company_label = QLabel("公司名称:")
                    company_label.setFixedWidth(80)
                    self.company_input = QLineEdit()
                    self.company_input.setPlaceholderText("例如：XX建筑工程有限公司")
                    self.company_input.setText(self.default_info.get('company_name', ''))
                    company_layout.addWidget(company_label)
                    company_layout.addWidget(self.company_input)
                    layout.addLayout(company_layout)
                    
                    # 工程编号
                    number_layout = QHBoxLayout()
                    number_label = QLabel("工程编号:")
                    number_label.setFixedWidth(80)
                    self.project_number_input = QLineEdit()
                    self.project_number_input.setPlaceholderText("例如：2024-HEAT-001")
                    self.project_number_input.setText(self.default_info.get('project_number', ''))
                    number_layout.addWidget(number_label)
                    number_layout.addWidget(self.project_number_input)
                    layout.addLayout(number_layout)
                    
                    # 工程名称
                    project_layout = QHBoxLayout()
                    project_label = QLabel("工程名称:")
                    project_label.setFixedWidth(80)
                    self.project_input = QLineEdit()
                    self.project_input.setPlaceholderText("例如：化工厂换热系统设计")
                    self.project_input.setText(self.default_info.get('project_name', ''))
                    project_layout.addWidget(project_label)
                    project_layout.addWidget(self.project_input)
                    layout.addLayout(project_layout)
                    
                    # 子项名称
                    subproject_layout = QHBoxLayout()
                    subproject_label = QLabel("子项名称:")
                    subproject_label.setFixedWidth(80)
                    self.subproject_input = QLineEdit()
                    self.subproject_input.setPlaceholderText("例如：主生产区换热器设计")
                    self.subproject_input.setText(self.default_info.get('subproject_name', ''))
                    subproject_layout.addWidget(subproject_label)
                    subproject_layout.addWidget(self.subproject_input)
                    layout.addLayout(subproject_layout)
                    
                    # 计算书编号
                    report_number_layout = QHBoxLayout()
                    report_number_label = QLabel("计算书编号:")
                    report_number_label.setFixedWidth(80)
                    self.report_number_input = QLineEdit()
                    self.report_number_input.setText(self.report_number)
                    report_number_layout.addWidget(report_number_label)
                    report_number_layout.addWidget(self.report_number_input)
                    layout.addLayout(report_number_layout)
                    
                    # 按钮
                    button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                    button_box.accepted.connect(self.accept)
                    button_box.rejected.connect(self.reject)
                    layout.addWidget(button_box)
                    
                def get_info(self):
                    return {
                        'company_name': self.company_input.text().strip(),
                        'project_number': self.project_number_input.text().strip(),
                        'project_name': self.project_input.text().strip(),
                        'subproject_name': self.subproject_input.text().strip(),
                        'report_number': self.report_number_input.text().strip()
                    }
            
            # 从数据管理器获取共享的项目信息
            saved_info = {}
            if self.data_manager:
                saved_info = self.data_manager.get_project_info()
            
            # 获取下一个报告编号
            report_number = ""
            if self.data_manager:
                report_number = self.data_manager.get_next_report_number("HEAT")
            
            dialog = ProjectInfoDialog(self, saved_info, report_number)
            if dialog.exec() == QDialog.Accepted:
                info = dialog.get_info()
                # 验证必填字段
                if not info['project_name']:
                    QMessageBox.warning(self, "输入错误", "工程名称不能为空")
                    return self.get_project_info()  # 重新弹出对话框
                
                # 保存项目信息到数据管理器
                if self.data_manager:
                    info_to_save = {
                        'company_name': info['company_name'],
                        'project_number': info['project_number'],
                        'project_name': info['project_name'],
                        'subproject_name': info['subproject_name']
                    }
                    self.data_manager.update_project_info(info_to_save)
                    print("项目信息已保存")
                
                return info
            else:
                return None  # 用户取消了
                    
        except Exception as e:
            print(f"获取工程信息失败: {e}")
            return None
    
    def generate_report(self):
        """生成计算书"""
        try:
            # 获取当前结果文本
            result_text = self.result_text.toPlainText()
            
            # 更宽松的检查条件
            if not result_text or ("计算结果" not in result_text and "输入参数" not in result_text):
                QMessageBox.warning(self, "生成失败", "请先进行计算再生成计算书")
                return None
                
            # 获取工程信息
            project_info = self.get_project_info()
            if not project_info:
                return None  # 用户取消了输入
            
            # 获取当前计算模式
            current_mode = self.mode_combo.currentText()
            
            # 添加报告头信息
            report = f"""工程计算书 - 换热器面积计算
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
计算工具: TofuSoft 工程计算模块
计算模式: {current_mode}
========================================

"""
            report += result_text
            
            # 添加工程信息部分
            report += f"""
══════════
📋 工程信息
══════════

    公司名称: {project_info['company_name']}
    工程编号: {project_info['project_number']}
    工程名称: {project_info['project_name']}
    子项名称: {project_info['subproject_name']}
    计算日期: {datetime.now().strftime('%Y-%m-%d')}

══════════
🏷️ 计算书标识
══════════

    计算书编号: {project_info['report_number']}
    版本: 1.0
    状态: 设计计算书

══════════
📝 备注说明
══════════

    1. 本计算书基于换热器设计原理及相关标准规范
    2. 计算结果仅供参考，实际设计需考虑详细工况
    3. 重要工程参数应经专业工程师审核确认
    4. 计算条件变更时应重新进行计算
    5. 换热器选型应考虑流体性质、压力等级、材料等因素
    6. 安全系数选择应根据流体腐蚀性、污垢情况等确定

---
生成于 TofuSoft 工程计算模块
"""
            return report
            
        except Exception as e:
            print(f"生成计算书失败: {e}")
            return None
    
    def download_txt_report(self):
        """下载TXT格式计算书"""
        try:
            report_content = self.generate_report()
            if report_content is None:
                return
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"换热器面积计算书_{timestamp}.txt"
            
            from PySide6.QtWidgets import QFileDialog
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存计算书", default_name, "Text Files (*.txt)"
            )
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                QMessageBox.information(self, "下载成功", f"计算书已保存到:\n{file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "下载失败", f"保存计算书时发生错误: {str(e)}")
    
    def generate_pdf_report(self):
        """生成PDF格式计算书"""
        try:
            # 直接调用 generate_report，它内部会进行检查
            report_content = self.generate_report()
            if report_content is None:  # 如果返回None，说明检查失败或用户取消
                return False
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"换热器面积计算书_{timestamp}.pdf"
            file_path, _ = QFileDialog.getSaveFileName(
                self, "保存PDF计算书", default_name, "PDF Files (*.pdf)"
            )
            
            if not file_path:
                return False
                
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
                    # 尝试注册常见的中文字体
                    font_paths = [
                        # Windows 字体路径
                        "C:/Windows/Fonts/simhei.ttf",  # 黑体
                        "C:/Windows/Fonts/simsun.ttc",  # 宋体
                        "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
                        # macOS 字体路径
                        "/Library/Fonts/Arial Unicode.ttf",
                        "/System/Library/Fonts/Arial.ttf",
                        # Linux 字体路径
                        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
                        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
                    ]
                    
                    chinese_font_registered = False
                    for font_path in font_paths:
                        if os.path.exists(font_path):
                            try:
                                if "simhei" in font_path.lower():
                                    pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                                    chinese_font_registered = True
                                    break
                                elif "simsun" in font_path.lower():
                                    pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                                    chinese_font_registered = True
                                    break
                                elif "msyh" in font_path.lower() or "microsoftyahei" in font_path.lower():
                                    pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                                    chinese_font_registered = True
                                    break
                                elif "arial unicode" in font_path.lower():
                                    pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                                    chinese_font_registered = True
                                    break
                            except:
                                continue
                    
                    if not chinese_font_registered:
                        # 如果没有找到系统字体，尝试使用 ReportLab 的默认字体（可能不支持中文）
                        pdfmetrics.registerFont(TTFont('ChineseFont', 'Helvetica'))
                except:
                    # 字体注册失败，使用默认字体
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
                title = Paragraph("工程计算书 - 换热器面积计算", chinese_style_heading)
                story.append(title)
                story.append(Spacer(1, 0.2*inch))
                
                # 处理报告内容，替换特殊字符和表情
                processed_content = self.process_content_for_pdf(report_content)
                
                # 添加内容
                for line in processed_content.split('\n'):
                    if line.strip():
                        # 处理特殊字符和空格
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
            "📏": "",
            "🌪️": "",
            "💨": "",
            "🌫️": "",
            "⚡": "",
            "💧": "",
            "🔄": "",
            "🌬️": "",
            "🔧": "",
            "🚒": "",
            "⚖️": "",
            "🧊": "",
            "🧪": "",
            "🔩": "",
            "🛡️": "",
            "🔥": "",
            "⚗️": "",
            "🚨": "",
            "⚛️": "",
            "❄️": "",
            "📄": "",
            "📊": "",
            "•": "",
            "🏷️": "",
            "📝": ""
        }
        
        # 替换表情图标
        for emoji, text in replacements.items():
            content = content.replace(emoji, text)
        
        # 替换单位符号
        content = content.replace("m³", "m3")
        content = content.replace("g/100g", "g/100g")
        content = content.replace("kg/m³", "kg/m3")
        content = content.replace("Nm³/h", "Nm3/h")
        content = content.replace("Pa·s", "Pa.s")
        content = content.replace("kJ/(kg·K)", "kJ/(kg.K)")
        content = content.replace("W/(K·m²)", "W/(K.m2)")
        
        return content


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    calculator = HeatExchangerAreaCalculator()
    calculator.resize(1200, 800)
    calculator.setWindowTitle("换热器面积计算器")
    calculator.show()
    
    sys.exit(app.exec())