# -*- coding: utf-8 -*-

from .WXDateBase import micro_msg_db,msg_db
from .WXDateBase.hard_link import decodeExtraBuf
from .analysis import my_message_counter
from ..models import Contact, WeChatMessage, PhoneData, ChartData
from datetime import datetime
from django.db.models import Q

# from WXDateBase import micro_msg_db,msg_db
# from WXDateBase.hard_link import decodeExtraBuf
# #from ..models import Contact, WeChatMessage, PhoneData


def process_contacts(PhoneNumber):
    contact_info_lists = micro_msg_db.get_contact()
    # if not contact_info_lists:
    #     #self.load_finish_signal.emit(True)
    #     # QMessageBox.critical(None, "错误", "数据库错误，请重启电脑后重试")
    #     close_db()
    #     import shutil
    #     try:
    #         shutil.rmtree('./WXDateBase/Database/Msg')
    #     except:
    #         pass
    #     return
    # 改为 contact_info_list
    contact_info_listes = []
    for contact_info_list in contact_info_lists:
        # UserName, Alias,Type,Remark,NickName,PYInitial,RemarkPYInitial,ContactHeadImgUrl.smallHeadImgUrl,ContactHeadImgUrl,bigHeadImgUrl,ExtraBuf
        detail = decodeExtraBuf(contact_info_list[9])
        contact_info = {
            'UserName': contact_info_list[0],
            'Alias': contact_info_list[1],
            'Type': contact_info_list[2],
            'Remark': contact_info_list[3],
            'NickName': contact_info_list[4],
            'PhoneNumber': PhoneNumber,
            'smallHeadImgUrl': contact_info_list[7],
            'detail': detail,
            'label_name': contact_info_list[10],
        }
        contact_info_listes.append(contact_info)

    return contact_info_listes

def get_wechat_messages(UserName, num=9999999999):
    #messages = msg_db.get_message_by_num(UserName, num)
    messages = msg_db.get_messages(UserName)
    chat_records = []
    index = 0
    for message in messages:
        try:
            if len(message) == 14:
                chat_record = {
                    'local_id': message[0],
                    'talker_id': message[1],
                    'type': message[2],
                    'subtype': message[3],
                    'is_sender': message[4],
                    'create_time': message[5],
                    'status': message[6],
                    'str_content': message[7],
                    'str_time': message[8],
                    'msg_svr_id': message[9],
                    'bytes_extra': message[10],
                    'compress_content': message[11],
                    'display_content': message[12],
                    'my_json_field': message[13],
                }
            else:
                chat_record = {
                    'local_id': message[0],
                    'talker_id': message[1],
                    'type': message[2],
                    'subtype': message[3],
                    'is_sender': message[4],
                    'create_time': message[5],
                    'status': message[6],
                    'str_content': message[7],
                    'str_time': message[8],
                    'msg_svr_id': message[9],
                    'bytes_extra': message[10],
                    'compress_content': message[11],
                    'display_content': message[12],
                    'my_json_field': {},  # 插入空值
                }
            chat_records.append(chat_record)
            index = index + 1
        except Exception as e:
            print(f"An error occurred at index {index}: {e}")

    return chat_records


import pytz
from datetime import datetime

def convert_to_django_datetime(value):
    # 假设value是一个字符串，表示日期时间
    try:
        # 尝试将字符串转换为datetime对象
        # 如果value是毫秒级的Unix时间戳，需要先转换为秒
        if len(value) == 13:
            value = int(value) / 1000
        # 确保value是字符串类型
        value = str(value)
        dt = datetime.fromtimestamp(float(value))
        # 设置时区为UTC
        utc_datetime = pytz.utc.localize(dt)
        # 返回Django可以理解的日期时间对象
        return utc_datetime
    except ValueError:
        # 如果转换失败，返回None或者抛出异常，根据你的需求决定
        return None

