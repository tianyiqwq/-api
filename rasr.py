# -*- coding: utf-8 -*-

from huaweicloud_sis.client.rasr_client import RasrClient
from huaweicloud_sis.bean.rasr_request import RasrRequest
from huaweicloud_sis.bean.callback import RasrCallBack
from huaweicloud_sis.bean.sis_config import SisConfig
from huaweicloud_sis.client.hot_word_client import HotWordClient
from huaweicloud_sis.bean.hot_word_request import HotWordRequest
import json
import re
from wav2pcm import *
from audio_record import *
# 鉴权信息
ak = 'AAIKBUI6SHMLDYHLUFKE'  # 用户的ak
sk = 'ayy5pGsRLOixCVH356zXgOzryTwkhPQWPa8i0r5M'  # 用户的sk
region = 'cn-north-4'  # region，如cn-north-4
project_id = '0a8c60868e00f34f2f01c008e37af773'  # 同region一一对应

"""
    todo 请正确填写音频格式和模型属性字符串
    1. 音频格式一定要相匹配.
         例如音频是pcm格式，并且采样率为8k，则格式填写pcm8k16bit
         如果返回audio_format is invalid 说明该文件格式不支持

    2. 音频采样率要与属性字符串的采样率要匹配
         例如格式选择pcm16k16bit，属性字符串却选择chinese_8k_common, 则会返回'audio_format' is not match model
"""

# 实时语音转写参数

audio_format = 'pcm16k16bit'  # 音频支持格式，如pcm8k16bit
property = 'chinese_16k_common'  # 属性字符串，language_sampleRate_domain, 如chinese_8k_common, 采样率要和音频一致

# 热词参数
name = ''  # 创建热词时，需要保证name在此之前没有被创建使用过。如 test1
word_list = list()  # 用于存放热词表。每个热词表最多可以存放1024个热词。如["计算机", "网络"]
vocabulary_id = ''  # 用于更新指定热词表id信息，查询指定热词表id信息，删除指定热词表id信息。使用前要保证热词表id存在，否则就不要使用。


class MyCallback(RasrCallBack):
    """ 回调类，用户需要在对应方法中实现自己的逻辑，其中on_response必须重写 """

    def __init__(self):
        self.response = ''

    def on_open(self):
        """ websocket连接成功会回调此函数 """
        print('websocket connect success')

    def on_start(self, message):
        """
            websocket 开始识别回调此函数
        :param message: 传入信息
        :return: -
        """
        print('webscoket start to recognize, %s' % message)

    def on_response(self, message):
        """
            websockert返回响应结果会回调此函数
        :param message: json格式
        :return: -
        """
        response = (json.dumps(message, indent=2, ensure_ascii=False))
        print(response)
        self.response = response

    def on_end(self, message):
        """
            websocket 结束识别回调此函数
        :param message: 传入信息
        :return: -
        """
        print('websocket is ended, %s' % message)

    def on_close(self):
        """ websocket关闭会回调此函数 """
        print('websocket is closed')

    def on_error(self, error):
        """
            websocket出错回调此函数
        :param error: 错误信息
        :return: -
        """
        print('websocket meets error, the error is %s' % error)


