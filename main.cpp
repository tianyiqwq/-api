
#include <string>
#include <opencv2/core/core.hpp> 
#include <opencv2/imgcodecs.hpp> 
#include <opencv2/opencv.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <iostream>
#include <WINSOCK2.H>
#include <thread>  
#include <opencv2\imgproc\types_c.h>
#include <regex>
#include <vector>
#include <stdlib.h>  
#include <math.h>  
#pragma comment(lib,"ws2_32.lib")
using std::string;
using std::cout;
using std::cin;
using std::endl;
using namespace cv;


int detected = 0;
int sendflag = 1;
string fname = "C://Users//yuncai//Desktop//img.jpg";
char receiveBuf[256] = {};
double posx, posy;
string classes;


void tcp_Client()
{
    //创建套接字
    WORD myVersionRequest;
    WSADATA wsaData;                    //包含系统所支持的WinStock版本信息
    myVersionRequest = MAKEWORD(1, 1);  //初始化版本1.1
    int err;
    err = WSAStartup(myVersionRequest, &wsaData);
    if (!err) {
        printf("已打开服务器\n");
    }
    else {
        printf("服务器未打开!");
        return;
    }
    SOCKET serSocket = socket(AF_INET, SOCK_STREAM, 0);//创建了可识别套接字

    //需要绑定的参数
    SOCKADDR_IN addr;
    addr.sin_family = AF_INET;
    addr.sin_addr.S_un.S_addr = inet_addr("127.0.0.1");//ip地址
    addr.sin_port = htons(3000);//绑定端口

    //将套接字绑定到指定的网络地址
    bind(serSocket, (SOCKADDR*)&addr, sizeof(SOCKADDR));//绑定完成
    listen(serSocket, 10);
    //第二个参数代表能够接收的最多的连接数
    SOCKADDR_IN clientsocket;
    int len = sizeof(SOCKADDR);
    SOCKET serConn;

    //等待客户端的连接
    serConn = accept(serSocket, (SOCKADDR*)&clientsocket, &len);
    cout << "客户端" << inet_ntoa(clientsocket.sin_addr) << "已连接" << endl;             //客户端已连接
    while (1) {
        char sendBuf[32];
        inet_ntoa(clientsocket.sin_addr);
        if (detected == sendflag) {

            if (detected == 1) {
                sprintf(sendBuf, "detected");

            }
            else {
                sprintf(sendBuf, "loss");

                sendflag = !detected;
            }
        }
        else {
            sprintf(sendBuf, "no");

        }
        //在对应的IP处并且将这行字打印到那里


        send(serConn, sendBuf, strlen(sendBuf) + 1, 0);

        //接收客户端传来的信息
        recv(serConn, receiveBuf, strlen(receiveBuf) + 1, 0);
        char* quit = "q";




        //如果客户端传来了q信号，则服务端关闭，客户端也关闭
        if (!strcmp(receiveBuf, quit)) {
            printf("%s", quit);
            break;
        }
    }

    closesocket(serConn);   //关闭
    WSACleanup();           //释放资源的操作
}



