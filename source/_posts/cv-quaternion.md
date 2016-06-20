title: 四元组与旋转矩阵
date: 2015-10-06 11:10
categories: 计算机视觉
tags: 
- 计算机视觉
- 点云配准
---

# 二维旋转矩阵（2D Rotation Matrix）

在欧几里得坐标系下，二维的旋转矩阵可以用一个旋转角 $ \theta $ 来表达出来。具体地，

$$ R = \begin{bmatrix} \cos \theta & -\sin \theta \\\\ \sin \theta & \cos \theta \\\\ \end{bmatrix} $$

二维点坐标表示为列向量乘以旋转矩阵，得到的列向量就是在欧几里得坐标系下的旋转后的坐标。

# 三维旋转矩阵（3D Rotation Matrix）

一般地，欧几里得理论下，三维旋转矩阵可以表达为绕着某个方向向量以及绕着这个方向向量的旋转角（默认采用右手原则）。也就是说，确定一个三维旋转矩阵有 4 个变量，方向向量 $x, y, z$ 以及旋转角 $\theta$ 。欧拉旋转指出，三维旋转矩阵的自由度是 3 。

三维旋转矩阵有多种表示方法，主要有 2 种方法：欧拉旋转、四元组。

## 1. 欧拉旋转（Euler Rotation)

欧拉旋转的想法和旋转向量相似。但是不是给定一个旋转向量，而是分别给出观测对象沿$x, y, z$ 三个坐标轴旋转（转化为了一个二维的旋转问题）。其中，沿着给定三个方向的旋转矩阵是这个样子的：

$$  \nonumber \begin{alignat}{1} R_x(\theta) &= \begin{bmatrix} 1 & 0 & 0 \\\\ 0 & \cos \theta & -\sin \theta \\\\ 0 & \sin \theta & \cos \theta \end{bmatrix} , R_y(\theta) &= \begin{bmatrix} \cos \theta & 0 & \sin \theta \\\\ 0 & 1 & 0 \\\\ -\sin \theta & 0 & \cos \theta \\\\ \end{bmatrix} , R_z(\theta) &= \begin{bmatrix} \cos \theta & -\sin \theta & 0 \\\\ \sin \theta & \cos \theta & 0\\\\ 0 & 0 & 1\\\\ \end{bmatrix} \end{alignat} $$

然后，旋转矩阵表示为：

$$ R=R_z R_y R_x $$

这种方法的缺点之一就是复杂，且由于欧拉万向角问题而表示不唯一。

## 2. 四元组（Quaternions）

四元组是扩展自复数的一个概念，延伸自欧拉旋转。定义三个复变量 $i^2=j^2=k^2=-1$ ，然后把向量的各个分量表示为 $i, j, k$ 的系数，即 (2, 3, 4) 表示为 $2i+3j+4k$ 。一个围绕单位向量 $\overrightarrow{u}=(u_x, u_y, u_z)=u_x i + u_y j + u_z k$的旋转$\theta$角度的旋转，可以利用欧拉公式的扩展来表达：

$$ q = e^{\frac{\theta}{2}(u_x i + u_y j + u_z k)} = \cos \frac{\theta}{2} + (u_x i + u_y j + u_z k) \sin \frac{\theta}{2} $$

然后，利用四元组乘法（注意，此处不是矩阵乘法！），上式可以应用于计算一个普通的三维点 $p=(p_x, p_y, p_z) = p_x i + p_y j + p_z k $ 的旋转：

$$ p' = q p q^{-1} $$

而 $p'=({p_x}', {p_y}', {p_z}')$ 是旋转后的坐标。如果 $ \overrightarrow{u} $ 和 点 $p$ 是沿原点同方向的，那么该旋转将绕 $\overrightarrow{u}$ 顺时针旋转 $\theta$。

### 2.1 四元组的矩阵表示

四元组表达的旋转也可以通过旋转矩阵来表示，即简化上述 $$ p' = q p q^{-1} $$ 的操作。其得到的旋转矩阵为：

