from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QScrollArea, QGridLayout, QFrame)
from PySide6.QtCore import Qt

class PowerConverter(QWidget):
    """功率单位换算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.unit_vars = {}
        self.setup_ui()
    
    def setup_ui(self):
        """设置功率换算器UI"""
        layout = QVBoxLayout(self)
        
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        scroll_layout.setSpacing(5)  # 减少行间距
        
        # 定义所有功率单位，分为两列
        units = [
            # 第一列单位
            ("瓦特 (W)", "W"), ("千瓦 (kW)", "kW"), ("英制马力 (hp)", "hp"), 
            ("米制马力 (PS)", "ps"), ("焦耳/秒 (J/s)", "J/s"), 
            
            # 第二列单位
            ("公斤·米/秒 (kg·m/s)", "kgm_s"), ("千卡/秒 (kcal/s)", "kcal_s"), 
            ("英热单位/秒 (BTU/s)", "BTU_s"), ("英尺·磅/秒 (ft·lb/s)", "ftlb_s"), 
            ("牛顿·米/秒 (N·m/s)", "Nm_s")
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
            label.setFixedWidth(140)  # 增加标签宽度以适应更长的名称
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
            label.setFixedWidth(140)  # 增加标签宽度以适应更长的名称
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
        """执行功率换算"""
        # 先转换为瓦特
        to_watt = {
            "W": value,                     # 1瓦特 = 1瓦特
            "kW": value * 1000,             # 1千瓦 = 1000瓦特
            "hp": value * 745.699872,       # 1英制马力 = 745.699872瓦特
            "ps": value * 735.49875,        # 1米制马力 = 735.49875瓦特
            "J/s": value,                   # 1焦耳/秒 = 1瓦特
            "kgm_s": value * 9.80665,       # 1公斤·米/秒 = 9.80665瓦特
            "kcal_s": value * 4184,         # 1千卡/秒 = 4184瓦特
            "BTU_s": value * 1055.05585,    # 1英热单位/秒 = 1055.05585瓦特
            "ftlb_s": value * 1.355817948,  # 1英尺·磅/秒 = 1.355817948瓦特
            "Nm_s": value                   # 1牛顿·米/秒 = 1瓦特
        }
        
        # 从瓦特转换为目标单位
        from_watt = {
            "W": 1,                         # 1瓦特 = 1瓦特
            "kW": 0.001,                    # 1瓦特 = 0.001千瓦
            "hp": 1/745.699872,             # 1瓦特 ≈ 0.00134102英制马力
            "ps": 1/735.49875,              # 1瓦特 ≈ 0.00135962米制马力
            "J/s": 1,                       # 1瓦特 = 1焦耳/秒
            "kgm_s": 1/9.80665,             # 1瓦特 ≈ 0.101972公斤·米/秒
            "kcal_s": 1/4184,               # 1瓦特 ≈ 0.000239006千卡/秒
            "BTU_s": 1/1055.05585,          # 1瓦特 ≈ 0.000947817英热单位/秒
            "ftlb_s": 1/1.355817948,        # 1瓦特 ≈ 0.737562英尺·磅/秒
            "Nm_s": 1                       # 1瓦特 = 1牛顿·米/秒
        }
        
        watts = to_watt.get(from_unit, value)
        return watts * from_watt.get(to_unit, 1)