# 来源、实证与素材权利

核查日期：2026-10-13。本文不作编译器或链接器发明史归属判断；以实际生成的一个 Linux x86-64 ELF 实例解释机制。

## 一手事实来源

1. [GCC：Options Controlling the Kind of Output](https://gcc.gnu.org/onlinedocs/gcc/Overall-Options.html)。支持预处理、编译、汇编、链接的阶段关系，以及 -c 输出目标文件而不链接的说明。具体版本、命令和字节以本次实际运行输出为准，不把在线当前手册版本当作本机版本。
2. [ELF gABI：Symbol Table](https://gabi.xinuos.com/elf/05-symtab.html)，重点第5.2、5.5、5.7节。支持全局/局部/弱绑定、SHN_UNDEF、定义符号在可重定位文件里的节内偏移等。网页标题标作 ELF Object File Format 4.3 DRAFT；本文保留草案身份。
3. [ELF gABI：Relocation](https://gabi.xinuos.com/elf/06-reloc.html)，重点6.1。支持r_offset、r_info、r_addend、REL与RELA以及处理器特定类型。它是通用格式说明，不单独用它推导x86-64的具体call编码。网页同属4.3 DRAFT。
4. [AMD64 System V ABI官方项目](https://gitlab.com/x86-psABIs/x86-64-ABI)及[官方PDF构建产物](https://gitlab.com/x86-psABIs/x86-64-ABI/-/jobs/artifacts/master/raw/x86-64-ABI/abi.pdf?job=build)。本次实际取得的PDF首页为 Version 1.0，2025-03-12；SHA-256为19f346cc723dbeb6ad80494614291f4e85aba3caca48dcfd537d33f82af6d6ac。第4.4.1节、表4.9支持P/S/L/A定义、R_X86_64_PC32与R_X86_64_PLT32不同公式；第3.2节及附录A支持函数与Linux系统调用约定。链接是可变化构建产物，后续下载应检查首页，不把它冒称永久固定版本。
5. [GNU binutils提交说明：x86-64: Generate branch with PLT32 relocation](https://sourceware.org/pipermail/binutils-cvs/2018-February/047522.html)，2018-02-13，H.J. Lu，提交bd7ab16b4537788ad53521c45469a1bdae84ad4a。支持PLT32标记可用于32位PC相对分支、可直接解析本地定义；不能把PLT类型名字等同于最终必有PLT跳板。本文同时直接核对GNU ld 2.44生成的实际call与无.plt结果，没有只依赖旧提交概述。
6. [GNU readelf 2.44手册](https://sourceware.org/binutils/docs-2.44/binutils/readelf.html)和[objdump手册](https://sourceware.org/binutils/docs/binutils/objdump.html)。支持选项含义与输出对象：-hW文件头、-SW节、-sW符号、-rW重定位、-lW程序头，objdump -drw联合反汇编与重定位。工具显示的信息和作者解释在图注区分。
7. [GNU ld选项](https://sourceware.org/binutils/docs/ld/Options.html)及[链接脚本基本概念](https://sourceware.org/binutils/docs/ld/Basic-Script-Concepts.html)。支持入口、静态链接、输出节地址及输入输出节/地址关系。本次特定链接顺序与字节布局由执行结果建立，不宣称任意链接器配置都只顺序串接。
8. [ELF gABI：Program Loading](https://gabi.xinuos.com/elf/07-pheader.html)与[Dynamic Linking](https://gabi.xinuos.com/elf/08-dynamic.html)。支持装载、程序头/段和动态链接职责边界，均为4.3 DRAFT。图18为概念边界，不是动态加载实测。
9. [Linux内核：x86-64系统调用表](https://github.com/torvalds/linux/blob/master/arch/x86/entry/syscalls/syscall_64.tbl)。支持本例exit系统调用编号60；正文不复制内核表或内核代码。程序单线程，因此直接exit满足本实验用途，不推广为多线程C运行时的通用退出实现。
10. [Intel 64与IA-32架构软件开发手册官方入口](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html)。作为call/ret、E8 rel32、小端与指令编码的进一步查阅入口。本文具体字节还由本机汇编、反汇编和独立字节解码彼此交叉验证；未复制Intel手册页面或插图。

## 原创实验与适用范围

实验源码、命令和ELF解析程序在examples/，无需下载任何外部项目。主例使用start.s、answer.c，padding.s仅改变布局，caller.c仅用于普通C调用的补充证据。

- 四个实际静态可执行文件的退出状态均为42；距离依次9、25、9、−11。
- 两个失败例确实执行链接，分别得到未定义引用和重复强定义；不是虚构错误信息。
- 输出数据见[expected-results.json](examples/expected-results.json)；完整命令可以从[reproduce.py](examples/reproduce.py)重新产生。
- 小型ELF解析器直接核验真实字节与表项，未用一个预写公式的打印输出冒充真实工具链实验。
- 20字节是normal的.text大小，不是整个ELF文件只有20字节。
- 不使用libc、动态链接器、用户设备或浏览器；不代表iOS/Mach-O，不代表整个文件为PIC/PIE。整体平移对照是两次静态重链接，不是运行期重定位或ASLR实验。
- 实验固定工具选项，仅用于教学；关闭若干防护相关代码生成不是生产环境推荐。

## 逐图来源、作用与权利

全部图片由本文原创制图脚本生成。作者/发布署名：zyuanming；AI辅助研究、撰写、编程、制图。原创版式、箭头、色块、解释性标签和封面采用CC BY 4.0。真实工具输出部分展示本文原创输入产生的事实信息；GNU程序名称、字段名、格式名和错误短语仍注明出处，不声称获得GNU软件或文档的统一再授权。

1. assets/01-observed-result.png：主例汇编、编译和运行结果的排印。42是实测退出状态；不冒充终端截图。
2. assets/02-separate-files.png：原创源文件→目标文件→链接器流程；区分汇编、编译和链接。
3. assets/03-elf-object.png：真实start.o头部前6字节和相关readelf字段，结合原创节作用图解；不是完整ELF结构图。
4. assets/04-symbols.png：真实readelf -sW中answer条目的选列重排，Value去前导零；说明UND与已定义节内偏移的差别。
5. assets/05-call-before.png：真实objdump关键行拆排和原创五字节放大；说明占位反汇编不是已解析目标。
6. assets/06-three-coordinates.png：按真实节位置和布局计算的原创坐标对照；区分节内/文件/虚拟地址。
7. assets/07-relocation-recipe.png：同一真实RELA条目的字段重排与中文解释；数据来自readelf和独立解析器。
8. assets/08-linked-layout.png：真实14+6字节布局的原创示意；包含最终符号值，无虚构地址。
9. assets/09-patched-bytes.png：实际链接前后五字节与objdump选行；说明具体字段的变化。
10. assets/10-relative-distance.png：原创一格一字节计数条；真实偏移0、5、14和19说明距离基准。
11. assets/11-addend-origin.png：原创公式推导图，问号明确是待定字段示意，不是文件内容；解释附加数−4。
12. assets/12-padding-experiment.png：真实增加16字节后位移25，按共同尺度绘制的布局对照；不是性能测试。
13. assets/13-negative-displacement.png：真实倒排后位移−11与字节f5 ff ff ff，结合原创逆向路线图。
14. assets/14-shifted-distance.png：两份真实静态文件的地址对照；说明共同平移抵消与非PIE边界。
15. assets/15-missing-symbol.png：真实GNU ld未定义引用错误的关键部分拆排；原创缺席图帮助诊断。
16. assets/16-duplicate-symbol.png：真实GNU ld重复定义错误的关键部分拆排；原创两个提供者图限定强全局定义。
17. assets/17-c-compiler-evidence.png：原创caller.c及真实生成的objdump选行；源代码另按MIT授权。
18. assets/18-link-load-execute.png：依据ELF概念独立设计的职责边界图；不是动态过程运行截图。
19. cover.png：独立原创封面，使用本例call字节变化，不与正文图复用计数。

具体生成数据、图片尺寸和有效字号另见[figure-metadata.json](examples/figure-metadata.json)。所有正文图原宽1062像素，在354像素显示宽度下，关键文字不小于约12像素。每图均有在正文附近的独立图注；不靠放大原图替代手机阅读。

## 第三方材料与再授权边界

- gABI页面版权声明属于Xinuos及其前身相关权利人；AMD64 ABI、Intel手册、GNU工具手册等各有其权利。本文仅链接并以自己的语言解释，没有把其PDF、网页截图、原表或插图装入公开文章目录。
- 因此，本篇没有需要与原创图片混合再授权的第三方照片、文档插图或截图。重要真实对象是我们自行构建的ELF文件和实际工具结果，未以虚构硬件照片代替证据。
- 本篇不是对GNU binutils程序本身的分发，也不把其软件许可外推为文档图片许可。简短字段名与错误事实排印不把第三方工具版权整体纳入CC BY。
- 制图使用本机Noto Sans CJK和DejaVu Sans Mono；只分发已渲染PNG，不分发字体二进制。字体权利分别遵循其原许可。

## 本文许可

原创正文、原创解释性图片、封面与说明：Creative Commons Attribution 4.0 International，[许可摘要](https://creativecommons.org/licenses/by/4.0/)、[完整法律文本](https://creativecommons.org/licenses/by/4.0/legalcode.zh-hans)。转载、改编时请署名zyuanming，链接原文和许可，并注明修改。

原创C/汇编/Python示例及制图代码：MIT，完整文本见[LICENSE-CODE.txt](LICENSE-CODE.txt)。不对工具输出中的事实数字主张独占权利；文档许可也不取消第三方已有权利。
