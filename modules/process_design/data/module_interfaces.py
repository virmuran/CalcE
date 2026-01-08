# TofuApp/modules/process_design/data/module_interfaces.py
"""
模块接口适配器 - 各模块通过这个接口访问统一数据
"""
from typing import Dict, List, Any, Optional

from .unified_data_manager import UIDDataManager
from .data_models import (
    UnifiedEquipment, MaterialProperty, 
    MSDSDocument, ProcessFlowDiagram, ProcessRoute, ProcessProject
)

class ModuleInterface:
    """模块统一接口"""
    
    def __init__(self, data_manager: UIDDataManager):
        self.data_manager = data_manager
    
    # ==================== 设备清单模块接口 ====================
    
    def inventory_save_equipment(self, inventory_data: Dict) -> str:
        """设备清单模块保存设备"""
        # 检查是否已存在（通过业务代码）
        existing = self.data_manager.get_equipment_by_code(inventory_data.get('code', ''))
        
        if existing:
            # 更新现有设备
            updated = existing.merge_with(
                UnifiedEquipment.create_from_inventory(**inventory_data)
            )
            if self.data_manager.save_equipment(updated):
                return updated.uid
        else:
            # 创建设备
            equipment = UnifiedEquipment.create_from_inventory(**inventory_data)
            if self.data_manager.save_equipment(equipment):
                return equipment.uid
        
        return ""
    
    def inventory_get_equipment_list(self) -> List[Dict]:
        """设备清单模块获取设备列表"""
        equipment_list = self.data_manager.get_all_equipment()
        
        result = []
        for eq in equipment_list:
            # 转换为设备清单格式
            item = eq.to_dict()
            
            # 添加数据完整性信息
            scores = eq.get_completeness_score()
            item['data_completeness'] = {
                'overall': scores['overall'],
                'inventory': scores['by_module'].get('inventory', 0),
                'pfd': scores['by_module'].get('pfd', 0),
                'msds': scores['by_module'].get('msds', 0)
            }
            
            # 标记需要补充的字段
            item['needs_inventory_data'] = eq.get_empty_fields_by_module('inventory')
            
            result.append(item)
        
        return result
    
    def inventory_get_equipment_detail(self, uid: str) -> Optional[Dict]:
        """设备清单模块获取设备详情"""
        equipment = self.data_manager.get_equipment(uid)
        if not equipment:
            return None
        
        detail = equipment.to_dict()
        
        # 添加所有模块的数据
        detail['all_module_data'] = {
            'inventory': self._extract_inventory_data(equipment),
            'pfd': self._extract_pfd_data(equipment),
            'msds': self._extract_msds_data(equipment)
        }
        
        return detail
    
    # ==================== 工艺流程图模块接口 ====================
    
    def pfd_save_equipment(self, pfd_data: Dict) -> str:
        """工艺流程图模块保存设备"""
        # 检查是否已存在（通过业务代码）
        code = pfd_data.get('code', '')
        if code:
            existing = self.data_manager.get_equipment_by_code(code)
        else:
            existing = None
        
        if existing:
            # 更新现有设备
            pfd_equipment = UnifiedEquipment.create_from_pfd(**pfd_data)
            updated = existing.merge_with(pfd_equipment)
            if self.data_manager.save_equipment(updated):
                return updated.uid
        else:
            # 创建设备
            equipment = UnifiedEquipment.create_from_pfd(**pfd_data)
            if self.data_manager.save_equipment(equipment):
                return equipment.uid
        
        return ""
    
    def pfd_get_equipment_for_diagram(self) -> List[Dict]:
        """工艺流程图模块获取设备数据"""
        equipment_list = self.data_manager.get_all_equipment()
        
        result = []
        for eq in equipment_list:
            # 只提取流程图需要的数据
            item = {
                'uid': eq.uid,
                'code': eq.code,
                'name': eq.name,
                'type': eq.equipment_type,
                'position': eq.pfd_position,
                'size': eq.pfd_size,
                'properties': eq.pfd_properties,
                # 显示设备清单的补充信息（只读）
                'inventory_info': {
                    'has_inventory': bool(eq.unique_code),
                    'specification': eq.specification,
                    'price': f"¥{eq.total_price:,.2f}" if eq.total_price else "未设置",
                    'status': '已完善' if eq.unique_code else '待补充'
                }
            }
            result.append(item)
        
        return result
    
    def pfd_save_diagram(self, diagram_data: Dict) -> str:
        """保存工艺流程图"""
        # 创建或更新流程图
        diagram = ProcessFlowDiagram(
            uid=diagram_data.get('uid', ''),
            diagram_id=diagram_data.get('diagram_id', ''),
            name=diagram_data.get('name', ''),
            nodes=diagram_data.get('nodes', []),
            connections=diagram_data.get('connections', []),
            metadata=diagram_data.get('metadata', {}),
            equipment_uids=diagram_data.get('equipment_uids', [])
        )
        
        # 保存到数据库
        return self.data_manager.save_process_flow(diagram)
    
    # ==================== MSDS模块接口 ====================
    
    def msds_link_to_equipment(self, msds_uid: str, equipment_uid: str) -> bool:
        """将MSDS关联到设备"""
        equipment = self.data_manager.get_equipment(equipment_uid)
        if not equipment:
            return False
        
        equipment.msds_uid = msds_uid
        
        # 获取MSDS的危险类别等信息，更新到设备
        msds = self.data_manager.get_msds(msds_uid)
        if msds:
            equipment.hazard_class = msds.hazard_class
            equipment.material_cas = msds.cas_number
        
        return bool(self.data_manager.save_equipment(equipment))
    
    def msds_get_equipment_without_msds(self) -> List[Dict]:
        """获取没有关联MSDS的设备"""
        equipment_list = self.data_manager.get_all_equipment()
        
        result = []
        for eq in equipment_list:
            if not eq.msds_uid:
                result.append({
                    'uid': eq.uid,
                    'code': eq.code,
                    'name': eq.name,
                    'equipment_type': eq.equipment_type,
                    'material': eq.material,
                    'hazard_class': eq.hazard_class
                })
        
        return result
    
    # ==================== 物料模块接口 ====================
    
    def material_save_material(self, material_data: Dict) -> str:
        """保存物料"""
        material = MaterialProperty.from_dict(material_data)
        return self.data_manager.save_material(material)
    
    def material_get_material(self, uid: str) -> Optional[Dict]:
        """获取物料"""
        material = self.data_manager.get_material(uid)
        if material:
            return material.to_dict()
        return None
    
    def material_get_all_materials(self) -> List[Dict]:
        """获取所有物料"""
        materials = self.data_manager.get_all_materials()
        return [m.to_dict() for m in materials]
    
    def material_search_materials(self, search_term: str) -> List[Dict]:
        """搜索物料"""
        materials = self.data_manager.search_materials(search_term)
        return [m.to_dict() for m in materials]
    
    # ==================== 工艺路线模块接口 ====================
    
    def route_save_route(self, route_data: Dict) -> str:
        """保存工艺路线"""
        route = ProcessRoute.from_dict(route_data)
        return self.data_manager.save_process_route(route)
    
    def route_get_route(self, uid: str) -> Optional[Dict]:
        """获取工艺路线"""
        route = self.data_manager.get_process_route(uid)
        if route:
            return route.to_dict()
        return None
    
    def route_get_all_routes(self) -> List[Dict]:
        """获取所有工艺路线"""
        routes = self.data_manager.get_all_process_routes()
        return [r.to_dict() for r in routes]
    
    # ==================== 项目模块接口 ====================
    
    def project_save_project(self, project_data: Dict) -> str:
        """保存项目"""
        project = ProcessProject.from_dict(project_data)
        return self.data_manager.save_project(project)
    
    def project_get_project(self, uid: str) -> Optional[Dict]:
        """获取项目"""
        project = self.data_manager.get_project(uid)
        if project:
            return project.to_dict()
        return None
    
    def project_get_all_projects(self) -> List[Dict]:
        """获取所有项目"""
        projects = self.data_manager.get_all_projects()
        return [p.to_dict() for p in projects]
    
    # ==================== 数据提取辅助方法 ====================
    
    def _extract_inventory_data(self, equipment: UnifiedEquipment) -> Dict:
        """提取设备清单数据"""
        return {
            'unique_code': equipment.unique_code,
            'specification': equipment.specification,
            'model': equipment.model,
            'manufacturer': equipment.manufacturer,
            'design_pressure': equipment.design_pressure,
            'design_temperature': equipment.design_temperature,
            'operating_pressure': equipment.operating_pressure,
            'operating_temperature': equipment.operating_temperature,
            'quantity': equipment.quantity,
            'running_quantity': equipment.running_quantity,
            'power': {
                'single': equipment.single_power,
                'total': equipment.total_power
            },
            'weight': {
                'estimate': equipment.weight_estimate,
                'operating': equipment.operating_weight
            },
            'price': {
                'unit': equipment.unit_price,
                'total': equipment.total_price
            },
            'material': equipment.material,
            'insulation': equipment.insulation,
            'notes': equipment.notes,
            'status': equipment.status,
            'location': equipment.location
        }
    
    def _extract_pfd_data(self, equipment: UnifiedEquipment) -> Dict:
        """提取工艺流程图数据"""
        return {
            'position': equipment.pfd_position,
            'size': equipment.pfd_size,
            'properties': equipment.pfd_properties,
            'in_diagram': bool(equipment.pfd_position['x'] != 0 or 
                              equipment.pfd_position['y'] != 0)
        }
    
    def _extract_msds_data(self, equipment: UnifiedEquipment) -> Dict:
        """提取MSDS数据"""
        return {
            'msds_uid': equipment.msds_uid,
            'hazard_class': equipment.hazard_class,
            'material_cas': equipment.material_cas,
            'has_msds': bool(equipment.msds_uid)
        }
    
    # ==================== 数据同步通知 ====================
    
    def notify_data_changed(self, uid: str, changed_by_module: str):
        """通知数据已变更（用于跨模块同步）"""
        print(f"📢 数据变更通知: UID={uid}, 修改模块={changed_by_module}")
        
        # 获取变更历史
        history = self.data_manager.get_change_history(
            object_uid=uid, 
            limit=1
        )
        
        if history:
            last_change = history[0]
            print(f"    变更内容: {last_change.get('operation')}")
            print(f"    变更时间: {last_change.get('changed_at')}")