import requests
import os
from panel import *
import subprocess
def admin():
    print("===========RainPaper一键开云工具===========")
    print("开户后端API正在启动...")
    input("注意:接下来弹出的黑窗口点最小化不要关闭！按回车继续")
    os.system("start start-api.bat")
    os.system("start start-job.bat")
    print("正在清除多余的nginx进程...")
    tmp=subprocess.Popen("taskkill /f /im nginx.exe",shell=True)
    tmp.wait()
    print("nginx正在启动")
    os.system("start start-nginx.bat")
    input("提示:进入管理面板后记得启动FRP，按回车键继续")
    os.system("cls")
    panel()