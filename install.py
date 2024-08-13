import os
from admin import *
from basic_functions import *
import secrets
def generate_key(length):
    key = secrets.token_hex(length)
    return key
def install():
    print("===========BS一键开云工具===========")
    temp=input("请确认系统为专业版及以上且是纯净中文系统!(确认按y，退出按n):")
    if temp=="y":
        pass
    else:
        exit()
    print("远程桌面启用中")
    # 启用RDP远程桌面
    os.system('reg add "HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Control\\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f')
    print("远程端口更改中")
    # 设置端口为3389
    os.system('reg add "HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Control\\Terminal Server\\WinStations\\RDP-Tcp" /v PortNumber /t REG_DWORD /d 3389 /f')
    print("多用户破解中")
    # 执行./rdpwrap/install.bat脚本
    os.system('rdpwrap\\run_init\\run_init.exe')
    os.system('rdpwrap\\install.bat')
    # 配置Nginx
    print("Nginx配置中")
    os.system('nginx\\nginx_init.exe')
    print("恭喜!远程桌面基本环境配置完成！即将进入开户信息配置页面！")
    BASE_URL=input("请输入FRP穿透开户后的外网地址(用于QQ登录回调，开户页面的地址，请严格按照格式填写，格式http://baidu.com/)")
    AUTHORIZE_URL=input("请输入聚合登录平台的地址(格式https://uniqueker.top/)")+"connect.php"
    APPID=input("请输入聚合登录平台的应用APPID")
    APPKEY=input("请输入聚合登录平台的应用APPKEY")
    ad_message=input("请输入你们云电脑的一条广告(不支持多行)(用于在云电脑内群发广告):")
    admin_count=int(input("请输入云电脑中要永不接受广告的用户的数量:"))
    admin_users_list=[]
    for i in range(1,(admin_count+1),1):
        print("请输入第%d位永不接受广告的用户的用户名:"%i,end="")
        admin_users_list.append(input(""))
    admin_users_list=str(admin_users_list)
    job_to_flask_key=generate_key(16)
    # 写入config.ini文件
    with open("config.ini", "a") as f:
        f.write("is_install=True\n")
        f.write("ad_message=%s\n"%ad_message)
        f.write("admin_users=%s\n"%admin_users_list)
        f.write("job_to_flask_key=%s\n"%job_to_flask_key)
        f.write("BASE_URL=%s\n"%BASE_URL)
        f.write("APPID=%s\n"%APPID)
        f.write("APPKEY=%s\n"%APPKEY)
        f.write("AUTHORIZE_URL=%s\n"%AUTHORIZE_URL)
    admin()