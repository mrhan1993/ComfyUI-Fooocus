import socket

def is_port_alive(host, port, timeout=2):
    """
    检测指定主机的端口是否存活
    :param host: 目标主机（IP 或域名）
    :param port: 目标端口
    :param timeout: 连接超时时间（秒）
    :return: True（端口存活） / False（端口关闭或不可达）
    """
    try:
        # 创建一个 socket 对象
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)  # 设置超时时间
        # 尝试连接
        result = sock.connect_ex((host, port))
        sock.close()  # 关闭连接
        # 如果返回 0，说明连接成功
        return result == 0
    except Exception as e:
        print(f"检测端口时出错: {e}")
        return False
