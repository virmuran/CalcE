# TofuApp/modules/process_design/data/data_sync.py
"""
数据同步管理器 - 处理跨模块数据同步和冲突解决
"""
import threading
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime

from .unified_data_manager import UIDDataManager
from .data_models import UnifiedEquipment

class DataSyncManager:
    """数据同步管理器"""
    
    def __init__(self, data_manager: UIDDataManager):
        self.data_manager = data_manager
        self.observers: Dict[str, List[Callable]] = {}
        self.lock = threading.RLock()
    
    def register_observer(self, module_name: str, callback: Callable):
        """注册观察者"""
        with self.lock:
            if module_name not in self.observers:
                self.observers[module_name] = []
            self.observers[module_name].append(callback)
    
    def unregister_observer(self, module_name: str, callback: Callable):
        """取消注册观察者"""
        with self.lock:
            if module_name in self.observers:
                if callback in self.observers[module_name]:
                    self.observers[module_name].remove(callback)
    
    def notify_observers(self, uid: str, changed_by_module: str, 
                        change_type: str, data: Dict):
        """通知所有观察者"""
        with self.lock:
            for module_name, callbacks in self.observers.items():
                # 不通知发起变更的模块自身
                if module_name == changed_by_module:
                    continue
                
                for callback in callbacks:
                    try:
                        callback({
                            'uid': uid,
                            'changed_by': changed_by_module,
                            'change_type': change_type,
                            'timestamp': datetime.now().isoformat(),
                            'data': data
                        })
                    except Exception as e:
                        print(f"⚠️ 通知观察者失败 ({module_name}): {e}")
    
    def sync_equipment_data(self, equipment_uid: str, source_module: str) -> bool:
        """同步设备数据到所有模块"""
        try:
            equipment = self.data_manager.get_equipment(equipment_uid)
            if not equipment:
                return False
            
            # 获取数据完整性信息
            completeness = equipment.get_completeness_score()
            
            # 通知所有观察者
            self.notify_observers(
                uid=equipment_uid,
                changed_by_module=source_module,
                change_type='equipment_updated',
                data={
                    'equipment': equipment.to_dict(),
                    'completeness': completeness
                }
            )
            
            return True
        except Exception as e:
            print(f"❌ 同步设备数据失败: {e}")
            return False
    
    def resolve_data_conflict(self, uid: str, 
                            conflicting_data: Dict[str, Any]) -> Dict[str, Any]:
        """解决数据冲突"""
        try:
            # 获取当前数据
            current_data = self.data_manager.get_equipment(uid)
            if not current_data:
                return conflicting_data
            
            # 简单冲突解决策略：使用最新的非空数据
            resolved = current_data.to_dict()
            
            for key, value in conflicting_data.items():
                if value is not None and value != '':
                    if isinstance(value, (dict, list)) and value:
                        resolved[key] = value
                    elif value:
                        resolved[key] = value
            
            # 更新版本
            resolved['version'] = resolved.get('version', 0) + 1
            resolved['updated_at'] = datetime.now().isoformat()
            
            return resolved
            
        except Exception as e:
            print(f"❌ 解决数据冲突失败: {e}")
            return conflicting_data
    
    def get_sync_status(self) -> Dict[str, Any]:
        """获取同步状态"""
        try:
            # 获取数据统计
            stats = self.data_manager.get_data_stats()
            
            # 获取最近变更
            recent_changes = self.data_manager.get_change_history(limit=10)
            
            # 计算同步状态
            sync_status = {
                'last_sync': datetime.now().isoformat(),
                'total_objects': sum(stats.values()),
                'by_type': stats,
                'recent_changes': recent_changes,
                'observer_count': sum(len(callbacks) for callbacks in self.observers.values())
            }
            
            return sync_status
        except Exception as e:
            print(f"❌ 获取同步状态失败: {e}")
            return {}