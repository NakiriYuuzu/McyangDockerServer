import datetime
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_406_NOT_ACCEPTABLE, \
    HTTP_500_INTERNAL_SERVER_ERROR, HTTP_417_EXPECTATION_FAILED, HTTP_410_GONE
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import *


# TODO:Create your views here[tableName->Function].
def home(request):
    return render(request, 'home.html')


# TODO:Create your Api Here[tableName->Function].

@csrf_exempt  # TODO: 登入驗證
def login(request):
    s_email = request.POST.get('S_email')
    s_password = request.POST.get('S_password')
    t_email = request.POST.get('T_email')
    t_password = request.POST.get('T_password')
    print(request.POST.get)
    data = {}

    if request.method == 'POST':
        if s_email and s_password:
            status = HTTP_200_OK
            if McyangStudent.objects.filter(S_email=s_email, S_password=s_password).exists():
                data['S_id'] = McyangStudent.objects.get(S_email=s_email, S_password=s_password).S_id
                data['S_name'] = McyangStudent.objects.get(S_email=s_email, S_password=s_password).S_name

            else:
                status = HTTP_400_BAD_REQUEST

        elif t_email and t_password:
            status = HTTP_200_OK
            if McyangTeacher.objects.filter(T_email=t_email, T_password=t_password).exists():
                data['T_id'] = McyangTeacher.objects.get(T_email=t_email, T_password=t_password).T_id
                data['T_name'] = McyangTeacher.objects.get(T_email=t_email, T_password=t_password).T_name

            else:
                data['MESSAGE'] = "帳號或密碼錯誤！"
                status = HTTP_400_BAD_REQUEST
        else:
            status = HTTP_404_NOT_FOUND

    else:
        status = HTTP_500_INTERNAL_SERVER_ERROR

    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, status=status)


@csrf_exempt  # TODO: 課程列表
def course_list(request):
    s_id = request.POST.get('S_id')
    t_id = request.POST.get('T_id')
    print(s_id, t_id)
    data = []

    if request.method == 'POST':
        if s_id:
            raw = McyangCourse.objects.raw('select DISTINCT c.*, t.T_name from mc_course c '
                                           'left join mc_courserecord cr on cr.C_id_id = c.C_id '
                                           'left join mc_teacher t on c.T_id_id = t.T_id '
                                           'where cr.S_id_id = %s', [s_id])
            if len(raw) > 0:
                status = HTTP_200_OK
                for result in raw:
                    data.append({'C_id': result.C_id, 'C_name': result.C_name, 'T_name': result.T_name})
            else:
                status = HTTP_400_BAD_REQUEST

        elif t_id:
            raw = McyangCourse.objects.raw('select DISTINCT c.*, t.T_name from mc_course c '
                                           'left join mc_courserecord cr on cr.C_id_id = c.C_id '
                                           'left join mc_teacher t on c.T_id_id = t.T_id '
                                           'where c.T_id_id = %s', [t_id])
            if len(raw) > 0:
                status = HTTP_200_OK
                for result in raw:
                    data.append({'C_id': result.C_id, 'C_name': result.C_name, 'T_name': result.T_name})

            else:
                status = HTTP_400_BAD_REQUEST

        else:
            status = HTTP_404_NOT_FOUND

    else:
        status = HTTP_500_INTERNAL_SERVER_ERROR

    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, status=status)


@csrf_exempt
def course_sign_list(request):
    sign_id = request.GET.get('id', '')
    print(sign_id)
    data = []

    if sign_id:
        raw = McyangSign.objects.raw('select s.Sign_id, c.C_name, t.T_name from mc_sign s '
                                     'left join mc_course c on s.C_id_id = c.C_id '
                                     'left join mc_teacher t on c.T_id_id = t.T_id '
                                     'where s.Sign_id = %s order by s.Sign_id ', [sign_id])
        status = HTTP_200_OK
        for result in raw:
            data.append({'T_name': result.T_name, 'C_name': result.C_name, 'Sign_id': result.Sign_id})
    else:
        raw = McyangSign.objects.raw('select s.Sign_id, c.C_name, t.T_name from mc_sign s '
                                     'left join mc_course c on s.C_id_id = c.C_id '
                                     'left join mc_teacher t on c.T_id_id = t.T_id '
                                     'order by s.Sign_id ')
        status = HTTP_200_OK
        for result in raw:
            data.append({'T_name': result.T_name, 'C_name': result.C_name, 'Sign_id': result.Sign_id})

    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, status=status)


