#目前调试完成，已经可以使用，中间输出可以进一步更改
#把文字识别api包装成函数，在node中加入文字属性，然后每次获得node区域图像后调用api函数，即可完成文字识别
import cv2 as cv
from queue import Queue
import numpy as np
import os
from aip import AipOcr

class node:
    formula = ['number', 'xmin', 'ymin', 'xmax', 'ymax', 'type', 'xcentral', 'ycentral', 'area_xmin', 'area_ymin', 'area_xmax', 'area_ymax', 'text']


class connection:
    formula = ['number1', 'number2', 'type', 'detected', 'edge_number', 'connection_number']#number1作为出发或源节点，number2作为目标节点，即箭头应该离number2节点更近
    type = 'and'
    detected = False


class pixel:
    formula = ['row', 'column']


count_node = 0
count_edge = 0
count_connection = 0
node_list = []
edge_list = []
filename_list=('actor','agent','goal','quality','resource','role','task','and','or','arrow')
row_direction = (-1,1,0,0,1,1,-1,-1)
column_direction = (0,0,-1,1,1,-1,1,-1)
connection_list = []


def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()


def text_recognition(number):
    """ 你的 APPID AK SK """
    APP_ID = '22427407'
    API_KEY = 'KsmO3V0HePNQbAdx3K7IMX1s'
    SECRET_KEY = 'b0NGGqGTsbmTfq5z5q1EQkDHjAU7qWtZ'
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    """ 读取图片 """
    image = get_file_content('/Users/spear/Desktop/node_temp/'+str(number)+'.png')
    """ 调用通用文字识别（高精度版） """
    res = client.basicAccurate(image)
    print(res)
    result = ''
    for i in res['words_result']:
        result += i['words']
    print(result)
    return result


def demonstrate(rsc):
    row, column = rsc.shape
    for i in range(row):
        for j in range(column):
            if rsc[i,j] == 0:
                rsc[i,j] = 255
            else:
                rsc[i,j] = 0
    cv.imshow("w",rsc)
    cv.waitKey(0)


def save(rsc):
    row, column = rsc.shape
    temp = rsc.copy()
    for i in range(row):
        for j in range(column):
            if temp[i,j] == 0:
                temp[i,j] = 255
            else:
                temp[i,j] = 0
    cv.imwrite('/Users/spear/Desktop/test.png',temp)


def pickup_node(name, filename, type):#和pickup_edge分开计数
    file = open(filename)
    s = file.readline()
    while s != '\n' and s != '':
        if s.find(name) == -1:
            s = file.readline()
            continue
        temp = node()
        global count_node
        a, b, temp.xmin, temp.ymin, temp.xmax, temp.ymax = s.split()
        if float(b) <= 0.9:
            s = file.readline()
            continue
        temp.number = count_node
        count_node += 1
        temp.xmin = int(float(temp.xmin))
        temp.ymin = int(float(temp.ymin))
        temp.xmax = int(float(temp.xmax))
        temp.ymax = int(float(temp.ymax))
        temp.xcentral = (temp.xmin + temp.xmax) / 2
        temp.ycentral = (temp.ymin + temp.ymax) / 2
        temp.type = type
        print(temp.number,temp.xmin,temp.ymin,temp.xmax,temp.ymax,temp.type)
        node_list.append(temp)
        s = file.readline()
    file.close()


def pickup_edge(name, filename, type):#和pickup_node分开计数
    file = open(filename)
    s = file.readline()
    while s != '\n' and s != '':
        if s.find(name) == -1:
            s = file.readline()
            continue
        temp = node()
        global count_edge
        a, b, temp.xmin, temp.ymin, temp.xmax, temp.ymax = s.split()
        if float(b) <= 0.9:
            s = file.readline()
            continue
        temp.number = count_edge
        count_edge += 1
        temp.xmin = int(float(temp.xmin))
        temp.ymin = int(float(temp.ymin))
        temp.xmax = int(float(temp.xmax))
        temp.ymax = int(float(temp.ymax))
        temp.xcentral = (temp.xmin + temp.xmax) / 2
        temp.ycentral = (temp.ymin + temp.ymax) / 2
        temp.type = type
        print(temp.number,temp.xmin,temp.ymin,temp.xmax,temp.ymax,temp.type)
        edge_list.append(temp)
        s = file.readline()
    file.close()



