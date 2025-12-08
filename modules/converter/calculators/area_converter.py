from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QScrollArea, QGridLayout, QFrame)
from PySide6.QtCore import Qt

class AreaConverter(QWidget):
    """面积单位换算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.unit_vars = {}
        self.setup_ui()
    
    def setup_ui(self):
        """设置面积换算器UI"""
        layout = QVBoxLayout(self)
        
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        scroll_layout.setSpacing(5)  # 减少行间距
        
        # 定义所有单位，分为两列
        units = [
            # 第一列单位
            ("平方公里 (km²)", "km2"), ("平方米 (m²)", "m2"), ("公顷 (ha)", "ha"), 
            ("公亩 (a)", "a"), ("平方分米 (dm²)", "dm2"), ("平方厘米 (cm²)", "cm2"), 
            ("平方毫米 (mm²)", "mm2"), ("平方微米 (μm²)", "um2"), ("平方英里 (mi²)", "mi2"),
            ("英亩 (ac)", "ac"), 
            
            # 第二列单位
            ("平方码 (yd²)", "yd2"), ("平方英尺 (ft²)", "ft2"), ("平方英寸 (in²)", "in2"), 
            ("平方竿 (rd²)", "rd2"), ("市顷", "qing"), ("市亩", "mu"), 
            ("平方尺", "chi2"), ("平方寸", "cun2")
        ]
        
        # 计算每列的单位数量
        first_column_count = 10
        second_column_count = 8
        
        # 添加第一列单位
        for i, (display_name, unit_code) in enumerate(units[:first_column_count]):
            unit_frame = QFrame()
            unit_frame.setFrameStyle(QFrame.NoFrame)
            unit_layout = QHBoxLayout(unit_frame)
            unit_layout.setContentsMargins(5, 2, 5, 2)  # 减少边距
            unit_layout.setSpacing(10)  # 减少标签和输入框之间的间距
            
            label = QLabel(display_name)
            label.setFixedWidth(120)  # 增加标签宽度以适应更长的名称
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            unit_layout.addWidget(label)
            
            entry = QLineEdit()
            entry.setFixedWidth(180)  # 增加输入框宽度
            entry.textChanged.connect(lambda text, u=unit_code: self.on_unit_input(text, u))
            unit_layout.addWidget(entry)
            
            self.unit_vars[unit_code] = entry
            scroll_layout.addWidget(unit_frame, i, 0)
        
        # 添加第二列单位
        for i, (display_name, unit_code) in enumerate(units[first_column_count:]):
            unit_frame = QFrame()
            unit_frame.setFrameStyle(QFrame.NoFrame)
            unit_layout = QHBoxLayout(unit_frame)
            unit_layout.setContentsMargins(5, 2, 5, 2)  # 减少边距
            unit_layout.setSpacing(10)  # 减少标签和输入框之间的间距
            
            label = QLabel(display_name)
            label.setFixedWidth(120)  # 增加标签宽度以适应更长的名称
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            unit_layout.addWidget(label)
            
            entry = QLineEdit()
            entry.setFixedWidth(180)  # 增加输入框宽度
            entry.textChanged.connect(lambda text, u=unit_code: self.on_unit_input(text, u))
            unit_layout.addWidget(entry)
            
            self.unit_vars[unit_code] = entry
            scroll_layout.addWidget(unit_frame, i, 1)
        
        # 设置列比例，使两列均匀分布
        scroll_layout.setColumnStretch(0, 1)
        scroll_layout.setColumnStretch(1, 1)
        scroll_layout.setHorizontalSpacing(15)  # 调整两列之间的间距
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
    
    def on_unit_input(self, text, source_unit):
        """处理单位输入"""
        try:
            source_value = text.strip()
            if not source_value:
                for unit_code, entry in self.unit_vars.items():
                    if unit_code != source_unit:
                        entry.blockSignals(True)
                        entry.setText("")
                        entry.blockSignals(False)
                return
            
            value = float(source_value)
            
            for unit_code, entry in self.unit_vars.items():
                if unit_code != source_unit:
                    result = self.do_conversion(value, source_unit, unit_code)
                    entry.blockSignals(True)
                    entry.setText(f"{result:.6g}")
                    entry.blockSignals(False)
                    
        except ValueError:
            pass
    
    def do_conversion(self, value, from_unit, to_unit):
        """执行面积换算"""
        # 先转换为平方米
        to_sqm = {
            # 国际单位制
            "km2": value * 1000000,      # 1平方公里 = 1,000,000平方米
            "m2": value,                 # 1平方米 = 1平方米
            "ha": value * 10000,         # 1公顷 = 10,000平方米
            "a": value * 100,            # 1公亩 = 100平方米
            "dm2": value * 0.01,         # 1平方分米 = 0.01平方米
            "cm2": value * 0.0001,       # 1平方厘米 = 0.0001平方米
            "mm2": value * 0.000001,     # 1平方毫米 = 0.000001平方米
            "um2": value * 0.000000000001, # 1平方微米 = 10^-12平方米
            
            # 英制单位
            "mi2": value * 2589988.110336, # 1平方英里 = 2,589,988.110336平方米
            "ac": value * 4046.8564224,    # 1英亩 = 4,046.8564224平方米
            "yd2": value * 0.83612736,     # 1平方码 = 0.83612736平方米
            "ft2": value * 0.09290304,     # 1平方英尺 = 0.09290304平方米
            "in2": value * 0.00064516,     # 1平方英寸 = 0.00064516平方米
            "rd2": value * 25.29285264,    # 1平方竿 = 25.29285264平方米
            
            # 中国市制单位
            "qing": value * 66666.6667,    # 1市顷 = 66,666.6667平方米
            "mu": value * 666.666667,      # 1市亩 = 666.666667平方米
            "chi2": value * 1/9,           # 1平方尺 = 1/9平方米 ≈ 0.111111平方米
            "cun2": value * 1/900          # 1平方寸 = 1/900平方米 ≈ 0.00111111平方米
        }
        
        # 从平方米转换为目标单位
        from_sqm = {
            # 国际单位制
            "km2": 0.000001,              # 1平方米 = 0.000001平方公里
            "m2": 1,                      # 1平方米 = 1平方米
            "ha": 0.0001,                 # 1平方米 = 0.0001公顷
            "a": 0.01,                    # 1平方米 = 0.01公亩
            "dm2": 100,                   # 1平方米 = 100平方分米
            "cm2": 10000,                 # 1平方米 = 10,000平方厘米
            "mm2": 1000000,               # 1平方米 = 1,000,000平方毫米
            "um2": 1000000000000,         # 1平方米 = 10^12平方微米
            
            # 英制单位
            "mi2": 1/2589988.110336,      # 1平方米 ≈ 0.000000386102平方英里
            "ac": 1/4046.8564224,         # 1平方米 ≈ 0.000247105英亩
            "yd2": 1/0.83612736,          # 1平方米 ≈ 1.19599平方码
            "ft2": 1/0.09290304,          # 1平方米 ≈ 10.7639平方英尺
            "in2": 1/0.00064516,          # 1平方米 ≈ 1550平方英寸
            "rd2": 1/25.29285264,         # 1平方米 ≈ 0.0395369平方竿
            
            # 中国市制单位
            "qing": 1/66666.6667,         # 1平方米 ≈ 0.000015市顷
            "mu": 1/666.666667,           # 1平方米 ≈ 0.0015市亩
            "chi2": 9,                    # 1平方米 = 9平方尺
            "cun2": 900                   # 1平方米 = 900平方寸
        }
        
        sqm = to_sqm.get(from_unit, value)
        return sqm * from_sqm.get(to_unit, 1)