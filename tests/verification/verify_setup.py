"""Verify project setup and dependencies"""
import sys
from pathlib import Path


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Current: {version.major}.{version.minor}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True


def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'pandas', 'numpy', 'tqdm', 'yaml'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'yaml':
                __import__('yaml')
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NOT INSTALLED")
            missing.append(package)
    
    # Check google-play-scraper separately
    try:
        import google_play_scraper
        print("✅ google-play-scraper")
    except ImportError:
        print("❌ google-play-scraper - NOT INSTALLED")
        missing.append('google-play-scraper')
    
    return len(missing) == 0


def check_directories():
    """Check if required directories exist"""
    project_root = Path(__file__).parent.parent.parent
    required_dirs = [
        'src', 'scripts', 'tests', 'config',
        'data/raw', 'data/processed', 'logs'
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"✅ {dir_path}/")
        else:
            print(f"⚠️  {dir_path}/ - Will be created automatically")
            all_exist = False
    
    return all_exist


def check_config_files():
    """Check if configuration files exist"""
    project_root = Path(__file__).parent.parent.parent
    config_file = project_root / "config" / "config.yaml"
    env_template = project_root / "env_template.txt"
    
    config_ok = config_file.exists()
    env_ok = env_template.exists()
    
    if config_ok:
        print("✅ config/config.yaml")
    else:
        print("❌ config/config.yaml - MISSING")
    
    if env_ok:
        print("✅ env_template.txt")
    else:
        print("⚠️  env_template.txt - MISSING")
    
    return config_ok


def main():
    """Run all verification checks"""
    print("=" * 60)
    print("PROJECT SETUP VERIFICATION")
    print("=" * 60)
    print()
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Directories", check_directories),
        ("Config Files", check_config_files)
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        print("-" * 60)
        result = check_func()
        results.append((name, result))
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = all(result for _, result in results)
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
    
    if all_passed:
        print("\n🎉 All checks passed! Project is ready to use.")
        return 0
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

