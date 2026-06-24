"""
剧本杀开发服务器 - 支持热更新
当检测到 .py 文件修改时自动重启服务器

使用方法:
1. 安装依赖: pip install watchdog
2. 运行: python dev.py
3. 修改 server.py 后会自动重启

按 Ctrl+C 停止服务器
"""

import subprocess
import sys
import time
from pathlib import Path

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    print("❌ 缺少 watchdog 库，请先安装:")
    print("   pip install watchdog")
    sys.exit(1)


class ServerRestartHandler(FileSystemEventHandler):
    """监听文件变化并重启服务器"""
    
    def __init__(self):
        self.process = None
        self.last_restart = 0
        self.restart()
    
    def on_modified(self, event):
        """文件修改时触发"""
        # 只监听 Python 文件
        if not event.src_path.endswith('.py'):
            return
        
        # 忽略 dev.py 自身的修改
        if event.src_path.endswith('dev.py'):
            return
        
        # 防抖：1秒内只重启一次
        now = time.time()
        if now - self.last_restart < 1:
            return
        
        self.last_restart = now
        filename = Path(event.src_path).name
        print(f"\n🔄 检测到 {filename} 变化，重启服务器...")
        self.restart()
    
    def restart(self):
        """重启服务器进程"""
        # 停止旧进程
        if self.process:
            print("⏹️  停止旧服务器...")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                print("⚠️  强制终止服务器...")
                self.process.kill()
                self.process.wait()
        
        # 启动新进程
        print("▶️  启动服务器...")
        self.process = subprocess.Popen(
            [sys.executable, 'server.py'],
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        print("✅ 服务器已启动，监听文件变化中...")
        print("   按 Ctrl+C 停止服务器\n")


def main():
    print("=" * 60)
    print("🚀 剧本杀开发服务器 (支持热更新)")
    print("=" * 60)
    print("📁 监听目录: " + str(Path.cwd()))
    print("📝 监听文件: *.py")
    print("=" * 60 + "\n")
    
    handler = ServerRestartHandler()
    observer = Observer()
    observer.schedule(handler, '.', recursive=False)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n⏹️  正在停止服务器...")
        observer.stop()
        if handler.process:
            handler.process.terminate()
            try:
                handler.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                handler.process.kil
        print("✅ 服务器已停止")
    
    observer.join()


if __name__ == '__main__':
    main()
