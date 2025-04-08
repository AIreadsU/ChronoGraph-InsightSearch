from django.db import models
from WachatMsgServer.itools.person import ContactDefault


class PhoneData(models.Model):
    serial_number = models.AutoField(primary_key=True)  # 序号字段
    phone_name = models.CharField(max_length=300, blank=True, null=True)  # 手机名称字段
    insert_time = models.DateTimeField(auto_now_add=True, blank=True, null=True)  # 数据插入时间字段
    is_valid = models.BooleanField(default=True, blank=True, null=True)  # 数据是否有效字段
    key = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.phone_name

    class Meta:
        app_label = 'WachatMsgServer'  # 指定应用标签

class Contact(models.Model):
    id = models.AutoField(primary_key=True)  # 唯一ID字段
    user_name = models.CharField(max_length=300, blank=True, null=True)
    alias = models.CharField(max_length=300, blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    remark = models.CharField(max_length=300, blank=True, null=True)
    nick_name = models.CharField(max_length=300, blank=True, null=True)
    small_head_img_url = models.CharField(max_length=300, blank=True, null=True)
    detail = models.TextField(blank=True, null=True)
    label_name = models.CharField(max_length=300, blank=True, null=True)
    is_valid = models.BooleanField(default=True, blank=True, null=True)  # 数据是否有效字段
    phone_number = models.CharField(max_length=300, blank=True, null=True)  # 手机号码字段
    phone_data = models.ForeignKey(PhoneData, on_delete=models.CASCADE, blank=True, null=True)  # 外键关联到PhoneData模型
    def __str__(self):
        return self.user_name

    class Meta:
        app_label = 'WachatMsgServer'  # 指定应用标签


class WeChatMessage(models.Model):
    id = models.AutoField(primary_key=True)  # 唯一ID字段
    user_name = models.CharField(max_length=300, blank=True, null=True)
    local_id = models.CharField(max_length=300, blank=True, null=True)
    talker_id = models.CharField(max_length=300, blank=True, null=True)
    type = models.IntegerField(blank=True, null=True)
    subtype = models.IntegerField(blank=True, null=True)
    is_sender = models.BooleanField(blank=True, null=True)
    create_time = models.DateTimeField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    str_content = models.TextField(blank=True, null=True, db_collation='utf8mb4_unicode_ci')
    str_time = models.CharField(max_length=300, blank=True, null=True)
    msg_svr_id = models.CharField(max_length=300, blank=True, null=True)
    bytes_extra = models.BinaryField(null=True, blank=True, max_length=1024)  # 假设最大长度为1024字节
    compress_content = models.TextField(blank=True, null=True)
    display_content = models.TextField(blank=True, null=True)
    Contact_data = models.ForeignKey(Contact, on_delete=models.CASCADE, blank=True,
                                       null=True)  # 外键关联到WeChatMessage模型
    my_json_field = models.JSONField(
        default=dict,  # 使用一个空字典作为默认值
    )


    def __str__(self):
        return self.local_id

    class Meta:
        app_label = 'WachatMsgServer'  # 指定应用标签


class ChartData(models.Model):
    id = models.AutoField(primary_key=True)  # 唯一ID字段
    chart_data_sender = models.TextField(blank=True, null=True, db_collation='utf8mb4_unicode_ci')
    chart_data_types = models.TextField(blank=True, null=True,  db_collation='utf8mb4_unicode_ci')
    chart_data_weekday = models.TextField(blank=True, null=True, db_collation='utf8mb4_unicode_ci')
    chart_data_wordcloud = models.TextField(blank=True, null=True, db_collation='utf8mb4_unicode_ci')
    keyword_max_num = models.TextField(blank=True, null=True)
    total_text_num = models.TextField(blank=True, null=True)
    keyword = models.TextField(blank=True, null=True)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, blank=True, null=True)  # 外键关联到Contact模型

    def __str__(self):
        return self.chart_data_sender

    class Meta:
        app_label = 'WachatMsgServer'  # 指定应用标签