@csrf_exempt
def course_signup(request):
    s_id = request.POST.get('S_id')
    sign_id = request.POST.get('Sign_id')
    print(s_id, sign_id)
    data = {}

    if request.method == 'POST':
        if s_id and sign_id:
            in_course = McyangCourseRecord.objects.raw('select cr.* from mc_courserecord cr '
                                                       'left join mc_student s on s.S_id = cr.S_id_id '
                                                       'left join mc_course c on c.C_id = cr.C_id_id '
                                                       'left join mc_sign sign on sign.C_id_id = c.C_id '
                                                       'where cr.S_id_id = %s and sign.Sign_id = %s ', [s_id, sign_id])
            if len(in_course) == 0:
                status = HTTP_406_NOT_ACCEPTABLE  # [406]不是此課堂的學生
            else:
                if McyangSignRecord.objects.filter(Sign_id=sign_id, S_id=s_id).exists():
                    status = HTTP_400_BAD_REQUEST  # [400]已簽到過
                else:
                    try:
                        with transaction.atomic():
                            status = HTTP_200_OK  # [200]簽到成功！
                            sign = McyangSign.objects.get(Sign_id=sign_id)
                            course_id = sign.C_id.C_id
                            crt_date = sign.crtTime
                            seq_no = McyangSignRecord.objects.filter().count() + 1
                            McyangSignRecord.objects.create(SR_id=seq_no, Sign_id_id=sign_id, S_id_id=s_id,
                                                            crtTime=datetime.datetime.now())
                            date = crt_date.date()
                            data['Sign_id'] = sign_id
                            data['C_id'] = course_id
                            data['Crt_time'] = date

                            channel_layer = get_channel_layer()
                            async_to_sync(channel_layer.group_send)(
                                'sign',
                                {
                                    'type': 'chat_message',
                                    'message': "RaceList",
                                    'Sign_id': sign_id
                                }
                            )
                    except Exception as e:
                        print(e)
                        status = HTTP_417_EXPECTATION_FAILED

        else:
            status = HTTP_404_NOT_FOUND  # [404]沒資料

    else:
        status = HTTP_500_INTERNAL_SERVER_ERROR  # [500]不是POST的情況

    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, status=status)


@csrf_exempt
def course_create(request):
    c_name = request.POST.get("C_name")
    t_id = request.POST.get("T_id")
    c_id = request.POST.get("C_id")
    print(c_name, t_id)
    data = {}

    if request.method == 'POST':
        if c_name and t_id and not c_id:
            status = HTTP_200_OK
            try:
                with transaction.atomic():
                    seq_no = McyangCourse.objects.filter().count() + 1
                    McyangCourse.objects.create(C_id=seq_no, C_name=c_name, T_id_id=t_id,
                                                C_image="", crtTime=datetime.datetime.now())
            except Exception as e:
                print(e)
                status = HTTP_417_EXPECTATION_FAILED
        elif c_id and not c_name and not t_id:
            status = HTTP_200_OK
            try:
                with transaction.atomic():
                    McyangCourse.objects.filter(C_id=c_id).update(crtTime=datetime.datetime.now())
            except Exception as e:
                print(e)
                status = HTTP_417_EXPECTATION_FAILED
        else:
            status = HTTP_404_NOT_FOUND

    else:
        status = HTTP_500_INTERNAL_SERVER_ERROR

    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, status=status)


@csrf_exempt
def sign_create(request):
    c_name = request.POST.get("C_name")
    t_id = request.POST.get("T_id")
    sign_id = request.POST.get("Sign_id")
    print(c_name, t_id)
    data = {}
    datas = []

    if request.method == 'POST':
        if c_name and t_id and not sign_id:
            c_id = McyangCourse.objects.get(T_id_id=t_id, C_name=c_name).C_id
            print(c_id)
            if c_id:
                status = HTTP_200_OK
                try:
                    with transaction.atomic():
                        seq_no = McyangSign.objects.filter().count() + 1
                        test = McyangSign.objects.create(Sign_id=seq_no, C_id_id=c_id, crtTime=datetime.datetime.now())
                        raw = McyangStudent.objects.raw(
                            'select s.* from mc_student s left join mc_courserecord cr on cr.S_id_id = s.S_id where cr.C_id_id = %s',
                            [c_id])

                        sign_id = test.Sign_id
                        for result in raw:
                            datas.append({'S_id': result.S_id, 'StudentID': result.S_email, 'S_name': result.S_name})
                        data['Sign_id'] = sign_id
                        data['C_id'] = test.C_id_id
                        data['Date'] = test.crtTime.date()
                        data['StudentList'] = datas
                except:
                    status = HTTP_417_EXPECTATION_FAILED

            else:
                status = HTTP_400_BAD_REQUEST
        elif sign_id and not c_name and not t_id:
            status = HTTP_200_OK
            try:
                with transaction.atomic():
                    McyangSign.objects.filter(Sign_id=sign_id).update(crtTime=datetime.datetime.now())
                    raw = McyangStudent.objects.raw(
                        'select s.* from mc_student s '
                        'left join mc_courserecord cr on cr.S_id_id = s.S_id '
                        'left join mc_sign sign on sign.C_id_id = cr.C_id_id '
                        'where Sign_id = %s', [sign_id])
                    for result in raw:
                        datas.append({'S_id': result.S_id, 'StudentID': result.S_email, 'S_name': result.S_name})
                    data['StudentList'] = datas
            except Exception as e:
                print(e)
                status = HTTP_417_EXPECTATION_FAILED
        else:
            status = HTTP_404_NOT_FOUND
    else:
        status = HTTP_500_INTERNAL_SERVER_ERROR

    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, status=status)


