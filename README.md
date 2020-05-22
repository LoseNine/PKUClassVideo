# PKUClassVideo


北大直播课堂视频下载小工具 (2020.05.22)

课程分类一键多线程下载

复制粘贴所得命令在命令行中运行：
```console
$ pip3 install requests
```

## 用法

1. 编辑`config.ini`输入学号密码
2. 打开网址`http://liveclass.pku.edu.cn/course/#/myCourses`，右键点击`检查`,刷新页面，找到数据包
![](https://github.com/LoseNine/PKUClassVideo/blob/master/img/1.PNG)
在右边下拉，找到cookies，复制后边的键值对到ini文件即可
![](https://github.com/LoseNine/PKUClassVideo/blob/master/img/2.PNG)
2. 命令行`python main.py`
