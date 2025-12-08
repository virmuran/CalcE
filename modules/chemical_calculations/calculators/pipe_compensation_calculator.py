from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGroupBox, QTextEdit, QComboBox
)
from PySide6.QtGui import QFont, QDoubleValidator
from PySide6.QtCore import Qt
import math


class PipeCompensationCalculator(QWidget):
    """管道补偿计算"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置管道补偿计算UI - 左右布局版本"""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 左侧：输入参数区域 (占2/3宽度)
        left_widget = QWidget()
        left_widget.setMaximumWidth(900)  # 限制最大宽度
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(15)
        
        # 说明文本
        description = QLabel(
            "计算管道热膨胀量和需要的补偿量，评估管道热应力。"
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 5px;")
        left_layout.addWidget(description)
        
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
        input_layout = QVBoxLayout(input_group)
        
        # 管道材料
        material_layout = QHBoxLayout()
        material_layout.addWidget(QLabel("管道材料:"))
        self.material_combo = QComboBox()
        self.material_combo.addItems([
            "碳钢 (α=11.7×10⁻⁶/°C, E=200GPa)",
            "不锈钢304 (α=16.5×10⁻⁶/°C, E=193GPa)",
            "不锈钢316 (α=16.0×10⁻⁶/°C, E=193GPa)",
            "铜 (α=16.5×10⁻⁶/°C, E=110GPa)",
            "铝 (α=23.1×10⁻⁶/°C, E=69GPa)",
            "PVC (α=70×10⁻⁶/°C, E=3GPa)",
            "自定义材料"
        ])
        self.material_combo.currentTextChanged.connect(self.on_material_changed)
        material_layout.addWidget(self.material_combo)
        input_layout.addLayout(material_layout)
        
        # 自定义材料参数
        self.custom_material_widget = QWidget()
        custom_layout = QHBoxLayout(self.custom_material_widget)
        custom_layout.addWidget(QLabel("线膨胀系数 (×10⁻⁶/°C):"))
        self.alpha_input = QLineEdit()
        self.alpha_input.setPlaceholderText("例如: 11.7")
        self.alpha_input.setValidator(QDoubleValidator(1.0, 100.0, 6))
        self.alpha_input.setMinimumWidth(100)
        custom_layout.addWidget(self.alpha_input)
        
        custom_layout.addWidget(QLabel("弹性模量 (GPa):"))
        self.elastic_input = QLineEdit()
        self.elastic_input.setPlaceholderText("例如: 200")
        self.elastic_input.setValidator(QDoubleValidator(1.0, 500.0, 6))
        self.elastic_input.setMinimumWidth(100)
        custom_layout.addWidget(self.elastic_input)
        input_layout.addWidget(self.custom_material_widget)
        self.custom_material_widget.setVisible(False)
        
        # 管道长度
        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel("管道长度 (m):"))
        self.length_input = QLineEdit()
        self.length_input.setPlaceholderText("例如: 50")
        self.length_input.setValidator(QDoubleValidator(0.1, 1000.0, 6))
        self.length_input.setMinimumWidth(150)
        length_layout.addWidget(self.length_input)
        length_layout.addStretch()
        input_layout.addLayout(length_layout)
        
        # 温度变化
        temp_change_layout = QHBoxLayout()
        temp_change_layout.addWidget(QLabel("温度变化 ΔT (°C):"))
        self.temp_change_input = QLineEdit()
        self.temp_change_input.setPlaceholderText("例如: 100 (安装温度到运行温度)")
        self.temp_change_input.setValidator(QDoubleValidator(1.0, 500.0, 6))
        self.temp_change_input.setMinimumWidth(150)
        temp_change_layout.addWidget(self.temp_change_input)
        temp_change_layout.addStretch()
        input_layout.addLayout(temp_change_layout)
        
        # 管道外径
        od_layout = QHBoxLayout()
        od_layout.addWidget(QLabel("管道外径 (mm):"))
        self.od_input = QLineEdit()
        self.od_input.setPlaceholderText("例如: 114.3")
        self.od_input.setValidator(QDoubleValidator(1.0, 2000.0, 6))
        self.od_input.setMinimumWidth(150)
        od_layout.addWidget(self.od_input)
        od_layout.addStretch()
        input_layout.addLayout(od_layout)
        
        # 管道壁厚
        thickness_layout = QHBoxLayout()
        thickness_layout.addWidget(QLabel("管道壁厚 (mm):"))
        self.thickness_input = QLineEdit()
        self.thickness_input.setPlaceholderText("例如: 6.02")
        self.thickness_input.setValidator(QDoubleValidator(0.1, 100.0, 6))
        self.thickness_input.setMinimumWidth(150)
        thickness_layout.addWidget(self.thickness_input)
        thickness_layout.addStretch()
        input_layout.addLayout(thickness_layout)
        
        input_layout.addStretch()
        left_layout.addWidget(input_group)
        
        # 计算按钮
        calculate_btn = QPushButton("🧮 计算补偿量")
        calculate_btn.setFont(QFont("Arial", 12, QFont.Bold))
        calculate_btn.clicked.connect(self.calculate_compensation)
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
        
        # 右侧：结果显示区域 (占1/3宽度)
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
                min-height: 400px;
            }
        """)
        result_layout.addWidget(self.result_text)
        
        right_layout.addWidget(self.result_group)
        
        # 将左右两部分添加到主布局
        main_layout.addWidget(left_widget, 2)  # 左侧占2/3
        main_layout.addWidget(right_widget, 1)  # 右侧占1/3
    
    def on_material_changed(self, text):
        """处理材料选择变化"""
        if "自定义" in text:
            self.custom_material_widget.setVisible(True)
        else:
            self.custom_material_widget.setVisible(False)
    
    def get_material_properties(self):
        """获取材料属性"""
        text = self.material_combo.currentText()
        
        if "自定义" in text:
            try:
                alpha = float(self.alpha_input.text() or 0) * 1e-6
                elastic = float(self.elastic_input.text() or 0) * 1e9
                return alpha, elastic
            except ValueError:
                return 11.7e-6, 200e9  # 默认碳钢
        elif "碳钢" in text:
            return 11.7e-6, 200e9
        elif "不锈钢304" in text:
            return 16.5e-6, 193e9
        elif "不锈钢316" in text:
            return 16.0e-6, 193e9
        elif "铜" in text:
            return 16.5e-6, 110e9
        elif "铝" in text:
            return 23.1e-6, 69e9
        elif "PVC" in text:
            return 70e-6, 3e9
        else:
            return 11.7e-6, 200e9  # 默认碳钢
    
    def calculate_compensation(self):
        """计算管道补偿"""
        try:
            # 获取输入值
            length = float(self.length_input.text() or 0)
            temp_change = float(self.temp_change_input.text() or 0)
            od = float(self.od_input.text() or 0) / 1000  # 转换为米
            thickness = float(self.thickness_input.text() or 0) / 1000  # 转换为米
            
            alpha, elastic = self.get_material_properties()
            
            # 验证输入
            if not all([length, temp_change, od, thickness]):
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "输入错误", "请填写所有参数")
                return
            
            # 计算热膨胀量
            expansion = alpha * temp_change * length  # 米
            
            # 计算截面面积
            id_val = od - 2 * thickness
            area = math.pi * (od**2 - id_val**2) / 4
            
            # 计算热应力 (如果完全约束)
            stress = elastic * alpha * temp_change  # Pa
            
            # 计算热推力
            force = stress * area  # N
            
            # 推荐补偿方式
            if expansion < 0.05:  # 50mm
                compensation = "自然补偿 (利用管道走向)"
            elif expansion < 0.15:  # 150mm
                compensation = "Π型补偿器"
            elif expansion < 0.3:  # 300mm
                compensation = "波纹管补偿器"
            else:
                compensation = "套筒补偿器或球形补偿器"
            
            # 显示结果
            result = f"""管道补偿计算结果：
            
