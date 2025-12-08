from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QScrollArea, QGridLayout, QFrame)
from PySide6.QtCore import Qt

class WeightConverter(QWidget):
    """重量单位换算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.unit_vars = {}
        self.setup_ui()
    
    def setup_ui(self):
        """设置重量换算器UI"""
        layout = QVBoxLayout(self)
        
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        scroll_layout.setSpacing(5)  # 减少行间距
        
        # 定义所有单位，分为两列
        units = [
            # 第一列单位
            ("吨 (t)", "t"), ("千克 (kg)", "kg"), ("克 (g)", "g"), 
            ("毫克 (mg)", "mg"), ("微克 (μg)", "ug"), ("公担 (q)", "q"), 
            ("克拉 (ct)", "ct"), ("磅 (lb)", "lb"), ("盎司 (oz)", "oz"),
            ("格令 (gr)", "gr"), ("长吨 (long ton)", "long_ton"),
            
            # 第二列单位
            ("短吨 (short ton)", "short_ton"), ("打兰 (dr)", "dr"), 
            ("英担 (cwt)", "cwt"), ("美担 (uscwt)", "uscwt"), 
            ("英石 (st)", "st"), ("斤", "jin"), ("两", "liang"), 
            ("钱", "qian"), ("担", "dan")
        ]
        
        # 计算每列的单位数量
        first_column_count = 11
        second_column_count = 9
        
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
        """执行重量换算"""
        # 先转换为克
        to_gram = {
            # 国际单位制
            "t": value * 1000000,        # 1吨 = 1,000,000克
            "kg": value * 1000,          # 1千克 = 1,000克
            "g": value,                  # 1克 = 1克
            "mg": value * 0.001,         # 1毫克 = 0.001克
            "ug": value * 0.000001,      # 1微克 = 0.000001克
            "q": value * 100000,         # 1公担 = 100,000克
            
            # 特殊单位
            "ct": value * 0.2,           # 1克拉 = 0.2克
            
            # 英制单位
            "lb": value * 453.59237,     # 1磅 = 453.59237克
            "oz": value * 28.349523125,  # 1盎司 = 28.349523125克
            "gr": value * 0.06479891,    # 1格令 = 0.06479891克
            "long_ton": value * 1016046.9088,    # 1长吨 = 1,016,046.9088克
            "short_ton": value * 907184.74,      # 1短吨 = 907,184.74克
            "dr": value * 1.7718451953125,       # 1打兰 = 1.7718451953125克
            "cwt": value * 50802.34544,          # 1英担 = 50,802.34544克
            "uscwt": value * 45359.237,          # 1美担 = 45,359.237克
            "st": value * 6350.29318,            # 1英石 = 6,350.29318克
            
            # 中国市制单位
            "jin": value * 500,          # 1斤 = 500克
            "liang": value * 50,         # 1两 = 50克
            "qian": value * 5,           # 1钱 = 5克
            "dan": value * 50000         # 1担 = 50,000克
        }
        
        # 从克转换为目标单位
        from_gram = {
            # 国际单位制
            "t": 0.000001,               # 1克 = 0.000001吨
            "kg": 0.001,                 # 1克 = 0.001千克
            "g": 1,                      # 1克 = 1克
            "mg": 1000,                  # 1克 = 1,000毫克
            "ug": 1000000,               # 1克 = 1,000,000微克
            "q": 0.00001,                # 1克 = 0.00001公担
            
            # 特殊单位
            "ct": 5,                     # 1克 = 5克拉
            
            # 英制单位
            "lb": 0.00220462262185,      # 1克 ≈ 0.00220462磅
            "oz": 0.03527396195,         # 1克 ≈ 0.03527396盎司
            "gr": 15.4323583529,         # 1克 ≈ 15.43236格令
            "long_ton": 1/1016046.9088,  # 1克 ≈ 0.000000984207长吨
            "short_ton": 1/907184.74,    # 1克 ≈ 0.00000110231短吨
            "dr": 0.564383391193,        # 1克 ≈ 0.564383打兰
            "cwt": 1/50802.34544,        # 1克 ≈ 0.00001968413英担
            "uscwt": 1/45359.237,        # 1克 ≈ 0.00002204623美担
            "st": 1/6350.29318,          # 1克 ≈ 0.000157473英石
            
            # 中国市制单位
            "jin": 0.002,                # 1克 = 0.002斤
            "liang": 0.02,               # 1克 = 0.02两
            "qian": 0.2,                 # 1克 = 0.2钱
            "dan": 0.00002               # 1克 = 0.00002担
        }
        
        grams = to_gram.get(from_unit, value)
        return grams * from_gram.get(to_unit, 1)