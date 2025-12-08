from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGroupBox, QTextEdit, QComboBox, QMessageBox, QFrame,
    QScrollArea, QDialog, QSpinBox, QButtonGroup, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QDoubleValidator
import math


class RefrigerationCycleCalculator(QWidget):
    """制冷循环计算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_refrigerant_data()
    
    def setup_ui(self):
        """设置制冷循环计算UI"""
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
            "计算蒸汽压缩制冷循环的性能参数，包括制冷量、压缩功、COP等。"
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 5px;")
        left_layout.addWidget(description)
        
        # 循环类型选择
        cycle_group = QGroupBox("❄️ 循环类型")
        cycle_group.setStyleSheet("""
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
        cycle_layout = QGridLayout(cycle_group)
        
        self.cycle_button_group = QButtonGroup(self)
        
        cycles = [
            ("理想循环", "无过冷过热"),
            ("实际循环", "包含过冷过热")
        ]
        
        for i, (cycle_name, tooltip) in enumerate(cycles):
            btn = QPushButton(cycle_name)
            btn.setCheckable(True)
            btn.setToolTip(tooltip)
            btn.setFixedWidth(180)
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
            self.cycle_button_group.addButton(btn, i)
            cycle_layout.addWidget(btn, i//2, i%2)
        
        self.cycle_button_group.button(0).setChecked(True)
        self.cycle_button_group.buttonClicked.connect(self.on_cycle_type_changed)
        
        left_layout.addWidget(cycle_group)
        
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
        
        # 制冷剂选择
        refrigerant_label = QLabel("制冷剂:")
        refrigerant_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        refrigerant_label.setStyleSheet(label_style)
        input_layout.addWidget(refrigerant_label, row, 0)
        
        self.refrigerant_combo = QComboBox()
        self.setup_refrigerant_options()
        self.refrigerant_combo.setFixedWidth(combo_width)
        self.refrigerant_combo.currentTextChanged.connect(self.on_refrigerant_changed)
        input_layout.addWidget(self.refrigerant_combo, row, 1, 1, 2)
        
        row += 1
        
        # 蒸发温度
        evap_temp_label = QLabel("蒸发温度 (°C):")
        evap_temp_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        evap_temp_label.setStyleSheet(label_style)
        input_layout.addWidget(evap_temp_label, row, 0)
        
        self.evap_temp_input = QLineEdit()
        self.evap_temp_input.setPlaceholderText("例如: -10")
        self.evap_temp_input.setValidator(QDoubleValidator(-100.0, 100.0, 2))
        self.evap_temp_input.setText("-10")
        self.evap_temp_input.setFixedWidth(input_width)
        input_layout.addWidget(self.evap_temp_input, row, 1)
        
        row += 1
        
        # 冷凝温度
        cond_temp_label = QLabel("冷凝温度 (°C):")
        cond_temp_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        cond_temp_label.setStyleSheet(label_style)
        input_layout.addWidget(cond_temp_label, row, 0)
        
        self.cond_temp_input = QLineEdit()
        self.cond_temp_input.setPlaceholderText("例如: 40")
        self.cond_temp_input.setValidator(QDoubleValidator(-50.0, 100.0, 2))
        self.cond_temp_input.setText("40")
        self.cond_temp_input.setFixedWidth(input_width)
        input_layout.addWidget(self.cond_temp_input, row, 1)
        
        row += 1
        
        # 过冷度
        self.subcool_label = QLabel("过冷度 (K):")
        self.subcool_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.subcool_label.setStyleSheet(label_style)
        input_layout.addWidget(self.subcool_label, row, 0)
        
        self.subcool_input = QLineEdit()
        self.subcool_input.setPlaceholderText("例如: 5")
        self.subcool_input.setValidator(QDoubleValidator(0.0, 50.0, 2))
        self.subcool_input.setText("5")
        self.subcool_input.setFixedWidth(input_width)
        input_layout.addWidget(self.subcool_input, row, 1)
        
        row += 1
        
        # 过热度
        self.superheat_label = QLabel("过热度 (K):")
        self.superheat_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.superheat_label.setStyleSheet(label_style)
        input_layout.addWidget(self.superheat_label, row, 0)
        
        self.superheat_input = QLineEdit()
        self.superheat_input.setPlaceholderText("例如: 5")
        self.superheat_input.setValidator(QDoubleValidator(0.0, 50.0, 2))
        self.superheat_input.setText("5")
        self.superheat_input.setFixedWidth(input_width)
        input_layout.addWidget(self.superheat_input, row, 1)
        
        row += 1
        
        # 制冷剂质量流量
        mass_flow_label = QLabel("质量流量 (kg/s):")
        mass_flow_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        mass_flow_label.setStyleSheet(label_style)
        input_layout.addWidget(mass_flow_label, row, 0)
        
        self.mass_flow_input = QLineEdit()
        self.mass_flow_input.setPlaceholderText("例如: 0.1")
        self.mass_flow_input.setValidator(QDoubleValidator(0.001, 100.0, 6))
        self.mass_flow_input.setText("0.1")
        self.mass_flow_input.setFixedWidth(input_width)
        input_layout.addWidget(self.mass_flow_input, row, 1)
        
        row += 1
        
        # 压缩机效率
        comp_eff_label = QLabel("压缩机效率 (%):")
        comp_eff_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        comp_eff_label.setStyleSheet(label_style)
        input_layout.addWidget(comp_eff_label, row, 0)
        
        self.comp_eff_input = QLineEdit()
        self.comp_eff_input.setPlaceholderText("例如: 80")
        self.comp_eff_input.setValidator(QDoubleValidator(10.0, 100.0, 2))
        self.comp_eff_input.setText("80")
        self.comp_eff_input.setFixedWidth(input_width)
        input_layout.addWidget(self.comp_eff_input, row, 1)
        
        left_layout.addWidget(input_group)
        
        # 计算按钮
        calculate_btn = QPushButton("🧮 计算制冷循环")
        calculate_btn.setFont(QFont("Arial", 12, QFont.Bold))
        calculate_btn.clicked.connect(self.calculate_cycle)
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
        
        # 初始状态设置
        self.on_cycle_type_changed()
    
    def setup_refrigerant_data(self):
        """设置制冷剂物性数据"""
        self.refrigerant_data = {
            "R134a": {
                "critical_temp": 101.1,  # °C
                "critical_pressure": 4059,  # kPa
                "molecular_weight": 102.03,  # g/mol
                "ODP": 0,  # 臭氧破坏潜能
                "GWP": 1430  # 全球变暖潜能
            },
            "R22": {
                "critical_temp": 96.2,
                "critical_pressure": 4970,
                "molecular_weight": 86.47,
                "ODP": 0.055,
                "GWP": 1810
            },
            "R410A": {
                "critical_temp": 72.1,
                "critical_pressure": 4900,
                "molecular_weight": 72.58,
                "ODP": 0,
                "GWP": 2088
            },
            "R32": {
                "critical_temp": 78.4,
                "critical_pressure": 5780,
                "molecular_weight": 52.02,
                "ODP": 0,
                "GWP": 675
            },
            "R717 (氨)": {
                "critical_temp": 132.3,
                "critical_pressure": 11280,
                "molecular_weight": 17.03,
                "ODP": 0,
                "GWP": 0
            },
            "R744 (CO₂)": {
                "critical_temp": 31.1,
                "critical_pressure": 7380,
                "molecular_weight": 44.01,
                "ODP": 0,
                "GWP": 1
            }
        }
    
    def setup_refrigerant_options(self):
        """设置制冷剂选项"""
        refrigerants = [
            "R134a - HFC制冷剂，环保型",
            "R22 - HCFC制冷剂，逐步淘汰",
            "R410A - HFC混合制冷剂，空调常用",
            "R32 - HFC制冷剂，低GWP",
            "R717 (氨) - 天然制冷剂，高效",
            "R744 (CO₂) - 天然制冷剂，环保"
        ]
        self.refrigerant_combo.addItems(refrigerants)
    
    def on_refrigerant_changed(self, text):
        """处理制冷剂选择变化"""
        pass
    
    def on_cycle_type_changed(self):
        """处理循环类型变化"""
        is_actual = self.cycle_button_group.checkedButton().text() == "实际循环"
        
        # 对于理想循环，隐藏过冷过热输入
        self.subcool_label.setVisible(is_actual)
        self.subcool_input.setVisible(is_actual)
        self.superheat_label.setVisible(is_actual)
        self.superheat_input.setVisible(is_actual)
    
    def calculate_saturation_pressure(self, refrigerant, temperature):
        """计算饱和压力（简化计算）"""
        # 使用Antoine方程简化计算
        if refrigerant == "R134a":
            A, B, C = 6.9094, 1169.0, 224.0
        elif refrigerant == "R22":
            A, B, C = 6.9399, 1117.0, 231.0
        elif refrigerant == "R410A":
            A, B, C = 6.9454, 1125.0, 232.0
        elif refrigerant == "R32":
            A, B, C = 6.8935, 1083.0, 236.0
        elif refrigerant == "R717 (氨)":
            A, B, C = 7.3605, 926.0, 240.0
        elif refrigerant == "R744 (CO₂)":
            A, B, C = 6.8123, 1301.0, 273.0
        else:
            A, B, C = 6.9094, 1169.0, 224.0  # 默认R134a
        
        T = temperature + 273.15  # 转换为K
        P_sat = math.exp(A - B/(T - C)) * 100  # kPa
        return P_sat
    
    def calculate_enthalpy(self, refrigerant, temperature, pressure, is_vapor=True):
        """计算焓值（简化计算）"""
        # 简化计算，实际应用中应使用详细的物性表或方程
        if refrigerant == "R134a":
            if is_vapor:
                # 蒸汽焓值
                return 250 + 1.8 * temperature  # kJ/kg
            else:
                # 液体焓值
                return 100 + 1.5 * temperature  # kJ/kg
        else:
            # 其他制冷剂的简化计算
            if is_vapor:
                return 250 + 1.8 * temperature
            else:
                return 100 + 1.5 * temperature
    
    def calculate_entropy(self, refrigerant, temperature, pressure, is_vapor=True):
        """计算熵值（简化计算）"""
        if refrigerant == "R134a":
            if is_vapor:
                return 0.9 + 0.01 * temperature  # kJ/kg·K
            else:
                return 0.4 + 0.005 * temperature  # kJ/kg·K
        else:
            if is_vapor:
                return 0.9 + 0.01 * temperature
            else:
                return 0.4 + 0.005 * temperature
    
    def calculate_cycle(self):
        """计算制冷循环"""
        try:
            # 获取输入值
            cycle_type = self.cycle_button_group.checkedButton().text()
            refrigerant_text = self.refrigerant_combo.currentText()
            refrigerant = refrigerant_text.split(" - ")[0]
            
            evap_temp = float(self.evap_temp_input.text())
            cond_temp = float(self.cond_temp_input.text())
            mass_flow = float(self.mass_flow_input.text())
            comp_efficiency = float(self.comp_eff_input.text()) / 100
            
            # 验证输入
            if evap_temp >= cond_temp:
                QMessageBox.warning(self, "输入错误", "蒸发温度必须低于冷凝温度")
                return
            
            if cycle_type == "实际循环":
                subcool = float(self.subcool_input.text())
                superheat = float(self.superheat_input.text())
            else:
                subcool = 0
                superheat = 0
            
            # 计算各状态点参数
            # 点1: 压缩机进口 (蒸发器出口)
            P_evap = self.calculate_saturation_pressure(refrigerant, evap_temp)
            T1 = evap_temp + superheat
            h1 = self.calculate_enthalpy(refrigerant, T1, P_evap, is_vapor=True)
            s1 = self.calculate_entropy(refrigerant, T1, P_evap, is_vapor=True)
            
            # 点2: 压缩机出口 (等熵压缩)
            P_cond = self.calculate_saturation_pressure(refrigerant, cond_temp)
            h2s = h1 + (P_cond - P_evap) * 0.1  # 简化计算
            h2 = h1 + (h2s - h1) / comp_efficiency
            T2 = cond_temp + 20  # 简化计算
            
            # 点3: 冷凝器出口
            T3 = cond_temp - subcool
            h3 = self.calculate_enthalpy(refrigerant, T3, P_cond, is_vapor=False)
            
            # 点4: 膨胀阀出口 (等焓膨胀)
            h4 = h3
            T4 = evap_temp
            
            # 计算循环性能参数
            refrigeration_effect = h1 - h4  # kJ/kg
            compressor_work = h2 - h1  # kJ/kg
            heat_rejection = h2 - h3  # kJ/kg
            
            COP = refrigeration_effect / compressor_work
            compressor_power = mass_flow * compressor_work  # kW
            refrigeration_capacity = mass_flow * refrigeration_effect  # kW
            
            # 计算效率指标
            carnot_COP = (evap_temp + 273.15) / (cond_temp - evap_temp)
            efficiency = COP / carnot_COP * 100
            
            # 显示结果
            result = self.format_results(
                cycle_type, refrigerant, evap_temp, cond_temp, subcool, superheat,
                mass_flow, comp_efficiency, P_evap, P_cond, h1, h2, h3, h4,
                refrigeration_effect, compressor_work, heat_rejection, COP,
                compressor_power, refrigeration_capacity, carnot_COP, efficiency
            )
            
            self.result_text.setText(result)
            
        except ValueError as e:
            QMessageBox.critical(self, "计算错误", f"参数输入格式错误: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "计算错误", f"计算过程中发生错误: {str(e)}")
    
    def format_results(self, cycle_type, refrigerant, evap_temp, cond_temp, subcool, 
                      superheat, mass_flow, comp_efficiency, P_evap, P_cond, h1, h2, 
                      h3, h4, refrigeration_effect, compressor_work, heat_rejection, 
                      COP, compressor_power, refrigeration_capacity, carnot_COP, efficiency):
        """格式化计算结果"""
        return f"""═══════════════════════════════════════════════════
                        📋 输入参数
═══════════════════════════════════════════════════

循环类型: {cycle_type}
制冷剂: {refrigerant}
蒸发温度: {evap_temp} °C
冷凝温度: {cond_temp} °C
过冷度: {subcool} K
过热度: {superheat} K
质量流量: {mass_flow} kg/s
压缩机效率: {comp_efficiency*100:.1f} %

═══════════════════════════════════════════════════
                        📊 状态点参数
═══════════════════════════════════════════════════

• 点1 (压缩机进口):
  温度: {evap_temp + superheat:.1f} °C, 压力: {P_evap:.1f} kPa
  焓值: {h1:.2f} kJ/kg

• 点2 (压缩机出口):
  温度: {cond_temp + 20:.1f} °C, 压力: {P_cond:.1f} kPa  
  焓值: {h2:.2f} kJ/kg

• 点3 (冷凝器出口):
  温度: {cond_temp - subcool:.1f} °C, 压力: {P_cond:.1f} kPa
  焓值: {h3:.2f} kJ/kg

• 点4 (膨胀阀出口):
  温度: {evap_temp:.1f} °C, 压力: {P_evap:.1f} kPa
  焓值: {h4:.2f} kJ/kg

═══════════════════════════════════════════════════
                        ⚡ 性能参数
═══════════════════════════════════════════════════

单位质量参数:
• 制冷效应: {refrigeration_effect:.2f} kJ/kg
• 压缩功: {compressor_work:.2f} kJ/kg  
• 排热量: {heat_rejection:.2f} kJ/kg

系统性能:
• 制冷量: {refrigeration_capacity:.2f} kW
• 压缩机功率: {compressor_power:.2f} kW
• 性能系数(COP): {COP:.3f}

效率分析:
• 卡诺循环COP: {carnot_COP:.3f}
• 循环效率: {efficiency:.1f} %

═══════════════════════════════════════════════════
                        💡 计算说明
═══════════════════════════════════════════════════

• 基于蒸汽压缩制冷循环理论计算
• 使用简化物性计算方法
• 假设压缩过程为等熵过程
• 膨胀过程为等焓过程
• 冷凝器和蒸发器压力为饱和压力
• 结果仅供参考，实际系统性能可能有所不同"""


if __name__ == "__main__":
    # 测试代码
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    widget = RefrigerationCycleCalculator()
    widget.resize(900, 700)
    widget.show()
    
    sys.exit(app.exec())