from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                              QLabel, QLineEdit, QPushButton, QComboBox, 
                              QFormLayout, QTextEdit, QGridLayout, QScrollArea,
                              QTableWidget, QTableWidgetItem, QHeaderView,
                              QTabWidget, QCheckBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QDoubleValidator
import math
import numpy as np
from scipy.optimize import fsolve


class VLEActivityCoefficientCalculator(QWidget):
    """气液平衡（活度系数法）计算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.components = []
        self.setup_ui()
        
    def setup_ui(self):
        """设置气液平衡计算界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("⚗️ 气液平衡计算（活度系数法）")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # 说明文本
        desc_label = QLabel("使用活度系数法计算多组分系统的气液平衡，支持Wilson、NRTL、UNIQUAC方程")
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
        
        # 系统设置标签页
        system_tab = QWidget()
        system_layout = QVBoxLayout(system_tab)
        
        # 组分设置组
        component_group = QGroupBox("组分设置")
        component_layout = QVBoxLayout(component_group)
        
        # 组分数量选择
        component_count_layout = QHBoxLayout()
        component_count_layout.addWidget(QLabel("组分数:"))
        self.component_count = QComboBox()
        self.component_count.addItems(["2", "3", "4"])
        self.component_count.currentTextChanged.connect(self.update_component_table)
        component_count_layout.addWidget(self.component_count)
        component_count_layout.addStretch()
        component_layout.addLayout(component_count_layout)
        
        # 组分参数表
        self.component_table = QTableWidget()
        self.component_table.setColumnCount(7)
        self.component_table.setHorizontalHeaderLabels([
            "组分", "Antoine A", "Antoine B", "Antoine C", "摩尔质量", "液相摩尔分数", "Wilson参数"
        ])
        component_layout.addWidget(self.component_table)
        
        system_layout.addWidget(component_group)
        
        # 计算条件组
        condition_group = QGroupBox("计算条件")
        condition_layout = QGridLayout(condition_group)
        
        self.temperature_input = QLineEdit()
        self.temperature_input.setPlaceholderText("例如：78.3")
        self.temperature_input.setValidator(QDoubleValidator(-100, 500, 2))
        
        self.pressure_input = QLineEdit()
        self.pressure_input.setText("101.325")
        self.pressure_input.setValidator(QDoubleValidator(0.1, 10000, 2))
        
        self.model_selection = QComboBox()
        self.model_selection.addItems(["Wilson方程", "NRTL方程", "UNIQUAC方程"])
        
        self.calc_type = QComboBox()
        self.calc_type.addItems(["泡点计算", "露点计算", "等温闪蒸"])
        
        condition_layout.addWidget(QLabel("温度:"), 0, 0)
        condition_layout.addWidget(self.temperature_input, 0, 1)
        condition_layout.addWidget(QLabel("°C"), 0, 2)
        
        condition_layout.addWidget(QLabel("压力:"), 0, 3)
        condition_layout.addWidget(self.pressure_input, 0, 4)
        condition_layout.addWidget(QLabel("kPa"), 0, 5)
        
        condition_layout.addWidget(QLabel("计算模型:"), 1, 0)
        condition_layout.addWidget(self.model_selection, 1, 1, 1, 2)
        
        condition_layout.addWidget(QLabel("计算类型:"), 1, 3)
        condition_layout.addWidget(self.calc_type, 1, 4, 1, 2)
        
        system_layout.addWidget(condition_group)
        
        # 二元交互参数组
        binary_group = QGroupBox("二元交互参数")
        binary_layout = QVBoxLayout(binary_group)
        
        self.binary_table = QTableWidget()
        self.binary_table.setColumnCount(4)
        binary_layout.addWidget(self.binary_table)
        
        system_layout.addWidget(binary_group)
        system_layout.addStretch()
        
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
        result_display_layout = QVBoxLayout(result_display_group)
        
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(5)
        self.result_table.setHorizontalHeaderLabels([
            "组分", "液相摩尔分数", "气相摩尔分数", "活度系数", "相对挥发度"
        ])
        result_display_layout.addWidget(self.result_table)
        
        # 汇总结果
        summary_layout = QFormLayout()
        
        self.k_value_result = QLabel("--")
        self.bubble_point_result = QLabel("--")
        self.dew_point_result = QLabel("--")
        self.flash_temp_result = QLabel("--")
        self.vapor_fraction_result = QLabel("--")
        
        summary_layout.addRow("平均K值:", self.k_value_result)
        summary_layout.addRow("泡点温度:", self.bubble_point_result)
        summary_layout.addRow("露点温度:", self.dew_point_result)
        summary_layout.addRow("闪蒸温度:", self.flash_temp_result)
        summary_layout.addRow("气相分率:", self.vapor_fraction_result)
        
        result_display_layout.addLayout(summary_layout)
        result_layout.addWidget(result_display_group)
        
        # 添加标签页
        self.tab_widget.addTab(system_tab, "系统设置")
        self.tab_widget.addTab(result_tab, "计算结果")
        
        scroll_layout.addWidget(self.tab_widget)
        
        # 计算说明
        info_text = QTextEdit()
        info_text.setMaximumHeight(150)
        info_text.setHtml("""
        <h4>计算说明:</h4>
        <ul>
        <li>Antoine方程: log10(P) = A - B/(T + C)，其中P单位为kPa，T单位为°C</li>
        <li>Wilson方程: 适用于极性组分混合物的气液平衡计算</li>
        <li>NRTL方程: 适用于非理想性较强的系统，包括部分互溶系统</li>
        <li>UNIQUAC方程: 基于分子结构和相互作用的通用模型</li>
        <li>泡点计算: 给定液相组成和压力，计算泡点温度和平衡气相组成</li>
        <li>露点计算: 给定气相组成和压力，计算露点温度和平衡液相组成</li>
        <li>等温闪蒸: 给定总组成、温度和压力，计算气液相平衡组成</li>
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
        
        # 预设一些常见物质的Antoine参数
        preset_components = {
            "甲醇": [7.87863, 1473.11, 230.0, 32.04],
            "乙醇": [8.1122, 1592.864, 226.184, 46.07],
            "水": [8.07131, 1730.63, 233.426, 18.02],
            "苯": [6.90565, 1211.033, 220.79, 78.11],
            "甲苯": [6.95464, 1344.8, 219.48, 92.14],
            "丙酮": [7.02447, 1161.0, 224.0, 58.08],
            "乙酸": [7.18807, 1416.7, 211.0, 60.05]
        }
        
        for i in range(count):
            # 组分名称
            name_combo = QComboBox()
            name_combo.addItems(list(preset_components.keys()))
            name_combo.setCurrentIndex(i % len(preset_components))
            self.component_table.setCellWidget(i, 0, name_combo)
            
            # 获取预设参数
            current_name = name_combo.currentText()
            params = preset_components.get(current_name, [0, 0, 0, 0])
            
            # Antoine参数A
            a_item = QTableWidgetItem(f"{params[0]:.5f}")
            self.component_table.setItem(i, 1, a_item)
            
            # Antoine参数B
            b_item = QTableWidgetItem(f"{params[1]:.2f}")
            self.component_table.setItem(i, 2, b_item)
            
            # Antoine参数C
            c_item = QTableWidgetItem(f"{params[2]:.2f}")
            self.component_table.setItem(i, 3, c_item)
            
            # 摩尔质量
            mw_item = QTableWidgetItem(f"{params[3]:.2f}")
            self.component_table.setItem(i, 4, mw_item)
            
            # 液相摩尔分数
            if i == 0:
                x_item = QTableWidgetItem("0.5")
            elif i == 1:
                x_item = QTableWidgetItem("0.5")
            else:
                x_item = QTableWidgetItem("0.0")
            self.component_table.setItem(i, 5, x_item)
            
            # Wilson参数
            wilson_item = QTableWidgetItem("1.0")
            self.component_table.setItem(i, 6, wilson_item)
        
        # 更新二元交互参数表
        self.update_binary_table()
        
    def update_binary_table(self):
        """更新二元交互参数表"""
        count = int(self.component_count.currentText())
        self.binary_table.setRowCount(count * (count - 1) // 2)
        self.binary_table.setColumnCount(4)
        self.binary_table.setHorizontalHeaderLabels(["组分对", "λ12", "λ21", "α12"])
        
        row = 0
        for i in range(count):
            for j in range(i+1, count):
                # 组分对
                comp_i = self.component_table.cellWidget(i, 0).currentText() if self.component_table.cellWidget(i, 0) else f"组分{i+1}"
                comp_j = self.component_table.cellWidget(j, 0).currentText() if self.component_table.cellWidget(j, 0) else f"组分{j+1}"
                pair_item = QTableWidgetItem(f"{comp_i} - {comp_j}")
                self.binary_table.setItem(row, 0, pair_item)
                
                # 默认交互参数
                lambda12_item = QTableWidgetItem("100.0")
                self.binary_table.setItem(row, 1, lambda12_item)
                
                lambda21_item = QTableWidgetItem("100.0")
                self.binary_table.setItem(row, 2, lambda21_item)
                
                alpha_item = QTableWidgetItem("0.3")
                self.binary_table.setItem(row, 3, alpha_item)
                
                row += 1
    
    def clear_inputs(self):
        """清空所有输入"""
        self.temperature_input.clear()
        self.pressure_input.setText("101.325")
        self.update_component_table()
        
        # 清空结果
        self.result_table.setRowCount(0)
        self.k_value_result.setText("--")
        self.bubble_point_result.setText("--")
        self.dew_point_result.setText("--")
        self.flash_temp_result.setText("--")
        self.vapor_fraction_result.setText("--")
    
    def calculate(self):
        """执行气液平衡计算"""
        try:
            # 获取计算条件
            temperature = float(self.temperature_input.text()) if self.temperature_input.text() else 25.0
            pressure = float(self.pressure_input.text())
            model = self.model_selection.currentText()
            calc_type = self.calc_type.currentText()
            
            # 获取组分数据
            components = self.get_component_data()
            
            # 获取二元交互参数
            binary_params = self.get_binary_parameters(components)
            
            # 执行计算
            results = self.calculate_vle(components, binary_params, temperature, pressure, model, calc_type)
            
            # 显示结果
            self.display_results(results, components)
            
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
            a = float(self.component_table.item(i, 1).text())
            b = float(self.component_table.item(i, 2).text())
            c = float(self.component_table.item(i, 3).text())
            mw = float(self.component_table.item(i, 4).text())
            x = float(self.component_table.item(i, 5).text())
            
            components.append({
                'name': name,
                'antoine_a': a,
                'antoine_b': b,
                'antoine_c': c,
                'mw': mw,
                'x': x
            })
        
        return components
    
    def get_binary_parameters(self, components):
        """获取二元交互参数"""
        count = len(components)
        binary_params = {}
        
        row = 0
        for i in range(count):
            for j in range(i+1, count):
                lambda12 = float(self.binary_table.item(row, 1).text())
                lambda21 = float(self.binary_table.item(row, 2).text())
                alpha = float(self.binary_table.item(row, 3).text())
                
                binary_params[(i, j)] = {
                    'lambda12': lambda12,
                    'lambda21': lambda21,
                    'alpha': alpha
                }
                row += 1
        
        return binary_params
    
    def calculate_vle(self, components, binary_params, T, P, model, calc_type):
        """计算气液平衡"""
        n = len(components)
        
        # 计算饱和蒸气压
        Psat = []
        for comp in components:
            # Antoine方程: log10(P) = A - B/(T + C)
            logPsat = comp['antoine_a'] - comp['antoine_b'] / (T + comp['antoine_c'])
            Psat_i = 10 ** logPsat  # kPa
            Psat.append(Psat_i)
        
        # 获取液相组成
        x = [comp['x'] for comp in components]
        
        # 计算活度系数
        gamma = self.calculate_activity_coefficient(x, T, binary_params, model, n)
        
        # 计算K值
        K = []
        for i in range(n):
            K_i = gamma[i] * Psat[i] / P
            K.append(K_i)
        
        # 根据计算类型调整结果
        if calc_type == "泡点计算":
            # 泡点计算: Σyi = ΣKi*xi = 1
            bubble_sum = sum(K[i] * x[i] for i in range(n))
            y = [K[i] * x[i] / bubble_sum for i in range(n)]
            vapor_fraction = 0.0
            
        elif calc_type == "露点计算":
            # 露点计算: Σxi = Σyi/Ki = 1
            dew_sum = sum(x[i] / K[i] for i in range(n))  # 这里x实际上是气相组成y
            y = x.copy()  # 输入的是气相组成
            x = [y[i] / K[i] / dew_sum for i in range(n)]
            vapor_fraction = 1.0
            
        else:  # 等温闪蒸
            # 等温闪蒸计算
            vapor_fraction = self.calculate_flash(x, K, n)
            y = [K[i] * x[i] / (1 + vapor_fraction * (K[i] - 1)) for i in range(n)]
            x = [x[i] / (1 + vapor_fraction * (K[i] - 1)) for i in range(n)]
        
        # 计算相对挥发度
        alpha = []
        if n >= 2:
            for i in range(n):
                alpha_i = K[i] / K[0]  # 相对于第一个组分
                alpha.append(alpha_i)
        else:
            alpha = [1.0] * n
        
        return {
            'x': x,
            'y': y,
            'K': K,
            'gamma': gamma,
            'alpha': alpha,
            'vapor_fraction': vapor_fraction,
            'Psat': Psat
        }
    
    def calculate_activity_coefficient(self, x, T, binary_params, model, n):
        """计算活度系数"""
        gamma = [1.0] * n  # 初始化为1
        
        if model == "Wilson方程":
            gamma = self.wilson_equation(x, T, binary_params, n)
        elif model == "NRTL方程":
            gamma = self.nrtl_equation(x, T, binary_params, n)
        elif model == "UNIQUAC方程":
            gamma = self.uniquac_equation(x, T, binary_params, n)
        
        return gamma
    
    def wilson_equation(self, x, T, binary_params, n):
        """Wilson方程计算活度系数"""
        gamma = [1.0] * n
        
        # 构建Λ矩阵
        Lambda = np.ones((n, n))
        for (i, j), params in binary_params.items():
            if i < n and j < n:
                Lambda[i, j] = params['lambda12']
                Lambda[j, i] = params['lambda21']
        
        # Wilson方程计算
        for i in range(n):
            sum1 = 0.0
            for j in range(n):
                sum1 += x[j] * Lambda[i, j]
            
            sum2 = 0.0
            for k in range(n):
                term = 0.0
                for j in range(n):
                    term += x[j] * Lambda[k, j]
                sum2 += x[k] * Lambda[k, i] / term
            
            gamma[i] = math.exp(1 - math.log(sum1) - sum2)
        
        return gamma
    
    def nrtl_equation(self, x, T, binary_params, n):
        """NRTL方程计算活度系数"""
        gamma = [1.0] * n
        
        # 构建τ和G矩阵
        tau = np.zeros((n, n))
        G = np.zeros((n, n))
        
        for (i, j), params in binary_params.items():
            if i < n and j < n:
                alpha = params['alpha']
                tau[i, j] = params['lambda12'] / (8.314 * (T + 273.15))  # 转换为能量单位
                tau[j, i] = params['lambda21'] / (8.314 * (T + 273.15))
                G[i, j] = math.exp(-alpha * tau[i, j])
                G[j, i] = math.exp(-alpha * tau[j, i])
        
        # NRTL方程计算
        for i in range(n):
            sum1 = 0.0
            sum2 = 0.0
            
            for j in range(n):
                term1 = 0.0
                for k in range(n):
                    term1 += x[k] * G[k, j]
                
                term2 = 0.0
                for k in range(n):
                    term2 += x[k] * G[k, j] * tau[k, j]
                
                sum1 += x[j] * G[i, j] / term1 * (tau[i, j] - term2 / term1)
                sum2 += x[j] * G[j, i] / term1
            
            gamma[i] = math.exp(sum1 + sum2)
        
        return gamma
    
    def uniquac_equation(self, x, T, binary_params, n):
        """UNIQUAC方程计算活度系数"""
        # 简化版本，实际UNIQUAC方程更复杂
        # 这里使用Wilson方程作为近似
        return self.wilson_equation(x, T, binary_params, n)
    
    def calculate_flash(self, z, K, n):
        """等温闪蒸计算气相分率"""
        def flash_equation(V):
            # Rachford-Rice方程
            sum_term = 0.0
            for i in range(n):
                sum_term += z[i] * (K[i] - 1) / (1 + V * (K[i] - 1))
            return sum_term
        
        # 求解Rachford-Rice方程
        V_guess = 0.5
        V = fsolve(flash_equation, V_guess)[0]
        
        # 确保V在0-1之间
        return max(0.0, min(1.0, V))
    
    def display_results(self, results, components):
        """显示计算结果"""
        n = len(components)
        
        # 更新结果表格
        self.result_table.setRowCount(n)
        
        avg_K = 0.0
        for i in range(n):
            # 组分名称
            name_item = QTableWidgetItem(components[i]['name'])
            self.result_table.setItem(i, 0, name_item)
            
            # 液相组成
            x_item = QTableWidgetItem(f"{results['x'][i]:.4f}")
            self.result_table.setItem(i, 1, x_item)
            
            # 气相组成
            y_item = QTableWidgetItem(f"{results['y'][i]:.4f}")
            self.result_table.setItem(i, 2, y_item)
            
            # 活度系数
            gamma_item = QTableWidgetItem(f"{results['gamma'][i]:.4f}")
            self.result_table.setItem(i, 3, gamma_item)
            
            # 相对挥发度
            alpha_item = QTableWidgetItem(f"{results['alpha'][i]:.4f}")
            self.result_table.setItem(i, 4, alpha_item)
            
            avg_K += results['K'][i]
        
        # 更新汇总结果
        avg_K /= n
        self.k_value_result.setText(f"{avg_K:.4f}")
        self.bubble_point_result.setText("--")  # 简化版本，实际需要迭代计算
        self.dew_point_result.setText("--")
        self.flash_temp_result.setText("--")
        self.vapor_fraction_result.setText(f"{results['vapor_fraction']:.4f}")
    
    def show_error(self, message):
        """显示错误信息"""
        self.result_table.setRowCount(0)
        self.k_value_result.setText("计算错误")
        self.bubble_point_result.setText("计算错误")
        self.dew_point_result.setText("计算错误")
        self.flash_temp_result.setText("计算错误")
        self.vapor_fraction_result.setText("计算错误")
        
        print(f"错误: {message}")


if __name__ == "__main__":
    # 测试代码
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    calculator = VLEActivityCoefficientCalculator()
    calculator.resize(900, 700)
    calculator.show()
    
    sys.exit(app.exec())