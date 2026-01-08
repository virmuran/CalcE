# TofuApp/modules/process_design/utils/file_utils.py
"""
文件操作工具函数
"""
import os
import json
import csv
import pandas as pd
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

def ensure_directory(directory_path: str) -> bool:
    """
    确保目录存在，如果不存在则创建
    
    参数:
        directory_path: 目录路径
    
    返回:
        是否成功
    """
    try:
        if not os.path.exists(directory_path):
            os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        print(f"❌ 创建目录失败: {e}")
        return False

def read_json_file(file_path: str) -> Optional[Dict[str, Any]]:
    """
    读取JSON文件
    
    参数:
        file_path: JSON文件路径
    
    返回:
        解析后的字典，失败返回None
    """
    try:
        if not os.path.exists(file_path):
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ 读取JSON文件失败: {e}")
        return None

def save_json_file(data: Dict[str, Any], file_path: str) -> bool:
    """
    保存数据到JSON文件
    
    参数:
        data: 要保存的数据
        file_path: 文件路径
    
    返回:
        是否成功
    """
    try:
        # 确保目录存在
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            ensure_directory(directory)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        return True
    except Exception as e:
        print(f"❌ 保存JSON文件失败: {e}")
        return False

def read_csv_file(file_path: str) -> Optional[List[Dict[str, Any]]]:
    """
    读取CSV文件
    
    参数:
        file_path: CSV文件路径
    
    返回:
        数据列表，失败返回None
    """
    try:
        if not os.path.exists(file_path):
            return None
        
        data = []
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(dict(row))
        return data
    except Exception as e:
        print(f"❌ 读取CSV文件失败: {e}")
        return None

def save_to_csv(data: List[Dict[str, Any]], file_path: str) -> bool:
    """
    保存数据到CSV文件
    
    参数:
        data: 数据列表
        file_path: 文件路径
    
    返回:
        是否成功
    """
    try:
        if not data:
            return False
        
        # 确保目录存在
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            ensure_directory(directory)
        
        # 获取字段名
        fieldnames = list(data[0].keys())
        
        with open(file_path, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        
        return True
    except Exception as e:
        print(f"❌ 保存CSV文件失败: {e}")
        return False

def save_to_excel(data: List[Dict[str, Any]], file_path: str) -> bool:
    """
    保存数据到Excel文件
    
    参数:
        data: 数据列表
        file_path: 文件路径
    
    返回:
        是否成功
    """
    try:
        if not data:
            return False
        
        # 确保目录存在
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            ensure_directory(directory)
        
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False)
        return True
    except Exception as e:
        print(f"❌ 保存Excel文件失败: {e}")
        return False

def get_file_extension(file_path: str) -> str:
    """
    获取文件扩展名
    
    参数:
        file_path: 文件路径
    
    返回:
        文件扩展名（小写）
    """
    return os.path.splitext(file_path)[1].lower()

def is_valid_file_path(file_path: str) -> bool:
    """
    检查文件路径是否有效
    
    参数:
        file_path: 文件路径
    
    返回:
        是否有效
    """
    try:
        # 检查路径是否合法
        if not file_path or len(file_path) > 260:  # Windows路径长度限制
            return False
        
        # 检查路径分隔符
        if '..' in file_path or '//' in file_path:
            return False
        
        # 检查文件名是否合法
        filename = os.path.basename(file_path)
        if not filename or filename.startswith('.') or filename.endswith('.'):
            return False
        
        # 检查非法字符（Windows）
        illegal_chars = '<>:"|?*'
        if any(char in filename for char in illegal_chars):
            return False
        
        return True
    except:
        return False

def get_file_size(file_path: str) -> Optional[int]:
    """
    获取文件大小（字节）
    
    参数:
        file_path: 文件路径
    
    返回:
        文件大小（字节），文件不存在返回None
    """
    try:
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return None
    except:
        return None

def backup_file(file_path: str, backup_suffix: str = ".bak") -> bool:
    """
    备份文件
    
    参数:
        file_path: 原文件路径
        backup_suffix: 备份文件后缀
    
    返回:
        是否成功
    """
    try:
        if not os.path.exists(file_path):
            return False
        
        backup_path = file_path + backup_suffix
        
        # 如果备份文件已存在，添加时间戳
        if os.path.exists(backup_path):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"{file_path}_{timestamp}{backup_suffix}"
        
        import shutil
        shutil.copy2(file_path, backup_path)
        return True
    except Exception as e:
        print(f"❌ 备份文件失败: {e}")
        return False

def find_files_by_extension(directory: str, extensions: List[str]) -> List[str]:
    """
    查找指定扩展名的文件
    
    参数:
        directory: 目录路径
        extensions: 扩展名列表（例如 ['.txt', '.csv']）
    
    返回:
        文件路径列表
    """
    result = []
    
    if not os.path.exists(directory):
        return result
    
    extensions = [ext.lower() for ext in extensions]
    
    for root, _, files in os.walk(directory):
        for file in files:
            if get_file_extension(file) in extensions:
                result.append(os.path.join(root, file))
    
    return result

def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小显示
    
    参数:
        size_bytes: 字节数
    
    返回:
        格式化后的字符串（如 "1.23 MB"）
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / 1024 ** 2:.2f} MB"
    else:
        return f"{size_bytes / 1024 ** 3:.2f} GB"

def load_template_file(template_name: str, data_dir: str = "templates") -> Optional[str]:
    """
    加载模板文件
    
    参数:
        template_name: 模板文件名
        data_dir: 模板目录
    
    返回:
        模板内容，失败返回None
    """
    try:
        template_path = os.path.join(data_dir, template_name)
        if not os.path.exists(template_path):
            return None
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"❌ 加载模板文件失败: {e}")
        return None