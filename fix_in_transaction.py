"""
批量修复in_transaction()调用，添加连接名称参数
"""
import os
import re

# 需要修复的文件列表
files_to_fix = [
    'app/api/v2/roles.py',
    'app/api/v2/users.py',
    'app/api/v2/menus.py',
    'app/api/v2/dict_types.py',
    'app/api/v2/dict_types_fixed.py',
    'app/api/v2/dict_types_backup.py',
    'app/api/v2/dict_data.py',
    'app/api/v2/system_params.py',
    'app/api/v2/system_params_backup.py',
]

def fix_file(filepath):
    """修复单个文件"""
    if not os.path.exists(filepath):
        print(f"⚠️  文件不存在: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 统计修改次数
    count = content.count('in_transaction()')
    
    if count == 0:
        print(f"✓ {filepath} - 无需修改")
        return False
    
    # 替换 in_transaction() 为 in_transaction("default")
    new_content = content.replace('in_transaction()', 'in_transaction("default")')
    
    # 写回文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"✓ {filepath} - 修改了 {count} 处")
    return True

def main():
    print("=" * 80)
    print("批量修复 in_transaction() 调用")
    print("=" * 80)
    print()
    
    fixed_count = 0
    total_changes = 0
    
    for filepath in files_to_fix:
        if fix_file(filepath):
            fixed_count += 1
    
    print()
    print("=" * 80)
    print(f"修复完成：共修改 {fixed_count} 个文件")
    print("=" * 80)

if __name__ == '__main__':
    main()
