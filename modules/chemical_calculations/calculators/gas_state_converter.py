from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGroupBox, QTextEdit, QComboBox, QGridLayout, QMessageBox
)
from PySide6.QtGui import QFont, QDoubleValidator
from PySide6.QtCore import Qt


class GasStateConverter(QWidget):
    """气体标准状态转压缩状态（左右布局优化版）"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置左右布局的气体状态转换UI"""
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
            "将气体从标准状态(0°C, 101.325kPa)转换为实际状态(压缩状态)。"
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
        
        # 标准状态流量
        flow_label = QLabel("标准状态流量 (Nm³/h):")
        flow_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        flow_label.setStyleSheet(label_style)
        input_layout.addWidget(flow_label, row, 0)
        
        self.flow_input = QLineEdit()
        self.flow_input.setPlaceholderText("例如: 1000")
        self.flow_input.setValidator(QDoubleValidator(0.1, 1000000.0, 6))
        self.flow_input.setFixedWidth(input_width)
        input_layout.addWidget(self.flow_input, row, 1)
        
        # 流量输入没有预设，放置一个禁用的下拉菜单占位
        self.flow_combo = QComboBox()
        self.flow_combo.setEnabled(False)
        self.flow_combo.addItem("直接输入流量值")
        self.flow_combo.setFixedWidth(combo_width)
        input_layout.addWidget(self.flow_combo, row, 2)
        
        row += 1
        
        # 标准状态定义
        standard_label = QLabel("标准状态:")
        standard_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        standard_label.setStyleSheet(label_style)
        input_layout.addWidget(standard_label, row, 0)
        
        self.standard_combo = QComboBox()
        self.standard_combo.addItems([
            "0°C, 101.325 kPa (国际标准)",
            "15°C, 101.325 kPa (欧美标准)",
            "20°C, 101.325 kPa (中国标准)",
            "自定义标准状态"
        ])
        self.standard_combo.setFixedWidth(input_width)
        input_layout.addWidget(self.standard_combo, row, 1)
        
        # 标准状态没有独立下拉
        self.standard_combo2 = QComboBox()
        self.standard_combo2.setEnabled(False)
        self.standard_combo2.addItem("选择标准状态定义")
        self.standard_combo2.setFixedWidth(combo_width)
        input_layout.addWidget(self.standard_combo2, row, 2)
        
        self.standard_combo.currentTextChanged.connect(self.on_standard_changed)
        
        row += 1
        
        # 自定义标准状态
        self.custom_standard_widget = QWidget()
        custom_layout = QGridLayout(self.custom_standard_widget)
        custom_layout.setHorizontalSpacing(10)
        
        std_temp_label = QLabel("标准温度 (°C):")
        std_temp_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        std_temp_label.setStyleSheet(label_style)
        custom_layout.addWidget(std_temp_label, 0, 0)
        
        self.std_temp_input = QLineEdit()
        self.std_temp_input.setPlaceholderText("例如: 0")
        self.std_temp_input.setValidator(QDoubleValidator(-50.0, 100.0, 6))
        self.std_temp_input.setFixedWidth(input_width)
        custom_layout.addWidget(self.std_temp_input, 0, 1)
        
        std_pressure_label = QLabel("标准压力 (kPa):")
        std_pressure_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        std_pressure_label.setStyleSheet(label_style)
        custom_layout.addWidget(std_pressure_label, 1, 0)
        
        self.std_pressure_input = QLineEdit()
        self.std_pressure_input.setPlaceholderText("例如: 101.325")
        self.std_pressure_input.setValidator(QDoubleValidator(50.0, 200.0, 6))
        self.std_pressure_input.setFixedWidth(input_width)
        custom_layout.addWidget(self.std_pressure_input, 1, 1)
        
        # 占位列
        custom_placeholder = QLabel()
        custom_layout.addWidget(custom_placeholder, 0, 2)
        
        input_layout.addWidget(self.custom_standard_widget, row, 0, 1, 3)
        self.custom_standard_widget.setVisible(False)
        
        row += 1
        
        # 实际状态压力
        actual_pressure_label = QLabel("实际状态压力 (kPa):")
        actual_pressure_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        actual_pressure_label.setStyleSheet(label_style)
        input_layout.addWidget(actual_pressure_label, row, 0)
        
        self.actual_pressure_input = QLineEdit()
        self.actual_pressure_input.setPlaceholderText("例如: 500")
        self.actual_pressure_input.setValidator(QDoubleValidator(0.1, 10000.0, 6))
        self.actual_pressure_input.setFixedWidth(input_width)
        input_layout.addWidget(self.actual_pressure_input, row, 1)
        
        # 压力输入没有预设
        self.pressure_combo = QComboBox()
        self.pressure_combo.setEnabled(False)
        self.pressure_combo.addItem("直接输入压力值")
        self.pressure_combo.setFixedWidth(combo_width)
        input_layout.addWidget(self.pressure_combo, row, 2)
        
        row += 1
        
        # 实际状态温度
        actual_temp_label = QLabel("实际状态温度 (°C):")
        actual_temp_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        actual_temp_label.setStyleSheet(label_style)
        input_layout.addWidget(actual_temp_label, row, 0)
        
        self.actual_temp_input = QLineEdit()
        self.actual_temp_input.setPlaceholderText("例如: 20")
        self.actual_temp_input.setValidator(QDoubleValidator(-50.0, 500.0, 6))
        self.actual_temp_input.setFixedWidth(input_width)
        input_layout.addWidget(self.actual_temp_input, row, 1)
        
        # 温度输入没有预设
        self.temp_combo = QComboBox()
        self.temp_combo.setEnabled(False)
        self.temp_combo.addItem("直接输入温度值")
        self.temp_combo.setFixedWidth(combo_width)
        input_layout.addWidget(self.temp_combo, row, 2)
        
        row += 1
        
        # 气体压缩因子
        compress_label = QLabel("气体压缩因子 Z:")
        compress_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        compress_label.setStyleSheet(label_style)
        input_layout.addWidget(compress_label, row, 0)
        
        self.compress_input = QLineEdit()
        self.compress_input.setPlaceholderText("例如: 1.0 (理想气体)")
        self.compress_input.setValidator(QDoubleValidator(0.1, 2.0, 6))
        self.compress_input.setText("1.0")
        self.compress_input.setFixedWidth(input_width)
        input_layout.addWidget(self.compress_input, row, 1)
        
        self.compress_combo = QComboBox()
        self.compress_combo.addItems([
            "1.0 - 理想气体",
            "0.9 - 轻微可压缩气体",
            "0.8 - 中等可压缩气体",
            "自定义压缩因子"
        ])
        self.compress_combo.setFixedWidth(combo_width)
        self.compress_combo.currentTextChanged.connect(self.on_compress_changed)
        input_layout.addWidget(self.compress_combo, row, 2)
        
        left_layout.addWidget(input_group)
        
        # 计算按钮
        calculate_btn = QPushButton("🧮 转换状态")
        calculate_btn.setFont(QFont("Arial", 12, QFont.Bold))
        calculate_btn.clicked.connect(self.convert_gas_state)
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
        
        # 右侧：结果显示区域 (占1/3宽度)
        right_widget = QWidget()
        right_widget.setMinimumWidth(400)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)
        
        # 结果显示
        self.result_group = QGroupBox("📤 转换结果")
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
    
    def on_standard_changed(self, text):
        """处理标准状态选择变化"""
        if "自定义" in text:
            self.custom_standard_widget.setVisible(True)
        else:
            self.custom_standard_widget.setVisible(False)
    
    def on_compress_changed(self, text):
        """处理压缩因子选择变化"""
        if "自定义" in text:
            self.compress_input.setReadOnly(False)
            self.compress_input.setPlaceholderText("输入自定义压缩因子")
            self.compress_input.clear()
        else:
            self.compress_input.setReadOnly(True)
            try:
                # 从文本中提取数字
                import re
                match = re.search(r'(\d+\.?\d*)', text)
                if match:
                    compress_value = float(match.group(1))
                    self.compress_input.setText(f"{compress_value:.1f}")
            except:
                pass
    
    def get_standard_conditions(self):
        """获取标准状态条件"""
        text = self.standard_combo.currentText()
        
        if "自定义" in text:
            try:
                std_temp = float(self.std_temp_input.text() or 0)
                std_pressure = float(self.std_pressure_input.text() or 0)
                return std_temp, std_pressure
            except ValueError:
                return 0.0, 101.325  # 默认国际标准
        elif "0°C" in text:
            return 0.0, 101.325
        elif "15°C" in text:
            return 15.0, 101.325
        elif "20°C" in text:
            return 20.0, 101.325
        else:
            return 0.0, 101.325  # 默认国际标准
    
    def convert_gas_state(self):
        """转换气体状态"""
        try:
            # 获取输入值
            std_flow = float(self.flow_input.text() or 0)
            actual_pressure = float(self.actual_pressure_input.text() or 0)
            actual_temp = float(self.actual_temp_input.text() or 0)
            compress_factor = float(self.compress_input.text() or 0)
            
            std_temp, std_pressure = self.get_standard_conditions()
            
            # 验证输入
            if not all([std_flow, actual_pressure, actual_temp is not None]):
                QMessageBox.warning(self, "输入错误", "请填写所有必需参数")
                return
            
            # 转换为绝对温度和绝对压力
            std_temp_k = std_temp + 273.15
            actual_temp_k = actual_temp + 273.15
            
            std_pressure_abs = std_pressure
            actual_pressure_abs = actual_pressure
            
            # 计算实际状态流量
            # 使用理想气体状态方程: P1·V1/T1 = P2·V2/T2 (考虑压缩因子)
            actual_flow = std_flow * (std_pressure_abs / actual_pressure_abs) * (actual_temp_k / std_temp_k) * compress_factor
            
            # 计算密度变化
            # 密度与压力成正比，与温度成反比
            std_density_factor = 1.0  # 相对密度
            actual_density_factor = std_density_factor * (actual_pressure_abs / std_pressure_abs) * (std_temp_k / actual_temp_k) / compress_factor
            
            # 显示结果 - 使用格式化的输出
            result = f"""═══════════════════════════════════════════════════
                        📋 输入参数
═══════════════════════════════════════════════════

标准状态:
• 流量: {std_flow} Nm³/h
• 温度: {std_temp} °C ({std_temp_k:.2f} K)
• 压力: {std_pressure} kPa

实际状态:
• 压力: {actual_pressure} kPa
• 温度: {actual_temp} °C ({actual_temp_k:.2f} K)
• 压缩因子 Z: {compress_factor}

═══════════════════════════════════════════════════
                        📊 转换结果
═══════════════════════════════════════════════════

流量转换:
• 实际状态流量: {actual_flow:.2f} m³/h
• 实际状态流量: {actual_flow/60:.4f} m³/min

密度变化:
• 相对密度变化: {actual_density_factor:.4f} 倍

流量对比:
"""
            
            if actual_flow < std_flow:
                result += f"• 实际状态流量比标准状态小 {std_flow/actual_flow:.2f} 倍"
            else:
                result += f"• 实际状态流量比标准状态大 {actual_flow/std_flow:.2f} 倍"

            result += f"""

═══════════════════════════════════════════════════
                        🧮 计算公式
═══════════════════════════════════════════════════

Q_actual = Q_std × (P_std / P_actual) × (T_actual / T_std) × Z

其中:
• Q = 体积流量
• P = 绝对压力 (kPa)
• T = 绝对温度 (K)  
• Z = 压缩因子

详细计算:
{std_flow} × ({std_pressure_abs} / {actual_pressure_abs}) × ({actual_temp_k:.2f} / {std_temp_k:.2f}) × {compress_factor}
= {actual_flow:.2f} m³/h

═══════════════════════════════════════════════════
                        💡 应用说明
═══════════════════════════════════════════════════

• 标准状态通常指 0°C, 101.325 kPa
• 实际工程中需根据具体气体性质确定压缩因子
• 对于高压气体，压缩因子对结果影响显著
• 计算结果仅供参考，实际应用请考虑安全系数"""
            
            self.result_text.setText(result)
            
        except ValueError as e:
            QMessageBox.critical(self, "计算错误", f"参数输入格式错误: {str(e)}")
        except ZeroDivisionError:
            QMessageBox.critical(self, "计算错误", "压力或温度不能为零")
        except Exception as e:
            QMessageBox.critical(self, "计算错误", f"计算过程中发生错误: {str(e)}")