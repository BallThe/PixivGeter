# coding=utf-8
import threading
from tkinter import *
from tkinter.filedialog import *
from tkinter.messagebox import *
import requests
import time

# 初始化
root = Tk()
# 大小
root.geometry("400x300")
# 窗口标题
root.title("Pixiv图片下载")

# 不可放大缩小
root.resizable(width=False, height=False)


# 下载函数
def downloadPics(id, number, path, name):
    # 请求头部
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}
    # 网址
    url = "https://pixiv.re/"

    # 设置命名
    name = name.replace("[序号]", "{}")

    # 下载失败
    not_passed = []

    # 获取编号
    for pic_num in range(1, number + 1):
        get_url = "{}{}-{}.jpg".format(url, id, pic_num)

        # 获取
        pic = requests.get(get_url, headers=headers)

        # 获取失败则下次重新尝试，否则保存
        if "503 Service Unavailable" in str(pic.content):
            not_passed.append(pic_num)
        else:
            print(get_url)
            with open("{}\\{}.jpg".format(path, name.format(pic_num)), "wb") as fp:
                fp.write(pic.content)
                fp.close()

        root.update()
        time.sleep(1)

    for i in range(2):
        for k in range(0, len(not_passed)):
            k = len(not_passed) - k - 1
            print(not_passed, not_passed[k])
            get_url = "{}{}-{}.jpg".format(url, id, not_passed[k])
            print(get_url)
            pic = requests.get(get_url, headers=headers)

            if "503 Service Unavailable" not in str(pic.content):
                with open("{}\\{}.jpg".format(path, name.format(not_passed[k])), "wb") as fp:
                    fp.write(pic.content)
                    fp.close()

            root.update()
            time.sleep(1)

    if len(not_passed) == 0:
        return True
    else:
        not_passed = [str(i) for i in not_passed]
        return "、".join(not_passed)


# 组件
# 大标题
Label(root, text="Pixiv图片下载", font=("宋体", 25)).place(x=10, y=10, height=30)

# 颜色框架
Frame(root, width=380, height=240, bg="white").place(x=10, y=50)

# 框架内输入的标题
Label(root, text="填入作品信息", font=("宋体", 17), bg="white").place(x=20, y=60)

# 输入标题
Label(root, text="作品id", font=("宋体", 13), bg="white").place(x=20, y=100, width=100, anchor="nw")
Label(root, text="画作数量", font=("宋体", 13), bg="white").place(x=28, y=130, width=100, anchor="nw")
Label(root, text="存放路径", font=("宋体", 13), bg="white").place(x=28, y=160, width=100, anchor="nw")
Label(root, text="储存文件名", font=("宋体", 13), bg="white").place(x=36, y=190, width=100, anchor="nw")


# 分流下载数据
def new_func(download_info):
    print(download_info)
    for download in download_info:
        if download != "":
            state = downloadPics(int(download[0]), int(download[1]), download[2], download[3])
            global download_finish
            global all_paint
            download_finish += 1
            if state == True:
                downloadMessagevar.set(
                    "*下载的文件会覆盖文件夹内同名文件 下载信息会展示在下面\nid: {} 下载完成！({}/{})".format(download[0], download_finish, all_paint))
            else:
                downloadMessagevar.set(
                    "*下载的文件会覆盖文件夹内同名文件 下载信息会展示在下面\nid: {} 第{}页下载失败！原因：限速 ({}/{})".format(download[0], state,
                                                                                         download_finish, all_paint))
            if download_finish == all_paint:
                showinfo(text="下载图片完成！", title="pixiv图片下载 - 完成")


# 多线程处理
def multiDownload(download_list):
    # 初始化变量
    thread_list = [[], [], []]
    number_list = [int(i[1]) for i in download_list]
    number_list.sort()
    global all_paint
    all_paint = len(number_list)
    global download_finish
    # 多线程下载数量
    download_finish = 0

    # 数据分流
    for num in range(len(number_list)):
        # 最大线程数：3， 以数字分类，从大到小放置数字所在索引的下载信息
        # 顺序：当num//3%2 == 0便从左往右放置，== 1时从右往左放置
        if num // 3 % 2 == 0:
            thread_list[num % 3].append(download_list[num])
        elif num // 3 % 2 == 1:
            thread_list[3 - 1 - num % 3].append(download_list[num])

    # 添加线程
    for download_info in thread_list:
        new_thread = threading.Thread(target=new_func, args=([download_info]))
        new_thread.start()
        time.sleep(0.5)


