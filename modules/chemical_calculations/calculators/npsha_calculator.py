from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGroupBox, QTextEdit, QComboBox, QGridLayout, QMessageBox
)
from PySide6.QtGui import QFont, QDoubleValidator
from PySide6.QtCore import Qt


class NPSHaCalculator(QWidget):
    """离心泵NPSHa计算（左右布局优化版）"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置左右布局的NPSHa计算UI"""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 左侧：输入参数区域 (占2/3宽度)
        left_widget = QWidget()
        left_widget.setMaximumWidth(900)  # 限制最大宽度
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(15)
        
        # 说明文本
        description = QLabel(
            "计算离心泵的可用汽蚀余量(NPSHa)，评估泵的汽蚀性能。"
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 5px;")
        left_layout.addWidget(description)
        
        # 输入参数组 - 使用GridLayout实现整齐的布局
        input_group = QGroupBox("📥 输入参数")
        input_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """)
        
        # 使用GridLayout确保整齐排列
        input_layout = QGridLayout(input_group)
        input_layout.setVerticalSpacing(12)
        input_layout.setHorizontalSpacing(10)
        
        # 标签样式 - 右对齐
        label_style = """
            QLabel {
                font-weight: bold;
                padding-right: 10px;
            }
        """
        
        # 输入框和下拉菜单的固定宽度
        input_width = 400
        combo_width = 250
        
        row = 0
        
        # 大气压力
        atm_pressure_label = QLabel("大气压力 (kPa):")
        atm_pressure_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        atm_pressure_label.setStyleSheet(label_style)
        input_layout.addWidget(atm_pressure_label, row, 0)
        
        self.atm_pressure_input = QLineEdit()
        self.atm_pressure_input.setPlaceholderText("例如: 101.3 (标准大气压)")
        self.atm_pressure_input.setValidator(QDoubleValidator(80.0, 110.0, 6))
        self.atm_pressure_input.setFixedWidth(input_width)
        input_layout.addWidget(self.atm_pressure_input, row, 1)
        
        self.atm_pressure_combo = QComboBox()
        self.atm_pressure_combo.addItems([
            "101.3 kPa - 标准大气压",
            "98.1 kPa - 海拔300米",
            "95.0 kPa - 海拔500米", 
            "89.9 kPa - 海拔1000米",
            "自定义大气压力"
        ])
        self.atm_pressure_combo.setFixedWidth(combo_width)
        self.atm_pressure_combo.currentTextChanged.connect(self.on_atm_pressure_changed)
        input_layout.addWidget(self.atm_pressure_combo, row, 2)
        
        row += 1
        
        # 液体饱和蒸汽压
        vapor_pressure_label = QLabel("液体饱和蒸汽压 (kPa):")
        vapor_pressure_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        vapor_pressure_label.setStyleSheet(label_style)
        input_layout.addWidget(vapor_pressure_label, row, 0)
        
        self.vapor_pressure_input = QLineEdit()
        self.vapor_pressure_input.setPlaceholderText("例如: 2.34 (水在20°C)")
        self.vapor_pressure_input.setValidator(QDoubleValidator(0.1, 100.0, 6))
        self.vapor_pressure_input.setFixedWidth(input_width)
        input_layout.addWidget(self.vapor_pressure_input, row, 1)
        
        self.vapor_pressure_combo = QComboBox()
        self.vapor_pressure_combo.addItems([
            "0.61 kPa - 水在0°C",
            "1.23 kPa - 水在10°C",
            "2.34 kPa - 水在20°C",
            "4.24 kPa - 水在30°C",
            "7.38 kPa - 水在40°C",
            "12.34 kPa - 水在50°C",
            "19.92 kPa - 水在60°C",
            "31.19 kPa - 水在70°C",
            "47.39 kPa - 水在80°C",
            "70.14 kPa - 水在90°C",
            "101.33 kPa - 水在100°C",
            "自定义蒸汽压"
        ])
        self.vapor_pressure_combo.setFixedWidth(combo_width)
        self.vapor_pressure_combo.currentTextChanged.connect(self.on_vapor_pressure_changed)
        input_layout.addWidget(self.vapor_pressure_combo, row, 2)
        
        row += 1
        
        # 吸入液面高度
        static_head_label = QLabel("吸入液面高度 (m):")
        static_head_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        static_head_label.setStyleSheet(label_style)
        input_layout.addWidget(static_head_label, row, 0)
        
        self.static_head_input = QLineEdit()
        self.static_head_input.setPlaceholderText("正值为灌注，负值为抽吸")
        self.static_head_input.setValidator(QDoubleValidator(-20.0, 50.0, 6))
        self.static_head_input.setFixedWidth(input_width)
        input_layout.addWidget(self.static_head_input, row, 1)
        
        self.static_head_combo = QComboBox()
        self.static_head_combo.addItems([
            "正压头 - 灌注吸入",
            "负压头 - 抽吸吸入",
            "零压头 - 水平吸入"
        ])
        self.static_head_combo.setFixedWidth(combo_width)
        self.static_head_combo.currentTextChanged.connect(self.on_static_head_changed)
        input_layout.addWidget(self.static_head_combo, row, 2)
        
        row += 1
        
        # 吸入管路损失
        friction_loss_label = QLabel("吸入管路损失 (m):")
        friction_loss_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        friction_loss_label.setStyleSheet(label_style)
        input_layout.addWidget(friction_loss_label, row, 0)
        
        self.friction_loss_input = QLineEdit()
        self.friction_loss_input.setPlaceholderText("例如: 1.5")
        self.friction_loss_input.setValidator(QDoubleValidator(0.0, 20.0, 6))
        self.friction_loss_input.setFixedWidth(input_width)
        input_layout.addWidget(self.friction_loss_input, row, 1)
        
        self.friction_loss_combo = QComboBox()
        self.friction_loss_combo.addItems([
            "0.5-1.0 m - 短直管路",
            "1.0-2.0 m - 中等管路",
            "2.0-3.0 m - 长管路",
            "3.0-5.0 m - 复杂管路",
            "自定义管路损失"
        ])
        self.friction_loss_combo.setFixedWidth(combo_width)
        self.friction_loss_combo.currentTextChanged.connect(self.on_friction_loss_changed)
        input_layout.addWidget(self.friction_loss_combo, row, 2)
        
        row += 1
        
        # 液体密度
        density_label = QLabel("液体密度 (kg/m³):")
        density_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        density_label.setStyleSheet(label_style)
        input_layout.addWidget(density_label, row, 0)
        
        self.density_input = QLineEdit()
        self.density_input.setPlaceholderText("例如: 1000 (水)")
        self.density_input.setValidator(QDoubleValidator(500.0, 2000.0, 6))
        self.density_input.setFixedWidth(input_width)
        input_layout.addWidget(self.density_input, row, 1)
        
        self.density_combo = QComboBox()
        self.density_combo.addItems([
            "1000 kg/m³ - 水(20°C)",
            "998 kg/m³ - 水(25°C)",
            "983 kg/m³ - 水(60°C)",
            "789 kg/m³ - 乙醇",
            "719 kg/m³ - 汽油", 
            "1261 kg/m³ - 甘油",
            "1025 kg/m³ - 海水",
            "680 kg/m³ - 汽油(轻质)",
            "850 kg/m³ - 柴油",
            "自定义密度"
        ])
        self.density_combo.setFixedWidth(combo_width)
        self.density_combo.currentTextChanged.connect(self.on_density_changed)
        input_layout.addWidget(self.density_combo, row, 2)
        
        row += 1
        
        # NPSHr (可选)
        npshr_label = QLabel("泵必需汽蚀余量NPSHr (m):")
        npshr_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        npshr_label.setStyleSheet(label_style)
        input_layout.addWidget(npshr_label, row, 0)
        
        self.npshr_input = QLineEdit()
        self.npshr_input.setPlaceholderText("可选，来自泵性能曲线")
        self.npshr_input.setValidator(QDoubleValidator(0.1, 20.0, 6))
        self.npshr_input.setFixedWidth(input_width)
        input_layout.addWidget(self.npshr_input, row, 1)
        
        self.npshr_combo = QComboBox()
        self.npshr_combo.addItems([
            "1.0-2.0 m - 低NPSHr泵",
            "2.0-4.0 m - 标准泵",
            "4.0-6.0 m - 高NPSHr泵",
            "6.0-8.0 m - 特殊泵",
            "未知NPSHr"
        ])
        self.npshr_combo.setFixedWidth(combo_width)
        self.npshr_combo.currentTextChanged.connect(self.on_npshr_changed)
        input_layout.addWidget(self.npshr_combo, row, 2)
        
        left_layout.addWidget(input_group)
        
        # 计算按钮
        calculate_btn = QPushButton("🧮 计算NPSHa")
        calculate_btn.setFont(QFont("Arial", 12, QFont.Bold))
        calculate_btn.clicked.connect(self.calculate_npsha)
        calculate_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        calculate_btn.setMinimumHeight(50)
        left_layout.addWidget(calculate_btn)
        
        # 右侧：结果显示区域 (占1/3宽度)
        right_widget = QWidget()
        right_widget.setMinimumWidth(400)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)
        
        # 结果显示
        self.result_group = QGroupBox("📤 计算结果")
        self.result_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """)
        result_layout = QVBoxLayout(self.result_group)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ecf0f1;
                border-radius: 6px;
                padding: 8px;
                background-color: #f8f9fa;
                min-height: 500px;
            }
        """)
        result_layout.addWidget(self.result_text)
        
        right_layout.addWidget(self.result_group)
        
        # 将左右两部分添加到主布局
        main_layout.addWidget(left_widget, 2)  # 左侧占2/3
        main_layout.addWidget(right_widget, 1)  # 右侧占1/3
    
    def on_atm_pressure_changed(self, text):
        """处理大气压力选择变化"""
        if "自定义" in text:
            self.atm_pressure_input.setReadOnly(False)
            self.atm_pressure_input.setPlaceholderText("输入自定义大气压力")
            self.atm_pressure_input.clear()
        else:
            self.atm_pressure_input.setReadOnly(True)
            try:
                # 从文本中提取数字
                import re
                match = re.search(r'(\d+\.?\d*)', text)
                if match:
                    pressure_value = float(match.group(1))
                    self.atm_pressure_input.setText(f"{pressure_value:.1f}")
            except:
                pass
    
    def on_vapor_pressure_changed(self, text):
        """处理蒸汽压选择变化"""
        if "自定义" in text:
            self.vapor_pressure_input.setReadOnly(False)
            self.vapor_pressure_input.setPlaceholderText("输入自定义蒸汽压")
            self.vapor_pressure_input.clear()
        else:
            self.vapor_pressure_input.setReadOnly(True)
            try:
                # 从文本中提取数字
                import re
                match = re.search(r'(\d+\.?\d*)', text)
                if match:
                    vapor_value = float(match.group(1))
                    self.vapor_pressure_input.setText(f"{vapor_value:.2f}")
            except:
                pass
    
    def on_static_head_changed(self, text):
        """处理静压头选择变化"""
        if "正压头" in text:
            self.static_head_input.setPlaceholderText("正值为灌注")
        elif "负压头" in text:
            self.static_head_input.setPlaceholderText("负值为抽吸")
        else:
            self.static_head_input.setPlaceholderText("零压头")
    
    def on_friction_loss_changed(self, text):
        """处理管路损失选择变化"""
        if "自定义" in text:
            self.friction_loss_input.setReadOnly(False)
            self.friction_loss_input.setPlaceholderText("输入自定义管路损失")
            self.friction_loss_input.clear()
        else:
            self.friction_loss_input.setReadOnly(True)
            try:
                # 从文本中提取数字范围
                import re
                match = re.search(r'(\d+\.?\d*)-(\d+\.?\d*)', text)
                if match:
                    min_val = float(match.group(1))
                    max_val = float(match.group(2))
                    avg_val = (min_val + max_val) / 2
                    self.friction_loss_input.setText(f"{avg_val:.1f}")
            except:
                pass
    
    def on_density_changed(self, text):
        """处理密度选择变化"""
        if "自定义" in text:
            self.density_input.setReadOnly(False)
            self.density_input.setPlaceholderText("输入自定义密度")
            self.density_input.clear()
        else:
            self.density_input.setReadOnly(True)
            try:
                # 从文本中提取数字
                import re
                match = re.search(r'(\d+\.?\d*)', text)
                if match:
                    density_value = float(match.group(1))
                    self.density_input.setText(f"{density_value:.0f}")
            except:
                pass
    
    def on_npshr_changed(self, text):
        """处理NPSHr选择变化"""
        if "未知" in text:
            self.npshr_input.clear()
            self.npshr_input.setPlaceholderText("不输入NPSHr")
        else:
            try:
                # 从文本中提取数字范围
                import re
                match = re.search(r'(\d+\.?\d*)-(\d+\.?\d*)', text)
                if match:
                    min_val = float(match.group(1))
                    max_val = float(match.group(2))
                    avg_val = (min_val + max_val) / 2
                    self.npshr_input.setText(f"{avg_val:.1f}")
            except:
                pass
    
    def calculate_npsha(self):
        """计算NPSHa"""
        try:
            # 获取输入值
            atm_pressure = float(self.atm_pressure_input.text() or 0)
            vapor_pressure = float(self.vapor_pressure_input.text() or 0)
            static_head = float(self.static_head_input.text() or 0)
            friction_loss = float(self.friction_loss_input.text() or 0)
            density = float(self.density_input.text() or 0)
            npshr = self.npshr_input.text()
            npshr_value = float(npshr) if npshr else None
            
            # 验证输入
            if not all([atm_pressure, vapor_pressure, static_head is not None, friction_loss, density]):
                QMessageBox.warning(self, "输入错误", "请填写所有必需参数")
                return
            
            # 计算NPSHa
            # NPSHa = (大气压头 + 静压头) - 蒸汽压头 - 损失压头
            # 压头 = 压力 / (密度 * 重力加速度)
            g = 9.81  # m/s²
            
            atm_head = (atm_pressure * 1000) / (density * g)  # 转换为Pa后计算压头
            vapor_head = (vapor_pressure * 1000) / (density * g)
            
            npsha = atm_head + static_head - vapor_head - friction_loss
            
            # 显示结果 - 使用格式化的输出
            result = f"""═══════════════════════════════════════════════════
                        📋 输入参数
