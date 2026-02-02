# CalcE/main.py
import sys
import os
import traceback
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

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
    QMessageBox, QMenuBar, QMenu, QStatusBar, QLabel, QDialog,
    QScrollArea, QPushButton, QTextEdit, QHBoxLayout
)
from PySide6.QtCore import Qt, QTimer, Signal, QUrl
from PySide6.QtGui import QAction, QFont, QDesktopServices
from datetime import datetime

try:
    from data_manager import DataManager
    from theme_manager import ThemeManager
    from module_loader import ModuleLoader
except ImportError as e:
    print(f"导入模块失败: {e}")
    traceback.print_exc()
    print("尝试继续运行程序...")

class CalcE(QMainWindow):
    """CalcE主应用程序"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CalcE - 个人生产力工具")
        self.setGeometry(160, 50, 1600, 970)
        
        # 初始化管理器
        self.theme_manager = ThemeManager()
        self.data_manager = DataManager.get_instance()
        
        # 存储模块实例
        self.modules = {}
        
        # 创建UI
        self.setup_ui()
        
        # 加载设置
        self.load_settings()
    
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
                    
            except Exception as e:
                print(f"❌ 创建 {tab_name} 标签页失败: {e}")
                traceback.print_exc()
                error_widget = ModuleLoader.create_error_widget(f"{tab_name} 加载失败", str(e))
                self.tab_widget.addTab(error_widget, f"{icon} {tab_name}")
    
    def create_error_tab(self, tab_name, error_message):
        """创建错误标签页"""
        from PySide6.QtWidgets import QLabel
        error_widget = QWidget()
        error_layout = QVBoxLayout(error_widget)
        error_layout.setAlignment(Qt.AlignCenter)
        
        error_label = QLabel(f"{tab_name} 加载失败")
        error_label.setStyleSheet("color: red; font-weight: bold; font-size: 14px;")
        error_layout.addWidget(error_label)
        
        detail_label = QLabel(error_message)
        detail_label.setStyleSheet("color: #666; font-size: 12px;")
        detail_label.setWordWrap(True)
        error_layout.addWidget(detail_label)
        
        self.tab_widget.addTab(error_widget, f"❌ {tab_name}")
    
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
        self.setup_help_menu(menubar)
    
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
    
    def setup_help_menu(self, menubar):
        """设置帮助菜单"""
        help_menu = menubar.addMenu("❓ 帮助")
        
        # 用户手册
        manual_action = QAction("📖 用户手册", self)
        manual_action.triggered.connect(self.show_user_manual)
        help_menu.addAction(manual_action)

        # 常见问题
        faq_action = QAction("❓ 常见问题", self)
        faq_action.triggered.connect(self.show_faq)
        help_menu.addAction(faq_action)

        # 系统信息
        sysinfo_action = QAction("🖥️ 系统信息", self)
        sysinfo_action.triggered.connect(self.show_system_info)
        help_menu.addAction(sysinfo_action)
        
        # 查看日志
        log_action = QAction("📋 查看日志", self)
        log_action.triggered.connect(self.show_logs)
        help_menu.addAction(log_action)

        # 开源许可
        license_action = QAction("📄 开源许可", self)
        license_action.triggered.connect(self.show_license)
        help_menu.addAction(license_action)
        
        # 关于软件
        about_action = QAction("ℹ️ 关于 CalcE", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """设置状态栏"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # 欢迎消息
        welcome_label = QLabel("CalcE - 您的个人生产力助手")
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
    
    def show_user_manual(self):
        """显示用户手册"""
        manual_text = """<h2>📖 CalcE 用户手册</h2>
<h3>欢迎使用 CalcE 个人生产力工具！</h3><br>

<b>📋 快速入门指南：</b><br>
1. <b>主界面介绍：</b><br>
   • 顶部菜单栏：文件、主题、帮助等功能入口<br>
   • 标签页区域：各功能模块的切换区域<br>
   • 状态栏：显示时间、主题和系统状态<br><br>

2. <b>功能模块使用：</b><br>
   • 点击标签页图标切换到不同功能模块<br>
   • 每个模块都有独立的操作界面<br>
   • 数据自动保存，无需手动操作<br><br>

3. <b>基本操作：</b><br>
   • 点击右键可显示上下文菜单<br>
   • 使用快捷键提高操作效率<br>
   • 定期使用"备份数据"功能保护数据<br><br>

<b>🔧 模块详细介绍：</b><br>

<b>1. 工程计算 (🔬)</b><br>
   • 提供化工、工程相关计算工具<br>
   • 支持公式计算和单位转换<br>
   • 可保存常用计算模板<br><br>

<b>2. 换算器 (📐)</b><br>
   • 支持长度、重量、温度等单位换算<br>
   • 实时计算，即时显示结果<br>
   • 可自定义常用换算类型<br><br>

<b>3. 番茄时钟 (🍅)</b><br>
   • 标准番茄工作法：25分钟工作+5分钟休息<br>
   • 可自定义工作时间<br>
   • 休息提醒和统计功能<br><br>

<b>4. 待办事项 (✅)</b><br>
   • 添加、编辑、删除任务<br>
   • 设置任务优先级和截止日期<br>
   • 任务完成状态跟踪<br><br>

<b>5. 笔记 (📝)</b><br>
   • 富文本笔记编辑<br>
   • 笔记分类管理<br>
   • 搜索和筛选功能<br><br>

<b>6. 书签 (🔖)</b><br>
   • 网页链接管理<br>
   • 快速访问常用网站<br>
   • 分类整理功能<br><br>

<b>7. 重要日期 (📅)</b><br>
   • 记录生日、纪念日等<br>
   • 提前提醒设置<br>
   • 倒计时显示<br><br>

<b>8. 倒计时 (⏰)</b><br>
   • 创建多个倒计时事件<br>
   • 自定义事件名称和时间<br>
   • 实时更新显示<br><br>

<b>9. 今年余额 (📊)</b><br>
   • 显示一年已过和剩余时间<br>
   • 百分比进度显示<br>
   • 每日更新<br><br>

<b>⚙️ 设置与个性化：</b><br>
1. <b>主题切换：</b><br>
   • 在"主题"菜单中选择亮色、暗色或蓝色主题<br>
   • 主题设置会自动保存<br><br>

2. <b>数据管理：</b><br>
   • 所有数据保存在用户目录下的 .calce 文件夹中<br>
   • 定期备份防止数据丢失<br>
   • 支持数据导入导出（开发中）<br><br>

<b>🔐 数据安全：</b><br>
• 所有数据仅存储在本地<br>
• 不会上传任何用户数据到服务器<br>
• 备份文件加密存储<br><br>

<b>❓ 获取帮助：</b><br>
• 查看本用户手册<br>
• 参考常见问题解答<br>
• 联系开发者反馈问题<br><br>

<b>📞 联系方式：</b><br>
如有问题或建议，请联系：<br>
邮箱：virmuran@163.com<br><br>

<b>💡 小贴士：</b><br>
• 使用快捷键提高工作效率<br>
• 定期备份重要数据<br>
• 关注更新获取新功能<br>"""
        
        self.show_scrollable_dialog("用户手册", manual_text)

    def show_faq(self):
        """显示常见问题"""
        faq_text = """<h2>❓ CalcE 常见问题解答</h2><br>

<b>🔧 安装与启动：</b><br>

<b>Q1: 如何安装 CalcE？</b><br>
A: CalcE 是便携式应用程序，无需安装。只需解压下载的压缩包，双击运行主程序即可。<br><br>

<b>Q2: 启动时提示"模块加载失败"怎么办？</b><br>
A: 请确保所有文件都在同一目录下，不要移动或删除任何文件。如果问题持续，请重新下载完整版本。<br><br>

<b>Q3: 支持哪些操作系统？</b><br>
A: 支持 Windows 10/11，未来计划支持 macOS 和 Linux。<br><br>

<b>💾 数据与存储：</b><br>

<b>Q4: 数据存储在哪里？</b><br>
A: 所有数据保存在用户目录下的 .calce 文件夹中：<br>
   • Windows: C:\\Users\\[用户名]\\.calce\\<br>
   • 可在设置中修改数据存储位置<br><br>

<b>Q5: 如何备份数据？</b><br>
A: 点击菜单栏"文件"→"备份数据"，或使用快捷键 Ctrl+B。备份文件会保存到指定位置。<br><br>

<b>Q6: 数据会同步到云端吗？</b><br>
A: 当前版本不支持云端同步。所有数据仅存储在本地，确保隐私安全。<br><br>

<b>Q7: 如何恢复备份的数据？</b><br>
A: 将备份的 JSON 文件复制到数据目录覆盖原文件，然后重启应用程序。<br><br>

<b>⚙️ 功能使用：</b><br>

<b>Q8: 为什么番茄时钟不提醒？</b><br>
A: 请检查系统通知设置，确保 CalcE 有显示通知的权限。同时检查系统音量是否开启。<br><br>

<b>Q9: 如何添加自定义换算单位？</b><br>
A: 当前版本支持预设单位换算，自定义单位功能将在后续版本中添加。<br><br>

<b>Q10: 待办事项能设置重复任务吗？</b><br>
A: 当前版本支持单次任务，重复任务功能正在开发中。<br><br>

<b>Q11: 笔记支持图片插入吗？</b><br>
A: 当前版本支持纯文本和基本格式，图片插入功能将在后续版本中添加。<br><br>

<b>🎨 外观与主题：</b><br>

<b>Q12: 如何切换主题？</b><br>
A: 点击菜单栏"主题"，选择喜欢的主题样式。支持亮色、暗色和蓝色主题。<br><br>

<b>Q13: 能自定义界面字体吗？</b><br>
A: 当前使用系统默认字体，自定义字体功能将在后续版本中添加。<br><br>

<b>Q14: 界面布局能调整吗？</b><br>
A: 当前为固定布局，可调整窗口大小。自定义布局功能正在规划中。<br><br>

<b>🔐 安全与隐私：</b><br>

<b>Q15: CalcE 安全吗？会收集我的数据吗？</b><br>
A: CalcE 完全安全：<br>
   • 所有数据本地存储<br>
   • 不收集任何用户信息<br>
   • 不开设网络连接<br>
   • 代码开源可审查<br><br>

<b>Q16: 如何确保数据不丢失？</b><br>
A: 建议：<br>
   • 定期使用备份功能<br>
   • 不要手动修改数据文件<br>
   • 避免在多个设备间直接复制文件<br><br>

<b>🔄 更新与维护：</b><br>

<b>Q17: 如何更新到最新版本？</b><br>
A: 访问官网或GitHub页面下载最新版本，覆盖安装即可。数据会自动迁移。<br><br>

<b>Q18: 更新会丢失数据吗？</b><br>
A: 正常情况下不会。但强烈建议更新前备份数据。<br><br>

<b>Q19: 更新频率是多久？</b><br>
A: 不定时更新，紧急修复会随时发布。<br><br>

<b>📞 支持与反馈：</b><br>

<b>Q20: 遇到问题如何反馈？</b><br>
A: 可以通过以下方式：<br>
   • 邮件：virmuran@163.com<br>

<b>Q21: 会开发移动版吗？</b><br>
A: 暂时不会。<br><br>

<b>Q22: 能请求新功能吗？</b><br>
A: 欢迎提出建议！通过反馈渠道发送您的想法，我们会认真考虑。<br><br>

<b>💰 收费与授权：</b><br>

<b>Q23: CalcE 收费吗？</b><br>
A: 完全免费！没有任何收费计划。<br><br>

<b>Q24: 能用于商业用途吗？</b><br>
A: 个人和商业用途均可，但需遵守开源协议。<br><br>

<b>🔧 故障排除：</b><br>

<b>Q25: 程序卡顿怎么办？</b><br>
A: 尝试以下方法：<br>
   • 重启应用程序<br>
   • 清理不必要的数据<br>
   • 确保有足够的内存<br><br>

<b>Q26: 界面显示异常怎么办？</b><br>
A: 尝试切换主题或重启程序。如果问题持续，请反馈给开发者。<br><br>

<b>Q27: 数据损坏了怎么办？</b><br>
A: 使用最近的备份文件恢复。如果没有备份，可能无法恢复数据。<br><br>

<b>💡 使用技巧：</b><br>
• 使用快捷键提高效率<br>
• 定期备份重要数据<br>
• 关注更新获取新功能<br>
• 参与社区讨论分享经验<br><br>

<b>📢 最后提醒：</b><br>
请从官方渠道下载 CalcE，确保安全！"""
        
        self.show_scrollable_dialog("常见问题", faq_text)

    def copy_to_clipboard(self, text):
        """复制文本到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        QMessageBox.information(self, "复制成功", f"已复制到剪贴板：\n{text}")
    
    def show_system_info(self):
        """显示系统信息"""
        import platform
        import psutil
        
        try:
            # 获取系统信息
            system_info = f"""
