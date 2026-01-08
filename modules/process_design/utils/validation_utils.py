# TofuApp/modules/process_design/utils/validation_utils.py
"""
验证和数据处理工具函数
"""
import re
from typing import Optional, List, Dict, Any, Union
import traceback

# ==================== 安全转换函数 ====================

def safe_float(value: Any, default: float = 0.0) -> float:
    """
    安全地将值转换为浮点数
    
    参数:
        value: 要转换的值
        default: 转换失败时的默认值
    
    返回:
        转换后的浮点数
    """
    if value is None:
        return default
    
    try:
        if isinstance(value, (int, float)):
            return float(value)
        elif isinstance(value, str):
            cleaned = value.strip()
            # 处理常见的非数值标记
            non_numeric = ['NT', 'NP', 'N/A', 'NA', 'NULL', 'NONE', '-', '--', '', '空', '空缺', '常温', '常压', '未指定', '未设置']
            if cleaned.upper() in [n.upper() for n in non_numeric]:
                return default
            # 移除中文单位和其他非数字字符（但保留小数点和负号）
            cleaned = re.sub(r'[^\d.-]', '', cleaned)
            if cleaned == '' or cleaned == '-':
                return default
            return float(cleaned)
        else:
            # 尝试强制转换
            return float(value)
    except (ValueError, TypeError, AttributeError) as e:
        print(f"❌ 安全转换浮点数失败: {e}, 值: {value}, 类型: {type(value)}")
        traceback.print_exc()
        return default

def safe_int(value: Any, default: int = 0) -> int:
    """
    安全地将值转换为整数
    
    参数:
        value: 要转换的值
        default: 转换失败时的默认值
    
    返回:
        转换后的整数
    """
    if value is None:
        return default
    
    try:
        if isinstance(value, (int, float)):
            return int(value)
        elif isinstance(value, str):
            cleaned = value.strip()
            # 处理常见的非数值标记
            non_numeric = ['NT', 'NP', 'N/A', 'NA', 'NULL', 'NONE', '-', '--', '', '空', '空缺']
            if cleaned.upper() in [n.upper() for n in non_numeric]:
                return default
            # 移除非数字字符
            cleaned = re.sub(r'[^\d-]', '', cleaned)
            if cleaned == '' or cleaned == '-':
                return default
            return int(float(cleaned))  # 先转浮点数再转整数，以处理小数
        else:
            return int(value)
    except (ValueError, TypeError, AttributeError):
        return default

def safe_str(value: Any, default: str = "") -> str:
    """
    安全地将值转换为字符串
    
    参数:
        value: 要转换的值
        default: 转换失败时的默认值
    
    返回:
        转换后的字符串
    """
    try:
        if value is None:
            return default
        return str(value)
    except:
        return default

def safe_bool(value: Any, default: bool = False) -> bool:
    """
    安全地将值转换为布尔值
    
    参数:
        value: 要转换的值
        default: 转换失败时的默认值
    
    返回:
        转换后的布尔值
    """
    if value is None:
        return default
    
    if isinstance(value, bool):
        return value
    
    if isinstance(value, (int, float)):
        return bool(value)
    
    if isinstance(value, str):
        true_values = ['true', 'yes', 'y', 't', '1', 'on', '是', '真']
        false_values = ['false', 'no', 'n', 'f', '0', 'off', '否', '假']
        
        cleaned = value.strip().lower()
        if cleaned in true_values:
            return True
        elif cleaned in false_values:
            return False
    
    return default

# ==================== 化学相关验证函数 ====================

def validate_cas_number(cas_number: str) -> bool:
    """验证CAS号格式"""
    if not cas_number:
        return True
    
    # CAS号格式: XXXXXXX-XX-X
    pattern = r'^\d{1,7}-\d{2}-\d$'
    return bool(re.match(pattern, cas_number))

def validate_molecular_formula(formula: str) -> bool:
    """验证分子式格式"""
    if not formula:
        return True
    
    # 简单验证：首字母大写，包含字母和数字
    pattern = r'^[A-Z][a-z]?\d*([A-Z][a-z]?\d*)*$'
    return bool(re.match(pattern, formula))

