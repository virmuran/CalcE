# CalcE/modules/todo.py
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QListWidget, QComboBox, QMessageBox, QGroupBox, QScrollArea, QListWidgetItem,
    QFrame, QTextEdit
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QPalette, QIcon


class TodoManager(QWidget):
    """待办事项管理模块 (PySide6版本) - 现代化UI"""
    
    def __init__(self, parent=None, data_manager=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.todos = self.data_manager.get_todos()
        
        self.setup_ui()
        self.refresh_todo_list()
    
    def setup_ui(self):
        """设置待办事项UI - 现代化设计"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # 主框架 - 卡片式设计
        main_group = QGroupBox("📝 待办事项管理")
        main_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 12px;
                margin-top: 10px;
                padding-top: 10px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ffffff, stop:1 #f8f9fa);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #2c3e50;
            }
        """)
        main_layout.addWidget(main_group)
        
        group_layout = QVBoxLayout(main_group)
        group_layout.setSpacing(15)
        
        # 添加待办事项框架 - 现代化输入区域
        add_group = QGroupBox("➕ 添加新任务")
        add_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #f8f9fa;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
        """)
        group_layout.addWidget(add_group)
        
        add_layout = QVBoxLayout(add_group)
        
        # 标题输入
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("任务标题:"))
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("输入待办事项标题...")
        self.title_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        title_layout.addWidget(self.title_edit)
        add_layout.addLayout(title_layout)
        
        # 优先级和按钮
        control_layout = QHBoxLayout()
        
        control_layout.addWidget(QLabel("优先级:"))
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["🔴 高", "🟡 中", "🟢 低"])
        self.priority_combo.setCurrentText("🟡 中")
        self.priority_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 6px;
                font-size: 14px;
                background-color: white;
            }
            QComboBox:focus {
                border-color: #3498db;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        control_layout.addWidget(self.priority_combo)
        
        control_layout.addStretch()
        
        add_button = QPushButton("➕ 添加任务")
        add_button.setFont(QFont("Arial", 11, QFont.Bold))
        add_button.clicked.connect(self.add_todo)
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #219955;
            }
        """)
        control_layout.addWidget(add_button)
        
        add_layout.addLayout(control_layout)
        
        # 内容区域 - 左右分栏
        content_layout = QHBoxLayout()
        content_layout.setSpacing(15)
        
        # 左侧 - 待办事项列表
        left_frame = QFrame()
        left_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 8px;
            }
        """)
        left_layout = QVBoxLayout(left_frame)
        
        # 列表标题
        list_header = QLabel("📋 任务列表")
        list_header.setFont(QFont("Arial", 12, QFont.Bold))
        list_header.setStyleSheet("color: #2c3e50; padding: 5px;")
        left_layout.addWidget(list_header)
        
        # 待办事项列表
        self.todo_list = QListWidget()
        self.todo_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ecf0f1;
                border-radius: 6px;
                background-color: white;
                font-size: 14px;
            }
            QListWidget::item {
                border-bottom: 1px solid #ecf0f1;
                padding: 12px 8px;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
        """)
        self.todo_list.currentRowChanged.connect(self.on_todo_select)
        left_layout.addWidget(self.todo_list)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        toggle_button = QPushButton("✅ 切换完成状态")
        toggle_button.setFont(QFont("Arial", 10))
        toggle_button.clicked.connect(self.toggle_todo)
        toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        button_layout.addWidget(toggle_button)
        
        delete_button = QPushButton("🗑️ 删除")
        delete_button.setFont(QFont("Arial", 10))
        delete_button.clicked.connect(self.delete_todo)
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        button_layout.addWidget(delete_button)
        
        refresh_button = QPushButton("🔄 刷新")
        refresh_button.setFont(QFont("Arial", 10))
        refresh_button.clicked.connect(self.refresh_todo_list)
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        button_layout.addWidget(refresh_button)
        
        left_layout.addLayout(button_layout)
        content_layout.addWidget(left_frame, 1)  # 1表示可伸缩
        
        # 右侧 - 详细信息
        right_frame = QFrame()
        right_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 8px;
            }
        """)
        right_layout = QVBoxLayout(right_frame)
        
        # 详情标题
        details_header = QLabel("📄 任务详情")
        details_header.setFont(QFont("Arial", 12, QFont.Bold))
        details_header.setStyleSheet("color: #2c3e50; padding: 5px;")
        right_layout.addWidget(details_header)
        
        # 详细信息显示区域
        details_content = QFrame()
        details_content.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #ecf0f1;
                border-radius: 6px;
                padding: 15px;
            }
        """)
        details_content_layout = QVBoxLayout(details_content)
        
        self.details_label = QLabel("选择一个待办事项查看详情")
        self.details_label.setWordWrap(True)
        self.details_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.details_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        details_content_layout.addWidget(self.details_label)
        
        right_layout.addWidget(details_content)
        right_layout.addStretch()
        
        content_layout.addWidget(right_frame, 1)  # 1表示可伸缩
        group_layout.addLayout(content_layout)
        
        # 底部统计信息
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        stats_layout = QHBoxLayout(stats_frame)
        
        self.stats_label = QLabel("总任务: 0 | 已完成: 0 | 进行中: 0")
        self.stats_label.setFont(QFont("Arial", 11, QFont.Bold))
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_label.setStyleSheet("color: #ecf0f1;")
        stats_layout.addWidget(self.stats_label)
        
        group_layout.addWidget(stats_frame)
    
    def add_todo(self):
        """添加待办事项"""
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "警告", "⚠️ 请输入待办事项标题")
            return
        
        # 将带图标的优先级转换为英文
        priority_map = {"🔴 高": "high", "🟡 中": "medium", "🟢 低": "low"}
        priority_text = self.priority_combo.currentText()
        priority = priority_map.get(priority_text, "medium")
        
        self.data_manager.add_todo(title, "", priority)
        self.title_edit.clear()
        self.refresh_todo_list()
        
        # 显示成功消息
        QMessageBox.information(self, "成功", "✅ 任务添加成功！")
    
    def toggle_todo(self):
        """切换待办事项完成状态"""
        current_row = self.todo_list.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "警告", "⚠️ 请选择一个待办事项")
            return
        
        if current_row < len(self.todos):
            todo = self.todos[current_row]
            completed = not todo["completed"]
            self.data_manager.update_todo(todo["id"], completed=completed)
            self.refresh_todo_list()
            
            status = "完成" if completed else "未完成"
            QMessageBox.information(self, "状态更新", f"✅ 任务标记为{status}！")
    
    def delete_todo(self):
        """删除待办事项"""
        current_row = self.todo_list.currentRow()
        if current_row == -1:
            QMessageBox.warning(self, "警告", "⚠️ 请选择一个待办事项")
            return
        
        if current_row < len(self.todos):
            todo = self.todos[current_row]
            
            reply = QMessageBox.question(self, "确认删除", 
                                       f"确定要删除待办事项 '{todo['title']}' 吗？",
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.data_manager.delete_todo(todo["id"])
                self.refresh_todo_list()
                self.details_label.setText("选择一个待办事项查看详情")
                QMessageBox.information(self, "成功", "🗑️ 任务已删除！")
    
    def on_todo_select(self, row):
        """处理待办事项选择事件"""
        if row == -1:  # 没有选择
            return
        
        if row < len(self.todos):
            todo = self.todos[row]
            
            # 格式化创建时间
            created_at = datetime.fromisoformat(todo["created_at"])
            created_str = created_at.strftime("%Y-%m-%d %H:%M")
            
            # 状态文本和颜色
            if todo["completed"]:
                status = "✅ 已完成"
                status_color = "#27ae60"
            else:
                status = "⏳ 进行中"
                status_color = "#f39c12"
            
            # 优先级文本和颜色
            priority_map = {"low": "🟢 低", "medium": "🟡 中", "high": "🔴 高"}
            priority_text = priority_map.get(todo["priority"], "🟡 中")
            priority_color_map = {"low": "#27ae60", "medium": "#f39c12", "high": "#e74c3c"}
            priority_color = priority_color_map.get(todo["priority"], "#f39c12")
            
            # 构建详细的HTML格式信息
            details = f"""
            <div style="line-height: 1.8;">
                <div style="font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;">
                    {todo['title']}
                </div>
                <div><span style="color: #7f8c8d;">状态:</span> <span style="color: {status_color}; font-weight: bold;">{status}</span></div>
                <div><span style="color: #7f8c8d;">优先级:</span> <span style="color: {priority_color}; font-weight: bold;">{priority_text}</span></div>
                <div><span style="color: #7f8c8d;">创建时间:</span> {created_str}</div>
            """
            
            if todo.get("description"):
                details += f"""
                <div style="margin-top: 10px;">
                    <div style="color: #7f8c8d;">描述:</div>
                    <div style="background: #ecf0f1; padding: 8px; border-radius: 4px; margin-top: 5px;">
                        {todo['description']}
                    </div>
                </div>
                """
            
            details += "</div>"
            
            self.details_label.setText(details)
    
    def refresh_todo_list(self):
        """刷新待办事项列表"""
        self.todos = self.data_manager.get_todos()
        self.todo_list.clear()
        
        # 统计信息
        total = len(self.todos)
        completed = sum(1 for todo in self.todos if todo["completed"])
        in_progress = total - completed
        
        # 更新统计标签
        self.stats_label.setText(f"总任务: {total} | 已完成: {completed} | 进行中: {in_progress}")
        
        for todo in self.todos:
            # 状态图标
            status_icon = "✅" if todo["completed"] else "⏳"
            
            # 优先级图标
            priority_icon = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(todo["priority"], "🟡")
            
            # 创建时间（简短格式）
            created_at = datetime.fromisoformat(todo["created_at"])
            time_str = created_at.strftime("%m/%d %H:%M")
            
            display_text = f"{status_icon} {priority_icon} {todo['title']} ({time_str})"
            
            item = QListWidgetItem(display_text)
            
            # 根据优先级和完成状态设置样式
            if todo["completed"]:
                # 已完成项目 - 灰色
                item.setForeground(QColor("#95a5a6"))
                item.setBackground(QColor("#ecf0f1"))
                font = item.font()
                font.setStrikeOut(True)
                item.setFont(font)
            else:
                # 未完成项目 - 根据优先级设置颜色
                priority_colors = {
                    "high": QColor("#e74c3c"),
                    "medium": QColor("#f39c12"), 
                    "low": QColor("#27ae60")
                }
                color = priority_colors.get(todo["priority"], QColor("#2c3e50"))
                item.setForeground(color)
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            
            self.todo_list.addItem(item)
        
        # 更新标签文本（如果父级是选项卡）
        if hasattr(self.parent(), 'setTabText'):
            # 查找当前选项卡的索引
            tab_widget = self.parent()
            for i in range(tab_widget.count()):
                if tab_widget.widget(i) == self:
                    tab_widget.setTabText(i, f"📝 待办事项 ({completed}/{total})")
                    break


if __name__ == "__main__":
    # 测试代码
    import sys
    from PySide6.QtWidgets import QApplication, QTabWidget
    
    class MockDataManager:
        def __init__(self):
            self.todos = [
                {
                    "id": 1,
                    "title": "完成项目报告",
                    "description": "编写季度项目总结报告，包括数据分析",
                    "priority": "high",
                    "completed": False,
                    "created_at": "2024-01-01T10:00:00.000000"
                },
                {
                    "id": 2,
                    "title": "购买办公用品",
                    "description": "笔记本、笔、文件夹等",
                    "priority": "medium",
                    "completed": True,
                    "created_at": "2024-01-02T14:30:00.000000"
                },
                {
                    "id": 3,
                    "title": "阅读技术文档",
                    "description": "",
                    "priority": "low",
                    "completed": False,
                    "created_at": "2024-01-03T09:15:00.000000"
                }
            ]
        
        def get_todos(self):
            return self.todos
        
        def add_todo(self, title, description, priority):
            new_todo = {
                "id": len(self.todos) + 1,
                "title": title,
                "description": description,
                "priority": priority,
                "completed": False,
                "created_at": datetime.now().isoformat()
            }
            self.todos.append(new_todo)
            return True
        
        def update_todo(self, todo_id, completed=None, title=None, description=None, priority=None):
            for todo in self.todos:
                if todo["id"] == todo_id:
                    if completed is not None:
                        todo["completed"] = completed
                    if title is not None:
                        todo["title"] = title
                    if description is not None:
                        todo["description"] = description
                    if priority is not None:
                        todo["priority"] = priority
                    return True
            return False
        
        def delete_todo(self, todo_id):
            self.todos = [todo for todo in self.todos if todo["id"] != todo_id]
            return True
    
    app = QApplication(sys.argv)
    
    # 创建选项卡容器
    tab_widget = QTabWidget()
    
    data_manager = MockDataManager()
    todo_widget = TodoManager(data_manager=data_manager)
    tab_widget.addTab(todo_widget, "📝 待办事项")
    
    tab_widget.resize(800, 600)
    tab_widget.show()
    sys.exit(app.exec())