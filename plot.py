import json
from pyecharts import options as opts
from pyecharts.charts import Geo
from pyecharts.globals import ChartType, SymbolType

data = {}
Trace = set()
Nodes_Dst = set()
Nodes_Route = set()


# 初始化节点数据
def init_data():
    global data, Trace, Nodes_Route, Nodes_Dst

    try:
        with open("./data/data.json", "r") as fp:
            data = json.loads(fp.read())
        with open("./data/node_dst.list", "r") as fp:
            res = fp.readlines()
            for dst in res:
                Nodes_Dst.add(dst.strip())
        with open("./data/node_route.list", "r") as fp:
            res = fp.readlines()
            for route in res:
                Nodes_Route.add(route.strip())
        with open("./data/trace.list", "r") as fp:
            res = fp.readlines()
            for trace in res:
                Trace.add(tuple(trace.strip().split(",")))
        return True
    except Exception as err:
        print(err)
        return False


def plot():
    # 初始化图表信息
    geo = Geo(init_opts=opts.InitOpts(width="96vw", height="96vh", page_title="教育网拓扑图",
                                      animation_opts=opts.AnimationOpts(animation=False)))
    
    # 添加地图
    geo.add_schema(maptype="china")
    
    # 添加所有点的地理信息
    geo.add_coordinate_json("./data/data.json")

    # 画中间节点
    geo.add("Route", [(i, "Route") for i in Nodes_Route], color="Red", point_size=4, symbol_size=4,
            effect_opts=opts.EffectOpts(is_show=False))

    # 画目的节点
    geo.add("Dst", [(i, "Dst") for i in Nodes_Dst], color="SeaGreen", point_size=4, symbol_size=4,
            effect_opts=opts.EffectOpts(is_show=False))

    # 画线 展示拓扑信息
    geo.add("", list(Trace), type_=ChartType.LINES,
            effect_opts=opts.EffectOpts(is_show=False, symbol_size=2),
            linestyle_opts=opts.LineStyleOpts(curve=0.1))

    geo.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    geo.set_global_opts(title_opts=opts.TitleOpts(title="教育网拓扑图"))

    # 生成图表到指定文件
    geo.render("./dist/render.html")


if __name__ == "__main__":
    if init_data():
        plot()
        print("Plot Over")