═══════════════════════════════════════════════════

• 大气压力: {atm_pressure} kPa
• 液体饱和蒸汽压: {vapor_pressure} kPa
• 吸入液面高度: {static_head} m
• 吸入管路损失: {friction_loss} m
• 液体密度: {density} kg/m³
{f"• 泵必需汽蚀余量 NPSHr: {npshr_value} m" if npshr_value else "• 泵必需汽蚀余量 NPSHr: 未指定"}

═══════════════════════════════════════════════════
                        📊 计算结果
═══════════════════════════════════════════════════

中间计算:
• 大气压头: {atm_head:.3f} m
• 蒸汽压头: {vapor_head:.3f} m

最终结果:
• 可用汽蚀余量 NPSHa = {npsha:.3f} m

汽蚀余量分析:"""
            
            if npshr_value:
                safety_margin = npsha - npshr_value
                result += f"""
• 泵必需汽蚀余量 NPSHr: {npshr_value} m
• 安全余量: {safety_margin:.3f} m

安全评估:"""
                
                if safety_margin >= 1.0:
                    result += "\n✅ 优秀 - 汽蚀余量非常充足，泵运行安全"
                elif safety_margin >= 0.5:
                    result += "\n✅ 良好 - 汽蚀余量充足，泵运行安全"
                elif safety_margin >= 0.3:
                    result += "\n⚠️ 注意 - 汽蚀余量基本满足，建议监控"
                elif safety_margin >= 0:
                    result += "\n⚠️ 警告 - 汽蚀余量刚好满足，风险较高"
                else:
                    result += "\n❌ 危险 - 汽蚀余量不足，可能发生汽蚀"
                    
                result += f"\n• NPSHa/NPSHr 比值: {npsha/npshr_value:.2f}"
            else:
                result += """