def calculate_molecular_weight(formula: str) -> Optional[float]:
    """根据分子式计算分子量（简单实现）"""
    if not formula:
        return None
    
    # 原子量字典
    atomic_weights = {
        'H': 1.008, 'C': 12.011, 'N': 14.007, 'O': 15.999,
        'F': 18.998, 'Na': 22.990, 'Mg': 24.305, 'Al': 26.982,
        'Si': 28.086, 'P': 30.974, 'S': 32.06, 'Cl': 35.45,
        'K': 39.098, 'Ca': 40.078, 'Fe': 55.845, 'Cu': 63.546,
        'Zn': 65.38, 'Br': 79.904, 'Ag': 107.868, 'I': 126.904,
        'He': 4.003, 'Ne': 20.180, 'Ar': 39.948, 'Kr': 83.798,
        'Xe': 131.293, 'Rn': 222.018, 'U': 238.029, 'Pu': 244.064
    }
    
    try:
        # 简单解析分子式（实际实现需要更复杂的解析）
        total_weight = 0.0
        i = 0
        while i < len(formula):
            # 解析元素符号
            element = formula[i]
            if i + 1 < len(formula) and formula[i+1].islower():
                element += formula[i+1]
                i += 1
            
            # 解析数量
            i += 1
            count = ""
            while i < len(formula) and formula[i].isdigit():
                count += formula[i]
                i += 1
            
            count = safe_int(count, 1)
            
            # 计算重量
            if element in atomic_weights:
                total_weight += atomic_weights[element] * count
            else:
                print(f"未知元素: {element}")
                return None
        
        return round(total_weight, 2)
    except Exception as e:
        print(f"计算分子量失败: {e}")
        return None

def extract_elements_from_formula(formula: str) -> Dict[str, int]:
    """从分子式中提取元素及其数量"""
    if not formula:
        return {}
    
    elements = {}
    i = 0
    
    while i < len(formula):
        # 解析元素符号
        element = formula[i]
        if i + 1 < len(formula) and formula[i+1].islower():
            element += formula[i+1]
            i += 1
        
        # 解析数量
        i += 1
        count = ""
        while i < len(formula) and formula[i].isdigit():
            count += formula[i]
            i += 1
        
        count = safe_int(count, 1)
        
        # 添加到元素字典
        if element in elements:
            elements[element] += count
        else:
            elements[element] = count
    
    return elements

def calculate_mass_fraction(formula: str, element: str) -> Optional[float]:
    """计算分子式中某元素的质量分数"""
    if not formula or not element:
        return None
    
    # 获取元素组成
    elements = extract_elements_from_formula(formula)
    if not elements:
        return None
    
    # 获取目标元素的数量
    element_count = elements.get(element, 0)
    if element_count == 0:
        return 0.0
    
    # 计算分子量
    molecular_weight = calculate_molecular_weight(formula)
    if not molecular_weight:
        return None
    
    # 计算元素的质量
    atomic_weights = {
        'H': 1.008, 'C': 12.011, 'N': 14.007, 'O': 15.999,
        'F': 18.998, 'Na': 22.990, 'Mg': 24.305, 'Al': 26.982,
        'Si': 28.086, 'P': 30.974, 'S': 32.06, 'Cl': 35.45
    }
    
    element_weight = atomic_weights.get(element, 0)
    if element_weight == 0:
        return None
    
    # 计算质量分数
    mass_fraction = (element_count * element_weight) / molecular_weight
    return round(mass_fraction * 100, 2)  # 返回百分比

def format_cas_number(cas_number: str) -> str:
    """格式化CAS号"""
    if not cas_number:
        return ""
    
    # 移除所有非数字和破折号字符
    cleaned = re.sub(r'[^\d-]', '', cas_number)
    
    # 确保格式正确
    parts = cleaned.split('-')
    if len(parts) == 3:
        return f"{parts[0]}-{parts[1]}-{parts[2]}"
    elif len(parts) == 1 and len(parts[0]) >= 6:
        # 尝试自动格式化
        num = parts[0]
        if len(num) >= 6:
            return f"{num[:-2]}-{num[-2:]}-{num[-1]}"
    
    return cleaned