@csrf_exempt
def sign_record_list(request):
    sign_id = request.GET.get('Sign_id', '')
    data = []

    if request.method == 'GET':
        if sign_id:
            status = HTTP_200_OK
            raw = McyangStudent.objects.raw('select distinct s.* from mc_student s '
                                            'left join mc_signrecord sr on sr.S_id_id = s.S_id '
                                            'where sr.Sign_id_id = %s', [sign_id])
            for result in raw:
                data.append({'S_id': result.S_id, 'StudentID': result.S_email, 'S_name': result.S_name})

        else:
            status = HTTP_200_OK
            raw = McyangStudent.objects.raw('select distinct s.* from mc_student s '
                                            'left join mc_signrecord sr on sr.S_id_id = s.S_id')
            for result in raw:
                data.append({'S_id': result.S_id, 'StudentID': result.S_email, 'S_name': result.S_name})

    else:
        status = HTTP_500_INTERNAL_SERVER_ERROR

    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, status=status)


@csrf_exempt
def race_create(request):
    c_id = request.POST.get("C_id")
    race_doc = request.POST.get("Race_doc")
    race_id = request.POST.get("Race_id")
    stat = request.POST.get("Status")
    print(c_id, race_doc, race_id, stat)
    data = {}

    if request.method == 'POST':
        if c_id and race_doc and not race_id and not stat:
            try:
                with transaction.atomic():
                    status = HTTP_200_OK
                    # status = 0 表示開始中 1表示結束
                    seq_no = McyangRaceAnswer.objects.filter().count() + 1
                    race = McyangRaceAnswer.objects.create(R_id=seq_no, R_doc=race_doc, Status=0,
                                                           crtTime=datetime.datetime.now(), C_id_id=c_id)
                    data['Race_id'] = race.R_id
                    data['Race_doc'] = race.R_doc
                    data['Status'] = race.Status
                    data['CrtTime'] = race.crtTime
                    data['C_id'] = c_id

            except Exception as e:
                status = HTTP_417_EXPECTATION_FAILED
                print(e)
        elif stat and race_id and not c_id and not race_doc:
            try:
                with transaction.atomic():
                    status = HTTP_200_OK
                    McyangRaceAnswer.objects.filter(R_id=race_id).update(Status=stat)

                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        'studentRace',
                        {
                            'type': 'chat_message',
                            'message': "race_student",
                            'Race_id': race_id
                        }
                    )
            except Exception as e:
                status = HTTP_417_EXPECTATION_FAILED
                print(e)

        else:
            status = HTTP_400_BAD_REQUEST
    else:
        status = HTTP_500_INTERNAL_SERVER_ERROR

    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, status=status)


@csrf_exempt  # 學生用搶答
def race_list_create(request):
    s_id = request.POST.get("S_id")
    s_name = request.POST.get("S_name")
    r_id = request.POST.get("Race_id")
    answer = request.POST.get("Answer")
    print(s_name, r_id, answer)

    room_name = "test"
    data = {}

    if request.method == 'POST':
        if s_name and r_id and s_id and not answer:
            current = McyangRaceAnswer.objects.get(R_id=r_id)
            if current.Status == 0:
                try:
                    with transaction.atomic():
                        status = HTTP_200_OK
                        # s_id = McyangStudent.objects.get(S_name=s_name).S_id
                        seq_no = McyangRaceList.objects.filter().count() + 1
                        McyangRaceList.objects.create(RL_id=seq_no, R_id_id=r_id, S_id_id=s_id,
                                                      crtTime=datetime.datetime.now(), Answer="0")

                        channel_layer = get_channel_layer()
                        async_to_sync(channel_layer.group_send)(
                            room_name,
                            {
                                'type': 'receive',
                                'message': "RaceList",
                                'Race_id': r_id
                            }
                        )

                except Exception as e:
                    status = HTTP_417_EXPECTATION_FAILED
                    print(e)
            else:
                status = HTTP_406_NOT_ACCEPTABLE
        elif s_name and r_id and answer:
            try:
                with transaction.atomic():
                    status = HTTP_200_OK
                    s_id = McyangStudent.objects.get(S_name=s_name).S_id
                    McyangRaceList.objects.filter(R_id_id=r_id, S_id_id=s_id).update(Answer=answer)

                    channel_layer = get_channel_layer()
                    async_to_sync(channel_layer.group_send)(
                        room_name,
                        {
                            'type': 'receive',
                            'message': 'RaceList',
                            'Race_id': r_id
                        }
                    )

            except Exception as e:
                status = HTTP_417_EXPECTATION_FAILED
                print(e)
        else:
            status = HTTP_400_BAD_REQUEST
    else:
        status = HTTP_500_INTERNAL_SERVER_ERROR

    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, status=status)