<b>🖥️ 系统信息</b><br><br>

<b>操作系统：</b><br>
• 系统：{platform.system()} {platform.release()}<br>
• 版本：{platform.version()}<br>
• 架构：{platform.machine()}<br><br>

<b>Python 环境：</b><br>
• Python 版本：{platform.python_version()}<br>
• Python 实现：{platform.python_implementation()}<br>
• 编译器：{platform.python_compiler()}<br><br>

<b>硬件信息：</b><br>
• 处理器：{platform.processor()}<br>
• 物理内存：{psutil.virtual_memory().total / (1024**3):.1f} GB<br>
• 可用内存：{psutil.virtual_memory().available / (1024**3):.1f} GB<br>
• 内存使用率：{psutil.virtual_memory().percent}%<br><br>

<b>CalcE 信息：</b><br>
• 版本：v1.0.20260131<br>
• 数据目录：{os.path.expanduser('~/.calce')}<br>
• 运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
• 标签页数量：{self.tab_widget.count()}<br>
• 加载模块：{len(self.modules)} 个<br><br>

<b>💾 存储信息：</b><br>
"""
            
            # 获取数据文件信息
            data_file = self.data_manager.data_file
            if os.path.exists(data_file):
                file_size = os.path.getsize(data_file)
                file_time = datetime.fromtimestamp(os.path.getmtime(data_file)).strftime('%Y-%m-%d %H:%M:%S')
                
                system_info += f"""• 数据文件：{data_file}<br>
