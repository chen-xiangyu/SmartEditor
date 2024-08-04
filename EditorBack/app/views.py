from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password, check_password
from app.models import User
from app.utils import create_token
from app import utils
from app import models
import json
from django.core.files.base import ContentFile
from PIL import Image
import os
from django.conf import settings
from pydub import AudioSegment
from moviepy.editor import VideoFileClip
# Create your views here.

# erniebot.api_type = 'aistudio'
# erniebot.access_token = 'b3d27cfee042938a09a088dfd302180c3467118f'

languageNote = """
    注意，你应该先判断一下这句话是中文还是英文，如果是中文，请给我返回中文的内容，
    如果是英文，请给我返回英文内容，只需要返回内容即可，不需要告知我是中文还是英文：
"""

formatNote = """
    注意，你生成的文本要符合相应的排版，如标题类型、列表、缩进、换行等，并且能够在 tiptap 编辑器中渲染（markdown形式）：
"""

@csrf_exempt
def signUp(request):
    # 注册
    if request.method == "POST":
        account = request.POST.get("account")
        password = request.POST.get("password")
        print(account, password)
        if User.objects.filter(account=account).exists():
            return JsonResponse({"status": False, 'etype': 1, "error": "账号已存在"})

        hashed_password = make_password(password)
        user = User(name="user" + account, account=account, password=hashed_password, coins=20)
        user.save()

        empty_file = ContentFile("".encode('utf-8'))
        empty_file.name = "undefined.html"  # 指定文件名
        first_file = models.File(
            name="undefined",
            creator=user,
            file=empty_file,
        )
        first_file.save()
        params = {
            "status": True,
            "message": "注册成功",
            "account": user.account,
            "token": create_token(user.account),
        }
        return JsonResponse(params)
    return JsonResponse({"status": False, "etype": 0, "error": "请求方法错误"})

@csrf_exempt
def signIn(request):
    # 登录
    if request.method == "POST":
        account = request.POST.get("account")
        password = request.POST.get("password")
        print(account, password)
        if not User.objects.filter(account=account).exists():
            return JsonResponse({"status": False, "etype": 1, "error": "账号不存在"})

        user = User.objects.get(account=account)
        if check_password(password, user.password):
            params = {
                "status": True,
                "message": "登录成功",
                "account": user.account,
                "token": create_token(user.account),
            }
            return JsonResponse(params)
        else:
            return JsonResponse({"status": False, "etype": 2, "error": "密码错误"})
    return JsonResponse({"status": False, "etype": 0, "error": "请求方法错误"})

@csrf_exempt
def getUserProfile(request):
    if request.method == "POST":
        account = request.META.get('HTTP_ACCOUNT')
        user = User.objects.get(account=account)
        params = {
            "status": True,
            "account": account,
            "accessToken": user.accessToken,
        }
        return JsonResponse(params)
    return JsonResponse({"status": False, "etype": 0, "error": "请求方法错误"})


@csrf_exempt
def setAccessToken(request):
    if request.method == "POST":
        account = request.META.get('HTTP_ACCOUNT')
        access_token = request.POST.get('accessToken')

        user = User.objects.get(account=account)
        user.accessToken = access_token
        user.save()

        params = {
            "status": True,
            "message": "成功设置访问令牌",
        }
        return JsonResponse(params)
    return JsonResponse({"status": False, "etype": 0, "error": "请求方法错误"})\

@csrf_exempt
def modifyPassword(request):
    if request.method == "POST":
        account = request.META.get('HTTP_ACCOUNT')
        old_password = request.POST.get("oldPassword")
        new_password = request.POST.get("newPassword")
        # print(old_password, new_password)
        if not User.objects.filter(account=account).exists():
            return JsonResponse({"status": False, "etype": 1, "error": "账号不存在"})

        user = User.objects.get(account=account)
        if check_password(old_password, user.password):
            hashed_password = make_password(new_password)
            user.password = hashed_password
            user.save()
            print(hashed_password)
            params = {
                "status": True,
                "message": "成功修改密码",
            }
            return JsonResponse(params)
        else:
            return JsonResponse({"status": False, "etype": 2, "error": "密码错误"})
    return JsonResponse({"status": False, "etype": 0, "error": "请求方法错误"})

@csrf_exempt
def translate(request):
    try:
        if request.method == "POST":
            prompt = '''
                请帮我翻译以下内容，在翻译之前，想先判断一下这个内容是不是中文，
                如果是中文，则翻译问英文，如果是其他语言，则需要翻译为中文，注意，
                你只需要返回翻译的结果，不需要对此进行任何解释，不需要除了翻译结果以外的其他任何内容：
            '''
            response = utils.getAIResponse(request, prompt)
            return JsonResponse({"status": True, "answer": response.get_result()})
            # return JsonResponse({"status": True, "answer": "AI的答案"})
    except Exception as e:
        return JsonResponse({"status": False, "error": "请求方法错误"})