# 获取变量中的数据
def get_data():
    # 获取数据
    paintId = paintIdvar.get()
    paintNumber = paintNumbervar.get()
    dirPath = dirPathvar.get()
    name = namevar.get()

    # 错误信息
    error = ""
    error_list = ["作品id", "画作数量", "存放路径", "储存文件名"]
    data_list = [paintId, paintNumber, dirPath, name]

    # 筛选错误
    for i in range(len(data_list)):
        if len(str(data_list[i]).strip()) == 0:
            error += error_list[i] + "不能为空\n\n"

    # 显示错误
    if error != "":
        showerror(title="Pixiv图片下载 - 错误", message=error)

    # 运行下载
    elif error == "":
        downloadPics(paintId, paintNumber, dirPath, name)


# 选择路径
def dir_select():
    dirPath = askdirectory(title="Pixiv图片下载 - 选择要储存作品的文件夹")
    dirPathvar.set(dirPath)
    root.update()


# 运行脚本
def run_script():
    # 选择脚本文件
    scriptPath = askopenfilename(title="Pixiv图片下载 - 选择脚本", filetypes=[("pG脚本文件", ".pgs")])
    if scriptPath == "" or None:
        return

    # 读取脚本文件
    with open(scriptPath, "r", encoding="utf-8") as f:
        script = f.read()
        f.close()

    # 弹窗
    showinfo(title="Pixiv图片下载 - 脚本导入成功", message="脚本导入成功！\n路径{}\n即将运行脚本".format(scriptPath))

    # 脚本处理
    script = [i.split("|") for i in script.split("\n")]

    # 校验脚本
    error_message = "脚本错误：\n"
    for i in script:
        if len(i) != 4:
            error_message += "  长度错误\n"
        try:
            int(i[0])
            int(i[1])
        except ValueError:
            error_message += "  类型错误\n"
    if error_message != "脚本错误：\n":
        showerror(title="Pixiv图片下载 - 脚本错误", message=error_message + "请检查脚本，本次脚本不会运行")
        return

    # 运行脚本
    multiDownload(script)

    showinfo(title="Pixiv图片下载 - 脚本运行", message="脚本运行中！\n不要关闭主窗口")
    downloadMessagevar.set("*下载的文件会覆盖文件夹内同名文件 下载信息会展示在下面\n下载中！")
    root.update()


# 变量
paintIdvar = IntVar()
paintNumbervar = IntVar()
dirPathvar = StringVar()
namevar = StringVar()
downloadMessagevar = StringVar()
namevar.set("[序号]")
paintIdvar.set(0)
paintNumbervar.set(1)
downloadMessagevar.set("*下载的文件会覆盖文件夹内同名文件 下载信息会展示在下面")

# id输入框、数量输入框、路径展示、选择框
Entry(root, bg="white", textvariable=paintIdvar, font=("宋体", 12)).place(x=130, y=100, width=230, height=25)
Entry(root, bg="white", textvariable=paintNumbervar, font=("宋体", 12)).place(x=130, y=130, width=230, height=25)
Label(root, bg="white", textvariable=dirPathvar, font=("宋体", 12)).place(x=130, y=160, width=180, height=25)
Button(root, bg="white", text="浏览", font=("宋体", 12), command=dir_select).place(x=310, y=160, width=50, height=25)
Entry(root, bg="white", text="", textvariable=namevar, font=("宋体", 12)).place(x=130, y=190, width=230, height=25)

# 确认按钮
Button(root, bg="white", text="确认", font=("宋体", 12), command=get_data).place(x=140, y=240, width=50, height=30,
                                                                             anchor="center")
# 脚本按钮
Button(root, bg="white", text="运行脚本", font=("宋体", 12), command=run_script).place(x=250, y=240, width=100, height=30,
                                                                                 anchor="center")
# 信息
Label(root, bg="white", textvariable=downloadMessagevar, font=("宋体", 10)).place(x=200, y=269, height=30,
                                                                                anchor="center")
# 循环
root.mainloop()
