# [file name]: calculators/tank_weight_calculator.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                              QLabel, QLineEdit, QComboBox, QPushButton, 
                              QTextEdit, QTableWidget, QTableWidgetItem,
                              QHeaderView, QMessageBox, QTabWidget, QDoubleSpinBox,
                              QRadioButton, QButtonGroup, QCheckBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QDoubleValidator
import math

class TankWeightCalculator(QWidget):
    """罐体重量计算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("⚖️ 罐体重量计算")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 添加计算标签页
        self.calculation_tab = self.create_calculation_tab()
        self.tab_widget.addTab(self.calculation_tab, "📊 重量计算")
        
        # 添加材料库标签页
        self.material_tab = self.create_material_tab()
        self.tab_widget.addTab(self.material_tab, "📚 材料库")
        
        main_layout.addWidget(self.tab_widget)
    
    def create_calculation_tab(self):
        """创建计算标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 罐体类型选择
        type_group = QGroupBox("🏺 罐体类型")
        type_layout = QHBoxLayout(type_group)
        
        self.tank_type_group = QButtonGroup(self)
        
        self.vertical_tank_radio = QRadioButton("立式储罐")
        self.vertical_tank_radio.setChecked(True)
        self.tank_type_group.addButton(self.vertical_tank_radio)
        type_layout.addWidget(self.vertical_tank_radio)
        
        self.horizontal_tank_radio = QRadioButton("卧式储罐")
        self.tank_type_group.addButton(self.horizontal_tank_radio)
        type_layout.addWidget(self.horizontal_tank_radio)
        
        self.sphere_tank_radio = QRadioButton("球罐")
        self.tank_type_group.addButton(self.sphere_tank_radio)
        type_layout.addWidget(self.sphere_tank_radio)
        
        self.reactor_radio = QRadioButton("反应釜")
        self.tank_type_group.addButton(self.reactor_radio)
        type_layout.addWidget(self.reactor_radio)
        
        type_layout.addStretch()
        layout.addWidget(type_group)
        
        # 基本尺寸组
        dimension_group = QGroupBox("📏 基本尺寸")
        dimension_layout = QVBoxLayout(dimension_group)
        
        # 直径和高度
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("内直径 (mm):"))
        self.diameter_input = QDoubleSpinBox()
        self.diameter_input.setRange(100, 50000)
        self.diameter_input.setValue(2000)
        self.diameter_input.setSuffix(" mm")
        size_layout.addWidget(self.diameter_input)
        
        size_layout.addWidget(QLabel("高度/长度 (mm):"))
        self.height_input = QDoubleSpinBox()
        self.height_input.setRange(100, 50000)
        self.height_input.setValue(3000)
        self.height_input.setSuffix(" mm")
        size_layout.addWidget(self.height_input)
        
        size_layout.addWidget(QLabel("设计压力 (MPa):"))
        self.pressure_input = QDoubleSpinBox()
        self.pressure_input.setRange(0, 10)
        self.pressure_input.setValue(0.6)
        self.pressure_input.setSuffix(" MPa")
        size_layout.addWidget(self.pressure_input)
        
        dimension_layout.addLayout(size_layout)
        
        # 壁厚和封头
        thickness_layout = QHBoxLayout()
        thickness_layout.addWidget(QLabel("筒体壁厚 (mm):"))
        self.shell_thickness_input = QDoubleSpinBox()
        self.shell_thickness_input.setRange(1, 100)
        self.shell_thickness_input.setValue(8)
        self.shell_thickness_input.setSuffix(" mm")
        thickness_layout.addWidget(self.shell_thickness_input)
        
        thickness_layout.addWidget(QLabel("封头类型:"))
        self.head_type_combo = QComboBox()
        self.head_type_combo.addItems(["椭圆封头", "碟形封头", "半球封头", "平盖"])
        thickness_layout.addWidget(self.head_type_combo)
        
        thickness_layout.addWidget(QLabel("封头壁厚 (mm):"))
        self.head_thickness_input = QDoubleSpinBox()
        self.head_thickness_input.setRange(1, 100)
        self.head_thickness_input.setValue(10)
        self.head_thickness_input.setSuffix(" mm")
        thickness_layout.addWidget(self.head_thickness_input)
        
        dimension_layout.addLayout(thickness_layout)
        
        layout.addWidget(dimension_group)
        
        # 材料参数组
        material_group = QGroupBox("🔩 材料参数")
        material_layout = QVBoxLayout(material_group)
        
        # 材料选择
        material_select_layout = QHBoxLayout()
        material_select_layout.addWidget(QLabel("主体材料:"))
        self.material_combo = QComboBox()
        self.material_combo.addItems([
            "Q235B", "Q345R", "304不锈钢", "316L不锈钢", 
            "碳钢", "合金钢", "铝", "铜"
        ])
        material_select_layout.addWidget(self.material_combo)
        
        material_select_layout.addWidget(QLabel("材料密度 (kg/m³):"))
        self.density_input = QDoubleSpinBox()
        self.density_input.setRange(1000, 9000)
        self.density_input.setValue(7850)
        self.density_input.setSuffix(" kg/m³")
        material_select_layout.addWidget(self.density_input)
        
        material_select_layout.addWidget(QLabel("腐蚀余量 (mm):"))
        self.corrosion_input = QDoubleSpinBox()
        self.corrosion_input.setRange(0, 10)
        self.corrosion_input.setValue(1)
        self.corrosion_input.setSuffix(" mm")
        material_select_layout.addWidget(self.corrosion_input)
        
        material_layout.addLayout(material_select_layout)
        
        # 附件选项
        attachment_layout = QHBoxLayout()
        self.nozzle_check = QCheckBox("管口")
        self.nozzle_check.setChecked(True)
        attachment_layout.addWidget(self.nozzle_check)
        
        self.support_check = QCheckBox("支座")
        self.support_check.setChecked(True)
        attachment_layout.addWidget(self.support_check)
        
        self.ladder_check = QCheckBox("梯子平台")
        self.ladder_check.setChecked(True)
        attachment_layout.addWidget(self.ladder_check)
        
        self.internal_check = QCheckBox("内件")
        attachment_layout.addWidget(self.internal_check)
        
        attachment_layout.addStretch()
        
        material_layout.addLayout(attachment_layout)
        
        layout.addWidget(material_group)
        
        # 按钮组
        button_layout = QHBoxLayout()
        self.calculate_btn = QPushButton("🚀 计算罐体重量")
        self.calculate_btn.clicked.connect(self.calculate_tank_weight)
        self.calculate_btn.setStyleSheet("QPushButton { background-color: #27ae60; color: white; font-weight: bold; }")
        button_layout.addWidget(self.calculate_btn)
        
        self.auto_thickness_btn = QPushButton("🔧 自动计算壁厚")
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
        
        # 重量明细表
        detail_group = QGroupBox("📋 重量明细")
        detail_layout = QVBoxLayout(detail_group)
        
        self.detail_table = QTableWidget()
        self.detail_table.setColumnCount(3)
        self.detail_table.setHorizontalHeaderLabels(["部件", "重量 (kg)", "百分比 (%)"])
        detail_layout.addWidget(self.detail_table)
        
        layout.addWidget(detail_group)
        
        return tab
    
    def create_material_tab(self):
        """创建材料库标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 材料库说明
        info_label = QLabel("常用材料参数参考")
        info_label.setFont(QFont("Arial", 12, QFont.Bold))
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # 材料参数表
        material_table = QTableWidget()
        material_table.setColumnCount(5)
        material_table.setHorizontalHeaderLabels(["材料", "密度 (kg/m³)", "许用应力 (MPa)", "弹性模量 (GPa)", "适用范围"])
        
        material_data = [
            ["Q235B", "7850", "113", "206", "一般压力容器"],
            ["Q345R", "7850", "189", "206", "压力容器专用钢"],
            ["304不锈钢", "7930", "137", "193", "食品、化工"],
            ["316L不锈钢", "8000", "130", "193", "耐腐蚀设备"],
            ["碳钢", "7850", "125", "200", "一般结构"],
            ["合金钢", "7850", "210", "210", "高压设备"],
            ["铝", "2700", "40", "70", "轻型设备"],
            ["铜", "8960", "50", "110", "特殊用途"]
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
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        
        layout.addWidget(material_table)
        
        # 计算公式说明
        formula_group = QGroupBox("📐 计算公式")
        formula_layout = QVBoxLayout(formula_group)
        
        formula_text = QTextEdit()
        formula_text.setReadOnly(True)
        formula_text.setHtml("""
        <h3>罐体重量计算公式</h3>
        
        <h4>筒体重量</h4>
        <p>W<sub>shell</sub> = π × D × L × t × ρ</p>
        <p>其中：D-平均直径，L-长度，t-壁厚，ρ-密度</p>
        
        <h4>封头重量</h4>
        <p><b>椭圆封头：</b>W<sub>head</sub> ≈ 1.084 × D² × t × ρ × 10⁻⁶</p>
        <p><b>碟形封头：</b>W<sub>head</sub> ≈ 1.124 × D² × t × ρ × 10⁻⁶</p>
        <p><b>半球封头：</b>W<sub>head</sub> ≈ 1.571 × D² × t × ρ × 10⁻⁶</p>
        <p><b>平盖：</b>W<sub>head</sub> = π/4 × D² × t × ρ × 10⁻⁶</p>
        
        <h4>壁厚计算（简化）</h4>
        <p>t = (P × D) / (2 × [σ] × φ - P) + C</p>
        <p>其中：P-设计压力，D-内径，[σ]-许用应力，φ-焊接系数，C-腐蚀余量</p>
        
        <h4>附件重量估算</h4>
        <ul>
            <li>管口：5-50 kg/个（根据尺寸）</li>
            <li>支座：5-20% 主体重量</li>
            <li>梯子平台：3-10% 主体重量</li>
            <li>内件：10-30% 主体重量</li>
        </ul>
        """)
        formula_layout.addWidget(formula_text)
        
        layout.addWidget(formula_group)
        
        return tab
    
    def calculate_tank_weight(self):
        """计算罐体重量"""
        try:
            # 获取输入值
            tank_type = self.get_tank_type()
            diameter = self.diameter_input.value() / 1000  # 转换为米
            height = self.height_input.value() / 1000      # 转换为米
            pressure = self.pressure_input.value()
            shell_thickness = self.shell_thickness_input.value() / 1000  # 转换为米
            head_thickness = self.head_thickness_input.value() / 1000    # 转换为米
            head_type = self.head_type_combo.currentText()
            material = self.material_combo.currentText()
            density = self.density_input.value()
            corrosion = self.corrosion_input.value() / 1000  # 转换为米
            
            # 计算各部件重量
            shell_weight = self.calculate_shell_weight(diameter, height, shell_thickness, density, tank_type)
            head_weight = self.calculate_head_weight(diameter, head_thickness, density, head_type, tank_type)
            
            # 计算附件重量
            attachments_weight = self.calculate_attachments_weight(shell_weight + head_weight)
            
            # 总重量
            total_weight = shell_weight + head_weight + attachments_weight
            
            # 显示结果
            self.display_results(total_weight, shell_weight, head_weight, attachments_weight, tank_type)
            
            # 更新明细表
            self.update_detail_table(shell_weight, head_weight, attachments_weight, total_weight)
            
        except Exception as e:
            QMessageBox.warning(self, "计算错误", f"计算过程中发生错误: {str(e)}")
    
    def get_tank_type(self):
        """获取罐体类型"""
        if self.vertical_tank_radio.isChecked():
            return "vertical"
        elif self.horizontal_tank_radio.isChecked():
            return "horizontal"
        elif self.sphere_tank_radio.isChecked():
            return "sphere"
        else:  # reactor
            return "reactor"
    
    def calculate_shell_weight(self, diameter, height, thickness, density, tank_type):
        """计算筒体重量"""
        if tank_type == "sphere":
            # 球罐筒体（实际是球壳）
            surface_area = 4 * math.pi * (diameter/2 + thickness/2) ** 2
            weight = surface_area * thickness * density
        else:
            # 圆柱形筒体
            mean_diameter = diameter + thickness
            if tank_type == "horizontal":
                length = height  # 卧式罐的长度
            else:
                length = height  # 立式罐的高度
            
            surface_area = math.pi * mean_diameter * length
            weight = surface_area * thickness * density
        
        return weight
    
    def calculate_head_weight(self, diameter, thickness, density, head_type, tank_type):
        """计算封头重量"""
        if tank_type == "sphere":
            # 球罐没有单独的封头
            return 0
        
        # 计算单个封头重量
        if head_type == "椭圆封头":
            head_weight = 1.084 * (diameter ** 2) * thickness * density * 1e-6
        elif head_type == "碟形封头":
            head_weight = 1.124 * (diameter ** 2) * thickness * density * 1e-6
        elif head_type == "半球封头":
            head_weight = 1.571 * (diameter ** 2) * thickness * density * 1e-6
        else:  # 平盖
            head_weight = (math.pi / 4) * (diameter ** 2) * thickness * density * 1e-6
        
        # 根据罐体类型确定封头数量
        if tank_type in ["vertical", "reactor"]:
            return head_weight  # 立式罐通常只有一个封头（顶部）
        else:  # horizontal
            return 2 * head_weight  # 卧式罐有两个封头
    
    def calculate_attachments_weight(self, main_weight):
        """计算附件重量"""
        attachments_weight = 0
        
        # 管口重量
        if self.nozzle_check.isChecked():
            # 估算管口重量，根据罐体大小
            nozzle_count = 6  # 假设6个管口
            nozzle_weight = nozzle_count * 15  # 每个管口约15kg
            attachments_weight += nozzle_weight
        
        # 支座重量
        if self.support_check.isChecked():
            support_weight = main_weight * 0.08  # 支座约为主重的8%
            attachments_weight += support_weight
        
        # 梯子平台重量
        if self.ladder_check.isChecked():
            ladder_weight = main_weight * 0.05  # 梯子平台约为主重的5%
            attachments_weight += ladder_weight
        
        # 内件重量
        if self.internal_check.isChecked():
            internal_weight = main_weight * 0.15  # 内件约为主重的15%
            attachments_weight += internal_weight
        
        return attachments_weight
    
    def auto_calculate_thickness(self):
        """自动计算壁厚"""
        try:
            diameter = self.diameter_input.value()
            pressure = self.pressure_input.value()
            material = self.material_combo.currentText()
            corrosion = self.corrosion_input.value()
            
            # 获取材料许用应力
            material_stress = self.get_material_stress(material)
            
            # 焊接系数
            weld_efficiency = 0.85
            
            # 计算最小壁厚 (简化公式)
            min_thickness = (pressure * diameter) / (2 * material_stress * weld_efficiency - pressure) + corrosion
            
            # 考虑制造和刚度要求，取整并增加余量
            recommended_thickness = math.ceil(min_thickness + 1)
            
            # 设置壁厚值
            self.shell_thickness_input.setValue(recommended_thickness)
            self.head_thickness_input.setValue(recommended_thickness * 1.2)  # 封头壁厚通常比筒体厚
            
            QMessageBox.information(self, "壁厚计算", f"推荐壁厚: {recommended_thickness} mm\n封头壁厚: {recommended_thickness * 1.2:.1f} mm")
            
        except Exception as e:
            QMessageBox.warning(self, "计算错误", f"壁厚计算失败: {str(e)}")
    
    def get_material_stress(self, material):
        """获取材料许用应力"""
        stress_values = {
            "Q235B": 113,
            "Q345R": 189,
            "304不锈钢": 137,
            "316L不锈钢": 130,
            "碳钢": 125,
            "合金钢": 210,
            "铝": 40,
            "铜": 50
        }
        return stress_values.get(material, 100)
    
    def display_results(self, total_weight, shell_weight, head_weight, attachments_weight, tank_type):
        """显示计算结果"""
        tank_type_names = {
            "vertical": "立式储罐",
            "horizontal": "卧式储罐", 
            "sphere": "球罐",
            "reactor": "反应釜"
        }
        
        result_text = f"""
        <h3>⚖️ {tank_type_names.get(tank_type, '罐体')} 重量计算结果</h3>
        
        <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr style="background-color: #f8f9fa;">
            <td style="padding: 8px; font-weight: bold;">项目</td>
            <td style="padding: 8px;">重量 (kg)</td>
            <td style="padding: 8px;">说明</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">筒体重量</td>
            <td style="padding: 8px; color: #3498db; font-weight: bold;">{shell_weight:.1f}</td>
            <td style="padding: 8px;">主体结构重量</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">封头重量</td>
            <td style="padding: 8px; color: #3498db;">{head_weight:.1f}</td>
            <td style="padding: 8px;">{self.head_type_combo.currentText()}</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">附件重量</td>
            <td style="padding: 8px; color: #e67e22;">{attachments_weight:.1f}</td>
            <td style="padding: 8px;">管口、支座、梯子等</td>
        </tr>
        <tr style="background-color: #2ecc71; color: white;">
            <td style="padding: 8px; font-weight: bold;">总重量</td>
            <td style="padding: 8px; font-weight: bold; font-size: 16px;">{total_weight:.1f}</td>
            <td style="padding: 8px;">空罐重量（不含介质）</td>
        </tr>
        </table>
        
        <h4>📋 设计建议</h4>
        <ul>
            <li>总重量: <b>{total_weight:.1f} kg</b> (约 {total_weight/1000:.2f} 吨)</li>
            <li>主体材料: {self.material_combo.currentText()}</li>
            <li>建议考虑吊装和运输方案</li>
            <li>基础设计应考虑罐体重量和介质重量</li>
        </ul>
        
        <p><i>注：此重量为罐体空重，不包括介质、保温层等重量。</i></p>
        """
        
        self.result_text.setHtml(result_text)
    
    def update_detail_table(self, shell_weight, head_weight, attachments_weight, total_weight):
        """更新明细表"""
        detail_data = [
            ["筒体", f"{shell_weight:.1f}", f"{(shell_weight/total_weight)*100:.1f}"],
            ["封头", f"{head_weight:.1f}", f"{(head_weight/total_weight)*100:.1f}"],
        ]
        
        # 添加附件明细
        if self.nozzle_check.isChecked():
            nozzle_weight = 90  # 6个管口 * 15kg
            detail_data.append(["管口", f"{nozzle_weight:.1f}", f"{(nozzle_weight/total_weight)*100:.1f}"])
        
        if self.support_check.isChecked():
            support_weight = (shell_weight + head_weight) * 0.08
            detail_data.append(["支座", f"{support_weight:.1f}", f"{(support_weight/total_weight)*100:.1f}"])
        
        if self.ladder_check.isChecked():
            ladder_weight = (shell_weight + head_weight) * 0.05
            detail_data.append(["梯子平台", f"{ladder_weight:.1f}", f"{(ladder_weight/total_weight)*100:.1f}"])
        
        if self.internal_check.isChecked():
            internal_weight = (shell_weight + head_weight) * 0.15
            detail_data.append(["内件", f"{internal_weight:.1f}", f"{(internal_weight/total_weight)*100:.1f}"])
        
        detail_data.append(["<b>总计</b>", f"<b>{total_weight:.1f}</b>", "<b>100.0</b>"])
        
        self.detail_table.setRowCount(len(detail_data))
        for i, row_data in enumerate(detail_data):
            for j, data in enumerate(row_data):
                item = QTableWidgetItem(data)
                item.setTextAlignment(Qt.AlignCenter)
                if i == len(detail_data) - 1:  # 最后一行（总计）
                    item.setBackground(Qt.lightGray)
                self.detail_table.setItem(i, j, item)
        
        # 调整列宽
        header = self.detail_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
    
    def clear_inputs(self):
        """清空输入"""
        self.vertical_tank_radio.setChecked(True)
        self.diameter_input.setValue(2000)
        self.height_input.setValue(3000)
        self.pressure_input.setValue(0.6)
        self.shell_thickness_input.setValue(8)
        self.head_type_combo.setCurrentIndex(0)
        self.head_thickness_input.setValue(10)
        self.material_combo.setCurrentIndex(0)
        self.density_input.setValue(7850)
        self.corrosion_input.setValue(1)
        self.nozzle_check.setChecked(True)
        self.support_check.setChecked(True)
        self.ladder_check.setChecked(True)
        self.internal_check.setChecked(False)
        self.result_text.clear()
        self.detail_table.setRowCount(0)

if __name__ == "__main__":
    # 测试代码
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    widget = TankWeightCalculator()
    widget.resize(900, 700)
    widget.show()
    
    sys.exit(app.exec())