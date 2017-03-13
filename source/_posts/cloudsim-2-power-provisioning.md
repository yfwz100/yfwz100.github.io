---
title: CloudSim 笔记（2）- 能耗节约的虚拟机调度评估
tags:
  - 服务评估
  - 云计算
date: 2016-06-24 20:21:15
---


CloudSim 的能耗模块是在 3.0 版本完善的。最早的工作可能在 2011 年到 2012 年之间，论文：

> Anton Beloglazov, and Rajkumar Buyya, "[Optimal Online Deterministic Algorithms and Adaptive Heuristics for Energy and Performance Efficient Dynamic Consolidation of Virtual Machines in Cloud Data Centers](http://dx.doi.org/10.1002/cpe.1867)", Concurrency and Computation: Practice and Experience (CCPE), Volume 24, Issue 13, Pages: 1397-1420, John Wiley & Sons, Ltd, New York, USA, 2012

<!-- more -->

论文主要讨论了能耗和性能之间平衡的最优方法。首先阐述了单机上的 VM 迁移问题，确定单机的最佳迁移时机并应用竞争分析建立一个在线最优算法，然后分析多机动态迁移的问题。分别使用竞争分析说明确定性的 online 最优算法、用平均情况说明非确定性的 online 最优算法。

相应地支持仿真实验， CloudSim 在核心程序中加入了 `org.cloudbus.cloudsim.power` 包，即虚拟机能耗仿真的包。其目录结构如下：

```
.
├── PowerDatacenter.java
├── PowerDatacenterBroker.java
├── PowerDatacenterNonPowerAware.java
├── PowerHost.java
├── PowerHostUtilizationHistory.java
├── PowerVm.java
├── PowerVmAllocationPolicyAbstract.java
├── PowerVmAllocationPolicyMigrationAbstract.java
├── PowerVmAllocationPolicyMigrationInterQuartileRange.java
├── PowerVmAllocationPolicyMigrationLocalRegression.java
├── PowerVmAllocationPolicyMigrationLocalRegressionRobust.java
├── PowerVmAllocationPolicyMigrationMedianAbsoluteDeviation.java
├── PowerVmAllocationPolicyMigrationStaticThreshold.java
├── PowerVmAllocationPolicySimple.java
├── PowerVmSelectionPolicy.java
├── PowerVmSelectionPolicyMaximumCorrelation.java
├── PowerVmSelectionPolicyMinimumMigrationTime.java
├── PowerVmSelectionPolicyMinimumUtilization.java
├── PowerVmSelectionPolicyRandomSelection.java
├── lists
│   └── PowerVmList.java
└── models
    ├── PowerModel.java
    ├── PowerModelCubic.java
    ├── PowerModelLinear.java
    ├── PowerModelSpecPower.java
    ├── PowerModelSpecPowerHpProLiantMl110G3PentiumD930.java
    ├── PowerModelSpecPowerHpProLiantMl110G4Xeon3040.java
    ├── PowerModelSpecPowerHpProLiantMl110G5Xeon3075.java
    ├── PowerModelSpecPowerIbmX3250XeonX3470.java
    ├── PowerModelSpecPowerIbmX3250XeonX3480.java
    ├── PowerModelSpecPowerIbmX3550XeonX5670.java
    ├── PowerModelSpecPowerIbmX3550XeonX5675.java
    ├── PowerModelSqrt.java
    └── PowerModelSquare.java
```

为了支持能耗评估，CloudSim 实际上作出了不少的修改，并采用了一种侵入式的设计，不仅仅局限于 `power` 包。为了获得性能参数，甚至改变了原来 CloudSim 的事件循环进行了修改。在数据收集方面，放弃了之前 CloudSim 论文发表时候用的 Sensor 类，而是采用在 `PowerDatacenter` 和 `VM` 等实体里嵌入数据收集的代码。分解起来有点费劲。

以下是简要的修改说明：
1. 实体相关：
   * 能耗数据中心（`PowerDatacenter`）：覆盖了调度更新的算法以支持能耗的计算，包括能耗调度算法的嵌入（见调度策略）、能耗收集计算两方面的更新
   * 能耗数据中心用户（`PowerDatacenterBroker`）：在处理出错上提前退出，几乎没更新
   * 能耗主机（`PowerHost`、`PowerHostUtilizationHistory`）：新增能耗模型相关的更新
   * 能耗虚拟机（`PowerVm`）：覆盖方法记录 CPU 使用历史
2. 模型：
   * 调度策略
     * 选择策略（`PowerVmSelectionPolicy`）：找出给定的 `PowerHost` 要迁移的虚拟机
     * 放置策略（`PowerVmAllocationPolicyAbstract`）：继承自 `VmAllocationPolicy`，简单实现了分配虚拟机到主机的策略，并在 `optimizeAllocation(vmList)` 方法中返回主机和虚拟机的优化配对
   * 资源利用率的能耗模型（`PowerModel`）：主要是根据资源利用率（CPU？）获取能耗

