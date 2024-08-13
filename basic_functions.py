import os
import sys
import random
import subprocess
import string
import re
def send_ad():
    with open("./config.ini", "r") as f:
        content = f.read()
        config = dict(line.split("=") for line in content.split("\n") if "=" in line)
        message = config.get("ad_message")
        excluded_users = eval(config.get("admin_users"))
        for user in get_active_rdp_users_return_only():
            if user not in excluded_users:
                subprocess.run(f'msg {user} {message}', shell=True)
def bytesToHex(bytes):
    sb = ''
    for i in range(len(bytes)):
        hexs = hex(bytes[i] & 0xFF)[2:]
        if len(hexs) < 2:
            sb += '0'
        sb += hexs
    return sb

def hexToByte(inHex):
    hexlen = len(inHex)
    result = []
    if (hexlen % 2 == 1):
        hexlen += 1
        inHex="0"+inHex
    for i in range(0, hexlen, 2):
        result.append(int(inHex[i:i+2],16))
    return result

def initKey(aKey):
    state = list(range(256))
    bkey =[ord(i) for i in list(aKey)]
    index1 = 0
    index2 = 0
    if (len(bkey) == 0):
        return []
    for i in range(256):
        index2 = ((bkey[index1] & 0xff) + (state[i] & 0xff) + index2) & 0xff
        state[i], state[index2] = state[index2], state[i]
        index1 = (index1 + 1) % len(bkey)
    return state

def RC4Base(input, mKkey):
    x = 0
    y = 0
    key = initKey(mKkey)
    result = list(range(len(input)))
    for i in range(len(input)):
        x = (x + 1) & 0xff
        y = ((key[x] & 0xff) + y) & 0xff
        key[x], key[y] = key[y], key[x]
        xorIndex = ((key[x] & 0xff) + (key[y] & 0xff)) & 0xff
        result[i] = (input[i] ^ key[xorIndex])
    return result

def encryRC4Byte(data, key, chartSet='utf-8'):
    if not chartSet:
        bData = [ord(i) for i in data]
        return RC4Base(bData, key)
    else:
        bData = list(data.encode(chartSet))
        return RC4Base(bData, key)

def decryRC4(data, key, chartSet='utf-8'):
    r = RC4Base(hexToByte(data), key)
    return bytes(r).decode(chartSet)

def encryRC4String(data, key, chartSet='utf-8'):
    return bytesToHex(encryRC4Byte(data, key, chartSet))

def RC4(data, key, signs):
    if signs == 'encode':
        datas = encryRC4String(data, key)
    else:
        datas = decryRC4(data, key)
    return datas
def create_tunnel_advanced():
    config_name=input("FRP配置文件的文件名:")
    server_addr=input("FRP服务器的IP(不带端口):")
    server_port=input("FRP服务器的端口(不是远程端口,frps端口):")
    temp=input("你的FRP服务器有没有user认证(配置文件要user字段)(y有n没有):")
    if temp=="y":
        server_user=input("user字段内容:")
        config_mode=1
    else:
        config_mode=0
    server_token=input("连接FRP服务器时的Token:")
    tunnel_name = input("请输入隧道名: ")
    local_port = input("请输入本地端口 (开户页面是53628,远程桌面是3389): ")
    remote_port = input("请输入远程端口: ")
    if config_mode==1:
        config_template = f"""
[common]
server_addr = {server_addr}
server_port = {server_port}
user = {server_user}
token= {server_token}

[{tunnel_name}]
type = tcp
local_ip = 127.0.0.1
local_port = {local_port}
remote_port = {remote_port}
    """
    else:
        config_template = f"""
[common]
server_addr = {server_addr}
server_port = {server_port}
token= {server_token}

[{tunnel_name}]
type = tcp
local_ip = 127.0.0.1
local_port = {local_port}
remote_port = {remote_port}
    """
    config_path = os.path.join('frp', f"{config_name}.ini")
    with open(config_path, 'w') as config_file:
        config_file.write(config_template.strip())
    print(f"隧道配置文件已创建: {config_path}")
    input("按回车键以回到面板，记得运行隧道:")
def create_tunnel_auto():
    input("自动化模式将使用IIS7提取的配置文件穿透远程桌面，使用freefrp.net的FRP服务器穿透开户网页，按回车确定")
    remote_port_1=random.randint(10000,65535)
    config_template = f"""
[common]
server_addr = 3389.iis7.net
server_port = 65502

[IIS7_{remote_port_1}]
type = tcp
local_ip = 127.0.0.1
local_port = 3389
remote_port = {remote_port_1}
    """
    config_path = os.path.join('frp', "IIS7-RDP.ini")
    with open(config_path, 'w') as config_file:
        config_file.write(config_template.strip())
    print(f"隧道配置文件已创建: {config_path}")

    tunnel_name=''.join(random.choice(string.ascii_letters + string.digits) for _ in range(20))
    remote_port_2=random.randint(10000,65535)
    config_template = f"""
[common]
server_addr = frp.freefrp.net
server_port = 7000
token = freefrp.net

[{tunnel_name}]
type = tcp
local_ip = 127.0.0.1
local_port = 53628
remote_port = {remote_port_2}

    """
    config_path = os.path.join('frp', "freefrp-net-kh-web.ini")
    with open(config_path, 'w') as config_file:
        config_file.write(config_template.strip())
    print(f"隧道配置文件已创建: {config_path}")
    print(f"远程IP是3389.iis7.net:{remote_port_1}\n网页开户地址是http://frp.freefrp.net:{remote_port_2}/")
    input("按回车键以回到面板，记得运行隧道:")
