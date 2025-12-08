# modules/process_design/tabs/process_route_tab.py
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class MSDSManagerTab(QWidget):
    """MSDS管理标签页"""
    
    def __init__(self, data_manager=None, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("MSDS管理 (功能开发中...)"))