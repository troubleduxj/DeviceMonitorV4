"""
整理项目根目录下的临时文档和脚本
"""
import os
import shutil
from pathlib import Path

# 定义目标目录
DOCS_DIR = Path('docs')
SCRIPTS_DIR = Path('scripts')

# 创建子目录
DOCS_API = DOCS_DIR / 'api-management'
DOCS_PERMISSIONS = DOCS_DIR / 'permissions'
DOCS_FIXES = DOCS_DIR / 'fixes'
DOCS_REPORTS = DOCS_DIR / 'reports'

SCRIPTS_API = SCRIPTS_DIR / 'api-management'
SCRIPTS_PERMISSIONS = SCRIPTS_DIR / 'permissions'
SCRIPTS_CHECK = SCRIPTS_DIR / 'check'
SCRIPTS_FIX = SCRIPTS_DIR / 'fix'
SCRIPTS_TEST = SCRIPTS_DIR / 'test'

# 文件分类规则
FILE_RULES = {
    # API管理相关文档
    'docs/api-management': [
        'API分类预览报告.md',
        'API分页加载问题修复说明.md',
        'API同步完成报告-优先级1.md',
        'API同步完整总结报告.md',
        'API同步工作索引.md',
        'API同步最终总结.md',
        'API同步最终状态.md',
        'API同步进度总结.md',
        'API质量全面检查报告.md',
        '接口权限完整性分析报告.md',
        '重复API清理完成报告.md',
        '高优先级API问题修复完成报告.md',
    ],
    
    # 权限相关文档
    'docs/permissions': [
        '按钮权限token问题诊断.md',
        '按钮权限问题修复报告.md',
        '按钮权限问题最终解决方案.md',
        '按钮权限问题最终解决步骤.md',
        '按钮权限问题诊断报告.md',
        '权限按钮全局统一完成.md',
        '权限按钮显示模式配置说明.md',
        '权限按钮统一配置完成报告.md',
        '权限系统最佳实践方案.md',
        '菜单权限按钮节点存在意义分析.md',
        '角色权限更新500错误修复报告.md',
        '角色权限更新500错误诊断报告.md',
        '角色权限问题修复完成总结.md',
        '角色权限问题完整修复总结.md',
    ],
    
    # 修复相关文档
    'docs/fixes': [
        '字典权限层级修复说明.md',
        '字典菜单修复完成.md',
        '字典菜单修复测试指南.md',
        '字典菜单显示问题修复报告.md',
        '审计日志问题修复总结.md',
        '数据库事务连接问题修复报告.md',
        '接口权限滚动优化完成总结.md',
        '接口权限滚动优化测试指南.md',
        '接口权限滚动问题修复说明.md',
        '接口权限界面滚动优化说明.md',
    ],
    
    # 报告文档
    'docs/reports': [
        '日志状态检查结果.md',
        '日志系统状态检查报告.md',
        '本次工作完成总结.md',
        '离线打包功能测试报告.md',
        '离线打包问题解答.md',
        'README_UPDATE_SUMMARY.md',
    ],
    
    # API管理脚本
    'scripts/api-management': [
        'batch_sync_apis.py',
        'check_ai_apis.py',
        'check_all_api_issues.py',
        'check_api_completeness.py',
        'check_api_names.py',
        'check_api_tables.py',
        'check_duplicate_apis.py',
        'check_maintenance_apis.py',
        'check_remaining_apis.py',
        'check_user_api_paths.py',
        'cleanup_backup_files.py',
        'do_sync_ai.py',
        'do_sync_priority1.py',
        'do_sync_priority2.py',
        'do_sync_priority3.py',
        'fix_duplicate_maintenance_apis.py',
        'fix_user_api_paths.py',
        'preview_api_classification.py',
        'preview_priority1.py',
        'remove_duplicate_user_apis.py',
        'sync_ai_apis.py',
        'sync_api_to_database.py',
        'sync_final_important_apis.py',
        'sync_priority1_apis.py',
        'sync_priority2_apis.py',
        'sync_priority3_apis.py',
        'sync_remaining_priority_apis.py',
    ],
    
    # 权限相关脚本
    'scripts/permissions': [
        'add_permission_button_mode_param.py',
        'check_button_permissions.py',
        'check_get_roles_permission.py',
        'check_role_api_table.py',
        'check_role_permissions.py',
        'check_roles_list_permission.py',
        'check_test_user_permissions.py',
        'create_roles_list_api.py',
        'execute_grant_permissions.py',
        'verify_test_user_api_permissions.py',
        'grant_button_permissions.sql',
    ],
    
    # 检查脚本
    'scripts/check': [
        'check_dict_component.py',
        'check_dict_menus.py',
        'check_dict_menus_sql.py',
        'check_dict_menu_visibility.py',
        'check_foreign_keys.py',
        'diagnose_tortoise_config.py',
    ],
    
    # 修复脚本
    'scripts/fix': [
        'fix_dict_menu_order.sql',
        'fix_in_transaction.py',
        'verify_dict_menus.py',
    ],
    
    # 测试脚本
    'scripts/test': [
        'test_api_permissions.py',
        'test_audit_log_fix.py',
        'test_role_menu_permissions.py',
        'test_role_permissions_update.py',
    ],
}

