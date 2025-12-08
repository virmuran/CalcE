from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGroupBox, QTextEdit, QComboBox, QGridLayout, QMessageBox
)
from PySide6.QtGui import QFont, QDoubleValidator
from PySide6.QtCore import Qt


class SteamPropertyCalculator(QWidget):
    """水蒸气物性数据查询（左右布局优化版）"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置左右布局的水蒸气物性数据查询UI"""
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
            "查询水蒸气在不同压力和温度下的物性参数，包括密度、比焓、比熵等。"
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
        
        # 压力输入
        pressure_label = QLabel("压力 (MPa):")
        pressure_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        pressure_label.setStyleSheet(label_style)
        input_layout.addWidget(pressure_label, row, 0)
        
        self.pressure_input = QLineEdit()
        self.pressure_input.setPlaceholderText("例如: 1.0")
        self.pressure_input.setValidator(QDoubleValidator(0.01, 30.0, 6))
        self.pressure_input.setFixedWidth(input_width)
        input_layout.addWidget(self.pressure_input, row, 1)
        
        self.pressure_combo = QComboBox()
        self.pressure_combo.addItems([
            "0.1013 - 常压",
            "0.1 - 低压蒸汽",
            "0.3 - 低压蒸汽",
            "0.6 - 中压蒸汽",
            "1.0 - 中压蒸汽",
            "1.6 - 高压蒸汽",
            "2.5 - 高压蒸汽",
            "4.0 - 超高压蒸汽",
            "10.0 - 超高压蒸汽",
            "自定义压力"
        ])
        self.pressure_combo.setFixedWidth(combo_width)
        self.pressure_combo.currentTextChanged.connect(self.on_pressure_changed)
        input_layout.addWidget(self.pressure_combo, row, 2)
        
        row += 1
        
        # 温度输入
        temperature_label = QLabel("温度 (°C):")
        temperature_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        temperature_label.setStyleSheet(label_style)
        input_layout.addWidget(temperature_label, row, 0)
        
        self.temperature_input = QLineEdit()
        self.temperature_input.setPlaceholderText("例如: 200")
        self.temperature_input.setValidator(QDoubleValidator(0.01, 800.0, 6))
        self.temperature_input.setFixedWidth(input_width)
        input_layout.addWidget(self.temperature_input, row, 1)
        
        self.temperature_combo = QComboBox()
        self.temperature_combo.addItems([
            "100 - 饱和蒸汽",
            "120 - 饱和蒸汽",
            "150 - 饱和蒸汽",
            "180 - 饱和蒸汽",
            "200 - 过热蒸汽",
            "250 - 过热蒸汽",
            "300 - 过热蒸汽",
            "400 - 高温蒸汽",
            "500 - 高温蒸汽",
            "600 - 超高温蒸汽",
            "自定义温度"
        ])
        self.temperature_combo.setFixedWidth(combo_width)
        self.temperature_combo.currentTextChanged.connect(self.on_temperature_changed)
        input_layout.addWidget(self.temperature_combo, row, 2)
        
        left_layout.addWidget(input_group)
        
        # 计算按钮
        calculate_btn = QPushButton("🧮 查询物性")
        calculate_btn.setFont(QFont("Arial", 12, QFont.Bold))
        calculate_btn.clicked.connect(self.calculate_steam_properties)
        calculate_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
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
        self.result_group = QGroupBox("📤 物性数据")
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
                    self.pressure_input.setText(f"{pressure_value:.4f}")
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
    
    def calculate_steam_properties(self):
        """计算水蒸气物性"""
        try:
            # 获取输入值
            pressure = float(self.pressure_input.text() or 0)
            temperature = float(self.temperature_input.text() or 0)
            
            # 验证输入
            if not pressure or not temperature:
                QMessageBox.warning(self, "输入错误", "请填写压力和温度")
                return
            
            # 计算饱和温度
            saturation_temp = self.calculate_saturation_temperature(pressure)
            
            # 判断蒸汽状态
            if temperature < saturation_temp - 0.1:
                state = "过冷水"
                state_icon = "💧"
            elif abs(temperature - saturation_temp) < 0.1:
                state = "饱和水/饱和蒸汽"
                state_icon = "💧🔥"
            else:
                state = "过热蒸汽"
                state_icon = "🔥"
            
            # 计算物性参数
            density = self.calculate_steam_density(pressure, temperature)
            enthalpy = self.calculate_enthalpy(pressure, temperature)
            entropy = self.calculate_entropy(pressure, temperature)
            specific_volume = 1 / density if density > 0 else 0
            
            # 计算过热度（如果是过热蒸汽）
            superheat = temperature - saturation_temp if temperature > saturation_temp else 0
            
            # 显示结果 - 使用格式化的输出
            result = f"""═══════════════════════════════════════════════════
                        📋 输入参数
═══════════════════════════════════════════════════

• 压力: {pressure} MPa
• 温度: {temperature} °C
• 状态: {state_icon} {state}

参考数据:
• 饱和温度: {saturation_temp:.2f} °C
{f"• 过热度: {superheat:.2f} °C" if superheat > 0 else ""}

═══════════════════════════════════════════════════
                        📊 物性参数
═══════════════════════════════════════════════════

基本物性:
• 密度: {density:.4f} kg/m³
• 比容: {specific_volume:.6f} m³/kg

热力学参数:
• 比焓: {enthalpy:.2f} kJ/kg
• 比熵: {entropy:.4f} kJ/(kg·K)

热物性对比:
• 与饱和蒸汽密度比: {density/self.calculate_steam_density(pressure, saturation_temp):.3f}
• 与饱和蒸汽焓值差: {enthalpy - self.calculate_enthalpy(pressure, saturation_temp):.1f} kJ/kg

═══════════════════════════════════════════════════
                        💡 状态说明
═══════════════════════════════════════════════════

{state_icon} {state}
{f"• 过热度: {superheat:.1f}°C，属于中等过热蒸汽" if 10 < superheat <= 50 else ""}
{f"• 过热度: {superheat:.1f}°C，属于高度过热蒸汽" if superheat > 50 else ""}
{f"• 接近饱和状态，需要注意汽水分离" if abs(temperature - saturation_temp) < 5 and temperature >= saturation_temp else ""}
{f"• 处于过冷水状态，需要加热才能产生蒸汽" if temperature < saturation_temp - 0.1 else ""}

═══════════════════════════════════════════════════
                        🎯 应用建议
═══════════════════════════════════════════════════

• 以上数据为工程近似值
• 实际应用请参考IAPWS-IF97标准
• 对于精确计算，建议使用专业物性软件
• 在临界点附近物性变化剧烈，需要特别注意"""
            
            self.result_text.setText(result)
            
        except ValueError as e:
            QMessageBox.critical(self, "计算错误", f"参数输入格式错误: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "计算错误", f"计算过程中发生错误: {str(e)}")
    
    def calculate_saturation_temperature(self, pressure_mpa):
        """计算饱和温度"""
        pressure_bar = pressure_mpa * 10
        if pressure_bar <= 0.1:
            return 45.8
        elif pressure_bar <= 1:
            return 99.6 + (pressure_bar - 0.1) * 30
        elif pressure_bar <= 10:
            return 179.9 + (pressure_bar - 1) * 12
        elif pressure_bar <= 50:
            return 263.9 + (pressure_bar - 10) * 3.5
        else:
            return 300 + (pressure_bar - 50) * 2
    
    def calculate_steam_density(self, pressure_mpa, temperature_c):
        """计算蒸汽密度"""
        pressure_bar = pressure_mpa * 10
        
        if temperature_c < 200:
            density = 0.6 * pressure_bar / (temperature_c + 100)
        else:
            density = 0.5 * pressure_bar / (temperature_c + 150)
        
        return max(density, 0.1)
    
    def calculate_enthalpy(self, pressure_mpa, temperature_c):
        """计算比焓"""
        saturation_temp = self.calculate_saturation_temperature(pressure_mpa)
        
        if temperature_c < saturation_temp - 0.1:
            return 4.18 * temperature_c
        elif abs(temperature_c - saturation_temp) < 0.1:
            return 2675 + pressure_mpa * 10
        else:
            return 2800 + (temperature_c - saturation_temp) * 2.0
    
    def calculate_entropy(self, pressure_mpa, temperature_c):
        """计算比熵"""
        saturation_temp = self.calculate_saturation_temperature(pressure_mpa)
        
        if temperature_c < saturation_temp - 0.1:
            return 0.5 + 0.01 * temperature_c
        elif abs(temperature_c - saturation_temp) < 0.1:
            return 6.5 + pressure_mpa * 0.1
        else:
            return 7.0 + (temperature_c - saturation_temp) * 0.005