注意: 未输入NPSHr值，无法进行安全性评估。
请参考泵的性能曲线获取NPSHr值。

一般要求:
• NPSHa ≥ NPSHr + 0.5 m (最小安全余量)
• NPSHa ≥ NPSHr + 1.0 m (推荐安全余量)
• 对于易汽化液体，建议更大的安全余量"""

            result += f"""

═══════════════════════════════════════════════════
                        🧮 计算公式
═══════════════════════════════════════════════════

NPSHa = (P_atm / (ρ·g)) + H_static - (P_vapor / (ρ·g)) - H_friction

其中:
P_atm = {atm_pressure} kPa (大气压力)
P_vapor = {vapor_pressure} kPa (饱和蒸汽压)
ρ = {density} kg/m³ (液体密度)
g = 9.81 m/s² (重力加速度)
H_static = {static_head} m (静压头)
H_friction = {friction_loss} m (摩擦损失)

详细计算:
({atm_pressure}×1000 / ({density}×9.81)) + {static_head} - ({vapor_pressure}×1000 / ({density}×9.81)) - {friction_loss}
= {atm_head:.3f} + {static_head} - {vapor_head:.3f} - {friction_loss}
= {npsha:.3f} m

═══════════════════════════════════════════════════
                        💡 应用说明
═══════════════════════════════════════════════════

• NPSHa必须大于NPSHr才能避免汽蚀
• 汽蚀会导致泵性能下降、振动和损坏
• 计算结果仅供参考，实际应用请考虑安全系数
• 对于高温液体，饱和蒸汽压对NPSHa影响显著"""
            
            self.result_text.setText(result)
            
        except ValueError as e:
            QMessageBox.critical(self, "计算错误", f"参数输入格式错误: {str(e)}")
        except ZeroDivisionError:
            QMessageBox.critical(self, "计算错误", "密度不能为零")
        except Exception as e:
            QMessageBox.critical(self, "计算错误", f"计算过程中发生错误: {str(e)}")