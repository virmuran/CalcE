from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QScrollArea, QGridLayout, QFrame)
from PySide6.QtCore import Qt

class SpeedConverter(QWidget):
    """速度单位换算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.unit_vars = {}
        self.setup_ui()
    
    def setup_ui(self):
        """设置速度换算器UI"""
        layout = QVBoxLayout(self)
        
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        scroll_layout.setSpacing(5)  # 减少行间距
        
        # 定义所有速度单位，分为两列
        units = [
            # 第一列单位
            ("米每秒 (m/s)", "m/s"), ("千米/时 (km/h)", "km/h"), ("千米/秒 (km/s)", "km/s"),
            ("光速 (c)", "c"), ("马赫 (Mach)", "mach"),
            
            # 第二列单位
            ("英里/时 (mph)", "mph"), ("英寸/秒 (in/s)", "in/s")
        ]
        
        # 计算每列的单位数量
        first_column_count = 5
        second_column_count = 2
        
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
        """执行速度换算"""
        # 先转换为米/秒
        to_mps = {
            "m/s": value,                    # 1米/秒 = 1米/秒
            "km/h": value / 3.6,             # 1千米/时 = 1/3.6米/秒
            "km/s": value * 1000,            # 1千米/秒 = 1000米/秒
            "c": value * 299792458,          # 1光速 = 299,792,458米/秒
            "mach": value * 340.3,           # 1马赫 ≈ 340.3米/秒 (在海平面和15°C条件下)
            "mph": value * 0.44704,          # 1英里/时 = 0.44704米/秒
            "in/s": value * 0.0254           # 1英寸/秒 = 0.0254米/秒
        }
        
        # 从米/秒转换为目标单位
        from_mps = {
            "m/s": 1,                        # 1米/秒 = 1米/秒
            "km/h": 3.6,                     # 1米/秒 = 3.6千米/时
            "km/s": 0.001,                   # 1米/秒 = 0.001千米/秒
            "c": 1/299792458,                # 1米/秒 ≈ 3.3356e-9光速
            "mach": 1/340.3,                 # 1米/秒 ≈ 0.00293858马赫
            "mph": 2.23694,                  # 1米/秒 ≈ 2.23694英里/时
            "in/s": 39.3701                  # 1米/秒 ≈ 39.3701英寸/秒
        }
        
        mps = to_mps.get(from_unit, value)
        return mps * from_mps.get(to_unit, 1)