def node_process(rate, shape):#计算area区域
    for i in node_list:
        i.xcentral = int((i.xmin+i.xmax)/2)
        i.ycentral = int((i.ymin+i.ymax)/2)
        x = i.xmax - i.xmin
        y = i.ymax - i.ymin
        x_extrude = int(x * rate)
        y_extrude = int(y * rate)
        i.area_xmin = max(i.xmin - x_extrude, 0)
        i.area_xmax = min(i.xmax + x_extrude, shape[1])#darknet结果横向x纵向y
        i.area_ymin = max(i.ymin - y_extrude, 0)
        i.area_ymax = min(i.ymax + y_extrude, shape[0])
        #print(i.xcentral,i.ycentral,i.area_xmin,i.area_xmax,i.area_ymin,i.area_ymax)


def edge_process(rate, shape):#计算area区域
    for i in edge_list:
        i.xcentral = int((i.xmin+i.xmax)/2)
        i.ycentral = int((i.ymin+i.ymax)/2)
        x = i.xmax - i.xmin
        y = i.ymax - i.ymin
        x_extrude = int(x * rate)
        y_extrude = int(y * rate)
        i.area_xmin = max(i.xmin - x_extrude, 0)
        i.area_xmax = min(i.xmax + x_extrude, shape[1])#darknet结果横向x纵向y
        i.area_ymin = max(i.ymin - y_extrude, 0)
        i.area_ymax = min(i.ymax + y_extrude, shape[0])
        #print(i.xcentral,i.ycentral,i.area_xmin,i.area_xmax,i.area_ymin,i.area_ymax)


def picture_init(rsc):#把所有node的黑点变白，同时识别文字
    # cur_path1 = '/Users/spear/Desktop/node_temp' #清除该目录下所有文件
    # ls = os.listdir(cur_path1)
    # for i in ls:
    #     c_path = os.path.join(cur_path1, i)
    #     os.remove(c_path)
    for n in node_list:
        new_picture = np.zeros((n.ymax-n.ymin,n.xmax-n.xmin))
        for i in range(n.ymin,n.ymax):
            for j in range(n.xmin,n.xmax):
                new_picture[i-n.ymin][j-n.xmin] = rsc[i][j]
                rsc[i][j] = 255
        #cv.imwrite('/Users/spear/Desktop/node_temp/' + str(n.number) + '.png', new_picture)
        #n.text = text_recognition(n.number)#此处打印文字识别结果
        n.text='a'
        #save(rsc)
    return rsc


def euclidean_distance(term1,term2):
    res = ((term1[0]-term2[0])**2+(term1[1]-term2[1])**2)**0.5
    return res


def judge_node(pixel, origin_node, temp_connection):#!!!目前还没有使用其他指向指向同一节点的已探测的边为没有探测到类型的边赋类型的值
    for i in node_list:  # 看结尾落在哪个node的area里
        if origin_node.number == i.number:  # 不能自己连接自己
            continue
        if pixel.row >= i.area_ymin and pixel.row <= i.area_ymax and pixel.column >= i.area_xmin and pixel.column <= i.area_xmax:#使用扩张
            if temp_connection.detected == True:#找到了箭头节点
                edge_num = temp_connection.edge_number
                print(edge_num)
                if euclidean_distance([origin_node.xcentral,origin_node.ycentral],[edge_list[edge_num].xcentral,edge_list[edge_num].ycentral]) >= euclidean_distance([i.xcentral,i.ycentral],[edge_list[edge_num].xcentral,edge_list[edge_num].ycentral]):#这时arrow距离i更近
                    temp_connection.number1 = origin_node.number
                    temp_connection.number2 = i.number
                else:#这时arrow距离origin_node更近
                    temp_connection.number1 = i.number
                    temp_connection.number2 = origin_node.number
            else:#没找到箭头节点
                if origin_node.ycentral >= i.ycentral:#此时i在上
                    temp_connection.number1 = origin_node.number
                    temp_connection.number2 = i.number
                else:
                    temp_connection.number1 = i.number
                    temp_connection.number2 = origin_node.number
            global count_connection
            temp_connection.connection_number = count_connection
            count_connection += 1
            connection_list.append(temp_connection)
            print("connection:", temp_connection.number1, node_list[temp_connection.number1].type, "<->", temp_connection.number2,
                  node_list[temp_connection.number2].type, "---> type:",temp_connection.type)
            return True
    return False


