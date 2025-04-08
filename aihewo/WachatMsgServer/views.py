import json
import shutil
import time
import zipfile
from .itools import readsqlQlite
from .itools.decrypt import run
import os.path
from djangoProject.settings import BASE_DIR
from WachatMsgServer.itools.WXDateBase import close_db,init_db
import datetime
import re
import os
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from .itools.write_tugraph import Tugraph
from .models import PhoneData, ChartData



def clear_folder(folder_path):
    close_db()
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')


def check_and_execute(path, method,phonenumber,WXKey):
    while True:
        if any(file.startswith('MSG') for file in os.listdir(path)):
            return method(PhoneNumber=phonenumber,key=WXKey)
        time.sleep(60)

def example_method(PhoneNumber,key):
    return readsqlQlite.save_contacts_and_messages(PhoneNumber=PhoneNumber,key=key)

def get_uploaded_zip_name(file_path):
    return os.path.basename(file_path)


def get_extracted_file_names(zip_file_path, extract_to):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

    extracted_file_name = get_uploaded_zip_name(zip_file_path)
    return extracted_file_name

def sanitize_filename(filename):
    # 使用正则表达式移除文件名中的非数字字符
    return re.sub(r'\W+', '', filename)

def get_formatted_current_time():
    current_time = datetime.datetime.now()
    # 确保格式化时间不包含任何无效字符
    formatted_time = current_time.strftime("%Y-%m-%d_%H-%M-%S")
    return formatted_time


def create_save_dir(phonenumber, formatted_time,wx_key):
    # 使用UTF-8编码来确保文件名和路径的正确性
    phonenumber = phonenumber.encode('utf-8').decode('utf-8')
    formatted_time = formatted_time.encode('utf-8').decode('utf-8')

    save_dir = os.path.join(os.getcwd(), 'WXDates', f"{phonenumber}-{formatted_time}-{wx_key}")
    os.makedirs(save_dir, exist_ok=True)

    return save_dir

@csrf_exempt
def upload_file(request):
    try:
        if request.method == 'POST':
            try:
                key = request.POST.get('key')
                phonenumber = request.POST.get('phonenumber')
                uploaded_file = request.FILES.get('file')

                if not key or not phonenumber or not uploaded_file:
                    return JsonResponse({'error': 'Missing required parameters'}, status=400)

                print ("===============文件上传成功================")
                formatted_time = get_formatted_current_time()
                save_dir = create_save_dir(phonenumber, formatted_time, key)

                file_path = os.path.join(save_dir, uploaded_file.name)
                with open(file_path, 'wb') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)
                print("===============文件解压缩成功================")
                database_dir = os.path.join(BASE_DIR, 'WachatMsgServer', 'DateBase')
                file_name = get_extracted_file_names(file_path, database_dir).split('.zip')[0]

                WXdb_path = os.path.join(BASE_DIR, 'WachatMsgServer', 'DateBase', file_name, 'Msg')
                db_path = os.path.join(BASE_DIR, 'WachatMsgServer', 'itools', 'WXDateBase', 'Database', 'Msg', formatted_time, file_name)

                run(key, WXdb_path, db_path)
                init_db(db_path)
                print("===============文件解密成功================")

                contact_info_list = check_and_execute(db_path, example_method, phonenumber, key)
                print("===============文件存取mysql数据库成功================")
                clear_folder(os.path.join(BASE_DIR, 'WachatMsgServer', 'itools', 'WXDateBase', 'Database', 'Msg'))
                clear_folder(os.path.join(BASE_DIR, 'WachatMsgServer', 'DateBase'))
                clear_folder(os.path.join(BASE_DIR, 'WXDates'))
                print("===============文件夹清理成功================")
                return JsonResponse({'message': 'File uploaded and processed successfully',
                                     'token': contact_info_list},status=200)
            except Exception as e:
            # 捕获所有异常并记录错误信息
                print(f"An error occurred: {e}")
                return JsonResponse({'error': 'Invalid request method'}, status=405)

    except Exception as e:
        # 捕获所有异常并记录错误信息
        print(f"An error occurred: {e}")
        return JsonResponse({'error': 'An internal error occurred'}, status=500)


