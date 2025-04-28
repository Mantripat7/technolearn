from django.urls import path
from . import views


urlpatterns = [
 
    # path('ckeditor/', include('ckeditor_uploader.urls')),
    path('',views.index, name="index"),
    path('courses/',views.courses, name="courses"),
    path('chatbot/',views.chatbot, name="chatbot"),
    path('download_notes/<int:lesson_id>/',views.download_notes, name="download_notes"),
    path('download_audio/<int:lesson_id>/',views.download_audio, name="download_audio"),
    path('generate_audio/',views.generate_audio, name="generate_audio"),
    path('pdftext',views.pdftext),
    path('login/',views.login, name="login"),
    path('register/',views.register),
    path('course_list/',views.course_list, name="course_list"),
    path('payment_success/<int:course_id>/',views.payment_success,name='payment_success'),
    path('payment_failed',views.payment_failed),
    path('create_checkout_session/<int:course_id>/',views.create_checkout_session,name='create_checkout_session'),
    path('course_detail/<int:course_id>/',views.course_detail,name='course_detail'),
    path('module_detail/<int:module_id>/',views.module_detail,name='module_detail'),
    path('mcq/<int:module_id>/',views.mcq,name='mcq'),
    path('faq/', views.faq, name='faq'),
    path('about_us/', views.about_us, name='about_us'),
    path('change-password/', views.change_password, name='change_password'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('profile_section/', views.profile_section, name='profile_section'),
    path('my_certificates/', views.my_certificates, name='my_certificates'),
    path('profile_course/', views.profile_course, name='profile_course'),
    path('contact/', views.contact, name='contact'),
    path('thanks/', views.thanks, name='thanks'),
    path('logout/', views.logout_view, name='logout'),
    path('download_certificate/<int:course_id>/', views.download_certificate, name='download_certificate'),
  
]
