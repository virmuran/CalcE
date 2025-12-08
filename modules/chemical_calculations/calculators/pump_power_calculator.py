from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGroupBox, QTextEdit, QComboBox, QGridLayout, QMessageBox
)
from PySide6.QtGui import QFont, QDoubleValidator
from PySide6.QtCore import Qt


class CentrifugalPumpCalculator(QWidget):
    """离心泵功率计算（左右布局优化版）"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置左右布局的离心泵功率计算UI"""
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
            "计算离心泵的轴功率、电机功率和效率，考虑流量、扬程、介质密度和泵效率。"
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
        input_layout.setHorizontalSpacing(10)
        
        # 标签样式 - 右对齐
        label_style = """
            QLabel {
                font-weight: bold;
                padding-right: 10px;
            }
        """
        
        # 输入框和下拉菜单的固定宽度
        input_width = 400
        combo_width = 250
        
        row = 0
        
        # 流量输入
        flow_label = QLabel("流量 (m³/h):")
        flow_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        flow_label.setStyleSheet(label_style)
        input_layout.addWidget(flow_label, row, 0)
        
        self.flow_input = QLineEdit()
        self.flow_input.setPlaceholderText("例如: 100")
        self.flow_input.setValidator(QDoubleValidator(0.1, 10000.0, 6))
        self.flow_input.setFixedWidth(input_width)
        input_layout.addWidget(self.flow_input, row, 1)
        
        self.flow_combo = QComboBox()
        self.flow_combo.addItems([
            "小流量: 0.1-10 m³/h",
            "中等流量: 10-100 m³/h",
            "大流量: 100-1000 m³/h",
            "超大流量: 1000-10000 m³/h",
            "自定义流量"
        ])
        self.flow_combo.setFixedWidth(combo_width)
        self.flow_combo.currentTextChanged.connect(self.on_flow_changed)
        input_layout.addWidget(self.flow_combo, row, 2)
        
        row += 1
        
        # 扬程输入
        head_label = QLabel("扬程 (m):")
        head_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        head_label.setStyleSheet(label_style)
        input_layout.addWidget(head_label, row, 0)
        
        self.head_input = QLineEdit()
        self.head_input.setPlaceholderText("例如: 50")
        self.head_input.setValidator(QDoubleValidator(0.1, 1000.0, 6))
        self.head_input.setFixedWidth(input_width)
        input_layout.addWidget(self.head_input, row, 1)
        
        self.head_combo = QComboBox()
        self.head_combo.addItems([
            "低扬程: 1-20 m",
            "中等扬程: 20-80 m",
            "高扬程: 80-200 m",
            "超高扬程: 200-1000 m",
            "自定义扬程"
        ])
        self.head_combo.setFixedWidth(combo_width)
        self.head_combo.currentTextChanged.connect(self.on_head_changed)
        input_layout.addWidget(self.head_combo, row, 2)
        
        row += 1
        
        # 介质密度
        density_label = QLabel("介质密度 (kg/m³):")
        density_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        density_label.setStyleSheet(label_style)
        input_layout.addWidget(density_label, row, 0)
        
        self.density_input = QLineEdit()
        self.density_input.setPlaceholderText("例如: 1000 (水)")
        self.density_input.setValidator(QDoubleValidator(1.0, 2000.0, 6))
        self.density_input.setFixedWidth(input_width)
        input_layout.addWidget(self.density_input, row, 1)
        
        self.density_combo = QComboBox()
        self.density_combo.addItems([
            "1000 - 水 (20°C)",
            "998 - 水 (25°C)",
            "983 - 水 (60°C)",
            "789 - 乙醇",
            "719 - 汽油",
            "850 - 柴油",
            "1261 - 甘油",
            "1025 - 海水",
            "自定义密度"
        ])
        self.density_combo.setFixedWidth(combo_width)
        self.density_combo.currentTextChanged.connect(self.on_density_changed)
        input_layout.addWidget(self.density_combo, row, 2)
        
        row += 1
        
        # 泵效率
        efficiency_label = QLabel("泵效率 (%):")
        efficiency_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        efficiency_label.setStyleSheet(label_style)
        input_layout.addWidget(efficiency_label, row, 0)
        
        self.efficiency_input = QLineEdit()
        self.efficiency_input.setPlaceholderText("例如: 75")
        self.efficiency_input.setValidator(QDoubleValidator(10.0, 95.0, 6))
        self.efficiency_input.setFixedWidth(input_width)
        input_layout.addWidget(self.efficiency_input, row, 1)
        
        self.efficiency_combo = QComboBox()
        self.efficiency_combo.addItems([
            "50-60% - 小型泵",
            "60-70% - 标准泵",
            "70-80% - 高效泵",
            "80-90% - 超高效泵",
            "自定义效率"
        ])
        self.efficiency_combo.setFixedWidth(combo_width)
        self.efficiency_combo.currentTextChanged.connect(self.on_efficiency_changed)
        input_layout.addWidget(self.efficiency_combo, row, 2)
        
        row += 1
        
        # 电机效率
        motor_efficiency_label = QLabel("电机效率 (%):")
        motor_efficiency_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        motor_efficiency_label.setStyleSheet(label_style)
        input_layout.addWidget(motor_efficiency_label, row, 0)
        
        self.motor_efficiency_input = QLineEdit()
        self.motor_efficiency_input.setPlaceholderText("例如: 92")
        self.motor_efficiency_input.setValidator(QDoubleValidator(50.0, 98.0, 6))
        self.motor_efficiency_input.setFixedWidth(input_width)
        input_layout.addWidget(self.motor_efficiency_input, row, 1)
        
        self.motor_efficiency_combo = QComboBox()
        self.motor_efficiency_combo.addItems([
            "85-88% - 小型电机",
            "88-92% - 标准电机",
            "92-95% - 高效电机",
            "95-97% - 超高效电机",
            "自定义效率"
        ])
        self.motor_efficiency_combo.setFixedWidth(combo_width)
        self.motor_efficiency_combo.currentTextChanged.connect(self.on_motor_efficiency_changed)
        input_layout.addWidget(self.motor_efficiency_combo, row, 2)
        
        row += 1
        
        # 安全系数
        safety_label = QLabel("安全系数:")
        safety_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        safety_label.setStyleSheet(label_style)
        input_layout.addWidget(safety_label, row, 0)
        
        self.safety_combo = QComboBox()
        self.safety_combo.addItems([
            "1.0 (无安全系数)",
            "1.05 (轻微)",
            "1.1 (标准)",
            "1.15 (保守)",
            "1.2 (高安全)",
            "1.25 (超高安全)"
        ])
        self.safety_combo.setFixedWidth(input_width)
        input_layout.addWidget(self.safety_combo, row, 1)
        
        self.safety_combo2 = QComboBox()
        self.safety_combo2.setEnabled(False)
        self.safety_combo2.addItem("选择安全系数")
        self.safety_combo2.setFixedWidth(combo_width)
        input_layout.addWidget(self.safety_combo2, row, 2)
        
        left_layout.addWidget(input_group)
        
        # 计算按钮
        calculate_btn = QPushButton("🧮 计算功率")
        calculate_btn.setFont(QFont("Arial", 12, QFont.Bold))
        calculate_btn.clicked.connect(self.calculate_pump_power)
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
                min-height: 500px;
            }
        """)
        result_layout.addWidget(self.result_text)
        
        right_layout.addWidget(self.result_group)
        
        # 将左右两部分添加到主布局
        main_layout.addWidget(left_widget, 2)  # 左侧占2/3
        main_layout.addWidget(right_widget, 1)  # 右侧占1/3
    
    def on_flow_changed(self, text):
        """处理流量选择变化"""
        if "自定义" in text:
            self.flow_input.setReadOnly(False)
            self.flow_input.setPlaceholderText("输入自定义流量")
            self.flow_input.clear()
        else:
            self.flow_input.setReadOnly(True)
            try:
                # 从文本中提取数字范围
                import re
                match = re.search(r'(\d+\.?\d*)-(\d+\.?\d*)', text)
                if match:
                    min_val = float(match.group(1))
                    max_val = float(match.group(2))
                    avg_val = (min_val + max_val) / 2
                    self.flow_input.setText(f"{avg_val:.1f}")
            except:
                pass
    
    def on_head_changed(self, text):
        """处理扬程选择变化"""
        if "自定义" in text:
            self.head_input.setReadOnly(False)
            self.head_input.setPlaceholderText("输入自定义扬程")
            self.head_input.clear()
        else:
            self.head_input.setReadOnly(True)
            try:
                # 从文本中提取数字范围
                import re
                match = re.search(r'(\d+\.?\d*)-(\d+\.?\d*)', text)
                if match:
                    min_val = float(match.group(1))
                    max_val = float(match.group(2))
                    avg_val = (min_val + max_val) / 2
                    self.head_input.setText(f"{avg_val:.1f}")
            except:
                pass
    
    def on_density_changed(self, text):
        """处理密度选择变化"""
        if "自定义" in text:
            self.density_input.setReadOnly(False)
            self.density_input.setPlaceholderText("输入自定义密度")
            self.density_input.clear()
        else:
            self.density_input.setReadOnly(True)
            try:
                # 从文本中提取数字
                import re
                match = re.search(r'(\d+\.?\d*)', text)
                if match:
                    density_value = float(match.group(1))
                    self.density_input.setText(f"{density_value:.0f}")
            except:
                pass
    
    def on_efficiency_changed(self, text):
        """处理泵效率选择变化"""
        if "自定义" in text:
            self.efficiency_input.setReadOnly(False)
            self.efficiency_input.setPlaceholderText("输入自定义效率")
            self.efficiency_input.clear()
        else:
            self.efficiency_input.setReadOnly(True)
            try:
                # 从文本中提取数字范围
                import re
                match = re.search(r'(\d+\.?\d*)-(\d+\.?\d*)', text)
                if match:
                    min_val = float(match.group(1))
                    max_val = float(match.group(2))
                    avg_val = (min_val + max_val) / 2
                    self.efficiency_input.setText(f"{avg_val:.1f}")
            except:
                pass
    
    def on_motor_efficiency_changed(self, text):
        """处理电机效率选择变化"""
        if "自定义" in text:
            self.motor_efficiency_input.setReadOnly(False)
            self.motor_efficiency_input.setPlaceholderText("输入自定义效率")
            self.motor_efficiency_input.clear()
        else:
            self.motor_efficiency_input.setReadOnly(True)
            try:
                # 从文本中提取数字范围
                import re
                match = re.search(r'(\d+\.?\d*)-(\d+\.?\d*)', text)
                if match:
                    min_val = float(match.group(1))
                    max_val = float(match.group(2))
                    avg_val = (min_val + max_val) / 2
                    self.motor_efficiency_input.setText(f"{avg_val:.1f}")
            except:
                pass
    
    def get_safety_factor(self):
        """获取安全系数"""
        text = self.safety_combo.currentText()
        
        if "1.0" in text:
            return 1.0
        elif "1.05" in text:
            return 1.05
        elif "1.1" in text:
            return 1.1
        elif "1.15" in text:
            return 1.15
        elif "1.2" in text:
            return 1.2
        elif "1.25" in text:
            return 1.25
        else:
            return 1.1
    
    def calculate_pump_power(self):
        """计算离心泵功率"""
        try:
            # 获取输入值
            flow_rate = float(self.flow_input.text() or 0)
            head = float(self.head_input.text() or 0)
            density = float(self.density_input.text() or 0)
            efficiency = float(self.efficiency_input.text() or 0)
            motor_efficiency = float(self.motor_efficiency_input.text() or 0)
            safety_factor = self.get_safety_factor()
            
            # 验证输入
            if not all([flow_rate, head, density, efficiency, motor_efficiency]):
                QMessageBox.warning(self, "输入错误", "请填写所有参数")
                return
            
            # 计算有效功率
            effective_power = (flow_rate / 3600) * density * 9.81 * head / 1000
            
            # 计算轴功率
            shaft_power = effective_power / (efficiency / 100)
            
            # 计算电机功率
            motor_power = shaft_power / (motor_efficiency / 100) * safety_factor
            
            # 计算总效率
            total_efficiency = (efficiency / 100) * (motor_efficiency / 100) * 100
            
            # 推荐电机规格
            standard_motors = [0.75, 1.1, 1.5, 2.2, 3.0, 4.0, 5.5, 7.5, 11, 15, 18.5, 22, 
                              30, 37, 45, 55, 75, 90, 110, 132, 160, 200, 250, 315, 355, 400]
            recommended_motor = min(standard_motors, key=lambda x: abs(x - motor_power))
            
            # 显示结果 - 使用格式化的输出
            result = f"""═══════════════════════════════════════════════════
                        📋 输入参数
