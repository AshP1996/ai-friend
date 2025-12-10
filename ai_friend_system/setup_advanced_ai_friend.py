"""
AI Friend Advanced Setup - One-Click Installation & Startup
Automatically installs all dependencies and starts all services
"""

import os
import sys
import subprocess
import platform
import time
from pathlib import Path
from typing import List, Tuple

class Color:
    HEADER = '\\033[95m'
    BLUE = '\\033[94m'
    CYAN = '\\033[96m'
    GREEN = '\\033[92m'
    YELLOW = '\\033[93m'
    RED = '\\033[91m'
    END = '\\033[0m'
    BOLD = '\\033[1m'

def print_header(text):
    print(f"\\n{Color.BOLD}{Color.CYAN}{'='*70}")
    print(f"{text.center(70)}")
    print(f"{'='*70}{Color.END}\\n")

def print_step(step_num, text):
    print(f"{Color.BOLD}{Color.GREEN}[{step_num}]{Color.END} {text}")

def print_success(text):
    print(f"{Color.GREEN}✅ {text}{Color.END}")

def print_error(text):
    print(f"{Color.RED}❌ {text}{Color.END}")

def print_warning(text):
    print(f"{Color.YELLOW}⚠️  {text}{Color.END}")

def print_info(text):
    print(f"{Color.BLUE}ℹ️  {text}{Color.END}")

