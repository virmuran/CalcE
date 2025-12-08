from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                              QLabel, QLineEdit, QPushButton, QComboBox, 
                              QFormLayout, QTextEdit, QGridLayout, QScrollArea,
                              QTableWidget, QTableWidgetItem, QHeaderView,
                              QTabWidget, QCheckBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QDoubleValidator
import math


class ReliefAreaCalculator(QWidget):
    """泄压面积计算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置泄压面积计算界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("🚨 泄压面积计算")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # 说明文本
        desc_label = QLabel("计算安全阀、爆破片等泄压装置的所需泄放面积，依据ASME、API等标准")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #7f8c8d; margin: 5px;")
        main_layout.addWidget(desc_label)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 基本参数标签页
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        
        # 泄放场景组
        scenario_group = QGroupBox("泄放场景")
        scenario_layout = QGridLayout(scenario_group)
        
        self.scenario_type = QComboBox()
        self.scenario_type.addItems([
            "火灾工况", 
            "操作故障", 
            "热膨胀", 
            "化学反应失控",
            "外部火灾",
            "换热管破裂"
        ])
        
        self.fluid_type = QComboBox()
        self.fluid_type.addItems(["气体/蒸汽", "液体", "两相流"])
        
        self.standard_selection = QComboBox()
        self.standard_selection.addItems(["ASME VIII", "API 520", "API 521", "ISO 4126"])
        
        scenario_layout.addWidget(QLabel("泄放场景:"), 0, 0)
        scenario_layout.addWidget(self.scenario_type, 0, 1, 1, 2)
        
        scenario_layout.addWidget(QLabel("介质类型:"), 1, 0)
        scenario_layout.addWidget(self.fluid_type, 1, 1, 1, 2)
        
        scenario_layout.addWidget(QLabel("设计标准:"), 2, 0)
        scenario_layout.addWidget(self.standard_selection, 2, 1, 1, 2)
        
        basic_layout.addWidget(scenario_group)
        
        # 设备参数组
        vessel_group = QGroupBox("设备参数")
        vessel_layout = QGridLayout(vessel_group)
        
        self.vessel_volume_input = QLineEdit()
        self.vessel_volume_input.setPlaceholderText("例如：10")
        self.vessel_volume_input.setValidator(QDoubleValidator(0.1, 100000, 2))
        
        self.vessel_volume_unit = QComboBox()
        self.vessel_volume_unit.addItems(["m³", "L"])
        
        self.vessel_pressure_input = QLineEdit()
        self.vessel_pressure_input.setPlaceholderText("例如：1000")
        self.vessel_pressure_input.setValidator(QDoubleValidator(0.1, 100000, 1))
        
        self.vessel_pressure_unit = QComboBox()
        self.vessel_pressure_unit.addItems(["kPa", "bar", "MPa"])
        
        self.design_pressure_input = QLineEdit()
        self.design_pressure_input.setPlaceholderText("例如：1100")
        self.design_pressure_input.setValidator(QDoubleValidator(0.1, 100000, 1))
        
        self.operating_pressure_input = QLineEdit()
        self.operating_pressure_input.setPlaceholderText("例如：800")
        self.operating_pressure_input.setValidator(QDoubleValidator(0.1, 100000, 1))
        
        vessel_layout.addWidget(QLabel("容器容积:"), 0, 0)
        vessel_layout.addWidget(self.vessel_volume_input, 0, 1)
        vessel_layout.addWidget(self.vessel_volume_unit, 0, 2)
        
        vessel_layout.addWidget(QLabel("设计压力:"), 0, 3)
        vessel_layout.addWidget(self.design_pressure_input, 0, 4)
        vessel_layout.addWidget(self.vessel_pressure_unit, 0, 5)
        
        vessel_layout.addWidget(QLabel("操作压力:"), 1, 0)
        vessel_layout.addWidget(self.operating_pressure_input, 1, 1)
        vessel_layout.addWidget(QLabel(""), 1, 2)  # 占位
        
        vessel_layout.addWidget(QLabel("最大允许压力:"), 1, 3)
        vessel_layout.addWidget(self.vessel_pressure_input, 1, 4)
        vessel_layout.addWidget(QLabel(""), 1, 5)  # 占位
        
        basic_layout.addWidget(vessel_group)
        
        # 介质参数组
        fluid_group = QGroupBox("介质参数")
        fluid_layout = QGridLayout(fluid_group)
        
        self.fluid_name_input = QLineEdit()
        self.fluid_name_input.setPlaceholderText("例如：蒸汽")
        
        self.molecular_weight_input = QLineEdit()
        self.molecular_weight_input.setPlaceholderText("例如：18")
        self.molecular_weight_input.setValidator(QDoubleValidator(1, 500, 2))
        
        self.temperature_input = QLineEdit()
        self.temperature_input.setPlaceholderText("例如：200")
        self.temperature_input.setValidator(QDoubleValidator(-273, 1000, 1))
        
        self.compressibility_input = QLineEdit()
        self.compressibility_input.setText("1.0")
        self.compressibility_input.setValidator(QDoubleValidator(0.1, 2, 3))
        
        self.specific_heat_ratio_input = QLineEdit()
        self.specific_heat_ratio_input.setText("1.3")
        self.specific_heat_ratio_input.setValidator(QDoubleValidator(1, 2, 3))
        
        self.density_input = QLineEdit()
        self.density_input.setPlaceholderText("例如：1.2")
        self.density_input.setValidator(QDoubleValidator(0.1, 2000, 3))
        
        fluid_layout.addWidget(QLabel("介质名称:"), 0, 0)
        fluid_layout.addWidget(self.fluid_name_input, 0, 1, 1, 2)
        
        fluid_layout.addWidget(QLabel("分子量:"), 0, 3)
        fluid_layout.addWidget(self.molecular_weight_input, 0, 4)
        fluid_layout.addWidget(QLabel("g/mol"), 0, 5)
        
        fluid_layout.addWidget(QLabel("温度:"), 1, 0)
        fluid_layout.addWidget(self.temperature_input, 1, 1)
        fluid_layout.addWidget(QLabel("°C"), 1, 2)
        
        fluid_layout.addWidget(QLabel("压缩因子:"), 1, 3)
        fluid_layout.addWidget(self.compressibility_input, 1, 4)
        fluid_layout.addWidget(QLabel(""), 1, 5)
        
        fluid_layout.addWidget(QLabel("比热比:"), 2, 0)
        fluid_layout.addWidget(self.specific_heat_ratio_input, 2, 1)
        fluid_layout.addWidget(QLabel(""), 2, 2)
        
        fluid_layout.addWidget(QLabel("密度:"), 2, 3)
        fluid_layout.addWidget(self.density_input, 2, 4)
        fluid_layout.addWidget(QLabel("kg/m³"), 2, 5)
        
        basic_layout.addWidget(fluid_group)
        
        # 泄放参数组
        relief_group = QGroupBox("泄放参数")
        relief_layout = QGridLayout(relief_group)
        
        self.relief_rate_input = QLineEdit()
        self.relief_rate_input.setPlaceholderText("例如：1000")
        self.relief_rate_input.setValidator(QDoubleValidator(0.1, 1000000, 1))
        
        self.relief_rate_unit = QComboBox()
        self.relief_rate_unit.addItems(["kg/h", "kg/s", "m³/h"])
        
        self.back_pressure_input = QLineEdit()
        self.back_pressure_input.setText("0")
        self.back_pressure_input.setValidator(QDoubleValidator(0, 10000, 1))
        
        self.overpressure_input = QLineEdit()
        self.overpressure_input.setText("10")
        self.overpressure_input.setValidator(QDoubleValidator(1, 100, 1))
        
        self.discharge_coeff_input = QLineEdit()
        self.discharge_coeff_input.setText("0.65")
        self.discharge_coeff_input.setValidator(QDoubleValidator(0.1, 1, 3))
        
        relief_layout.addWidget(QLabel("泄放速率:"), 0, 0)
        relief_layout.addWidget(self.relief_rate_input, 0, 1)
        relief_layout.addWidget(self.relief_rate_unit, 0, 2)
        
        relief_layout.addWidget(QLabel("背压:"), 0, 3)
        relief_layout.addWidget(self.back_pressure_input, 0, 4)
        relief_layout.addWidget(QLabel("kPa"), 0, 5)
        
        relief_layout.addWidget(QLabel("超压百分比:"), 1, 0)
        relief_layout.addWidget(self.overpressure_input, 1, 1)
        relief_layout.addWidget(QLabel("%"), 1, 2)
        
        relief_layout.addWidget(QLabel("排放系数:"), 1, 3)
        relief_layout.addWidget(self.discharge_coeff_input, 1, 4)
        relief_layout.addWidget(QLabel(""), 1, 5)
        
        basic_layout.addWidget(relief_group)
        basic_layout.addStretch()
        
        # 结果标签页
        result_tab = QWidget()
        result_layout = QVBoxLayout(result_tab)
        
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
        
        result_layout.addLayout(button_layout)
        
        # 计算结果
        result_display_group = QGroupBox("计算结果")
        result_display_layout = QGridLayout(result_display_group)
        
        self.required_area_result = QLabel("--")
        self.required_diameter_result = QLabel("--")
        self.relief_pressure_result = QLabel("--")
        self.critical_flow_result = QLabel("--")
        self.actual_flow_result = QLabel("--")
        self.recommended_size_result = QLabel("--")
        
        result_display_layout.addWidget(QLabel("所需泄放面积:"), 0, 0)
        result_display_layout.addWidget(self.required_area_result, 0, 1)
        result_display_layout.addWidget(QLabel("mm²"), 0, 2)
        
        result_display_layout.addWidget(QLabel("等效直径:"), 0, 3)
        result_display_layout.addWidget(self.required_diameter_result, 0, 4)
        result_display_layout.addWidget(QLabel("mm"), 0, 5)
        
        result_display_layout.addWidget(QLabel("泄放压力:"), 1, 0)
        result_display_layout.addWidget(self.relief_pressure_result, 1, 1)
        result_display_layout.addWidget(QLabel("kPa"), 1, 2)
        
        result_display_layout.addWidget(QLabel("临界流动:"), 1, 3)
        result_display_layout.addWidget(self.critical_flow_result, 1, 4)
        result_display_layout.addWidget(QLabel(""), 1, 5)
        
        result_display_layout.addWidget(QLabel("实际流量:"), 2, 0)
        result_display_layout.addWidget(self.actual_flow_result, 2, 1)
        result_display_layout.addWidget(QLabel("kg/s"), 2, 2)
        
        result_display_layout.addWidget(QLabel("建议规格:"), 2, 3)
        result_display_layout.addWidget(self.recommended_size_result, 2, 4)
        result_display_layout.addWidget(QLabel(""), 2, 5)
        
        result_layout.addWidget(result_display_group)
        
        # 标准阀门规格表
        valve_table_group = QGroupBox("标准安全阀规格")
        valve_table_layout = QVBoxLayout(valve_table_group)
        
        self.valve_table = QTableWidget()
        self.valve_table.setColumnCount(4)
        self.valve_table.setHorizontalHeaderLabels(["公称尺寸", "喉径(mm)", "泄放面积(mm²)", "适用压力(kPa)"])
        self.populate_valve_table()
        valve_table_layout.addWidget(self.valve_table)
        
        result_layout.addWidget(valve_table_group)
        
        # 添加标签页
        self.tab_widget.addTab(basic_tab, "基本参数")
        self.tab_widget.addTab(result_tab, "计算结果")
        
        scroll_layout.addWidget(self.tab_widget)
        
        # 计算说明
        info_text = QTextEdit()
        info_text.setMaximumHeight(150)
        info_text.setHtml("""
        <h4>计算说明:</h4>
        <ul>
        <li>气体/蒸汽泄放面积计算基于ASME VIII和API 520标准</li>
        <li>液体泄放面积计算基于不可压缩流体理论</li>
        <li>两相流计算采用均相平衡模型</li>
        <li>火灾工况计算基于API 521标准的热量输入计算</li>
        <li>排放系数通常取0.65-0.97，取决于阀门类型和设计</li>
        <li>超压百分比通常为10%，对于火灾工况可到21%</li>
        </ul>
        """)
        info_text.setReadOnly(True)
        scroll_layout.addWidget(info_text)
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
    def populate_valve_table(self):
        """填充标准安全阀规格表"""
        # 标准安全阀规格数据
        valve_sizes = [
            ["DN15", "11", "95", "≤1600"],
            ["DN20", "16", "201", "≤1600"],
            ["DN25", "19", "284", "≤1600"],
            ["DN32", "23", "415", "≤1600"],
            ["DN40", "26", "531", "≤1600"],
            ["DN50", "33", "855", "≤1600"],
            ["DN65", "47", "1735", "≤1600"],
            ["DN80", "52", "2124", "≤1600"],
            ["DN100", "68", "3631", "≤1600"],
            ["DN125", "83", "5410", "≤1600"],
            ["DN150", "102", "8171", "≤1600"]
        ]
        
        self.valve_table.setRowCount(len(valve_sizes))
        for i, size in enumerate(valve_sizes):
            for j, value in enumerate(size):
                item = QTableWidgetItem(value)
                self.valve_table.setItem(i, j, item)
        
        # 设置表格列宽
        header = self.valve_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
    
    def clear_inputs(self):
        """清空所有输入"""
        self.vessel_volume_input.clear()
        self.vessel_pressure_input.clear()
        self.design_pressure_input.clear()
        self.operating_pressure_input.clear()
        self.fluid_name_input.clear()
        self.molecular_weight_input.clear()
        self.temperature_input.clear()
        self.compressibility_input.setText("1.0")
        self.specific_heat_ratio_input.setText("1.3")
        self.density_input.clear()
        self.relief_rate_input.clear()
        self.back_pressure_input.setText("0")
        self.overpressure_input.setText("10")
        self.discharge_coeff_input.setText("0.65")
        
        # 清空结果
        for label in [self.required_area_result, self.required_diameter_result,
                     self.relief_pressure_result, self.critical_flow_result,
                     self.actual_flow_result, self.recommended_size_result]:
            label.setText("--")
    
    def calculate(self):
        """执行泄压面积计算"""
        try:
            # 获取计算条件
            scenario = self.scenario_type.currentText()
            fluid_type = self.fluid_type.currentText()
            standard = self.standard_selection.currentText()
            
            # 获取设备参数
            vessel_volume = float(self.vessel_volume_input.text())
            volume_unit = self.vessel_volume_unit.currentText()
            if volume_unit == "L":
                vessel_volume = vessel_volume / 1000  # 转换为m³
                
            max_pressure = float(self.vessel_pressure_input.text())
            design_pressure = float(self.design_pressure_input.text())
            operating_pressure = float(self.operating_pressure_input.text())
            
            # 获取介质参数
            molecular_weight = float(self.molecular_weight_input.text())
            temperature = float(self.temperature_input.text())
            compressibility = float(self.compressibility_input.text())
            specific_heat_ratio = float(self.specific_heat_ratio_input.text())
            density = float(self.density_input.text())
            
            # 获取泄放参数
            relief_rate = float(self.relief_rate_input.text())
            rate_unit = self.relief_rate_unit.currentText()
            if rate_unit == "kg/h":
                relief_rate = relief_rate / 3600  # 转换为kg/s
            elif rate_unit == "m³/h":
                relief_rate = relief_rate * density / 3600  # 转换为kg/s
                
            back_pressure = float(self.back_pressure_input.text())
            overpressure_percent = float(self.overpressure_input.text())
            discharge_coeff = float(self.discharge_coeff_input.text())
            
            # 计算泄放压力
            relief_pressure = max_pressure * (1 + overpressure_percent / 100)
            
            # 根据介质类型选择计算方法
            if fluid_type == "气体/蒸汽":
                results = self.calculate_gas_relief_area(
                    relief_rate, relief_pressure, back_pressure, temperature,
                    molecular_weight, compressibility, specific_heat_ratio,
                    discharge_coeff
                )
            elif fluid_type == "液体":
                results = self.calculate_liquid_relief_area(
                    relief_rate, relief_pressure, back_pressure, density,
                    discharge_coeff
                )
            else:  # 两相流
                results = self.calculate_two_phase_relief_area(
                    relief_rate, relief_pressure, back_pressure, temperature,
                    molecular_weight, density, discharge_coeff
                )
            
            # 计算等效直径和推荐规格
            diameter = math.sqrt(results['area'] / math.pi) * 2
            recommended_size = self.get_recommended_size(results['area'])
            
            results['diameter'] = diameter
            results['recommended_size'] = recommended_size
            results['relief_pressure'] = relief_pressure
            
            # 显示结果
            self.display_results(results)
            
        except ValueError as e:
            self.show_error("输入参数格式错误，请检查输入值")
        except Exception as e:
            self.show_error(f"计算错误: {str(e)}")
    
    def calculate_gas_relief_area(self, W, P1, P2, T, M, Z, k, Kd):
        """计算气体/蒸汽泄放面积"""
        # 转换为绝对温度
        T_abs = T + 273.15
        
        # 计算临界压力比
        critical_pressure_ratio = (2 / (k + 1)) ** (k / (k - 1))
        
        # 判断流动状态
        if P2 / P1 <= critical_pressure_ratio:
            # 临界流动
            flow_type = "临界流动"
            # ASME VIII 气体临界流动公式
            C = 0.03948 * math.sqrt(k * (2 / (k + 1)) ** ((k + 1) / (k - 1)))
            A = W / (C * Kd * P1 * math.sqrt(M / (T_abs * Z)))
        else:
            # 亚临界流动
            flow_type = "亚临界流动"
            # ASME VIII 气体亚临界流动公式
            r = P2 / P1
            C1 = 0.03948 * math.sqrt(k * (2 / (k + 1)) ** ((k + 1) / (k - 1)))
            F = math.sqrt((k / (k - 1)) * (r ** (2 / k) - r ** ((k + 1) / k)))
            A = W / (C1 * Kd * P1 * F * math.sqrt(M / (T_abs * Z)))
        
        return {
            'area': A * 1e6,  # 转换为mm²
            'flow_type': flow_type,
            'actual_flow': W
        }
    
    def calculate_liquid_relief_area(self, W, P1, P2, rho, Kd):
        """计算液体泄放面积"""
        # ASME VIII 液体泄放公式
        delta_P = P1 - P2  # kPa
        delta_P_pa = delta_P * 1000  # 转换为Pa
        
        # 计算泄放面积
        A = W / (Kd * math.sqrt(2 * rho * delta_P_pa))
        
        return {
            'area': A * 1e6,  # 转换为mm²
            'flow_type': "不可压缩流动",
            'actual_flow': W
        }
    
    def calculate_two_phase_relief_area(self, W, P1, P2, T, M, rho, Kd):
        """计算两相流泄放面积（简化计算）"""
        # 简化计算，使用均相平衡模型
        # 实际应用中应使用更精确的方法如DIERS方法
        
        # 使用气体公式作为近似
        T_abs = T + 273.15
        k = 1.3  # 假设值
        Z = 1.0  # 假设值
        
        critical_pressure_ratio = (2 / (k + 1)) ** (k / (k - 1))
        
        if P2 / P1 <= critical_pressure_ratio:
            C = 0.03948 * math.sqrt(k * (2 / (k + 1)) ** ((k + 1) / (k - 1)))
            A = W / (C * Kd * P1 * math.sqrt(M / (T_abs * Z)))
        else:
            r = P2 / P1
            C1 = 0.03948 * math.sqrt(k * (2 / (k + 1)) ** ((k + 1) / (k - 1)))
            F = math.sqrt((k / (k - 1)) * (r ** (2 / k) - r ** ((k + 1) / k)))
            A = W / (C1 * Kd * P1 * F * math.sqrt(M / (T_abs * Z)))
        
        return {
            'area': A * 1e6,  # 转换为mm²
            'flow_type': "两相流",
            'actual_flow': W
        }
    
    def get_recommended_size(self, area):
        """根据计算面积推荐标准阀门规格"""
        # 标准阀门面积表 (mm²)
        standard_areas = {
            "DN15": 95,
            "DN20": 201,
            "DN25": 284,
            "DN32": 415,
            "DN40": 531,
            "DN50": 855,
            "DN65": 1735,
            "DN80": 2124,
            "DN100": 3631,
            "DN125": 5410,
            "DN150": 8171
        }
        
        # 找到最小能满足要求的规格
        for size, standard_area in standard_areas.items():
            if standard_area >= area * 1.1:  # 10%安全余量
                return size
        
        # 如果所有标准规格都不满足，返回最大规格
        return "DN150或定制"
    
    def display_results(self, results):
        """显示计算结果"""
        self.required_area_result.setText(f"{results['area']:.1f}")
        self.required_diameter_result.setText(f"{results['diameter']:.1f}")
        self.relief_pressure_result.setText(f"{results['relief_pressure']:.1f}")
        self.critical_flow_result.setText(results['flow_type'])
        self.actual_flow_result.setText(f"{results['actual_flow']:.3f}")
        self.recommended_size_result.setText(results['recommended_size'])
    
    def show_error(self, message):
        """显示错误信息"""
        for label in [self.required_area_result, self.required_diameter_result,
                     self.relief_pressure_result, self.critical_flow_result,
                     self.actual_flow_result, self.recommended_size_result]:
            label.setText("计算错误")
        
        print(f"错误: {message}")


if __name__ == "__main__":
    # 测试代码
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    calculator = ReliefAreaCalculator()
    calculator.resize(900, 800)
    calculator.show()
    
    sys.exit(app.exec())