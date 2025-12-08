# TofuApp\modules\process_design\process_design_manager.py
import sys
import os

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from .process_design_data import ProcessProject, MaterialProperty, EquipmentItem, MSDSDocument
    print("✅ 成功导入 process_design_data")
except ImportError as e:
    print(f"❌ 导入 process_design_data 失败: {e}")
    # 尝试绝对导入
    try:
        from process_design_data import ProcessProject, MaterialProperty, EquipmentItem, MSDSDocument
        print("✅ 成功使用绝对导入")
    except ImportError:
        print("⚠️  无法导入 process_design_data")
        # 创建简单的占位符类
        class ProcessProject:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
            
            def to_dict(self):
                return self.__dict__
            
            @classmethod
            def from_dict(cls, data):
                return cls(**data)
        
        class MaterialProperty:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
            
            def to_dict(self):
                return self.__dict__
            
            @classmethod
            def from_dict(cls, data):
                return cls(**data)
        
        class EquipmentItem:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
            
            def to_dict(self):
                return self.__dict__
            
            @classmethod
            def from_dict(cls, data):
                return cls(**data)
        
        class MSDSDocument:
            def __init__(self, **kwargs):
                for key, value in kwargs.items():
                    setattr(self, key, value)
            
            def to_dict(self):
                return self.__dict__
            
            @classmethod
            def from_dict(cls, data):
                return cls(**data)

from datetime import datetime
from typing import List, Optional, Dict, Any

