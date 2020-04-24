# Originated from https://blog.naver.com/chandong83/221194085638

#! /usr/bin/env python

# Client and server for tcp (stream) echo.
#
# Usage: tcpecho.py -s [port]            (to start a server)
# or:    tcpecho.py -c host [port] <file (client)
# e.g.
#   Server params: -s 9190
#   Client params: -c 127.0.0.1 9190

# Client and server for tcp echo.
import sys
from socket import *
import time
import cv2
import numpy as np
from struct import *

# ECHO_PORT 기본 포트
ECHO_PORT = 9190

# 버퍼 사이즈
BUFSIZE = 1024

# 서버 대기 큐
QUEUE_LIMIT = 5

isRunning = False

# 메인 함수
def main():
    print(sys.argv)
    # 매개변수가 2개보다 적다면
    if len(sys.argv) < 2:
        # 사용 방법 표시
        usage()

    # 첫 매개변수가 '-s' 라면
    if sys.argv[1] == '-s':
        # 서버 함수 호출
        server()

    # 첫 매개변수가 '-c' 라면
    elif sys.argv[1] == '-c':
        # 클라이언트 함수 호출
        client()

    # '-s' 또는 '-c' 가 아니라면
    else:
        # 사용 방법 표시
        usage()


# 사용하는 방법 화면에 표시하는 함수
def usage():
    sys.stdout = sys.stderr
    print('Usage: python tcpecho.py -s [port]            (server)')
    print('or:    python tcpecho.py -c host [port] <file (client)')
    # 종료
    sys.exit(2)


# 서버 함수
def server():
    # 매개 변수가 2개 초과라면
    # ex>$ python tcpecho.py -s 8001
    if len(sys.argv) > 2:
        # 두번째 매개변수를 포트로 지정
        port = eval(sys.argv[2])

    # 매개 변수가 2개 라면
    # ex>$ python tcpecho.py -s
    else:
        # 기본 포트로 설정
        port = ECHO_PORT

    # 소켓 생성 (UDP = SOCK_DGRAM, TCP = SOCK_STREAM)
    s = socket(AF_INET, SOCK_STREAM)

    # 포트 설정
    s.bind(('', port))

    # 포트 ON
    s.listen(QUEUE_LIMIT)

    # 준비 완료 화면에 표시
    print('tcp echo server ready')

    # 연결 대기
    print('wait for client ')
    c_sock, addr = s.accept()

    print('connected from {}:{}'.format(addr[0], addr[1]))

    isRunning = True
    # 루프 돌면서 클라이언트로 들어온 데이터 그대로 재 전송
    while (isRunning):
        # readBuf = c_sock.recv(BUFSIZE)
        txt_length = c_sock.recv(4)  # Read the length of text
        txt_name = c_sock.recv(int.from_bytes(txt_length, "little", signed=False))
        st_length = c_sock.recv(4)  # Read the length of stream
        readBuf = c_sock.recv(int.from_bytes(st_length, "little", signed=False))
        if len(readBuf) == 0:
            break

        nparr = np.frombuffer(readBuf, dtype="uint8")
        img_decode = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        # cv2.imshow("img_decode", img_decode)
        # cv2.waitKey(1)
        cv2.imwrite("recv_" + txt_name.decode(), img_decode)

        time.sleep(5)

        # print('read data {}, length {}'.format(readBuf, len(readBuf)))
        # c_sock.send(readBuf)
        print('read data: {}, length: {}'.format(txt_name.decode(), int.from_bytes(st_length, "little", signed=False)))
        c_sock.send(b"Done")
    print('disconnected ')
    c_sock.close()
    s.close()


# 클라이언트 함수
def client():
    # 매개변수가 3개 미만 이라면
    if len(sys.argv) < 3:
        # 사용 방법 화면에 출력
        # usage함수에서 프로그램 종료
        usage()

    # 두번째 매개변수를 서버 IP로 설정
    host = sys.argv[2]

    # 매개변수가 3개를 초과하였다면(4개라면)
    # ex>$ python tcp_echo.py -c 127.0.0.1 8001
    if len(sys.argv) > 3:
        # 3번째 매개변수를 포트로 설정
        port = eval(sys.argv[3])

    # 초과하지 않았다면(즉, 3개라면)
    # ex>$ python tcp_echo.py -c 127.0.0.1
    else:
        # 기본 포트로 설정
        port = ECHO_PORT

    # IP 주소 변수에 서버 주소와 포트 설정
    addr = host, port

    # 소켓 생성
    s = socket(AF_INET, SOCK_STREAM)

    try:
        s.connect(addr)
    except Exception as e:
        print('connection failed')
        sys.exit(2)

    # 연결되어 준비 완료 화면에 출력
    print('connected! \n tcp echo client ready')

    # 무한 루프
    isRunning = True
    while isRunning:
        # 터미널 창(입력창)에서 타이핑을하고 ENTER키를 누를때 까지
        txt = sys.stdin.readline()

        # 변수에 값이 없다면
        if not txt:
            break

        # 개행 제거
        txt = txt.replace('\n', '')
        txt_name = txt.encode()
        txt_length = len(txt_name)
        print("txt: ", txt)

        # # 입력받은 텍스트를 서버로 발송
        # sent = s.send(txt.encode())

        # Send input image in bytes to server
        img = cv2.imread(txt, -1)
        en = cv2.imencode(".jpg", img)
        stream = en[1].tostring()
        st_length = len(stream)

        fmt = "<i" + str(txt_length) + "si" + str(st_length) + "s"
        data_to_send = pack(fmt, txt_length, txt_name, st_length, stream)
        sent = s.send(data_to_send)

        if sent == 0:
            print("socket connection broken")
            break

        # 리턴 대기
        chunks = []
        bytes_cnt = 0
        while bytes_cnt < 4:    # 4 = Done
            chunk = s.recv(BUFSIZE)
            if chunk == b'':
                isRunning = False
                print("read error")
                break
            chunks.append(chunk)
            bytes_cnt = bytes_cnt + len(chunk)

        data = b''.join(chunks)

        # 서버로부터 받은 메시지 출력
        print('client received {}'.format(data))

    s.close()
    print('close')


main()