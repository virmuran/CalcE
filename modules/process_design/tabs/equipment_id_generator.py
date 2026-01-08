# modules/process_design/tabs/equipment_id_generator.py
"""
设备ID生成器
"""
import hashlib
import uuid
from datetime import datetime

class EquipmentIDGenerator:
    """设备ID生成器"""
    
    @staticmethod
    def generate_equipment_id(equipment_type, custom_seed=None):
        """
        生成设备唯一编码
        
        参数:
            equipment_type: 设备类型
            custom_seed: 自定义种子（如设备名称）
        
        返回:
            设备唯一编码
        """
        # 生成基础部分
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # 使用类型和种子创建哈希
        seed_str = f"{equipment_type}_{custom_seed or ''}_{timestamp}"
        hash_str = hashlib.md5(seed_str.encode()).hexdigest()[:8].upper()
        
        # 构建ID格式: 类型首字母_哈希_时间戳
        type_code = equipment_type[:1] if equipment_type else "X"
        equipment_id = f"{type_code}_{hash_str}"
        
        return equipment_id
    
    @staticmethod
    def generate_unique_code():
        """生成全局唯一编码"""
        return str(uuid.uuid4()).upper()