class ProcessDesignManager:
    """工艺设计数据管理器"""
    
    def __init__(self, data_manager=None):
        self.data_manager = data_manager
        self.data_key = "process_design"
        
        # 初始化默认数据结构
        self._init_default_data()
    
    def _init_default_data(self):
        """初始化默认数据结构"""
        if self.data_manager is None:
            return
            
        data = self.data_manager.data
        if self.data_key not in data:
            data[self.data_key] = {
                "projects": [],
                "materials": [],
                "equipment": [],
                "msds_documents": []  # 添加MSDS文档数据
            }
            self.data_manager._save_data()
    
    # ==================== MSDS 文档相关方法 ====================
    
    def get_all_msds(self) -> List[MSDSDocument]:
        """获取所有MSDS文档"""
        if self.data_manager is None:
            return []
            
        data = self.data_manager.data[self.data_key]
        msds_list = data.get("msds_documents", [])
        
        return [MSDSDocument.from_dict(m) for m in msds_list]
    
    def get_msds(self, msds_id: str) -> Optional[MSDSDocument]:
        """获取MSDS文档"""
        if self.data_manager is None:
            return None
            
        data = self.data_manager.data[self.data_key]
        msds_list = data.get("msds_documents", [])
        
        for m in msds_list:
            if m.get("msds_id") == msds_id:
                return MSDSDocument.from_dict(m)
        return None
    
    def add_msds(self, msds: MSDSDocument) -> bool:
        """添加MSDS文档"""
        if self.data_manager is None:
            return False
            
        data = self.data_manager.data[self.data_key]
        msds_list = data.get("msds_documents", [])
        
        # 检查MSDS ID是否已存在
        for m in msds_list:
            if m.get("msds_id") == msds.msds_id:
                return False
        
        msds_list.append(msds.to_dict())
        self.data_manager._save_data()
        return True
    
    def update_msds(self, msds: MSDSDocument) -> bool:
        """更新MSDS文档"""
        if self.data_manager is None:
            return False
            
        data = self.data_manager.data[self.data_key]
        msds_list = data.get("msds_documents", [])
        
        for i, m in enumerate(msds_list):
            if m.get("msds_id") == msds.msds_id:
                msds_list[i] = msds.to_dict()
                self.data_manager._save_data()
                return True
        
        return False
    
    def delete_msds(self, msds_id: str) -> bool:
        """删除MSDS文档"""
        if self.data_manager is None:
            return False
            
        data = self.data_manager.data[self.data_key]
        msds_list = data.get("msds_documents", [])
        
        for i, m in enumerate(msds_list):
            if m.get("msds_id") == msds_id:
                del msds_list[i]
                self.data_manager._save_data()
                return True
        
        return False
    
    def search_msds(self, search_term: str) -> List[MSDSDocument]:
        """搜索MSDS文档"""
        if self.data_manager is None:
            return []
            
        data = self.data_manager.data[self.data_key]
        msds_list = data.get("msds_documents", [])
        
        results = []
        search_term = search_term.lower()
        
        for m in msds_list:
            # 搜索物料名称
            if search_term in m.get("material_name", "").lower():
                results.append(MSDSDocument.from_dict(m))
                continue
            
            # 搜索CAS号
            if search_term in m.get("cas_number", "").lower():
                results.append(MSDSDocument.from_dict(m))
                continue
            
            # 搜索供应商
            if search_term in m.get("supplier", "").lower():
                results.append(MSDSDocument.from_dict(m))
                continue
            
            # 搜索MSDS ID
            if search_term in m.get("msds_id", "").lower():
                results.append(MSDSDocument.from_dict(m))
                continue
            
            # 搜索危险类别
            if search_term in m.get("hazard_class", "").lower():
                results.append(MSDSDocument.from_dict(m))
                continue
        
        return results
    
    def advanced_search_msds(self, criteria: Dict[str, Any]) -> List[MSDSDocument]:
        """高级搜索MSDS文档"""
        if self.data_manager is None:
            return []
            
        data = self.data_manager.data[self.data_key]
        msds_list = data.get("msds_documents", [])
        
        results = []
        
        for m in msds_list:
            msds = MSDSDocument.from_dict(m)
            match = True
            
            # 供应商过滤
            if 'supplier' in criteria:
                if criteria['supplier'].lower() not in msds.supplier.lower():
                    match = False
            
            # 版本过滤
            if 'version' in criteria:
                if criteria['version'].lower() not in msds.version.lower():
                    match = False
            
            # 生效日期范围过滤
            if 'start_date' in criteria and msds.effective_date:
                try:
                    start_date = datetime.strptime(criteria['start_date'], '%Y-%m-%d')
                    if msds.effective_date < start_date:
                        match = False
                except ValueError:
                    pass
            
            if 'end_date' in criteria and msds.effective_date:
                try:
                    end_date = datetime.strptime(criteria['end_date'], '%Y-%m-%d')
                    if msds.effective_date > end_date:
                        match = False
                except ValueError:
                    pass
            
            # 危险类别过滤
            if 'hazard_classes' in criteria and msds.hazard_class:
                hazard_match = False
                for hazard in criteria['hazard_classes']:
                    if hazard in msds.hazard_class:
                        hazard_match = True
                        break
                if not hazard_match:
                    match = False
            
            # 状态过滤
            if 'status' in criteria:
                if msds.status != criteria['status']:
                    match = False
            
            if match:
                results.append(msds)
        
        return results
    
    def get_material_by_cas(self, cas_number: str) -> Optional[MaterialProperty]:
        """根据CAS号获取物料"""
        if self.data_manager is None:
            return None
            
        data = self.data_manager.data[self.data_key]
        materials = data.get("materials", [])
        
        for m in materials:
            if m.get("cas_number") == cas_number:
                return MaterialProperty.from_dict(m)
        return None
    
    # ==================== 项目相关方法 ====================
    
    def create_project(self, project: ProcessProject) -> bool:
        """创建新项目"""
        data = self.data_manager.data[self.data_key]
        projects = data["projects"]
        
        # 检查项目ID是否已存在
        for p in projects:
            if p["project_id"] == project.project_id:
                return False
        
        projects.append(project.to_dict())
        self.data_manager._save_data()
        return True
    
    def get_project(self, project_id: str) -> Optional[ProcessProject]:
        """获取项目"""
        data = self.data_manager.data[self.data_key]
        projects = data["projects"]
        
        for p in projects:
            if p["project_id"] == project_id:
                return ProcessProject.from_dict(p)
        return None
    
    def get_all_projects(self) -> List[ProcessProject]:
        """获取所有项目"""
        data = self.data_manager.data[self.data_key]
        projects = data["projects"]
        
        return [ProcessProject.from_dict(p) for p in projects]
    
    def update_project(self, project: ProcessProject) -> bool:
        """更新项目"""
        data = self.data_manager.data[self.data_key]
        projects = data["projects"]
        
        for i, p in enumerate(projects):
            if p["project_id"] == project.project_id:
                projects[i] = project.to_dict()
                self.data_manager._save_data()
                return True
        
        return False
    
    def delete_project(self, project_id: str) -> bool:
        """删除项目"""
        data = self.data_manager.data[self.data_key]
        projects = data["projects"]
        
        for i, p in enumerate(projects):
            if p["project_id"] == project_id:
                del projects[i]
                self.data_manager._save_data()
                return True
        
        return False
    
    # ==================== 物料相关方法 ====================
    
    def add_material(self, material: MaterialProperty) -> bool:
        """添加物料"""
        data = self.data_manager.data[self.data_key]
        materials = data["materials"]
        
        # 检查物料ID是否已存在
        for m in materials:
            if m["material_id"] == material.material_id:
                return False
        
        materials.append(material.to_dict())
        self.data_manager._save_data()
        return True
    
    def get_material(self, material_id: str) -> Optional[MaterialProperty]:
        """获取物料"""
        data = self.data_manager.data[self.data_key]
        materials = data["materials"]
        
        for m in materials:
            if m["material_id"] == material_id:
                return MaterialProperty.from_dict(m)
        return None
    
    def get_all_materials(self) -> List[MaterialProperty]:
        """获取所有物料"""
        data = self.data_manager.data[self.data_key]
        materials = data["materials"]
        
        return [MaterialProperty.from_dict(m) for m in materials]
    
    def update_material(self, material: MaterialProperty) -> bool:
        """更新物料"""
        data = self.data_manager.data[self.data_key]
        materials = data["materials"]
        
        for i, m in enumerate(materials):
            if m["material_id"] == material.material_id:
                materials[i] = material.to_dict()
                self.data_manager._save_data()
                return True
        
        return False
    
    def delete_material(self, material_id: str) -> bool:
        """删除物料"""
        data = self.data_manager.data[self.data_key]
        materials = data["materials"]
        
        for i, m in enumerate(materials):
            if m["material_id"] == material_id:
                del materials[i]
                self.data_manager._save_data()
                return True
        
        return False
    
    def search_materials(self, search_term: str) -> List[MaterialProperty]:
        """搜索物料"""
        data = self.data_manager.data[self.data_key]
        materials = data["materials"]
        
        results = []
        search_term = search_term.lower()
        
        for m in materials:
            # 搜索物料名称
            if search_term in m.get("name", "").lower():
                results.append(MaterialProperty.from_dict(m))
                continue
            
            # 搜索CAS号
            if search_term in m.get("cas_number", "").lower():
                results.append(MaterialProperty.from_dict(m))
                continue
            
            # 搜索物料ID
            if search_term in m.get("material_id", "").lower():
                results.append(MaterialProperty.from_dict(m))
                continue
            
            # 搜索分子式
            if search_term in m.get("molecular_formula", "").lower():
                results.append(MaterialProperty.from_dict(m))
                continue
            
            # 搜索危险类别
            if search_term in m.get("hazard_class", "").lower():
                results.append(MaterialProperty.from_dict(m))
                continue
        
        return results
    
    def advanced_search_materials(self, criteria: Dict[str, Any]) -> List[MaterialProperty]:
        """高级搜索物料"""
        data = self.data_manager.data[self.data_key]
        materials = data["materials"]
        
        results = []
        
        for m in materials:
            material = MaterialProperty.from_dict(m)
            match = True
            
            # 分子量范围过滤
            if 'min_molecular_weight' in criteria:
                if material.molecular_weight < criteria['min_molecular_weight']:
                    match = False
            
            if 'max_molecular_weight' in criteria:
                if material.molecular_weight > criteria['max_molecular_weight']:
                    match = False
            
            # 密度范围过滤
            if 'min_density' in criteria and material.density:
                if material.density < criteria['min_density']:
                    match = False
            
            if 'max_density' in criteria and material.density:
                if material.density > criteria['max_density']:
                    match = False
            
            # 沸点范围过滤
            if 'min_boiling_point' in criteria and material.boiling_point:
                if material.boiling_point < criteria['min_boiling_point']:
                    match = False
            
            if 'max_boiling_point' in criteria and material.boiling_point:
                if material.boiling_point > criteria['max_boiling_point']:
                    match = False
            
            # 危险类别过滤
            if 'hazard_classes' in criteria and material.hazard_class:
                hazard_match = False
                for hazard in criteria['hazard_classes']:
                    if hazard in material.hazard_class:
                        hazard_match = True
                        break
                if not hazard_match:
                    match = False
            
            if match:
                results.append(material)
        
        return results
    
    def material_exists(self, material_id: str) -> bool:
        """检查物料是否存在"""
        return self.get_material(material_id) is not None
    
    def get_materials_count(self) -> int:
        """获取物料总数"""
        data = self.data_manager.data[self.data_key]
        materials = data["materials"]
        return len(materials)
    
    # ==================== 设备相关方法 ====================
    
    def add_equipment(self, equipment: EquipmentItem) -> bool:
        """添加设备"""
        data = self.data_manager.data[self.data_key]
        equipment_list = data["equipment"]
        
        # 检查设备ID是否已存在
        for e in equipment_list:
            if e["equipment_id"] == equipment.equipment_id:
                return False
        
        equipment_list.append(equipment.to_dict())
        self.data_manager._save_data()
        return True
    
    def get_equipment(self, equipment_id: str) -> Optional[EquipmentItem]:
        """获取设备"""
        data = self.data_manager.data[self.data_key]
        equipment_list = data["equipment"]
        
        for e in equipment_list:
            if e["equipment_id"] == equipment_id:
                return EquipmentItem.from_dict(e)
        return None
    
    def get_all_equipment(self) -> List[EquipmentItem]:
        """获取所有设备"""
        data = self.data_manager.data[self.data_key]
        equipment_list = data["equipment"]
        
        return [EquipmentItem.from_dict(e) for e in equipment_list]
    
    def get_equipment_by_project(self, project_id: str) -> List[EquipmentItem]:
        """根据项目ID获取设备清单"""
        # 这里简化处理，返回所有设备
        # 实际应用中可能需要根据项目ID过滤设备
        return self.get_all_equipment()
    
    def update_equipment(self, equipment: EquipmentItem) -> bool:
        """更新设备"""
        data = self.data_manager.data[self.data_key]
        equipment_list = data["equipment"]
        
        for i, e in enumerate(equipment_list):
            if e["equipment_id"] == equipment.equipment_id:
                equipment_list[i] = equipment.to_dict()
                self.data_manager._save_data()
                return True
        
        return False
    
    def delete_equipment(self, equipment_id: str) -> bool:
        """删除设备"""
        data = self.data_manager.data[self.data_key]
        equipment_list = data["equipment"]
        
        for i, e in enumerate(equipment_list):
            if e["equipment_id"] == equipment_id:
                del equipment_list[i]
                self.data_manager._save_data()
                return True
        
        return False
    
    def import_materials(self, materials_data: List[Dict], mode: str = 'append') -> Dict[str, int]:
        """批量导入物料"""
        stats = {'success': 0, 'failed': 0, 'skipped': 0}
        
        # 如果是替换模式，先清空所有物料
        if mode == 'replace':
            data = self.data_manager.data[self.data_key]
            data["materials"] = []
        
        for item_data in materials_data:
            try:
                material = MaterialProperty.from_dict(item_data)
                
                # 检查物料是否存在
                existing = self.get_material(material.material_id)
                
                if existing:
                    if mode == 'update':
                        # 更新现有物料
                        if self.update_material(material):
                            stats['success'] += 1
                        else:
                            stats['failed'] += 1
                    else:  # append模式，跳过
                        stats['skipped'] += 1
                else:
                    # 添加新物料
                    if self.add_material(material):
                        stats['success'] += 1
                    else:
                        stats['failed'] += 1
                        
            except Exception:
                stats['failed'] += 1
        
        return stats