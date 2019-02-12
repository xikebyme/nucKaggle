from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .models import UserProfile,Team,UserCompetition,TeamRequest

# Create your views here.

def user_login(request):
    context = {}
    if request.method == 'POST':
        get_name = request.POST.get('username').strip()
        get_password = request.POST.get('password')
        user = authenticate(username=get_name, password=get_password)
        if user is not None:
            if user.is_active:
                request.session["username"] = user.username
                login(request,user)
                return HttpResponseRedirect('/')
            else:
                context['message'] = "您的用户已经被限制,请联系工作人员"
        else:
            context['message'] = "用户名或者密码错误"
        context['type']="登录"
        referer = request.META.get('HTTP_REFERER')
        context["redirect_to"] = referer
        return render(request,'account/error.html',context)
    return render(request,'account/login.html')


def register(request):
    context={}
    if request.method == 'POST':
        name = request.POST.get('Username').strip()
        u = User.objects.filter(username=name)
        if u:
            context['type'] = '注册'
            context['message'] = '该名字已被使用'
            referer = request.META.get('HTTP_REFERER')
            context["redirect_to"] = referer
            return render(request,'account/error.html',context)
        password = request.POST.get('password')
        email = request.POST.get('email')
        user = User.objects.create_user(name, email, password)
        user.save()
        url = r'/account/login'
        return HttpResponseRedirect(url)
    return render(request, 'account/register.html')


def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')

def team(request):
    context = {}
    teams = Team.objects.all()
    context["teams"] = teams
    return render(request,'account/team.html',context)

def create_team(request):
    context = {}
    if request.method == "POST":
        if(request.user.is_authenticated()):
            userprofile = UserProfile.objects.filter(user=request.user) #如果存在，则是一个对象的列表
            if userprofile:
                team_name = request.POST.get('队伍名').strip()
                i = Team.objects.filter(team_name=team_name)
                j = Team.objects.filter(captain=request.user)
                if (i or j):
                    context['type'] = '创建队伍'
                    context['message'] = '该队伍名字已被使用或您已创建过队伍,请更改队名或查找队伍'
                    referer = request.META.get('HTTP_REFERER')
                    context["redirect_to"] = referer
                    return render(request,'account/error.html',context)
                team = Team()
                team.team_name = team_name
                team.captain = request.user
                team.save()

                uc = UserCompetition()
                uc.userprofile = userprofile[0]
                uc.team = team
                uc.save()

                url = r'/account/team'
                return HttpResponseRedirect(url)
            else:
                context['type'] = '未报名参赛'
                context['message'] = '登录本网站,报名参赛后才能创建队伍'
                referer = request.META.get('HTTP_REFERER')
                context["redirect_to"] = referer
                return render(request,'account/error.html',context)
        else:
            context['type'] = '未登录'
            context['message'] = '请在主页按照网站注册信息登录或注册成为网站用户后登录'
            referer = request.META.get('HTTP_REFERER')
            context["redirect_to"] = referer
            return render(request,'account/error.html',context)
    return render(request,'account/create_team.html')

def enter_com(request):
    context = {}
    if request.method == 'POST':
        if(request.user.is_authenticated()):
            name = request.POST.get('name').strip()
            school = request.POST.get('school').strip()
            student_id = request.POST.get('student_id').strip()
            phone = request.POST.get('phone').strip()
            sex = request.POST.get('sex').strip()     ###好像只有phone是不可能重复的，留个疑问？？？？

            up = UserProfile()
            up.student_id = student_id
            up.name = name
            up.user = request.user
            up.college = school
            up.phone = phone
            up.sex = sex
            up.save()

            competitors = UserProfile.objects.all()
            context["competitors"] = competitors
            url = r'/account/entercom'
            return HttpResponseRedirect(url)
        else:
            context['type'] = '未登录'
            context['message'] = '请在主页按照网站注册信息登录或注册成为网站用户后登录'
            referer = request.META.get('HTTP_REFERER')
            context["redirect_to"] = referer
            return render(request,'account/error.html',context)
    competitors = UserProfile.objects.all()
    context["competitors"] = competitors
    context["send_by_team"] = 1
    return render(request,'account/enter_com.html',context)

