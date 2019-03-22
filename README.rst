=======
fablinker usage
=======
1.fablinker是什么
fablinker是一个多服务器项目部署和管理的工具。基于python 2.7 ，用到fabric第三方库，在一台服务器上可管理控制多个远程主机，目前V0.01已开发完成。
![原理图](https://github.com/gangly/fablinker/blob/master/fab.png)

2.应用场景

2.1 项目部署

比如分布式爬虫部署在12台机器上，一旦代码更改，那么所有worker上的代码都要更新。
当然你可以写一个shell脚本，用12个scp命令从master上将代码拷贝到worker上，但是相对麻烦一点。
用fablinker工具只需一个put命令搞定。
然后我还需要kill掉所有worker进程，重新启动程序。没办法，这样你就只有一个个登录worker服务器，用kill，sh  **.py命令依次执行。
用fablinker工具只需kill 和 sh **.py两条命令搞定。
如果我还要将各个woker上生成的数据 data.dat收集起来，同样你可以写shell脚本用12个scp命令。
用fablinker工具只需一个get命令搞定。

2.2 运维

比如公司给咱蜂鸟分配了50台服务器，现在需要个每台服务器安装些软件，配置些环境。可以写个shell脚本，然后用scp将脚本分发到各个服务器上，
依次登录各个服务器，执行该shell脚本。
用fablinker可以在所有服务器上执行命令，当然也支持批处理和root权限（正在开发中，v0.02完成）。

3.fablinker有哪些功能

* put : 从本地主机上分发文件至所有远程主机
* get : 从远程主机上收集文件至本地主机，将远程主机文件都搜集到本机并将文件名带上主机名，-n参数，将远程文件名加上数字
* at: 切换到某个单机，或者切换到某个机器组
* addgrp: 动态机器分组
* fab shellcmd : 在所有远程主机上执行shellcmd命令， 比如 ls ， php  test.php， kill
* fab vim test.txt : 依次打开所有远程主机上的test.txt文件，可写入，更改， 保存。
* !cmd   可以在本地执行命令

更多信息请查看wiki:http://blog.csdn.net/freefishly/article/details/50748483