@csrf_exempt
def race_answer_list(request):
    race_id = request.GET.get('Race_id', '')
    data = {}

    if request.method == 'GET':
        if race_id:
            status = HTTP_200_OK
            result = McyangRaceAnswer.objects.get(R_id=race_id)
            data['Race_doc'] = result.R_doc
        else:
            status = HTTP_400_BAD_REQUEST
    else:
        status = HTTP_500_INTERNAL_SERVER_ERROR

    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, status=status)


@csrf_exempt
def race_list_list(request):
    race_id = request.GET.get('Race_id', '')
    sid = request.GET.get('S_id', '')
    data = []

    if request.method == 'GET':
        if race_id and not sid:
            status = HTTP_200_OK
            raw = McyangRaceList.objects.raw('select rl.*, s.S_name, s.S_email from mc_racelist rl '
                                             'left join mc_student s on s.S_id = rl.S_id_id '
                                             'where rl.R_id_id = %s order by rl.RL_id desc ', [race_id])
            for result in raw:
                data.append({'RL_id': result.RL_id, 'Answer': result.Answer, 'S_name': result.S_name,
                             'StudentID': result.S_email})
        elif sid and race_id:
            status = HTTP_200_OK
            raw = McyangRaceList.objects.raw('select rl.*, s.S_name, s.S_email from mc_racelist rl '
                                             'left join mc_student s on s.S_id = rl.S_id_id '
                                             'where rl.R_id_id = %s and rl.S_id_id = %s', [race_id, sid])
            data = {}
            for result in raw:
                data['Answer'] = result.Answer

        else:
            status = HTTP_400_BAD_REQUEST
    else:
        status = HTTP_500_INTERNAL_SERVER_ERROR

    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, status=status)


@csrf_exempt  # TeamDesc[主要] team[隊長](可以用來當聊天室) teamMember[組員]
def team_desc_create(request):
    course_id = request.POST.get('C_id')
    doc = request.POST.get('Doc')
    total = request.POST.get('Total')
    limit = request.POST.get('Limit')

    data = {}

    if request.method == 'POST':
        if course_id and doc and total and limit:
            try:
                with transaction.atomic():
                    status = HTTP_200_OK
                    seq_no = McyangTeamDesc.objects.filter().count() + 1
                    insert = McyangTeamDesc.objects.create(TD_id=seq_no, TD_doc=doc, TD_total=total, TD_limit=limit,
                                                           C_id_id=course_id, TD_status='0')
                    data['TeamDesc_id'] = insert.TD_id
            except Exception as e:
                print(e)
                status = HTTP_417_EXPECTATION_FAILED
        else:
            status = HTTP_400_BAD_REQUEST
    else:
        status = HTTP_500_INTERNAL_SERVER_ERROR

    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, status=status)


