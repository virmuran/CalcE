# TofuApp/resource_helper.py
import sys
import os
from pathlib import Path

class ResourceHelper:
    """资源助手 - 仅管理应用程序资源"""
    
    @staticmethod
    def resource_path(relative_path):
        """获取打包后资源的绝对路径"""
        try:
            # PyInstaller创建临时文件夹存储资源，路径在_MEIPASS中
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        
        return os.path.join(base_path, relative_path)
    
    @staticmethod
    def get_icon_path(icon_name):
        """获取图标文件路径"""
        # 优先在当前目录查找
        local_icon_path = os.path.join("icons", icon_name)
        if os.path.exists(local_icon_path):
            return local_icon_path
        
        # 然后在资源路径中查找
        try:
            resource_icon_path = ResourceHelper.resource_path(f"icons/{icon_name}")
            if os.path.exists(resource_icon_path):
                return resource_icon_path
        except:
            pass
        
        # 如果都找不到，返回 None（应用程序将使用默认图标）
        return None
    
    @staticmethod
    def get_data_file_path():
        """获取数据文件路径（保持与现有代码兼容）"""
        # 尝试使用与 data_manager.py 相同的逻辑
        try:
            from PySide6.QtCore import QStandardPaths
            app_data_dir = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
            if not app_data_dir:
                app_data_dir = os.path.abspath(".")
            return os.path.join(app_data_dir, "tofu_data.json")
        except Exception:
            return os.path.join(os.path.abspath("."), "tofu_data.json")

# 保持向后兼容的函数
def resource_path(relative_path):
    return ResourceHelper.resource_path(relative_path)

def get_icon_path(icon_name):
    return ResourceHelper.get_icon_path(icon_name)