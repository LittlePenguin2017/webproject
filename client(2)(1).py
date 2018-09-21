#coding:utf-8
'''
file:client.py.py
date:2017/9/11 11:01
author:lockey
email:lockey@123.com
platform:win7.x86_64 pycharm python3
desc:p2p communication clientside
'''
from socket import *
import threading,sys,json,re
import webbrowser
import requests

HOST = 'localhost'  ##
PORT=8136
BUFSIZE = 1024  ##缓冲区大小  1K
ADDR = (HOST,PORT)
myre = r"^[_a-zA-Z]\w{0,}"
tcpCliSock = socket(AF_INET,SOCK_STREAM)
userAccount = None
def socket_server():
    HOST = ''  # 本地localhost
    PORT = 50010
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(1)

    conn, addr = s.accept()  # 接受连接
    print('Connected by', addr)
    while True:
        data = conn.recv(1024).decode('utf-8')  # 1024个字节
        # 单连接，没有数据断开，服务器断开
        if not data:
            break
        print('Received', data)
        msg = input(">>:").strip()
        if len(msg) == 0:
            continue
        # s.sendall('Hello Huangpingyi')
        conn.sendall(msg.encode('utf-8'))
    conn.close()


def socket_client():
    HOST = 'localhost'
    PORT = 50010

    s = socket(AF_INET, SOCK_STREAM)
    s.connect((HOST, PORT))

    while True:
        msg = input(">>:").strip()
        if len(msg) == 0:
            continue
        elif msg == "exit":
            break
            # s.sendall('Hello Huangpingyi')
        s.sendall(msg.encode('utf-8'))
        data = s.recv(1024)
        print(data)
    s.close()


def register():
    print("""
    Glad to have you a member of us!
    """)
    accout = input('Please input your account: ')
    if not re.findall(myre, accout):
        print('Account illegal!')
        return None
    password1  = input('Please input your password: ')
    password2 = input('Please confirm your password: ')
    tag = input('Please input your role(user or manager): ')
    if not (password1 and password1 == password2):
        print('Password not illegal!')
        return None
    global userAccount
    userAccount = accout
    regInfo = [accout,password1,'register',tag]
    datastr = json.dumps(regInfo)
    tcpCliSock.send(datastr.encode('utf-8'))
    data = tcpCliSock.recv(BUFSIZE)
    data = data.decode('utf-8')
    if data == '0':
        print('Success to register!')
        return True
    elif data == '1':
        print('Failed to register, account existed!')
        return False
    else:
        print('Failed for exceptions!')
        return False

def login():
    print("""
    Welcome to login in!
    """)
    accout = input('Account: ')
    if not re.findall(myre, accout):
        print('Account illegal!')
        return None
    password = input('Password: ')
    if not password:
        print('Password illegal!')
        return None
    tag = input('Role: ')
    global userAccount
    userAccount = accout
    loginInfo = [accout, password,'login',tag]
    datastr = json.dumps(loginInfo)
    tcpCliSock.send(datastr.encode('utf-8'))
    data = tcpCliSock.recv(BUFSIZE)
    data = data.decode('utf-8')
    if data == '0':
        print('Success to login!')
        return True
    else:
        print('Failed to login in(user not exist or username not match the password)!')
        return False
def addGroup():
    groupname = input('Please input group name: ')
    if not re.findall(myre, groupname):
        print('group name illegal!')
        return None
    return groupname

def chat(target):
    while True:
        print('{} -> {}: '.format(userAccount,target))
        msg = input()
        if len(msg) > 0 and not msg in 'qQ':
            if 'group' in target:
                optype = 'cg'
            else:
                optype = 'cp'

            dataObj = {'type': optype, 'to': target, 'msg': msg, 'froms': userAccount}
            datastr = json.dumps(dataObj)
            tcpCliSock.send(datastr.encode('utf-8'))
            continue
        elif msg in 'qQ':
            break
        else:
            print('Send data illegal!')