def judge_type(pixel):
    temp_connection = connection()
    for i in edge_list:  # 看结尾落在哪个edge的area里
        if pixel.row >= i.area_ymin and pixel.row <= i.area_ymax and pixel.column >= i.area_xmin and pixel.column <= i.area_xmax:#使用扩张.否则可能出现先到达节点但并没有到达箭头的情况
            temp_connection.type = i.type
            temp_connection.detected = True
            temp_connection.edge_number = i.number
            return True, temp_connection
    return False, temp_connection


def bfs(rsc, start, origin_node):
    count = 0
    q = Queue(maxsize=0)
    q.put(start)
    flag = np.zeros(rsc.shape, dtype=np.int)
    row, column = rsc.shape
    flag[start.row][start.column] = 1
    received_connection = connection()
    temp_connection = connection()
    connection_flag = False
    while not q.empty():
        now = q.get_nowait()
        rsc[now.row][now.column] = 0
        count += 1
        if connection_flag == False:
            connection_flag, received_connection = judge_type(now)
        if judge_node(now, origin_node, received_connection) == True:
            return rsc
        for i in range(8):
            next_pixel = pixel()
            next_pixel.row = max(min(now.row + row_direction[i], row), 0)#保证上下限,数组不越界
            next_pixel.column = max(min(now.column + column_direction[i], column), 0)
            if rsc[next_pixel.row][next_pixel.column] == 1 and flag[next_pixel.row][next_pixel.column] == 0:
                flag[next_pixel.row][next_pixel.column] = 1
                q.put(next_pixel)
    #demonstrate(rsc)
    #save(rsc)
    # print("消除：",count)
    return rsc


#使用pixel_list[-1]来探测
#或者每走一步就判断一次

def search_start(rsc, n):#成功返回坐标，不成功返回-1
    for i in range(n.area_ymin,n.area_ymax):
        for j in range(n.area_xmin,n.area_xmax):
            if rsc[i][j] == 0:
                continue
            else:
                return i,j
    return -1,-1


def detect(rsc):
    for n in node_list:
        row, column = search_start(rsc, n)
        #print(row,column)
        while row != -1:
            start = pixel()
            start.row = row
            start.column = column
            rsc = bfs(rsc, start, n)
            row, column = search_start(rsc, n)
            #print(row,column)
    return rsc


