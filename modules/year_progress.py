# CalcE/modules/year_progress.py
from datetime import datetime, timedelta
import math
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QScrollArea, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, QDateTime
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QPalette, QBrush


class YearProgressCircle(QWidget):
    """自定义圆形进度条控件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(200, 200)
        self.remaining_percent = 0.0
    
    def set_progress(self, percent):
        """设置剩余百分比"""
        self.remaining_percent = percent
        self.update()  # 触发重绘
    
    def paintEvent(self, event):
        """绘制圆形进度条"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 圆形参数
        center_x, center_y = 100, 100
        radius = 80
        start_angle = 90  # 从顶部开始
        
        # 绘制背景圆（已过去的部分）
        pen = QPen(QColor("#e0e0e0"))
        pen.setWidth(10)
        painter.setPen(pen)
        painter.drawEllipse(center_x - radius, center_y - radius, 
                           radius * 2, radius * 2)
        
        # 绘制剩余进度圆弧
        if self.remaining_percent > 0:
            # 计算结束角度 - 顺时针绘制剩余部分
            extent = -self.remaining_percent * 3.6  # 360度 = 100%
            
            pen = QPen(QColor("#FF6B6B"))
            pen.setWidth(10)
            painter.setPen(pen)
            
            # 绘制圆弧
            painter.drawArc(center_x - radius, center_y - radius, 
                           radius * 2, radius * 2, 
                           start_angle * 16, extent * 16)
        
        # 绘制中心文本
        painter.setPen(QColor("#FF6B6B"))
        font = QFont("Arial", 16, QFont.Bold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, f"{self.remaining_percent:.1f}%")


