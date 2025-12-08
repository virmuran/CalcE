# [file name]: calculators/insulation_thickness_calculator.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                              QLabel, QLineEdit, QComboBox, QPushButton, 
                              QTextEdit, QTableWidget, QTableWidgetItem,
                              QHeaderView, QMessageBox, QTabWidget, QDoubleSpinBox,
                              QCheckBox, QRadioButton, QButtonGroup, QSlider)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QDoubleValidator
import math

class InsulationThicknessCalculator(QWidget):
    """保温厚度计算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("🧊 保温厚度计算")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 添加计算标签页
        self.calculation_tab = self.create_calculation_tab()
        self.tab_widget.addTab(self.calculation_tab, "📊 厚度计算")
        
        # 添加材料库标签页
        self.material_tab = self.create_material_tab()
        self.tab_widget.addTab(self.material_tab, "📚 保温材料库")
        
        main_layout.addWidget(self.tab_widget)
    
    def create_calculation_tab(self):
        """创建计算标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 设备参数组
        equipment_group = QGroupBox("🏭 设备参数")
        equipment_layout = QVBoxLayout(equipment_group)
        
        # 设备类型和尺寸
        equipment_type_layout = QHBoxLayout()
        equipment_type_layout.addWidget(QLabel("设备类型:"))
        self.equipment_type_combo = QComboBox()
        self.equipment_type_combo.addItems([
            "管道", "储罐", "反应器", "换热器", "阀门", "法兰"
        ])
        equipment_type_layout.addWidget(self.equipment_type_combo)
        
        equipment_type_layout.addWidget(QLabel("外径/尺寸 (mm):"))
        self.diameter_input = QDoubleSpinBox()
        self.diameter_input.setRange(1, 5000)
        self.diameter_input.setValue(219)
        self.diameter_input.setSuffix(" mm")
        equipment_type_layout.addWidget(self.diameter_input)
        
        equipment_type_layout.addWidget(QLabel("长度/高度 (m):"))
        self.length_input = QDoubleSpinBox()
        self.length_input.setRange(0.1, 1000)
        self.length_input.setValue(100)
        self.length_input.setSuffix(" m")
        equipment_type_layout.addWidget(self.length_input)
        
        equipment_layout.addLayout(equipment_type_layout)
        
        layout.addWidget(equipment_group)
        
        # 温度参数组
        temperature_group = QGroupBox("🌡️ 温度参数")
        temperature_layout = QVBoxLayout(temperature_group)
        
        # 操作温度和环境温度
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("介质温度 (°C):"))
        self.media_temp_input = QDoubleSpinBox()
        self.media_temp_input.setRange(-200, 1000)
        self.media_temp_input.setValue(150)
        self.media_temp_input.setSuffix(" °C")
        temp_layout.addWidget(self.media_temp_input)
        
        temp_layout.addWidget(QLabel("环境温度 (°C):"))
        self.ambient_temp_input = QDoubleSpinBox()
        self.ambient_temp_input.setRange(-50, 60)
        self.ambient_temp_input.setValue(20)
        self.ambient_temp_input.setSuffix(" °C")
        temp_layout.addWidget(self.ambient_temp_input)
        
        temp_layout.addWidget(QLabel("允许表面温度 (°C):"))
        self.surface_temp_input = QDoubleSpinBox()
        self.surface_temp_input.setRange(0, 100)
        self.surface_temp_input.setValue(50)
        self.surface_temp_input.setSuffix(" °C")
        temp_layout.addWidget(self.surface_temp_input)
        
        temperature_layout.addLayout(temp_layout)
        
        layout.addWidget(temperature_group)
        
        # 保温材料组
        insulation_group = QGroupBox("🧱 保温材料")
        insulation_layout = QVBoxLayout(insulation_group)
        
        # 材料选择
        material_layout = QHBoxLayout()
        material_layout.addWidget(QLabel("保温材料:"))
        self.insulation_combo = QComboBox()
        self.insulation_combo.addItems([
            "岩棉", "玻璃棉", "硅酸铝纤维", "聚氨酯泡沫", 
            "聚苯乙烯泡沫", "橡塑海绵", "气凝胶", "复合硅酸盐",
            "微孔硅酸钙", "珍珠岩", "自定义材料"
        ])
        self.insulation_combo.currentTextChanged.connect(self.on_insulation_changed)
        material_layout.addWidget(self.insulation_combo)
        
        material_layout.addWidget(QLabel("导热系数 (W/m·K):"))
        self.conductivity_input = QDoubleSpinBox()
        self.conductivity_input.setRange(0.01, 1.0)
        self.conductivity_input.setValue(0.04)
        self.conductivity_input.setSingleStep(0.001)
        self.conductivity_input.setSuffix(" W/m·K")
        material_layout.addWidget(self.conductivity_input)
        
        material_layout.addWidget(QLabel("使用温度范围 (°C):"))
        self.temp_range_label = QLabel("-50 ~ 650")
        material_layout.addWidget(self.temp_range_label)
        
        insulation_layout.addLayout(material_layout)
        
        # 材料密度和厚度
        material_prop_layout = QHBoxLayout()
        material_prop_layout.addWidget(QLabel("材料密度 (kg/m³):"))
        self.density_input = QDoubleSpinBox()
        self.density_input.setRange(10, 500)
        self.density_input.setValue(120)
        self.density_input.setSuffix(" kg/m³")
        material_prop_layout.addWidget(self.density_input)
        
        material_prop_layout.addWidget(QLabel("推荐厚度 (mm):"))
        self.recommended_thickness_label = QLabel("50")
        material_prop_layout.addWidget(self.recommended_thickness_label)
        
        material_prop_layout.addWidget(QLabel("当前厚度 (mm):"))
        self.thickness_input = QDoubleSpinBox()
        self.thickness_input.setRange(1, 500)
        self.thickness_input.setValue(50)
        self.thickness_input.setSuffix(" mm")
        material_prop_layout.addWidget(self.thickness_input)
        
        insulation_layout.addLayout(material_prop_layout)
        
        layout.addWidget(insulation_group)
        
        # 计算条件组
        condition_group = QGroupBox("⚙️ 计算条件")
        condition_layout = QVBoxLayout(condition_group)
        
        # 计算标准选择
        standard_layout = QHBoxLayout()
        standard_layout.addWidget(QLabel("计算标准:"))
        self.standard_combo = QComboBox()
        self.standard_combo.addItems([
            "GB/T 8175-2008", "ASHRAE", "ASTM C680", "ISO 12241", 
            "经济厚度法", "表面温度法", "热损失法"
        ])
        standard_layout.addWidget(self.standard_combo)
        
        standard_layout.addWidget(QLabel("允许热损失 (W/m²):"))
        self.heat_loss_input = QDoubleSpinBox()
        self.heat_loss_input.setRange(10, 500)
        self.heat_loss_input.setValue(150)
        self.heat_loss_input.setSuffix(" W/m²")
        standard_layout.addWidget(self.heat_loss_input)
        
        condition_layout.addLayout(standard_layout)
        
        # 环境条件
        environment_layout = QHBoxLayout()
        environment_layout.addWidget(QLabel("环境风速 (m/s):"))
        self.wind_speed_input = QDoubleSpinBox()
        self.wind_speed_input.setRange(0, 20)
        self.wind_speed_input.setValue(2.5)
        self.wind_speed_input.setSuffix(" m/s")
        environment_layout.addWidget(self.wind_speed_input)
        
        environment_layout.addWidget(QLabel("相对湿度 (%):"))
        self.humidity_input = QDoubleSpinBox()
        self.humidity_input.setRange(0, 100)
        self.humidity_input.setValue(60)
        self.humidity_input.setSuffix(" %")
        environment_layout.addWidget(self.humidity_input)
        
        self.weather_proof_check = QCheckBox("室外安装")
        self.weather_proof_check.setChecked(True)
        environment_layout.addWidget(self.weather_proof_check)
        
        condition_layout.addLayout(environment_layout)
        
        layout.addWidget(condition_group)
        
        # 按钮组
        button_layout = QHBoxLayout()
        self.calculate_btn = QPushButton("🚀 计算保温厚度")
        self.calculate_btn.clicked.connect(self.calculate_insulation)
        self.calculate_btn.setStyleSheet("QPushButton { background-color: #16a085; color: white; font-weight: bold; }")
        button_layout.addWidget(self.calculate_btn)
        
        self.auto_thickness_btn = QPushButton("🔧 自动计算厚度")
        self.auto_thickness_btn.clicked.connect(self.auto_calculate_thickness)
        self.auto_thickness_btn.setStyleSheet("QPushButton { background-color: #3498db; color: white; }")
        button_layout.addWidget(self.auto_thickness_btn)
        
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
        self.result_text.setMaximumHeight(200)
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
    
    def on_insulation_changed(self, material_name):
        """保温材料改变事件"""
        material_properties = {
            "岩棉": {"conductivity": 0.04, "density": 120, "temp_range": "-50 ~ 650", "recommended": 50},
            "玻璃棉": {"conductivity": 0.042, "density": 64, "temp_range": "-50 ~ 450", "recommended": 50},
            "硅酸铝纤维": {"conductivity": 0.12, "density": 200, "temp_range": "0 ~ 1000", "recommended": 80},
            "聚氨酯泡沫": {"conductivity": 0.025, "density": 40, "temp_range": "-200 ~ 120", "recommended": 40},
            "聚苯乙烯泡沫": {"conductivity": 0.038, "density": 30, "temp_range": "-50 ~ 75", "recommended": 50},
            "橡塑海绵": {"conductivity": 0.038, "density": 80, "temp_range": "-40 ~ 105", "recommended": 25},
            "气凝胶": {"conductivity": 0.018, "density": 180, "temp_range": "-200 ~ 650", "recommended": 20},
            "复合硅酸盐": {"conductivity": 0.048, "density": 180, "temp_range": "-40 ~ 800", "recommended": 60},
            "微孔硅酸钙": {"conductivity": 0.055, "density": 220, "temp_range": "0 ~ 1000", "recommended": 70},
            "珍珠岩": {"conductivity": 0.065, "density": 80, "temp_range": "-50 ~ 800", "recommended": 80}
        }
        
        if material_name in material_properties:
            props = material_properties[material_name]
            self.conductivity_input.setValue(props["conductivity"])
            self.density_input.setValue(props["density"])
            self.temp_range_label.setText(props["temp_range"])
            self.recommended_thickness_label.setText(str(props["recommended"]))
            self.thickness_input.setValue(props["recommended"])
    
    def create_material_tab(self):
        """创建材料库标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 材料库说明
        info_label = QLabel("常用保温材料参数参考")
        info_label.setFont(QFont("Arial", 12, QFont.Bold))
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # 材料参数表
        material_table = QTableWidget()
        material_table.setColumnCount(6)
        material_table.setHorizontalHeaderLabels(["材料", "导热系数(W/m·K)", "密度(kg/m³)", "使用温度(°C)", "推荐厚度(mm)", "特点"])
        
        material_data = [
            ["岩棉", "0.035-0.044", "80-200", "-50~650", "40-100", "防火性好，耐高温"],
            ["玻璃棉", "0.032-0.044", "24-96", "-50~450", "40-100", "轻质，施工方便"],
            ["硅酸铝纤维", "0.12-0.16", "180-220", "0~1000", "80-150", "耐高温，强度好"],
            ["聚氨酯泡沫", "0.018-0.028", "30-60", "-200~120", "30-60", "保温性好，闭孔"],
            ["聚苯乙烯泡沫", "0.033-0.044", "20-40", "-50~75", "50-100", "成本低，易吸水"],
            ["橡塑海绵", "0.034-0.040", "60-100", "-40~105", "15-30", "柔韧性好，防水"],
            ["气凝胶", "0.015-0.020", "150-200", "-200~650", "10-25", "超强保温，昂贵"],
            ["复合硅酸盐", "0.035-0.055", "180-220", "-40~800", "50-100", "综合性能好"],
            ["微孔硅酸钙", "0.048-0.062", "200-250", "0~1000", "60-120", "耐高温，强度高"],
            ["珍珠岩", "0.045-0.075", "60-120", "-50~800", "60-120", "天然材料，环保"]
        ]
        
        material_table.setRowCount(len(material_data))
        for i, row_data in enumerate(material_data):
            for j, data in enumerate(row_data):
                item = QTableWidgetItem(data)
                item.setTextAlignment(Qt.AlignCenter)
                material_table.setItem(i, j, item)
        
        # 调整列宽
        header = material_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        
        layout.addWidget(material_table)
        
        # 计算公式说明
        formula_group = QGroupBox("📐 计算公式")
        formula_layout = QVBoxLayout(formula_group)
        
        formula_text = QTextEdit()
        formula_text.setReadOnly(True)
        formula_text.setHtml("""
        <h3>保温厚度计算公式</h3>
        
        <h4>1. 圆管热损失计算</h4>
        <p>Q = 2πλ(T₁ - T₂) / ln(D₂/D₁)</p>
        <p>其中：λ-导热系数，T₁-介质温度，T₂-环境温度，D₁-管道外径，D₂-保温外径</p>
        
        <h4>2. 表面温度计算</h4>
        <p>T<sub>s</sub> = T₂ + Q × R<sub>s</sub></p>
        <p>其中：T<sub>s</sub>-表面温度，R<sub>s</sub>-表面热阻</p>
        
        <h4>3. 经济厚度计算</h4>
        <p>δ = [P<sub>E</sub> × λ × τ × (T - T<sub>a</sub>) / (P<sub>T</sub> × S)]<sup>0.5</sup> - λ / α</p>
        <p>其中：P<sub>E</sub>-能源价格，τ-年运行时间，P<sub>T</sub>-保温材料价格，S-投资回收期，α-表面传热系数</p>
        
        <h4>4. 表面传热系数</h4>
        <p>α = 9.4 + 0.052 × (T<sub>s</sub> - T<sub>a</sub>) + 3.6 × v<sup>0.5</sup></p>
        <p>其中：v-风速，T<sub>s</sub>-表面温度，T<sub>a</sub>-环境温度</p>
        
        <h3>📖 参考标准</h3>
        <ul>
            <li>GB/T 8175-2008 设备及管道绝热设计导则</li>
            <li>GB 50264-2013 工业设备及管道绝热工程设计规范</li>
            <li>ASHRAE Handbook - Fundamentals</li>
            <li>ASTM C680 保温厚度计算标准</li>
        </ul>
        """)
        formula_layout.addWidget(formula_text)
        
        layout.addWidget(formula_group)
        
        return tab
    
    def calculate_insulation(self):
        """计算保温厚度"""
        try:
            # 获取输入值
            equipment_type = self.equipment_type_combo.currentText()
            diameter = self.diameter_input.value() / 1000  # 转换为米
            length = self.length_input.value()
            media_temp = self.media_temp_input.value()
            ambient_temp = self.ambient_temp_input.value()
            surface_temp_limit = self.surface_temp_input.value()
            conductivity = self.conductivity_input.value()
            thickness = self.thickness_input.value() / 1000  # 转换为米
            heat_loss_limit = self.heat_loss_input.value()
            wind_speed = self.wind_speed_input.value()
            is_outdoor = self.weather_proof_check.isChecked()
            standard = self.standard_combo.currentText()
            
            # 计算保温外径
            outer_diameter = diameter + 2 * thickness
            
            # 计算热损失
            heat_loss = self.calculate_heat_loss(diameter, outer_diameter, media_temp, ambient_temp, conductivity)
            
            # 计算表面温度
            surface_temp = self.calculate_surface_temperature(heat_loss, ambient_temp, wind_speed, outer_diameter)
            
            # 计算经济厚度
            economic_thickness = self.calculate_economic_thickness(diameter, media_temp, ambient_temp, conductivity)
            
            # 验证厚度是否满足要求
            is_valid = self.validate_thickness(surface_temp, surface_temp_limit, heat_loss, heat_loss_limit)
            
            # 计算材料用量和成本
            material_usage = self.calculate_material_usage(diameter, thickness, length)
            
            # 显示结果
            self.display_results(heat_loss, surface_temp, economic_thickness, is_valid, material_usage)
            
            # 更新详细参数表
            self.update_detail_table(heat_loss, surface_temp, economic_thickness, material_usage)
            
        except Exception as e:
            QMessageBox.warning(self, "计算错误", f"计算过程中发生错误: {str(e)}")
    
    def calculate_heat_loss(self, inner_diameter, outer_diameter, media_temp, ambient_temp, conductivity):
        """计算热损失"""
        # 圆管热损失公式
        if outer_diameter > inner_diameter:
            heat_loss = (2 * math.pi * conductivity * (media_temp - ambient_temp)) / math.log(outer_diameter / inner_diameter)
        else:
            heat_loss = 0
        
        # 转换为W/m²
        surface_area = math.pi * outer_diameter
        heat_loss_per_area = heat_loss / surface_area if surface_area > 0 else 0
        
        return heat_loss_per_area
    
    def calculate_surface_temperature(self, heat_loss, ambient_temp, wind_speed, diameter):
        """计算表面温度"""
        # 计算表面传热系数
        # 先假设表面温度进行迭代计算
        surface_temp_guess = ambient_temp + 20  # 初始猜测
        
        for i in range(10):  # 最多迭代10次
            # 表面传热系数公式
            h = 9.4 + 0.052 * (surface_temp_guess - ambient_temp) + 3.6 * math.sqrt(wind_speed)
            
            # 计算新的表面温度
            surface_temp_new = ambient_temp + heat_loss * math.pi * diameter / h
            
            # 检查收敛
            if abs(surface_temp_new - surface_temp_guess) < 0.1:
                return surface_temp_new
            
            surface_temp_guess = surface_temp_new
        
        return surface_temp_guess
    
    def calculate_economic_thickness(self, diameter, media_temp, ambient_temp, conductivity):
        """计算经济厚度"""
        # 简化经济厚度计算
        # 基于GB/T 8175标准简化公式
        
        delta_t = media_temp - ambient_temp
        
        if delta_t <= 0:
            return 0
        
        # 经济厚度经验公式 (mm)
        if media_temp <= 100:
            economic_thickness = 20 + 0.1 * delta_t
        elif media_temp <= 200:
            economic_thickness = 30 + 0.15 * delta_t
        elif media_temp <= 300:
            economic_thickness = 40 + 0.2 * delta_t
        elif media_temp <= 400:
            economic_thickness = 50 + 0.25 * delta_t
        else:
            economic_thickness = 60 + 0.3 * delta_t
        
        # 考虑管道直径的影响
        diameter_factor = 1 + (diameter * 1000 - 100) / 1000  # 基于100mm管径的修正
        
        return economic_thickness * diameter_factor
    
    def validate_thickness(self, surface_temp, surface_temp_limit, heat_loss, heat_loss_limit):
        """验证厚度是否满足要求"""
        # 检查表面温度
        if surface_temp > surface_temp_limit:
            return False
        
        # 检查热损失
        if heat_loss > heat_loss_limit:
            return False
        
        return True
    
    def calculate_material_usage(self, diameter, thickness, length):
        """计算材料用量"""
        # 计算保温层体积
        outer_diameter = diameter + 2 * thickness
        volume = math.pi * (outer_diameter**2 - diameter**2) / 4 * length
        
        # 计算材料重量
        density = self.density_input.value()
        weight = volume * density
        
        # 估算成本 (简化估算)
        cost_per_m3 = 800  # 假设800元/m³
        cost = volume * cost_per_m3
        
        return {
            "volume": volume,
            "weight": weight,
            "cost": cost
        }
    
    def auto_calculate_thickness(self):
        """自动计算厚度"""
        try:
            diameter = self.diameter_input.value()
            media_temp = self.media_temp_input.value()
            ambient_temp = self.ambient_temp_input.value()
            conductivity = self.conductivity_input.value()
            surface_temp_limit = self.surface_temp_input.value()
            heat_loss_limit = self.heat_loss_input.value()
            
            # 使用迭代方法找到满足条件的最小厚度
            thickness = 10  # 从10mm开始
            max_thickness = 200  # 最大厚度200mm
            
            for thickness in range(10, max_thickness + 1, 5):
                thickness_m = thickness / 1000
                diameter_m = diameter / 1000
                outer_diameter = diameter_m + 2 * thickness_m
                
                # 计算热损失
                heat_loss = self.calculate_heat_loss(diameter_m, outer_diameter, media_temp, ambient_temp, conductivity)
                
                # 计算表面温度
                surface_temp = self.calculate_surface_temperature(heat_loss, ambient_temp, 
                                                                self.wind_speed_input.value(), outer_diameter)
                
                # 检查是否满足条件
                if surface_temp <= surface_temp_limit and heat_loss <= heat_loss_limit:
                    break
            
            # 设置计算出的厚度
            self.thickness_input.setValue(thickness)
            
            QMessageBox.information(self, "厚度计算", f"推荐保温厚度: {thickness} mm")
            
        except Exception as e:
            QMessageBox.warning(self, "计算错误", f"厚度计算失败: {str(e)}")
    
    def display_results(self, heat_loss, surface_temp, economic_thickness, is_valid, material_usage):
        """显示计算结果"""
        status_color = "green" if is_valid else "red"
        status_text = "✅ 满足要求" if is_valid else "❌ 不满足要求"
        
        result_text = f"""
        <h3>🧊 保温厚度计算结果</h3>
        
        <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr style="background-color: #f8f9fa;">
            <td style="padding: 8px; font-weight: bold;">项目</td>
            <td style="padding: 8px;">计算结果</td>
            <td style="padding: 8px;">说明</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">热损失</td>
            <td style="padding: 8px; color: #e74c3c; font-weight: bold;">{heat_loss:.1f} W/m²</td>
            <td style="padding: 8px;">单位面积热损失</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">表面温度</td>
            <td style="padding: 8px; color: #3498db;">{surface_temp:.1f} °C</td>
            <td style="padding: 8px;">保温层外表面温度</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">经济厚度</td>
            <td style="padding: 8px; color: #27ae60;">{economic_thickness:.0f} mm</td>
            <td style="padding: 8px;">基于经济性计算</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">验证结果</td>
            <td style="padding: 8px; color: {status_color}; font-weight: bold;">{status_text}</td>
            <td style="padding: 8px;">满足温度和热损失要求</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">材料体积</td>
            <td style="padding: 8px;">{material_usage['volume']:.2f} m³</td>
            <td style="padding: 8px;">所需保温材料体积</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">材料重量</td>
            <td style="padding: 8px;">{material_usage['weight']:.0f} kg</td>
            <td style="padding: 8px;">保温材料总重量</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">估算成本</td>
            <td style="padding: 8px;">¥{material_usage['cost']:.0f}</td>
            <td style="padding: 8px;">材料成本估算</td>
        </tr>
        </table>
        """
        
        if not is_valid:
            result_text += """
            <h4 style="color: red;">⚠️ 设计建议</h4>
            <ul>
                <li>增加保温层厚度以满足要求</li>
                <li>选择导热系数更低的保温材料</li>
                <li>考虑使用多层保温结构</li>
                <li>检查环境条件是否合理</li>
            </ul>
            """
        else:
            result_text += """
            <h4 style="color: green;">✅ 设计建议</h4>
            <ul>
                <li>当前厚度满足设计要求</li>
                <li>可考虑经济厚度进行优化</li>
                <li>确保施工质量以减少热桥</li>
                <li>定期检查保温层完整性</li>
            </ul>
            """
        
        self.result_text.setHtml(result_text)
    
    def update_detail_table(self, heat_loss, surface_temp, economic_thickness, material_usage):
        """更新详细参数表"""
        detail_data = [
            ["热损失", f"{heat_loss:.1f}", "W/m²"],
            ["表面温度", f"{surface_temp:.1f}", "°C"],
            ["经济厚度", f"{economic_thickness:.0f}", "mm"],
            ["材料体积", f"{material_usage['volume']:.3f}", "m³"],
            ["材料重量", f"{material_usage['weight']:.1f}", "kg"],
            ["估算成本", f"¥{material_usage['cost']:.0f}", "元"],
            ["年节能量", f"{heat_loss * 8760 / 1000:.0f}", "kWh/m"],
            ["投资回收期", "2-5", "年"]
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
    
    def clear_inputs(self):
        """清空输入"""
        self.equipment_type_combo.setCurrentIndex(0)
        self.diameter_input.setValue(219)
        self.length_input.setValue(100)
        self.media_temp_input.setValue(150)
        self.ambient_temp_input.setValue(20)
        self.surface_temp_input.setValue(50)
        self.insulation_combo.setCurrentIndex(0)
        self.conductivity_input.setValue(0.04)
        self.density_input.setValue(120)
        self.thickness_input.setValue(50)
        self.standard_combo.setCurrentIndex(0)
        self.heat_loss_input.setValue(150)
        self.wind_speed_input.setValue(2.5)
        self.humidity_input.setValue(60)
        self.weather_proof_check.setChecked(True)
        self.result_text.clear()
        self.detail_table.setRowCount(0)

if __name__ == "__main__":
    # 测试代码
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    widget = InsulationThicknessCalculator()
    widget.resize(900, 700)
    widget.show()
    
    sys.exit(app.exec())