def output_istarML():#关联还没有建立，节点之间可以进一步缩放排版
    with open("/Users/spear/Desktop/result.txt", "w") as f:
        f.write("{\n  \"actors\": [\n")#将编号改得和node number相关，并且先actor再agent再role
        for i in node_list:#这遍是actor
            if i.type == 'actor':
                f.write("    {\n      \"id\": \"node"+str(i.number)+"\",\n")
                f.write("      \"text\": \"" + i.text + "\",\n")
                f.write("      \"type\": \"" + "istar.Actor" + "\",\n")
                f.write("      \"x\": \"" + str(i.xcentral*0.3) + "\",\n")#目前使用强制缩放，未来可以使用自动缩放
                f.write("      \"y\": \"" + str(i.ycentral*0.3) + "\",\n")
                f.write("      \"customProperties\": {\n        \"Description\": \"\"\n      },\n")
                f.write("      \"nodes\": []\n")
                f.write("    },\n")
        for i in node_list:#这遍是agent
            if i.type == 'agent':
                f.write("    {\n      \"id\": \"node"+str(i.number)+"\",\n")
                f.write("      \"text\": \"" + i.text + "\",\n")
                f.write("      \"type\": \"" + "istar.Agent" + "\",\n")
                f.write("      \"x\": \"" + str(i.xcentral*0.3) + "\",\n")
                f.write("      \"y\": \"" + str(i.ycentral*0.3) + "\",\n")
                f.write("      \"customProperties\": {\n        \"Description\": \"\"\n      },\n")
                f.write("      \"nodes\": []\n")
                f.write("    },\n")
        for i in node_list:#这遍是role
            if i.type == 'role':
                f.write("    {\n      \"id\": \"node"+str(i.number)+"\",\n")
                f.write("      \"text\": \"" + i.text + "\",\n")
                f.write("      \"type\": \"" + "istar.Role" + "\",\n")
                f.write("      \"x\": \"" + str(i.xcentral*0.3) + "\",\n")
                f.write("      \"y\": \"" + str(i.ycentral*0.3) + "\",\n")
                f.write("      \"customProperties\": {\n        \"Description\": \"\"\n      },\n")
                f.write("      \"nodes\": []\n")
                f.write("    },\n")

    with open("/Users/spear/Desktop/result.txt", 'rb+') as f:#把最后一个，和\n都截取掉
        f.seek(-2, os.SEEK_END)
        if f.read(1).decode('utf-8') == ',':
            f.seek(-2, os.SEEK_END)
            f.truncate()
        else:
            f.seek(-1, os.SEEK_END)
            f.truncate()

    with open("/Users/spear/Desktop/result.txt", "a") as f:
        f.write("\n  ],\n  \"orphans\": [\n")
        for i in node_list:  # 这遍是goal
            if i.type == 'goal':
                f.write("    {\n")
                f.write("      \"id\": \"node" + str(i.number) + "\",\n")
                f.write("      \"text\": \"" + i.text + "\",\n")
                f.write("      \"type\": \"istar.Goal\",\n")
                f.write("      \"x\": \"" + str(i.xcentral*0.3) + "\",\n")
                f.write("      \"y\": \"" + str(i.ycentral*0.3) + "\",\n")
                f.write("      \"customProperties\": {\n        \"Description\": \"\"\n      }\n")
                f.write("    },\n")
        for i in node_list:  # 这遍是task
            if i.type == 'task':
                f.write("    {\n")
                f.write("      \"id\": \"node" + str(i.number) + "\",\n")
                f.write("      \"text\": \"" + i.text + "\",\n")
                f.write("      \"type\": \"istar.Task\",\n")
                f.write("      \"x\": \"" + str(i.xcentral*0.3) + "\",\n")
                f.write("      \"y\": \"" + str(i.ycentral*0.3) + "\",\n")
                f.write("      \"customProperties\": {\n        \"Description\": \"\"\n      }\n")
                f.write("    },\n")
        for i in node_list:  # 这遍是resource
            if i.type == 'resource':
                f.write("    {\n")
                f.write("      \"id\": \"node" + str(i.number) + "\",\n")
                f.write("      \"text\": \"" + i.text + "\",\n")
                f.write("      \"type\": \"istar.Resource\",\n")
                f.write("      \"x\": \"" + str(i.xcentral*0.3) + "\",\n")
                f.write("      \"y\": \"" + str(i.ycentral*0.3) + "\",\n")
                f.write("      \"customProperties\": {\n        \"Description\": \"\"\n      }\n")
                f.write("    },\n")
        for i in node_list:  # 这遍是quality
            if i.type == 'quality':
                f.write("    {\n")
                f.write("      \"id\": \"node" + str(i.number) + "\",\n")
                f.write("      \"text\": \"" + i.text + "\",\n")
                f.write("      \"type\": \"istar.Quality\",\n")
                f.write("      \"x\": \"" + str(i.xcentral*0.3) + "\",\n")
                f.write("      \"y\": \"" + str(i.ycentral*0.3) + "\",\n")
                f.write("      \"customProperties\": {\n        \"Description\": \"\"\n      }\n")
                f.write("    },\n")

    with open("/Users/spear/Desktop/result.txt", 'rb+') as f:#把最后一个，和\n都截取掉
        f.seek(-2, os.SEEK_END)
        if f.read(1).decode('utf-8') == ',':
            f.seek(-2, os.SEEK_END)
            f.truncate()
        else:
            f.seek(-1, os.SEEK_END)
            f.truncate()

    with open("/Users/spear/Desktop/result.txt", "a") as f:
        f.write("\n  ],\n")
        f.write("  \"dependencies\": [],\n")#目前没有dependencies,未来有dependencies需要改
        f.write("  \"links\": [\n")
        #arrow类型还没有处理
        for i in connection_list:  # 这遍是and
            if i.type == 'and':
                f.write("    {\n")
                f.write("      \"id\": \"edge" + str(i.connection_number) + "\",\n")
                f.write("      \"type\": \"istar.AndRefinementLink\",\n")
                f.write("      \"source\": \"node" + str(i.number1) + "\",\n")
                f.write("      \"target\": \"node" + str(i.number2) + "\"\n")
                f.write("    },\n")
        for i in connection_list:  # 这遍是or
            if i.type == 'or':
                f.write("    {\n")
                f.write("      \"id\": \"edge" + str(i.connection_number) + "\",\n")
                f.write("      \"type\": \"istar.OrRefinementLink\",\n")
                f.write("      \"source\": \"node" + str(i.number1) + "\",\n")
                f.write("      \"target\": \"node" + str(i.number2) + "\"\n")
                f.write("    },\n")

    with open("/Users/spear/Desktop/result.txt", 'rb+') as f:#把最后一个，和\n都截取掉
        f.seek(-2, os.SEEK_END)
        if f.read(1).decode('utf-8') == ',':
            f.seek(-2, os.SEEK_END)
            f.truncate()
        else:
            f.seek(-1, os.SEEK_END)
            f.truncate()

    with open("/Users/spear/Desktop/result.txt", "a") as f:
        f.write("\n  ],\n")


