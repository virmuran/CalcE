from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                              QLabel, QLineEdit, QPushButton, QComboBox, 
                              QFormLayout, QTextEdit, QGridLayout, QScrollArea,
                              QTableWidget, QTableWidgetItem, QHeaderView,
                              QTabWidget, QCheckBox, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QDoubleValidator
import math

# 检查 numpy 是否可用
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("警告: numpy 未安装，部分高级功能可能受限")


class EOSCalculator(QWidget):
    """状态方程计算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置状态方程计算界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("⚛️ 状态方程计算")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # 说明文本
        desc_label = QLabel("使用各种状态方程计算流体的热力学性质，包括PR、SRK、RK、理想气体等")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #7f8c8d; margin: 5px;")
        main_layout.addWidget(desc_label)
        
        # 如果 numpy 不可用，显示警告
        if not NUMPY_AVAILABLE:
            warning_label = QLabel("⚠️ 警告: numpy 库未安装，部分高级功能受限")
            warning_label.setStyleSheet("color: #e74c3c; font-weight: bold; padding: 10px; background-color: #ffeaa7; border-radius: 5px;")
            warning_label.setWordWrap(True)
            main_layout.addWidget(warning_label)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 物质参数标签页
        substance_tab = QWidget()
        substance_layout = QVBoxLayout(substance_tab)
        
        # 物质选择组
        substance_group = QGroupBox("物质参数")
        substance_layout_grid = QGridLayout(substance_group)
        
        self.substance_selection = QComboBox()
        self.substance_selection.addItems([
            "自定义", "甲烷", "乙烷", "丙烷", "正丁烷", "二氧化碳", 
            "氮气", "氢气", "水", "氩气", "氧气"
        ])
        self.substance_selection.currentTextChanged.connect(self.update_substance_parameters)
        
        self.tc_input = QLineEdit()
        self.tc_input.setPlaceholderText("例如：190.6")
        self.tc_input.setValidator(QDoubleValidator(1, 2000, 2))
        
        self.pc_input = QLineEdit()
        self.pc_input.setPlaceholderText("例如：4600")
        self.pc_input.setValidator(QDoubleValidator(100, 100000, 1))
        
        self.omega_input = QLineEdit()
        self.omega_input.setPlaceholderText("例如：0.008")
        self.omega_input.setValidator(QDoubleValidator(-1, 2, 4))
        
        self.mw_input = QLineEdit()
        self.mw_input.setPlaceholderText("例如：16.04")
        self.mw_input.setValidator(QDoubleValidator(1, 500, 3))
        
        self.zc_input = QLineEdit()
        self.zc_input.setPlaceholderText("例如：0.286")
        self.zc_input.setValidator(QDoubleValidator(0.1, 0.5, 3))
        
        substance_layout_grid.addWidget(QLabel("物质:"), 0, 0)
        substance_layout_grid.addWidget(self.substance_selection, 0, 1, 1, 2)
        
        substance_layout_grid.addWidget(QLabel("临界温度:"), 1, 0)
        substance_layout_grid.addWidget(self.tc_input, 1, 1)
        substance_layout_grid.addWidget(QLabel("K"), 1, 2)
        
        substance_layout_grid.addWidget(QLabel("临界压力:"), 1, 3)
        substance_layout_grid.addWidget(self.pc_input, 1, 4)
        substance_layout_grid.addWidget(QLabel("kPa"), 1, 5)
        
        substance_layout_grid.addWidget(QLabel("偏心因子:"), 2, 0)
        substance_layout_grid.addWidget(self.omega_input, 2, 1)
        substance_layout_grid.addWidget(QLabel(""), 2, 2)
        
        substance_layout_grid.addWidget(QLabel("分子量:"), 2, 3)
        substance_layout_grid.addWidget(self.mw_input, 2, 4)
        substance_layout_grid.addWidget(QLabel("g/mol"), 2, 5)
        
        substance_layout_grid.addWidget(QLabel("临界压缩因子:"), 3, 0)
        substance_layout_grid.addWidget(self.zc_input, 3, 1)
        substance_layout_grid.addWidget(QLabel(""), 3, 2)
        
        substance_layout.addWidget(substance_group)
        
        # 状态方程选择组
        eos_group = QGroupBox("状态方程选择")
        eos_layout = QGridLayout(eos_group)
        
        self.eos_type = QComboBox()
        self.eos_type.addItems([
            "理想气体方程", 
            "范德瓦尔斯方程", 
            "Redlich-Kwong方程"
        ])
        
        # 如果 numpy 可用，添加需要 numpy 的方程
        if NUMPY_AVAILABLE:
            self.eos_type.addItems([
                "Soave-Redlich-Kwong方程", 
                "Peng-Robinson方程"
            ])
        
        self.calculation_type = QComboBox()
        self.calculation_type.addItems([
            "P-V-T关系计算",
            "压缩因子计算", 
            "逸度系数计算",
            "剩余性质计算"
        ])
        
        eos_layout.addWidget(QLabel("状态方程:"), 0, 0)
        eos_layout.addWidget(self.eos_type, 0, 1, 1, 2)
        
        eos_layout.addWidget(QLabel("计算类型:"), 0, 3)
        eos_layout.addWidget(self.calculation_type, 0, 4, 1, 2)
        
        substance_layout.addWidget(eos_group)
        
        # 计算条件组
        condition_group = QGroupBox("计算条件")
        condition_layout = QGridLayout(condition_group)
        
        self.temperature_input = QLineEdit()
        self.temperature_input.setPlaceholderText("例如：298.15")
        self.temperature_input.setValidator(QDoubleValidator(1, 2000, 2))
        
        self.pressure_input = QLineEdit()
        self.pressure_input.setPlaceholderText("例如：101.325")
        self.pressure_input.setValidator(QDoubleValidator(0.1, 100000, 2))
        
        self.volume_input = QLineEdit()
        self.volume_input.setPlaceholderText("例如：0.024")
        self.volume_input.setValidator(QDoubleValidator(1e-6, 1000, 6))
        
        condition_layout.addWidget(QLabel("温度:"), 0, 0)
        condition_layout.addWidget(self.temperature_input, 0, 1)
        condition_layout.addWidget(QLabel("K"), 0, 2)
        
        condition_layout.addWidget(QLabel("压力:"), 0, 3)
        condition_layout.addWidget(self.pressure_input, 0, 4)
        condition_layout.addWidget(QLabel("kPa"), 0, 5)
        
        condition_layout.addWidget(QLabel("摩尔体积:"), 1, 0)
        condition_layout.addWidget(self.volume_input, 1, 1)
        condition_layout.addWidget(QLabel("m³/mol"), 1, 2)
        
        substance_layout.addWidget(condition_group)
        substance_layout.addStretch()
        
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
        
        # 基本结果
        basic_result_group = QGroupBox("基本热力学性质")
        basic_result_layout = QGridLayout(basic_result_group)
        
        self.z_factor_result = QLabel("--")
        self.density_result = QLabel("--")
        self.molar_volume_result = QLabel("--")
        self.fugacity_coeff_result = QLabel("--")
        self.fugacity_result = QLabel("--")
        
        basic_result_layout.addWidget(QLabel("压缩因子:"), 0, 0)
        basic_result_layout.addWidget(self.z_factor_result, 0, 1)
        basic_result_layout.addWidget(QLabel(""), 0, 2)
        
        basic_result_layout.addWidget(QLabel("密度:"), 0, 3)
        basic_result_layout.addWidget(self.density_result, 0, 4)
        basic_result_layout.addWidget(QLabel("kg/m³"), 0, 5)
        
        basic_result_layout.addWidget(QLabel("摩尔体积:"), 1, 0)
        basic_result_layout.addWidget(self.molar_volume_result, 1, 1)
        basic_result_layout.addWidget(QLabel("m³/mol"), 1, 2)
        
        basic_result_layout.addWidget(QLabel("逸度系数:"), 1, 3)
        basic_result_layout.addWidget(self.fugacity_coeff_result, 1, 4)
        basic_result_layout.addWidget(QLabel(""), 1, 5)
        
        basic_result_layout.addWidget(QLabel("逸度:"), 2, 0)
        basic_result_layout.addWidget(self.fugacity_result, 2, 1)
        basic_result_layout.addWidget(QLabel("kPa"), 2, 2)
        
        result_layout.addWidget(basic_result_group)
        
        # 剩余性质结果
        residual_group = QGroupBox("剩余性质")
        residual_layout = QGridLayout(residual_group)
        
        self.residual_enthalpy_result = QLabel("--")
        self.residual_entropy_result = QLabel("--")
        self.residual_gibbs_result = QLabel("--")
        
        residual_layout.addWidget(QLabel("剩余焓:"), 0, 0)
        residual_layout.addWidget(self.residual_enthalpy_result, 0, 1)
        residual_layout.addWidget(QLabel("J/mol"), 0, 2)
        
        residual_layout.addWidget(QLabel("剩余熵:"), 0, 3)
        residual_layout.addWidget(self.residual_entropy_result, 0, 4)
        residual_layout.addWidget(QLabel("J/(mol·K)"), 0, 5)
        
        residual_layout.addWidget(QLabel("剩余吉布斯自由能:"), 1, 0)
        residual_layout.addWidget(self.residual_gibbs_result, 1, 1)
        residual_layout.addWidget(QLabel("J/mol"), 1, 2)
        
        result_layout.addWidget(residual_group)
        
        # 对比状态参数
        reduced_group = QGroupBox("对比状态参数")
        reduced_layout = QGridLayout(reduced_group)
        
        self.reduced_temp_result = QLabel("--")
        self.reduced_pressure_result = QLabel("--")
        self.reduced_volume_result = QLabel("--")
        self.acentric_factor_result = QLabel("--")
        
        reduced_layout.addWidget(QLabel("对比温度:"), 0, 0)
        reduced_layout.addWidget(self.reduced_temp_result, 0, 1)
        reduced_layout.addWidget(QLabel(""), 0, 2)
        
        reduced_layout.addWidget(QLabel("对比压力:"), 0, 3)
        reduced_layout.addWidget(self.reduced_pressure_result, 0, 4)
        reduced_layout.addWidget(QLabel(""), 0, 5)
        
        reduced_layout.addWidget(QLabel("对比体积:"), 1, 0)
        reduced_layout.addWidget(self.reduced_volume_result, 1, 1)
        reduced_layout.addWidget(QLabel(""), 1, 2)
        
        reduced_layout.addWidget(QLabel("偏心因子:"), 1, 3)
        reduced_layout.addWidget(self.acentric_factor_result, 1, 4)
        reduced_layout.addWidget(QLabel(""), 1, 5)
        
        result_layout.addWidget(reduced_group)
        
        # 状态方程参数
        eos_params_group = QGroupBox("状态方程参数")
        eos_params_layout = QGridLayout(eos_params_group)
        
        self.a_parameter_result = QLabel("--")
        self.b_parameter_result = QLabel("--")
        self.alpha_parameter_result = QLabel("--")
        
        eos_params_layout.addWidget(QLabel("a参数:"), 0, 0)
        eos_params_layout.addWidget(self.a_parameter_result, 0, 1)
        eos_params_layout.addWidget(QLabel(""), 0, 2)
        
        eos_params_layout.addWidget(QLabel("b参数:"), 0, 3)
        eos_params_layout.addWidget(self.b_parameter_result, 0, 4)
        eos_params_layout.addWidget(QLabel(""), 0, 5)
        
        eos_params_layout.addWidget(QLabel("α参数:"), 1, 0)
        eos_params_layout.addWidget(self.alpha_parameter_result, 1, 1)
        eos_params_layout.addWidget(QLabel(""), 1, 2)
        
        result_layout.addWidget(eos_params_group)
        
        # 添加标签页
        self.tab_widget.addTab(substance_tab, "物质参数")
        self.tab_widget.addTab(result_tab, "计算结果")
        
        scroll_layout.addWidget(self.tab_widget)
        
        # 计算说明
        info_text = QTextEdit()
        info_text.setMaximumHeight(200)
        
        eos_info = """
        <h4>状态方程说明:</h4>
        <ul>
        <li><b>理想气体方程</b>: PV = RT，适用于低压高温条件</li>
        <li><b>范德瓦尔斯方程</b>: (P + a/V²)(V - b) = RT，考虑分子体积和分子间作用力</li>
        <li><b>Redlich-Kwong方程</b>: P = RT/(V-b) - a/√T/(V(V+b))，改进了温度依赖关系</li>
        """
        
        if NUMPY_AVAILABLE:
            eos_info += """
            <li><b>Soave-Redlich-Kwong方程</b>: P = RT/(V-b) - aα(T)/(V(V+b))，引入偏心因子改进精度</li>
            <li><b>Peng-Robinson方程</b>: P = RT/(V-b) - aα(T)/(V²+2bV-b²)，在临界区有更好表现</li>
            """
        else:
            eos_info += """
            <li><b>注意</b>: Soave-Redlich-Kwong和Peng-Robinson方程需要numpy库支持</li>
            """
            
        eos_info += """
        </ul>
        <p><b>剩余性质</b>: 真实气体与理想气体在相同T,P下的性质差异</p>
        <p><b>逸度</b>: 有效压力，用于真实气体的相平衡计算</p>
        """
        
        info_text.setHtml(eos_info)
        info_text.setReadOnly(True)
        scroll_layout.addWidget(info_text)
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # 初始化物质参数
        self.update_substance_parameters()
        
    def update_substance_parameters(self):
        """更新物质参数"""
        substance = self.substance_selection.currentText()
        
        if substance == "自定义":
            # 清空所有输入
            self.tc_input.clear()
            self.pc_input.clear()
            self.omega_input.clear()
            self.mw_input.clear()
            self.zc_input.clear()
        else:
            # 预设物质参数
            substance_params = self.get_substance_parameters(substance)
            self.tc_input.setText(f"{substance_params['tc']}")
            self.pc_input.setText(f"{substance_params['pc']}")
            self.omega_input.setText(f"{substance_params['omega']}")
            self.mw_input.setText(f"{substance_params['mw']}")
            self.zc_input.setText(f"{substance_params.get('zc', 0.27)}")
    
    def get_substance_parameters(self, substance):
        """获取物质参数"""
        params = {
            "甲烷": {"tc": 190.6, "pc": 4600, "omega": 0.008, "mw": 16.04, "zc": 0.286},
            "乙烷": {"tc": 305.3, "pc": 4880, "omega": 0.098, "mw": 30.07, "zc": 0.285},
            "丙烷": {"tc": 369.8, "pc": 4248, "omega": 0.152, "mw": 44.10, "zc": 0.281},
            "正丁烷": {"tc": 425.2, "pc": 3800, "omega": 0.193, "mw": 58.12, "zc": 0.274},
            "二氧化碳": {"tc": 304.2, "pc": 7377, "omega": 0.225, "mw": 44.01, "zc": 0.274},
            "氮气": {"tc": 126.2, "pc": 3390, "omega": 0.037, "mw": 28.01, "zc": 0.290},
            "氢气": {"tc": 33.2, "pc": 1315, "omega": -0.216, "mw": 2.016, "zc": 0.305},
            "水": {"tc": 647.3, "pc": 22064, "omega": 0.344, "mw": 18.02, "zc": 0.229},
            "氩气": {"tc": 150.9, "pc": 4898, "omega": -0.002, "mw": 39.95, "zc": 0.291},
            "氧气": {"tc": 154.6, "pc": 5043, "omega": 0.021, "mw": 32.00, "zc": 0.288}
        }
        
        return params.get(substance, {"tc": 0, "pc": 0, "omega": 0, "mw": 0, "zc": 0.27})
    
    def clear_inputs(self):
        """清空所有输入"""
        self.tc_input.clear()
        self.pc_input.clear()
        self.omega_input.clear()
        self.mw_input.clear()
        self.zc_input.clear()
        self.temperature_input.clear()
        self.pressure_input.clear()
        self.volume_input.clear()
        
        # 清空结果
        for label in [self.z_factor_result, self.density_result, 
                     self.molar_volume_result, self.fugacity_coeff_result,
                     self.fugacity_result, self.residual_enthalpy_result,
                     self.residual_entropy_result, self.residual_gibbs_result,
                     self.reduced_temp_result, self.reduced_pressure_result,
                     self.reduced_volume_result, self.acentric_factor_result,
                     self.a_parameter_result, self.b_parameter_result,
                     self.alpha_parameter_result]:
            label.setText("--")
    
    def calculate(self):
        """执行状态方程计算"""
        try:
            # 获取物质参数
            tc = float(self.tc_input.text())
            pc = float(self.pc_input.text())
            omega = float(self.omega_input.text())
            mw = float(self.mw_input.text())
            zc = float(self.zc_input.text()) if self.zc_input.text() else 0.27
            
            # 获取计算条件
            T = float(self.temperature_input.text())
            P = float(self.pressure_input.text())
            V_input = self.volume_input.text()
            V = float(V_input) if V_input else None
            
            # 获取状态方程类型
            eos_type = self.eos_type.currentText()
            
            # 检查是否需要 numpy 但不可用
            if eos_type in ["Soave-Redlich-Kwong方程", "Peng-Robinson方程"] and not NUMPY_AVAILABLE:
                QMessageBox.warning(self, "功能受限", 
                    f"{eos_type} 需要 numpy 库支持。\n\n请运行: pip install numpy")
                return
            
            # 计算对比参数
            Tr = T / tc
            Pr = P / pc
            
            # 执行计算
            results = self.calculate_eos_properties(
                eos_type, T, P, V, tc, pc, omega, mw, zc, Tr, Pr
            )
            
            # 显示结果
            self.display_results(results)
            
        except ValueError as e:
            self.show_error("输入参数格式错误，请检查输入值")
        except Exception as e:
            self.show_error(f"计算错误: {str(e)}")
    
    def calculate_eos_properties(self, eos_type, T, P, V, tc, pc, omega, mw, zc, Tr, Pr):
        """计算状态方程性质"""
        R = 8.314  # J/(mol·K)
        
        # 计算状态方程参数
        eos_params = self.calculate_eos_parameters(eos_type, tc, pc, omega, T, Tr)
        
        # 计算压缩因子
        if V is None:
            # 需要计算摩尔体积
            if eos_type == "理想气体方程":
                V = R * T / (P * 1000)  # 转换为m³/mol
                Z = 1.0
            else:
                # 使用状态方程求解摩尔体积
                Z = self.solve_eos(eos_type, eos_params, Tr, Pr)
                V = Z * R * T / (P * 1000)  # m³/mol
        else:
            # 使用输入的摩尔体积
            V_m3 = V  # m³/mol
            Z = P * 1000 * V_m3 / (R * T)
        
        # 计算密度
        density = mw / (V * 1000) if V else 0  # kg/m³
        
        # 计算逸度系数
        phi = self.calculate_fugacity_coefficient(eos_type, eos_params, Z, Tr, Pr)
        fugacity = phi * P  # kPa
        
        # 计算剩余性质
        residual_props = self.calculate_residual_properties(eos_type, eos_params, Z, Tr, Pr, T)
        
        # 计算对比体积
        Vr = V / (R * tc / (pc * 1000)) if V else 0
        
        return {
            'z_factor': Z,
            'density': density,
            'molar_volume': V,
            'fugacity_coeff': phi,
            'fugacity': fugacity,
            'residual_enthalpy': residual_props['enthalpy'],
            'residual_entropy': residual_props['entropy'],
            'residual_gibbs': residual_props['gibbs'],
            'reduced_temp': Tr,
            'reduced_pressure': Pr,
            'reduced_volume': Vr,
            'acentric_factor': omega,
            'a_parameter': eos_params.get('a', 0),
            'b_parameter': eos_params.get('b', 0),
            'alpha_parameter': eos_params.get('alpha', 0)
        }
    
    def calculate_eos_parameters(self, eos_type, tc, pc, omega, T, Tr):
        """计算状态方程参数"""
        R = 8.314  # J/(mol·K)
        
        if eos_type == "理想气体方程":
            return {}
        
        elif eos_type == "范德瓦尔斯方程":
            a = 27 * (R * tc) ** 2 / (64 * pc * 1000)
            b = R * tc / (8 * pc * 1000)
            return {'a': a, 'b': b}
        
        elif eos_type == "Redlich-Kwong方程":
            a = 0.42748 * (R * tc) ** 2 / (pc * 1000) / (tc ** 0.5)
            b = 0.08664 * R * tc / (pc * 1000)
            return {'a': a, 'b': b}
        
        elif eos_type == "Soave-Redlich-Kwong方程":
            # SRK方程
            a0 = 0.42748 * (R * tc) ** 2 / (pc * 1000)
            b = 0.08664 * R * tc / (pc * 1000)
            
            # Soave alpha函数
            m = 0.480 + 1.574 * omega - 0.176 * omega ** 2
            alpha = (1 + m * (1 - Tr ** 0.5)) ** 2
            a = a0 * alpha
            
            return {'a': a, 'b': b, 'alpha': alpha, 'm': m}
        
        elif eos_type == "Peng-Robinson方程":
            # PR方程
            a0 = 0.45724 * (R * tc) ** 2 / (pc * 1000)
            b = 0.07780 * R * tc / (pc * 1000)
            
            # PR alpha函数
            kappa = 0.37464 + 1.54226 * omega - 0.26992 * omega ** 2
            alpha = (1 + kappa * (1 - Tr ** 0.5)) ** 2
            a = a0 * alpha
            
            return {'a': a, 'b': b, 'alpha': alpha, 'kappa': kappa}
        
        else:
            return {}
    
    def solve_eos(self, eos_type, params, Tr, Pr):
        """求解状态方程的压缩因子"""
        R = 8.314
        
        if eos_type == "范德瓦尔斯方程":
            # 范德瓦尔斯方程: Z³ - (1+B)Z² + AZ - AB = 0
            A = params['a'] * Pr / (R * Tr) ** 2
            B = params['b'] * Pr / (R * Tr)
            
            # 使用迭代法求解三次方程
            return self.solve_cubic_equation_iterative(1, -(1 + B), A, -A*B)
        
        elif eos_type in ["Soave-Redlich-Kwong方程", "Peng-Robinson方程"] and NUMPY_AVAILABLE:
            # 使用 numpy 求解
            A = params['a'] * Pr / (R * Tr) ** 2
            B = params['b'] * Pr / (R * Tr)
            
            if eos_type == "Soave-Redlich-Kwong方程":
                # SRK方程: Z³ - Z² + (A - B - B²)Z - AB = 0
                coeffs = [1, -1, A - B - B**2, -A*B]
            else:  # Peng-Robinson方程
                # PR方程: Z³ - (1-B)Z² + (A-2B-3B²)Z - (AB-B²-B³) = 0
                coeffs = [1, -(1-B), A-2*B-3*B**2, -(A*B - B**2 - B**3)]
            
            roots = np.roots(coeffs)
            real_roots = [r for r in roots if np.isreal(r) and r > 0]
            return max(real_roots).real if real_roots else 1.0
        
        elif eos_type == "Redlich-Kwong方程":
            # 使用迭代法求解 RK 方程
            A = params['a'] * Pr / (R * Tr) ** 2
            B = params['b'] * Pr / (R * Tr)
            
            # RK方程: Z³ - Z² + (A - B - B²)Z - AB = 0 (与SRK形式相同)
            return self.solve_cubic_equation_iterative(1, -1, A - B - B**2, -A*B)
        
        else:
            return 1.0  # 默认值
    
    def solve_cubic_equation_iterative(self, a, b, c, d, max_iter=100, tol=1e-8):
        """使用迭代法求解三次方程 a*x³ + b*x² + c*x + d = 0"""
        # 初始猜测
        x = 1.0
        
        for i in range(max_iter):
            f = a*x**3 + b*x**2 + c*x + d
            f_prime = 3*a*x**2 + 2*b*x + c
            
            if abs(f_prime) < tol:
                break
                
            x_new = x - f / f_prime
            
            if abs(x_new - x) < tol:
                return x_new
                
            x = x_new
            
        return x
    
    def calculate_fugacity_coefficient(self, eos_type, params, Z, Tr, Pr):
        """计算逸度系数"""
        R = 8.314
        
        if eos_type == "理想气体方程":
            return 1.0
        
        elif eos_type == "Soave-Redlich-Kwong方程":
            A = params['a'] * Pr / (R * Tr) ** 2
            B = params['b'] * Pr / (R * Tr)
            
            ln_phi = Z - 1 - math.log(Z - B) - (A/B) * math.log(1 + B/Z)
            return math.exp(ln_phi)
        
        elif eos_type == "Peng-Robinson方程":
            A = params['a'] * Pr / (R * Tr) ** 2
            B = params['b'] * Pr / (R * Tr)
            
            ln_phi = Z - 1 - math.log(Z - B) - (A/(2*math.sqrt(2)*B)) * math.log((Z + (1+math.sqrt(2))*B)/(Z + (1-math.sqrt(2))*B))
            return math.exp(ln_phi)
        
        else:
            return 1.0  # 简化计算
    
    def calculate_residual_properties(self, eos_type, params, Z, Tr, Pr, T):
        """计算剩余性质"""
        R = 8.314
        
        if eos_type == "理想气体方程":
            return {'enthalpy': 0, 'entropy': 0, 'gibbs': 0}
        
        # 简化计算，实际应根据具体状态方程推导
        H_res = R * T * (1 - Z)  # 简化
        S_res = R * math.log(Z)  # 简化
        G_res = H_res - T * S_res
        
        return {
            'enthalpy': H_res,
            'entropy': S_res,
            'gibbs': G_res
        }
    
    def display_results(self, results):
        """显示计算结果"""
        self.z_factor_result.setText(f"{results['z_factor']:.4f}")
        self.density_result.setText(f"{results['density']:.3f}")
        self.molar_volume_result.setText(f"{results['molar_volume']:.6f}")
        self.fugacity_coeff_result.setText(f"{results['fugacity_coeff']:.4f}")
        self.fugacity_result.setText(f"{results['fugacity']:.3f}")
        
        self.residual_enthalpy_result.setText(f"{results['residual_enthalpy']:.2f}")
        self.residual_entropy_result.setText(f"{results['residual_entropy']:.4f}")
        self.residual_gibbs_result.setText(f"{results['residual_gibbs']:.2f}")
        
        self.reduced_temp_result.setText(f"{results['reduced_temp']:.3f}")
        self.reduced_pressure_result.setText(f"{results['reduced_pressure']:.3f}")
        self.reduced_volume_result.setText(f"{results['reduced_volume']:.3f}")
        self.acentric_factor_result.setText(f"{results['acentric_factor']:.4f}")
        
        self.a_parameter_result.setText(f"{results['a_parameter']:.4f}")
        self.b_parameter_result.setText(f"{results['b_parameter']:.6f}")
        self.alpha_parameter_result.setText(f"{results['alpha_parameter']:.4f}")
    
    def show_error(self, message):
        """显示错误信息"""
        QMessageBox.critical(self, "计算错误", message)
        
        for label in [self.z_factor_result, self.density_result, 
                     self.molar_volume_result, self.fugacity_coeff_result,
                     self.fugacity_result, self.residual_enthalpy_result,
                     self.residual_entropy_result, self.residual_gibbs_result,
                     self.reduced_temp_result, self.reduced_pressure_result,
                     self.reduced_volume_result, self.acentric_factor_result,
                     self.a_parameter_result, self.b_parameter_result,
                     self.alpha_parameter_result]:
            label.setText("计算错误")


if __name__ == "__main__":
    # 测试代码
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    calculator = EOSCalculator()
    calculator.resize(900, 800)
    calculator.show()
    
    sys.exit(app.exec())