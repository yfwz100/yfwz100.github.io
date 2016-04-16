Title: 在 ODPS SQL 上使用自定义函数（UDF）
Date: 2015-11-08 12:19
Category: 在天池打比赛
Tags: 数据挖掘
Slug: articles/tianchi/odps-udf
Author: yfwz100
Summary: 纪念在比赛中打酱油的日子……

穿衣搭配算法比赛终于要用UDF了，赶紧配置一个。发现官网上的介绍已经跟不上ODPS发展的步伐了，如果之前不是对Maven还有点了解，感觉配置一个UDF都不容易。几个相关的官网链接：[编写UDF][]、[移动推荐算法参赛攻略][]以及[UDF/MR本地开发工具]（比较详细）。

Alibaba ODPS 为 Eclipse 专门定制了插件，但事实上，ODPS UDF 是为 Maven 定制的，任何对Maven提供标准支持的IDE都可以正常用。我就比较习惯用IntelliJ，对Maven和Gradle支持都不错。

ODPS 为 UDF 和 MapReduce 项目都提供了项目模板支持（就是官网的archetype，这个步骤实际上是建立一个UDF或者MapReduce的模板），在IntelliJ IDEA下，实际上直接输入官网提供的参数即可：

![IntelliJ IDEA 配置 Maven Archetype](http://upload-images.jianshu.io/upload_images/78901-8b52eea17879ee9c.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

其中，

    GroupId: com.alibaba.base
    ArtifactId: base-udf-archetype/base-mr-archetype
    Version:  1.0.0-SNAPSHOT
    Repository: http://maven.sdk.de.yushanfang.com/SNAPSHOT

然后，就可以根据生成的例子实现自己的UDF了（貌似就是继承 UDF 类，详情见文档）。

和官网有点不一样的地方是，IntelliJ IDEA 不会提示你编写自己的项目信息，需要编辑 `main/resources/credential.properties` 和 `main/resources/META-INF/base.udf.xml` 。另外需要注意的是 idePath 的文件夹需要预先存在（官网给出的『workflow』需要改为『工作流』，否则文件夹不存在……）。

根据官网提示，编辑 `.m2/settings.xml` 文件，一般在 $HOME 目录下。这个步骤是为了添加向 Maven 注册非官方插件（还不在 Maven 的官方仓库里）。

最后，正常运行 Maven Goal 即可（在Maven面板），并填写相关参数（这个参数每个人都一样），如图：

![运行Maven目标](http://upload-images.jianshu.io/upload_images/78901-fa5678976a26f383.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

[编写UDF]: https://docs.aliyun.com/?spm=0.0.0.0.3cuHAi#/pub/odps/quick_start/udf "UDF官方文档"
[移动推荐算法参赛攻略]: http://bbs.aliyun.com/read/240435.html?spm=5176.7189909.0.0.2k2cyc "官方论坛"
[UDF/MR本地开发工具]: http://yushanfang.com/portal/help/doc.html?spm=0.0.0.0.HnJuqY&file=MrUdfLocalDev "官方文档"