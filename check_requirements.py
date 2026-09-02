"""
System Requirements Checker
Checks for Python, Node.js, and required packages.
Auto-installs missing dependencies.
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

# ANSI colors for terminal output
class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    END = "\033[0m"

def print_step(step, message, status="info"):
    symbols = {
        "info": ">>",
        "success": "[OK]",
        "warning": "[WARN]",
        "error": "[ERROR]",
        "progress": "[...]"
    }
    colors = {
        "info": Colors.BLUE,
        "success": Colors.GREEN,
        "warning": Colors.YELLOW,
        "error": Colors.RED,
        "progress": Colors.BLUE
    }
    print(f"{colors.get(status, '')}{symbols.get(status, '•')} [{step}]{Colors.END} {message}")

def run_command(cmd, check=True, capture=True, timeout=300):
    """Run a shell command and return output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=capture,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout if capture else "", result.stderr if capture else ""
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except FileNotFoundError:
        return False, "", f"Command not found: {cmd.split()[0]}"
    except Exception as e:
        return False, "", str(e)

def check_python():
    """Check Python installation."""
    print_step("SYS", "Checking Python installation...", "progress")

    # Try python command
    success, stdout, stderr = run_command("python --version", timeout=10)
    if success:
        version = stdout.strip()
        print_step("SYS", f"Found: {version}", "success")

        # Check version compatibility
        try:
            import re
            match = re.search(r'Python (\d+)\.(\d+)', version)
            if match:
                major, minor = int(match.group(1)), int(match.group(2))
                if major == 3 and 10 <= minor <= 12:
                    print_step("SYS", "Python version is fully supported (3.10-3.12)", "success")
                elif major == 3 and minor >= 13:
                    print_step("SYS", "Python 3.13+ detected - may have PyTorch compatibility issues", "warning")
                    print_step("SYS", "Recommended: Python 3.10-3.12 from https://www.python.org/downloads/", "info")
                else:
                    print_step("SYS", f"Python 3.{minor} is older than recommended (3.10+)", "warning")
        except:
            pass
        return True

    # Try python3
    success, stdout, stderr = run_command("python3 --version", timeout=10)
    if success:
        version = stdout.strip()
        print_step("SYS", f"Found: {version}", "success")
        return True

    print_step("SYS", "Python not found!", "error")
    print()
    print("=" * 60)
    print("  PYTHON NOT INSTALLED - Please install Python 3.10 - 3.12")
    print("  Download: https://www.python.org/downloads/")
    print("  During installation, CHECK 'Add Python to PATH'")
    print("=" * 60)
    print()
    return False

def check_node():
    """Check Node.js installation."""
    print_step("SYS", "Checking Node.js installation...", "progress")

    success, stdout, stderr = run_command("node --version", timeout=10)
    if success:
        version = stdout.strip()
        print_step("SYS", f"Found: {version}", "success")
        return True

    print_step("SYS", "Node.js not found (needed for frontend build)", "warning")
    return False

def check_git():
    """Check Git installation (optional, for Git LFS fallback)."""
    print_step("SYS", "Checking Git installation (optional)...", "progress")

    success, stdout, stderr = run_command("git --version", timeout=10)
    if success:
        version = stdout.strip()
        print_step("SYS", f"Found: {version}", "success")

        # Check if git-lfs is available
        success_lfs, _, _ = run_command("git lfs version", timeout=10)
        if success_lfs:
            print_step("SYS", "Git LFS available (model fallback enabled)", "success")
        else:
            print_step("SYS", "Git LFS not installed (run: git lfs install)", "warning")
        return True

    print_step("SYS", "Git not found (optional - needed for Git LFS model fallback)", "warning")
    print_step("SYS", "Install from: https://git-scm.com/ (check 'Git from command line' option)", "info")
    return False

def check_pip_package(package):
    """Check if a pip package is installed."""
    success, _, _ = run_command(f'python -c "import {package}"', timeout=10)
    return success