//从摄像头读取数据
void gcap(VideoCapture g_cap)
{
    using namespace std;
    Mat img, frame;



    g_cap >> img;

    FileStorage fs2("config/camera.yml", FileStorage::READ);

    int frameCount = (int)fs2["nframes"];

    std::string date;

    fs2["calibration_time"] >> date;

    Mat cameraMatrix, distCoeffs;

    fs2["camera_matrix"] >> cameraMatrix;

    fs2["distortion_coefficients"] >> distCoeffs;

    Mat view, map1, map2;

    initUndistortRectifyMap(cameraMatrix, distCoeffs, Mat(), getOptimalNewCameraMatrix(cameraMatrix, distCoeffs, img.size(), 1, img.size(), 0), img.size(), CV_16SC2, map1, map2);
    //得到摄像头的校正矩阵map1,map2
    g_cap >> frame;

    Mat rview;

    Mat m;

    remap(frame, m, map1, map2, INTER_LINEAR);//m矩阵就是经过校正的图像
}//对工业相机生成的变形图像进行校正
void writePix(Mat img)
{
    if (detected)
    {
        std::this_thread::sleep_for(std::chrono::seconds(3));
        if (detected)
        {
            cv::imwrite(fname, img);
            detected = 0;
            std::this_thread::sleep_for(std::chrono::seconds(3));
        }

    }

}
Mat MoveDetect(Mat background_data, Mat img)
{
    using namespace std;
    //将background和img转为灰度图
    Mat result = img.clone();
    Mat gray1, gray2;
    Mat background;

    thread imgw(writePix, img);
    imgw.detach();
    cvtColor(background_data, gray1, CV_BGR2GRAY);
    cvtColor(img, gray2, CV_BGR2GRAY);

    //进行canny边缘检测 
    Canny(background_data, background, 0, 30, 3);

    //将background和img做差；对差值图diff进行阈值化处理
    Mat diff;
    absdiff(gray1, gray2, diff);
    //imshow("absdiss", diff);
    threshold(diff, diff, 50, 255, CV_THRESH_BINARY);
    //imshow("threshold", diff);

    //腐蚀膨胀消除噪音

    Mat element1 = getStructuringElement(MORPH_RECT, Size(3, 3));
    Mat element2 = getStructuringElement(MORPH_RECT, Size(15, 15));
    erode(diff, diff, element1);
    //imshow("erode", diff);
    dilate(diff, diff, element2);
    //imshow("dilate", diff);


    //二值化后使用中值滤波+膨胀
    Mat element = getStructuringElement(MORPH_RECT, Size(11, 11));
    medianBlur(diff, diff, 5);//中值滤波
    //imshow("medianBlur", diff);
    dilate(diff, diff, element);
    blur(diff, diff, Size(10, 10)); //均值滤波
    //imshow("dilate", diff);

    //查找并绘制轮廓
    vector<vector<Point>> contours;
    vector<Vec4i> hierarcy;
    findContours(diff, contours, hierarcy, CV_RETR_EXTERNAL, CHAIN_APPROX_NONE); //查找轮廓
    vector<Rect> boundRect(contours.size()); //定义外接矩形集合
    //drawContours(img2, contours, -1, Scalar(0, 0, 255), 1, 8);  //绘制轮廓

    if (contours.size() > 0)
    {
        detected = 1;

    }
    else
        detected = 0;
    //查找正外接矩形
    int x0 = 0, y0 = 0, w0 = 0, h0 = 0;
    double Area = 0, AreaAll = 0;
    for (int i = 0; i < contours.size(); i++)
    {
        boundRect[i] = boundingRect((Mat)contours[i]); //查找每个轮廓的外接矩形
        x0 = boundRect[i].x;  //获得第i个外接矩形的左上角的x坐标
        y0 = boundRect[i].y; //获得第i个外接矩形的左上角的y坐标
        w0 = boundRect[i].width; //获得第i个外接矩形的宽度
        h0 = boundRect[i].height; //获得第i个外接矩形的高度

        //计算面积
        double Area = contourArea(contours[i]);//计算第i个轮廓的面积
        AreaAll = Area + AreaAll;

        //筛选
        if (w0 > 140 && h0 > 140)
            rectangle(result, Point(x0, y0), Point(x0 + w0, y0 + h0), Scalar(0, 255, 0), 2, 8); //绘制第i个外接矩形
            //文字输出
        Point org(10, 35);
        if (i >= 1 && AreaAll >= 19600)
            putText(result, "Is Blocked ", org, FONT_HERSHEY_SIMPLEX, 0.8f, Scalar(0, 255, 0), 2);


    }
    return result;
}
std::vector<std::string> regexsplit(const std::string& input)
{
    std::regex re("', '");

    std::sregex_token_iterator p(input.begin(), input.end(), re, -1);
    std::sregex_token_iterator end;
    std::vector<std::string> vec;
    while (p != end)
        vec.emplace_back(*p++);

    return vec;
}
void position()
{
    std::vector<std::string> vec;
    std::string recv = receiveBuf;
    vec = regexsplit(recv);
    int i = 0;

    if (vec.size() > 8)
    {

        classes = vec[1];
        posx = atof(vec[3].c_str()) + atof(vec[5].c_str()) / 2;
        posy = atof(vec[4].c_str()) + atof(vec[6].c_str()) / 2;

    }
    cout << classes << endl << posx << endl << posy << endl;
}
void main()
{
    using namespace std;
    VideoCapture cap;
    cap.open(0);
    if (!cap.isOpened()) //检查打开是否成功
        return;
    Mat frame;
    Mat background;
    Mat result;
    thread ttcp(tcp_Client);

    ttcp.detach();

    int count = 0;
    while (1)
    {

        cap >> frame;
        if (!frame.empty())
        {
            count++;
            if (count == 1)
                background = frame.clone(); //提取第一帧为背景帧

            result = MoveDetect(background, frame);
            imshow("result", result);

            if (waitKey(50) == 27)
                break;
            position();
        }
        else
            continue;
    }

    cap.release();
}
