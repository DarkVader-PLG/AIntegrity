#!/usr/bin/env python3
"""
PayloadGuard: Destructive Merge Detection with Forensic Report Generation

Maps three analytical layers to forensic report structure:
- Layer 1: Surface Scan → "What Was Presented"
- Layer 2: Deep Forensic → "What Branch Contains" + "What Gets Deleted" + "What Replaces It"
- Layer 3: Consequence → Verdict & Recommendations
- Layer 4: Structural Drift → Python class/function analysis
- Layer 5: Observations → Narrative interpretation & mismatch detection

Usage:
    python analyze.py /path/to/repo branch-name [target-branch] [--markdown]
    python analyze.py /path/to/repo feature-branch main --markdown
"""

import ast
import git
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


class StructuralPayloadAnalyzer:
    """
    Layer 4: AST-based structural drift detection.
    Detects removed classes and functions in Python files.
    """

    def __init__(self, original_code: str, modified_code: str):
        self.original_code = original_code
        self.modified_code = modified_code

    def _extract_core_nodes(self, source: str) -> dict:
        """Extract all classes and functions with context."""
        tree = ast.parse(source)
        nodes = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                node_type = "class" if isinstance(node, ast.ClassDef) else "function"
                nodes[node.name] = {
                    'type': node_type,
                    'lineno': node.lineno
                }
        return nodes

    def analyze_structural_drift(self) -> Dict[str, Any]:
        try:
            original_nodes = self._extract_core_nodes(self.original_code)
            modified_nodes = self._extract_core_nodes(self.modified_code)
        except SyntaxError as e:
            return {"error": str(e), "status": "PARSE_FAILURE"}

        deleted_nodes = set(original_nodes.keys()) - set(modified_nodes.keys())
        added_nodes = set(modified_nodes.keys()) - set(original_nodes.keys())
        n = len(original_nodes)
        deletion_ratio = len(deleted_nodes) / n if n else 0

        # Confidence scales to 1.0 at 10+ nodes
        confidence = min(n / 10.0, 1.0)
        score = deletion_ratio * confidence * 3.0

        return {
            "score": round(score, 3),
            "metrics": {
                "original_node_count": n,
                "deleted_node_count": len(deleted_nodes),
                "structural_deletion_ratio": round(deletion_ratio * 100, 2),
            },
            "deleted_components": sorted(deleted_nodes),
            "added_components": sorted(added_nodes),
        }