提出的几种算法：
1. 虚拟机放置（分配）择策略：主要是使用稳定估计量估计主机是否需要过载
   * 基础统计量：`MigrationInterQuartileRange`、`MigrationMedianAbsoluteDeviation`
   * 回归预测：`MigrationLocalRegression`、`MigrationLocalRegressionRobust`
   * 固定阈值判断：`MigrationStaticThreshold`
   * 不优化（对照实验）：`Simple`
2. 虚拟机选择策略：
   * 最大相关性：`MaximumCorrelation` 选择资源利用率向量的相关性最大的虚拟机进行迁移
   * 最短迁移时间：`MinimumMigrationTime` 尽可能近，并且内存尽可能少的虚拟机进行迁移
   * 最低利用率：`MinimumUtilization` 选择利用率最低的进行迁移，使性能损失减小
   * 随机选择（对照实验）：`RandomSelection`

其选择虚拟机的基本依据来自资源利用率和能耗的历史统计量，算法的具体过程可以参考论文。

对能耗的仿真模型定义在 `PowerModel`，这个借口只提供一个抽象方法，就是 `getPower(double):double` 从给定的资源利用率里推导出能耗。估计 CloudSim 的想法是对每个资源都建立一个利用率到能耗的映射，然后能耗是所有资源的累积和：


$$
P = \sum_{u\in U} P_u(u)
$$
其中的 $P_u(u)$ 即建立的利用率到能耗的映射。对于 CloudSim Power 部分的论文和具体实现来说，只考虑了粗粒度下 CPU 的能耗代表整机能耗，具体的依据来源于

> Kusic D, Kephart JO, Hanson JE, Kandasamy N, Jiang G. Power and performance management of virtualized computing environments via lookahead control. Cluster Computing 2009; 12(1):1–15.

另一篇文献同样说到这个事情，出自 Google 研究员的关于 CPU 到能耗的经验曲线模型：

> Fan, Xiaobo, W. D. Weber, and L. A. Barroso. "Power provisioning for a warehouse-sized computer." Acm Sigarch Computer Architecture News 35.2(2007):13-23.

形式化描述为：

$$
P_{CPU}(u) = \alpha (2u - u^r) + \sigma
$$
思路都是用 CPU 能耗直接替代整机能耗。这个一方面确实是 CPU 在能耗方面占了主导，另一方面，则是由于分析的便捷性。

当然，对能耗模型的调研，觉得这篇文章的说法比较靠谱：

> Kansal, Aman, et al. "Virtual machine power metering and provisioning." Acm Symposium on Cloud Computing ACM, 2010:39-50.

CPU 大约占了 60% 的能耗，其余的能耗大户包括 RAM 和磁盘。但是要对 CloudSim 进行扩展，不修改 `power` 包里的内容估计是做不到了。

另外，对于多核架构来说，简单的线性模型也是很难说服的，在论文的实验部分，作者意识到这个问题，因此，还引用了标准组织 [SPECPower 2008](http://www.spec.org/power_ssj2008/) 公布的季度各主流服务器厂商的服务器 CPU 利用率和功耗的对应表作为关系映射。

由于动态调度，涉及到一台物理主机服务多个 VM 的情况。大多数论文认为虚拟机放置是一种装箱问题，但实际上一台物理机可以服务的 VM 数目应该是不确定的。但是，要考虑“过载”（overload）的情况，作为一种性能损失的衡量。论文认为过载是由于所分配的 VM 都满载以后，可能违反一次 SLA（服务等级协定）。而这个定义感觉是不清晰的。实际上，物理核心数和 VM 要求的核心数可能存在不一致的情况。在典型的 Web 应用场景，实际上 CPU 满载的情况并不多，主要以 IO 处理为主。桌面应用满载的情况更低了，这个自己就可以验证。因此，多个 VM 共用一个核心也是完全可能的，也是资源极大化利用应该考虑的。

在后来修改版里，CloudSim 3.0 引入了 `VmSchedulerTimeSharedOverSubscription` 类对满载的虚拟机进行调度。但采用的是简单的分时调度，采用 MIPS （每秒指令数）来量度：

$$
MIPS\_{VM} = \min \left( \frac{MIPS\_{PM} }{n\_{VM} }, MIPS_{VM} \right)
$$

随着 VM 的增加，每个 VM 获得的实际 MIPS 比所请求的 MIPS 少；而分配的 VM 较少时，单个 VM 最多的资源也只能是规定的资源量。然而这么定义在公平调度的意义上是合理的。但 VM 在实际的调度环境中，是可以进入休眠状态而基本不消耗资源，分配给该 VM 的资源可以被另一个资源所独占（优先级调度）。另外一点是调度器也没有考虑优先级的问题。