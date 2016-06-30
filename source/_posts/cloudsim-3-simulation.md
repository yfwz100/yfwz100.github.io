---
title: CloudSim 笔记（3）- 仿真过程
tags:
  - CloudSim
  - 服务评估
date: 2016-07-01 00:21:57
---


CloudSim 的仿真过程是一个相对简单而又有些复杂的过程。简单的地方在于它是对离散事件处理系统的一种抽象，复杂在于这种抽象导致的异步事件处理，难以直接从代码中一目了然地掌控仿真的流程。为了便于描述，把 CloudSim 的模拟层次分为三层：第一层是基于 CloudSim、SimEntity、 SimEvent 构建的离散事件系统，第二层是在 SimEntity 基础上构建 Datacenter 并在 Datacenter 下构建云计算实体模拟系统，第三层是以云计算基础设施上构建的调度模拟系统。

<!-- more -->

## 第一层：异步事件处理系统

对于第一层，我把由 CloudSim、SimEntity、SimEvent 组成的系统为异步事件处理系统。这是由 CloudSim 类的工作原理所决定的。而主要的步骤有三个，控制了仿真的初始化、运行、结束：

初始化：主要是创建两个实体 CloudSimShutdown 和 CloudInformationService ，添加到实体列表里。

```
CloudSim.init()
├── CloudSimShutdown [SimEntity]
└── CloudInformationService [SimEntity]
```

运行：进行实体的仿真，其过程如下。其中的要点是，每个实体异步执行，并在 `run()` 方法里进行时钟的同步（让超时的等待，让未来得及运行的补充运行）；其是否同步的请求，是在 SimEntity 的 `run()` 方法和发出的 `SimEvent` 来决定的。

```
CloudSim.startSimulation() [Wait until simulation shutdown]
├── run()
│   ├── // loop of simulation
│   │   ├── SimEntity#startEntity() for all
│   │   ├── CloudSim.runClockTick(): break the loop if no future events
│   │   │   ├── SimEntity#run() for all if SimEntity#running
│   │   │   └── CloudSim.processEvent(SimEvent) while SimEvents at the same time
│   │   │       ├── set clock to SimEvent#eventTime()
│   │   │       └── create/send/hold_done
│   │   └── // procedure to terminate at a specific time
│   ├── CloudSim.finishSimulation()
│   └── CloudSim.runStop()
└── // reset in order to restart
```

结束：结束分为两种情况，如果没有未来的时间，那么 CloudSim 将进入收尾阶段；如果手动终止（abruptTerminate 为真）则直接终止。调用图：

```
CloudSim.finishSimulation()
├── abruptTerminate?
│   └── SimEntity#run() for all until SimEntity#getState() == FINISHED
├── SimEntity#shutdown() for all
└── set all parameters to null.
```

这个过程里，已知的仿真实体有 CloudSimShutdown 和 CloudInformationService ，两者的 `run()` 和 `startEntity()` 基本上什么都没做。而 CloudInformationService 则通知所有 datacenter 关闭（发送关闭信息号）。实际上，在 datacenter 和 datacenterbroker 默认都不处理这个事件。 `run()` 方法的默认内容是调用自身的 `processEvent()` 来处理事件。

## 第二层：云基础设施

对于所归纳的第二层，即云计算实体的模拟系统，实际上就是在前些天发布的文章的实验部分。在我们自己进行云计算资源调度实验的时候，最容易关注的是这一部分，即进行资源实体的定义，然后在主循环里，资源实体根据自身的特性，例如实体机调动虚拟机进行 cloudlet 的处理，cloudlet 自身根据负载模型的定义顺序执行，在经过一定周期以后，随着 cloudlet 执行结束，整个仿真流程结束。在这个过程中，手机 cloudlet 的执行数据，例如负载的变化历史、负载的等待时间、负载的执行时间、负载的完成时间、负载完成的周期、同时运行的负载的数量。即：

```
Datacenter [SimEntity]
├── DatacenterBroker [SimEntity]
│   ├── CloudSim.addEntity(~)
│   ├── // submit VM requests
│   └── // submit cloudlet requests
└── CloudSim.addEntity(~)
```

这个过程实际上是所说的第三层调度的编写执行，而其中涉及的实体，则是第二层抽象所关注的内容。这里的 `Datacenter` 和 `DatacenterBroker` 继承于 `SimEntity` ，接着 CloudSim 的运行流程进行其他实体的仿真。这个过程主要是由 Datacenter 和 DatacenterBroker 来带动。其中 DatacenterBroker 和 Datacenter 都没有覆盖 `run()` 方法，而是通过覆盖 `processEvent()` 来构建自身的方法：Datacenter 负责接受 DatacenterBroker 提交的虚拟机、cloudlet 的分配和调度工作，而 DatacenterBroker 则处理用户负载队列的问题。

在 Datacenter 这一层的模拟上，主要是根据事件的接收和发送来维持运转。由于是事件驱动的异步系统，因此根据某一条执行线来描述：
- 初始化阶段：Datacenter 和 DatacenterBroker 之间会来回传送一些参数，用于感知对方
- 运行阶段：DatacenterBroker 会把 cloudlet 通过 CloudSim 底层的事件传递机制提交给 Datacenter 处理
  - Datacenter 通过设定的 VmAllocationPolicy 分配 VM 给 cloudlet
  - VM 通过设定的 CloudletScheduler 调度 cloudlet，估计完成执行的时间并延迟发送 VM_DATACENTER_EVENT
- 结束阶段：当所有事件完成后，调用 CloudSim 的结束清理方法

在 CloudSim 里，它的仿真过程实际上是快进的。与其根据执行时钟的周期一步步来，CloudSim 内部通过消息的传递接收为根据，在一段很长的时间里，如果只有个别几个变化的事件，CloudSim 会选择按照事件来处理，跳过中途的时间。这样的好处是执行的时间大大减小了；而坏处是，如果控制不当，或者考虑上的失误，仿真的结果很可能和现实相距甚远。

## 第三层：应用和实验

第三层是建立于第二层云计算基础设施上的应用层，在之前的文章中粗略介绍过用法。至于怎么构建一个合理的实验，主要取决于作者为了云计算的某一种评估目标而建立的分析模型。这里没有特别的章法，CloudSim 的作者预留了足够的想象空间。但是，需要注意的是，在 CloudSim 里，像算法调度过程产生的周期消耗、量度算法执行的时间都是依靠分析模型进行时间的仿真模拟。在实际设计仿真实验的时候，要注意到 CloudSim 不仅仅是一个单纯的仿真平台，也是一个带有一定假设的分析仿真模型。合理的分析假设，在 CloudSim 上才能得到合理的结果。
