"""
Security scan — runs available DevSecOps tools and reports findings.
Gracefully skips tools that are not installed.

Usage:
  python security-scan.py [path]           # Scan a directory (default: workspace root)
  python security-scan.py --install        # Show install commands for all tools

Tools checked:
  1. bandit     — Python security linter
  2. pip-audit  — Python dependency vulnerabilities
  3. gitleaks   — Secret detection in git repos
  4. semgrep    — Multi-language static analysis
  5. trivy      — Container + filesystem scanning
"""
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Files/patterns to exclude from scanning (reduce false positives on encrypted/binary files)
EXCLUDE_PATTERNS = [
    "*.db", "*.sqlite", "*.sqlite3",
    "*.wallet", "*.p12", "*.pfx", "*.jks",
    "*.pyc", "*.pyo", "__pycache__",
    "node_modules", ".git", ".claude-memory",
    "*.whl", "*.egg-info", "*.tar.gz", "*.zip",
]

TOOLS = {
    "bandit": {
        "check": ["bandit", "--version"],
        "run": ["bandit", "-r", "{path}", "-f", "json", "-q",
                "--exclude", ",".join(d for d in EXCLUDE_PATTERNS if not d.startswith("*"))],
        "install": "pip install bandit",
        "desc": "Python security linter",
    },
    "pip-audit": {
        "check": ["pip-audit", "--version"],
        "run": ["pip-audit", "--format", "json", "--desc"],
        "install": "pip install pip-audit",
        "desc": "Python dependency vulnerabilities",
    },
    "gitleaks": {
        "check": ["gitleaks", "version"],
        "run": ["gitleaks", "detect", "--source", "{path}", "--report-format", "json",
                "--report-path", "-", "--no-banner"],
        "install": "brew install gitleaks  # or: choco install gitleaks",
        "desc": "Secret detection in git history",
    },
    "semgrep": {
        "check": ["semgrep", "--version"],
        "run": ["semgrep", "scan", "--config", "auto", "--json", "--quiet", "{path}"],
        "install": "pip install semgrep",
        "desc": "Multi-language static analysis",
    },
    "trivy": {
        "check": ["trivy", "--version"],
        "run": ["trivy", "fs", "--format", "json", "--scanners", "vuln,secret", "{path}"],
        "install": "brew install trivy  # or: choco install trivy",
        "desc": "Container + filesystem scanning",
    },
}


def check_tool(name: str) -> bool:
    try:
        subprocess.run(TOOLS[name]["check"], capture_output=True, timeout=10)
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def run_tool(name: str, path: str) -> dict:
    cmd = [arg.replace("{path}", path) for arg in TOOLS[name]["run"]]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        try:
            findings = json.loads(result.stdout)
        except (json.JSONDecodeError, ValueError):
            findings = result.stdout[:2000] if result.stdout else None
        return {
            "tool": name,
            "status": "ok" if result.returncode == 0 else "findings",
            "returncode": result.returncode,
            "findings": findings,
            "stderr": result.stderr[:500] if result.stderr else None,
        }
    except subprocess.TimeoutExpired:
        return {"tool": name, "status": "timeout", "findings": None}
    except Exception as e:
        return {"tool": name, "status": "error", "findings": str(e)}


def main():
    if "--install" in sys.argv:
        print("Install commands for security tools:\n")
        for name, info in TOOLS.items():
            available = check_tool(name)
            status = "installed" if available else "NOT FOUND"
            print(f"  [{status}] {name} — {info['desc']}")
            if not available:
                print(f"           {info['install']}")
        return

    scan_path = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "."
    scan_path = str(Path(scan_path).resolve())

    print(f"Security scan: {scan_path}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    available = []
    for name in TOOLS:
        if check_tool(name):
            available.append(name)
            print(f"  [OK] {name}")
        else:
            print(f"  [SKIP] {name} (not installed)")

    if not available:
        print("\nNo security tools found. Run: python security-scan.py --install")
        return

    print(f"\nRunning {len(available)} tools...\n")

    results = []
    total_findings = 0
    for name in available:
        print(f"  Scanning with {name}...", end=" ", flush=True)
        result = run_tool(name, scan_path)
        results.append(result)

        if result["status"] == "ok":
            print("clean")
        elif result["status"] == "findings":
            count = "?"
            if isinstance(result["findings"], list):
                count = len(result["findings"])
            elif isinstance(result["findings"], dict):
                count = result["findings"].get("metrics", {}).get("_totals", {}).get("findings", "?")
            print(f"{count} findings")
            if isinstance(count, int):
                total_findings += count
        else:
            print(f"{result['status']}")

    # Save report
    report = {
        "scan_path": scan_path,
        "timestamp": datetime.now().isoformat(),
        "tools_available": available,
        "tools_skipped": [n for n in TOOLS if n not in available],
        "total_findings": total_findings,
        "results": results,
    }

    report_dir = Path(scan_path) / ".claude-memory"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "security-scan.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\nSummary: {total_findings} findings from {len(available)} tools")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