@csrf_exempt
def abstract(request):
    try:
        if request.method == "POST":
            prompt = "请帮我总结以下内容(就是做摘要)，并直接返回总结的结果，" + languageNote
            response = utils.getAIResponse(request, prompt)
            return JsonResponse({"status": True, "answer": response.get_result()})
    except Exception as e:
        return JsonResponse({"status": False, "error": "请求方法错误"})

@csrf_exempt
def decorate(request):
    try:
        if request.method == "POST":
            prompt = "请帮我修饰以下内容，并直接返回修饰后的结果，" + languageNote
            response = utils.getAIResponse(request, prompt)
            return JsonResponse({"status": True, "answer": response.get_result()})
    except Exception as e:
        return JsonResponse({"status": False, "error": "请求方法错误"})

@csrf_exempt
def continueWrite(request):
    try:
        if request.method == "POST":
            prompt = "请帮我续写以上内容，发挥你的想象力，添加更多细节，并直接返回续写的结果，" + languageNote
            response = utils.getAIResponse(request, prompt)
            return JsonResponse({"status": True, "answer": response.get_result()})
    except Exception as e:
        return JsonResponse({"status": False, "error": "请求方法错误"})

@csrf_exempt
def rewrite(request):
    try:
        if request.method == "POST":
            prompt = "请帮我检查下面这段话的语法和内容，修改其中的病句（或者不合适的地方），并直接返回改正后的结果，" + languageNote
            response = utils.getAIResponse(request, prompt)
            return JsonResponse({"status": True, "answer": response.get_result()})
    except Exception as e:
        return JsonResponse({"status": False, "error": "请求方法错误"})

@csrf_exempt
def improveWrite(request):
    try:
        if request.method == "POST":
            prompt = "请帮我改进以下内容，对其进行优化，并直接返回改进后的结果，" + languageNote
            response = utils.getAIResponse(request, prompt)
            return JsonResponse({"status": True, "answer": response.get_result()})
    except Exception as e:
        return JsonResponse({"status": False, "error": "请求方法错误"})

@csrf_exempt
def summarize(request):
    try:
        if request.method == "POST":
            prompt = "请帮我总结以下内容，并直接返回总结的结果" + languageNote
            response = utils.getAIResponse(request, prompt)
            return JsonResponse({"status": True, "answer": response.get_result()})
    except Exception as e:
     return JsonResponse({"status": False, "error": "请求方法错误"})

@csrf_exempt
def analysis(request):
    try:
        if request.method == "POST":
            prompt = "请帮我分析以下内容（依照内容选择一个最合适的角度进行分析即可），并直接返回分析的结果" + languageNote
            response = utils.getAIResponse(request, prompt)
            return JsonResponse({"status": True, "answer": response.get_result()})
    except Exception as e:
        return JsonResponse({"status": False, "error": "请求方法错误"})

@csrf_exempt
def useOCR(request):
    try:
        if request.method == "POST":
            file_path = utils.saveFile(request)
            account = request.META.get('HTTP_ACCOUNT')
            user = User.objects.get(account=account)
            user.coins -= 1
            user.save()
            return JsonResponse({"status": True, "answer": utils.handleOCR(file_path)})
            # return JsonResponse({"status": True, "answer": "ok"})
    except Exception as e:
        return JsonResponse({"status": False, "error": "请求方法错误"})


@csrf_exempt
def voiceRecognise(request):
    try:
        if request.method == "POST":
            file_path = utils.saveFile(request)
            audio = AudioSegment.from_file(file_path)
            if len(audio) > 40000:
                return JsonResponse({"status": False, "error": "请求方法错误"})
            account = request.META.get('HTTP_ACCOUNT')
            user = User.objects.get(account=account)
            user.coins -= 1
            user.save()
            return JsonResponse({"status": True, "answer": utils.handleVoice(file_path)})
    except Exception as e:
        return JsonResponse({"status": False, "error": "请求方法错误"})

@csrf_exempt
def videoRecognise(request):
    try:
        if request.method == "POST":
            file_path = utils.saveFile(request)
            video = VideoFileClip(file_path)
            audio = video.audio
            if audio.duration > 40:
                return JsonResponse({"status": False, "error": "请求方法错误"})
            account = request.META.get('HTTP_ACCOUNT')
            user = User.objects.get(account=account)
            user.coins -= 1
            user.save()
            return JsonResponse({"status": True, "answer": utils.handleVidio(file_path)})
    except Exception as e:
        return JsonResponse({"status": False, "error": "请求方法错误"})


