from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QScrollArea, QGridLayout, QFrame)
from PySide6.QtCore import Qt

class VolumeConverter(QWidget):
    """体积单位换算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.unit_vars = {}
        self.setup_ui()
    
    def setup_ui(self):
        """设置体积换算器UI"""
        layout = QVBoxLayout(self)
        
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QGridLayout(scroll_widget)
        scroll_layout.setSpacing(5)  # 减少行间距
        
        # 定义所有单位，分为两列
        units = [
            # 第一列单位
            ("立方米 (m³)", "m3"), ("立方分米 (dm³)", "dm3"), ("立方厘米 (cm³)", "cm3"), 
            ("立方毫米 (mm³)", "mm3"), ("百升 (hL)", "hl"), ("升 (L)", "l"), 
            ("升（公制）", "l_metric"), ("厘升 (cL)", "cl"), ("毫升 (mL)", "ml"),
            
            # 第二列单位
            ("立方英尺 (ft³)", "ft3"), ("立方英寸 (in³)", "in3"), ("立方码 (yd³)", "yd3"), 
            ("英制加仑 (gal)", "gal_uk"), ("美制加仑 (gal)", "gal_us"), 
            ("英制盎司 (fl oz)", "oz_uk"), ("美制盎司 (fl oz)", "oz_us")
        ]
        
        # 计算每列的单位数量
        first_column_count = 9
        second_column_count = 7
        
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
        """执行体积换算"""
        # 先转换为立方米
        to_cum = {
            # 国际单位制
            "m3": value,                    # 1立方米 = 1立方米
            "dm3": value * 0.001,           # 1立方分米 = 0.001立方米
            "cm3": value * 0.000001,        # 1立方厘米 = 0.000001立方米
            "mm3": value * 0.000000001,     # 1立方毫米 = 10^-9立方米
            
            # 公制容量单位
            "hl": value * 0.1,              # 1百升 = 0.1立方米
            "l": value * 0.001,             # 1升 = 0.001立方米
            "l_metric": value * 0.001,      # 1升（公制）= 0.001立方米
            "cl": value * 0.00001,          # 1厘升 = 0.00001立方米
            "ml": value * 0.000001,         # 1毫升 = 0.000001立方米
            
            # 英制单位
            "ft3": value * 0.0283168466,    # 1立方英尺 = 0.0283168466立方米
            "in3": value * 0.000016387064,  # 1立方英寸 = 0.000016387064立方米
            "yd3": value * 0.764554857984,  # 1立方码 = 0.764554857984立方米
            
            # 英制容量单位
            "gal_uk": value * 0.00454609,   # 1英制加仑 = 0.00454609立方米
            "gal_us": value * 0.003785411784, # 1美制加仑 = 0.003785411784立方米
            "oz_uk": value * 0.0000284130625, # 1英制盎司 = 0.0000284130625立方米
            "oz_us": value * 0.0000295735295625 # 1美制盎司 = 0.0000295735295625立方米
        }
        
        # 从立方米转换为目标单位
        from_cum = {
            # 国际单位制
            "m3": 1,                        # 1立方米 = 1立方米
            "dm3": 1000,                    # 1立方米 = 1000立方分米
            "cm3": 1000000,                 # 1立方米 = 1,000,000立方厘米
            "mm3": 1000000000,              # 1立方米 = 1,000,000,000立方毫米
            
            # 公制容量单位
            "hl": 10,                       # 1立方米 = 10百升
            "l": 1000,                      # 1立方米 = 1000升
            "l_metric": 1000,               # 1立方米 = 1000升（公制）
            "cl": 100000,                   # 1立方米 = 100,000厘升
            "ml": 1000000,                  # 1立方米 = 1,000,000毫升
            
            # 英制单位
            "ft3": 35.3146667214886,        # 1立方米 ≈ 35.3147立方英尺
            "in3": 61023.7440947323,        # 1立方米 ≈ 61,023.7441立方英寸
            "yd3": 1.30795061931439,        # 1立方米 ≈ 1.30795立方码
            
            # 英制容量单位
            "gal_uk": 219.969248299088,     # 1立方米 ≈ 219.969英制加仑
            "gal_us": 264.172052358148,     # 1立方米 ≈ 264.172美制加仑
            "oz_uk": 35195.079727854,       # 1立方米 ≈ 35,195.08英制盎司
            "oz_us": 33814.022701843,       # 1立方米 ≈ 33,814.023美制盎司
        }
        
        cum = to_cum.get(from_unit, value)
        return cum * from_cum.get(to_unit, 1)