# Hunt A Squirrel

## 网站链接

访问[这个网站](https://tools-254123.appspot.com)，追踪中央公园的松鼠！

<img src="{{ site.url }}{{ site.baseurl }}/images/tools/tools1.png" alt="松鼠观察记录网站">

## 项目介绍

Hunt A Squirrel 是一个用于记录中央公园所有已知松鼠的 Web 应用。它在地图上展示松鼠目击地点，也提供松鼠是否正在进食、奔跑等信息。无论你喜欢松鼠还是害怕松鼠，想找到它们还是避开它们，这个应用都可以提供帮助。

## 背景

公司新老板 Joffrey Hosencratz 喜欢《瑞克和莫蒂》。剧中的某个场景，加上他童年与松鼠有关的创伤经历，以及在塞多纳一次糟糕的水晶浴体验，让他产生了一个愿望：开始记录所有已知的松鼠，并打算先从中央公园做起。

## 数据来源

2018 年中央公园松鼠普查（2018 Central Park Squirrel Census）。

## 依赖

Django。

## 主要功能

### 管理命令

- 导入：从 2018 年普查的 CSV 文件中导入数据。在管理命令名称后，通过命令行指定文件路径。

  `python manage.py import_squirrel_data /path/to/file.csv`

- 导出：将数据导出为 CSV 文件。在管理命令名称后，通过命令行指定文件路径。

  `python manage.py export_squirrel_data /path/to/file.csv`

### 视图

- 在 OpenStreets 地图上展示松鼠目击地点。
  - 路径：/map
  - 支持的方法：GET
- 列出所有松鼠目击记录，并提供各条记录的编辑链接。
  - 路径：/sightings
  - 支持的方法：GET
- 更新指定的目击记录。
  - 路径：`/sightings/<unique-squirrel-id>`
  - 支持的方法：GET & POST
- 创建新的目击记录。
  - 路径：/sightings/add
  - 支持的方法：GET & POST
- 展示目击记录的总体统计。
  - 路径：/sightings/stats
  - 方法：GET

#### 松鼠数据的编辑页面

<img src="{{ site.url }}{{ site.baseurl }}/images/tools/tools2.png" alt="松鼠目击记录编辑页面">

## 项目成员

小组编号：74。

班级编号：02。

小组成员：Annan Chen、Tianqi Shen。

UNI：[ac4619, ts3255]。
