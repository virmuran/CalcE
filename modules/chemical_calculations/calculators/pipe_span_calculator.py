from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGroupBox, QTextEdit, QComboBox, QGridLayout, QMessageBox, QDialog,
    QFileDialog, QDialogButtonBox
)
from PySide6.QtGui import QFont, QDoubleValidator
from PySide6.QtCore import Qt
import math
import re
from datetime import datetime


class ProjectInfoDialog(QDialog):
    """工程信息对话框"""
    
    def __init__(self, parent=None, default_info=None, report_number=""):
        super().__init__(parent)
        self.default_info = default_info or {}
        self.report_number = report_number
        self.setWindowTitle("工程信息")
        self.setFixedSize(400, 300)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("请输入工程信息")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px; margin: 10px;")
        layout.addWidget(title_label)
        
        # 项目名称
        project_layout = QHBoxLayout()
        project_label = QLabel("项目名称:")
        project_label.setFixedWidth(80)
        self.project_input = QLineEdit()
        self.project_input.setPlaceholderText("例如：XX化工厂管道项目")
        self.project_input.setText(self.default_info.get('project_name', ''))
        project_layout.addWidget(project_label)
        project_layout.addWidget(self.project_input)
        layout.addLayout(project_layout)
        
        # 设计单位
        design_layout = QHBoxLayout()
        design_label = QLabel("设计单位:")
        design_label.setFixedWidth(80)
        self.design_input = QLineEdit()
        self.design_input.setPlaceholderText("例如：XX设计院")
        self.design_input.setText(self.default_info.get('design_unit', ''))
        design_layout.addWidget(design_label)
        design_layout.addWidget(self.design_input)
        layout.addLayout(design_layout)
        
        # 计算人员
        calc_layout = QHBoxLayout()
        calc_label = QLabel("计算人员:")
        calc_label.setFixedWidth(80)
        self.calc_input = QLineEdit()
        self.calc_input.setPlaceholderText("请输入姓名")
        self.calc_input.setText(self.default_info.get('calculator', ''))
        calc_layout.addWidget(calc_label)
        calc_layout.addWidget(self.calc_input)
        layout.addLayout(calc_layout)
        
        # 审核人员
        review_layout = QHBoxLayout()
        review_label = QLabel("审核人员:")
        review_label.setFixedWidth(80)
        self.review_input = QLineEdit()
        self.review_input.setPlaceholderText("请输入姓名")
        self.review_input.setText(self.default_info.get('reviewer', ''))
        review_layout.addWidget(review_label)
        review_layout.addWidget(self.review_input)
        layout.addLayout(review_layout)
        
        # 计算书编号
        number_layout = QHBoxLayout()
        number_label = QLabel("计算书编号:")
        number_label.setFixedWidth(80)
        self.number_input = QLineEdit()
        self.number_input.setText(self.report_number)
        number_layout.addWidget(number_label)
        number_layout.addWidget(self.number_input)
        layout.addLayout(number_layout)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_info(self):
        return {
            'project_name': self.project_input.text().strip(),
            'design_unit': self.design_input.text().strip(),
            'calculator': self.calc_input.text().strip(),
            'reviewer': self.review_input.text().strip(),
            'report_number': self.number_input.text().strip()
        }