def join_team(request):
    context = {}
    if(request.user.is_authenticated()):   #如果登录
        userprofile = UserProfile.objects.filter(user=request.user)
        if userprofile:                    #如果报名参赛
            team = Team.objects.filter(captain=request.user)
            if not team:                       #如果用户不是队长
                teams = Team.objects.all()
                context["send_by_team"] = 0
                context["teams"] = teams
            else:
                context['type'] = '队长已加入队伍'
                context['message'] = '您已经是队长,请在报名参赛页面邀请队员加入队伍'
                referer = request.META.get('HTTP_REFERER')
                context["redirect_to"] = referer
                return render(request,'account/error.html',context)
        else:
            context['type'] = '未报名参赛'
            context['message'] = '登录本网站,报名参赛后才能加入队伍'
            referer = request.META.get('HTTP_REFERER')
            context["redirect_to"] = referer
            return render(request,'account/error.html',context)
    else:
        context['type'] = '未登录'
        context['message'] = '请在主页按照网站注册信息登录或注册成为网站用户后登录'
        referer = request.META.get('HTTP_REFERER')
        context["redirect_to"] = referer
        return render(request,'account/error.html',context)
    return render(request,'account/join_team.html',context)

def join_req(request,team_pk,send_by_team):
    context = {}

    #判断此用户是否已经加入队伍
    userprofile = UserProfile.objects.filter(user=request.user)
    up = userprofile[0]
    user_com = UserCompetition.objects.filter(userprofile=up)
    if user_com:
        context['type'] = '已加入队伍'
        context['message'] = '您已经加入队伍,无法再申请加入队伍,请前往个人中心查看'
        referer = request.META.get('HTTP_REFERER')
        context["redirect_to"] = referer
        return render(request,'account/error.html',context)

    team = Team.objects.filter(pk=team_pk)
    te = team[0]

    req = TeamRequest.objects.filter(userprofile=up)
    if req:     ###如果此请求对象已经创建,此行避免报错
        context['type'] = '已发送入队请求'
        context['message'] = '您已经发送过入队请求,无法再申请加入队伍,请前往个人中心查看'
        referer = request.META.get('HTTP_REFERER')
        context["redirect_to"] = referer
        return render(request,'account/error.html',context)
    if int(te.peo_num)==5:
        context['type'] = '人数超限'
        context['message'] = '您申请加入的队伍的队伍成员已达五人,无法再申请加入队伍'
        referer = request.META.get('HTTP_REFERER')
        context["redirect_to"] = referer
        return render(request,'account/error.html',context)
    ##判断在邀请的同时对方是否也在申请你的队伍
    uespro = UserProfile.filter(user = request.user)
    team_reqe1 = TeamRequest.objects.filter(userprofile=uespro[0],team=te,tag=True)
    if team_reqe1:  #对方也在邀请你
        te_re = team_reqe1[0]

        uc = UserCompetition()
        uc.userprofile = te_re.userprofile
        uc.team = te_re.team
        uc.save()
        num = int(tm.peo_num)
        num += 1
        tm.peo_num = num    #成功加入队伍，队伍人数计数加一

        #清除 请求 数据表
        te_re.delete()

        userprofile_name = te_re.userprofile.user.username
        context["userprofile_name"] = userprofile_name
        context["team"] = te_re.team.team_name
        return render(request,'account/successful.html',context)
    team_req = TeamRequest()
    team_req.team_id = te.pk
    team_req.userprofile_id = up.pk
    if int(send_by_team):
        team_req.tag = True
    else:
        team_req.tag = False
    team_req.save()

    team_name = te.team_name
    context["team_name"] = team_name
    return render(request,'account/join_req.html',context)

