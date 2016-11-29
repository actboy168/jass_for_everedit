jass for everedit
=================

这是一个[EverEdit](http://www.everedit.net/  "EverEdit official site.")的Jass扩展。包括了


* 支持Jass、vJass和预处理的语法高亮
* 支持common.j、blizzard.j所有函数的函数列表、参数列表、中文解释的提示
* 支持Jass、vJass的语法检查和编译(使用JassHelper)


编译
====

1. 安装python2.7
2. 双击build.py

使用
====
* For EverEdit 4.0+

将jass.ezip拖到*EverEdit*上,然后新建一个叫"jass"的模式（模式文件保存于安装目录的mode文件夹，所有以esm结尾的文件都是模式文件）。  
示例如下：  
```
[Menu]
Title=Jass
[Menu0]
Key=CS+C
Command0=3,JassHelper 编译,${AppPath}\mode\Jass\jasshelper_compile.mac
[Menu1]
Key=CS+V
Command0=3,JassHelper 检查语法,${AppPath}\mode\Jass\jasshelper_check.mac
```
然后在 主菜单→工具→设置→语法着色，选定"jass.mac"语法文件，点击高级，绑定即可。

* For EverEdit 3.2 ~3.7

将jass.ezip拖到*EverEdit*上。

* For EverEdit 3.0 ~ 3.1

将jass_for_everedit目录覆盖到*EverEdit*，然后打开*EverEdit*菜单设置->语法着色，手动添加一个语法着色，可以参考以下设置选项。

```
标题: Jass
语法文件: jass.mac
扩展名: j
*高级*
模式: jass
```
