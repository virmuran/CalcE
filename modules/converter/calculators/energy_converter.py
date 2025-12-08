from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QScrollArea, QGridLayout, QFrame)
from PySide6.QtCore import Qt

class EnergyConverter(QWidget):
    """热能单位换算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.unit_vars = {}
        self.setup_ui()
    
    def setup_ui(self):
        """设置热能换算器UI"""
        layout = QVBoxLayout(self)
        
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        scroll_layout.setSpacing(5)  # 减少行间距
        
        # 定义所有热能单位，分为两列
        units = [
            # 第一列单位
            ("焦耳 (J)", "J"), ("千焦 (kJ)", "kJ"), ("千瓦时 (kWh)", "kWh"), 
            ("千克·米 (kg·m)", "kgm"), ("米制马力·时 (PS·h)", "psh"),
            
            # 第二列单位
            ("英制马力·时 (HP·h)", "hph"), ("卡路里 (cal)", "cal"), ("千卡 (kcal)", "kcal"), 
            ("英热单位 (BTU)", "BTU"), ("英尺·磅 (ft·lb)", "ftlb")
        ]
        
        # 计算每列的单位数量
        first_column_count = 5
        second_column_count = 5
        
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
        """执行热能换算"""
        # 先转换为焦耳
        to_joule = {
            "J": value,                     # 1焦耳 = 1焦耳
            "kJ": value * 1000,             # 1千焦 = 1000焦耳
            "kWh": value * 3600000,         # 1千瓦时 = 3,600,000焦耳
            "kgm": value * 9.80665,         # 1千克·米 = 9.80665焦耳
            "psh": value * 2647795.5,       # 1米制马力·时 = 2,647,795.5焦耳
            "hph": value * 2684519.5,       # 1英制马力·时 = 2,684,519.5焦耳
            "cal": value * 4.184,           # 1卡路里 = 4.184焦耳
            "kcal": value * 4184,           # 1千卡 = 4184焦耳
            "BTU": value * 1055.06,         # 1英热单位 = 1055.06焦耳
            "ftlb": value * 1.35582         # 1英尺·磅 = 1.35582焦耳
        }
        
        # 从焦耳转换为目标单位
        from_joule = {
            "J": 1,                         # 1焦耳 = 1焦耳
            "kJ": 0.001,                    # 1焦耳 = 0.001千焦
            "kWh": 1/3600000,               # 1焦耳 ≈ 2.77778e-7千瓦时
            "kgm": 1/9.80665,               # 1焦耳 ≈ 0.101972千克·米
            "psh": 1/2647795.5,             # 1焦耳 ≈ 3.77673e-7米制马力·时
            "hph": 1/2684519.5,             # 1焦耳 ≈ 3.72506e-7英制马力·时
            "cal": 1/4.184,                 # 1焦耳 ≈ 0.239006卡路里
            "kcal": 1/4184,                 # 1焦耳 ≈ 0.000239006千卡
            "BTU": 1/1055.06,               # 1焦耳 ≈ 0.000947817英热单位
            "ftlb": 1/1.35582               # 1焦耳 ≈ 0.737562英尺·磅
        }
        
        joules = to_joule.get(from_unit, value)
        return joules * from_joule.get(to_unit, 1)