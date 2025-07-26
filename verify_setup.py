#!/usr/bin/env python3
"""
Final verification script for Discord bot deployment
"""

import os
import json
import sys

def check_files():
    """Check if all required files exist"""
    required_files = [
        'bot.py',
        'database.py', 
        'utils.py',
        'requirements.txt',
        'runtime.txt',
        'Procfile',
        'render.yaml',
        'RENDER_SETUP.md',
        'render_env_example.txt',
        'README.md',
        '.gitignore'
    ]
    
    print("📋 Checking required files...")
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            missing_files.append(file)
    
    return missing_files

def check_python_syntax():
    """Check Python syntax of main files"""
    print("\n🐍 Checking Python syntax...")
    
    python_files = ['bot.py', 'database.py', 'utils.py']
    syntax_errors = []
    
    for file in python_files:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                compile(f.read(), file, 'exec')
            print(f"✅ {file} - Syntax OK")
        except SyntaxError as e:
            print(f"❌ {file} - Syntax Error: {e}")
            syntax_errors.append(f"{file}: {e}")
        except Exception as e:
            print(f"⚠️  {file} - Warning: {e}")
    
    return syntax_errors

def check_config():
    """Check configuration files"""
    print("\n⚙️ Checking configuration...")
    
    # Check config.json
    if os.path.exists('config.json'):
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            print("✅ config.json - Valid JSON")
            
            # Check for placeholder values
            placeholders = []
            for key, value in config.items():
                if isinstance(value, str) and 'YOUR_' in value:
                    placeholders.append(key)
            
            if placeholders:
                print(f"⚠️  Placeholder values found: {', '.join(placeholders)}")
                print("   These should be set as environment variables in Render")
            else:
                print("✅ All configuration values are set")
                
        except json.JSONDecodeError as e:
            print(f"❌ config.json - Invalid JSON: {e}")
            return False
    else:
        print("⚠️  config.json not found (will use environment variables)")
    
    # Check render.yaml
    if os.path.exists('render.yaml'):
        try:
            with open('render.yaml', 'r') as f:
                yaml_content = f.read()
            print("✅ render.yaml - File exists")
        except Exception as e:
            print(f"❌ render.yaml - Error: {e}")
            return False
    
    return True

def check_requirements():
    """Check requirements.txt"""
    print("\n📦 Checking requirements...")
    
    if os.path.exists('requirements.txt'):
        try:
            with open('requirements.txt', 'r') as f:
                requirements = f.read().strip().split('\n')
            
            if requirements:
                print(f"✅ requirements.txt - {len(requirements)} packages listed")
                for req in requirements:
                    if req.strip():
                        print(f"   📦 {req.strip()}")
            else:
                print("❌ requirements.txt - Empty file")
                return False
        except Exception as e:
            print(f"❌ requirements.txt - Error: {e}")
            return False
    else:
        print("❌ requirements.txt - Missing")
        return False
    
    return True

def check_render_files():
    """Check Render-specific files"""
    print("\n🚀 Checking Render deployment files...")
    
    render_files = {
        'runtime.txt': 'Python version specification',
        'Procfile': 'Process definition',
        'render.yaml': 'Render configuration',
        'RENDER_SETUP.md': 'Deployment guide'
    }
    
    for file, description in render_files.items():
        if os.path.exists(file):
            print(f"✅ {file} - {description}")
        else:
            print(f"❌ {file} - Missing ({description})")
            return False
    
    return True

def main():
    """Main verification function"""
    print("🔍 Discord Bot Deployment Verification")
    print("=" * 50)
    
    all_good = True
    
    # Check files
    missing_files = check_files()
    if missing_files:
        all_good = False
    
    # Check Python syntax
    syntax_errors = check_python_syntax()
    if syntax_errors:
        all_good = False
    
    # Check configuration
    if not check_config():
        all_good = False
    
    # Check requirements
    if not check_requirements():
        all_good = False
    
    # Check Render files
    if not check_render_files():
        all_good = False
    
    # Final summary
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 VERIFICATION COMPLETE - ALL CHECKS PASSED!")
        print("\n✅ Your Discord bot is ready for deployment!")
        print("\n📋 Next steps:")
        print("1. Create GitHub repository")
        print("2. Upload all files to GitHub")
        print("3. Follow RENDER_SETUP.md for deployment")
        print("4. Set environment variables in Render dashboard")
    else:
        print("❌ VERIFICATION FAILED - Please fix the issues above")
        print("\n🔧 Issues to fix:")
        if missing_files:
            print(f"   - Missing files: {', '.join(missing_files)}")
        if syntax_errors:
            print(f"   - Syntax errors: {len(syntax_errors)} found")
        print("   - Check the error messages above")
    
    print("\n📚 For help, check RENDER_SETUP.md")
    
    return all_good

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 