def create_tunnel_easy():
    input("提示:开户页面本地端口是53628,远程桌面本地端口是3389，请核对，按回车继续")
    config_name=input("FRP配置文件的文件名(扩展名会自动添加):")
    config_template = ""
    print('请在此处粘贴frp配置文件的内容，粘贴后先按Enter后Ctrl+Z结束输入:')
    config_template = sys.stdin.read()
    config_path = os.path.join('frp', f"{config_name}.ini")
    with open(config_path, 'w') as config_file:
        config_file.write(config_template.strip())
    print(f"隧道配置文件已创建: {config_path}")
    input("按回车键以回到面板，记得运行隧道:")
def list_ini_files(directory):
    ini_files = [file for file in os.listdir(directory) if file.endswith('.ini')]
    result = '\n'.join(ini_files)
    return result
def get_active_rdp_users():
    usernames = []
    try:
        # Execute the qwinsta command and capture the output
        output = subprocess.check_output('qwinsta', stderr=subprocess.STDOUT, text=True, shell=True)
        
        # Parse the output to extract usernames
        for line in output.splitlines():
            # Match lines that include session information
            match = re.match(r'^\s*\S+\s+(\S+)\s+\d+\s+\S+', line)
            if match:
                # Extract the username, ensuring to strip any whitespace
                username = match.group(1).strip()
                # Exclude empty usernames and special session names
                if username and username not in ['services', 'console', 'rdp-tcp']:
                    usernames.append(username)
    except subprocess.CalledProcessError as e:
        print(f"出现错误:{e}")
    result = "\n".join(usernames)
    print(result)
    input("任务完成，按回车回到管理面板")
    return
def get_active_rdp_users_return_only():
    usernames = []
    try:
        # Execute the qwinsta command and capture the output
        output = subprocess.check_output('qwinsta', stderr=subprocess.STDOUT, text=True, shell=True)
        
        # Parse the output to extract usernames
        for line in output.splitlines():
            # Match lines that include session information
            match = re.match(r'^\s*\S+\s+(\S+)\s+\d+\s+\S+', line)
            if match:
                # Extract the username, ensuring to strip any whitespace
                username = match.group(1).strip()
                # Exclude empty usernames and special session names
                if username and username not in ['services', 'console', 'rdp-tcp']:
                    usernames.append(username)
    except subprocess.CalledProcessError as e:
        return(f"出现错误:{e}")
    return usernames
def run_tunnel():
    ini_files = list_ini_files('frp')
    if not ini_files:
        print("没有找到FRP配置文件,请先创建隧道!")
        input("任务已完成,按回车键以回到面板:")
        return
    print("找到以下配置文件:")
    print(ini_files)
    ini_files = ini_files.split("\n")
    choice = input("请选择你要启动的隧道序号(从1开始): ")
    try:
        selected_file = ini_files[int(choice) - 1]
    except (IndexError, ValueError):
        print("无效的序号")
        return
    
    config_path = os.path.join('frp', selected_file)
    cmd = f"start start-frp.bat {config_path}"
    try:
        print(f"正在用此配置文件启动内网穿透: {selected_file}")
        subprocess.run(cmd,shell=True,check=True)
    except subprocess.CalledProcessError as e:
        print(f"FRP程序报错: {e}")
def print_file_contents(file_path, lines_per_page=10):
    os.system("cls")
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for i in range(0, len(lines), lines_per_page):
            print(''.join(lines[i:i+lines_per_page]))
            command = input("输入c退出查看界面，按回车查看下一行 ")
            os.system("cls")
            if command.lower() == 'c':
                break
    input("查看完成，按回车回到管理面板")
def delete_items(file_path, item):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        # 使用列表推导式和条件表达式来过滤掉空白行和指定内容
        lines_to_write = [line for line in lines if line.strip() and line.strip() != item]
        # 计算需要写入的行数，以便确定何时不添加换行符
        total_lines = len(lines_to_write)
        for i, line in enumerate(lines_to_write):
            # 对于最后一行，不添加换行符
            if i == total_lines - 1:
                file.write(line.strip())
            else:
                file.write(line)
def add_to_file(file_path, word):
    with open(file_path, 'a') as file:
        file.write(f"\n{word}")
    delete_items(file_path,"")