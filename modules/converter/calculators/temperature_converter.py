from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QScrollArea, QGridLayout, QFrame)
from PySide6.QtCore import Qt

class TemperatureConverter(QWidget):
    """温度单位换算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.unit_vars = {}
        self.setup_ui()
    
    def setup_ui(self):
        """设置温度换算器UI"""
        layout = QVBoxLayout(self)
        
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        scroll_layout.setSpacing(5)  # 减少行间距
        
        # 定义所有温度单位，分为两列
        units = [
            # 第一列单位
            ("摄氏度 (°C)", "c"), ("华氏度 (°F)", "f"), ("开尔文 (K)", "k"),
            
            # 第二列单位
            ("兰氏度 (°R)", "r"), ("列氏度 (°Ré)", "re")
        ]
        
        # 计算每列的单位数量
        first_column_count = 3
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
        """执行温度换算"""
        # 先转换为摄氏度
        if from_unit == "c":
            celsius = value
        elif from_unit == "f":
            celsius = (value - 32) * 5/9
        elif from_unit == "k":
            celsius = value - 273.15
        elif from_unit == "r":
            celsius = (value - 491.67) * 5/9  # 兰氏度转摄氏度
        elif from_unit == "re":
            celsius = value * 5/4  # 列氏度转摄氏度
        else:
            celsius = value
        
        # 从摄氏度转换为目标单位
        if to_unit == "c":
            return celsius
        elif to_unit == "f":
            return celsius * 9/5 + 32
        elif to_unit == "k":
            return celsius + 273.15
        elif to_unit == "r":
            return (celsius + 273.15) * 9/5  # 摄氏度转兰氏度
        elif to_unit == "re":
            return celsius * 4/5  # 摄氏度转列氏度
        else:
            return celsius