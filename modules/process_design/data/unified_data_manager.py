# TofuApp/modules/process_design/data/unified_data_manager.py
"""
基于UID的统一数据管理器 - 管理所有工艺设计数据
"""
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
import threading
import os

from .data_models import (
    UnifiedEquipment, MaterialProperty, 
    ProcessRoute, MSDSDocument, ProcessFlowDiagram, ProcessProject
)
from .uid_generator import global_uid_generator

class UIDDataManager:
    """基于UID的统一数据管理器"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # 使用相对路径，存储在模块目录下的data文件夹中
            module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(module_dir, "data", "tofu_process_design.db")
        
        self.db_path = db_path
        self.conn = None
        self.lock = threading.RLock()
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        with self.lock:
            try:
                # 确保目录存在
                os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
                
                self.conn = sqlite3.connect(self.db_path)
                cursor = self.conn.cursor()
                
                # 创建统一设备表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS unified_equipment (
                        uid TEXT PRIMARY KEY,
                        equipment_id TEXT UNIQUE NOT NULL,
                        code TEXT,
                        name TEXT NOT NULL,
                        equipment_type TEXT,
                        
                        -- 设备清单字段
                        unique_code TEXT,
                        specification TEXT,
                        model TEXT,
                        manufacturer TEXT,
                        design_pressure TEXT,
                        design_temperature TEXT,
                        operating_pressure TEXT,
                        operating_temperature TEXT,
                        quantity INTEGER DEFAULT 1,
                        running_quantity INTEGER DEFAULT 1,
                        single_power REAL DEFAULT 0,
                        total_power REAL DEFAULT 0,
                        material TEXT,
                        insulation TEXT,
                        weight_estimate REAL DEFAULT 0,
                        operating_weight REAL DEFAULT 0,
                        unit_price REAL DEFAULT 0,
                        total_price REAL DEFAULT 0,
                        notes TEXT,
                        
                        -- 流程图字段
                        pfd_position_x REAL DEFAULT 0,
                        pfd_position_y REAL DEFAULT 0,
                        pfd_width REAL DEFAULT 100,
                        pfd_height REAL DEFAULT 60,
                        pfd_connections TEXT DEFAULT '[]',
                        pfd_properties TEXT DEFAULT '{}',
                        
                        -- MSDS字段
                        msds_uid TEXT,
                        hazard_class TEXT,
                        material_cas TEXT,
                        
                        -- 通用字段
                        status TEXT DEFAULT 'active',
                        location TEXT,
                        description TEXT,
                        tags TEXT DEFAULT '[]',
                        
                        -- 时间戳
                        created_at TIMESTAMP,
                        updated_at TIMESTAMP,
                        created_by TEXT,
                        updated_by TEXT,
                        
                        -- 版本控制
                        version INTEGER DEFAULT 1,
                        revision_history TEXT DEFAULT '[]',
                        
                        -- 元数据
                        source_module TEXT,
                        completeness_score REAL DEFAULT 0
                    )
                ''')
                
                # 创建物料表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS materials (
                        uid TEXT PRIMARY KEY,
                        material_id TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        cas_number TEXT,
                        molecular_formula TEXT,
                        molecular_weight REAL,
                        density REAL,
                        boiling_point REAL,
                        melting_point REAL,
                        flash_point REAL,
                        phase TEXT DEFAULT 'liquid',
                        hazard_class TEXT,
                        msds_id TEXT,
                        created_at TIMESTAMP,
                        updated_at TIMESTAMP
                    )
                ''')
                
                # 创建工艺路线表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS process_routes (
                        uid TEXT PRIMARY KEY,
                        route_id TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        product TEXT,
                        description TEXT,
                        steps TEXT DEFAULT '[]',
                        status TEXT DEFAULT 'draft',
                        notes TEXT,
                        created_at TIMESTAMP,
                        updated_at TIMESTAMP
                    )
                ''')
                
                # 创建MSDS表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS msds_documents (
                        uid TEXT PRIMARY KEY,
                        msds_id TEXT UNIQUE NOT NULL,
                        material_name TEXT NOT NULL,
                        cas_number TEXT,
                        supplier TEXT,
                        version TEXT,
                        effective_date TEXT,
                        expiry_date TEXT,
                        hazard_class TEXT,
                        status TEXT DEFAULT '有效',
                        description TEXT,
                        file_path TEXT,
                        file_size INTEGER,
                        created_at TIMESTAMP,
                        updated_at TIMESTAMP
                    )
                ''')
                
                # 创建工艺流程图表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS process_flows (
                        uid TEXT PRIMARY KEY,
                        diagram_id TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        nodes TEXT DEFAULT '[]',
                        connections TEXT DEFAULT '[]',
                        metadata TEXT DEFAULT '{}',
                        equipment_uids TEXT DEFAULT '[]',
                        created_at TIMESTAMP,
                        updated_at TIMESTAMP
                    )
                ''')
                
                # 创建项目表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS process_projects (
                        uid TEXT PRIMARY KEY,
                        project_id TEXT UNIQUE NOT NULL,
                        name TEXT NOT NULL,
                        description TEXT,
                        status TEXT DEFAULT 'active',
                        start_date TEXT,
                        end_date TEXT,
                        manager TEXT,
                        created_at TIMESTAMP,
                        updated_at TIMESTAMP
                    )
                ''')
                
                # 创建变化历史表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS change_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        object_uid TEXT NOT NULL,
                        object_type TEXT NOT NULL,
                        operation TEXT NOT NULL,
                        changed_by TEXT,
                        changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        changes TEXT DEFAULT '{}',
                        before_state TEXT,
                        after_state TEXT
                    )
                ''')
                
                # 创建索引
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_equipment_uid ON unified_equipment(uid)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_equipment_code ON unified_equipment(code)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_material_uid ON materials(uid)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_msds_uid ON msds_documents(uid)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_route_uid ON process_routes(uid)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_flow_uid ON process_flows(uid)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_project_uid ON process_projects(uid)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_change_object ON change_history(object_uid)')
                
                self.conn.commit()
                print(f"✅ 数据库初始化完成: {self.db_path}")
                
            except Exception as e:
                print(f"❌ 初始化数据库失败: {e}")
                if self.conn:
                    self.conn.rollback()
                raise
    
    # ==================== 基础CRUD操作 ====================
    
    def _save_record(self, table: str, obj: Any) -> bool:
        """保存记录到数据库"""
        with self.lock:
            try:
                data = obj.to_dict()
                
                # 处理JSON字段
                json_fields_mapping = {
                    'unified_equipment': {
                        'pfd_connections': 'list',
                        'pfd_properties': 'dict',
                        'tags': 'list',
                        'revision_history': 'list'
                    },
                    'process_routes': {
                        'steps': 'list'
                    },
                    'process_flows': {
                        'nodes': 'list',
                        'connections': 'list',
                        'metadata': 'dict',
                        'equipment_uids': 'list'
                    }
                }
                
                # ==================== 修复：在构建SQL参数之前转换所有JSON字段 ====================
                table_fields = json_fields_mapping.get(table, {})
                for field, field_type in table_fields.items():
                    if field in data:
                        if data[field] is None:
                            if field_type == 'list':
                                data[field] = '[]'
                            elif field_type == 'dict':
                                data[field] = '{}'
                        elif field_type == 'list':
                            # 确保转换为JSON字符串
                            if not isinstance(data[field], str):
                                data[field] = json.dumps(data[field], ensure_ascii=False)
                        elif field_type == 'dict':
                            # 确保转换为JSON字符串
                            if not isinstance(data[field], str):
                                data[field] = json.dumps(data[field], ensure_ascii=False)
                # ==================== 修复结束 ====================
                
                # 特殊处理位置和尺寸（仅设备表）
                if table == 'unified_equipment':
                    if 'pfd_position' in data:
                        position = data.pop('pfd_position', {'x': 0, 'y': 0})
                        data['pfd_position_x'] = position.get('x', 0)
                        data['pfd_position_y'] = position.get('y', 0)
                    
                    if 'pfd_size' in data:
                        size = data.pop('pfd_size', {'width': 100, 'height': 60})
                        data['pfd_width'] = size.get('width', 100)
                        data['pfd_height'] = size.get('height', 60)
                
                cursor = self.conn.cursor()
                
                # 检查是否存在
                cursor.execute(f"SELECT uid FROM {table} WHERE uid = ?", (data['uid'],))
                exists = cursor.fetchone()
                
                if exists:
                    # 更新
                    set_clause = ', '.join([f"{k} = ?" for k in data.keys() if k != 'uid'])
                    params = [v for k, v in data.items() if k != 'uid']
                    params.append(data['uid'])
                    
                    sql = f"UPDATE {table} SET {set_clause} WHERE uid = ?"
                else:
                    # 插入
                    columns = ', '.join(data.keys())
                    placeholders = ', '.join(['?' for _ in data])
                    params = list(data.values())
                    
                    sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
                
                cursor.execute(sql, params)
                self.conn.commit()
                
                # 记录变更历史
                self._log_change(
                    object_uid=data['uid'],
                    object_type=table,
                    operation='UPDATE' if exists else 'INSERT',
                    changes=data
                )
                
                return True
                
            except Exception as e:
                print(f"❌ 保存记录失败 ({table}): {e}")
                import traceback
                traceback.print_exc()  # 打印详细的错误堆栈
                self.conn.rollback()
                return False
    
    def _get_record(self, table: str, uid: str) -> Optional[Dict]:
        """获取单个记录"""
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"SELECT * FROM {table} WHERE uid = ?", (uid,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            # 转换为字典
            columns = [description[0] for description in cursor.description]
            data = dict(zip(columns, row))
            
            # 处理JSON字段
            json_fields_mapping = {
                'unified_equipment': {
                    'pfd_connections': 'list',
                    'pfd_properties': 'dict',
                    'tags': 'list',
                    'revision_history': 'list'
                },
                'process_routes': {
                    'steps': 'list'
                },
                'process_flows': {
                    'nodes': 'list',
                    'connections': 'list',
                    'metadata': 'dict',
                    'equipment_uids': 'list'
                }
            }
            
            table_fields = json_fields_mapping.get(table, {})
            for field, field_type in table_fields.items():
                if field in data and data[field]:
                    try:
                        if field_type == 'list':
                            data[field] = json.loads(data[field])
                        elif field_type == 'dict':
                            data[field] = json.loads(data[field])
                    except:
                        if field_type == 'list':
                            data[field] = []
                        elif field_type == 'dict':
                            data[field] = {}
                elif field in data:
                    if field_type == 'list':
                        data[field] = []
                    elif field_type == 'dict':
                        data[field] = {}
            
            # 重构位置和尺寸（仅设备表）
            if table == 'unified_equipment':
                if 'pfd_position_x' in data and 'pfd_position_y' in data:
                    data['pfd_position'] = {
                        'x': data.pop('pfd_position_x', 0),
                        'y': data.pop('pfd_position_y', 0)
                    }
                
                if 'pfd_width' in data and 'pfd_height' in data:
                    data['pfd_size'] = {
                        'width': data.pop('pfd_width', 100),
                        'height': data.pop('pfd_height', 60)
                    }
                
                # 处理tags字段
                if 'tags' in data and isinstance(data['tags'], list):
                    data['tags'] = set(data['tags'])
            
            return data
            
        except Exception as e:
            print(f"❌ 获取记录失败 ({table}): {e}")
            return None
    
    def _get_all_records(self, table: str, filter_dict: Optional[Dict] = None) -> List[Dict]:
        """获取所有记录"""
        try:
            cursor = self.conn.cursor()
            
            if filter_dict:
                conditions = []
                params = []
                for key, value in filter_dict.items():
                    conditions.append(f"{key} = ?")
                    params.append(value)
                
                where_clause = " AND ".join(conditions)
                cursor.execute(f"SELECT * FROM {table} WHERE {where_clause}", params)
            else:
                cursor.execute(f"SELECT * FROM {table}")
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            records = []
            for row in rows:
                data = dict(zip(columns, row))
                
                # 处理JSON字段
                json_fields_mapping = {
                    'unified_equipment': {
                        'pfd_connections': 'list',
                        'pfd_properties': 'dict',
                        'tags': 'list',
                        'revision_history': 'list'
                    },
                    'process_routes': {
                        'steps': 'list'
                    },
                    'process_flows': {
                        'nodes': 'list',
                        'connections': 'list',
                        'metadata': 'dict',
                        'equipment_uids': 'list'
                    }
                }
                
                table_fields = json_fields_mapping.get(table, {})
                for field, field_type in table_fields.items():
                    if field in data and data[field]:
                        try:
                            if field_type == 'list':
                                data[field] = json.loads(data[field])
                            elif field_type == 'dict':
                                data[field] = json.loads(data[field])
                        except:
                            if field_type == 'list':
                                data[field] = []
                            elif field_type == 'dict':
                                data[field] = {}
                    elif field in data:
                        if field_type == 'list':
                            data[field] = []
                        elif field_type == 'dict':
                            data[field] = {}
                
                # 重构位置和尺寸（仅设备表）
                if table == 'unified_equipment':
                    if 'pfd_position_x' in data and 'pfd_position_y' in data:
                        data['pfd_position'] = {
                            'x': data.pop('pfd_position_x', 0),
                            'y': data.pop('pfd_position_y', 0)
                        }
                    
                    if 'pfd_width' in data and 'pfd_height' in data:
                        data['pfd_size'] = {
                            'width': data.pop('pfd_width', 100),
                            'height': data.pop('pfd_height', 60)
                        }
                    
                    # 处理tags字段
                    if 'tags' in data and isinstance(data['tags'], list):
                        data['tags'] = set(data['tags'])
                
                records.append(data)
            
            return records
            
        except Exception as e:
            print(f"❌ 获取所有记录失败 ({table}): {e}")
            return []
    
    def _delete_record(self, table: str, uid: str) -> bool:
        """删除记录"""
        with self.lock:
            try:
                # 先获取记录用于审计
                before_state = self._get_record(table, uid)
                
                cursor = self.conn.cursor()
                cursor.execute(f"DELETE FROM {table} WHERE uid = ?", (uid,))
                self.conn.commit()
                
                # 记录变更历史
                if before_state:
                    self._log_change(
                        object_uid=uid,
                        object_type=table,
                        operation='DELETE',
                        before_state=before_state
                    )
                
                return cursor.rowcount > 0
                
            except Exception as e:
                print(f"❌ 删除记录失败 ({table}): {e}")
                self.conn.rollback()
                return False
    
    def _log_change(self, object_uid: str, object_type: str, operation: str, 
                   changes: Optional[Dict] = None, before_state: Optional[Dict] = None,
                   after_state: Optional[Dict] = None, changed_by: Optional[str] = None):
        """记录变更历史"""
        try:
            cursor = self.conn.cursor()
            
            changes_json = json.dumps(changes, ensure_ascii=False) if changes else '{}'
            before_json = json.dumps(before_state, ensure_ascii=False) if before_state else None
            after_json = json.dumps(after_state, ensure_ascii=False) if after_state else None
            
            cursor.execute('''
                INSERT INTO change_history 
                (object_uid, object_type, operation, changed_by, changes, before_state, after_state)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (object_uid, object_type, operation, changed_by, changes_json, before_json, after_json))
            
            self.conn.commit()
        except Exception as e:
            print(f"⚠️ 记录变更历史失败: {e}")
    
    # ==================== 设备管理 ====================
    
    def save_equipment(self, equipment: UnifiedEquipment) -> str:
        """保存设备"""
        if self._save_record('unified_equipment', equipment):
            return equipment.uid
        return ""
    
    def get_equipment(self, uid: str) -> Optional[UnifiedEquipment]:
        """获取设备"""
        data = self._get_record('unified_equipment', uid)
        if data:
            return UnifiedEquipment.from_dict(data)
        return None
    
    def get_equipment_by_code(self, code: str) -> Optional[UnifiedEquipment]:
        """通过业务代码获取设备"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM unified_equipment WHERE code = ? OR equipment_id = ?", 
                          (code, code))
            row = cursor.fetchone()
            
            if row:
                columns = [description[0] for description in cursor.description]
                data = dict(zip(columns, row))
                
                # 处理JSON字段
                for field in ['pfd_connections', 'pfd_properties', 'tags', 'revision_history']:
                    if field in data and data[field]:
                        try:
                            data[field] = json.loads(data[field])
                        except:
                            if field == 'tags':
                                data[field] = set()
                            elif field == 'revision_history':
                                data[field] = []
                            else:
                                data[field] = {}
                    elif field in data:
                        if field == 'tags':
                            data[field] = set()
                        elif field == 'revision_history':
                            data[field] = []
                        else:
                            data[field] = {}
                
                # 重构位置和尺寸
                if 'pfd_position_x' in data and 'pfd_position_y' in data:
                    data['pfd_position'] = {
                        'x': data.pop('pfd_position_x', 0),
                        'y': data.pop('pfd_position_y', 0)
                    }
                
                if 'pfd_width' in data and 'pfd_height' in data:
                    data['pfd_size'] = {
                        'width': data.pop('pfd_width', 100),
                        'height': data.pop('pfd_height', 60)
                    }
                
                return UnifiedEquipment.from_dict(data)
            return None
        except Exception as e:
            print(f"❌ 通过代码获取设备失败: {e}")
            return None
    
    def get_all_equipment(self, filter_dict: Optional[Dict] = None) -> List[UnifiedEquipment]:
        """获取所有设备"""
        records = self._get_all_records('unified_equipment', filter_dict)
        return [UnifiedEquipment.from_dict(r) for r in records]
    
    def delete_equipment(self, uid: str) -> bool:
        """删除设备"""
        return self._delete_record('unified_equipment', uid)
    
    def search_equipment(self, search_term: str, 
                        fields: List[str] = None) -> List[UnifiedEquipment]:
        """搜索设备"""
        try:
            if not fields:
                fields = ['equipment_id', 'name', 'unique_code', 'equipment_type', 'code']
            
            cursor = self.conn.cursor()
            
            conditions = []
            params = []
            search_pattern = f"%{search_term}%"
            
            for field in fields:
                conditions.append(f"{field} LIKE ?")
                params.append(search_pattern)
            
            where_clause = " OR ".join(conditions)
            
            cursor.execute(f'''
                SELECT * FROM unified_equipment 
                WHERE {where_clause}
                ORDER BY equipment_id
            ''', params)
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            results = []
            for row in rows:
                data = dict(zip(columns, row))
                
                # 处理JSON字段
                for field in ['pfd_connections', 'pfd_properties', 'tags', 'revision_history']:
                    if field in data and data[field]:
                        try:
                            data[field] = json.loads(data[field])
                        except:
                            if field == 'tags':
                                data[field] = set()
                            elif field == 'revision_history':
                                data[field] = []
                            else:
                                data[field] = {}
                    elif field in data:
                        if field == 'tags':
                            data[field] = set()
                        elif field == 'revision_history':
                            data[field] = []
                        else:
                            data[field] = {}
                
                # 重构位置和尺寸
                if 'pfd_position_x' in data and 'pfd_position_y' in data:
                    data['pfd_position'] = {
                        'x': data.pop('pfd_position_x', 0),
                        'y': data.pop('pfd_position_y', 0)
                    }
                
                if 'pfd_width' in data and 'pfd_height' in data:
                    data['pfd_size'] = {
                        'width': data.pop('pfd_width', 100),
                        'height': data.pop('pfd_height', 60)
                    }
                
                results.append(UnifiedEquipment.from_dict(data))
            
            return results
            
        except Exception as e:
            print(f"❌ 搜索设备失败: {e}")
            return []
    
    # ==================== 物料管理 ====================
    
    def save_material(self, material: MaterialProperty) -> str:
        """保存物料"""
        if self._save_record('materials', material):
            return material.uid
        return ""
    
    def get_material(self, uid: str) -> Optional[MaterialProperty]:
        """获取物料"""
        data = self._get_record('materials', uid)
        if data:
            return MaterialProperty.from_dict(data)
        return None
    
    def get_material_by_id(self, material_id: str) -> Optional[MaterialProperty]:
        """通过物料ID获取物料"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM materials WHERE material_id = ?", (material_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [description[0] for description in cursor.description]
                data = dict(zip(columns, row))
                return MaterialProperty.from_dict(data)
            return None
        except Exception as e:
            print(f"❌ 通过ID获取物料失败: {e}")
            return None
    
    def get_all_materials(self) -> List[MaterialProperty]:
        """获取所有物料"""
        records = self._get_all_records('materials')
        return [MaterialProperty.from_dict(r) for r in records]
    
    def delete_material(self, uid: str) -> bool:
        """删除物料"""
        return self._delete_record('materials', uid)
    
    def search_materials(self, search_term: str) -> List[MaterialProperty]:
        """搜索物料"""
        materials = self.get_all_materials()
        search_term = search_term.lower()
        results = []
        
        for material in materials:
            if (search_term in material.name.lower() or
                search_term in material.cas_number.lower() or
                search_term in material.material_id.lower()):
                results.append(material)
        
        return results
    
    # ==================== 工艺路线管理 ====================
    
    def save_process_route(self, route: ProcessRoute) -> str:
        """保存工艺路线"""
        if self._save_record('process_routes', route):
            return route.uid
        return ""
    
    def get_process_route(self, uid: str) -> Optional[ProcessRoute]:
        """获取工艺路线"""
        data = self._get_record('process_routes', uid)
        if data:
            # 处理steps字段
            if 'steps' in data and isinstance(data['steps'], str):
                try:
                    data['steps'] = json.loads(data['steps'])
                except:
                    data['steps'] = []
            return ProcessRoute.from_dict(data)
        return None
    
    def get_process_route_by_id(self, route_id: str) -> Optional[ProcessRoute]:
        """通过路线ID获取工艺路线"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM process_routes WHERE route_id = ?", (route_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [description[0] for description in cursor.description]
                data = dict(zip(columns, row))
                
                # 处理steps字段
                if 'steps' in data and isinstance(data['steps'], str):
                    try:
                        data['steps'] = json.loads(data['steps'])
                    except:
                        data['steps'] = []
                
                return ProcessRoute.from_dict(data)
            return None
        except Exception as e:
            print(f"❌ 通过ID获取工艺路线失败: {e}")
            return None
    
    def get_all_process_routes(self) -> List[ProcessRoute]:
        """获取所有工艺路线"""
        records = self._get_all_records('process_routes')
        
        # 处理steps字段
        for record in records:
            if 'steps' in record and isinstance(record['steps'], str):
                try:
                    record['steps'] = json.loads(record['steps'])
                except:
                    record['steps'] = []
        
        return [ProcessRoute.from_dict(r) for r in records]
    
    def delete_process_route(self, uid: str) -> bool:
        """删除工艺路线"""
        return self._delete_record('process_routes', uid)
    
    # ==================== MSDS管理 ====================
    
    def save_msds(self, msds: MSDSDocument) -> str:
        """保存MSDS"""
        if self._save_record('msds_documents', msds):
            return msds.uid
        return ""
    
    def get_msds(self, uid: str) -> Optional[MSDSDocument]:
        """获取MSDS"""
        data = self._get_record('msds_documents', uid)
        if data:
            return MSDSDocument.from_dict(data)
        return None
    
    def get_all_msds(self) -> List[MSDSDocument]:
        """获取所有MSDS"""
        records = self._get_all_records('msds_documents')
        return [MSDSDocument.from_dict(r) for r in records]
    
    def delete_msds(self, uid: str) -> bool:
        """删除MSDS"""
        return self._delete_record('msds_documents', uid)
    
    # ==================== 工艺流程图管理 ====================
    
    def save_process_flow(self, flow: ProcessFlowDiagram) -> str:
        """保存工艺流程图"""
        if self._save_record('process_flows', flow):
            return flow.uid
        return ""
    
    def get_process_flow(self, uid: str) -> Optional[ProcessFlowDiagram]:
        """获取工艺流程图"""
        data = self._get_record('process_flows', uid)
        if data:
            return ProcessFlowDiagram.from_dict(data)
        return None
    
    def get_all_process_flows(self) -> List[ProcessFlowDiagram]:
        """获取所有工艺流程图"""
        records = self._get_all_records('process_flows')
        return [ProcessFlowDiagram.from_dict(r) for r in records]
    
    def delete_process_flow(self, uid: str) -> bool:
        """删除工艺流程图"""
        return self._delete_record('process_flows', uid)
    
    # ==================== 项目管理 ====================
    
    def save_project(self, project: ProcessProject) -> str:
        """保存项目"""
        if self._save_record('process_projects', project):
            return project.uid
        return ""
    
    def get_project(self, uid: str) -> Optional[ProcessProject]:
        """获取项目"""
        data = self._get_record('process_projects', uid)
        if data:
            return ProcessProject.from_dict(data)
        return None
    
    def get_project_by_id(self, project_id: str) -> Optional[ProcessProject]:
        """通过项目ID获取项目"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM process_projects WHERE project_id = ?", (project_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [description[0] for description in cursor.description]
                data = dict(zip(columns, row))
                return ProcessProject.from_dict(data)
            return None
        except Exception as e:
            print(f"❌ 通过ID获取项目失败: {e}")
            return None
    
    def get_all_projects(self) -> List[ProcessProject]:
        """获取所有项目"""
        records = self._get_all_records('process_projects')
        return [ProcessProject.from_dict(r) for r in records]
    
    def delete_project(self, uid: str) -> bool:
        """删除项目"""
        return self._delete_record('process_projects', uid)
    
    # ==================== 数据统计和审计 ====================
    
    def get_change_history(self, object_uid: str = None, 
                          limit: int = 100) -> List[Dict]:
        """获取变更历史"""
        try:
            cursor = self.conn.cursor()
            
            if object_uid:
                cursor.execute('''
                    SELECT * FROM change_history 
                    WHERE object_uid = ? 
                    ORDER BY changed_at DESC 
                    LIMIT ?
                ''', (object_uid, limit))
            else:
                cursor.execute('''
                    SELECT * FROM change_history 
                    ORDER BY changed_at DESC 
                    LIMIT ?
                ''', (limit,))
            
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            history = []
            for row in rows:
                data = dict(zip(columns, row))
                
                # 处理JSON字段
                for field in ['changes', 'before_state', 'after_state']:
                    if field in data and data[field]:
                        try:
                            data[field] = json.loads(data[field])
                        except:
                            data[field] = {}
                    elif field in data:
                        data[field] = {}
                
                history.append(data)
            
            return history
        except Exception as e:
            print(f"❌ 获取变更历史失败: {e}")
            return []
    
    def get_data_completeness(self) -> Dict[str, float]:
        """获取数据完整性统计"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT source_module, AVG(completeness_score) as avg_score
                FROM unified_equipment
                GROUP BY source_module
            ''')
            
            result = {}
            for row in cursor.fetchall():
                result[row[0]] = row[1]
            
            return result
        except Exception as e:
            print(f"❌ 获取数据完整性统计失败: {e}")
            return {}
    
    def get_data_stats(self) -> Dict[str, int]:
        """获取数据统计"""
        try:
            cursor = self.conn.cursor()
            stats = {}
            
            # 统计各个表的记录数
            tables = ['unified_equipment', 'materials', 'process_routes', 
                     'msds_documents', 'process_flows', 'process_projects']
            
            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                stats[table] = count
            
            return stats
        except Exception as e:
            print(f"❌ 获取数据统计失败: {e}")
            return {}
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()

# 全局数据管理器实例
global_data_manager = UIDDataManager()