class ForensicReportGenerator:
    """
    Layer 5: Narrative interpretation and forensic report generation.
    
    Converts analytical data into human-readable forensic narrative,
    following the structure of CODEX_FORENSIC_REPORT.md:
    
    1. What Was Presented to the User
    2. What the Branch Actually Contains
    3. What Would Have Been Deleted
    4. What Would Have Replaced It
    5. Observations (presentation/payload mismatch, branch origin, consequences, irony)
    6. Summary (metrics table)
    """

    def __init__(self, analysis_data: Dict[str, Any], repo_path: str):
        self.data = analysis_data
        self.repo_path = repo_path

    def _detect_presentation_mismatch(self) -> List[str]:
        """Detect divergence between expected scope and actual payload."""
        observations = []
        
        files_deleted = self.data['files']['deleted']
        lines_deleted = self.data['lines']['deleted']
        days_old = self.data['temporal']['branch_age_days']
        deletion_ratio = self.data['lines']['deletion_ratio_percent']
        
        # Presentation/Payload mismatch
        if days_old > 180 and files_deleted > 20:
            observations.append(
                f"Branch is {days_old} days old but surfaces as current suggestion. "
                f"Actual payload predates {days_old} days of development."
            )
        
        if files_deleted > 50 and deletion_ratio > 90:
            observations.append(
                f"User shown a minor suggestion. Actual payload: {files_deleted} files deleted, "
                f"98%+ codebase reduction. Surface presentation does not communicate true scope."
            )
        
        # Branch origin mismatch
        if days_old > 365:
            observations.append(
                f"Branch origin (>{days_old} days ago) predates entire modern architecture. "
                f"Represents prototype state, not current working version."
            )
        
        return observations

    def _extract_section_1(self) -> str:
        """What Was Presented to the User"""
        branch = self.data['analysis']['branch']
        return f"""## 1. What Was Presented to the User

A suggestion to merge branch `{branch}` into the target branch.
The user was shown what appeared to be a routine code improvement.
"""

    def _extract_section_2(self) -> str:
        """What the Branch Actually Contains"""
        files_added = self.data['files']['added']
        lines_added = self.data['lines']['added']
        
        content = f"## 2. What the Branch Actually Contains\n\n"
        content += f"The branch contains exactly **{files_added} files**:\n\n"
        content += f"- {files_added} file(s) added\n"
        content += f"- {lines_added:,} line(s) of code\n\n"
        content += "### Commit history on the branch\n\n"
        
        try:
            branch_commit = self.data['temporal']['branch_commit_hash']
            content += f"```\nMost recent commit: {branch_commit}\n```\n"
        except:
            pass
        
        return content

    def _extract_section_3(self) -> str:
        """What Would Have Been Deleted"""
        files_deleted = self.data['files']['deleted']
        lines_deleted = self.data['lines']['deleted']
        deleted_files = self.data['deleted_files']['all']
        critical = self.data['deleted_files']['critical']
        
        content = f"## 3. What Would Have Been Deleted ({files_deleted} files, {lines_deleted:,} lines)\n\n"
        
        if critical:
            content += "### Critical Deletions\n\n"
            for f in critical[:10]:
                content += f"- `{f}`\n"
            if len(critical) > 10:
                content += f"- ... and {len(critical) - 10} more critical files\n"
            content += "\n"
        
        if deleted_files:
            content += "### All Deleted Files\n\n"
            for f in deleted_files[:20]:
                content += f"- `{f}`\n"
            if len(deleted_files) > 20:
                content += f"- ... and {len(deleted_files) - 20} more files\n"
        
        return content

    def _extract_section_4(self) -> str:
        """What Would Have Replaced It"""
        files_added = self.data['files']['added']
        lines_added = self.data['lines']['added']
        
        return f"""## 4. What Would Have Replaced It

A total of **{files_added} file(s)** containing **{lines_added:,} line(s)**.

This represents a **{self.data['lines']['codebase_reduction_percent']}% reduction** in codebase size.
"""

    def _extract_section_5(self) -> str:
        """Observations: narrative interpretation"""
        observations = self._detect_presentation_mismatch()
        verdict = self.data['verdict']
        
        content = "## 5. Observations\n\n"
        
        if observations:
            content += "### 5.1 Key Observations\n\n"
            for i, obs in enumerate(observations, 1):
                content += f"- {obs}\n"
            content += "\n"
        
        content += f"### 5.2 Verdict\n\n"
        content += f"**Status:** {verdict['status']}\n"
        content += f"**Severity:** {verdict['severity']}\n"
        content += f"**Recommendation:** {verdict['recommendation']}\n\n"
        
        if verdict.get('flags'):
            content += "### 5.3 Flags\n\n"
            for flag in verdict['flags']:
                content += f"- {flag}\n"
        
        return content

    def _extract_section_6(self) -> str:
        """Summary: metrics table"""
        content = "## 6. Summary\n\n"
        content += "| Metric | Value |\n"
        content += "|--------|-------|\n"
        content += f"| Files deleted | {self.data['files']['deleted']} |\n"
        content += f"| Lines deleted | {self.data['lines']['deleted']:,} |\n"
        content += f"| Files added | {self.data['files']['added']} |\n"
        content += f"| Lines added | {self.data['lines']['added']:,} |\n"
        content += f"| Branch age (days) | {self.data['temporal']['branch_age_days']} |\n"
        content += f"| Deletion ratio | {self.data['lines']['deletion_ratio_percent']}% |\n"
        content += f"| Codebase reduction | {self.data['lines']['codebase_reduction_percent']}% |\n"
        content += f"| Structural drift score | {self.data['structural'].get('score', 0.0)} |\n"
        
        return content

    def generate_markdown(self) -> str:
        """Generate complete forensic markdown report."""
        branch = self.data['analysis']['branch']
        target = self.data['analysis']['target']
        verdict = self.data['verdict']['status']
        timestamp = self.data['timestamp']
        
        report = f"""# Payload Forensic Analysis Report

**Date of analysis:** {timestamp[:10]}
**Analyst:** PayloadGuard
**Branch examined:** `{branch}`
**Target branch (if merged):** `{target}`
**Verdict:** {verdict}

---

"""
        report += self._extract_section_1()
        report += "\n---\n\n"
        report += self._extract_section_2()
        report += "\n---\n\n"
        report += self._extract_section_3()
        report += "\n---\n\n"
        report += self._extract_section_4()
        report += "\n---\n\n"
        report += self._extract_section_5()
        report += "\n---\n\n"
        report += self._extract_section_6()
        report += "\n\n---\n\n"
        report += "*Report generated by PayloadGuard — Destructive Merge Detection*\n"
        
        return report


