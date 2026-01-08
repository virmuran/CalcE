# TofuApp/modules/bookmarks.py
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                               QPushButton, QListWidget, QListWidgetItem, QComboBox,
                               QMessageBox, QInputDialog, QGroupBox, QSplitter)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDesktopServices
from datetime import datetime

class BookmarksWidget(QWidget):
    """书签管理模块"""
    
    def __init__(self, parent=None, data_manager=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.current_folder = "全部"
        self.setup_ui()
        self.refresh_bookmarks()
    
    def setup_ui(self):
        """设置书签UI"""
        main_layout = QVBoxLayout(self)
        
        # 主框架
        main_group = QGroupBox("书签管理")
        main_layout.addWidget(main_group)
        
        main_group_layout = QVBoxLayout(main_group)
        
        # 使用分割器创建左右布局
        splitter = QSplitter(Qt.Horizontal)
        main_group_layout.addWidget(splitter)
        
        # 左侧文件夹框架
        folder_group = QGroupBox("文件夹")
        folder_layout = QVBoxLayout(folder_group)
        
        # 文件夹列表和按钮
        folder_button_layout = QHBoxLayout()
        new_folder_btn = QPushButton("新建")
        new_folder_btn.clicked.connect(self.new_folder)
        folder_button_layout.addWidget(new_folder_btn)
        folder_button_layout.addStretch()
        folder_layout.addLayout(folder_button_layout)
        
        # 文件夹列表
        self.folder_listbox = QListWidget()
        self.folder_listbox.itemSelectionChanged.connect(self.on_folder_select)
        folder_layout.addWidget(self.folder_listbox)
        
        # 右侧书签框架
        bookmark_widget = QWidget()
        bookmark_layout = QVBoxLayout(bookmark_widget)
        
        # 书签列表和按钮
        bookmark_button_layout = QHBoxLayout()
        bookmark_button_layout.addWidget(QLabel("书签"))
        new_bookmark_btn = QPushButton("添加")
        new_bookmark_btn.clicked.connect(self.new_bookmark)
        bookmark_button_layout.addWidget(new_bookmark_btn)
        bookmark_button_layout.addStretch()
        bookmark_layout.addLayout(bookmark_button_layout)
        
        # 书签列表
        self.bookmark_listbox = QListWidget()
        self.bookmark_listbox.itemSelectionChanged.connect(self.on_bookmark_select)
        self.bookmark_listbox.itemDoubleClicked.connect(self.on_bookmark_double_click)
        bookmark_layout.addWidget(self.bookmark_listbox)
        
        # 将左右两部分添加到分割器
        splitter.addWidget(folder_group)
        splitter.addWidget(bookmark_widget)
        splitter.setSizes([200, 400])
        
        # 书签详情框架
        details_group = QGroupBox("书签详情")
        main_group_layout.addWidget(details_group)
        
        details_layout = QVBoxLayout(details_group)
        
        # 标题
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("标题:"))
        self.title_entry = QLineEdit()
        title_layout.addWidget(self.title_entry)
        details_layout.addLayout(title_layout)
        
        # URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL:"))
        self.url_entry = QLineEdit()
        url_layout.addWidget(self.url_entry)
        details_layout.addLayout(url_layout)
        
        # 文件夹选择
        folder_select_layout = QHBoxLayout()
        folder_select_layout.addWidget(QLabel("文件夹:"))
        self.folder_combo = QComboBox()
        folder_select_layout.addWidget(self.folder_combo)
        details_layout.addLayout(folder_select_layout)
        
        # 按钮框架
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_bookmark)
        button_layout.addWidget(save_btn)
        
        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(self.delete_bookmark)
        button_layout.addWidget(delete_btn)
        
        open_btn = QPushButton("打开")
        open_btn.clicked.connect(self.open_bookmark)
        button_layout.addWidget(open_btn)
        
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.refresh_bookmarks)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        details_layout.addLayout(button_layout)
        
        # 初始化文件夹列表
        self.refresh_folders()
    
    def refresh_folders(self):
        """刷新文件夹列表"""
        folders = self.get_folders()
        self.folder_listbox.clear()
        self.folder_listbox.addItem("全部")
        
        for folder in folders:
            self.folder_listbox.addItem(folder)
        
        # 更新文件夹选择框
        self.folder_combo.clear()
        self.folder_combo.addItems(folders)
        
        # 默认选择第一个文件夹
        if folders:
            self.folder_combo.setCurrentText(folders[0])
    
    def refresh_bookmarks(self):
        """刷新书签列表"""
        bookmarks = self.data_manager.get_bookmarks()
        self.bookmark_listbox.clear()
        
        for bookmark in bookmarks:
            # 如果当前文件夹不是"全部"，则只显示该文件夹的书签
            if self.current_folder != "全部" and bookmark.get("folder") != self.current_folder:
                continue
            
            self.bookmark_listbox.addItem(bookmark["title"])
    
    def get_folders(self):
        """获取所有文件夹"""
        bookmarks = self.data_manager.get_bookmarks()
        folders = set()
        
        for bookmark in bookmarks:
            folder = bookmark.get("folder", "默认")
            folders.add(folder)
        
        return sorted(list(folders))
    
    def on_folder_select(self):
        """处理文件夹选择事件"""
        current_item = self.folder_listbox.currentItem()
        if not current_item:
            return
        
        folder_name = current_item.text()
        self.current_folder = folder_name
        self.refresh_bookmarks()
    
    def on_bookmark_select(self):
        """处理书签选择事件"""
        current_item = self.bookmark_listbox.currentItem()
        if not current_item:
            return
        
        index = self.bookmark_listbox.row(current_item)
        bookmarks = self.data_manager.get_bookmarks()
        filtered_bookmarks = self.get_filtered_bookmarks(bookmarks)
        
        if index < len(filtered_bookmarks):
            bookmark = filtered_bookmarks[index]
            self.title_entry.setText(bookmark["title"])
            self.url_entry.setText(bookmark["url"])
            self.folder_combo.setCurrentText(bookmark.get("folder", "默认"))
    
    def on_bookmark_double_click(self, item):
        """处理书签双击事件"""
        self.open_bookmark()
    
    def get_filtered_bookmarks(self, bookmarks):
        """获取过滤后的书签列表"""
        if self.current_folder == "全部":
            return bookmarks
        else:
            return [b for b in bookmarks if b.get("folder") == self.current_folder]
    
    def new_folder(self):
        """新建文件夹"""
        folder_name, ok = QInputDialog.getText(self, "新建文件夹", "请输入文件夹名称:")
        if ok and folder_name:
            # 这里可以添加文件夹创建逻辑
            self.refresh_folders()
            QMessageBox.information(self, "成功", f"文件夹 '{folder_name}' 已创建")
    
    def new_bookmark(self):
        """新建书签"""
        self.title_entry.clear()
        self.url_entry.clear()
        self.folder_combo.setCurrentText("默认")
        self.bookmark_listbox.clearSelection()
    
    def save_bookmark(self):
        """保存书签"""
        title = self.title_entry.text().strip()
        url = self.url_entry.text().strip()
        folder = self.folder_combo.currentText().strip()
        
        if not title:
            QMessageBox.critical(self, "错误", "请输入书签标题")
            return
        
        if not url:
            QMessageBox.critical(self, "错误", "请输入书签URL")
            return
        
        # 验证URL格式
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        
        # 检查是新建还是更新
        current_item = self.bookmark_listbox.currentItem()
        if current_item:
            # 更新现有书签
            index = self.bookmark_listbox.row(current_item)
            bookmarks = self.data_manager.get_bookmarks()
            filtered_bookmarks = self.get_filtered_bookmarks(bookmarks)
            
            if index < len(filtered_bookmarks):
                bookmark = filtered_bookmarks[index]
                self.data_manager.update_bookmark(bookmark["id"], title=title, url=url, folder=folder)
                QMessageBox.information(self, "成功", "书签已更新")
        else:
            # 创建新书签
            self.data_manager.add_bookmark(title, url, folder)
            QMessageBox.information(self, "成功", "书签已添加")
        
        self.refresh_bookmarks()
        self.refresh_folders()
    
    def delete_bookmark(self):
        """删除书签"""
        current_item = self.bookmark_listbox.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择一个书签")
            return
        
        index = self.bookmark_listbox.row(current_item)
        bookmarks = self.data_manager.get_bookmarks()
        filtered_bookmarks = self.get_filtered_bookmarks(bookmarks)
        
        if index < len(filtered_bookmarks):
            bookmark = filtered_bookmarks[index]
            reply = QMessageBox.question(self, "确认", 
                                        f"确定要删除书签 '{bookmark['title']}' 吗？",
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.data_manager.delete_bookmark(bookmark["id"])
                self.refresh_bookmarks()
                self.refresh_folders()
                QMessageBox.information(self, "成功", "书签已删除")
    
    def open_bookmark(self):
        """打开书签"""
        current_item = self.bookmark_listbox.currentItem()
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择一个书签")
            return
        
        index = self.bookmark_listbox.row(current_item)
        bookmarks = self.data_manager.get_bookmarks()
        filtered_bookmarks = self.get_filtered_bookmarks(bookmarks)
        
        if index < len(filtered_bookmarks):
            bookmark = filtered_bookmarks[index]
            QDesktopServices.openUrl(bookmark["url"])