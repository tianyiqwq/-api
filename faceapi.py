# -*- coding:utf-8 -*-
import requests
import base64
import re
from cap import *
project_id = "0a8c60868e00f34f2f01c008e37af773"
region_url = "cn-north-4.myhuaweicloud.com"
userid = 'hw71399210'
password = 'Wyx20010404'
region = 'cn-north-4'
model_url ='https://8f361d579b054dd8bf57e0901026a0f7.apig.cn-north-4.huaweicloudapis.com/v1/infers/538ef43e-dc8a-4d32-bfe8-f3c84c1aeb3a'
class API:

    def __init__(self, name, password, region):
        """token获取"""
        IAMurl = 'https://iam.'+region_url+'/v3/auth/tokens?nocatalog=true'
        data = {
            "auth": {
                "identity": {
                    "methods": [
                        "password"
                    ],
                    "password": {
                        "user": {
                            "name": name,
                            "password": password,
                            "domain": {
                                "name": name
                            }
                        }
                    }
                },
                "scope": {
                    "project": {
                        "name": region
                    }
                }
            }
        }

        response = requests.post(IAMurl, json=data)
        self.Token = str(response.headers["X-Subject-Token"])

        print(response.headers)


class face(API):

    def __init__(self, name, password, region):
        API.__init__(self, name, password, region)

    def subscribe(self):
        """人脸识别检测接口状态"""
        faceurl = 'https://face.'+region_url+'/v1/'+project_id+'/subscribe'
        headers = {

            'X-Auth-Token': self.Token,

        }
        response = requests.get(faceurl, headers=headers)
        print(response.text)
        return response.text

    def live_detect(self, image_url):
        """活体检测"""

        live_detect_url = 'https://face.'+region_url+'/v1/'+project_id+'/live-detect-face'

        headers = {
            "X-Auth-Token": self.Token,
            "Content-Type": "application/json"
        }

        f = open(image_url, 'rb')
        image_base64 = str(base64.b64encode(f.read()), "utf-8")

        data = {

            "image_base64": image_base64

        }

        response = requests.post(live_detect_url, headers=headers, json=data)
        print(response.text)
        return response.text

    def live_compare(self, image1_url, image2_url):
        """人脸比对"""

        live_detect_url = 'https://face.'+region_url+'/v1/'+project_id+'/face-compare'

        headers = {
            "X-Auth-Token": self.Token,
            "Content-Type": "application/json"
        }

        f = open(image1_url, 'rb')
        image1_base64 = str(base64.b64encode(f.read()), "utf-8")
        f = open(image2_url, 'rb')
        image2_base64 = str(base64.b64encode(f.read()), "utf-8")

        data = {

            "image1_base64": image1_base64,
            "image2_base64": image2_base64

        }

        response = requests.post(live_detect_url, headers=headers, json=data)
        print(response.text)
        return response.text

    def new_face_database(self, database_name):
        """新建人脸库"""

        url = 'https://face.'+region_url+'/v2/'+project_id+'/face-sets'

        headers = {
            "X-Auth-Token": self.Token,
            "Content-Type": "application/json"
        }

        data = {

            "face_set_name": database_name

        }

        response = requests.post(url, headers=headers, json=data)
        print(response.text)
        return response.text

    def search_face_database(self):
        """查询人脸库"""

        url = 'https://face.'+region_url+'/v2/'+project_id+'/face-sets/facedata'

        headers = {
            "X-Auth-Token": self.Token,
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)
        print(response.text)
        return response.text

    def delete_face_database(self, database_name):
        """删除人脸库"""

        url = 'https://face.'+region_url+'/v2/'+project_id+'/face-sets/'+database_name

        headers = {
            "X-Auth-Token": self.Token,
            "Content-Type": "application/json"
        }

        response = requests.delete(url, headers=headers)
        print(response.text)
        return response.text

    def add_face_data(self, image_url):
        """添加人脸"""

        url = 'https://face.'+region_url+'/v2/'+project_id+'/face-sets/facedata/faces'

        headers = {
            "X-Auth-Token": self.Token,
            "Content-Type": "application/json"
        }

        f = open(image_url, 'rb')
        image_base64 = str(base64.b64encode(f.read()), "utf-8")

        data = {

            "image_base64": image_base64

        }

        response = requests.post(url, headers=headers, json=data)
        print(response.text)
        return response.text

    def search_face_data(self, offset, limit):
        """查询人脸数据"""

        url = 'https://face.'+region_url+'/v2/'+project_id+'/face-sets/facedata/faces?' + 'offset=' + str(
            offset) + '&limit=' + str(limit)

        headers = {
            "X-Auth-Token": self.Token,
            "Content-Type": "application/json"
        }

        response = requests.get(url, headers=headers)

        print(response.text)
        return response.text

    def change_face_data(self, face_id, name):
        """更新人脸数据"""

        url = 'https://face.'+region_url+'/v2/'+project_id+'/face-sets/facedata/faces'

        headers = {
            "X-Auth-Token": self.Token,
            "Content-Type": "application/json"
        }

        data = {

            "face_id": face_id,
            "external_image_id": name

        }

        response = requests.put(url, headers=headers, json=data)
        print(response.text)
        return response.text

    def delete_face_data(self, face_id):
        """删除人脸"""

        url = 'https://face.'+region_url+'/v2/'+project_id+'/face-sets/facedata/faces' \
              '?face_id=' + str(face_id)

        headers = {
            "X-Auth-Token": self.Token,
            "Content-Type": "application/json"
        }

        response = requests.delete(url, headers=headers)
        print(response.text)
        return response.text

    def search_face(self, image_url):
        """搜索人脸"""

        url = 'https://face.'+region_url+'/v2/'+project_id+'/face-sets/facedata/search'

        headers = {
            "X-Auth-Token": self.Token,
            "Content-Type": "application/json"
        }

        f = open(image_url, 'rb')
        image_base64 = str(base64.b64encode(f.read()), "utf-8")

        data = {

            "image_base64": image_base64

        }

        response = requests.post(url, headers=headers, json=data)

        print(response.text)

        response_index = re.findall(r'"similarity":(.*?)}',response.text)
        return response_index

    def modelarts_api(self, filename):
        """modelarts api"""

        url = model_url

        headers = {
            "X-Auth-Token": self.Token,
        }

        files = {'images': open(filename, 'rb')}

        response = requests.post(url, headers=headers, files = files)
        print(response.text)
        response_index = re.findall(r'"(.*?)"', response.text, re.S)
        return response_index




def face_compare(capture_file):
        fapi = face(userid, password, region)

        capture_index = cap_image(capture_file) - 1

        image_file = capture_file + '//' + str(capture_index) + '.jpeg'

        compare_index = fapi.search_face(image_file)

        while capture_index >= 0:

            i_file = capture_file + '//' + str(capture_index) + '.jpeg'

            if os.path.exists(i_file):  # 如果文件存在
                # 删除文件，可使用以下两种方法。
                os.remove(i_file)
                # os.unlink(path)
            else:
                print('no such file:%s' % i_file)

            capture_index -= 1

        if os.path.exists(capture_file):
            os.removedirs(capture_file)

        print(compare_index)
        """相似度判别"""
        for i in range(len(compare_index)):
            if float(compare_index[i]) > 0.95:
                print("识别成功")
                return "识别成功"
        print("识别失败")
        return "识别失败"

