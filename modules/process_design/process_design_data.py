# TofuApp\modules\process_design\process_design_data.py
import sys
import os
from datetime import datetime, date
import json

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

print(f"📁 工艺设计数据模块路径: {current_dir}")

from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional, Any

class JSONEncoder(json.JSONEncoder):
    """自定义JSON编码器，处理datetime和date对象"""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

@dataclass
class MSDSDocument:
    """MSDS文档数据类"""
    msds_id: str
    material_name: str
    cas_number: str
    supplier: str = ""
    version: str = "1.0"
    effective_date: datetime = field(default_factory=datetime.now)
    expiry_date: Optional[datetime] = None
    hazard_class: str = ""
    status: str = "有效"
    description: str = ""
    
    # 危险信息
    hazard_statements: str = ""
    precautionary_statements: str = ""  # 注意：修复拼写错误
    symptoms: str = ""
    
    # 应急处理
    first_aid_measures: str = ""
    fire_fighting_measures: str = ""
    accidental_release_measures: str = ""
    
    # 存储运输
    handling_and_storage: str = ""
    exposure_controls: str = ""
    transport_information: str = ""
    
    # 文件信息
    file_path: str = ""
    file_name: str = ""
    file_size: Optional[int] = None
    file_type: str = ""
    
    # 元数据
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，处理datetime对象"""
        result = {}
        for key, value in self.__dict__.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, date):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MSDSDocument':
        """从字典创建对象"""
        # 处理datetime字符串
        datetime_fields = ['effective_date', 'expiry_date', 'created_at', 'updated_at', 'last_updated']
        
        processed_data = data.copy()
        for field_name in datetime_fields:
            if field_name in processed_data and processed_data[field_name]:
                if isinstance(processed_data[field_name], str):
                    try:
                        # 尝试解析ISO格式
                        processed_data[field_name] = datetime.fromisoformat(processed_data[field_name].replace('Z', '+00:00'))
                    except ValueError:
                        # 尝试其他格式
                        try:
                            processed_data[field_name] = datetime.strptime(processed_data[field_name], '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            try:
                                processed_data[field_name] = datetime.strptime(processed_data[field_name], '%Y-%m-%d')
                            except ValueError:
                                processed_data[field_name] = datetime.now()
                elif isinstance(processed_data[field_name], (int, float)):
                    # 可能是时间戳
                    processed_data[field_name] = datetime.fromtimestamp(processed_data[field_name])
            elif field_name in ['expiry_date']:
                # expiry_date 可以为 None
                if field_name in processed_data and not processed_data[field_name]:
                    processed_data[field_name] = None
        
        # 过滤掉不存在的字段
        import dataclasses
        valid_fields = {f.name for f in dataclasses.fields(cls)}
        filtered_data = {k: v for k, v in processed_data.items() if k in valid_fields}
        
        return cls(**filtered_data)
    
    def validate(self) -> List[str]:
        """验证数据，返回错误列表"""
        errors = []
        
        if not self.msds_id.strip():
            errors.append("MSDS ID不能为空")
        
        if not self.material_name.strip():
            errors.append("物料名称不能为空")
        
        if not self.cas_number.strip():
            errors.append("CAS号不能为空")
        
        if self.expiry_date and self.effective_date and self.expiry_date < self.effective_date:
            errors.append("有效期不能早于生效日期")
        
        return errors
    
    def is_expired(self) -> bool:
        """检查是否过期"""
        if not self.expiry_date:
            return False
        return datetime.now() > self.expiry_date
    
    def days_until_expiry(self) -> Optional[int]:
        """距离过期的天数（负数表示已过期）"""
        if not self.expiry_date:
            return None
        delta = self.expiry_date - datetime.now()
        return delta.days

@dataclass
class MaterialProperty:
    """物料物性参数"""
    material_id: str
    name: str
    cas_number: str = ""
    molecular_formula: str = ""
    molecular_weight: float = 0.0
    density: Optional[float] = None
    boiling_point: Optional[float] = None
    melting_point: Optional[float] = None
    flash_point: Optional[float] = None
    phase: str = "liquid"
    hazard_class: str = ""
    notes: str = ""
    
    # 添加更多物理化学性质（可选）
    vapor_pressure: Optional[float] = None
    viscosity: Optional[float] = None
    heat_capacity: Optional[float] = None
    solubility: Optional[str] = None
    
    # 元数据
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        # 过滤掉不存在的字段
        import dataclasses
        valid_fields = {f.name for f in dataclasses.fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)
    
    def validate(self) -> List[str]:
        """验证数据，返回错误列表"""
        errors = []
        
        if not self.material_id.strip():
            errors.append("物料ID不能为空")
        
        if not self.name.strip():
            errors.append("物料名称不能为空")
        
        if self.molecular_weight < 0:
            errors.append("分子量不能为负数")
        
        if self.density and self.density < 0:
            errors.append("密度不能为负数")
        
        if self.phase not in ["liquid", "solid", "gas"]:
            errors.append("相态必须是 liquid, solid 或 gas")
        
        return errors

@dataclass
class ProcessProject:
    """工艺设计项目"""
    project_id: str
    name: str
    client: str = ""
    design_capacity: float = 0.0
    operating_hours: float = 8000.0
    description: str = ""
    
    # 元数据
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)

@dataclass
class EquipmentItem:
    """设备清单项"""
    equipment_id: str
    name: str
    type: str
    model: str = ""
    specification: str = ""
    manufacturer: str = ""
    location: str = ""
    status: str = ""
    commission_date: Optional[str] = None
    design_pressure: Optional[float] = None
    design_temperature: Optional[float] = None
    capacity: str = ""
    project_id: str = ""
    description: str = ""
    description_en: str = ""  # 新增：英文描述
    tag_number: str = ""
    equipment_type: str = ""
    notes: str = ""

    # 新增字段，用于导出设备清单
    pid_dwg_no: str = ""  # P&ID DWG. NO.
    quantity: int = 1  # QTY.
    unit_price: Optional[float] = None  # 单价
    total_price: Optional[float] = None  # 总价
    operating_temperature: Optional[float] = None  # 操作温度
    operating_pressure: Optional[float] = None  # 操作压力
    estimated_power: Optional[float] = None  # 估计功率
    material: str = ""  # 材质
    insulation: str = ""  # 保温
    weight_estimate: Optional[float] = None  # 重量估计
    dynamic: str = ""  # 动态
    
    # 元数据
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        # 过滤掉不存在的字段
        import dataclasses
        valid_fields = {f.name for f in dataclasses.fields(cls)}
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered_data)

@dataclass
class ProcessStream:
    """工艺流股"""
    stream_id: str
    name: str
    source_equipment: str = ""
    destination_equipment: str = ""
    temperature: float = 25.0
    pressure: float = 101.3
    flow_rate: float = 0.0
    composition: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)