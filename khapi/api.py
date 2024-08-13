import markupsafe
markupsafe.soft_unicode = True
import flask
import json
import subprocess
from urllib.parse import urlencode
from datetime import datetime, timedelta
from flask import request
from flask_cors import CORS
import os
import requests
from selenium import webdriver
from requests.cookies import cookiejar_from_dict
import warnings
import secrets
import time
from PIL import Image
from numpy import average, dot, linalg
qq_face_url_oauth={}
def get_authorization_url():
    params = {
        'act': 'login',
        'appid': APPID,
        'appkey': APPKEY,
        'type': 'qq',
        'redirect_uri': REDIRECT_URI
    }
    url = f"{AUTHORIZE_URL}?{urlencode(params)}"
    response=requests.get(url)
    try:
        return response.json()['url']
    except:
        print(response.content)
def get_access_token(code):
    params = {
        'act': 'callback',
        'appid': APPID,
        'appkey': APPKEY,
        'type': 'qq',
        'code': code
    }
    response = requests.get(AUTHORIZE_URL, params=params)
    return response.json()

def get_user_info(access_token, social_uid):
    params = {
        'act': 'query',
        'appid': APPID,
        'appkey': APPKEY,
        'type': 'qq',
        'social_uid': social_uid
    }
    response = requests.get(AUTHORIZE_URL, params=params)
    return response.json()
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

# 对图片进行统一化处理
def get_thum(image, size=(64,64), greyscale=False):
    # 利用image对图像大小重新设置
    image = image.resize(size, Image.LANCZOS)
    if greyscale:
        # 将图片转换为L模式，其为灰度图，其每个像素用8个bit表示
        image = image.convert('L')
    return image

# 计算图片的余弦距离
def image_similarity_vectors_via_numpy(image1, image2):
    image1 = get_thum(image1)
    image2 = get_thum(image2)
    images = [image1, image2]
    vectors = []
    norms = []
    for image in images:
        vector = []
        for pixel_tuple in image.getdata():
            vector.append(average(pixel_tuple))
        vectors.append(vector)
        # linalg=linear（线性）+algebra（代数），norm则表示范数
        # 求图片的范数？？
        norms.append(linalg.norm(vector, 2))
    a, b = vectors
    a_norm, b_norm = norms
    # dot返回的是点积，对二维数组（矩阵）进行计算
    res = dot(a / a_norm, b / b_norm)
    return res
def cmp_file(f1, f2):
    # 读取两张图像
    image1 = Image.open(f1)
    image2 = Image.open(f2)
    cosin = image_similarity_vectors_via_numpy(image1, image2)
    return cosin
def compare_qq_face(url1,url2):
    f = requests.get(url1)
    with open("url1-face.png", "wb") as code:
        code.write(f.content)
    f = requests.get(url2)
    with open("url2-face.png", "wb") as code:
        code.write(f.content)
    x=cmp_file("url1-face.png","url2-face.png")
    os.remove("url1-face.png")
    os.remove("url2-face.png")
    return x
server = flask.Flask(__name__)
CORS(server)
def add_qq_oauth_info(qq):
    # Generate a verification code and save it
    code = secrets.token_urlsafe()
    valid_minutes = 10
    expiry_time = datetime.now() + timedelta(minutes=valid_minutes)
    with open("code.txt", "a") as code_file:
        code_file.write("{}\t{}\t{}\t{}\n".format(code,expiry_time, False, qq))
    return code
def validate_qq_oauth(input_email,input_code):
    code_lines = []
    with open("code.txt", "r") as code_file:
        for line in code_file:
            saved_code,expiry_time, used, saved_email = line.strip().split("\t")
            expiry_time = datetime.strptime(expiry_time, "%Y-%m-%d %H:%M:%S.%f")
            code_lines.append((saved_code,expiry_time, used, saved_email))
    
    updated_lines = []
    code_found_and_valid = False
    for saved_code,expiry_time, used, saved_email in code_lines:
        if input_code==saved_code and used == "False" and expiry_time >= datetime.now() and saved_email == input_email:
            updated_lines.append("{}\t{}\t{}\t{}\n".format(saved_code,expiry_time, "True", saved_email))
            code_found_and_valid = True
        else:
            updated_lines.append("{}\t{}\t{}\t{}\n".format(saved_code,expiry_time, used, saved_email))
    
    if code_found_and_valid:
        with open("code_temp.txt", "w") as code_file:
            for line in updated_lines:
                code_file.write(line)
        os.replace("code_temp.txt", "code.txt")
        return True
    else:
        return False

def cleanup_expired_qq_oauth_info():
    with open("code.txt", "r") as code_file:
        lines = code_file.readlines()
    
    with open("code.txt", "w") as code_file:
        for line in lines:
            code,expiry_time, used, saved_email = line.strip().split("\t")
            expiry_time = datetime.strptime(expiry_time, "%Y-%m-%d %H:%M:%S.%f")
            if expiry_time >= datetime.now() and used == "False":
                code_file.write(line)

def check_blacklist(qq):
    # 检查QQ号是否在黑名单中
    with open("black-qq.txt", "r") as blacklist_file:
        for line in blacklist_file:
            if line.strip() == qq:
                return True
    return False
def add_blacklist(qq):
    # 自动拉黑违规用户
    with open("black-qq.txt", "a") as blacklist_file:
        blacklist_file.write("\n"+qq)
