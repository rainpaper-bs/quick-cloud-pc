from basic_functions import *
import logging
import time
import requests
print("此窗口为计划任务执行程序，请挂后台")
time.sleep(10)
with open("./config.ini", "r") as f:
    content = f.read()
config = dict(line.split("=") for line in content.split("\n") if "=" in line)
auth_key = config.get("job_to_flask_key")
def job():
    while True:
        # 此处进行Logging.basicConfig() 设置，后面设置无效
        logging.basicConfig(filename='job-log.txt',
                        format = '[%(asctime)s] - %(levelname)s - %(message)s',
                        filemode='w',level=logging.DEBUG)
        logging.info("本次计划任务开始运行")
        logging.info("正在执行Windows消息系统广告群发")
        send_ad()
        logging.info("广告群发结束")
        logging.info("正在清理过期的验证码")
        try:
            key=str(int(time.time())%10)
            response = requests.get('http://127.0.0.1:12300/cleanup_expired_codes?auth='+RC4(auth_key,key,'encode'))
            if response.text=="OK":
                logging.info("过期验证码清理成功")
            else:
                logging.error("计划任务端与flask端密钥不匹配，请重启云电脑搭建软件！")
        except Exception as e:
            logging.error("请求后端发生异常(如果当时正在登录雨云请忽略):"+e)
        logging.info("本次计划任务结束运行")
        time.sleep(300)
job()