# modules/process_design/tabs/equipment_dialogs.py
import sys
import os
import re
from datetime import datetime
from typing import Dict, Any

from PySide6.QtCore import Qt, QTimer, QPoint, QRect
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit,
    QPushButton, QComboBox, QCheckBox, QDoubleSpinBox, QSpinBox,
    QGroupBox, QFormLayout, QTabWidget, QScrollArea, QWidget,
    QDialogButtonBox, QTableWidget, QTableWidgetItem, QToolBar,
    QListWidget, QListWidgetItem, QMessageBox, QFileDialog,
    QToolTip
)

# 内联定义 EQUIPMENT_TYPES，避免循环导入
EQUIPMENT_TYPES = {
    "pump": {"name": "泵", "category": "P"},
    "tank": {"name": "储罐", "category": "T"},
    "reactor": {"name": "反应器", "category": "R"},
    "heat_exchanger": {"name": "换热器", "category": "E"},
    "column": {"name": "塔器", "category": "C"},
    "vessel": {"name": "容器", "category": "V"},
    "compressor": {"name": "压缩机", "category": "K"},
    "fan": {"name": "风机", "category": "B"},
    "filter": {"name": "过滤器", "category": "S"},
    "mixer": {"name": "混合器", "category": "M"},
    "conveyor": {"name": "输送机", "category": "V"},
    "valve": {"name": "阀门", "category": "X"},
    "instrument": {"name": "仪表", "category": "I"},
    "piping": {"name": "管道", "category": "L"},
    "other": {"name": "其他", "category": "O"},
}

# 导入设备ID生成器
from .equipment_id_generator import EquipmentIDGenerator


class ProjectInfoDialog(QDialog):
    """项目信息对话框 - 针对实际Excel文件格式"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("填写项目信息")
        self.setMinimumWidth(500)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        basic_group = QGroupBox("基本信息")
        basic_layout = QFormLayout(basic_group)
        
        self.project_name_input = QLineEdit()
        self.project_name_input.setText("某化工项目")
        self.project_name_input.setPlaceholderText("项目名称")
        
        self.sub_item_name_input = QLineEdit()
        self.sub_item_name_input.setText(f"子项-{datetime.now().strftime('%Y%m')}-001")
        self.sub_item_name_input.setPlaceholderText("子项名称")
        
        self.doc_no_input = QLineEdit()
        self.doc_no_input.setText("B-MD001")
        self.doc_no_input.setPlaceholderText("文件编号")
        
        basic_layout.addRow("项目名称:", self.project_name_input)
        basic_layout.addRow("子项名称:", self.sub_item_name_input)
        basic_layout.addRow("文件编号(Doc. No.):", self.doc_no_input)
        
        layout.addWidget(basic_group)
        
        design_group = QGroupBox("设计信息")
        design_layout = QFormLayout(design_group)
        
        self.speciality_combo = QComboBox()
        self.speciality_combo.addItems(["Mechnical", "Process", "Electrical", "Instrument", "Civil"])
        self.speciality_combo.setCurrentText("Mechnical")
        
        self.phase_combo = QComboBox()
        self.phase_combo.addItems(["Basic", "Detailed", "Construction", "Feasibility"])
        self.phase_combo.setCurrentText("Basic")
        
        self.revision_input = QLineEdit()
        self.revision_input.setText("A")
        
        self.date_input = QLineEdit()
        self.date_input.setText(datetime.now().strftime("%Y/%m/%d"))
        
        design_layout.addRow("专业(SPECIALITY):", self.speciality_combo)
        design_layout.addRow("阶段(PHASE):", self.phase_combo)
        design_layout.addRow("版次(REV.):", self.revision_input)
        design_layout.addRow("日期(D/M/Y):", self.date_input)
        
        layout.addWidget(design_group)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_project_info(self):
        """获取项目信息 - 针对实际Excel文件格式"""
        return {
            # 基本信息
            "project_name": self.project_name_input.text().strip(),
            "sub_item_name": self.sub_item_name_input.text().strip(),
            "doc_no": self.doc_no_input.text().strip(),
            
            # 设计信息
            "speciality": self.speciality_combo.currentText(),
            "phase": self.phase_combo.currentText(),
            "revision": self.revision_input.text().strip(),
            "date": self.date_input.text().strip(),
            
            # 兼容旧版本的字段
            "project_code": self.sub_item_name_input.text().strip(),  # 子项名称作为项目编号
            "design_phase": self.phase_combo.currentText(),  # 阶段作为设计阶段
            "department": self.speciality_combo.currentText(),  # 专业作为部门
            "project_location": "",  # 实际模板中没有项目地点字段
        }


class TemplateTypeDialog(QDialog):
    """模板类型选择对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择模板类型")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("请选择要创建的模板类型:"))
        
        self.template_type_combo = QComboBox()
        self.template_type_combo.addItems([
            "ACME模板"
        ])
        
        layout.addWidget(self.template_type_combo)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_template_type(self):
        return self.template_type_combo.currentText()


class BatchEditDialog(QDialog):
    """批量编辑对话框"""
    def __init__(self, equipment_ids, process_manager, parent=None):
        super().__init__(parent)
        self.equipment_ids = equipment_ids
        self.process_manager = process_manager
        self.setWindowTitle(f"批量编辑设备 ({len(equipment_ids)} 个)")

        self.setMinimumSize(600, 600)      # 最小宽度800，最小高度600
        self.setMaximumSize(1600, 900)     # 最大宽度1000，最大高度800
        self.resize(600, 600)             # 初始大小宽度900，高度700
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 基本信息组
        basic_group = QGroupBox("基本信息")
        basic_layout = QFormLayout(basic_group)
        
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("留空则不修改")
        basic_layout.addRow("型号:", self.model_input)
        
        self.manufacturer_input = QLineEdit()
        self.manufacturer_input.setPlaceholderText("留空则不修改")
        basic_layout.addRow("制造商:", self.manufacturer_input)
        
        layout.addWidget(basic_group)
        
        # PID和设计参数组
        design_group = QGroupBox("设计参数")
        design_layout = QFormLayout(design_group)
        
        self.pid_dwg_no_input = QLineEdit()
        self.pid_dwg_no_input.setPlaceholderText("留空则不修改")
        design_layout.addRow("P&ID图号:", self.pid_dwg_no_input)
        
        self.design_pressure_input = QLineEdit()
        self.design_pressure_input.setPlaceholderText("例如: 0.6 MPa 或 NP (常压)")
        design_layout.addRow("设计压力:", self.design_pressure_input)
        
        self.design_temperature_input = QLineEdit()
        self.design_temperature_input.setPlaceholderText("例如: 150 °C 或 NT (常温)")
        design_layout.addRow("设计温度:", self.design_temperature_input)
        
        self.operating_pressure_input = QLineEdit()
        self.operating_pressure_input.setPlaceholderText("例如: 0.5 MPa 或 NP (常压)")
        design_layout.addRow("操作压力:", self.operating_pressure_input)
        
        self.operating_temperature_input = QLineEdit()
        self.operating_temperature_input.setPlaceholderText("例如: 120 °C 或 NT (常温)")
        design_layout.addRow("操作温度:", self.operating_temperature_input)
        
        layout.addWidget(design_group)
        
        # 材质和保温组
        material_group = QGroupBox("材质和结构")
        material_layout = QFormLayout(material_group)
        
        self.material_input = QLineEdit()
        self.material_input.setPlaceholderText("留空则不修改")
        material_layout.addRow("材质:", self.material_input)
        
        self.insulation_input = QLineEdit()
        self.insulation_input.setPlaceholderText("留空则不修改")
        material_layout.addRow("保温:", self.insulation_input)
        
        self.dynamic_input = QLineEdit()
        self.dynamic_input.setPlaceholderText("例如: 1.2 (荷载系数)")
        material_layout.addRow("荷载系数:", self.dynamic_input)
        
        self.weight_estimate_input = QLineEdit()
        self.weight_estimate_input.setPlaceholderText("例如: 3.5 t")
        material_layout.addRow("单机重量:", self.weight_estimate_input)
        
        layout.addWidget(material_group)
        
        # 功率参数组
        power_group = QGroupBox("功率参数")
        power_layout = QFormLayout(power_group)
        
        self.single_power_input = QLineEdit()
        self.single_power_input.setPlaceholderText("例如: 15.5 kW")
        power_layout.addRow("单机功率:", self.single_power_input)
        
        self.operating_power_input = QLineEdit()
        self.operating_power_input.setPlaceholderText("例如: 15.5 kW")
        power_layout.addRow("运行功率:", self.operating_power_input)
        
        self.total_power_input = QLineEdit()
        self.total_power_input.setPlaceholderText("例如: 31.0 kW")
        power_layout.addRow("装机功率:", self.total_power_input)
        
        layout.addWidget(power_group)
        
        # 备注组
        other_group = QGroupBox("其他信息")
        other_layout = QFormLayout(other_group)
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(100)
        self.notes_input.setPlaceholderText("留空则不修改")
        other_layout.addRow("备注:", self.notes_input)
        
        layout.addWidget(other_group)
        
        # 提示信息
        layout.addWidget(QLabel("注意：空字段不会修改原有值"))
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.apply_changes)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def apply_changes(self):
        changes = {}
        
        # 状态
        status = self.status_combo.currentText()
        if status:
            changes['status'] = status
        
        # 安装位置
        location = self.location_input.text().strip()
        if location:
            changes['location'] = location
        
        # 型号
        model = self.model_input.text().strip()
        if model:
            changes['model'] = model
        
        # 制造商
        manufacturer = self.manufacturer_input.text().strip()
        if manufacturer:
            changes['manufacturer'] = manufacturer
        
        # PID图号
        pid_dwg_no = self.pid_dwg_no_input.text().strip()
        if pid_dwg_no:
            changes['pid_dwg_no'] = pid_dwg_no
        
        # 设计压力
        design_pressure = self.design_pressure_input.text().strip()
        if design_pressure:
            # 处理压力值，转换为合适格式
            if design_pressure.upper() in ['NP', 'NT', '']:
                changes['design_pressure'] = design_pressure.upper()
            else:
                # 尝试提取数字部分
                import re
                match = re.search(r'([\d\.]+)', design_pressure)
                if match:
                    try:
                        changes['design_pressure'] = float(match.group(1))
                    except ValueError:
                        changes['design_pressure'] = design_pressure
                else:
                    changes['design_pressure'] = design_pressure
        
        # 设计温度
        design_temperature = self.design_temperature_input.text().strip()
        if design_temperature:
            if design_temperature.upper() in ['NT', 'NP', '']:
                changes['design_temperature'] = design_temperature.upper()
            else:
                import re
                match = re.search(r'([\d\.]+)', design_temperature)
                if match:
                    try:
                        changes['design_temperature'] = float(match.group(1))
                    except ValueError:
                        changes['design_temperature'] = design_temperature
                else:
                    changes['design_temperature'] = design_temperature
        
        # 操作压力
        operating_pressure = self.operating_pressure_input.text().strip()
        if operating_pressure:
            if operating_pressure.upper() in ['NP', 'NT', '']:
                changes['operating_pressure'] = operating_pressure.upper()
            else:
                import re
                match = re.search(r'([\d\.]+)', operating_pressure)
                if match:
                    try:
                        changes['operating_pressure'] = float(match.group(1))
                    except ValueError:
                        changes['operating_pressure'] = operating_pressure
                else:
                    changes['operating_pressure'] = operating_pressure
        
        # 操作温度
        operating_temperature = self.operating_temperature_input.text().strip()
        if operating_temperature:
            if operating_temperature.upper() in ['NT', 'NP', '']:
                changes['operating_temperature'] = operating_temperature.upper()
            else:
                import re
                match = re.search(r'([\d\.]+)', operating_temperature)
                if match:
                    try:
                        changes['operating_temperature'] = float(match.group(1))
                    except ValueError:
                        changes['operating_temperature'] = operating_temperature
                else:
                    changes['operating_temperature'] = operating_temperature
        
        # 材质
        material = self.material_input.text().strip()
        if material:
            changes['material'] = material
        
        # 保温
        insulation = self.insulation_input.text().strip()
        if insulation:
            changes['insulation'] = insulation
        
        # 荷载系数
        dynamic = self.dynamic_input.text().strip()
        if dynamic:
            changes['dynamic'] = dynamic
        
        # 单机重量
        weight_estimate = self.weight_estimate_input.text().strip()
        if weight_estimate:
            # 提取数字部分
            import re
            match = re.search(r'([\d\.]+)', weight_estimate)
            if match:
                try:
                    changes['weight_estimate'] = float(match.group(1))
                except ValueError:
                    changes['weight_estimate'] = weight_estimate
            else:
                changes['weight_estimate'] = weight_estimate
        
        # 功率相关
        single_power = self.single_power_input.text().strip()
        if single_power:
            import re
            match = re.search(r'([\d\.]+)', single_power)
            if match:
                try:
                    changes['single_power'] = float(match.group(1))
                except ValueError:
                    changes['single_power'] = single_power
            else:
                changes['single_power'] = single_power
        
        operating_power = self.operating_power_input.text().strip()
        if operating_power:
            import re
            match = re.search(r'([\d\.]+)', operating_power)
            if match:
                try:
                    changes['operating_power'] = float(match.group(1))
                except ValueError:
                    changes['operating_power'] = operating_power
            else:
                changes['operating_power'] = operating_power
        
        total_power = self.total_power_input.text().strip()
        if total_power:
            import re
            match = re.search(r'([\d\.]+)', total_power)
            if match:
                try:
                    changes['total_power'] = float(match.group(1))
                except ValueError:
                    changes['total_power'] = total_power
            else:
                changes['total_power'] = total_power
        
        # 备注
        notes = self.notes_input.toPlainText().strip()
        if notes:
            changes['notes'] = notes
        
        if not changes:
            QMessageBox.warning(self, "警告", "没有修改任何字段")
            return
        
        success_count = 0
        failed_count = 0
        
        for equipment_id in self.equipment_ids:
            equipment = self.process_manager.get_equipment(equipment_id)
            if equipment:
                try:
                    # 应用所有更改
                    if 'status' in changes:
                        equipment.status = changes['status']
                    if 'location' in changes:
                        equipment.location = changes['location']
                    if 'model' in changes:
                        equipment.model = changes['model']
                    if 'manufacturer' in changes:
                        equipment.manufacturer = changes['manufacturer']
                    if 'pid_dwg_no' in changes:
                        equipment.pid_dwg_no = changes['pid_dwg_no']
                    if 'design_pressure' in changes:
                        equipment.design_pressure = changes['design_pressure']
                    if 'design_temperature' in changes:
                        equipment.design_temperature = changes['design_temperature']
                    if 'operating_pressure' in changes:
                        equipment.operating_pressure = changes['operating_pressure']
                    if 'operating_temperature' in changes:
                        equipment.operating_temperature = changes['operating_temperature']
                    if 'material' in changes:
                        equipment.material = changes['material']
                    if 'insulation' in changes:
                        equipment.insulation = changes['insulation']
                    if 'dynamic' in changes:
                        equipment.dynamic = changes['dynamic']
                    if 'weight_estimate' in changes:
                        equipment.weight_estimate = changes['weight_estimate']
                    if 'single_power' in changes:
                        equipment.single_power = changes['single_power']
                    if 'operating_power' in changes:
                        equipment.operating_power = changes['operating_power']
                    if 'total_power' in changes:
                        equipment.total_power = changes['total_power']
                    if 'notes' in changes:
                        equipment.notes = changes['notes']
                    
                    if self.process_manager.update_equipment(equipment):
                        success_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    print(f"更新设备 {equipment_id} 时出错: {e}")
                    failed_count += 1
        
        message = f"批量编辑完成\n\n成功: {success_count} 个设备"
        if failed_count > 0:
            message += f"\n失败: {failed_count} 个设备"
        
        QMessageBox.information(self, "批量编辑完成", message)
        self.accept()


