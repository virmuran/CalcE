# TofuApp/modules/process_design/utils/__init__.py
"""
工具函数模块
提供文件操作、数据验证等工具函数
"""
from .file_utils import (
    ensure_directory,
    read_json_file,
    save_json_file,
    read_csv_file,
    save_to_csv,
    save_to_excel,
    get_file_extension,
    is_valid_file_path,
    get_file_size,
    backup_file,
    find_files_by_extension,
    format_file_size,
    load_template_file
)

from .validation_utils import (
    # 安全转换函数
    safe_float,
    safe_int,
    safe_str,
    safe_bool,
    
    # 化学验证函数
    validate_cas_number,
    validate_molecular_formula,
    calculate_molecular_weight,
    extract_elements_from_formula,
    calculate_mass_fraction,
    format_cas_number,
    parse_chemical_formula,
    is_valid_chemical_name,
    
    # 通用验证函数
    validate_email,
    validate_phone,
    validate_date_string,
    validate_number_range,
    validate_required_fields,
    sanitize_input,
    is_valid_filename
)

# 提供便捷导入
__all__ = [
    # 文件操作
    'ensure_directory',
    'read_json_file',
    'save_json_file',
    'read_csv_file',
    'save_to_csv',
    'save_to_excel',
    'get_file_extension',
    'is_valid_file_path',
    'get_file_size',
    'backup_file',
    'find_files_by_extension',
    'format_file_size',
    'load_template_file',
    
    # 安全转换
    'safe_float',
    'safe_int',
    'safe_str',
    'safe_bool',
    
    # 化学验证
    'validate_cas_number',
    'validate_molecular_formula',
    'calculate_molecular_weight',
    'extract_elements_from_formula',
    'calculate_mass_fraction',
    'format_cas_number',
    'parse_chemical_formula',
    'is_valid_chemical_name',
    
    # 通用验证
    'validate_email',
    'validate_phone',
    'validate_date_string',
    'validate_number_range',
    'validate_required_fields',
    'sanitize_input',
    'is_valid_filename'
]