# modules/process_design/tabs/equipment_properties.py
import re
from typing import List, Tuple, Any, Optional


class EquipmentPropertiesExtractor:
    """设备技术参数提取器"""
    
    @staticmethod
    def get_properties_by_equipment_type(equipment_type: str, equipment: Any) -> List[Tuple[str, str]]:
        """根据新设备类型返回要显示的技术参数列表"""
        
        properties = []
        
        # 通用参数
        common_properties = [
            ("设计压力", EquipmentPropertiesExtractor._format_parameter(equipment.design_pressure, "MPa", 2)),
            ("设计温度", EquipmentPropertiesExtractor._format_parameter(equipment.design_temperature, "°C", 1)),
            ("操作压力", EquipmentPropertiesExtractor._format_parameter(equipment.operating_pressure, "MPa", 2)),
            ("操作温度", EquipmentPropertiesExtractor._format_parameter(equipment.operating_temperature, "°C", 1)),
            ("单机功率", f"{getattr(equipment, 'single_power', 0):.1f} kW" if getattr(equipment, 'single_power', 0) else "未知"),
            ("装机功率", f"{getattr(equipment, 'total_power', 0):.1f} kW" if getattr(equipment, 'total_power', 0) else "未知"),
            ("材质", getattr(equipment, 'material', '未知')),
        ]
        
        # 根据新设备类型添加特定参数
        if equipment_type == "A 搅拌设备类":
            specific_properties = EquipmentPropertiesExtractor._get_agitator_properties(equipment)
        elif equipment_type == "B 风机类":
            specific_properties = EquipmentPropertiesExtractor._get_fan_properties(equipment)
        elif equipment_type == "C 塔器":
            specific_properties = EquipmentPropertiesExtractor._get_tower_properties(equipment)
        elif equipment_type == "D 槽罐":
            specific_properties = EquipmentPropertiesExtractor._get_trough_tank_properties(equipment)
        elif equipment_type == "E 换热设备类":
            specific_properties = EquipmentPropertiesExtractor._get_heatexchanger_properties(equipment)
        elif equipment_type == "G 成粒成型设备类":
            specific_properties = EquipmentPropertiesExtractor._get_forming_properties(equipment)
        elif equipment_type == "H 贮斗、料斗类":
            specific_properties = EquipmentPropertiesExtractor._get_hopper_properties(equipment)
        elif equipment_type == "J 喷射器类":
            specific_properties = EquipmentPropertiesExtractor._get_injector_properties(equipment)
        elif equipment_type == "K 压缩机类":
            specific_properties = EquipmentPropertiesExtractor._get_compressor_properties(equipment)
        elif equipment_type == "L 起重、装卸、包装机械设备类":
            specific_properties = EquipmentPropertiesExtractor._get_lifting_properties(equipment)
        elif equipment_type == "M 磨碎设备类、混合器类":
            specific_properties = EquipmentPropertiesExtractor._get_mixer_grinder_properties(equipment)
        elif equipment_type == "P 泵类":
            specific_properties = EquipmentPropertiesExtractor._get_pump_properties(equipment)
        elif equipment_type == "R 反应器":
            specific_properties = EquipmentPropertiesExtractor._get_reactor_properties(equipment)
        elif equipment_type == "S 分离设备类":
            specific_properties = EquipmentPropertiesExtractor._get_separator_properties(equipment)
        elif equipment_type == "T 储罐":
            specific_properties = EquipmentPropertiesExtractor._get_tank_properties(equipment)
        elif equipment_type == "U 公用辅助设备类":
            specific_properties = EquipmentPropertiesExtractor._get_utility_properties(equipment)
        elif equipment_type == "V 固体输送类（刮板机、铰刀、提升机、皮带机）":
            specific_properties = EquipmentPropertiesExtractor._get_conveyor_properties(equipment)
        elif equipment_type == "W 称重类设备":
            specific_properties = EquipmentPropertiesExtractor._get_weighing_properties(equipment)
        elif equipment_type == "X 成套设备类":
            specific_properties = EquipmentPropertiesExtractor._get_package_properties(equipment)
        else:
            specific_properties = EquipmentPropertiesExtractor._get_other_properties(equipment)
        
        # 合并通用参数和特定参数
        properties.extend(common_properties)
        properties.extend(specific_properties)
        
        return properties
    
    @staticmethod
    def _get_agitator_properties(equipment):
        """获取搅拌设备类特有参数"""
        properties = []
        
        spec_str = getattr(equipment, 'specification', '')
        
        # 搅拌转速
        agitation_match = re.search(r'搅拌转速[:：]\s*([\d\.]+)\s*rpm', spec_str)
        if agitation_match:
            properties.append(("搅拌转速", f"{agitation_match.group(1)} rpm"))
        
        # 搅拌功率
        power_match = re.search(r'搅拌功率[:：]\s*([\d\.]+)\s*kW', spec_str)
        if power_match:
            properties.append(("搅拌功率", f"{power_match.group(1)} kW"))
        
        # 搅拌直径
        diameter_match = re.search(r'搅拌直径[:：]\s*([\d\.]+)\s*mm', spec_str)
        if diameter_match:
            properties.append(("搅拌直径", f"{diameter_match.group(1)} mm"))
        
        # 搅拌类型
        type_match = re.search(r'搅拌类型[:：]\s*(\w+)', spec_str)
        if type_match:
            properties.append(("搅拌类型", type_match.group(1)))
        
        return properties

    @staticmethod
    def _get_fan_properties(equipment):
        """获取风机类特有参数"""
        properties = []
        
        spec_str = getattr(equipment, 'specification', '')
        
        # 风量
        flow_match = re.search(r'风量[:：]\s*([\d\.]+)\s*m³/h', spec_str)
        if flow_match:
            properties.append(("风量", f"{flow_match.group(1)} m³/h"))
        
        # 风压
        pressure_match = re.search(r'风压[:：]\s*([\d\.]+)\s*Pa', spec_str)
        if pressure_match:
            properties.append(("风压", f"{pressure_match.group(1)} Pa"))
        
        # 转速
        speed_match = re.search(r'转速[:：]\s*([\d\.]+)\s*rpm', spec_str)
        if speed_match:
            properties.append(("转速", f"{speed_match.group(1)} rpm"))
        
        return properties

    @staticmethod
    def _get_tower_properties(equipment):
        """获取塔器特有参数"""
        properties = []
        
        spec_str = getattr(equipment, 'specification', '')
        
        # 塔径
        diameter_match = re.search(r'塔径[:：]\s*([\d\.]+)\s*mm', spec_str)
        if diameter_match:
            properties.append(("塔径", f"{diameter_match.group(1)} mm"))
        
        # 塔高
        height_match = re.search(r'塔高[:：]\s*([\d\.]+)\s*mm', spec_str)
        if height_match:
            properties.append(("塔高", f"{height_match.group(1)} mm"))
        
        # 填料高度
        packing_match = re.search(r'填料高度[:：]\s*([\d\.]+)\s*mm', spec_str)
        if packing_match:
            properties.append(("填料高度", f"{packing_match.group(1)} mm"))
        
        return properties

    @staticmethod
    def _get_trough_tank_properties(equipment):
        """获取槽罐特有参数"""
        properties = []
        
        spec_str = getattr(equipment, 'specification', '')
        
        # 尝试从规格中提取长度、宽度和高度
        length = None
        width = None
        height = None
        volume = None
        
        # 长度
        length_match = re.search(r'长度[:：]\s*([\d\.]+)\s*mm', spec_str)
        if length_match:
            length = float(length_match.group(1))
            properties.append(("长度", f"{length} mm"))
        
        # 宽度
        width_match = re.search(r'宽度[:：]\s*([\d\.]+)\s*mm', spec_str)
        if width_match:
            width = float(width_match.group(1))
            properties.append(("宽度", f"{width} mm"))
        
        # 高度
        height_match = re.search(r'高度[:：]\s*([\d\.]+)\s*mm', spec_str)
        if height_match:
            height = float(height_match.group(1))
            properties.append(("高度", f"{height} mm"))
        
        # 容积 - 首先尝试从规格中提取
        volume_match = re.search(r'容积[:：]\s*([\d\.]+)\s*m³', spec_str)
        if volume_match:
            volume = float(volume_match.group(1))
            properties.append(("容积", f"{volume} m³"))
        else:
            # 如果规格中没有容积，但有了长、宽、高，尝试计算
            if length and width and height:
                # 将毫米转换为米
                length_m = length / 1000.0
                width_m = width / 1000.0
                height_m = height / 1000.0
                
                # 计算长方体体积
                calculated_volume = length_m * width_m * height_m
                
                properties.append(("容积", f"{calculated_volume:.3f} m³ (计算值)"))
            else:
                properties.append(("容积", "未知"))
        
        # 壁厚
        thickness_match = re.search(r'壁厚[:：]\s*([\d\.]+)\s*mm', spec_str)
        if thickness_match:
            properties.append(("壁厚", f"{thickness_match.group(1)} mm"))
        
        # 材质
        material_match = re.search(r'材质[:：]\s*(\w+)', spec_str)
        if material_match:
            properties.append(("材质", material_match.group(1)))
        
        # 设计液位
        level_match = re.search(r'设计液位[:：]\s*([\d\.]+)\s*m', spec_str)
        if level_match:
            properties.append(("设计液位", f"{level_match.group(1)} m"))
        
        return properties
    
    @staticmethod
    def _get_heatexchanger_properties(equipment):
        """获取换热设备类特有参数"""
        properties = []
        
        spec_str = getattr(equipment, 'specification', '')
        
        # 换热面积
        area_match = re.search(r'换热面积[:：]\s*([\d\.]+)\s*m²', spec_str)
        if area_match:
            properties.append(("换热面积", f"{area_match.group(1)} m²"))
        
        # 管程数
        tube_passes_match = re.search(r'管程数[:：]\s*(\d+)', spec_str)
        if tube_passes_match:
            properties.append(("管程数", tube_passes_match.group(1)))
        
        # 壳程数
        shell_passes_match = re.search(r'壳程数[:：]\s*(\d+)', spec_str)
        if shell_passes_match:
            properties.append(("壳程数", shell_passes_match.group(1)))
        
        # 管径
        tube_dia_match = re.search(r'管径[:：]\s*([\d\.]+)\s*mm', spec_str)
        if tube_dia_match:
            properties.append(("管径", f"{tube_dia_match.group(1)} mm"))
        
        # 管长
        tube_len_match = re.search(r'管长[:：]\s*([\d\.]+)\s*mm', spec_str)
        if tube_len_match:
            properties.append(("管长", f"{tube_len_match.group(1)} mm"))
        
        # 设计温度（管程/壳程）
        design_temp_match = re.search(r'设计温度[:：]\s*管程\s*([\d\.]+)\s*°C[/、]\s*壳程\s*([\d\.]+)\s*°C', spec_str)
        if design_temp_match:
            properties.append(("设计温度(管程/壳程)", f"{design_temp_match.group(1)} / {design_temp_match.group(2)} °C"))
        
        # 设计压力（管程/壳程）
        design_pressure_match = re.search(r'设计压力[:：]\s*管程\s*([\d\.]+)\s*MPa[/、]\s*壳程\s*([\d\.]+)\s*MPa', spec_str)
        if design_pressure_match:
            properties.append(("设计压力(管程/壳程)", f"{design_pressure_match.group(1)} / {design_pressure_match.group(2)} MPa"))
        
        return properties

    @staticmethod
    def _get_forming_properties(equipment):
        """获取成粒成型设备类特有参数"""
        properties = []
        
        spec_str = getattr(equipment, 'specification', '')
        
        # 生产能力
        capacity_match = re.search(r'生产能力[:：]\s*([\d\.]+)\s*kg/h', spec_str)
        if capacity_match:
            properties.append(("生产能力", f"{capacity_match.group(1)} kg/h"))
        
        # 颗粒直径
        diameter_match = re.search(r'颗粒直径[:：]\s*([\d\.]+)\s*mm', spec_str)
        if diameter_match:
            properties.append(("颗粒直径", f"{diameter_match.group(1)} mm"))
        
        # 成型方式
        method_match = re.search(r'成型方式[:：]\s*(\w+)', spec_str)
        if method_match:
            properties.append(("成型方式", method_match.group(1)))
        
        # 电机功率
        power_match = re.search(r'电机功率[:：]\s*([\d\.]+)\s*kW', spec_str)
        if power_match:
            properties.append(("电机功率", f"{power_match.group(1)} kW"))
        
        # 生产能力范围
        capacity_range_match = re.search(r'生产能力范围[:：]\s*([\d\.]+)\s*~\s*([\d\.]+)\s*kg/h', spec_str)
        if capacity_range_match:
            properties.append(("生产能力范围", f"{capacity_range_match.group(1)} ~ {capacity_range_match.group(2)} kg/h"))
        
        return properties

    @staticmethod
    def _get_hopper_properties(equipment):
        """获取贮斗、料斗类特有参数"""
        properties = []
        
        spec_str = getattr(equipment, 'specification', '')
        
        # 容积
        volume_match = re.search(r'容积[:：]\s*([\d\.]+)\s*m³', spec_str)
        if volume_match:
            properties.append(("容积", f"{volume_match.group(1)} m³"))
        
        # 卸料口尺寸
        outlet_match = re.search(r'卸料口尺寸[:：]\s*([\d\.]+)\s*mm', spec_str)
        if outlet_match:
            properties.append(("卸料口尺寸", f"{outlet_match.group(1)} mm"))
        
        # 料斗角度
        angle_match = re.search(r'料斗角度[:：]\s*([\d\.]+)\s*°', spec_str)
        if angle_match:
            properties.append(("料斗角度", f"{angle_match.group(1)} °"))
        
        # 材质
        material_match = re.search(r'材质[:：]\s*(\w+)', spec_str)
        if material_match:
            properties.append(("材质", material_match.group(1)))
        
        # 出料方式
        discharge_match = re.search(r'出料方式[:：]\s*(\w+)', spec_str)
        if discharge_match:
            properties.append(("出料方式", discharge_match.group(1)))
        
        return properties

    @staticmethod
    def _get_injector_properties(equipment):
        """获取喷射器类特有参数"""
        properties = []
        
        spec_str = getattr(equipment, 'specification', '')
        
        # 喷射能力
        capacity_match = re.search(r'喷射能力[:：]\s*([\d\.]+)\s*m³/h', spec_str)
        if capacity_match:
            properties.append(("喷射能力", f"{capacity_match.group(1)} m³/h"))
        
        # 喷射压力
        pressure_match = re.search(r'喷射压力[:：]\s*([\d\.]+)\s*MPa', spec_str)
        if pressure_match:
            properties.append(("喷射压力", f"{pressure_match.group(1)} MPa"))
        
        # 喷嘴直径
        diameter_match = re.search(r'喷嘴直径[:：]\s*([\d\.]+)\s*mm', spec_str)
        if diameter_match:
            properties.append(("喷嘴直径", f"{diameter_match.group(1)} mm"))
        
        # 工作介质
        medium_match = re.search(r'工作介质[:：]\s*(\w+)', spec_str)
        if medium_match:
            properties.append(("工作介质", medium_match.group(1)))
        
        # 喷射距离
        distance_match = re.search(r'喷射距离[:：]\s*([\d\.]+)\s*m', spec_str)
        if distance_match:
            properties.append(("喷射距离", f"{distance_match.group(1)} m"))
        
        return properties
    
    @staticmethod
    def _get_compressor_properties(equipment):
        """获取压缩机类特有参数"""
        properties = []
        
        spec_str = getattr(equipment, 'specification', '')
        
        # 排气量
        displacement_match = re.search(r'排气量[:：]\s*([\d\.]+)\s*m³/min', spec_str)
        if displacement_match:
            properties.append(("排气量", f"{displacement_match.group(1)} m³/min"))
        
        # 排气压力
        discharge_pressure_match = re.search(r'排气压力[:：]\s*([\d\.]+)\s*MPa', spec_str)
        if discharge_pressure_match:
            properties.append(("排气压力", f"{discharge_pressure_match.group(1)} MPa"))
        
        # 吸气压力
        suction_pressure_match = re.search(r'吸气压力[:：]\s*([\d\.]+)\s*MPa', spec_str)
        if suction_pressure_match:
            properties.append(("吸气压力", f"{suction_pressure_match.group(1)} MPa"))
        
        # 冷却方式
        cooling_match = re.search(r'冷却方式[:：]\s*(\w+)', spec_str)
        if cooling_match:
            properties.append(("冷却方式", cooling_match.group(1)))
        
        # 压缩机类型
        compressor_type_match = re.search(r'压缩机类型[:：]\s*(\w+)', spec_str)
        if compressor_type_match:
            properties.append(("压缩机类型", compressor_type_match.group(1)))
        
        # 驱动方式
        drive_match = re.search(r'驱动方式[:：]\s*(\w+)', spec_str)
        if drive_match:
            properties.append(("驱动方式", drive_match.group(1)))
        
        return properties

    @staticmethod
    def _get_lifting_properties(equipment):
        """获取起重、装卸、包装机械设备类特有参数"""
        properties = []
        
        spec_str = getattr(equipment, 'specification', '')
        
        # 起重能力
        capacity_match = re.search(r'起重能力[:：]\s*([\d\.]+)\s*t', spec_str)
        if capacity_match:
            properties.append(("起重能力", f"{capacity_match.group(1)} t"))
        
        # 起升高度
        height_match = re.search(r'起升高度[:：]\s*([\d\.]+)\s*m', spec_str)
        if height_match:
            properties.append(("起升高度", f"{height_match.group(1)} m"))
        
        # 包装速度
        speed_match = re.search(r'包装速度[:：]\s*([\d\.]+)\s*袋/小时', spec_str)
        if speed_match:
            properties.append(("包装速度", f"{speed_match.group(1)} 袋/小时"))
        
        # 包装规格
        package_match = re.search(r'包装规格[:：]\s*([\d\.]+)\s*kg/袋', spec_str)
        if package_match:
            properties.append(("包装规格", f"{package_match.group(1)} kg/袋"))
        
        # 跨度
        span_match = re.search(r'跨度[:：]\s*([\d\.]+)\s*m', spec_str)
        if span_match:
            properties.append(("跨度", f"{span_match.group(1)} m"))
        
        return properties

    @staticmethod
    def _get_mixer_grinder_properties(equipment):
        """获取磨碎设备类、混合器类特有参数"""
        properties = []
        
        spec_str = getattr(equipment, 'specification', '')
        
        # 处理能力
        capacity_match = re.search(r'处理能力[:：]\s*([\d\.]+)\s*kg/h', spec_str)
        if capacity_match:
            properties.append(("处理能力", f"{capacity_match.group(1)} kg/h"))
        
        # 混合均匀度
        uniformity_match = re.search(r'混合均匀度[:：]\s*([\d\.]+)\s*%', spec_str)
        if uniformity_match:
            properties.append(("混合均匀度", f"{uniformity_match.group(1)} %"))
        
        # 细度
        fineness_match = re.search(r'细度[:：]\s*([\d\.]+)\s*目', spec_str)
        if fineness_match:
            properties.append(("细度", f"{fineness_match.group(1)} 目"))
        
        # 混合时间
        time_match = re.search(r'混合时间[:：]\s*([\d\.]+)\s*min', spec_str)
        if time_match:
            properties.append(("混合时间", f"{time_match.group(1)} min"))
        
        # 粉碎粒度
        particle_match = re.search(r'粉碎粒度[:：]\s*([\d\.]+)\s*mm', spec_str)
        if particle_match:
            properties.append(("粉碎粒度", f"{particle_match.group(1)} mm"))
        
        # 混合容积
        volume_match = re.search(r'混合容积[:：]\s*([\d\.]+)\s*m³', spec_str)
        if volume_match:
            properties.append(("混合容积", f"{volume_match.group(1)} m³"))
        
        return properties

    @staticmethod
    def _get_pump_properties(equipment):
        """获取泵类特有参数"""
        properties = []
        
        spec_str = getattr(equipment, 'specification', '')
        
        # 流量
        flow_match = re.search(r'流量[:：]\s*([\d\.]+)\s*m³/h', spec_str)
        if flow_match:
            properties.append(("流量", f"{flow_match.group(1)} m³/h"))
        
        # 扬程
        head_match = re.search(r'扬程[:：]\s*([\d\.]+)\s*m', spec_str)
        if head_match:
            properties.append(("扬程", f"{head_match.group(1)} m"))
        
        # 必需汽蚀余量
        npsh_match = re.search(r'必需汽蚀余量[:：]\s*([\d\.]+)\s*m', spec_str)
        if npsh_match:
            properties.append(("必需汽蚀余量", f"{npsh_match.group(1)} m"))
        
        # 效率
        efficiency_match = re.search(r'效率[:：]\s*([\d\.]+)\s*%', spec_str)
        if efficiency_match:
            properties.append(("效率", f"{efficiency_match.group(1)} %"))
        
        # 进出口直径
        port_match = re.search(r'进出口直径[:：]\s*([\d\.]+)\s*mm', spec_str)
        if port_match:
            properties.append(("进出口直径", f"{port_match.group(1)} mm"))
        
        # 泵的类型
        pump_type_match = re.search(r'泵类型[:：]\s*(\w+)', spec_str)
        if pump_type_match:
            properties.append(("泵类型", pump_type_match.group(1)))
        
        # 密封形式
        seal_match = re.search(r'密封形式[:：]\s*(\w+)', spec_str)
        if seal_match:
            properties.append(("密封形式", seal_match.group(1)))
        
        return properties
    
    @staticmethod
    def _get_reactor_properties(equipment):
        """获取反应器特有参数"""
        properties = []
        
        spec_str = getattr(equipment, 'specification', '')
        
        # 容积
        volume_match = re.search(r'容积[:：]\s*([\d\.]+)\s*m³', spec_str)
        if volume_match:
            properties.append(("容积", f"{volume_match.group(1)} m³"))
        else:
            properties.append(("容积", "未知"))
        
        # 直径
        diameter_match = re.search(r'直径[:：]\s*([\d\.]+)\s*mm', spec_str)
        if diameter_match:
            properties.append(("直径", f"{diameter_match.group(1)} mm"))
        
        # 高度
        height_match = re.search(r'高度[:：]\s*([\d\.]+)\s*mm', spec_str)
        if height_match:
            properties.append(("高度", f"{height_match.group(1)} mm"))
        
        # 壁厚
        thickness_match = re.search(r'壁厚[:：]\s*([\d\.]+)\s*mm', spec_str)
        if thickness_match:
            properties.append(("壁厚", f"{thickness_match.group(1)} mm"))
        
        # 搅拌转速
        agitation_match = re.search(r'搅拌转速[:：]\s*([\d\.]+)\s*rpm', spec_str)
        if agitation_match:
            properties.append(("搅拌转速", f"{agitation_match.group(1)} rpm"))
        
        # 搅拌功率
        agitation_power_match = re.search(r'搅拌功率[:：]\s*([\d\.]+)\s*kW', spec_str)
        if agitation_power_match:
            properties.append(("搅拌功率", f"{agitation_power_match.group(1)} kW"))
        
        # 传热面积
        heat_area_match = re.search(r'传热面积[:：]\s*([\d\.]+)\s*m²', spec_str)
        if heat_area_match:
            properties.append(("传热面积", f"{heat_area_match.group(1)} m²"))
        
        return properties
    
    @staticmethod
    def _get_separator_properties(equipment):
        """获取分离设备类特有参数"""
        properties = []
        
        spec_str = getattr(equipment, 'specification', '')
        
        # 容积
        volume_match = re.search(r'容积[:：]\s*([\d\.]+)\s*m³', spec_str)
        if volume_match:
            properties.append(("容积", f"{volume_match.group(1)} m³"))
        
        # 直径
        diameter_match = re.search(r'直径[:：]\s*([\d\.]+)\s*mm', spec_str)
        if diameter_match:
            properties.append(("直径", f"{diameter_match.group(1)} mm"))
        
        # 设计处理量
        capacity_match = re.search(r'处理量[:：]\s*([\d\.]+)\s*m³/h', spec_str)
        if capacity_match:
            properties.append(("处理量", f"{capacity_match.group(1)} m³/h"))
        
        # 分离效率
        efficiency_match = re.search(r'分离效率[:：]\s*([\d\.]+)\s*%', spec_str)
        if efficiency_match:
            properties.append(("分离效率", f"{efficiency_match.group(1)} %"))
        
        # 分离原理
        principle_match = re.search(r'分离原理[:：]\s*(\w+)', spec_str)
        if principle_match:
            properties.append(("分离原理", principle_match.group(1)))
        
        # 工作压力
        pressure_match = re.search(r'工作压力[:：]\s*([\d\.]+)\s*MPa', spec_str)
        if pressure_match:
            properties.append(("工作压力", f"{pressure_match.group(1)} MPa"))
        
        return properties
    
    @staticmethod
    def _get_tank_properties(equipment):
        """获取储罐特有参数"""
        properties = []
        
        spec_str = getattr(equipment, 'specification', '')
        
        # 尝试从规格中提取直径和高度
        diameter = None
        height = None
        volume = None
        
        # 直径
        diameter_match = re.search(r'直径[:：]\s*([\d\.]+)\s*mm', spec_str)
        if diameter_match:
            diameter = float(diameter_match.group(1))
            properties.append(("直径", f"{diameter} mm"))
        
        # 高度
        height_match = re.search(r'高度[:：]\s*([\d\.]+)\s*mm', spec_str)
        if height_match:
            height = float(height_match.group(1))
            properties.append(("高度", f"{height} mm"))
        
        # 容积 - 首先尝试从规格中提取
        volume_match = re.search(r'容积[:：]\s*([\d\.]+)\s*m³', spec_str)
        if volume_match:
            volume = float(volume_match.group(1))
            properties.append(("容积", f"{volume} m³"))
        else:
            # 如果规格中没有容积，但有了直径和高度，尝试计算
            if diameter and height:
                # 将毫米转换为米
                diameter_m = diameter / 1000.0
                height_m = height / 1000.0
                
                # 计算圆柱体积
                radius = diameter_m / 2.0
                calculated_volume = 3.141592653589793 * radius * radius * height_m
                
                properties.append(("容积", f"{calculated_volume:.3f} m³ (计算值)"))
            else:
                properties.append(("容积", "未知"))
        
        # 壁厚
        thickness_match = re.search(r'壁厚[:：]\s*([\d\.]+)\s*mm', spec_str)
        if thickness_match:
            properties.append(("壁厚", f"{thickness_match.group(1)} mm"))
        
        # 封头类型
        head_match = re.search(r'封头类型[:：]\s*(\w+)', spec_str)
        if head_match:
            properties.append(("封头类型", head_match.group(1)))
        
        # 设计液位
        level_match = re.search(r'设计液位[:：]\s*([\d\.]+)\s*m', spec_str)
        if level_match:
            properties.append(("设计液位", f"{level_match.group(1)} m"))
        
        # 储罐类型
        tank_type_match = re.search(r'储罐类型[:：]\s*(\w+)', spec_str)
        if tank_type_match:
            properties.append(("储罐类型", tank_type_match.group(1)))
        
        # 工作压力
        pressure_match = re.search(r'工作压力[:：]\s*([\d\.]+)\s*MPa', spec_str)
        if pressure_match:
            properties.append(("工作压力", f"{pressure_match.group(1)} MPa"))
        
        # 工作温度
        temperature_match = re.search(r'工作温度[:：]\s*([\d\.]+)\s*°C', spec_str)
        if temperature_match:
            properties.append(("工作温度", f"{temperature_match.group(1)} °C"))
        
        return properties

    @staticmethod
    def _get_utility_properties(equipment):
        """获取公用辅助设备类特有参数"""
        properties = []
        
        spec_str = getattr(equipment, 'specification', '')
        
        # 处理能力
        capacity_match = re.search(r'处理能力[:：]\s*([\d\.]+)\s*(\w+)', spec_str)
        if capacity_match:
            properties.append(("处理能力", f"{capacity_match.group(1)} {capacity_match.group(2)}"))
        
        # 工作介质
        medium_match = re.search(r'工作介质[:：]\s*(\w+)', spec_str)
        if medium_match:
            properties.append(("工作介质", medium_match.group(1)))
        
        # 工作压力
        pressure_match = re.search(r'工作压力[:：]\s*([\d\.]+)\s*MPa', spec_str)
        if pressure_match:
            properties.append(("工作压力", f"{pressure_match.group(1)} MPa"))
        
        # 工作温度
        temperature_match = re.search(r'工作温度[:：]\s*([\d\.]+)\s*°C', spec_str)
        if temperature_match:
            properties.append(("工作温度", f"{temperature_match.group(1)} °C"))
        
        # 设备用途
        purpose_match = re.search(r'设备用途[:：]\s*(\w+)', spec_str)
        if purpose_match:
            properties.append(("设备用途", purpose_match.group(1)))
        
        return properties

    @staticmethod
    def _get_conveyor_properties(equipment):
        """获取固体输送类特有参数"""
        properties = []
        
        spec_str = getattr(equipment, 'specification', '')
        
        # 输送能力
        capacity_match = re.search(r'输送能力[:：]\s*([\d\.]+)\s*t/h', spec_str)
        if capacity_match:
            properties.append(("输送能力", f"{capacity_match.group(1)} t/h"))
        
        # 输送长度
        length_match = re.search(r'输送长度[:：]\s*([\d\.]+)\s*m', spec_str)
        if length_match:
            properties.append(("输送长度", f"{length_match.group(1)} m"))
        
        # 输送速度
        speed_match = re.search(r'输送速度[:：]\s*([\d\.]+)\s*m/s', spec_str)
        if speed_match:
            properties.append(("输送速度", f"{speed_match.group(1)} m/s"))
        
        # 输送设备类型
        type_match = re.search(r'输送设备类型[:：]\s*(\w+)', spec_str)
        if type_match:
            properties.append(("输送设备类型", type_match.group(1)))
        
        # 带宽
        width_match = re.search(r'带宽[:：]\s*([\d\.]+)\s*mm', spec_str)
        if width_match:
            properties.append(("带宽", f"{width_match.group(1)} mm"))
        
        # 倾角
        angle_match = re.search(r'倾角[:：]\s*([\d\.]+)\s*°', spec_str)
        if angle_match:
            properties.append(("倾角", f"{angle_match.group(1)} °"))
        
        # 提升高度
        height_match = re.search(r'提升高度[:：]\s*([\d\.]+)\s*m', spec_str)
        if height_match:
            properties.append(("提升高度", f"{height_match.group(1)} m"))
        
        return properties

    @staticmethod
    def _get_weighing_properties(equipment):
        """获取称重类设备特有参数"""
        properties = []
        
        spec_str = getattr(equipment, 'specification', '')
        
        # 称重范围
        range_match = re.search(r'称重范围[:：]\s*([\d\.]+)\s*~\s*([\d\.]+)\s*kg', spec_str)
        if range_match:
            properties.append(("称重范围", f"{range_match.group(1)} ~ {range_match.group(2)} kg"))
        else:
            # 尝试单个值
            capacity_match = re.search(r'称重能力[:：]\s*([\d\.]+)\s*kg', spec_str)
            if capacity_match:
                properties.append(("称重能力", f"{capacity_match.group(1)} kg"))
        
        # 精度
        accuracy_match = re.search(r'精度[:：]\s*([\d\.]+)\s*%', spec_str)
        if accuracy_match:
            properties.append(("精度", f"{accuracy_match.group(1)} %"))
        
        # 分度值
        division_match = re.search(r'分度值[:：]\s*([\d\.]+)\s*kg', spec_str)
        if division_match:
            properties.append(("分度值", f"{division_match.group(1)} kg"))
        
        # 称重方式
        method_match = re.search(r'称重方式[:：]\s*(\w+)', spec_str)
        if method_match:
            properties.append(("称重方式", method_match.group(1)))
        
        # 显示方式
        display_match = re.search(r'显示方式[:：]\s*(\w+)', spec_str)
        if display_match:
            properties.append(("显示方式", display_match.group(1)))
        
        return properties

    @staticmethod
    def _get_package_properties(equipment):
        """获取成套设备类特有参数"""
        properties = []
        
        spec_str = getattr(equipment, 'specification', '')
        
        # 处理能力
        capacity_match = re.search(r'处理能力[:：]\s*([\d\.]+)\s*(\w+)', spec_str)
        if capacity_match:
            properties.append(("处理能力", f"{capacity_match.group(1)} {capacity_match.group(2)}"))
        
        # 设备组成
        composition_match = re.search(r'设备组成[:：]\s*(.+)', spec_str)
        if composition_match:
            properties.append(("设备组成", composition_match.group(1)))
        
        # 总功率
        total_power_match = re.search(r'总功率[:：]\s*([\d\.]+)\s*kW', spec_str)
        if total_power_match:
            properties.append(("总功率", f"{total_power_match.group(1)} kW"))
        
        # 外形尺寸
        dimension_match = re.search(r'外形尺寸[:：]\s*([\d\.]+)\s*×\s*([\d\.]+)\s*×\s*([\d\.]+)\s*mm', spec_str)
        if dimension_match:
            properties.append(("外形尺寸", f"{dimension_match.group(1)} × {dimension_match.group(2)} × {dimension_match.group(3)} mm"))
        
        # 成套设备用途
        purpose_match = re.search(r'成套设备用途[:：]\s*(\w+)', spec_str)
        if purpose_match:
            properties.append(("成套设备用途", purpose_match.group(1)))
        
        return properties

    @staticmethod
    def _get_other_properties(equipment):
        """获取其他设备类型参数"""
        properties = []
        
        spec_str = getattr(equipment, 'specification', '')
        
        # 处理能力
        capacity_match = re.search(r'处理能力[:：]\s*([\d\.]+)\s*(\w+)', spec_str)
        if capacity_match:
            properties.append(("处理能力", f"{capacity_match.group(1)} {capacity_match.group(2)}"))
        
        # 工作介质
        medium_match = re.search(r'工作介质[:：]\s*(\w+)', spec_str)
        if medium_match:
            properties.append(("工作介质", medium_match.group(1)))
        
        # 设备用途
        purpose_match = re.search(r'设备用途[:：]\s*(\w+)', spec_str)
        if purpose_match:
            properties.append(("设备用途", purpose_match.group(1)))
        
        # 特殊要求
        requirement_match = re.search(r'特殊要求[:：]\s*(.+)', spec_str)
        if requirement_match:
            properties.append(("特殊要求", requirement_match.group(1)))
        
        return properties
    
    @staticmethod
    def _format_parameter(value, unit, decimals):
        if value is None or value == '':
            return "未知"
        
        if isinstance(value, str):
            value = value.strip()
            if value.upper() == 'NT' or value.upper() == 'NP':
                return value.upper()
        
        if isinstance(value, (int, float)):
            if decimals == 1:
                return f"{value:.1f} {unit}"
            elif decimals == 2:
                return f"{value:.2f} {unit}"
            else:
                return f"{value} {unit}"
        else:
            return f"{value} {unit}"