输入参数:
管道长度: {length} m
温度变化: {temp_change} °C
管道外径: {od*1000:.1f} mm
管道壁厚: {thickness*1000:.1f} mm
材料线膨胀系数: {alpha*1e6:.2f} ×10⁻⁶/°C
材料弹性模量: {elastic/1e9:.0f} GPa

计算结果:
热膨胀量: {expansion*1000:.1f} mm
热膨胀量: {expansion:.4f} m

应力分析:
完全约束时的热应力: {stress/1e6:.1f} MPa
完全约束时的热推力: {force/1000:.1f} kN

补偿建议:
推荐补偿方式: {compensation}

安全建议:"""
            
            # 应力评估
            if stress/1e6 < 80:
                result += "\n✓ 热应力在安全范围内"
            elif stress/1e6 < 137:
                result += "\n⚠ 热应力较高，需要详细应力分析"
            else:
                result += "\n✗ 热应力过高，必须采取补偿措施"
            
            result += f"""

计算公式:
ΔL = α × L × ΔT
σ = E × α × ΔT
F = σ × A

其中:
α = 线膨胀系数, L = 管道长度
ΔT = 温度变化, E = 弹性模量
A = 管道截面积"""
            
            self.result_text.setText(result)
            
        except ValueError as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "计算错误", f"参数输入格式错误: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "计算错误", f"计算过程中发生错误: {str(e)}")