---
title: Go lang 使用感受
tags:
  - 编程语言
date: 2017-04-16 10:01:15
---


使用 Go 语言进行开发已经两周了，学习过程中感觉 Go 语言借鉴了很多其他语言的概念，但是又推陈出新。Go 语言有几个语言特性我觉得还是很值得借鉴的~

<!-- more -->

# 没有类，只有结构体

Java 流行的原因是面向对象编程的概念普及。面向对象涉及到的三个概念确实使得编程更为方便，例如继承。但是继承也会引入很多问题，例如，继承的层级越多导致代码膨胀。而有时候你也不知道你应该有多少种抽象。而且，当一个类希望复用两个类的概念的时候，Java 并不能实现多重继承，只能通过组合模式以及代理模式实现多重继承。并且，多重继承用于代码复用被认为是一个反模式而被弃用。新的代码鼓励使用所谓 POJO （plain old java object）实现，并多用组合实现代码复用，使得代码复用较复杂。

Go 语言里没有类的概念，也就无所谓的继承。但是 Go 的结构体实现了类似继承的代码复用的特性。在结构体内声明匿名结构体，则视为该结构体“继承”了该结构体的内容，而且该结构体的所有属性、方法被默认地“继承”到新的结构体上，可以直接调用。正确地讲，这并不是真正的继承，而是一种概念复用。我们实现一个概念，实际上并不是代表我对这个概念名称有多执着，而是对其实现的认可。因此，Go 并没有实现概念的层级关系，也就没有所谓的“继承”关系了，而只是一种复用。并且，可以复用多个结构体。

如果了解了 Go 语言的接口以后，我觉得会更清晰。

# 接口与实现

Go 语言的接口和 C++、Java 等语言不同，接口的实现与否并不是在结构体声明的时候决定的，而是该结构体实现了接口所需要的所有函数，即视为实现了该接口。由此，我们可以做出一些很新颖的做法。例如，我们声明一个表达式类：

```go
type Expr interface {
    String()  string
    Compute() float64
}
```

上述代码如果用 C 语言来写，估计要声明一个联合体或者一个结构体，来描述常量的定义。而在 Go 语言中，则没有引入任何结构体定义，只是新增了一个概念，用 float64 来表达的常量表达式的概念：

```go
type ValExpr float64

func (v ValExpr) String() {
    return fmt.Sprintf("%.6f", float64(v))
}

func (v ValExpr) Compute() {
    return float64(v)
}
```

而上述代码清晰地表达了常量表达式本身就是一个常数，但在表达式的场合下，也是一个运算表达式。 Go 语言在概念的表达能力上要优于很多其他语言，十分值得其他语言借鉴。回到结构体实现的部分， Go 语言应该是面向概念和实现的语言，只要符合条件，都可以被认为是实现，从而简化了复用。

# 并发控制

Go 有着良好的并发控制，或者说作者一开始就是为多核时代的并发编程而设计的。 Go 从语言层面上支持多线程，关键字 `go` 可以为任意一个函数新建一个“线程”来执行。这里的“线程”并不是真的线程，而是一种轻量级并发单元。我们知道线程是进程的轻量级实现，但是也是由操作系统调度的。因此，线程的并行涉及到 CPU 的任务调度，这种调度是十分消耗资源的，涉及到上下文的切换等，尤其是 CPU 的多核环境。Go 使用了一种比线程更轻量级的实现，go routine ，即上述所谓的“线程”。Go routine 和真实的线程是多对多关系，并且 go routine 的数量远大于线程数量，Go routine 由内部调度器来执行，减少实际线程的切换。

这部分有很多良好的阅读材料就不再叙述：

 * [《Go 语言圣经》](http://shinley.com/)
 * [《Effective Go》](http://www.kancloud.cn/kancloud/effective/72199)

# 吐槽：泛型

Go 语言值得吐槽的地方恐怕在于泛型了。虽然 Go 灵活的接口机制使得很多泛型限制可以很好地实现，但这种机制只是单向的，并不能作为返回类型限制。例如，要实现一个简单的 HashMap，于是，我们定义方法：

```go
func (s *HashSet) Put(item HashItem, value interface{}) {
    // ignore...
}
```

其中 item 是一个带有 `hash()` 方法的接口：

```go
type HashItem interface {
    Hash() int
}
```

这个接口定义很完美，如果是 C++，要做 hash key 还要实现一个接口体之类的，而 Go 直接通过接口定义概念了。然而，作为 value 应该是没有什么输入限制的，所以，value 被定义为万能类型 `interface{}` 。然而，当我们定义取出函数的时候：

```go
func (s *HashSet) Get(item HashItem) interface{} {
    // ignore...
}
```

存进去的 value 的类型丢失了，我们只能得到万能类型 `interface{}`，这没什么用。因此， Go 语言的接口可以在一定程度上替代泛型的作用，但是这种泛型是单向的，是限制输入的，对于输出毫无办法。类型推断到这里就很糟糕了。于是，在基础的 Go 集合类里，大多数都是使用万能类型作为输出操作的类型，使得每次调用还要进行强制类型转换。这对于以集合作为输出的函数就是一个灾难，类型抹除使得调用者根本不知道返回的是什么，除非注释。为了让我的代码看起来容易理解，我还特意[新建了两个类来封装用到的集合](http://git.oschina.net/zhi/expr.go)……
