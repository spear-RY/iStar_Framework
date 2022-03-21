# iStar_Framework

1.Darknet框架

1.1 Darknet安装
使用仓库中Darknet文件夹下的darknet框架即可，可能需要装一些前置的包，如openCV，numpy等。
直接从仓库克隆，然后make
根据有无GPU等情况调整makefile前5行的设置

测试darknet是否运行：
在shell中打开darknet目录
运行
./darknet detector test cfg/voc.data cfg/yolov3-voc.cfg yolov3_608_50000.weights L-CJB-01.png （最后一个是图片名，可以更换）
如果能够运行，说明yolo安装成功。会在darknet目录下生成 predictions.jpg (如仓库中的predictions.jpg类似的结果)

Darknet使用方法：
https://www.cnblogs.com/hichens/p/12861370.html

1.2 Darknet训练方法：(如果只使用，不做进一步的训练的话，可以忽略这部分)
https://www.cnblogs.com/hejunlin1992/p/9925293.html
把训练图片放到trainImage中，对应的label的xml文件放入trainImageXML
把验证图片放到validateImage中，对应的label的xml文件放入validateImageXML
输入命令 python createID.py 生成 trainImageId.txt 和 validateImageId.txt。Mac系统把文件中的.DS_Store删掉
输入命令 python trans.py 根据xml文件生成对应的txt
修改对应训练的网络参数，如iteration等
(* 待完善 *)

1.3 Darknet批量测试方法：（使用方法部分）
1）把所有需要测试的的图片放入validateImage文件夹，不需要准备对应的XML文件
2）输入命令 python createID.py 生成 trainImageId.txt 和 validateImageId.txt。Mac系统把文件中的.DS_Store删掉
3）输入命令 python trans_for_valid.py 生成文件路径，注意使用trans_for_valid.py
4）运行 ./darknet detector valid cfg/voc.data cfg/yolov3-voc.cfg yolov3_608_50000.weights -i 1 -out ""
执行完毕后 results目录下会有actor.txt agent.txt等文件，代表的是对应的目标在不同的文件中检测的结果
以本目录下 actor.txt 中 L-CJB-08 1.000000 2663.259277 221.508026 3215.958008 770.540283 为例：
在L-CJB-08中， 在 2663.259277 221.508026 3215.958008 770.540283 范围内，有actor对象的致信率为100%


2.识别重组工具
1）将pro2_source.py中的423行修改成对应的路径。路径是darknet下results文件夹的路径，句末需要带上 / 符号
2）输入需要转化的图片名称。图片一定先经过测试，结果已经生成在results目录的文件中
3）输入需要转化的图片完整路径
4）输入转化的candidate area比率，推荐0.1左右
5）结果的输出格式：A <-> B, type: T， A以类型T的关系指向B

完整过程示例：
spear@maodeMBP iStar_Framework % python pro2_source.py  #运行pro2_source.py文件
图片名称（不要有后缀名，正确的输入样例：L-CJB-01）：L-CJB-01   #输入需要转化的图片名
0 589 996 1328 1454 goal        #图片中已经探测到的实体对象的位置及类型
1 1823 1008 2575 1440 goal
2 999 77 2013 561 goal
3 2572 1675 3149 2145 task
4 808 2310 1537 2801 task
5 1820 2279 2521 2790 task
6 91 1710 773 2191 task
0 1812 546 1968 642 and
1 1129 562 1319 682 and
2 2194 1403 2351 1557 arrow
3 826 1402 996 1605 arrow
4 2379 1393 2558 1518 arrow
5 1039 1425 1190 1585 arrow
图片完整路径：/Users/spear/darknet/L-CJB-01.png         #输入需要转化的图片完整路径
libpng warning: iCCP: profile 'ICC Profile': 'RGB ': RGB color space not permitted on grayscale PNG
转化完成，输入area比率：0.1        #输入candidate area比率
1
connection: 0 goal <-> 2 goal ---> type: and        #识别结果，意为0号goal对象指向2号goal对象，关系类别为and
3
connection: 6 task <-> 0 goal ---> type: arrow
5
connection: 4 task <-> 0 goal ---> type: arrow
0
connection: 1 goal <-> 2 goal ---> type: and
2
connection: 5 task <-> 1 goal ---> type: arrow
4
connection: 3 task <-> 1 goal ---> type: arrow