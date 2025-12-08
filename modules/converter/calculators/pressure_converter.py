from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QScrollArea, QGridLayout, QFrame)
from PySide6.QtCore import Qt

class PressureConverter(QWidget):
    """压强单位换算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.unit_vars = {}
        self.setup_ui()
    
    def setup_ui(self):
        """设置压强换算器UI"""
        layout = QVBoxLayout(self)
        
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        scroll_layout.setSpacing(5)  # 减少行间距
        
        # 定义所有压强单位，分为两列
        units = [
            # 第一列单位
            ("帕斯卡 (Pa)", "Pa"), ("千帕 (kPa)", "kPa"), ("兆帕 (MPa)", "MPa"), 
            ("百帕 (hPa)", "hPa"), ("巴 (bar)", "bar"), ("毫巴 (mbar)", "mbar"),
            ("标准大气压 (atm)", "atm"), 
            
            # 第二列单位
            ("毫米汞柱 (mmHg)", "mmHg"), ("英寸汞柱 (inHg)", "inHg"), 
            ("毫米水柱 (mmH₂O)", "mmH2O"), ("磅力/平方英寸 (psi)", "psi"), 
            ("公斤力/平方厘米 (kgf/cm²)", "kgf_cm2"), ("公斤力/平方米 (kgf/m²)", "kgf_m2")
        ]
        
        # 计算每列的单位数量
        first_column_count = 7
        second_column_count = 6
        
        # 添加第一列单位
        for i, (display_name, unit_code) in enumerate(units[:first_column_count]):
            unit_frame = QFrame()
            unit_frame.setFrameStyle(QFrame.NoFrame)
            unit_layout = QHBoxLayout(unit_frame)
            unit_layout.setContentsMargins(5, 2, 5, 2)  # 减少边距
            unit_layout.setSpacing(10)  # 减少标签和输入框之间的间距
            
            label = QLabel(display_name)
            label.setFixedWidth(150)  # 增加标签宽度以适应更长的名称
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
            label.setFixedWidth(150)  # 增加标签宽度以适应更长的名称
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
        """执行压强换算"""
        # 先转换为帕斯卡
        to_pascal = {
            "Pa": value,                    # 1帕斯卡 = 1帕斯卡
            "kPa": value * 1000,            # 1千帕 = 1000帕斯卡
            "MPa": value * 1000000,         # 1兆帕 = 1,000,000帕斯卡
            "hPa": value * 100,             # 1百帕 = 100帕斯卡
            "bar": value * 100000,          # 1巴 = 100,000帕斯卡
            "mbar": value * 100,            # 1毫巴 = 100帕斯卡
            "atm": value * 101325,          # 1标准大气压 = 101,325帕斯卡
            "mmHg": value * 133.322,        # 1毫米汞柱 = 133.322帕斯卡
            "inHg": value * 3386.39,        # 1英寸汞柱 = 3,386.39帕斯卡
            "mmH2O": value * 9.80665,       # 1毫米水柱 = 9.80665帕斯卡
            "psi": value * 6894.76,         # 1磅力/平方英寸 = 6,894.76帕斯卡
            "kgf_cm2": value * 98066.5,     # 1公斤力/平方厘米 = 98,066.5帕斯卡
            "kgf_m2": value * 9.80665       # 1公斤力/平方米 = 9.80665帕斯卡
        }
        
        # 从帕斯卡转换为目标单位
        from_pascal = {
            "Pa": 1,                        # 1帕斯卡 = 1帕斯卡
            "kPa": 0.001,                   # 1帕斯卡 = 0.001千帕
            "MPa": 0.000001,                # 1帕斯卡 = 0.000001兆帕
            "hPa": 0.01,                    # 1帕斯卡 = 0.01百帕
            "bar": 0.00001,                 # 1帕斯卡 = 0.00001巴
            "mbar": 0.01,                   # 1帕斯卡 = 0.01毫巴
            "atm": 1/101325,                # 1帕斯卡 ≈ 9.86923e-6标准大气压
            "mmHg": 1/133.322,              # 1帕斯卡 ≈ 0.00750062毫米汞柱
            "inHg": 1/3386.39,              # 1帕斯卡 ≈ 0.0002953英寸汞柱
            "mmH2O": 1/9.80665,             # 1帕斯卡 ≈ 0.101972毫米水柱
            "psi": 1/6894.76,               # 1帕斯卡 ≈ 0.000145038磅力/平方英寸
            "kgf_cm2": 1/98066.5,           # 1帕斯卡 ≈ 1.01972e-5公斤力/平方厘米
            "kgf_m2": 1/9.80665             # 1帕斯卡 ≈ 0.101972公斤力/平方米
        }
        
        pascals = to_pascal.get(from_unit, value)
        return pascals * from_pascal.get(to_unit, 1)