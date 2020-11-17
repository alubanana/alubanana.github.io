---
title: "NBA Database Design"
date: 2020-05-11
categories: [Database, Columbia,Web Application]
tags: [SQL, PostgreSQL, Flask, Database, GCP, Web Application]
header: 
    image: "images/header_square.png"
excerpt: "Building a Database for All NBA Fans"
mathjax: false
toc_label: "Outline"
toc: true
toc_sticky: true

---

## NBA Database Project

- COMSW 4111 001: Introduction to Databases

- Project: NBA Database

- Instructor: Kenneth Ross

- Group 36

- [Link to Github](https://github.com/alubanana/NBA_Database_Project)

Member: 
- ac4619 Annan Chen
- jl5521 Jiepeng Lian

This is a project of relational database that gives us a scope of how NBA league and its members behave and how do they connect to each other. With this database, you can find out each team and player’s actions and basic stats during the season(stadium, players, coaches, etc), each player’s shot informatrion during one specific game(time clock, shot distance, etc.)

Inside the Virtual Machine command line, type the following commands with account name and password to activate the database. 

1. `source ../jl5521/.virtualenvs/dbproj/bin/activate`
2. `PGPASSWORD=6447 psql -U jl5521 -h 35.231.103.173 -d proj1part2`


[Web application URL](http://35.227.53.125:8111/)
- *Note: Page might not work as VM is not activated on the Google Cloud.*

### ER Diagram

In our part 1 description, we plan to build the NBA stats database with following functions: We would like to provide our users with a web-based platform where they can search their interested players and see his seasonal stats, and how he perform in each game during the entire season (visualization could be done here). Also, if someone wants to know more about his/her favorite team, he/she can click the team and see team’s game schedule, past records, news, team info etc. And we can use different visualization factor to demonstrate those results. 

<img src="{{ site.url }}{{ site.baseurl }}/images/database/er.png" alt="ER Diagram" width = "600">


### Database Overview

We have done most of the part we planned: 1. Player Search to view his seasonal stat and basic information, the performance each game, news about the players. 2. Team Search that provides team schedule, team information and player lists. For most of the cases, the project will satisfy our users’ need of knowing more about the NBA players and team, and we can enrich our database if we have more data about NBA’s seasonal stats. 

For further improvement of our project, one could add trade information among teams and players. We can not find specific trading information on our season that we have data on. And as it is time-related data, for user who view this database before and after the trade might observe different result. Therefore the implementation of this function could be challenging. Also, people can insert visualization function of team in the future, such as the bar chart of the player of 10 highest salary, or every shot result of a player made in each game using basketball court as background. This might require a 2-dimension statistics about the shot and also the implementation of visualization tools in the database web interface. Therefore if someone possesses such data, he/she can try on this direction.  

### Database Pages

#### Search for Players

The two main pages we build is “Search for players” and “Search for teams”. 
Search for Player will provide all players that match your searched string. For example, if you type in “Stephen”, the database will return “Stephen Curry” and “Lance Stephenson”. By clicking the name of each player, you can view the seasonal statistic for this player, including team name, position, height, weight, total blocks, rebound, assist, career start year, salary, and seasonal average data such as 2-point and 3-point shot percentage, etc. Also, if you want to have more information about this player, you can click “News” to view all the news related to this player. Finally, you can click “Schedule” to view all the matches that this player had during this period(for our database, it only records the matches during 2016 March 1st to March 4th). This schedule bottom provides information for this player in each game, including the number of total attempted shots, made shot, missed shot and some other information about the shots like average time clock, average shot distance, etc. One of the interesting things we found out is that, for Stephen Curry his average shot distance is higher than most of other players, for example, Lance Stephenson, which is very intuitive as we know Curry is such a player who likes making the shot from downtown. 

+ Example Query: Find players whose salary is 4 times higher than league average

```sql
SELECT p1.player_name, p1.team_name, p1.salary FROM players p1, players p2 GROUP BY p1.player_name, p1.team_name, p1.salary HAVING p1.salary > AVG(p2.salary) * 4 ORDER BY p1.salary DESC;
```

<img src="{{ site.url }}{{ site.baseurl }}/images/database/db1.png" alt="my photo">

#### Search for Teams

Search for teams will gives back specific team information about the team you want to search for. For example, if you type in “New York”, the database will return “New York Knicks”, and you can further click on the team name to have more information about it. The team’s information contains found year, city of the team, state, stadium of the team, the main coach, player list and all match schedule during the given period. The “players lists” will give back all the players in this team. Similar to the “search for players” function, you can click on any player name in this team to view the same information like you directly search for him. Also, “schedule” function will provide all the match this team play against other team, and from here you can view other team’s information as well. 

+ Example Query:Rank the total salary for all teams and select 5 highest ones

```sql
SELECT SUM(salary) AS total_salary, team_name FROM players GROUP BY team_name ORDER BY sum(salary) DESC LIMIT 5;
```

<img src="{{ site.url }}{{ site.baseurl }}/images/database/db2.png" alt="my photo">


### More Information

For more information about the database schema, design process and function please refer to the following links: 
1. Part 1: [Database Overview and ER Diagram](https://github.com/alubanana/NBA_Database_Project/blob/master/part%201.pdf)
2. Part 2: [SQL Schema and Test Queries](https://github.com/alubanana/NBA_Database_Project/blob/master/part%202/DB_project_part2.pdf)
3. Part 3: [Web Application Development](https://github.com/alubanana/NBA_Database_Project/tree/master/part3)
3. Part 4: [Updates and Full Text Search](https://github.com/alubanana/NBA_Database_Project/blob/master/part4/README_part4.pdf)