@csrf_exempt
def check_phone_data(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone')
        if phone_number:
            try:
                # 使用 filter() 方法来筛选 is_valid 为 True 的记录
                phone_data = PhoneData.objects.filter(phone_name=phone_number, is_valid=True).get()
                return JsonResponse({
                    'exists': True,
                    'insert_time': phone_data.insert_time.isoformat()
                })
            except PhoneData.DoesNotExist:
                return JsonResponse({
                    'exists': False,
                    'message': 'No data found for the given phone number.'
                })
        else:
            return JsonResponse({
                'error': 'Phone number is required.'
            }, status=400)
    else:
        return JsonResponse({
            'error': 'Invalid request method.'
        }, status=405)


@csrf_exempt
def get_contacts_by_phone_number(request):
    if request.method == 'GET' or request.method == 'POST':
        phone_number = request.GET.get('phone_number')
        if phone_number:
            try:
                # 通过手机号查询PhoneData对象
                phone_data = PhoneData.objects.get(phone_name=phone_number, is_valid=True)
                # 通过phone_data查询关联的Contact对象
                contacts = Contact.objects.filter(phone_data=phone_data).all()
                user_names = []
                for contact in contacts:
                    user_date_info = {
                        'user_name': contact.user_name,
                        'alias': contact.alias,
                        'type': contact.type,
                        'remark': contact.remark,
                        'nick_name': contact.nick_name,
                        'small_head_img_url': contact.small_head_img_url,
                        'detail': contact.detail,
                        'label_name': contact.label_name,
                        'phone_number': contact.phone_number,
                    }
                    user_names.append(user_date_info)
                # 将联系人列表转换为JSON格式并返回
                return JsonResponse({'message': 'File uploaded and processed successfully',
                                 'date': user_names},status=200)
            except ObjectDoesNotExist:
                # 如果PhoneData对象不存在，返回错误代码
                return JsonResponse({'error': 'Phone number not found'}, status=404)
        else:
            return JsonResponse({'error': 'Phone number is required'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


from.models import Contact, WeChatMessage

@csrf_exempt
def get_wechat_messages_by_contact_username(request):
    if request.method == 'GET':
        contact_username = request.GET.get('user_name')
        if contact_username:
            # 首先，查询出Contact中is_valid为True且user_name等于给定值的记录
            contacts = Contact.objects.filter(is_valid=True, user_name=contact_username)

            # 然后，查询出与这些Contact记录关联的WeChatMessage记录
            wechat_messages = WeChatMessage.objects.filter(Contact_data__in=contacts)
            messages_json = []
            for msg in wechat_messages:
                if msg.my_json_field:
                    # 将查询到的WeChatMessage数据转换为JSON格式
                    messages_json_data = {'id': msg.id, 'user_name': msg.user_name, 'local_id': msg.local_id,
                                          'talker_id': msg.talker_id, 'type': msg.type, 'subtype': msg.subtype,
                                          'is_sender': msg.is_sender, 'create_time': msg.create_time,
                                          'status': msg.status, 'str_content': msg.str_content,
                                          'str_time': msg.str_time, 'msg_svr_id': msg.msg_svr_id,
                                          'compress_content': msg.compress_content,
                                          'display_content': msg.display_content,
                                          'my_json_field': json.loads(msg.my_json_field)}
                else:
                    messages_json_data = {'id': msg.id, 'user_name': msg.user_name, 'local_id': msg.local_id,
                                          'talker_id': msg.talker_id, 'type': msg.type, 'subtype': msg.subtype,
                                          'is_sender': msg.is_sender, 'create_time': msg.create_time,
                                          'status': msg.status, 'str_content': msg.str_content,
                                          'str_time': msg.str_time, 'msg_svr_id': msg.msg_svr_id,
                                          'compress_content': msg.compress_content,
                                          'display_content': msg.display_content,
                                          'my_json_field': {}}

                messages_json.append(messages_json_data)
            return JsonResponse({'messages': messages_json})
        else:
            return JsonResponse({'error': 'Contact username is required.'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def get_contacts_with_messages(request):
    if request.method == 'GET':
        phone_number = request.GET.get('phone_number')
        if not phone_number:
            return JsonResponse({'error': 'Missing phone_number parameter'}, status=400)

        # 使用正确的外键字段进行 select_related 查询
        contacts = Contact.objects.filter(phone_number=phone_number, is_valid=True).select_related('phone_data')
        if not contacts.exists():
            return JsonResponse({'error': 'No matching contacts found'}, status=404)

        user_names = []
        for contact in contacts:
            messages = contact.wechatmessage_set.all()
            if messages.exists():
                user_date_info = {
                    'user_name': contact.user_name,
                    'alias': contact.alias,
                    'type': contact.type,
                    'remark': contact.remark,
                    'nick_name': contact.nick_name,
                    'small_head_img_url': contact.small_head_img_url,
                    'detail': contact.detail,
                    'label_name': contact.label_name,
                    'phone_number': contact.phone_number,
                }
                user_names.append(user_date_info)

        return JsonResponse({'message': 'File uploaded and processed successfully',
                             'data': user_names},status=200)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

@csrf_exempt
def get_chart_data(request):
    user_name = request.GET.get('user_name')  # 从请求中获取用户名参数
    if not user_name:
        return JsonResponse({'error': 'Missing user_name parameter'}, status=400)

    try:
        contact = Contact.objects.get(user_name=user_name, is_valid=True)  # 根据用户名查询 Contact 对象
        chart_data = ChartData.objects.filter(contact=contact).values('chart_data_sender',
                                                                      'chart_data_types',
                                                                      'chart_data_weekday',
                                                                      'chart_data_wordcloud',
                                                                      'keyword_max_num',
                                                                      'total_text_num',
                                                                      'keyword')  # 查询 ChartData 对象并获取指定字段的值
    except Contact.DoesNotExist:
        return JsonResponse({'error': 'Contact not found'}, status=404)

    chart_json = {'chart_data_sender': json.loads(chart_data[0]['chart_data_sender']),
                  'chart_data_types': json.loads(chart_data[0]['chart_data_types']),
                  'chart_data_weekday': json.loads(chart_data[0]['chart_data_weekday']),
                  'chart_data_wordcloud': json.loads(chart_data[0]['chart_data_wordcloud']),
                  'keyword_max_num': json.loads(chart_data[0]['keyword_max_num']),
                      'total_text_num': json.loads(chart_data[0]['total_text_num']),
                      'keyword': chart_data[0]['keyword']}


    return JsonResponse({'message': 'File uploaded and processed successfully',
                         'data': chart_json})

from django.core.paginator import Paginator

@csrf_exempt
def get_wechat_messages_by_contact_username_ten(request):
    if request.method == 'GET':
        contact_username = request.GET.get('user_name')
        if contact_username:
            # 首先，查询出Contact中is_valid为True且user_name等于给定值的记录
            contacts = Contact.objects.filter(is_valid=True, user_name=contact_username)

            # 然后，查询出与这些Contact记录关联的WeChatMessage记录
            wechat_messages = WeChatMessage.objects.filter(Contact_data__in=contacts)

            # 引入分页机制
            paginator = Paginator(wechat_messages, 50)  # 每页显示10条消息
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

            messages_json = []
            for msg in page_obj:
                if msg.my_json_field:
                    # 将查询到的WeChatMessage数据转换为JSON格式
                    messages_json_data = {'id': msg.id, 'user_name': msg.user_name, 'local_id': msg.local_id,
                                          'talker_id': msg.talker_id, 'type': msg.type, 'subtype': msg.subtype,
                                          'is_sender': msg.is_sender, 'create_time': msg.create_time,
                                          'status': msg.status, 'str_content': msg.str_content,
                                          'str_time': msg.str_time, 'msg_svr_id': msg.msg_svr_id,
                                          'compress_content': msg.compress_content,
                                          'display_content': msg.display_content,
                                          'my_json_field': json.loads(msg.my_json_field)}
                else:
                    messages_json_data = {'id': msg.id, 'user_name': msg.user_name, 'local_id': msg.local_id,
                                          'talker_id': msg.talker_id, 'type': msg.type, 'subtype': msg.subtype,
                                          'is_sender': msg.is_sender, 'create_time': msg.create_time,
                                          'status': msg.status, 'str_content': msg.str_content,
                                          'str_time': msg.str_time, 'msg_svr_id': msg.msg_svr_id,
                                          'compress_content': msg.compress_content,
                                          'display_content': msg.display_content,
                                          'my_json_field': {}}
                messages_json.append(messages_json_data)

            return JsonResponse({'messages': messages_json, 'has_next': page_obj.has_next()})
        else:
            return JsonResponse({'error': 'Contact username is required.'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method.'}, status=405)


from django.core.paginator import Paginator
from django.http import JsonResponse


def get_contacts_by_phone_number_ten(request):
    if request.method == 'GET' or request.method == 'POST':
        phone_number = request.GET.get('phone_number')
        if phone_number:
            try:
                # 通过手机号查询PhoneData对象
                phone_data = PhoneData.objects.get(phone_name=phone_number, is_valid=True)
                # 通过phone_data查询关联的Contact对象
                contacts = Contact.objects.filter(phone_data=phone_data).all()

                # 使用Paginator进行分页
                paginator = Paginator(contacts, 15)  # 每页显示10个联系人
                page_number = request.GET.get('page')
                page_obj = paginator.get_page(page_number)

                user_names = []
                for contact in page_obj:
                    user_date_info = {
                        'user_name': contact.user_name,
                        'alias': contact.alias,
                        'type': contact.type,
                        'remark': contact.remark,
                        'nick_name': contact.nick_name,
                        'small_head_img_url': contact.small_head_img_url,
                        'detail': contact.detail,
                        'label_name': contact.label_name,
                        'phone_number': contact.phone_number,
                    }
                    user_names.append(user_date_info)

                # 将当前页的联系人列表转换为JSON格式并返回
                return JsonResponse({'message': 'File uploaded and processed successfully',
                                     'date': user_names,
                                     'has_next': page_obj.has_next()})
            except ObjectDoesNotExist:
                # 如果PhoneData对象不存在，返回错误代码
                return JsonResponse({'error': 'Phone number not found'}, status=404)
        else:
            return JsonResponse({'error': 'Phone number is required'}, status=400)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)

import pandas as pd

@csrf_exempt
def process_form_data(request):
    if request.method == 'POST':
        # 从POST请求中获取表单数据
        neo4j_uri = request.POST.get('NEO4J_URI')
        neo4j_username = request.POST.get('NEO4J_USERNAME')
        neo4j_password = request.POST.get('NEO4J_PASSWORD')
        phone_number = request.POST.get('phonenumber')
        lib_name = request.POST.get('lib_name')

        # 使用正确的外键字段进行 select_related 查询
        contacts = Contact.objects.filter(phone_number=phone_number, is_valid=True).select_related('phone_data')
        if not contacts.exists():
            return JsonResponse({'error': 'No matching contacts found'}, status=404)

        user_names = []
        for contact in contacts:
            messages = contact.wechatmessage_set.all()
            if messages.exists():
                user_date_info = {
                    'user_name': contact.user_name,
                    'alias': contact.alias,
                    'type': contact.type,
                    'remark': contact.remark,
                    'nick_name': contact.nick_name,
                    'small_head_img_url': contact.small_head_img_url,
                    'detail': contact.detail,
                    'label_name': contact.label_name,
                    'phone_number': contact.phone_number,
                }
                user_names.append(user_date_info)

        # data = user_names
        # json_data = json.loads(data)
        Contact_df_resp = pd.DataFrame(user_names)

        uri=neo4j_uri
        user=neo4j_username
        password=neo4j_password
        tugraph = Tugraph(uri, user, password,lib_name)
        tugraph.insert_data(Contact_df_resp,phone_number,phone_number)

        # 通过手机号查询PhoneData对象
        phone_data = PhoneData.objects.get(phone_name=phone_number, is_valid=True)
        # 通过phone_data查询关联的Contact对象
        contacts = Contact.objects.filter(phone_data=phone_data).all()
        user_names = []
        for contact in contacts:
            user_date_info = {
                'user_name': contact.user_name,
                'alias': contact.alias,
                'type': contact.type,
                'remark': contact.remark,
                'nick_name': contact.nick_name,
                'small_head_img_url': contact.small_head_img_url,
                'detail': contact.detail,
                'label_name': contact.label_name,
                'phone_number': contact.phone_number,
            }
            user_names.append(user_date_info)

        Contact_df_resp = pd.DataFrame(user_names)

        uri = neo4j_uri
        user = neo4j_username
        password = neo4j_password
        tugraph = Tugraph(uri, user, password, lib_name)
        tugraph.insert_data(Contact_df_resp, phone_number, phone_number)

        # 返回一个JSON响应，表示数据处理成功
        return JsonResponse({'message': 'Data processed successfully'})
    else:
        # 如果请求方法不是POST，返回一个错误响应
        return JsonResponse({'error': 'Invalid request method'}, status=400)