@csrf_exempt  # [ID]欄位可以當成聊天室 [Group_number]欄位可以用於判斷 0 = 未選上， 1 = 選上
def team_leader_create(request):
    leader_sid = request.POST.get('S_id')
    teamdesc_id = request.POST.get('TeamDesc_id')
    group_num = request.POST.get('Group_number')
    user = request.POST.get('User')
    teamleader_id = request.POST.get('TeamLeader_id')
    data = {}

    if request.method == 'POST':
        if leader_sid and teamdesc_id and user and not group_num and not teamleader_id:
            check_duplicate = McyangTeam.objects.filter(TD_id_id=teamdesc_id, Leader_id_id=leader_sid).count()
            if check_duplicate == 0:
                try:
                    with transaction.atomic():
                        status = HTTP_200_OK
                        seq_no = McyangTeam.objects.filter().count() + 1
                        insert = McyangTeam.objects.create(T_id=seq_no, Group_number=0,
                                                           Leader_id_id=leader_sid,
                                                           TD_id_id=teamdesc_id)
                        data['TeamLeader_id'] = insert.T_id

                        channel_layer = get_channel_layer()
                        async_to_sync(channel_layer.group_send)(
                            'group',
                            {
                                'type': 'receive',
                                'message': 'RaceList',
                                'TeamDesc_id': teamdesc_id,
                                'Identity': user,
                                'Leader': insert.T_id,
                                'Member': '0'
                            }
                        )

                except Exception as e:
                    print(e)
                    status = HTTP_417_EXPECTATION_FAILED
            else:
                status = HTTP_406_NOT_ACCEPTABLE  # 不可重複選取隊長

        elif teamdesc_id and teamleader_id and group_num and user and not leader_sid:
            try:
                with transaction.atomic():
                    status = HTTP_200_OK
                    teamleader_total = McyangTeamDesc.objects.get(TD_id=teamdesc_id).TD_total
                    teamleader_current = McyangTeam.objects.filter(TD_id_id=teamdesc_id, Group_number=1).count()
                    print(teamleader_current, teamleader_total)

                    if teamleader_current < teamleader_total:
                        McyangTeam.objects.filter(T_id=teamleader_id).update(Group_number=group_num)
                        channel_layer = get_channel_layer()
                        async_to_sync(channel_layer.group_send)(
                            'group',
                            {
                                'type': 'receive',
                                'message': 'RaceList',
                                'TeamDesc_id': teamdesc_id,
                                'Identity': user,
                                'Leader': 2,
                                'Member': '0'
                            }
                        )
                    else:
                        if group_num == '0':
                            status = HTTP_200_OK
                            McyangTeam.objects.filter(T_id=teamleader_id).update(Group_number=group_num)
                            channel_layer = get_channel_layer()
                            async_to_sync(channel_layer.group_send)(
                                'group',
                                {
                                    'type': 'receive',
                                    'message': 'RaceList',
                                    'TeamDesc_id': teamdesc_id,
                                    'Identity': user,
                                    'Leader': 2,
                                    'Member': '0'
                                }
                            )
                        else:
                            status = HTTP_406_NOT_ACCEPTABLE

            except Exception as e:
                status = HTTP_417_EXPECTATION_FAILED
                print(e)
        elif teamdesc_id and user and not teamleader_id and not leader_sid and not group_num:
            status = HTTP_200_OK
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'group',
                {
                    'type': 'receive',
                    'message': 'RaceList',
                    'TeamDesc_id': teamdesc_id,
                    'Identity': user,
                    'Leader': 1,
                    'Member': '0'
                }
            )
        else:
            status = HTTP_400_BAD_REQUEST
    else:
        status = HTTP_500_INTERNAL_SERVER_ERROR

    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, status=status)


@csrf_exempt
def team_member_create(request):
    member_sid = request.POST.get('S_id')
    teamleader_id = request.POST.get('TeamLeader_id')
    teamdesc_id = request.POST.get('TeamDesc_id')
    team_num = request.POST.get('Team_number')
    user = request.POST.get('User')
    data = {}

    if request.method == 'POST':
        if member_sid and teamleader_id and user and not team_num and not teamdesc_id:
            teamdesc_id = McyangTeam.objects.get(T_id=teamleader_id).TD_id_id
            limited = McyangTeamDesc.objects.get(TD_id=teamdesc_id).TD_limit
            current = McyangTeamMember.objects.filter(T_id_id=teamleader_id).count() + 1
            leader_raw = McyangTeam.objects.raw('select distinct t.* from mc_team t '
                                                'left join mc_teamdesc td on td.TD_id = t.TD_id_id '
                                                'left join mc_teammember tm on tm.T_id_id = t.T_id '
                                                'where td.TD_id = %s and t.Group_number = %s', [teamdesc_id, 1])
            duplicate_sid = McyangTeamMember.objects.raw('select tm.*, td.TD_id from mc_teammember tm '
                                                         'left join mc_team tl on tm.T_id_id = tl.T_id '
                                                         'left join mc_teamdesc td on tl.TD_id_id = td.TD_id '
                                                         'where td.TD_id = %s and tm.S_id_id = %s',
                                                         [teamdesc_id, member_sid])
            check_ldr = []
            for result in leader_raw:
                check_ldr.append(result.Leader_id_id)

            if current < limited:  # 判斷人數不超過老師設定！
                if int(member_sid) not in check_ldr:  # 判斷組長是否混在其中！
                    if len(duplicate_sid) == 0:  # 判斷組員不重複！
                        try:
                            with transaction.atomic():
                                status = HTTP_200_OK
                                seq_no = McyangTeamMember.objects.filter().count() + 1
                                insert = McyangTeamMember.objects.create(TM_id=seq_no, S_id_id=member_sid,
                                                                         T_id_id=teamleader_id, Team_number=0)
                                data['TeamMember_id'] = insert.TM_id

                                channel_layer = get_channel_layer()
                                async_to_sync(channel_layer.group_send)(
                                    'group',
                                    {
                                        'type': 'receive',
                                        'message': 'RaceList',
                                        'TeamDesc_id': teamdesc_id,
                                        'Identity': user,
                                        'Leader': 0,
                                        'Member': 1
                                    }
                                )

                        except Exception as e:
                            status = HTTP_417_EXPECTATION_FAILED
                            print(e)
                    else:
                        status = HTTP_406_NOT_ACCEPTABLE
                        print('不能同時在兩個隊伍！')
                else:
                    status = HTTP_410_GONE
                    print('隊長不能兼任隊員！')
            else:
                status = HTTP_404_NOT_FOUND
                print('人數已上限！')
        elif teamdesc_id and user and not teamleader_id and not team_num and not member_sid:  # STOP GROUPING
            status = HTTP_200_OK
            McyangTeamDesc.objects.filter(TD_id=teamdesc_id).update(TD_status=1)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'group',
                {
                    'type': 'receive',
                    'message': 'RaceList',
                    'TeamDesc_id': teamdesc_id,
                    'Identity': user,
                    'Leader': 0,
                    'Member': 0
                }
            )
        else:
            status = HTTP_400_BAD_REQUEST
    else:
        status = HTTP_500_INTERNAL_SERVER_ERROR

    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, status=status)


