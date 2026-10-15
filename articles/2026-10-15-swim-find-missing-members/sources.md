# 来源、图像身份与AI辅助说明

核查日期：2026-10-14。正文为面向学生的原创机制讲解，A至F的故事、时刻、教学代码、图与数据均为本文构造或本文实际运行所得，不是历史案例或原论文实验数据。

## 一手来源及支持范围

1. Abhinandan Das、Indranil Gupta、Ashish Motivala，[SWIM原论文](https://www.cs.cornell.edu/projects/Quicksilver/public_pdfs/SWIM.pdf)，DSN 2002。第3.1节核对带序号的直接/间接探测与帮手转发ACK；第3.2节核对加入需要已知联系入口；第4.1节核对更新搭载、传播次数和队列选择；第4.2节核对怀疑、本人提升incarnation、乱序覆盖规则与Confirm语义；第4.3节核对打乱后逐项遍历的目标选择。本文重新构造可逐条运行的小例，不复述原论文整套实验或照搬其参数。
2. [Cornell计算机系2001—2002年报发表目录](https://www.cs.cornell.edu/annual_report/01-02/publications.htm)，研究机构当年记录。支持三位作者与DSN 2002发表信息；不据此猜测个人动机、对话或谁最先想到某个点子。
3. Indranil Gupta、Tushar D. Chandra、Germán S. Goldszmidt，[On Scalable and Efficient Distributed Failure Detectors](https://www.cs.cornell.edu/projects/Quicksilver/public_pdfs/On%20Scalable.pdf)，作者机构保存的论文。作为随机探测与可扩展性分析的前置原始研究；正文的六成员概率由明确假设重新推导并用Fraction计算，未引用其实验数值。
4. Armon Dadgar、James Phillips、Jon Currey，[Lifeguard: Local Health Awareness for More Accurate Failure Detection](https://arxiv.org/abs/1707.00788)，[2018年修订版全文](https://arxiv.org/html/1707.00788v2)。arXiv记录首版为2017-07-04，v2为2018-04-03。支持观察者自身处理变慢、局部健康感知、怀疑调整与更快通知被怀疑者这些后续扩展；本文没有运行Lifeguard或引用其提升倍数作为本次结果。
5. Jon Currey，[HashiCorp：Making Gossip More Robust with Lifeguard](https://www.hashicorp.com/en/blog/making-gossip-more-robust-with-lifeguard)，2017-07-06，参与者所在机构的发布文章。辅助核对Self-Awareness、Dogpile、Buddy System的动机与大意。旧文中的软件默认值与性能数字未当作现行产品参数。
6. HashiCorp，[Consul Gossip概念说明](https://developer.hashicorp.com/consul/docs/concept/gossip)及[Consensus概念说明](https://developer.hashicorp.com/consul/docs/concept/consensus)，产品维护方官方资料。支持成员发现、故障检测与共识职责不同。文中没有宣称已部署Consul或验证特定版本的线上行为。
7. HashiCorp，[memberlist项目](https://github.com/hashicorp/memberlist)及[state.go](https://github.com/hashicorp/memberlist/blob/master/state.go)、[suspicion.go](https://github.com/hashicorp/memberlist/blob/master/suspicion.go)，用于核对“后续工程实现不是原论文逐字翻译”这一阅读边界。master链接会变化，本文不以其今天的每个分支定义2002年原协议，也没有复制其代码或将其许可混入原创代码。

## 原件图片盘点与使用边界

SWIM核心原件共有4个编号图：Figure 1探测时序；Figure 2消息负载；Figure 3含检测延迟、传播延迟、怀疑等待三个面板；Figure 4人工丢包下的成员加入结果。均已随原PDF核对。Figure 1与机制最直接相关，Figure 2—4属于原论文历史实验，不能充当本次实验结果。

原PDF能公开阅读，并不等于其图被授予本文的CC BY 4.0再分发权。本文未找到足够明确的图像开放许可，因此不把原图搬进公开素材目录，只链接原论文；也没有截图后假称获得了开放许可。没有使用人物照片、服务器产品照、厂商徽标或生成的伪历史照片。

Lifeguard文章的性能图与人像等第三方图像也未复制。本篇只用其研究作为边界与后续方向，不讲人物生平或设备外观。正文需要的可见证据由本次实际UDP应用日志、实际执行的教学模型事件与原创机制图提供；这些不能替代原论文作者的历史实验，也没有被这样表述。

## 原创视觉及证据身份

- 图01—03、08、13—15：原创机制示意与状态规则说明。
- 图04—05：从本次离散事件模型的CSV筛选并绘制；虚拟时间，不是pcap。
- 图06—07：根据同一模型中的怀疑、本人反驳与更新返回事件重排，未显示所有无关ACK。
- 图09：固定种子2301的独立六成员传播模型；不是生产SWIM收敛时间统计。
- 图10—11：本文指定输入下的整数及概率计算。
- 图12：本次真实本机UDP应用日志重绘，使用原始单调时钟记录；故意的应用等待与忽略规则不冒称物理网络延迟或真实断电。
- cover.png：独立原创程序封面，不计入15张正文图。

详细尺寸、最小字号与身份见[figure-metadata.json](examples/figure-metadata.json)，数据与运行限制见[README](README.md)。正文图和封面均由可复现Python/Pillow程序绘制；没有使用图像生成模型制造照片。

## AI辅助的真实范围

本文由OpenAI AI助手在用户授权的技术科普文章任务中辅助研究、构思、撰写中文、编写与执行实验代码、制作程序图、核查数值并修订。资料通过公开一手来源核对，代码实际运行并保存原始结果。AI生成的文字、代码或图本身不作为外部事实证据；文中的校园游戏与六台服务器是教学设定，没有假装作者亲历过真实故障事故。

原创正文、图、封面与原创数据采用[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，署名可注明本篇题名及文章发布者；原创代码采用[MIT](LICENSE-CODE.txt)。外部原件的权利保留于原作者与出版方，不包含在上述授权中。
