#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
版本管理工具
自动化版本标记、变更日志生成和发布管理
"""

import os
import re
import sys
import json
import subprocess
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import argparse


@dataclass
class CommitInfo:
    """提交信息"""
    hash: str
    type: str
    scope: Optional[str]
    description: str
    body: str
    breaking: bool
    date: datetime
    author: str


@dataclass
class VersionInfo:
    """版本信息"""
    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None
    
    def __str__(self):
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        return version
    
    @classmethod
    def from_string(cls, version_str: str):
        """从字符串解析版本"""
        # 移除 'v' 前缀
        version_str = version_str.lstrip('v')
        
        # 分离预发布版本
        if '-' in version_str:
            version_part, prerelease = version_str.split('-', 1)
        else:
            version_part, prerelease = version_str, None
        
        # 解析主版本号
        parts = version_part.split('.')
        if len(parts) != 3:
            raise ValueError(f"Invalid version format: {version_str}")
        
        return cls(
            major=int(parts[0]),
            minor=int(parts[1]),
            patch=int(parts[2]),
            prerelease=prerelease
        )


class GitManager:
    """Git操作管理器"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
    
    def run_command(self, command: List[str]) -> str:
        """执行Git命令"""
        try:
            result = subprocess.run(
                command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Git command failed: {' '.join(command)}\nError: {e.stderr}")
    
    def get_current_branch(self) -> str:
        """获取当前分支"""
        return self.run_command(["git", "branch", "--show-current"])
    
    def get_latest_tag(self) -> Optional[str]:
        """获取最新标签"""
        try:
            return self.run_command(["git", "describe", "--tags", "--abbrev=0"])
        except RuntimeError:
            return None
    
    def get_commits_since_tag(self, tag: Optional[str] = None) -> List[str]:
        """获取自指定标签以来的提交"""
        if tag:
            range_spec = f"{tag}..HEAD"
        else:
            range_spec = "HEAD"
        
        try:
            output = self.run_command([
                "git", "log", range_spec,
                "--pretty=format:%H|%s|%b|%ad|%an",
                "--date=iso"
            ])
            return output.split('\n') if output else []
        except RuntimeError:
            return []
    
    def parse_commit(self, commit_line: str) -> Optional[CommitInfo]:
        """解析提交信息"""
        if not commit_line:
            return None
        
        parts = commit_line.split('|')
        if len(parts) < 5:
            return None
        
        hash_val, subject, body, date_str, author = parts[:5]
        
        # 解析提交类型和范围
        commit_pattern = r'^(\w+)(?:\(([^)]+)\))?: (.+)$'
        match = re.match(commit_pattern, subject)
        
        if match:
            commit_type, scope, description = match.groups()
        else:
            commit_type, scope, description = "other", None, subject
        
        # 检查是否为破坏性变更
        breaking = "BREAKING CHANGE" in body or subject.endswith("!")
        
        try:
            commit_date = datetime.fromisoformat(date_str.replace(' ', 'T'))
        except ValueError:
            commit_date = datetime.now()
        
        return CommitInfo(
            hash=hash_val,
            type=commit_type,
            scope=scope,
            description=description,
            body=body,
            breaking=breaking,
            date=commit_date,
            author=author
        )
    
    def create_tag(self, version: str, message: str) -> None:
        """创建标签"""
        tag_name = f"v{version}"
        self.run_command(["git", "tag", "-a", tag_name, "-m", message])
        print(f"✅ 创建标签: {tag_name}")
    
    def push_tag(self, version: str) -> None:
        """推送标签"""
        tag_name = f"v{version}"
        self.run_command(["git", "push", "origin", tag_name])
        print(f"✅ 推送标签: {tag_name}")
    
    def get_tag_list(self) -> List[str]:
        """获取所有标签列表"""
        try:
            output = self.run_command(["git", "tag", "-l", "--sort=-version:refname"])
            return output.split('\n') if output else []
        except RuntimeError:
            return []


class VersionManager:
    """版本管理器"""
    
    def __init__(self, repo_path: str = "."):
        self.git = GitManager(repo_path)
        self.repo_path = Path(repo_path)
    
    def get_current_version(self) -> VersionInfo:
        """获取当前版本"""
        latest_tag = self.git.get_latest_tag()
        if latest_tag:
            return VersionInfo.from_string(latest_tag)
        else:
            return VersionInfo(0, 1, 0)  # 默认初始版本
    
    def calculate_next_version(self, current: VersionInfo, commits: List[CommitInfo]) -> VersionInfo:
        """根据提交计算下一个版本"""
        has_breaking = any(commit.breaking for commit in commits)
        has_feat = any(commit.type == "feat" for commit in commits)
        has_fix = any(commit.type == "fix" for commit in commits)
        
        if has_breaking:
            # 破坏性变更，增加主版本号
            return VersionInfo(current.major + 1, 0, 0)
        elif has_feat:
            # 新功能，增加次版本号
            return VersionInfo(current.major, current.minor + 1, 0)
        elif has_fix:
            # 错误修复，增加补丁版本号
            return VersionInfo(current.major, current.minor, current.patch + 1)
        else:
            # 其他变更，增加补丁版本号
            return VersionInfo(current.major, current.minor, current.patch + 1)
    
    def generate_changelog_section(self, version: str, commits: List[CommitInfo]) -> str:
        """生成变更日志部分"""
        if not commits:
            return ""
        
        changelog = f"\n## [{version}] - {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        # 按类型分组提交
        grouped_commits = {}
        for commit in commits:
            commit_type = commit.type
            if commit_type not in grouped_commits:
                grouped_commits[commit_type] = []
            grouped_commits[commit_type].append(commit)
        
        # 定义类型顺序和标题
        type_order = [
            ("feat", "🚀 新功能"),
            ("fix", "🐛 错误修复"),
            ("perf", "⚡ 性能优化"),
            ("refactor", "♻️ 代码重构"),
            ("docs", "📚 文档更新"),
            ("style", "💄 代码格式"),
            ("test", "✅ 测试"),
            ("chore", "🔧 其他变更"),
            ("ci", "👷 CI/CD"),
            ("build", "📦 构建")
        ]
        
        for commit_type, title in type_order:
            if commit_type in grouped_commits:
                changelog += f"### {title}\n\n"
                for commit in grouped_commits[commit_type]:
                    scope_str = f"**{commit.scope}**: " if commit.scope else ""
                    breaking_str = " ⚠️ BREAKING CHANGE" if commit.breaking else ""
                    changelog += f"- {scope_str}{commit.description}{breaking_str} ([{commit.hash[:8]}])\n"
                changelog += "\n"
        
        # 处理其他类型的提交
        other_types = set(grouped_commits.keys()) - set(dict(type_order).keys())
        if other_types:
            changelog += "### 🔄 其他变更\n\n"
            for commit_type in sorted(other_types):
                for commit in grouped_commits[commit_type]:
                    scope_str = f"**{commit.scope}**: " if commit.scope else ""
                    changelog += f"- {scope_str}{commit.description} ([{commit.hash[:8]}])\n"
            changelog += "\n"
        
        return changelog
    
    def update_changelog(self, version: str, commits: List[CommitInfo]) -> None:
        """更新变更日志文件"""
        changelog_path = self.repo_path / "CHANGELOG.md"
        
        # 生成新的变更日志部分
        new_section = self.generate_changelog_section(version, commits)
        
        if changelog_path.exists():
            # 读取现有内容
            with open(changelog_path, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            # 在第一个 ## 之前插入新内容
            if "## [" in existing_content:
                parts = existing_content.split("## [", 1)
                new_content = parts[0] + new_section + "## [" + parts[1]
            else:
                new_content = existing_content + new_section
        else:
            # 创建新的变更日志文件
            header = "# 变更日志\n\n本文档记录了项目的所有重要变更。\n\n格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，\n并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。\n"
            new_content = header + new_section
        
        # 写入文件
        with open(changelog_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ 更新变更日志: {changelog_path}")
    
    def update_version_files(self, version: str) -> None:
        """更新版本文件"""
        version_files = [
            ("package.json", self._update_package_json),
            ("app/settings/config.py", self._update_python_version),
            ("version.txt", self._update_version_txt)
        ]
        
        for file_path, update_func in version_files:
            full_path = self.repo_path / file_path
            if full_path.exists():
                try:
                    update_func(full_path, version)
                    print(f"✅ 更新版本文件: {file_path}")
                except Exception as e:
                    print(f"⚠️ 更新版本文件失败 {file_path}: {e}")
    
    def _update_package_json(self, file_path: Path, version: str) -> None:
        """更新package.json版本"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        data['version'] = version
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _update_python_version(self, file_path: Path, version: str) -> None:
        """更新Python配置文件版本"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找VERSION变量并更新
        pattern = r'VERSION:\s*str\s*=\s*["\'][^"\']*["\']'
        replacement = f'VERSION: str = "{version}"'
        
        if re.search(pattern, content):
            new_content = re.sub(pattern, replacement, content)
        else:
            # 如果没找到，在类定义后添加
            pattern = r'(class Settings\(BaseSettings\):.*?\n)'
            replacement = f'\\1    VERSION: str = "{version}"\n'
            new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
    
    def _update_version_txt(self, file_path: Path, version: str) -> None:
        """更新version.txt文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(version)
    
    def create_release(self, version_type: str = "auto", prerelease: Optional[str] = None, dry_run: bool = False) -> None:
        """创建发布版本"""
        print("🚀 开始创建发布版本...")
        
        # 检查当前分支
        current_branch = self.git.get_current_branch()
        print(f"当前分支: {current_branch}")
        
        # 获取当前版本
        current_version = self.get_current_version()
        print(f"当前版本: v{current_version}")
        
        # 获取自上次标签以来的提交
        latest_tag = self.git.get_latest_tag()
        commit_lines = self.git.get_commits_since_tag(latest_tag)
        commits = [self.git.parse_commit(line) for line in commit_lines]
        commits = [c for c in commits if c is not None]
        
        if not commits:
            print("❌ 没有新的提交，无需创建新版本")
            return
        
        print(f"发现 {len(commits)} 个新提交")
        
        # 计算下一个版本
        if version_type == "auto":
            next_version = self.calculate_next_version(current_version, commits)
        elif version_type == "major":
            next_version = VersionInfo(current_version.major + 1, 0, 0)
        elif version_type == "minor":
            next_version = VersionInfo(current_version.major, current_version.minor + 1, 0)
        elif version_type == "patch":
            next_version = VersionInfo(current_version.major, current_version.minor, current_version.patch + 1)
        else:
            raise ValueError(f"不支持的版本类型: {version_type}")
        
        # 添加预发布标识
        if prerelease:
            next_version.prerelease = prerelease
        
        print(f"下一个版本: v{next_version}")
        
        if dry_run:
            print("🔍 预览模式，不会实际创建版本")
            print("\n变更日志预览:")
            print(self.generate_changelog_section(str(next_version), commits))
            return
        
        # 更新版本文件
        self.update_version_files(str(next_version))
        
        # 更新变更日志
        self.update_changelog(str(next_version), commits)
        
        # 创建标签
        tag_message = f"Release version {next_version}"
        self.create_tag(str(next_version), tag_message)
        
        print(f"✅ 成功创建版本 v{next_version}")
        print(f"💡 使用以下命令推送标签: git push origin v{next_version}")
    
    def list_versions(self) -> None:
        """列出所有版本"""
        tags = self.git.get_tag_list()
        if not tags:
            print("📝 暂无版本标签")
            return
        
        print("📋 版本列表:")
        for tag in tags[:10]:  # 显示最近10个版本
            print(f"  {tag}")
        
        if len(tags) > 10:
            print(f"  ... 还有 {len(tags) - 10} 个版本")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="版本管理工具")
    parser.add_argument("--repo", default=".", help="仓库路径")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 创建发布命令
    release_parser = subparsers.add_parser("release", help="创建新版本")
    release_parser.add_argument(
        "--type", 
        choices=["auto", "major", "minor", "patch"], 
        default="auto",
        help="版本类型"
    )
    release_parser.add_argument("--prerelease", help="预发布标识 (alpha, beta, rc)")
    release_parser.add_argument("--dry-run", action="store_true", help="预览模式")
    
    # 列出版本命令
    subparsers.add_parser("list", help="列出所有版本")
    
    # 当前版本命令
    subparsers.add_parser("current", help="显示当前版本")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    version_manager = VersionManager(args.repo)
    
    try:
        if args.command == "release":
            version_manager.create_release(
                version_type=args.type,
                prerelease=args.prerelease,
                dry_run=args.dry_run
            )
        elif args.command == "list":
            version_manager.list_versions()
        elif args.command == "current":
            current_version = version_manager.get_current_version()
            print(f"当前版本: v{current_version}")
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()