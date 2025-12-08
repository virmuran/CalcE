# module_loader.py
import sys
import os
import traceback
import importlib
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PySide6.QtCore import Qt

class ModuleLoader:
    """模块加载器 - 统一管理模块的导入和初始化"""
    
    @staticmethod
    def load_module(module_file, class_name, parent=None, data_manager=None):
        try:
            # 导入模块
            module = importlib.import_module(module_file)
            # 获取类
            module_class = getattr(module, class_name)
            # 创建实例，传递数据管理器
            if data_manager is not None:
                instance = module_class(parent, data_manager)
            else:
                instance = module_class(parent)
            return instance
        except Exception as e:
            print(f"加载模块 {module_file}.{class_name} 失败: {e}")
            traceback.print_exc()
            return ModuleLoader.create_error_widget(f"模块加载失败: {module_file}", str(e))

    @staticmethod
    def create_error_widget(title, error_msg):
        """创建错误显示组件"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        error_label = QLabel(f"❌ {title}")
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setStyleSheet("color: red; font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(error_label)
        
        error_text = QTextEdit()
        error_text.setPlainText(f"错误详情:\n{error_msg}")
        error_text.setReadOnly(True)
        error_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 5px;
                padding: 10px;
                font-family: monospace;
                font-size: 10px;
            }
        """)
        layout.addWidget(error_text)
        
        debug_label = QLabel("💡 请检查:\n1. 模块文件是否存在\n2. 文件中是否有语法错误\n3. 依赖是否正确安装")
        debug_label.setAlignment(Qt.AlignCenter)
        debug_label.setStyleSheet("color: gray; font-size: 12px; padding: 10px;")
        layout.addWidget(debug_label)
        
        return widget
    
    @staticmethod
    def get_available_modules():
        """获取所有可用的模块配置"""
        return [
            # 使用完整模块路径
            ("modules.process_design", "ProcessDesignWidget", "工艺设计", "🏭"),
            ("modules.chemical_calculations", "ChemicalCalculationsWidget", "工程计算", "🔬"),
            ("modules.converter.converter_widget", "ConverterWidget", "换算器", "📐"),
            ("modules.pomodoro", "PomodoroTimer", "番茄时钟", "🍅"),
            ("modules.todo", "TodoManager", "待办事项", "✅"),
            ("modules.notes", "NotesWidget", "笔记", "📝"),
            ("modules.bookmarks", "BookmarksWidget", "书签", "🔖"),
            ("modules.important_dates", "ImportantDatesWidget", "重要日期", "📅"),
            ("modules.countdowns", "CountdownsWidget", "倒计时", "⏰"),
            ("modules.year_progress", "YearProgressWidget", "今年余额", "📊")
        ]

# 为了向后兼容，提供函数形式的接口
def load_module(module_file, class_name, parent=None, data_manager=None):
    return ModuleLoader.load_module(module_file, class_name, parent, data_manager)

def create_error_widget(title, error_msg):
    return ModuleLoader.create_error_widget(title, error_msg)