@csrf_exempt
def team_leader_list(request):
    teamdesc_id = request.GET.get('TeamDesc_id', '')
    teamleader_id = request.GET.get('TeamLeader_id', '')
    data = []

    if request.method == 'GET':
        if teamdesc_id and not teamleader_id:
            status = HTTP_200_OK
            result = McyangTeam.objects.filter(TD_id_id=teamdesc_id)

            for i in result:
                data.append({'TeamLeader_id': i.T_id, 'IsPicked': i.Group_number, 'S_id': i.Leader_id.S_id,
                             'S_name': i.Leader_id.S_name, 'S_email': i.Leader_id.S_email})
        elif teamleader_id and not teamdesc_id:
            result = McyangTeam.objects.get(T_id=teamleader_id)
            if result.Group_number == 1:
                status = HTTP_200_OK
            else:
                status = HTTP_406_NOT_ACCEPTABLE

        else:
            status = HTTP_200_OK
            result = McyangTeam.objects.filter()
            for i in result:
                data.append({'TeamLeader_id': i.T_id, 'IsPicked': i.Group_number, 'S_id': i.Leader_id.S_id,
                             'S_name': i.Leader_id.S_name, 'S_email': i.Leader_id.S_email})

    else:
        status = HTTP_500_INTERNAL_SERVER_ERROR

    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, status=status)


@csrf_exempt
def team_member_list(request):
    teamdesc_id = request.GET.get('TeamDesc_id', '')
    teamleader_id = request.GET.get('TeamLeader_id', '')
    data = []

    if request.method == 'GET':
        if teamdesc_id and not teamleader_id:
            status = HTTP_200_OK
            limit = McyangTeamDesc.objects.get(TD_id=teamdesc_id).TD_limit
            leader_data = McyangTeam.objects.filter(TD_id_id=teamdesc_id, Group_number=1)
            for leader in leader_data:
                count = McyangTeamMember.objects.filter(T_id_id=leader.T_id).count()
                people_count = "{}/{}".format(count + 1, limit)
                data.append({'TeamLeader_id': leader.T_id, 'S_name': leader.Leader_id.S_name,
                             'S_email': leader.Leader_id.S_email, 'PeopleCount': people_count})

        elif teamdesc_id and teamleader_id:  # TODO: For leader and member who need see his teammate
            status = HTTP_200_OK
            leader_data = McyangTeam.objects.get(T_id=teamleader_id).Leader_id
            result = McyangTeamMember.objects.raw('select distinct tm.*, st.S_name from mc_teammember tm '
                                                  'left join mc_team tl on tm.T_id_id = tl.T_id '
                                                  'left join mc_teamdesc td on tl.TD_id_id = td.TD_id '
                                                  'left join mc_student st on tm.S_id_id = st.S_id '
                                                  'where td.TD_id = %s and tl.T_id = %s ', [teamdesc_id, teamleader_id])
            data.append({'Id': teamleader_id, 'S_name': leader_data.S_name, 'IsLeader': True})
            for i in result:
                data.append({'Id': i.TM_id, 'S_name': i.S_name, 'IsLeader': False})

        elif teamleader_id and not teamdesc_id:
            status = HTTP_200_OK
            member_data = McyangTeamMember.objects.filter(T_id_id=teamleader_id)

            for member in member_data:
                data.append(
                    {'TeamMember_id': member.TM_id, 'S_name': member.S_id.S_name, 'S_email': member.S_id.S_email})

        else:
            status = HTTP_400_BAD_REQUEST
    else:
        status = HTTP_500_INTERNAL_SERVER_ERROR

    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, status=status)