class EquipmentDialog(QDialog):
    """设备对话框"""
    def __init__(self, parent=None, equipment=None):
        super().__init__(parent)
        self.parent_widget = parent
        self.equipment = equipment
        self.setWindowTitle("添加设备" if not equipment else "编辑设备")

        self.setMinimumSize(600, 600)      # 最小宽度900，最小高度700
        self.setMaximumSize(1600, 800)    # 最大宽度1200，最大高度1000
        self.resize(600, 600)            # 初始大小宽度1000，高度800
        
        self.spec_params = {}
        self.volume_widgets = {}
        
        # 初始化当前设备类型
        self.current_equipment_type = "其他"
        
        self.setup_ui()
        
        # 确保 type_combo 已经初始化后再调用
        if equipment:
            self.load_equipment_data()
        else:
            # 只有新建设备时才使用延迟调用
            QTimer.singleShot(150, lambda: self._on_type_changed_delayed(self.type_combo.currentText()))
    
        if not self.equipment:
            equipment_type = self.type_combo.currentText()
            self.generate_unique_code(equipment_type)
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        tab_widget = QTabWidget()
        
        # ==================== 基本信息标签页 ====================
        basic_tab = QWidget()
        basic_layout = QFormLayout(basic_tab)
        
        # 唯一编码
        self.unique_code_input = QLineEdit()
        self.unique_code_input.setReadOnly(True)  # 设置为只读
        
        # 设备位号
        self.equipment_id_input = QLineEdit()
        
        # 设备名称
        self.name_input = QLineEdit()
        
        # 英文描述
        self.description_en_input = QLineEdit()
        self.description_en_input.setPlaceholderText("自动从对照表获取，可修改")
        
        # 型号
        self.model_input = QLineEdit()
        
        # 制造商
        self.manufacturer_input = QLineEdit()
        
        # 设备类型
        type_group = QGroupBox("设备类型")
        type_layout = QHBoxLayout(type_group)
        
        self.type_combo = QComboBox()
        # 新设备类型分类
        equipment_types = [
            "A 搅拌设备类",
            "B 风机类", 
            "C 塔器",
            "D 槽罐",
            "E 换热设备类",
            "G 成粒成型设备类",
            "H 贮斗、料斗类",
            "J 喷射器类", 
            "K 压缩机类",
            "L 起重、装卸、包装机械设备类",
            "M 磨碎设备类、混合器类",
            "P 泵类",
            "R 反应器",
            "S 分离设备类", 
            "T 储罐",
            "U 公用辅助设备类",
            "V 固体输送类（刮板机、铰刀、提升机、皮带机）",
            "W 称重类设备",
            "X 成套设备类",
            "其他"
        ]        

        for eq_type in equipment_types:
            self.type_combo.addItem(eq_type)

        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.type_combo)
        type_layout.addStretch()

        # 添加到基本信息页
        basic_layout.addRow("唯一编码*:", self.unique_code_input)
        basic_layout.addRow("设备位号*:", self.equipment_id_input)
        basic_layout.addRow("设备名称(中文)*:", self.name_input)
        basic_layout.addRow("设备名称(英文):", self.description_en_input)
        basic_layout.addRow("型号:", self.model_input)
        basic_layout.addRow("制造商:", self.manufacturer_input)
        basic_layout.addRow(type_group)
        
        # 连接设备名称变化信号，自动更新英文描述
        self.name_input.textChanged.connect(self.update_english_name)
        
        tab_widget.addTab(basic_tab, "基本信息")
        
        # ==================== 技术规格标签页 ====================
        self.spec_tab = QWidget()
        self.spec_layout = QVBoxLayout(self.spec_tab)
        
        # 滚动区域，用于容纳技术规格表单
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.spec_form_layout = QFormLayout(scroll_content)
        scroll_area.setWidget(scroll_content)
        self.spec_layout.addWidget(scroll_area)
        
        # 设计操作参数组
        design_group = QGroupBox("设计操作参数")
        design_layout = QFormLayout(design_group)
        
        # 设计压力
        design_pressure_layout = QHBoxLayout()
        self.design_pressure_input = QDoubleSpinBox()
        self.design_pressure_input.setRange(0, 1000)
        self.design_pressure_input.setDecimals(3)
        self.design_pressure_input.setSuffix(" MPa")
        self.design_pressure_input.setMinimumWidth(100)
        
        self.normal_pressure_check = QCheckBox("常压 (0.1013 MPa)")
        self.normal_pressure_check.toggled.connect(self.on_normal_pressure_toggled)
        
        # 添加压力系数设置
        pressure_coeff_layout = QHBoxLayout()
        pressure_coeff_label = QLabel("压力系数:")
        self.pressure_coeff_spin = QDoubleSpinBox()
        self.pressure_coeff_spin.setRange(1.0, 2.0)
        self.pressure_coeff_spin.setDecimals(2)
        self.pressure_coeff_spin.setValue(1.1)  # 默认1.1倍
        self.pressure_coeff_spin.setMinimumWidth(60)
        self.pressure_coeff_spin.setToolTip("设计压力 = 操作压力 × 系数 (国标建议1.05-1.2)")
        
        # 自动计算复选框
        self.auto_calc_pressure_check = QCheckBox("自动计算")
        self.auto_calc_pressure_check.setChecked(True)  # 默认开启自动计算
        self.auto_calc_pressure_check.toggled.connect(self.on_auto_calc_pressure_toggled)
        
        pressure_coeff_layout.addWidget(pressure_coeff_label)
        pressure_coeff_layout.addWidget(self.pressure_coeff_spin)
        pressure_coeff_layout.addWidget(self.auto_calc_pressure_check)
        pressure_coeff_layout.addStretch()
        
        design_pressure_layout.addWidget(self.design_pressure_input)
        design_pressure_layout.addWidget(self.normal_pressure_check)
        design_pressure_layout.addLayout(pressure_coeff_layout)
        
        design_layout.addRow("设计压力:", design_pressure_layout)
        
        # 设计温度
        design_temperature_layout = QHBoxLayout()
        self.design_temperature_input = QDoubleSpinBox()
        self.design_temperature_input.setRange(-273, 1000)
        self.design_temperature_input.setDecimals(1)
        self.design_temperature_input.setSuffix(" °C")
        self.design_temperature_input.setMinimumWidth(100)
        
        self.normal_temperature_check = QCheckBox("常温 (25 °C)")
        self.normal_temperature_check.toggled.connect(self.on_normal_temperature_toggled)
        
        # 添加温度裕量设置
        temp_margin_layout = QHBoxLayout()
        temp_margin_label = QLabel("温度裕量:")
        self.temp_margin_spin = QDoubleSpinBox()
        self.temp_margin_spin.setRange(0, 100)
        self.temp_margin_spin.setDecimals(1)
        self.temp_margin_spin.setValue(10.0)  # 默认10°C
        self.temp_margin_spin.setSuffix(" °C")
        self.temp_margin_spin.setMinimumWidth(80)
        self.temp_margin_spin.setToolTip("设计温度 = 操作温度 + 裕量 (国标建议10-30°C)")
        
        # 自动计算复选框
        self.auto_calc_temp_check = QCheckBox("自动计算")
        self.auto_calc_temp_check.setChecked(True)  # 默认开启自动计算
        self.auto_calc_temp_check.toggled.connect(self.on_auto_calc_temp_toggled)
        
        temp_margin_layout.addWidget(temp_margin_label)
        temp_margin_layout.addWidget(self.temp_margin_spin)
        temp_margin_layout.addWidget(self.auto_calc_temp_check)
        temp_margin_layout.addStretch()
        
        design_temperature_layout.addWidget(self.design_temperature_input)
        design_temperature_layout.addWidget(self.normal_temperature_check)
        design_temperature_layout.addLayout(temp_margin_layout)
        
        design_layout.addRow("设计温度:", design_temperature_layout)
        
        # 操作压力
        operating_pressure_layout = QHBoxLayout()
        self.operating_pressure_input = QDoubleSpinBox()
        self.operating_pressure_input.setRange(0, 1000)
        self.operating_pressure_input.setDecimals(3)
        self.operating_pressure_input.setSuffix(" MPa")
        self.operating_pressure_input.setMinimumWidth(100)
        
        self.operating_normal_pressure_check = QCheckBox("常压 (0.1013 MPa)")
        self.operating_normal_pressure_check.toggled.connect(self.on_operating_normal_pressure_toggled)
        
        operating_pressure_layout.addWidget(self.operating_pressure_input)
        operating_pressure_layout.addWidget(self.operating_normal_pressure_check)
        operating_pressure_layout.addStretch()
        
        design_layout.addRow("操作压力:", operating_pressure_layout)
        
        # 操作温度
        operating_temperature_layout = QHBoxLayout()
        self.operating_temperature_input = QDoubleSpinBox()
        self.operating_temperature_input.setRange(-273, 1000)
        self.operating_temperature_input.setDecimals(1)
        self.operating_temperature_input.setSuffix(" °C")
        self.operating_temperature_input.setMinimumWidth(100)
        
        self.operating_normal_temperature_check = QCheckBox("常温 (25 °C)")
        self.operating_normal_temperature_check.toggled.connect(self.on_operating_normal_temperature_toggled)
        
        operating_temperature_layout.addWidget(self.operating_temperature_input)
        operating_temperature_layout.addWidget(self.operating_normal_temperature_check)
        operating_temperature_layout.addStretch()
        
        design_layout.addRow("操作温度:", operating_temperature_layout)
        
        # 操作压力输入框变化时触发计算
        self.operating_pressure_input.valueChanged.connect(self.on_operating_pressure_changed)
        # 操作温度输入框变化时触发计算
        self.operating_temperature_input.valueChanged.connect(self.on_operating_temperature_changed)
        
        # 当压力系数变化时也触发重新计算
        self.pressure_coeff_spin.valueChanged.connect(self.on_operating_pressure_changed)
        # 当温度裕量变化时也触发重新计算
        self.temp_margin_spin.valueChanged.connect(self.on_operating_temperature_changed)
        
        # 添加到技术规格页
        self.spec_form_layout.addRow(design_group)
        
        tab_widget.addTab(self.spec_tab, "技术规格")
        
        # ==================== 操作参数标签页 ====================
        operation_param_tab = QWidget()
        operation_param_layout = QVBoxLayout(operation_param_tab)
        
        # 设备数量组
        quantity_group = QGroupBox("设备数量")
        quantity_layout = QFormLayout(quantity_group)
        
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(1, 1000)
        self.quantity_input.setValue(1)
        self.quantity_input.valueChanged.connect(self.on_quantity_changed)
        quantity_layout.addRow("设备数量:", self.quantity_input)
        
        self.running_quantity_input = QSpinBox()
        self.running_quantity_input.setRange(1, 1000)
        self.running_quantity_input.setValue(1)
        self.running_quantity_input.valueChanged.connect(self.on_running_quantity_changed)
        quantity_layout.addRow("运行设备数量:", self.running_quantity_input)
        
        operation_param_layout.addWidget(quantity_group)
        
        # 功率参数组
        power_group = QGroupBox("功率参数")
        power_layout = QFormLayout(power_group)
        
        self.single_power_input = QDoubleSpinBox()
        self.single_power_input.setRange(0, 10000)
        self.single_power_input.setDecimals(2)
        self.single_power_input.setSuffix(" kW")
        self.single_power_input.valueChanged.connect(self.on_single_power_changed)
        power_layout.addRow("单机功率:", self.single_power_input)
        
        self.operating_power_input = QDoubleSpinBox()
        self.operating_power_input.setRange(0, 10000)
        self.operating_power_input.setDecimals(2)
        self.operating_power_input.setSuffix(" kW")
        power_layout.addRow("运行功率:", self.operating_power_input)
        
        self.total_power_input = QDoubleSpinBox()
        self.total_power_input.setRange(0, 100000)
        self.total_power_input.setDecimals(2)
        self.total_power_input.setSuffix(" kW")
        power_layout.addRow("装机功率:", self.total_power_input)
        
        # 连接功率计算信号
        self.quantity_input.valueChanged.connect(self.calculate_total_power)
        self.running_quantity_input.valueChanged.connect(self.calculate_operating_power)
        self.single_power_input.valueChanged.connect(self.calculate_operating_power)
        self.single_power_input.valueChanged.connect(self.calculate_total_power)
        
        operation_param_layout.addWidget(power_group)
        
        # 材质和重量组
        material_weight_group = QGroupBox("材质和重量")
        material_weight_layout = QFormLayout(material_weight_group)
        
        self.material_input = QLineEdit()
        self.material_input.setPlaceholderText("材质")
        material_weight_layout.addRow("材质:", self.material_input)
        
        self.insulation_input = QLineEdit()
        self.insulation_input.setPlaceholderText("保温")
        material_weight_layout.addRow("保温:", self.insulation_input)
        
        self.weight_estimate_input = QDoubleSpinBox()
        self.weight_estimate_input.setRange(0, 1000)
        self.weight_estimate_input.setDecimals(2)
        self.weight_estimate_input.setSuffix(" t")
        material_weight_layout.addRow("单机重量:", self.weight_estimate_input)
        
        self.operating_weight_input = QDoubleSpinBox()
        self.operating_weight_input.setRange(0, 1000)
        self.operating_weight_input.setDecimals(2)
        self.operating_weight_input.setSuffix(" t")
        material_weight_layout.addRow("操作重量:", self.operating_weight_input)
        
        self.total_weight_input = QDoubleSpinBox()
        self.total_weight_input.setRange(0, 10000)
        self.total_weight_input.setDecimals(2)
        self.total_weight_input.setSuffix(" t")
        material_weight_layout.addRow("总重量:", self.total_weight_input)
        
        operation_param_layout.addWidget(material_weight_group)
        operation_param_layout.addStretch()
        
        tab_widget.addTab(operation_param_tab, "操作参数")
        
        # ==================== 其他标签页 ====================
        other_tab = QWidget()
        other_layout = QVBoxLayout(other_tab)
        
        # P&ID和其他信息组
        pid_info_group = QGroupBox("P&ID和费用信息")
        pid_info_layout = QFormLayout(pid_info_group)
        
        self.pid_dwg_no_input = QLineEdit()
        self.pid_dwg_no_input.setPlaceholderText("P&ID图号")
        pid_info_layout.addRow("P&ID图号:", self.pid_dwg_no_input)
        
        self.unit_price_input = QDoubleSpinBox()
        self.unit_price_input.setRange(0, 10000000)
        self.unit_price_input.setDecimals(2)
        self.unit_price_input.setPrefix("¥ ")
        pid_info_layout.addRow("单价:", self.unit_price_input)
        
        self.total_price_input = QDoubleSpinBox()
        self.total_price_input.setRange(0, 10000000)
        self.total_price_input.setDecimals(2)
        self.total_price_input.setPrefix("¥ ")
        pid_info_layout.addRow("总价:", self.total_price_input)
        
        self.dynamic_input = QLineEdit()
        self.dynamic_input.setPlaceholderText("荷载系数")
        pid_info_layout.addRow("荷载系数:", self.dynamic_input)
        
        other_layout.addWidget(pid_info_group)
        
        # 备注信息组
        notes_group = QGroupBox("备注信息")
        notes_layout = QVBoxLayout(notes_group)
        
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("备注信息...")
        self.notes_input.setMaximumHeight(200)
        notes_layout.addWidget(self.notes_input)
        
        other_layout.addWidget(notes_group)
        other_layout.addStretch()
        
        tab_widget.addTab(other_tab, "其他")
        
        # ==================== 对话框底部区域 ====================
        layout.addWidget(tab_widget)
        
        self.validation_label = QLabel()
        self.validation_label.setStyleSheet("color: red;")
        layout.addWidget(self.validation_label)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # 如果是新建设备，自动生成唯一编码
        if not self.equipment:
            equipment_type = self.type_combo.currentText()
            self.generate_unique_code(equipment_type)
        
        # 监听设备类型变化，如果唯一编码为空则重新生成
        self.type_combo.currentTextChanged.connect(self.on_equipment_type_changed)
        
        # 延迟初始化技术规格字段
        QTimer.singleShot(100, self.delayed_setup_spec_fields)

    def on_auto_calc_pressure_toggled(self, checked):
        """自动计算设计压力复选框状态变化"""
        if checked:
            # 启用自动计算，触发一次计算
            self.on_operating_pressure_changed()
            # 锁定压力系数输入框（仍可编辑系数，但设计压力会自动计算）
            self.pressure_coeff_spin.setEnabled(True)
        else:
            # 禁用自动计算，用户可手动输入设计压力
            self.pressure_coeff_spin.setEnabled(False)
            QToolTip.showText(
                self.mapToGlobal(QPoint(0, 0)),
                "已禁用自动计算，请手动输入设计压力值",
                self, QRect(), 2000
            )

    def on_auto_calc_temp_toggled(self, checked):
        """自动计算设计温度复选框状态变化"""
        if checked:
            # 启用自动计算，触发一次计算
            self.on_operating_temperature_changed()
            # 锁定温度裕量输入框
            self.temp_margin_spin.setEnabled(True)
        else:
            # 禁用自动计算，用户可手动输入设计温度
            self.temp_margin_spin.setEnabled(False)
            QToolTip.showText(
                self.mapToGlobal(QPoint(0, 0)),
                "已禁用自动计算，请手动输入设计温度值",
                self, QRect(), 2000
            )

    def on_operating_pressure_changed(self):
        """操作压力变化时，自动计算设计压力"""
        if not self.auto_calc_pressure_check.isChecked():
            return  # 自动计算未启用
        
        if self.normal_pressure_check.isChecked():
            # 如果是常压，设计压力也是常压
            self.design_pressure_input.setValue(0.1013)
            self.normal_pressure_check.setChecked(True)
        else:
            # 获取操作压力值
            op_pressure = self.operating_pressure_input.value()
            
            # 计算设计压力：操作压力 × 压力系数
            pressure_coeff = self.pressure_coeff_spin.value()
            design_pressure = op_pressure * pressure_coeff
            
            # 设置设计压力值
            self.design_pressure_input.setValue(round(design_pressure, 3))
            
            # 如果操作压力不是常压，确保设计压力也不是常压
            if not self.operating_normal_pressure_check.isChecked():
                self.normal_pressure_check.setChecked(False)

    def on_operating_temperature_changed(self):
        """操作温度变化时，自动计算设计温度"""
        if not self.auto_calc_temp_check.isChecked():
            return  # 自动计算未启用
        
        if self.normal_temperature_check.isChecked():
            # 如果是常温，设计温度也是常温
            self.design_temperature_input.setValue(25.0)
            self.normal_temperature_check.setChecked(True)
        else:
            # 获取操作温度值
            op_temperature = self.operating_temperature_input.value()
            
            # 计算设计温度：操作温度 + 温度裕量
            temp_margin = self.temp_margin_spin.value()
            design_temperature = op_temperature + temp_margin
            
            # 设置设计温度值
            self.design_temperature_input.setValue(round(design_temperature, 1))
            
            # 如果操作温度不是常温，确保设计温度也不是常温
            if not self.operating_normal_temperature_check.isChecked():
                self.normal_temperature_check.setChecked(False)
        
    def delayed_setup_spec_fields(self):
        """延迟初始化技术规格字段，确保UI完全加载"""
        try:
            equipment_type = self.type_combo.currentText()
            # 新建设备时才需要重新创建字段
            force_recreate = not self.equipment
            self.setup_specification_fields(equipment_type, force_recreate)
        except Exception as e:
            print(f"初始化技术规格字段时出错: {e}")
            # 使用默认类型
            self.setup_specification_fields("其他", force_recreate)
        
    def on_equipment_type_changed(self, equipment_type):
        """设备类型变化时，如果唯一编码为空则重新生成"""
        if not self.unique_code_input.text():
            self.generate_unique_code(equipment_type)
    
    def generate_unique_code(self, equipment_type):
        """生成唯一编码"""
        try:
            unique_code = EquipmentIDGenerator.generate_equipment_id(
                equipment_type, 
                custom_seed=self.name_input.text()  # 使用设备名称作为种子
            )
            self.unique_code_input.setText(unique_code)
        except Exception as e:
            print(f"❌ 生成唯一编码时出错: {e}")
            # 备选方案：使用简单UUID
            import uuid
            unique_code = f"{equipment_type[:1]}_{str(uuid.uuid4())[:8].upper()}"
            self.unique_code_input.setText(unique_code)
    
    def setup_specification_fields(self, equipment_type=None, force_recreate=True):
        """设置技术规格字段
        Args:
            equipment_type: 设备类型
            force_recreate: 是否强制重新创建字段（默认为True，编辑设备时为False）
        """
        if equipment_type is None:
            try:
                equipment_type = self.type_combo.currentText()
            except Exception:
                equipment_type = "其他"
        
        # 只有在需要重新创建时才清除并重新创建字段
        if force_recreate or not self.spec_params:
            self.clear_layout(self.spec_form_layout)
            self.spec_params = {}
            self.volume_widgets = {}
            
            # 根据新设备类型设置不同的规格字段
            if equipment_type == "A 搅拌设备类":
                self.add_spec_field("搅拌转速", "agitation_speed", "rpm")
                self.add_spec_field("搅拌功率", "agitation_power", "kW")
                self.add_spec_field("搅拌直径", "agitation_diameter", "mm")
                self.add_spec_field("搅拌类型", "agitation_type", "")
                
            elif equipment_type == "B 风机类":
                self.add_spec_field("风量", "air_flow", "m³/h")
                self.add_spec_field("风压", "air_pressure", "Pa")
                self.add_spec_field("转速", "fan_speed", "rpm")
                self.add_spec_field("风机类型", "fan_type", "")
                
            elif equipment_type == "C 塔器":
                self.add_spec_field("塔径", "tower_diameter", "mm")
                self.add_spec_field("塔高", "tower_height", "mm")
                self.add_spec_field("填料高度", "packing_height", "mm")
                self.add_spec_field("塔器类型", "tower_type", "")
                
            elif equipment_type == "D 槽罐":
                # 槽罐的参数（矩形或方形）
                self.add_spec_field("长度", "length", "mm")
                self.add_spec_field("宽度", "width", "mm")
                self.add_spec_field("高度", "height", "mm")
                
                # 添加容积字段，并附带计算按钮
                volume_layout = QHBoxLayout()
                
                # 容积输入框
                self.volume_input = QDoubleSpinBox()
                self.volume_input.setRange(0, 1000000)
                self.volume_input.setDecimals(3)
                self.volume_input.setSuffix(" m³")
                self.volume_input.setMinimumWidth(120)
                
                # 计算按钮
                calculate_btn = QPushButton("计算")
                calculate_btn.setMaximumWidth(60)
                calculate_btn.clicked.connect(self.calculate_trough_volume)
                
                # 手动修改标记
                self.volume_manually_modified = False
                
                # 连接容积输入框的信号
                self.volume_input.valueChanged.connect(self.on_volume_modified)
                
                volume_layout.addWidget(self.volume_input)
                volume_layout.addWidget(calculate_btn)
                volume_layout.addStretch()
                
                self.spec_form_layout.addRow("容积:", volume_layout)
                
                # 将容积字段添加到参数字典中
                self.spec_params['volume'] = {
                    'label': '容积',
                    'widget': self.volume_input,
                    'unit': 'm³',
                    'type': 'spinbox'
                }
                
                # 保存长、宽、高的widget引用，用于计算
                self.volume_widgets['length'] = self.spec_params.get('length', {}).get('widget')
                self.volume_widgets['width'] = self.spec_params.get('width', {}).get('widget')
                self.volume_widgets['height'] = self.spec_params.get('height', {}).get('widget')
                
                # 添加其他槽罐参数
                self.add_spec_field("壁厚", "wall_thickness", "mm")
                self.add_spec_field("设计液位", "design_level", "m")
                
            elif equipment_type == "E 换热设备类":
                self.add_spec_field("换热面积", "heat_exchange_area", "m²")
                self.add_spec_field("管程数", "tube_passes", "")
                self.add_spec_field("壳程数", "shell_passes", "")
                self.add_spec_field("管径", "tube_diameter", "mm")
                self.add_spec_field("管长", "tube_length", "mm")
                
            elif equipment_type == "G 成粒成型设备类":
                self.add_spec_field("生产能力", "production_capacity", "kg/h")
                self.add_spec_field("颗粒直径", "particle_diameter", "mm")
                self.add_spec_field("成型方式", "forming_method", "")
                
            elif equipment_type == "H 贮斗、料斗类":
                self.add_spec_field("容积", "volume", "m³")
                self.add_spec_field("卸料口尺寸", "outlet_size", "mm")
                self.add_spec_field("料斗角度", "hopper_angle", "°")
                
            elif equipment_type == "J 喷射器类":
                self.add_spec_field("喷射能力", "injection_capacity", "m³/h")
                self.add_spec_field("喷射压力", "injection_pressure", "MPa")
                self.add_spec_field("喷嘴直径", "nozzle_diameter", "mm")
                
            elif equipment_type == "K 压缩机类":
                self.add_spec_field("排气量", "displacement", "m³/min")
                self.add_spec_field("排气压力", "discharge_pressure", "MPa")
                self.add_spec_field("吸气压力", "suction_pressure", "MPa")
                self.add_spec_field("冷却方式", "cooling_method", "")
                
            elif equipment_type == "L 起重、装卸、包装机械设备类":
                self.add_spec_field("起重能力", "lifting_capacity", "t")
                self.add_spec_field("起升高度", "lifting_height", "m")
                self.add_spec_field("包装速度", "packaging_speed", "袋/小时")
                
            elif equipment_type == "M 磨碎设备类、混合器类":
                self.add_spec_field("处理能力", "processing_capacity", "kg/h")
                self.add_spec_field("混合均匀度", "mixing_uniformity", "%")
                self.add_spec_field("细度", "fineness", "目")
                
            elif equipment_type == "P 泵类":
                self.add_spec_field("流量", "flow_rate", "m³/h")
                self.add_spec_field("扬程", "head", "m")
                self.add_spec_field("必需汽蚀余量", "npsh", "m")
                self.add_spec_field("效率", "efficiency", "%")
                
            elif equipment_type == "R 反应器":
                # 反应器也有容积参数，可以类似处理
                self.add_spec_field("直径", "diameter", "mm")
                self.add_spec_field("高度", "height", "mm")
                
                volume_layout = QHBoxLayout()
                self.volume_input = QDoubleSpinBox()
                self.volume_input.setRange(0, 1000000)
                self.volume_input.setDecimals(3)
                self.volume_input.setSuffix(" m³")
                self.volume_input.setMinimumWidth(120)
                
                calculate_btn = QPushButton("计算")
                calculate_btn.setMaximumWidth(60)
                calculate_btn.clicked.connect(self.calculate_tank_volume)
                
                self.volume_manually_modified = False
                self.volume_input.valueChanged.connect(self.on_volume_modified)
                
                volume_layout.addWidget(self.volume_input)
                volume_layout.addWidget(calculate_btn)
                volume_layout.addStretch()
                
                self.spec_form_layout.addRow("体积:", volume_layout)
                
                self.spec_params['volume'] = {
                    'label': '体积',
                    'widget': self.volume_input,
                    'unit': 'm³',
                    'type': 'spinbox'
                }
                
                self.volume_widgets['diameter'] = self.spec_params.get('diameter', {}).get('widget')
                self.volume_widgets['height'] = self.spec_params.get('height', {}).get('widget')
                
            elif equipment_type == "S 分离设备类":
                # 分离设备也有容积参数
                self.add_spec_field("直径", "diameter", "mm")
                self.add_spec_field("高度", "height", "mm")
                
                volume_layout = QHBoxLayout()
                self.volume_input = QDoubleSpinBox()
                self.volume_input.setRange(0, 1000000)
                self.volume_input.setDecimals(3)
                self.volume_input.setSuffix(" m³")
                self.volume_input.setMinimumWidth(120)
                
                calculate_btn = QPushButton("计算")
                calculate_btn.setMaximumWidth(60)
                calculate_btn.clicked.connect(self.calculate_tank_volume)
                
                self.volume_manually_modified = False
                self.volume_input.valueChanged.connect(self.on_volume_modified)
                
                volume_layout.addWidget(self.volume_input)
                volume_layout.addWidget(calculate_btn)
                volume_layout.addStretch()
                
                self.spec_form_layout.addRow("容积:", volume_layout)
                
                self.spec_params['volume'] = {
                    'label': '容积',
                    'widget': self.volume_input,
                    'unit': 'm³',
                    'type': 'spinbox'
                }
                
                self.volume_widgets['diameter'] = self.spec_params.get('diameter', {}).get('widget')
                self.volume_widgets['height'] = self.spec_params.get('height', {}).get('widget')
                
                self.add_spec_field("处理量", "processing_capacity", "m³/h")
                
            elif equipment_type == "T 储罐":
                # 添加直径、高度等参数字段
                self.add_spec_field("直径", "diameter", "mm")
                self.add_spec_field("高度", "height", "mm")
                
                # 添加容积字段，并附带计算按钮
                volume_layout = QHBoxLayout()
                
                # 容积输入框
                self.volume_input = QDoubleSpinBox()
                self.volume_input.setRange(0, 1000000)
                self.volume_input.setDecimals(3)
                self.volume_input.setSuffix(" m³")
                self.volume_input.setMinimumWidth(120)
                
                # 计算按钮
                calculate_btn = QPushButton("计算")
                calculate_btn.setMaximumWidth(60)
                calculate_btn.clicked.connect(self.calculate_tank_volume)
                
                # 手动修改标记
                self.volume_manually_modified = False
                
                # 连接容积输入框的信号
                self.volume_input.valueChanged.connect(self.on_volume_modified)
                
                volume_layout.addWidget(self.volume_input)
                volume_layout.addWidget(calculate_btn)
                volume_layout.addStretch()
                
                self.spec_form_layout.addRow("容积:", volume_layout)
                
                # 将容积字段添加到参数字典中
                self.spec_params['volume'] = {
                    'label': '容积',
                    'widget': self.volume_input,
                    'unit': 'm³',
                    'type': 'spinbox'
                }
                
                # 保存直径和高度的widget引用，用于计算
                self.volume_widgets['diameter'] = self.spec_params.get('diameter', {}).get('widget')
                self.volume_widgets['height'] = self.spec_params.get('height', {}).get('widget')
                
                # 添加其他储罐参数
                self.add_spec_field("壁厚", "wall_thickness", "mm")
                self.add_spec_field("封头类型", "head_type", "")
                self.add_spec_field("设计液位", "design_level", "m")
                
            elif equipment_type == "U 公用辅助设备类":
                self.add_spec_field("处理能力", "processing_capacity", "")
                self.add_spec_field("工作介质", "working_medium", "")
                
            elif equipment_type == "V 固体输送类（刮板机、铰刀、提升机、皮带机）":
                self.add_spec_field("输送能力", "conveying_capacity", "t/h")
                self.add_spec_field("输送长度", "conveying_length", "m")
                self.add_spec_field("输送速度", "conveying_speed", "m/s")
                self.add_spec_field("输送设备类型", "conveyor_type", "")
                
            elif equipment_type == "W 称重类设备":
                self.add_spec_field("称重范围", "weighing_range", "kg")
                self.add_spec_field("精度", "accuracy", "%")
                self.add_spec_field("分度值", "division_value", "kg")
                
            elif equipment_type == "X 成套设备类":
                self.add_spec_field("处理能力", "processing_capacity", "")
                self.add_spec_field("设备组成", "equipment_composition", "")
                
            else:  # 其他设备
                self.add_spec_field("主要规格", "main_spec", "")
                self.add_spec_field("处理能力", "capacity", "")
                self.add_spec_field("工作介质", "working_medium", "")
            
            self.add_textedit_field("其他规格", "other_specifications")
        
        # 添加设计操作参数组到布局底部（这个保持不变）
        if force_recreate or not hasattr(self, 'design_parameters_group'):
            self.design_parameters_group = self.create_design_parameters_group()
            self.spec_form_layout.addRow(self.design_parameters_group)
        
    def create_design_parameters_group(self):
        """创建设计操作参数组 - 返回组框，但不添加到布局"""
        design_group = QGroupBox("设计操作参数")
        design_layout = QFormLayout(design_group)
        
        # ======== 设计压力 ========
        design_pressure_layout = QHBoxLayout()
        self.design_pressure_input = QDoubleSpinBox()
        self.design_pressure_input.setRange(0, 1000)
        self.design_pressure_input.setDecimals(3)
        self.design_pressure_input.setSuffix(" MPa")
        self.design_pressure_input.setMinimumWidth(100)
        
        self.normal_pressure_check = QCheckBox("常压 (0.1013 MPa)")
        self.normal_pressure_check.toggled.connect(self.on_normal_pressure_toggled)
        
        # 添加压力系数设置
        pressure_coeff_layout = QHBoxLayout()
        pressure_coeff_label = QLabel("压力系数:")
        self.pressure_coeff_spin = QDoubleSpinBox()
        self.pressure_coeff_spin.setRange(1.0, 2.0)
        self.pressure_coeff_spin.setDecimals(2)
        self.pressure_coeff_spin.setValue(1.1)  # 默认1.1倍
        self.pressure_coeff_spin.setMinimumWidth(60)
        self.pressure_coeff_spin.setToolTip("设计压力 = 操作压力 × 系数 (国标建议1.05-1.2)")
        
        # 自动计算复选框
        self.auto_calc_pressure_check = QCheckBox("自动计算")
        self.auto_calc_pressure_check.setChecked(True)  # 默认开启自动计算
        self.auto_calc_pressure_check.toggled.connect(self.on_auto_calc_pressure_toggled)
        
        pressure_coeff_layout.addWidget(pressure_coeff_label)
        pressure_coeff_layout.addWidget(self.pressure_coeff_spin)
        pressure_coeff_layout.addWidget(self.auto_calc_pressure_check)
        pressure_coeff_layout.addStretch()
        
        design_pressure_layout.addWidget(self.design_pressure_input)
        design_pressure_layout.addWidget(self.normal_pressure_check)
        design_pressure_layout.addLayout(pressure_coeff_layout)
        
        design_layout.addRow("设计压力:", design_pressure_layout)
        
        # ======== 设计温度 ========
        design_temperature_layout = QHBoxLayout()
        self.design_temperature_input = QDoubleSpinBox()
        self.design_temperature_input.setRange(-273, 1000)
        self.design_temperature_input.setDecimals(1)
        self.design_temperature_input.setSuffix(" °C")
        self.design_temperature_input.setMinimumWidth(100)
        
        self.normal_temperature_check = QCheckBox("常温 (25 °C)")
        self.normal_temperature_check.toggled.connect(self.on_normal_temperature_toggled)
        
        # 添加温度裕量设置
        temp_margin_layout = QHBoxLayout()
        temp_margin_label = QLabel("温度裕量:")
        self.temp_margin_spin = QDoubleSpinBox()
        self.temp_margin_spin.setRange(0, 100)
        self.temp_margin_spin.setDecimals(1)
        self.temp_margin_spin.setValue(10.0)  # 默认10°C
        self.temp_margin_spin.setSuffix(" °C")
        self.temp_margin_spin.setMinimumWidth(80)
        self.temp_margin_spin.setToolTip("设计温度 = 操作温度 + 裕量 (国标建议10-30°C)")
        
        # 自动计算复选框
        self.auto_calc_temp_check = QCheckBox("自动计算")
        self.auto_calc_temp_check.setChecked(True)  # 默认开启自动计算
        self.auto_calc_temp_check.toggled.connect(self.on_auto_calc_temp_toggled)
        
        temp_margin_layout.addWidget(temp_margin_label)
        temp_margin_layout.addWidget(self.temp_margin_spin)
        temp_margin_layout.addWidget(self.auto_calc_temp_check)
        temp_margin_layout.addStretch()
        
        design_temperature_layout.addWidget(self.design_temperature_input)
        design_temperature_layout.addWidget(self.normal_temperature_check)
        design_temperature_layout.addLayout(temp_margin_layout)
        
        design_layout.addRow("设计温度:", design_temperature_layout)
        
        # ======== 操作压力 ========
        operating_pressure_layout = QHBoxLayout()
        self.operating_pressure_input = QDoubleSpinBox()
        self.operating_pressure_input.setRange(0, 1000)
        self.operating_pressure_input.setDecimals(3)
        self.operating_pressure_input.setSuffix(" MPa")
        self.operating_pressure_input.setMinimumWidth(100)
        
        self.operating_normal_pressure_check = QCheckBox("常压 (0.1013 MPa)")
        self.operating_normal_pressure_check.toggled.connect(self.on_operating_normal_pressure_toggled)
        
        operating_pressure_layout.addWidget(self.operating_pressure_input)
        operating_pressure_layout.addWidget(self.operating_normal_pressure_check)
        operating_pressure_layout.addStretch()
        
        design_layout.addRow("操作压力:", operating_pressure_layout)
        
        # ======== 操作温度 ========
        operating_temperature_layout = QHBoxLayout()
        self.operating_temperature_input = QDoubleSpinBox()
        self.operating_temperature_input.setRange(-273, 1000)
        self.operating_temperature_input.setDecimals(1)
        self.operating_temperature_input.setSuffix(" °C")
        self.operating_temperature_input.setMinimumWidth(100)
        
        self.operating_normal_temperature_check = QCheckBox("常温 (25 °C)")
        self.operating_normal_temperature_check.toggled.connect(self.on_operating_normal_temperature_toggled)
        
        operating_temperature_layout.addWidget(self.operating_temperature_input)
        operating_temperature_layout.addWidget(self.operating_normal_temperature_check)
        operating_temperature_layout.addStretch()
        
        design_layout.addRow("操作温度:", operating_temperature_layout)
        
        # 连接信号
        self.operating_pressure_input.valueChanged.connect(self.on_operating_pressure_changed)
        self.operating_temperature_input.valueChanged.connect(self.on_operating_temperature_changed)
        self.pressure_coeff_spin.valueChanged.connect(self.on_operating_pressure_changed)
        self.temp_margin_spin.valueChanged.connect(self.on_operating_temperature_changed)
        
        return design_group

    def calculate_tank_volume(self):
        """计算储罐/反应器/分离设备等的圆柱形容积"""
        if not self.volume_widgets.get('diameter') or not self.volume_widgets.get('height'):
            return
        
        diameter_widget = self.volume_widgets['diameter']
        height_widget = self.volume_widgets['height']
        
        try:
            diameter = diameter_widget.value()
            height = height_widget.value()
            
            if diameter > 0 and height > 0:
                # 将毫米转换为米
                diameter_m = diameter / 1000.0
                height_m = height / 1000.0
                
                # 计算圆柱体积：π × (直径/2)² × 高度
                radius = diameter_m / 2.0
                volume = 3.141592653589793 * radius * radius * height_m
                
                # 更新容积输入框的值，但不触发手动修改标记
                self.volume_input.blockSignals(True)
                self.volume_input.setValue(round(volume, 3))
                self.volume_input.blockSignals(False)
                
                # 显示工具提示
                QToolTip.showText(
                    self.mapToGlobal(QPoint(0, 0)),
                    f"根据直径 {diameter} mm 和高度 {height} mm 计算得出",
                    self, QRect(), 2000
                )
        except Exception as e:
            print(f"计算容积时出错: {e}")
            
    def calculate_trough_volume(self):
        """计算槽罐的长方形容积"""
        if not self.volume_widgets.get('length') or not self.volume_widgets.get('width') or not self.volume_widgets.get('height'):
            return
        
        length_widget = self.volume_widgets['length']
        width_widget = self.volume_widgets['width']
        height_widget = self.volume_widgets['height']
        
        try:
            length = length_widget.value()
            width = width_widget.value()
            height = height_widget.value()
            
            if length > 0 and width > 0 and height > 0:
                # 将毫米转换为米
                length_m = length / 1000.0
                width_m = width / 1000.0
                height_m = height / 1000.0
                
                # 计算长方体体积：长 × 宽 × 高
                volume = length_m * width_m * height_m
                
                # 更新容积输入框的值，但不触发手动修改标记
                self.volume_input.blockSignals(True)
                self.volume_input.setValue(round(volume, 3))
                self.volume_input.blockSignals(False)
                
                # 显示工具提示
                QToolTip.showText(
                    self.mapToGlobal(QPoint(0, 0)),
                    f"根据长 {length} mm、宽 {width} mm、高 {height} mm 计算得出",
                    self, QRect(), 2000
                )
        except Exception as e:
            print(f"计算容积时出错: {e}")
            
    def on_volume_modified(self, value):
        """当用户手动修改容积时标记"""
        # 只有当值非零时才标记为手动修改
        if value > 0:
            self.volume_manually_modified = True
            
            # 显示提示信息
            current_type = self.type_combo.currentText()
            QToolTip.showText(
                self.mapToGlobal(QPoint(0, 0)),
                f"容积已手动修改为 {value} m³，点击计算按钮可重新计算",
                self, QRect(), 3000
            )
    
    def calculate_volume(self):
        diameter_widget = self.volume_widgets.get('diameter')
        height_widget = self.volume_widgets.get('height')
        
        if diameter_widget and height_widget:
            diameter = diameter_widget.value()
            height = height_widget.value()
            
            if diameter > 0 and height > 0:
                diameter_m = diameter / 1000.0
                height_m = height / 1000.0
                
                radius = diameter_m / 2.0
                volume = 3.141592653589793 * radius * radius * height_m
                
                self.volume_input.setValue(round(volume, 2))
                
                QToolTip.showText(self.mapToGlobal(QPoint(0, 0)), f"根据直径 {diameter} mm 和高度 {height} mm 计算得出", self, QRect(), 2000)
    
    def add_spec_field(self, label_text, field_name, unit):
        layout = QHBoxLayout()
        
        if unit in ["m³", "kW", "MPa", "m", "m³/h", "m²"]:
            input_widget = QDoubleSpinBox()
            input_widget.setRange(0, 1000000)
            input_widget.setDecimals(2)
        elif unit in ["mm", "kg/m³", "cP", "m³/min"]:
            input_widget = QDoubleSpinBox()
            input_widget.setRange(0, 1000000)
            input_widget.setDecimals(1)
        elif unit in ["%", "rpm"]:
            input_widget = QDoubleSpinBox()
            input_widget.setRange(0, 1000000)
            input_widget.setDecimals(0)
        else:
            input_widget = QLineEdit()
        
        if unit:
            if isinstance(input_widget, QDoubleSpinBox):
                input_widget.setSuffix(f" {unit}")
                input_widget.setMinimumWidth(100)
            else:
                input_widget.setPlaceholderText(unit)
        
        layout.addWidget(input_widget)
        layout.addStretch()
        
        self.spec_form_layout.addRow(f"{label_text}:", layout)
        
        self.spec_params[field_name] = {
            'label': label_text,
            'widget': input_widget,
            'unit': unit,
            'type': 'spinbox' if isinstance(input_widget, QDoubleSpinBox) else 'lineedit'
        }
    
    def add_checkbox_field(self, label_text, field_name):
        checkbox = QCheckBox()
        self.spec_form_layout.addRow(f"{label_text}:", checkbox)
        
        self.spec_params[field_name] = {
            'label': label_text,
            'widget': checkbox,
            'type': 'checkbox'
        }
    
    def add_textedit_field(self, label_text, field_name):
        textedit = QTextEdit()
        textedit.setMaximumHeight(100)
        self.spec_form_layout.addRow(f"{label_text}:", textedit)
        
        self.spec_params[field_name] = {
            'label': label_text,
            'widget': textedit,
            'type': 'textedit'
        }
    
    def clear_layout(self, layout):
        while layout.rowCount() > 0:
            layout.removeRow(0)
    
    def on_type_changed(self, equipment_type):
        """设备类型变化时处理"""
        # 只有在不是编辑设备时才使用延迟调用
        if not self.equipment:
            try:
                # 延迟执行，确保UI完全加载
                QTimer.singleShot(50, lambda: self._on_type_changed_delayed(equipment_type))
            except Exception as e:
                print(f"设备类型变化处理时出错: {e}")
        else:
            # 编辑设备时直接调用，避免延迟导致数据加载问题
            try:
                self._on_type_changed_delayed(equipment_type)
            except Exception as e:
                print(f"编辑设备时设置技术规格字段时出错: {e}")
            
    def _on_type_changed_delayed(self, equipment_type):
        """延迟的设备类型变化处理"""
        try:
            # 编辑设备时不强制重新创建字段
            force_recreate = not self.equipment
            self.setup_specification_fields(equipment_type, force_recreate)
        except Exception as e:
            print(f"设置技术规格字段时出错: {e}")

    def on_normal_pressure_toggled(self, checked):
        """设计压力常压复选框状态变化"""
        if checked:
            self.design_pressure_input.setValue(0.1013)
            self.design_pressure_input.setEnabled(False)
            # 当手动选择常压时，自动计算选项应保持可用状态
            self.auto_calc_pressure_check.setChecked(False)
        else:
            self.design_pressure_input.setEnabled(True)
            # 如果不是常压，重新启用自动计算（如果之前是启用的）
            if hasattr(self, 'operating_pressure_input') and self.operating_pressure_input.value() > 0:
                self.auto_calc_pressure_check.setChecked(True)

    def on_normal_temperature_toggled(self, checked):
        """设计温度常温复选框状态变化"""
        if checked:
            self.design_temperature_input.setValue(25.0)
            self.design_temperature_input.setEnabled(False)
            # 当手动选择常温时，自动计算选项应保持可用状态
            self.auto_calc_temp_check.setChecked(False)
        else:
            self.design_temperature_input.setEnabled(True)
            # 如果不是常温，重新启用自动计算（如果之前是启用的）
            if hasattr(self, 'operating_temperature_input') and self.operating_temperature_input.value() != 25:
                self.auto_calc_temp_check.setChecked(True)

    # 同样需要修改操作压力的常压复选框处理方法：
    def on_operating_normal_pressure_toggled(self, checked):
        """操作压力常压复选框状态变化"""
        if checked:
            self.operating_pressure_input.setValue(0.1013)
            self.operating_pressure_input.setEnabled(False)
            # 操作压力是常压时，自动计算设计压力为常压
            self.on_operating_pressure_changed()
        else:
            self.operating_pressure_input.setEnabled(True)
            # 重新计算设计压力
            self.on_operating_pressure_changed()

    def on_operating_normal_temperature_toggled(self, checked):
        """操作温度常温复选框状态变化"""
        if checked:
            self.operating_temperature_input.setValue(25.0)
            self.operating_temperature_input.setEnabled(False)
            # 操作温度是常温时，自动计算设计温度为常温
            self.on_operating_temperature_changed()
        else:
            self.operating_temperature_input.setEnabled(True)
            # 重新计算设计温度
            self.on_operating_temperature_changed()
    
    def on_quantity_changed(self, value):
        self.calculate_total_power()
    
    def on_running_quantity_changed(self, value):
        self.calculate_operating_power()
    
    def on_single_power_changed(self, value):
        self.calculate_operating_power()
        self.calculate_total_power()
    
    def calculate_operating_power(self):
        """计算运行功率"""
        single_power = self.single_power_input.value()
        running_quantity = self.running_quantity_input.value()
        
        if single_power > 0 and running_quantity > 0:
            operating_power = single_power * running_quantity
            self.operating_power_input.setValue(operating_power)
    
    def calculate_total_power(self):
        """计算装机功率"""
        single_power = self.single_power_input.value()
        quantity = self.quantity_input.value()
        
        if single_power > 0 and quantity > 0:
            total_power = single_power * quantity
            self.total_power_input.setValue(total_power)
    
    def update_english_name(self):
        chinese_name = self.name_input.text().strip()
        if chinese_name and self.parent_widget and hasattr(self.parent_widget, 'data_manager'):
            english_name = self.parent_widget.data_manager.get_english_name(chinese_name)
            if english_name:
                self.description_en_input.setText(english_name)
    
    def validate_and_accept(self):
        equipment_id = self.equipment_id_input.text().strip()
        name = self.name_input.text().strip()
        unique_code = self.unique_code_input.text().strip()
        
        errors = []
        
        if not equipment_id:
            errors.append("设备位号不能为空")
        if not name:
            errors.append("设备名称不能为空")
        if not unique_code:
            errors.append("唯一编码不能为空")
        
        # 检查设备位号唯一性（如果是编辑且设备位号有变化）
        if self.parent_widget and hasattr(self.parent_widget, 'process_manager'):
            existing_equipment = self.parent_widget.process_manager.get_equipment(equipment_id)
            if existing_equipment:
                # 如果是编辑现有设备，检查是否是同一个设备（通过唯一编码判断）
                if self.equipment and hasattr(existing_equipment, 'unique_code'):
                    if existing_equipment.unique_code != self.equipment.unique_code:
                        errors.append(f"设备位号 '{equipment_id}' 已存在，请使用其他设备位号")
                elif not self.equipment:  # 添加新设备
                    errors.append(f"设备位号 '{equipment_id}' 已存在，请使用其他设备位号")
        
        if errors:
            self.validation_label.setText("错误: " + "; ".join(errors))
            return
        
        self.validation_label.setText("")
        self.accept()

    def load_equipment_data(self):
        """加载设备数据 - 适配新的布局"""
        if not self.equipment:
            return
        
        # 基本信息
        self.unique_code_input.setText(getattr(self.equipment, 'unique_code', ''))
        self.equipment_id_input.setText(self.equipment.equipment_id)
        self.name_input.setText(self.equipment.name)
        self.description_en_input.setText(getattr(self.equipment, 'description_en', ''))
        self.model_input.setText(getattr(self.equipment, 'model', ''))
        self.manufacturer_input.setText(getattr(self.equipment, 'manufacturer', ''))
        
        # 设备类型（现在在技术规格页）
        equipment_type = getattr(self.equipment, 'type', getattr(self.equipment, 'equipment_type', '其他'))
        if not equipment_type:
            equipment_type = "其他"
        
        index = self.type_combo.findText(equipment_type)
        if index >= 0:
            self.type_combo.setCurrentIndex(index)
        
        # 关键修改：先设置技术规格页面，然后直接加载数据，避免延迟导致的数据丢失
        # 使用同步调用而不是延迟调用
        self._on_type_changed_delayed(equipment_type)
        
        # 解析技术规格数据
        self.parse_specification_data()
        
        # 设计压力
        if hasattr(self.equipment, 'design_pressure') and self.equipment.design_pressure:
            if isinstance(self.equipment.design_pressure, str) and self.equipment.design_pressure.upper() == "NP":
                self.normal_pressure_check.setChecked(True)
                self.auto_calc_pressure_check.setChecked(False)  # 手动设置为常压，关闭自动计算
            else:
                try:
                    pressure_val = float(self.equipment.design_pressure)
                    if abs(pressure_val - 0.1013) < 0.0001:
                        self.normal_pressure_check.setChecked(True)
                        self.auto_calc_pressure_check.setChecked(False)
                    else:
                        self.design_pressure_input.setValue(pressure_val)
                        # 如果是编辑现有设备，默认关闭自动计算（因为已有设计值）
                        self.auto_calc_pressure_check.setChecked(False)
                except (ValueError, TypeError):
                    self.design_pressure_input.setValue(0.0)
                    self.auto_calc_pressure_check.setChecked(True)  # 新建设备默认开启
        
        # 设计温度
        if hasattr(self.equipment, 'design_temperature') and self.equipment.design_temperature:
            if isinstance(self.equipment.design_temperature, str) and self.equipment.design_temperature.upper() == "NT":
                self.normal_temperature_check.setChecked(True)
                self.auto_calc_temp_check.setChecked(False)
            else:
                try:
                    temp_val = float(self.equipment.design_temperature)
                    if abs(temp_val - 25.0) < 0.001:
                        self.normal_temperature_check.setChecked(True)
                        self.auto_calc_temp_check.setChecked(False)
                    else:
                        self.design_temperature_input.setValue(temp_val)
                        self.auto_calc_temp_check.setChecked(False)
                except (ValueError, TypeError):
                    self.design_temperature_input.setValue(0.0)
                    self.auto_calc_temp_check.setChecked(True)
        
        # 操作压力
        if hasattr(self.equipment, 'operating_pressure') and self.equipment.operating_pressure:
            if isinstance(self.equipment.operating_pressure, str) and self.equipment.operating_pressure.upper() == "NP":
                self.operating_normal_pressure_check.setChecked(True)
            else:
                try:
                    pressure_val = float(self.equipment.operating_pressure)
                    if abs(pressure_val - 0.1013) < 0.0001:
                        self.operating_normal_pressure_check.setChecked(True)
                    else:
                        self.operating_pressure_input.setValue(pressure_val)
                except (ValueError, TypeError):
                    self.operating_pressure_input.setValue(0.0)
        
        # 操作温度
        if hasattr(self.equipment, 'operating_temperature') and self.equipment.operating_temperature:
            if isinstance(self.equipment.operating_temperature, str) and self.equipment.operating_temperature.upper() == "NT":
                self.operating_normal_temperature_check.setChecked(True)
            else:
                try:
                    temp_val = float(self.equipment.operating_temperature)
                    if abs(temp_val - 25.0) < 0.001:
                        self.operating_normal_temperature_check.setChecked(True)
                    else:
                        self.operating_temperature_input.setValue(temp_val)
                except (ValueError, TypeError):
                    self.operating_temperature_input.setValue(0.0)
        
        # 操作参数页字段
        # 安全加载数值字段的辅助函数
        def safe_int(value, default=1):
            if value is None or value == '':
                return default
            try:
                return int(float(value))
            except (ValueError, TypeError):
                return default
        
        def safe_float(value, default=0.0):
            if value is None or value == '':
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        
        # 数量相关字段
        if hasattr(self.equipment, 'quantity'):
            self.quantity_input.setValue(safe_int(self.equipment.quantity, 1))
        
        if hasattr(self.equipment, 'running_quantity'):
            self.running_quantity_input.setValue(safe_int(self.equipment.running_quantity, 1))
        
        # 功率相关字段
        if hasattr(self.equipment, 'single_power'):
            self.single_power_input.setValue(safe_float(self.equipment.single_power, 0.0))
        
        if hasattr(self.equipment, 'operating_power'):
            self.operating_power_input.setValue(safe_float(self.equipment.operating_power, 0.0))
        
        if hasattr(self.equipment, 'total_power'):
            self.total_power_input.setValue(safe_float(self.equipment.total_power, 0.0))
        
        # 材质和重量字段
        if hasattr(self.equipment, 'material'):
            material_value = self.equipment.material
            if material_value:
                self.material_input.setText(str(material_value))
        
        if hasattr(self.equipment, 'insulation'):
            self.insulation_input.setText(self.equipment.insulation or "")
        
        if hasattr(self.equipment, 'weight_estimate'):
            self.weight_estimate_input.setValue(safe_float(self.equipment.weight_estimate, 0.0))

        if hasattr(self.equipment, 'operating_weight'):
            self.operating_weight_input.setValue(safe_float(self.equipment.operating_weight, 0.0))

        if hasattr(self.equipment, 'total_weight'):
            self.total_weight_input.setValue(safe_float(self.equipment.total_weight, 0.0))
        
        # 其他页字段
        if hasattr(self.equipment, 'pid_dwg_no'):
            self.pid_dwg_no_input.setText(self.equipment.pid_dwg_no or "")
        
        if hasattr(self.equipment, 'unit_price'):
            self.unit_price_input.setValue(safe_float(self.equipment.unit_price, 0.0))
        
        if hasattr(self.equipment, 'total_price'):
            self.total_price_input.setValue(safe_float(self.equipment.total_price, 0.0))
        
        if hasattr(self.equipment, 'dynamic'):
            self.dynamic_input.setText(self.equipment.dynamic or "")
        
        if hasattr(self.equipment, 'notes'):
            self.notes_input.setText(self.equipment.notes or "")
    
    def parse_specification_data(self):
        """解析技术规格数据"""
        if not self.equipment or not self.equipment.specification:
            return
        
        spec_str = self.equipment.specification
        if not spec_str:
            return
        
        # 按分号分割规格项
        spec_items = [item.strip() for item in spec_str.split(';') if item.strip()]
        
        for item in spec_items:
            if ':' in item:
                parts = item.split(':', 1)
                if len(parts) == 2:
                    label = parts[0].strip()
                    value_part = parts[1].strip()
                    self.set_specification_value(label, value_part)
        
        # 尝试从规格中提取体积信息
        self.extract_volume_from_spec(spec_str)
        
        # 尝试提取其他可能的信息
        self.extract_other_info_from_spec(spec_str)
        
    def extract_other_info_from_spec(self, spec_str):
        """从规格中提取其他信息"""
        if not spec_str:
            return
        
        # 提取材质
        material_match = re.search(r'材质[:：]\s*([^;]+)', spec_str)
        if material_match and not self.material_input.text():
            self.material_input.setText(material_match.group(1).strip())
        
        # 提取保温
        insulation_match = re.search(r'保温[:：]\s*([^;]+)', spec_str)
        if insulation_match and not self.insulation_input.text():
            self.insulation_input.setText(insulation_match.group(1).strip())
        
    def set_specification_value(self, label, value_part):
        """设置技术规格值"""
        # 遍历所有规格参数
        for field_name, field_info in self.spec_params.items():
            field_label = field_info.get('label', '')
            
            # 检查标签是否匹配（忽略大小写）
            if field_label and field_label.lower() in label.lower():
                widget = field_info.get('widget')
                field_type = field_info.get('type', '')
                
                if not widget:
                    continue
                
                try:
                    if field_type == 'spinbox':
                        import re
                        numbers = re.findall(r'[-+]?\d*\.\d+|\d+', value_part)
                        if numbers:
                            num_value = float(numbers[0])
                            widget.setValue(num_value)
                    
                    elif field_type == 'lineedit':
                        widget.setText(value_part)
                    
                    elif field_type == 'checkbox':
                        if '是' in value_part:
                            widget.setChecked(True)
                        elif '否' in value_part:
                            widget.setChecked(False)
                    
                    elif field_type == 'textedit':
                        if field_name == 'other_specifications':
                            current_text = widget.toPlainText()
                            if current_text:
                                widget.setPlainText(current_text + '\n' + label + ': ' + value_part)
                            else:
                                widget.setPlainText(label + ': ' + value_part)
                
                except Exception:
                    pass
                break  # 找到一个匹配就退出
                    
    def extract_volume_from_spec(self, spec_str):
        if not spec_str:
            return
        
        diameter_match = re.search(r'直径[:：]\s*([\d\.]+)\s*mm', spec_str)
        if diameter_match and 'diameter' in self.spec_params:
            try:
                diameter = float(diameter_match.group(1))
                diameter_widget = self.spec_params['diameter'].get('widget')
                if diameter_widget:
                    diameter_widget.setValue(diameter)
            except:
                pass
        
        height_match = re.search(r'高度[:：]\s*([\d\.]+)\s*mm', spec_str)
        if height_match and 'height' in self.spec_params:
            try:
                height = float(height_match.group(1))
                height_widget = self.spec_params['height'].get('widget')
                if height_widget:
                    height_widget.setValue(height)
            except:
                pass
        
        volume_match = re.search(r'体积[:：]\s*([\d\.]+)\s*m³', spec_str)
        if volume_match and 'volume' in self.spec_params:
            try:
                volume = float(volume_match.group(1))
                volume_widget = self.spec_params['volume'].get('widget')
                if volume_widget:
                    volume_widget.setValue(volume)
            except:
                pass
    
    def get_equipment(self):
        """获取设备对象"""
        from ..data.data_models import UnifiedEquipment
        
        # 基本信息
        equipment_id = self.equipment_id_input.text().strip()
        name = self.name_input.text().strip()
        description_en = self.description_en_input.text().strip()
        unique_code = self.unique_code_input.text().strip()
        
        # 如果唯一编码为空，重新生成
        if not unique_code:
            equipment_type = self.type_combo.currentText()
            self.generate_unique_code(equipment_type)
            unique_code = self.unique_code_input.text().strip()
    
        # 如果用户输入了英文描述，更新对照表
        if name and description_en and self.parent_widget and hasattr(self.parent_widget, 'data_manager'):
            self.parent_widget.data_manager.add_equipment_name_mapping(name, description_en)
        
        # 构建规格字符串
        specification_parts = []
        
        # 添加型号到规格
        model = self.model_input.text().strip()
        if model:
            specification_parts.append(f"型号: {model}")
        
        # 根据设备类型添加特定规格
        equipment_type = self.type_combo.currentText()
        for field_name, field_info in self.spec_params.items():
            widget = field_info.get('widget')
            label = field_info.get('label')
            unit = field_info.get('unit', '')
            field_type = field_info.get('type', '')
            
            value = None
            if field_type == 'spinbox':
                value = widget.value()
                if value > 0:
                    specification_parts.append(f"{label}: {value} {unit}")
            elif field_type == 'lineedit':
                value = widget.text().strip()
                if value:
                    specification_parts.append(f"{label}: {value}")
            elif field_type == 'checkbox':
                value = widget.isChecked()
                if value:
                    specification_parts.append(f"{label}: 是")
                else:
                    specification_parts.append(f"{label}: 否")
            elif field_type == 'textedit':
                value = widget.toPlainText().strip()
                if value:
                    # 其他规格可能会包含多条信息，每行作为单独的规格项
                    lines = value.split('\n')
                    for line in lines:
                        if line.strip():
                            specification_parts.append(line.strip())
        
        # 合并规格字符串
        specification = "; ".join(specification_parts)
        
        # 获取设计操作参数
        design_pressure = self.design_pressure_input.value() if self.design_pressure_input.isEnabled() else "NP"
        design_temperature = self.design_temperature_input.value() if self.design_temperature_input.isEnabled() else "NT"
        operating_pressure = self.operating_pressure_input.value() if self.operating_pressure_input.isEnabled() else "NP"
        operating_temperature = self.operating_temperature_input.value() if self.operating_temperature_input.isEnabled() else "NT"
        
        # 安全地获取数值字段，防止出现无效值
        def safe_float(value, default=None):
            if value is None or value == '':
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default
        
        def safe_int(value, default=1):
            if value is None or value == '':
                return default
            try:
                return int(float(value))
            except (ValueError, TypeError):
                return default
        
        # 创建设备数据字典
        equipment_data = {
            'equipment_id': equipment_id,
            'unique_code': unique_code,
            'name': name,
            "equipment_type": equipment_type,
            'model': model,
            'specification': specification,
            'manufacturer': self.manufacturer_input.text().strip(),
            'design_pressure': design_pressure,
            'design_temperature': design_temperature,
            'operating_pressure': operating_pressure,
            'operating_temperature': operating_temperature,
            'description_en': description_en,
            'pid_dwg_no': self.pid_dwg_no_input.text().strip(),
            'quantity': safe_int(self.quantity_input.value()),
            'running_quantity': safe_int(self.running_quantity_input.value()),
            'single_power': safe_float(self.single_power_input.value()),
            'operating_power': safe_float(self.operating_power_input.value()),
            'total_power': safe_float(self.total_power_input.value()),
            'material': self.material_input.text().strip(),
            'insulation': self.insulation_input.text().strip(),
            'weight_estimate': safe_float(self.weight_estimate_input.value()),
            'operating_weight': safe_float(self.operating_weight_input.value()),
            'total_weight': safe_float(self.total_weight_input.value()),
            'unit_price': safe_float(self.unit_price_input.value()),
            'total_price': safe_float(self.total_price_input.value()),
            'dynamic': self.dynamic_input.text().strip(),
            'notes': self.notes_input.toPlainText().strip()
        }
        
        # 移除空字符串
        for key in ['material', 'insulation', 'dynamic', 'notes']:
            if equipment_data[key] == '':
                equipment_data[key] = None
        
        # 创建设备对象
        equipment = UnifiedEquipment(**equipment_data)
        
        return equipment