def rasr_detect(path):
    """ 实时语音转写demo """
    # step1 初始化RasrClient, 暂不支持使用代理
    my_callback = MyCallback()
    config = SisConfig()
    # 设置连接超时,默认是10
    config.set_connect_timeout(10)
    # 设置读取超时, 默认是10
    config.set_read_timeout(10)
    # 设置connect lost超时，一般在普通并发下，不需要设置此值。默认是4
    config.set_connect_lost_timeout(4)
    # websocket暂时不支持使用代理
    rasr_client = RasrClient(ak=ak, sk=sk, use_aksk=True, region=region, project_id=project_id, callback=my_callback,
                             config=config)

    # step2 构造请求
    request = RasrRequest(audio_format, property)
    # 所有参数均可不设置，使用默认值
    request.set_add_punc('yes')  # 设置是否添加标点， yes or no， 默认no
    request.set_vad_head(10000)  # 设置有效头部， [0, 60000], 默认10000
    request.set_vad_tail(500)  # 设置有效尾部，[0, 3000]， 默认500
    request.set_max_seconds(30)  # 设置一句话最大长度，[0, 60], 默认30
    request.set_interim_results('no')  # 设置是否返回中间结果，yes or no，默认no
    request.set_digit_norm('no')  # 设置是否将语音中数字转写为阿拉伯数字，yes or no，默认yes
    request.set_vocabulary_id('039061ac-d8f7-44e1-b2f5-6cb1c4b82c6a')  # 设置热词表id，若不存在则不填写，否则会报错

    # step3 选择连接模式
    rasr_client.short_stream_connect(request)       # 流式一句话模式
    # rasr_client.sentence_stream_connect(request)    # 实时语音转写单句模式
    # rasr_client.continue_stream_connect(request)  # 实时语音转写连续模式

    # step4 发送音频
    rasr_client.send_start()
    # 连续模式下，可多次发送音频，发送格式为byte数组
    with open(path, 'rb') as f:
        data = f.read()
        rasr_client.send_audio(data)  # 可选byte_len和sleep_time参数，建议使用默认值
    rasr_client.send_end()

    # step5 关闭客户端，使用完毕后一定要关闭，否则服务端20s内没收到数据会报错并主动断开。
    rasr_client.close()

    response_text = re.findall(r'"text": "(.*?)。', str(my_callback.response))
    print(response_text)
    return response_text


def hot_word_example(name):
    """
        1. 热词使用包含创建、更新、查询、删除等，一个用户可以创建多个热词表，一个热词表可以包含多个热词。一个vocabulary_id对应一个热词表。
        2. 目前支持一个用户最多创建10个热词表，一个热词表最多包含1024个热词。
        3. 热词可在一句话识别、录音文件识别、实时语音转写使用。例如将地名和人名作为热词，则语音可以准确识别出人名和地名。
    :return: 无
    """
    # 初始化客户端
    config = SisConfig()
    config.set_connect_timeout(10)  # 设置连接超时
    config.set_read_timeout(10)  # 设置读取超时
    # 设置代理，使用代理前一定要确保代理可用。 代理格式可为[host, port] 或 [host, port, username, password]
    # config.set_proxy(proxy)
    hot_word_client = HotWordClient(ak, sk, region, project_id, sis_config=config)

    # option 1 创建热词表
    word_list.append('test')
    create_request = HotWordRequest(name, word_list)
    # 可选，热词语言，目前仅支持中文 chinese_mandarin。
    create_request.set_language('chinese_mandarin')
    # 可选，热词表描述信息
    create_request.set_description('test')
    create_result = hot_word_client.create(create_request)
    # 返回结果为json格式
    print('成功创建热词表')
    print(json.dumps(create_result, indent=2, ensure_ascii=False))
    """
    # option 2 根据热词表id 更新热词表。新的热词表会替换旧的热词表。使用前需确保热词表id已存在。
    word_list.append('进入系统')
    update_request = HotWordRequest('test2', word_list)
    update_result = hot_word_client.update(update_request, vocabulary_id)
    # 返回结果为json格式
    print('成功更新热词表', vocabulary_id)
    print(json.dumps(update_result, indent=2, ensure_ascii=False))
    """
    # option 3 查看热词表列表
    query_list_result = hot_word_client.query_list()
    print(json.dumps(query_list_result, indent=2, ensure_ascii=False))

    # option 4 根据热词表id查询具体热词表信息，使用前需确保热词表id已存在。
    query_result = hot_word_client.query_by_vocabulary_id(vocabulary_id)
    print(json.dumps(query_result, indent=2, ensure_ascii=False))

    # option 5 根据热词表id删除热词表，使用前需确保热词表id已存在。
    delete_result = hot_word_client.delete(vocabulary_id)
    if delete_result is None:
        print('成功删除热词表', vocabulary_id)
    else:
        print(json.dumps(delete_result, indent=2, ensure_ascii=False))


def audio2text(audio_record_file, record_time):
    audio_record(audio_record_file, record_time)

    pcm_file = wav_to_pcm(audio_record_file)

    audio_text = rasr_detect(pcm_file)

    return audio_text