• 文件大小：{file_size} 字节 ({file_size/1024:.1f} KB)<br>
• 最后修改：{file_time}<br><br>"""
            
            # 获取磁盘信息
            try:
                disk_usage = psutil.disk_usage(os.path.expanduser('~'))
                system_info += f"""<b>磁盘使用：</b><br>
• 总容量：{disk_usage.total / (1024**3):.1f} GB<br>
• 已使用：{disk_usage.used / (1024**3):.1f} GB<br>
• 可用空间：{disk_usage.free / (1024**3):.1f} GB<br>
• 使用率：{disk_usage.percent}%<br><br>"""
            except:
                system_info += "<b>磁盘信息获取失败</b><br><br>"
            
            self.show_scrollable_dialog("系统信息", system_info)
            
        except Exception as e:
            QMessageBox.warning(self, "系统信息错误", f"获取系统信息失败：{str(e)}")
    
    def show_logs(self):
        """查看日志"""
        # 这里可以添加实际的日志查看逻辑
        log_text = """<h2>📋 日志信息</h2><br>

<b>当前版本：</b> v1.0.20260131<br>
<b>启动时间：</b> {start_time}<br>
<b>运行时长：</b> {running_time}<br><br>

<b>模块加载状态：</b><br>
• 工程计算：✓ 已加载<br>
• 换算器：✓ 已加载<br>
• 番茄时钟：✓ 已加载<br>
• 待办事项：✓ 已加载<br>
• 笔记：✓ 已加载<br>
• 书签：✓ 已加载<br>
• 重要日期：✓ 已加载<br>
• 倒计时：✓ 已加载<br>
• 今年余额：✓ 已加载<br><br>