class PayloadAnalyzer:
    """
    Multi-layer analysis system for detecting destructive merges.
    
    Layer 1: Surface Scan - Extract PR intent, identify red flags
    Layer 2: Deep Forensic Analysis - File/line deltas, temporal validation
    Layer 3: Consequence Modeling - What breaks if merged?
    Layer 4: Structural Drift - Python AST analysis
    Layer 5: Observations - Narrative interpretation & mismatch detection
    """
    
    def __init__(self, repo_path, branch, target_branch="main"):
        try:
            self.repo = git.Repo(repo_path)
        except Exception as e:
            print(f"ERROR: Could not open repository at {repo_path}")
            print(f"Details: {e}")
            sys.exit(1)
        
        self.branch = branch
        self.target = target_branch
        self.repo_path = repo_path
        
    def analyze(self) -> Dict[str, Any]:
        """Run complete multi-layer analysis."""
        try:
            try:
                self.repo.commit(self.target)
            except git.exc.BadName:
                return {
                    "error": f"Target branch '{self.target}' not found",
                    "available_branches": [ref.name for ref in self.repo.heads]
                }
            
            try:
                self.repo.commit(self.branch)
            except git.exc.BadName:
                return {
                    "error": f"Branch '{self.branch}' not found",
                    "available_branches": [ref.name for ref in self.repo.heads]
                }
            
            merge_base = self.repo.merge_base(self.target, self.branch)
            diffs = merge_base[0].diff(self.branch)
            
            # LAYER 2: DEEP FORENSIC ANALYSIS
            files_added = len([d for d in diffs if d.change_type == 'A'])
            files_deleted = len([d for d in diffs if d.change_type == 'D'])
            files_modified = len([d for d in diffs if d.change_type == 'M'])
            files_renamed = len([d for d in diffs if d.change_type == 'R'])
            files_copied = len([d for d in diffs if d.change_type == 'C'])
            files_typed = len([d for d in diffs if d.change_type == 'T'])
            
            lines_added = 0
            lines_deleted = 0
            
            for d in diffs:
                if d.change_type == 'A':
                    try:
                        content = d.b_blob.data_stream.read().decode('utf-8', errors='ignore')
                        lines_added += len(content.split('\n'))
                    except Exception:
                        pass
                elif d.change_type == 'D':
                    try:
                        content = d.a_blob.data_stream.read().decode('utf-8', errors='ignore')
                        lines_deleted += len(content.split('\n'))
                    except Exception:
                        pass
            
            # LAYER 4: STRUCTURAL DRIFT (Python files only)
            structural_score = 0.0
            structural_flags = []
            for d in diffs:
                if d.change_type != 'M':
                    continue
                path = d.b_path or d.a_path or ''
                if not path.endswith('.py'):
                    continue
                try:
                    original = d.a_blob.data_stream.read().decode('utf-8', errors='ignore')
                    modified = d.b_blob.data_stream.read().decode('utf-8', errors='ignore')
                    result = StructuralPayloadAnalyzer(original, modified).analyze_structural_drift()
                    if 'error' not in result and result['metrics']['deleted_node_count'] > 0:
                        structural_score = max(structural_score, result['score'])
                        structural_flags.append({
                            'file': path,
                            'score': result['score'],
                            'metrics': result['metrics'],
                            'deleted_components': result['deleted_components'],
                        })
                except Exception:
                    pass

            branch_commit = self.repo.commit(self.branch)
            target_commit = self.repo.commit(self.target)
            branch_date = branch_commit.committed_datetime
            target_date = target_commit.committed_datetime
            days_old = (target_date - branch_date).days
            
            total_lines_changed = lines_added + lines_deleted
            deletion_ratio = (lines_deleted / total_lines_changed * 100) if total_lines_changed > 0 else 0
            codebase_reduction = (lines_deleted / total_lines_changed * 100) if total_lines_changed > 0 else 0
            
            # LAYER 3: CONSEQUENCE ASSESSMENT
            verdict = self._assess_consequence(
                files_deleted,
                lines_deleted,
                days_old,
                deletion_ratio,
                structural_score,
            )
            
            deleted_files = [d.a_path for d in diffs if d.change_type == 'D']
            
            critical_patterns = [
                'test', 'tests', '.github/workflows', 'requirements', 'setup.py',
                '__init__.py', 'core', 'modules', 'config', '.yml', '.yaml'
            ]
            critical_deletions = [
                f for f in deleted_files 
                if any(pattern.lower() in f.lower() for pattern in critical_patterns)
            ]
            
            report = {
                "timestamp": datetime.now().isoformat(),
                "analysis": {
                    "branch": self.branch,
                    "target": self.target,
                    "repo_path": str(self.repo_path)
                },
                "files": {
                    "added": files_added,
                    "deleted": files_deleted,
                    "modified": files_modified,
                    "renamed": files_renamed,
                    "copied": files_copied,
                    "type_changed": files_typed,
                    "total_changed": files_added + files_deleted + files_modified + files_renamed + files_copied + files_typed
                },
                "lines": {
                    "added": lines_added,
                    "deleted": lines_deleted,
                    "net_change": lines_added - lines_deleted,
                    "deletion_ratio_percent": round(deletion_ratio, 1),
                    "codebase_reduction_percent": round(codebase_reduction, 1)
                },
                "temporal": {
                    "branch_age_days": days_old,
                    "branch_last_commit": branch_date.isoformat(),
                    "branch_commit_hash": branch_commit.hexsha[:7],
                    "target_last_commit": target_date.isoformat(),
                    "target_commit_hash": target_commit.hexsha[:7]
                },
                "verdict": verdict,
                "structural": {
                    "score": round(structural_score, 3),
                    "flagged_files": structural_flags[:10],
                },
                "deleted_files": {
                    "total": len(deleted_files),
                    "critical": critical_deletions[:10],
                    "all": deleted_files[:30]
                }
            }
            
            return report
            
        except Exception as e:
            return {
                "error": f"Analysis failed: {str(e)}",
                "error_type": type(e).__name__
            }
    
    def _assess_consequence(self, files_deleted, lines_deleted, days_old, deletion_ratio, structural_score=0.0):
        """LAYER 3: Assess consequence and determine verdict."""
        flags = []
        severity_score = 0.0
        
        if days_old > 365:
            flags.append(f"Branch is {days_old} days old (1+ year)")
            severity_score += 3
        elif days_old > 180:
            flags.append(f"Branch is {days_old} days old (6+ months)")
            severity_score += 2
        elif days_old > 90:
            flags.append(f"Branch is {days_old} days old (3+ months)")
            severity_score += 1
        
        if files_deleted > 50:
            flags.append(f"{files_deleted} files would be deleted (massive scope)")
            severity_score += 3
        elif files_deleted > 20:
            flags.append(f"{files_deleted} files would be deleted (large scope)")
            severity_score += 2
        elif files_deleted > 10:
            flags.append(f"{files_deleted} files would be deleted")
            severity_score += 1
        
        if deletion_ratio > 90:
            flags.append(f"Deletion ratio: {deletion_ratio}% (almost entire changeset is deletions)")
            severity_score += 3
        elif deletion_ratio > 70:
            flags.append(f"Deletion ratio: {deletion_ratio}% (majority of changes are deletions)")
            severity_score += 2
        elif deletion_ratio > 50:
            flags.append(f"Deletion ratio: {deletion_ratio}% (more deletions than additions)")
            severity_score += 1
        
        if structural_score >= 2.0:
            flags.append(f"Structural drift score: {structural_score:.2f} — significant Python class/function deletions")
            severity_score += structural_score
        elif structural_score >= 0.5:
            flags.append(f"Structural drift score: {structural_score:.2f} — Python class/function deletions detected")
            severity_score += structural_score

        if lines_deleted > 50000:
            flags.append(f"{lines_deleted:,} lines would be deleted (massive codebase change)")
            severity_score += 3
        elif lines_deleted > 10000:
            flags.append(f"{lines_deleted:,} lines would be deleted (large codebase change)")
            severity_score += 2
        elif lines_deleted > 5000:
            flags.append(f"{lines_deleted:,} lines would be deleted")
            severity_score += 1
        
        if severity_score >= 5:
            return {
                "status": "DESTRUCTIVE",
                "severity": "CRITICAL",
                "flags": flags,
                "recommendation": "❌ DO NOT MERGE — This would catastrophically alter the codebase",
                "severity_score": severity_score
            }
        elif severity_score >= 3:
            return {
                "status": "CAUTION",
                "severity": "HIGH",
                "flags": flags,
                "recommendation": "⚠️  REVIEW CAREFULLY — Significant destructive changes detected",
                "severity_score": severity_score
            }
        elif severity_score >= 1:
            return {
                "status": "REVIEW",
                "severity": "MEDIUM",
                "flags": flags if flags else ["Some changes detected"],
                "recommendation": "→ Proceed with normal review process, but note the flags above",
                "severity_score": severity_score
            }
        else:
            return {
                "status": "SAFE",
                "severity": "LOW",
                "flags": flags if flags else ["No major red flags detected"],
                "recommendation": "✓ Proceed with normal review process",
                "severity_score": severity_score
            }


