# 中国教育网拓扑探测

### 0x00 简介
+ HITwh2016级，信息安全课程设计III
+ 任务概述：对中国教育网CERNET进行拓扑发现；实现对教育网的拓扑数据采集，拓扑数据处理，以及拓扑数据展示，并将拓扑结构以图形界面呈现。


### 0x01 要求
+ 拓扑数据采集
    1. 采用基于traceroute的网络探测方法;
    2. 判断目标网络节点的存活情况，并获取目标网络中节点的连接情况。
+ 拓扑数据处理
    1. 根据采集到的拓扑数据，生成路径总表；
    2. 通过解析路径总表中的信息得到目标网络的拓扑结构，完成IP信息获取和保存；
    3. 将处理好的拓扑数据传输给数据展示模块进行结果展示。
+ 拓扑数据展示
    1. 物理布局：以地图为背景展示出拓扑的位置分布。结合节点的地理位置信息以中国地图为背景，显示探测的节点在全国的位置分布，反映出中国教育网CERNET在全国的分布密度和连接情况；
    2. 逻辑布局：以一种直观的方式展示拓扑连接关系，采用图形的方式显示网络的拓扑。通过运行程序实现对从数据处理模块中获取的拓扑信息做处理，生成拓扑图。

### 0x02 说明
+ 开发语言、数据库不限；
+ 拓扑测量节点数量多，拓扑数据展示清晰，成绩可以评定为优秀；
+ 地理位置信息呈现在全国范围即可。


### 0x03 思路
+ 由于教育网的IPv4地址段数目过多，考虑多进程实现；
+ 先探测主机的存活性（使用ping实现），对于存活的主机进行路径探测（使用traceroute实现）；
+ IP地址的经纬度获取一开始考虑使用网上一些著名的API接口，最后发现都限速、限量并且不免费，最终选择使用埃文科技的试用版离线数据库和API相结合的方式进行获取相应IP的经纬度信息，其速度和精准度都相当的可观；
+ 将获取到的数据存储到MongoDB数据库，其格式如下：
```json
{
    "dst" : "目标主机Host",
    "point" : [ 
        "目标主机经度", 
        "目标主机纬度"
    ],
    "trace" : [ 
        {
            "ip" : "中间节点Host",
            "point" : [ 
                "中间节点经度", 
                "中间节点纬度"
            ]
        },
        {
            "ip" : "中间节点Host",
            "point" : [ 
                "中间节点经度", 
                "中间节点纬度"
            ]
        }
    ]
}
```
+ 利用Python中的pyecharts库进行画图，这里我将逻辑图和物理图画在了一起，同时在地图上展示中间节点和目的节点。

### 目录
```html
├── data                   数据目录
|   ├── data.json          节点经纬度
|   ├── ip.list            教育网IP地址
|   └── ip_info.json       MongoDB数据库所有IP信息备份
|   ├── node_dst.list      所有目的节点
|   ├── node_route.list    所有中间节点
|   └── trace.list         拓扑路径信息
├── dist                   编译结果目录
|   ├── maps               地图
|   ├── echarts.min.js     画图
|   └── render.html        拓扑图展示文件（主文件）
├── conf.py                数据库配置信息
├── IPLocate.py            埃文科技IP数据查询辅助文件
├── plot.py                使用data文件夹下的数据进行绘图
├── snmp.py                探测主机存活、获取并保存拓扑信息
├── sort_data.py           将数据库信息转换成可画图信息
├── requirements.txt       所使用的Python3依赖库
└── READMD.md              项目介绍
```

### 补充说明
+ 埃文科技IP数据库请自行下载：[IP问问-离线库](https://mall.ipplus360.com/pros/IPGeoDB)；
+ MongoDB数据库的安装与使用请自行学习；
+ 使用`pip install -r requriements.txt`安装依赖库；
+ 关于pyecharts的使用请参考：[pyecharts官方文档](https://pyecharts.org/#/zh-cn/intro)
+ 关于scapy的使用请参考：[scapy官方文档](https://scapy.readthedocs.io/en/latest/)
+ 关于multiprocessing的使用请参考：[multiprocessing官方文档](https://docs.python.org/zh-cn/3/library/multiprocessing.html)
+ 关于threading的使用请参考：[threading官方文档](https://docs.python.org/zh-cn/3/library/threading.html)