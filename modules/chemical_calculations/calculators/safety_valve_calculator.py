from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                              QLabel, QLineEdit, QComboBox, QPushButton, 
                              QTextEdit, QTableWidget, QTableWidgetItem,
                              QHeaderView, QMessageBox, QTabWidget, QDoubleSpinBox,
                              QCheckBox, QRadioButton, QButtonGroup, QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QDoubleValidator
import math

class SafetyValveCalculator(QWidget):
    """安全阀计算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("🛡️ 安全阀计算")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 添加计算标签页
        self.calculation_tab = self.create_calculation_tab()
        self.tab_widget.addTab(self.calculation_tab, "📊 安全阀计算")
        
        # 添加选型指南标签页
        self.selection_tab = self.create_selection_tab()
        self.tab_widget.addTab(self.selection_tab, "📋 选型指南")
        
        main_layout.addWidget(self.tab_widget)
    
    def create_calculation_tab(self):
        """创建计算标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 工况条件组
        condition_group = QGroupBox("⚙️ 工况条件")
        condition_layout = QVBoxLayout(condition_group)
        
        # 介质和压力
        medium_layout = QHBoxLayout()
        medium_layout.addWidget(QLabel("介质类型:"))
        self.medium_combo = QComboBox()
        self.medium_combo.addItems(["蒸汽", "空气", "气体", "液体", "两相流"])
        self.medium_combo.currentTextChanged.connect(self.on_medium_changed)
        medium_layout.addWidget(self.medium_combo)
        
        medium_layout.addWidget(QLabel("分子量 (气体):"))
        self.molecular_weight_input = QDoubleSpinBox()
        self.molecular_weight_input.setRange(1, 200)
        self.molecular_weight_input.setValue(18)
        self.molecular_weight_input.setSuffix(" g/mol")
        medium_layout.addWidget(self.molecular_weight_input)
        
        medium_layout.addWidget(QLabel("绝热指数 (γ):"))
        self.gamma_input = QDoubleSpinBox()
        self.gamma_input.setRange(1.0, 2.0)
        self.gamma_input.setValue(1.3)
        self.gamma_input.setSingleStep(0.1)
        medium_layout.addWidget(self.gamma_input)
        
        condition_layout.addLayout(medium_layout)
        
        # 压力参数
        pressure_layout = QHBoxLayout()
        pressure_layout.addWidget(QLabel("设定压力 (MPa):"))
        self.set_pressure_input = QDoubleSpinBox()
        self.set_pressure_input.setRange(0.1, 50.0)
        self.set_pressure_input.setValue(1.0)
        self.set_pressure_input.setSuffix(" MPa")
        pressure_layout.addWidget(self.set_pressure_input)
        
        pressure_layout.addWidget(QLabel("背压 (MPa):"))
        self.back_pressure_input = QDoubleSpinBox()
        self.back_pressure_input.setRange(0.0, 50.0)
        self.back_pressure_input.setValue(0.1)
        self.back_pressure_input.setSuffix(" MPa")
        pressure_layout.addWidget(self.back_pressure_input)
        
        pressure_layout.addWidget(QLabel("超压百分比 (%):"))
        self.overpressure_input = QDoubleSpinBox()
        self.overpressure_input.setRange(10, 100)
        self.overpressure_input.setValue(10)
        self.overpressure_input.setSuffix(" %")
        pressure_layout.addWidget(self.overpressure_input)
        
        condition_layout.addLayout(pressure_layout)
        
        # 温度参数
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("操作温度 (°C):"))
        self.temperature_input = QDoubleSpinBox()
        self.temperature_input.setRange(-273, 1000)
        self.temperature_input.setValue(100)
        self.temperature_input.setSuffix(" °C")
        temp_layout.addWidget(self.temperature_input)
        
        temp_layout.addWidget(QLabel("泄放温度 (°C):"))
        self.relief_temp_input = QDoubleSpinBox()
        self.relief_temp_input.setRange(-273, 1000)
        self.relief_temp_input.setValue(150)
        self.relief_temp_input.setSuffix(" °C")
        temp_layout.addWidget(self.relief_temp_input)
        
        temp_layout.addWidget(QLabel("压缩因子 Z:"))
        self.compressibility_input = QDoubleSpinBox()
        self.compressibility_input.setRange(0.1, 2.0)
        self.compressibility_input.setValue(1.0)
        self.compressibility_input.setSingleStep(0.1)
        temp_layout.addWidget(self.compressibility_input)
        
        condition_layout.addLayout(temp_layout)
        
        layout.addWidget(condition_group)
        
        # 泄放条件组
        relief_group = QGroupBox("💨 泄放条件")
        relief_layout = QVBoxLayout(relief_group)
        
        # 泄放量计算
        relief_calc_layout = QHBoxLayout()
        relief_calc_layout.addWidget(QLabel("泄放量计算方式:"))
        self.relief_method_combo = QComboBox()
        self.relief_method_combo.addItems(["已知泄放量", "计算泄放量"])
        relief_calc_layout.addWidget(self.relief_method_combo)
        
        relief_calc_layout.addWidget(QLabel("泄放量 (kg/h):"))
        self.relief_rate_input = QDoubleSpinBox()
        self.relief_rate_input.setRange(0, 1000000)
        self.relief_rate_input.setValue(1000)
        self.relief_rate_input.setSuffix(" kg/h")
        relief_calc_layout.addWidget(self.relief_rate_input)
        
        relief_layout.addLayout(relief_calc_layout)
        
        # 火灾工况
        fire_layout = QHBoxLayout()
        self.fire_case_check = QCheckBox("火灾工况")
        fire_layout.addWidget(self.fire_case_check)
        
        fire_layout.addWidget(QLabel("润湿面积 (m²):"))
        self.wetted_area_input = QDoubleSpinBox()
        self.wetted_area_input.setRange(0, 10000)
        self.wetted_area_input.setValue(50)
        self.wetted_area_input.setSuffix(" m²")
        fire_layout.addWidget(self.wetted_area_input)
        
        fire_layout.addWidget(QLabel("环境因子 F:"))
        self.env_factor_input = QDoubleSpinBox()
        self.env_factor_input.setRange(0.1, 2.0)
        self.env_factor_input.setValue(1.0)
        self.env_factor_input.setSingleStep(0.1)
        fire_layout.addWidget(self.env_factor_input)
        
        relief_layout.addLayout(fire_layout)
        
        layout.addWidget(relief_group)
        
        # 安全阀参数组
        valve_group = QGroupBox("🔧 安全阀参数")
        valve_layout = QVBoxLayout(valve_group)
        
        # 阀门类型和材料
        valve_type_layout = QHBoxLayout()
        valve_type_layout.addWidget(QLabel("安全阀类型:"))
        self.valve_type_combo = QComboBox()
        self.valve_type_combo.addItems(["弹簧式", "先导式", "重锤式"])
        valve_type_layout.addWidget(self.valve_type_combo)
        
        valve_type_layout.addWidget(QLabel("材料:"))
        self.valve_material_combo = QComboBox()
        self.valve_material_combo.addItems(["碳钢", "不锈钢", "合金钢", "特殊合金"])
        valve_type_layout.addWidget(self.valve_material_combo)
        
        valve_type_layout.addWidget(QLabel("排放方式:"))
        self.discharge_type_combo = QComboBox()
        self.discharge_type_combo.addItems(["开式", "闭式", "半开式"])
        valve_type_layout.addWidget(self.discharge_type_combo)
        
        valve_layout.addLayout(valve_type_layout)
        
        layout.addWidget(valve_group)
        
        # 按钮组
        button_layout = QHBoxLayout()
        self.calculate_btn = QPushButton("🚀 计算安全阀")
        self.calculate_btn.clicked.connect(self.calculate_safety_valve)
        self.calculate_btn.setStyleSheet("QPushButton { background-color: #c0392b; color: white; font-weight: bold; }")
        button_layout.addWidget(self.calculate_btn)
        
        self.standard_btn = QPushButton("📖 查看标准")
        self.standard_btn.clicked.connect(self.show_standards)
        self.standard_btn.setStyleSheet("QPushButton { background-color: #3498db; color: white; }")
        button_layout.addWidget(self.standard_btn)
        
        self.clear_btn = QPushButton("🗑️ 清空")
        self.clear_btn.clicked.connect(self.clear_inputs)
        self.clear_btn.setStyleSheet("QPushButton { background-color: #95a5a6; color: white; }")
        button_layout.addWidget(self.clear_btn)
        
        layout.addLayout(button_layout)
        
        # 结果显示组
        result_group = QGroupBox("📈 计算结果")
        result_layout = QVBoxLayout(result_group)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(250)
        result_layout.addWidget(self.result_text)
        
        layout.addWidget(result_group)
        
        # 详细参数表
        detail_group = QGroupBox("📋 详细参数")
        detail_layout = QVBoxLayout(detail_group)
        
        self.detail_table = QTableWidget()
        self.detail_table.setColumnCount(3)
        self.detail_table.setHorizontalHeaderLabels(["参数", "数值", "单位"])
        detail_layout.addWidget(self.detail_table)
        
        layout.addWidget(detail_group)
        
        return tab
    
    def on_medium_changed(self, medium):
        """介质类型改变事件"""
        if medium == "蒸汽":
            self.molecular_weight_input.setValue(18)
            self.gamma_input.setValue(1.3)
        elif medium == "空气":
            self.molecular_weight_input.setValue(29)
            self.gamma_input.setValue(1.4)
        elif medium == "气体":
            self.molecular_weight_input.setValue(16)
            self.gamma_input.setValue(1.3)
        elif medium == "液体":
            self.molecular_weight_input.setValue(18)
            self.gamma_input.setValue(1.0)
    
    def create_selection_tab(self):
        """创建选型指南标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 选型指南说明
        selection_text = QTextEdit()
        selection_text.setReadOnly(True)
        selection_text.setHtml(self.get_selection_guide_html())
        layout.addWidget(selection_text)
        
        return tab
    
    def get_selection_guide_html(self):
        """获取选型指南HTML内容"""
        return """
        <h2>📋 安全阀选型指南</h2>
        
        <h3>🛡️ 安全阀类型选择</h3>
        
        <h4>1. 弹簧式安全阀</h4>
        <p><b>特点：</b>结构简单，动作可靠，应用广泛</p>
        <p><b>适用场合：</b></p>
        <ul>
            <li>蒸汽、空气、气体、液体介质</li>
            <li>固定背压或背压变化不大的场合</li>
            <li>温度≤450°C的工况</li>
            <li>一般工业应用</li>
        </ul>
        
        <h4>2. 先导式安全阀</h4>
        <p><b>特点：</b>精度高，密封性好，背压适应性强</p>
        <p><b>适用场合：</b></p>
        <ul>
            <li>高背压或背压波动大的场合</li>
            <li>要求高密封性的工况</li>
            <li>大排量泄放要求</li>
            <li>苛刻工况</li>
        </ul>
        
        <h4>3. 重锤式安全阀</h4>
        <p><b>特点：</b>结构简单，成本低</p>
        <p><b>适用场合：</b></p>
        <ul>
            <li>低压工况</li>
            <li>非危险介质</li>
            <li>温度不高的场合</li>
        </ul>
        
        <h3>📊 泄放量计算原则</h3>
        
        <h4>1. 阻塞流判断</h4>
        <p>对于气体和蒸汽，需要判断是否为阻塞流（临界流）：</p>
        <p>P<sub>b</sub> / P<sub>s</sub> ≤ [2 / (γ + 1)]<sup>γ/(γ-1)</sup></p>
        <p>其中：P<sub>b</sub>为背压，P<sub>s</sub>为泄放压力，γ为绝热指数</p>
        
        <h4>2. 气体和蒸汽泄放量计算</h4>
        <p><b>临界流：</b> W = C × K × A × P × √(M / (Z × T))</p>
        <p><b>亚临界流：</b> W = C × K × A × P × √(M / (Z × T)) × f(P<sub>b</sub>/P)</p>
        
        <h4>3. 液体泄放量计算</h4>
        <p>W = 5.1 × K × A × √(ρ × (P - P<sub>b</sub>))</p>
        
        <h4>4. 火灾工况泄放量</h4>
        <p>Q = 43.2 × F × A<sup>0.82</sup></p>
        <p>其中：F为环境因子，A为润湿面积</p>
        
        <h3>🔧 喉径计算</h3>
        <p>根据泄放量和工况条件计算最小泄放面积：</p>
        <p>A = W / (C × K × P × √(M / (Z × T)))</p>
        <p>然后根据面积确定喉径： d = √(4A / π)</p>
        
        <h3>⚠️ 选型注意事项</h3>
        <ul>
            <li>考虑介质的腐蚀性选择材料</li>
            <li>根据背压情况选择平衡型或非平衡型</li>
            <li>考虑温度对弹簧性能的影响</li>
            <li>确保泄放能力大于等于计算泄放量</li>
            <li>符合相关安全标准和规范</li>
        </ul>
        
        <h3>📖 参考标准</h3>
        <ul>
            <li>ASME Boiler and Pressure Vessel Code Section VIII</li>
            <li>API RP 520 Sizing, Selection, and Installation</li>
            <li>ISO 4126 Safety valves</li>
            <li>GB/T 12241 安全阀一般要求</li>
        </ul>
        """
    
    def calculate_safety_valve(self):
        """计算安全阀"""
        try:
            # 获取输入值
            medium = self.medium_combo.currentText()
            molecular_weight = self.molecular_weight_input.value()
            gamma = self.gamma_input.value()
            set_pressure = self.set_pressure_input.value() * 1e6  # 转换为Pa
            back_pressure = self.back_pressure_input.value() * 1e6  # 转换为Pa
            overpressure = self.overpressure_input.value() / 100
            temperature = self.temperature_input.value() + 273.15  # 转换为K
            relief_temp = self.relief_temp_input.value() + 273.15  # 转换为K
            compressibility = self.compressibility_input.value()
            relief_rate = self.relief_rate_input.value() / 3600  # 转换为kg/s
            is_fire_case = self.fire_case_check.isChecked()
            wetted_area = self.wetted_area_input.value()
            env_factor = self.env_factor_input.value()
            
            # 计算泄放压力
            relief_pressure = set_pressure * (1 + overpressure)
            
            # 计算泄放量（如果是火灾工况）
            if is_fire_case:
                relief_rate = self.calculate_fire_relief(wetted_area, env_factor)
            
            # 计算喉径面积
            if medium in ["蒸汽", "空气", "气体"]:
                area = self.calculate_gas_area(relief_rate, relief_pressure, back_pressure, 
                                             relief_temp, molecular_weight, gamma, compressibility)
            else:  # 液体
                area = self.calculate_liquid_area(relief_rate, relief_pressure, back_pressure)
            
            # 计算喉径
            diameter = math.sqrt(4 * area / math.pi) * 1000  # 转换为mm
            
            # 显示结果
            self.display_results(area, diameter, relief_rate, medium)
            
            # 更新详细参数表
            self.update_detail_table(area, diameter, relief_rate, relief_pressure, back_pressure)
            
        except Exception as e:
            QMessageBox.warning(self, "计算错误", f"计算过程中发生错误: {str(e)}")
    
    def calculate_fire_relief(self, wetted_area, env_factor):
        """计算火灾工况泄放量"""
        # API 521 火灾工况计算公式
        # Q = 43.2 * F * A^0.82 (kW)
        heat_input = 43.2 * env_factor * (wetted_area ** 0.82)  # kW
        
        # 假设介质为烃类，汽化潜热为300 kJ/kg
        latent_heat = 300  # kJ/kg
        relief_rate = (heat_input / latent_heat) * 3600  # kg/h
        
        return relief_rate / 3600  # 返回kg/s
    
    def calculate_gas_area(self, relief_rate, relief_pressure, back_pressure, 
                          temperature, molecular_weight, gamma, compressibility):
        """计算气体泄放面积"""
        # 通用气体常数
        R = 8314  # J/(kmol·K)
        
        # 判断是否为阻塞流
        critical_pressure_ratio = (2 / (gamma + 1)) ** (gamma / (gamma - 1))
        pressure_ratio = back_pressure / relief_pressure
        
        if pressure_ratio <= critical_pressure_ratio:
            # 阻塞流
            C = gamma * math.sqrt((2 / (gamma + 1)) ** ((gamma + 1) / (gamma - 1))) / math.sqrt(R)
            area = relief_rate / (C * relief_pressure * math.sqrt(molecular_weight / (compressibility * temperature)))
        else:
            # 亚临界流
            # 简化计算，实际应使用更复杂的公式
            C = 0.9  # 经验系数
            area = relief_rate / (C * relief_pressure * math.sqrt(molecular_weight / (compressibility * temperature)))
        
        return area
    
    def calculate_liquid_area(self, relief_rate, relief_pressure, back_pressure):
        """计算液体泄放面积"""
        # 假设液体密度为1000 kg/m³
        density = 1000  # kg/m³
        # 流量系数
        K = 0.65
        
        # 压差
        delta_p = relief_pressure - back_pressure
        
        # 计算面积
        area = relief_rate / (5.1 * K * math.sqrt(density * delta_p))
        
        return area
    
    def display_results(self, area, diameter, relief_rate, medium):
        """显示计算结果"""
        # 选择标准喉径
        standard_diameters = [6, 8, 10, 15, 20, 25, 32, 40, 50, 65, 80, 100, 125, 150, 200]
        selected_diameter = min(standard_diameters, key=lambda x: abs(x - diameter))
        
        result_text = f"""
        <h3>🛡️ 安全阀计算结果</h3>
        
        <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr style="background-color: #f8f9fa;">
            <td style="padding: 8px; font-weight: bold;">项目</td>
            <td style="padding: 8px;">计算结果</td>
            <td style="padding: 8px;">说明</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">所需喉径面积</td>
            <td style="padding: 8px; color: #c0392b; font-weight: bold;">{area*1e6:.2f} mm²</td>
            <td style="padding: 8px;">最小泄放面积</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">计算喉径</td>
            <td style="padding: 8px;">{diameter:.1f} mm</td>
            <td style="padding: 8px;">理论计算值</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">推荐喉径</td>
            <td style="padding: 8px; color: #27ae60; font-weight: bold;">{selected_diameter} mm</td>
            <td style="padding: 8px;">标准规格</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">泄放量</td>
            <td style="padding: 8px;">{relief_rate*3600:.1f} kg/h</td>
            <td style="padding: 8px;">设计泄放量</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">介质类型</td>
            <td style="padding: 8px;">{medium}</td>
            <td style="padding: 8px;">泄放介质</td>
        </tr>
        </table>
        
        <h4>🔧 选型建议</h4>
        <ul>
            <li>选择喉径不小于 {selected_diameter} mm 的安全阀</li>
            <li>确保安全阀的额定排量大于计算泄放量</li>
            <li>根据介质特性选择合适的材料和结构</li>
            <li>考虑背压影响，必要时选择平衡式结构</li>
        </ul>
        """
        
        self.result_text.setHtml(result_text)
    
    def update_detail_table(self, area, diameter, relief_rate, relief_pressure, back_pressure):
        """更新详细参数表"""
        detail_data = [
            ["喉径面积", f"{area*1e6:.2f}", "mm²"],
            ["计算喉径", f"{diameter:.1f}", "mm"],
            ["泄放量", f"{relief_rate*3600:.1f}", "kg/h"],
            ["泄放压力", f"{relief_pressure/1e6:.2f}", "MPa"],
            ["背压", f"{back_pressure/1e6:.2f}", "MPa"],
            ["背压比", f"{(back_pressure/relief_pressure)*100:.1f}", "%"],
            ["超压比例", f"{self.overpressure_input.value()}", "%"]
        ]
        
        self.detail_table.setRowCount(len(detail_data))
        for i, row_data in enumerate(detail_data):
            for j, data in enumerate(row_data):
                item = QTableWidgetItem(data)
                item.setTextAlignment(Qt.AlignCenter)
                self.detail_table.setItem(i, j, item)
        
        # 调整列宽
        header = self.detail_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
    
    def show_standards(self):
        """显示标准信息"""
        standards_text = """
        <h3>📖 安全阀相关标准</h3>
        
        <h4>国际标准</h4>
        <ul>
            <li><b>ASME BPVC Section VIII:</b> 压力容器建造规则，包含安全阀要求</li>
            <li><b>API RP 520:</b> 炼油厂泄压装置的选型、选择和安装</li>
            <li><b>API Std 526:</b> 法兰钢制安全阀</li>
            <li><b>ISO 4126:</b> 安全阀的一般要求</li>
        </ul>
        
        <h4>中国标准</h4>
        <ul>
            <li><b>GB/T 12241:</b> 安全阀一般要求</li>
            <li><b>GB/T 12242:</b> 压力释放装置性能试验规范</li>
            <li><b>GB/T 12243:</b> 弹簧直接载荷式安全阀</li>
            <li><b>HG/T 20570.2:</b> 安全阀的设置和选用</li>
        </ul>
        
        <h4>关键参数</h4>
        <ul>
            <li><b>设定压力:</b> 安全阀开始开启的压力</li>
            <li><b>泄放压力:</b> 安全阀达到额定排量时的压力</li>
            <li><b>回座压力:</b> 安全阀关闭时的压力</li>
            <li><b>额定排量:</b> 安全阀的泄放能力</li>
        </ul>
        """
        
        QMessageBox.information(self, "相关标准", standards_text)
    
    def clear_inputs(self):
        """清空输入"""
        self.medium_combo.setCurrentIndex(0)
        self.molecular_weight_input.setValue(18)
        self.gamma_input.setValue(1.3)
        self.set_pressure_input.setValue(1.0)
        self.back_pressure_input.setValue(0.1)
        self.overpressure_input.setValue(10)
        self.temperature_input.setValue(100)
        self.relief_temp_input.setValue(150)
        self.compressibility_input.setValue(1.0)
        self.relief_rate_input.setValue(1000)
        self.fire_case_check.setChecked(False)
        self.wetted_area_input.setValue(50)
        self.env_factor_input.setValue(1.0)
        self.result_text.clear()
        self.detail_table.setRowCount(0)

if __name__ == "__main__":
    # 测试代码
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    widget = SafetyValveCalculator()
    widget.resize(900, 700)
    widget.show()
    
    sys.exit(app.exec())