def p2pchat(target):
    while True:
        msg = target
        if len(msg) > 0 and not msg in 'qQ':
            if 'group' in target:
                optype = 'cg'
            else:
                optype = 'cp'

            dataObj = {'type': optype, 'to': target, 'msg': msg, 'froms': userAccount}
            datastr = json.dumps(dataObj)
            tcpCliSock.send(datastr.encode('utf-8'))
            continue
        elif msg in 'qQ':
            break
        else:
            print('Send data illegal!')
class inputdata(threading.Thread):
    def run(self):
        menu = """
                        (CP): Chat with individual
                        (CG): Chat with group member
                        (AG): Add a group
                        (EG): Enter a group
                        (WE): visit the website
                        (RE): get the readme.txt by http
                        (H):  For help menu
                        (Q):  Quit the system
                        """
        print(menu)
        while True:
            operation = input('Please input your operation("h" for help): ')
            if operation in 'cPCPCpcp':
                target = input('Who would you like to chat with: ')
                chat(target)
                print('client')
                socket_client()
                continue

            if  operation in 'cgCGCgcG':
                target = input('Which group would you like to chat with: ')
                chat('group'+target)
                continue
            if operation in 'agAGAgaG':
                groupName = addGroup()
                if groupName:
                    dataObj = {'type': 'ag', 'groupName': groupName,'name':userAccount}
                    dataObj = json.dumps(dataObj)
                    tcpCliSock.send(dataObj.encode('utf-8'))
                continue

            if operation in 'egEGEgeG':
                groupname = input('Please input group name fro entering: ')
                if not re.findall(myre, groupname):
                    print('group name illegal!')
                    return None
                dataObj = {'type': 'eg', 'groupName': 'group'+groupname}
                dataObj = json.dumps(dataObj)
                tcpCliSock.send(dataObj.encode('utf-8'))
                continue
            if operation in 'hH':
                print(menu)
                continue

            if operation in 'WEwe':
                target = input('Which website do you want to visit: ')
                url2 = target
                webbrowser.open(url2, new=0, autoraise=True)
                webbrowser.open_new(url2)
                webbrowser.open_new_tab(url2)
                continue

            if operation in 'REre':
                import requests
                url = "http://127.0.0.1:8000/readme.html"
                payload = {'message': "hello server"}
                r = requests.post(url, data=payload)
                if r.status_code == 200:
                    print("successful post")
                    print(r.status_code)
                    str = r.content
                    str2 = str.decode('utf-8')
                    print(str2)
                continue


            if operation in 'qQ':
                sys.exit(1)

class getdata(threading.Thread):
    def run(self):
        while True:
            data = tcpCliSock.recv(BUFSIZE).decode('utf-8')
            if data == '-1':
                print('can not connect to target!')
                continue
            if data == 'ag0':
                print('Group added!')
                continue

            if data == 'eg0':
                print('Entered group!')
                continue

            if data == 'eg1':
                print('Failed to enter group!')
                continue

            if data == 'server':
                socket_server()
                continue

            if len(data) > 6:
                dataObj = json.loads(data)
                if dataObj['type'] == 'cg':
                    print('{}(from {})-> : {}'.format(dataObj['froms'], dataObj['to'], dataObj['msg']))
            else:
                print(type(data))


def main():

        try:
            tcpCliSock.connect(ADDR)
            print('Connected with server')
            while True:
                loginorReg = input('(l)ogin or (r)egister a new account: ')
                if loginorReg in 'lL':
                    log = login()
                    if log:
                        break
                if loginorReg in 'rR':
                    reg = register()
                    if reg:
                        break

            myinputd = inputdata()
            mygetdata = getdata()
            myinputd.start()
            mygetdata.start()
            myinputd.join()
            mygetdata.join()

        except Exception:
            print('error')
            tcpCliSock.close()
            sys.exit()


if __name__ == '__main__':
    main()