def is_gbk_encodable(text):
    """
    尝试将字符串编码为 GBK，如果成功则返回 True，否则返回 False。
    注意：这个方法不是完美的，因为它依赖于编码过程中是否抛出异常来判断。
    有些情况下，即使字符串包含非 GBK 字符，编码过程也可能不会立即失败（例如，如果字符串以 UTF-8 编码的字节形式存在）。
    """
    try:
        text.encode('gbk')
        return True
    except UnicodeEncodeError:
        return False


def clean_non_gbk_characters(data_list, fields_to_clean):
    """
    清洗数据列表中的非 GBK 字符。

    :param data_list: 要清洗的数据列表，每个元素是一个字典。
    :param fields_to_clean: 需要清洗的字段名称列表。
    :return: 清洗后的数据列表。
    """
    cleaned_data_list = []
    for item in data_list:
        cleaned_item = item.copy()  # 创建字典的副本以避免修改原始数据
        for field in fields_to_clean:
            if isinstance(cleaned_item.get(field), str):
                # 这里我们使用正则表达式来匹配并替换非 ASCII 字符，但这不是精确判断 GBK 的方法
                # 由于 GBK 包含很多特殊字符和汉字，简单的正则表达式无法准确匹配
                # 因此，我们采用上面定义的 is_gbk_encodable 函数来检查
                if not is_gbk_encodable(cleaned_item[field]):
                    # 使用空字符串替换非 GBK 字符（或者你可以选择其他占位符）
                    cleaned_item[field] = ''.join([char for char in cleaned_item[field] if is_gbk_encodable(char)])
                    # 注意：上面的方法并不高效，因为 is_gbk_encodable 对每个字符都进行了编码尝试
                    # 一个更优化的方法是使用第三方库或自己实现一个 GBK 字符集检查函数
                    # 但由于复杂性，这里我们保持简单的方法
                # 另外，上面的方法仍然有问题，因为 is_gbk_encodable 对单个字符调用时会失败（因为单个字符不是有效的 GBK 编码单元）
                # 正确的做法应该是对整个字符串进行编码尝试，然后处理编码错误
                # 下面的代码是一个更实际的实现：
                try:
                    cleaned_item[field] = cleaned_item[field].encode('gbk', 'ignore').decode('gbk')
                except (UnicodeEncodeError, UnicodeDecodeError):
                    # 如果编码/解码过程中仍然出现问题（理论上不应该，因为我们使用了 ignore 错误处理），则设置为空字符串
                    cleaned_item[field] = ""
        cleaned_data_list.append(cleaned_item)
    return cleaned_data_list