def install_requirements():
    """Install Python requirements from requirements.txt."""
    print_step("PIP", "Checking Python packages...", "progress")

    requirements_file = Path("backend/requirements.txt")
    if not requirements_file.exists():
        print_step("PIP", "requirements.txt not found", "warning")
        return True

    # Read requirements
    with open(requirements_file, "r") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    missing = []
    for req in requirements:
        # Extract package name (before >=, ==, etc.)
        pkg_name = req.split(">")[0].split("=")[0].split("<")[0].strip()
        if not check_pip_package(pkg_name):
            missing.append(req)

    if not missing:
        print_step("PIP", "All Python packages installed", "success")
        return True

    print_step("PIP", f"Installing {len(missing)} missing packages...", "progress")

    # Try installing all at once
    cmd = f'python -m pip install --upgrade {" ".join(missing)}'
    success, stdout, stderr = run_command(cmd, timeout=300)

    if not success:
        print_step("PIP", "Failed to install all packages, trying one by one...", "warning")

        # Try installing individually
        failed = []
        for req in missing:
            pkg_name = req.split(">")[0].split("=")[0].split("<")[0].strip()
            print_step("PIP", f"  Installing {pkg_name}...", "progress")
            success, _, stderr = run_command(f"python -m pip install {req}", timeout=120)
            if not success:
                failed.append((pkg_name, stderr))

        if failed:
            print_step("PIP", "Some packages failed to install:", "warning")
            for pkg, err in failed:
                print(f"    {pkg}: {err[:100]}...")
            return False

    print_step("PIP", "All Python packages installed", "success")
    return True

def check_npm_packages():
    """Check if npm packages are installed."""
    print_step("NPM", "Checking npm packages...", "progress")

    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print_step("NPM", "Frontend directory not found", "warning")
        return True

    node_modules = frontend_dir / "node_modules"
    if node_modules.exists():
        print_step("NPM", "npm packages already installed", "success")
        return True

    print_step("NPM", "npm packages not installed, run: cd frontend && npm install", "warning")
    return True

def check_frontend_built():
    """Check if frontend is built."""
    print_step("UI", "Checking frontend build...", "progress")

    dist_dir = Path("frontend/dist")
    if dist_dir.exists() and (dist_dir / "index.html").exists():
        print_step("UI", "Frontend build found", "success")
        return True

    print_step("UI", "Frontend not built. Run: cd frontend && npm run build", "warning")
    return True

def run_full_check():
    """Run all system checks."""
    print()
    print("=" * 60)
    print("  OceanSpill System Requirements Check")
    print("=" * 60)
    print()

    results = {}

    # System requirements
    results["python"] = check_python()
    results["node"] = check_node()
    results["git"] = check_git()

    # Python packages
    if results["python"]:
        results["pip_packages"] = install_requirements()

    # Frontend
    results["npm"] = check_npm_packages()
    results["frontend_built"] = check_frontend_built()

    # Summary
    print()
    print("=" * 60)
    print("  Summary")
    print("=" * 60)
    print()

    all_passed = True
    for check, passed in results.items():
        status = "[OK]" if passed else "[FAILED]"
        print(f"  {check.replace('_', ' ').title()}: {status}")
        if not passed and check not in ["npm", "frontend_built"]:
            all_passed = False

    print()

    if all_passed:
        print_step("SYS", "All system requirements satisfied!", "success")
        print()
        return True
    else:
        print_step("SYS", "Some requirements not met. Please fix the issues above.", "error")
        print()
        return False

def auto_setup():
    """Attempt to automatically fix missing requirements."""
    print()
    print("=" * 60)
    print("  Auto-Setup Mode")
    print("=" * 60)
    print()

    # Check if we have Python
    if not check_python():
        print()
        print("Cannot auto-setup without Python. Please install Python manually.")
        return False

    # Try to create venv and install packages
    print_step("AUTO", "Creating virtual environment...", "progress")

    venv_path = Path("venv")
    if not venv_path.exists():
        success, _, err = run_command("python -m venv venv", timeout=60)
        if not success:
            print_step("AUTO", f"Failed to create venv: {err}", "error")
            return False

    print_step("AUTO", "Virtual environment created", "success")

    # Activate venv and install
    print_step("AUTO", "Installing packages in venv...", "progress")

    # Windows activate and install
    install_cmd = "venv\\Scripts\\python.exe -m pip install --upgrade pip"
    run_command(install_cmd, timeout=120)

    install_cmd = "venv\\Scripts\\python.exe -m pip install -r backend\\requirements.txt"
    success, _, err = run_command(install_cmd, timeout=300)

    if success:
        print_step("AUTO", "Packages installed successfully!", "success")
        print()
        print_step("SYS", "To run the app, use:", "info")
        print()
        print("  venv\\Scripts\\activate")
        print("  python -m uvicorn backend.main:app --reload")
        print()
        return True
    else:
        print_step("AUTO", f"Some packages failed: {err[:200]}", "warning")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--auto":
        success = auto_setup()
    else:
        success = run_full_check()

    sys.exit(0 if success else 1)