@csrf_exempt
def projectDocument(request):
    try:
        if request.method == "POST":
            prompt = """
                假设你是一个大学生，正在参加学校组织的大学生创新创业项目，下面就是关于项目的简介，请你根据下面的内容，
                写一份详细的项目申请书文档，内容包括：项目背景与意义、项目目标与预期成果、研究内容与方法（理论依据）、
                创新点、技术路线与实施计划等，
            """ + formatNote
            response = utils.getAIResponse(request, prompt)
            return JsonResponse({"status": True, "answer": response.get_result()})
    except Exception as e:
        return JsonResponse({"status": False, "error": "请求方法错误"})

@csrf_exempt
def codeEdit(request):
    try:
        if request.method == "POST":
            prompt = """
               假设你是一个程序员，请根据下面的需求和语言写代码，如果用户没有指定使用的语言，就写Python代码，
               可以在关键代码和重要变量（如参数等）的旁边加上注释，将代码写在markdown的代码块中，
               除了代码块不要给我任何其他的内容，将所有代码都生成完毕再将结果返回给我
           """
            response = utils.getAIResponse(request, prompt)
            code = utils.getCode(response.get_result())
            return JsonResponse({"status": True, "answer": code if code != "" else response.get_result() })
    except Exception as e:
        return JsonResponse({"status": False, "error": "请求方法错误"})

@csrf_exempt
def makeBar(request):
    try:
        if request.method == "POST":
            # print(request.POST.get("question"))
            # prompt = """
            #     假设你正在使用echarts，请你根据下面用户输入的内容和数据，生成一份类型为 EChartsOption 的配置数据
            #     图表的类型为柱状图，图中元素不要相互遮挡，最左侧和最右侧的元素不要超出边界和坐标轴，留一下段距离
            #     不需要说明如何使用，只要配置项，直接在 {} 中写配置项，放在markdown代码块（json格式，其中不要加任何注释 // ）中，
            # """
            prompt = """
                假设你正在使用echarts，请你根据下面用户输入的内容和数据，生成一份类型为 EChartsOption 的配置数据，
                图表的类型为柱状图，不需要说明如何使用，只要配置项，直接在 {} 中写配置项，放在markdown代码块，
                json 文件的格式，
            """
            response = utils.getAIResponse(request, prompt)
            print(response.get_result())
            print(json.loads(utils.getJson(response.get_result())))
            return JsonResponse({"status": True, "answer": json.loads(utils.getJson(response.get_result()))})
        # return JsonResponse({"status": True, "answer": "ok"})
    except Exception as e:
        return JsonResponse({"status": False, "error": "请求方法错误"})

@csrf_exempt
def makePie(request):
    try:
        if request.method == "POST":
            prompt = """
                假设你正在使用echarts，请你根据下面用户输入的内容和数据，生成一份类型为 EChartsOption 的配置数据，
                图表的类型为饼图，不需要说明如何使用，只要配置项，直接在 {} 中写配置项，放在markdown代码块，
                json 文件的格式，
            """
            response = utils.getAIResponse(request, prompt)
            return JsonResponse({"status": True, "answer": json.loads(utils.getJson(response.get_result()))})
    except Exception as e:
        return JsonResponse({"status": False, "error": "请求方法错误"})

@csrf_exempt
def makeLine(request):
    try:
        if request.method == "POST":
            prompt = """
                假设你正在使用echarts，请你根据下面用户输入的内容和数据，生成一份类型为 EChartsOption 的配置数据，
                图表的类型为折线图，不需要说明如何使用，只要配置项，直接在 {} 中写配置项，放在markdown代码块，
                请注意json 文件的格式，不要写错，
            """
            response = utils.getAIResponse(request, prompt)
            return JsonResponse({"status": True, "answer": json.loads(utils.getJson(response.get_result()))})
    except Exception as e:
        return JsonResponse({"status": False, "error": "请求方法错误"})

