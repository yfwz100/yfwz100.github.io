---
title: Gradient Boosting 学习笔记
tags:
  - 机器学习
date: 2017-05-14 23:45:48
---

也来学习一下近来比较火的 Gradient Boosting 算法，最近数据比赛里较热门的 xgboost 、 lightGBM、 GBM 都是基于 Grandient Boosting 的思路。 Gradient Boosting 集合了 Boosting 和 Bagging 的思想，其结果泛化性能较好，并且由决策树本身的性质决定了并不需要过多干预特征筛选，这些特性使得它在比赛中有较广泛的用途。

<!-- more -->

GBDT 的一个重要关键是所谓的 Boosting，那么什么是 Boosting ？

> 💡 什么是 Boosting ？ 
>
> 简单地说，Boosting 算法就是通过不断地累积弱分类器的预测最终成为一个强分类器。如何理解使用弱分类器的目的呢？一个直观的理解，弱分类器往往发现的是事物的趋势，而不是具体到事物的本质（往往也没有这个能力），在积累了各种分类器从不同角度对趋势的理解，叠加以后，分类器的分类结果将会加深对趋势的理解；而如果一开始用强分类器，强分类器往往把握的是具体的特征，而且往往是用贪心算法（参考决策树学习）进行局部最优估计，因而很容易过拟合，而如果多个强分类器集中在一起，反而把过拟合现象进行加深，从而学习出过拟合的数据。
> 
> 一个可视化参考：http://www.r-bloggers.com/an-attempt-to-understand-boosting-algorithms/ 

GDBT 的一般算法流程：

1. 初始化基础模型 $F_0(x) = \underset{\gamma}{\arg\min} \sum_{i=1}^n L(y_i, \gamma)$
2. 迭代 $m \in (1, M)$
   1. 计算伪梯度 $r_{im} = -\left[\frac{\partial L(y_i, F(x_i))}{\partial F(x_i)}\right]_{F(x)=F_{m-1}(x)} \quad \mbox{for } i=1,\ldots,n$
   2. 以伪梯度为类标，训练基础模型 $h_m(x)$
   3. 计算模型权重 $\gamma_m = \underset{\gamma}{\arg\min} \sum_{i=1}^n L\left(y_i, F_{m-1}(x_i) + \gamma h_m(x_i)\right)$
   4. 更新模型： $F_m(x) = F_{m-1}(x) + \gamma_m h_m(x)$
3. 得到最终模型 $F_m(x)$

其中步骤 2 的第 4 小步，计算模型权重采用的是一维模型，更恰当地，应该采用区域模型（决策树对特征向量的预测实际上是就是对特征空间进行划分）：

$$F_m(x) = F_{m-1}(x) + \sum_{j=1}^J \gamma_{jm} I(x \in R_{jm}), \quad\gamma_{jm} = \underset{\gamma}{\arg\min} \sum_{x_i \in R_{jm}} L(y_i, F_{m-1}(x_i) + \gamma h_m(x_i))$$

但这样做无疑增加了计算量。为了简化操作，很多实现，例如 Spark MLlib 的 GradientBoostTree 中，模型参数 $\gamma_m$ 被规定为 1 ，这个并不没有简化学习率。

## 损失函数

统计学习里提到的一个关键此时损失函数（Loss Function），这也是贯穿机器学习算法的一个思想，因此，GBDT 也可以从这个角度来解释。上文介绍到的 $L(y_i, \gamma)$ 实际上就是损失函数的统称。

阿里巴巴机器学习平台里对 GBDT 分类器作出了两种不同的节点：“GBDT 二分类”节点和“GBDT回归与排序”。“GBDT二分类”节点和"GBDT回归与排序”节点实际上都可以处理分类问题，区别就在于其中的损失函数的计算。据文档介绍“GBDT二分类”节点实际上是GBDT-LR即带有 Logistic Regression Loss 损失函数的 GBDT 。而“GBDT回归与排序”节点则是采用普通的均方误差（MSE）损失函数。使用均方误差的函数实际上就是正常的 Gradient Boosting 方法，而不同在于，御膳房算法平台的 GBDT-LR 是经过 Logistic 函数改造的。

Gradient Boosting 方法是对损失函数的梯度的逐步学习（迭代），那么损失函数的梯度就决定了算法最终的收敛方向了。而 Gradient Boosting 方法对学习器的要求不高，因此基础构建的学习器错误率肯定很高的，而 Logistic 回归函数（即 sigmoid 曲线）表达式为 $ f(x) = \frac{1}{1+e^-x} $ ，其目的是把 $(-\infty, +\infty)$ 映射到 $(0, 1)$ ；而一个副作用是，尽可能地使每一个数值向极端值（0或1）靠近。如果选择这类损失函数，那么将有两个结果：使“靠近 1 的更靠近 1 ”或“靠近 0 的更靠近 0”，即加快了迭代收敛；也可能使“本来是 1 的更靠近 0”或“本来是 0 的更靠近 1”，即偏离了估计，使迭代更难收敛。如果每次分类器的分类效果不错，看起来能够加速收敛过程，提高算法效率。

## 其他参数

学习率（Learning Rate） $F_m(x) = F_{m-1}(x) + \nu \cdot \gamma_m h_m(x), \quad 0 < \nu \leq 1$ ，实践中越小的学习率分类预测效果越好。但是也要防止遇到鞍点，即拟合遇到局部最小值。

关于训练数据选择，随机梯度提升（Stochastic Gradient Boosting），受 Bagging 思想启发，每次训练时不直接用全局数据，而是对数据进行抽样，每次只选择一部分数据进行训练。