# modules/process_design/__init__.py
"""
工艺设计模块包
"""

__version__ = "1.0.0"
__author__ = "TofuApp Team"

import os
import sys
from pathlib import Path

print("🚀 初始化 process_design 包")

# 添加当前目录到 Python 路径
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

print(f"📁 工艺设计模块路径: {current_dir}")

# 导出主要的类和函数
from .process_design_widget import ProcessDesignWidget
from .process_design_manager import ProcessDesignManager
from .process_design_data import MaterialProperty

# 尝试导入其他模块
try:
    from .tabs.material_database_tab import MaterialDatabaseTab
    print("✅ 成功导入 MaterialDatabaseTab")
except ImportError as e:
    print(f"❌ 导入 MaterialDatabaseTab 失败: {e}")
    # 创建简单的占位符
    class MaterialDatabaseTab:
        def __init__(self, *args, **kwargs):
            pass
        def load_materials(self):
            pass

# 动态导入函数
def import_material_database_tab():
    """动态导入 MaterialDatabaseTab"""
    try:
        from .tabs.material_database_tab import MaterialDatabaseTab
        return MaterialDatabaseTab
    except ImportError:
        try:
            from .material_database_tab import MaterialDatabaseTab
            return MaterialDatabaseTab
        except ImportError:
            return None
        
def import_equipment_list_tab():
    """动态导入 EquipmentListTab"""
    try:
        from .tabs.equipment_list_tab import EquipmentListTab
        return EquipmentListTab
    except ImportError as e:
        print(f"❌ 导入 EquipmentListTab 失败: {e}")
        return None
    
def import_msds_manager_tab():
    """动态导入 MSDSManagerTab"""
    try:
        from .tabs.msds_manager_tab import MSDSManagerTab
        return MSDSManagerTab
    except ImportError as e:
        print(f"❌ 导入 MSDSManagerTab 失败: {e}")
        try:
            from .msds_manager_tab import MSDSManagerTab
            return MSDSManagerTab
        except ImportError:
            return None
    
# 导出常用类
__all__ = [
    'MaterialProperty',
    'ProcessDesignManager',
    'ProcessDesignWidget',
    'MaterialDatabaseTab',
    'import_material_database_tab',
    'import_equipment_list_tab', 
    'import_msds_manager_tab',
]

print("🚀 工艺设计模块初始化完成")