@csrf_exempt
def team_list(request):
    teamdesc_id = request.GET.get('TeamDesc_id', '')
    course_id = request.GET.get('C_id', '')
    s_id = request.GET.get('S_id', '')
    data = []
    print(teamdesc_id)

    if request.method == 'GET':
        if teamdesc_id and not s_id:
            status = HTTP_200_OK
            leader = McyangTeam.objects.raw('select distinct tl.* from mc_team tl '
                                            'left join mc_teamdesc td on td.TD_id = tl.TD_id_id and td.TD_status = 1 '
                                            'where td.TD_id = %s', [teamdesc_id])
            for i in leader:
                member_list = []
                member = McyangTeamMember.objects.raw('select distinct tm.*, tl.Leader_id_id, td.TD_doc from mc_teammember tm '
                                                      'left join mc_team tl on tl.T_id = tm.T_id_id and tl.Group_number = 1 '
                                                      'left join mc_teamdesc td on td.TD_id = tl.TD_id_id and td.TD_status = 1 '
                                                      'where tl.T_id = %s', [i.T_id])
                for j in member:
                    member_list.append({'S_id': j.S_id_id, 'S_name': McyangStudent.objects.get(S_id=j.S_id_id).S_name})
                data.append({'TeamDesc_id': i.TD_id_id, 'T_id': i.T_id, 'S_id': i.Leader_id_id, 'S_name': McyangStudent.objects.get(S_id=i.Leader_id_id).S_name, 'Member': member_list})
        elif course_id and not teamdesc_id and not s_id:
            status = HTTP_200_OK
            select = McyangTeamDesc.objects.filter(C_id_id=course_id, TD_status=1).order_by('-crtTime')
            for i in select:
                data.append({'TD_id': i.TD_id, 'TD_doc': i.TD_doc, 'CrtTime': i.crtTime.date()})
        elif s_id and not teamdesc_id:
            status = HTTP_200_OK
            if McyangTeamMember.objects.filter(S_id_id=s_id).exists():
                select = McyangTeamMember.objects.raw('select distinct tm.*, tl.Leader_id_id, td.TD_id, td.TD_doc from mc_teammember tm '
                                                      'inner join mc_team tl on tm.T_id_id = tl.T_id and tl.Group_number = 1 '
                                                      'inner join mc_teamdesc td on td.TD_id = tl.TD_id_id and td.TD_status = 1 '
                                                      'where tm.S_id_id = %s', [s_id])
                for i in select:
                    name = McyangStudent.objects.get(S_id=i.S_id_id).S_name
                    data.append({'TeamDesc_id': i.TD_id, 'TeamLeader_id': i.T_id_id, 'Doc': i.TD_doc, 'S_id': i.S_id_id, 'S_name': name, 'IsLeader': 'false'})
            if McyangTeam.objects.filter(Leader_id_id=s_id).exists():
                select = McyangTeam.objects.raw('select distinct tl.*, tl.Leader_id_id, td.TD_doc from mc_team tl '
                                                'inner join mc_teammember tm on tm.T_id_id = tl.T_id '
                                                'inner join mc_teamdesc td on td.TD_id = tl.TD_id_id and td.TD_status = 1 '
                                                'where tl.Group_number = 1 and tl.Leader_id_id = %s', [s_id])
                for i in select:
                    name = McyangStudent.objects.get(S_id=i.Leader_id_id).S_name
                    data.append({'TeamDesc_id': i.TD_id_id, 'TeamLeader_id': i.T_id, 'Doc': i.TD_doc, 'S_id': i.Leader_id_id, 'S_name': name, 'IsLeader': 'true'})
            data.sort(key=lambda x: -x['TeamDesc_id'])
        else:
            status = HTTP_400_BAD_REQUEST
    else:
        status = HTTP_500_INTERNAL_SERVER_ERROR

    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, status=status)


@csrf_exempt
def team_chat_create(request):
    teamdesc_id = request.POST.get('TeamDesc_id')
    chat_title = request.POST.get('Chat_title')
    print(teamdesc_id, chat_title)
    data = []

    if request.method == 'POST':
        if teamdesc_id and chat_title:
            if not McyangTeamChat.objects.filter(TeamDesc_id=teamdesc_id).exists():  # 判斷是否已經建立！
                try:
                    with transaction.atomic():
                        status = HTTP_200_OK
                        course_id = McyangTeamDesc.objects.get(TD_id=teamdesc_id).C_id
                        leader = McyangTeam.objects.raw('select distinct tl.* from mc_team tl '
                                                        'left join mc_teamdesc td on td.TD_id = tl.TD_id_id and td.TD_status = 1 '
                                                        'where td.TD_id = %s', [teamdesc_id])
                        for i in leader:
                            seq_no = McyangTeamChat.objects.filter().count() + 1
                            insert = McyangTeamChat.objects.create(GroupChat_id=seq_no, TeamLeader_id_id=i.T_id,
                                                                   TeamDesc_id_id=i.TD_id_id, ChatRoom=chat_title, Course_id=course_id, status=True)
                            data.append({'GroupChat_id': insert.GroupChat_id, 'ChatTitle': insert.ChatRoom, 'TeamLeader_id': insert.TeamLeader_id.T_id, 'S_name': insert.TeamLeader_id.Leader_id.S_name, 'CrtTime': insert.crtTime})

                except Exception as e:
                    status = HTTP_417_EXPECTATION_FAILED
                    print(e)
            else:
                title = McyangTeamChat.objects.filter(TeamDesc_id=teamdesc_id)[0].ChatRoom
                if chat_title != title:
                    try:
                        with transaction.atomic():
                            status = HTTP_200_OK
                            course_id = McyangTeamDesc.objects.get(TD_id=teamdesc_id).C_id
                            leader = McyangTeam.objects.raw('select distinct tl.* from mc_team tl '
                                                            'left join mc_teamdesc td on td.TD_id = tl.TD_id_id '
                                                            'where td.TD_id = %s', [teamdesc_id])
                            for i in leader:
                                seq_no = McyangTeamChat.objects.filter().count() + 1
                                insert = McyangTeamChat.objects.create(GroupChat_id=seq_no, TeamLeader_id_id=i.T_id, TeamDesc_id_id=i.TD_id_id, ChatRoom=chat_title, Course_id=course_id, status=True)
                                data.append({'GroupChat_id': insert.GroupChat_id, 'ChatTitle': insert.ChatRoom, 'TeamLeader_id': insert.TeamLeader_id.T_id, 'S_name': insert.TeamLeader_id.Leader_id.S_name, 'CrtTime': insert.crtTime})

                    except Exception as e:
                        status = HTTP_417_EXPECTATION_FAILED
                        print(e)
                else:
                    status = HTTP_406_NOT_ACCEPTABLE  # 重複！
        else:
            status = HTTP_400_BAD_REQUEST
    else:
        status = HTTP_500_INTERNAL_SERVER_ERROR

    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, status=status)


