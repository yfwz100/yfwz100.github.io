---
title: 基于 Hexo 打造一个数学博客
date: 2017-03-21 12:05:46
tags:
---

在 Hexo 博客引擎折腾了一下午数学公式显示。试了几个 Hexo 插件，效果都不是很理想。目前 Hexo 支持 Markdown 写博客，配合 [Typora][] 写博客不错，也不用担心格式问题。不过，在 Markdown 写数学公式是一个问题。存在的解决方法是以 \$...\$ 为区域渲染 Latex 公式，但这种转换方式目前有存在一些问题。

<!-- more -->

一般来说，Hexo 的数学公式插件有两种处理方法：

1. 先把 \$...\$ 处理为 HTML 然后处理 Markdown；
2. 先处理 Markdown 然后再处理 \$...\$。

前者一般是 plugin，后者一般就是主题搭配 MathJax 或 Katex 了。但 Markdown 格式和 Latex 公式之间存在冲突：

1. “_”（下划线）在 Markdown 里会被转义为斜体；
2. “*”（星号）在 Markdown 里被转义为粗体；
3. “\\”（反斜杠）在 Markdown 里被转义为“\”。

于是，有些主题带的 MathJax 和 Katex 都无法使用了，书写复杂公式以后会被默认的 Markdown 引擎渲染转义掉。之前写的很多 Markdown 文档其实都没考虑这个问题，包括 [Typora][] 生成的 Markdown 文档也没有对 Markdown 里的格式进行特殊处理。于是，很多引擎识别不正常。然后，就把默认的 Markdown 引擎改为 Pandoc 了，配合 MathJax 一切正常。在 package.json 里，把

```json
{
    "dependencies": {
        "hexo-renderer-marked": "*"
    }
}
```

中的 `hexo-renderer-marked` 改为 `hexo-renderer-pandoc` 即可。

另外，Katex 对 Latex 公式支持不全，暂时建议不要使用。

[Typora]: http://typora.io "A Markdown Editor"