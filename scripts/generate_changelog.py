#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
变更日志生成工具
自动生成和维护项目变更日志
"""

import os
import re
import sys
import subprocess
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import argparse


class ChangelogGenerator:
    """变更日志生成器"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path)
        self.changelog_path = self.repo_path / "CHANGELOG.md"
    
    def run_git_command(self, command: List[str]) -> str:
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
    
    def get_commits_between_tags(self, from_tag: Optional[str] = None, to_tag: str = "HEAD") -> List[Dict]:
        """获取两个标签之间的提交"""
        if from_tag:
            range_spec = f"{from_tag}..{to_tag}"
        else:
            range_spec = to_tag
        
        try:
            # 获取提交信息
            output = self.run_git_command([
                "git", "log", range_spec,
                "--pretty=format:%H|%s|%b|%ad|%an|%ae",
                "--date=iso"
            ])
            
            commits = []
            for line in output.split('\n'):
                if not line:
                    continue
                
                parts = line.split('|')
                if len(parts) >= 6:
                    commit_hash, subject, body, date_str, author_name, author_email = parts[:6]
                    
                    # 解析提交类型
                    commit_type, scope, description, breaking = self.parse_commit_message(subject)
                    
                    commits.append({
                        'hash': commit_hash,
                        'subject': subject,
                        'body': body,
                        'type': commit_type,
                        'scope': scope,
                        'description': description,
                        'breaking': breaking,
                        'date': date_str,
                        'author_name': author_name,
                        'author_email': author_email
                    })
            
            return commits
        except RuntimeError:
            return []
    
    def parse_commit_message(self, subject: str) -> Tuple[str, Optional[str], str, bool]:
        """解析提交消息"""
        # Conventional Commits 格式: type(scope): description
        pattern = r'^(\w+)(?:\(([^)]+)\))?: (.+)$'
        match = re.match(pattern, subject)
        
        if match:
            commit_type, scope, description = match.groups()
        else:
            commit_type, scope, description = "other", None, subject
        
        # 检查破坏性变更
        breaking = subject.endswith("!") or "BREAKING CHANGE" in subject
        
        return commit_type, scope, description, breaking
    
    def get_all_tags(self) -> List[str]:
        """获取所有标签"""
        try:
            output = self.run_git_command(["git", "tag", "-l", "--sort=-version:refname"])
            return output.split('\n') if output else []
        except RuntimeError:
            return []
    
    def get_tag_date(self, tag: str) -> str:
        """获取标签日期"""
        try:
            output = self.run_git_command(["git", "log", "-1", "--format=%ad", "--date=short", tag])
            return output
        except RuntimeError:
            return datetime.now().strftime('%Y-%m-%d')
    
    def group_commits_by_type(self, commits: List[Dict]) -> Dict[str, List[Dict]]:
        """按类型分组提交"""
        grouped = {}
        for commit in commits:
            commit_type = commit['type']
            if commit_type not in grouped:
                grouped[commit_type] = []
            grouped[commit_type].append(commit)
        return grouped
    
    def format_commit_entry(self, commit: Dict) -> str:
        """格式化提交条目"""
        scope_str = f"**{commit['scope']}**: " if commit['scope'] else ""
        breaking_str = " ⚠️ BREAKING CHANGE" if commit['breaking'] else ""
        hash_short = commit['hash'][:8]
        
        return f"- {scope_str}{commit['description']}{breaking_str} ([{hash_short}])"
    
    def generate_section_for_version(self, version: str, commits: List[Dict], date: str = None) -> str:
        """为特定版本生成变更日志部分"""
        if not commits:
            return ""
        
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        section = f"\n## [{version}] - {date}\n\n"
        
        # 按类型分组
        grouped_commits = self.group_commits_by_type(commits)
        
        # 定义类型顺序和标题映射
        type_mapping = {
            'feat': ('🚀 新功能', 'Features'),
            'fix': ('🐛 错误修复', 'Bug Fixes'),
            'perf': ('⚡ 性能优化', 'Performance Improvements'),
            'refactor': ('♻️ 代码重构', 'Code Refactoring'),
            'docs': ('📚 文档更新', 'Documentation'),
            'style': ('💄 代码格式', 'Styles'),
            'test': ('✅ 测试', 'Tests'),
            'chore': ('🔧 其他变更', 'Chores'),
            'ci': ('👷 CI/CD', 'Continuous Integration'),
            'build': ('📦 构建', 'Build System'),
            'revert': ('⏪ 回滚', 'Reverts')
        }
        
        # 按优先级排序类型
        type_order = ['feat', 'fix', 'perf', 'refactor', 'docs', 'style', 'test', 'chore', 'ci', 'build', 'revert']
        
        # 生成各类型的变更
        for commit_type in type_order:
            if commit_type in grouped_commits:
                emoji_title, english_title = type_mapping[commit_type]
                section += f"### {emoji_title}\n\n"
                
                for commit in grouped_commits[commit_type]:
                    section += self.format_commit_entry(commit) + "\n"
                section += "\n"
        
        # 处理其他类型
        other_types = set(grouped_commits.keys()) - set(type_order)
        if other_types:
            section += "### 🔄 其他变更\n\n"
            for commit_type in sorted(other_types):
                for commit in grouped_commits[commit_type]:
                    section += self.format_commit_entry(commit) + "\n"
            section += "\n"
        
        return section
    
    def generate_full_changelog(self) -> str:
        """生成完整的变更日志"""
        print("🔄 生成完整变更日志...")
        
        # 获取所有标签
        tags = self.get_all_tags()
        
        if not tags:
            print("⚠️ 没有找到任何标签，生成从HEAD开始的变更日志")
            commits = self.get_commits_between_tags()
            if commits:
                return self.generate_section_for_version("Unreleased", commits)
            else:
                return "# 变更日志\n\n暂无变更记录。\n"
        
        # 生成变更日志头部
        changelog = """# 变更日志

本文档记录了项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

"""
        
        # 生成未发布的变更
        unreleased_commits = self.get_commits_between_tags(tags[0], "HEAD")
        if unreleased_commits:
            changelog += self.generate_section_for_version("Unreleased", unreleased_commits)
        
        # 生成每个版本的变更
        for i, tag in enumerate(tags):
            print(f"处理标签: {tag}")
            
            # 获取标签日期
            tag_date = self.get_tag_date(tag)
            
            # 获取该版本的提交
            if i < len(tags) - 1:
                # 不是最后一个标签，获取与上一个标签之间的提交
                commits = self.get_commits_between_tags(tags[i + 1], tag)
            else:
                # 最后一个标签，获取从开始到该标签的所有提交
                commits = self.get_commits_between_tags(None, tag)
            
            if commits:
                version = tag.lstrip('v')  # 移除 'v' 前缀
                changelog += self.generate_section_for_version(version, commits, tag_date)
        
        return changelog
    
    def generate_since_last_tag(self) -> str:
        """生成自上次标签以来的变更日志"""
        print("🔄 生成自上次标签以来的变更日志...")
        
        tags = self.get_all_tags()
        last_tag = tags[0] if tags else None
        
        commits = self.get_commits_between_tags(last_tag, "HEAD")
        
        if not commits:
            return "暂无新的变更。\n"
        
        version = "Unreleased"
        return self.generate_section_for_version(version, commits)
    
    def update_changelog_file(self, content: str) -> None:
        """更新变更日志文件"""
        with open(self.changelog_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ 变更日志已更新: {self.changelog_path}")
    
    def preview_changelog(self, content: str) -> None:
        """预览变更日志"""
        print("📋 变更日志预览:")
        print("-" * 80)
        print(content)
        print("-" * 80)
    
    def get_contributors(self, from_tag: Optional[str] = None) -> List[Dict]:
        """获取贡献者列表"""
        commits = self.get_commits_between_tags(from_tag, "HEAD")
        
        contributors = {}
        for commit in commits:
            email = commit['author_email']
            name = commit['author_name']
            
            if email not in contributors:
                contributors[email] = {
                    'name': name,
                    'email': email,
                    'commits': 0
                }
            contributors[email]['commits'] += 1
        
        # 按提交数排序
        return sorted(contributors.values(), key=lambda x: x['commits'], reverse=True)
    
    def generate_release_notes(self, version: str, from_tag: Optional[str] = None) -> str:
        """生成发布说明"""
        commits = self.get_commits_between_tags(from_tag, "HEAD")
        
        if not commits:
            return f"# Release {version}\n\n暂无变更。\n"
        
        # 生成变更日志部分
        changelog_section = self.generate_section_for_version(version, commits)
        
        # 获取贡献者
        contributors = self.get_contributors(from_tag)
        
        # 生成发布说明
        release_notes = f"# Release {version}\n"
        release_notes += f"\n发布日期: {datetime.now().strftime('%Y-%m-%d')}\n"
        release_notes += changelog_section
        
        if contributors:
            release_notes += "## 🙏 贡献者\n\n"
            for contributor in contributors:
                release_notes += f"- {contributor['name']} ({contributor['commits']} commits)\n"
            release_notes += "\n"
        
        # 统计信息
        total_commits = len(commits)
        feat_count = len([c for c in commits if c['type'] == 'feat'])
        fix_count = len([c for c in commits if c['type'] == 'fix'])
        
        release_notes += "## 📊 统计信息\n\n"
        release_notes += f"- 总提交数: {total_commits}\n"
        release_notes += f"- 新功能: {feat_count}\n"
        release_notes += f"- 错误修复: {fix_count}\n"
        release_notes += f"- 贡献者: {len(contributors)}\n"
        
        return release_notes


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="变更日志生成工具")
    parser.add_argument("--repo", default=".", help="仓库路径")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 生成完整变更日志
    full_parser = subparsers.add_parser("full", help="生成完整变更日志")
    full_parser.add_argument("--preview", action="store_true", help="预览模式")
    
    # 生成自上次标签以来的变更
    since_parser = subparsers.add_parser("since", help="生成自上次标签以来的变更")
    since_parser.add_argument("--preview", action="store_true", help="预览模式")
    
    # 生成发布说明
    release_parser = subparsers.add_parser("release", help="生成发布说明")
    release_parser.add_argument("version", help="版本号")
    release_parser.add_argument("--from-tag", help="起始标签")
    release_parser.add_argument("--output", help="输出文件路径")
    
    # 获取贡献者列表
    contributors_parser = subparsers.add_parser("contributors", help="获取贡献者列表")
    contributors_parser.add_argument("--from-tag", help="起始标签")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    generator = ChangelogGenerator(args.repo)
    
    try:
        if args.command == "full":
            content = generator.generate_full_changelog()
            if args.preview:
                generator.preview_changelog(content)
            else:
                generator.update_changelog_file(content)
        
        elif args.command == "since":
            content = generator.generate_since_last_tag()
            if args.preview:
                generator.preview_changelog(content)
            else:
                print(content)
        
        elif args.command == "release":
            content = generator.generate_release_notes(args.version, args.from_tag)
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 发布说明已保存到: {args.output}")
            else:
                print(content)
        
        elif args.command == "contributors":
            contributors = generator.get_contributors(args.from_tag)
            print("🙏 贡献者列表:")
            for contributor in contributors:
                print(f"  {contributor['name']} <{contributor['email']}> ({contributor['commits']} commits)")
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()