@csrf_exempt
def team_chat_list(request):
    course_id = request.GET.get('C_id', '')
    teamdesc_id = request.GET.get('TeamDesc_id', '')
    teamleader_id = request.GET.get('TeamLeader_id', '')
    chat_title = request.GET.get('ChatTitle', '')
    data = []

    if request.method == 'GET':
        if course_id and not teamdesc_id and not chat_title and not teamleader_id:
            status = HTTP_200_OK
            select = McyangTeamChat.objects.filter(Course_id=course_id)
            for i in select:
                data.append({'GroupChat_id': i.GroupChat_id, 'TeamLeader_id': i.TeamLeader_id.T_id, 'S_name': i.TeamLeader_id.Leader_id.S_name, 'ChatTitle': i.ChatRoom, 'CrtTime': i.crtTime.date(), 'TeamDesc_id': i.TeamDesc_id.TD_id})

        elif teamdesc_id and not course_id and not chat_title:
            status = HTTP_200_OK
            select = McyangTeamChat.objects.filter(TeamDesc_id=teamdesc_id).distinct()
            for i in select:
                data.append({'GroupChat_id': i.GroupChat_id, 'TeamLeader_id': i.TeamLeader_id.T_id, 'S_name': i.TeamLeader_id.Leader_id.S_name, 'ChatTitle': i.ChatRoom, 'CrtTime': i.crtTime.date(), 'C_id': i.Course_id.C_id})
        elif teamdesc_id and course_id and not chat_title and not teamleader_id:
            status = HTTP_200_OK
            duplicate = []
            select = McyangTeamChat.objects.filter(TeamDesc_id=teamdesc_id, Course_id=course_id).order_by('-crtTime')
            for i in select:
                if len(duplicate) == 0:
                    duplicate.append(i.ChatRoom)
                    data.append({'ChatTitle': i.ChatRoom, 'CrtTime': i.crtTime.date()})
                else:
                    if i.ChatRoom in duplicate:
                        continue
                    else:
                        duplicate.append(i.ChatRoom)
                        data.append({'ChatTitle': i.ChatRoom, 'CrtTime': i.crtTime.date()})
        elif chat_title and teamdesc_id and not course_id and not teamleader_id:
            status = HTTP_200_OK
            select = McyangTeamChat.objects.filter(ChatRoom=chat_title, TeamDesc_id=teamdesc_id)
            for i in select:
                data.append({'GroupChat_id': i.GroupChat_id, 'TeamLeader_id': i.TeamLeader_id.T_id, 'S_name': i.TeamLeader_id.Leader_id.S_name, 'ChatTitle': i.ChatRoom, 'CrtTime': i.crtTime.date(), 'C_id': i.Course_id.C_id})
        elif teamleader_id and not chat_title and not teamdesc_id and not course_id:
            status = HTTP_200_OK
            select = McyangTeamChat.objects.filter(TeamLeader_id_id=teamleader_id)
            for i in select:
                data.append({'GroupChat_id': i.GroupChat_id, 'S_name': i.TeamLeader_id.Leader_id.S_name, 'ChatTitle': i.ChatRoom})
        else:
            status = HTTP_400_BAD_REQUEST
    else:
        status = HTTP_500_INTERNAL_SERVER_ERROR

    return JsonResponse(data, safe=False, json_dumps_params={'ensure_ascii': False}, status=status)
