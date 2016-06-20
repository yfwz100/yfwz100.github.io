title: 频繁集算法：ECLAT
date: 2014-05-06 21:24
categories: 数据挖掘
tags: 频繁项集挖掘
---

<p>接着<a href="http://z-north.diandian.com/post/frequent-itemset-intro" title="频繁集的算法">频繁集算法</a>的话题。FP-Growth 在这几天实验里还是最快的，几乎是一个极限了。不过这次来看一个比较特别的算法 <a href="http://www.cs.rpi.edu/~zaki/PaperDir/TKDE00.pdf" title="ECLAT 算法">ECLAT</a> ：利用“垂直数据库”（vertical database）进行频繁集的挖掘。</p><p>这里所指的垂直数据库实际上是一种类似数据库理论里面的正规化（normalization）过程，把原来横向的数据库纵向分割存储。用例子说吧，一般来说，之前频繁集中所用的数据库都是像如下形式的：</p>

tid | item
----|------
1   | A,B
2   | B,C
3   | A,C
4   | A,B,C

<p>而“垂直数据库”（vertical database）则把上述数据库表示如下：</p>

item | tids
-----|------
A    | 1,3,4
B    | 1,2,4
C    | 2,3,4

<p>注意到，一行数据由原来的 tid -&gt; items 的形式变成了 item -&gt; tids 的形式，就像把原来的数据库旋转 90 度一样，因此称为“垂直数据库”。</p><p>在挖掘算法上，<a href="http://www.cs.rpi.edu/~zaki/PaperDir/TKDE00.pdf" title="ECLAT 算法">ECLAT</a> 算法实际上并没有脱离 <a href="http://z-north.diandian.com/post/frequent-itemset-intro" title="频繁集的算法">Apriori</a> 算法的影子，也是根据著名的 Apriori 属性进行逐层生成的（混合模式的表现似乎不是很好，有兴趣可以参看<a href="http://www.cs.rpi.edu/~zaki/PaperDir/TKDE00.pdf" title="ECLAT 算法">原文</a>中关于搜索空间的部分）。</p><p>那么，这种表达方式对于算法上有什么优势吗？这个转换可以从两方面带来好处：</p><ol class="edui-filter-decimal"><li><p>一方面是支持度计算上的简化：使用垂直数据库后，要判断 {A,B} 是否具有足够支持可以直接通过对 A 的 tidset 以及 B 的 tidset 进行类似 SQL 里的联合（join）操作，即计算它们重合的 tid 的个数，即是 {A, B} 的支持度计数。</p>

<p>另外，要判断 {A, B, C} 的支持度，我们可以通过 {A, B} 和 {A, C} 的 tidset 联合（join）即可。可以参考 <a href="http://z-north.diandian.com/post/frequent-pattern-lattice" title="频繁集与偏序集、格">3</a>，实际上，定义了子集（subset）运算以后，由 {A, B, C} 组成的所有组合就可以称为“格”（lattice），并且符合“布尔格”（Boolean lattice）特征：

$$ A \cup (B \cap C) = (A \cup B) \cap (A \cup C) $$ 。</p>
</li>
<li><p>我们可以把每一项独立地保存起来而且能够随时访问。例如，如果需要判断 A 和 Z 是否可能组合在一起，可以分别取出 A 和 Z 的 tidset 相联合（join），即支持随机判断。</p></li></ol><p>这个算法的这个特性使得它和其他的算法都不太一样。对于快速支持度判断，有人还提出了 bitmap 方法（即 SPAM 算法），使得垂直数据库更易于比对。不过，根据实现的 ECLAT 方法对比 FP-Growth 算法还是有很大的差距（FP-Growth 在 <a href="http://fimi.ua.ac.be/data/" title="频繁集测试数据库">T10I4D100K</a> 数据库中的速度是 ECLAT 的方法的 2 倍）。
