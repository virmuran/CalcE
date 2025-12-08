from threading import Thread
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QGroupBox, QTextEdit, QComboBox, QMessageBox, QFrame,
    QScrollArea, QDialog, QSpinBox, QButtonGroup, QGridLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar
)
from PySide6.QtCore import Qt, Signal, QThread  # 修复：使用 Signal 和 QThread
from PySide6.QtGui import QFont, QDoubleValidator
import math
import json
import time


class SolubilityWorker(QThread):  # 修复：继承自 QThread 而不是 Thread
    """溶解度查询工作线程"""
    finished = Signal(dict)  # 修复：使用 Signal 而不是 pyqtSignal
    error = Signal(str)      # 修复：使用 Signal 而不是 pyqtSignal
    
    def __init__(self, compound, solvent, temperature):
        super().__init__()
        self.compound = compound
        self.solvent = solvent
        self.temperature = temperature
    
    def run(self):
        try:
            # 模拟数据查询过程
            self.msleep(500)  # 使用 QThread 的 msleep
            
            result = self.query_solubility_data(
                self.compound, self.solvent, self.temperature
            )
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))
    
    def query_solubility_data(self, compound, solvent, temperature):
        """查询溶解度数据"""
        # 这里使用内置的溶解度数据库
        # 实际应用中可以从外部数据库或API获取数据
        solubility_data = self.get_solubility_database()
        
        key = f"{compound}_{solvent}"
        if key in solubility_data:
            base_data = solubility_data[key]
            solubility = self.calculate_temperature_effect(
                base_data, temperature
            )
            return {
                'compound': compound,
                'solvent': solvent,
                'temperature': temperature,
                'solubility': solubility,
                'unit': base_data['unit'],
                'temperature_range': base_data.get('temperature_range', '0-100'),
                'source': base_data.get('source', 'Handbook'),
                'notes': base_data.get('notes', ''),
                'confidence': 'High'
            }
        else:
            return {
                'compound': compound,
                'solvent': solvent,
                'temperature': temperature,
                'solubility': 'N/A',
                'unit': 'g/100g',
                'temperature_range': 'N/A',
                'source': 'Not Found',
                'notes': 'No data available for this compound-solvent pair',
                'confidence': 'Low'
            }
    
    def calculate_temperature_effect(self, base_data, temperature):
        """计算温度对溶解度的影响"""
        if 'solubility' not in base_data:
            return 'N/A'
        
        base_temp = base_data.get('base_temperature', 25)
        base_solubility = base_data['solubility']
        
        # 如果请求温度与基础温度相同，直接返回基础溶解度
        if temperature == base_temp:
            return base_solubility
        
        # 使用简化的温度影响模型
        # 实际应用中应使用更精确的模型或实验数据
        temp_coeff = base_data.get('temperature_coefficient', 0.02)  # 默认2%/°C
        
        if isinstance(base_solubility, (int, float)):
            # 数值型溶解度数据
            delta_temp = temperature - base_temp
            adjusted_solubility = base_solubility * (1 + temp_coeff * delta_temp)
            return max(0, adjusted_solubility)  # 确保非负
        else:
            # 字符串型数据（如"可溶"、"微溶"等）
            return base_solubility
    
    def get_solubility_database(self):
        """获取内置溶解度数据库"""
        return {
            # 无机盐在水中的溶解度
            "氯化钠_水": {
                "solubility": 35.7,
                "unit": "g/100g",
                "base_temperature": 20,
                "temperature_coefficient": 0.005,
                "temperature_range": "0-100",
                "source": "CRC Handbook",
                "notes": "温度对溶解度影响较小"
            },
            "氯化钾_水": {
                "solubility": 34.0,
                "unit": "g/100g", 
                "base_temperature": 20,
                "temperature_coefficient": 0.008,
                "temperature_range": "0-100",
                "source": "CRC Handbook",
                "notes": "溶解度随温度升高而增加"
            },
            "硫酸钠_水": {
                "solubility": 19.5,
                "unit": "g/100g",
                "base_temperature": 20,
                "temperature_coefficient": 0.015,
                "temperature_range": "0-32.4",
                "source": "CRC Handbook", 
                "notes": "在32.4°C时溶解度最大"
            },
            "碳酸钙_水": {
                "solubility": 0.0014,
                "unit": "g/100g",
                "base_temperature": 25,
                "temperature_coefficient": -0.02,
                "temperature_range": "0-100",
                "source": "CRC Handbook",
                "notes": "溶解度随温度升高而降低"
            },
            
            # 有机化合物在水中的溶解度
            "蔗糖_水": {
                "solubility": 211.5,
                "unit": "g/100g",
                "base_temperature": 20,
                "temperature_coefficient": 0.025,
                "temperature_range": "0-100", 
                "source": "CRC Handbook",
                "notes": "溶解度随温度显著增加"
            },
            "苯甲酸_水": {
                "solubility": 0.34,
                "unit": "g/100g",
                "base_temperature": 25,
                "temperature_coefficient": 0.03,
                "temperature_range": "0-100",
                "source": "Merck Index",
                "notes": "微溶于冷水，易溶于热水"
            },
            "阿司匹林_水": {
                "solubility": 0.33,
                "unit": "g/100g", 
                "base_temperature": 25,
                "temperature_coefficient": 0.02,
                "temperature_range": "15-40",
                "source": "Merck Index",
                "notes": "微溶于水"
            },
            "咖啡因_水": {
                "solubility": 2.17,
                "unit": "g/100g",
                "base_temperature": 25,
                "temperature_coefficient": 0.04,
                "temperature_range": "0-100",
                "source": "Merck Index", 
                "notes": "溶解度随温度显著增加"
            },
            
            # 在不同溶剂中的溶解度
            "氯化钠_乙醇": {
                "solubility": 0.065,
                "unit": "g/100g",
                "base_temperature": 25,
                "temperature_coefficient": 0.01,
                "temperature_range": "0-78",
                "source": "Handbook",
                "notes": "在乙醇中溶解度很低"
            },
            "蔗糖_乙醇": {
                "solubility": 0.6,
                "unit": "g/100g",
                "base_temperature": 20,
                "temperature_coefficient": 0.015,
                "temperature_range": "0-78", 
                "source": "Handbook",
                "notes": "在乙醇中微溶"
            },
            "碘_乙醇": {
                "solubility": 20.5,
                "unit": "g/100g",
                "base_temperature": 25,
                "temperature_coefficient": 0.02,
                "temperature_range": "0-78",
                "source": "Handbook",
                "notes": "易溶于乙醇"
            },
            "萘_乙醇": {
                "solubility": 19.5,
                "unit": "g/100g",
                "base_temperature": 25, 
                "temperature_coefficient": 0.025,
                "temperature_range": "0-78",
                "source": "Handbook",
                "notes": "在乙醇中溶解度较高"
            },
            
            # 定性溶解度描述
            "碳酸钙_盐酸": {
                "solubility": "可溶",
                "unit": "定性",
                "base_temperature": 25,
                "temperature_range": "0-100", 
                "source": "Chemical Properties",
                "notes": "与酸反应生成可溶性盐"
            },
            "氢氧化铝_氢氧化钠": {
                "solubility": "可溶",
                "unit": "定性",
                "base_temperature": 25,
                "temperature_range": "0-100",
                "source": "Chemical Properties",
                "notes": "两性氢氧化物，溶于强碱"
            }
        }