class YearProgressWidget(QWidget):
    """今年余额模块 (PySide6版本)"""
    
    def __init__(self, parent=None, data_manager=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.setup_ui()
        self.update_progress()
        
        # 启动定时器，每秒更新一次
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(1000)
    
    def setup_ui(self):
        """设置今年余额UI"""
        main_layout = QVBoxLayout(self)
        
        # 主框架
        main_group = QGroupBox("今年余额")
        main_layout.addWidget(main_group)
        
        group_layout = QVBoxLayout(main_group)
        
        # 进度显示框架
        progress_layout = QVBoxLayout()
        
        # 圆形进度条
        self.progress_circle = YearProgressCircle()
        progress_layout.addWidget(self.progress_circle, 0, Qt.AlignCenter)
        
        # 进度信息
        self.progress_label = QLabel("")
        self.progress_label.setFont(QFont("Arial", 14))
        self.progress_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.progress_label)
        
        # 倒计时显示
        self.countdown_label = QLabel("")
        self.countdown_label.setFont(QFont("Arial", 12))
        self.countdown_label.setStyleSheet("color: #FF6B6B;")
        self.countdown_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.countdown_label)
        
        group_layout.addLayout(progress_layout)
        
        # 详细信息框架
        details_group = QGroupBox("详细信息")
        group_layout.addWidget(details_group)
        
        details_layout = QVBoxLayout(details_group)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setFont(QFont("Arial", 10))
        details_layout.addWidget(self.details_text)
        
        # 按钮框架
        button_layout = QHBoxLayout()
        
        copy_button = QPushButton("复制进度")
        copy_button.clicked.connect(self.copy_progress)
        button_layout.addWidget(copy_button)
        
        button_layout.addStretch()
        group_layout.addLayout(button_layout)
    
    def update_progress(self):
        """更新进度显示"""
        now = datetime.now()
        year = now.year
        
        # 计算一年中的天数
        start_of_year = datetime(year, 1, 1)
        end_of_year = datetime(year, 12, 31, 23, 59, 59)
        
        # 计算总天数和剩余时间
        total_seconds = (end_of_year - start_of_year).total_seconds()
        remaining_seconds = (end_of_year - now).total_seconds()
        
        # 计算剩余百分比（从100%到0%）
        remaining_percent = (remaining_seconds / total_seconds) * 100
        
        # 计算剩余天数、小时、分钟、秒
        days_remaining = int(remaining_seconds // (24 * 3600))
        remaining_seconds %= (24 * 3600)
        hours_remaining = int(remaining_seconds // 3600)
        remaining_seconds %= 3600
        minutes_remaining = int(remaining_seconds // 60)
        seconds_remaining = int(remaining_seconds % 60)
        
        # 更新圆形进度条（显示剩余百分比）
        self.progress_circle.set_progress(remaining_percent)
        
        # 更新进度标签
        progress_text = f"{year}年剩余: {remaining_percent:.1f}%"
        self.progress_label.setText(progress_text)
        
        # 更新倒计时标签
        countdown_text = f"倒计时: {days_remaining}天 {hours_remaining:02d}:{minutes_remaining:02d}:{seconds_remaining:02d}"
        self.countdown_label.setText(countdown_text)
        
        # 更新详细信息
        total_days = (end_of_year - start_of_year).days + 1
        days_passed = total_days - days_remaining
        
        details = f"年份: {year}年\n\n"
        details += f"开始日期: {start_of_year.strftime('%Y-%m-%d')}\n"
        details += f"结束日期: {end_of_year.strftime('%Y-%m-%d')}\n"
        details += f"总天数: {total_days}天\n"
        details += f"已过去: {days_passed}天\n"
        details += f"剩余天数: {days_remaining}天\n"
        details += f"剩余时间: {remaining_percent:.1f}%\n\n"
        
        # 添加季度和月度剩余信息
        quarter_remaining = self.get_quarter_remaining(now)
        month_remaining = self.get_month_remaining(now)
        details += f"当前季度剩余: {quarter_remaining:.1f}%\n"
        details += f"当前月份剩余: {month_remaining:.1f}%"
        
        self.details_text.setPlainText(details)
    
    def get_quarter_remaining(self, now):
        """获取季度剩余百分比"""
        quarter = self.get_current_quarter(now.month)
        
        # 季度开始和结束月份
        if quarter == 1:
            start_month, end_month = 1, 3
        elif quarter == 2:
            start_month, end_month = 4, 6
        elif quarter == 3:
            start_month, end_month = 7, 9
        else:
            start_month, end_month = 10, 12
        
        # 季度开始和结束日期
        quarter_start = datetime(now.year, start_month, 1)
        quarter_end = datetime(now.year, end_month, 
                              self.get_days_in_month(now.year, end_month), 23, 59, 59)
        
        # 计算季度剩余百分比
        quarter_seconds = (quarter_end - quarter_start).total_seconds()
        remaining_seconds = (quarter_end - now).total_seconds()
        
        return (remaining_seconds / quarter_seconds) * 100
    
    def get_month_remaining(self, now):
        """获取月度剩余百分比"""
        year, month = now.year, now.month
        month_end = datetime(year, month, self.get_days_in_month(year, month), 23, 59, 59)
        month_start = datetime(year, month, 1)
        
        # 计算月度剩余百分比
        month_seconds = (month_end - month_start).total_seconds()
        remaining_seconds = (month_end - now).total_seconds()
        
        return (remaining_seconds / month_seconds) * 100
    
    def get_current_quarter(self, month):
        """获取当前季度"""
        if 1 <= month <= 3:
            return 1
        elif 4 <= month <= 6:
            return 2
        elif 7 <= month <= 9:
            return 3
        else:
            return 4
    
    def get_days_in_month(self, year, month):
        """获取月份的天数"""
        if month == 12:
            return 31
        else:
            return (datetime(year, month + 1, 1) - datetime(year, month, 1)).days
    
    def copy_progress(self):
        """复制进度信息到剪贴板"""
        progress_text = self.progress_label.text()
        countdown_text = self.countdown_label.text()
        details = self.details_text.toPlainText()
        
        clipboard_text = f"{progress_text}\n{countdown_text}\n\n{details}"
        
        try:
            from PySide6.QtWidgets import QApplication
            clipboard = QApplication.clipboard()
            clipboard.setText(clipboard_text)
            QMessageBox.information(self, "成功", "进度信息已复制到剪贴板")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"复制失败: {str(e)}")


if __name__ == "__main__":
    # 测试代码
    import sys
    from PySide6.QtWidgets import QApplication
    
    class MockDataManager:
        pass
    
    app = QApplication(sys.argv)
    data_manager = MockDataManager()
    widget = YearProgressWidget(data_manager=data_manager)
    widget.show()
    sys.exit(app.exec())