def save_contacts_and_messages(PhoneNumber,key):
    # 获取当前时间
    now = datetime.now()
    # 格式化为字符串
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')

    # 检查是否存在相同 phone_name 且 is_valid 为有效的数据
    existing_phone = PhoneData.objects.filter(phone_name=PhoneNumber, is_valid=True).first()

    if existing_phone:
        # 如果存在，将其 is_valid 更新为 False
        existing_phone.is_valid = False
        existing_phone.save()

        # 使用Q对象构建复杂查询条件
        contacts_to_invalidate = Contact.objects.filter(Q(phone_number=existing_phone) & Q(is_valid=True))
        # 批量更新is_valid字段为False
        contacts_to_invalidate.update(is_valid=False)


    # # 创建新的 PhoneData 实例
    Phone = PhoneData.objects.create(phone_name=PhoneNumber,key=key, insert_time=now_str)

    contact_info_list = process_contacts(PhoneNumber)
    ChartDataes = []
    for contact_info in contact_info_list:
        # 逐个字段传递
        contact = Contact.objects.create(
            user_name=contact_info['UserName'],
            alias=contact_info['Alias'],
            type=contact_info['Type'],
            remark=contact_info['Remark'],
            nick_name=contact_info['NickName'],
            phone_number=contact_info['PhoneNumber'],
            small_head_img_url=contact_info['smallHeadImgUrl'],
            detail=contact_info['detail'],
            label_name=contact_info['label_name'],
            phone_data=Phone
        )

        # 创建一个列表来存储 WeChatMessage 对象
        wechat_messages = []
        # 获取联系人聊天数据
        messages = get_wechat_messages(contact_info['UserName'])
        for message in messages:
            try:
                if message['my_json_field'] is None:
                    my_json_field = {}
                else:
                    my_json_field = message['my_json_field'].to_json()

                # 逐个字段传递
                # my_json_field = message['my_json_field'].to_json()
                    # 使用自定义解码器解码
                wechat_message = WeChatMessage(
                    user_name=contact_info['UserName'],
                    local_id=message['local_id'],
                    talker_id=message['talker_id'],
                    type=message['type'],
                    subtype=message['subtype'],
                    is_sender=message['is_sender'],
                    create_time=convert_to_django_datetime(str(message['create_time'])),
                    status=message['status'],
                    str_content=message['str_content'],
                    str_time=message['str_time'],
                    msg_svr_id=message['msg_svr_id'],
                    bytes_extra=message['bytes_extra'],
                    compress_content=message['compress_content'],
                    display_content=message['display_content'],
                    Contact_data=contact,
                    my_json_field=my_json_field,
                )
            except Exception as e:
                # 使用自定义解码器解码
                wechat_message = WeChatMessage(
                    user_name=contact_info['UserName'],
                    local_id=message['local_id'],
                    talker_id=message['talker_id'],
                    type=message['type'],
                    subtype=message['subtype'],
                    is_sender=message['is_sender'],
                    create_time=convert_to_django_datetime(str(message['create_time'])),
                    status=message['status'],
                    str_content=message['str_content'],
                    str_time=message['str_time'],
                    msg_svr_id=message['msg_svr_id'],
                    bytes_extra=message['bytes_extra'],
                    compress_content=message['compress_content'],
                    display_content=message['display_content'],
                    Contact_data=contact,
                    my_json_field={},
                )
            wechat_messages.append(wechat_message)
        # 使用 bulk_create 一次性保存所有消息对象
        WeChatMessage.objects.bulk_create(wechat_messages)

        if not messages:
            ChartDatainfo = ChartData(chart_data_sender={},
                                     chart_data_types={},
                                     chart_data_weekday={},
                                     chart_data_wordcloud={},
                                     keyword_max_num='0',
                                     total_text_num='0',
                                     keyword='0',
                                     contact=contact)
            # 或者抛出一个异常
            # raise ValueError(f"No messages found for user {contact_info['UserName']}")
        else:
            wxid = contact_info['UserName']
            data = my_message_counter(wxid, time_range=None)

            ChartDatainfo = ChartData(chart_data_sender=data['chart_data_sender'],
                                     chart_data_types=data['chart_data_types'],
                                     chart_data_weekday=data['chart_data_weekday'],
                                     chart_data_wordcloud=data['chart_data_wordcloud'],
                                     keyword_max_num=data['keyword_max_num'],
                                     total_text_num=data['total_text_num'],
                                     keyword=data['keyword'],
                                     contact=contact)
        ChartDataes.append(ChartDatainfo)
    ChartData.objects.bulk_create(ChartDataes)



    return contact_info_list

# import os
# BASE_DIR = "D:\WhcatMsgServer\djangoProject"
# file_name = 'wxid_yzy19wfvnozj21'
# WXdb_path = os.path.join(BASE_DIR, 'WachatMsgServer', 'DateBase', file_name, 'Msg')
# db_path = os.path.join(BASE_DIR, 'WachatMsgServer', 'itools', 'WXDateBase', 'Database', 'Msg')
#
# clear_folder(db_path)
# run(key, WXdb_path, db_path)
# init_db()

# contact_info_list = check_and_execute(db_path, example_method, phonenumber)

# save_contacts_and_messages(PhoneNumber="15000537641")