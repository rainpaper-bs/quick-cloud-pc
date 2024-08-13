from basic_functions import *
from panel import *
from install import *
from admin import *
def main():
    if not os.path.exists("config.ini"):
        install()
        return
    # 读取config.ini文件内容
    with open("config.ini", "r") as f:
        content = f.read()
    config = dict(line.split("=") for line in content.split("\n") if "=" in line)
    is_install = config.get("is_install", "False")
    if is_install == "True":
        admin()
    else:
        install()
main()
