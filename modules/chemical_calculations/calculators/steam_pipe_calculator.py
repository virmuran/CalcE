from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGroupBox, QTextEdit, QComboBox, QGridLayout, QMessageBox
)
from PySide6.QtGui import QFont, QDoubleValidator
from PySide6.QtCore import Qt
import math


class SteamPipeCalculator(QWidget):
    """蒸汽管径和流量查询（左右布局优化版）"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置左右布局的蒸汽管径和流量查询UI"""
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
            "根据蒸汽压力、温度和流量计算推荐管径，或根据管径计算最大蒸汽流量。"
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
        
        # 计算模式选择
        mode_label = QLabel("计算模式:")
        mode_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        mode_label.setStyleSheet(label_style)
        input_layout.addWidget(mode_label, row, 0)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["根据流量计算管径", "根据管径计算流量"])
        self.mode_combo.setFixedWidth(input_width)
        input_layout.addWidget(self.mode_combo, row, 1)
        
        self.mode_combo2 = QComboBox()
        self.mode_combo2.setEnabled(False)
        self.mode_combo2.addItem("选择计算模式")
        self.mode_combo2.setFixedWidth(combo_width)
        input_layout.addWidget(self.mode_combo2, row, 2)
        
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        
        row += 1
        
        # 蒸汽压力
        pressure_label = QLabel("蒸汽压力 (MPa):")
        pressure_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        pressure_label.setStyleSheet(label_style)
        input_layout.addWidget(pressure_label, row, 0)
        
        self.pressure_input = QLineEdit()
        self.pressure_input.setPlaceholderText("例如: 1.0")
        self.pressure_input.setValidator(QDoubleValidator(0.01, 20.0, 6))
        self.pressure_input.setFixedWidth(input_width)
        input_layout.addWidget(self.pressure_input, row, 1)
        
        self.pressure_combo = QComboBox()
        self.pressure_combo.addItems([
            "0.1 MPa - 低压蒸汽",
            "0.3 MPa - 低压蒸汽",
            "0.6 MPa - 中压蒸汽",
            "1.0 MPa - 中压蒸汽",
            "1.6 MPa - 高压蒸汽",
            "2.5 MPa - 高压蒸汽",
            "4.0 MPa - 超高压蒸汽",
            "自定义压力"
        ])
        self.pressure_combo.setFixedWidth(combo_width)
        self.pressure_combo.currentTextChanged.connect(self.on_pressure_changed)
        input_layout.addWidget(self.pressure_combo, row, 2)
        
        row += 1
        
        # 蒸汽温度
        temperature_label = QLabel("蒸汽温度 (°C):")
        temperature_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        temperature_label.setStyleSheet(label_style)
        input_layout.addWidget(temperature_label, row, 0)
        
        self.temperature_input = QLineEdit()
        self.temperature_input.setPlaceholderText("例如: 200")
        self.temperature_input.setValidator(QDoubleValidator(100.0, 600.0, 6))
        self.temperature_input.setFixedWidth(input_width)
        input_layout.addWidget(self.temperature_input, row, 1)
        
        self.temperature_combo = QComboBox()
        self.temperature_combo.addItems([
            "100°C - 饱和蒸汽",
            "120°C - 饱和蒸汽",
            "150°C - 饱和蒸汽",
            "180°C - 饱和蒸汽",
            "200°C - 过热蒸汽",
            "250°C - 过热蒸汽",
            "300°C - 过热蒸汽",
            "400°C - 高温蒸汽",
            "自定义温度"
        ])
        self.temperature_combo.setFixedWidth(combo_width)
        self.temperature_combo.currentTextChanged.connect(self.on_temperature_changed)
        input_layout.addWidget(self.temperature_combo, row, 2)
        
        row += 1
        
        # 流量输入（管径计算模式）
        self.flow_widget = QWidget()
        flow_layout = QGridLayout(self.flow_widget)
        
        flow_label = QLabel("蒸汽流量 (kg/h):")
        flow_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        flow_label.setStyleSheet(label_style)
        flow_layout.addWidget(flow_label, 0, 0)
        
        self.flow_input = QLineEdit()
        self.flow_input.setPlaceholderText("例如: 1000")
        self.flow_input.setValidator(QDoubleValidator(1.0, 100000.0, 6))
        self.flow_input.setFixedWidth(input_width)
        flow_layout.addWidget(self.flow_input, 0, 1)
        
        self.flow_combo = QComboBox()
        self.flow_combo.addItems([
            "小流量: 10-100 kg/h",
            "中等流量: 100-1000 kg/h",
            "大流量: 1000-10000 kg/h",
            "超大流量: 10000-100000 kg/h",
            "自定义流量"
        ])
        self.flow_combo.setFixedWidth(combo_width)
        self.flow_combo.currentTextChanged.connect(self.on_flow_changed)
        flow_layout.addWidget(self.flow_combo, 0, 2)
        
        input_layout.addWidget(self.flow_widget, row, 0, 1, 3)
        
        # 管径输入（流量计算模式）
        self.diameter_widget = QWidget()
        diameter_layout = QGridLayout(self.diameter_widget)
        
        diameter_label = QLabel("管道内径 (mm):")
        diameter_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        diameter_label.setStyleSheet(label_style)
        diameter_layout.addWidget(diameter_label, 0, 0)
        
        self.diameter_input = QLineEdit()
        self.diameter_input.setPlaceholderText("例如: 50")
        self.diameter_input.setValidator(QDoubleValidator(10.0, 1000.0, 6))
        self.diameter_input.setFixedWidth(input_width)
        diameter_layout.addWidget(self.diameter_input, 0, 1)
        
        self.diameter_combo = QComboBox()
        self.diameter_combo.addItems([
            "DN15 - 15 mm",
            "DN20 - 20 mm",
            "DN25 - 25 mm",
            "DN32 - 32 mm",
            "DN40 - 40 mm",
            "DN50 - 50 mm",
            "DN65 - 65 mm",
            "DN80 - 80 mm",
            "DN100 - 100 mm",
            "DN125 - 125 mm",
            "DN150 - 150 mm",
            "DN200 - 200 mm",
            "DN250 - 250 mm",
            "DN300 - 300 mm",
            "自定义管径"
        ])
        self.diameter_combo.setFixedWidth(combo_width)
        self.diameter_combo.currentTextChanged.connect(self.on_diameter_changed)
        diameter_layout.addWidget(self.diameter_combo, 0, 2)
        
        input_layout.addWidget(self.diameter_widget, row, 0, 1, 3)
        self.diameter_widget.setVisible(False)
        
        left_layout.addWidget(input_group)
        
        # 计算按钮
        calculate_btn = QPushButton("🧮 计算")
        calculate_btn.setFont(QFont("Arial", 12, QFont.Bold))
        calculate_btn.clicked.connect(self.calculate_steam_pipe)
        calculate_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
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
    
    def on_mode_changed(self, text):
        """处理计算模式变化"""
        if "根据管径计算流量" in text:
            self.flow_widget.setVisible(False)
            self.diameter_widget.setVisible(True)
        else:
            self.flow_widget.setVisible(True)
            self.diameter_widget.setVisible(False)
    
    def on_pressure_changed(self, text):
        """处理压力选择变化"""
        if "自定义" in text:
            self.pressure_input.setReadOnly(False)
            self.pressure_input.setPlaceholderText("输入自定义压力")
            self.pressure_input.clear()
        else:
            self.pressure_input.setReadOnly(True)
            try:
                # 从文本中提取数字
                import re
                match = re.search(r'(\d+\.?\d*)', text)
                if match:
                    pressure_value = float(match.group(1))
                    self.pressure_input.setText(f"{pressure_value:.1f}")
            except:
                pass
    
    def on_temperature_changed(self, text):
        """处理温度选择变化"""
        if "自定义" in text:
            self.temperature_input.setReadOnly(False)
            self.temperature_input.setPlaceholderText("输入自定义温度")
            self.temperature_input.clear()
        else:
            self.temperature_input.setReadOnly(True)
            try:
                # 从文本中提取数字
                import re
                match = re.search(r'(\d+\.?\d*)', text)
                if match:
                    temperature_value = float(match.group(1))
                    self.temperature_input.setText(f"{temperature_value:.0f}")
            except:
                pass
    
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
                    self.flow_input.setText(f"{avg_val:.0f}")
            except:
                pass
    
    def on_diameter_changed(self, text):
        """处理管径选择变化"""
        if "自定义" in text:
            self.diameter_input.setReadOnly(False)
            self.diameter_input.setPlaceholderText("输入自定义管径")
            self.diameter_input.clear()
        else:
            self.diameter_input.setReadOnly(True)
            try:
                # 从文本中提取数字
                import re
                match = re.search(r'(\d+\.?\d*)', text)
                if match:
                    diameter_value = float(match.group(1))
                    self.diameter_input.setText(f"{diameter_value:.0f}")
            except:
                pass
    
    def calculate_steam_pipe(self):
        """计算蒸汽管径或流量"""
        try:
            # 获取输入值
            pressure = float(self.pressure_input.text() or 0)
            temperature = float(self.temperature_input.text() or 0)
            mode = self.mode_combo.currentText()
            
            # 验证输入
            if not pressure or not temperature:
                QMessageBox.warning(self, "输入错误", "请填写蒸汽压力和温度")
                return
            
            # 计算蒸汽密度
            steam_density = self.calculate_steam_density(pressure, temperature)
            specific_volume = 1 / steam_density if steam_density > 0 else 0
            
            if "根据流量计算管径" in mode:
                flow_rate = float(self.flow_input.text() or 0)
                if not flow_rate:
                    QMessageBox.warning(self, "输入错误", "请填写蒸汽流量")
                    return
                
                # 推荐蒸汽流速
                recommended_velocity = 25.0
                
                # 质量流量转换为体积流量
                volume_flow = (flow_rate / 3600) * specific_volume
                
                # 计算所需管径
                required_area = volume_flow / recommended_velocity
                required_diameter = math.sqrt(4 * required_area / math.pi) * 1000  # mm
                
                # 推荐标准管径
                standard_diameters = [15, 20, 25, 32, 40, 50, 65, 80, 100, 125, 150, 200, 250, 300]
                recommended_diameter = min(standard_diameters, key=lambda x: abs(x - required_diameter))
                
                # 计算实际流速
                actual_area = math.pi * (recommended_diameter / 1000 / 2) ** 2
                actual_velocity = volume_flow / actual_area
                
                # 显示结果 - 使用格式化的输出
                result = f"""═══════════════════════════════════════════════════
                            📋 输入参数
═══════════════════════════════════════════════════

蒸汽参数:
• 压力: {pressure} MPa
• 温度: {temperature} °C
• 密度: {steam_density:.4f} kg/m³
• 比容: {specific_volume:.4f} m³/kg

流量参数:
• 质量流量: {flow_rate} kg/h
• 体积流量: {volume_flow*3600:.2f} m³/h

═══════════════════════════════════════════════════
                            📊 计算结果
═══════════════════════════════════════════════════

管径计算:
• 计算所需管径: {required_diameter:.1f} mm
• 推荐标准管径: DN{recommended_diameter} ({recommended_diameter} mm)
• 实际蒸汽流速: {actual_velocity:.1f} m/s

流速评估:
• 推荐蒸汽流速范围: 20-40 m/s
• 当前流速状态: {"✓ 正常" if 20 <= actual_velocity <= 40 else "⚠ 注意"}

═══════════════════════════════════════════════════
                            🧮 计算公式
═══════════════════════════════════════════════════

v = 25 m/s (推荐流速)
Q_v = m / ρ = {flow_rate} / {steam_density:.4f} = {flow_rate/steam_density:.2f} m³/h
Q_v' = Q_v / 3600 = {flow_rate/steam_density/3600:.6f} m³/s
A = Q_v' / v = {flow_rate/steam_density/3600:.6f} / 25 = {required_area:.6f} m²
D = √(4A/π) = √(4 × {required_area:.6f} / π) = {required_diameter:.1f} mm

═══════════════════════════════════════════════════
                            💡 应用说明
═══════════════════════════════════════════════════

• 推荐蒸汽流速范围: 20-40 m/s
• 低压蒸汽可取较低流速，高压蒸汽可取较高流速
• 实际应用请考虑压力损失和管道材质
• 对于长距离输送，建议选择较低流速以减小压降"""
                
            else:  # 根据管径计算流量
                diameter = float(self.diameter_input.text() or 0)
                if not diameter:
                    QMessageBox.warning(self, "输入错误", "请填写管道内径")
                    return
                
                # 推荐蒸汽流速
                recommended_velocity = 25.0
                
                # 计算最大流量
                area = math.pi * (diameter / 1000 / 2) ** 2
                volume_flow = area * recommended_velocity
                max_flow_rate = volume_flow / specific_volume * 3600  # kg/h
                
                # 显示结果 - 使用格式化的输出
                result = f"""═══════════════════════════════════════════════════
                            📋 输入参数
═══════════════════════════════════════════════════

蒸汽参数:
• 压力: {pressure} MPa
• 温度: {temperature} °C
• 密度: {steam_density:.4f} kg/m³
• 比容: {specific_volume:.4f} m³/kg

管道参数:
• 内径: {diameter} mm

═══════════════════════════════════════════════════
                            📊 计算结果
═══════════════════════════════════════════════════

流量计算:
• 推荐蒸汽流速: {recommended_velocity} m/s
• 最大蒸汽流量: {max_flow_rate:.0f} kg/h

流速范围对应流量:
• 20 m/s (低流速): {volume_flow / recommended_velocity * 20 / specific_volume * 3600:.0f} kg/h
• 25 m/s (标准流速): {max_flow_rate:.0f} kg/h
• 30 m/s (较高流速): {volume_flow / recommended_velocity * 30 / specific_volume * 3600:.0f} kg/h
• 40 m/s (高流速): {volume_flow / recommended_velocity * 40 / specific_volume * 3600:.0f} kg/h

═══════════════════════════════════════════════════
                            🧮 计算公式
═══════════════════════════════════════════════════

A = π × (D/2)² = π × ({diameter/1000}/2)² = {area:.6f} m²
Q_v = A × v = {area:.6f} × 25 = {volume_flow:.6f} m³/s
m = Q_v × ρ × 3600 = {volume_flow:.6f} × {steam_density:.4f} × 3600 = {max_flow_rate:.0f} kg/h

═══════════════════════════════════════════════════
                            💡 应用说明
═══════════════════════════════════════════════════

• 推荐蒸汽流速范围: 20-40 m/s
• 实际流量应考虑压力损失和安全系数
• 对于重要应用，建议进行详细的水力计算
• 计算结果仅供参考，实际应用请考虑具体工况"""
            
            self.result_text.setText(result)
            
        except ValueError as e:
            QMessageBox.critical(self, "计算错误", f"参数输入格式错误: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "计算错误", f"计算过程中发生错误: {str(e)}")
    
    def calculate_steam_density(self, pressure_mpa, temperature_c):
        """计算蒸汽密度"""
        pressure_bar = pressure_mpa * 10
        
        if temperature_c < 200:
            density = 0.6 * pressure_bar / (temperature_c + 100)
        else:
            density = 0.5 * pressure_bar / (temperature_c + 150)
        
        return max(density, 0.1)