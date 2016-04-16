Title: 频繁集挖掘的算法
Date: 2014-04-21 23:20
Category: 数据挖掘
Tags: 频繁项集挖掘
Slug: articles/datamining/freqpattern/apriori
Author: yfwz100
Summary: 介绍频繁序列挖掘算法 Apriori。

<p>不知道是我还不习惯面向接口的编码风格，还是我被面向接口的编码风格束缚了，<a href="http://z-north.diandian.com/post/fp-growth" title="频繁集的 FP-Growth 算法">FP-Growth 算法</a>竟然调了一个下午。好了，用这篇文章回顾一下吧。</p><h3>问题概览</h3><p>频繁集挖掘（Frequent Pattern Mining）应该算是数据挖掘里面比较基础的问题了，讨论的是如何从一些频繁发生的事件中寻找关联。如果一件事频繁发生，那么肯定是有理由的。两件事都频繁发生，那么它们的关联就越大。真有这样的事情吗？历史上是有的，很多实验也证明了，而且我们切实感受到过，著名的例子包括传说中的“啤酒尿布”的营销故事，具体可以移步 [wikipedia 中对购物篮分析的解释][4] 。</p><p>那么，我们可以从一些事件集合（一般称为 Itemset）中寻找这样同时发生的事件（Item），然后按照某种规范计算它们的关联程度。为了得到频繁集的“频繁”的理由，我们可以人为地规定一个阈值，只有超过这样的阈值的，才称之为“频繁集”。</p><p>更数学的表达方式就不重复了，有兴趣可以看看文献 <a href="http://wwwqbic.almaden.ibm.com/cs/projects/iis/hdb/Publications/papers/vldb95_tax_rj.pdf" title="Agrawal, Rakesh, and Ramakrishnan Srikant. ">1</a> 。不过这里需要提到的是，有三件事同时发生的话，其中两两又可以组成事件集合，那么这些集合是否也算是频繁集呢？一般来说，是的，根据经验，三件事同时发生的可能性要比两件事同时发生的概率低。因此，在频繁集挖掘里，我们还需要考虑三件事同时发生是支持其中两件事两两相互发生的。</p><h3>算法实现</h3><p>嗯，看了问题概览以后，觉得好像频繁集也不复杂，不就是一个计数器吗？和通常做的单词计数器有吗，就是把单词变成了一个事件而已，事实上单词确实也可以表示为一个事件。我就做一个 HashMap 作为计数的容器吧，遇到一个单词（事件），我就看这个 Map 里面有没有这个单词，有的话，为它的 value 增加 1 ，没有的话，新建一个，对应 value 设置为 1 。</p><p>但是，我们预先不知道有多少个事件将会同时发生，要生成一个 n 个事件同时发生的集合，那么，将要生成 2^n 个不同组合的事件集。想想我们用 Map 来计数的时候，遇到一个 n 个事件（就是 n 个单词了）同时发生的集合呢？为了便于统计，我们必须把这个集合中单词的所有可能组合都保存到 Map 中，也就是有 2^n 个了。从时间或空间上都要造成很大的浪费，想想指数函数的增长有多快就知道了。</p><h4>Apriori 算法</h4><p>R. Argrawal. 等人首先提出了 <a href="http://en.wikipedia.org/wiki/Market_basket_analysis" title="Affinity analysis">Apriori</a> 算法，这是一个很经典的算法，以至于快 20 年过去了，数据挖掘的书上还不得不提。该算法可以按照 itemset 的长度分层生成 itemset ，根据著名的 Apriori 属性：频繁集的所有子集都必须是频繁的。该命题的逆反命题是存在一个子集非频繁，那么这个集合不可能频繁，即频繁集只可能从短的集合中产生，于是，Apriori 就从第一层（频繁项）开始，逐层生成候选集，然后遍历数据库进行测试，删除非频繁项，又从该层的频繁集中构建更长的频繁候选集，以此递归。</p><p>以上算法可以用下面的逻辑复述一下：</p><ol class="edui-filter-decimal"><li><p>获取频繁项。在这个阶段，数据库中所有序列的每一项被频繁集过滤，保留频繁的项而删除非频繁的项。</p></li><li><p>生成候选集。在这个阶段，基于Apriori条件，通过连接（join）的方式，把k-1集合组合为k集合生成候选项。</p></li><li><p>计数并删减。通过数据库遍历，为前一阶段的候选集进行计数。最后计数的结果经过过滤，删除不合要求的集合。</p></li><li><p>递归以上过程，直到没有候选集可以被生成。</p></li></ol><p>参考代码：</p>

```java
cycle = 0;
database.forEach(transaction -&gt; {  
  transaction.getItemset().forEach(item -&gt; {
    root.getOrCreate(item).incrementCount();
  });
});
pruneCandidates(root, 0);
do {
  cycle++;
  remaining = 0;
  generateCandidates(root, 0);
  countCandidates();
  pruneCandidates(root, 0);
} while (!isDone());
```

这个算法用候选集的方法很好地避免了空间浪费的问题，但是，由于要多次访问数据库，要造成大量的 IO 操作，从而拖慢整个挖掘过程（不过实际上这种方法已经很快了，论文标题就写是一个快速方法，不过，科学无止境嘛）。

当然了，既然知道缺点了，改进是少不了的，下篇文章再介绍另一个经典的算法：[频繁集的 FP-Growth 算法](fp-growth)。
