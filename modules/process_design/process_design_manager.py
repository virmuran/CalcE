# TofuApp/modules/process_design/process_design_manager.py
import os
import sys
import sqlite3
from typing import List, Optional, Dict, Any
from PySide6.QtCore import QObject, Signal

# 1. 计算 TofuApp 根目录路径（精准匹配你的项目结构）
# 当前文件路径：process_design_manager.py → process_design/ → modules/ → TofuApp/
current_file = os.path.abspath(__file__)
# 向上追溯3级目录，找到 TofuApp 根目录（关键：适配你的文件夹层级）
tofu_app_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

# 2. 把根目录加入 Python 搜索路径
if tofu_app_root not in sys.path:
    sys.path.insert(0, tofu_app_root)

# 3. 现在可以正常导入 DataManager 了（无需写 TofuApp 前缀，直接导入 data_manager）
try:
    from data_manager import DataManager
    print("✅ 成功从根目录导入 DataManager")
except Exception as e:
    print(f"❌ 导入 DataManager 失败: {e}")
    DataManager

class ProcessDesignManager(QObject):
    """工艺设计管理器"""
    
    # 数据变更信号
    equipment_changed = Signal(str)  # equipment_id
    material_changed = Signal(str)   # material_id
    msds_changed = Signal(str)       # msds_id
    project_changed = Signal(str)    # project_id
    
    def __init__(self, parent=None):
        self.parent = parent
        self.db_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.db_dir, exist_ok=True)
        self.db_path = os.path.join(self.db_dir, "tofu_process_design.db")
        self.main_data_manager = DataManager()
        self.data_manager = self.main_data_manager
        self.init_database()
    
    def init_database(self):
        """初始化数据库（创建必要的表结构，如物料表、MSDS表）"""
        try:
            # 导入sqlite3（如果没导入，先添加导入）
            import sqlite3
            # 连接数据库（不存在则自动创建）
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 1. 创建物料表（和你的 MaterialProperty 对应）
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS materials (
                material_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                cas_number TEXT,
                molecular_formula TEXT,
                molecular_weight REAL,
                phase TEXT,
                density REAL,
                boiling_point REAL,
                melting_point REAL,
                flash_point REAL,
                hazard_class TEXT,
                notes TEXT
            )
            ''')
            
            # 2. 可选：创建MSDS表（如果需要，保留和你项目一致的结构）
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS msds_documents (
                msds_id TEXT PRIMARY KEY,
                material_id TEXT,
                document_name TEXT,
                file_path TEXT,
                upload_date TEXT,
                FOREIGN KEY (material_id) REFERENCES materials (material_id)
            )
            ''')
            
            # 提交更改并关闭连接
            conn.commit()
            conn.close()
            print(f"✅ 数据库初始化完成: {self.db_path}")
        
        except Exception as e:
            print(f"❌ 数据库初始化失败: {str(e)}")
            raise  # 抛出异常，方便排查问题
    
    def get_english_name(self, chinese_name):
        """根据中文名称获取英文名称（从全局数据管家读取）"""
        name_mapping = self.main_data_manager.get_equipment_name_mapping()
        return name_mapping.get(chinese_name, "")
    
    def save_flow_diagram(self, flow_diagram_data):
        """保存流程图数据到全局数据管家（兼容原有调用逻辑）"""
        try:
            # 调用全局数据管理器保存工艺参数（流程图数据）
            self.main_data_manager.update_process_params("flow_diagram", flow_diagram_data)
            print("✅ 流程图数据已成功保存到全局数据管家")
            return True
        except Exception as e:
            print(f"❌ 保存流程图数据失败: {str(e)}")
            return False
    
    def get_equipment_data(self):
        """获取设备数据（兼容方法）"""
        return self.get_all_equipment()
    
    def _init_demo_data(self):
        """初始化演示数据"""
        try:
            # 检查是否需要加载演示物料
            materials = self.get_all_materials()
            if not materials:
                self._load_demo_materials()
            
            # 检查是否需要加载演示设备
            equipment = self.get_all_equipment()
            if not equipment:
                self._load_demo_equipment()
                
        except Exception as e:
            print(f"❌ 初始化演示数据时出错: {e}")
    
    def _load_demo_materials(self):
        """加载演示物料数据"""
        try:
            demo_materials = [
                {
                    "material_id": "M-001",
                    "name": "甲醇",
                    "cas_number": "67-56-1",
                    "molecular_formula": "CH3OH",
                    "molecular_weight": 32.04,
                    "density": 0.791,
                    "boiling_point": 64.7,
                    "melting_point": -97.6,
                    "flash_point": 11,
                    "phase": "liquid",
                    "hazard_class": "易燃液体"
                },
                {
                    "material_id": "M-002",
                    "name": "水",
                    "cas_number": "7732-18-5",
                    "molecular_formula": "H2O",
                    "molecular_weight": 18.02,
                    "density": 1.0,
                    "boiling_point": 100.0,
                    "melting_point": 0.0,
                    "phase": "liquid",
                    "hazard_class": "无"
                },
                {
                    "material_id": "M-003",
                    "name": "二氧化碳",
                    "cas_number": "124-38-9",
                    "molecular_formula": "CO2",
                    "molecular_weight": 44.01,
                    "density": 1.98,
                    "boiling_point": -78.5,
                    "phase": "gas",
                    "hazard_class": "窒息性气体"
                }
            ]
            
            for material_data in demo_materials:
                self.main_data_manager.add_material(material_data)
            
            print(f"✅ 演示物料数据加载完成: {len(demo_materials)} 个物料")
            
        except Exception as e:
            print(f"❌ 加载演示物料数据失败: {e}")
    
    def _load_demo_equipment(self):
        """加载演示设备数据"""
        try:
            demo_equipment = [
                {
                    "equipment_id": "EQ-001",
                    "name": "反应器R-101",
                    "type": "reactor",
                    "unique_code": "R-101",
                    "model": "STR-1000",
                    "manufacturer": "ABC公司",
                    "design_pressure": 5.0,
                    "design_temperature": 250.0,
                    "capacity": "1000L",
                    "description": "甲醇合成反应器",
                    "status": "运行中"
                },
                {
                    "equipment_id": "EQ-002",
                    "name": "精馏塔C-101",
                    "type": "column",
                    "unique_code": "C-101",
                    "model": "DT-500",
                    "manufacturer": "XYZ公司",
                    "design_pressure": 0.5,
                    "design_temperature": 150.0,
                    "capacity": "500mm",
                    "description": "甲醇精馏塔",
                    "status": "运行中"
                },
            ]
            
            for equipment_data in demo_equipment:
                self.main_data_manager.add_equipment(equipment_data)
            
            print(f"✅ 演示设备数据加载完成: {len(demo_equipment)} 个设备")
            
        except Exception as e:
            print(f"❌ 加载演示设备数据失败: {e}")
    
    # ==================== 设备管理方法 ====================
    
    def get_all_equipment(self) -> List[Dict]:
        """获取所有设备"""
        return self.main_data_manager.get_equipment_data()
    
    def get_equipment_by_id(self, equipment_id: str) -> Optional[Dict]:
        """根据ID获取设备"""
        return self.main_data_manager.get_equipment_by_id(equipment_id)
    
    def get_equipment_by_code(self, equipment_code: str) -> Optional[Dict]:
        """根据编码获取设备"""
        return self.main_data_manager.get_equipment_by_unique_code(equipment_code)
    
    def save_equipment(self, equipment_data: Dict) -> bool:
        """保存设备"""
        success = self.main_data_manager.add_equipment(equipment_data)
        if success:
            self.equipment_changed.emit(equipment_data.get('equipment_id', ''))
        return success
    
    def update_equipment(self, equipment_id: str, update_data: Dict) -> bool:
        """更新设备"""
        success = self.main_data_manager.update_equipment(equipment_id, update_data)
        if success:
            self.equipment_changed.emit(equipment_id)
        return success
    
    def delete_equipment(self, equipment_id: str) -> bool:
        """删除设备"""
        success = self.main_data_manager.delete_equipment(equipment_id)
        if success:
            self.equipment_changed.emit(equipment_id)
        return success
    
    # ==================== 物料管理方法 ====================
    
    def get_all_materials(self) -> List[Dict]:
        """获取所有物料"""
        return self.main_data_manager.get_materials()
    
    def get_material_by_id(self, material_id: str) -> Optional[Dict]:
        """根据ID获取物料"""
        materials = self.get_all_materials()
        for material in materials:
            if material.get('material_id') == material_id:
                return material
        return None
    
    def save_material(self, material_data: Dict) -> bool:
        """保存物料"""
        success = self.main_data_manager.add_material(material_data)
        if success:
            self.material_changed.emit(material_data.get('material_id', ''))
        return success
    
    # ==================== MSDS管理方法 ====================
    
    def get_all_msds(self) -> List[Dict]:
        """获取所有MSDS"""
        return self.main_data_manager.get_msds_documents()
    
    def save_msds(self, msds_data: Dict) -> bool:
        """保存MSDS"""
        success = self.main_data_manager.add_msds_document(msds_data)
        if success:
            self.msds_changed.emit(msds_data.get('msds_id', ''))
        return success
    
    # ==================== 项目管理方法 ====================
    
    def get_all_projects(self) -> List[Dict]:
        """获取所有项目"""
        return self.main_data_manager.get_projects()
    
    def save_project(self, project_data: Dict) -> bool:
        """保存项目"""
        success = self.main_data_manager.add_project(project_data)
        if success:
            self.project_changed.emit(project_data.get('project_id', ''))
        return success
    
    # ==================== 数据统计 ====================
    
    def get_data_stats(self) -> Dict[str, int]:
        """获取数据统计"""
        return {
            'materials': len(self.get_all_materials()),
            'equipment': len(self.get_all_equipment()),
            'msds': len(self.get_all_msds()),
            'projects': len(self.get_all_projects())
        }
    
    def get_main_data_manager(self):
        """获取主 DataManager 实例"""
        return self.main_data_manager


# 全局管理器实例
global_process_design_manager = ProcessDesignManager()