<b>数据状态：</b><br>
• 数据文件：正常<br>
• 备份文件：正常<br>
• 设置文件：正常<br><br>

<b>最近操作：</b><br>
• 应用启动成功<br>
• 主题已加载：{theme}<br>
• 所有模块初始化完成<br><br>

<b>错误日志：</b><br>
• 无错误记录<br><br>

<b>💡 日志说明：</b><br>
1. 详细日志记录在用户目录的 .calce/logs 文件夹中<br>
2. 日志文件每日轮转，保留最近7天<br>
3. 日志仅用于故障诊断，不包含敏感信息<br><br>

<b>🛠️ 日志管理：</b><br>
• 点击"清理日志"可删除历史日志文件<br>
• 日志文件采用纯文本格式，可用任何文本编辑器查看<br>
• 日志文件会自动压缩以节省空间<br><br>""".format(
    start_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    running_time="0分钟",
    theme=self.theme_manager.current_theme.capitalize()
)
        
        self.show_scrollable_dialog("查看日志", log_text)
    
    def show_license(self):
        """显示开源许可"""
        # 根据实际情况修改以下部分
        your_name = "CalcE Team"  # 修改这里
        your_email = "virmuran@163.com"  # 修改这里
        current_year = "2025"  # 修改为项目开始年份或当前年份
        project_name = "CalcE"  # 项目名称
        
        license_text = f"""<h2>📄 开源许可协议</h2><br>

