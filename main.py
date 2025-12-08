# main.py (只修改关键部分)
import sys
import os
import traceback
from datetime import datetime

# 添加当前目录和模块目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# 添加 modules 目录到路径
modules_dir = os.path.join(current_dir, 'modules')
if modules_dir not in sys.path:
    sys.path.insert(0, modules_dir)

# 添加 converter 目录到路径
converter_dir = os.path.join(current_dir, 'modules', 'converter')
if converter_dir not in sys.path:
    sys.path.insert(0, converter_dir)

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
    QMessageBox, QMenuBar, QMenu, QStatusBar, QLabel
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QFont
from datetime import datetime

try:
    from data_manager import DataManager
    from theme_manager import ThemeManager
    from module_loader import ModuleLoader
except ImportError as e:
    print(f"导入模块失败: {e}")
    traceback.print_exc()
    print("尝试继续运行程序...")

class TofuApp(QMainWindow):
    """Tofu主应用程序"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tofu - 个人生产力工具")
        self.setGeometry(100, 100, 1600, 900)
        
        # 初始化管理器
        self.theme_manager = ThemeManager()
        self.data_manager = DataManager.get_instance()
        
        # 存储模块实例
        self.modules = {}
        
        # 创建UI
        self.setup_ui()
        
        # 加载设置
        self.load_settings()
        
        print("✅ Tofu应用程序初始化完成")

    def center_window(self):
        """居中显示窗口"""
        screen = QApplication.primaryScreen().geometry()
        window_geometry = self.frameGeometry()
        center_point = screen.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())
    
    def setup_ui(self):
        """设置用户界面"""
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # 创建各功能标签页
        self.create_modules()
        
        # 添加菜单和状态栏
        self.setup_menu()
        self.setup_status_bar()
        
        # 连接信号
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.theme_manager.theme_changed.connect(self.apply_theme)
    
    def create_modules(self):
        """创建所有功能模块"""
        modules_config = [
            # 修改：使用完整模块路径
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
        
        for module_file, class_name, tab_name, icon in modules_config:
            try:
                widget = ModuleLoader.load_module(module_file, class_name, self, self.data_manager)
                tab_text = f"{icon} {tab_name}"
                self.tab_widget.addTab(widget, tab_text)
                self.modules[tab_name] = widget
                
                if hasattr(widget, 'on_theme_changed'):
                    self.theme_manager.theme_changed.connect(widget.on_theme_changed)
                    
                print(f"✅ {tab_name} 模块加载成功")
                    
            except Exception as e:
                print(f"❌ 创建 {tab_name} 标签页失败: {e}")
                traceback.print_exc()
                error_widget = ModuleLoader.create_error_widget(f"{tab_name} 加载失败", str(e))
                self.tab_widget.addTab(error_widget, f"{icon} {tab_name}")
    
    def setup_menu(self):
        """设置菜单"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("📁 文件")
        
        backup_action = QAction("💾 备份数据", self)
        backup_action.triggered.connect(self.backup_data)
        file_menu.addAction(backup_action)
        
        refresh_action = QAction("🔄 刷新所有模块", self)
        refresh_action.triggered.connect(self.refresh_all_modules)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("🚪 退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 主题菜单
        self.setup_theme_menu(menubar)
        
        # 帮助菜单
        help_menu = menubar.addMenu("❓ 帮助")
        about_action = QAction("ℹ️ 关于 Tofu", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # 调试菜单 (开发用)
        debug_menu = menubar.addMenu("🐛 调试")
        debug_data_action = QAction("📊 显示数据状态", self)
        debug_data_action.triggered.connect(self.show_data_status)
        debug_menu.addAction(debug_data_action)
    
    def setup_theme_menu(self, menubar):
        """设置主题菜单"""
        theme_menu = menubar.addMenu("🎨 主题")
        
        theme_names = self.theme_manager.get_theme_names()
        for theme_name in theme_names:
            theme_action = QAction(f"{self.get_theme_icon(theme_name)} {theme_name.capitalize()}主题", self)
            theme_action.triggered.connect(
                lambda checked, name=theme_name: self.theme_manager.set_theme(name)
            )
            theme_menu.addAction(theme_action)
    
    def setup_status_bar(self):
        """设置状态栏"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # 欢迎消息
        welcome_label = QLabel("Tofu - 您的个人生产力助手")
        status_bar.addWidget(welcome_label)
        
        # 主题信息
        status_bar.addPermanentWidget(QLabel(" | "))
        self.theme_label = QLabel(f"主题: {self.theme_manager.current_theme.capitalize()}")
        status_bar.addPermanentWidget(self.theme_label)
        
        # 数据管理器状态
        status_bar.addPermanentWidget(QLabel(" | "))
        self.data_status_label = QLabel("数据: 单例模式")
        status_bar.addPermanentWidget(self.data_status_label)
        
        # 时间显示
        status_bar.addPermanentWidget(QLabel(" | "))
        self.time_label = QLabel()
        status_bar.addPermanentWidget(self.time_label)
        
        # 启动时间更新
        self.update_time()
        self.time_timer = QTimer(self)
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
    
    def load_settings(self):
        """加载设置"""
        settings = self.data_manager.get_settings()
        saved_theme = settings.get("theme", "light")
        self.theme_manager.set_theme(saved_theme)
        
        # 应用字体设置
        self.setup_fonts()
        
        print("✅ 设置加载完成")
    
    def setup_fonts(self):
        """设置字体"""
        app_font = QFont("Microsoft YaHei", 10)
        QApplication.setFont(app_font)
        
        title_font = QFont("Microsoft YaHei", 12, QFont.Bold)
        self.tab_widget.setFont(title_font)
    
    def get_theme_icon(self, theme_name):
        """获取主题图标"""
        icons = {"light": "☀️", "dark": "🌙", "blue": "🔵"}
        return icons.get(theme_name, "🎨")
    
    def apply_theme(self, theme_name):
        """应用主题"""
        self.setStyleSheet(self.theme_manager.get_theme())
        self.theme_label.setText(f"主题: {theme_name.capitalize()}")
        
        # 保存主题设置
        settings = self.data_manager.get_settings()
        settings["theme"] = theme_name
        self.data_manager.update_settings(settings)
        
        print(f"✅ 主题已切换为: {theme_name}")
    
    def update_time(self):
        """更新状态栏时间"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(current_time)
    
    def on_tab_changed(self, index):
        """标签页切换事件"""
        if index >= 0:
            tab_name = self.tab_widget.tabText(index)
            self.statusBar().showMessage(f"当前标签页: {tab_name}", 3000)
            
            # 通知模块激活（如果模块支持）
            widget = self.tab_widget.widget(index)
            if hasattr(widget, 'on_activate'):
                widget.on_activate()
    
    def refresh_all_modules(self):
        """刷新所有模块"""
        refresh_count = 0
        for module_name, widget in self.modules.items():
            if hasattr(widget, 'refresh'):
                try:
                    widget.refresh()
                    print(f"✅ {module_name} 刷新完成")
                    refresh_count += 1
                except Exception as e:
                    print(f"❌ {module_name} 刷新失败: {e}")
        
        QMessageBox.information(self, "刷新完成", f"已刷新 {refresh_count} 个模块")
    
    def backup_data(self):
        """备份数据"""
        from resource_helper import backup_data_file
        if backup_data_file():
            QMessageBox.information(self, "备份成功", "数据备份已完成")
        else:
            QMessageBox.warning(self, "备份失败", "数据备份失败，请检查文件权限")
    
    def show_about(self):
        """显示关于信息"""
        about_text = """Tofu - 个人生产力工具
v0.1.3 (2025-12-04)
© 2025 杜孝双 · 独立开发者
邮件：virmuran@163.com
——
采用模块化设计，所有数据保存在本地JSON文件中。
使用单例数据管理器，避免数据冲突。"""
        QMessageBox.about(self, "关于 Tofu", about_text)
    
    def show_data_status(self):
        """显示数据状态 (调试用)"""
        try:
            data_file = self.data_manager.data_file
            file_exists = os.path.exists(data_file)
            file_size = os.path.getsize(data_file) if file_exists else 0
            
            project_info = self.data_manager.get_project_info()
            report_counter = self.data_manager.get_report_counter()
            
            status_text = f"""数据文件状态:
位置: {data_file}
存在: {'是' if file_exists else '否'}
大小: {file_size} 字节

项目信息: {project_info}
报告计数器: {report_counter}

数据管理器实例 ID: {id(self.data_manager)}"""
            
            QMessageBox.information(self, "数据状态", status_text)
        except Exception as e:
            QMessageBox.warning(self, "数据状态错误", f"获取数据状态失败: {e}")
    
    def closeEvent(self, event):
        """关闭应用程序事件处理"""
        print("🔄 正在关闭应用程序...")
        
        # 停止所有计时器
        if hasattr(self, 'time_timer'):
            self.time_timer.stop()
        
        # 保存所有模块数据
        for module_name, widget in self.modules.items():
            if hasattr(widget, 'save_data'):
                try:
                    widget.save_data()
                    print(f"✅ {module_name} 数据保存完成")
                except Exception as e:
                    print(f"❌ 保存 {module_name} 数据失败: {e}")
        
        # 保存主数据
        try:
            self.data_manager._save_data()
            print("✅ 主数据保存完成")
        except Exception as e:
            print(f"❌ 主数据保存失败: {e}")
        
        print("👋 应用程序关闭完成")
        event.accept()

def main():
    """应用程序入口点"""
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("Tofu")
    app.setApplicationVersion("2.1")
    app.setOrganizationName("TofuSoft")
    
    try:
        print("🚀 启动 Tofu 应用程序...")
        window = TofuApp()
        window.show()
        window.center_window()
        print("✅ 应用程序启动成功")
        return app.exec()
    except Exception as e:
        print(f"❌ 应用程序启动失败: {e}")
        traceback.print_exc()
        QMessageBox.critical(None, "启动失败", f"应用程序启动失败:\n{str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())