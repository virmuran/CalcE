# modules/process_design/tabs/equipment_id_table_item.py
from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtCore import Qt

class EquipmentIDTableWidgetItem(QTableWidgetItem):
    """用于设备ID排序的自定义表格项"""
    def __init__(self, text):
        super().__init__(text)
        self._object_id = id(self)  # 保存对象ID用于调试
    
    def __lt__(self, other):
        """
        自定义排序规则，按照新的设备类型代码排序
        设备ID格式：EQ-{TYPE_CODE}-{TIMESTAMP}-{HASH}
        其中 TYPE_CODE 是5位设备类型代码
        """
        self_text = self.text()
        other_text = other.text()
        
        # 如果设备ID不符合预期格式，退回到默认的字符串比较
        if len(self_text) < 9 or len(other_text) < 9:
            return self_text < other_text
        
        try:
            # 提取各个部分
            # 项目编号: 前4位 (例如: 5011)
            self_project = self_text[0:4]
            other_project = other_text[0:4]
            
            # 工段号: 第6-7位 (例如: 01)
            self_section = self_text[5:7]
            other_section = other_text[5:7]
            
            # 设备序号: 最后2位 (例如: 01)
            self_sequence = self_text[7:9]
            other_sequence = other_text[7:9]
            
            # 设备类型代码: 第5位 (例如: T, P, A)
            self_type_code = self_text[4]
            other_type_code = other_text[4]
            
            # 排序优先级:
            # 1. 项目编号
            if self_project != other_project:
                return self_project < other_project
            
            # 2. 工段号 (转为整数比较)
            try:
                self_section_int = int(self_section)
                other_section_int = int(other_section)
                if self_section_int != other_section_int:
                    return self_section_int < other_section_int
            except ValueError:
                pass
            
            # 3. 设备序号 (转为整数比较)
            try:
                self_sequence_int = int(self_sequence)
                other_sequence_int = int(other_sequence)
                if self_sequence_int != other_sequence_int:
                    return self_sequence_int < other_sequence_int
            except ValueError:
                pass
            
            # 4. 设备类型代码 (自定义顺序)
            type_order = {
                'T': 0,  # 储罐/容器
                'A': 1,  # 搅拌/搅拌器
                'P': 2,  # 泵
                'C': 3,  # 压缩机
                'E': 4,  # 换热器
                'R': 5,  # 反应器
                'S': 6,  # 分离器
                'V': 7,  # 阀门
                'X': 8,  # 其他设备
            }
            
            self_order = type_order.get(self_type_code, 99)
            other_order = type_order.get(other_type_code, 99)
            
            if self_order != other_order:
                return self_order < other_order
            
            # 如果都相同，返回默认比较
            return self_text < other_text
            
        except (ValueError, IndexError, AttributeError):
            # 如果解析失败，使用默认的字符串比较
            return self_text < other_text