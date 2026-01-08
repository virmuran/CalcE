# TofuApp/modules/process_design/data/__init__.py
"""
工艺设计数据层模块
"""

from .uid_generator import UIDGenerator, global_uid_generator
from .data_models import (
    UnifiedEquipment, MaterialProperty, 
    ProcessRoute, MSDSDocument, ProcessFlowDiagram,
    ProcessProject  # 添加 ProcessProject
)
from .unified_data_manager import UIDDataManager, global_data_manager
from .module_interfaces import ModuleInterface
from .data_sync import DataSyncManager

__all__ = [
    'UIDGenerator',
    'global_uid_generator',
    'UnifiedEquipment',
    'MaterialProperty',
    'ProcessRoute',
    'MSDSDocument',
    'ProcessFlowDiagram',
    'ProcessProject',  # 添加到 __all__
    'UIDDataManager',
    'global_data_manager',
    'ModuleInterface',
    'DataSyncManager'
]