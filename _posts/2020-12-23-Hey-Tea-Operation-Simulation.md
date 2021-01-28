---
title: "Which Order First, Offline or Online?--HEYTEA Operating Strategy"
date: 2020-12-23
categories: [Simulation, Columbia, Python, Simpy]
tags: [Strategy, Operation, Python, Simpy]
header: 
    image: "images/header_square.png"
excerpt: "Improve operation for one of the most famous milk tea brands in China"
mathjax: true
toc_label: "Outline"
toc: true
toc_sticky: true

---

- [Link to Github](https://github.com/alubanana/Hey_Tea_Operation_Simulation)

- [Full Report](https://github.com/alubanana/Hey_Tea_Operation_Simulation/blob/master/HEYTEA%20Project%20Report-Group%202.pdf)

- [Presentation Slides](https://github.com/alubanana/Hey_Tea_Operation_Simulation/blob/master/HEYTEA%20PPT_Group%202.pdf)

- [Draft](https://github.com/alubanana/Hey_Tea_Operation_Simulation/blob/master/heytea%20model%20draft.pdf)



# Background, Value and Question

## Background

HEYTEA(喜茶) is one of the most famous tea brands in China founded in 2012, providing drinks such as milk tea, fruit tea and cheese tea for especially young customers. As the creator of the original Cheezo Tea, HEYTEA sources the finest tea globally, at the same time, supports artistic creation, hoping to breathe new life into the traditional tea culture and make drinking tea become a style of life. With such concepts, HEYTEA quickly expands among higher-tier cities, and has over 400 stores nationwide. Customers can choose to order in store or online via WeChat Mini-program.

<img src="{{ site.url }}{{ site.baseurl }}/images/tea/tea1.png" alt="my photo">

Warm welcome by customers and rapid expansion arise HEYTEA’s reputation but also bring about efficiency management problems. In the case of milk tea merchants have launched delivery services, HEYTEA launched its own small program and entered the public comment platform to provide delivery services. However, this exacerbates the efficiency problems faced by companies.

In many order delivery platforms, the most common complaint is that the queue is too long and the meal is too slow. On September 16, 2019, there was even a vicious incident of physical conflict between delivery personnel and staff due to untimely meal delivery. Although the company subsequently made a public apology and explained the matter, it caused a very bad impact on public opinion. [link](https://kuaibao.qq.com/s/20190917A0IT8000?refer=spider)

This is due to the fact that many new tea brands, including HEYTEA, adopt the manual production mode, so the production capacity of such stores is relatively low, and the order peak is prone to lead to the backlog of orders and the problems of queuing and dining lag.

Therefore, it is important for the company to balance the production and distribution of takeout and offline orders to reduce the waiting time of customers and improve customer satisfaction. At the same time, maximize the company's revenue. **To achieve the balance between revenue and customer experience is the significance of our project.**
 

## Value Proposition

Value is not only reflected in the money value, but also in the reputation and brand value of the enterprise.

For the enterprise level, our recommendation strategy not only focuses on revenue, but also focuses on customer experience. Through the optimization of multi-objective function, we propose the most feasible strategy. It can optimize the balance between the overall revenue and customer satisfaction in the case of high-speed expansion.

For customers, our strategy reduces the average waiting time, which significantly improves the dining experience of customers and helps to improve the reputation and brand value of enterprises.
It has a positive impact both in the short and long term. In the short term, the strategy will improve efficiency, thus improving the overall revenue. In the long run, improving customer satisfaction will help improve customer retention and repurchase, which is valuable asset for the company.


## Business Question

In this project, we, representing the consulting group of HEYTEA to help find the proper plan, will simulate the real scenarios of a HEYTEA store in Beijing, considering every single working procedure in detail. We will set different objectives for HEYTEA, including maximizing total revenue, minimizing the average customer waiting time and maximizing the combination of the two objects, total revenue with the time penalty. In addition, we use three other objects, total order, total lost orders, total lost revenue to cross check our validation of the parameter of our strategy. We will find the best solution to prioritize orders based on different objectives or multi-objectives. The real scenario simulation works as follows.



## Data Exploration and Databases

We mainly explored the following two databases: Preqin and Capital IQ.

Preqin is a database focusing on PE and VC funds. Under the Performance tag, we can see fund specific historical performance data. Users have access to download two kinds of performance data: historical funds info data and funds specific historical performance data.

# Models 

We simulate typical rush hours for HEYTEA from 11:00AM to 16:00PM. Any customers arriving before 15:00PM will be served and no customers arriving after 15:00PM will be served. There are two types of customers: offline customers who arrive the HEYTEA store and online customers who order online and wait for the delivery service of drinks. Based on actual operating data, the online arrival rate is λ_online=240 per hour and offline arrival rate is λ_offline=120 per hour. Usually, the online arrival rate is higher than the offline arrival rate, but the price from online channel is lower than that of offline. We further assume that there are 5 kinds of drinks provided by offline channel:

<img src="{{ site.url }}{{ site.baseurl }}/images/tea/tea2.png" alt="my photo">

Each type has different price, different probability to be ordered and different speed to be completed by HEYTEA workers. The making time for each product follows exponential distribution with rate 𝜇 determined by the type of the product. Online products have the same probability to be ordered. However, online price may enjoy a discount of 𝑑 = 35% and the serve rate is higher than the offline rate by 1. This is because offline customers need more serving time, including face-to-face ordering, collecting money and other things. For simplicity, we model these time occupations by assigning lower serve rates for offline customers. Moreover, because of limited capacity, both online and offline order system will be suspended if number of customers waiting in line exceeds the corresponding limits. The online limit γ_online=200 and γ_offline=30. If a customer arrivals and finds the system has been shut down, the customer will leave.

There are n=10 homogenous workers in a typical HEYTEA store. Upon arrival, a customer may submit an order for several drinks. The number of drinks follows an i.i.d. geometric distribution with p_offline=0.9 for offline customers and p_online=0.7 for online customers. This is because online customers tend to order more cups of drinks than offline ones. The type of each drink is independently determined. There are two waiting lines, one for online customers and the other for offline ones. We now assume that there are two operating strategies:

*STRATEGY 1: FIFO. Based on the time of arrival, orders are fulfilled sequentially, regardless of the online/offline channel. This is the traditional operating strategy and is equivalent to combining the two waiting lines into one.*

*STRATEGY 2: Priority Balance. We first set a parameter 𝜃 indicating the ideal ratio of online and offline orders. On each customer arrival, if the ratio of cumulated number of finished online orders to offline orders is higher than 𝜃, the first offline customers will be served when next worker is available, regardless of the arrival time of the customer.*

The information asymmetry between HEYTEA store and customers makes it possible to implement Strategy 2. Offline customers usually care about how many people in front of them in the offline queue and they seldomly know or care about how many people are waiting in the online queue. This is the same for online customers. Therefore, HEYTEA could give priority to specific type of customers without inducing any customers’ challenge of unfairness.

By introducing priority into the fulfilling process, strategy 2 may help HEYTEA to achieve several operating goals. Moreover, HEYTEA could control the ratio of served online and offline orders. For example, if the store wants to maximize the revenue, it may try to serve more offline customers because offline price is higher. We now list several goals that HEYTEA pursue:

1. *Maximize total revenue*
2. *Minimizing average waiting time of customers*
3. *Maximize total revenue with waiting time penalty*

To increase the utility of customers, HEYTEA may want customers to wait less time without eroding much revenue. GOAL3 is the closest one to the reality. We quantify the total revenue with waiting time penalty by:

<img src="{{ site.url }}{{ site.baseurl }}/images/tea/tea3.png" alt="my photo">

where *total price* is the total price for customer i, *t* is the total waiting time for customer i, *N* is the total number of served customers, and *a* is the adjusting factor. Notice that (1 − *at* ) squeezes the prices based on waiting time and *a* stands for the linear discount rate. We set *a* = 20%, which means that the total price for each customer is discounted by 20% for every hour waited.

# Implementation

For each above goal, we search the optimal *θ* by simulating the system by 100 arounds. Specifically, we try a sequence of *θ* from 0.01 to 100 and compare the mean, standard deviation and 95% confidence interval of each goal variable. We use Antithetic Method for variance reduction. We also compare our results to STRATEGY 1, which is our benchmark case.


# Result

For the vanilla LSTM model, we try to keep the most of the previous architecture, such as optimizer, the number of layers, epochs and loss function. However, we encounter the exploding gradient problem when we make the prediction. Though we have tried to use clip value, R2 regularization and batch normalization to put constraints on the weight, it doesn’t perform as desired. Also, as the previous mentioned that they experienced vanishing gradient problems and periodic results, for the first problem we changed the state activation function to ReLU and keep this change for the further models, for the second one we continue to use mini-batch size equal to 100 to avoid periodic prediction.

## 1. Total revenue

<img src="{{ site.url }}{{ site.baseurl }}/images/tea/tea4.png" alt="my photo">

This is our first goal of maximizing the total revenue. The result in panel A shows that the mean of total revenue does not show much difference when 𝜃 is smaller than 1.0. The total revenue reaches to its maximum of 29362.25 with 𝜃 being 1, which is reasonable, because the value of offline orders is larger than the online order. We should balance these two channels. Compared with the benchmark strategy, the revenue improves by 7%, which shows a significant improvement of profitability. In addition, the CI width is significantly small compared with the mean of total revenue, which shows the robust of our result.

## 2. Average waiting time

<img src="{{ site.url }}{{ site.baseurl }}/images/tea/tea5.png" alt="my photo">

<img src="{{ site.url }}{{ site.baseurl }}/images/tea/tea6.png" alt="my photo">

The result in panel A shows our second goal, minimizing the average waiting time. Both the mean and standard deviation is decreased compared with the benchmark result. When 𝜃 equals to 0.4 and 0.6, the average waiting time reaches 0.695, decreased by 10.8% compared with the FIFO strategy. In terms of the best *θ*, it is acceptable in the range of 0.01 to 0.8.

## 3. Total revenue with waiting time penalty

This goal is the mixed to reach the balance between maximizing revenue and the minimizing the average time at the same time. The result in Panel A shows the objectives reaches the highest when *θ* is 0.1. However, *θ* has no significant differences in the range of 0.01 to 0.8. What’s more, the best result of 24622 is significantly better than the benchmark result of 22305, increased by 10.4%. Also, our result is robust because both the CI width and standard deviation is significantly small compared with the mean of the objective.

<img src="{{ site.url }}{{ site.baseurl }}/images/tea/tea7.png" alt="my photo">

## 4. Total orders

<img src="{{ site.url }}{{ site.baseurl }}/images/tea/tea8.png" alt="my photo">

This goal is the to maximize total order we serve in the busy hour. The total order reaches the maximum value at 1117.13 at *θ* is 1, still grabbing 35 orders more than the benchmark. It is the busy hour already and the system has the limit capacity, so the improvement may not be that significant. However, we still see a better result by our strategy.

## 5. Total lost orders

<img src="{{ site.url }}{{ site.baseurl }}/images/tea/tea9.png" alt="my photo">

We are supposed to minimize the total lost order. The result is symmetrical to the total order we grab listed above. We get the best result at *θ* equals to 1.

## 6. Total lost revenue

<img src="{{ site.url }}{{ site.baseurl }}/images/tea/tea10.png" alt="my photo">

This result is related to the goal of minimizing the total lost revenue. When *θ* increases from 0.4 to 4.0, the total revenue lost decreases from 11032 to 10147. However, it does not achieve our benchmark of 10146, which is reasonable. Because our goal is not only to maximize the revenue, but also to improve the satisfaction of our customers.


## Policy Recommendation and Optimization

According to the results of the above six objective functions, we want to synthesize them to get the optimization strategy.

The import objectives for our model are revenue and total waiting time. When simply maximizing revenue, *θ* is 1. When minimizing average waiting time, the range from 0.4 to 0.6 is the optimal. When synthesize these two objectives, which is the total revenue with waiting time penalty, the optimization is achieved when *θ* reaches 0.8. It is approximately the average between 0.6 and 1. This result is in line with the model setting and our intuition, because the total revenue with waiting time penalty is the combination of the two object, our best *θ* is also the mixture of these two objects’ results.

We use other three objectives to do cross validation. At *θ* is 0.8, the total revenue, the average waiting time and total revenue with waiting time penalty are 29333, 0.701 and 24575.21, all of which are significantly better off than our benchmark, FIFO. In addition, the three other objectives, total order, total lost order are all in acceptable range.

To sum up, we balance profit and efficiency to achieve the strategy of control the online / offline order is about 0.8, which is the optimal state.

Our model is also very feasible. When the historical proportion of online and offline orders is different from our target proportion, in the future, we will change the service priority and go to manual intervention to maintain this proportion.

## Variance Reduction Technique

We use Antithetic Method on both the service time and the inter arrival time. The result achieved above is after the antithetic method. It leads to a robust result with relatively small CI.

# Contributions and Limitation

## Contributions

As the pioneer of new tea drinks in China, HEYTEA is popular and widely accepted, but it also faces many problems with its rapid expansion. Especially after the launch of the take away order platform with small programs and public comments, the contradiction between efficiency and customer experience has become increasingly prominent. After actual research and real ordering experience, our group decided to study how to balance efficiency and customer experience satisfaction, in order to achieve the optimization of the overall goal of the enterprise.

We simulate the process of customers' ordering and taking meals during the peak time of a day. Efficiency we use total revenue as the goal, customer satisfaction, we use the total waiting time to simulate. And using the other three objectives: total order quantity, total loss order quantity and total loss order revenue to cross verify, in order to achieve feasible and robust result.

In terms of parameter setting. First, in the selection of parameters. We choose a wealth of parameters that will affect the results, such as the proficiency of workers, the different rates of online and offline arrival, the value of SKU, and so on. Second, the parameters of our model are all from the observed offline real data and personal rich dining experience, and use the online data for cross validation.

In terms of strategy selection, we creatively put forward the strategy of manual intervention on the proportion of online and offline orders. Based on the proportion of historical data, it dynamically adjusts the order of receiving service orders in the future to ensure the best characteristics of optimization objectives. And this strategy has practical operability.

The results also show that the objective function of our recommendation strategy is improved by more than 10% compared with the basic strategy, which has a very positive impact on the overall development of enterprises.

## Limitation and Future Work


In terms of parameter setting, first of all, the selection of parameter size is based on our observation and actual ordering experience, and cross validation is conducted through online search news / research. However, due to the insufficient sample size, there may be differences between the parameters and the actual situation. Secondly, due to the limitation of operation speed, we have not carried out more parameter simulation and parameter sensitivity analysis, which can be optimized and improved in the future.

In terms of model setting, we simplify the actual situation in reality. For example, for online orders, we set a unified discount price, but in reality, there will be 5 yuan coupons, buy one get one coupon, free shipping coupons and other promotional activities.

In terms of method recommendation, our strategy is that if the online and offline proportion of historical orders does not meet the 𝜃 set by us, we will adjust the number of online and offline services in the future to make it close to 𝜃. In the future, more complex strategies based on different situations can be considered.

