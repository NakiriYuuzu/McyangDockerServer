from django.db import models


# Create your models here.
# 資料庫中創建字段
class McyangTeacher(models.Model):
    T_id = models.AutoField(primary_key=True, default=1)
    T_name = models.TextField(max_length=30)
    T_email = models.CharField(max_length=50, unique=True)
    T_password = models.TextField(max_length=50)
    T_image = models.ImageField(upload_to='img_teacher/', blank=True, null=True)
    crtTime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'T_id: {self.T_id}   TeacherName: {self.T_name}'

    class Meta:
        unique_together = (('T_id', 'T_email'),)
        db_table = 'mc_teacher'


class McyangStudent(models.Model):
    S_id = models.AutoField(primary_key=True, default=1)
    S_name = models.TextField(max_length=30)
    S_email = models.CharField(max_length=50, unique=True)
    S_password = models.TextField(max_length=50)
    S_image = models.ImageField(upload_to='img_student/', blank=True, null=True)
    crtTime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'S_id: {self.S_id}   StudentName: {self.S_name}'

    class Meta:
        db_table = 'mc_student'


# 課程
class McyangCourse(models.Model):
    C_id = models.AutoField(primary_key=True, default=1)
    T_id = models.ForeignKey(McyangTeacher, on_delete=models.CASCADE, to_field="T_id")
    C_name = models.TextField(max_length=30)
    C_image = models.ImageField(upload_to='img_course/', blank=True, null=True)
    crtTime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'C_id: {self.C_id}   CourseName: {self.C_name}'

    class Meta:
        db_table = 'mc_course'


# 修課紀錄
class McyangCourseRecord(models.Model):
    CR_id = models.AutoField(primary_key=True, default=1)
    C_id = models.ForeignKey(McyangCourse, on_delete=models.CASCADE, to_field="C_id")
    S_id = models.ForeignKey(McyangStudent, on_delete=models.CASCADE, to_field="S_id")
    crtTime = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mc_courserecord'


class McyangRaceAnswer(models.Model):
    R_id = models.AutoField(primary_key=True, default=1)
    C_id = models.ForeignKey(McyangCourse, on_delete=models.CASCADE, to_field="C_id")
    R_doc = models.TextField(max_length=255)
    Status = models.BooleanField(default=True)
    crtTime = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mc_raceanswer'


class McyangRaceList(models.Model):
    RL_id = models.AutoField(primary_key=True, default=1)
    R_id = models.ForeignKey(McyangRaceAnswer, on_delete=models.CASCADE, to_field="R_id")
    S_id = models.ForeignKey(McyangStudent, on_delete=models.CASCADE, to_field="S_id")  # 搶答的學生
    Answer = models.IntegerField(default=0)  # 0, 1, 99 沒回答, 回答,
    crtTime = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mc_racelist'


# 點名單
class McyangSign(models.Model):
    Sign_id = models.AutoField(primary_key=True, default=1)
    C_id = models.ForeignKey(McyangCourse, on_delete=models.CASCADE, to_field="C_id")
    crtTime = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mc_sign'


# 紀錄有簽到的學生
class McyangSignRecord(models.Model):
    SR_id = models.AutoField(primary_key=True, default=1)
    Sign_id = models.ForeignKey(McyangSign, on_delete=models.CASCADE, to_field="Sign_id")
    S_id = models.ForeignKey(McyangStudent, on_delete=models.CASCADE, to_field="S_id")
    crtTime = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mc_signrecord'


class McyangTeamDesc(models.Model):
    TD_id = models.AutoField(primary_key=True, default=1)
    TD_doc = models.TextField(max_length=255)
    TD_total = models.IntegerField()
    TD_limit = models.IntegerField()
    TD_status = models.IntegerField(null=True)  # 0=Close 1=On
    C_id = models.ForeignKey(McyangCourse, on_delete=models.CASCADE, to_field="C_id")
    crtTime = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mc_teamdesc'


class McyangTeam(models.Model):
    T_id = models.AutoField(primary_key=True, default=1)
    TD_id = models.ForeignKey(McyangTeamDesc, on_delete=models.CASCADE, to_field="TD_id")
    Group_number = models.IntegerField(null=True)  # 0=未選上 1=選上
    Leader_id = models.ForeignKey(McyangStudent, on_delete=models.CASCADE)
    crtTime = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mc_team'


class McyangTeamMember(models.Model):
    TM_id = models.AutoField(primary_key=True, default=1)
    S_id = models.ForeignKey(McyangStudent, on_delete=models.CASCADE, to_field="S_id")
    T_id = models.ForeignKey(McyangTeam, on_delete=models.CASCADE, to_field="T_id")
    Team_number = models.IntegerField(null=True)  # 0=未選上 1=選上
    crtTime = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mc_teammember'


class McyangQuizTopic(models.Model):
    QT_id = models.AutoField(primary_key=True, default=1)
    QT_doc = models.TextField(max_length=255)
    C_id = models.ForeignKey(McyangCourse, on_delete=models.CASCADE, to_field="C_id")
    crtTime = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mc_quiztopic'


class McyangQuizQuestion(models.Model):
    QQ_id = models.AutoField(primary_key=True, default=1)
    QT_id = models.ForeignKey(McyangQuizTopic, on_delete=models.CASCADE, to_field="QT_id")
    QQ_title = models.TextField(max_length=255)
    QQ_doc = models.TextField(max_length=255)
    QQ_status = models.BooleanField(default=True)  # 0, 1
    crtTime = models.DateTimeField(auto_now_add=255)

    class Meta:
        db_table = 'mc_quizquestion'


class McyangQuizAnswer(models.Model):
    QA_id = models.AutoField(primary_key=True, default=1)
    QQ_id = models.ForeignKey(McyangQuizQuestion, on_delete=models.CASCADE, to_field="QQ_id")
    S_id = models.ForeignKey(McyangStudent, on_delete=models.CASCADE, to_field="S_id")
    Answer_doc = models.TextField(max_length=255)
    Answer = models.IntegerField(default=0)  # 0沒回答， 1回答， 99答對
    crtTime = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mc_answermember'


class McyangTeamChat(models.Model):
    GroupChat_id = models.AutoField(primary_key=True, default=1)
    TeamDesc_id = models.ForeignKey(McyangTeamDesc, on_delete=models.CASCADE, to_field="TD_id")
    Course_id = models.ForeignKey(McyangCourse, on_delete=models.CASCADE, to_field="C_id")
    TeamLeader_id = models.ForeignKey(McyangTeam, on_delete=models.CASCADE, to_field="T_id")
    ChatRoom = models.CharField(max_length=100, null=True)
    crtTime = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(null=True)

    class Meta:
        db_table = 'mc_Teamchat'
