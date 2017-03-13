title: 矩阵分解技巧
date: 2016-02-29 23:49
categories: 在天池打比赛
tags: 数据挖掘
---

前段时间了解了一下协同过滤模型，提到了稀疏性的问题，就来看看《Matrix Factorization Techniques for Recommender Systems》中关于矩阵分解的描述是如何来解决的吧。理论上说应该是潜在语义分析中的主题模型的，具体做法在 2006 年以前已经有了。其中提到两种方法：随机梯度下降法和交替最小二乘法，这两个方法还挺有意思的，如有错误请指正。

# 问题描述

假设大家已经了解协同过滤算法了，也知道评分矩阵是怎么一回事。为了简化描述，首先给出问题描述，为了解决潜在因子分解的问题，我们最终要优化如下表达式：

$$ \\min\_{q^\*, p^\*}\\sum\_{(u,i) \\in K} (r\_{ui}-q\_i^T p\_u)^2 + \\lambda (|q\_i|^2+|p\_u|^2) $$

其中集合 $K$ 表示显式给出的提示的 $(u,i)$ 组合，而 $\\lambda$ 表示正则化参数。
按惯例，所有小写字母只代表一个数值或向量，这里的 $q\_i$  和 $p\_u$  是等维度的向量，其余是数值。

## 随机梯度下降法（SDG）

随机梯度下降法是一种比较简单的解法，具体做法是：

1. 从集合 $K$ 中随机选择某一对 $(u, i)$ ，计算相对误差 $ e\_{ui} = r\_{ui} - q_i^T p_u $
2. 更新两个矩阵：

   $$ q_i \\leftarrow q_i + \\gamma \\cdot (e_ui \\cdot p_u - \\lambda \\cdot q_i ) $$

   $$ p_u \\leftarrow p_u + \\gamma \\cdot (e_ui \\cdot p_u - \\lambda \\cdot p_u ) $$

3. 重复以上过程，最终使得大部分（给出的阈值）的 $e_{ui}=0$ 则结束算法。

## 交替最小二乘法（ALS）

最小二乘……怎么听着这么熟悉？让我们看回原来的优化函数，如果 $q_i^T$  或者 $p_u$  是固定的矩阵，是不是就很熟悉了？那样就是经典的最小二乘法了。可是，$q_i^T$ 和 $p_u$ 都是待优化参数，这样这个问题就不是简单的最小二乘问题了（应该说不是凸优化 convex optimization 问题了）。但是，如果我们每次都固定其中的一项，然后计算另一项，这个问题就迎刃而解了。交替最小二乘法说的就是每次迭代，都交替地优化 $q_i^T$ 和 $p_u$ 使得问题可以以普通的最小二乘法来解。事实上并没有什么黑魔法。

# 整合外部信息

这篇文章另一个有意思的部分是把外部信息引入到矩阵分解算法中。实际上就是修改了优化函数：

$$ \\min\_{p^\*,q^\*,b^\*} \\sum\_{(u,i) \\in K} (r\_{ui} - \\mu - b\_u - b\_i - p\_u^T q\_i )^2 + \\lambda (|p\_u|^2+|q\_i|^2+b\_u^2+b\_i^2) $$

这里的技巧就是把需要的外部信息整合为矩阵，然后加入到优化算法中。

对于外部信息，文章提到：

1. 偏见：用户评分的标准不一，有些用户总爱评高分，有些用户总爱平低分。
2. 隐式反馈：没看的很明白 。。。参见 Collaborative Filtering for Implicit Feedback Datasets
3. 时变：用户对某商品的偏好是随时间而改变的，因此评分和其他变量，例如偏好，都是时间的函数。
4. 置信水平：对这种评分可信度的评价。

# 最后

附上一段 Python 写的用随机梯度下降方法解的矩阵分解算法吧。

```python
def sgd_mf(ratings, p=None, q=None, factors=40, g=1e-2, l=1e-6, s=1.0, max_iters=100):
    """ Stochastic Gradient Descent for Matrix Factorization.

    :param ratings: the ratings matrix.
    :param p: (optional) the P matrix for the first dimension of ratings matrix.
    :param q: (optional) the Q matrix for the second dimension of ratings matrix.
    :param factors: (optional) the number of latent factors.
    :param g: (optional) the learning rate.
    :param l: (optional) the regularized coefficient.
    :param s: (optional) the number of samples that used to calculate the matrix.
    :param max_iters: (optional) the maximum number of iterations.
    :return : (optional) the tuple of (P, Q) matrix.
    """
    rows, cols = ratings.shape
    nz = transpose(nonzero(ratings))
    sn = int(len(nz) * s)
    p = p or random.random_sample((rows, factors)) * 0.1
    q = q or random.random_sample((cols, factors)) * 0.1
    for it in range(max_iters):
        snz = random.choice(len(nz), sn, replace=False)
        for n, (u, i) in enumerate(nz[snz]):
            pu = p[u].copy()
            qi = q[i].copy()
            e = ratings[u, i] - pu @ qi.T
            p[u] = pu + g * (e * qi - l * pu)
            assert not any(isnan(p[u]) | isinf(p[u])), '%d p Nan/inf: %d %d %d %f' % (n, e, u, i, pu @ qi.T)
            q[i] = qi + g * (e * pu - l * qi)
            assert not any(isnan(q[i]) | isinf(q[i])), '%d q Nan/inf: %d %d %d %f' % (n, e, u, i, pu @ qi.T)
    return p, q
```