def run_command(cmd: List[str], description: str, ignore_error: bool = False) -> bool:
    """Run a command and return success status"""
    try:
        print(f"   Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print_success(description)
        return True
    except subprocess.CalledProcessError as e:
        if ignore_error:
            print_warning(f"{description} (non-critical)")
            return True
        print_error(f"{description} failed: {e.stderr}")
        return False
    except FileNotFoundError:
        print_error(f"Command not found: {cmd[0]}")
        return False

def check_python_version():
    """Check if Python version is 3.8+"""
    print_step(1, "Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} ✓")
        return True
    else:
        print_error(f"Python 3.8+ required, found {version.major}.{version.minor}")
        return False

def check_and_install_redis():
    """Check if Redis is installed and running"""
    print_step(2, "Checking Redis installation...")
    
    # Check if redis-server exists
    try:
        subprocess.run(['redis-server', '--version'], 
                      capture_output=True, check=True)
        print_success("Redis is installed")
        
        # Try to ping Redis
        try:
            result = subprocess.run(['redis-cli', 'ping'], 
                                   capture_output=True, text=True, timeout=2)
            if 'PONG' in result.stdout:
                print_success("Redis is running")
                return True
        except:
            pass
        
        # Redis installed but not running - start it
        print_info("Starting Redis server...")
        if platform.system() == 'Windows':
            subprocess.Popen(['redis-server'], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(['redis-server'], 
                           stdout=subprocess.DEVNULL, 
                           stderr=subprocess.DEVNULL)
        
        time.sleep(2)
        print_success("Redis server started")
        return True
        
    except FileNotFoundError:
        print_warning("Redis not installed")
        print_info("Installing Redis...")
        
        system = platform.system()
        if system == 'Linux':
            print_info("Run: sudo apt-get install redis-server")
        elif system == 'Darwin':  # macOS
            print_info("Run: brew install redis")
        elif system == 'Windows':
            print_info("Download from: https://redis.io/download")
        
        print_error("Please install Redis manually and run this script again")
        return False

def check_ollama():
    """Check if Ollama is installed and running"""
    print_step(3, "Checking Ollama (optional)...")
    
    try:
        result = subprocess.run(['ollama', 'list'], 
                              capture_output=True, text=True, timeout=3)
        print_success("Ollama is installed")
        
        # Check if llama2 model exists
        if 'llama2' in result.stdout:
            print_success("Llama2 model found")
        else:
            print_warning("Llama2 model not found")
            print_info("You can install it with: ollama pull llama2")
        return True
        
    except:
        print_warning("Ollama not found (optional - system works without it)")
        print_info("For better AI responses, install from: https://ollama.com")
        return True  # Not critical

def create_env_file():
    """Create .env file if it doesn't exist"""
    print_step(4, "Creating environment file...")
    
    env_file = Path('.env')
    if env_file.exists():
        print_info(".env file already exists")
        return True
    
    env_content = """# AI Friend - Environment Configuration

# AI Model API Keys (Optional)
ANTHROPIC_API_KEY=
OPENAI_API_KEY=

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
DEBUG=true
LOG_LEVEL=INFO
"""
    
    env_file.write_text(env_content)
    print_success(".env file created")
    return True

def install_dependencies():
    """Install Python dependencies"""
    print_step(5, "Installing Python dependencies...")
    print_info("This may take several minutes...")
    
    # Upgrade pip first
    run_command([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'],
                "Upgrading pip", ignore_error=True)
    
    # Install requirements
    if not run_command([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'],
                       "Installing dependencies"):
        return False
    
    # Download textblob corpora
    print_info("Downloading NLP data...")
    run_command([sys.executable, '-m', 'textblob.download_corpora'],
                "NLP data downloaded", ignore_error=True)
    
    return True

def setup_database():
    """Initialize database"""
    print_step(6, "Setting up database...")
    return run_command([sys.executable, 'setup_database.py'],
                       "Database initialized")

def start_services():
    """Start all services"""
    print_step(7, "Starting services...")
    
    print_info("Services will start in separate terminals...")
    print_info("You can monitor them in the background")
    
    services = []
    
    # Start Celery Worker
    print_info("Starting Celery worker...")
    if platform.system() == 'Windows':
        celery_worker = subprocess.Popen(
            [sys.executable, '-m', 'celery', '-A', 'tasks.celery_tasks', 'worker', '--loglevel=info', '--pool=solo'],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        celery_worker = subprocess.Popen(
            [sys.executable, '-m', 'celery', '-A', 'tasks.celery_tasks', 'worker', '--loglevel=info'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    services.append(('Celery Worker', celery_worker))
    time.sleep(2)
    
    # Start Celery Beat
    print_info("Starting Celery beat...")
    if platform.system() == 'Windows':
        celery_beat = subprocess.Popen(
            [sys.executable, '-m', 'celery', '-A', 'tasks.celery_tasks', 'beat', '--loglevel=info'],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        celery_beat = subprocess.Popen(
            [sys.executable, '-m', 'celery', '-A', 'tasks.celery_tasks', 'beat', '--loglevel=info'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    services.append(('Celery Beat', celery_beat))
    time.sleep(1)
    
    # Start Flower (monitoring)
    print_info("Starting Flower monitoring...")
    if platform.system() == 'Windows':
        flower = subprocess.Popen(
            [sys.executable, '-m', 'celery', '-A', 'tasks.celery_tasks', 'flower', '--port=5555'],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
    else:
        flower = subprocess.Popen(
            [sys.executable, '-m', 'celery', '-A', 'tasks.celery_tasks', 'flower', '--port=5555'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    services.append(('Flower', flower))
    time.sleep(2)
    
    print_success("Background services started")
    return services

def start_api_server():
    """Start FastAPI server"""
    print_step(8, "Starting FastAPI server...")
    
    print_info("API server starting on http://localhost:8000")
    print_info("Press Ctrl+C to stop all services")
    
    try:
        subprocess.run([sys.executable, 'main.py', '--mode', 'api'])
    except KeyboardInterrupt:
        print_info("\\nShutting down...")
        return True

def main():
    """Main setup function"""
    print_header("🤖 AI FRIEND ADVANCED - ONE-CLICK SETUP 🤖")
    
    print(f"{Color.CYAN}This script will:")
    print("  1. Check Python version")
    print("  2. Install and start Redis")
    print("  3. Check Ollama (optional)")
    print("  4. Create environment file")
    print("  5. Install all dependencies")
    print("  6. Initialize database")
    print("  7. Start Celery workers")
    print("  8. Start API server")
    print(f"{Color.END}")
    
    input("Press Enter to continue...")
    
    # Run all setup steps
    if not check_python_version():
        sys.exit(1)
    
    if not check_and_install_redis():
        sys.exit(1)
    
    check_ollama()  # Optional
    
    if not create_env_file():
        sys.exit(1)
    
    if not install_dependencies():
        sys.exit(1)
    
    if not setup_database():
        sys.exit(1)
    
    services = start_services()
    
    print_header("🎉 SETUP COMPLETE! 🎉")
    
    print(f"{Color.GREEN}")
    print("Services running:")
    print("  • Redis:          redis://localhost:6379")
    print("  • API Server:     http://localhost:8000")
    print("  • API Docs:       http://localhost:8000/docs")
    print("  • Flower Monitor: http://localhost:5555")
    print(f"{Color.END}")
    
    print(f"{Color.YELLOW}")
    print("Quick Start:")
    print("  1. Open http://localhost:8000/docs")
    print("  2. Register: POST /api/auth/register")
    print("  3. Login: POST /api/auth/login")
    print("  4. Copy token and click 'Authorize'")
    print("  5. Start chatting: POST /api/chat/send")
    print(f"{Color.END}")
    
    # Start API server (blocking)
    start_api_server()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\\n\\nSetup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print_error(f"Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)