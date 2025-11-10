#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整理根目录临时文件
将临时文件移动到合适的目录
"""

import shutil
from pathlib import Path

project_root = Path(__file__).parent.parent

# 文件移动计划
move_plan = {
    # 文档类 -> docs/
    'AI-API审查总结-最终报告.md': 'docs/device-data-model/',
    'FINAL_SUMMARY.md': 'docs/device-data-model/',
    'README-AI-PREDICTION-COMPLETE.md': 'docs/device-data-model/',
    'CHANGELOG-AI-PREDICTION.md': 'docs/device-data-model/',
    'final_diagnosis.md': 'docs/archived/',
    'Java环境核查-最终总结.md': 'docs/archived/',
    'Java环境核查结果-最终报告.md': 'docs/archived/',
    'CRITICAL_MILESTONE.md': 'docs/project/',
    'MIGRATION_PROGRESS.md': 'docs/database/',
    'MIGRATION_STATUS.md': 'docs/database/',
    'PERMISSION_FIX_REPORT.md': 'docs/archived/',
    'VERIFICATION_GUIDE.md': 'docs/project/',
    'project-status.md': 'docs/project/',
    '权限控制系统文档.md': 'docs/system/',
    '环境检查报告.md': 'docs/archived/',
    
    # Python脚本 -> scripts/archived/
    'check_admin_fields.py': 'scripts/archived/',
    'check_admin_superuser.py': 'scripts/archived/',
    'diagnose_menu_issue.py': 'scripts/archived/',
    'fix_admin_role.py': 'scripts/archived/',
    
    # SQL文件 -> database/archived/
    'check_menu.sql': 'database/archived/',
    'fix_admin_role.sql': 'database/archived/',
    
    # 其他临时文件
    'exclude_v3.txt': 'docs/archived/',
}

print("=" * 70)
print("  Organize Root Directory Files")
print("=" * 70)
print()

# 创建必要的目录
dirs_to_create = [
    'docs/archived',
    'docs/project',
    'docs/database',
    'docs/system',
    'scripts/archived',
    'database/archived',
]

print("[CREATE] Creating directories...")
for dir_path in dirs_to_create:
    full_path = project_root / dir_path
    full_path.mkdir(parents=True, exist_ok=True)
    print(f"   ✓ {dir_path}")
print()

# 移动文件
print("[MOVE] Moving files...")
print("-" * 70)

moved_count = 0
not_found = []

for filename, dest_dir in move_plan.items():
    source = project_root / filename
    dest_path = project_root / dest_dir
    dest = dest_path / filename
    
    if source.exists():
        try:
            shutil.move(str(source), str(dest))
            moved_count += 1
            print(f"   ✓ {filename}")
            print(f"     -> {dest_dir}")
        except Exception as e:
            print(f"   ✗ {filename}: {e}")
    else:
        not_found.append(filename)

print()
print(f"[SUCCESS] Moved {moved_count} files")

if not_found:
    print(f"[INFO] {len(not_found)} files not found (already moved or deleted):")
    for f in not_found:
        print(f"   - {f}")

print()
print("=" * 70)
print("[COMPLETE] Root directory organized!")
print("=" * 70)
print()
print("[SUMMARY]:")
print(f"   Files moved: {moved_count}")
print(f"   Files not found: {len(not_found)}")
print()
print("[RESULT]:")
print("   ✓ Root directory is now cleaner")
print("   ✓ Files organized by category")
print("   ✓ Archived files in docs/archived/")
print("   ✓ Scripts in scripts/archived/")
print()

