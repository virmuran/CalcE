# TofuApp/debug_data.py
import os
import json
import sys
import traceback

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from resource_helper import get_data_file_path

def diagnose_data_issue():
    """诊断数据文件问题"""
    print("=== Tofu 数据文件诊断工具 ===\n")
    
    # 获取数据文件路径
    data_file = get_data_file_path()
    print(f"1. 数据文件路径: {data_file}")
    print(f"2. 文件是否存在: {os.path.exists(data_file)}")
    
    if os.path.exists(data_file):
        file_size = os.path.getsize(data_file)
        print(f"3. 文件大小: {file_size} 字节")
        
        # 尝试读取文件内容
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                print(f"4. 文件内容长度: {len(content)} 字符")
                
                if content:
                    # 尝试解析JSON
                    try:
                        data = json.loads(content)
                        print("5. JSON解析: ✅ 成功")
                        
                        # 检查数据结构
                        required_keys = ["todos", "notes", "bookmarks", "settings"]
                        missing_keys = [key for key in required_keys if key not in data]
                        if missing_keys:
                            print(f"6. 数据结构: ❌ 缺少字段: {missing_keys}")
                        else:
                            print("6. 数据结构: ✅ 完整")
                            
                        # 显示各数据项的数量
                        print("\n7. 数据统计:")
                        for key in data:
                            if isinstance(data[key], list):
                                print(f"   - {key}: {len(data[key])} 项")
                            elif isinstance(data[key], dict):
                                print(f"   - {key}: {len(data[key])} 个键值对")
                            else:
                                print(f"   - {key}: {type(data[key]).__name__}")
                                
                    except json.JSONDecodeError as e:
                        print(f"5. JSON解析: ❌ 失败 - {e}")
                        print(f"   文件内容前500字符: {content[:500]}")
                        
                else:
                    print("5. 文件内容: ❌ 为空")
                    
        except Exception as e:
            print(f"4. 文件读取: ❌ 失败 - {e}")
            traceback.print_exc()
    else:
        print("3. 文件状态: ❌ 不存在")
    
    print(f"\n8. 当前工作目录: {os.getcwd()}")
    print(f"9. 脚本所在目录: {current_dir}")
    
    # 检查可能的其他数据文件位置
    print("\n10. 搜索其他可能的数据文件:")
    possible_locations = [
        os.path.join(current_dir, "tofu_data.json"),
        os.path.join(current_dir, "data", "tofu_data.json"),
        os.path.join(os.path.expanduser("~"), "tofu_data.json"),
        os.path.join(os.path.expanduser("~"), "AppData", "Local", "Tofu", "tofu_data.json"),
        os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "Tofu", "tofu_data.json"),
    ]
    
    for location in possible_locations:
        if os.path.exists(location):
            size = os.path.getsize(location)
            print(f"   找到: {location} ({size} 字节)")

def test_data_manager():
    """测试数据管理器"""
    print("\n=== 测试数据管理器 ===\n")
    
    try:
        from data_manager import DataManager
        
        print("创建 DataManager 实例...")
        dm = DataManager()
        
        print("加载数据...")
        data = dm.load_data()
        
        if data:
            print("✅ 数据加载成功")
            print(f"待办事项数量: {len(data.get('todos', []))}")
            print(f"笔记数量: {len(data.get('notes', []))}")
            print(f"书签数量: {len(data.get('bookmarks', []))}")
        else:
            print("❌ 数据加载失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_data_issue()
    test_data_manager()
    
    print("\n=== 诊断完成 ===")
    input("按回车键退出...")