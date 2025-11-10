#!/usr/bin/env python3
"""强制清理根目录文档"""
from pathlib import Path
import shutil

root = Path('.')

# 需要移动的文件
to_move = {
    'AI-API审查总结-最终报告.md': 'docs/device-data-model/',
    'Java环境核查-最终总结.md': 'docs/archived/',
    'Java环境核查结果-最终报告.md': 'docs/archived/',
    '权限控制系统文档.md': 'docs/archived/',
    '环境检查报告.md': 'docs/archived/',
}

print("=" * 70)
print("  Force Cleanup Root Directory")
print("=" * 70)
print()

# 创建目录
Path('docs/archived').mkdir(parents=True, exist_ok=True)
Path('docs/device-data-model').mkdir(parents=True, exist_ok=True)

moved = 0
for filename, dest_dir in to_move.items():
    src = root / filename
    dest = Path(dest_dir) / filename
    
    if src.exists():
        try:
            shutil.move(str(src), str(dest))
            print(f"[MOVED] {filename}")
            print(f"   -> {dest_dir}")
            moved += 1
        except Exception as e:
            print(f"[ERROR] {filename}: {e}")
    else:
        print(f"[SKIP] {filename} (not found)")

print()
print(f"[SUCCESS] Moved {moved} files")
print()

# 列出剩余的.md文件
remaining = sorted([f.name for f in root.iterdir() if f.is_file() and f.suffix == '.md'])
print(f"[REMAINING] {len(remaining)} .md files in root:")
for f in remaining:
    print(f"  - {f}")

print()
print("=" * 70)
print("[COMPLETE] Cleanup finished!")
print("=" * 70)

