# modules/process_design/tabs/pfd_constants.py

from PySide6.QtCore import *
from PySide6.QtGui import *

# 设备类型定义
EQUIPMENT_TYPE_DETAILED_MAPPING = {
    "vessel": {
        "pfd_type": "vessel",
        "inventory_type": "T 储罐",
        "icon": "📦",
        "color": QColor(100, 150, 200),
        "default_properties": {
            "capacity": "储罐",
            "material": "碳钢",
            "dynamic": "静设备"
        }
    },
    "pump": {
        "pfd_type": "pump", 
        "inventory_type": "P 泵类",
        "icon": "🔧",
        "color": QColor(150, 100, 200),
        "default_properties": {
            "capacity": "输送",
            "material": "不锈钢",
            "dynamic": "动设备",
            "single_power": 7.5,
            "total_power": 7.5
        }
    },
    "reactor": {
        "pfd_type": "reactor",
        "inventory_type": "R 反应器",
        "icon": "⚗️",
        "color": QColor(200, 100, 100),
        "default_properties": {
            "capacity": "反应",
            "material": "不锈钢",
            "dynamic": "静设备"
        }
    },
    "heat_exchanger": {
        "pfd_type": "heat_exchanger",
        "inventory_type": "E 换热设备类",
        "icon": "🔥",
        "color": QColor(200, 150, 50),
        "default_properties": {
            "capacity": "换热",
            "material": "不锈钢",
            "dynamic": "静设备"
        }
    },
    "column": {
        "pfd_type": "column",
        "inventory_type": "C 塔器",
        "icon": "🗼",
        "color": QColor(100, 200, 150),
        "default_properties": {
            "capacity": "分离",
            "material": "不锈钢",
            "dynamic": "静设备"
        }
    },
    "valve": {
        "pfd_type": "valve",
        "inventory_type": "其他",
        "icon": "🚰",
        "color": QColor(150, 200, 100),
        "default_properties": {
            "capacity": "控制",
            "material": "铸钢",
            "dynamic": "静设备"
        }
    },
    "filter": {
        "pfd_type": "filter",
        "inventory_type": "S 分离设备类",
        "icon": "🧹",
        "color": QColor(100, 200, 200),
        "default_properties": {
            "capacity": "过滤",
            "material": "不锈钢",
            "dynamic": "静设备"
        }
    },
    "mixer": {
        "pfd_type": "mixer",
        "inventory_type": "A 搅拌设备类",
        "icon": "🌀",
        "color": QColor(200, 100, 150),
        "default_properties": {
            "capacity": "混合",
            "material": "不锈钢",
            "dynamic": "动设备",
            "single_power": 5.5,
            "total_power": 5.5
        }
    },
    "separator": {
        "pfd_type": "separator",
        "inventory_type": "S 分离设备类",
        "icon": "⚖️",
        "color": QColor(150, 150, 200),
        "default_properties": {
            "capacity": "分离",
            "material": "碳钢",
            "dynamic": "静设备"
        }
    }
}

EQUIPMENT_TYPES = {}
for key, info in EQUIPMENT_TYPE_DETAILED_MAPPING.items():
    EQUIPMENT_TYPES[key] = {
        "name": info["default_properties"]["capacity"],
        "icon": info["icon"],
        "color": info["color"]
    }

# 物料类型定义
MATERIAL_TYPES = {
    "liquid": {"name": "液体", "color": QColor(0, 100, 200)},
    "gas": {"name": "气体", "color": QColor(200, 100, 0)},
    "solid": {"name": "固体", "color": QColor(150, 100, 50)},
    "slurry": {"name": "浆料", "color": QColor(100, 100, 150)}
}