@csrf_exempt
def makeScatter(request):
    try:
        if request.method == "POST":
            prompt = """
                假设你正在使用echarts，请你根据下面用户输入的内容和数据，生成一份类型为 EChartsOption 的配置数据，
                图表的类型为散点图，不需要说明如何使用，只要配置项，直接在 {} 中写配置项，放在markdown代码块，
                请注意json文件的格式，不要写错，不要在json对象中写注释，数据结构类似这样，
                option = {
                  xAxis: {},
                  yAxis: {},
                  series: [
                    {
                      symbolSize: 20,
                      data: [
                        [10.0, 8.04],
                        [8.07, 6.95],
                        [13.0, 7.58],
                        [9.05, 8.81]
                      ],
                      type: 'scatter'
                    }
                  ]
                };
            """
            response = utils.getAIResponse(request, prompt)
            return JsonResponse({"status": True, "answer": json.loads(utils.getJson(response.get_result()))})
    except Exception as e:
        return JsonResponse({"status": False, "error": "请求方法错误"})

@csrf_exempt
def makeMindMap(request):
    try:
        if request.method == "POST":
            prompt = """
                假设你正在使用Mind elixir，请你根据下面用户输入的内容，生成一份类型为 MindElixirData 的配置数据，
                这份配置数据是思维导图的初始数据，等待所有数据全部生成再将结果返回，思维导图的项不要超过15个，
                数据结构类似这样：            {
                                              nodeData: {
                                                id: 'root',
                                                topic: 'root',
                                                children: [
                                                  {
                                                    id: 'sub1',
                                                    topic: 'sub1',
                                                    children: [
                                                      {
                                                        id: 'sub2',
                                                        topic: 'sub2',
                                                      },
                                                    ],
                                                  },
                                                ],
                                              },
                                            }，
                不需要说明如何使用，只要配置项，直接在 {} 中写配置项，放在markdown代码块（json格式，其中不要加任何注释 // ）中，
            """
            response = utils.getAIResponse(request, prompt)
            # print(response.get_result())
            # print(json.loads(utils.getJson(response.get_result())))
            return JsonResponse({"status": True, "answer": json.loads(utils.getJson(response.get_result()))})
    except Exception as e:
        return JsonResponse({"status": False, "error": "请求方法错误"})


@csrf_exempt
def autoTypography(request):
    try:
        if request.method == "POST":
            # print(request.POST.get("question"))
            prompt = """
                你是一个乐于助人的markdown排版专家，请你将以下文本按照markdown形式排版，
                包括但不限于从一级开始设置标题等级，设置字号，设置加粗等修改，
                注意不要输出除markdown代码之外的任何内容，也不要对原文本的内容进行删减，只修改为markdown格式！
            """
            response = utils.getAIResponse(request, prompt)
            return JsonResponse({"status": True, "answer": response.get_result()})
    except Exception as e:
        return JsonResponse({"status": False, "error": "请求方法错误"})


@csrf_exempt
def personResume(request):
    try:
        if request.method == "POST":
            prompt = """
                假设你是一个求职者，正在编写你的个人简历，下面就是你的个人简介、工作经验等信息，请你根据下面的内容，
                写一份详细的个人简历，内容包括但不限于：个人信息，职业目标，教育背景，工作经验，技能，项目经验等，
                可以对信息进行适当的扩展，注意排版（markdown格式），默认是中文简历，如果要求英文，则返回英文简历
            """ + formatNote
            response = utils.getAIResponse(request, prompt)
            return JsonResponse({"status": True, "answer": response.get_result()})
    except Exception as e:
        return JsonResponse({"status": False, "error": "请求方法错误"})

@csrf_exempt
def commonUse(request):
    try:
        if request.method == "POST":
            prompt = """
                下面是用户的需求（或者问题等），请给出你的建议（或者解决方案等），
            """ + formatNote
            response = utils.getAIResponse(request, prompt)
            return JsonResponse({"status": True, "answer": response.get_result()})
    except Exception as e:
        return JsonResponse({"status": False, "error": "请求方法错误"})

@csrf_exempt
def testReport(request):
    try:
        if request.method == "POST":
            prompt = """
                假设你是一个研究员，正在做一项实验，因此你需要写一份实验报告，下面就是你的实验内容和结果，
                写一份详细的实验报告，内容包括但不限于：实验目的，实验环境，实验材料和方法，实验结果，分析，结论，参考文献等，
                可以对信息进行适当的扩展，注意排版（markdown格式），默认是中文报告，如果要求英文，则返回英文报告
            """ + formatNote
            response = utils.getAIResponse(request, prompt)
            return JsonResponse({"status": True, "answer": response.get_result()})
    except Exception as e:
        return JsonResponse({"status": False, "error": "请求方法错误"})