def invite(request,user_id,send_by_team,userprofile_id):
    context = {}
    ##判断此用户是否是队长
    team = Team.objects.filter(captain=request.user)
    if team:  #是队长
        #判断所邀请的参赛者是否是队长
        team1 = Team.objects.filter(captain_id=user_id)
        if team1:  #邀请的成员是队长，返回错误界面
            context['type'] = '无法邀请'
            context['message'] = '您邀请的此成员是队长,您无法邀请'
            referer = request.META.get('HTTP_REFERER')
            context["redirect_to"] = referer
            return render(request,'account/error.html',context)
        else:
            tm = team[0]
            if int(tm.peo_num)<5:
                ##判断在邀请的同时对方是否也在申请你的队伍 
                team_reqe1 = TeamRequest.objects.filter(userprofile_id=userprofile_id,team=team[0],tag=False)
                if team_reqe1:  #对方也在邀请你
                    te_re = team_reqe1[0]

                    uc = UserCompetition()
                    uc.userprofile = te_re.userprofile
                    uc.team = te_re.team
                    uc.save()
                    num = int(tm.peo_num)
                    num += 1
                    tm.peo_num = num    #成功加入队伍，队伍人数计数加一

                    #清除 请求 数据表_____________
                    te_re.delete()

                    userprofile_name = te_re.userprofile.user.username
                    context["userprofile_name"] = userprofile_name
                    context["team"] = te_re.team.team_name
                    return render(request,'account/successful.html',context)
                else:
                    #判断队长是否已经发送过请求，避免多次点击此页面重复建记录不友好报错
                    team_reqe2 = TeamRequest.objects.filter(userprofile_id=userprofile_id,team=team[0],tag=True)
                    if team_reqe2:  #数据库中已经存在此条请求记录
                        context['type'] = '已发送入队邀请'
                        context['message'] = '您已经发送过此条入队请求,无法再次邀请,请前往个人中心查看'
                        referer = request.META.get('HTTP_REFERER')
                        context["redirect_to"] = referer
                        return render(request,'account/error.html',context)
                    else:
                        te = team[0]
                        userprofile = UserProfile.objects.filter(user_id = user_id)
                        up = userprofile[0]
                        if int(send_by_team):
                            send_by_team = True
                        else:
                            send_by_team = False

                        team_req = TeamRequest()
                        team_req.team_id = te.pk
                        team_req.userprofile_id = up.pk
                        team_req.tag = send_by_team
                        team_req.save()

                        context["userprofile_name"] = up.user.username
            else:
                context['type'] = '人数超限'
                context['message'] = '您的队伍成员已达五人,无法继续邀请成员'
                referer = request.META.get('HTTP_REFERER')
                context["redirect_to"] = referer
                return render(request,'account/error.html',context)
    else:
        context['type'] = '无权限'
        context['message'] = '您不是队长,您没有邀请权限'
        referer = request.META.get('HTTP_REFERER')
        context["redirect_to"] = referer
        return render(request,'account/error.html',context)
    return render(request,'account/invite.html',context)

def req_deal(request):
    context = {}
    if(request.user.is_authenticated()):   #如果登录
        user = request.user
        userprofile = UserProfile.objects.filter(user=user)
        if userprofile:
            team = Team.objects.filter(captain=user)
            if team:
                te = team[0]
                context["status"] = "队长"
                context["team"] = te
                context["team_compare"] = UserCompetition.objects.filter(team=te)
                inv = TeamRequest.objects.filter(team=te)
                peo_invite = []
                ap = []
                for i in inv:
                    if i.tag == True:
                        peo_invite.append(i)
                    else:
                        ap.append(i)
                context["peo_invite"] = peo_invite
                context["ap"] = ap
            else:
                context["status"] = "报名参赛人员"
                teamrequest  = TeamRequest.objects.filter(userprofile=userprofile)
                invite = []
                ap = []
                for i in teamrequest:
                    if i.tag==True:
                        invite.append(i)
                    else:
                        ap.append(i)
                context["invite"] = invite
                context["ap"] = ap
        else:
            context['type'] = '未报名参赛'
            context['message'] = '登录本网站,报名参赛后才能查看此页面'
            referer = request.META.get('HTTP_REFERER')
            context["redirect_to"] = referer
            return render(request,'account/error.html',context)
    else:
        context['type'] = '未登录'
        context['message'] = '请在主页按照网站注册信息登录或注册成为网站用户后登录'
        referer = request.META.get('HTTP_REFERER')
        context["redirect_to"] = referer
        return render(request,'account/error.html',context)
    return render(request,'account/req_deal.html',context)

def agree(request,team_id,userprofile_id,team_req_pk):  
    ##写入数据库的响应最好加些后端判断，前端的简单判断不行------后期要做----------
    context = {}
    team = Team.objects.filter(id=team_id)
    te = team[0]
    uc = UserCompetition.objects.filter(userprofile_id = userprofile_id)
    if uc:
        context['type'] = '已经加入队伍'
        context['message'] = '您或您邀请的人已经加入队伍,可以到个人中心查看,请不要重复操作'
        referer = request.META.get('HTTP_REFERER')
        context["redirect_to"] = referer
        return render(request,'account/error.html',context)
    if int(te.peo_num)<5: #看看队伍人数是否超过人数5人 
        usercompetition = UserCompetition()
        usercompetition.team_id = team_id
        usercompetition.userprofile_id = userprofile_id
        usercompetition.save()
        num = int(te.peo_num)
        num += 1
        te.peo_num = num  #成员数计数加一
        team_req = TeamRequest.objects.filter(id=team_req_pk)
        tr = team_req[0]
        tr.delete()       #清除请求数据表
        url = r'/account/reqdeal'
        return HttpResponseRedirect(url)
    else:
        context['type'] = '人数超限'
        context['message'] = '该队伍已达最大人数5人,您无法继续加入或邀请人加入'
        referer = request.META.get('HTTP_REFERER')
        context["redirect_to"] = referer
        return render(request,'account/error.html',context)

 