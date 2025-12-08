# pomodoro.py
import time
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QLineEdit, QMessageBox, QGroupBox, QFrame
)
from PySide6.QtCore import Qt, QTimer, QTime
from PySide6.QtGui import QFont, QPalette, QColor, QLinearGradient


class PomodoroTimer(QWidget):
    """番茄时钟模块 (PySide6版本) - 现代化UI"""
    
    def __init__(self, parent=None, data_manager=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.is_running = False
        self.is_break = False
        self.remaining_time = 25 * 60  # 默认25分钟
        self.work_duration = 25 * 60
        self.break_duration = 5 * 60
        
        self.setup_ui()
        
        # 设置定时器
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        
        # 更新统计信息
        self.update_stats()
    
    def setup_ui(self):
        """设置番茄时钟UI - 现代化设计"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        # 主框架 - 使用卡片式设计
        main_group = QGroupBox("🍅 番茄时钟")
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
        
        # 计时器显示 - 大型数字显示
        self.time_label = QLabel("25:00")
        self.time_label.setFont(QFont("Arial", 48, QFont.Bold))
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("""
            QLabel {
                color: #e74c3c;
                background-color: #fdf2f2;
                border: 3px solid #e74c3c;
                border-radius: 15px;
                padding: 20px;
                margin: 10px;
            }
        """)
        group_layout.addWidget(self.time_label)
        
        # 状态显示
        self.status_label = QLabel("准备开始")
        self.status_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                background-color: #ecf0f1;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        group_layout.addWidget(self.status_label)
        
        # 控制按钮框架 - 现代化按钮设计
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.start_button = QPushButton("▶ 开始")
        self.start_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.start_button.clicked.connect(self.start_timer)
        self.start_button.setStyleSheet("""
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
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        button_layout.addWidget(self.start_button)
        
        self.pause_button = QPushButton("⏸️ 暂停")
        self.pause_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.pause_button.clicked.connect(self.pause_timer)
        self.pause_button.setEnabled(False)
        self.pause_button.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        button_layout.addWidget(self.pause_button)
        
        self.reset_button = QPushButton("🔄 重置")
        self.reset_button.setFont(QFont("Arial", 12, QFont.Bold))
        self.reset_button.clicked.connect(self.reset_timer)
        self.reset_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        button_layout.addWidget(self.reset_button)
        
        group_layout.addLayout(button_layout)
        
        # 设置框架
        settings_group = QGroupBox("⚙️ 时间设置")
        settings_group.setStyleSheet("""
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
        group_layout.addWidget(settings_group)
        
        settings_layout = QHBoxLayout(settings_group)
        settings_layout.setSpacing(10)
        
        # 工作时间设置
        work_layout = QVBoxLayout()
        work_layout.addWidget(QLabel("工作时间"))
        self.work_edit = QLineEdit("25")
        self.work_edit.setMaximumWidth(70)
        self.work_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        work_layout.addWidget(self.work_edit)
        settings_layout.addLayout(work_layout)
        
        # 休息时间设置
        break_layout = QVBoxLayout()
        break_layout.addWidget(QLabel("休息时间"))
        self.break_edit = QLineEdit("5")
        self.break_edit.setMaximumWidth(70)
        self.break_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                padding: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        break_layout.addWidget(self.break_edit)
        settings_layout.addLayout(break_layout)
        
        apply_button = QPushButton("应用设置")
        apply_button.setFont(QFont("Arial", 10))
        apply_button.clicked.connect(self.apply_settings)
        apply_button.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
                margin-top: 15px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        settings_layout.addWidget(apply_button)
        
        settings_layout.addStretch()
        
        # 统计信息
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        stats_layout = QVBoxLayout(stats_frame)
        
        self.stats_label = QLabel("今日已完成: 0个番茄钟")
        self.stats_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.stats_label.setAlignment(Qt.AlignCenter)
        self.stats_label.setStyleSheet("color: #ecf0f1;")
        stats_layout.addWidget(self.stats_label)
        
        group_layout.addWidget(stats_frame)
        
        group_layout.addStretch()
    
    def start_timer(self):
        """开始计时"""
        if not self.is_running:
            self.is_running = True
            self.start_button.setEnabled(False)
            self.pause_button.setEnabled(True)
            
            # 更新按钮状态
            self.start_button.setText("▶ 进行中")
            
            # 启动定时器，每秒触发一次
            self.timer.start(1000)
            
            # 更新状态和颜色
            self.update_status_display()
    
    def pause_timer(self):
        """暂停计时"""
        if self.is_running:
            self.is_running = False
            self.timer.stop()
            self.start_button.setEnabled(True)
            self.pause_button.setEnabled(False)
            
            # 更新按钮状态
            self.start_button.setText("▶ 继续")
            
            self.status_label.setText("⏸️ 已暂停")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #2c3e50;
                    background-color: #f39c12;
                    border-radius: 8px;
                    padding: 8px;
                }
            """)
    
    def reset_timer(self):
        """重置计时器"""
        self.is_running = False
        self.timer.stop()
        self.is_break = False
        self.remaining_time = self.work_duration
        self.update_display()
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        
        # 重置按钮状态
        self.start_button.setText("▶ 开始")
        
        self.status_label.setText("🔄 准备开始")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                background-color: #ecf0f1;
                border-radius: 8px;
                padding: 8px;
            }
        """)
    
    def apply_settings(self):
        """应用设置"""
        try:
            work_minutes = int(self.work_edit.text())
            break_minutes = int(self.break_edit.text())
            
            if work_minutes <= 0 or break_minutes <= 0:
                QMessageBox.critical(self, "错误", "⏰ 时间必须大于0分钟")
                return
            
            if work_minutes > 120 or break_minutes > 60:
                QMessageBox.warning(self, "提示", "⚠️ 建议工作时间不超过120分钟，休息时间不超过60分钟")
            
            self.work_duration = work_minutes * 60
            self.break_duration = break_minutes * 60
            
            if not self.is_running:
                self.remaining_time = self.work_duration
                self.update_display()
            
            QMessageBox.information(self, "成功", "✅ 时间设置已应用")
        except ValueError:
            QMessageBox.critical(self, "错误", "❌ 请输入有效的数字")
    
    def update_timer(self):
        """定时器更新回调"""
        if self.is_running and self.remaining_time > 0:
            self.remaining_time -= 1
            self.update_display()
        
        if self.is_running and self.remaining_time <= 0:
            self.timer_complete()
    
    def timer_complete(self):
        """计时完成"""
        self.is_running = False
        self.timer.stop()
        self.is_break = not self.is_break
        
        if self.is_break:
            self.remaining_time = self.break_duration
            QMessageBox.information(self, "🍅 番茄时钟", "✅ 工作时间结束! 开始休息。")
        else:
            self.remaining_time = self.work_duration
            QMessageBox.information(self, "🍅 番茄时钟", "🔄 休息时间结束! 开始工作。")
            
            # 记录完成的番茄钟
            session = {
                "completed_at": datetime.now().isoformat(),
                "duration": self.work_duration
            }
            self.data_manager.data.setdefault("pomodoro_sessions", []).append(session)
            self.data_manager.save_data()
            
            # 更新统计信息
            self.update_stats()
        
        # 更新状态显示
        self.update_status_display()
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.start_button.setText("▶ 开始")
        self.update_display()
    
    def update_display(self):
        """更新显示"""
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.time_label.setText(f"{minutes:02d}:{seconds:02d}")
    
    def update_status_display(self):
        """更新状态显示"""
        if self.is_break:
            status = "☕ 休息中"
            status_color = """
                QLabel {
                    color: #2c3e50;
                    background-color: #2ecc71;
                    border-radius: 8px;
                    padding: 8px;
                }
            """
            time_color = """
                QLabel {
                    color: #27ae60;
                    background-color: #d5f4e6;
                    border: 3px solid #27ae60;
                    border-radius: 15px;
                    padding: 20px;
                    margin: 10px;
                }
            """
        else:
            status = "💼 工作中"
            status_color = """
                QLabel {
                    color: #2c3e50;
                    background-color: #e74c3c;
                    border-radius: 8px;
                    padding: 8px;
                }
            """
            time_color = """
                QLabel {
                    color: #e74c3c;
                    background-color: #fdf2f2;
                    border: 3px solid #e74c3c;
                    border-radius: 15px;
                    padding: 20px;
                    margin: 10px;
                }
            """
        
        if self.is_running:
            status += " - 进行中"
        
        self.status_label.setText(status)
        self.status_label.setStyleSheet(status_color)
        self.time_label.setStyleSheet(time_color)
    
    def update_stats(self):
        """更新统计信息"""
        sessions = self.data_manager.data.get("pomodoro_sessions", [])
        
        # 计算今日完成的番茄钟
        today = datetime.now().date()
        today_sessions = [
            session for session in sessions 
            if datetime.fromisoformat(session["completed_at"]).date() == today
        ]
        
        # 计算总番茄钟
        total_sessions = len(sessions)
        
        self.stats_label.setText(f"今日: {len(today_sessions)}个番茄钟\n总计: {total_sessions}个番茄钟")


if __name__ == "__main__":
    # 测试代码
    import sys
    from PySide6.QtWidgets import QApplication
    
    class MockDataManager:
        def __init__(self):
            self.data = {
                "pomodoro_sessions": []
            }
        
        def save_data(self):
            print("数据已保存:", self.data)
    
    app = QApplication(sys.argv)
    data_manager = MockDataManager()
    widget = PomodoroTimer(data_manager=data_manager)
    widget.resize(400, 500)
    widget.show()
    sys.exit(app.exec())