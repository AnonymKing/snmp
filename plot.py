import json
from pyecharts import options as opts
from pyecharts.charts import Geo
from pyecharts.globals import ChartType, SymbolType

data = {}
Trace = set()
Nodes_Dst = set()
Nodes_Route = set()


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
    geo = Geo(init_opts=opts.InitOpts(width="96vw", height="96vh",
                                      animation_opts=opts.AnimationOpts(animation=False)))

    geo.add_schema(maptype="china")
    geo.add_coordinate_json("./data/data.json")

    geo.add("Route", [(i, "Route") for i in Nodes_Route], color="Red", point_size=4, symbol_size=4,
            effect_opts=opts.EffectOpts(is_show=False))

    geo.add("Dst", [(i, "Dst") for i in Nodes_Dst], color="SeaGreen", point_size=4, symbol_size=4,
            effect_opts=opts.EffectOpts(is_show=False))

    geo.add("", list(Trace), type_=ChartType.LINES,
            effect_opts=opts.EffectOpts(is_show=False, symbol_size=2),
            linestyle_opts=opts.LineStyleOpts(curve=0.1))

    geo.set_series_opts(label_opts=opts.LabelOpts(is_show=False))
    geo.set_global_opts(title_opts=opts.TitleOpts(title="教育网拓扑图"))

    geo.render("./dist/render.html")


if __name__ == "__main__":
    if init_data():
        plot()
        print("Plot Over")