@csrf_exempt
def smartTable(request):
    try:
        if request.method == "POST":
            prompt = """
                请你根据下面的要求和数据，制作一个markdown形式的表格，并将表格用代码块进行包裹，代码块只能包含表格，
                不能有其他内容，可以根据情况对表格的形式和内容进行适当的扩展：
            """
            response = utils.getAIResponse(request, prompt)
            return JsonResponse({"status": True, "answer": utils.getTable(response.get_result())})
    except Exception as e:
        return JsonResponse({"status": False, "error": "请求方法错误"})

@csrf_exempt
def getCatalog(request):
    if request.method == "POST":
        account = request.META.get('HTTP_ACCOUNT')
        user = User.objects.get(account=account)

        files = models.File.objects.filter(creator=user)
        filename_list = [{"id": file.id, "name": file.name} for file in files]

        if files.exists():
            latest_file = files.order_by('-created_time').first()
            current_file_content = latest_file.file.read().decode('utf-8')  # 读取文件内容并解码为字符串
            current_file_id = latest_file.id
        else:
            current_file_content = ""
            current_file_id = 0

        params = {
            "status": True,
            "filenameList": filename_list,
            "currentFile": current_file_content,
            "currentFileID": current_file_id,
        }
        return JsonResponse(params)
    return JsonResponse({"status": False, "error": "请求方法错误"})

@csrf_exempt
def updateFile(request):
    if request.method == "POST":
        # print(request.POST)
        file_id = request.POST.get("id")
        content = request.POST.get("content")

        current_file = models.File.objects.get(id=file_id)
        #
        # new_file = ContentFile(content.encode('utf-8'))
        # new_file.name = current_file.name + ".html"  # 指定文件名
        # current_file.file = new_file
        # current_file.save()
        # 更新文件内容
        file_path = current_file.get_file_path()
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        current_file.save()  # 更新文件的修改时间等
        params = {
            "status": True,
            "message": "成功更新文件",
        }
        return JsonResponse(params)
    return JsonResponse({"status": False, "error": "请求方法错误"})

@csrf_exempt
def createNewFile(request):
    if request.method == "POST":
        account = request.META.get('HTTP_ACCOUNT')
        filename = request.POST.get("filename")
        user = User.objects.get(account=account)

        empty_file = ContentFile("".encode('utf-8'))
        empty_file.name =  filename + ".html"  # 指定文件名
        new_file = models.File(
            name=filename,
            creator=user,
            file=empty_file,
        )
        new_file.save()
        params = {
            "status": True,
            "message": "成功新建文件",
        }
        return JsonResponse(params)
    return JsonResponse({"status": False, "error": "请求方法错误"})

@csrf_exempt
def getCurrentFile(request):
    if request.method == "POST":
        file_id = request.POST.get("id")
        current_file = models.File.objects.filter(id=file_id).first()
        current_file_content = current_file.file.read().decode('utf-8')  # 读取文件内容并解码为字符串

        params = {
            "status": True,
            "content": current_file_content,
        }
        return JsonResponse(params)
    return JsonResponse({"status": False, "error": "请求方法错误"})

@csrf_exempt
def renameFile(request):
    if request.method == "POST":
        file_id = request.POST.get("id")
        new_filename = request.POST.get("filename")

        current_file = models.File.objects.filter(id=file_id).first()
        current_file.name = new_filename
        current_file.save()

        params = {
            "status": True,
            "message": "成功修改文件名",
        }
        return JsonResponse(params)
    return JsonResponse({"status": False, "error": "请求方法错误"})

@csrf_exempt
def deleteFile(request):
    if request.method == "POST":
        file_id = request.POST.get("id")

        delete_file = models.File.objects.filter(id=file_id).first()
        delete_file_path = delete_file.get_file_path()
        if os.path.exists(delete_file_path):
            os.remove(delete_file_path)
        delete_file.delete()

        params = {
            "status": True,
            "message": "成功删除文件",
        }
        return JsonResponse(params)
    return JsonResponse({"status": False, "error": "请求方法错误"})

@csrf_exempt
def getCoins(request):
    if request.method == "GET":
        account = request.META.get('HTTP_ACCOUNT')
        user = User.objects.get(account=account)
        params = {
            "status": True,
            "coins": user.coins,
        }
        return JsonResponse(params)
    return JsonResponse({"status": False, "etype": 0, "error": "请求方法错误"})

@csrf_exempt
def recharge(request):
    if request.method == "POST":
        account = request.META.get('HTTP_ACCOUNT')
        # print(request.POST)
        amount = request.POST.get('amount')
        user = User.objects.get(account=account)
        user.coins += int(amount)
        user.save()

        params = {
            "status": True,
            "message": "充值成功",
            "coins": user.coins,
        }
        return JsonResponse(params)
    return JsonResponse({"status": False, "etype": 0, "error": "请求方法错误"})