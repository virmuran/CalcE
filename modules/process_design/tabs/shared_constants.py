# modules/process_design/tabs/shared_constants.py
"""
共享常量定义
"""

# 设备类型定义
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

# 新设备类型分类
EQUIPMENT_TYPE_CATEGORIES = [
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

# 状态常量
STATUS_ACTIVE = "active"
STATUS_INACTIVE = "inactive"
STATUS_MAINTENANCE = "maintenance"
STATUS_DECOMMISSIONED = "decommissioned"

# 物料状态
MATERIAL_STATUS_ACTIVE = "active"
MATERIAL_STATUS_DISCONTINUED = "discontinued"

# MSDS状态
MSDS_STATUS_VALID = "有效"
MSDS_STATUS_EXPIRED = "已过期"
MSDS_STATUS_DRAFT = "草案"