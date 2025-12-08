# TofuApp\modules\process_design\utils.py
import re
from typing import Optional, List, Dict, Any

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
            
            count = int(count) if count else 1
            
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
        
        count = int(count) if count else 1
        
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

def calculate_density_from_formula(formula: str, phase: str = "liquid") -> Optional[float]:
    """根据分子式和相态估算密度"""
    if not formula:
        return None
    
    elements = extract_elements_from_formula(formula)
    molecular_weight = calculate_molecular_weight(formula)
    
    if not elements or not molecular_weight:
        return None
    
    # 简单的密度估算规则（可根据实际情况扩展）
    if phase == "liquid":
        # 对于液体，简单的经验公式
        return round(molecular_weight / 40, 2) * 1000  # kg/m³
    elif phase == "solid":
        # 对于固体，简单的经验公式
        return round(molecular_weight / 50, 2) * 1000  # kg/m³
    elif phase == "gas":
        # 对于气体，标准条件下的密度
        return round(molecular_weight / 22.4, 2)  # kg/m³
    else:
        return None

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
            
            count = int(count) if count else 1
            
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
            
            count = int(count) if count else 1
            
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