if __name__ == '__main__':
    filename_head = '/Users/spear/darknet/results/' #把这里修改成对应的路径，特别是darknet目录之前的目录
    picture_name = input("图片名称（不要有后缀名，正确的输入样例：L-CJB-01）：")
    node_list.clear()
    for i in filename_list:
        filename = filename_head + i + '.txt'
        if i == 'and' or i == 'or' or i == 'arrow':#边类型
            pickup_edge(picture_name, filename, i)
        else:
            pickup_node(picture_name, filename, i)
    picture_path = input("图片完整路径：")
    picture = cv.imread(picture_path) 
    gray = cv.cvtColor(picture, cv.COLOR_BGR2GRAY)
    r, dst = cv.threshold(gray, 0, 255, cv.THRESH_OTSU)#黑色1，白色0
    dst = cv.dilate(dst, None, iterations=1)  # 腐蚀和膨胀是对白色部分而言的，膨胀，白区域变大，最后的参数为迭代次数
    dst = cv.erode(dst, None, iterations=4)  # 腐蚀，白区域变小
    row, column = dst.shape
    dst = picture_init(dst)#预处理图片，进行节点分离
    for i in range(row):
        for j in range(column):
            if dst[i,j] == 255:
                dst[i,j] = 0
            else:
                dst[i,j] = 1
    #save(dst)
    area_rate = float(input("转化完成，输入area比率："))
    node_process(area_rate, (row,column))
    edge_process(area_rate, (row,column))
    #demonstrate(dst)
    dst = detect(dst)
    output_istarML()
    #save(dst)
