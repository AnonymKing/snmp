# 将数据库中的数据转行成画图说要用到的数据
# 将数据保存到文件
# 这样不用每次画图都重新从数据库获取数据并计算

import IPy
import json
from pymongo import MongoClient
from conf import DB_URL

my_client = MongoClient(DB_URL)
my_db = my_client.get_database("dbname")
my_set = my_db.get_collection("ip_info")
result = my_set.find()
result_list = list(result[:])
ip_list = IPy.IPSet()

data = {}
Trace = set()
Nodes_Dst = set()
Nodes_Route = set()


def load_ip_list():
    try:
        with open("./data/ip.list", "r") as fp:
            tmp = fp.readlines()
            for ip in tmp:
                ip_list.add(IPy.IP(ip.strip()))
        return True
    except Exception as err:
        print(err)
        return False


def limit_cernet(route_list):
    routes = []
    for item in route_list:
        if IPy.IP(item["ip"]).iptype() == "PRIVATE" or IPy.IP(item["ip"]) in ip_list:
            routes.append(item)
    return routes


def limit_china(route_list):
    routes = []
    for item in route_list:
        if item["point"][0] != "" and item["point"][1] != "":
            lon = float(item["point"][0])
            lan = float(item["point"][1])
            if 73 < lon < 136 and 3 < lan < 54:
                routes.append(item)
    return routes


def sort_data():
    try:
        print(len(result_list))
        for res in result_list:
            Nodes_Dst.add(res["dst"])
            data[res["dst"]] = res["point"]
            trace = limit_china(res["trace"])
            length = len(trace)
            for index, route in enumerate(trace):
                Nodes_Route.add(route["ip"])
                data[route["ip"]] = route["point"]
                if index < length - 1:
                    Trace.add((route["ip"], trace[index + 1]["ip"]))
        return True
    except Exception as err:
        print("DB Error: ", err)
        return False


def save_data():
    try:
        with open("./data/data.json", "w+") as fp:
            fp.write(json.dumps(data))
        with open("./data/node_dst.list", "w+") as fp:
            for dst in Nodes_Dst:
                fp.write(dst + "\n")
        with open("./data/node_route.list", "w+") as fp:
            for route in Nodes_Route:
                fp.write(route + "\n")
        with open("./data/trace.list", "w+") as fp:
            for trace in Trace:
                fp.write("{},{}\n".format(trace[0], trace[1]))
        return True
    except Exception as err:
        print(err)
        return False


if __name__ == "__main__":
    if load_ip_list():
        if sort_data():
            if save_data():
                print("Sort Data Over!")
