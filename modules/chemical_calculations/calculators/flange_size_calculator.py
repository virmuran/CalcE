from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                              QLabel, QLineEdit, QComboBox, QPushButton, 
                              QTextEdit, QTableWidget, QTableWidgetItem,
                              QHeaderView, QMessageBox, QTabWidget, QDoubleSpinBox,
                              QCheckBox, QRadioButton, QButtonGroup, QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QDoubleValidator
import math

class FlangeSizeCalculator(QWidget):
    """法兰尺寸查询计算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.flange_data = self.load_flange_data()
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("🔩 法兰尺寸查询")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 添加查询标签页
        self.query_tab = self.create_query_tab()
        self.tab_widget.addTab(self.query_tab, "🔍 尺寸查询")
        
        # 添加标准库标签页
        self.standard_tab = self.create_standard_tab()
        self.tab_widget.addTab(self.standard_tab, "📚 标准库")
        
        # 添加选型指南标签页
        self.selection_tab = self.create_selection_tab()
        self.tab_widget.addTab(self.selection_tab, "📋 选型指南")
        
        main_layout.addWidget(self.tab_widget)
    
    def create_query_tab(self):
        """创建查询标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 查询条件组
        query_group = QGroupBox("🔍 查询条件")
        query_layout = QVBoxLayout(query_group)
        
        # 法兰标准和类型
        standard_layout = QHBoxLayout()
        standard_layout.addWidget(QLabel("法兰标准:"))
        self.standard_combo = QComboBox()
        self.standard_combo.addItems([
            "HG/T 20592", "HG/T 20615", "GB/T 9119", "JB/T 81", 
            "ANSI B16.5", "DIN", "JIS", "EN"
        ])
        self.standard_combo.currentTextChanged.connect(self.on_standard_changed)
        standard_layout.addWidget(self.standard_combo)
        
        standard_layout.addWidget(QLabel("法兰类型:"))
        self.type_combo = QComboBox()
        standard_layout.addWidget(self.type_combo)
        
        standard_layout.addWidget(QLabel("公称压力:"))
        self.pressure_combo = QComboBox()
        standard_layout.addWidget(self.pressure_combo)
        
        query_layout.addLayout(standard_layout)
        
        # 尺寸参数
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("公称通径:"))
        self.dn_combo = QComboBox()
        self.dn_combo.addItems([str(dn) for dn in [10, 15, 20, 25, 32, 40, 50, 65, 80, 100, 
                                                  125, 150, 200, 250, 300, 350, 400, 450, 500,
                                                  600, 700, 800, 900, 1000, 1200, 1400, 1600, 1800, 2000]])
        size_layout.addWidget(self.dn_combo)
        
        size_layout.addWidget(QLabel("密封面形式:"))
        self.face_type_combo = QComboBox()
        size_layout.addWidget(self.face_type_combo)
        
        size_layout.addWidget(QLabel("材料:"))
        self.material_combo = QComboBox()
        self.material_combo.addItems(["Q235A", "20#", "304", "316", "304L", "316L", "碳钢", "不锈钢"])
        size_layout.addWidget(self.material_combo)
        
        query_layout.addLayout(size_layout)
        
        layout.addWidget(query_group)
        
        # 按钮组
        button_layout = QHBoxLayout()
        self.query_btn = QPushButton("🚀 查询法兰尺寸")
        self.query_btn.clicked.connect(self.query_flange_size)
        self.query_btn.setStyleSheet("QPushButton { background-color: #34495e; color: white; font-weight: bold; }")
        button_layout.addWidget(self.query_btn)
        
        self.bolt_calc_btn = QPushButton("🔧 螺栓计算")
        self.bolt_calc_btn.clicked.connect(self.bolt_calculation)
        self.bolt_calc_btn.setStyleSheet("QPushButton { background-color: #3498db; color: white; }")
        button_layout.addWidget(self.bolt_calc_btn)
        
        self.clear_btn = QPushButton("🗑️ 清空")
        self.clear_btn.clicked.connect(self.clear_inputs)
        self.clear_btn.setStyleSheet("QPushButton { background-color: #95a5a6; color: white; }")
        button_layout.addWidget(self.clear_btn)
        
        layout.addLayout(button_layout)
        
        # 基本尺寸组
        basic_size_group = QGroupBox("📏 基本尺寸")
        basic_size_layout = QVBoxLayout(basic_size_group)
        
        self.basic_size_table = QTableWidget()
        self.basic_size_table.setColumnCount(3)
        self.basic_size_table.setHorizontalHeaderLabels(["尺寸参数", "数值", "单位"])
        basic_size_layout.addWidget(self.basic_size_table)
        
        layout.addWidget(basic_size_group)
        
        # 螺栓尺寸组
        bolt_size_group = QGroupBox("🔩 螺栓尺寸")
        bolt_size_layout = QVBoxLayout(bolt_size_group)
        
        self.bolt_size_table = QTableWidget()
        self.bolt_size_table.setColumnCount(3)
        self.bolt_size_table.setHorizontalHeaderLabels(["螺栓参数", "数值", "单位"])
        bolt_size_layout.addWidget(self.bolt_size_table)
        
        layout.addWidget(bolt_size_group)
        
        # 重量和材料组
        weight_material_group = QGroupBox("⚖️ 重量和材料")
        weight_material_layout = QVBoxLayout(weight_material_group)
        
        self.weight_material_table = QTableWidget()
        self.weight_material_table.setColumnCount(3)
        self.weight_material_table.setHorizontalHeaderLabels(["参数", "数值", "单位"])
        weight_material_layout.addWidget(self.weight_material_table)
        
        layout.addWidget(weight_material_group)
        
        # 初始化下拉框
        self.on_standard_changed(self.standard_combo.currentText())
        
        return tab
    
    def on_standard_changed(self, standard):
        """标准改变事件"""
        # 更新法兰类型
        types = {
            "HG/T 20592": ["WN(带颈对焊)", "SO(带颈平焊)", "PL(板式平焊)", "BL(法兰盖)", "TH(螺纹)"],
            "HG/T 20615": ["WN(带颈对焊)", "SO(带颈平焊)", "PL(板式平焊)", "BL(法兰盖)"],
            "GB/T 9119": ["整体法兰", "对焊法兰", "板式平焊法兰", "法兰盖"],
            "JB/T 81": ["板式平焊法兰"],
            "ANSI B16.5": ["Weld Neck", "Slip On", "Blind", "Socket Weld", "Lap Joint"],
            "DIN": ["DIN 2633", "DIN 2634", "DIN 2635", "DIN 2636", "DIN 2637", "DIN 2638"],
            "JIS": ["10K", "16K", "20K", "30K", "40K"],
            "EN": ["EN 1092-1 Type 01", "EN 1092-1 Type 02", "EN 1092-1 Type 05", "EN 1092-1 Type 11"]
        }
        
        self.type_combo.clear()
        if standard in types:
            self.type_combo.addItems(types[standard])
        
        # 更新公称压力
        pressures = {
            "HG/T 20592": ["PN6", "PN10", "PN16", "PN25", "PN40", "PN63", "PN100"],
            "HG/T 20615": ["Class150", "Class300", "Class600", "Class900", "Class1500", "Class2500"],
            "GB/T 9119": ["PN0.25", "PN0.6", "PN1.0", "PN1.6", "PN2.5", "PN4.0"],
            "JB/T 81": ["PN0.25", "PN0.6", "PN1.0", "PN1.6", "PN2.5"],
            "ANSI B16.5": ["Class150", "Class300", "Class600", "Class900", "Class1500"],
            "DIN": ["PN6", "PN10", "PN16", "PN25", "PN40"],
            "JIS": ["10K", "16K", "20K", "30K", "40K"],
            "EN": ["PN6", "PN10", "PN16", "PN25", "PN40"]
        }
        
        self.pressure_combo.clear()
        if standard in pressures:
            self.pressure_combo.addItems(pressures[standard])
        
        # 更新密封面形式
        face_types = {
            "HG/T 20592": ["FF(全平面)", "RF(凸面)", "MFM(凹凸面)", "TG(榫槽面)"],
            "HG/T 20615": ["RF(凸面)", "MFM(凹凸面)", "TG(榫槽面)", "RJ(环连接面)"],
            "GB/T 9119": ["平面", "凸面", "凹凸面", "榫槽面"],
            "ANSI B16.5": ["Flat Face", "Raised Face", "Ring Joint", "Male-Female", "Tongue-Groove"],
            "DIN": ["Plane", "Raised Face", "Tongue-Groove"],
            "JIS": ["平面", "凸面"],
            "EN": ["Type A", "Type B", "Type C", "Type D", "Type E", "Type F"]
        }
        
        self.face_type_combo.clear()
        if standard in face_types:
            self.face_type_combo.addItems(face_types[standard])
    
    def create_standard_tab(self):
        """创建标准库标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 标准库说明
        info_label = QLabel("常用法兰标准对照表")
        info_label.setFont(QFont("Arial", 12, QFont.Bold))
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # 标准对照表
        standard_table = QTableWidget()
        standard_table.setColumnCount(5)
        standard_table.setHorizontalHeaderLabels(["标准", "压力等级", "温度范围(°C)", "适用介质", "应用领域"])
        
        standard_data = [
            ["HG/T 20592", "PN6-PN100", "-20~300", "一般介质", "化工、石化"],
            ["HG/T 20615", "Class150-2500", "-20~425", "易燃、有毒介质", "化工、石油"],
            ["GB/T 9119", "PN0.25-PN4.0", "-20~300", "一般介质", "通用工业"],
            ["JB/T 81", "PN0.25-PN2.5", "-20~300", "一般介质", "机械、设备"],
            ["ANSI B16.5", "Class150-2500", "-20~538", "各种介质", "石油、化工"],
            ["DIN", "PN6-PN40", "-20~400", "一般介质", "欧洲项目"],
            ["JIS", "10K-40K", "-20~350", "一般介质", "日本项目"],
            ["EN 1092-1", "PN6-PN40", "-20~400", "各种介质", "欧洲标准"]
        ]
        
        standard_table.setRowCount(len(standard_data))
        for i, row_data in enumerate(standard_data):
            for j, data in enumerate(row_data):
                item = QTableWidgetItem(data)
                item.setTextAlignment(Qt.AlignCenter)
                standard_table.setItem(i, j, item)
        
        # 调整列宽
        header = standard_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        layout.addWidget(standard_table)
        
        # 压力等级对照
        pressure_group = QGroupBox("📊 压力等级对照")
        pressure_layout = QVBoxLayout(pressure_group)
        
        pressure_table = QTableWidget()
        pressure_table.setColumnCount(4)
        pressure_table.setHorizontalHeaderLabels(["标准", "压力等级", "公称压力(MPa)", "对应Class"])
        
        pressure_data = [
            ["HG/T 20592", "PN6", "0.6", "-"],
            ["HG/T 20592", "PN10", "1.0", "-"],
            ["HG/T 20592", "PN16", "1.6", "Class150"],
            ["HG/T 20592", "PN25", "2.5", "Class300"],
            ["HG/T 20592", "PN40", "4.0", "Class600"],
            ["ANSI B16.5", "Class150", "1.96", "PN16"],
            ["ANSI B16.5", "Class300", "5.1", "PN40"],
            ["ANSI B16.5", "Class600", "10.2", "PN100"],
            ["GB/T 9119", "PN1.6", "1.6", "Class150"],
            ["GB/T 9119", "PN2.5", "2.5", "Class300"]
        ]
        
        pressure_table.setRowCount(len(pressure_data))
        for i, row_data in enumerate(pressure_data):
            for j, data in enumerate(row_data):
                item = QTableWidgetItem(data)
                item.setTextAlignment(Qt.AlignCenter)
                pressure_table.setItem(i, j, item)
        
        pressure_layout.addWidget(pressure_table)
        layout.addWidget(pressure_group)
        
        return tab
    
    def create_selection_tab(self):
        """创建选型指南标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 选型指南说明
        selection_text = QTextEdit()
        selection_text.setReadOnly(True)
        selection_text.setHtml(self.get_selection_guide_html())
        layout.addWidget(selection_text)
        
        return tab
    
    def get_selection_guide_html(self):
        """获取选型指南HTML内容"""
        return """
        <h2>📋 法兰选型指南</h2>
        
        <h3>🔩 法兰类型选择</h3>
        
        <h4>1. 对焊法兰 (WN)</h4>
        <p><b>特点：</b>颈部与管道对焊连接，强度高，密封性好</p>
        <p><b>适用场合：</b></p>
        <ul>
            <li>高温高压管道</li>
            <li>易燃、有毒介质</li>
            <li>剧烈循环工况</li>
            <li>DN≤600mm的管道</li>
        </ul>
        
        <h4>2. 平焊法兰 (SO)</h4>
        <p><b>特点：</b>管道插入法兰内孔焊接，制造简单</p>
        <p><b>适用场合：</b></p>
        <ul>
            <li>中低压管道</li>
            <li>非剧烈循环工况</li>
            <li>一般介质</li>
            <li>成本敏感项目</li>
        </ul>
        
        <h4>3. 板式平焊法兰 (PL)</h4>
        <p><b>特点：</b>管道插入法兰焊接，刚度较差</p>
        <p><b>适用场合：</b></p>
        <ul>
            <li>低压管道</li>
            <li>非危险介质</li>
            <li>温度压力波动小</li>
            <li>DN≤600mm</li>
        </ul>
        
        <h4>4. 法兰盖 (BL)</h4>
        <p><b>特点：</b>用于管道端部或设备开口的封闭</p>
        <p><b>适用场合：</b></p>
        <ul>
            <li>管道末端封堵</li>
            <li>设备预留口</li>
            <li>检修口</li>
        </ul>
        
        <h3>🔧 密封面形式选择</h3>
        
        <h4>1. 全平面 (FF)</h4>
        <p><b>特点：</b>密封面与法兰面平齐</p>
        <p><b>适用：</b>低压、非危险介质，与铸铁法兰配用</p>
        
        <h4>2. 凸面 (RF)</h4>
        <p><b>特点：</b>密封面凸出法兰面</p>
        <p><b>适用：</b>一般工况，应用最广泛</p>
        
        <h4>3. 凹凸面 (MFM)</h4>
        <p><b>特点：</b>一凸一凹配合使用</p>
        <p><b>适用：</b>中高压工况，密封要求较高</p>
        
        <h4>4. 榫槽面 (TG)</h4>
        <p><b>特点：</b>一榫一槽配合使用</p>
        <p><b>适用：</b>高压、易燃、有毒介质</p>
        
        <h4>5. 环连接面 (RJ)</h4>
        <p><b>特点：</b>金属环垫密封</p>
        <p><b>适用：</b>高温高压工况，Class600及以上</p>
        
        <h3>📊 压力温度等级</h3>
        
        <h4>压力-温度额定值</h4>
        <p>法兰的压力等级随温度升高而降低，选型时应根据最高工作温度确定许用压力。</p>
        
        <h4>材料选择原则</h4>
        <ul>
            <li><b>碳钢：</b>一般工况，温度≤425°C</li>
            <li><b>不锈钢：</b>腐蚀介质，高温工况</li>
            <li><b>合金钢：</b>高温高压工况</li>
            <li><b>低温钢：</b>低温工况(≤-20°C)</li>
        </ul>
        
        <h3>⚠️ 选型注意事项</h3>
        <ul>
            <li>考虑介质腐蚀性选择材料</li>
            <li>根据最高工作温度和压力确定压力等级</li>
            <li>振动和热循环工况选用对焊法兰</li>
            <li>易燃有毒介质选用高密封性结构</li>
            <li>考虑安装和检修的便利性</li>
            <li>符合项目统一标准要求</li>
        </ul>
        
        <h3>📖 参考标准</h3>
        <ul>
            <li>HG/T 20592~20635 钢制管法兰、垫片、紧固件</li>
            <li>GB/T 9112~9124 钢制管法兰</li>
            <li>ASME B16.5 Pipe Flanges and Flanged Fittings</li>
            <li>EN 1092-1 Flanges and their joints</li>
            <li>JIS B2220 钢制管法兰</li>
        </ul>
        """
    
    def load_flange_data(self):
        """加载法兰数据"""
        # 模拟法兰数据库
        flange_data = {
            "HG/T 20592-WN-PN16-DN100": {
                "basic": {
                    "外径": 215, "螺栓孔中心圆直径": 180, "螺栓孔直径": 18,
                    "螺栓孔数量": 8, "法兰厚度": 24, "颈部高度": 52,
                    "密封面直径": 148, "密封面高度": 3
                },
                "bolt": {
                    "螺栓规格": "M16", "螺栓长度": 90, "螺栓数量": 8,
                    "螺纹长度": 30, "螺栓材料": "8.8级"
                },
                "weight": {
                    "理论重量": 10.5, "材料": "20#", "标准号": "HG/T 20592-2009"
                }
            },
            "HG/T 20592-WN-PN25-DN100": {
                "basic": {
                    "外径": 230, "螺栓孔中心圆直径": 190, "螺栓孔直径": 22,
                    "螺栓孔数量": 8, "法兰厚度": 26, "颈部高度": 56,
                    "密封面直径": 148, "密封面高度": 3
                },
                "bolt": {
                    "螺栓规格": "M20", "螺栓长度": 100, "螺栓数量": 8,
                    "螺纹长度": 35, "螺栓材料": "8.8级"
                },
                "weight": {
                    "理论重量": 12.8, "材料": "20#", "标准号": "HG/T 20592-2009"
                }
            },
            "HG/T 20592-SO-PN16-DN100": {
                "basic": {
                    "外径": 215, "螺栓孔中心圆直径": 180, "螺栓孔直径": 18,
                    "螺栓孔数量": 8, "法兰厚度": 20, "内径": 108,
                    "密封面直径": 148, "密封面高度": 3
                },
                "bolt": {
                    "螺栓规格": "M16", "螺栓长度": 75, "螺栓数量": 8,
                    "螺纹长度": 25, "螺栓材料": "8.8级"
                },
                "weight": {
                    "理论重量": 6.2, "材料": "Q235A", "标准号": "HG/T 20592-2009"
                }
            },
            "ANSI B16.5-Weld Neck-Class150-DN100": {
                "basic": {
                    "外径": 229, "螺栓孔中心圆直径": 190.5, "螺栓孔直径": 19,
                    "螺栓孔数量": 8, "法兰厚度": 22.4, "颈部高度": 64,
                    "密封面直径": 155.6, "密封面高度": 6.4
                },
                "bolt": {
                    "螺栓规格": "5/8''", "螺栓长度": 102, "螺栓数量": 8,
                    "螺纹长度": 32, "螺栓材料": "ASTM A193 B7"
                },
                "weight": {
                    "理论重量": 11.2, "材料": "A105", "标准号": "ASME B16.5"
                }
            }
        }
        
        return flange_data
    
    def query_flange_size(self):
        """查询法兰尺寸"""
        try:
            # 获取查询条件
            standard = self.standard_combo.currentText()
            flange_type = self.type_combo.currentText()
            pressure = self.pressure_combo.currentText()
            dn = self.dn_combo.currentText()
            face_type = self.face_type_combo.currentText()
            material = self.material_combo.currentText()
            
            # 构建查询键
            query_key = f"{standard}-{flange_type.split('(')[0]}-{pressure}-DN{dn}"
            
            # 查询数据
            if query_key in self.flange_data:
                data = self.flange_data[query_key]
                self.display_basic_sizes(data["basic"])
                self.display_bolt_sizes(data["bolt"])
                self.display_weight_material(data["weight"])
            else:
                # 如果没有精确匹配，显示标准数据
                self.display_standard_data(standard, flange_type, pressure, dn)
                
        except Exception as e:
            QMessageBox.warning(self, "查询错误", f"查询过程中发生错误: {str(e)}")
    
    def display_basic_sizes(self, basic_data):
        """显示基本尺寸"""
        basic_sizes = [
            ["外径 D", f"{basic_data['外径']}", "mm"],
            ["螺栓孔中心圆直径 K", f"{basic_data['螺栓孔中心圆直径']}", "mm"],
            ["螺栓孔直径 L", f"{basic_data['螺栓孔直径']}", "mm"],
            ["螺栓孔数量 n", f"{basic_data['螺栓孔数量']}", "个"],
            ["法兰厚度 C", f"{basic_data['法兰厚度']}", "mm"]
        ]
        
        # 添加可选参数
        if '颈部高度' in basic_data:
            basic_sizes.append(["颈部高度 H", f"{basic_data['颈部高度']}", "mm"])
        if '内径' in basic_data:
            basic_sizes.append(["内径 B", f"{basic_data['内径']}", "mm"])
        if '密封面直径' in basic_data:
            basic_sizes.append(["密封面直径 d", f"{basic_data['密封面直径']}", "mm"])
        if '密封面高度' in basic_data:
            basic_sizes.append(["密封面高度 f", f"{basic_data['密封面高度']}", "mm"])
        
        self.update_table(self.basic_size_table, basic_sizes)
    
    def display_bolt_sizes(self, bolt_data):
        """显示螺栓尺寸"""
        bolt_sizes = [
            ["螺栓规格", bolt_data["螺栓规格"], "-"],
            ["螺栓数量", f"{bolt_data['螺栓数量']}", "个"],
            ["螺栓长度", f"{bolt_data['螺栓长度']}", "mm"],
            ["螺纹长度", f"{bolt_data['螺纹长度']}", "mm"],
            ["螺栓材料", bolt_data["螺栓材料"], "-"]
        ]
        
        self.update_table(self.bolt_size_table, bolt_sizes)
    
    def display_weight_material(self, weight_data):
        """显示重量和材料"""
        weight_material = [
            ["理论重量", f"{weight_data['理论重量']}", "kg"],
            ["材料", weight_data["材料"], "-"],
            ["标准号", weight_data["标准号"], "-"]
        ]
        
        self.update_table(self.weight_material_table, weight_material)
    
    def display_standard_data(self, standard, flange_type, pressure, dn):
        """显示标准数据"""
        # 基于标准的估算数据
        dn_int = int(dn)
        
        if standard == "HG/T 20592":
            if "WN" in flange_type:
                # 对焊法兰估算
                basic_data = {
                    "外径": 215 + (dn_int - 100) * 0.5,
                    "螺栓孔中心圆直径": 180 + (dn_int - 100) * 0.4,
                    "螺栓孔直径": 18,
                    "螺栓孔数量": 8,
                    "法兰厚度": 24,
                    "颈部高度": 52
                }
            else:
                # 平焊法兰估算
                basic_data = {
                    "外径": 215 + (dn_int - 100) * 0.5,
                    "螺栓孔中心圆直径": 180 + (dn_int - 100) * 0.4,
                    "螺栓孔直径": 18,
                    "螺栓孔数量": 8,
                    "法兰厚度": 20,
                    "内径": dn_int
                }
            
            bolt_data = {
                "螺栓规格": "M16",
                "螺栓长度": 90,
                "螺栓数量": 8,
                "螺纹长度": 30,
                "螺栓材料": "8.8级"
            }
            
            weight_data = {
                "理论重量": 10.5 * (dn_int / 100),
                "材料": "20#",
                "标准号": "HG/T 20592-2009"
            }
        
        elif standard == "ANSI B16.5":
            # ANSI标准估算
            basic_data = {
                "外径": 229 + (dn_int - 100) * 0.6,
                "螺栓孔中心圆直径": 190.5 + (dn_int - 100) * 0.5,
                "螺栓孔直径": 19,
                "螺栓孔数量": 8,
                "法兰厚度": 22.4,
                "颈部高度": 64
            }
            
            bolt_data = {
                "螺栓规格": "5/8''",
                "螺栓长度": 102,
                "螺栓数量": 8,
                "螺纹长度": 32,
                "螺栓材料": "ASTM A193 B7"
            }
            
            weight_data = {
                "理论重量": 11.2 * (dn_int / 100),
                "材料": "A105",
                "标准号": "ASME B16.5"
            }
        
        else:
            QMessageBox.information(self, "查询结果", "未找到精确匹配数据，请参考标准手册")
            return
        
        self.display_basic_sizes(basic_data)
        self.display_bolt_sizes(bolt_data)
        self.display_weight_material(weight_data)
        
        QMessageBox.information(self, "查询结果", "显示的是基于标准的估算数据，实际尺寸请参考相关标准手册。")
    
    def update_table(self, table, data):
        """更新表格数据"""
        table.setRowCount(len(data))
        for i, row_data in enumerate(data):
            for j, data_item in enumerate(row_data):
                item = QTableWidgetItem(data_item)
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(i, j, item)
        
        # 调整列宽
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
    
    def bolt_calculation(self):
        """螺栓计算"""
        try:
            standard = self.standard_combo.currentText()
            pressure = self.pressure_combo.currentText()
            dn = self.dn_combo.currentText()
            material = self.material_combo.currentText()
            
            # 简化的螺栓计算
            dn_int = int(dn)
            
            if "PN16" in pressure or "Class150" in pressure:
                bolt_size = "M16"
                bolt_count = 8
                bolt_length = 90
            elif "PN25" in pressure or "Class300" in pressure:
                bolt_size = "M20"
                bolt_count = 8
                bolt_length = 100
            elif "PN40" in pressure or "Class600" in pressure:
                bolt_size = "M24"
                bolt_count = 12
                bolt_length = 120
            else:
                bolt_size = "M16"
                bolt_count = 8
                bolt_length = 90
            
            # 计算预紧力
            if bolt_size == "M16":
                preload = 80  # kN
            elif bolt_size == "M20":
                preload = 125  # kN
            elif bolt_size == "M24":
                preload = 180  # kN
            else:
                preload = 80  # kN
            
            total_preload = preload * bolt_count
            
            result_text = f"""
            <h3>🔩 螺栓计算报告</h3>
            
            <table border="1" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #f8f9fa;">
                <td style="padding: 8px; font-weight: bold;">项目</td>
                <td style="padding: 8px;">计算结果</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">法兰规格</td>
                <td style="padding: 8px;">DN{dn} {pressure}</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">推荐螺栓规格</td>
                <td style="padding: 8px;">{bolt_size}</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">螺栓数量</td>
                <td style="padding: 8px;">{bolt_count}个</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">推荐螺栓长度</td>
                <td style="padding: 8px;">{bolt_length}mm</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">单颗螺栓预紧力</td>
                <td style="padding: 8px;">{preload} kN</td>
            </tr>
            <tr>
                <td style="padding: 8px; font-weight: bold;">总预紧力</td>
                <td style="padding: 8px;">{total_preload} kN</td>
            </tr>
            </table>
            
            <h4>🔧 安装建议</h4>
            <ul>
                <li>使用扭矩扳手按十字交叉顺序紧固</li>
                <li>最终扭矩值参考螺栓材料等级确定</li>
                <li>安装垫片时确保密封面清洁</li>
                <li>运行24小时后检查螺栓扭矩</li>
            </ul>
            """
            
            QMessageBox.information(self, "螺栓计算", result_text)
            
        except Exception as e:
            QMessageBox.warning(self, "计算错误", f"螺栓计算失败: {str(e)}")
    
    def clear_inputs(self):
        """清空输入"""
        self.standard_combo.setCurrentIndex(0)
        self.dn_combo.setCurrentIndex(0)
        self.material_combo.setCurrentIndex(0)
        self.basic_size_table.setRowCount(0)
        self.bolt_size_table.setRowCount(0)
        self.weight_material_table.setRowCount(0)

if __name__ == "__main__":
    # 测试代码
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    widget = FlangeSizeCalculator()
    widget.resize(900, 700)
    widget.show()
    
    sys.exit(app.exec())