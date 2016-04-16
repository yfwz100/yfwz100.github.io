Title: 2016 微软实习生笔试
Date: 2016-04-07 23:10
Category: 找工作
Tags: 笔试, OJ
Slug: articles/interv/microsoft-2016
Author: yfwz100
Summary: 微软的笔试情况

难度：★★★★

微软 4 月校招实习生笔试在昨天结束了，简单总结一下，~~感觉难度不算很~~ ，对细节要求比较多、和产品（应用）结合的题目比较多。

题目地址：[mstest2016april1](http://hihocoder.com/contest/mstest2016april1/problems)

共四题。

# Font Size

第一题是一个最佳字体的问题，可以想象是 Word 等文本处理、阅读器用于适配屏幕时候采用的最佳匹配算法。我把这个题目处理为一个优化问题：设定优化目标、选定初始值、误差最小化迭代。目标函数如下：

$$ \\sum\_{i=0}^N \\left \\lceil a\_i / \\left \\lfloor \\frac{S}{W} \\right \\rfloor \\right \\rceil \\leq \\left \\lfloor \\frac{H}{S} \\right \\rfloor \\cdot P$$

初值的选取根据：

$$ S\_{max} =  \\min \\left (W, H, \\left \\lceil \\frac{P \\cdot H}{N}  \\right \\rceil \\right )$$

这个是 S 的最大值了。由于 S 是一个整数，不断递减达到目标函数即可。

# 403 Forbidden

这道题基本上就是解释防火墙规则，如果熟悉网络配置的话，应该很快能够做出来。难点有两个：

1. IP 地址转换成二进制，并进行截位匹配；
2. 字符串的快速前缀搜索（前缀树？）。

# Demo day

第三题往后都没有完整做出来了。这道题的关键是找出最小的障碍物数目，这个数目并不那么直观可以得到。只要确定了一个地图和障碍物的分布，机器人走出这个地方只有一种可能，于是就想了个回溯的方法，当然，时间复杂度估计会很高。暂时还没有很好的方法……

> Update: 被提示了一下 DP，就想到递推方程了，我感觉只要涉及方格、最小等字样的题目，可以直接联想递推方程。从结果倒推，要达到这个方格，只有两种可能，从上方往下，或者从左方往右。于是，这个方程可以设定为：
>
> $$
f(x,y,k) = \\begin{cases}
 \\min ( f(x-1,y,k), f(x,y-1, \\texttt{down}) + c(x, y+1) ) + b(x, y), k=\\texttt{right} \\\\
 \\min ( f(x,y-1,k), f(x-1,y, \\texttt{right}) + c(x+1, y) ) + b(x, y), k=\\texttt{down}
\\end{cases}
$$
>
> 其中 $c(x,y)$ 表示此处是否需要增加一个 block 才能通行；而 $b(x, y)$ 表示此处是否已经有一个 block 。
>
>剩下的事情就是遍历格子了……

# Building in Sandbox

第一反应是 MineCraft 游戏……然后发现确实是相关的。简单地说，就是模拟玩家进行城堡的建设，给定摆放砖块的坐标序列，要满足两个条件：

1. 相邻性：砖块和其他砖块相邻，或者直接放在地上（z 坐标为 1）；
2. 可达性：可以从外面进入城堡放置砖块。

实际上都和邻域搜索相关。做过计算机视觉的人，可能第一反应就是 FLANN 了。可达性的判断可能稍微麻烦一点。一个想法是从选定目标节点走出到最外围的城墙，如果可以走出去，就是可达的。