def print_report(report):
    """Print human-readable summary."""
    if "error" in report:
        print("\n" + "="*70)
        print("❌ ANALYSIS FAILED")
        print("="*70)
        print(f"\nError: {report['error']}")
        if "error_type" in report:
            print(f"Type: {report['error_type']}")
        if "available_branches" in report:
            print(f"\nAvailable branches: {', '.join(report['available_branches'][:5])}")
        print()
        return
    
    analysis = report['analysis']
    files = report['files']
    lines = report['lines']
    temporal = report['temporal']
    verdict = report['verdict']
    deleted = report['deleted_files']
    
    print("\n" + "="*70)
    print(f"PAYLOAD GUARD: {analysis['branch']} → {analysis['target']}")
    print("="*70)
    
    print(f"\n📅 TEMPORAL ANALYSIS")
    print(f"   Branch age: {temporal['branch_age_days']} days")
    print(f"   Branch: {temporal['branch_commit_hash']} ({temporal['branch_last_commit'][:10]})")
    print(f"   Target: {temporal['target_commit_hash']} ({temporal['target_last_commit'][:10]})")
    
    print(f"\n📁 FILE CHANGES")
    print(f"   Added:    {files['added']:3d}")
    print(f"   Deleted:  {files['deleted']:3d}")
    print(f"   Modified: {files['modified']:3d}")
    print(f"   Total:    {files['total_changed']:3d}")
    
    print(f"\n📝 LINE CHANGES")
    print(f"   Added:    {lines['added']:>7,} lines")
    print(f"   Deleted:  {lines['deleted']:>7,} lines")
    print(f"   Net:      {lines['net_change']:>7,} lines")
    print(f"   Deletion ratio: {lines['deletion_ratio_percent']}%")
    print(f"   Codebase reduction: {lines['codebase_reduction_percent']}%")
    
    if 'structural' in report and report['structural']['score'] > 0:
        s = report['structural']
        print(f"\n🧬 STRUCTURAL DRIFT (Layer 4)")
        print(f"   Score: {s['score']:.3f} / 3.000")
        for f in s['flagged_files']:
            m = f['metrics']
            print(f"   {f['file']}: {m['deleted_node_count']} nodes deleted ({m['structural_deletion_ratio']}%)")
            for comp in f['deleted_components'][:5]:
                print(f"      - {comp}")

    print(f"\n🔍 VERDICT: {verdict['status']} [{verdict['severity']}]")
    for flag in verdict['flags']:
        print(f"   ⚠️  {flag}")
    
    print(f"\n✉️  RECOMMENDATION:")
    print(f"   {verdict['recommendation']}")
    
    if deleted['total'] > 0:
        print(f"\n🗑️  DELETED FILES ({deleted['total']} total)")
        if deleted['critical']:
            print(f"\n   CRITICAL DELETIONS:")
            for f in deleted['critical']:
                print(f"      - {f}")
        if deleted['all'] and len(deleted['all']) > 0:
            print(f"\n   OTHER DELETIONS:")
            for f in deleted['all'][:10]:
                print(f"      - {f}")
        if deleted['total'] > 30:
            remaining = deleted['total'] - len(deleted['all'])
            if remaining > 0:
                print(f"      ... and {remaining} more files")
    
    print("\n" + "="*70 + "\n")


