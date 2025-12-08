from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                              QLabel, QLineEdit, QComboBox, QPushButton, 
                              QTextEdit, QTableWidget, QTableWidgetItem,
                              QHeaderView, QMessageBox, QTabWidget, QDoubleSpinBox,
                              QCheckBox, QRadioButton, QButtonGroup)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QDoubleValidator
import math

class CompressibleFlowPressureDrop(QWidget):
    """可压缩流体压降计算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("🌪️ 可压缩流体压降计算")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 添加计算标签页
        self.calculation_tab = self.create_calculation_tab()
        self.tab_widget.addTab(self.calculation_tab, "📊 压降计算")
        
        # 添加理论说明标签页
        self.theory_tab = self.create_theory_tab()
        self.tab_widget.addTab(self.theory_tab, "📖 理论说明")
        
        main_layout.addWidget(self.tab_widget)
    
    def create_calculation_tab(self):
        """创建计算标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 流体性质组
        fluid_group = QGroupBox("💨 流体性质")
        fluid_layout = QVBoxLayout(fluid_group)
        
        # 流体类型和参数
        fluid_type_layout = QHBoxLayout()
        fluid_type_layout.addWidget(QLabel("流体类型:"))
        self.fluid_combo = QComboBox()
        self.fluid_combo.addItems([
            "空气", "氮气", "氧气", "氢气", "二氧化碳", "天然气", 
            "蒸汽", "甲烷", "乙烷", "丙烷", "自定义气体"
        ])
        self.fluid_combo.currentTextChanged.connect(self.on_fluid_changed)
        fluid_type_layout.addWidget(self.fluid_combo)
        
        fluid_type_layout.addWidget(QLabel("分子量 (g/mol):"))
        self.molecular_weight_input = QDoubleSpinBox()
        self.molecular_weight_input.setRange(1, 200)
        self.molecular_weight_input.setValue(28.97)
        self.molecular_weight_input.setSuffix(" g/mol")
        fluid_type_layout.addWidget(self.molecular_weight_input)
        
        fluid_type_layout.addWidget(QLabel("比热比 (γ):"))
        self.gamma_input = QDoubleSpinBox()
        self.gamma_input.setRange(1.0, 2.0)
        self.gamma_input.setValue(1.4)
        self.gamma_input.setSingleStep(0.01)
        fluid_type_layout.addWidget(self.gamma_input)
        
        fluid_layout.addLayout(fluid_type_layout)
        
        # 气体常数和粘度
        gas_prop_layout = QHBoxLayout()
        gas_prop_layout.addWidget(QLabel("气体常数 R (J/kg·K):"))
        self.gas_constant_input = QDoubleSpinBox()
        self.gas_constant_input.setRange(50, 1000)
        self.gas_constant_input.setValue(287)
        self.gas_constant_input.setSuffix(" J/kg·K")
        gas_prop_layout.addWidget(self.gas_constant_input)
        
        gas_prop_layout.addWidget(QLabel("粘度 (μPa·s):"))
        self.viscosity_input = QDoubleSpinBox()
        self.viscosity_input.setRange(1, 100)
        self.viscosity_input.setValue(18.27)
        self.viscosity_input.setSuffix(" μPa·s")
        gas_prop_layout.addWidget(self.viscosity_input)
        
        fluid_layout.addLayout(gas_prop_layout)
        
        layout.addWidget(fluid_group)
        
        # 管道参数组
        pipe_group = QGroupBox("📏 管道参数")
        pipe_layout = QVBoxLayout(pipe_group)
        
        # 管道尺寸
        pipe_size_layout = QHBoxLayout()
        pipe_size_layout.addWidget(QLabel("管道内径 (mm):"))
        self.diameter_input = QDoubleSpinBox()
        self.diameter_input.setRange(1, 2000)
        self.diameter_input.setValue(100)
        self.diameter_input.setSuffix(" mm")
        pipe_size_layout.addWidget(self.diameter_input)
        
        pipe_size_layout.addWidget(QLabel("管道长度 (m):"))
        self.length_input = QDoubleSpinBox()
        self.length_input.setRange(1, 10000)
        self.length_input.setValue(100)
        self.length_input.setSuffix(" m")
        pipe_size_layout.addWidget(self.length_input)
        
        pipe_size_layout.addWidget(QLabel("绝对粗糙度 (mm):"))
        self.roughness_input = QDoubleSpinBox()
        self.roughness_input.setRange(0.001, 5)
        self.roughness_input.setValue(0.046)
        self.roughness_input.setSuffix(" mm")
        pipe_size_layout.addWidget(self.roughness_input)
        
        pipe_layout.addLayout(pipe_size_layout)
        
        # 管道形状和配件
        pipe_config_layout = QHBoxLayout()
        pipe_config_layout.addWidget(QLabel("管道形状:"))
        self.pipe_shape_combo = QComboBox()
        self.pipe_shape_combo.addItems(["圆形", "矩形"])
        pipe_config_layout.addWidget(self.pipe_shape_combo)
        
        pipe_config_layout.addWidget(QLabel("当量长度系数:"))
        self.equivalent_length_factor = QDoubleSpinBox()
        self.equivalent_length_factor.setRange(1.0, 3.0)
        self.equivalent_length_factor.setValue(1.5)
        self.equivalent_length_factor.setSingleStep(0.1)
        pipe_config_layout.addWidget(self.equivalent_length_factor)
        
        pipe_config_layout.addStretch()
        
        pipe_layout.addLayout(pipe_config_layout)
        
        layout.addWidget(pipe_group)
        
        # 操作条件组
        condition_group = QGroupBox("⚙️ 操作条件")
        condition_layout = QVBoxLayout(condition_group)
        
        # 压力和温度
        pressure_temp_layout = QHBoxLayout()
        pressure_temp_layout.addWidget(QLabel("入口压力 (kPa):"))
        self.inlet_pressure_input = QDoubleSpinBox()
        self.inlet_pressure_input.setRange(1, 10000)
        self.inlet_pressure_input.setValue(500)
        self.inlet_pressure_input.setSuffix(" kPa")
        pressure_temp_layout.addWidget(self.inlet_pressure_input)
        
        pressure_temp_layout.addWidget(QLabel("出口压力 (kPa):"))
        self.outlet_pressure_input = QDoubleSpinBox()
        self.outlet_pressure_input.setRange(1, 10000)
        self.outlet_pressure_input.setValue(400)
        self.outlet_pressure_input.setSuffix(" kPa")
        pressure_temp_layout.addWidget(self.outlet_pressure_input)
        
        pressure_temp_layout.addWidget(QLabel("温度 (°C):"))
        self.temperature_input = QDoubleSpinBox()
        self.temperature_input.setRange(-200, 1000)
        self.temperature_input.setValue(20)
        self.temperature_input.setSuffix(" °C")
        pressure_temp_layout.addWidget(self.temperature_input)
        
        condition_layout.addLayout(pressure_temp_layout)
        
        # 流量参数
        flow_layout = QHBoxLayout()
        flow_layout.addWidget(QLabel("质量流量 (kg/h):"))
        self.mass_flow_input = QDoubleSpinBox()
        self.mass_flow_input.setRange(0.1, 100000)
        self.mass_flow_input.setValue(1000)
        self.mass_flow_input.setSuffix(" kg/h")
        flow_layout.addWidget(self.mass_flow_input)
        
        flow_layout.addWidget(QLabel("体积流量 (Nm³/h):"))
        self.volume_flow_input = QDoubleSpinBox()
        self.volume_flow_input.setRange(0.1, 100000)
        self.volume_flow_input.setValue(800)
        self.volume_flow_input.setSuffix(" Nm³/h")
        flow_layout.addWidget(self.volume_flow_input)
        
        condition_layout.addLayout(flow_layout)
        
        layout.addWidget(condition_group)
        
        # 计算方法选择
        method_group = QGroupBox("🔧 计算方法")
        method_layout = QHBoxLayout(method_group)
        
        self.method_group = QButtonGroup(self)
        
        self.darcy_radio = QRadioButton("Darcy-Weisbach方程")
        self.darcy_radio.setChecked(True)
        self.method_group.addButton(self.darcy_radio)
        method_layout.addWidget(self.darcy_radio)
        
        self.weymouth_radio = QRadioButton("Weymouth公式")
        self.method_group.addButton(self.weymouth_radio)
        method_layout.addWidget(self.weymouth_radio)
        
        self.panhandle_radio = QRadioButton("Panhandle公式")
        self.method_group.addButton(self.panhandle_radio)
        method_layout.addWidget(self.panhandle_radio)
        
        self.aga_radio = QRadioButton("AGA公式")
        self.method_group.addButton(self.aga_radio)
        method_layout.addWidget(self.aga_radio)
        
        method_layout.addStretch()
        layout.addWidget(method_group)
        
        # 按钮组
        button_layout = QHBoxLayout()
        self.calculate_btn = QPushButton("🚀 计算压降")
        self.calculate_btn.clicked.connect(self.calculate_pressure_drop)
        self.calculate_btn.setStyleSheet("QPushButton { background-color: #9b59b6; color: white; font-weight: bold; }")
        button_layout.addWidget(self.calculate_btn)
        
        self.auto_calc_btn = QPushButton("🔧 自动计算流量")
        self.auto_calc_btn.clicked.connect(self.auto_calculate_flow)
        self.auto_calc_btn.setStyleSheet("QPushButton { background-color: #3498db; color: white; }")
        button_layout.addWidget(self.auto_calc_btn)
        
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
    
    def on_fluid_changed(self, fluid_name):
        """流体类型改变事件"""
        fluid_properties = {
            "空气": {"mw": 28.97, "gamma": 1.4, "R": 287, "viscosity": 18.27},
            "氮气": {"mw": 28.01, "gamma": 1.4, "R": 297, "viscosity": 17.9},
            "氧气": {"mw": 32.00, "gamma": 1.4, "R": 260, "viscosity": 20.8},
            "氢气": {"mw": 2.02, "gamma": 1.4, "R": 4124, "viscosity": 8.9},
            "二氧化碳": {"mw": 44.01, "gamma": 1.3, "R": 189, "viscosity": 14.8},
            "天然气": {"mw": 18.0, "gamma": 1.3, "R": 462, "viscosity": 11.2},
            "蒸汽": {"mw": 18.02, "gamma": 1.33, "R": 461, "viscosity": 12.3},
            "甲烷": {"mw": 16.04, "gamma": 1.32, "R": 518, "viscosity": 11.2},
            "乙烷": {"mw": 30.07, "gamma": 1.2, "R": 277, "viscosity": 9.5},
            "丙烷": {"mw": 44.10, "gamma": 1.13, "R": 189, "viscosity": 8.1}
        }
        
        if fluid_name in fluid_properties:
            props = fluid_properties[fluid_name]
            self.molecular_weight_input.setValue(props["mw"])
            self.gamma_input.setValue(props["gamma"])
            self.gas_constant_input.setValue(props["R"])
            self.viscosity_input.setValue(props["viscosity"])
    
    def create_theory_tab(self):
        """创建理论说明标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 理论说明文本
        theory_text = QTextEdit()
        theory_text.setReadOnly(True)
        theory_text.setHtml(self.get_theory_html())
        layout.addWidget(theory_text)
        
        return tab
    
    def get_theory_html(self):
        """获取理论说明HTML内容"""
        return """
        <h2>📚 可压缩流体压降计算理论</h2>
        
        <h3>🔍 可压缩流体特点</h3>
        <p>可压缩流体（气体、蒸汽等）在流动过程中密度会随压力和温度变化，这与不可压缩流体有本质区别。计算可压缩流体压降时需要考虑：</p>
        <ul>
            <li>密度变化对流速的影响</li>
            <li>压力变化对气体性质的影响</li>
            <li>可压缩性导致的流动特性变化</li>
            <li>音速限制（阻塞流）</li>
        </ul>
        
        <h3>📊 常用计算方法</h3>
        
        <h4>1. Darcy-Weisbach方程（通用方法）</h4>
        <p>ΔP = f × (L/D) × (ρ × v²/2)</p>
        <p>其中考虑可压缩性的修正：</p>
        <ul>
            <li>使用平均密度</li>
            <li>考虑密度沿管道的变化</li>
            <li>适用于各种流态</li>
        </ul>
        
        <h4>2. Weymouth公式（天然气管道）</h4>
        <p>Q = C × (P₁² - P₂²)<sup>0.5</sup> × D<sup>2.667</sup> / (L × γ)<sup>0.5</sup></p>
        <p>适用于高压天然气管道，经验公式。</p>
        
        <h4>3. Panhandle公式</h4>
        <p>Q = C × E × (P₁² - P₂²)<sup>0.5394</sup> × D<sup>2.6182</sup> / (L × γ)<sup>0.4606</sup></p>
        <p>改进的天然气流量公式，考虑效率因子。</p>
        
        <h4>4. AGA公式（美国燃气协会）</h4>
        <p>基于完全湍流和部分湍流的详细计算，考虑：</p>
        <ul>
            <li>雷诺数影响</li>
            <li>管道粗糙度</li>
            <li>气体压缩因子</li>
        </ul>
        
        <h3>📐 关键参数说明</h3>
        
        <h4>比热比 (γ)</h4>
        <p>γ = Cₚ/Cᵥ，定压比热与定容比热的比值：</p>
        <ul>
            <li>单原子气体：~1.67</li>
            <li>双原子气体：~1.40</li>
            <li>多原子气体：~1.33-1.10</li>
        </ul>
        
        <h4>雷诺数 (Re)</h4>
        <p>Re = (ρ × v × D) / μ</p>
        <p>判断流态：</p>
        <ul>
            <li>层流：Re < 2000</li>
            <li>过渡流：2000 < Re < 4000</li>
            <li>湍流：Re > 4000</li>
        </ul>
        
        <h4>马赫数 (Ma)</h4>
        <p>Ma = v / a，其中 a = √(γ × R × T)</p>
        <p>判断可压缩性影响：</p>
        <ul>
            <li>Ma < 0.3：不可压缩流动</li>
            <li>0.3 < Ma < 0.8：可压缩流动</li>
            <li>Ma > 0.8：高速可压缩流动</li>
            <li>Ma = 1：音速流动（阻塞）</li>
        </ul>
        
        <h3>⚠️ 注意事项</h3>
        <ul>
            <li>可压缩流体计算通常需要迭代求解</li>
            <li>高压差时需要考虑真实气体效应</li>
            <li>接近音速时流动可能发生阻塞</li>
            <li>温度变化显著时需要考虑能量方程</li>
        </ul>
        
        <h3>📖 参考标准</h3>
        <ul>
            <li>ASME MFC-3M 气体流量测量</li>
            <li>ISO 5167 流量测量</li>
            <li>API MPMS 石油测量标准</li>
            <li>AGA Report No. 3 气体流量计算</li>
        </ul>
        """
    
    def calculate_pressure_drop(self):
        """计算压降"""
        try:
            # 获取输入值
            method = self.get_selected_method()
            diameter = self.diameter_input.value() / 1000  # 转换为米
            length = self.length_input.value()
            roughness = self.roughness_input.value() / 1000  # 转换为米
            inlet_pressure = self.inlet_pressure_input.value() * 1000  # 转换为Pa
            outlet_pressure = self.outlet_pressure_input.value() * 1000  # 转换为Pa
            temperature = self.temperature_input.value() + 273.15  # 转换为K
            mass_flow = self.mass_flow_input.value() / 3600  # 转换为kg/s
            molecular_weight = self.molecular_weight_input.value()
            gamma = self.gamma_input.value()
            gas_constant = self.gas_constant_input.value()
            viscosity = self.viscosity_input.value() * 1e-6  # 转换为Pa·s
            
            # 计算气体性质
            density_inlet = self.calculate_density(inlet_pressure, temperature, gas_constant)
            density_outlet = self.calculate_density(outlet_pressure, temperature, gas_constant)
            avg_density = (density_inlet + density_outlet) / 2
            
            # 计算流速和其他参数
            area = math.pi * diameter**2 / 4
            velocity = mass_flow / (avg_density * area)
            reynolds = self.calculate_reynolds(diameter, velocity, avg_density, viscosity)
            friction_factor = self.calculate_friction_factor(reynolds, roughness, diameter)
            
            # 根据选择的方法计算
            if method == "darcy":
                pressure_drop, results = self.calculate_darcy_method(
                    length, diameter, friction_factor, avg_density, velocity,
                    inlet_pressure, outlet_pressure, mass_flow, temperature, gas_constant
                )
            elif method == "weymouth":
                pressure_drop, results = self.calculate_weymouth_method(
                    length, diameter, inlet_pressure, outlet_pressure, 
                    mass_flow, temperature, gas_constant, gamma
                )
            elif method == "panhandle":
                pressure_drop, results = self.calculate_panhandle_method(
                    length, diameter, inlet_pressure, outlet_pressure,
                    mass_flow, temperature, gas_constant, gamma
                )
            else:  # AGA
                pressure_drop, results = self.calculate_aga_method(
                    length, diameter, roughness, inlet_pressure, outlet_pressure,
                    mass_flow, temperature, gas_constant, viscosity
                )
            
            # 计算马赫数
            speed_of_sound = math.sqrt(gamma * gas_constant * temperature)
            mach_number = velocity / speed_of_sound
            
            # 显示结果
            self.display_results(pressure_drop, results, mach_number, reynolds, method)
            
            # 更新详细参数表
            self.update_detail_table(results, mach_number, reynolds, friction_factor)
            
        except Exception as e:
            QMessageBox.warning(self, "计算错误", f"计算过程中发生错误: {str(e)}")
    
    def get_selected_method(self):
        """获取选择的方法"""
        if self.darcy_radio.isChecked():
            return "darcy"
        elif self.weymouth_radio.isChecked():
            return "weymouth"
        elif self.panhandle_radio.isChecked():
            return "panhandle"
        else:
            return "aga"
    
    def calculate_density(self, pressure, temperature, gas_constant):
        """计算气体密度"""
        return pressure / (gas_constant * temperature)
    
    def calculate_reynolds(self, diameter, velocity, density, viscosity):
        """计算雷诺数"""
        return (density * velocity * diameter) / viscosity
    
    def calculate_friction_factor(self, reynolds, roughness, diameter):
        """计算摩擦系数 (Colebrook-White方程)"""
        if reynolds < 2000:
            # 层流
            return 64 / reynolds
        else:
            # 湍流 - Colebrook-White方程迭代求解
            rel_roughness = roughness / diameter
            f = 0.02  # 初始猜测
            for i in range(20):  # 最多迭代20次
                f_new = 1 / (-2 * math.log10(rel_roughness/3.7 + 2.51/(reynolds * math.sqrt(f))))**2
                if abs(f_new - f) < 1e-6:
                    return f_new
                f = f_new
            return f
    
    def calculate_darcy_method(self, length, diameter, friction_factor, density, velocity,
                             inlet_pressure, outlet_pressure, mass_flow, temperature, gas_constant):
        """Darcy-Weisbach方法"""
        # 考虑可压缩性的Darcy方程
        equivalent_length = length * self.equivalent_length_factor.value()
        pressure_drop_pa = friction_factor * (equivalent_length / diameter) * (density * velocity**2) / 2
        pressure_drop_kpa = pressure_drop_pa / 1000
        
        results = {
            "摩擦系数": friction_factor,
            "当量长度": equivalent_length,
            "压力损失": pressure_drop_kpa,
            "计算方法": "Darcy-Weisbach"
        }
        
        return pressure_drop_kpa, results
    
    def calculate_weymouth_method(self, length, diameter, inlet_pressure, outlet_pressure,
                                mass_flow, temperature, gas_constant, gamma):
        """Weymouth公式"""
        # Weymouth公式 (英制单位转换)
        diameter_inch = diameter * 39.37
        length_mile = length / 1609.34
        p1_psia = inlet_pressure / 6894.76
        p2_psia = outlet_pressure / 6894.76
        
        # Weymouth常数
        C = 433.5  # 英制单位常数
        
        # 计算流量 (SCFD)
        Q_scfd = C * (p1_psia**2 - p2_psia**2)**0.5 * diameter_inch**2.667 / (length_mile * gamma)**0.5
        
        # 转换为SI单位
        Q_sm3h = Q_scfd * 0.0283168  # SCFD to m³/h
        
        # 计算压降
        pressure_drop_kpa = (inlet_pressure - outlet_pressure) / 1000
        
        results = {
            "计算流量": Q_sm3h,
            "压力平方差": (p1_psia**2 - p2_psia**2),
            "压力损失": pressure_drop_kpa,
            "计算方法": "Weymouth公式"
        }
        
        return pressure_drop_kpa, results
    
    def calculate_panhandle_method(self, length, diameter, inlet_pressure, outlet_pressure,
                                 mass_flow, temperature, gas_constant, gamma):
        """Panhandle公式"""
        # Panhandle A公式
        diameter_inch = diameter * 39.37
        length_mile = length / 1609.34
        p1_psia = inlet_pressure / 6894.76
        p2_psia = outlet_pressure / 6894.76
        
        # Panhandle常数和效率因子
        C = 435.87  # 英制单位常数
        E = 0.92    # 效率因子
        
        # 计算流量 (SCFD)
        Q_scfd = C * E * (p1_psia**2 - p2_psia**2)**0.5394 * diameter_inch**2.6182 / (length_mile * gamma)**0.4606
        
        # 转换为SI单位
        Q_sm3h = Q_scfd * 0.0283168  # SCFD to m³/h
        
        # 计算压降
        pressure_drop_kpa = (inlet_pressure - outlet_pressure) / 1000
        
        results = {
            "计算流量": Q_sm3h,
            "效率因子": E,
            "压力损失": pressure_drop_kpa,
            "计算方法": "Panhandle公式"
        }
        
        return pressure_drop_kpa, results
    
    def calculate_aga_method(self, length, diameter, roughness, inlet_pressure, outlet_pressure,
                           mass_flow, temperature, gas_constant, viscosity):
        """AGA方法"""
        # 简化版AGA计算
        density = self.calculate_density(inlet_pressure, temperature, gas_constant)
        velocity = mass_flow / (density * math.pi * diameter**2 / 4)
        reynolds = self.calculate_reynolds(diameter, velocity, density, viscosity)
        friction_factor = self.calculate_friction_factor(reynolds, roughness, diameter)
        
        # AGA完全湍流摩擦系数
        rel_roughness = roughness / diameter
        f_turbulent = 1 / (2 * math.log10(3.7 / rel_roughness))**2
        
        # 使用Darcy方程计算压降
        pressure_drop_pa = f_turbulent * (length / diameter) * (density * velocity**2) / 2
        pressure_drop_kpa = pressure_drop_pa / 1000
        
        results = {
            "雷诺数": reynolds,
            "摩擦系数": f_turbulent,
            "相对粗糙度": rel_roughness,
            "压力损失": pressure_drop_kpa,
            "计算方法": "AGA公式"
        }
        
        return pressure_drop_kpa, results
    
    def auto_calculate_flow(self):
        """自动计算流量"""
        try:
            # 基于压降自动估算流量
            diameter = self.diameter_input.value() / 1000
            length = self.length_input.value()
            inlet_pressure = self.inlet_pressure_input.value()
            outlet_pressure = self.outlet_pressure_input.value()
            
            # 简化流量估算
            pressure_ratio = outlet_pressure / inlet_pressure
            if pressure_ratio > 0.9:
                # 小压降情况
                estimated_flow = 1000  # kg/h
            elif pressure_ratio > 0.5:
                # 中等压降
                estimated_flow = 2000  # kg/h
            else:
                # 大压降
                estimated_flow = 5000  # kg/h
            
            # 考虑管道尺寸调整
            flow_factor = (diameter * 1000 / 100) ** 2  # 基于100mm管径的平方关系
            estimated_flow *= flow_factor
            
            self.mass_flow_input.setValue(estimated_flow)
            
            QMessageBox.information(self, "流量估算", f"基于当前参数估算的质量流量: {estimated_flow:.0f} kg/h")
            
        except Exception as e:
            QMessageBox.warning(self, "计算错误", f"流量估算失败: {str(e)}")
    
    def display_results(self, pressure_drop, results, mach_number, reynolds, method):
        """显示计算结果"""
        flow_regime = "层流" if reynolds < 2000 else "过渡流" if reynolds < 4000 else "湍流"
        compressibility = "不可压缩" if mach_number < 0.3 else "可压缩" if mach_number < 0.8 else "高速可压缩"
        
        result_text = f"""
        <h3>🌪️ 可压缩流体压降计算结果</h3>
        
        <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr style="background-color: #f8f9fa;">
            <td style="padding: 8px; font-weight: bold;">项目</td>
            <td style="padding: 8px;">计算结果</td>
            <td style="padding: 8px;">说明</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">压降</td>
            <td style="padding: 8px; color: #9b59b6; font-weight: bold;">{pressure_drop:.2f} kPa</td>
            <td style="padding: 8px;">压力损失</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">计算方法</td>
            <td style="padding: 8px;">{results.get('计算方法', '未知')}</td>
            <td style="padding: 8px;">采用的计算公式</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">雷诺数</td>
            <td style="padding: 8px;">{reynolds:.0f}</td>
            <td style="padding: 8px;">{flow_regime}</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">马赫数</td>
            <td style="padding: 8px; {'color: red;' if mach_number > 0.8 else 'color: green;'}">
                {mach_number:.3f}
            </td>
            <td style="padding: 8px;">{compressibility}</td>
        </tr>
        """
        
        # 添加方法特定结果
        for key, value in results.items():
            if key not in ["计算方法", "压力损失"]:
                result_text += f"""
        <tr>
            <td style="padding: 8px; font-weight: bold;">{key}</td>
            <td style="padding: 8px;">{value:.4f}</td>
            <td style="padding: 8px;">{self.get_parameter_description(key)}</td>
        </tr>
                """
        
        result_text += "</table>"
        
        # 添加警告信息
        if mach_number > 0.8:
            result_text += """
            <h4 style="color: red;">⚠️ 警告：接近音速流动</h4>
            <p>马赫数大于0.8，流动可能接近音速，需要考虑阻塞流效应。</p>
            """
        
        if reynolds > 100000:
            result_text += """
            <h4 style="color: orange;">💡 提示：完全湍流</h4>
            <p>雷诺数较高，流动处于完全湍流状态，摩擦系数主要取决于管道粗糙度。</p>
            """
        
        self.result_text.setHtml(result_text)
    
    def get_parameter_description(self, parameter):
        """获取参数说明"""
        descriptions = {
            "摩擦系数": "管道摩擦损失系数",
            "当量长度": "考虑局部阻力的等效长度",
            "计算流量": "基于公式计算的体积流量",
            "压力平方差": "入口和出口压力的平方差",
            "效率因子": "管道效率修正系数",
            "雷诺数": "流动状态判断参数",
            "相对粗糙度": "管道粗糙度与直径比值"
        }
        return descriptions.get(parameter, "")
    
    def update_detail_table(self, results, mach_number, reynolds, friction_factor):
        """更新详细参数表"""
        detail_data = [
            ["马赫数", f"{mach_number:.4f}", "-"],
            ["雷诺数", f"{reynolds:.0f}", "-"],
            ["摩擦系数", f"{friction_factor:.4f}", "-"],
            ["流动状态", "层流" if reynolds < 2000 else "过渡流" if reynolds < 4000 else "湍流", "-"],
            ["可压缩性", "不可压缩" if mach_number < 0.3 else "可压缩" if mach_number < 0.8 else "高速可压缩", "-"]
        ]
        
        # 添加方法特定参数
        for key, value in results.items():
            if key not in ["计算方法"]:
                detail_data.append([key, f"{value:.4f}", self.get_parameter_unit(key)])
        
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
    
    def get_parameter_unit(self, parameter):
        """获取参数单位"""
        units = {
            "摩擦系数": "-",
            "当量长度": "m",
            "计算流量": "Nm³/h",
            "压力平方差": "kPa²",
            "效率因子": "-",
            "压力损失": "kPa",
            "相对粗糙度": "-"
        }
        return units.get(parameter, "")
    
    def clear_inputs(self):
        """清空输入"""
        self.fluid_combo.setCurrentIndex(0)
        self.molecular_weight_input.setValue(28.97)
        self.gamma_input.setValue(1.4)
        self.gas_constant_input.setValue(287)
        self.viscosity_input.setValue(18.27)
        self.diameter_input.setValue(100)
        self.length_input.setValue(100)
        self.roughness_input.setValue(0.046)
        self.pipe_shape_combo.setCurrentIndex(0)
        self.equivalent_length_factor.setValue(1.5)
        self.inlet_pressure_input.setValue(500)
        self.outlet_pressure_input.setValue(400)
        self.temperature_input.setValue(20)
        self.mass_flow_input.setValue(1000)
        self.volume_flow_input.setValue(800)
        self.darcy_radio.setChecked(True)
        self.result_text.clear()
        self.detail_table.setRowCount(0)

if __name__ == "__main__":
    # 测试代码
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    widget = CompressibleFlowPressureDrop()
    widget.resize(900, 700)
    widget.show()
    
    sys.exit(app.exec())