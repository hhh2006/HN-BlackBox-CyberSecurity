"""Deterministic offline audit for HN BlackBox release gates.

This tool inventories source files, parses Python, checks for unfinished-work
markers and high-risk dynamic execution patterns, and records the crypto engine
surface. It does not execute network actions or mutate project source files.
"""
from __future__ import annotations
import ast
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
EXCLUDE = {'.git', '__pycache__', '.pytest_cache', 'node_modules', 'dist'}
UNFINISHED = re.compile(r'\b(?:TODO|FIXME|NotImplemented)\b')
RISKY = re.compile(r'\b(?:eval|exec)\s*\(|\bshell\s*=\s*True\b|\bpickle\.loads\s*\(|\byaml\.load\s*\(')


def iter_source():
    for p in ROOT.rglob('*'):
        if not p.is_file() or any(part in EXCLUDE for part in p.parts):
            continue
        if p.suffix.lower() in {'.py', '.js', '.ts', '.tsx', '.css', '.html', '.json', '.bat', '.md'}:
            yield p


def main():
    files = list(iter_source())
    report = {
        'project': 'HN-BlackBox-CyberOpsv6',
        'python_files': 0,
        'source_files': len(files),
        'python_lines': 0,
        'syntax_errors': [],
        'unfinished_markers': [],
        'risky_patterns': [],
        'crypto_engine_files': [],
    }
    for p in files:
        text = p.read_text(encoding='utf-8', errors='ignore')
        if p.suffix.lower() == '.py':
            report['python_files'] += 1
            report['python_lines'] += len(text.splitlines())
            try:
                ast.parse(text, filename=str(p))
            except SyntaxError as exc:
                report['syntax_errors'].append({'file': str(p.relative_to(ROOT)), 'line': exc.lineno, 'message': exc.msg})
        if 'docs' not in p.parts and 'tests' not in p.parts and p.name != 'security_audit.py' and p.suffix.lower() not in {'.md'}:
            for i, line in enumerate(text.splitlines(), 1):
                if UNFINISHED.search(line):
                    report['unfinished_markers'].append({'file': str(p.relative_to(ROOT)), 'line': i, 'text': line.strip()[:180]})
                if RISKY.search(line):
                    report['risky_patterns'].append({'file': str(p.relative_to(ROOT)), 'line': i, 'text': line.strip()[:180]})
        if 'core' in p.parts and 'cryptography' in p.parts and p.suffix == '.py':
            report['crypto_engine_files'].append(str(p.relative_to(ROOT)))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not report['syntax_errors'] and not report['unfinished_markers'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
