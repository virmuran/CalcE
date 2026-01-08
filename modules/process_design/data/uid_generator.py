# TofuApp/modules/process_design/data/uid_generator.py
"""
UID生成器 - 为所有对象生成唯一标识符
"""
import uuid
import time
from typing import Optional, Dict

class UIDGenerator:
    """UID生成器"""
    
    def __init__(self, prefix: str = ""):
        self.prefix = prefix
        self.counter = 0
    
    def generate_uid(self, object_type: Optional[str] = None) -> str:
        """生成UID"""
        self.counter += 1
        
        # 基于时间戳的UID
        timestamp = int(time.time() * 1000)
        random_part = str(uuid.uuid4())[:8]
        
        parts = []
        if self.prefix:
            parts.append(self.prefix)
        
        if object_type:
            parts.append(object_type[:3].upper())
        
        parts.extend([
            str(timestamp)[-8:],
            str(self.counter).zfill(6),
            random_part
        ])
        
        return "_".join(parts)
    
    def parse_uid(self, uid: str) -> Dict[str, str]:
        """解析UID"""
        parts = uid.split('_')
        return {
            'prefix': parts[0] if len(parts) > 1 else '',
            'type': parts[1] if len(parts) > 2 else '',
            'timestamp': parts[-3] if len(parts) > 3 else '',
            'counter': parts[-2] if len(parts) > 2 else '',
            'random': parts[-1] if len(parts) > 1 else ''
        }

# 全局UID生成器实例
global_uid_generator = UIDGenerator(prefix="TOFU")