$$  \begin{bmatrix} c + a_x^2 (1-c) & a_x a_y (1-c) - a_z s & a_x a_z (1-c) + a_y s \\\\ a_y a_x (1-c) + a_z s & c + a_y^2 (1-c) & a_y a_z (1-c) - a_x s \\\\ a_z a_x (1-c) - a_y s & a_z a_y (1-c) + a_x s & c + a_z^2 (1-c) \end{bmatrix} $$

其中，$s=\sin \theta, c = \cos \theta$ 。对于一个旋转四元组 $q=q_r+q_i i + q_j j + q_k k$，以上变量可以通过 

$$ \\begin\{align\} \\theta \& =2 \\arccos q_r=2 \\arcsin \\sqrt{ {q_i}^2+{q_j}^2+{q_k}^2} \\\\ (a_x, a_y, a_z) \& =\\frac{1}{\\sin \\frac\{1\}\{2\} \\theta} (q_i, q_j, q_k) \\end\{align\} $$

得到。

如果直接从四元组中的变量出发，也可以把矩阵表达为：

$$  \begin{bmatrix} 1 - 2 q_j^2 - 2 q_k^2 & 2 (q_i q_j - q_k q_r) & 2 (q_i q_k + q_j q_r) \\\\ 2 (q_i q_j + q_k q_r) & 1 - 2 q_i^2 - 2 q_k^2 & 2 (q_j q_k - q_i q_r) \\\\ 2 (q_i q_k - q_j q_r) & 2 (q_j q_k + q_i q_r) & 1 - 2 q_i^2 - 2 q_j^2 \end{bmatrix}  $$

或（已知 $q_r$，可以通过变换式代换主轴线上的量）

$$  \begin{bmatrix} q_r^2 + q_i^2 -  q_j^2 -  q_k^2 & 2 (q_i q_j - q_k q_r) & 2 (q_i q_k + q_j q_r) \\\\ 2 (q_i q_j + q_k q_r) & q_r^2 + q_j^2 -  q_i^2 -  q_k^2 & 2 (q_j q_k - q_i q_r) \\\\ 2 (q_i q_k - q_j q_r) & 2 (q_j q_k + q_i q_r) & q_r^2 + q_k^2 - q_i^2 - q_j^2 \end{bmatrix}  $$

上述两个矩阵是等价的。

以上旋转默认物体绕着原点的旋转，其他形式的旋转，可以把物体平移到相对坐标系，再做四元组旋转，然后再把坐标系变换回去。 

### 2.2 四元组的矩阵恢复

从旋转矩阵恢复四元组可以通过构造矩阵求特征值为 1 的 特征向量（即四元组）。设 $Q$ 是一个 $3\times 3$ 的旋转矩阵，构造矩阵：

$$  K = \frac13 \begin{bmatrix} Q_{xx}-Q_{yy}-Q_{zz} & Q_{yx}+Q_{xy} & Q_{zx}+Q_{xz} & Q_{yz}-Q_{zy} \\\\ Q_{yx}+Q_{xy} & Q_{yy}-Q_{xx}-Q_{zz} & Q_{zy}+Q_{yz} & Q_{zx}-Q_{xz} \\\\ Q_{zx}+Q_{xz} & Q_{zy}+Q_{yz} & Q_{zz}-Q_{xx}-Q_{yy} & Q_{xy}-Q_{yx} \\\\ Q_{yz}-Q_{zy} & Q_{zx}-Q_{xz} & Q_{xy}-Q_{yx} & Q_{xx}+Q_{yy}+Q_{zz} \end{bmatrix}  $$

如果 $Q$ 是一个纯旋转矩阵，那么$ K $ 将会有一个特征值为 1 的特征向量，该向量即四元组。如果 $Q$ 不是一个纯旋转矩阵，那么我们求出最大的特征值所对应的向量为四元组，该四元组求得的旋转矩阵将接近$Q$。
