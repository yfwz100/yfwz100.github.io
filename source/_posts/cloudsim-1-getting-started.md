---
title: CloudSim 笔记 (1)
tags:
  - 服务评估
  - 云计算
date: 2016-06-23 22:24:58
---


[CloudSim](^CloudSim) 是在 2009 年提出的云计算模拟仿真软件。主要工作是模拟云计算模型，为了持续地解决云计算资源、应用负载模型、资源性能模型的性能评估问题而提出。 CloudSim 可以支持系统组件的系统级和行为建模，设计了包括数据中心、虚拟机、资源管理策略的基本接口，甚至支持云联盟模型。在 2010 年发表前， CloudSim 已经被 HP 等公司用作云资源供给的研究[2][^CloudSimTheToolkit]。

<!-- more -->

版本记录：
* 1.0~2.0： 对云计算基础设施的建设，支持数据中心、虚拟机、应用程序的仿真。
* 3.0：加入能耗模型辅助能耗分析（未来可能会给出详细分析）。
* 4.0：加入应用程序容器仿真的支持。

CloudSim 的建模层次是在 IaaS 之上，包括了 Host、VM、Cloudlet 三层的建模。而负载的仿真，则是通过 Broker（在 CloudSim 里可以被视为用户）这个接口对 VM、Cloudlet、Utilization 三者的行为控制来实现的。

一个典型的 CloudSim 仿真实验，一般流程如下：

1. 初始化 DataCenter
   - 初始化数据中心的特性（例如费用信息）
   - 初始化所管辖 Host 集群（包括 VM 分配策略、VM 使用策略，但是不分配 VM）
2. 初始化 Broker（用户）
   - 由用户进行 VM 集群申请（VM 分配策略由 DataCenter 决定）
   - 并给定实验的 Cloudlet 队列（包括资源负载的仿真）
3. 调用 `CloudSim.startSimulation()` 进行实验
4. 调用 `CloudSim.stopSimulation()` 结束实验

如果没有设置 `CloudSim.terminateSimulation(cycles)` ，则 CloudSim 会在完成所有 Broker 的 Cloudlet 请求后结束，否则只执行到特定的周期数 `cycles` 。例子可以参看

CloudSim 支持在调用过程中动态地创建 Broker 以及相关的 VM 集群、Cloudlet 队列，可以在多线程中创建。但在线程中进行动态调度的时候，需要先使用 `CloudSim.pauseSimulation()` 暂停当前的调度工作，否则不能保证在某个时间点执行。

为什么不能直接在其他线程中更改 CloudSim 的仿真对象？

CloudSim 并不是一个直接的简单时钟循环来更新所有主机的状态。在 CloudSim 中，所有仿真实体（数据中心、主机、虚拟机、Cloudlet）都是 SimEntity 的子类，创建之初就会默认添加到 CloudSim 的对象池中，可以和所有其他节点进行通信（以ID为目标）。而这个对象池，由于连接着 CloudSim 的所有资源，也可以认为是一个网络结构，而其中的 SimEntity 就是网络中的节点。CloudSim 内部维护一个时钟，而每次遍历更新 SimEntity，但是 SimEntity 并不一定同步系统时间进行状态更新，而是等待时钟到某一个节点的时候才进行自身的更新。因此，如果直接使用多线程来修改仿真对象（例如 Datacenter、Host、VM 之类），可能会破坏状态的更新而导致错误的实验结果。因此，CloudSim 实际上是一个异步系统，`CloudSim.pauseSimulation()` 有点相当于一个同步锁，只有锁同步了，才能进行状态的更新。

而异步系统则是由 CloudSim 的本质决定的。试想象一个调度过程，调度算法是无法把自身拆解成多个步骤嵌入到模拟的时钟周期的。现在实现的调度算法，基本上都是封装为一个方法，方法执行了就输出结果了，如果这算是一个时钟周期，那单位有点大了。而如果真的把算法拆解成指令，做到处理器级别的精度模拟，那么对用户行为建模的 Cloudlet 就不合适了（Cloudlet 只描述了资源占用的百分比）。CloudSim 本质上是一种第代价模拟，它希望有些不重要的部分进行快进和忽略，如果真的做到了处理器级别精度的仿真，就相当于开了几个真的虚拟机来实验，这样做的代价显然违背了 CloudSim 的初衷。

如何模拟用户行为？

在 CloudSim 给出的例子中，负载的描述都过于简单了。CloudSim 中的负载单位是 Cloudlet（这个奇怪的单词估计是从 Applet 之类的词语引申而来的），作为一个负载的基本任务。 Cloudlet 的组成是执行的周期数、所需文件以及最重要的资源利用率模型。有了这些基础，一个 Cloudlet 可以认为是一个程序，或者用户的活动。如果要仿真的对象是程序的执行时间，那么 Cloudlet 可以被认为是单独的程序，如果要仿真的对象是用户活动，那么 Cloudlet 可以被抽象为用户活动。

和 VM 不一样，Cloudlet 在初始化后，并不会立即执行，而会根据 CloudletScheduler 来调度执行（队列/并行）。 CloudSim 提供了分时调度和分空间调度，分时调度里一个cloudlet 独占 VM 资源；而分空间调度，cloudlet 则分布在可用的核数里并行执行。因此，如果把 cloudlet 视作用户对资源利用的活动，应该把调度器设置为分时调度，并使 cloudlet 和 VM 一一对应，使得 cloudlet 独占 VM。

一个物理主机可以有多少个 VM ？

这个策略是可以进行调整的，在 CloudSim 1.0~2.0 的时候，一个物理机的资源数等于所分配的 VM 的资源数，否则分配失败。

[^CloudSim]: https://github.com/Cloudslab/cloudsim
[^CloudSimTheToolkit]: http://www.buyya.com/papers/CloudSim2010.pdf
