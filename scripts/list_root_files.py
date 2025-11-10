#!/usr/bin/env python3
"""列出根目录所有文件"""
from pathlib import Path

root = Path('.')
files = sorted([f for f in root.iterdir() if f.is_file()])

print("=" * 80)
print("  Root Directory Files")
print("=" * 80)
print()

# 按类型分类
docs = [f for f in files if f.suffix == '.md']
scripts = [f for f in files if f.suffix in ['.py', '.bat', '.sh']]
configs = [f for f in files if f.suffix in ['.ini', '.txt', '.json', '.yml', '.yaml', '.toml']]
sql = [f for f in files if f.suffix == '.sql']
others = [f for f in files if f not in docs + scripts + configs + sql]

print(f"[MARKDOWN] {len(docs)} files:")
for f in docs:
    print(f"  - {f.name}")
print()

print(f"[SCRIPTS] {len(scripts)} files:")
for f in scripts:
    print(f"  - {f.name}")
print()

print(f"[CONFIGS] {len(configs)} files:")
for f in configs:
    print(f"  - {f.name}")
print()

if sql:
    print(f"[SQL] {len(sql)} files:")
    for f in sql:
        print(f"  - {f.name}")
    print()

if others:
    print(f"[OTHERS] {len(others)} files:")
    for f in others:
        print(f"  - {f.name}")
    print()

print("=" * 80)
print(f"Total files in root: {len(files)}")
print("=" * 80)

