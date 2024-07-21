import time
from django.core import signing
import hashlib
import cv2
import numpy as np
import os
import paddle
from paddleocr import PaddleOCR, draw_ocr
from django.conf import settings
from paddlespeech.cli.asr.infer import ASRExecutor
from pathlib import Path
from pydub import AudioSegment
from moviepy.editor import VideoFileClip
import json
import erniebot
from app.models import User
import re

HEADER = {'typ': 'JWP', 'alg': 'default'}
KEY = "editor"
SALT = "hello world"

def encrypt(obj):
    """加密：signing 加密 and Base64 编码"""
    value = signing.dumps(obj, key=KEY, salt=SALT)
    value = signing.b64_encode(value.encode()).decode()
    return value

def decrypt(src):
    """解密：Base64 解码 and signing 解密"""
    src = signing.b64_decode(src.encode()).decode()
    raw = signing.loads(src, key=KEY, salt=SALT)
    return raw

def create_token(account):
    """生成token信息"""
    # 1. 加密头信息
    header = encrypt(HEADER)
    # 2. 构造Payload(有效期14天)
    payload = {"username": account, "iat": time.time(),
               "exp": time.time()+1209600.0}
    payload = encrypt(payload)
    # 3. MD5 生成签名
    md5 = hashlib.md5()
    md5.update(("%s.%s" % (header, payload)).encode())
    signature = md5.hexdigest()
    token = "%s.%s.%s" % (header, payload, signature)
    return token

def get_payload(token):
    """解析 token 获取 payload 数据"""
    payload = str(token).split('.')[1]
    payload = decrypt(payload)
    return payload

def get_username(token):
    """解析 token 获取 username"""
    payload = get_payload(token)
    return payload['username']

def get_exp_time(token):
    """解析 token 获取过期时间"""
    payload = get_payload(token)
    return payload['exp']

def check_token(account, token):
    """验证 token：检查 username 和 token 是否一致且未过期"""
    return get_username(token) == account and get_exp_time(token) > time.time()

def saveFile(request):
    uploaded_file = request.FILES.get("file")
    account = request.META.get('HTTP_ACCOUNT')
    account_directory = os.path.join(settings.MEDIA_ROOT, account)
    if not os.path.exists(account_directory):
        os.makedirs(account_directory)
    # 生成保存文件的路径
    file_path = os.path.join(account_directory, uploaded_file.name)
    with open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    return file_path


ocr = PaddleOCR(use_angle_cls=True, lang="ch")
asr = ASRExecutor()

def handleOCR(img_path):
    result = ocr.ocr(img_path, cls=True)
    ocr_results = ""
    for idx in range(len(result)):
        res = result[idx]
        for line in res:
            ocr_results += line[1][0]
    return ocr_results

def handleVoice(file_path):
    audio = AudioSegment.from_file(file_path)
    audio = audio.set_frame_rate(16000)
    audio = audio.set_sample_width(2)
    audio = audio.set_channels(1)
    audio.export(file_path, format="wav")

    file_name, file_extension = os.path.splitext(file_path)
    file_path = file_name + '.wav'
    result = asr(audio_file=Path(file_path))
    return result

def handleVidio(file_path):
    file_name, file_extension = os.path.splitext(file_path)
    audio_path = file_name + '.wav'
    video = VideoFileClip(file_path)
    audio = video.audio
    audio.write_audiofile(audio_path)

    return handleVoice(audio_path)


def getAIResponse(request, prompt):
    account = request.META.get('HTTP_ACCOUNT')
    question = request.POST.get("question")
    user = User.objects.get(account=account)
    erniebot.api_type = 'aistudio'
    erniebot.access_token = user.accessToken

    response = erniebot.ChatCompletion.create(
        model='ernie-bot',
        messages=[{'role': 'user', 'content': prompt + question}],
    )
    return response

def getCode(text):
    # 正则表达式模式
    pattern = r'`{3}(.*?)`{3}'
    # return "```python\nprint('hello world')\n```"
    # 使用 re.search 查找第一个匹配的结果，使用 re.DOTALL 标志
    match = re.search(pattern, text, re.DOTALL)
    if match:
        # 提取匹配结果中的内容
        return "```" + match.group(1) + "```"
    else:
        return ""

def getJson(text):
    # 正则表达式模式
    pattern = r'`{3}(.*?)`{3}'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        # 提取匹配结果中的内容，去除注释
        result = re.sub(r'//.*$', '', match.group(1)[4:], flags=re.MULTILINE)
        return result
    else:
        return ""

# import fitz  # fitz就是pip install PyMuPDF
# import os
# import cv2
# from paddleocr import PPStructure,save_structure_res
# from paddleocr.ppstructure.recovery.recovery_to_doc import sorted_layout_boxes, convert_info_docx
#
# def pdf2png(pdfPath, baseImagePath):
#     imagePath=os.path.join(baseImagePath,os.path.basename(pdfPath).split('.')[0])
#     if not os.path.exists(imagePath):
#         os.makedirs(imagePath)
#     pdfDoc = fitz.open(pdfPath)
#     totalPage=pdfDoc.page_count
#     for pg in range(totalPage):
#         page = pdfDoc[pg]
#         rotate = int(0)
#         zoom_x = 2
#         zoom_y = 2
#         mat = fitz.Matrix(zoom_x, zoom_y).prerotate(rotate)
#         pix = page.get_pixmap(matrix=mat, alpha=False)
#         pix.save(imagePath + '/' + f'images_{pg+1}.png')
#
#
# # 中文测试图
# table_engine = PPStructure(recovery=True,lang='ch')
#
# image_path = './imgs/demo-scan'
# save_folder = './txt'
# def img2docx(img_path):
#     text=[]
#     imgs=os.listdir(img_path)
#     for img_name in imgs:
#         print(os.path.join(img_path,img_name))
#         img = cv2.imread(os.path.join(img_path,img_name))
#         result = table_engine(img)
#
#         save_structure_res(result, save_folder, os.path.basename(img_path).split('.')[0])
#
#         h, w, _ = img.shape
#         res = sorted_layout_boxes(result, w)
#         convert_info_docx(img, res, save_folder, os.path.basename(img_path).split('.')[0])
#
#         for line in res:
#             line.pop('img')
#             print(line)
#             for pra in line['res']:
#                 text.append(pra['text'])
#             text.append('\n')
#     return text
# print(img2docx())