def create_directories():
    """创建目标目录"""
    dirs = [
        DOCS_API,
        DOCS_PERMISSIONS,
        DOCS_FIXES,
        DOCS_REPORTS,
        SCRIPTS_API,
        SCRIPTS_PERMISSIONS,
        SCRIPTS_CHECK,
        SCRIPTS_FIX,
        SCRIPTS_TEST,
    ]
    
    for dir_path in dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"✅ 创建目录: {dir_path}")

def move_files():
    """移动文件到目标目录"""
    moved_count = 0
    skipped_count = 0
    
    for target_dir, files in FILE_RULES.items():
        print(f"\n📁 处理目录: {target_dir}")
        
        for filename in files:
            source = Path(filename)
            
            if not source.exists():
                print(f"  ⏭️  跳过（不存在）: {filename}")
                skipped_count += 1
                continue
            
            # 构建目标路径
            target = Path(target_dir) / filename
            
            # 如果目标文件已存在，先删除
            if target.exists():
                target.unlink()
                print(f"  🗑️  删除旧文件: {target}")
            
            # 移动文件
            shutil.move(str(source), str(target))
            print(f"  ✅ 移动: {filename} -> {target}")
            moved_count += 1
    
    return moved_count, skipped_count

def create_readme():
    """创建README文件"""
    # API管理README
    api_readme = DOCS_API / 'README.md'
    api_readme.write_text("""# API管理文档

本目录包含API同步、管理和质量检查相关的文档。

## 文档列表

### API同步
- API同步工作索引.md - 所有API同步工作的索引
- API同步最终状态.md - API同步的最终状态
- API同步完整总结报告.md - 完整的同步总结

### API质量
- API质量全面检查报告.md - 全面的质量检查
- 重复API清理完成报告.md - 重复API清理
- 高优先级API问题修复完成报告.md - 高优先级问题修复

### 相关脚本
参见 `scripts/api-management/` 目录
""", encoding='utf-8')
    
    # 权限管理README
    perm_readme = DOCS_PERMISSIONS / 'README.md'
    perm_readme.write_text("""# 权限管理文档

本目录包含权限系统相关的文档。

## 文档列表

### 按钮权限
- 按钮权限问题最终解决方案.md - 最终解决方案
- 权限按钮全局统一完成.md - 全局统一配置

### 角色权限
- 角色权限问题完整修复总结.md - 完整修复总结

### 最佳实践
- 权限系统最佳实践方案.md - 推荐的最佳实践

### 相关脚本
参见 `scripts/permissions/` 目录
""", encoding='utf-8')
    
    print("\n✅ 创建README文件")

def main():
    """主函数"""
    print("="*80)
    print("🗂️  整理项目根目录文件")
    print("="*80)
    
    # 创建目录
    print("\n1️⃣  创建目标目录")
    create_directories()
    
    # 移动文件
    print("\n2️⃣  移动文件")
    moved, skipped = move_files()
    
    # 创建README
    print("\n3️⃣  创建README文件")
    create_readme()
    
    # 总结
    print("\n" + "="*80)
    print("📊 整理完成")
    print("="*80)
    print(f"移动文件: {moved} 个")
    print(f"跳过文件: {skipped} 个")
    print("="*80)

if __name__ == '__main__':
    main()