class ProcessDesignTab(QWidget):
    """工艺设计标签页（设备清单模块）"""
    
    def import_from_flow_diagram(self):
        """从流程图导入设备到设备清单"""
        try:
            if not self.parent_window:
                QMessageBox.warning(self, "错误", "未找到主窗口")
                return
            
            # 获取流程图模块
            flow_diagram_tab = None
            for widget in self.parent_window.tab_widget.findChildren(QWidget):
                if hasattr(widget, '__class__') and widget.__class__.__name__ == "ProcessFlowDiagramTab":
                    flow_diagram_tab = widget
                    break
            
            if not flow_diagram_tab:
                QMessageBox.warning(self, "错误", "未找到流程图模块")
                return
            
            # 获取流程图中的所有设备
            diagram_equipment = flow_diagram_tab.flow_diagram.equipment_nodes
            if not diagram_equipment:
                QMessageBox.information(self, "提示", "流程图中没有设备")
                return
            
            # 创建导入对话框
            dialog = QDialog(self)
            dialog.setWindowTitle("从流程图导入设备")
            dialog.setMinimumSize(600, 400)
            
            layout = QVBoxLayout(dialog)
            
            # 表格显示流程图设备
            table = QTableWidget()
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(["选择", "设备位号", "设备名称", "PFD类型", "状态"])
            table.setRowCount(len(diagram_equipment))
            
            checkboxes = []
            
            for i, (eq_id, equipment) in enumerate(diagram_equipment.items()):
                # 复选框
                checkbox = QCheckBox()
                checkboxes.append(checkbox)
                
                # 创建包含复选框的widget
                checkbox_widget = QWidget()
                checkbox_layout = QHBoxLayout(checkbox_widget)
                checkbox_layout.addWidget(checkbox)
                checkbox_layout.setAlignment(Qt.AlignCenter)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                
                table.setCellWidget(i, 0, checkbox_widget)
                table.setItem(i, 1, QTableWidgetItem(eq_id))
                table.setItem(i, 2, QTableWidgetItem(equipment.name))
                table.setItem(i, 3, QTableWidgetItem(
                    EQUIPMENT_TYPES.get(equipment.equipment_type, {}).get("name", "未知")
                ))
                
                # 检查是否已在设备清单中
                existing = self.data_manager.get_equipment(eq_id) if self.data_manager else None
                status = "已在清单中" if existing else "新设备"
                table.setItem(i, 4, QTableWidgetItem(status))
                
                # 如果已存在，禁用复选框
                if existing:
                    checkbox.setEnabled(False)
                    table.item(i, 4).setForeground(QColor("gray"))
            
            table.horizontalHeader().setStretchLastSection(True)
            layout.addWidget(table)
            
            # 按钮
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(dialog.accept)
            button_box.rejected.connect(dialog.reject)
            layout.addWidget(button_box)
            
            if dialog.exec() == QDialog.Accepted:
                imported_count = 0
                existing_count = 0
                
                for i, checkbox in enumerate(checkboxes):
                    if checkbox.isChecked():
                        eq_id = table.item(i, 1).text()
                        equipment = diagram_equipment.get(eq_id)
                        
                        if equipment and self.data_manager:
                            # 检查是否已存在
                            existing_eq = self.data_manager.get_equipment(eq_id)
                            
                            if not existing_eq:
                                # 创建设备清单数据
                                equipment_data = {
                                    "equipment_id": eq_id,
                                    "name": equipment.name,
                                    "type": getattr(equipment, 'inventory_type', "其他"),
                                    "unique_code": getattr(equipment, 'unique_code', ""),
                                    "status": "active",
                                    "pfd_position_x": equipment.x(),
                                    "pfd_position_y": equipment.y(),
                                    "material": equipment.properties.get("material", ""),
                                    "operating_temperature": equipment.properties.get("temperature", 25.0),
                                    "operating_pressure": equipment.properties.get("pressure", 101.325),
                                    "flow_rate": equipment.properties.get("flow_rate", 0.0)
                                }
                                
                                # 添加到设备清单
                                if self.data_manager.add_equipment(equipment_data):
                                    imported_count += 1
                                else:
                                    print(f"❌ 添加设备 {eq_id} 到设备清单失败")
                            else:
                                existing_count += 1
                
                # 显示结果
                message = f"导入完成！\n"
                if imported_count > 0:
                    message += f"成功导入 {imported_count} 个新设备\n"
                if existing_count > 0:
                    message += f"跳过 {existing_count} 个已存在的设备"
                
                QMessageBox.information(self, "导入完成", message)
                
                # 刷新设备表格
                self.refresh_equipment_table()
                
        except Exception as e:
            print(f"❌ 从流程图导入设备时出错: {e}")
            QMessageBox.critical(self, "错误", f"导入失败: {str(e)}")