<b>{project_name} - MIT License</b><br><br>

Copyright © {current_year} {your_name}<br><br>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:<br><br>

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.<br><br>

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.<br><br>

<b>📦 使用的第三方库及其许可证：</b><br>
• PySide6 - LGPLv3 License (https://doc.qt.io/qt-6/licensing.html)<br>
• psutil - BSD-3-Clause License (https://github.com/giampaolo/psutil)<br>
• 其他依赖请查看项目根目录下的requirements.txt文件<br><br>

<b>⚠️ 重要注意事项：</b><br>
1. 本软件基于LGPLv3许可的PySide6库构建<br>
2. 用户有权获取、修改和替换PySide6库<br>
3. 本软件的源代码可在[https://github.com/virmuran/CalcE.git]获取<br><br>

<b>⚖️ 许可条款摘要：</b><br>
1. <b>允许</b>：商业使用、修改、分发、私人使用<br>
2. <b>要求</b>：包含原始许可声明和版权声明<br>
3. <b>禁止</b>：使用作者商标、作者担保、作者责任<br>
4. <b>责任</b>：作者不承担任何直接或间接责任<br><br>

<b>🔗 完整协议：</b><br>
完整MIT许可证文本可在以下位置找到：<br>
• 软件包中的 LICENSE 文件<br>
• https://opensource.org/licenses/MIT<br><br>

<b>🤝 贡献者协议：</b><br>
向本项目贡献代码即表示您同意：<br>
• 您的贡献将使用MIT许可证授权<br>
• 您拥有贡献代码的合法权利<br>
• 您的贡献不会侵犯第三方权利<br><br>

<b>📝 免责声明：</b><br>
1. 本软件按"原样"提供，不作任何明示或暗示的保证<br>
2. 用户需自行承担使用风险<br>
3. 建议在使用前备份重要数据<br><br>

<b>🌍 开源承诺：</b><br>
• 核心代码保持开源<br>
• 接受社区贡献<br>
• 尊重开源精神<br><br>

<b>📧 联系信息：</b><br>
如有许可证相关问题，请联系：<br>
邮箱：{your_email}<br><br>

<b>📅 最后更新：</b>2026-01-31<br>"""
    
        self.show_scrollable_dialog("开源许可", license_text)
    
    def show_scrollable_dialog(self, title, content):
        """显示带滚动条的对话框"""
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        dialog.setMinimumSize(700, 500)
        
        # 创建主布局
        main_layout = QVBoxLayout(dialog)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 创建内容标签
        content_label = QLabel()
        content_label.setTextFormat(Qt.TextFormat.RichText)
        content_label.setText(content)
        content_label.setWordWrap(True)
        content_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        content_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        
        # 将标签添加到滚动区域
        scroll_area.setWidget(content_label)
        
        # 创建确定按钮
        button_box = QPushButton("确定")
        button_box.clicked.connect(dialog.accept)
        
        # 添加到布局
        main_layout.addWidget(scroll_area)
        main_layout.addWidget(button_box, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 显示对话框
        dialog.exec()
    
    def show_about(self):
        """显示关于信息"""
        about_text = """<h2>CalcE - 个人生产力工具</h2>
<h3>V1.1 稳定版</h3><br>
<b>版本信息：</b><br>
v1.1.20260202<br>
版权所有 © 2025 CalcE Team<br>
邮件：virmuran@163.com<br><br>

<b>关于作者：</b><br>
CalcE由独立开发者维护，致力于为用户提供简洁高效的个人生产力工具。<br><br>

<b>免责声明：</b><br>
本应用仅作学习用途，使用本应用造成的任何不良后果，本人概不负责。<br><br>

<b>核心功能：</b><br>
• 工程计算：化工、工程相关计算工具<br>
• 换算器：多种单位快速换算<br>
• 番茄时钟：科学的时间管理方法<br>
• 待办事项：高效管理您的日常任务<br>
• 笔记：随时记录重要信息<br>
• 重要日期：提醒重要日程安排<br>
• 倒计时：重要事件的倒计时提醒<br><br>

<b>数据安全承诺：</b><br>
1. 所有数据仅在本地存储，不会上传到任何服务器<br>
2. 不会收集用户的个人隐私信息<br>
3. 代码开源，欢迎审查<br>
4. 提供完整的备份和恢复功能<br><br>

<b>更新日志：</b><br><br>

<b>v1.1.20260202</b><br>
1. 修改帮助菜单<br>
2. 增加“水蒸气性质”模块<br><br>

<b>v1.0.20260131</b><br>
1. 初始版本发布<br><br>

<b>软件定位：</b><br>
CalcE致力于为用户提供轻量级、高效的个人生产力工具。我们相信好的工具应该简单易用，专注于提升用户的工作效率。通过模块化设计，CalcE可以在不增加复杂性的前提下，提供多种实用的功能。<br><br>

<b>温馨提示：</b><br>
• 定期备份数据以防丢失<br>
• 如有建议或问题，欢迎反馈"""
    
        self.show_scrollable_dialog("关于 CalcE", about_text)
    
    def closeEvent(self, event):
        """关闭应用程序事件处理"""
        
        # 停止所有计时器
        if hasattr(self, 'time_timer'):
            self.time_timer.stop()
        
        # 保存所有模块数据
        for module_name, widget in self.modules.items():
            if hasattr(widget, 'save_data'):
                try:
                    widget.save_data()
                except Exception as e:
                    print(f"❌ 保存 {module_name} 数据失败: {e}")
        
        # 保存主数据
        try:
            self.data_manager._save_data()
        except Exception as e:
            print(f"❌ 主数据保存失败: {e}")
        
        event.accept()

def main():
    """应用程序入口点"""
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("CalcE")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("CalcE")
    
    try:
        window = CalcE()
        window.show()
        return app.exec()
    except Exception as e:
        print(f"❌ 应用程序启动失败: {e}")
        traceback.print_exc()
        QMessageBox.critical(None, "启动失败", f"应用程序启动失败:\n{str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())