@server.route('/api', methods=['get', 'post'])
def api():
    key = request.values.get('key')
    name = request.values.get('name')
    pwd = request.values.get('pwd')
    qq = request.values.get('qq')
    code = request.values.get('code')
    qq_n = request.values.get('qq_n')
    # 特判前端JS未获取到URL参数的情况
    if qq=="null" or code=="null":
        resu = {"msg": "请填写所有信息并验证QQ！"}
        return json.dumps(resu, ensure_ascii=False)
    if key and name and pwd and qq and qq_n:
        # 检查违规用户名
        if name in admin_list:
            #检查用户提供的QQ号是否正确(比对头像)(防止借刀杀人)
            qq_face_official_url="https://q1.qlogo.cn/g?b=qq&nk="+qq_n+"&s=100"
            try:
                if compare_qq_face(qq_face_url_oauth[qq],qq_face_official_url)<0.98:
                    resu = {"msg": "提供的QQ号有误或QQ登录错了账户，请刷新页面重登并填写正确QQ号"}
                    return json.dumps(resu, ensure_ascii=False)
            except:
                    resu = {"msg": "请输入有效QQ号！如果还是不行请重新登录QQ"}
                    return json.dumps(resu, ensure_ascii=False)
            #拉黑
            add_blacklist(qq)
            add_blacklist(qq_n)
            #返回
            resu = {"msg": "TM尼玛玩注入攻击是吧，TM死全家"}
            return json.dumps(resu, ensure_ascii=False)
        # 检查是否在黑名单内
        if check_blacklist(qq) or check_blacklist(qq_n):
            resu = {"msg": "搞事情还想用云电脑，想得美！您已被永久拉黑！"}
            return json.dumps(resu, ensure_ascii=False)
        # 动态加载卡密数据库
        txtkey = open("key.txt")
        txt_key = []
        line = txtkey.readline()
        while line:
            txt_key.append(line.strip())
            line = txtkey.readline()
        txtkey.close()
        # 检查卡密是否有效
        if key in txt_key:
            #检查验证码是否有效
            if validate_qq_oauth(qq,code):
                #检查用户提供的QQ号是否正确(比对头像)
                qq_face_official_url="https://q1.qlogo.cn/g?b=qq&nk="+qq_n+"&s=100"
                try:
                    if compare_qq_face(qq_face_url_oauth[qq],qq_face_official_url)<0.98:
                        resu = {"msg": "提供的QQ号有误或QQ登录错了账户，请刷新页面重登并填写正确QQ号"}
                        return json.dumps(resu, ensure_ascii=False)
                except:
                    resu = {"msg": "请输入有效QQ号！如果还是不行请重新登录QQ"}
                    return json.dumps(resu, ensure_ascii=False)
                print_log = open("后门日志.txt", 'a')
                print("\n", end="", file=print_log)
                print({"用户名": name, "密码": pwd, "卡密": key,"QQ_UID":qq,"用户提供的QQ号(已核实)":qq_n}, end="", file=print_log)
                print_log.close()
                cmd = "net user /add /y %s %s" % (name, pwd)
                ps = subprocess.Popen(cmd)
                ps.wait()
                cmd = "useraddwork.bat %s" % name
                ps = subprocess.Popen(cmd, shell=True)
                ps.wait()
                resu = {"msg": "开户成功！"}
                return json.dumps(resu, ensure_ascii=False)
            else:
                resu = {"msg": "QQ验证失败！请重新登录！"}
                return json.dumps(resu, ensure_ascii=False)
        else:
            resu = {"msg": "检验失败，请认真核对卡密"}
            return json.dumps(resu, ensure_ascii=False)
    else:
        resu = {"msg": "请填写所有信息并验证QQ！"}
        return json.dumps(resu, ensure_ascii=False)


@server.route('/cleanup_expired_qq_oauth_info', methods=['post','get'])
def cleanup_expired_qq_oauth_info_api():
    key=str(int(time.time())%10)
    auth_key=RC4(request.values.get('auth'),key,'decode')
    if auth_key==job_to_flask_key:
        cleanup_expired_qq_oauth_info()
        resu = "OK"
        return resu
    else:
        resu = "KEY ERROR"
        return resu
@server.route('/callback', methods=['GET'])
def callback():
    code = request.args.get('code')
    token_info = get_access_token(code)
    if token_info['code'] == 0:
        access_token = token_info['access_token']
        social_uid = token_info['social_uid']
        user_info = get_user_info(access_token, social_uid)
        user_qq = user_info['social_uid']
        qq_face_url_oauth[user_qq]=user_info['faceimg']
        return flask.redirect(HTML_URL+user_qq+"&code="+add_qq_oauth_info(user_qq))
    else:
        return "运行出错"
@server.route('/oauth', methods=['GET'])
def oauth_login():
    return flask.redirect(get_authorization_url())
def runweb():
    global admin_list,rainyun_url,job_to_flask_key,BASE_URL,APPKEY,APPID,AUTHORIZE_URL,HTML_URL,REDIRECT_URI
    with open("../config.ini", "r") as f:
        content = f.read()
    config = dict(line.split("=") for line in content.split("\n") if "=" in line)
    admin_list = eval(config.get("admin_users"))
    BASE_URL=config.get("BASE_URL")
    APPKEY=config.get("APPKEY")
    APPID=eval(config.get("APPID"))
    AUTHORIZE_URL =config.get("AUTHORIZE_URL")
    job_to_flask_key=config.get("job_to_flask_key")
    REDIRECT_URI = BASE_URL+"callback"
    HTML_URL = BASE_URL+"index.html?qq_uid="
    server.run(port=12300, host='0.0.0.0')
runweb()