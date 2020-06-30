# ClockWorkOrange
A lightweight digital circuit simulation package for humans. In memory of Stanley Kubrick's A Clockwork Orange.
一个轻量级的Python数字电路仿真库，命名用于纪念斯坦利库布里克的同名电影《发条橙》。

开发了一个数字电路仿真库，可以连接元件可以仿真得到时序图。当然，该库目前还不是很完善，但是已经可以满足大部分的数字电路仿真的需求。

该库由四个核心对象：
1. 与非门电路：接受n个输入，一个输出 NAND
2. 元件：可由若干个门电路组成 Component
3. 电路：电路上可以放置元件和与非门，可以理解为一个面包板 Circuit
4. 测试器：用于提供时钟信号、输入、绘制输出图 Tester

使用方法：
首先，安装ClockworkOrange库：
```bash
pip install ClockworkOrange
```
然后，在程序中引入该库：
```python
from ClockworkOrange.ClockworkOrange import *
```
添加元件：
本例中，我们以一个D触发器为例：
```python
D = Component(3, 2) # 实例化一个空的元件，该元件有三个输入，两个输出
# 使用add方法添加门电路，并第一个参数为门电路对象，第二个参数为输入的网表（为一个dict，如下所示），第三个参数为取名；取名不可重复。(注意：一定要用关键字参数！)
D.add(NAND(2), network_port={PIN.IN(1): [1, ], 'IN0': [0, ]}, component_name='G4') # PIN.IN(1)等效于字符串‘IN1’，指定输入的端口1，IN0、IN1是默认分配的端口名，不可修改。network_port={PIN.IN(1): [1, ]}等效于将第1个输入端口连接上与非门G4的第一个输入端口
D.add(NAND(2), network_port={'IN0': [0, ], 'G4': [1, ]}, component_name='G3')
D.add(NAND(2), network_port={'G4': [1, ], 'G1': [0, ]}, component_name='G2')
D.add(NAND(2), network_port={'G3': [0, ], 'G2': [1, ]}, component_name='G1')
D.add('OUT0', network_port={'G1': [0, ]}) #将门电路输出连接至输出端口，输出端口为OUT0、OUT1以此类推，不可更改，可以等效写成PIN.OUT(0),network_port={'G1': [0, ]}等效于将与非门‘G1’的输出连接至OUT0。
D.add('OUT1', network_port={'G2': [0, ]})
# 这些门电路的名字都是可以自定义的，但是不能重复
```
D触发器构建完毕，我们将它添加到面包板上：
```python
breadboard = Circuit(2, 2)
breadboard.add(D, network_port={PIN.IN(0): [0, ], PIN.IN(1): [1, ]}, component_name='C1')
    breadboard.add(PIN.OUT(0), network_port={PIN.COMPONENT_OUTPIN('C1', 0): [0, ]})
    breadboard.add(PIN.OUT(1), network_port={PIN.COMPONENT_OUTPIN('C1', 1): [0, ]})
    #PIN.OUT(1), network_port={PIN.COMPONENT_OUTPIN('C1', 1): [0, ] 相当于将元件c1的第一个输出接到面包板的第一个输出口，PIN.COMPONENT_OUTPIN('C1', 1)以为元件C1的第一个输出。同样，元件名可以自定义，但是不能重复。
```
现在，我们使用测试器来测试这个电路：
```python
tester = Tester(breadboard, clock_pin=PIN.IN(0), watchlist=['OUT0', 'OUT1']) # 实例化一个测试器，并指定时钟引脚（如果是组合逻辑电路，可以不指定时钟引脚）指定查看哪几个引脚的时序图，（时钟、输入引脚不用额外指定）
# PIN.IN(0) 等效于字符串‘IN0’，意为面包板的输入0端口，和前面一样，这个名字是系统自动分配的。
tester.input({'IN1': [LOGIC.LOW, LOGIC.LOW, LOGIC.HIGH, LOGIC.HIGH, LOGIC.HIGH, LOGIC.HIGH, LOGIC.HIGH, LOGIC.HIGH,
                          LOGIC.LOW, LOGIC.LOW, LOGIC.HIGH, LOGIC.LOW, LOGIC.HIGH, LOGIC.LOW, LOGIC.HIGH, LOGIC.LOW],
                  })# 给IN1引脚输入一串01，同样，‘IN1’可以用PIN.IN(1)代替，两者等效。LOGIC.HIGH等效于True，LOGIC.LOW等效于False。
tester.figure_size=(20, 10) # 设定输出时序图的大小
tester.draw() # 运行结束之后，我们将时序图画出来。
```

**下面展示完成的代码**：
```python
from ClockworkOrange.ClockworkOrange import *

if __name__ == '__main__':
    breadboard = Circuit(3, 2)
    D = Component(3, 2)

    D.add(NAND(2), network_port={PIN.IN(1): [1, ], 'IN0': [0, ]}, component_name='G4')
    D.add(NAND(2), network_port={'IN0': [0, ], 'G4': [1, ]}, component_name='G3')
    D.add(NAND(2), network_port={'G4': [1, ], 'G1': [0, ]}, component_name='G2')
    D.add(NAND(2), network_port={'G3': [0, ], 'G2': [1, ]}, component_name='G1')
    D.add('OUT0', network_port={'G1': [0, ]})
    D.add('OUT1', network_port={'G2': [0, ]})

    breadboard.add(D, network_port={PIN.IN(0): [0, ], PIN.IN(1): [1, ]}, component_name='C1')
    breadboard.add(PIN.OUT(0), network_port={PIN.COMPONENT_OUTPIN('C1', 0): [0, ]})
    breadboard.add(PIN.OUT(1), network_port={PIN.COMPONENT_OUTPIN('C1', 1): [0, ]})

    tester = Tester(breadboard, clock_pin=PIN.IN(0), watchlist=['OUT0', 'OUT1'], duty_cycle=0.2)
    tester.input({'IN1': [LOGIC.LOW, LOGIC.LOW, LOGIC.HIGH, LOGIC.HIGH, LOGIC.HIGH, LOGIC.HIGH, LOGIC.HIGH, LOGIC.HIGH,
                          LOGIC.LOW, LOGIC.LOW, LOGIC.HIGH, LOGIC.LOW, LOGIC.HIGH, LOGIC.LOW, LOGIC.HIGH, LOGIC.LOW],
                  })
    tester.figure_size = (20, 10)
    tester.draw()
```

输出的时序图如下：

![在这里插入图片描述](https://img-blog.csdnimg.cn/20200701001314694.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80Mjc0NDEwMg==,size_16,color_FFFFFF,t_70)
可以看见D触发器时序是正确的（输入数据延迟了一个时钟周期后输出）

下面讲一讲Tester的参数：
use_num_for_plot:默认为True，意味画图时横坐标为离散的值，通过计数器确定横坐标，若为False，则横坐标为unix时间戳的电路开始运转时的差值。
initial_impulse:默认为None，接受整数n，意味在真正input之前先进行n个时钟周期，使电路进入正常状态。

这个库目前功能大概就是这么多，现在还比较简陋，望大家见谅～我会在之后的时间更新的。非常欢迎大家的使用，谢谢大家的支持～如果大家想和我一起共同维护这个库的话，欢迎与我联系：yixiaolan@foxmail.com




