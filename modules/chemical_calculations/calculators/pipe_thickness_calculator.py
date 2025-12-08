from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGroupBox, QTextEdit, QComboBox, QMessageBox, QFrame,
    QScrollArea, QDialog, QSpinBox, QButtonGroup, QGridLayout,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QDoubleValidator
import math


class MaterialDatabaseDialog(QDialog):
    """材料数据库对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("材料许用应力数据库")
        self.setModal(True)
        self.resize(800, 600)
        self.setup_ui()
        self.load_material_data()
    
    def setup_ui(self):
        """设置材料数据库UI"""
        layout = QVBoxLayout(self)
        
        # 说明文本
        description = QLabel("金属材料许用应力数据库 (单位: MPa)")
        description.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px;")
        layout.addWidget(description)
        
        # 创建表格
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #dcdcdc;
                background-color: white;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #f0f0f0;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        layout.addWidget(self.table)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def load_material_data(self):
        """加载材料数据"""
        # 材料数据库 - 许用应力 (MPa)
        materials = [
            # 碳钢
            ["Q235-A", "碳钢", "常温", 113, "GB/T 700", "一般结构用钢"],
            ["Q235-B", "碳钢", "常温", 113, "GB/T 700", "一般结构用钢"],
            ["Q235-C", "碳钢", "常温", 113, "GB/T 700", "一般结构用钢"],
            ["Q235-D", "碳钢", "常温", 113, "GB/T 700", "一般结构用钢"],
            ["20", "碳钢", "常温", 130, "GB/T 699", "优质碳素结构钢"],
            ["20", "碳钢", "100°C", 130, "GB/T 699", "优质碳素结构钢"],
            ["20", "碳钢", "200°C", 130, "GB/T 699", "优质碳素结构钢"],
            ["20", "碳钢", "300°C", 130, "GB/T 699", "优质碳素结构钢"],
            ["20", "碳钢", "350°C", 122, "GB/T 699", "优质碳素结构钢"],
            ["20", "碳钢", "400°C", 111, "GB/T 699", "优质碳素结构钢"],
            ["20", "碳钢", "425°C", 104, "GB/T 699", "优质碳素结构钢"],
            ["20", "碳钢", "450°C", 97, "GB/T 699", "优质碳素结构钢"],
            
            # 不锈钢
            ["304", "奥氏体不锈钢", "常温", 137, "GB/T 1220", "通用不锈钢"],
            ["304", "奥氏体不锈钢", "100°C", 137, "GB/T 1220", "通用不锈钢"],
            ["304", "奥氏体不锈钢", "200°C", 137, "GB/T 1220", "通用不锈钢"],
            ["304", "奥氏体不锈钢", "300°C", 137, "GB/T 1220", "通用不锈钢"],
            ["304", "奥氏体不锈钢", "400°C", 132, "GB/T 1220", "通用不锈钢"],
            ["304", "奥氏体不锈钢", "500°C", 121, "GB/T 1220", "通用不锈钢"],
            ["304", "奥氏体不锈钢", "600°C", 103, "GB/T 1220", "通用不锈钢"],
            
            ["316", "奥氏体不锈钢", "常温", 130, "GB/T 1220", "耐腐蚀不锈钢"],
            ["316", "奥氏体不锈钢", "100°C", 130, "GB/T 1220", "耐腐蚀不锈钢"],
            ["316", "奥氏体不锈钢", "200°C", 130, "GB/T 1220", "耐腐蚀不锈钢"],
            ["316", "奥氏体不锈钢", "300°C", 130, "GB/T 1220", "耐腐蚀不锈钢"],
            ["316", "奥氏体不锈钢", "400°C", 125, "GB/T 1220", "耐腐蚀不锈钢"],
            ["316", "奥氏体不锈钢", "500°C", 116, "GB/T 1220", "耐腐蚀不锈钢"],
            ["316", "奥氏体不锈钢", "600°C", 101, "GB/T 1220", "耐腐蚀不锈钢"],
            
            # 合金钢
            ["16Mn", "低合金钢", "常温", 170, "GB/T 1591", "低合金高强度钢"],
            ["16Mn", "低合金钢", "100°C", 170, "GB/T 1591", "低合金高强度钢"],
            ["16Mn", "低合金钢", "200°C", 170, "GB/T 1591", "低合金高强度钢"],
            ["16Mn", "低合金钢", "300°C", 170, "GB/T 1591", "低合金高强度钢"],
            ["16Mn", "低合金钢", "350°C", 170, "GB/T 1591", "低合金高强度钢"],
            ["16Mn", "低合金钢", "400°C", 163, "GB/T 1591", "低合金高强度钢"],
            ["16Mn", "低合金钢", "450°C", 150, "GB/T 1591", "低合金高强度钢"],
            
            ["15CrMo", "铬钼钢", "常温", 150, "GB/T 3077", "耐热钢"],
            ["15CrMo", "铬钼钢", "100°C", 150, "GB/T 3077", "耐热钢"],
            ["15CrMo", "铬钼钢", "200°C", 150, "GB/T 3077", "耐热钢"],
            ["15CrMo", "铬钼钢", "300°C", 150, "GB/T 3077", "耐热钢"],
            ["15CrMo", "铬钼钢", "400°C", 150, "GB/T 3077", "耐热钢"],
            ["15CrMo", "铬钼钢", "450°C", 147, "GB/T 3077", "耐热钢"],
            ["15CrMo", "铬钼钢", "500°C", 140, "GB/T 3077", "耐热钢"],
            ["15CrMo", "铬钼钢", "550°C", 128, "GB/T 3077", "耐热钢"],
        ]
        
        # 设置表格
        headers = ["材料牌号", "材料类型", "温度", "许用应力(MPa)", "标准", "说明"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(materials))
        
        # 填充数据
        for row, material in enumerate(materials):
            for col, value in enumerate(material):
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)
        
        # 调整列宽
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        header.setStretchLastSection(True)


class PipeThicknessCalculator(QWidget):
    """管道壁厚计算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # 先初始化 material_database
        self.material_database = {}
        self.setup_material_database()  # 先调用这个
        self.setup_ui()  # 然后调用 setup_ui
    
    def setup_ui(self):
        """设置管道壁厚计算UI"""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 左侧：输入参数区域
        left_widget = QWidget()
        left_widget.setMaximumWidth(900)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(15)
        
        # 说明文本
        description = QLabel(
            "根据ASME B31.3等标准计算管道壁厚，包含金属材料许用应力数据库。"
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 5px;")
        left_layout.addWidget(description)
        
        # 计算标准选择
        standard_group = QGroupBox("📏 计算标准")
        standard_group.setStyleSheet("""
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
        standard_layout = QHBoxLayout(standard_group)
        
        self.standard_combo = QComboBox()
        self.standard_combo.addItems([
            "ASME B31.3 - 工艺管道",
            "GB/T 20801 - 压力管道规范",
            "ASME B31.1 - 动力管道",
            "SH/T 3059 - 石油化工管道设计"
        ])
        self.standard_combo.setFixedWidth(300)
        standard_layout.addWidget(self.standard_combo)
        standard_layout.addStretch()
        
        left_layout.addWidget(standard_group)
        
        # 输入参数组
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
        
        input_layout = QGridLayout(input_group)
        input_layout.setVerticalSpacing(12)
        input_layout.setHorizontalSpacing(10)
        
        label_style = """
            QLabel {
                font-weight: bold;
                padding-right: 10px;
            }
        """
        
        input_width = 400
        combo_width = 250
        
        row = 0
        
        # 设计压力
        pressure_label = QLabel("设计压力 (MPa):")
        pressure_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        pressure_label.setStyleSheet(label_style)
        input_layout.addWidget(pressure_label, row, 0)
        
        self.pressure_input = QLineEdit()
        self.pressure_input.setPlaceholderText("例如: 1.0")
        self.pressure_input.setValidator(QDoubleValidator(0.01, 100.0, 3))
        self.pressure_input.setText("1.0")
        self.pressure_input.setFixedWidth(input_width)
        input_layout.addWidget(self.pressure_input, row, 1)
        
        row += 1
        
        # 设计温度
        temp_label = QLabel("设计温度 (°C):")
        temp_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        temp_label.setStyleSheet(label_style)
        input_layout.addWidget(temp_label, row, 0)
        
        self.temp_input = QLineEdit()
        self.temp_input.setPlaceholderText("例如: 150")
        self.temp_input.setValidator(QDoubleValidator(-200.0, 800.0, 1))
        self.temp_input.setText("150")
        self.temp_input.setFixedWidth(input_width)
        input_layout.addWidget(self.temp_input, row, 1)
        
        row += 1
        
        # 管道外径
        diameter_label = QLabel("管道外径 (mm):")
        diameter_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        diameter_label.setStyleSheet(label_style)
        input_layout.addWidget(diameter_label, row, 0)
        
        self.diameter_input = QLineEdit()
        self.diameter_input.setPlaceholderText("例如: 114.3")
        self.diameter_input.setValidator(QDoubleValidator(1.0, 2000.0, 2))
        self.diameter_input.setText("114.3")
        self.diameter_input.setFixedWidth(input_width)
        input_layout.addWidget(self.diameter_input, row, 1)
        
        row += 1
        
        # 材料选择
        material_label = QLabel("管道材料:")
        material_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        material_label.setStyleSheet(label_style)
        input_layout.addWidget(material_label, row, 0)
        
        self.material_combo = QComboBox()
        self.setup_material_options()
        self.material_combo.setFixedWidth(combo_width)
        self.material_combo.currentTextChanged.connect(self.on_material_changed)
        input_layout.addWidget(self.material_combo, row, 1)
        
        # 材料数据库按钮
        self.material_db_btn = QPushButton("📚 材料数据库")
        self.material_db_btn.setFixedWidth(120)
        self.material_db_btn.clicked.connect(self.show_material_database)
        self.material_db_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        input_layout.addWidget(self.material_db_btn, row, 2)
        
        row += 1
        
        # 许用应力
        stress_label = QLabel("许用应力 (MPa):")
        stress_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        stress_label.setStyleSheet(label_style)
        input_layout.addWidget(stress_label, row, 0)
        
        self.stress_input = QLineEdit()
        self.stress_input.setPlaceholderText("自动填充")
        self.stress_input.setReadOnly(True)
        self.stress_input.setFixedWidth(input_width)
        input_layout.addWidget(self.stress_input, row, 1)
        
        row += 1
        
        # 焊缝系数
        weld_label = QLabel("焊缝系数:")
        weld_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        weld_label.setStyleSheet(label_style)
        input_layout.addWidget(weld_label, row, 0)
        
        self.weld_input = QLineEdit()
        self.weld_input.setPlaceholderText("例如: 1.0")
        self.weld_input.setValidator(QDoubleValidator(0.1, 1.0, 3))
        self.weld_input.setText("1.0")
        self.weld_input.setFixedWidth(input_width)
        input_layout.addWidget(self.weld_input, row, 1)
        
        self.weld_combo = QComboBox()
        self.weld_combo.addItems([
            "1.0 - 无缝钢管",
            "0.95 - 纵缝焊接管",
            "0.85 - 螺旋焊接管",
            "0.7 - 铸造管"
        ])
        self.weld_combo.setFixedWidth(combo_width)
        self.weld_combo.currentTextChanged.connect(self.on_weld_factor_changed)
        input_layout.addWidget(self.weld_combo, row, 2)
        
        row += 1
        
        # 腐蚀余量
        corrosion_label = QLabel("腐蚀余量 (mm):")
        corrosion_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        corrosion_label.setStyleSheet(label_style)
        input_layout.addWidget(corrosion_label, row, 0)
        
        self.corrosion_input = QLineEdit()
        self.corrosion_input.setPlaceholderText("例如: 1.5")
        self.corrosion_input.setValidator(QDoubleValidator(0.0, 10.0, 2))
        self.corrosion_input.setText("1.5")
        self.corrosion_input.setFixedWidth(input_width)
        input_layout.addWidget(self.corrosion_input, row, 1)
        
        self.corrosion_combo = QComboBox()
        self.corrosion_combo.addItems([
            "0.5 mm - 无腐蚀介质",
            "1.0 mm - 轻微腐蚀",
            "1.5 mm - 一般腐蚀",
            "2.0 mm - 中等腐蚀", 
            "3.0 mm - 严重腐蚀"
        ])
        self.corrosion_combo.setFixedWidth(combo_width)
        self.corrosion_combo.currentTextChanged.connect(self.on_corrosion_changed)
        input_layout.addWidget(self.corrosion_combo, row, 2)
        
        row += 1
        
        # 负偏差
        tolerance_label = QLabel("负偏差 (%):")
        tolerance_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        tolerance_label.setStyleSheet(label_style)
        input_layout.addWidget(tolerance_label, row, 0)
        
        self.tolerance_input = QLineEdit()
        self.tolerance_input.setPlaceholderText("例如: 12.5")
        self.tolerance_input.setValidator(QDoubleValidator(0.0, 20.0, 2))
        self.tolerance_input.setText("12.5")
        self.tolerance_input.setFixedWidth(input_width)
        input_layout.addWidget(self.tolerance_input, row, 1)
        
        self.tolerance_combo = QComboBox()
        self.tolerance_combo.addItems([
            "12.5% - 标准偏差",
            "10.0% - 较小偏差",
            "15.0% - 较大偏差",
            "0.0% - 无偏差"
        ])
        self.tolerance_combo.setFixedWidth(combo_width)
        self.tolerance_combo.currentTextChanged.connect(self.on_tolerance_changed)
        input_layout.addWidget(self.tolerance_combo, row, 2)
        
        left_layout.addWidget(input_group)
        
        # 计算按钮
        calculate_btn = QPushButton("🧮 计算壁厚")
        calculate_btn.setFont(QFont("Arial", 12, QFont.Bold))
        calculate_btn.clicked.connect(self.calculate_thickness)
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
        
        # 右侧：结果显示区域
        right_widget = QWidget()
        right_widget.setMinimumWidth(400)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)
        
        # 结果显示
        self.result_group = QGroupBox("📤 计算结果")
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
        main_layout.addWidget(left_widget, 2)
        main_layout.addWidget(right_widget, 1)
        
        # 初始材料选择
        self.on_material_changed(self.material_combo.currentText())
    
    def setup_material_database(self):
        """设置材料数据库"""
        # 材料许用应力数据库 (MPa)
        self.material_database = {
            # 碳钢
            "Q235-A (20°C)": {"stress": 113, "type": "碳钢", "temp": 20},
            "Q235-A (100°C)": {"stress": 113, "type": "碳钢", "temp": 100},
            "Q235-A (200°C)": {"stress": 113, "type": "碳钢", "temp": 200},
            "20# (20°C)": {"stress": 130, "type": "碳钢", "temp": 20},
            "20# (100°C)": {"stress": 130, "type": "碳钢", "temp": 100},
            "20# (200°C)": {"stress": 130, "type": "碳钢", "temp": 200},
            "20# (300°C)": {"stress": 130, "type": "碳钢", "temp": 300},
            "20# (350°C)": {"stress": 122, "type": "碳钢", "temp": 350},
            "20# (400°C)": {"stress": 111, "type": "碳钢", "temp": 400},
            "20# (425°C)": {"stress": 104, "type": "碳钢", "temp": 425},
            "20# (450°C)": {"stress": 97, "type": "碳钢", "temp": 450},
            
            # 不锈钢
            "304 (20°C)": {"stress": 137, "type": "不锈钢", "temp": 20},
            "304 (100°C)": {"stress": 137, "type": "不锈钢", "temp": 100},
            "304 (200°C)": {"stress": 137, "type": "不锈钢", "temp": 200},
            "304 (300°C)": {"stress": 137, "type": "不锈钢", "temp": 300},
            "304 (400°C)": {"stress": 132, "type": "不锈钢", "temp": 400},
            "304 (500°C)": {"stress": 121, "type": "不锈钢", "temp": 500},
            "304 (600°C)": {"stress": 103, "type": "不锈钢", "temp": 600},
            
            "316 (20°C)": {"stress": 130, "type": "不锈钢", "temp": 20},
            "316 (100°C)": {"stress": 130, "type": "不锈钢", "temp": 100},
            "316 (200°C)": {"stress": 130, "type": "不锈钢", "temp": 200},
            "316 (300°C)": {"stress": 130, "type": "不锈钢", "temp": 300},
            "316 (400°C)": {"stress": 125, "type": "不锈钢", "temp": 400},
            "316 (500°C)": {"stress": 116, "type": "不锈钢", "temp": 500},
            "316 (600°C)": {"stress": 101, "type": "不锈钢", "temp": 600},
            
            # 合金钢
            "16Mn (20°C)": {"stress": 170, "type": "合金钢", "temp": 20},
            "16Mn (100°C)": {"stress": 170, "type": "合金钢", "temp": 100},
            "16Mn (200°C)": {"stress": 170, "type": "合金钢", "temp": 200},
            "16Mn (300°C)": {"stress": 170, "type": "合金钢", "temp": 300},
            "16Mn (350°C)": {"stress": 170, "type": "合金钢", "temp": 350},
            "16Mn (400°C)": {"stress": 163, "type": "合金钢", "temp": 400},
            "16Mn (450°C)": {"stress": 150, "type": "合金钢", "temp": 450},
            
            "15CrMo (20°C)": {"stress": 150, "type": "合金钢", "temp": 20},
            "15CrMo (100°C)": {"stress": 150, "type": "合金钢", "temp": 100},
            "15CrMo (200°C)": {"stress": 150, "type": "合金钢", "temp": 200},
            "15CrMo (300°C)": {"stress": 150, "type": "合金钢", "temp": 300},
            "15CrMo (400°C)": {"stress": 150, "type": "合金钢", "temp": 400},
            "15CrMo (450°C)": {"stress": 147, "type": "合金钢", "temp": 450},
            "15CrMo (500°C)": {"stress": 140, "type": "合金钢", "temp": 500},
            "15CrMo (550°C)": {"stress": 128, "type": "合金钢", "temp": 550},
        }
    
    def setup_material_options(self):
        """设置材料选项"""
        materials = [
            "20# (20°C) - 优质碳素结构钢",
            "20# (100°C) - 优质碳素结构钢", 
            "20# (200°C) - 优质碳素结构钢",
            "20# (300°C) - 优质碳素结构钢",
            "20# (350°C) - 优质碳素结构钢",
            "20# (400°C) - 优质碳素结构钢",
            "Q235-A (20°C) - 一般结构用钢",
            "304 (20°C) - 通用不锈钢",
            "304 (300°C) - 通用不锈钢",
            "304 (500°C) - 通用不锈钢", 
            "316 (20°C) - 耐腐蚀不锈钢",
            "316 (300°C) - 耐腐蚀不锈钢",
            "16Mn (20°C) - 低合金高强度钢",
            "16Mn (300°C) - 低合金高强度钢",
            "15CrMo (20°C) - 耐热钢",
            "15CrMo (500°C) - 耐热钢"
        ]
        self.material_combo.addItems(materials)
    
    def on_material_changed(self, text):
        """处理材料选择变化"""
        material_key = text.split(" - ")[0]
        if material_key in self.material_database:
            stress = self.material_database[material_key]["stress"]
            self.stress_input.setText(f"{stress}")
    
    def on_weld_factor_changed(self, text):
        """处理焊缝系数变化"""
        try:
            weld_factor = float(text.split(" - ")[0])
            self.weld_input.setText(f"{weld_factor}")
        except:
            pass
    
    def on_corrosion_changed(self, text):
        """处理腐蚀余量变化"""
        try:
            corrosion = float(text.split(" ")[0])
            self.corrosion_input.setText(f"{corrosion}")
        except:
            pass
    
    def on_tolerance_changed(self, text):
        """处理负偏差变化"""
        try:
            tolerance = float(text.split("%")[0])
            self.tolerance_input.setText(f"{tolerance}")
        except:
            pass
    
    def show_material_database(self):
        """显示材料数据库"""
        dialog = MaterialDatabaseDialog(self)
        dialog.exec()
    
    def calculate_thickness(self):
        """计算管道壁厚"""
        try:
            # 获取输入值
            standard = self.standard_combo.currentText()
            design_pressure = float(self.pressure_input.text())  # MPa
            design_temp = float(self.temp_input.text())  # °C
            outer_diameter = float(self.diameter_input.text())  # mm
            allowable_stress = float(self.stress_input.text())  # MPa
            weld_factor = float(self.weld_input.text())
            corrosion_allowance = float(self.corrosion_input.text())  # mm
            tolerance = float(self.tolerance_input.text()) / 100  # 转换为小数
            
            # 验证输入
            if not all([design_pressure, outer_diameter, allowable_stress, weld_factor]):
                QMessageBox.warning(self, "输入错误", "请填写所有必需参数")
                return
            
            if design_pressure <= 0 or outer_diameter <= 0 or allowable_stress <= 0:
                QMessageBox.warning(self, "输入错误", "压力、直径和许用应力必须大于0")
                return
            
            # 根据ASME B31.3公式计算理论壁厚
            # t = P * D / (2 * S * E + 2 * P * Y) + C
            # 其中Y为系数，对于铁素体钢，温度低于482°C时取0.4
            
            if design_temp <= 482:
                Y_factor = 0.4
            else:
                Y_factor = 0.7
            
            # 计算理论壁厚 (mm)
            theoretical_thickness = (design_pressure * outer_diameter) / \
                                  (2 * allowable_stress * weld_factor + 2 * design_pressure * Y_factor)
            
            # 计算设计壁厚 (包含腐蚀余量)
            design_thickness = theoretical_thickness + corrosion_allowance
            
            # 计算名义壁厚 (考虑负偏差)
            nominal_thickness = design_thickness / (1 - tolerance)
            
            # 选择标准管壁厚
            standard_thickness = self.select_standard_thickness(nominal_thickness)
            
            # 计算实际应力
            actual_stress = design_pressure * (outer_diameter - 2 * standard_thickness * tolerance) / \
                          (2 * standard_thickness * weld_factor)
            
            # 安全系数
            safety_factor = allowable_stress / actual_stress if actual_stress > 0 else 0
            
            # 显示结果
            result = self.format_results(
                standard, design_pressure, design_temp, outer_diameter, 
                allowable_stress, weld_factor, corrosion_allowance, tolerance,
                theoretical_thickness, design_thickness, nominal_thickness,
                standard_thickness, actual_stress, safety_factor, Y_factor
            )
            
            self.result_text.setText(result)
            
        except ValueError as e:
            QMessageBox.critical(self, "计算错误", f"参数输入格式错误: {str(e)}")
        except ZeroDivisionError:
            QMessageBox.critical(self, "计算错误", "参数不能为零")
        except Exception as e:
            QMessageBox.critical(self, "计算错误", f"计算过程中发生错误: {str(e)}")
    
    def select_standard_thickness(self, required_thickness):
        """选择标准壁厚"""
        # 标准壁厚系列 (mm)
        standard_thicknesses = [
            2.0, 2.3, 2.6, 2.9, 3.2, 3.6, 4.0, 4.5, 5.0, 5.6, 6.3, 
            7.1, 8.0, 8.8, 10.0, 11.0, 12.5, 14.2, 16.0, 17.5, 20.0,
            22.2, 25.0, 28.0, 30.0, 32.0, 36.0, 40.0, 45.0, 50.0
        ]
        
        for thickness in standard_thicknesses:
            if thickness >= required_thickness:
                return thickness
        
        # 如果需要的壁厚超过最大值，返回最大值
        return standard_thicknesses[-1]
    
    def format_results(self, standard, design_pressure, design_temp, outer_diameter,
                      allowable_stress, weld_factor, corrosion_allowance, tolerance,
                      theoretical_thickness, design_thickness, nominal_thickness,
                      standard_thickness, actual_stress, safety_factor, Y_factor):
        """格式化计算结果"""
        return f"""═══════════════════════════════════════════════════
                        📋 输入参数
═══════════════════════════════════════════════════

计算标准: {standard}
设计压力: {design_pressure} MPa
设计温度: {design_temp} °C
管道外径: {outer_diameter} mm
许用应力: {allowable_stress} MPa
焊缝系数: {weld_factor}
腐蚀余量: {corrosion_allowance} mm
负偏差: {tolerance*100:.1f} %
Y系数: {Y_factor}

═══════════════════════════════════════════════════
                        📊 计算结果
═══════════════════════════════════════════════════

壁厚计算:
• 理论计算壁厚: {theoretical_thickness:.2f} mm
• 设计壁厚(含腐蚀): {design_thickness:.2f} mm  
• 名义壁厚(含偏差): {nominal_thickness:.2f} mm
• 选用标准壁厚: {standard_thickness} mm

强度校核:
• 实际计算应力: {actual_stress:.1f} MPa
• 安全系数: {safety_factor:.2f}
• 强度状态: {'✅ 安全' if safety_factor >= 1.0 else '⚠️ 需重新设计'}

壁厚系列推荐:
• Sch 10S: ~{standard_thickness * 0.6:.1f} mm
• Sch 40S: ~{standard_thickness * 0.8:.1f} mm  
• Sch 80S: ~{standard_thickness:.1f} mm
• Sch 160: ~{standard_thickness * 1.4:.1f} mm

═══════════════════════════════════════════════════
                        💡 计算说明
═══════════════════════════════════════════════════

• 采用ASME B31.3壁厚计算公式
• Y系数根据材料类型和温度确定
• 标准壁厚按GB/T 17395系列选取
• 腐蚀余量根据介质特性确定
• 负偏差考虑制造公差影响
• 建议安全系数不小于1.0"""


if __name__ == "__main__":
    # 测试代码
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    widget = PipeThicknessCalculator()
    widget.resize(900, 700)
    widget.show()
    
    sys.exit(app.exec())