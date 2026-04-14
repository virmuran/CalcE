# CalcE/modules/important_dates.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QListWidget, QListWidgetItem, QComboBox,
    QMessageBox, QInputDialog, QGroupBox, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from datetime import datetime

class ImportantDatesWidget(QWidget):
    """重要日期模块 - 整合生日和纪念日功能"""
    
    def __init__(self, parent=None, data_manager=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.setup_ui()
        self.refresh_all()
    
    def setup_ui(self):
        """设置重要日期UI"""
        main_layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel("重要日期管理")
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 添加日期区域
        add_group = QGroupBox("添加重要日期")
        main_layout.addWidget(add_group)
        
        add_layout = QVBoxLayout(add_group)
        
        # 类型选择
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("类型:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["生日", "纪念日"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        self.type_combo.setFixedWidth(100)
        type_layout.addWidget(self.type_combo)
        type_layout.addStretch()
        add_layout.addLayout(type_layout)
        
        # 输入行
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("名称:"))
        self.name_entry = QLineEdit()
        self.name_entry.setPlaceholderText("输入姓名或事件名称")
        input_layout.addWidget(self.name_entry)
        
        input_layout.addWidget(QLabel("日期:"))
        self.date_entry = QLineEdit()
        self.date_entry.setPlaceholderText("YYYY-MM-DD")
        self.date_entry.setFixedWidth(100)
        input_layout.addWidget(self.date_entry)
        
        # 纪念日类型选择（默认隐藏）
        self.anniversary_type_label = QLabel("纪念日类型:")
        self.anniversary_type_combo = QComboBox()
        self.anniversary_type_combo.addItems(["个人", "家庭", "工作", "爱情", "友情", "其他"])
        self.anniversary_type_combo.setFixedWidth(80)
        
        input_layout.addWidget(self.anniversary_type_label)
        input_layout.addWidget(self.anniversary_type_combo)
        
        add_btn = QPushButton("添加")
        add_btn.clicked.connect(self.add_date)
        input_layout.addWidget(add_btn)
        
        input_layout.addStretch()
        add_layout.addLayout(input_layout)
        
        # 初始隐藏纪念日类型选择
        self.anniversary_type_label.setVisible(False)
        self.anniversary_type_combo.setVisible(False)
        
        # 日期列表
        list_group = QGroupBox("重要日期列表")
        main_layout.addWidget(list_group)
        
        list_layout = QVBoxLayout(list_group)
        
        self.date_list = QListWidget()
        self.date_list.itemSelectionChanged.connect(self.on_date_select)
        list_layout.addWidget(self.date_list)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        edit_btn = QPushButton("编辑")
        edit_btn.clicked.connect(self.edit_date)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("删除")
        delete_btn.clicked.connect(self.delete_date)
        button_layout.addWidget(delete_btn)
        
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.refresh_all)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        list_layout.addLayout(button_layout)
        
        # 详细信息区域
        details_group = QGroupBox("详细信息")
        main_layout.addWidget(details_group)
        
        details_layout = QVBoxLayout(details_group)
        self.details_label = QLabel("选择一个日期查看详情")
        self.details_label.setWordWrap(True)
        self.details_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        details_layout.addWidget(self.details_label)
        
        # 即将到来的日期
        upcoming_group = QGroupBox("即将到来的重要日期")
        main_layout.addWidget(upcoming_group)
        
        upcoming_layout = QVBoxLayout(upcoming_group)
        self.upcoming_label = QLabel("")
        self.upcoming_label.setWordWrap(True)
        self.upcoming_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        upcoming_layout.addWidget(self.upcoming_label)
    
    def on_type_changed(self, date_type):
        """处理日期类型变化"""
        if date_type == "纪念日":
            self.anniversary_type_label.setVisible(True)
            self.anniversary_type_combo.setVisible(True)
            self.name_entry.setPlaceholderText("输入纪念日名称")
        else:
            self.anniversary_type_label.setVisible(False)
            self.anniversary_type_combo.setVisible(False)
            self.name_entry.setPlaceholderText("输入姓名")
    
    def add_date(self):
        """添加重要日期"""
        date_type = self.type_combo.currentText()
        name = self.name_entry.text().strip()
        date_str = self.date_entry.text().strip()
        
        if not name:
            QMessageBox.warning(self, "输入错误", "请输入名称")
            return
        
        if not self.validate_date(date_str, "YYYY-MM-DD"):
            QMessageBox.warning(self, "输入错误", "日期格式错误，请使用 YYYY-MM-DD 格式")
            return
        
        if date_type == "生日":
            self.data_manager.add_birthday(name, date_str)
        else:  # 纪念日
            anniversary_type = self.anniversary_type_combo.currentText()
            self.data_manager.add_anniversary(name, date_str, anniversary_type)
        
        self.name_entry.clear()
        self.date_entry.clear()
        self.refresh_all()
    
    def edit_date(self):
        """编辑重要日期"""
        current_item = self.date_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "选择错误", "请先选择一个日期")
            return
        
        # 获取存储的数据
        item_data = current_item.data(Qt.UserRole)
        if not item_data:
            return
        
        date_type = item_data.get("type")
        item_id = item_data.get("id")
        
        if date_type == "birthday":
            birthdays = self.data_manager.get_birthdays()
            birthday = next((b for b in birthdays if b["id"] == item_id), None)
            if not birthday:
                return
            
            new_name, ok = QInputDialog.getText(self, "编辑生日", "请输入新姓名:", text=birthday["name"])
            if not ok:
                return
            
            new_date, ok = QInputDialog.getText(self, "编辑生日", "请输入新生日:", text=birthday["date"])
            if not ok:
                return
            
            if not self.validate_date(new_date, "YYYY-MM-DD"):
                QMessageBox.warning(self, "输入错误", "生日格式错误，请使用 YYYY-MM-DD 格式")
                return
            
            self.data_manager.update_birthday(birthday["id"], name=new_name, date=new_date)
            
        else:  # anniversary
            anniversaries = self.data_manager.get_anniversaries()
            anniversary = next((a for a in anniversaries if a["id"] == item_id), None)
            if not anniversary:
                return
            
            new_name, ok = QInputDialog.getText(self, "编辑纪念日", "请输入新名称:", text=anniversary["name"])
            if not ok:
                return
            
            new_date, ok = QInputDialog.getText(self, "编辑纪念日", "请输入新日期:", text=anniversary["date"])
            if not ok:
                return
            
            if not self.validate_date(new_date, "YYYY-MM-DD"):
                QMessageBox.warning(self, "输入错误", "日期格式错误，请使用 YYYY-MM-DD 格式")
                return
            
            # 纪念日类型选择
            types = ["个人", "家庭", "工作", "爱情", "友情", "其他"]
            current_type = anniversary.get("type", "个人")
            new_type, ok = QInputDialog.getItem(self, "编辑纪念日", "选择纪念日类型:", 
                                               types, types.index(current_type) if current_type in types else 0, False)
            if not ok:
                return
            
            self.data_manager.update_anniversary(anniversary["id"], name=new_name, date=new_date, type=new_type)
        
        self.refresh_all()
    
    def delete_date(self):
        """删除重要日期"""
        current_item = self.date_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "选择错误", "请先选择一个日期")
            return
        
        # 获取存储的数据
        item_data = current_item.data(Qt.UserRole)
        if not item_data:
            return
        
        date_type = item_data.get("type")
        item_id = item_data.get("id")
        name = item_data.get("name")
        
        reply = QMessageBox.question(self, "确认删除", 
                                    f"确定要删除 {name} 吗？")
        if reply == QMessageBox.Yes:
            if date_type == "birthday":
                self.data_manager.delete_birthday(item_id)
            else:  # anniversary
                self.data_manager.delete_anniversary(item_id)
            
            self.refresh_all()
    
    def on_date_select(self):
        """处理日期选择事件"""
        current_item = self.date_list.currentItem()
        if not current_item:
            self.details_label.setText("选择一个日期查看详情")
            return
        
        # 获取存储的数据
        item_data = current_item.data(Qt.UserRole)
        if not item_data:
            return
        
        date_type = item_data.get("type")
        item_id = item_data.get("id")
        
        if date_type == "birthday":
            birthdays = self.data_manager.get_birthdays()
            birthday = next((b for b in birthdays if b["id"] == item_id), None)
            if birthday:
                details = self.get_birthday_details(birthday)
                self.details_label.setText(details)
        else:  # anniversary
            anniversaries = self.data_manager.get_anniversaries()
            anniversary = next((a for a in anniversaries if a["id"] == item_id), None)
            if anniversary:
                details = self.get_anniversary_details(anniversary)
                self.details_label.setText(details)
    
    def refresh_all(self):
        """刷新所有数据"""
        self.refresh_date_list()
        self.update_upcoming_dates()
    
    def refresh_date_list(self):
        """刷新日期列表"""
        birthdays = self.data_manager.get_birthdays()
        anniversaries = self.data_manager.get_anniversaries()
        
        self.date_list.clear()
        
        # 合并所有日期
        all_dates = []
        
        # 添加生日
        for birthday in birthdays:
            all_dates.append({
                "type": "birthday",
                "id": birthday["id"],
                "name": birthday["name"],
                "date": birthday["date"],
                "sort_key": birthday["date"]  # 使用日期排序
            })
        
        # 添加纪念日
        for anniversary in anniversaries:
            all_dates.append({
                "type": "anniversary",
                "id": anniversary["id"],
                "name": anniversary["name"],
                "date": anniversary["date"],
                "sort_key": anniversary["date"]  # 使用日期排序
            })
        
        # 按日期排序
        all_dates.sort(key=lambda x: x["sort_key"])
        
        # 添加到列表
        for date_item in all_dates:
            if date_item["type"] == "birthday":
                age = self.calculate_age(date_item["date"])
                days_until = self.days_until_next_birthday(date_item["date"])
                display_text = f"{date_item['name']} - {date_item['date']} ({age}岁)"
                item = QListWidgetItem(display_text)
                
                # 颜色标记
                if days_until <= 7:
                    item.setForeground(QColor("#ff4444"))  # 红色 - 一周内
                elif days_until <= 30:
                    item.setForeground(QColor("#ff8800"))  # 橙色 - 一月内
                elif days_until <= 90:
                    item.setForeground(QColor("#ffaa00"))  # 黄色 - 三月内
                    
            else:  # anniversary
                days_passed = self.days_since_date(date_item["date"])
                years = days_passed // 365
                days_until = self.days_until_next_anniversary(date_item["date"])
                display_text = f"{date_item['name']} - {date_item['date']} ({years}周年)"
                item = QListWidgetItem(display_text)
                
                # 颜色标记
                if days_until <= 7:
                    item.setForeground(QColor("#ff4444"))
                elif days_until <= 30:
                    item.setForeground(QColor("#ff8800"))
                elif days_until <= 90:
                    item.setForeground(QColor("#ffaa00"))
            
            # 存储数据以便后续使用
            item.setData(Qt.UserRole, date_item)
            self.date_list.addItem(item)
    
    # 通用方法
    def validate_date(self, date_str, format):
        """验证日期格式"""
        try:
            if format == "YYYY-MM-DD":
                datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def calculate_age(self, birth_date_str):
        """计算年龄"""
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
        today = datetime.now()
        age = today.year - birth_date.year
        
        if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
            age -= 1
        
        return age
    
    def days_until_next_birthday(self, birth_date_str):
        """计算距离下一次生日天数"""
        birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")
        today = datetime.now()
        next_birthday = birth_date.replace(year=today.year)
        
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        
        return (next_birthday - today).days
    
    def days_since_date(self, date_str):
        """计算从某个日期到现在经过的天数"""
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
        today = datetime.now()
        return (today - target_date).days
    
    def days_until_next_anniversary(self, date_str):
        """计算距离下一个周年纪念天数"""
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
        today = datetime.now()
        next_anniversary = target_date.replace(year=today.year)
        
        if next_anniversary < today:
            next_anniversary = next_anniversary.replace(year=today.year + 1)
        
        return (next_anniversary - today).days
    
    def get_birthday_details(self, birthday):
        """获取生日详细信息"""
        age = self.calculate_age(birthday["date"])
        days_until = self.days_until_next_birthday(birthday["date"])
        
        details = f"<b>{birthday['name']}</b><br>"
        details += f"生日: {birthday['date']}<br>"
        details += f"当前年龄: {age} 岁<br>"
        details += f"下次生日: 还有 {days_until} 天<br>"
        details += f"下次年龄: {age + 1} 岁"
        
        return details
    
    def get_anniversary_details(self, anniversary):
        """获取纪念日详细信息"""
        days_passed = self.days_since_date(anniversary["date"])
        years = days_passed // 365
        months = (days_passed % 365) // 30
        days_until = self.days_until_next_anniversary(anniversary["date"])
        
        details = f"<b>{anniversary['name']}</b><br>"
        details += f"日期: {anniversary['date']}<br>"
        details += f"类型: {anniversary.get('type', '个人')}<br>"
        details += f"已过去: {days_passed} 天 ({years}年{months}个月)<br>"
        details += f"距离下一个周年: {days_until} 天"
        
        return details
    
    def update_upcoming_dates(self):
        """更新即将到来的日期"""
        birthdays = self.data_manager.get_birthdays()
        anniversaries = self.data_manager.get_anniversaries()
        
        upcoming_lines = []
        
        # 即将到来的生日
        upcoming_birthdays = []
        for birthday in birthdays:
            days_until = self.days_until_next_birthday(birthday["date"])
            if days_until <= 60:
                upcoming_birthdays.append((birthday["name"], days_until, self.calculate_age(birthday["date"]) + 1))
        
        upcoming_birthdays.sort(key=lambda x: x[1])
        if upcoming_birthdays:
            upcoming_lines.append("<b>即将到来的生日:</b>")
            for name, days, age in upcoming_birthdays[:5]:
                upcoming_lines.append(f"• {name}: 还有{days}天 ({age}岁)")
        
        # 即将到来的纪念日
        upcoming_anniversaries = []
        for anniversary in anniversaries:
            days_until = self.days_until_next_anniversary(anniversary["date"])
            if days_until <= 60:
                years_passed = self.days_since_date(anniversary["date"]) // 365
                upcoming_anniversaries.append((anniversary["name"], days_until, years_passed + 1))
        
        upcoming_anniversaries.sort(key=lambda x: x[1])
        if upcoming_anniversaries:
            if upcoming_lines:
                upcoming_lines.append("")  # 添加空行分隔
            upcoming_lines.append("<b>即将到来的纪念日:</b>")
            for name, days, years in upcoming_anniversaries[:5]:
                upcoming_lines.append(f"• {name}: 还有{days}天 ({years}周年)")
        
        if not upcoming_lines:
            upcoming_lines.append("未来60天内没有即将到来的重要日期")
        
        self.upcoming_label.setText("<br>".join(upcoming_lines))