class TemplateImportPreviewDialog(QDialog):
    """模板导入预览对话框"""
    def __init__(self, project_info, equipment_list, parent=None):
        super().__init__(parent)
        self.project_info = project_info
        self.equipment_list = equipment_list
        self.import_options = {
            'skip_existing': True,
            'update_existing': False,
            'import_all': True
        }
        
        self.setWindowTitle("模板导入预览")
        self.setMinimumSize(800, 600)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 项目信息区域
        if self.project_info:
            project_group = QGroupBox("项目信息")
            project_layout = QFormLayout(project_group)
            
            if 'project_name' in self.project_info:
                project_layout.addRow("项目名称:", QLabel(self.project_info['project_name']))
            
            if 'sub_item_name' in self.project_info:
                project_layout.addRow("子项名称:", QLabel(self.project_info['sub_item_name']))
            
            if 'doc_no' in self.project_info:
                project_layout.addRow("文件编号:", QLabel(self.project_info['doc_no']))
            
            if 'speciality' in self.project_info:
                project_layout.addRow("专业:", QLabel(self.project_info['speciality']))
            
            if 'phase' in self.project_info:
                project_layout.addRow("阶段:", QLabel(self.project_info['phase']))
            
            layout.addWidget(project_group)
        
        # 设备列表预览
        equipment_group = QGroupBox(f"设备列表 ({len(self.equipment_list)} 个设备)")
        equipment_layout = QVBoxLayout(equipment_group)
        
        self.equipment_table = QTableWidget()
        self.equipment_table.setColumnCount(5)
        self.equipment_table.setHorizontalHeaderLabels([
            "序号", "设备位号", "设备名称", "规格", "唯一编码"
        ])
        
        self.equipment_table.setRowCount(len(self.equipment_list))
        for i, equipment in enumerate(self.equipment_list):
            self.equipment_table.setItem(i, 0, QTableWidgetItem(str(i+1)))
            self.equipment_table.setItem(i, 1, QTableWidgetItem(equipment.get('equipment_id', '')))
            self.equipment_table.setItem(i, 2, QTableWidgetItem(equipment.get('name', '')))
            self.equipment_table.setItem(i, 3, QTableWidgetItem(equipment.get('specification', '')[:50] + '...' 
                                                            if len(equipment.get('specification', '')) > 50 
                                                            else equipment.get('specification', '')))
            self.equipment_table.setItem(i, 4, QTableWidgetItem(equipment.get('unique_code', '')))
        
        self.equipment_table.horizontalHeader().setStretchLastSection(True)
        equipment_layout.addWidget(self.equipment_table)
        
        layout.addWidget(equipment_group)
        
        # 导入选项
        options_group = QGroupBox("导入选项")
        options_layout = QVBoxLayout(options_group)
        
        self.skip_existing_check = QCheckBox("跳过已存在的设备（根据设备位号）")
        self.skip_existing_check.setChecked(True)
        options_layout.addWidget(self.skip_existing_check)
        
        self.update_existing_check = QCheckBox("更新已存在的设备")
        self.update_existing_check.setChecked(False)
        options_layout.addWidget(self.update_existing_check)
        
        self.import_all_check = QCheckBox("导入所有设备")
        self.import_all_check.setChecked(True)
        options_layout.addWidget(self.import_all_check)
        
        layout.addWidget(options_group)
        
        # 按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
    
    def get_import_options(self):
        """获取导入选项"""
        self.import_options.update({
            'skip_existing': self.skip_existing_check.isChecked(),
            'update_existing': self.update_existing_check.isChecked(),
            'import_all': self.import_all_check.isChecked()
        })
        return self.import_options