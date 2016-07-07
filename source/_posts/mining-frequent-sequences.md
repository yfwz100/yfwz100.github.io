---
title: 挖掘频繁序列的非正式调研
tags:
  - 数据挖掘
  - 频繁模式挖掘
date: 2016-07-07 15:15:03
---


频繁序列挖掘（sequential pattern mining）是数据挖掘里的热门话题之一，它的目标是挖掘数据里潜在的有价值的时间序列关系。频繁序列挖掘与时间序列挖掘相似，但不同的是频繁序列挖掘一般假设挖掘的项目是离散的，因而和时间序列的连续数据分列为两个不同的话题。由于频繁序列挖掘是从半结构化的序列中挖掘有价值的序列，也被归为结构化数据挖掘（structured data mining）的范畴。

<!-- more -->

频繁序列挖掘是从频繁项集（frequent pattern mining）(可以参考之前的[博文](/tags/频繁项集挖掘))、关联规则（association rule）挖掘中引申出来的。频繁项集挖掘关注的模式是项目（itemset）的共现性（co-ocurrence）；而关联规则关注的模式是从频繁项集中提取有意思的项集推导模式，例如 Itemset A → Itemset B。频繁序列挖掘则是从关联规则的基础上，根据项集发生的先后关系，推导项集之间的时间发展关系。

频繁序列挖掘根据数据中的项目单位，可以分为频繁项集序列挖掘和字符串序列挖掘。其中频繁项集序列即在关联规则的基础上添加时序得出项目集之间在时间先后上的推导关系，而字符串挖掘则是项目集挖掘的一化版本。每个项集只有一个项目，可以用一个字符来表示。在频繁项集序列挖掘中，可以通过映射到单实体的方法把项集当作一个单一的实体来处理，退化为字符串挖掘。

根据比较早的高引用文献来看，频繁项集相关的挖掘已经发展了至少 25 年历史了。接触这个话题是在实习的时候，需要实现频繁项集、频繁序列挖掘算法，所以最开始主要关注算法性能的改进。至今频繁模式挖掘的性能改进仍然是热门的话题之一。因为列举所有的频繁序列，是一个排列组合问题。暴力算法穷举整个搜索空间需要 O(n!) 的复杂度。为了降低算法的复杂度，研究社区陆续提出了 Apriori、SPADE、FreeSpan、PrefixSpan 之类的算法。对于序列挖掘，也扩展出了 GSP（基于 Apriori）、PrefixSpan（基于 FP-Growth）等。

分层挖掘的 Apriori 系算法：

> 1. 根据时间整理项集序列，得到 <uid, <itemsets...>> 形式；
> 2. 找出频繁 1 序列，并展开项集，然后为所有项（集）映射一个编号，例如 (1, 2) 会被拆分为 (1), (2), (1, 2) 映射为 3 个单独的项目，最后删除支持度低于阈值的非频繁的项目；
> 3. 对原始数据进行转化，把所有序列里的项集替换为第 2 步中抽取的项目，如果序列里包含删除的非频繁项目，则删除该交易；
> 4. 从上一层生成的 k 序列生成候选的 k+1 序列，然后遍历数据库，确定候选的 k+1 序列是否频繁，并**重复这个过程，直到 k+1 层候选序列中不存在频繁序列**；
> 5. 删除不需要的子序列，例如 a→b→c 包含的 a→b 和 a→c 都被删除，保留最长的序列 a→b→c 。
>
> _Agrawal R, Srikant R. Mining sequential patterns[C]// icde. IEEE Computer Society, 1995:3-14._

利用前缀递归的 PrefixSpan 算法：

> 1. 统计 1-序列 ，删除支持度小于阈值的非频繁项；
> 2. 利用 1-序列 按照如下规则生成投影数据库（后缀数据库）：
>    1. 对于每一个 1'-序列 元素，找到序列数据库中包含它自己以及频率比它高的元素的序列；
>    2. 对于每个元素生成的投影数据库，重复 FreeSpan 中的过程，直到投影数据库为空。
> 3. 在生成投影数据库过程中，投影数据库前缀加上投影数据库中的频繁项组成频繁序列。
>
> _Pei J, Han J, Mortazaviasl B, et al. PrefixSpan: Mining Sequential Patterns Efficiently by Prefix-Projected Pattern Growth[C]// International Conference on Data Engineering. IEEE Computer Society, 2001:215-224._

