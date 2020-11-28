
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
    //�����׽���
    WORD myVersionRequest;
    WSADATA wsaData;                    //����ϵͳ��֧�ֵ�WinStock�汾��Ϣ
    myVersionRequest = MAKEWORD(1, 1);  //��ʼ���汾1.1
    int err;
    err = WSAStartup(myVersionRequest, &wsaData);
    if (!err) {
        printf("�Ѵ򿪷�����\n");
    }
    else {
        printf("������δ��!");
        return;
    }
    SOCKET serSocket = socket(AF_INET, SOCK_STREAM, 0);//�����˿�ʶ���׽���

    //��Ҫ�󶨵Ĳ���
    SOCKADDR_IN addr;
    addr.sin_family = AF_INET;
    addr.sin_addr.S_un.S_addr = inet_addr("127.0.0.1");//ip��ַ
    addr.sin_port = htons(3000);//�󶨶˿�

    //���׽��ְ󶨵�ָ���������ַ
    bind(serSocket, (SOCKADDR*)&addr, sizeof(SOCKADDR));//�����
    listen(serSocket, 10);
    //�ڶ������������ܹ����յ�����������
    SOCKADDR_IN clientsocket;
    int len = sizeof(SOCKADDR);
    SOCKET serConn;

    //�ȴ��ͻ��˵�����
    serConn = accept(serSocket, (SOCKADDR*)&clientsocket, &len);
    cout << "�ͻ���" << inet_ntoa(clientsocket.sin_addr) << "������" << endl;             //�ͻ���������
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
        //�ڶ�Ӧ��IP�����ҽ������ִ�ӡ������


        send(serConn, sendBuf, strlen(sendBuf) + 1, 0);

        //���տͻ��˴�������Ϣ
        recv(serConn, receiveBuf, strlen(receiveBuf) + 1, 0);
        char* quit = "q";




        //����ͻ��˴�����q�źţ������˹رգ��ͻ���Ҳ�ر�
        if (!strcmp(receiveBuf, quit)) {
            printf("%s", quit);
            break;
        }
    }

    closesocket(serConn);   //�ر�
    WSACleanup();           //�ͷ���Դ�Ĳ���
}



//������ͷ��ȡ����
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
    //�õ�����ͷ��У������map1,map2
    g_cap >> frame;

    Mat rview;

    Mat m;

    remap(frame, m, map1, map2, INTER_LINEAR);//m������Ǿ���У����ͼ��
}//�Թ�ҵ������ɵı���ͼ�����У��
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
    //��background��imgתΪ�Ҷ�ͼ
    Mat result = img.clone();
    Mat gray1, gray2;
    Mat background;

    thread imgw(writePix, img);
    imgw.detach();
    cvtColor(background_data, gray1, CV_BGR2GRAY);
    cvtColor(img, gray2, CV_BGR2GRAY);

    //����canny��Ե��� 
    Canny(background_data, background, 0, 30, 3);

    //��background��img����Բ�ֵͼdiff������ֵ������
    Mat diff;
    absdiff(gray1, gray2, diff);
    //imshow("absdiss", diff);
    threshold(diff, diff, 50, 255, CV_THRESH_BINARY);
    //imshow("threshold", diff);

    //��ʴ������������

    Mat element1 = getStructuringElement(MORPH_RECT, Size(3, 3));
    Mat element2 = getStructuringElement(MORPH_RECT, Size(15, 15));
    erode(diff, diff, element1);
    //imshow("erode", diff);
    dilate(diff, diff, element2);
    //imshow("dilate", diff);


    //��ֵ����ʹ����ֵ�˲�+����
    Mat element = getStructuringElement(MORPH_RECT, Size(11, 11));
    medianBlur(diff, diff, 5);//��ֵ�˲�
    //imshow("medianBlur", diff);
    dilate(diff, diff, element);
    blur(diff, diff, Size(10, 10)); //��ֵ�˲�
    //imshow("dilate", diff);

    //���Ҳ���������
    vector<vector<Point>> contours;
    vector<Vec4i> hierarcy;
    findContours(diff, contours, hierarcy, CV_RETR_EXTERNAL, CHAIN_APPROX_NONE); //��������
    vector<Rect> boundRect(contours.size()); //������Ӿ��μ���
    //drawContours(img2, contours, -1, Scalar(0, 0, 255), 1, 8);  //��������

    if (contours.size() > 0)
    {
        detected = 1;

    }
    else
        detected = 0;
    //��������Ӿ���
    int x0 = 0, y0 = 0, w0 = 0, h0 = 0;
    double Area = 0, AreaAll = 0;
    for (int i = 0; i < contours.size(); i++)
    {
        boundRect[i] = boundingRect((Mat)contours[i]); //����ÿ����������Ӿ���
        x0 = boundRect[i].x;  //��õ�i����Ӿ��ε����Ͻǵ�x����
        y0 = boundRect[i].y; //��õ�i����Ӿ��ε����Ͻǵ�y����
        w0 = boundRect[i].width; //��õ�i����Ӿ��εĿ��
        h0 = boundRect[i].height; //��õ�i����Ӿ��εĸ߶�

        //�������
        double Area = contourArea(contours[i]);//�����i�����������
        AreaAll = Area + AreaAll;

        //ɸѡ
        if (w0 > 140 && h0 > 140)
            rectangle(result, Point(x0, y0), Point(x0 + w0, y0 + h0), Scalar(0, 255, 0), 2, 8); //���Ƶ�i����Ӿ���
            //�������
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
    if (!cap.isOpened()) //�����Ƿ�ɹ�
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
                background = frame.clone(); //��ȡ��һ֡Ϊ����֡

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
