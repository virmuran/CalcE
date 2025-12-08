from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QScrollArea, QGridLayout, QFrame)
from PySide6.QtCore import Qt

class LengthConverter(QWidget):
    """长度单位换算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.unit_vars = {}
        self.setup_ui()
    
    def setup_ui(self):
        """设置长度换算器UI"""
        layout = QVBoxLayout(self)
        
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        scroll_layout.setSpacing(5)  # 减少行间距
        
        # 定义所有单位，分为两列
        units = [
            # 第一列单位
            ("公里 (km)", "km"), ("米 (m)", "m"), ("分米 (dm)", "dm"), 
            ("厘米 (cm)", "cm"), ("毫米 (mm)", "mm"), ("微米 (μm)", "um"), 
            ("纳米 (nm)", "nm"), ("皮米 (pm)", "pm"), ("光年 (ly)", "ly"),
            ("天文单位 (AU)", "au"), ("里", "li"), ("丈", "zhang"), ("尺", "chi"),
            
            # 第二列单位
            ("寸", "cun"), ("分", "fen"), ("厘", "li_small"), ("毫", "hao"),
            ("海里 (nmi)", "nmi"), ("英寻 (fathom)", "fathom"), ("英里 (mi)", "mi"), 
            ("弗隆 (fur)", "fur"), ("码 (yd)", "yd"), ("英尺 (ft)", "ft"), 
            ("英寸 (in)", "in"), ("密耳 (mil)", "mil")
        ]
        
        # 计算每列的单位数量
        first_column_count = 13
        second_column_count = 12
        
        # 添加第一列单位
        for i, (display_name, unit_code) in enumerate(units[:first_column_count]):
            unit_frame = QFrame()
            unit_frame.setFrameStyle(QFrame.NoFrame)
            unit_layout = QHBoxLayout(unit_frame)
            unit_layout.setContentsMargins(5, 2, 5, 2)  # 减少边距
            unit_layout.setSpacing(10)  # 减少标签和输入框之间的间距
            
            label = QLabel(display_name)
            label.setFixedWidth(100)  # 增加标签宽度以适应更长的名称
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
            label.setFixedWidth(100)  # 增加标签宽度以适应更长的名称
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
        """执行长度换算"""
        # 先转换为米
        to_meter = {
            # 国际单位制
            "km": value * 1000,
            "m": value,
            "dm": value * 0.1,
            "cm": value * 0.01,
            "mm": value * 0.001,
            "um": value * 0.000001,
            "nm": value * 0.000000001,
            "pm": value * 0.000000000001,  # 皮米
            
            # 天文单位
            "ly": value * 9460730472580800,  # 光年
            "au": value * 149597870700,      # 天文单位
            
            # 中国市制单位
            "li": value * 500,               # 1里=500米
            "zhang": value * 10/3,           # 1丈=10/3米≈3.333米
            "chi": value * 1/3,              # 1尺=1/3米≈0.333米
            "cun": value * 1/30,             # 1寸=1/30米≈0.033米
            "fen": value * 1/300,            # 1分=1/300米≈0.00333米
            "li_small": value * 1/3000,      # 1厘=1/3000米≈0.000333米
            "hao": value * 1/30000,          # 1毫=1/30000米≈0.0000333米
            
            # 英制单位
            "nmi": value * 1852,             # 1海里=1852米
            "fathom": value * 1.8288,        # 1英寻=1.8288米
            "mi": value * 1609.344,          # 1英里=1609.344米
            "fur": value * 201.168,          # 1弗隆=201.168米
            "yd": value * 0.9144,            # 1码=0.9144米
            "ft": value * 0.3048,            # 1英尺=0.3048米
            "in": value * 0.0254,            # 1英寸=0.0254米
            "mil": value * 0.0000254         # 1密耳=0.001英寸=0.0000254米
        }
        
        # 从米转换为目标单位
        from_meter = {
            # 国际单位制
            "km": 0.001,
            "m": 1,
            "dm": 10,
            "cm": 100,
            "mm": 1000,
            "um": 1000000,
            "nm": 1000000000,
            "pm": 1000000000000,      # 皮米
            
            # 天文单位
            "ly": 1/9460730472580800, # 光年
            "au": 1/149597870700,     # 天文单位
            
            # 中国市制单位
            "li": 0.002,              # 1米=0.002里
            "zhang": 0.3,             # 1米=0.3丈
            "chi": 3,                 # 1米=3尺
            "cun": 30,                # 1米=30寸
            "fen": 300,               # 1米=300分
            "li_small": 3000,         # 1米=3000厘
            "hao": 30000,             # 1米=30000毫
            
            # 英制单位
            "nmi": 1/1852,            # 1米≈0.000539957海里
            "fathom": 1/1.8288,       # 1米≈0.546807英寻
            "mi": 1/1609.344,         # 1米≈0.000621371英里
            "fur": 1/201.168,         # 1米≈0.00497097弗隆
            "yd": 1/0.9144,           # 1米≈1.09361码
            "ft": 1/0.3048,           # 1米≈3.28084英尺
            "in": 1/0.0254,           # 1米≈39.3701英寸
            "mil": 1/0.0000254        # 1米≈39370.1密耳
        }
        
        meters = to_meter.get(from_unit, value)
        return meters * from_meter.get(to_unit, 1)