到 PrefixSpan 以后，基本上没出现更高效的算法了。现行序列挖掘的算法，基本上都是这两类算法的变形，例如挖掘长序列的 CloSpan 算法。而 PrefixSpan 至今仍然是较流行的算法。

除了对算法本身的研究，在应用方面，序列模式挖掘也十分多。一些显而易见的模式，例如吃饭用筷子、买了一本书的下册很可能买上册，挖掘起来其实用处不大；一些偶然共现，由于两本热门的书在同一时期卖而成了一种模式，意义也不大。另外，对于不同的人来说，挖掘的意义也可能不一样。这个时候，从发掘模式的“频繁”引向发现“有趣”。

对模式中的 Item 加入分类（taxonomy）的限制：

> 可以扩展使生成的模式不包含相同类型的模式或者包含更抽象的“上级”概念的模式。这种模式主要应用于有关联的特征之间的模式挖掘。例如，挖掘地理位置和时间的关系，那么时间和时间之间的关联是不必要的，因此不需要挖掘这类型的模式。又例如商品之间的关联，苹果和李子都是水果，可以挖掘它们上级“水果”概念和其他概念的关联关系。
>
> 参考：_Srikant R, Agrawal R. Mining sequential patterns: Generalizations and performance improvements[M]// Advances in Database Technology — EDBT '96. Springer Berlin Heidelberg, 1996:1-17._

为项目加入效用（utility）：

> 如果我们把模式挖掘看做一个搜索问题，从一大堆模式中发现我们感兴趣的模式。由于信息过载，我们可能关注有限的模式，因此，每种模式都应该有一个权重，使得重要的模式被我们所了解。这里的权值称为效用（utility），标示这个模式有多大可能是有趣的。对于不同的场景来说，这种方法可以有不同的应用。
>
> 参考：_Ahmed C F. A Novel Approach for Mining High-Utility Sequential Patterns in Sequence Databases[J]. Etri Journal, 2010, 32(5):676-686._

通过用户的反馈进行学习：

> 在效用的基础上，考虑到每个人给予模式的重要程度是不一样的，那么如何判别用户的兴趣点，从而在频繁模式中挖掘相关的兴趣，也是一个很有趣的话题。为此，需要利用用户的初始兴趣分布。那么如何得到初始兴趣分布估计呢？一种方法是利用用户的反馈进行拟合……
>
> 参考：_Xin D, Shen X, Mei Q, et al. Discovering interesting patterns through user's interactive feedback[C]// ACM SIGKDD International Conference on Knowledge Discovery and Data Mining. ACM, 2006:773--778._

从相反的角度看，挖掘“稀有”模式：

> 所谓“稀有”模式指的是出现次数低于某一个阈值的模式（rare patterns、infrequent pattern 或者 non frequent pattern）。在一些场合下，例如一些流程工业上，很多模式往往是出现度很高的，反而有些异常情况偶然出现，而这些异常情况可能导致巨大的经济损失。
>
> 但“稀有”也不仅仅定义于低于某个阈值，毕竟低于某个阈值的模式也太多了。例如对于KDD大会，对于新手来说，对会议上的热门主题感兴趣，但专家可能会对新兴的话题感兴趣。因此，“稀有”模式还和用户的先验知识有关。
>
> 参考：
> 1. _Li H, Laurent A, Poncelet P. Towards Unexpected Sequential Patterns[J]. Atelier Bases De Donn茅es Inductives Plateforme Afia, 2008._
> 2. _Jaroszewicz S, Scheffer T. Fast discovery of unexpected patterns in data, relative to a Bayesian network[C]// 2005:118-127._

对于大部分实际应用来说，当然少不了对序列进行预处理了，然而这些和影响结合相对紧密的方面，好像还没有什么正式的 paper，一般就是从两方面：降噪和删除已知无用组合，或者对序列进行删减。
