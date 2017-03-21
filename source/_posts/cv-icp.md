---
title: ICP 算法过程
date: 2015-12-30 11:10
categories: 计算机视觉
tags: 
- 计算机视觉
- 点云配准
---

以下为读《[A Method for Registration of 3D Shape](http://xueshu.baidu.com/s?wd=paperuri%3A%289d45801efcd5be3894347f9dfecc88f3%29&filter=sc_long_sign&sc_ks_para=q%3DMethod%20for%20registration%20of%203-D%20shapes&tn=SE_baiduxueshu_c1gjeupa&ie=utf-8)》论文笔记。

<!-- more -->

# ICP 整体框架

定义点到点集的距离为点到点集的点的最短距离：

$$ d(\vec{p}, X)=\min_{\vec{x} \in X}\left \| \vec{x} - \vec{p} \right \| $$

那么点的对应点定义为

$$ d(\vec{p}, X)=\arg \min_{\vec{x} \in X}\left \| \vec{x} - \vec{p} \right \| $$

定义过程为求所有的在点集上的对应点的集合（通过上式给出）。
定义旋转过程（由下文给出）为：

$$ (\vec{q}, d) = Q (P, Y) $$

其中 $Y = C(P, X)$。

算法描述如下：

1. 取测量点集 $P$ 和模型点集 $X$，令 $\vec{p}\in P$，$\vec{x}\in X$，且 $N_p=\left \| P \right \|$，$N_x=\left \| X \right \|$；
2. 初始化初始点集为测量点集 $P_0=P$，初始化变换向量 $\vec{q}=[1,0,0,0,0,0]$，即旋转为 0，且各方向位移为 0，初始化迭代次数 $k=0$，执行以下几个步骤直到收敛：

   1. 计算最近点集：$Y_k=C(P_k, X)$
   2. 计算配准：$(\vec{q}_k,d)=Q(P_0, Y_k)$
   3. 应用配准：$P_{k+1}=\vec{q}_k (P_0)$
   4. 终止迭代过程：两次误差小于一个给定阈值 $\tau>0$ 使 $d_k-d_{k+1}<\tau$

如果希望用一个无维度的阈值，可以把$\tau$替换为$\tau\sqrt{tr(\Sigma_x)}$，其中模型的协方差矩阵的迹基本上和模型点的个数相等。

# 求点集间变换矩阵

设单位四元组 $\vec{q}_R=[q_0,q_1,q_2,q_3]^T$ ，其中 $q_0>0, q_0^2+q_1^2+q_2^2+q_3^2+q_4^2=1$

有四元组到旋转矩阵的变换来说，旋转矩阵可以表示为：

$$ R(\vec{q}_R)=\begin{bmatrix}
(q_0^2+q_1^2-q_2^2-q_3^2 & 2(q_1 q_2-q_0 q_3 ) & (q_1 q_3+q_0 q_2 ) \\
2(q_1 q_2+q_0 q_3 )  & q_0^2+q_2^2-q_1^2-q_3^2  & 2(q_2 q_3-q_0 q_1 ) \\
2(q_1 q_3-q_0 q_2 )  & 2(q_2 q_3+q_0 q_1 ) & q_0^2+q_3^2-q_1^2-q_2^2 )
 \end{bmatrix} $$

令位移向量为 $\vec{q}_T=[q_4,q_5,q_6]^T$

完整的配准状态向量表示为 $\vec{q}=[\vec{q}_R | \vec{q}_T]$

令测量点集为$P=\{\vec{p}\}$，模型点集为 $X=\{\vec{x}\}$，并且点数目 $N_p$。目标是求使 $P$ 靠拢（变换）到 $X$ 的坐标系下，设目标函数为

$$ f(\vec{q})=\frac{1}{N_p} \sum_{i=1}^{N_p} \left \| \vec{x}_i-R(\vec{q}_R ) \vec{p}_i-\vec{q}_T \right \|^2 $$   

设点集 $P$ 的质心为

$$\vec{\mu}_p=\frac{1}{N_p} \sum_{i=1}^{N_p} \vec{p}$$

点集 $X$ 的质心为

$$\vec{\mu}_x=\frac{1}{N_x} \sum_{i=1}^{N_x} \vec{x}$$

设点集和的协方差矩阵为

$$ \Sigma_{px}=\frac{1}{N_p} \sum_{i=1}^{N_x} \left [ (\vec{p}_i-\vec{\mu}_p)(\vec{x}_i-\vec{\mu}_x)^T \right]=\frac{1}{N_p} \sum_{i=1}^{N_x} \left [ \vec{p}_i \cdot \vec{x}_i^T - \vec{\mu}_p \vec{\mu}_x^T \right ] $$

设反对称矩阵

$$ A_{ij} = \left ( \Sigma_{px} - \Sigma_{px}^T \right )_{ij} $$

取其循环部分组成列向量

$$ \Delta = [A_{23}, A_{31}, A_{12}]^T $$

使得

$$ Q(\Sigma_{px}) = \begin{bmatrix}
tr(\Sigma_{px}) & \Delta^T \\
\Delta & \Sigma_{px}-\Sigma_{px}^T-tr(\Sigma_{px}) I_3
\end{bmatrix} $$

其中 $I_3$ 是单位矩阵。取矩阵 $Q(\Sigma_{px})$ 最大的特征向量对应的单位特征向量 $\vec{q}_R=[q_0, q_1, q_2, q_3]^T$ 为最优旋转。

最优位移向量为

$$ \vec{q}_T = \vec{\mu}_x - R(\vec{q}_R) \vec{\mu}_p $$

这个用最小二乘法解四元组的方法记为

$$ (\vec{q}, d_{ms}) = Q(P, X) $$

而 $d_{ms}$ 为配对的均方误差（见目标函数）。另外 $\vec{q}(P)$ 被记为经过配准量 $\vec{q}$ 的点集。
