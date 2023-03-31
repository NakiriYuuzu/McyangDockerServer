from django.urls import path
from .views import *

urlpatterns = [
    # FIXME: API先資料庫在事件！
    # path('yuuzu/home/', home),
    path('api/Login/', login),
    path('api/CourseList/', course_list),
    path('api/CourseSignList/', course_sign_list),
    path('api/CourseSignup/', course_signup),
    path('api/CourseCreate/', course_create),
    path('api/SignCreate/', sign_create),
    path('api/SignRecordList/', sign_record_list),
    path('api/RaceCreate/', race_create),
    path('api/RaceListList/', race_list_list),
    path('api/RaceListCreate/', race_list_create),
    path('api/RaceAnswerList/', race_answer_list),
    path('api/TeamDescCreate/', team_desc_create),
    path('api/TeamLeaderCreate/', team_leader_create),
    path('api/TeamMemberCreate/', team_member_create),
    path('api/TeamLeaderList/', team_leader_list),
    path('api/TeamMemberList/', team_member_list),
    path('api/TeamDescList/', team_list),
    path('api/TeamChatCreate/', team_chat_create),
    path('api/TeamChatList/', team_chat_list)

    # path('api/studentLogin/', student_login),
    # path('api/showCourse/', show_course),
    # path('api/courseSigned/', course_sign),
    # path('api/listSignCourse/', show_sign_course),

    # FIXME: 後臺網頁
    # path('', views.login, name="login"),
    # path('user_login/', views.user_login, name="user_login"),

]
