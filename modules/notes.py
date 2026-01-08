# TofuApp/modules/notes.py
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, 
    QListWidget, QPushButton, QMessageBox, QFrame, QGroupBox, QScrollArea,
    QListWidgetItem, QInputDialog, QComboBox  # 添加 QComboBox
)
from PySide6.QtCore import Qt, QTimer, QDateTime
from PySide6.QtGui import QFont, QGuiApplication, QPalette, QColor


class NoteItemWidget(QWidget):
    """自定义笔记项组件 - 实现块状布局"""
    
    def __init__(self, note_data, parent=None):
        super().__init__(parent)
        self.note_data = note_data
        self.setup_ui()
    
    def setup_ui(self):
        """设置笔记项UI"""
        self.setFixedHeight(80)
        self.setStyleSheet("""
            NoteItemWidget {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin: 2px;
                padding: 8px;
            }
            NoteItemWidget:hover {
                background-color: #f5f5f5;
                border: 1px solid #0078d4;
            }
            QLabel {
                background-color: transparent;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # 标题
        self.title_label = QLabel(self.note_data["title"])
        self.title_label.setFont(QFont("Arial", 10, QFont.Bold))
        self.title_label.setStyleSheet("color: #333333;")
        self.title_label.setWordWrap(True)
        self.title_label.setMaximumHeight(40)
        layout.addWidget(self.title_label)
        
        # 底部信息栏
        bottom_layout = QHBoxLayout()
        
        # 日期
        date_str = ""
        created_at = self.note_data.get("created_at", "")
        if created_at:
            try:
                if "T" in created_at:
                    date_part = created_at.split("T")[0]
                    date_obj = datetime.strptime(date_part, "%Y-%m-%d")
                    date_str = date_obj.strftime("%m/%d")
                else:
                    date_obj = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    date_str = date_obj.strftime("%m/%d")
            except:
                date_str = ""
        
        self.date_label = QLabel(date_str)
        self.date_label.setFont(QFont("Arial", 8))
        self.date_label.setStyleSheet("color: #666666;")
        bottom_layout.addWidget(self.date_label)
        
        bottom_layout.addStretch()
        
        # 文件夹标签
        folder_name = self.note_data.get("folder", "未分类")
        self.folder_label = QLabel(folder_name)
        self.folder_label.setFont(QFont("Arial", 8))
        self.folder_label.setStyleSheet("""
            color: #666666;
            background-color: #f0f0f0;
            padding: 2px 6px;
            border-radius: 4px;
        """)
        bottom_layout.addWidget(self.folder_label)
        
        layout.addLayout(bottom_layout)


class NotesWidget(QWidget):
    """笔记模块 - 块状布局 + 文件夹分类"""
    
    def __init__(self, parent=None, data_manager=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.current_note_id = None
        self.current_folder = "全部"
        
        # 验证数据管理器
        if not self.data_manager:
            print("错误: 数据管理器未提供")
            return
            
        self.setup_ui()
        self.refresh_folders()
        self.refresh_notes_list()
    
    def setup_ui(self):
        """设置笔记UI"""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # 左侧文件夹面板 - 最小
        left_panel = QWidget()
        left_panel.setMinimumWidth(120)
        left_panel.setMaximumWidth(180)
        left_panel.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 5px;
            }
        """)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 10, 5, 10)
        left_layout.setSpacing(5)
        
        # 文件夹标题
        folder_title = QLabel("文件夹")
        folder_title.setFont(QFont("Arial", 11, QFont.Bold))
        folder_title.setStyleSheet("color: #333333; margin-bottom: 10px;")
        left_layout.addWidget(folder_title)
        
        # 文件夹列表
        self.folder_list = QListWidget()
        self.folder_list.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
            }
            QListWidget::item {
                padding: 8px 12px;
                border-radius: 6px;
                margin: 2px 0px;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e8f4ff;
            }
        """)
        self.folder_list.currentItemChanged.connect(self.on_folder_select)
        left_layout.addWidget(self.folder_list)
        
        # 新建文件夹按钮
        new_folder_btn = QPushButton("新建文件夹")
        new_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 6px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        new_folder_btn.clicked.connect(self.new_folder)
        left_layout.addWidget(new_folder_btn)
        
        # 删除文件夹按钮
        delete_folder_btn = QPushButton("删除文件夹")
        delete_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 6px;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        delete_folder_btn.clicked.connect(self.delete_folder)
        left_layout.addWidget(delete_folder_btn)
        
        main_layout.addWidget(left_panel)
        
        # 中间笔记列表面板 - 中等
        middle_panel = QWidget()
        middle_panel.setMinimumWidth(250)
        middle_layout = QVBoxLayout(middle_panel)
        
        # 笔记列表顶部
        list_top_layout = QHBoxLayout()
        
        # 搜索框
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("搜索笔记...")
        self.search_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background-color: white;
            }
        """)
        self.search_edit.textChanged.connect(self.refresh_notes_list)
        list_top_layout.addWidget(self.search_edit)
        
        list_top_layout.addStretch()
        
        # 新建笔记按钮
        new_button = QPushButton("新建笔记")
        new_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        new_button.clicked.connect(self.new_note)
        list_top_layout.addWidget(new_button)
        
        middle_layout.addLayout(list_top_layout)
        
        # 笔记列表 - 使用QListWidget但自定义item
        self.notes_list = QListWidget()
        self.notes_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                border: none;
                padding: 0px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: transparent;
            }
        """)
        self.notes_list.setSelectionMode(QListWidget.SingleSelection)
        self.notes_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.notes_list.currentItemChanged.connect(self.on_note_select)
        middle_layout.addWidget(self.notes_list)
        
        main_layout.addWidget(middle_panel)
        
        # 右侧笔记编辑面板 - 最大
        right_panel = QWidget()
        right_panel.setMinimumWidth(400)
        right_layout = QVBoxLayout(right_panel)
        
        # 笔记内容框架
        content_group = QGroupBox("笔记内容")
        content_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        content_group_layout = QVBoxLayout(content_group)
        
        # 标题输入
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("标题:"))
        
        self.title_edit = QLineEdit()
        self.title_edit.setStyleSheet("padding: 8px 12px; border: 1px solid #e0e0e0; border-radius: 6px;")
        title_layout.addWidget(self.title_edit)
        
        content_group_layout.addLayout(title_layout)
        
        # 文件夹选择
        folder_select_layout = QHBoxLayout()
        folder_select_layout.addWidget(QLabel("文件夹:"))
        
        self.folder_combo = QComboBox()
        self.folder_combo.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                background-color: white;
            }
        """)
        folder_select_layout.addWidget(self.folder_combo)

        content_group_layout.addLayout(folder_select_layout)
        
        # 日期显示
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("创建时间:"))
        
        self.create_date_label = QLabel("未选择笔记")
        self.create_date_label.setFont(QFont("Arial", 9))
        self.create_date_label.setStyleSheet("color: #666666;")
        date_layout.addWidget(self.create_date_label)
        
        date_layout.addStretch()
        date_layout.addWidget(QLabel("更新时间:"))
        
        self.update_date_label = QLabel("未选择笔记")
        self.update_date_label.setFont(QFont("Arial", 9))
        self.update_date_label.setStyleSheet("color: #666666;")
        date_layout.addWidget(self.update_date_label)
        
        content_group_layout.addLayout(date_layout)
        
        # 笔记内容
        content_group_layout.addWidget(QLabel("内容:"))
        
        self.content_edit = QTextEdit()
        self.content_edit.setAcceptRichText(False)
        self.content_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 12px;
                background-color: white;
                font-size: 14px;
            }
        """)
        content_group_layout.addWidget(self.content_edit)
        
        # 按钮框架
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("保存")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        save_button.clicked.connect(self.save_note)
        button_layout.addWidget(save_button)
        
        delete_button = QPushButton("删除")
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        delete_button.clicked.connect(self.delete_note)
        button_layout.addWidget(delete_button)
        
        copy_button = QPushButton("复制")
        copy_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        copy_button.clicked.connect(self.copy_note)
        button_layout.addWidget(copy_button)
        
        content_group_layout.addLayout(button_layout)
        
        # 状态显示
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Arial", 9))
        self.status_label.setStyleSheet("color: #666666; padding: 8px; background-color: #f8f9fa; border-radius: 4px;")
        content_group_layout.addWidget(self.status_label)
        
        right_layout.addWidget(content_group)
        
        main_layout.addWidget(right_panel)
        
        # 设置布局比例 - 调整为主次分明
        main_layout.setStretchFactor(left_panel, 1)   # 最小 - 文件夹面板
        main_layout.setStretchFactor(middle_panel, 2) # 中等 - 笔记列表
        main_layout.setStretchFactor(right_panel, 3)  # 最大 - 笔记编辑区
    
    def on_folder_select(self, current, previous):
        """处理文件夹选择事件"""
        if current:
            self.current_folder = current.text()
            self.refresh_notes_list()
    
    def refresh_folders(self):
        """刷新文件夹列表"""
        self.folder_list.clear()
        
        # 添加默认文件夹
        folders = ["全部", "未分类"]
        
        # 从data_manager获取用户创建的文件夹
        user_folders = self.data_manager.get_folders() if hasattr(self.data_manager, 'get_folders') else []
        folders.extend(user_folders)
        
        for folder in folders:
            item = QListWidgetItem(folder)
            self.folder_list.addItem(item)
        
        # 默认选中"全部"
        self.folder_list.setCurrentRow(0)
    
    def refresh_notes_list(self):
        """刷新笔记列表 - 按修改时间倒序排列"""
        notes = self.data_manager.get_notes()
        
        # 过滤笔记
        search_text = self.search_edit.text().strip().lower()
        if search_text:
            notes = [note for note in notes if search_text in note["title"].lower() or 
                    search_text in note["content"].lower()]
        
        # 按文件夹过滤
        if self.current_folder == "全部":
            filtered_notes = notes
        elif self.current_folder == "未分类":
            filtered_notes = [note for note in notes if not note.get("folder") or note.get("folder") == "未分类"]
        else:
            filtered_notes = [note for note in notes if note.get("folder") == self.current_folder]
        
        # 按修改时间倒序排序
        def get_update_time(note):
            updated_at = note.get("updated_at", note.get("created_at", ""))
            if updated_at:
                try:
                    if "T" in updated_at:
                        return datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                    else:
                        return datetime.fromisoformat(updated_at)
                except:
                    return datetime.min
            return datetime.min
        
        filtered_notes.sort(key=get_update_time, reverse=True)
        
        # 更新笔记列表
        self.notes_list.clear()
        
        for note in filtered_notes:
            item = QListWidgetItem()
            item_widget = NoteItemWidget(note)
            item.setSizeHint(item_widget.sizeHint())
            
            # 存储笔记ID在item中
            item.setData(Qt.UserRole, note["id"])
            
            self.notes_list.addItem(item)
            self.notes_list.setItemWidget(item, item_widget)
    
    def on_note_select(self, current, previous):
        """处理笔记选择事件"""
        try:
            if not current:
                self.clear_note_display()
                return
            
            note_id = current.data(Qt.UserRole)
            if not note_id:
                return
                
            notes = self.data_manager.get_notes()
            if not notes:
                return
                
            # 查找选中的笔记
            note_found = False
            for note in notes:
                if note["id"] == note_id:
                    self.display_note_data(note)
                    note_found = True
                    break
                    
            if not note_found:
                self.clear_note_display()
                
        except Exception as e:
            print(f"选择笔记时出错: {e}")
            self.clear_note_display()
    
    def display_note_data(self, note):
        """显示笔记数据"""
        self.current_note_id = note["id"]
        self.title_edit.setText(note["title"])
        self.content_edit.setPlainText(note["content"])
        
        # 更新文件夹选择
        self.refresh_folder_combo(note.get("folder", "未分类"))
        
        # 显示日期信息
        created_at = note.get("created_at", "")
        updated_at = note.get("updated_at", "")
        
        if created_at:
            try:
                if "T" in created_at:
                    date_part = created_at.split("T")[0]
                    time_part = created_at.split("T")[1].split(".")[0]
                    formatted_date = f"{date_part} {time_part}"
                else:
                    date_obj = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                    formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
                self.create_date_label.setText(formatted_date)
            except:
                self.create_date_label.setText(created_at)
        else:
            self.create_date_label.setText("未知")
            
        if updated_at:
            try:
                if "T" in updated_at:
                    date_part = updated_at.split("T")[0]
                    time_part = updated_at.split("T")[1].split(".")[0]
                    formatted_date = f"{date_part} {time_part}"
                else:
                    date_obj = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                    formatted_date = date_obj.strftime("%Y-%m-%d %H:%M:%S")
                self.update_date_label.setText(formatted_date)
            except:
                self.update_date_label.setText(updated_at)
        else:
            self.update_date_label.setText("未知")

    def clear_note_display(self):
        """清空笔记显示"""
        self.current_note_id = None
        self.title_edit.clear()
        self.content_edit.clear()
        self.create_date_label.setText("未选择笔记")
        self.update_date_label.setText("未选择笔记")
    
    def refresh_folder_combo(self, current_folder="未分类"):
        """刷新文件夹选择下拉框"""
        self.folder_combo.clear()
        
        folders = ["未分类"]
        user_folders = self.data_manager.get_folders() if hasattr(self.data_manager, 'get_folders') else []
        folders.extend(user_folders)
        
        for folder in folders:
            self.folder_combo.addItem(folder)
        
        # 设置当前选中的文件夹
        index = self.folder_combo.findText(current_folder)
        if index >= 0:
            self.folder_combo.setCurrentIndex(index)
    
    def new_note(self):
        """创建新笔记"""
        self.current_note_id = None
        self.title_edit.clear()
        self.content_edit.clear()
        self.refresh_folder_combo()
        self.notes_list.clearSelection()
        self.create_date_label.setText("新笔记")
        self.update_date_label.setText("新笔记")
        self.status_label.setText("已创建新笔记")
        
        # 3秒后清除状态
        QTimer.singleShot(3000, lambda: self.status_label.setText(""))
    
    def new_folder(self):
        """新建文件夹"""
        folder_name, ok = QInputDialog.getText(self, "新建文件夹", "请输入文件夹名称:")
        if ok and folder_name.strip():
            folder_name = folder_name.strip()
            if hasattr(self.data_manager, 'add_folder'):
                success = self.data_manager.add_folder(folder_name)
                if success:
                    self.refresh_folders()
                    self.status_label.setText(f"已创建文件夹: {folder_name}")
                else:
                    QMessageBox.warning(self, "警告", f"文件夹 '{folder_name}' 已存在！")
            else:
                self.status_label.setText("数据管理器不支持文件夹功能")
            
            QTimer.singleShot(3000, lambda: self.status_label.setText(""))
    
    def delete_folder(self):
        """删除文件夹"""
        if not self.folder_list.currentItem():
            QMessageBox.warning(self, "警告", "请先选择一个文件夹")
            return
        
        folder_name = self.folder_list.currentItem().text()
        
        # 不允许删除默认文件夹
        if folder_name in ["全部", "未分类"]:
            QMessageBox.warning(self, "警告", "不能删除默认文件夹")
            return
        
        reply = QMessageBox.question(self, "确认", f"确定要删除文件夹 '{folder_name}' 吗？\n该文件夹下的笔记将移动到'未分类'文件夹。",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            if hasattr(self.data_manager, 'delete_folder'):
                success = self.data_manager.delete_folder(folder_name)
                if success:
                    self.refresh_folders()
                    self.refresh_notes_list()
                    self.status_label.setText(f"已删除文件夹: {folder_name}")
                else:
                    QMessageBox.warning(self, "错误", "删除文件夹失败")
            
            QTimer.singleShot(3000, lambda: self.status_label.setText(""))
    
    def save_note(self):
        """保存笔记"""
        try:
            title = self.title_edit.text().strip()
            content = self.content_edit.toPlainText().strip()
            
            if not title:
                QMessageBox.critical(self, "错误", "请输入笔记标题")
                return
            
            # 获取选中的文件夹
            folder = self.folder_combo.currentText() if self.folder_combo.currentText() else "未分类"
            
            if self.current_note_id:
                # 更新现有笔记
                success = self.data_manager.update_note(
                    self.current_note_id, 
                    title=title, 
                    content=content,
                    folder=folder
                )
                if success:
                    self.status_label.setText("笔记已更新")
                else:
                    QMessageBox.critical(self, "错误", "更新笔记失败")
            else:
                # 创建新笔记
                success = self.data_manager.add_note(title, content, folder)
                if success:
                    self.status_label.setText("笔记已创建")
                else:
                    QMessageBox.critical(self, "错误", "创建笔记失败")
            
            self.refresh_notes_list()
            
            # 3秒后清除状态
            QTimer.singleShot(3000, lambda: self.status_label.setText(""))
            
        except Exception as e:
            print(f"保存笔记时出错: {e}")
            QMessageBox.critical(self, "错误", f"保存笔记失败: {str(e)}")
    
    def delete_note(self):
        """删除笔记"""
        if not self.current_note_id:
            QMessageBox.warning(self, "警告", "请先选择一个笔记")
            return
        
        reply = QMessageBox.question(self, "确认", "确定要删除这个笔记吗？",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.data_manager.delete_note(self.current_note_id)
            self.new_note()
            self.refresh_notes_list()
            self.status_label.setText("笔记已删除")
            
            # 3秒后清除状态
            QTimer.singleShot(3000, lambda: self.status_label.setText(""))
    
    def copy_note(self):
        """复制笔记内容到剪贴板"""
        if not self.current_note_id:
            QMessageBox.warning(self, "警告", "请先选择一个笔记")
            return
        
        title = self.title_edit.text().strip()
        content = self.content_edit.toPlainText().strip()
        
        if not title and not content:
            QMessageBox.warning(self, "警告", "笔记内容为空")
            return
        
        # 格式化要复制的内容
        copy_text = f"{title}\n\n{content}"
        
        try:
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(copy_text)
            
            self.status_label.setText("笔记内容已复制到剪贴板")
            
            # 3秒后清除状态
            QTimer.singleShot(3000, lambda: self.status_label.setText(""))
        except Exception as e:
            QMessageBox.critical(self, "错误", f"复制失败: {str(e)}")
    
    def check_data_file(self):
        """检查数据文件内容 - 用于调试"""
        if hasattr(self.data_manager, 'data_file'):
            print(f"数据文件路径: {self.data_manager.data_file}")
            try:
                with open(self.data_manager.data_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    print(f"数据文件内容: {content}")
            except Exception as e:
                print(f"读取数据文件失败: {e}")


if __name__ == "__main__":
    # 测试代码
    import sys
    from PySide6.QtWidgets import QApplication, QInputDialog
    
    class MockDataManager:
        def __init__(self):
            self.notes = [
                {
                    "id": 1,
                    "title": "项目计划",
                    "content": "完成项目需求分析和技术方案设计",
                    "folder": "工作",
                    "created_at": "2024-01-15T10:00:00.000000",
                    "updated_at": "2024-01-20T14:30:00.000000"
                },
                {
                    "id": 2,
                    "title": "购物清单",
                    "content": "牛奶、面包、水果、蔬菜",
                    "folder": "生活",
                    "created_at": "2024-01-18T16:20:00.000000",
                    "updated_at": "2024-01-19T09:15:00.000000"
                },
                {
                    "id": 3,
                    "title": "读书笔记",
                    "content": "《深入理解计算机系统》第一章总结...",
                    "folder": "学习",
                    "created_at": "2024-01-10T08:30:00.000000",
                    "updated_at": "2024-01-12T11:45:00.000000"
                },
                {
                    "id": 4,
                    "title": "临时想法",
                    "content": "突然想到的一个好点子...",
                    "folder": "",
                    "created_at": "2024-01-22T20:10:00.000000",
                    "updated_at": "2024-01-22T20:10:00.000000"
                }
            ]
            self.folders = ["工作", "生活", "学习"]
        
        def get_notes(self):
            return self.notes
        
        def get_folders(self):
            return self.folders
        
        def add_folder(self, folder_name):
            if folder_name not in self.folders:
                self.folders.append(folder_name)
                return True
            return False
        
        def delete_folder(self, folder_name):
            if folder_name in self.folders:
                self.folders.remove(folder_name)
                # 将该文件夹下的笔记移动到"未分类"
                for note in self.notes:
                    if note.get("folder") == folder_name:
                        note["folder"] = "未分类"
                return True
            return False
        
        def add_note(self, title, content, folder="未分类"):
            new_note = {
                "id": len(self.notes) + 1,
                "title": title,
                "content": content,
                "folder": folder,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            self.notes.append(new_note)
            return True
        
        def update_note(self, note_id, title, content, folder="未分类"):
            for note in self.notes:
                if note["id"] == note_id:
                    note["title"] = title
                    note["content"] = content
                    note["folder"] = folder
                    note["updated_at"] = datetime.now().isoformat()
                    return True
            return False
        
        def delete_note(self, note_id):
            self.notes = [note for note in self.notes if note["id"] != note_id]
            return True
    
    app = QApplication(sys.argv)
    data_manager = MockDataManager()
    widget = NotesWidget(data_manager=data_manager)
    widget.show()
    sys.exit(app.exec())