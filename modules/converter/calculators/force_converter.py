from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QScrollArea, QGridLayout, QFrame)
from PySide6.QtCore import Qt

class ForceConverter(QWidget):
    """力单位换算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.unit_vars = {}
        self.setup_ui()
    
    def setup_ui(self):
        """设置力换算器UI"""
        layout = QVBoxLayout(self)
        
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        scroll_layout.setSpacing(5)  # 减少行间距
        
        # 定义所有力单位，分为两列
        units = [
            # 第一列单位
            ("牛顿 (N)", "N"), ("千牛 (kN)", "kN"), ("千克力 (kgf)", "kgf"), 
            ("克力 (gf)", "gf"), ("公吨力 (tf)", "tf"),
            
            # 第二列单位
            ("磅力 (lbf)", "lbf"), ("千磅力 (kip)", "kip"), ("达因 (dyn)", "dyn")
        ]
        
        # 计算每列的单位数量
        first_column_count = 5
        second_column_count = 3
        
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
        """执行力换算"""
        # 先转换为牛顿
        to_newton = {
            "N": value,                     # 1牛顿 = 1牛顿
            "kN": value * 1000,             # 1千牛 = 1000牛顿
            "kgf": value * 9.80665,         # 1千克力 = 9.80665牛顿
            "gf": value * 0.00980665,       # 1克力 = 0.00980665牛顿
            "tf": value * 9806.65,          # 1公吨力 = 9806.65牛顿
            "lbf": value * 4.4482216152605, # 1磅力 = 4.4482216152605牛顿
            "kip": value * 4448.2216152605, # 1千磅力 = 4448.2216152605牛顿
            "dyn": value * 0.00001          # 1达因 = 0.00001牛顿
        }
        
        # 从牛顿转换为目标单位
        from_newton = {
            "N": 1,                         # 1牛顿 = 1牛顿
            "kN": 0.001,                    # 1牛顿 = 0.001千牛
            "kgf": 1/9.80665,               # 1牛顿 ≈ 0.101972千克力
            "gf": 1/0.00980665,             # 1牛顿 ≈ 101.972克力
            "tf": 1/9806.65,                # 1牛顿 ≈ 0.000101972公吨力
            "lbf": 1/4.4482216152605,       # 1牛顿 ≈ 0.224809磅力
            "kip": 1/4448.2216152605,       # 1牛顿 ≈ 0.000224809千磅力
            "dyn": 100000                   # 1牛顿 = 100,000达因
        }
        
        newtons = to_newton.get(from_unit, value)
        return newtons * from_newton.get(to_unit, 1)