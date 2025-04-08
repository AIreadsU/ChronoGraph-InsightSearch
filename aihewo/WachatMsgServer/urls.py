from django.urls import path
from. import views

urlpatterns = [
    path('upload_file',
         views.upload_file, name='upload_file'),
    path('check_phone_data',
         views.check_phone_data, name='check_phone_data'),
    path('get_contacts_by_phone_number',
         views.get_contacts_by_phone_number, name='get_contacts_by_phone_number'),
    path('get_wechat_messages_by_contact_username',
         views.get_wechat_messages_by_contact_username, name='get_wechat_messages_by_contact_username'),
    path('get_contacts_with_messages',
         views.get_contacts_with_messages, name='get_contacts_with_messages'),
    path('get_chart_data',
         views.get_chart_data,name='get_chart_data'),
    path('get_wechat_messages_by_contact_username_ten',
         views.get_wechat_messages_by_contact_username_ten, name='get_wechat_messages_by_contact_username_ten'),
    path('get_contacts_by_phone_number_ten',
         views.get_contacts_by_phone_number_ten, name='get_contacts_by_phone_number_ten'),
    path('process_form_data',
         views.process_form_data, name='process_form_data'),
]