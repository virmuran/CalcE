from PySide6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QLabel, 
                               QLineEdit, QPushButton, QGroupBox, QTextEdit,
                               QMessageBox)

class TaxCalculator(QWidget):
    """个人所得税计算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置个税计算器UI"""
        layout = QVBoxLayout(self)
        
        # 输入框架
        input_group = QGroupBox("收入信息")
        input_layout = QGridLayout(input_group)
        
        # 月收入
        input_layout.addWidget(QLabel("月收入(元):"), 0, 0)
        self.monthly_income = QLineEdit("10000")
        input_layout.addWidget(self.monthly_income, 0, 1)
        
        # 社保公积金
        input_layout.addWidget(QLabel("社保公积金(元):"), 1, 0)
        self.social_security = QLineEdit("2000")
        input_layout.addWidget(self.social_security, 1, 1)
        
        # 专项附加扣除
        input_layout.addWidget(QLabel("专项附加扣除(元):"), 2, 0)
        self.special_deduction = QLineEdit("1000")
        input_layout.addWidget(self.special_deduction, 2, 1)
        
        # 计算按钮
        calc_btn = QPushButton("计算")
        calc_btn.clicked.connect(self.calculate_tax)
        input_layout.addWidget(calc_btn, 3, 0, 1, 2)
        
        layout.addWidget(input_group)
        
        # 结果显示框架
        result_group = QGroupBox("计算结果")
        result_layout = QVBoxLayout(result_group)
        
        self.tax_result = QTextEdit()
        self.tax_result.setMaximumHeight(150)
        result_layout.addWidget(self.tax_result)
        
        layout.addWidget(result_group)
        layout.addStretch()
    
    def calculate_tax(self):
        """计算个人所得税"""
        try:
            monthly_income = float(self.monthly_income.text())
            social_security = float(self.social_security.text())
            special_deduction = float(self.special_deduction.text())
            
            # 个税起征点
            tax_threshold = 5000
            
            # 月度应纳税所得额
            monthly_taxable_income = monthly_income - social_security - special_deduction - tax_threshold
            
            if monthly_taxable_income <= 0:
                monthly_tax = 0
            else:
                # 个税税率表（月度）
                tax_brackets = [
                    (0, 3000, 0.03, 0),
                    (3000, 12000, 0.10, 210),
                    (12000, 25000, 0.20, 1410),
                    (25000, 35000, 0.25, 2660),
                    (35000, 55000, 0.30, 4410),
                    (55000, 80000, 0.35, 7160),
                    (80000, float('inf'), 0.45, 15160)
                ]
                
                monthly_tax = 0
                for bracket in tax_brackets:
                    if monthly_taxable_income > bracket[0] and monthly_taxable_income <= bracket[1]:
                        monthly_tax = monthly_taxable_income * bracket[2] - bracket[3]
                        break
            
            # 年度计算
            annual_income = monthly_income * 12
            annual_tax = monthly_tax * 12
            after_tax_monthly = monthly_income - monthly_tax - social_security
            after_tax_annual = after_tax_monthly * 12
            
            result = f"月收入: {monthly_income:,.2f} 元\n"
            result += f"年收入: {annual_income:,.2f} 元\n"
            result += f"社保公积金: {social_security:,.2f} 元/月\n"
            result += f"专项附加扣除: {special_deduction:,.2f} 元/月\n\n"
            result += f"月度应纳税所得额: {monthly_taxable_income:,.2f} 元\n"
            result += f"月度个人所得税: {monthly_tax:,.2f} 元\n"
            result += f"年度个人所得税: {annual_tax:,.2f} 元\n\n"
            result += f"税后月收入: {after_tax_monthly:,.2f} 元\n"
            result += f"税后年收入: {after_tax_annual:,.2f} 元"
            
            self.tax_result.setText(result)
            
        except ValueError:
            QMessageBox.critical(self, "错误", "请输入有效的数字")