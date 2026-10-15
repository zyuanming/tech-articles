# ELF 符号与重定位：可选复现实验

正文在 [read.md](read.md)。无需运行代码也能读懂正文。这里给想核对真实字节的读者使用。

## 已验证环境与范围

- Linux x86-64，ELF64 little endian。
- GCC (Debian 14.2.0-19) 14.2.0。
- GNU as / ld / readelf / objdump (GNU Binutils for Debian) 2.44。
- Python 3，实验脚本只用标准库。
- 图片由 Pillow 12.3.0、Noto Sans CJK 与 DejaVu Sans Mono 渲染；只重做编译实验不需要 Pillow 或字体。

本实验是 Linux x86-64 静态可执行文件，没有 libc、共享库或动态解释器。不是 iOS、macOS、ARM64、Mach-O 或运行期 ASLR 实验。不同工具版本可能改变实际字节，脚本保留了本次固定实例的严格断言，不保证其他工具链逐字节相同。

## 文件

- examples/start.s：14 字节的程序入口，通过 Linux x86-64 exit 系统调用交回 answer 的返回值。
- examples/answer.c：返回整数42。
- examples/padding.s：16个0x90字节（nop）。
- examples/caller.c：普通C调用的补充目标文件。只单独编译查看，不冒充另一个已运行程序。
- examples/reproduce.py：完整构建、反汇编、ELF二进制字段解析与断言。
- examples/expected-results.json：本次实测数据，用于与重算结果比较和生成图片。
- examples/build_figures.py：原创建图源，读取预期数据后重建18幅正文PNG与封面。
- examples/figure-metadata.json：逐图教学职责、实证与字号数据。

## 一键重算

在 examples 目录运行：

```sh
python3 reproduce.py --out ./my-results
```

指定目录必须为空。脚本拒绝覆盖已有内容，不会下载、安装、访问网络或修改系统。它只运行随文原创代码和已安装工具；最后运行的四个程序正常把42作为退出状态，脚本把42当作预期结果，不按一般命令行惯例误判为实验失败。

输出目录会包含所有源码副本、.o、四个静态可执行文件、每条命令的完整输出、结构化结果和二进制SHA-256。请不要把整个输出目录误当成需要公开上传的正文素材。

预期摘要：

```text
PASS: four linked programs return 42; displacements 9, 25, 9, -11; two expected link failures; ELF bytes independently verified.
```

四种布局对应 normal、padded、shifted、reversed。缺定义与重复定义是主动构造的反例，链接退出状态应非零。

## 主例命令

以下在源码所在目录使用一个新建的工作子目录即可。为保持简洁，用当前目录文件名展示；完整脚本负责隔离输出。

```sh
as --64 start.s -o start.o
gcc -c -O1 -fno-pie -fno-asynchronous-unwind-tables \
  -fno-stack-protector -fcf-protection=none answer.c -o answer.o
ld -m elf_x86_64 -static -e _start --build-id=none \
  -Ttext=0x401000 start.o answer.o -o normal
readelf -sW start.o
readelf -rW start.o
objdump -drw start.o
objdump -drw normal
./normal; echo $?
```

-c 停在目标文件，不做链接。-O1 用低级别优化得到简短实现；其余编译选项在本次实验中排除PIE代码生成、异步栈展开表、栈保护与控制流保护指令带来的干扰。禁用这些默认特性的目的只是固定教学字节，不能作为真实产品的安全构建建议。--build-id=none 省去构建标识，-Ttext 指定输出.text地址，-e 指定入口。

## 独立核验在检查什么

reproduce.py 使用 Python struct 从实际 ELF64 文件读取：ELF头、节头表、字符串表、符号表、RELA条目，以及输出.text字节。这条核验路径没有用 readelf / objdump 的文字结论来代替字节检查。

它验证三者一致：符号地址、从真实指令里按小端有符号32位解码的位移，以及下一条指令地址。检查式为 next_instruction + displacement == answer。

本次预期：

- start.o补丁节内偏移1，文件偏移65，重定位类型4（R_X86_64_PLT32），附加数−4。
- normal：_start=0x401000，answer=0x40100e，位移9。
- padded：answer=0x40101e，位移25。
- shifted：_start=0x501000，answer=0x50100e，位移9。
- reversed：_start=0x401006，answer=0x401000，位移−11。
- 四个静态文件都没有PT_INTERP或.plt，也没有剩余.text重定位。

## 重绘图片

在已有 Pillow 和所列字体的环境中运行：

```sh
python3 examples/build_figures.py
```

原始数据固定在 examples/expected-results.json；如要用不同工具链的结果重做教学图，必须同时重新核对正文、固定标签和数据，不可只换JSON冒称所有标注自动适配。

原创正文、原创图与说明采用CC BY 4.0；原创示例和制图脚本采用MIT许可，见 [LICENSE-CODE.txt](LICENSE-CODE.txt)。第三方工具和规范权利见 [sources.md](sources.md)。
