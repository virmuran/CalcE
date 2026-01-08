# modules/process_design/data/data_models.py
"""
统一数据模型 - 所有模块共享的基础数据类
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
import json

@dataclass
class UnifiedEquipment:
    """统一设备模型 - 整合所有模块的设备数据"""
    uid: str = ""  # 全局唯一ID
    equipment_id: str = ""  # 设备位号/编号
    code: str = ""  # 业务代码
    name: str = ""
    equipment_type: str = ""
    
    # 设备清单字段
    unique_code: str = ""
    specification: str = ""
    model: str = ""
    manufacturer: str = ""
    design_pressure: str = ""
    design_temperature: str = ""
    operating_pressure: str = ""
    operating_temperature: str = ""
    quantity: int = 1
    running_quantity: int = 1
    single_power: float = 0.0
    total_power: float = 0.0
    material: str = ""
    insulation: str = ""
    weight_estimate: float = 0.0
    operating_weight: float = 0.0
    unit_price: float = 0.0
    total_price: float = 0.0
    notes: str = ""
    
    # 流程图字段
    pfd_position: Dict[str, float] = field(default_factory=lambda: {"x": 0, "y": 0})
    pfd_size: Dict[str, float] = field(default_factory=lambda: {"width": 100, "height": 60})
    pfd_properties: Dict[str, Any] = field(default_factory=dict)
    pfd_connections: List[Dict] = field(default_factory=list)
    
    # MSDS关联字段
    msds_uid: str = ""
    hazard_class: str = ""
    material_cas: str = ""
    
    # 通用字段
    status: str = "active"
    location: str = ""
    description: str = ""
    tags: Set[str] = field(default_factory=set)
    
    # 时间戳
    created_at: str = ""
    updated_at: str = ""
    created_by: str = ""
    updated_by: str = ""
    
    # 版本控制
    version: int = 1
    revision_history: List[Dict] = field(default_factory=list)
    
    # 元数据
    source_module: str = ""
    completeness_score: float = 0.0
    
    def __post_init__(self):
        if not self.uid:
            from .uid_generator import global_uid_generator
            self.uid = global_uid_generator.generate_uid()
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        data = asdict(self)
        # 特殊处理集合类型
        if 'tags' in data:
            data['tags'] = list(data['tags'])
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UnifiedEquipment':
        """从字典创建对象"""
        # 处理集合类型
        if 'tags' in data and isinstance(data['tags'], list):
            data['tags'] = set(data['tags'])
        return cls(**data)
    
    def merge_with(self, other: 'UnifiedEquipment') -> 'UnifiedEquipment':
        """合并两个设备的数据"""
        merged = self.to_dict()
        other_dict = other.to_dict()
        
        # 智能合并策略：新数据覆盖空值，保留非空数据
        for key, value in other_dict.items():
            if value and (not merged[key] or isinstance(value, (dict, list)) and value):
                merged[key] = value
        
        # 更新版本和时间戳
        merged['version'] += 1
        merged['updated_at'] = datetime.now().isoformat()
        merged['revision_history'].append({
            'timestamp': merged['updated_at'],
            'version': merged['version'],
            'source': other.source_module
        })
        
        # 重新计算完整性
        merged_obj = self.from_dict(merged)
        merged_obj.get_completeness_score()
        
        return merged_obj
    
    def get_completeness_score(self) -> Dict[str, float]:
        """计算数据完整性评分"""
        scores = {
            'inventory': 0.0,
            'pfd': 0.0,
            'msds': 0.0,
            'material': 0.0
        }
        
        # 设备清单完整性（权重：40%）
        inventory_fields = ['unique_code', 'specification', 'model', 'manufacturer']
        filled = sum(1 for field in inventory_fields if getattr(self, field))
        scores['inventory'] = (filled / len(inventory_fields)) * 0.4
        
        # 流程图完整性（权重：30%）
        pfd_fields = ['pfd_position', 'pfd_properties']
        filled = sum(1 for field in pfd_fields if getattr(self, field))
        scores['pfd'] = (filled / len(pfd_fields)) * 0.3
        
        # MSDS完整性（权重：20%）
        msds_fields = ['msds_uid', 'hazard_class']
        filled = sum(1 for field in msds_fields if getattr(self, field))
        scores['msds'] = (filled / len(msds_fields)) * 0.2
        
        # 物料完整性（权重：10%）
        material_fields = ['material', 'material_cas']
        filled = sum(1 for field in material_fields if getattr(self, field))
        scores['material'] = (filled / len(material_fields)) * 0.1
        
        # 计算总分
        self.completeness_score = sum(scores.values())
        
        return {
            'overall': self.completeness_score,
            'by_module': scores
        }
    
    def get_empty_fields_by_module(self, module: str) -> List[str]:
        """获取指定模块的空字段"""
        module_field_maps = {
            'inventory': ['unique_code', 'specification', 'model', 'manufacturer'],
            'pfd': ['pfd_position', 'pfd_properties'],
            'msds': ['msds_uid', 'hazard_class'],
            'material': ['material', 'material_cas']
        }
        
        empty_fields = []
        for field_name in module_field_maps.get(module, []):
            if not getattr(self, field_name):
                empty_fields.append(field_name)
        
        return empty_fields
    
    @classmethod
    def create_from_inventory(cls, **kwargs) -> 'UnifiedEquipment':
        """从设备清单数据创建"""
        data = {
            'source_module': 'inventory',
            'unique_code': kwargs.get('unique_code', ''),
            'equipment_id': kwargs.get('equipment_id', ''),
            'name': kwargs.get('name', ''),
            'equipment_type': kwargs.get('type', ''),
            'specification': kwargs.get('specification', ''),
            'model': kwargs.get('model', ''),
            'manufacturer': kwargs.get('manufacturer', ''),
            'design_pressure': kwargs.get('design_pressure', ''),
            'design_temperature': kwargs.get('design_temperature', ''),
            'operating_pressure': kwargs.get('operating_pressure', ''),
            'operating_temperature': kwargs.get('operating_temperature', ''),
            'quantity': kwargs.get('quantity', 1),
            'running_quantity': kwargs.get('running_quantity', 1),
            'single_power': kwargs.get('single_power', 0.0),
            'total_power': kwargs.get('total_power', 0.0),
            'material': kwargs.get('material', ''),
            'insulation': kwargs.get('insulation', ''),
            'weight_estimate': kwargs.get('weight_estimate', 0.0),
            'operating_weight': kwargs.get('operating_weight', 0.0),
            'unit_price': kwargs.get('unit_price', 0.0),
            'total_price': kwargs.get('total_price', 0.0),
            'notes': kwargs.get('notes', ''),
            'status': kwargs.get('status', 'active'),
            'location': kwargs.get('location', '')
        }
        return cls(**data)
    
    @classmethod
    def create_from_pfd(cls, **kwargs) -> 'UnifiedEquipment':
        """从工艺流程图数据创建"""
        data = {
            'source_module': 'pfd',
            'equipment_id': kwargs.get('equipment_id', ''),
            'code': kwargs.get('code', ''),
            'name': kwargs.get('name', ''),
            'equipment_type': kwargs.get('type', ''),
            'pfd_position': kwargs.get('position', {'x': 0, 'y': 0}),
            'pfd_size': kwargs.get('size', {'width': 100, 'height': 60}),
            'pfd_properties': kwargs.get('properties', {}),
            'pfd_connections': kwargs.get('connections', [])
        }
        return cls(**data)

@dataclass
class MaterialProperty:
    """物料属性模型"""
    uid: str = ""
    material_id: str = ""
    name: str = ""
    cas_number: str = ""
    molecular_formula: str = ""
    molecular_weight: float = 0.0
    density: float = 0.0
    boiling_point: float = 0.0
    melting_point: float = 0.0
    flash_point: float = 0.0
    phase: str = "liquid"
    hazard_class: str = ""
    msds_id: str = ""
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.uid:
            from .uid_generator import global_uid_generator
            self.uid = global_uid_generator.generate_uid()
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MaterialProperty':
        return cls(**data)

@dataclass
class ProcessRoute:
    """工艺路线模型"""
    uid: str = ""
    route_id: str = ""
    name: str = ""
    product: str = ""
    description: str = ""
    steps: List[Dict] = field(default_factory=list)
    status: str = "draft"
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.uid:
            from .uid_generator import global_uid_generator
            self.uid = global_uid_generator.generate_uid()
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessRoute':
        return cls(**data)

@dataclass
class MSDSDocument:
    """MSDS文档模型"""
    uid: str = ""
    msds_id: str = ""
    material_name: str = ""
    cas_number: str = ""
    supplier: str = ""
    version: str = ""
    effective_date: str = ""
    expiry_date: str = ""
    hazard_class: str = ""
    status: str = "有效"
    description: str = ""
    file_path: str = ""
    file_size: int = 0
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.uid:
            from .uid_generator import global_uid_generator
            self.uid = global_uid_generator.generate_uid()
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MSDSDocument':
        return cls(**data)

@dataclass
class ProcessFlowDiagram:
    """工艺流程图模型"""
    uid: str = ""
    diagram_id: str = ""
    name: str = ""
    nodes: List[Dict] = field(default_factory=list)
    connections: List[Dict] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    equipment_uids: List[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.uid:
            from .uid_generator import global_uid_generator
            self.uid = global_uid_generator.generate_uid()
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessFlowDiagram':
        return cls(**data)

@dataclass
class ProcessProject:
    """工艺项目模型"""
    uid: str = ""
    project_id: str = ""
    name: str = ""
    description: str = ""
    status: str = "active"
    start_date: str = ""
    end_date: str = ""
    manager: str = ""
    created_at: str = ""
    updated_at: str = ""
    
    def __post_init__(self):
        if not self.uid:
            from .uid_generator import global_uid_generator
            self.uid = global_uid_generator.generate_uid()
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProcessProject':
        return cls(**data)