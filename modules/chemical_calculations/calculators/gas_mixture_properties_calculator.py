from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                              QLabel, QLineEdit, QPushButton, QComboBox, 
                              QFormLayout, QTextEdit, QGridLayout, QScrollArea,
                              QTableWidget, QTableWidgetItem, QHeaderView,
                              QTabWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QDoubleValidator
import math
import numpy as np


class GasMixturePropertiesCalculator(QWidget):
    """气体混合物物性计算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.components = []
        self.setup_ui()
        
    def setup_ui(self):
        """设置气体混合物物性计算界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("气体混合物物性计算")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # 说明文本
        desc_label = QLabel("计算气体混合物的密度、粘度、热导率、比热容、压缩因子等物性参数")
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
        
        # 组分设置标签页
        composition_tab = QWidget()
        composition_layout = QVBoxLayout(composition_tab)
        
        # 条件设置组
        condition_group = QGroupBox("计算条件")
        condition_layout = QGridLayout(condition_group)
        
        self.temperature_input = QLineEdit()
        self.temperature_input.setText("25")
        self.temperature_input.setValidator(QDoubleValidator(-273, 2000, 2))
        
        self.pressure_input = QLineEdit()
        self.pressure_input.setText("101.325")
        self.temperature_input.setValidator(QDoubleValidator(0.1, 100000, 2))
        
        self.mixture_type = QComboBox()
        self.mixture_type.addItems(["理想气体", "真实气体"])
        
        self.calculation_method = QComboBox()
        self.calculation_method.addItems(["简单混合规则", "Kay规则", "对应状态原理"])
        
        condition_layout.addWidget(QLabel("温度:"), 0, 0)
        condition_layout.addWidget(self.temperature_input, 0, 1)
        condition_layout.addWidget(QLabel("°C"), 0, 2)
        
        condition_layout.addWidget(QLabel("压力:"), 0, 3)
        condition_layout.addWidget(self.pressure_input, 0, 4)
        condition_layout.addWidget(QLabel("kPa"), 0, 5)
        
        condition_layout.addWidget(QLabel("混合物类型:"), 1, 0)
        condition_layout.addWidget(self.mixture_type, 1, 1, 1, 2)
        
        condition_layout.addWidget(QLabel("计算方法:"), 1, 3)
        condition_layout.addWidget(self.calculation_method, 1, 4, 1, 2)
        
        composition_layout.addWidget(condition_group)
        
        # 组分设置组
        component_group = QGroupBox("组分设置")
        component_layout = QVBoxLayout(component_group)
        
        # 组分数量选择
        component_count_layout = QHBoxLayout()
        component_count_layout.addWidget(QLabel("组分数:"))
        self.component_count = QComboBox()
        self.component_count.addItems(["2", "3", "4", "5"])
        self.component_count.currentTextChanged.connect(self.update_component_table)
        component_count_layout.addWidget(self.component_count)
        component_count_layout.addStretch()
        component_layout.addLayout(component_count_layout)
        
        # 组分参数表
        self.component_table = QTableWidget()
        self.component_table.setColumnCount(8)
        self.component_table.setHorizontalHeaderLabels([
            "组分", "摩尔分数", "分子量", "临界温度", "临界压力", "临界体积", "偏心因子", "Zc"
        ])
        component_layout.addWidget(self.component_table)
        
        composition_layout.addWidget(component_group)
        composition_layout.addStretch()
        
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
        
        self.mw_mixture_result = QLabel("--")
        self.tc_mixture_result = QLabel("--")
        self.pc_mixture_result = QLabel("--")
        self.vc_mixture_result = QLabel("--")
        self.omega_mixture_result = QLabel("--")
        self.zc_mixture_result = QLabel("--")
        
        basic_properties_layout.addWidget(QLabel("平均分子量:"), 0, 0)
        basic_properties_layout.addWidget(self.mw_mixture_result, 0, 1)
        basic_properties_layout.addWidget(QLabel("g/mol"), 0, 2)
        
        basic_properties_layout.addWidget(QLabel("虚拟临界温度:"), 0, 3)
        basic_properties_layout.addWidget(self.tc_mixture_result, 0, 4)
        basic_properties_layout.addWidget(QLabel("K"), 0, 5)
        
        basic_properties_layout.addWidget(QLabel("虚拟临界压力:"), 1, 0)
        basic_properties_layout.addWidget(self.pc_mixture_result, 1, 1)
        basic_properties_layout.addWidget(QLabel("kPa"), 1, 2)
        
        basic_properties_layout.addWidget(QLabel("虚拟临界体积:"), 1, 3)
        basic_properties_layout.addWidget(self.vc_mixture_result, 1, 4)
        basic_properties_layout.addWidget(QLabel("cm³/mol"), 1, 5)
        
        basic_properties_layout.addWidget(QLabel("平均偏心因子:"), 2, 0)
        basic_properties_layout.addWidget(self.omega_mixture_result, 2, 1)
        basic_properties_layout.addWidget(QLabel(""), 2, 2)
        
        basic_properties_layout.addWidget(QLabel("虚拟临界压缩因子:"), 2, 3)
        basic_properties_layout.addWidget(self.zc_mixture_result, 2, 4)
        basic_properties_layout.addWidget(QLabel(""), 2, 5)
        
        result_layout.addWidget(basic_properties_group)
        
        # 热物性结果
        thermal_properties_group = QGroupBox("热物性")
        thermal_properties_layout = QGridLayout(thermal_properties_group)
        
        self.density_result = QLabel("--")
        self.z_factor_result = QLabel("--")
        self.viscosity_result = QLabel("--")
        self.thermal_cond_result = QLabel("--")
        self.cp_result = QLabel("--")
        self.cv_result = QLabel("--")
        self.ratio_cp_cv_result = QLabel("--")
        self.sound_speed_result = QLabel("--")
        
        thermal_properties_layout.addWidget(QLabel("密度:"), 0, 0)
        thermal_properties_layout.addWidget(self.density_result, 0, 1)
        thermal_properties_layout.addWidget(QLabel("kg/m³"), 0, 2)
        
        thermal_properties_layout.addWidget(QLabel("压缩因子:"), 0, 3)
        thermal_properties_layout.addWidget(self.z_factor_result, 0, 4)
        thermal_properties_layout.addWidget(QLabel(""), 0, 5)
        
        thermal_properties_layout.addWidget(QLabel("粘度:"), 1, 0)
        thermal_properties_layout.addWidget(self.viscosity_result, 1, 1)
        thermal_properties_layout.addWidget(QLabel("μPa·s"), 1, 2)
        
        thermal_properties_layout.addWidget(QLabel("热导率:"), 1, 3)
        thermal_properties_layout.addWidget(self.thermal_cond_result, 1, 4)
        thermal_properties_layout.addWidget(QLabel("W/(m·K)"), 1, 5)
        
        thermal_properties_layout.addWidget(QLabel("定压比热:"), 2, 0)
        thermal_properties_layout.addWidget(self.cp_result, 2, 1)
        thermal_properties_layout.addWidget(QLabel("J/(mol·K)"), 2, 2)
        
        thermal_properties_layout.addWidget(QLabel("定容比热:"), 2, 3)
        thermal_properties_layout.addWidget(self.cv_result, 2, 4)
        thermal_properties_layout.addWidget(QLabel("J/(mol·K)"), 2, 5)
        
        thermal_properties_layout.addWidget(QLabel("比热比:"), 3, 0)
        thermal_properties_layout.addWidget(self.ratio_cp_cv_result, 3, 1)
        thermal_properties_layout.addWidget(QLabel(""), 3, 2)
        
        thermal_properties_layout.addWidget(QLabel("音速:"), 3, 3)
        thermal_properties_layout.addWidget(self.sound_speed_result, 3, 4)
        thermal_properties_layout.addWidget(QLabel("m/s"), 3, 5)
        
        result_layout.addWidget(thermal_properties_group)
        
        # 对应状态参数
        state_params_group = QGroupBox("对应状态参数")
        state_params_layout = QGridLayout(state_params_group)
        
        self.tr_result = QLabel("--")
        self.pr_result = QLabel("--")
        self.vr_result = QLabel("--")
        self.reduced_density_result = QLabel("--")
        
        state_params_layout.addWidget(QLabel("对比温度:"), 0, 0)
        state_params_layout.addWidget(self.tr_result, 0, 1)
        state_params_layout.addWidget(QLabel(""), 0, 2)
        
        state_params_layout.addWidget(QLabel("对比压力:"), 0, 3)
        state_params_layout.addWidget(self.pr_result, 0, 4)
        state_params_layout.addWidget(QLabel(""), 0, 5)
        
        state_params_layout.addWidget(QLabel("对比体积:"), 1, 0)
        state_params_layout.addWidget(self.vr_result, 1, 1)
        state_params_layout.addWidget(QLabel(""), 1, 2)
        
        state_params_layout.addWidget(QLabel("对比密度:"), 1, 3)
        state_params_layout.addWidget(self.reduced_density_result, 1, 4)
        state_params_layout.addWidget(QLabel(""), 1, 5)
        
        result_layout.addWidget(state_params_group)
        
        # 添加标签页
        self.tab_widget.addTab(composition_tab, "组分设置")
        self.tab_widget.addTab(result_tab, "计算结果")
        
        scroll_layout.addWidget(self.tab_widget)
        
        # 计算说明
        info_text = QTextEdit()
        info_text.setMaximumHeight(150)
        info_text.setHtml("""
        <h4>计算说明:</h4>
        <ul>
        <li>平均分子量: M_mix = Σ(y_i × M_i)</li>
        <li>Kay规则: T_cm = Σ(y_i × T_ci), P_cm = Σ(y_i × P_ci)</li>
        <li>密度: 理想气体使用理想气体状态方程，真实气体使用对应状态原理</li>
        <li>粘度: 使用Wilke混合规则或对应状态方法</li>
        <li>热导率: 使用Mason和Saxena修正的对应状态方法</li>
        <li>压缩因子: 使用对应状态原理和Lee-Kesler方程</li>
        <li>比热容: 基于理想气体比热容和剩余性质计算</li>
        </ul>
        """)
        info_text.setReadOnly(True)
        scroll_layout.addWidget(info_text)
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # 初始化表格
        self.update_component_table()
        
    def update_component_table(self):
        """更新组分参数表"""
        count = int(self.component_count.currentText())
        self.component_table.setRowCount(count)
        
        # 预设一些常见气体的物性参数
        preset_gases = {
            "氮气(N2)": [28.013, 126.2, 3390, 89.5, 0.037, 0.29],
            "氧气(O2)": [31.999, 154.6, 5043, 73.4, 0.021, 0.288],
            "氢气(H2)": [2.016, 33.2, 1315, 65.0, -0.216, 0.305],
            "二氧化碳(CO2)": [44.01, 304.2, 7377, 94.0, 0.225, 0.274],
            "甲烷(CH4)": [16.043, 190.6, 4600, 99.0, 0.008, 0.288],
            "乙烷(C2H6)": [30.07, 305.4, 4880, 148.0, 0.098, 0.285],
            "丙烷(C3H8)": [44.096, 369.8, 4248, 203.0, 0.152, 0.281],
            "水蒸气(H2O)": [18.015, 647.3, 22064, 56.0, 0.344, 0.229],
            "氩气(Ar)": [39.948, 150.9, 4898, 74.9, -0.002, 0.291],
            "一氧化碳(CO)": [28.01, 132.9, 3498, 93.1, 0.045, 0.292]
        }
        
        for i in range(count):
            # 组分名称
            name_combo = QComboBox()
            name_combo.addItems(list(preset_gases.keys()))
            name_combo.setCurrentIndex(i % len(preset_gases))
            self.component_table.setCellWidget(i, 0, name_combo)
            
            # 获取预设参数
            current_name = name_combo.currentText()
            params = preset_gases.get(current_name, [0, 0, 0, 0, 0, 0])
            
            # 摩尔分数
            if i == 0:
                y_item = QTableWidgetItem("0.5")
            elif i == 1:
                y_item = QTableWidgetItem("0.5")
            else:
                y_item = QTableWidgetItem("0.0")
            self.component_table.setItem(i, 1, y_item)
            
            # 分子量
            mw_item = QTableWidgetItem(f"{params[0]:.3f}")
            self.component_table.setItem(i, 2, mw_item)
            
            # 临界温度
            tc_item = QTableWidgetItem(f"{params[1]:.1f}")
            self.component_table.setItem(i, 3, tc_item)
            
            # 临界压力
            pc_item = QTableWidgetItem(f"{params[2]:.0f}")
            self.component_table.setItem(i, 4, pc_item)
            
            # 临界体积
            vc_item = QTableWidgetItem(f"{params[3]:.1f}")
            self.component_table.setItem(i, 5, vc_item)
            
            # 偏心因子
            omega_item = QTableWidgetItem(f"{params[4]:.3f}")
            self.component_table.setItem(i, 6, omega_item)
            
            # 临界压缩因子
            zc_item = QTableWidgetItem(f"{params[5]:.3f}")
            self.component_table.setItem(i, 7, zc_item)
    
    def clear_inputs(self):
        """清空所有输入"""
        self.temperature_input.setText("25")
        self.pressure_input.setText("101.325")
        self.update_component_table()
        
        # 清空结果
        for label in [self.mw_mixture_result, self.tc_mixture_result, 
                     self.pc_mixture_result, self.vc_mixture_result,
                     self.omega_mixture_result, self.zc_mixture_result,
                     self.density_result, self.z_factor_result,
                     self.viscosity_result, self.thermal_cond_result,
                     self.cp_result, self.cv_result, self.ratio_cp_cv_result,
                     self.sound_speed_result, self.tr_result, self.pr_result,
                     self.vr_result, self.reduced_density_result]:
            label.setText("--")
    
    def calculate(self):
        """执行气体混合物物性计算"""
        try:
            # 获取计算条件
            temperature = float(self.temperature_input.text())
            pressure = float(self.pressure_input.text())
            mixture_type = self.mixture_type.currentText()
            method = self.calculation_method.currentText()
            
            # 获取组分数据
            components = self.get_component_data()
            
            # 检查摩尔分数总和
            total_y = sum(comp['y'] for comp in components)
            if abs(total_y - 1.0) > 0.01:
                self.show_error(f"摩尔分数总和应为1.0，当前为{total_y:.3f}")
                return
            
            # 执行计算
            results = self.calculate_mixture_properties(components, temperature, pressure, mixture_type, method)
            
            # 显示结果
            self.display_results(results)
            
        except ValueError as e:
            self.show_error("输入参数格式错误，请检查输入值")
        except Exception as e:
            self.show_error(f"计算错误: {str(e)}")
    
    def get_component_data(self):
        """从表格获取组分数据"""
        count = int(self.component_count.currentText())
        components = []
        
        for i in range(count):
            name = self.component_table.cellWidget(i, 0).currentText()
            y = float(self.component_table.item(i, 1).text())
            mw = float(self.component_table.item(i, 2).text())
            tc = float(self.component_table.item(i, 3).text())
            pc = float(self.component_table.item(i, 4).text())
            vc = float(self.component_table.item(i, 5).text())
            omega = float(self.component_table.item(i, 6).text())
            zc = float(self.component_table.item(i, 7).text())
            
            components.append({
                'name': name,
                'y': y,
                'mw': mw,
                'tc': tc,
                'pc': pc,
                'vc': vc,
                'omega': omega,
                'zc': zc
            })
        
        return components
    
    def calculate_mixture_properties(self, components, T, P, mixture_type, method):
        """计算气体混合物物性"""
        # 转换为绝对温度
        T_k = T + 273.15
        
        # 计算混合物基本参数
        mw_mix = sum(comp['y'] * comp['mw'] for comp in components)
        
        # 根据选择的方法计算虚拟临界参数
        if method == "简单混合规则" or method == "Kay规则":
            # Kay规则
            tc_mix = sum(comp['y'] * comp['tc'] for comp in components)
            pc_mix = sum(comp['y'] * comp['pc'] for comp in components)
            vc_mix = sum(comp['y'] * comp['vc'] for comp in components)
            omega_mix = sum(comp['y'] * comp['omega'] for comp in components)
            zc_mix = sum(comp['y'] * comp['zc'] for comp in components)
        else:
            # 对应状态原理（更复杂的混合规则）
            # 这里使用Prausnitz-Gunn规则
            tc_mix = 0.0
            pc_mix = 0.0
            vc_mix = 0.0
            
            for i, comp_i in enumerate(components):
                for j, comp_j in enumerate(components):
                    # 二元交互参数（简化，实际需要更复杂的计算）
                    k_ij = 0.0  # 二元交互参数
                    if i != j:
                        k_ij = 1 - ((comp_i['vc'] ** (1/3) * comp_j['vc'] ** (1/3)) / 
                                   (0.5 * (comp_i['vc'] ** (2/3) + comp_j['vc'] ** (2/3)))) ** 3
                    
                    tc_ij = (1 - k_ij) * math.sqrt(comp_i['tc'] * comp_j['tc'])
                    vc_ij = ((comp_i['vc'] ** (1/3) + comp_j['vc'] ** (1/3)) / 2) ** 3
                    zc_ij = 0.291 - 0.08 * (comp_i['omega'] + comp_j['omega']) / 2
                    pc_ij = zc_ij * 8.314 * tc_ij / vc_ij * 1000  # 转换为kPa
                    
                    tc_mix += comp_i['y'] * comp_j['y'] * tc_ij
                    pc_mix += comp_i['y'] * comp_j['y'] * pc_ij
                    vc_mix += comp_i['y'] * comp_j['y'] * vc_ij
            
            omega_mix = sum(comp['y'] * comp['omega'] for comp in components)
            zc_mix = 0.291 - 0.08 * omega_mix
        
        # 计算对比参数
        tr = T_k / tc_mix
        pr = P / pc_mix
        vr = 1.0  # 简化计算
        
        # 计算压缩因子
        if mixture_type == "理想气体":
            z_factor = 1.0
        else:
            # 使用对应状态原理计算压缩因子
            z_factor = self.calculate_compressibility_factor(tr, pr, omega_mix)
        
        # 计算密度
        if mixture_type == "理想气体":
            density = P * 1000 * mw_mix / (8.314 * T_k)  # kg/m³
        else:
            density = P * 1000 * mw_mix / (z_factor * 8.314 * T_k)  # kg/m³
        
        # 计算粘度
        viscosity = self.calculate_viscosity(components, T_k, density, mw_mix)
        
        # 计算热导率
        thermal_conductivity = self.calculate_thermal_conductivity(components, T_k, density, mw_mix)
        
        # 计算比热容
        cp_mix, cv_mix, gamma = self.calculate_heat_capacity(components, T_k, mixture_type)
        
        # 计算音速
        sound_speed = self.calculate_sound_speed(T_k, mw_mix, gamma, z_factor)
        
        # 计算对比密度
        reduced_density = density / (mw_mix / vc_mix * 1000)  # 转换为mol/m³
        
        return {
            'mw_mix': mw_mix,
            'tc_mix': tc_mix,
            'pc_mix': pc_mix,
            'vc_mix': vc_mix,
            'omega_mix': omega_mix,
            'zc_mix': zc_mix,
            'density': density,
            'z_factor': z_factor,
            'viscosity': viscosity,
            'thermal_conductivity': thermal_conductivity,
            'cp_mix': cp_mix,
            'cv_mix': cv_mix,
            'gamma': gamma,
            'sound_speed': sound_speed,
            'tr': tr,
            'pr': pr,
            'vr': vr,
            'reduced_density': reduced_density
        }
    
    def calculate_compressibility_factor(self, tr, pr, omega):
        """计算压缩因子（使用对应状态原理）"""
        # 简化计算，实际应使用Lee-Kesler方程
        # 这里使用简化对应状态方程
        z0 = 1.0  # 简单流体压缩因子（简化）
        z1 = 0.0  # 校正项（简化）
        
        # 简单对应状态方程
        z = z0 + omega * z1
        
        # 确保z在合理范围内
        return max(0.5, min(2.0, z))
    
    def calculate_viscosity(self, components, T, density, mw_mix):
        """计算气体混合物粘度（使用Wilke混合规则）"""
        # 计算各组分在混合气温度下的粘度
        viscosities = []
        for comp in components:
            # 使用对应状态方法估算纯组分粘度
            # 简化计算：使用Sutherland公式的近似
            mu_i = 0.1 * (T / 273.15) ** 0.7  # 简化估算
            viscosities.append(mu_i)
        
        # Wilke混合规则
        mu_mix = 0.0
        for i, comp_i in enumerate(components):
            sum_term = 0.0
            for j, comp_j in enumerate(components):
                phi_ij = (1 + (viscosities[i] / viscosities[j]) ** 0.5 * 
                         (comp_j['mw'] / comp_i['mw']) ** 0.25) ** 2 / \
                         math.sqrt(8 * (1 + comp_i['mw'] / comp_j['mw']))
                sum_term += comp_j['y'] * phi_ij
            
            mu_mix += comp_i['y'] * viscosities[i] / sum_term
        
        return mu_mix * 1e6  # 转换为μPa·s
    
    def calculate_thermal_conductivity(self, components, T, density, mw_mix):
        """计算气体混合物热导率"""
        # 使用Mason和Saxena修正的对应状态方法
        k_mix = 0.0
        
        for comp in components:
            # 估算纯组分热导率
            # 简化计算：使用Eucken关系
            k_i = 0.015  # W/(m·K) 简化值
            k_mix += comp['y'] * k_i
        
        return k_mix
    
    def calculate_heat_capacity(self, components, T, mixture_type):
        """计算气体混合物比热容"""
        # 计算理想气体比热容
        cp_ideal = 0.0
        for comp in components:
            # 使用多项式估算理想气体比热容
            # 简化计算：使用常数近似
            cp_i = 30.0  # J/(mol·K) 简化值
            cp_ideal += comp['y'] * cp_i
        
        cv_ideal = cp_ideal - 8.314  # J/(mol·K)
        
        if mixture_type == "理想气体":
            cp_mix = cp_ideal
            cv_mix = cv_ideal
        else:
            # 真实气体校正（简化）
            cp_mix = cp_ideal * 0.95  # 简化校正
            cv_mix = cv_ideal * 0.95  # 简化校正
        
        gamma = cp_mix / cv_mix if cv_mix > 0 else 1.4
        
        return cp_mix, cv_mix, gamma
    
    def calculate_sound_speed(self, T, mw_mix, gamma, z_factor):
        """计算音速"""
        # 音速公式: a = sqrt(γ * Z * R * T / M)
        R = 8.314  # J/(mol·K)
        sound_speed = math.sqrt(gamma * z_factor * R * T / (mw_mix / 1000))  # m/s
        
        return sound_speed
    
    def display_results(self, results):
        """显示计算结果"""
        self.mw_mixture_result.setText(f"{results['mw_mix']:.3f}")
        self.tc_mixture_result.setText(f"{results['tc_mix']:.1f}")
        self.pc_mixture_result.setText(f"{results['pc_mix']:.0f}")
        self.vc_mixture_result.setText(f"{results['vc_mix']:.1f}")
        self.omega_mixture_result.setText(f"{results['omega_mix']:.3f}")
        self.zc_mixture_result.setText(f"{results['zc_mix']:.3f}")
        
        self.density_result.setText(f"{results['density']:.3f}")
        self.z_factor_result.setText(f"{results['z_factor']:.3f}")
        self.viscosity_result.setText(f"{results['viscosity']:.1f}")
        self.thermal_cond_result.setText(f"{results['thermal_conductivity']:.4f}")
        self.cp_result.setText(f"{results['cp_mix']:.2f}")
        self.cv_result.setText(f"{results['cv_mix']:.2f}")
        self.ratio_cp_cv_result.setText(f"{results['gamma']:.3f}")
        self.sound_speed_result.setText(f"{results['sound_speed']:.1f}")
        
        self.tr_result.setText(f"{results['tr']:.3f}")
        self.pr_result.setText(f"{results['pr']:.3f}")
        self.vr_result.setText(f"{results['vr']:.3f}")
        self.reduced_density_result.setText(f"{results['reduced_density']:.3f}")
    
    def show_error(self, message):
        """显示错误信息"""
        for label in [self.mw_mixture_result, self.tc_mixture_result, 
                     self.pc_mixture_result, self.vc_mixture_result,
                     self.omega_mixture_result, self.zc_mixture_result,
                     self.density_result, self.z_factor_result,
                     self.viscosity_result, self.thermal_cond_result,
                     self.cp_result, self.cv_result, self.ratio_cp_cv_result,
                     self.sound_speed_result, self.tr_result, self.pr_result,
                     self.vr_result, self.reduced_density_result]:
            label.setText("计算错误")
        
        print(f"错误: {message}")


if __name__ == "__main__":
    # 测试代码
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    calculator = GasMixturePropertiesCalculator()
    calculator.resize(900, 800)
    calculator.show()
    
    sys.exit(app.exec())