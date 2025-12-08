from PySide6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QLabel, 
                               QLineEdit, QPushButton, QGroupBox, QTextEdit,
                               QComboBox, QMessageBox)

class LoanCalculator(QWidget):
    """住房贷款计算器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置贷款计算器UI"""
        layout = QVBoxLayout(self)
        
        # 输入框架
        input_group = QGroupBox("贷款信息")
        input_layout = QGridLayout(input_group)
        
        input_layout.addWidget(QLabel("贷款金额(元):"), 0, 0)
        self.loan_amount = QLineEdit("1000000")
        input_layout.addWidget(self.loan_amount, 0, 1)
        
        input_layout.addWidget(QLabel("贷款年限(年):"), 1, 0)
        self.loan_years = QLineEdit("30")
        input_layout.addWidget(self.loan_years, 1, 1)
        
        input_layout.addWidget(QLabel("年利率(%):"), 2, 0)
        self.loan_rate = QLineEdit("4.5")
        input_layout.addWidget(self.loan_rate, 2, 1)
        
        input_layout.addWidget(QLabel("还款方式:"), 3, 0)
        self.loan_type = QComboBox()
        self.loan_type.addItems(["等额本息", "等额本金"])
        input_layout.addWidget(self.loan_type, 3, 1)
        
        calc_btn = QPushButton("计算")
        calc_btn.clicked.connect(self.calculate_loan)
        input_layout.addWidget(calc_btn, 4, 0, 1, 2)
        
        layout.addWidget(input_group)
        
        # 结果显示框架
        result_group = QGroupBox("计算结果")
        result_layout = QVBoxLayout(result_group)
        
        self.loan_result = QTextEdit()
        self.loan_result.setMaximumHeight(150)
        result_layout.addWidget(self.loan_result)
        
        layout.addWidget(result_group)
        layout.addStretch()
    
    def calculate_loan(self):
        """计算住房贷款"""
        try:
            amount = float(self.loan_amount.text())
            years = int(self.loan_years.text())
            rate = float(self.loan_rate.text()) / 100
            loan_type = self.loan_type.currentText()
            
            months = years * 12
            monthly_rate = rate / 12
            
            if loan_type == "等额本息":
                # 等额本息计算公式
                if monthly_rate == 0:
                    monthly_payment = amount / months
                else:
                    monthly_payment = amount * monthly_rate * (1 + monthly_rate) ** months / ((1 + monthly_rate) ** months - 1)
                
                total_payment = monthly_payment * months
                total_interest = total_payment - amount
                
                result = f"贷款总额: {amount:,.2f} 元\n"
                result += f"贷款期限: {years} 年 ({months} 个月)\n"
                result += f"年利率: {rate*100:.2f}%\n"
                result += f"月利率: {monthly_rate*100:.4f}%\n\n"
                result += f"每月还款: {monthly_payment:,.2f} 元\n"
                result += f"还款总额: {total_payment:,.2f} 元\n"
                result += f"支付利息: {total_interest:,.2f} 元"
                
            else:  # 等额本金
                monthly_principal = amount / months
                total_interest = 0
                monthly_payments = []
                
                for i in range(months):
                    monthly_interest = (amount - i * monthly_principal) * monthly_rate
                    monthly_payment = monthly_principal + monthly_interest
                    monthly_payments.append(monthly_payment)
                    total_interest += monthly_interest
                
                total_payment = amount + total_interest
                first_month_payment = monthly_payments[0]
                last_month_payment = monthly_payments[-1]
                
                result = f"贷款总额: {amount:,.2f} 元\n"
                result += f"贷款期限: {years} 年 ({months} 个月)\n"
                result += f"年利率: {rate*100:.2f}%\n"
                result += f"月利率: {monthly_rate*100:.4f}%\n\n"
                result += f"首月还款: {first_month_payment:,.2f} 元\n"
                result += f"末月还款: {last_month_payment:,.2f} 元\n"
                result += f"还款总额: {total_payment:,.2f} 元\n"
                result += f"支付利息: {total_interest:,.2f} 元"
            
            self.loan_result.setText(result)
            
        except ValueError:
            QMessageBox.critical(self, "错误", "请输入有效的数字")