class SolidSolubilityCalculator(QWidget):
    """固体溶解度查询计算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.setup_ui()
        
    def setup_ui(self):
        """设置固体溶解度查询界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # 标题
        title_label = QLabel("🧪 固体溶解度查询")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # 说明文本
        desc_label = QLabel("查询固体在不同溶剂和温度条件下的溶解度数据")
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #7f8c8d; margin: 5px;")
        main_layout.addWidget(desc_label)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        
        # 查询条件组
        query_group = QGroupBox("查询条件")
        query_layout = QGridLayout(query_group)
        
        self.compound_input = QComboBox()
        self.compound_input.setEditable(True)
        self.compound_input.addItems([
            "氯化钠", "氯化钾", "硫酸钠", "碳酸钙", 
            "蔗糖", "苯甲酸", "阿司匹林", "咖啡因",
            "碘", "萘", "氢氧化铝", "硫酸钡"
        ])
        
        self.solvent_input = QComboBox()
        self.solvent_input.setEditable(True)
        self.solvent_input.addItems([
            "水", "乙醇", "甲醇", "丙酮", 
            "乙醚", "苯", "氯仿", "盐酸",
            "氢氧化钠", "硫酸"
        ])
        
        self.temperature_input = QLineEdit()
        self.temperature_input.setText("25")
        self.temperature_input.setValidator(QDoubleValidator(-273, 500, 1))
        
        self.pressure_input = QLineEdit()
        self.pressure_input.setText("101.3")
        self.pressure_input.setValidator(QDoubleValidator(50, 10000, 1))
        
        query_layout.addWidget(QLabel("化合物:"), 0, 0)
        query_layout.addWidget(self.compound_input, 0, 1, 1, 2)
        
        query_layout.addWidget(QLabel("溶剂:"), 0, 3)
        query_layout.addWidget(self.solvent_input, 0, 4, 1, 2)
        
        query_layout.addWidget(QLabel("温度:"), 1, 0)
        query_layout.addWidget(self.temperature_input, 1, 1)
        query_layout.addWidget(QLabel("°C"), 1, 2)
        
        query_layout.addWidget(QLabel("压力:"), 1, 3)
        query_layout.addWidget(self.pressure_input, 1, 4)
        query_layout.addWidget(QLabel("kPa"), 1, 5)
        
        scroll_layout.addWidget(query_group)
        
        # 按钮组
        button_layout = QHBoxLayout()
        
        self.query_btn = QPushButton("查询溶解度")
        self.query_btn.setStyleSheet("QPushButton { background-color: #3498db; color: white; padding: 8px; border-radius: 4px; }"
                                   "QPushButton:hover { background-color: #2980b9; }")
        self.query_btn.clicked.connect(self.query_solubility)
        
        self.clear_btn = QPushButton("清空")
        self.clear_btn.setStyleSheet("QPushButton { background-color: #95a5a6; color: white; padding: 8px; border-radius: 4px; }"
                                   "QPushButton:hover { background-color: #7f8c8d; }")
        self.clear_btn.clicked.connect(self.clear_inputs)
        
        button_layout.addWidget(self.query_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        
        scroll_layout.addLayout(button_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()  # 修复：使用 QProgressBar
        self.progress_bar.setVisible(False)
        scroll_layout.addWidget(self.progress_bar)
        
        # 查询结果
        result_group = QGroupBox("查询结果")
        result_layout = QGridLayout(result_group)  # 使用 GridLayout 替代 FormLayout
        
        self.compound_result = QLabel("--")
        self.solvent_result = QLabel("--")
        self.temperature_result = QLabel("--")
        self.solubility_result = QLabel("--")
        self.unit_result = QLabel("--")
        self.temperature_range_result = QLabel("--")
        self.source_result = QLabel("--")
        self.confidence_result = QLabel("--")
        self.notes_result = QLabel("--")
        
        result_layout.addWidget(QLabel("化合物:"), 0, 0)
        result_layout.addWidget(self.compound_result, 0, 1)
        result_layout.addWidget(QLabel("溶剂:"), 1, 0)
        result_layout.addWidget(self.solvent_result, 1, 1)
        result_layout.addWidget(QLabel("温度:"), 2, 0)
        result_layout.addWidget(self.temperature_result, 2, 1)
        result_layout.addWidget(QLabel("溶解度:"), 3, 0)
        result_layout.addWidget(self.solubility_result, 3, 1)
        result_layout.addWidget(QLabel("单位:"), 4, 0)
        result_layout.addWidget(self.unit_result, 4, 1)
        result_layout.addWidget(QLabel("温度范围:"), 5, 0)
        result_layout.addWidget(self.temperature_range_result, 5, 1)
        result_layout.addWidget(QLabel("数据来源:"), 6, 0)
        result_layout.addWidget(self.source_result, 6, 1)
        result_layout.addWidget(QLabel("置信度:"), 7, 0)
        result_layout.addWidget(self.confidence_result, 7, 1)
        result_layout.addWidget(QLabel("备注:"), 8, 0)
        result_layout.addWidget(self.notes_result, 8, 1)
        
        scroll_layout.addWidget(result_group)
        
        # 批量查询组
        batch_group = QGroupBox("批量查询")
        batch_layout = QVBoxLayout(batch_group)
        
        # 批量查询表格
        self.batch_table = QTableWidget()
        self.batch_table.setColumnCount(4)
        self.batch_table.setHorizontalHeaderLabels(["化合物", "溶剂", "温度(°C)", "溶解度"])
        batch_layout.addWidget(self.batch_table)
        
        # 批量查询按钮
        batch_button_layout = QHBoxLayout()
        
        self.add_row_btn = QPushButton("添加行")
        self.add_row_btn.clicked.connect(self.add_batch_row)
        
        self.batch_query_btn = QPushButton("批量查询")
        self.batch_query_btn.clicked.connect(self.batch_query)
        
        self.clear_batch_btn = QPushButton("清空表格")
        self.clear_batch_btn.clicked.connect(self.clear_batch_table)
        
        batch_button_layout.addWidget(self.add_row_btn)
        batch_button_layout.addWidget(self.batch_query_btn)
        batch_button_layout.addWidget(self.clear_batch_btn)
        batch_button_layout.addStretch()
        
        batch_layout.addLayout(batch_button_layout)
        
        scroll_layout.addWidget(batch_group)
        
        # 溶解度数据表
        data_table_group = QGroupBox("常见固体溶解度参考表")
        data_table_layout = QVBoxLayout(data_table_group)
        
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(5)
        self.data_table.setHorizontalHeaderLabels(["化合物", "溶剂", "温度(°C)", "溶解度", "单位"])
        self.populate_reference_table()
        data_table_layout.addWidget(self.data_table)
        
        scroll_layout.addWidget(data_table_group)
        
        # 计算说明
        info_text = QTextEdit()
        info_text.setMaximumHeight(150)
        info_text.setHtml("""
        <h4>计算说明:</h4>
        <ul>
        <li>溶解度定义：在一定温度和压力下，某固态物质在100克溶剂里达到饱和状态时所溶解的质量</li>
        <li>温度影响：大多数固体的溶解度随温度升高而增加，少数物质溶解度随温度变化不大或降低</li>
        <li>压力影响：压力对固体溶解度影响很小，通常可以忽略</li>
        <li>数据来源：CRC Handbook、Merck Index、化学性质手册等权威参考资料</li>
        <li>定性描述："易溶"（>10g/100g）、"可溶"（1-10g/100g）、"微溶"（0.1-1g/100g）、"难溶"（<0.1g/100g）</li>
        </ul>
        """)
        info_text.setReadOnly(True)
        scroll_layout.addWidget(info_text)
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # 初始化批量查询表格
        self.add_batch_row()
        
    def populate_reference_table(self):
        """填充参考数据表"""
        reference_data = [
            ["氯化钠", "水", "20", "35.7", "g/100g"],
            ["氯化钾", "水", "20", "34.0", "g/100g"],
            ["硫酸钠", "水", "20", "19.5", "g/100g"],
            ["碳酸钙", "水", "25", "0.0014", "g/100g"],
            ["蔗糖", "水", "20", "211.5", "g/100g"],
            ["苯甲酸", "水", "25", "0.34", "g/100g"],
            ["氯化钠", "乙醇", "25", "0.065", "g/100g"],
            ["碘", "乙醇", "25", "20.5", "g/100g"],
            ["萘", "乙醇", "25", "19.5", "g/100g"]
        ]
        
        self.data_table.setRowCount(len(reference_data))
        for i, row_data in enumerate(reference_data):
            for j, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                self.data_table.setItem(i, j, item)
        
        # 设置表格列宽
        header = self.data_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
    
    def add_batch_row(self):
        """添加批量查询行"""
        row_count = self.batch_table.rowCount()
        self.batch_table.setRowCount(row_count + 1)
        
        # 化合物列（下拉框）
        compound_combo = QComboBox()
        compound_combo.setEditable(True)
        compound_combo.addItems([
            "氯化钠", "氯化钾", "硫酸钠", "碳酸钙", 
            "蔗糖", "苯甲酸", "阿司匹林", "咖啡因"
        ])
        self.batch_table.setCellWidget(row_count, 0, compound_combo)
        
        # 溶剂列（下拉框）
        solvent_combo = QComboBox()
        solvent_combo.setEditable(True)
        solvent_combo.addItems(["水", "乙醇", "甲醇", "丙酮"])
        self.batch_table.setCellWidget(row_count, 1, solvent_combo)
        
        # 温度列（输入框）
        temp_edit = QLineEdit()
        temp_edit.setText("25")
        temp_edit.setValidator(QDoubleValidator(-273, 500, 1))
        self.batch_table.setCellWidget(row_count, 2, temp_edit)
        
        # 溶解度列（结果，初始为空）
        result_item = QTableWidgetItem("--")
        self.batch_table.setItem(row_count, 3, result_item)
    
    def clear_batch_table(self):
        """清空批量查询表格"""
        self.batch_table.setRowCount(0)
        self.add_batch_row()
    
    def clear_inputs(self):
        """清空所有输入"""
        self.compound_input.setCurrentIndex(0)
        self.solvent_input.setCurrentIndex(0)
        self.temperature_input.setText("25")
        self.pressure_input.setText("101.3")
        
        # 清空结果
        for label in [self.compound_result, self.solvent_result,
                     self.temperature_result, self.solubility_result,
                     self.unit_result, self.temperature_range_result,
                     self.source_result, self.confidence_result,
                     self.notes_result]:
            label.setText("--")
    
    def query_solubility(self):
        """查询溶解度数据"""
        compound = self.compound_input.currentText().strip()
        solvent = self.solvent_input.currentText().strip()
        temperature = float(self.temperature_input.text())
        
        if not compound or not solvent:
            self.show_error("请输入化合物和溶剂名称")
            return
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # 无限进度条
        self.query_btn.setEnabled(False)
        
        # 创建工作线程
        self.worker = SolubilityWorker(compound, solvent, temperature)
        self.worker.finished.connect(self.on_query_finished)
        self.worker.error.connect(self.on_query_error)
        self.worker.start()
    
    def batch_query(self):
        """批量查询溶解度"""
        row_count = self.batch_table.rowCount()
        
        for row in range(row_count):
            compound_widget = self.batch_table.cellWidget(row, 0)
            solvent_widget = self.batch_table.cellWidget(row, 1)
            temp_widget = self.batch_table.cellWidget(row, 2)
            
            if compound_widget and solvent_widget and temp_widget:
                compound = compound_widget.currentText().strip()
                solvent = solvent_widget.currentText().strip()
                
                try:
                    temperature = float(temp_widget.text())
                except ValueError:
                    temperature = 25
                
                # 执行查询（简化版本，实际应该使用工作线程）
                worker = SolubilityWorker(compound, solvent, temperature)
                result = worker.query_solubility_data(compound, solvent, temperature)
                
                # 更新表格
                solubility_text = f"{result['solubility']} {result['unit']}" if result['solubility'] != 'N/A' else "N/A"
                self.batch_table.item(row, 3).setText(solubility_text)
    
    def on_query_finished(self, result):
        """查询完成处理"""
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        self.query_btn.setEnabled(True)
        
        # 显示结果
        self.display_results(result)
    
    def on_query_error(self, error_message):
        """查询错误处理"""
        self.progress_bar.setVisible(False)
        self.query_btn.setEnabled(True)
        self.show_error(f"查询错误: {error_message}")
    
    def display_results(self, result):
        """显示查询结果"""
        self.compound_result.setText(result['compound'])
        self.solvent_result.setText(result['solvent'])
        self.temperature_result.setText(f"{result['temperature']} °C")
        
        if isinstance(result['solubility'], (int, float)):
            self.solubility_result.setText(f"{result['solubility']:.4f}")
        else:
            self.solubility_result.setText(result['solubility'])
            
        self.unit_result.setText(result['unit'])
        self.temperature_range_result.setText(result['temperature_range'])
        self.source_result.setText(result['source'])
        self.confidence_result.setText(result['confidence'])
        self.notes_result.setText(result['notes'])
        
        # 根据置信度设置颜色
        if result['confidence'] == 'High':
            self.confidence_result.setStyleSheet("color: green; font-weight: bold;")
        elif result['confidence'] == 'Medium':
            self.confidence_result.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.confidence_result.setStyleSheet("color: red; font-weight: bold;")
    
    def show_error(self, message):
        """显示错误信息"""
        for label in [self.compound_result, self.solvent_result,
                     self.temperature_result, self.solubility_result,
                     self.unit_result, self.temperature_range_result,
                     self.source_result, self.confidence_result,
                     self.notes_result]:
            label.setText("查询错误")
        
        self.confidence_result.setStyleSheet("color: red; font-weight: bold;")
        self.confidence_result.setText("Error")
        self.notes_result.setText(message)
        
        print(f"错误: {message}")


if __name__ == "__main__":
    # 测试代码
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    calculator = SolidSolubilityCalculator()
    calculator.resize(900, 800)
    calculator.show()
    
    sys.exit(app.exec())