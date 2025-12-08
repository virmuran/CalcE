# base_converter.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QScrollArea, QGridLayout, QFrame)
from PySide6.QtCore import Qt

class BaseConverter(QWidget):
    """进制转换器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.unit_vars = {}
        self.setup_ui()
    
    def setup_ui(self):
        """设置进制转换器UI"""
        layout = QVBoxLayout(self)
        
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(5)  # 修复拼写错误：setVerticalSpacing
        
        # 定义所有进制单位
        units = [
            ("二进制", "bin"), 
            ("八进制", "oct"), 
            ("十进制", "dec"), 
            ("十六进制", "hex")
        ]
        
        # 添加所有进制单位，垂直排列
        for display_name, unit_code in units:
            unit_frame = QFrame()
            unit_frame.setFrameStyle(QFrame.NoFrame)
            unit_layout = QHBoxLayout(unit_frame)
            unit_layout.setContentsMargins(5, 2, 5, 2)  # 减少边距
            unit_layout.setSpacing(10)  # 减少标签和输入框之间的间距
            
            label = QLabel(display_name)
            label.setFixedWidth(80)  # 设置标签宽度
            label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            unit_layout.addWidget(label)
            
            entry = QLineEdit()
            entry.setFixedWidth(200)  # 设置输入框宽度
            if unit_code == "bin":
                entry.setPlaceholderText("输入二进制数")
                entry.textChanged.connect(lambda text, u=unit_code: self.on_base_input(text, u))
            elif unit_code == "oct":
                entry.setPlaceholderText("输入八进制数")
                entry.textChanged.connect(lambda text, u=unit_code: self.on_base_input(text, u))
            elif unit_code == "dec":
                entry.setPlaceholderText("输入十进制数")
                entry.textChanged.connect(lambda text, u=unit_code: self.on_base_input(text, u))
            elif unit_code == "hex":
                entry.setPlaceholderText("输入十六进制数")
                entry.textChanged.connect(lambda text, u=unit_code: self.on_base_input(text, u))
            
            unit_layout.addWidget(entry)
            
            self.unit_vars[unit_code] = entry
            scroll_layout.addWidget(unit_frame)
        
        # 存储输入框引用，便于批量操作
        self.inputs = {
            "bin": self.unit_vars["bin"],
            "oct": self.unit_vars["oct"], 
            "dec": self.unit_vars["dec"],
            "hex": self.unit_vars["hex"]
        }
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
    
    def on_base_input(self, text, source_base):
        """处理进制输入"""
        try:
            source_value = text.strip()
            if not source_value:
                # 清空所有输入框
                for base_code, entry in self.inputs.items():
                    if base_code != source_base:
                        entry.blockSignals(True)
                        entry.setText("")
                        entry.blockSignals(False)
                return
            
            # 转换为十进制
            decimal_val = 0
            if source_base == "bin":
                # 验证二进制输入
                if any(c not in '01' for c in source_value):
                    return
                decimal_val = int(source_value, 2)
            elif source_base == "oct":
                # 验证八进制输入
                if any(c not in '01234567' for c in source_value):
                    return
                decimal_val = int(source_value, 8)
            elif source_base == "dec":
                # 验证十进制输入
                if not source_value.isdigit():
                    return
                decimal_val = int(source_value)
            elif source_base == "hex":
                # 验证十六进制输入
                if any(c.upper() not in '0123456789ABCDEF' for c in source_value):
                    return
                decimal_val = int(source_value, 16)
            else:
                return
            
            # 更新其他输入框
            for base_code, entry in self.inputs.items():
                if base_code != source_base:
                    entry.blockSignals(True)
                    if base_code == "bin":
                        entry.setText(bin(decimal_val)[2:])
                    elif base_code == "oct":
                        entry.setText(oct(decimal_val)[2:])
                    elif base_code == "dec":
                        entry.setText(str(decimal_val))
                    elif base_code == "hex":
                        entry.setText(hex(decimal_val)[2:].upper())
                    entry.blockSignals(False)
            
        except ValueError:
            pass