═══════════════════════════════════════════════════

运行参数:
• 流量: {flow_rate} m³/h
• 扬程: {head} m
• 介质密度: {density} kg/m³
• 泵效率: {efficiency} %
• 电机效率: {motor_efficiency} %
• 安全系数: {safety_factor}

═══════════════════════════════════════════════════
                        📊 计算结果
═══════════════════════════════════════════════════

功率计算:
• 有效功率: {effective_power:.2f} kW
• 轴功率: {shaft_power:.2f} kW
• 电机功率: {motor_power:.2f} kW

效率分析:
• 总效率: {total_efficiency:.1f} %

设备选型:
• 推荐电机功率: {recommended_motor} kW

安全评估:
• 功率余量: {(recommended_motor - motor_power) / motor_power * 100:.1f}%

═══════════════════════════════════════════════════
                        🧮 计算公式
═══════════════════════════════════════════════════

P_有效 = (Q × ρ × g × H) / 3600000
P_轴 = P_有效 / η_泵
P_电机 = P_轴 / η_电机 × K_安全

其中:
Q = {flow_rate} m³/h (流量)
ρ = {density} kg/m³ (密度)
g = 9.81 m/s² (重力加速度)
H = {head} m (扬程)
η_泵 = {efficiency/100:.3f} (泵效率)
η_电机 = {motor_efficiency/100:.3f} (电机效率)
K_安全 = {safety_factor} (安全系数)

详细计算:
P_有效 = ({flow_rate} × {density} × 9.81 × {head}) / 3600000 = {effective_power:.2f} kW
P_轴 = {effective_power:.2f} / {efficiency/100:.3f} = {shaft_power:.2f} kW
P_电机 = {shaft_power:.2f} / {motor_efficiency/100:.3f} × {safety_factor} = {motor_power:.2f} kW

═══════════════════════════════════════════════════
                        💡 应用说明
═══════════════════════════════════════════════════

• 实际选型应选择比计算功率大的标准电机
• 考虑启动电流和过载能力
• 对于重载启动，建议选择更大的安全系数
• 计算结果仅供参考，实际应用请考虑具体工况"""
            
            self.result_text.setText(result)
            
        except ValueError as e:
            QMessageBox.critical(self, "计算错误", f"参数输入格式错误: {str(e)}")
        except ZeroDivisionError:
            QMessageBox.critical(self, "计算错误", "效率不能为零")
        except Exception as e:
            QMessageBox.critical(self, "计算错误", f"计算过程中发生错误: {str(e)}")