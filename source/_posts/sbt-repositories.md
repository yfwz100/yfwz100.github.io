---
title: Scala 的构建工具 SBT 镜像设置
tags:
  - 开发工具
date: 2016-07-31 09:02:35
---

SBT 使用内置的 Ivy 来解释软件库的依赖关系，虽然因为 Ivy 支持 Maven 而支持 Maven。但和 Gradle 之类的构建工具不同， SBT 并不能继承 Maven 的设置。因此，针对 SBT 的镜像要重新设置。

<!-- more -->

而 SBT 的软件库镜像相对 Maven 的设置来说简单很多，只需要编辑 `~/.sbt/repositories` 文件，加入

```
[repositories]
  local
  aliyun: http://maven.aliyun.com/nexus/content/groups/public/
  central: http://repo1.maven.org/maven2/
  typesafe: http://repo.typesafe.com/typesafe/ivy-releases/, [organization]/[module]/[revision]/[type]s/[artifact](-[classifier]).[ext], bootOnly
```

以上配置文件解释顺序是：本地→阿里云镜像→Maven主镜像。如果需要添加公司的 maven 镜像，可以按照 key: value 的形式添加，key 的命名没有要求（暂时没注意到，但是最好也不要用什么特殊符号吧 😂）。同时，安利一下[阿里云的 Maven 镜像](http://maven.aliyun.com)，国内访问很快。

> 2016年9月27日更新：
>
> 在 `repositories` 文件中应该至少加入如下仓库：
> ```
> typesafe: http://repo.typesafe.com/typesafe/ivy-releases/, [organization]/[module]/[revision]/[type]s/[artifact](-[classifier]).[ext], bootOnly
> ```
> 国内的镜像貌似都没有把 sbt 的新版本包括进去。因此，如果公司内网不能访问，则需要通过 Proxifier 等全局代理工具至少把 sbt 下载下来，然后其他的依赖关系通过国内镜像也可以顺利地下载了。
