# TofuApp/modules/process_design/process_design_manager.py
import sys
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
import traceback

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 导入新的数据层
from .data import (
    global_data_manager, 
    MaterialProperty, ProcessRoute, 
    MSDSDocument, ProcessProject,
    UnifiedEquipment, ModuleInterface
)

# 如果需要，可以导入流程图相关的类
try:
    from .tabs import ProcessFlowDiagram, EquipmentNode, MaterialConnection
except ImportError:
    ProcessFlowDiagram = None
    EquipmentNode = None
    MaterialConnection = None

class ProcessDesignManager:
    """工艺设计数据管理器 - 重构版，使用统一数据架构"""
    
    def __init__(self, data_manager=None):
        # 使用统一数据管理器
        self.data_manager = global_data_manager
        
        # 模块接口
        self.interface = ModuleInterface(self.data_manager)
        
        # 初始化演示数据
        self._init_demo_data()
    
    def _init_demo_data(self):
        """初始化演示数据"""
        try:
            # 检查是否需要加载演示物料
            materials = self.data_manager.get_all_materials()
            if not materials:
                self._load_demo_materials()
            
            # 检查是否需要加载演示工艺路线
            routes = self.data_manager.get_all_process_routes()
            if not routes:
                self._load_demo_routes()
                
        except Exception as e:
            print(f"❌ 初始化演示数据时出错: {e}")
    
    def _load_demo_materials(self):
        """加载演示物料数据"""
        try:
            demo_materials = [
                MaterialProperty(
                    material_id="M-001",
                    name="甲醇",
                    cas_number="67-56-1",
                    molecular_formula="CH3OH",
                    molecular_weight=32.04,
                    density=0.791,
                    boiling_point=64.7,
                    melting_point=-97.6,
                    flash_point=11,
                    phase="liquid",
                    hazard_class="易燃液体"
                ),
                MaterialProperty(
                    material_id="M-002",
                    name="水",
                    cas_number="7732-18-5",
                    molecular_formula="H2O",
                    molecular_weight=18.02,
                    density=1.0,
                    boiling_point=100.0,
                    melting_point=0.0,
                    phase="liquid",
                    hazard_class="无"
                ),
                MaterialProperty(
                    material_id="M-003",
                    name="二氧化碳",
                    cas_number="124-38-9",
                    molecular_formula="CO2",
                    molecular_weight=44.01,
                    density=1.98,
                    boiling_point=-78.5,
                    phase="gas",
                    hazard_class="窒息性气体"
                ),
                MaterialProperty(
                    material_id="M-004",
                    name="氢氧化钠",
                    cas_number="1310-73-2",
                    molecular_formula="NaOH",
                    molecular_weight=40.0,
                    density=2.13,
                    melting_point=318,
                    boiling_point=1388,
                    phase="solid",
                    hazard_class="腐蚀性"
                ),
                MaterialProperty(
                    material_id="M-005",
                    name="苯",
                    cas_number="71-43-2",
                    molecular_formula="C6H6",
                    molecular_weight=78.11,
                    density=0.879,
                    boiling_point=80.1,
                    melting_point=5.5,
                    flash_point=-11,
                    phase="liquid",
                    hazard_class="易燃液体，致癌物"
                ),
                MaterialProperty(
                    material_id="M-006",
                    name="氧气",
                    cas_number="7782-44-7",
                    molecular_formula="O2",
                    molecular_weight=32.0,
                    density=1.43,
                    boiling_point=-183,
                    melting_point=-218,
                    phase="gas",
                    hazard_class="氧化剂"
                ),
                MaterialProperty(
                    material_id="M-007",
                    name="盐酸",
                    cas_number="7647-01-0",
                    molecular_formula="HCl",
                    molecular_weight=36.46,
                    density=1.2,
                    boiling_point=-85,
                    melting_point=-114,
                    phase="liquid",
                    hazard_class="腐蚀性"
                ),
                MaterialProperty(
                    material_id="M-008",
                    name="硫酸",
                    cas_number="7664-93-9",
                    molecular_formula="H2SO4",
                    molecular_weight=98.08,
                    density=1.84,
                    boiling_point=337,
                    melting_point=10,
                    phase="liquid",
                    hazard_class="腐蚀性，氧化剂"
                ),
                MaterialProperty(
                    material_id="M-009",
                    name="乙醇",
                    cas_number="64-17-5",
                    molecular_formula="C2H5OH",
                    molecular_weight=46.07,
                    density=0.789,
                    boiling_point=78.37,
                    melting_point=-114,
                    flash_point=13,
                    phase="liquid",
                    hazard_class="易燃液体"
                ),
                MaterialProperty(
                    material_id="M-010",
                    name="氨",
                    cas_number="7664-41-7",
                    molecular_formula="NH3",
                    molecular_weight=17.03,
                    density=0.73,
                    boiling_point=-33.34,
                    melting_point=-77.73,
                    phase="gas",
                    hazard_class="有毒，腐蚀性"
                ),
            ]
            
            for material in demo_materials:
                self.data_manager.save_material(material)
            
            print(f"✅ 演示物料数据加载完成: {len(demo_materials)} 个物料")
            
        except Exception as e:
            print(f"❌ 加载演示物料数据失败: {e}")
    
    def _load_demo_routes(self):
        """加载演示工艺路线数据"""
        try:
            demo_routes = [
                ProcessRoute(
                    route_id="PR-001",
                    name="甲醇合成工艺",
                    product="甲醇",
                    description="从合成气生产甲醇的工艺路线",
                    steps=[
                        {
                            "step_number": 1,
                            "operation": "合成气净化",
                            "equipment": "净化塔C-101",
                            "materials": [{"name": "合成气", "amount": "1000", "unit": "Nm³/h"}],
                            "parameters": {"温度": "40", "压力": "2.5", "单位": "MPa"},
                            "description": "去除合成气中的硫化物和二氧化碳"
                        },
                        {
                            "step_number": 2,
                            "operation": "甲醇合成反应",
                            "equipment": "反应器R-101",
                            "materials": [{"name": "合成气", "amount": "950", "unit": "Nm³/h"}],
                            "parameters": {"温度": "250", "压力": "5.0", "单位": "MPa"},
                            "description": "在铜基催化剂作用下合成甲醇"
                        },
                        {
                            "step_number": 3,
                            "operation": "甲醇精馏",
                            "equipment": "精馏塔C-102",
                            "materials": [{"name": "粗甲醇", "amount": "500", "unit": "kg/h"}],
                            "parameters": {"温度": "65", "压力": "0.1", "单位": "MPa"},
                            "description": "分离甲醇和水，得到精甲醇产品"
                        }
                    ],
                    status="active",
                    notes="这是一个演示工艺路线"
                ),
                ProcessRoute(
                    route_id="PR-002",
                    name="苯乙烯生产工艺",
                    product="苯乙烯",
                    description="通过乙苯脱氢生产苯乙烯的工艺路线",
                    steps=[
                        {
                            "step_number": 1,
                            "operation": "乙苯蒸发",
                            "equipment": "蒸发器E-201",
                            "materials": [{"name": "乙苯", "amount": "1000", "unit": "kg/h"}],
                            "parameters": {"温度": "150", "压力": "0.2", "单位": "MPa"},
                            "description": "将液态乙苯蒸发为气态"
                        },
                        {
                            "step_number": 2,
                            "operation": "脱氢反应",
                            "equipment": "反应器R-201",
                            "materials": [
                                {"name": "乙苯", "amount": "950", "unit": "kg/h"},
                                {"name": "水蒸气", "amount": "2000", "unit": "kg/h"}
                            ],
                            "parameters": {"温度": "600", "压力": "0.1", "单位": "MPa"},
                            "description": "在铁基催化剂作用下进行脱氢反应"
                        },
                        {
                            "step_number": 3,
                            "operation": "苯乙烯分离",
                            "equipment": "分离塔C-201",
                            "materials": [{"name": "反应产物", "amount": "850", "unit": "kg/h"}],
                            "parameters": {"温度": "80", "压力": "0.05", "单位": "MPa"},
                            "description": "分离苯乙烯、乙苯和副产物"
                        }
                    ],
                    status="active",
                    notes=""
                ),
                ProcessRoute(
                    route_id="PR-003",
                    name="硫酸生产（接触法）",
                    product="硫酸",
                    description="通过接触法生产硫酸的工艺路线",
                    steps=[
                        {
                            "step_number": 1,
                            "operation": "硫磺焚烧",
                            "equipment": "焚硫炉F-301",
                            "materials": [{"name": "硫磺", "amount": "500", "unit": "kg/h"}],
                            "parameters": {"温度": "1200", "压力": "常压", "单位": "°C"},
                            "description": "硫磺与空气燃烧生成二氧化硫"
                        },
                        {
                            "step_number": 2,
                            "operation": "二氧化硫转化",
                            "equipment": "转化器R-301",
                            "materials": [{"name": "二氧化硫", "amount": "1000", "unit": "Nm³/h"}],
                            "parameters": {"温度": "450", "压力": "0.1", "单位": "MPa"},
                            "description": "在钒催化剂作用下转化为三氧化硫"
                        },
                        {
                            "step_number": 3,
                            "operation": "三氧化硫吸收",
                            "equipment": "吸收塔C-301",
                            "materials": [
                                {"name": "三氧化硫", "amount": "800", "unit": "Nm³/h"},
                                {"name": "98%硫酸", "amount": "2000", "unit": "kg/h"}
                            ],
                            "parameters": {"温度": "60", "压力": "0.1", "单位": "MPa"},
                            "description": "用浓硫酸吸收三氧化硫生成发烟硫酸"
                        },
                        {
                            "step_number": 4,
                            "operation": "硫酸稀释",
                            "equipment": "稀释器M-301",
                            "materials": [
                                {"name": "发烟硫酸", "amount": "1500", "unit": "kg/h"},
                                {"name": "水", "amount": "200", "unit": "kg/h"}
                            ],
                            "parameters": {"温度": "40", "压力": "常压", "单位": "°C"},
                            "description": "将发烟硫酸稀释为98%硫酸产品"
                        }
                    ],
                    status="draft",
                    notes="草稿状态，需要进一步完善"
                )
            ]
            
            for route in demo_routes:
                self.data_manager.save_process_route(route)
            
            print(f"✅ 演示工艺路线加载完成: {len(demo_routes)} 条路线")
            
        except Exception as e:
            print(f"❌ 加载演示工艺路线失败: {e}")
            traceback.print_exc()
    
    # ==================== 工艺路线相关方法 ====================
    
    def get_all_process_routes(self) -> List[ProcessRoute]:
        """获取所有工艺路线"""
        return self.data_manager.get_all_process_routes()
    
    def get_process_route(self, route_id: str) -> Optional[ProcessRoute]:
        """获取工艺路线"""
        return self.data_manager.get_process_route_by_id(route_id)
    
    def add_process_route(self, route: ProcessRoute) -> bool:
        """添加工艺路线"""
        uid = self.data_manager.save_process_route(route)
        return bool(uid)
    
    def update_process_route(self, route: ProcessRoute) -> bool:
        """更新工艺路线"""
        uid = self.data_manager.save_process_route(route)
        return bool(uid)
    
    def delete_process_route(self, route_id: str) -> bool:
        """删除工艺路线"""
        route = self.data_manager.get_process_route_by_id(route_id)
        if route:
            return self.data_manager.delete_process_route(route.uid)
        return False
    
    def search_process_routes(self, search_term: str) -> List[ProcessRoute]:
        """搜索工艺路线"""
        routes = self.data_manager.get_all_process_routes()
        search_term = search_term.lower()
        results = []
        
        for route in routes:
            if (search_term in route.name.lower() or
                search_term in route.route_id.lower() or
                search_term in route.product.lower() or
                search_term in route.description.lower()):
                results.append(route)
        
        return results
    
    # ==================== MSDS 相关方法 ====================
    
    def get_all_msds(self) -> List[MSDSDocument]:
        """获取所有MSDS文档"""
        return self.data_manager.get_all_msds()
    
    def get_msds(self, msds_id: str) -> Optional[MSDSDocument]:
        """获取MSDS文档"""
        msds_list = self.data_manager.get_all_msds()
        for msds in msds_list:
            if msds.msds_id == msds_id:
                return msds
        return None
    
    def add_msds(self, msds: MSDSDocument) -> bool:
        """添加MSDS文档"""
        uid = self.data_manager.save_msds(msds)
        return bool(uid)
    
    def update_msds(self, msds: MSDSDocument) -> bool:
        """更新MSDS文档"""
        uid = self.data_manager.save_msds(msds)
        return bool(uid)
    
    def delete_msds(self, msds_id: str) -> bool:
        """删除MSDS文档"""
        msds_list = self.data_manager.get_all_msds()
        for msds in msds_list:
            if msds.msds_id == msds_id:
                return self.data_manager.delete_msds(msds.uid)
        return False
    
    def search_msds(self, search_term: str) -> List[MSDSDocument]:
        """搜索MSDS文档"""
        msds_list = self.data_manager.get_all_msds()
        search_term = search_term.lower()
        results = []
        
        for msds in msds_list:
            if (search_term in msds.material_name.lower() or
                search_term in msds.cas_number.lower() or
                search_term in msds.supplier.lower() or
                search_term in msds.msds_id.lower()):
                results.append(msds)
        
        return results
    
    def advanced_search_msds(self, criteria: Dict[str, Any]) -> List[MSDSDocument]:
        """高级搜索MSDS文档"""
        msds_list = self.data_manager.get_all_msds()
        results = []
        
        for msds in msds_list:
            match = True
            
            # 供应商过滤
            if 'supplier' in criteria and criteria['supplier']:
                if criteria['supplier'].lower() not in msds.supplier.lower():
                    match = False
            
            # 版本过滤
            if 'version' in criteria and criteria['version']:
                if criteria['version'].lower() not in msds.version.lower():
                    match = False
            
            # 生效日期范围过滤
            if 'start_date' in criteria and criteria['start_date'] and msds.effective_date:
                try:
                    start_date = datetime.strptime(criteria['start_date'], '%Y-%m-%d')
                    msds_date = datetime.strptime(msds.effective_date, '%Y-%m-%d')
                    if msds_date < start_date:
                        match = False
                except ValueError:
                    pass
            
            if 'end_date' in criteria and criteria['end_date'] and msds.effective_date:
                try:
                    end_date = datetime.strptime(criteria['end_date'], '%Y-%m-%d')
                    msds_date = datetime.strptime(msds.effective_date, '%Y-%m-%d')
                    if msds_date > end_date:
                        match = False
                except ValueError:
                    pass
            
            # 危险类别过滤
            if 'hazard_classes' in criteria and criteria['hazard_classes'] and msds.hazard_class:
                hazard_match = False
                for hazard in criteria['hazard_classes']:
                    if hazard in msds.hazard_class:
                        hazard_match = True
                        break
                if not hazard_match:
                    match = False
            
            # 状态过滤
            if 'status' in criteria and criteria['status']:
                if msds.status != criteria['status']:
                    match = False
            
            if match:
                results.append(msds)
        
        return results
    
    def get_material_by_cas(self, cas_number: str) -> Optional[MaterialProperty]:
        """根据CAS号获取物料"""
        materials = self.data_manager.get_all_materials()
        for material in materials:
            if material.cas_number == cas_number:
                return material
        return None
    
    # ==================== 物料相关方法 ====================
    
    def add_material(self, material: MaterialProperty) -> bool:
        """添加物料"""
        uid = self.data_manager.save_material(material)
        return bool(uid)
    
    def get_material(self, material_id: str) -> Optional[MaterialProperty]:
        """获取物料"""
        return self.data_manager.get_material_by_id(material_id)
    
    def get_all_materials(self) -> List[MaterialProperty]:
        """获取所有物料"""
        return self.data_manager.get_all_materials()
    
    def update_material(self, material: MaterialProperty) -> bool:
        """更新物料"""
        uid = self.data_manager.save_material(material)
        return bool(uid)
    
    def delete_material(self, material_id: str) -> bool:
        """删除物料"""
        material = self.data_manager.get_material_by_id(material_id)
        if material:
            return self.data_manager.delete_material(material.uid)
        return False
    
    def search_materials(self, search_term: str) -> List[MaterialProperty]:
        """搜索物料"""
        return self.data_manager.search_materials(search_term)
    
    def advanced_search_materials(self, criteria: Dict[str, Any]) -> List[MaterialProperty]:
        """高级搜索物料"""
        materials = self.data_manager.get_all_materials()
        results = []
        
        for material in materials:
            match = True
            
            # 分子量范围过滤
            if 'min_molecular_weight' in criteria and criteria['min_molecular_weight'] is not None:
                if material.molecular_weight < criteria['min_molecular_weight']:
                    match = False
            
            if 'max_molecular_weight' in criteria and criteria['max_molecular_weight'] is not None:
                if material.molecular_weight > criteria['max_molecular_weight']:
                    match = False
            
            # 密度范围过滤
            if 'min_density' in criteria and criteria['min_density'] is not None and material.density:
                if material.density < criteria['min_density']:
                    match = False
            
            if 'max_density' in criteria and criteria['max_density'] is not None and material.density:
                if material.density > criteria['max_density']:
                    match = False
            
            # 沸点范围过滤
            if 'min_boiling_point' in criteria and criteria['min_boiling_point'] is not None and material.boiling_point:
                if material.boiling_point < criteria['min_boiling_point']:
                    match = False
            
            if 'max_boiling_point' in criteria and criteria['max_boiling_point'] is not None and material.boiling_point:
                if material.boiling_point > criteria['max_boiling_point']:
                    match = False
            
            # 危险类别过滤
            if 'hazard_classes' in criteria and criteria['hazard_classes'] and material.hazard_class:
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
        return len(self.data_manager.get_all_materials())
    
    # ==================== 设备相关方法 ====================
    
    def add_equipment(self, equipment: UnifiedEquipment) -> bool:
        """添加设备"""
        uid = self.data_manager.save_equipment(equipment)
        return bool(uid)
    
    def get_equipment(self, equipment_id: str) -> Optional[UnifiedEquipment]:
        """获取设备"""
        return self.data_manager.get_equipment_by_code(equipment_id)
    
    def get_all_equipment(self) -> List[UnifiedEquipment]:
        """获取所有设备"""
        return self.data_manager.get_all_equipment()
    
    def get_equipment_by_project(self, project_id: str) -> List[UnifiedEquipment]:
        """根据项目ID获取设备清单"""
        # 简化处理，返回所有设备
        return self.get_all_equipment()
    
    def update_equipment(self, equipment: UnifiedEquipment) -> bool:
        """更新设备"""
        uid = self.data_manager.save_equipment(equipment)
        return bool(uid)
    
    def delete_equipment(self, equipment_id: str) -> bool:
        """删除设备"""
        equipment = self.data_manager.get_equipment_by_code(equipment_id)
        if equipment:
            return self.data_manager.delete_equipment(equipment.uid)
        return False
    
    def import_materials(self, materials_data: List[Dict], mode: str = 'append') -> Dict[str, int]:
        """批量导入物料"""
        stats = {'success': 0, 'failed': 0, 'skipped': 0}
        
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
    
    # ==================== 项目相关方法 ====================
    
    def create_project(self, project: ProcessProject) -> bool:
        """创建新项目"""
        uid = self.data_manager.save_project(project)
        return bool(uid)
    
    def get_project(self, project_id: str) -> Optional[ProcessProject]:
        """获取项目"""
        return self.data_manager.get_project_by_id(project_id)
    
    def get_all_projects(self) -> List[ProcessProject]:
        """获取所有项目"""
        return self.data_manager.get_all_projects()
    
    def update_project(self, project: ProcessProject) -> bool:
        """更新项目"""
        uid = self.data_manager.save_project(project)
        return bool(uid)
    
    def delete_project(self, project_id: str) -> bool:
        """删除项目"""
        project = self.data_manager.get_project_by_id(project_id)
        if project:
            return self.data_manager.delete_project(project.uid)
        return False
    
    # ==================== 流程图相关方法 ====================
    
    def save_flow_diagram(self, diagram_data: Dict[str, Any]) -> bool:
        """保存工艺流程图数据"""
        try:
            # 使用模块接口保存
            diagram_id = self.interface.pfd_save_diagram(diagram_data)
            return bool(diagram_id)
        except Exception as e:
            print(f"❌ 保存流程图数据失败: {e}")
            return False
    
    def load_flow_diagram(self) -> Optional[Dict[str, Any]]:
        """加载工艺流程图数据"""
        try:
            # 这里简化实现，实际应该从数据库加载
            return None
        except Exception as e:
            print(f"❌ 加载流程图数据失败: {e}")
            return None
    
    def clear_flow_diagram(self) -> bool:
        """清空工艺流程图数据"""
        # 这里简化实现
        return True
    
    # ==================== 数据统计方法 ====================
    
    def get_data_stats(self) -> Dict[str, int]:
        """获取数据统计"""
        return {
            'materials': len(self.get_all_materials()),
            'equipment': len(self.get_all_equipment()),
            'routes': len(self.get_all_process_routes()),
            'msds': len(self.get_all_msds()),
            'projects': len(self.get_all_projects())
        }
    
    def get_completeness_stats(self) -> Dict[str, float]:
        """获取数据完整性统计"""
        return self.data_manager.get_data_completeness()
    
    def get_module_interface(self) -> ModuleInterface:
        """获取模块接口"""
        return self.interface

# 全局管理器实例
global_process_design_manager = ProcessDesignManager()