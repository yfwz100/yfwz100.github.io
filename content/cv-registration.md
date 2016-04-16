Title: 点云配准问题
Date: 2015-11-30 11:10
Category: 计算机视觉
Tags: 计算机视觉, 点云配准
Slug: articles/cv/registration
Author: yfwz100
Summary: 点云配准问题描述。

接触配准问题有一段时间了，但是由于缺少一些最优化的初始知识，入门还是比较慢（为什么学院不开这门课 = =）。点云（点的集合）配准问题在最原始的定义下就是一个函数优化的问题，可以表述为：给定两幅由不同变换得到的同一场景（或近似同一场景）下的点云，求出两幅点云之间的相对变换。

形式化地，给定点云 $p_i\\in P$，以及 $p_i^′\\in P^′$  且 $p_i^′\\approx R \\cdot p_i + t$，求函数 $f_R (P, P^′)=R$ 以及 $f_t (P, P^′)=t$ 并且满足 $p_i=f_R (P, P^′ ) \\cdot p_i^′  + f_t (P,P^′)$ ，即优化

$$\\min_{R,t} \\frac{1}{N} \\sum_i^N \\sqrt{(s_i-t-R \\cdot t_i)^2}$$

解出 $R$ 以及 $t$ 。

其中比较有名的算法是迭代临近点算法（Iteractive Closest Points, 简称 ICP），主要思想是1992年发表的论文《A Method for Registration of 3D Shape》[1]。这篇论文的核心就在于揭示点云配准的函数优化问题。并利用迭代方法求出两幅点云的旋转矩阵 R 以及平移向量 t 。因此，因为如果把点云配准视为优化问题，那么可以通过通用函数求解器来求出最优解。因此，点云配准问题根据所用的算法不同，演化出非线性搜索（non-linear search）、 LM 优化方法等；根据点云预处理方法的不同，演化出点线匹配、正态分布变换等方法。

通过 ICP 算法文章的启发，针对点云配准问题的研究集中于以下方面：
1. 对点云的预处理方法的研究（特征提取）
   1. 特征点提取：提取点、线、面特征，法向量特征，颜色特征
   2. 高斯混合模型 [2]
2. 点匹配算法的研究（对应点选择）
   1. 双向对应（互相对应）
   2. 近似对应点
   3. 拒绝离群点
3. 点云配准问题中优化目标的研究
   1. 限制点云配准目标函数中旋转矩阵的向量
   2. 惩罚参数矩阵的大小
4. 对函数优化方法的研究
   1. SVD 方法
   2. 非线性搜索方法（Non-linear search）
   3. LM 优化（Levenberg-Marquardt Optimization）

如果看过一些文献，实际上特征提取的方法就是某一类特殊的聚类方法（聚类成为有几何意义的数据特征），特别是高斯混合模型，就是图像算法里很常见的。

最『原始』的文献很难找得到了，就列一下提及上述方法的一些文献吧：

1. Besl P, Mckay H. A method for registration of 3-D shapes[J]. IEEE Transactions on Pattern Analysis and Machine Intelligence, 1992, 14(2): 239-256.
2. Bing J, Vemuri B C. Robust Point Set Registration Using Gaussian Mixture Models.[J]. IEEE Transactions on Pattern Analysis & Machine Intelligence, 2011, 33(8):1633-1645.
3. Point Cloud Library. http://www.pointclouds.org
