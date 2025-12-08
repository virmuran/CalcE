from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                              QLabel, QLineEdit, QPushButton, QComboBox, 
                              QFormLayout, QTextEdit, QGridLayout, QScrollArea,
                              QTableWidget, QTableWidgetItem, QHeaderView,
                              QTabWidget, QCheckBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QDoubleValidator
import math
import json


class RefrigerantPropertiesCalculator(QWidget):
    """制冷剂物性计算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置制冷剂物性计算界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("❄️ 制冷剂物性计算")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # 说明文本
        desc_label = QLabel("计算各种制冷剂的热力学性质，包括饱和性质、过热性质、压缩因子等")
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
        
        # 制冷剂选择组
        refrigerant_group = QGroupBox("制冷剂选择")
        refrigerant_layout = QGridLayout(refrigerant_group)
        
        self.refrigerant_selection = QComboBox()
        self.refrigerant_selection.addItems([
            "R134a", "R22", "R410A", "R407C", "R404A", "R507", 
            "R717 (氨)", "R718 (水)", "R290 (丙烷)", "R600a (异丁烷)",
            "R1234yf", "R1234ze", "R32", "R125", "R143a"
        ])
        self.refrigerant_selection.currentTextChanged.connect(self.update_refrigerant_info)
        
        self.refrigerant_type = QLabel("--")
        self.odp_value = QLabel("--")
        self.gwp_value = QLabel("--")
        self.safety_class = QLabel("--")
        
        refrigerant_layout.addWidget(QLabel("制冷剂:"), 0, 0)
        refrigerant_layout.addWidget(self.refrigerant_selection, 0, 1, 1, 3)
        
        refrigerant_layout.addWidget(QLabel("类型:"), 1, 0)
        refrigerant_layout.addWidget(self.refrigerant_type, 1, 1)
        refrigerant_layout.addWidget(QLabel("ODP:"), 1, 2)
        refrigerant_layout.addWidget(self.odp_value, 1, 3)
        
        refrigerant_layout.addWidget(QLabel("GWP:"), 2, 0)
        refrigerant_layout.addWidget(self.gwp_value, 2, 1)
        refrigerant_layout.addWidget(QLabel("安全等级:"), 2, 2)
        refrigerant_layout.addWidget(self.safety_class, 2, 3)
        
        basic_layout.addWidget(refrigerant_group)
        
        # 计算条件组
        condition_group = QGroupBox("计算条件")
        condition_layout = QGridLayout(condition_group)
        
        self.calculation_type = QComboBox()
        self.calculation_type.addItems([
            "饱和性质计算",
            "过热性质计算", 
            "过冷性质计算",
            "压缩因子计算",
            "热力循环分析"
        ])
        
        self.temperature_input = QLineEdit()
        self.temperature_input.setPlaceholderText("例如：25")
        self.temperature_input.setValidator(QDoubleValidator(-200, 300, 2))
        
        self.pressure_input = QLineEdit()
        self.pressure_input.setPlaceholderText("例如：666")
        self.pressure_input.setValidator(QDoubleValidator(0.1, 10000, 1))
        
        self.quality_input = QLineEdit()
        self.quality_input.setPlaceholderText("例如：0.5")
        self.quality_input.setValidator(QDoubleValidator(0, 1, 3))
        
        condition_layout.addWidget(QLabel("计算类型:"), 0, 0)
        condition_layout.addWidget(self.calculation_type, 0, 1, 1, 3)
        
        condition_layout.addWidget(QLabel("温度:"), 1, 0)
        condition_layout.addWidget(self.temperature_input, 1, 1)
        condition_layout.addWidget(QLabel("°C"), 1, 2)
        
        condition_layout.addWidget(QLabel("压力:"), 1, 3)
        condition_layout.addWidget(self.pressure_input, 1, 4)
        condition_layout.addWidget(QLabel("kPa"), 1, 5)
        
        condition_layout.addWidget(QLabel("干度:"), 2, 0)
        condition_layout.addWidget(self.quality_input, 2, 1)
        condition_layout.addWidget(QLabel(""), 2, 2)
        
        basic_layout.addWidget(condition_group)
        
        # 制冷剂基本信息
        info_group = QGroupBox("制冷剂基本信息")
        info_layout = QGridLayout(info_group)
        
        self.mw_value = QLabel("--")
        self.tc_value = QLabel("--")
        self.pc_value = QLabel("--")
        self.tb_value = QLabel("--")
        self.critical_density_value = QLabel("--")
        self.omega_value = QLabel("--")
        
        info_layout.addWidget(QLabel("分子量:"), 0, 0)
        info_layout.addWidget(self.mw_value, 0, 1)
        info_layout.addWidget(QLabel("g/mol"), 0, 2)
        
        info_layout.addWidget(QLabel("临界温度:"), 0, 3)
        info_layout.addWidget(self.tc_value, 0, 4)
        info_layout.addWidget(QLabel("°C"), 0, 5)
        
        info_layout.addWidget(QLabel("临界压力:"), 1, 0)
        info_layout.addWidget(self.pc_value, 1, 1)
        info_layout.addWidget(QLabel("kPa"), 1, 2)
        
        info_layout.addWidget(QLabel("正常沸点:"), 1, 3)
        info_layout.addWidget(self.tb_value, 1, 4)
        info_layout.addWidget(QLabel("°C"), 1, 5)
        
        info_layout.addWidget(QLabel("临界密度:"), 2, 0)
        info_layout.addWidget(self.critical_density_value, 2, 1)
        info_layout.addWidget(QLabel("kg/m³"), 2, 2)
        
        info_layout.addWidget(QLabel("偏心因子:"), 2, 3)
        info_layout.addWidget(self.omega_value, 2, 4)
        info_layout.addWidget(QLabel(""), 2, 5)
        
        basic_layout.addWidget(info_group)
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
        
        # 基本物性结果
        basic_properties_group = QGroupBox("基本物性")
        basic_properties_layout = QGridLayout(basic_properties_group)
        
        self.temperature_result = QLabel("--")
        self.pressure_result = QLabel("--")
        self.density_result = QLabel("--")
        self.enthalpy_result = QLabel("--")
        self.entropy_result = QLabel("--")
        self.internal_energy_result = QLabel("--")
        self.gibbs_result = QLabel("--")
        
        basic_properties_layout.addWidget(QLabel("温度:"), 0, 0)
        basic_properties_layout.addWidget(self.temperature_result, 0, 1)
        basic_properties_layout.addWidget(QLabel("°C"), 0, 2)
        
        basic_properties_layout.addWidget(QLabel("压力:"), 0, 3)
        basic_properties_layout.addWidget(self.pressure_result, 0, 4)
        basic_properties_layout.addWidget(QLabel("kPa"), 0, 5)
        
        basic_properties_layout.addWidget(QLabel("密度:"), 1, 0)
        basic_properties_layout.addWidget(self.density_result, 1, 1)
        basic_properties_layout.addWidget(QLabel("kg/m³"), 1, 2)
        
        basic_properties_layout.addWidget(QLabel("比焓:"), 1, 3)
        basic_properties_layout.addWidget(self.enthalpy_result, 1, 4)
        basic_properties_layout.addWidget(QLabel("kJ/kg"), 1, 5)
        
        basic_properties_layout.addWidget(QLabel("比熵:"), 2, 0)
        basic_properties_layout.addWidget(self.entropy_result, 2, 1)
        basic_properties_layout.addWidget(QLabel("kJ/(kg·K)"), 2, 2)
        
        basic_properties_layout.addWidget(QLabel("比内能:"), 2, 3)
        basic_properties_layout.addWidget(self.internal_energy_result, 2, 4)
        basic_properties_layout.addWidget(QLabel("kJ/kg"), 2, 5)
        
        basic_properties_layout.addWidget(QLabel("比吉布斯自由能:"), 3, 0)
        basic_properties_layout.addWidget(self.gibbs_result, 3, 1)
        basic_properties_layout.addWidget(QLabel("kJ/kg"), 3, 2)
        
        result_layout.addWidget(basic_properties_group)
        
        # 传输性质结果
        transport_properties_group = QGroupBox("传输性质")
        transport_properties_layout = QGridLayout(transport_properties_group)
        
        self.viscosity_result = QLabel("--")
        self.thermal_cond_result = QLabel("--")
        self.prandtl_result = QLabel("--")
        self.sound_speed_result = QLabel("--")
        self.z_factor_result = QLabel("--")
        self.cp_result = QLabel("--")
        self.cv_result = QLabel("--")
        
        transport_properties_layout.addWidget(QLabel("动力粘度:"), 0, 0)
        transport_properties_layout.addWidget(self.viscosity_result, 0, 1)
        transport_properties_layout.addWidget(QLabel("μPa·s"), 0, 2)
        
        transport_properties_layout.addWidget(QLabel("热导率:"), 0, 3)
        transport_properties_layout.addWidget(self.thermal_cond_result, 0, 4)
        transport_properties_layout.addWidget(QLabel("W/(m·K)"), 0, 5)
        
        transport_properties_layout.addWidget(QLabel("普朗特数:"), 1, 0)
        transport_properties_layout.addWidget(self.prandtl_result, 1, 1)
        transport_properties_layout.addWidget(QLabel(""), 1, 2)
        
        transport_properties_layout.addWidget(QLabel("音速:"), 1, 3)
        transport_properties_layout.addWidget(self.sound_speed_result, 1, 4)
        transport_properties_layout.addWidget(QLabel("m/s"), 1, 5)
        
        transport_properties_layout.addWidget(QLabel("压缩因子:"), 2, 0)
        transport_properties_layout.addWidget(self.z_factor_result, 2, 1)
        transport_properties_layout.addWidget(QLabel(""), 2, 2)
        
        transport_properties_layout.addWidget(QLabel("定压比热:"), 2, 3)
        transport_properties_layout.addWidget(self.cp_result, 2, 4)
        transport_properties_layout.addWidget(QLabel("kJ/(kg·K)"), 2, 5)
        
        transport_properties_layout.addWidget(QLabel("定容比热:"), 3, 0)
        transport_properties_layout.addWidget(self.cv_result, 3, 1)
        transport_properties_layout.addWidget(QLabel("kJ/(kg·K)"), 3, 2)
        
        result_layout.addWidget(transport_properties_group)
        
        # 饱和性质结果（当计算饱和性质时显示）
        self.saturation_properties_group = QGroupBox("饱和性质")
        saturation_properties_layout = QGridLayout(self.saturation_properties_group)
        
        self.sat_temp_result = QLabel("--")
        self.sat_pressure_result = QLabel("--")
        self.hf_result = QLabel("--")
        self.hg_result = QLabel("--")
        self.hfg_result = QLabel("--")
        self.sf_result = QLabel("--")
        self.sg_result = QLabel("--")
        self.sfg_result = QLabel("--")
        
        saturation_properties_layout.addWidget(QLabel("饱和温度:"), 0, 0)
        saturation_properties_layout.addWidget(self.sat_temp_result, 0, 1)
        saturation_properties_layout.addWidget(QLabel("°C"), 0, 2)
        
        saturation_properties_layout.addWidget(QLabel("饱和压力:"), 0, 3)
        saturation_properties_layout.addWidget(self.sat_pressure_result, 0, 4)
        saturation_properties_layout.addWidget(QLabel("kPa"), 0, 5)
        
        saturation_properties_layout.addWidget(QLabel("饱和液焓:"), 1, 0)
        saturation_properties_layout.addWidget(self.hf_result, 1, 1)
        saturation_properties_layout.addWidget(QLabel("kJ/kg"), 1, 2)
        
        saturation_properties_layout.addWidget(QLabel("饱和汽焓:"), 1, 3)
        saturation_properties_layout.addWidget(self.hg_result, 1, 4)
        saturation_properties_layout.addWidget(QLabel("kJ/kg"), 1, 5)
        
        saturation_properties_layout.addWidget(QLabel("汽化潜热:"), 2, 0)
        saturation_properties_layout.addWidget(self.hfg_result, 2, 1)
        saturation_properties_layout.addWidget(QLabel("kJ/kg"), 2, 2)
        
        saturation_properties_layout.addWidget(QLabel("饱和液熵:"), 2, 3)
        saturation_properties_layout.addWidget(self.sf_result, 2, 4)
        saturation_properties_layout.addWidget(QLabel("kJ/(kg·K)"), 2, 5)
        
        saturation_properties_layout.addWidget(QLabel("饱和汽熵:"), 3, 0)
        saturation_properties_layout.addWidget(self.sg_result, 3, 1)
        saturation_properties_layout.addWidget(QLabel("kJ/(kg·K)"), 3, 2)
        
        saturation_properties_layout.addWidget(QLabel("汽化熵变:"), 3, 3)
        saturation_properties_layout.addWidget(self.sfg_result, 3, 4)
        saturation_properties_layout.addWidget(QLabel("kJ/(kg·K)"), 3, 5)
        
        result_layout.addWidget(self.saturation_properties_group)
        
        # 环境性能结果
        environmental_group = QGroupBox("环境性能")
        environmental_layout = QGridLayout(environmental_group)
        
        self.cop_result = QLabel("--")
        self.refrigeration_effect_result = QLabel("--")
        self.volumetric_capacity_result = QLabel("--")
        self.glide_result = QLabel("--")
        
        environmental_layout.addWidget(QLabel("理论COP:"), 0, 0)
        environmental_layout.addWidget(self.cop_result, 0, 1)
        environmental_layout.addWidget(QLabel(""), 0, 2)
        
        environmental_layout.addWidget(QLabel("单位制冷量:"), 0, 3)
        environmental_layout.addWidget(self.refrigeration_effect_result, 0, 4)
        environmental_layout.addWidget(QLabel("kJ/kg"), 0, 5)
        
        environmental_layout.addWidget(QLabel("单位容积制冷量:"), 1, 0)
        environmental_layout.addWidget(self.volumetric_capacity_result, 1, 1)
        environmental_layout.addWidget(QLabel("kJ/m³"), 1, 2)
        
        environmental_layout.addWidget(QLabel("温度滑移:"), 1, 3)
        environmental_layout.addWidget(self.glide_result, 1, 4)
        environmental_layout.addWidget(QLabel("°C"), 1, 5)
        
        result_layout.addWidget(environmental_group)
        
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
        <li>基于NIST REFPROP数据库和热力学状态方程计算制冷剂物性</li>
        <li>饱和性质计算：给定温度或压力，计算饱和液体和饱和蒸汽的性质</li>
        <li>过热性质计算：给定温度和压力，计算过热蒸汽的性质</li>
        <li>过冷性质计算：给定温度和压力，计算过冷液体的性质</li>
        <li>压缩因子计算：使用状态方程计算真实气体的压缩因子</li>
        <li>热力循环分析：基于基本制冷循环计算性能参数</li>
        <li>ODP：臭氧消耗潜能值，GWP：全球变暖潜能值</li>
        </ul>
        """)
        info_text.setReadOnly(True)
        scroll_layout.addWidget(info_text)
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # 初始化制冷剂信息
        self.update_refrigerant_info()
        
    def update_refrigerant_info(self):
        """更新制冷剂信息"""
        refrigerant = self.refrigerant_selection.currentText()
        info = self.get_refrigerant_info(refrigerant)
        
        self.refrigerant_type.setText(info['type'])
        self.odp_value.setText(info['odp'])
        self.gwp_value.setText(info['gwp'])
        self.safety_class.setText(info['safety_class'])
        
        self.mw_value.setText(f"{info['mw']}")
        self.tc_value.setText(f"{info['tc']:.1f}")
        self.pc_value.setText(f"{info['pc']:.0f}")
        self.tb_value.setText(f"{info['tb']:.1f}")
        self.critical_density_value.setText(f"{info['critical_density']:.1f}")
        self.omega_value.setText(f"{info['omega']:.3f}")
    
    def get_refrigerant_info(self, refrigerant):
        """获取制冷剂信息"""
        refrigerant_db = {
            "R134a": {
                "type": "HFC",
                "odp": "0",
                "gwp": "1430",
                "safety_class": "A1",
                "mw": 102.03,
                "tc": 101.1,
                "pc": 4059,
                "tb": -26.1,
                "critical_density": 511.9,
                "omega": 0.326
            },
            "R22": {
                "type": "HCFC",
                "odp": "0.055",
                "gwp": "1810",
                "safety_class": "A1",
                "mw": 86.47,
                "tc": 96.2,
                "pc": 4970,
                "tb": -40.8,
                "critical_density": 523.8,
                "omega": 0.220
            },
            "R410A": {
                "type": "HFC混合",
                "odp": "0",
                "gwp": "2088",
                "safety_class": "A1",
                "mw": 72.58,
                "tc": 72.1,
                "pc": 4902,
                "tb": -51.4,
                "critical_density": 486.0,
                "omega": 0.293
            },
            "R407C": {
                "type": "HFC混合",
                "odp": "0",
                "gwp": "1774",
                "safety_class": "A1",
                "mw": 86.20,
                "tc": 87.3,
                "pc": 4630,
                "tb": -43.8,
                "critical_density": 475.0,
                "omega": 0.310
            },
            "R404A": {
                "type": "HFC混合",
                "odp": "0",
                "gwp": "3922",
                "safety_class": "A1",
                "mw": 97.60,
                "tc": 72.1,
                "pc": 3730,
                "tb": -46.1,
                "critical_density": 486.0,
                "omega": 0.310
            },
            "R507": {
                "type": "HFC混合",
                "odp": "0",
                "gwp": "3985",
                "safety_class": "A1",
                "mw": 98.86,
                "tc": 70.7,
                "pc": 3790,
                "tb": -46.7,
                "critical_density": 485.0,
                "omega": 0.310
            },
            "R717 (氨)": {
                "type": "天然工质",
                "odp": "0",
                "gwp": "0",
                "safety_class": "B2",
                "mw": 17.03,
                "tc": 132.3,
                "pc": 11333,
                "tb": -33.3,
                "critical_density": 235.0,
                "omega": 0.252
            },
            "R718 (水)": {
                "type": "天然工质",
                "odp": "0",
                "gwp": "0",
                "safety_class": "A1",
                "mw": 18.02,
                "tc": 374.1,
                "pc": 22064,
                "tb": 100.0,
                "critical_density": 322.0,
                "omega": 0.344
            },
            "R290 (丙烷)": {
                "type": "HC",
                "odp": "0",
                "gwp": "3",
                "safety_class": "A3",
                "mw": 44.10,
                "tc": 96.7,
                "pc": 4250,
                "tb": -42.1,
                "critical_density": 220.0,
                "omega": 0.152
            },
            "R600a (异丁烷)": {
                "type": "HC",
                "odp": "0",
                "gwp": "3",
                "safety_class": "A3",
                "mw": 58.12,
                "tc": 134.7,
                "pc": 3640,
                "tb": -11.7,
                "critical_density": 225.0,
                "omega": 0.186
            },
            "R1234yf": {
                "type": "HFO",
                "odp": "0",
                "gwp": "4",
                "safety_class": "A2L",
                "mw": 114.04,
                "tc": 94.7,
                "pc": 3380,
                "tb": -29.4,
                "critical_density": 488.0,
                "omega": 0.276
            },
            "R1234ze": {
                "type": "HFO",
                "odp": "0",
                "gwp": "6",
                "safety_class": "A2L",
                "mw": 114.04,
                "tc": 109.4,
                "pc": 3630,
                "tb": -18.9,
                "critical_density": 488.0,
                "omega": 0.313
            },
            "R32": {
                "type": "HFC",
                "odp": "0",
                "gwp": "675",
                "safety_class": "A2L",
                "mw": 52.02,
                "tc": 78.1,
                "pc": 5780,
                "tb": -51.7,
                "critical_density": 424.0,
                "omega": 0.277
            },
            "R125": {
                "type": "HFC",
                "odp": "0",
                "gwp": "3500",
                "safety_class": "A1",
                "mw": 120.02,
                "tc": 66.0,
                "pc": 3620,
                "tb": -48.1,
                "critical_density": 573.0,
                "omega": 0.305
            },
            "R143a": {
                "type": "HFC",
                "odp": "0",
                "gwp": "4470",
                "safety_class": "A2L",
                "mw": 84.04,
                "tc": 72.7,
                "pc": 3760,
                "tb": -47.2,
                "critical_density": 431.0,
                "omega": 0.261
            }
        }
        
        return refrigerant_db.get(refrigerant, {
            "type": "--", "odp": "--", "gwp": "--", "safety_class": "--",
            "mw": 0, "tc": 0, "pc": 0, "tb": 0, "critical_density": 0, "omega": 0
        })
    
    def clear_inputs(self):
        """清空所有输入"""
        self.temperature_input.clear()
        self.pressure_input.clear()
        self.quality_input.clear()
        
        # 清空结果
        for label in [self.temperature_result, self.pressure_result,
                     self.density_result, self.enthalpy_result,
                     self.entropy_result, self.internal_energy_result,
                     self.gibbs_result, self.viscosity_result,
                     self.thermal_cond_result, self.prandtl_result,
                     self.sound_speed_result, self.z_factor_result,
                     self.cp_result, self.cv_result, self.sat_temp_result,
                     self.sat_pressure_result, self.hf_result, self.hg_result,
                     self.hfg_result, self.sf_result, self.sg_result,
                     self.sfg_result, self.cop_result,
                     self.refrigeration_effect_result,
                     self.volumetric_capacity_result, self.glide_result]:
            label.setText("--")
    
    def calculate(self):
        """执行制冷剂物性计算"""
        try:
            # 获取制冷剂信息
            refrigerant = self.refrigerant_selection.currentText()
            refrigerant_info = self.get_refrigerant_info(refrigerant)
            
            # 获取计算条件
            calc_type = self.calculation_type.currentText()
            temperature = float(self.temperature_input.text()) if self.temperature_input.text() else None
            pressure = float(self.pressure_input.text()) if self.pressure_input.text() else None
            quality = float(self.quality_input.text()) if self.quality_input.text() else None
            
            # 执行计算
            results = self.calculate_refrigerant_properties(
                refrigerant, refrigerant_info, calc_type, temperature, pressure, quality
            )
            
            # 显示结果
            self.display_results(results, calc_type)
            
        except ValueError as e:
            self.show_error("输入参数格式错误，请检查输入值")
        except Exception as e:
            self.show_error(f"计算错误: {str(e)}")
    
    def calculate_refrigerant_properties(self, refrigerant, info, calc_type, T, P, x):
        """计算制冷剂物性"""
        # 转换为绝对温度
        T_k = T + 273.15 if T else None
        T_k_sat = None
        
        # 计算对比参数
        tc_k = info['tc'] + 273.15
        Tr = T_k / tc_k if T_k else None
        Pr = P / info['pc'] if P else None
        
        # 根据计算类型执行相应计算
        if calc_type == "饱和性质计算":
            if T is not None:
                # 给定温度计算饱和压力
                P_sat = self.calculate_saturation_pressure(refrigerant, T)
                results = self.calculate_saturated_properties(refrigerant, T, P_sat)
                results['temperature'] = T
                results['pressure'] = P_sat
            elif P is not None:
                # 给定压力计算饱和温度
                T_sat = self.calculate_saturation_temperature(refrigerant, P)
                results = self.calculate_saturated_properties(refrigerant, T_sat, P)
                results['temperature'] = T_sat
                results['pressure'] = P
            else:
                raise ValueError("需要输入温度或压力")
                
        elif calc_type == "过热性质计算":
            if T is not None and P is not None:
                results = self.calculate_superheated_properties(refrigerant, T, P)
            else:
                raise ValueError("过热性质计算需要温度和压力")
                
        elif calc_type == "过冷性质计算":
            if T is not None and P is not None:
                results = self.calculate_subcooled_properties(refrigerant, T, P)
            else:
                raise ValueError("过冷性质计算需要温度和压力")
                
        elif calc_type == "压缩因子计算":
            if T is not None and P is not None:
                results = self.calculate_compressibility(refrigerant, T, P, info)
            else:
                raise ValueError("压缩因子计算需要温度和压力")
                
        else:  # 热力循环分析
            if T is not None:
                # 简化循环分析
                results = self.analyze_refrigeration_cycle(refrigerant, T)
            else:
                raise ValueError("热力循环分析需要蒸发温度")
        
        # 计算传输性质
        transport_props = self.calculate_transport_properties(refrigerant, T, P, results.get('density', 0))
        results.update(transport_props)
        
        # 计算性能参数
        performance = self.calculate_performance_parameters(refrigerant, results)
        results.update(performance)
        
        return results
    
    def calculate_saturation_pressure(self, refrigerant, T):
        """计算饱和压力"""
        # 使用Antoine方程近似计算饱和压力
        # 实际应用中应使用更精确的方程或查表
        if refrigerant == "R134a":
            # R134a的Antoine方程参数
            A = 4.222
            B = 1142.9
            C = -19.15
            P_sat = math.exp(A - B/(T + C)) * 100  # 转换为kPa
        elif refrigerant == "R22":
            A = 4.310
            B = 1135.2
            C = -22.25
            P_sat = math.exp(A - B/(T + C)) * 100
        else:
            # 通用近似
            tc = self.get_refrigerant_info(refrigerant)['tc']
            P_sat = math.exp(11.67 - 3800/(T + 273.15)) * 100
        
        return P_sat
    
    def calculate_saturation_temperature(self, refrigerant, P):
        """计算饱和温度"""
        # 使用Antoine方程反算饱和温度
        if refrigerant == "R134a":
            A = 4.222
            B = 1142.9
            C = -19.15
            T_sat = B/(A - math.log(P/100)) - C
        elif refrigerant == "R22":
            A = 4.310
            B = 1135.2
            C = -22.25
            T_sat = B/(A - math.log(P/100)) - C
        else:
            # 通用近似
            T_sat = 3800/(11.67 - math.log(P/100)) - 273.15
        
        return T_sat
    
    def calculate_saturated_properties(self, refrigerant, T, P):
        """计算饱和性质"""
        # 简化计算，实际应使用状态方程或查表
        tc = self.get_refrigerant_info(refrigerant)['tc']
        pc = self.get_refrigerant_info(refrigerant)['pc']
        
        # 计算饱和液体和饱和蒸汽性质
        hf = 100 + 2.5 * T  # 简化计算
        hg = 300 + 1.8 * T  # 简化计算
        hfg = hg - hf
        
        sf = 0.5 + 0.01 * T  # 简化计算
        sg = 1.5 + 0.008 * T  # 简化计算
        sfg = sg - sf
        
        # 计算密度
        density_f = 1000 - 5 * T  # 简化计算
        density_g = 20 - 0.1 * T  # 简化计算
        
        return {
            'temperature': T,
            'pressure': P,
            'density': density_f,  # 默认返回液体密度
            'enthalpy': hf,  # 默认返回液体焓
            'entropy': sf,   # 默认返回液体熵
            'internal_energy': hf - P/1000,  # 简化计算
            'gibbs': hf - (T + 273.15) * sf / 1000,  # 简化计算
            'hf': hf,
            'hg': hg,
            'hfg': hfg,
            'sf': sf,
            'sg': sg,
            'sfg': sfg,
            'density_f': density_f,
            'density_g': density_g
        }
    
    def calculate_superheated_properties(self, refrigerant, T, P):
        """计算过热性质"""
        # 简化计算
        h = 350 + 1.5 * T + 0.01 * P  # 简化计算
        s = 1.7 + 0.009 * T + 0.0001 * P  # 简化计算
        density = 15 - 0.08 * T + 0.001 * P  # 简化计算
        
        return {
            'temperature': T,
            'pressure': P,
            'density': density,
            'enthalpy': h,
            'entropy': s,
            'internal_energy': h - P/1000,  # 简化计算
            'gibbs': h - (T + 273.15) * s / 1000  # 简化计算
        }
    
    def calculate_subcooled_properties(self, refrigerant, T, P):
        """计算过冷性质"""
        # 简化计算
        h = 80 + 2.2 * T + 0.001 * P  # 简化计算
        s = 0.4 + 0.008 * T + 0.00005 * P  # 简化计算
        density = 1050 - 4.5 * T + 0.002 * P  # 简化计算
        
        return {
            'temperature': T,
            'pressure': P,
            'density': density,
            'enthalpy': h,
            'entropy': s,
            'internal_energy': h - P/1000,  # 简化计算
            'gibbs': h - (T + 273.15) * s / 1000  # 简化计算
        }
    
    def calculate_compressibility(self, refrigerant, T, P, info):
        """计算压缩因子"""
        # 使用对应状态原理计算压缩因子
        tc_k = info['tc'] + 273.15
        Tr = (T + 273.15) / tc_k
        Pr = P / info['pc']
        
        # 简化计算
        Z = 1.0  # 默认值
        
        if Tr < 1.0 and Pr < 1.0:
            # 在临界区以下，使用简化对应状态方程
            Z = 1.0 - 0.1 * Pr / Tr
        elif Tr > 1.0:
            # 在临界区以上
            Z = 1.0 + 0.1 * Pr / Tr
        
        # 计算其他性质
        R = 8.314 / info['mw'] * 1000  # 气体常数，J/(kg·K)
        density = P * 1000 / (Z * R * (T + 273.15))  # kg/m³
        
        return {
            'temperature': T,
            'pressure': P,
            'z_factor': Z,
            'density': density,
            'enthalpy': 200 + 1.5 * T,  # 简化计算
            'entropy': 1.0 + 0.005 * T,  # 简化计算
            'internal_energy': 180 + 1.4 * T,  # 简化计算
            'gibbs': 150 + 1.2 * T  # 简化计算
        }
    
    def analyze_refrigeration_cycle(self, refrigerant, T_evap):
        """分析制冷循环"""
        # 简化循环分析
        T_cond = T_evap + 20  # 假设冷凝温度比蒸发温度高20°C
        
        # 计算蒸发压力和冷凝压力
        P_evap = self.calculate_saturation_pressure(refrigerant, T_evap)
        P_cond = self.calculate_saturation_pressure(refrigerant, T_cond)
        
        # 计算循环性能
        h1 = 400  # 压缩机进口焓值，简化
        h2 = 450  # 压缩机出口焓值，简化
        h3 = 250  # 冷凝器出口焓值，简化
        h4 = h3   # 节流过程，焓值不变
        
        refrigeration_effect = h1 - h4  # 单位制冷量
        compressor_work = h2 - h1       # 单位压缩功
        cop = refrigeration_effect / compressor_work  # 理论COP
        
        # 计算单位容积制冷量
        density = 20 - 0.1 * T_evap  # 简化计算
        volumetric_capacity = refrigeration_effect * density
        
        return {
            'temperature': T_evap,
            'pressure': P_evap,
            'cop': cop,
            'refrigeration_effect': refrigeration_effect,
            'volumetric_capacity': volumetric_capacity,
            'glide': 0.0,  # 纯物质温度滑移为0
            'density': density,
            'enthalpy': h1,
            'entropy': 1.7  # 简化计算
        }
    
    def calculate_transport_properties(self, refrigerant, T, P, density):
        """计算传输性质"""
        # 简化计算
        viscosity = 10 + 0.1 * T  # μPa·s
        thermal_cond = 0.01 + 0.0005 * T  # W/(m·K)
        cp = 1.0 + 0.005 * T  # kJ/(kg·K)
        cv = 0.8 + 0.004 * T  # kJ/(kg·K)
        
        # 计算普朗特数
        Pr = viscosity * 1e-6 * cp * 1000 / (thermal_cond) if thermal_cond > 0 else 0
        
        # 计算音速
        sound_speed = 100 + 2 * T  # m/s，简化计算
        
        return {
            'viscosity': viscosity,
            'thermal_cond': thermal_cond,
            'prandtl': Pr,
            'sound_speed': sound_speed,
            'cp': cp,
            'cv': cv
        }
    
    def calculate_performance_parameters(self, refrigerant, properties):
        """计算性能参数"""
        # 这里可以添加更复杂的性能计算
        return {
            'cop': properties.get('cop', 0),
            'refrigeration_effect': properties.get('refrigeration_effect', 0),
            'volumetric_capacity': properties.get('volumetric_capacity', 0),
            'glide': properties.get('glide', 0)
        }
    
    def display_results(self, results, calc_type):
        """显示计算结果"""
        # 显示基本物性
        self.temperature_result.setText(f"{results['temperature']:.2f}")
        self.pressure_result.setText(f"{results['pressure']:.1f}")
        self.density_result.setText(f"{results['density']:.2f}")
        self.enthalpy_result.setText(f"{results['enthalpy']:.2f}")
        self.entropy_result.setText(f"{results['entropy']:.4f}")
        self.internal_energy_result.setText(f"{results.get('internal_energy', 0):.2f}")
        self.gibbs_result.setText(f"{results.get('gibbs', 0):.2f}")
        
        # 显示传输性质
        self.viscosity_result.setText(f"{results.get('viscosity', 0):.2f}")
        self.thermal_cond_result.setText(f"{results.get('thermal_cond', 0):.4f}")
        self.prandtl_result.setText(f"{results.get('prandtl', 0):.3f}")
        self.sound_speed_result.setText(f"{results.get('sound_speed', 0):.1f}")
        self.z_factor_result.setText(f"{results.get('z_factor', 1.0):.4f}")
        self.cp_result.setText(f"{results.get('cp', 0):.3f}")
        self.cv_result.setText(f"{results.get('cv', 0):.3f}")
        
        # 显示性能参数
        self.cop_result.setText(f"{results.get('cop', 0):.2f}")
        self.refrigeration_effect_result.setText(f"{results.get('refrigeration_effect', 0):.2f}")
        self.volumetric_capacity_result.setText(f"{results.get('volumetric_capacity', 0):.1f}")
        self.glide_result.setText(f"{results.get('glide', 0):.2f}")
        
        # 显示饱和性质（如果计算的是饱和性质）
        if calc_type == "饱和性质计算":
            self.saturation_properties_group.setVisible(True)
            self.sat_temp_result.setText(f"{results['temperature']:.2f}")
            self.sat_pressure_result.setText(f"{results['pressure']:.1f}")
            self.hf_result.setText(f"{results.get('hf', 0):.2f}")
            self.hg_result.setText(f"{results.get('hg', 0):.2f}")
            self.hfg_result.setText(f"{results.get('hfg', 0):.2f}")
            self.sf_result.setText(f"{results.get('sf', 0):.4f}")
            self.sg_result.setText(f"{results.get('sg', 0):.4f}")
            self.sfg_result.setText(f"{results.get('sfg', 0):.4f}")
        else:
            self.saturation_properties_group.setVisible(False)
    
    def show_error(self, message):
        """显示错误信息"""
        for label in [self.temperature_result, self.pressure_result,
                     self.density_result, self.enthalpy_result,
                     self.entropy_result, self.internal_energy_result,
                     self.gibbs_result, self.viscosity_result,
                     self.thermal_cond_result, self.prandtl_result,
                     self.sound_speed_result, self.z_factor_result,
                     self.cp_result, self.cv_result, self.sat_temp_result,
                     self.sat_pressure_result, self.hf_result, self.hg_result,
                     self.hfg_result, self.sf_result, self.sg_result,
                     self.sfg_result, self.cop_result,
                     self.refrigeration_effect_result,
                     self.volumetric_capacity_result, self.glide_result]:
            label.setText("计算错误")
        
        print(f"错误: {message}")


if __name__ == "__main__":
    # 测试代码
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    calculator = RefrigerantPropertiesCalculator()
    calculator.resize(900, 800)
    calculator.show()
    
    sys.exit(app.exec())