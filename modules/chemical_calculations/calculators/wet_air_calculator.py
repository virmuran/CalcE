from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                              QLabel, QLineEdit, QPushButton, QComboBox, 
                              QFormLayout, QTextEdit, QGridLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QDoubleValidator
import math


class WetAirCalculator(QWidget):
    """湿空气计算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置湿空气计算界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("湿空气计算")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # 说明文本
        desc_label = QLabel("计算湿空气的各种物性参数：相对湿度、绝对湿度、露点温度、比焓、比容等")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #7f8c8d; margin: 5px;")
        main_layout.addWidget(desc_label)
        
        # 输入参数组
        input_group = QGroupBox("输入参数")
        input_layout = QGridLayout(input_group)
        
        # 第一行输入
        self.temp_input = QLineEdit()
        self.temp_input.setPlaceholderText("例如：25")
        self.temp_input.setValidator(QDoubleValidator(-50, 200, 2))
        
        self.temp_unit = QComboBox()
        self.temp_unit.addItems(["°C", "K"])
        
        self.pressure_input = QLineEdit()
        self.pressure_input.setText("101.325")
        self.pressure_input.setValidator(QDoubleValidator(50, 2000, 2))
        
        self.pressure_unit = QComboBox()
        self.pressure_unit.addItems(["kPa", "bar", "atm"])
        
        input_layout.addWidget(QLabel("干球温度:"), 0, 0)
        input_layout.addWidget(self.temp_input, 0, 1)
        input_layout.addWidget(self.temp_unit, 0, 2)
        
        input_layout.addWidget(QLabel("大气压力:"), 0, 3)
        input_layout.addWidget(self.pressure_input, 0, 4)
        input_layout.addWidget(self.pressure_unit, 0, 5)
        
        # 第二行输入
        self.rh_input = QLineEdit()
        self.rh_input.setPlaceholderText("例如：60")
        self.rh_input.setValidator(QDoubleValidator(0, 100, 2))
        
        self.humidity_input = QLineEdit()
        self.humidity_input.setPlaceholderText("例如：0.012")
        self.humidity_input.setValidator(QDoubleValidator(0, 1, 6))
        
        self.humidity_unit = QComboBox()
        self.humidity_unit.addItems(["kg/kg干空气", "g/kg干空气"])
        
        input_layout.addWidget(QLabel("相对湿度(%):"), 1, 0)
        input_layout.addWidget(self.rh_input, 1, 1)
        input_layout.addWidget(QLabel(""), 1, 2)  # 占位
        
        input_layout.addWidget(QLabel("绝对湿度:"), 1, 3)
        input_layout.addWidget(self.humidity_input, 1, 4)
        input_layout.addWidget(self.humidity_unit, 1, 5)
        
        # 第三行输入
        self.wet_bulb_input = QLineEdit()
        self.wet_bulb_input.setPlaceholderText("例如：20")
        self.wet_bulb_input.setValidator(QDoubleValidator(-50, 200, 2))
        
        self.dew_point_input = QLineEdit()
        self.dew_point_input.setPlaceholderText("例如：15")
        self.dew_point_input.setValidator(QDoubleValidator(-50, 200, 2))
        
        input_layout.addWidget(QLabel("湿球温度:"), 2, 0)
        input_layout.addWidget(self.wet_bulb_input, 2, 1)
        input_layout.addWidget(QLabel("°C"), 2, 2)
        
        input_layout.addWidget(QLabel("露点温度:"), 2, 3)
        input_layout.addWidget(self.dew_point_input, 2, 4)
        input_layout.addWidget(QLabel("°C"), 2, 5)
        
        main_layout.addWidget(input_group)
        
        # 按钮组
        button_layout = QHBoxLayout()
        
        self.calc_btn = QPushButton("计算")
        self.calc_btn.setStyleSheet("QPushButton { background-color: #3498db; color: white; padding: 8px; border-radius: 4px; }"
                                  "QPushButton:hover { background-color: #2980b9; }")
        self.calc_btn.clicked.connect(self.calculate)
        
        self.clear_btn = QPushButton("清空")
        self.clear_btn.setStyleSheet("QPushButton { background-color: #95a5a6; color: white; padding: 8px; border-radius: 4px; }"
                                   "QPushButton:hover { background-color: #7f8c8d; }")
        self.clear_btn.clicked.connect(self.clear_inputs)
        
        button_layout.addWidget(self.calc_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # 结果显示
        result_group = QGroupBox("计算结果")
        result_layout = QFormLayout(result_group)
        
        self.relative_humidity_result = QLabel("--")
        self.absolute_humidity_result = QLabel("--")
        self.dew_point_result = QLabel("--")
        self.wet_bulb_result = QLabel("--")
        self.enthalpy_result = QLabel("--")
        self.specific_volume_result = QLabel("--")
        self.vapor_pressure_result = QLabel("--")
        self.humidity_ratio_result = QLabel("--")
        
        result_layout.addRow("相对湿度:", self.relative_humidity_result)
        result_layout.addRow("绝对湿度:", self.absolute_humidity_result)
        result_layout.addRow("露点温度:", self.dew_point_result)
        result_layout.addRow("湿球温度:", self.wet_bulb_result)
        result_layout.addRow("比焓:", self.enthalpy_result)
        result_layout.addRow("比容:", self.specific_volume_result)
        result_layout.addRow("水蒸气分压:", self.vapor_pressure_result)
        result_layout.addRow("湿度比:", self.humidity_ratio_result)
        
        main_layout.addWidget(result_group)
        
        # 计算说明
        info_text = QTextEdit()
        info_text.setMaximumHeight(120)
        info_text.setHtml("""
        <h4>计算说明:</h4>
        <ul>
        <li>至少需要输入干球温度和另外一个参数（相对湿度、绝对湿度、湿球温度或露点温度）</li>
        <li>大气压力默认为标准大气压101.325kPa</li>
        <li>计算基于ASHRAE标准和理想气体状态方程</li>
        <li>适用于常压下的湿空气物性计算</li>
        </ul>
        """)
        info_text.setReadOnly(True)
        main_layout.addWidget(info_text)
        
    def clear_inputs(self):
        """清空所有输入"""
        self.temp_input.clear()
        self.rh_input.clear()
        self.humidity_input.clear()
        self.wet_bulb_input.clear()
        self.dew_point_input.clear()
        self.pressure_input.setText("101.325")
        
        # 清空结果
        for label in [self.relative_humidity_result, self.absolute_humidity_result,
                     self.dew_point_result, self.wet_bulb_result, self.enthalpy_result,
                     self.specific_volume_result, self.vapor_pressure_result, 
                     self.humidity_ratio_result]:
            label.setText("--")
    
    def calculate(self):
        """执行湿空气计算"""
        try:
            # 获取输入值
            temp_str = self.temp_input.text().strip()
            if not temp_str:
                self.show_error("请输入干球温度")
                return
                
            temp = float(temp_str)
            if self.temp_unit.currentText() == "K":
                temp = temp - 273.15  # 转换为摄氏度
            
            # 获取压力并转换为kPa
            pressure = float(self.pressure_input.text())
            pressure_unit = self.pressure_unit.currentText()
            if pressure_unit == "bar":
                pressure_kpa = pressure * 100
            elif pressure_unit == "atm":
                pressure_kpa = pressure * 101.325
            else:  # kPa
                pressure_kpa = pressure
            
            # 确定已知参数并计算
            known_params = {}
            
            if self.rh_input.text().strip():
                known_params['rh'] = float(self.rh_input.text())
            if self.humidity_input.text().strip():
                humidity = float(self.humidity_input.text())
                if self.humidity_unit.currentText() == "g/kg干空气":
                    humidity = humidity / 1000  # 转换为kg/kg
                known_params['abs_humidity'] = humidity
            if self.wet_bulb_input.text().strip():
                known_params['wet_bulb'] = float(self.wet_bulb_input.text())
            if self.dew_point_input.text().strip():
                known_params['dew_point'] = float(self.dew_point_input.text())
            
            if len(known_params) == 0:
                self.show_error("请至少输入相对湿度、绝对湿度、湿球温度或露点温度中的一个参数")
                return
            
            # 这里实现湿空气计算逻辑
            results = self.calculate_wet_air_properties(temp, pressure_kpa, known_params)
            
            # 显示结果
            self.display_results(results)
            
        except ValueError as e:
            self.show_error("输入参数格式错误，请检查输入值")
        except Exception as e:
            self.show_error(f"计算错误: {str(e)}")
    
    def calculate_wet_air_properties(self, temp, pressure, known_params):
        """计算湿空气物性参数"""
        # 饱和水蒸气压力计算 (Antoine公式)
        def psat(t):
            # t in °C, returns kPa
            return 0.61078 * math.exp((17.27 * t) / (t + 237.3))
        
        # 根据已知参数计算其他参数
        if 'rh' in known_params:
            rh = known_params['rh'] / 100  # 转换为小数
            p_v = rh * psat(temp)
        elif 'abs_humidity' in known_params:
            W = known_params['abs_humidity']
            p_v = (W * pressure) / (0.622 + W)
            rh = p_v / psat(temp)
        elif 'dew_point' in known_params:
            dew_point = known_params['dew_point']
            p_v = psat(dew_point)
            rh = p_v / psat(temp)
        elif 'wet_bulb' in known_params:
            # 简化计算，实际应该使用迭代计算
            wet_bulb = known_params['wet_bulb']
            p_v_wet = psat(wet_bulb)
            p_v = p_v_wet - 0.000662 * pressure * (temp - wet_bulb)
            rh = p_v / psat(temp)
        else:
            raise ValueError("未知的计算条件")
        
        # 计算其他参数
        W = 0.622 * p_v / (pressure - p_v)  # 湿度比 kg/kg
        dew_point = (237.3 * math.log(p_v / 0.61078)) / (17.27 - math.log(p_v / 0.61078))
        
        # 比焓 (kJ/kg干空气)
        h = 1.006 * temp + W * (2501 + 1.86 * temp)
        
        # 比容 (m³/kg干空气)
        R_a = 0.287  # 干空气气体常数 kJ/(kg·K)
        T_k = temp + 273.15
        v = (R_a * T_k * (1 + 1.608 * W)) / pressure
        
        # 湿球温度近似计算
        wet_bulb_approx = temp * math.atan(0.151977 * (rh*100 + 8.313659)**0.5) + \
                          math.atan(temp + rh*100) - math.atan(rh*100 - 1.676331) + \
                          0.00391838 * (rh*100)**1.5 * math.atan(0.023101 * rh*100) - 4.686035
        
        return {
            'relative_humidity': rh * 100,
            'absolute_humidity': W,
            'dew_point': dew_point,
            'wet_bulb': wet_bulb_approx,
            'enthalpy': h,
            'specific_volume': v,
            'vapor_pressure': p_v,
            'humidity_ratio': W
        }
    
    def display_results(self, results):
        """显示计算结果"""
        self.relative_humidity_result.setText(f"{results['relative_humidity']:.2f} %")
        self.absolute_humidity_result.setText(f"{results['absolute_humidity']*1000:.2f} g/kg干空气")
        self.dew_point_result.setText(f"{results['dew_point']:.2f} °C")
        self.wet_bulb_result.setText(f"{results['wet_bulb']:.2f} °C")
        self.enthalpy_result.setText(f"{results['enthalpy']:.2f} kJ/kg")
        self.specific_volume_result.setText(f"{results['specific_volume']:.3f} m³/kg")
        self.vapor_pressure_result.setText(f"{results['vapor_pressure']:.3f} kPa")
        self.humidity_ratio_result.setText(f"{results['humidity_ratio']:.4f} kg/kg干空气")
    
    def show_error(self, message):
        """显示错误信息"""
        for label in [self.relative_humidity_result, self.absolute_humidity_result,
                     self.dew_point_result, self.wet_bulb_result, self.enthalpy_result,
                     self.specific_volume_result, self.vapor_pressure_result, 
                     self.humidity_ratio_result]:
            label.setText("计算错误")
        
        # 在实际应用中，这里可以显示一个错误对话框
        print(f"错误: {message}")


if __name__ == "__main__":
    # 测试代码
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    calculator = WetAirCalculator()
    calculator.resize(600, 700)
    calculator.show()
    
    sys.exit(app.exec())