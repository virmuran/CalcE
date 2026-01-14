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

# 3. 导入 DataManager（仅保留导入兼容，实际数据读写使用 SQLite）
try:
    from data_manager import DataManager
    print("✅ 成功从根目录导入 DataManager（仅兼容保留）")
except Exception as e:
    print(f"❌ 导入 DataManager 失败: {e}")
    DataManager = None  # 兼容处理


class ProcessDesignManager(QObject):
    """工艺设计管理器（兼容SQLite存储）"""
    
    # 数据变更信号
    equipment_changed = Signal(str)  # equipment_id
    material_changed = Signal(str)   # material_id
    msds_changed = Signal(str)       # msds_id
    project_changed = Signal(str)    # project_id
    
    def __init__(self, parent=None):
        super().__init__(parent)  # 调用QObject父类初始化（关键）
        self.parent = parent
        self.db_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.db_dir, exist_ok=True)
        self.db_path = os.path.join(self.db_dir, "tofu_process_design.db")
        # 保留DataManager实例（仅兼容，不依赖其数据读写）
        self.main_data_manager = DataManager() if DataManager else None
        self.data_manager = self.main_data_manager
        # 初始化数据库（包含所有表结构）
        self.init_database()
        # 初始化演示数据
        self._init_demo_data()
    
    def init_database(self):
        """初始化数据库（创建所有必要表结构）"""
        try:
            # 连接数据库（不存在则自动创建）
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 1. 创建物料表
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
            
            # 2. 创建MSDS表
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
            
            # 3. 创建设备表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS equipment (
                equipment_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT,
                unique_code TEXT UNIQUE,
                model TEXT,
                manufacturer TEXT,
                design_pressure REAL,
                design_temperature REAL,
                capacity TEXT,
                description TEXT,
                status TEXT
            )
            ''')
            
            # 4. 创建项目表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                code TEXT UNIQUE,
                description TEXT,
                start_date TEXT,
                end_date TEXT,
                status TEXT
            )
            ''')
            
            # 提交更改并关闭连接
            conn.commit()
            conn.close()
            print(f"✅ 数据库初始化完成: {self.db_path}")
        
        except Exception as e:
            print(f"❌ 数据库初始化失败: {str(e)}")
            raise  # 抛出异常，方便排查问题
    
    def _get_db_connection(self):
        """获取数据库连接（通用方法，避免重复代码）"""
        conn = sqlite3.connect(self.db_path)
        # 设置行工厂，使查询结果以字典形式返回
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_english_name(self, chinese_name):
        """根据中文名称获取英文名称（兼容保留方法）"""
        if self.main_data_manager:
            name_mapping = self.main_data_manager.get_equipment_name_mapping()
            return name_mapping.get(chinese_name, "")
        return ""
    
    def save_flow_diagram(self, flow_diagram_data):
        """保存流程图数据（兼容保留方法）"""
        try:
            # 流程图数据存入SQLite（新增逻辑）
            conn = self._get_db_connection()
            cursor = conn.cursor()
            # 创建流程图表（按需）
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS flow_diagrams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            # 清空原有数据，只保留最新版本
            cursor.execute("DELETE FROM flow_diagrams")
            # 插入新数据
            cursor.execute("INSERT INTO flow_diagrams (data) VALUES (?)", (str(flow_diagram_data),))
            conn.commit()
            conn.close()
            print("✅ 流程图数据已成功保存到SQLite")
            return True
        except Exception as e:
            print(f"❌ 保存流程图数据失败: {str(e)}")
            return False
    
    # ==================== 设备管理方法（SQLite实现） ====================
    
    def get_equipment_data(self):
        """获取设备数据（兼容方法）"""
        return self.get_all_equipment()
    
    def get_all_equipment(self) -> List[Dict]:
        """获取所有设备"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM equipment")
            rows = cursor.fetchall()
            conn.close()
            # 转换为字典列表
            equipment_list = [dict(row) for row in rows]
            return equipment_list
        except Exception as e:
            print(f"❌ 获取所有设备失败: {str(e)}")
            return []
    
    def get_equipment_by_id(self, equipment_id: str) -> Optional[Dict]:
        """根据ID获取设备"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM equipment WHERE equipment_id = ?", (equipment_id,))
            row = cursor.fetchone()
            conn.close()
            return dict(row) if row else None
        except Exception as e:
            print(f"❌ 根据ID获取设备失败: {str(e)}")
            return None
    
    def get_equipment_by_code(self, equipment_code: str) -> Optional[Dict]:
        """根据编码获取设备"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM equipment WHERE unique_code = ?", (equipment_code,))
            row = cursor.fetchone()
            conn.close()
            return dict(row) if row else None
        except Exception as e:
            print(f"❌ 根据编码获取设备失败: {str(e)}")
            return None
    
    def save_equipment(self, equipment_data: Dict) -> bool:
        """保存设备（新增/更新）"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            # 提取字段（兼容原有数据结构）
            equipment_id = equipment_data.get('equipment_id')
            if not equipment_id:
                raise ValueError("设备ID不能为空")
            
            # 插入/更新设备数据
            cursor.execute('''
            INSERT OR REPLACE INTO equipment (
                equipment_id, name, type, unique_code, model, manufacturer,
                design_pressure, design_temperature, capacity, description, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                equipment_id,
                equipment_data.get('name', ''),
                equipment_data.get('type', ''),
                equipment_data.get('unique_code', ''),
                equipment_data.get('model', ''),
                equipment_data.get('manufacturer', ''),
                equipment_data.get('design_pressure', None),
                equipment_data.get('design_temperature', None),
                equipment_data.get('capacity', ''),
                equipment_data.get('description', ''),
                equipment_data.get('status', '')
            ))
            conn.commit()
            conn.close()
            # 发射信号
            self.equipment_changed.emit(equipment_id)
            print(f"✅ 设备[{equipment_id}]已保存到SQLite")
            return True
        except Exception as e:
            print(f"❌ 保存设备失败: {str(e)}")
            return False
    
    def update_equipment(self, equipment_id: str, update_data: Dict) -> bool:
        """更新设备"""
        # 先获取原有数据
        equipment = self.get_equipment_by_id(equipment_id)
        if not equipment:
            print(f"❌ 设备[{equipment_id}]不存在")
            return False
        # 合并更新数据
        equipment.update(update_data)
        # 调用保存方法
        return self.save_equipment(equipment)
    
    def delete_equipment(self, equipment_id: str) -> bool:
        """删除设备"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM equipment WHERE equipment_id = ?", (equipment_id,))
            conn.commit()
            conn.close()
            # 发射信号
            self.equipment_changed.emit(equipment_id)
            print(f"✅ 设备[{equipment_id}]已从SQLite删除")
            return True
        except Exception as e:
            print(f"❌ 删除设备失败: {str(e)}")
            return False
    
    # ==================== 物料管理方法（SQLite实现） ====================
    
    def get_all_materials(self) -> List[Dict]:
        """获取所有物料"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM materials")
            rows = cursor.fetchall()
            conn.close()
            # 转换为字典列表
            material_list = [dict(row) for row in rows]
            return material_list
        except Exception as e:
            print(f"❌ 获取所有物料失败: {str(e)}")
            return []
    
    def get_material_by_id(self, material_id: str) -> Optional[Dict]:
        """根据ID获取物料"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM materials WHERE material_id = ?", (material_id,))
            row = cursor.fetchone()
            conn.close()
            return dict(row) if row else None
        except Exception as e:
            print(f"❌ 根据ID获取物料失败: {str(e)}")
            return None
    
    def save_material(self, material_data: Dict) -> bool:
        """保存物料（新增/更新）"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            # 提取字段
            material_id = material_data.get('material_id')
            if not material_id:
                raise ValueError("物料ID不能为空")
            
            # 插入/更新物料数据
            cursor.execute('''
            INSERT OR REPLACE INTO materials (
                material_id, name, cas_number, molecular_formula, molecular_weight,
                phase, density, boiling_point, melting_point, flash_point,
                hazard_class, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                material_id,
                material_data.get('name', ''),
                material_data.get('cas_number', ''),
                material_data.get('molecular_formula', ''),
                material_data.get('molecular_weight', None),
                material_data.get('phase', ''),
                material_data.get('density', None),
                material_data.get('boiling_point', None),
                material_data.get('melting_point', None),
                material_data.get('flash_point', None),
                material_data.get('hazard_class', ''),
                material_data.get('notes', '')
            ))
            conn.commit()
            conn.close()
            # 发射信号
            self.material_changed.emit(material_id)
            print(f"✅ 物料[{material_id}]已保存到SQLite")
            return True
        except Exception as e:
            print(f"❌ 保存物料失败: {str(e)}")
            return False
    
    # ==================== MSDS管理方法（SQLite实现） ====================
    
    def get_all_msds(self) -> List[Dict]:
        """获取所有MSDS"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM msds_documents")
            rows = cursor.fetchall()
            conn.close()
            # 转换为字典列表
            msds_list = [dict(row) for row in rows]
            return msds_list
        except Exception as e:
            print(f"❌ 获取所有MSDS失败: {str(e)}")
            return []
    
    def save_msds(self, msds_data: Dict) -> bool:
        """保存MSDS（新增/更新）"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            # 提取字段
            msds_id = msds_data.get('msds_id')
            if not msds_id:
                raise ValueError("MSDS ID不能为空")
            
            # 插入/更新MSDS数据
            cursor.execute('''
            INSERT OR REPLACE INTO msds_documents (
                msds_id, material_id, document_name, file_path, upload_date
            ) VALUES (?, ?, ?, ?, ?)
            ''', (
                msds_id,
                msds_data.get('material_id', ''),
                msds_data.get('document_name', ''),
                msds_data.get('file_path', ''),
                msds_data.get('upload_date', '')
            ))
            conn.commit()
            conn.close()
            # 发射信号
            self.msds_changed.emit(msds_id)
            print(f"✅ MSDS[{msds_id}]已保存到SQLite")
            return True
        except Exception as e:
            print(f"❌ 保存MSDS失败: {str(e)}")
            return False
    
    # ==================== 项目管理方法（SQLite实现） ====================
    
    def get_all_projects(self) -> List[Dict]:
        """获取所有项目"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM projects")
            rows = cursor.fetchall()
            conn.close()
            # 转换为字典列表
            project_list = [dict(row) for row in rows]
            return project_list
        except Exception as e:
            print(f"❌ 获取所有项目失败: {str(e)}")
            return []
    
    def save_project(self, project_data: Dict) -> bool:
        """保存项目（新增/更新）"""
        try:
            conn = self._get_db_connection()
            cursor = conn.cursor()
            # 提取字段
            project_id = project_data.get('project_id')
            if not project_id:
                raise ValueError("项目ID不能为空")
            
            # 插入/更新项目数据
            cursor.execute('''
            INSERT OR REPLACE INTO projects (
                project_id, name, code, description, start_date, end_date, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                project_id,
                project_data.get('name', ''),
                project_data.get('code', ''),
                project_data.get('description', ''),
                project_data.get('start_date', ''),
                project_data.get('end_date', ''),
                project_data.get('status', '')
            ))
            conn.commit()
            conn.close()
            # 发射信号
            self.project_changed.emit(project_id)
            print(f"✅ 项目[{project_id}]已保存到SQLite")
            return True
        except Exception as e:
            print(f"❌ 保存项目失败: {str(e)}")
            return False
    
    # ==================== 数据统计 ====================
    
    def get_data_stats(self) -> Dict[str, int]:
        """获取数据统计"""
        return {
            'materials': len(self.get_all_materials()),
            'equipment': len(self.get_all_equipment()),
            'msds': len(self.get_all_msds()),
            'projects': len(self.get_all_projects())
        }
    
    # ==================== 演示数据初始化 ====================
    
    def _init_demo_data(self):
        """初始化演示数据（仅首次运行时加载）"""
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
        """加载演示物料数据到SQLite"""
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
                self.save_material(material_data)
            
            print(f"✅ 演示物料数据加载完成: {len(demo_materials)} 个物料")
            
        except Exception as e:
            print(f"❌ 加载演示物料数据失败: {e}")
    
    def _load_demo_equipment(self):
        """加载演示设备数据到SQLite"""
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
                self.save_equipment(equipment_data)
            
            print(f"✅ 演示设备数据加载完成: {len(demo_equipment)} 个设备")
            
        except Exception as e:
            print(f"❌ 加载演示设备数据失败: {e}")
    
    # ==================== 兼容方法 ====================
    
    def get_main_data_manager(self):
        """获取主 DataManager 实例（兼容保留）"""
        return self.main_data_manager


# 全局管理器实例
global_process_design_manager = ProcessDesignManager()