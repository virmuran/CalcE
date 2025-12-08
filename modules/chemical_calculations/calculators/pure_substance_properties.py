from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                              QLabel, QLineEdit, QComboBox, QPushButton, 
                              QTextEdit, QTableWidget, QTableWidgetItem,
                              QHeaderView, QMessageBox, QTabWidget, QDoubleSpinBox,
                              QCheckBox, QRadioButton, QButtonGroup, QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QDoubleValidator
import math

class PureSubstanceProperties(QWidget):
    """纯物质物性数据查询"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.substance_data = self.load_substance_data()
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("🧪 纯物质物性数据查询")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 添加查询标签页
        self.query_tab = self.create_query_tab()
        self.tab_widget.addTab(self.query_tab, "🔍 物性查询")
        
        # 添加物质库标签页
        self.substance_lib_tab = self.create_substance_lib_tab()
        self.tab_widget.addTab(self.substance_lib_tab, "📚 物质库")
        
        # 添加计算公式标签页
        self.formula_tab = self.create_formula_tab()
        self.tab_widget.addTab(self.formula_tab, "📐 计算公式")
        
        main_layout.addWidget(self.tab_widget)
    
    def create_query_tab(self):
        """创建查询标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 查询条件组
        query_group = QGroupBox("🔍 查询条件")
        query_layout = QVBoxLayout(query_group)
        
        # 物质选择
        substance_layout = QHBoxLayout()
        substance_layout.addWidget(QLabel("物质类别:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "无机物", "有机物", "金属", "气体", "液体", "固体"
        ])
        self.category_combo.currentTextChanged.connect(self.on_category_changed)
        substance_layout.addWidget(self.category_combo)
        
        substance_layout.addWidget(QLabel("具体物质:"))
        self.substance_combo = QComboBox()
        substance_layout.addWidget(self.substance_combo)
        
        substance_layout.addWidget(QLabel("CAS号:"))
        self.cas_label = QLabel("")
        substance_layout.addWidget(self.cas_label)
        
        query_layout.addLayout(substance_layout)
        
        # 温度压力条件
        condition_layout = QHBoxLayout()
        condition_layout.addWidget(QLabel("温度 (°C):"))
        self.temperature_input = QDoubleSpinBox()
        self.temperature_input.setRange(-273, 5000)
        self.temperature_input.setValue(25)
        self.temperature_input.setSuffix(" °C")
        condition_layout.addWidget(self.temperature_input)
        
        condition_layout.addWidget(QLabel("压力 (kPa):"))
        self.pressure_input = QDoubleSpinBox()
        self.pressure_input.setRange(0.1, 100000)
        self.pressure_input.setValue(101.3)
        self.pressure_input.setSuffix(" kPa")
        condition_layout.addWidget(self.pressure_input)
        
        condition_layout.addWidget(QLabel("状态:"))
        self.state_label = QLabel("液态")
        condition_layout.addWidget(self.state_label)
        
        query_layout.addLayout(condition_layout)
        
        layout.addWidget(query_group)
        
        # 按钮组
        button_layout = QHBoxLayout()
        self.query_btn = QPushButton("🚀 查询物性数据")
        self.query_btn.clicked.connect(self.query_properties)
        self.query_btn.setStyleSheet("QPushButton { background-color: #8e44ad; color: white; font-weight: bold; }")
        button_layout.addWidget(self.query_btn)
        
        self.temp_calc_btn = QPushButton("🔧 温度影响计算")
        self.temp_calc_btn.clicked.connect(self.temperature_calculation)
        self.temp_calc_btn.setStyleSheet("QPushButton { background-color: #3498db; color: white; }")
        button_layout.addWidget(self.temp_calc_btn)
        
        self.clear_btn = QPushButton("🗑️ 清空")
        self.clear_btn.clicked.connect(self.clear_inputs)
        self.clear_btn.setStyleSheet("QPushButton { background-color: #95a5a6; color: white; }")
        button_layout.addWidget(self.clear_btn)
        
        layout.addLayout(button_layout)
        
        # 基本物性组
        basic_prop_group = QGroupBox("📊 基本物性")
        basic_prop_layout = QVBoxLayout(basic_prop_group)
        
        self.basic_prop_table = QTableWidget()
        self.basic_prop_table.setColumnCount(3)
        self.basic_prop_table.setHorizontalHeaderLabels(["物性", "数值", "单位"])
        basic_prop_layout.addWidget(self.basic_prop_table)
        
        layout.addWidget(basic_prop_group)
        
        # 热力学性质组
        thermo_prop_group = QGroupBox("🔥 热力学性质")
        thermo_prop_layout = QVBoxLayout(thermo_prop_group)
        
        self.thermo_prop_table = QTableWidget()
        self.thermo_prop_table.setColumnCount(3)
        self.thermo_prop_table.setHorizontalHeaderLabels(["物性", "数值", "单位"])
        thermo_prop_layout.addWidget(self.thermo_prop_table)
        
        layout.addWidget(thermo_prop_group)
        
        # 初始化下拉框
        self.on_category_changed(self.category_combo.currentText())
        
        return tab
    
    def on_category_changed(self, category):
        """类别改变事件"""
        substances = {
            "无机物": ["水", "氨", "硫酸", "盐酸", "氢氧化钠", "氯化钠", "二氧化碳"],
            "有机物": ["甲烷", "乙烷", "丙烷", "乙烯", "丙烯", "苯", "甲苯", "甲醇", "乙醇"],
            "金属": ["铁", "铜", "铝", "锌", "铅", "银", "金"],
            "气体": ["空气", "氧气", "氮气", "氢气", "氦气", "氩气"],
            "液体": ["水", "乙醇", "甲醇", "丙酮", "苯", "甲苯", "四氯化碳"],
            "固体": ["冰", "食盐", "石英", "石墨", "金刚石"]
        }
        
        self.substance_combo.clear()
        if category in substances:
            self.substance_combo.addItems(substances[category])
        
        # 默认选择第一个物质
        if self.substance_combo.count() > 0:
            self.substance_combo.setCurrentIndex(0)
            self.update_cas_number()
    
    def update_cas_number(self):
        """更新CAS号"""
        substance = self.substance_combo.currentText()
        cas_numbers = {
            "水": "7732-18-5",
            "氨": "7664-41-7",
            "硫酸": "7664-93-9",
            "盐酸": "7647-01-0",
            "氢氧化钠": "1310-73-2",
            "氯化钠": "7647-14-5",
            "二氧化碳": "124-38-9",
            "甲烷": "74-82-8",
            "乙烷": "74-84-0",
            "丙烷": "74-98-6",
            "乙烯": "74-85-1",
            "丙烯": "115-07-1",
            "苯": "71-43-2",
            "甲苯": "108-88-3",
            "甲醇": "67-56-1",
            "乙醇": "64-17-5",
            "铁": "7439-89-6",
            "铜": "7440-50-8",
            "铝": "7429-90-5",
            "空气": "132259-10-0",
            "氧气": "7782-44-7",
            "氮气": "7727-37-9",
            "氢气": "1333-74-0"
        }
        
        self.cas_label.setText(cas_numbers.get(substance, "未知"))
    
    def create_substance_lib_tab(self):
        """创建物质库标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 物质库说明
        info_label = QLabel("常见纯物质物性数据参考")
        info_label.setFont(QFont("Arial", 12, QFont.Bold))
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # 物质参数表
        substance_table = QTableWidget()
        substance_table.setColumnCount(7)
        substance_table.setHorizontalHeaderLabels(["物质", "分子式", "分子量", "沸点(°C)", "熔点(°C)", "密度(g/cm³)", "CAS号"])
        
        substance_data = [
            ["水", "H₂O", "18.02", "100.0", "0.0", "1.000", "7732-18-5"],
            ["氨", "NH₃", "17.03", "-33.3", "-77.7", "0.682", "7664-41-7"],
            ["硫酸", "H₂SO₄", "98.08", "337.0", "10.4", "1.840", "7664-93-9"],
            ["盐酸", "HCl", "36.46", "-85.0", "-114.2", "1.200", "7647-01-0"],
            ["氢氧化钠", "NaOH", "40.00", "1388", "323", "2.130", "1310-73-2"],
            ["氯化钠", "NaCl", "58.44", "1465", "801", "2.165", "7647-14-5"],
            ["二氧化碳", "CO₂", "44.01", "-78.5", "-56.6", "1.980", "124-38-9"],
            ["甲烷", "CH₄", "16.04", "-161.5", "-182.5", "0.424", "74-82-8"],
            ["乙烷", "C₂H₆", "30.07", "-88.6", "-182.8", "0.546", "74-84-0"],
            ["丙烷", "C₃H₈", "44.10", "-42.1", "-187.7", "0.493", "74-98-6"],
            ["乙烯", "C₂H₄", "28.05", "-103.7", "-169.2", "0.610", "74-85-1"],
            ["丙烯", "C₃H₆", "42.08", "-47.6", "-185.2", "0.519", "115-07-1"],
            ["苯", "C₆H₆", "78.11", "80.1", "5.5", "0.879", "71-43-2"],
            ["甲苯", "C₇H₈", "92.14", "110.6", "-95.0", "0.867", "108-88-3"],
            ["甲醇", "CH₃OH", "32.04", "64.7", "-97.6", "0.791", "67-56-1"],
            ["乙醇", "C₂H₅OH", "46.07", "78.4", "-114.1", "0.789", "64-17-5"],
            ["铁", "Fe", "55.85", "2862", "1538", "7.874", "7439-89-6"],
            ["铜", "Cu", "63.55", "2562", "1085", "8.960", "7440-50-8"],
            ["铝", "Al", "26.98", "2467", "660", "2.700", "7429-90-5"],
            ["氧气", "O₂", "32.00", "-183.0", "-218.8", "1.429", "7782-44-7"],
            ["氮气", "N₂", "28.01", "-195.8", "-210.0", "1.251", "7727-37-9"],
            ["氢气", "H₂", "2.02", "-252.9", "-259.2", "0.090", "1333-74-0"]
        ]
        
        substance_table.setRowCount(len(substance_data))
        for i, row_data in enumerate(substance_data):
            for j, data in enumerate(row_data):
                item = QTableWidgetItem(data)
                item.setTextAlignment(Qt.AlignCenter)
                substance_table.setItem(i, j, item)
        
        # 调整列宽
        header = substance_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)
        
        layout.addWidget(substance_table)
        
        return tab
    
    def create_formula_tab(self):
        """创建计算公式标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 计算公式说明
        formula_text = QTextEdit()
        formula_text.setReadOnly(True)
        formula_text.setHtml(self.get_formula_html())
        layout.addWidget(formula_text)
        
        return tab
    
    def get_formula_html(self):
        """获取计算公式HTML内容"""
        return """
        <h2>📐 物性计算公式</h2>
        
        <h3>1. 密度计算</h3>
        <p><b>理想气体密度：</b>ρ = P × M / (R × T)</p>
        <p>其中：P-压力(Pa)，M-分子量(kg/mol)，R-气体常数(8.314 J/mol·K)，T-温度(K)</p>
        
        <h3>2. 蒸气压计算</h3>
        <p><b>Antoine方程：</b>log₁₀(P) = A - B / (T + C)</p>
        <p>其中：P-蒸气压(mmHg)，T-温度(°C)，A、B、C为物质常数</p>
        
        <h3>3. 粘度计算</h3>
        <p><b>液体粘度：</b>μ = A × exp(B / T)</p>
        <p><b>气体粘度：</b>μ = μ₀ × (T/T₀)<sup>n</sup></p>
        <p>其中：A、B、μ₀、T₀、n为物质常数</p>
        
        <h3>4. 热导率计算</h3>
        <p><b>液体热导率：</b>k = A + B × T + C × T²</p>
        <p><b>气体热导率：</b>k = k₀ × (T/T₀)<sup>m</sup></p>
        
        <h3>5. 热容计算</h3>
        <p><b>定压热容：</b>C<sub>p</sub> = A + B × T + C × T² + D × T³</p>
        <p><b>定容热容：</b>C<sub>v</sub> = C<sub>p</sub> - R</p>
        
        <h3>6. 临界性质关系</h3>
        <p><b>对比温度：</b>T<sub>r</sub> = T / T<sub>c</sub></p>
        <p><b>对比压力：</b>P<sub>r</sub> = P / P<sub>c</sub></p>
        <p><b>对比体积：</b>V<sub>r</sub> = V / V<sub>c</sub></p>
        
        <h3>7. 状态方程</h3>
        <p><b>理想气体：</b>PV = nRT</p>
        <p><b>van der Waals：</b>(P + a/V²)(V - b) = RT</p>
        <p><b>Redlich-Kwong：</b>P = RT/(V - b) - a/(√T × V(V + b))</p>
        
        <h3>8. 热力学关系</h3>
        <p><b>焓变：</b>ΔH = ∫C<sub>p</sub>dT</p>
        <p><b>熵变：</b>ΔS = ∫(C<sub>p</sub>/T)dT</p>
        <p><b>Gibbs自由能：</b>ΔG = ΔH - TΔS</p>
        
        <h3>📖 常用常数</h3>
        <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr style="background-color: #3498db; color: white;">
            <th style="padding: 8px;">常数</th>
            <th style="padding: 8px;">符号</th>
            <th style="padding: 8px;">数值</th>
            <th style="padding: 8px;">单位</th>
        </tr>
        <tr>
            <td style="padding: 8px;">通用气体常数</td>
            <td style="padding: 8px;">R</td>
            <td style="padding: 8px;">8.314</td>
            <td style="padding: 8px;">J/mol·K</td>
        </tr>
        <tr>
            <td style="padding: 8px;">Avogadro常数</td>
            <td style="padding: 8px;">N<sub>A</sub></td>
            <td style="padding: 8px;">6.022×10²³</td>
            <td style="padding: 8px;">mol⁻¹</td>
        </tr>
        <tr>
            <td style="padding: 8px;">Boltzmann常数</td>
            <td style="padding: 8px;">k</td>
            <td style="padding: 8px;">1.381×10⁻²³</td>
            <td style="padding: 8px;">J/K</td>
        </tr>
        <tr>
            <td style="padding: 8px;">标准大气压</td>
            <td style="padding: 8px;">P<sub>atm</sub></td>
            <td style="padding: 8px;">101.325</td>
            <td style="padding: 8px;">kPa</td>
        </tr>
        </table>
        
        <h3>📚 参考数据源</h3>
        <ul>
            <li>CRC Handbook of Chemistry and Physics</li>
            <li>Perry's Chemical Engineers' Handbook</li>
            <li>NIST Chemistry WebBook</li>
            <li>DIPPR Project 801 Database</li>
        </ul>
        """
    
    def load_substance_data(self):
        """加载物质数据"""
        # 模拟物质数据库
        substance_data = {
            "水": {
                "basic": {
                    "分子式": "H₂O", "分子量": 18.02, "CAS号": "7732-18-5",
                    "沸点": 100.0, "熔点": 0.0, "临界温度": 373.9,
                    "临界压力": 22064, "临界密度": 0.322
                },
                "thermal": {
                    "密度": 0.997, "粘度": 0.89, "热导率": 0.606,
                    "比热容": 4.181, "蒸发热": 2257, "表面张力": 72.0
                },
                "formula_params": {
                    "antoine_A": 8.07131, "antoine_B": 1730.63, "antoine_C": 233.426
                }
            },
            "乙醇": {
                "basic": {
                    "分子式": "C₂H₅OH", "分子量": 46.07, "CAS号": "64-17-5",
                    "沸点": 78.4, "熔点": -114.1, "临界温度": 513.9,
                    "临界压力": 6148, "临界密度": 0.276
                },
                "thermal": {
                    "密度": 0.789, "粘度": 1.07, "热导率": 0.167,
                    "比热容": 2.44, "蒸发热": 841, "表面张力": 22.3
                },
                "formula_params": {
                    "antoine_A": 8.11220, "antoine_B": 1592.86, "antoine_C": 226.184
                }
            },
            "甲醇": {
                "basic": {
                    "分子式": "CH₃OH", "分子量": 32.04, "CAS号": "67-56-1",
                    "沸点": 64.7, "熔点": -97.6, "临界温度": 512.6,
                    "临界压力": 8094, "临界密度": 0.272
                },
                "thermal": {
                    "密度": 0.791, "粘度": 0.59, "热导率": 0.202,
                    "比热容": 2.53, "蒸发热": 1100, "表面张力": 22.6
                },
                "formula_params": {
                    "antoine_A": 8.08097, "antoine_B": 1582.27, "antoine_C": 239.726
                }
            },
            "苯": {
                "basic": {
                    "分子式": "C₆H₆", "分子量": 78.11, "CAS号": "71-43-2",
                    "沸点": 80.1, "熔点": 5.5, "临界温度": 562.1,
                    "临界压力": 4898, "临界密度": 0.304
                },
                "thermal": {
                    "密度": 0.879, "粘度": 0.65, "热导率": 0.144,
                    "比热容": 1.73, "蒸发热": 394, "表面张力": 28.9
                },
                "formula_params": {
                    "antoine_A": 6.90565, "antoine_B": 1211.03, "antoine_C": 220.790
                }
            },
            "氨": {
                "basic": {
                    "分子式": "NH₃", "分子量": 17.03, "CAS号": "7664-41-7",
                    "沸点": -33.3, "熔点": -77.7, "临界温度": 405.5,
                    "临界压力": 11333, "临界密度": 0.235
                },
                "thermal": {
                    "密度": 0.682, "粘度": 0.22, "热导率": 0.522,
                    "比热容": 4.70, "蒸发热": 1371, "表面张力": 23.4
                },
                "formula_params": {
                    "antoine_A": 7.55466, "antoine_B": 1002.71, "antoine_C": 247.885
                }
            }
        }
        
        return substance_data
    
    def query_properties(self):
        """查询物性数据"""
        try:
            # 获取查询条件
            substance = self.substance_combo.currentText()
            temperature = self.temperature_input.value()
            pressure = self.pressure_input.value()
            
            # 查询数据
            if substance in self.substance_data:
                data = self.substance_data[substance]
                self.update_state_label(substance, temperature)
                self.display_basic_properties(data["basic"])
                self.display_thermal_properties(data["thermal"], temperature, pressure)
            else:
                QMessageBox.information(self, "查询结果", f"未找到物质 '{substance}' 的物性数据")
                
        except Exception as e:
            QMessageBox.warning(self, "查询错误", f"查询过程中发生错误: {str(e)}")
    
    def update_state_label(self, substance, temperature):
        """更新状态标签"""
        if substance in self.substance_data:
            data = self.substance_data[substance]
            boiling_point = data["basic"]["沸点"]
            melting_point = data["basic"]["熔点"]
            
            if temperature > boiling_point:
                state = "气态"
            elif temperature < melting_point:
                state = "固态"
            else:
                state = "液态"
            
            self.state_label.setText(state)
    
    def display_basic_properties(self, basic_data):
        """显示基本物性"""
        basic_props = [
            ["分子式", basic_data["分子式"], "-"],
            ["分子量", f"{basic_data['分子量']}", "g/mol"],
            ["CAS号", basic_data["CAS号"], "-"],
            ["沸点", f"{basic_data['沸点']}", "°C"],
            ["熔点", f"{basic_data['熔点']}", "°C"],
            ["临界温度", f"{basic_data['临界温度']}", "K"],
            ["临界压力", f"{basic_data['临界压力']}", "kPa"],
            ["临界密度", f"{basic_data['临界密度']}", "g/cm³"]
        ]
        
        self.update_table(self.basic_prop_table, basic_props)
    
    def display_thermal_properties(self, thermal_data, temperature, pressure):
        """显示热力学性质"""
        # 计算温度影响
        density = self.calculate_temperature_effect(thermal_data["密度"], temperature, "density")
        viscosity = self.calculate_temperature_effect(thermal_data["粘度"], temperature, "viscosity")
        thermal_cond = self.calculate_temperature_effect(thermal_data["热导率"], temperature, "thermal_cond")
        heat_capacity = self.calculate_temperature_effect(thermal_data["比热容"], temperature, "heat_capacity")
        
        thermal_props = [
            ["密度", f"{density:.3f}", "g/cm³"],
            ["粘度", f"{viscosity:.3f}", "mPa·s"],
            ["热导率", f"{thermal_cond:.3f}", "W/m·K"],
            ["比热容", f"{heat_capacity:.3f}", "kJ/kg·K"],
            ["蒸发热", f"{thermal_data['蒸发热']}", "kJ/kg"],
            ["表面张力", f"{thermal_data['表面张力']}", "mN/m"]
        ]
        
        self.update_table(self.thermo_prop_table, thermal_props)
    
    def calculate_temperature_effect(self, base_value, temperature, property_type):
        """计算温度对物性的影响"""
        # 简化的温度修正模型
        base_temp = 25  # 基准温度25°C
        
        if property_type == "density":
            # 密度随温度升高而降低
            temp_coeff = -0.0005  # 温度系数
            return base_value * (1 + temp_coeff * (temperature - base_temp))
        elif property_type == "viscosity":
            # 粘度随温度升高而降低
            temp_coeff = -0.02  # 温度系数
            return base_value * (1 + temp_coeff * (temperature - base_temp) / 100)
        elif property_type == "thermal_cond":
            # 热导率随温度变化较小
            temp_coeff = 0.001  # 温度系数
            return base_value * (1 + temp_coeff * (temperature - base_temp))
        elif property_type == "heat_capacity":
            # 比热容随温度变化
            temp_coeff = 0.002  # 温度系数
            return base_value * (1 + temp_coeff * (temperature - base_temp) / 100)
        else:
            return base_value
    
    def update_table(self, table, data):
        """更新表格数据"""
        table.setRowCount(len(data))
        for i, row_data in enumerate(data):
            for j, data_item in enumerate(row_data):
                item = QTableWidgetItem(data_item)
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(i, j, item)
        
        # 调整列宽
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
    
    def temperature_calculation(self):
        """温度影响计算"""
        try:
            substance = self.substance_combo.currentText()
            if substance not in self.substance_data:
                QMessageBox.warning(self, "计算错误", "请先选择有效的物质")
                return
            
            # 创建温度范围数据
            temperatures = [0, 25, 50, 75, 100]
            data = self.substance_data[substance]["thermal"]
            
            result_text = f"<h3>🌡️ {substance} 温度影响分析</h3>"
            result_text += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
            result_text += "<tr style='background-color: #f8f9fa;'>"
            result_text += "<th style='padding: 8px;'>温度(°C)</th>"
            result_text += "<th style='padding: 8px;'>密度(g/cm³)</th>"
            result_text += "<th style='padding: 8px;'>粘度(mPa·s)</th>"
            result_text += "<th style='padding: 8px;'>热导率(W/m·K)</th>"
            result_text += "<th style='padding: 8px;'>比热容(kJ/kg·K)</th>"
            result_text += "</tr>"
            
            for temp in temperatures:
                density = self.calculate_temperature_effect(data["密度"], temp, "density")
                viscosity = self.calculate_temperature_effect(data["粘度"], temp, "viscosity")
                thermal_cond = self.calculate_temperature_effect(data["热导率"], temp, "thermal_cond")
                heat_capacity = self.calculate_temperature_effect(data["比热容"], temp, "heat_capacity")
                
                result_text += f"""
                <tr>
                    <td style='padding: 8px;'>{temp}</td>
                    <td style='padding: 8px;'>{density:.3f}</td>
                    <td style='padding: 8px;'>{viscosity:.3f}</td>
                    <td style='padding: 8px;'>{thermal_cond:.3f}</td>
                    <td style='padding: 8px;'>{heat_capacity:.3f}</td>
                </tr>
                """
            
            result_text += "</table>"
            
            QMessageBox.information(self, "温度影响分析", result_text.replace("<table", "<table width='100%'").replace("<h3>", "").replace("</h3>", ""))
            
        except Exception as e:
            QMessageBox.warning(self, "计算错误", f"温度影响计算失败: {str(e)}")
    
    def clear_inputs(self):
        """清空输入"""
        self.category_combo.setCurrentIndex(0)
        self.temperature_input.setValue(25)
        self.pressure_input.setValue(101.3)
        self.basic_prop_table.setRowCount(0)
        self.thermo_prop_table.setRowCount(0)

if __name__ == "__main__":
    # 测试代码
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    widget = PureSubstanceProperties()
    widget.resize(900, 700)
    widget.show()
    
    sys.exit(app.exec())