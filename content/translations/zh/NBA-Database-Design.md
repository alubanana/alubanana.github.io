## NBA 数据库项目

- COMSW 4111 001：数据库导论（Introduction to Databases）
- 项目：NBA 数据库
- 教师：Kenneth Ross
- 第 36 组
- [GitHub 链接](https://github.com/alubanana/NBA_Database_Project)

成员：

- ac4619 Annan Chen
- jl5521 Jiepeng Lian

这是一个关系数据库项目，用于了解 NBA 联盟及其成员的表现，以及他们之间的联系。通过数据库，可以查看各支球队和球员在赛季中的活动与基本数据，例如球馆、球员、教练等信息；也可以查看某位球员在一场特定比赛中的投篮信息，例如比赛计时、投篮距离等。

在虚拟机的命令行中，输入以下带有账户名和密码的命令，激活数据库。

1. `source ../jl5521/.virtualenvs/dbproj/bin/activate`
2. `PGPASSWORD=<redacted> psql -U jl5521 -h 35.231.103.173 -d proj1part2`

[Web 应用地址](http://35.227.53.125:8111/)

- *注：如果 Google Cloud 上的虚拟机未启动，页面可能无法访问。*

### ER 图

在第一部分的项目说明中，我们计划构建一个 NBA 数据库，并提供以下功能：用户可以通过网页搜索感兴趣的球员，查看其赛季统计，以及整个赛季中每场比赛的表现；这里可以加入可视化。如果用户想进一步了解喜欢的球队，也可以点击球队，查看赛程、历史战绩、新闻和球队信息等。我们还可以采用不同的可视化方式来展示这些结果。

<img src="{{ site.url }}{{ site.baseurl }}/images/database/er.png" alt="ER Diagram" width = "600">

### 数据库概览

我们完成了原计划中的大部分内容：1. 球员搜索，可以查看赛季统计、基本信息、各场比赛表现及相关新闻；2. 球队搜索，可以查看球队赛程、球队信息和球员名单。在大多数情况下，项目能够满足用户了解 NBA 球员和球队的需求。如果有更多 NBA 赛季统计数据，还可以继续丰富数据库。

后续可以加入球队和球员之间的交易信息。我们未能找到当前数据所属赛季的具体交易资料。这类数据具有时间属性，用户在交易前后查看数据库，可能会得到不同结果，因此实现起来可能比较复杂。此外，未来还可以加入可视化，例如薪资最高的 10 名球员的柱状图，或以篮球场为背景展示某位球员在每场比赛中的每次投篮结果。后者可能需要投篮的二维位置数据，以及数据库网页界面中的可视化工具。如果具备这类数据，可以沿这个方向继续尝试。

### 数据库页面

#### 球员搜索

我们构建的两个主要页面是“球员搜索”和“球队搜索”。

球员搜索会返回所有与搜索字符串匹配的球员。例如，输入“Stephen”，数据库会返回“Stephen Curry”和“Lance Stephenson”。点击球员姓名，即可查看其赛季统计，包括球队、位置、身高、体重、盖帽总数、篮板、助攻、职业生涯起始年份、薪资，以及两分球和三分球命中率等赛季平均数据。还可以点击“News”，查看与该球员有关的全部新闻。

最后，点击“Schedule”，可以查看该球员在指定时期参加的全部比赛；我们的数据库只记录了 2016 年 3 月 1 日至 3 月 4 日的比赛。赛程按钮还提供球员在每场比赛中的投篮出手总数、命中数、未命中数，以及平均比赛计时、平均投篮距离等信息。我们发现，Stephen Curry 的平均投篮距离高于许多其他球员，例如 Lance Stephenson。这也符合直觉，因为库里喜欢在三分线外出手。

+ 查询示例：查找薪资高于联盟平均薪资 4 倍的球员。

```sql
SELECT p1.player_name, p1.team_name, p1.salary FROM players p1, players p2 GROUP BY p1.player_name, p1.team_name, p1.salary HAVING p1.salary > AVG(p2.salary) * 4 ORDER BY p1.salary DESC;
```

<img src="{{ site.url }}{{ site.baseurl }}/images/database/db1.png" alt="球员查询页面">

#### 球队搜索

球队搜索会返回目标球队的具体信息。例如，输入“New York”，数据库会返回“New York Knicks”；进一步点击球队名称，可以查看成立年份、所在城市和州、主场球馆、主教练、球员名单，以及指定时期内的全部赛程。

“players lists”会列出球队的全部球员。与球员搜索类似，点击其中任意球员的姓名，就可以查看直接搜索该球员时得到的相同信息。“schedule”则会列出该球队对阵其他球队的比赛，也可以从这里继续查看其他球队的信息。

+ 查询示例：按球队总薪资排序，选出最高的 5 支球队。

```sql
SELECT SUM(salary) AS total_salary, team_name FROM players GROUP BY team_name ORDER BY sum(salary) DESC LIMIT 5;
```

<img src="{{ site.url }}{{ site.baseurl }}/images/database/db2.png" alt="球队查询页面">

### 更多资料

数据库模式、设计过程和功能的更多信息见以下链接：

1. 第一部分：[数据库概览与 ER 图](https://github.com/alubanana/NBA_Database_Project/blob/master/part%201.pdf)
2. 第二部分：[SQL 模式与测试查询](https://github.com/alubanana/NBA_Database_Project/blob/master/part%202/DB_project_part2.pdf)
3. 第三部分：[Web 应用开发](https://github.com/alubanana/NBA_Database_Project/tree/master/part3)
3. 第四部分：[更新与全文搜索](https://github.com/alubanana/NBA_Database_Project/blob/master/part4/README_part4.pdf)
