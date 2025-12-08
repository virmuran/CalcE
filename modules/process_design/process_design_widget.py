# modules/process_design/process_design_widget.py
import sys
import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel,
    QPushButton, QMessageBox, QTextEdit, QGroupBox, QFrame
)
from PySide6.QtCore import Qt

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

class ProcessDesignWidget(QWidget):
    """工艺设计主窗口部件"""
    
    def __init__(self, parent=None, data_manager=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.process_manager = None
        self.material_tab = None
        self.equipment_tab = None
        self.msds_tab = None
        
        # 延迟导入 process_design_manager
        try:
            from .process_design_manager import ProcessDesignManager
            if data_manager:
                self.process_manager = ProcessDesignManager(data_manager)
                print("✅ 成功创建 ProcessDesignManager")
        except Exception as e:
            print(f"❌ 创建 ProcessDesignManager 失败: {e}")
            self.process_manager = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
            
        # 标题
        title_label = QLabel("🏭 工艺设计系统")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
            
        # 标签页
        self.tab_widget = QTabWidget()

        # 使用包中提供的动态导入函数
        from . import import_material_database_tab, import_equipment_list_tab, import_msds_manager_tab
            
        # 物料数据库标签页
        try:
            MaterialDatabaseTab = import_material_database_tab()
            if MaterialDatabaseTab and self.data_manager:
                self.material_tab = MaterialDatabaseTab(self.data_manager)
                self.tab_widget.addTab(self.material_tab, "🧪 物料数据库")
                print("✅ 物料数据库标签页创建成功")
            else:
                self.create_error_tab("物料数据库", "数据管理器未初始化或模块加载失败")
        except Exception as e:
            print(f"❌ 创建物料数据库标签页失败: {e}")
            self.create_error_tab("物料数据库", f"创建失败: {str(e)}")

        # MSDS 管理标签页 - 使用统一的动态导入模式
        try:
            MSDSManagerTab = import_msds_manager_tab()
            if MSDSManagerTab and self.data_manager:
                self.msds_tab = MSDSManagerTab(self.data_manager)
                self.tab_widget.addTab(self.msds_tab, "📄 MSDS 管理")
                print("✅ MSDS 管理标签页创建成功")
            else:
                self.create_error_tab("MSDS 管理", "数据管理器未初始化或模块加载失败")
        except Exception as e:
            print(f"❌ 创建 MSDS 管理标签页失败: {e}")
            self.create_error_tab("MSDS 管理", f"创建失败: {str(e)}")
            
        # 设备清单标签页
        try:
            EquipmentListTab = import_equipment_list_tab()
            if EquipmentListTab and self.data_manager:
                self.equipment_tab = EquipmentListTab(self.data_manager)
                self.tab_widget.addTab(self.equipment_tab, "⚙️ 设备清单")
                print("✅ 设备清单标签页创建成功")
            else:
                self.create_error_tab("设备清单", "数据管理器未初始化或模块加载失败")
        except Exception as e:
            print(f"❌ 创建设备清单标签页失败: {e}")
            self.create_error_tab("设备清单", f"创建失败: {str(e)}")

        # 添加更多标签页（未来扩展）
        # 项目设计标签页
        project_widget = self.create_project_design_tab()
        self.tab_widget.addTab(project_widget, "📋 项目设计")
        
        # 计算工具标签页
        calculator_widget = self.create_calculator_tab()
        self.tab_widget.addTab(calculator_widget, "🧮 计算工具")
        
        layout.addWidget(self.tab_widget)
        
        # 底部信息栏
        info_layout = QHBoxLayout()
        info_label = QLabel("工艺设计系统 v1.0.0")
        info_label.setStyleSheet("color: gray; font-size: 10px;")
        info_layout.addWidget(info_label)
        info_layout.addStretch()
        
        refresh_btn = QPushButton("🔄 刷新")
        refresh_btn.clicked.connect(self.refresh_data)
        info_layout.addWidget(refresh_btn)
        
        layout.addLayout(info_layout)
    
    def create_error_tab(self, tab_name, error_message):
        """创建错误标签页"""
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
    
    def create_project_design_tab(self):
        """创建项目设计标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 标题
        title = QLabel("📋 项目设计")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(title)
        
        # 项目信息框
        info_group = QGroupBox("项目信息")
        info_layout = QVBoxLayout(info_group)
        
        # 项目ID
        id_frame = QFrame()
        id_layout = QHBoxLayout(id_frame)
        id_label = QLabel("项目ID:")
        id_input = QLabel("PD-2024-001")
        id_input.setStyleSheet("background-color: #f0f0f0; padding: 5px; border-radius: 3px;")
        id_layout.addWidget(id_label)
        id_layout.addWidget(id_input)
        id_layout.addStretch()
        info_layout.addWidget(id_frame)
        
        # 项目名称
        name_frame = QFrame()
        name_layout = QHBoxLayout(name_frame)
        name_label = QLabel("项目名称:")
        name_input = QLabel("年产10万吨甲醇项目")
        name_input.setStyleSheet("background-color: #f0f0f0; padding: 5px; border-radius: 3px;")
        name_layout.addWidget(name_label)
        name_layout.addWidget(name_input)
        name_layout.addStretch()
        info_layout.addWidget(name_frame)
        
        # 设计能力
        capacity_frame = QFrame()
        capacity_layout = QHBoxLayout(capacity_frame)
        capacity_label = QLabel("设计能力:")
        capacity_input = QLabel("100,000 吨/年")
        capacity_input.setStyleSheet("background-color: #f0f0f0; padding: 5px; border-radius: 3px;")
        capacity_layout.addWidget(capacity_label)
        capacity_layout.addWidget(capacity_input)
        capacity_layout.addStretch()
        info_layout.addWidget(capacity_frame)
        
        layout.addWidget(info_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        new_project_btn = QPushButton("新建项目")
        new_project_btn.setStyleSheet("padding: 8px 15px;")
        button_layout.addWidget(new_project_btn)
        
        open_project_btn = QPushButton("打开项目")
        open_project_btn.setStyleSheet("padding: 8px 15px;")
        button_layout.addWidget(open_project_btn)
        
        layout.addLayout(button_layout)
        
        layout.addStretch()
        return widget
    
    def create_equipment_tab(self):
        """创建设备清单标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 标题
        title = QLabel("⚙️ 设备清单")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(title)
        
        # 设备列表
        list_group = QGroupBox("设备列表")
        list_layout = QVBoxLayout(list_group)
        
        # 示例设备
        devices = [
            ("R-101", "反应器", "不锈钢反应釜", "10 m³"),
            ("C-101", "塔器", "精馏塔", "Ø1.2m × 15m"),
            ("P-101", "泵", "离心泵", "50 m³/h"),
            ("T-101", "储罐", "原料储罐", "100 m³"),
        ]
        
        for tag, name, type_, capacity in devices:
            device_frame = QFrame()
            device_frame.setFrameStyle(QFrame.StyledPanel)
            device_layout = QHBoxLayout(device_frame)
            
            tag_label = QLabel(f"<b>{tag}</b>")
            tag_label.setMinimumWidth(60)
            device_layout.addWidget(tag_label)
            
            info_label = QLabel(f"{name} ({type_}) - {capacity}")
            device_layout.addWidget(info_label)
            
            device_layout.addStretch()
            
            edit_btn = QPushButton("编辑")
            edit_btn.setFixedWidth(60)
            device_layout.addWidget(edit_btn)
            
            list_layout.addWidget(device_frame)
        
        layout.addWidget(list_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        add_device_btn = QPushButton("添加设备")
        add_device_btn.setStyleSheet("padding: 8px 15px;")
        button_layout.addWidget(add_device_btn)
        
        import_btn = QPushButton("导入清单")
        import_btn.setStyleSheet("padding: 8px 15px;")
        button_layout.addWidget(import_btn)
        
        layout.addLayout(button_layout)
        
        layout.addStretch()
        return widget
    
    def create_calculator_tab(self):
        """创建计算工具标签页"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 标题
        title = QLabel("🧮 计算工具")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px 0;")
        layout.addWidget(title)
        
        # 工具列表
        tools_group = QGroupBox("可用工具")
        tools_layout = QVBoxLayout(tools_group)
        
        tools = [
            ("物料衡算", "计算物料输入输出平衡"),
            ("能量衡算", "计算能量输入输出平衡"),
            ("设备选型", "根据工艺参数选择设备"),
            ("管道计算", "计算管道尺寸和压降"),
            ("成本估算", "估算项目投资成本"),
        ]
        
        for tool_name, description in tools:
            tool_frame = QFrame()
            tool_frame.setFrameStyle(QFrame.StyledPanel)
            tool_layout = QHBoxLayout(tool_frame)
            
            name_label = QLabel(f"<b>{tool_name}</b>")
            name_label.setMinimumWidth(100)
            tool_layout.addWidget(name_label)
            
            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: #666;")
            tool_layout.addWidget(desc_label)
            
            tool_layout.addStretch()
            
            open_btn = QPushButton("打开")
            open_btn.setFixedWidth(60)
            tool_layout.addWidget(open_btn)
            
            tools_layout.addWidget(tool_frame)
        
        layout.addWidget(tools_group)
        
        # 快速计算
        quick_group = QGroupBox("快速计算")
        quick_layout = QVBoxLayout(quick_group)
        
        # 示例：单位换算
        conv_frame = QFrame()
        conv_layout = QHBoxLayout(conv_frame)
        conv_label = QLabel("单位换算:")
        conv_layout.addWidget(conv_label)
        
        conv_input = QLabel("100 kg/h = 2.78e-2 kg/s")
        conv_input.setStyleSheet("background-color: #f0f0f0; padding: 5px; border-radius: 3px;")
        conv_layout.addWidget(conv_input)
        
        conv_layout.addStretch()
        quick_layout.addWidget(conv_frame)
        
        layout.addWidget(quick_group)
        
        layout.addStretch()
        return widget
    
    def refresh_data(self):
        """刷新数据"""
        try:
            if self.process_manager:
                # 重新初始化管理器
                from .process_design_manager import ProcessDesignManager
                self.process_manager = ProcessDesignManager(self.data_manager)
                
                # 通知物料标签页刷新（如果存在）
                if hasattr(self, 'material_tab') and self.material_tab:
                    self.material_tab.load_materials()
                
                QMessageBox.information(self, "刷新完成", "工艺设计数据已刷新")
            else:
                QMessageBox.warning(self, "刷新失败", "数据管理器未初始化")
        except Exception as e:
            QMessageBox.critical(self, "刷新失败", f"刷新数据时发生错误:\n{str(e)}")
    
    def save_data(self):
        """保存数据"""
        try:
            if self.data_manager:
                self.data_manager._save_data()
                return True
        except Exception as e:
            print(f"保存数据失败: {e}")
            return False
    
    def on_theme_changed(self, theme_name):
        """主题变化处理"""
        # 这里可以添加主题相关的处理
        pass
    
    def on_activate(self):
        """模块激活时调用"""
        print("✅ 工艺设计模块已激活")
        
        # 刷新物料数据
        if hasattr(self, 'material_tab') and self.material_tab:
            try:
                self.material_tab.load_materials()
            except Exception as e:
                print(f"刷新物料数据失败: {e}")