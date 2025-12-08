from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
                              QLabel, QLineEdit, QComboBox, QPushButton, 
                              QTextEdit, QTableWidget, QTableWidgetItem,
                              QHeaderView, QMessageBox, QTabWidget, QDoubleSpinBox,
                              QCheckBox, QRadioButton, QButtonGroup, QScrollArea)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QDoubleValidator
import math

class CorrosionDataQuery(QWidget):
    """腐蚀数据查询计算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.corrosion_data = self.load_corrosion_data()
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("⚠️ 腐蚀数据查询")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 添加查询标签页
        self.query_tab = self.create_query_tab()
        self.tab_widget.addTab(self.query_tab, "🔍 腐蚀查询")
        
        # 添加材料库标签页
        self.material_tab = self.create_material_tab()
        self.tab_widget.addTab(self.material_tab, "📚 材料库")
        
        # 添加腐蚀类型标签页
        self.corrosion_types_tab = self.create_corrosion_types_tab()
        self.tab_widget.addTab(self.corrosion_types_tab, "🔬 腐蚀类型")
        
        main_layout.addWidget(self.tab_widget)
    
    def create_query_tab(self):
        """创建查询标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 查询条件组
        query_group = QGroupBox("🔍 查询条件")
        query_layout = QVBoxLayout(query_group)
        
        # 材料选择
        material_layout = QHBoxLayout()
        material_layout.addWidget(QLabel("材料类型:"))
        self.material_category_combo = QComboBox()
        self.material_category_combo.addItems([
            "碳钢", "不锈钢", "合金钢", "铜及铜合金", "铝及铝合金", 
            "钛及钛合金", "镍基合金", "塑料", "橡胶", "陶瓷"
        ])
        self.material_category_combo.currentTextChanged.connect(self.on_material_category_changed)
        material_layout.addWidget(self.material_category_combo)
        
        material_layout.addWidget(QLabel("具体材料:"))
        self.material_combo = QComboBox()
        material_layout.addWidget(self.material_combo)
        
        query_layout.addLayout(material_layout)
        
        # 介质选择
        medium_layout = QHBoxLayout()
        medium_layout.addWidget(QLabel("腐蚀介质:"))
        self.medium_category_combo = QComboBox()
        self.medium_category_combo.addItems([
            "酸类", "碱类", "盐类", "有机溶剂", "气体", "水及水溶液"
        ])
        self.medium_category_combo.currentTextChanged.connect(self.on_medium_category_changed)
        medium_layout.addWidget(self.medium_category_combo)
        
        medium_layout.addWidget(QLabel("具体介质:"))
        self.medium_combo = QComboBox()
        medium_layout.addWidget(self.medium_combo)
        
        query_layout.addLayout(medium_layout)
        
        # 条件参数
        condition_layout = QHBoxLayout()
        condition_layout.addWidget(QLabel("温度 (°C):"))
        self.temperature_input = QDoubleSpinBox()
        self.temperature_input.setRange(-50, 500)
        self.temperature_input.setValue(25)
        self.temperature_input.setSuffix(" °C")
        condition_layout.addWidget(self.temperature_input)
        
        condition_layout.addWidget(QLabel("浓度 (%):"))
        self.concentration_input = QDoubleSpinBox()
        self.concentration_input.setRange(0, 100)
        self.concentration_input.setValue(10)
        self.concentration_input.setSuffix(" %")
        condition_layout.addWidget(self.concentration_input)
        
        condition_layout.addWidget(QLabel("pH值:"))
        self.ph_input = QDoubleSpinBox()
        self.ph_input.setRange(0, 14)
        self.ph_input.setValue(7)
        condition_layout.addWidget(self.ph_input)
        
        query_layout.addLayout(condition_layout)
        
        layout.addWidget(query_group)
        
        # 按钮组
        button_layout = QHBoxLayout()
        self.query_btn = QPushButton("🚀 查询腐蚀数据")
        self.query_btn.clicked.connect(self.query_corrosion_data)
        self.query_btn.setStyleSheet("QPushButton { background-color: #c0392b; color: white; font-weight: bold; }")
        button_layout.addWidget(self.query_btn)
        
        self.advanced_query_btn = QPushButton("🔧 高级查询")
        self.advanced_query_btn.clicked.connect(self.advanced_query)
        self.advanced_query_btn.setStyleSheet("QPushButton { background-color: #3498db; color: white; }")
        button_layout.addWidget(self.advanced_query_btn)
        
        self.clear_btn = QPushButton("🗑️ 清空")
        self.clear_btn.clicked.connect(self.clear_inputs)
        self.clear_btn.setStyleSheet("QPushButton { background-color: #95a5a6; color: white; }")
        button_layout.addWidget(self.clear_btn)
        
        layout.addLayout(button_layout)
        
        # 结果显示组
        result_group = QGroupBox("📈 查询结果")
        result_layout = QVBoxLayout(result_group)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setMaximumHeight(200)
        result_layout.addWidget(self.result_text)
        
        layout.addWidget(result_group)
        
        # 详细数据表
        detail_group = QGroupBox("📋 详细数据")
        detail_layout = QVBoxLayout(detail_group)
        
        self.detail_table = QTableWidget()
        self.detail_table.setColumnCount(4)
        self.detail_table.setHorizontalHeaderLabels(["参数", "数值", "单位", "说明"])
        detail_layout.addWidget(self.detail_table)
        
        layout.addWidget(detail_group)
        
        # 初始化下拉框
        self.on_material_category_changed(self.material_category_combo.currentText())
        self.on_medium_category_changed(self.medium_category_combo.currentText())
        
        return tab
    
    def on_material_category_changed(self, category):
        """材料类别改变事件"""
        materials = {
            "碳钢": ["Q235", "Q345", "20#钢", "45#钢", "A36", "A53"],
            "不锈钢": ["304", "304L", "316", "316L", "321", "310S", "2205", "2507"],
            "合金钢": ["15CrMo", "12Cr1MoV", "P91", "P92", "4130", "4140"],
            "铜及铜合金": ["纯铜", "黄铜", "青铜", "白铜", "铜镍合金"],
            "铝及铝合金": ["1060", "3003", "5052", "6061", "7075"],
            "钛及钛合金": ["纯钛", "Ti-6Al-4V", "Ti-0.2Pd"],
            "镍基合金": ["Inconel 600", "Inconel 625", "Hastelloy C276", "Monel 400"],
            "塑料": ["PVC", "PP", "PE", "PTFE", "PVDF"],
            "橡胶": ["NBR", "EPDM", "FKM", "CR", "SBR"],
            "陶瓷": ["氧化铝", "碳化硅", "氧化锆", "氮化硅"]
        }
        
        self.material_combo.clear()
        if category in materials:
            self.material_combo.addItems(materials[category])
    
    def on_medium_category_changed(self, category):
        """介质类别改变事件"""
        mediums = {
            "酸类": ["盐酸", "硫酸", "硝酸", "磷酸", "醋酸", "氢氟酸", "柠檬酸"],
            "碱类": ["氢氧化钠", "氢氧化钾", "氨水", "碳酸钠", "石灰水"],
            "盐类": ["氯化钠", "氯化钾", "硫酸钠", "碳酸氢钠", "氯化钙", "硫酸铜"],
            "有机溶剂": ["甲醇", "乙醇", "丙酮", "苯", "甲苯", "二甲苯", "氯仿"],
            "气体": ["氧气", "氯气", "硫化氢", "二氧化碳", "氨气", "二氧化硫"],
            "水及水溶液": ["纯水", "自来水", "海水", "河水", "冷却水", "锅炉水"]
        }
        
        self.medium_combo.clear()
        if category in mediums:
            self.medium_combo.addItems(mediums[category])
    
    def create_material_tab(self):
        """创建材料库标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 材料库说明
        info_label = QLabel("常用工程材料耐腐蚀性能参考")
        info_label.setFont(QFont("Arial", 12, QFont.Bold))
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)
        
        # 材料参数表
        material_table = QTableWidget()
        material_table.setColumnCount(6)
        material_table.setHorizontalHeaderLabels(["材料", "主要成分", "适用温度(°C)", "主要耐腐蚀介质", "不耐腐蚀介质", "应用领域"])
        
        material_data = [
            ["304不锈钢", "Cr18Ni9", "-270~800", "硝酸、有机酸、碱", "盐酸、氯化物", "化工、食品、医药"],
            ["316不锈钢", "Cr17Ni12Mo2", "-270~800", "硫酸、磷酸、有机酸", "盐酸、氢氟酸", "化工、海洋、医药"],
            ["碳钢Q235", "Fe-C", "-20~400", "碱、大气、水", "酸、氧化性介质", "建筑、结构、管道"],
            ["哈氏合金C276", "Ni-Mo-Cr", "-196~1000", "盐酸、硫酸、氯化物", "强氧化性酸", "化工、环保、海洋"],
            ["钛TA2", "Ti", "-270~300", "氯化物、海水、硝酸", "氢氟酸、干氯气", "化工、海洋、航空"],
            ["聚四氟乙烯", "C2F4", "-200~260", "几乎所有化学品", "熔融碱金属", "化工、电子、医疗"],
            ["聚丙烯", "C3H6", "0~100", "酸、碱、盐溶液", "氧化性酸、溶剂", "化工、水处理"],
            ["丁腈橡胶", "NBR", "-30~120", "油类、脂肪烃", "酮、酯、臭氧", "密封、油管"]
        ]
        
        material_table.setRowCount(len(material_data))
        for i, row_data in enumerate(material_data):
            for j, data in enumerate(row_data):
                item = QTableWidgetItem(data)
                item.setTextAlignment(Qt.AlignCenter)
                material_table.setItem(i, j, item)
        
        # 调整列宽
        header = material_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)
        
        layout.addWidget(material_table)
        
        return tab
    
    def create_corrosion_types_tab(self):
        """创建腐蚀类型标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 腐蚀类型说明
        corrosion_text = QTextEdit()
        corrosion_text.setReadOnly(True)
        corrosion_text.setHtml(self.get_corrosion_types_html())
        layout.addWidget(corrosion_text)
        
        return tab
    
    def get_corrosion_types_html(self):
        """获取腐蚀类型HTML内容"""
        return """
        <h2>🔬 常见腐蚀类型</h2>
        
        <h3>1. 均匀腐蚀</h3>
        <p><b>特征：</b>整个金属表面均匀减薄</p>
        <p><b>原因：</b>化学或电化学反应在整个表面均匀发生</p>
        <p><b>防护：</b>选用耐腐蚀材料、涂层、缓蚀剂</p>
        
        <h3>2. 点蚀</h3>
        <p><b>特征：</b>局部区域形成小孔或凹坑</p>
        <p><b>原因：</b>局部破坏钝化膜，形成腐蚀电池</p>
        <p><b>易发材料：</b>不锈钢、铝、钛在含氯离子环境中</p>
        
        <h3>3. 缝隙腐蚀</h3>
        <p><b>特征：</b>在缝隙或遮蔽区域发生</p>
        <p><b>原因：</b>缝隙内外氧浓度差异形成浓差电池</p>
        <p><b>防护：</b>避免缝隙设计、使用密封剂</p>
        
        <h3>4. 电偶腐蚀</h3>
        <p><b>特征：</b>两种不同金属接触处的腐蚀</p>
        <p><b>原因：</b>电位差驱动电子流动</p>
        <p><b>防护：</b>避免异种金属接触、使用绝缘材料</p>
        
        <h3>5. 应力腐蚀开裂</h3>
        <p><b>特征：</b>在拉应力和特定介质共同作用下开裂</p>
        <p><b>原因：</b>应力加速局部腐蚀</p>
        <p><b>典型组合：</b>奥氏体不锈钢-氯离子、碳钢-硝酸盐</p>
        
        <h3>6. 晶间腐蚀</h3>
        <p><b>特征：</b>沿晶界选择性腐蚀</p>
        <p><b>原因：</b>晶界区与晶内成分差异</p>
        <p><b>典型材料：</b>不锈钢敏化态、铝合金</p>
        
        <h3>7. 腐蚀疲劳</h3>
        <p><b>特征：</b>交变应力与腐蚀介质共同作用</p>
        <p><b>原因：</b>腐蚀降低材料疲劳强度</p>
        <p><b>防护：</b>降低应力集中、表面处理</p>
        
        <h3>8. 冲刷腐蚀</h3>
        <p><b>特征：</b>流体冲刷加速腐蚀</p>
        <p><b>原因：</b>机械磨损与化学腐蚀协同作用</p>
        <p><b>防护：</b>降低流速、选用耐磨材料</p>
        
        <h3>📊 腐蚀速率等级</h3>
        <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr style="background-color: #3498db; color: white;">
            <th style="padding: 8px;">腐蚀速率(mm/年)</th>
            <th style="padding: 8px;">等级</th>
            <th style="padding: 8px;">评价</th>
        </tr>
        <tr>
            <td style="padding: 8px;">&lt; 0.025</td>
            <td style="padding: 8px;">优秀</td>
            <td style="padding: 8px;">完全耐蚀</td>
        </tr>
        <tr>
            <td style="padding: 8px;">0.025 - 0.05</td>
            <td style="padding: 8px;">良好</td>
            <td style="padding: 8px;">耐蚀</td>
        </tr>
        <tr>
            <td style="padding: 8px;">0.05 - 0.125</td>
            <td style="padding: 8px;">可用</td>
            <td style="padding: 8px;">尚耐蚀</td>
        </tr>
        <tr>
            <td style="padding: 8px;">0.125 - 0.25</td>
            <td style="padding: 8px;">差</td>
            <td style="padding: 8px;">不耐蚀</td>
        </tr>
        <tr>
            <td style="padding: 8px;">&gt; 0.25</td>
            <td style="padding: 8px;">很差</td>
            <td style="padding: 8px;">严重腐蚀</td>
        </tr>
        </table>
        
        <h3>📖 参考标准</h3>
        <ul>
            <li>GB/T 10123-2001 金属和合金的腐蚀基本术语</li>
            <li>GB/T 18590-2001 金属和合金的腐蚀点蚀评定方法</li>
            <li>ASTM G31 实验室浸渍腐蚀试验</li>
            <li>NACE MR0175 油田设备用金属材料抗硫化物应力开裂</li>
        </ul>
        """
    
    def load_corrosion_data(self):
        """加载腐蚀数据"""
        # 模拟腐蚀数据库
        corrosion_data = {
            # 碳钢数据
            "Q235-盐酸": {"rate": 12.5, "rating": "很差", "notes": "严重腐蚀，不推荐使用"},
            "Q235-硫酸": {"rate": 1.2, "rating": "差", "notes": "浓度<70%时可用，但腐蚀严重"},
            "Q235-氢氧化钠": {"rate": 0.02, "rating": "优秀", "notes": "常温下耐蚀性良好"},
            "Q235-海水": {"rate": 0.15, "rating": "差", "notes": "需要防护涂层"},
            
            # 不锈钢数据
            "304-盐酸": {"rate": 2.5, "rating": "很差", "notes": "不推荐使用，腐蚀严重"},
            "304-硫酸": {"rate": 0.08, "rating": "可用", "notes": "低浓度、常温下可用"},
            "304-硝酸": {"rate": 0.01, "rating": "优秀", "notes": "优良的耐硝酸性能"},
            "304-海水": {"rate": 0.05, "rating": "可用", "notes": "可能发生点蚀"},
            
            "316-盐酸": {"rate": 1.8, "rating": "很差", "notes": "不推荐使用"},
            "316-硫酸": {"rate": 0.05, "rating": "良好", "notes": "耐蚀性优于304"},
            "316-海水": {"rate": 0.02, "rating": "良好", "notes": "较好的耐海水性能"},
            
            # 钛数据
            "纯钛-盐酸": {"rate": 0.001, "rating": "优秀", "notes": "优良的耐盐酸性能"},
            "纯钛-海水": {"rate": 0.0001, "rating": "优秀", "notes": "极佳的耐海水性能"},
            "纯钛-硝酸": {"rate": 0.001, "rating": "优秀", "notes": "优良的耐硝酸性能"},
            
            # 哈氏合金数据
            "哈氏合金C276-盐酸": {"rate": 0.05, "rating": "可用", "notes": "在高温高浓度下仍可用"},
            "哈氏合金C276-硫酸": {"rate": 0.02, "rating": "良好", "notes": "优良的耐硫酸性能"},
            
            # 塑料数据
            "PVC-盐酸": {"rate": 0.001, "rating": "优秀", "notes": "优良的耐盐酸性能"},
            "PVC-硫酸": {"rate": 0.001, "rating": "优秀", "notes": "优良的耐硫酸性能"},
            "PTFE-盐酸": {"rate": 0.0001, "rating": "优秀", "notes": "几乎不腐蚀"}
        }
        
        return corrosion_data
    
    def query_corrosion_data(self):
        """查询腐蚀数据"""
        try:
            # 获取查询条件
            material_category = self.material_category_combo.currentText()
            material = self.material_combo.currentText()
            medium_category = self.medium_category_combo.currentText()
            medium = self.medium_combo.currentText()
            temperature = self.temperature_input.value()
            concentration = self.concentration_input.value()
            ph = self.ph_input.value()
            
            # 构建查询键
            query_key = f"{material}-{medium}"
            
            # 查询数据
            if query_key in self.corrosion_data:
                data = self.corrosion_data[query_key]
                self.display_results(data, material, medium, temperature, concentration)
                self.update_detail_table(data, material, medium, temperature, concentration)
            else:
                # 如果没有精确匹配，尝试模糊查询
                self.fuzzy_query(material, medium, temperature, concentration)
                
        except Exception as e:
            QMessageBox.warning(self, "查询错误", f"查询过程中发生错误: {str(e)}")
    
    def fuzzy_query(self, material, medium, temperature, concentration):
        """模糊查询"""
        # 查找相关数据
        related_data = []
        for key, value in self.corrosion_data.items():
            if material in key and medium in key:
                related_data.append((key, value))
        
        if related_data:
            # 显示相关数据
            result_text = f"<h3>🔍 相关腐蚀数据</h3>"
            result_text += f"<p>未找到精确匹配，以下是相关数据：</p>"
            result_text += "<table border='1' style='border-collapse: collapse; width: 100%;'>"
            result_text += "<tr style='background-color: #f8f9fa;'><th>材料-介质</th><th>腐蚀速率(mm/年)</th><th>评级</th><th>说明</th></tr>"
            
            for key, data in related_data:
                rate_color = self.get_rate_color(data["rate"])
                result_text += f"""
                <tr>
                    <td style='padding: 8px;'>{key}</td>
                    <td style='padding: 8px; color: {rate_color};'>{data['rate']}</td>
                    <td style='padding: 8px;'>{data['rating']}</td>
                    <td style='padding: 8px;'>{data['notes']}</td>
                </tr>
                """
            
            result_text += "</table>"
            self.result_text.setHtml(result_text)
            
            # 清空详细表格
            self.detail_table.setRowCount(0)
        else:
            QMessageBox.information(self, "查询结果", "未找到相关腐蚀数据")
    
    def get_rate_color(self, rate):
        """根据腐蚀速率获取颜色"""
        if rate < 0.025:
            return "green"
        elif rate < 0.05:
            return "blue"
        elif rate < 0.125:
            return "orange"
        else:
            return "red"
    
    def display_results(self, data, material, medium, temperature, concentration):
        """显示查询结果"""
        rate_color = self.get_rate_color(data["rate"])
        
        result_text = f"""
        <h3>⚠️ 腐蚀数据查询结果</h3>
        
        <table border="1" style="border-collapse: collapse; width: 100%;">
        <tr style="background-color: #f8f9fa;">
            <td style="padding: 8px; font-weight: bold;">项目</td>
            <td style="padding: 8px;">结果</td>
            <td style="padding: 8px;">说明</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">材料-介质</td>
            <td style="padding: 8px;">{material} - {medium}</td>
            <td style="padding: 8px;">查询组合</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">腐蚀速率</td>
            <td style="padding: 8px; color: {rate_color}; font-weight: bold;">{data['rate']} mm/年</td>
            <td style="padding: 8px;">年腐蚀深度</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">耐蚀评级</td>
            <td style="padding: 8px;">{data['rating']}</td>
            <td style="padding: 8px;">耐腐蚀性能等级</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">温度条件</td>
            <td style="padding: 8px;">{temperature} °C</td>
            <td style="padding: 8px;">操作温度</td>
        </tr>
        <tr>
            <td style="padding: 8px; font-weight: bold;">浓度条件</td>
            <td style="padding: 8px;">{concentration} %</td>
            <td style="padding: 8px;">介质浓度</td>
        </tr>
        </table>
        
        <h4>📝 说明与建议</h4>
        <p>{data['notes']}</p>
        """
        
        # 添加建议
        if data["rate"] < 0.05:
            result_text += "<p style='color: green;'>✅ <b>建议：</b>该材料在此介质中耐蚀性良好，可以选用。</p>"
        elif data["rate"] < 0.125:
            result_text += "<p style='color: orange;'>⚠️ <b>建议：</b>该材料在此介质中耐蚀性一般，需要定期检查和维护。</p>"
        else:
            result_text += "<p style='color: red;'>❌ <b>建议：</b>该材料在此介质中耐蚀性差，不推荐使用，请选用其他材料。</p>"
        
        self.result_text.setHtml(result_text)
    
    def update_detail_table(self, data, material, medium, temperature, concentration):
        """更新详细数据表"""
        # 计算使用寿命估算
        thickness_options = [3, 5, 8, 10]  # mm
        service_life = {}
        for thickness in thickness_options:
            if data["rate"] > 0:
                life = thickness / data["rate"]
                service_life[thickness] = life
        
        detail_data = [
            ["腐蚀速率", f"{data['rate']}", "mm/年", "年腐蚀深度"],
            ["耐蚀等级", data["rating"], "-", "耐腐蚀性能评级"],
            ["操作温度", f"{temperature}", "°C", "介质温度"],
            ["介质浓度", f"{concentration}", "%", "介质浓度"],
            ["pH值", f"{self.ph_input.value()}", "-", "介质酸碱度"],
        ]
        
        # 添加使用寿命估算
        for thickness, life in service_life.items():
            detail_data.append([
                f"{thickness}mm厚度寿命", 
                f"{life:.1f}", 
                "年", 
                f"假设腐蚀均匀，{thickness}mm厚度估算寿命"
            ])
        
        self.detail_table.setRowCount(len(detail_data))
        for i, row_data in enumerate(detail_data):
            for j, data in enumerate(row_data):
                item = QTableWidgetItem(data)
                item.setTextAlignment(Qt.AlignCenter)
                self.detail_table.setItem(i, j, item)
        
        # 调整列宽
        header = self.detail_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
    
    def advanced_query(self):
        """高级查询"""
        # 这里可以实现更复杂的查询逻辑
        QMessageBox.information(self, "高级查询", "高级查询功能正在开发中...")
    
    def clear_inputs(self):
        """清空输入"""
        self.material_category_combo.setCurrentIndex(0)
        self.medium_category_combo.setCurrentIndex(0)
        self.temperature_input.setValue(25)
        self.concentration_input.setValue(10)
        self.ph_input.setValue(7)
        self.result_text.clear()
        self.detail_table.setRowCount(0)

if __name__ == "__main__":
    # 测试代码
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    widget = CorrosionDataQuery()
    widget.resize(900, 700)
    widget.show()
    
    sys.exit(app.exec())