class PipeSpanCalculator(QWidget):
    """管道跨距计算（优化版，包含计算书功能）"""
    
    def __init__(self, parent=None, data_manager=None):
        super().__init__(parent)
        
        # 使用传入的数据管理器或创建新的
        if data_manager is not None:
            self.data_manager = data_manager
            print("使用共享的数据管理器")
        else:
            self.init_data_manager()
        
        self.setup_ui()
    
    def init_data_manager(self):
        """初始化数据管理器 - 使用单例模式"""
        try:
            from data_manager import DataManager
            self.data_manager = DataManager.get_instance()
            print("使用共享的数据管理器实例")
        except Exception as e:
            print(f"数据管理器初始化失败: {e}")
            self.data_manager = None
    
    def setup_ui(self):
        """设置左右布局的管道跨距计算UI"""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 左侧：输入参数区域 (占2/3宽度)
        left_widget = QWidget()
        left_widget.setMaximumWidth(900)  # 与压降计算器保持一致
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(15)
        
        # 说明文本
        description = QLabel(
            "计算管道在不同支撑条件下的最大允许跨距。考虑管道重量、流体重量和保温层重量。"
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 5px;")
        left_layout.addWidget(description)
        
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
        input_layout = QGridLayout(input_group)
        input_layout.setVerticalSpacing(12)
        input_layout.setHorizontalSpacing(15)  # 增加水平间距
        
        # 标签样式 - 右对齐
        label_style = """
            QLabel {
                font-weight: bold;
                padding-right: 10px;
            }
        """
        
        # 输入框和下拉菜单的固定宽度 - 与压降计算器保持一致
        input_width = 400
        combo_width = 250
        
        row = 0
        
        # 管道外径
        od_label = QLabel("管道外径 (mm):")
        od_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        od_label.setStyleSheet(label_style)
        input_layout.addWidget(od_label, row, 0)
        
        self.od_input = QLineEdit()
        self.od_input.setPlaceholderText("例如: 114.3")
        self.od_input.setValidator(QDoubleValidator(1.0, 2000.0, 6))
        self.od_input.setFixedWidth(input_width)
        input_layout.addWidget(self.od_input, row, 1)
        
        self.od_combo = QComboBox()
        self.od_combo.addItems([
            "21.3 mm - DN15 [1/2\"]",
            "26.9 mm - DN20 [3/4\"]",
            "33.7 mm - DN25 [1\"]",
            "42.4 mm - DN32 [1¼\"]", 
            "48.3 mm - DN40 [1½\"]",
            "60.3 mm - DN50 [2\"]",
            "76.1 mm - DN65 [2½\"]",
            "88.9 mm - DN80 [3\"]",
            "114.3 mm - DN100 [4\"]",
            "139.7 mm - DN125 [5\"]",
            "168.3 mm - DN150 [6\"]",
            "219.1 mm - DN200 [8\"]",
            "273.0 mm - DN250 [10\"]",
            "323.9 mm - DN300 [12\"]",
            "自定义外径"
        ])
        self.od_combo.setFixedWidth(combo_width)
        self.od_combo.currentTextChanged.connect(self.on_od_changed)
        input_layout.addWidget(self.od_combo, row, 2)
        
        row += 1
        
        # 管道壁厚
        thickness_label = QLabel("管道壁厚 (mm):")
        thickness_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        thickness_label.setStyleSheet(label_style)
        input_layout.addWidget(thickness_label, row, 0)
        
        self.thickness_input = QLineEdit()
        self.thickness_input.setPlaceholderText("例如: 6.02")
        self.thickness_input.setValidator(QDoubleValidator(0.1, 100.0, 6))
        self.thickness_input.setFixedWidth(input_width)
        input_layout.addWidget(self.thickness_input, row, 1)
        
        self.thickness_combo = QComboBox()
        self.thickness_combo.addItems([
            "SCH 10 - 薄壁",
            "SCH 20 - 标准壁厚", 
            "SCH 40 - 厚壁",
            "SCH 80 - 加厚壁",
            "SCH 160 - 特厚壁",
            "自定义壁厚"
        ])
        self.thickness_combo.setFixedWidth(combo_width)
        self.thickness_combo.currentTextChanged.connect(self.on_thickness_changed)
        input_layout.addWidget(self.thickness_combo, row, 2)
        
        row += 1
        
        # 管道材料
        material_label = QLabel("管道材料:")
        material_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        material_label.setStyleSheet(label_style)
        input_layout.addWidget(material_label, row, 0)
        
        self.material_combo = QComboBox()
        self.material_combo.addItems([
            "碳钢 - 密度: 7850 kg/m³, 弹性模量: 200 GPa",
            "不锈钢304 - 密度: 7930 kg/m³, 弹性模量: 193 GPa",
            "不锈钢316 - 密度: 8000 kg/m³, 弹性模量: 193 GPa",
            "铜 - 密度: 8960 kg/m³, 弹性模量: 110 GPa",
            "铝 - 密度: 2700 kg/m³, 弹性模量: 69 GPa",
            "PVC - 密度: 1380 kg/m³, 弹性模量: 3 GPa",
            "自定义材料"
        ])
        self.material_combo.setFixedWidth(input_width)
        self.material_combo.currentTextChanged.connect(self.on_material_changed)
        input_layout.addWidget(self.material_combo, row, 1)
        
        # 材料属性显示
        self.material_props_label = QLabel("")
        self.material_props_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        self.material_props_label.setFixedWidth(combo_width)
        input_layout.addWidget(self.material_props_label, row, 2)
        
        row += 1
        
        # 流体密度
        fluid_label = QLabel("流体密度 (kg/m³):")
        fluid_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        fluid_label.setStyleSheet(label_style)
        input_layout.addWidget(fluid_label, row, 0)
        
        self.fluid_density_input = QLineEdit()
        self.fluid_density_input.setPlaceholderText("例如: 1000 (水)")
        self.fluid_density_input.setValidator(QDoubleValidator(0.0, 10000.0, 6))
        self.fluid_density_input.setFixedWidth(input_width)
        input_layout.addWidget(self.fluid_density_input, row, 1)
        
        self.fluid_combo = QComboBox()
        self.fluid_combo.addItems([
            "0 - 空管",
            "1000 - 水",
            "789 - 乙醇", 
            "719 - 汽油",
            "850 - 柴油",
            "1261 - 甘油",
            "13600 - 汞",
            "自定义密度"
        ])
        self.fluid_combo.setFixedWidth(combo_width)
        self.fluid_combo.currentTextChanged.connect(self.on_fluid_changed)
        input_layout.addWidget(self.fluid_combo, row, 2)
        
        row += 1
        
        # 保温层厚度
        insulation_label = QLabel("保温层厚度 (mm):")
        insulation_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        insulation_label.setStyleSheet(label_style)
        input_layout.addWidget(insulation_label, row, 0)
        
        self.insulation_input = QLineEdit()
        self.insulation_input.setPlaceholderText("例如: 50")
        self.insulation_input.setValidator(QDoubleValidator(0.0, 500.0, 6))
        self.insulation_input.setFixedWidth(input_width)
        input_layout.addWidget(self.insulation_input, row, 1)
        
        self.insulation_combo = QComboBox()
        self.insulation_combo.addItems([
            "0 - 无保温",
            "25 - 薄保温",
            "50 - 标准保温", 
            "75 - 厚保温",
            "100 - 超厚保温",
            "自定义厚度"
        ])
        self.insulation_combo.setFixedWidth(combo_width)
        self.insulation_combo.currentTextChanged.connect(self.on_insulation_changed)
        input_layout.addWidget(self.insulation_combo, row, 2)
        
        row += 1
        
        # 保温层密度
        insulation_density_label = QLabel("保温层密度 (kg/m³):")
        insulation_density_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        insulation_density_label.setStyleSheet(label_style)
        input_layout.addWidget(insulation_density_label, row, 0)
        
        self.insulation_density_input = QLineEdit()
        self.insulation_density_input.setPlaceholderText("例如: 200")
        self.insulation_density_input.setValidator(QDoubleValidator(0.0, 2000.0, 6))
        self.insulation_density_input.setFixedWidth(input_width)
        input_layout.addWidget(self.insulation_density_input, row, 1)
        
        self.insulation_density_combo = QComboBox()
        self.insulation_density_combo.addItems([
            "50 - 玻璃棉",
            "100 - 岩棉",
            "200 - 硅酸铝", 
            "300 - 泡沫玻璃",
            "自定义密度"
        ])
        self.insulation_density_combo.setFixedWidth(combo_width)
        self.insulation_density_combo.currentTextChanged.connect(self.on_insulation_density_changed)
        input_layout.addWidget(self.insulation_density_combo, row, 2)
        
        row += 1
        
        # 允许应力
        stress_label = QLabel("允许应力 (MPa):")
        stress_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        stress_label.setStyleSheet(label_style)
        input_layout.addWidget(stress_label, row, 0)
        
        self.stress_input = QLineEdit()
        self.stress_input.setPlaceholderText("例如: 137.9 (碳钢)")
        self.stress_input.setValidator(QDoubleValidator(1.0, 1000.0, 6))
        self.stress_input.setFixedWidth(input_width)
        input_layout.addWidget(self.stress_input, row, 1)
        
        self.stress_combo = QComboBox()
        self.stress_combo.addItems([
            "137.9 MPa - 碳钢(A53)",
            "172.4 MPa - 高强度钢",
            "117.2 MPa - 不锈钢304",
            "34.5 MPa - PVC",
            "82.7 MPa - 铝",
            "自定义应力"
        ])
        self.stress_combo.setFixedWidth(combo_width)
        self.stress_combo.currentTextChanged.connect(self.on_stress_changed)
        input_layout.addWidget(self.stress_combo, row, 2)
        
        left_layout.addWidget(input_group)
        
        # 计算按钮
        calculate_btn = QPushButton("🧮 计算跨距")
        calculate_btn.setFont(QFont("Arial", 12, QFont.Bold))
        calculate_btn.clicked.connect(self.calculate_span)
        calculate_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
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

        download_layout.addWidget(download_txt_btn)
        download_layout.addWidget(download_pdf_btn)
        left_layout.addLayout(download_layout)
        
        # 右侧：结果显示区域 (占1/3宽度)
        right_widget = QWidget()
        right_widget.setMinimumWidth(400)  # 与压降计算器保持一致
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
        main_layout.addWidget(left_widget, 2)  # 左侧占2/3
        main_layout.addWidget(right_widget, 1)  # 右侧占1/3
        
        # 设置默认值 - 不预先填入任何数值
        self.set_default_values()
    
    def set_default_values(self):
        """设置默认值 - 不预先填入任何数值"""
        # 只设置下拉框的默认选项，但不触发数值填入
        # 使用 blockSignals 防止触发 currentTextChanged 事件
        self.od_combo.blockSignals(True)
        self.thickness_combo.blockSignals(True)
        self.material_combo.blockSignals(True)
        self.fluid_combo.blockSignals(True)
        self.insulation_combo.blockSignals(True)
        self.insulation_density_combo.blockSignals(True)
        self.stress_combo.blockSignals(True)
        
        # 设置下拉框默认选项
        self.od_combo.setCurrentIndex(8)  # DN100
        self.thickness_combo.setCurrentIndex(2)  # SCH 40
        self.material_combo.setCurrentIndex(0)  # 碳钢
        self.fluid_combo.setCurrentIndex(1)  # 水
        self.insulation_combo.setCurrentIndex(2)  # 标准保温
        self.insulation_density_combo.setCurrentIndex(1)  # 岩棉
        self.stress_combo.setCurrentIndex(0)  # 碳钢
        
        # 重新启用信号
        self.od_combo.blockSignals(False)
        self.thickness_combo.blockSignals(False)
        self.material_combo.blockSignals(False)
        self.fluid_combo.blockSignals(False)
        self.insulation_combo.blockSignals(False)
        self.insulation_density_combo.blockSignals(False)
        self.stress_combo.blockSignals(False)
        
        # 手动触发下拉菜单变化，确保输入框状态正确
        self.on_od_changed(self.od_combo.currentText())
        self.on_thickness_changed(self.thickness_combo.currentText())
        self.on_fluid_changed(self.fluid_combo.currentText())
        self.on_insulation_changed(self.insulation_combo.currentText())
        self.on_insulation_density_changed(self.insulation_density_combo.currentText())
        self.on_stress_changed(self.stress_combo.currentText())
    
    def on_od_changed(self, text):
        """处理外径选择变化"""
        if "自定义" in text:
            self.od_input.setReadOnly(False)
            self.od_input.setPlaceholderText("输入自定义外径")
            self.od_input.clear()
        else:
            self.od_input.setReadOnly(False)  # 改为可编辑，与压降计算器保持一致
            self.od_input.setPlaceholderText("例如: 114.3")
            # 从选项文本中提取数值
            try:
                match = re.search(r'(\d+\.?\d*)', text)
                if match:
                    od_value = float(match.group(1))
                    self.od_input.setText(f"{od_value}")
            except:
                pass
    
    def on_thickness_changed(self, text):
        """处理壁厚选择变化"""
        if "自定义" in text:
            self.thickness_input.setReadOnly(False)
            self.thickness_input.setPlaceholderText("输入自定义壁厚")
            self.thickness_input.clear()
        else:
            self.thickness_input.setReadOnly(False)  # 改为可编辑
            self.thickness_input.setPlaceholderText("例如: 6.02")
            # 根据选项设置默认值
            if "SCH 10" in text:
                self.thickness_input.setText("3.05")
            elif "SCH 20" in text:
                self.thickness_input.setText("3.40")
            elif "SCH 40" in text:
                self.thickness_input.setText("6.02")
            elif "SCH 80" in text:
                self.thickness_input.setText("8.56")
            elif "SCH 160" in text:
                self.thickness_input.setText("13.49")
    
    def on_material_changed(self, text):
        """处理材料选择变化"""
        if "自定义" in text:
            # 对于自定义材料，可以在这里添加输入框
            pass
        else:
            # 更新材料属性显示
            self.material_props_label.setText(text.split(" - ")[1])
    
    def on_fluid_changed(self, text):
        """处理流体密度选择变化"""
        if "自定义" in text:
            self.fluid_density_input.setReadOnly(False)
            self.fluid_density_input.setPlaceholderText("输入自定义密度")
            self.fluid_density_input.clear()
        else:
            self.fluid_density_input.setReadOnly(False)  # 改为可编辑
            self.fluid_density_input.setPlaceholderText("例如: 1000 (水)")
            # 从选项文本中提取数值
            try:
                match = re.search(r'(\d+)', text)
                if match:
                    density_value = float(match.group(1))
                    self.fluid_density_input.setText(f"{density_value}")
            except:
                pass
    
    def on_insulation_changed(self, text):
        """处理保温层厚度选择变化"""
        if "自定义" in text:
            self.insulation_input.setReadOnly(False)
            self.insulation_input.setPlaceholderText("输入自定义厚度")
            self.insulation_input.clear()
        else:
            self.insulation_input.setReadOnly(False)  # 改为可编辑
            self.insulation_input.setPlaceholderText("例如: 50")
            # 从选项文本中提取数值
            try:
                match = re.search(r'(\d+)', text)
                if match:
                    thickness_value = float(match.group(1))
                    self.insulation_input.setText(f"{thickness_value}")
            except:
                pass
    
    def on_insulation_density_changed(self, text):
        """处理保温层密度选择变化"""
        if "自定义" in text:
            self.insulation_density_input.setReadOnly(False)
            self.insulation_density_input.setPlaceholderText("输入自定义密度")
            self.insulation_density_input.clear()
        else:
            self.insulation_density_input.setReadOnly(False)  # 改为可编辑
            self.insulation_density_input.setPlaceholderText("例如: 200")
            # 从选项文本中提取数值
            try:
                match = re.search(r'(\d+)', text)
                if match:
                    density_value = float(match.group(1))
                    self.insulation_density_input.setText(f"{density_value}")
            except:
                pass
    
    def on_stress_changed(self, text):
        """处理允许应力选择变化"""
        if "自定义" in text:
            self.stress_input.setReadOnly(False)
            self.stress_input.setPlaceholderText("输入自定义应力")
            self.stress_input.clear()
        else:
            self.stress_input.setReadOnly(False)  # 改为可编辑
            self.stress_input.setPlaceholderText("例如: 137.9 (碳钢)")
            # 从选项文本中提取数值
            try:
                match = re.search(r'(\d+\.?\d*)', text)
                if match:
                    stress_value = float(match.group(1))
                    self.stress_input.setText(f"{stress_value}")
            except:
                pass
    
    def get_material_properties(self):
        """获取材料属性"""
        text = self.material_combo.currentText()
        
        if "碳钢" in text:
            return 7850, 200e9
        elif "不锈钢304" in text:
            return 7930, 193e9
        elif "不锈钢316" in text:
            return 8000, 193e9
        elif "铜" in text:
            return 8960, 110e9
        elif "铝" in text:
            return 2700, 69e9
        elif "PVC" in text:
            return 1380, 3e9
        else:
            return 7850, 200e9  # 默认碳钢
    
    def calculate_span(self):
        """计算管道跨距"""
        try:
            # 获取输入值
            od = float(self.od_input.text() or 0) / 1000  # 转换为米
            thickness = float(self.thickness_input.text() or 0) / 1000  # 转换为米
            material_density, elastic_modulus = self.get_material_properties()
            fluid_density = float(self.fluid_density_input.text() or 0)
            insulation_thickness = float(self.insulation_input.text() or 0) / 1000  # 转换为米
            insulation_density = float(self.insulation_density_input.text() or 0)
            allowable_stress = float(self.stress_input.text() or 0) * 1e6  # 转换为Pa
            
            # 验证输入
            if not all([od, thickness, allowable_stress]):
                QMessageBox.warning(self, "输入错误", "请填写管道外径、壁厚和允许应力")
                return
            
            # 计算管道内径
            id_val = od - 2 * thickness
            
            # 计算截面惯性矩
            I = math.pi * (od**4 - id_val**4) / 64
            
            # 计算截面模量
            Z = math.pi * (od**4 - id_val**4) / (32 * od)
            
            # 计算单位长度重量
            # 管道重量
            pipe_area = math.pi * (od**2 - id_val**2) / 4
            pipe_weight = pipe_area * material_density * 9.81  # N/m
            
            # 流体重量
            if fluid_density > 0:
                fluid_area = math.pi * id_val**2 / 4
                fluid_weight = fluid_area * fluid_density * 9.81  # N/m
            else:
                fluid_weight = 0
            
            # 保温层重量
            if insulation_thickness > 0 and insulation_density > 0:
                insulation_od = od + 2 * insulation_thickness
                insulation_area = math.pi * (insulation_od**2 - od**2) / 4
                insulation_weight = insulation_area * insulation_density * 9.81  # N/m
            else:
                insulation_weight = 0
            
            # 总重量
            total_weight = pipe_weight + fluid_weight + insulation_weight
            
            # 计算最大跨距
            span_stress = math.sqrt(8 * allowable_stress * Z / total_weight)
            
            # 基于挠度的跨距
            max_deflection = span_stress / 360  # L/360 挠度限制
            span_deflection = (384 * elastic_modulus * I / (5 * total_weight * max_deflection)) ** 0.25
            
            # 取较小值作为推荐跨距
            recommended_span = min(span_stress, span_deflection)
            
            # 显示结果 - 使用格式化的输出
            result = f"""═══════════════════════════════════════════════════
                        📋 输入参数
═══════════════════════════════════════════════════

管道参数:
• 外径: {od*1000:.1f} mm
• 内径: {id_val*1000:.1f} mm  
• 壁厚: {thickness*1000:.1f} mm

材料参数:
• 管道材料密度: {material_density} kg/m³
• 弹性模量: {elastic_modulus/1e9:.0f} GPa
• 允许应力: {allowable_stress/1e6:.1f} MPa

载荷参数:
• 流体密度: {fluid_density} kg/m³
• 保温层厚度: {insulation_thickness*1000:.0f} mm
• 保温层密度: {insulation_density} kg/m³

═══════════════════════════════════════════════════
                        📊 计算结果
═══════════════════════════════════════════════════

重量计算:
• 管道重量: {pipe_weight:.2f} N/m
• 流体重量: {fluid_weight:.2f} N/m
• 保温层重量: {insulation_weight:.2f} N/m
• 总重量: {total_weight:.2f} N/m

跨距计算结果:
• 基于应力限制: {span_stress:.2f} m
• 基于挠度限制: {span_deflection:.2f} m
• 推荐最大跨距: {recommended_span:.2f} m

安全评估:
• 应力利用率: {total_weight * recommended_span**2 / (8 * Z) / allowable_stress * 100:.1f}%
• 挠度利用率: {total_weight * recommended_span**4 / (384 * elastic_modulus * I) / max_deflection * 100:.1f}%

═══════════════════════════════════════════════════
                        🧮 计算公式
═══════════════════════════════════════════════════

应力限制跨距: L = √(8·σ·Z / w)
挠度限制跨距: L = ⁴√(384·E·I / (5·w·δ_max))

其中:
σ = {allowable_stress/1e6:.1f} MPa (允许应力)
E = {elastic_modulus/1e9:.0f} GPa (弹性模量)
Z = {Z*1e6:.3f} cm³ (截面模量)
I = {I*1e8:.3f} cm⁴ (惯性矩)
w = {total_weight:.2f} N/m (总载荷)
δ_max = L/360 (最大允许挠度)

═══════════════════════════════════════════════════
                        💡 应用说明
═══════════════════════════════════════════════════

• 实际跨距应小于计算值，建议取 0.8-0.9 的安全系数
• 对于振动较大的管道，应进一步减小跨距
• 重要管道应进行详细的应力分析
• 计算结果仅供参考，实际设计需符合相关规范"""
            
            self.result_text.setText(result)
            
        except ValueError as e:
            QMessageBox.critical(self, "计算错误", f"参数输入格式错误: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "计算错误", f"计算过程中发生错误: {str(e)}")
    
    def get_project_info(self):
        """获取工程信息 - 使用共享的项目信息"""
        try:
            # 从数据管理器获取共享的项目信息
            saved_info = {}
            if self.data_manager:
                saved_info = self.data_manager.get_project_info()
            
            # 获取下一个报告编号
            report_number = ""
            if self.data_manager:
                report_number = self.data_manager.get_next_report_number("SPAN")
            
            dialog = ProjectInfoDialog(self, saved_info, report_number)
            if dialog.exec() == QDialog.Accepted:
                info = dialog.get_info()
                # 验证必填字段
                if not info['project_name']:
                    QMessageBox.warning(self, "输入错误", "项目名称不能为空")
                    return self.get_project_info()  # 重新弹出对话框
                
                # 保存项目信息到数据管理器
                if self.data_manager:
                    # 只保存项目信息，不保存报告编号
                    info_to_save = {
                        'project_name': info['project_name'],
                        'design_unit': info['design_unit'],
                        'calculator': info['calculator'],
                        'reviewer': info['reviewer']
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
            
            # 更宽松的检查条件：只要结果文本不为空且包含计算结果的关键字
            if not result_text or ("计算结果" not in result_text and "跨距计算结果" not in result_text):
                QMessageBox.warning(self, "生成失败", "请先进行计算再生成计算书")
                return None
                
            # 获取工程信息
            project_info = self.get_project_info()
            if not project_info:
                return None  # 用户取消了输入
            
            # 添加报告头信息
            report = f"""工程计算书 - 管道跨距计算
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
计算工具: TofuSoft 工程计算模块
========================================

"""
            report += result_text
            
            # 添加工程信息部分
            report += f"""
════════════════════════════════════════
                            📋 工程信息
════════════════════════════════════════

项目名称: {project_info['project_name']}
设计单位: {project_info['design_unit']}
计算人员: {project_info['calculator']}
审核人员: {project_info['reviewer']}
计算日期: {datetime.now().strftime('%Y-%m-%d')}

════════════════════════════════════════
                            🏷️ 计算书标识
════════════════════════════════════════

计算书编号: SP-{datetime.now().strftime('%Y%m%d')}-001
版本: 1.0
状态: 正式计算书

════════════════════════════════════════
                            📝 备注说明
════════════════════════════════════════

1. 本计算书基于结构力学原理及相关标准规范
2. 计算结果仅供参考，实际应用需考虑安全系数
3. 重要工程参数应经专业工程师审核确认
4. 计算条件变更时应重新进行计算

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
            import os
            
            # 直接调用 generate_report，它内部会进行检查
            report_content = self.generate_report()
            if report_content is None:  # 如果返回None，说明检查失败或用户取消
                return
                
            # 选择保存路径
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"管道跨距计算书_{timestamp}.txt"
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
            default_name = f"管道跨距计算书_{timestamp}.pdf"
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
                title = Paragraph("工程计算书 - 管道跨距计算", chinese_style_heading)
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
        
        return content


if __name__ == "__main__":
    # 测试代码
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    calculator = PipeSpanCalculator()
    calculator.resize(1200, 800)
    calculator.show()
    
    sys.exit(app.exec())