def save_json_report(report, filename="payload_report.json"):
    """Save JSON report for CI/CD integration."""
    try:
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"✓ JSON report saved to {filename}")
        return True
    except Exception as e:
        print(f"⚠️  Could not save JSON report: {e}")
        return False


def save_markdown_report(report, repo_path, filename=None):
    """Save markdown forensic report."""
    if filename is None:
        branch = report['analysis']['branch'].replace('/', '_')
        filename = f"forensic_report_{branch}.md"
    
    try:
        generator = ForensicReportGenerator(report, repo_path)
        markdown = generator.generate_markdown()
        with open(filename, 'w') as f:
            f.write(markdown)
        print(f"✓ Markdown report saved to {filename}")
        return True
    except Exception as e:
        print(f"⚠️  Could not save markdown report: {e}")
        return False


def main():
    if len(sys.argv) < 3:
        print("\n" + "="*70)
        print("PAYLOADGUARD v1.0")
        print("="*70)
        print("\nDetects destructive payloads hidden in code suggestions before merge")
        print("\nUSAGE:")
        print("  python analyze.py <repo_path> <branch> [target_branch] [--markdown]")
        print("\nEXAMPLES:")
        print("  python analyze.py . feature-branch main")
        print("  python analyze.py . feature-branch main --markdown")
        print("  python analyze.py /path/to/repo old-branch main --markdown")
        print("\nDEFAULTS:")
        print("  target_branch: main")
        print("\nOUTPUT:")
        print("  - Console summary")
        print("  - JSON report (payload_report.json)")
        print("  - Markdown forensic report (if --markdown flag)")
        print("\nEXIT CODES:")
        print("  0 = SAFE")
        print("  1 = ERROR")
        print("  2 = DESTRUCTIVE")
        print("\n" + "="*70 + "\n")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    branch = sys.argv[2]
    target_branch = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else "main"
    generate_markdown = '--markdown' in sys.argv
    
    analyzer = PayloadAnalyzer(repo_path, branch, target_branch)
    report = analyzer.analyze()
    print_report(report)
    
    if "error" not in report:
        save_json_report(report)
        if generate_markdown:
            save_markdown_report(report, repo_path)
    
    # Exit codes for CI/CD
    if "error" in report:
        sys.exit(1)
    elif report.get('verdict', {}).get('status') == 'DESTRUCTIVE':
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
