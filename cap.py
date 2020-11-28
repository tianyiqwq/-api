import cv2
import os


def cap_image(file_path):
    print("=============================================")
    print("=  热键(请在摄像头的窗口使用)：             =")
    print("=  z: 更改存储目录                          =")
    print("=  x: 拍摄图片                              =")
    print("=  q: 退出                                  =")
    print("=============================================")
    # 提醒用户操作字典

    class_name = file_path

    os.mkdir(class_name)

    # 存储

    index = 1
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if cap.isOpened() == 0:
        return -1

    width = 224
    height = 224

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    print(width, height)
    # 设置特定值

    while True:
        ret, frame = cap.read()

        frame = cv2.flip(frame, 1, dst=None)
        # 镜像显示
        cv2.imshow("capture", frame)
        # 显示

        key_input = cv2.waitKey(1) & 0xFF

        if key_input == ord('x'):
            cv2.imwrite("%s/%d.jpeg" % (class_name, index),
                        cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA))
            print("%s: %d 张图片" % (class_name, index))
            index += 1

        if key_input == ord('q'):
            break

        # 退出

    cap.release()
    cv2.destroyAllWindows()
    return index



