from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class ScipyMissingCalculator(QWidget):
    """Scipy缺失提示页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # 警告图标和标题
        title_label = QLabel("⚠️ 高级功能需要 SciPy 库")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #e74c3c; margin: 20px;")
        layout.addWidget(title_label)
        
        # 说明文本
        explanation = QTextEdit()
        explanation.setReadOnly(True)
        explanation.setHtml("""
        <div style="font-family: Arial; font-size: 14px; line-height: 1.6;">
            <h3 style="color: #2c3e50;">缺少 SciPy 科学计算库</h3>
            
            <p>以下高级功能需要 SciPy 库支持：</p>
            
            <ul>
                <li>🌪️ 可压缩流体压降计算</li>
                <li>🔥 长输蒸汽管道温降计算</li>
                <li>⚗️ 气液平衡计算</li>
                <li>🌫️ 气体混合物物性计算</li>
                <li>⚛️ 状态方程计算</li>
                <li>❄️ 制冷剂物性计算</li>
            </ul>
            
            <h3 style="color: #27ae60;">安装方法</h3>
            
            <p>请运行以下命令安装 SciPy：</p>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef;">
                <code style="font-family: 'Courier New', monospace; font-size: 16px;">
                    pip install scipy numpy
                </code>
            </div>
            
            <p style="margin-top: 20px;">
                <strong>或者使用清华镜像加速下载：</strong>
            </p>
            
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; border: 1px solid #e9ecef;">
                <code style="font-family: 'Courier New', monospace; font-size: 16px;">
                    pip install scipy numpy -i https://pypi.tuna.tsinghua.edu.cn/simple
                </code>
            </div>
            
            <p style="margin-top: 20px;">
                <strong>注意：</strong>安装完成后需要重启应用程序。
            </p>
            
            <h3 style="color: #3498db;">当前可用功能</h3>
            
            <p>以下基础功能仍可正常使用：</p>
            
            <ul>
                <li>📊 管道压降计算</li>
                <li>📏 管径计算</li>
                <li>📐 管道跨距计算</li>
                <li>💨 蒸汽管径查询</li>
                <li>🌫️ 水蒸气物性</li>
                <li>⚡ 泵功率计算</li>
                <li>💧 NPSHa计算</li>
                <li>🔄 管道补偿</li>
                <li>🌬️ 气体状态转换</li>
                <li>🔧 压力管道定义</li>
                <li>🚒 消火栓计算</li>
                <li>⚖️ 罐体重量计算</li>
                <li>🧊 保温厚度计算</li>
                <li>⚠️ 腐蚀数据查询</li>
                <li>🧪 纯物质物性</li>
                <li>🔩 法兰尺寸查询</li>
                <li>🛡️ 安全阀计算</li>
                <li>💨 湿空气计算</li>
                <li>🌬️ 风机功率计算</li>
                <li>🚨 泄压面积计算</li>
                <li>🔥 换热器计算</li>
                <li>🧪 固体溶解度查询</li>
                <li>🔄 制冷循环计算</li>
                <li>📏 管道壁厚计算</li>
                <li>🔥 混合液体闪点计算</li>
                <li>⚠️ 危险化学品查询</li>
            </ul>
        </div>
        """)
        layout.addWidget(explanation)
        
        layout.addStretch()


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    widget = ScipyMissingCalculator()
    widget.resize(600, 500)
    widget.show()
    sys.exit(app.exec())