def parse_chemical_formula(formula: str) -> List[Dict[str, Any]]:
    """解析化学式为结构化数据"""
    if not formula:
        return []
    
    result = []
    i = 0
    
    while i < len(formula):
        # 处理括号
        if formula[i] == '(':
            j = i + 1
            bracket_count = 1
            while j < len(formula) and bracket_count > 0:
                if formula[j] == '(':
                    bracket_count += 1
                elif formula[j] == ')':
                    bracket_count -= 1
                j += 1
            
            sub_formula = formula[i+1:j-1]
            i = j
            
            # 解析括号后的数字
            count = ""
            while i < len(formula) and formula[i].isdigit():
                count += formula[i]
                i += 1
            
            count = safe_int(count, 1)
            
            result.append({
                "type": "group",
                "formula": sub_formula,
                "count": count
            })
        else:
            # 解析元素
            element = formula[i]
            if i + 1 < len(formula) and formula[i+1].islower():
                element += formula[i+1]
                i += 1
            
            i += 1
            
            # 解析数量
            count = ""
            while i < len(formula) and formula[i].isdigit():
                count += formula[i]
                i += 1
            
            count = safe_int(count, 1)
            
            result.append({
                "type": "element",
                "element": element,
                "count": count
            })
    
    return result

def is_valid_chemical_name(name: str) -> bool:
    """验证化学品名称是否有效"""
    if not name or len(name.strip()) < 2:
        return False
    
    # 允许字母、数字、空格、括号、连字符
    pattern = r'^[a-zA-Z0-9\u4e00-\u9fa5\s\(\)-]+$'
    return bool(re.match(pattern, name))

# ==================== 通用验证函数 ====================

def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """验证手机号码格式（中国）"""
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))

def validate_date_string(date_str: str, date_format: str = "%Y-%m-%d") -> bool:
    """验证日期字符串格式"""
    try:
        from datetime import datetime
        datetime.strptime(date_str, date_format)
        return True
    except ValueError:
        return False

def validate_number_range(value: Union[int, float, str], 
                         min_val: Optional[Union[int, float]] = None, 
                         max_val: Optional[Union[int, float]] = None) -> bool:
    """验证数字范围"""
    try:
        num = safe_float(value)
        
        if min_val is not None and num < min_val:
            return False
        
        if max_val is not None and num > max_val:
            return False
        
        return True
    except:
        return False

def validate_required_fields(data: Dict[str, Any], 
                           required_fields: List[str]) -> List[str]:
    """
    验证必填字段
    
    参数:
        data: 数据字典
        required_fields: 必填字段列表
    
    返回:
        错误消息列表
    """
    errors = []
    
    for field in required_fields:
        if field not in data or data[field] is None or str(data[field]).strip() == '':
            errors.append(f"字段 '{field}' 为必填项")
    
    return errors

def sanitize_input(text: str) -> str:
    """
    清理用户输入，防止SQL注入和XSS攻击
    
    参数:
        text: 输入文本
    
    返回:
        清理后的文本
    """
    if not text:
        return ""
    
    # 移除SQL关键字
    sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'UNION', 'OR', 'AND']
    cleaned = text.upper()
    for keyword in sql_keywords:
        cleaned = cleaned.replace(keyword, '')
    
    # 转义HTML特殊字符
    html_entities = {
        '<': '&lt;',
        '>': '&gt;',
        '&': '&amp;',
        '"': '&quot;',
        "'": '&#39;',
        '/': '&#x2F;'
    }
    
    for char, entity in html_entities.items():
        cleaned = cleaned.replace(char, entity)
    
    return cleaned

def is_valid_filename(filename: str) -> bool:
    """验证文件名是否有效"""
    if not filename or len(filename) > 255:
        return False
    
    # 检查非法字符
    illegal_chars = '<>:"/\\|?*'
    if any(char in filename for char in illegal_chars):
        return False
    
    # 检查Windows保留文件名
    reserved_names = [
        'CON', 'PRN', 'AUX', 'NUL',
        'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
        'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'
    ]
    
    name_without_ext = filename.split('.')[0].upper()
    if name_without_ext in reserved_names:
        return False
    
    return True