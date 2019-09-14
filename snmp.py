# 多进程探测主机的存活性
# 获取存活主机的拓扑
# 保存主机及其拓扑信息到MongoDB
from scapy.layers.inet import *
import logging
import IPy
from pymongo import MongoClient
import threading
import multiprocessing
import IPLocate
from conf import DB_URL

Debug = False
my_client = MongoClient(DB_URL)
my_db = my_client.get_database("dbname")
my_set = my_db.get_collection("ip_info")
ip_db = IPLocate.IP()
ip_db.load_dat("./data/埃文科技IP数据库.dat")


def get_point(ip):
    if IPy.IP(ip).iptype() == "PRIVATE":
        return (122.089909, 37.540047)
    else:
        # 这里由于IP数据库数据不全 会报错
        # 应该与在线IP定位API配合使用
        # 经过测试 本项目所有的数据均可以正常获取 故无需多做处理
        return tuple((float(ip_db.locate_ip(ip)[9]), float(ip_db.locate_ip(ip)[10])))


def is_alive(ip):
    global Debug
    ans, _ = sr(IP(dst=ip) / TCP(dport=80, flags="S"), timeout=3, verbose=Debug)
    # ans, _ = sr(IP(dst=ip) / ICMP(), timeout=2, verbose=Debug)
    if ans:
        for _, rcv in ans:
            if rcv.src == ip:
                return True
        return False
    else:
        return False


def get_trace(ip, retry=2):
    global Debug
    dport = [3389, 22, 80]
    ans, _ = traceroute(ip, maxttl=30, timeout=3, dport=dport[retry], verbose=Debug)
    # print("Ans:", ans.get_trace())
    trace = ans.get_trace()[ip]
    res = False
    for k in trace.keys():
        res = trace[k][1]
        if res:
            break
    if not res:
        if retry > 0:
            return get_trace(ip, retry - 1)
        else:
            return False, None
    else:
        data = {
            "ip": ip,
            "trace": []
        }
        notes = sorted(list(trace.keys()))
        for note in notes:
            data["trace"].append(
                {
                    "ip": trace[note][0],
                    "point": get_point(trace[note][0])
                }
            )
            if trace[note][1]:
                break
        return True, data


def save_ip(trace, point):
    global my_set
    ip_info = {
        "dst": trace["ip"],
        "point": point,
        "trace": trace["trace"]
    }
    # print("update!")
    # $setOnInsert 作用：不存在才插入数据
    my_set.update_one({'dst': trace["ip"]}, {'$setOnInsert': ip_info}, upsert=True)


def worker(in_queue, out_queue):
    while True:
        ip = in_queue.get()
        if not ip:
            return
        try:
            ip_active = is_alive(ip)
            if ip_active:
                # print(ip)
                # print("Alive", end=" ")
                point = get_point(ip)
                res, data = get_trace(ip)
                if res:
                    out_queue.put((data, point))
                    # print("Succ", end=" ")
                # print()
        except:
            # traceback.print_exc()
            pass
        finally:
            in_queue.task_done()


def get_result(out_queue):
    while True:
        res = out_queue.get()
        if not res:
            return
        try:
            save_ip(res[0], res[1])
        except Exception as err:
            logging.error("DB Error: " + str(err))
        finally:
            out_queue.task_done()


if __name__ == '__main__':
    worker_amount = 32
    queue_size = worker_amount * 4
    in_queue = multiprocessing.JoinableQueue(maxsize=queue_size)
    out_queue = multiprocessing.JoinableQueue(maxsize=queue_size)

    fp = open("ip.list", "r")
    ip_list = fp.readlines()
    fp.close()

    pool = []
    for i in range(worker_amount):
        process = multiprocessing.Process(target=worker, args=(in_queue, out_queue))
        process.start()
        pool.append(process)

    thread = threading.Thread(target=get_result, args=(out_queue,))
    thread.start()

    for ips in ip_list:
        for ip in IPy.IP(ips.strip()):
            in_queue.put(ip.strNormal())

    # end input
    in_queue.join()

    # 发送结束指令
    for _ in range(worker_amount):
        in_queue.put("")

    # end output
    out_queue.join()
    out_queue.put("")

    # end all
    for p in pool:
        p.join()
    thread.join()

    my_client.close()
    print("Scan Host Over!")
