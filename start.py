# (C) 2019-2020 lifegpc
# This file is part of bili.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import requests
import HTMLParser
import JSONParser
import PrintInfo
import biliLogin
import biliPlayerXmlParser
import biliDanmu
import biliTime
import chon
import videodownload
import biliBv
from re import search,I
import os 
import sys
from command import gopt
import json
from math import ceil
from dictcopy import copyip,copydict
from biliHdVideo import getninfo
import traceback
import biliLiveDanmu
def main(ip={}):
    se=JSONParser.loadset()
    ns=True
    if 's' in ip :
        ns=False
    if not isinstance(se,dict) :
        se=None
        print('建议运行setsettings.py设置程序以减少不必要的询问。')
    nte=False
    if JSONParser.getset(se,'te')==False :
        nte=True
    if 'te' in ip:
        nte=not ip['te']
    if 'i' in ip :
        inp=ip['i']
    elif ns:
        inp=input("请输入av号（支持SS、EP、MD号，BV号请以BV开头，现在已支持链接，支持用户页的收藏夹、频道、投稿、小视频链接，支持直播回放链接）：")
    else :
        print('请使用-i <输入>')
        return -1
    av=False
    ss=False
    ep=False
    pl=False #收藏夹
    hd=False #互动视频
    ch=False #频道
    uv=False #投稿
    md=False #番剧信息页
    sm=False #小视频
    lr=False #直播回放
    uid=-1 #收藏夹/频道主人id
    fid=-1 #收藏夹id
    cid=-1 #频道id
    uvd={} #投稿查询信息
    pld={} #收藏夹扩展信息
    mid=-1 #md号
    sid=-1 #小视频id
    rid="" #直播回放id
    if inp[0:2].lower()=='ss' and inp[2:].isnumeric() :
        s="https://www.bilibili.com/bangumi/play/ss"+inp[2:]
        ss=True
    elif inp[0:2].lower()=='ep' and inp[2:].isnumeric() :
        s="https://www.bilibili.com/bangumi/play/ep"+inp[2:]
        ep=True
    elif inp[0:2].lower()=='av' and inp[2:].isnumeric() :
        s="https://www.bilibili.com/video/av"+inp[2:]
        av=True
    elif inp[0:2].lower()=='bv' :
        inp=str(biliBv.debv(inp))
        s="https://www.bilibili.com/video/av"+inp
        av=True
    elif inp[0:2].lower()=='md' and inp[2:].isnumeric() :
        md=True
        mid=int(inp[2:])
    elif inp.isnumeric() :
        s="https://www.bilibili.com/video/av"+inp
        av=True
    else :
        re=search(r'([^:]+://)?(www.)?(space.)?(vc.)?(m.)?(live.)?bilibili.com/(video/av([0-9]+))?(video/(bv[0-9A-Z]+))?(bangumi/play/(ss[0-9]+))?(bangumi/play/(ep[0-9]+))?(([0-9]+)/favlist(\?(.+)?)?)?(([0-9]+)/channel/(index)?(detail\?cid=([0-9]+))?)?(([0-9]+)/video(\?(.+)?)?)?(bangumi/media/md([0-9]+))?(video/([0-9]+))?(mobile/detail\?vc=([0-9]+))?(record/([^\?]+))?',inp,I)
        if re==None :
            re=search(r'([^:]+://)?(www.)?b23.tv/(av([0-9]+))?(bv[0-9A-Z]+)?(ss[0-9]+)?(ep[0-9]+)?',inp,I)
            if re==None :
                print('输入有误')
                exit()
            else :
                re=re.groups()
                if re[3] :
                    inp=re[3]
                    s="https://www.bilibili.com/video/av"+inp
                    av=True
                elif re[4] :
                    inp=str(biliBv.debv(re[4]))
                    s="https://www.bilibili.com/video/av"+inp
                    av=True
                elif re[5] :
                    inp=re[5]
                    s="https://www.bilibili.com/bangumi/play/"+inp
                    ss=True
                elif re[6] :
                    inp=re[6]
                    s="https://www.bilibili.com/bangumi/play/"+inp
                    ep=True
                else :
                    print('输入有误')
                    exit()
        else :
            re=re.groups()
            if re[7] :
                inp=re[7]
                s="https://www.bilibili.com/video/av"+inp
                av=True
            elif re[9] :
                inp=str(biliBv.debv(re[9]))
                s="https://www.bilibili.com/video/av"+inp
                av=True
            elif re[11] :
                inp=re[11]
                s="https://www.bilibili.com/bangumi/play/"+inp
                ss=True
            elif re[13] :
                inp=re[13]
                s="https://www.bilibili.com/bangumi/play/"+inp
                ep=True
            elif re[15] :
                pl=True
                uid=int(re[15])
                pld['k']=''
                pld['t']=0
                if re[17] :
                    sl=re[17].split('&')
                    for us in sl:
                        rep=search(r'^(fid=([0-9]+))?(keyword=(.+))?(type=([0-9]+))?',us,I)
                        if rep!=None :
                            rep=rep.groups()
                            if rep[0]:
                                fid=int(rep[1])
                            if rep[2]:
                                pld['k']=rep[3]
                            if rep[4]:
                                pld['t']=int(rep[5])
            elif re[18]:
                ch=True
                uid=int(re[19])
                if re[22] :
                    cid=int(re[22])
            elif re[23]:
                uv=True
                uid=int(re[24])
                uvd['t']=0
                uvd['k']=''
                uvd['o']='pubdate'
                if re[26]:
                    sl=re[26].split('&')
                    for us in sl:
                        rep=search(r'^(tid=([0-9]+))?(keyword=(.+)?)?(order=(.+)?)?',us,I)
                        if rep!=None :
                            rep=rep.groups()
                            if rep[0]:
                                uvd['t']=int(rep[1])
                            elif rep[3]:
                                uvd['k']=rep[3]
                            elif rep[5]:
                                uvd['o']=rep[5]
            elif re[27] :
                md=True
                mid=int(re[28])
            elif re[29] :
                sm=True
                sid=int(re[30])
            elif re[31]:
                sm=True
                sid=int(re[32])
            elif re[33] :
                lr=True
                rid=re[34]
            else :
                print('输入有误')
                exit()
    section=requests.session()
    section.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36","Connection": "keep-alive","Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8","Accept-Language": "zh-CN,zh;q=0.8"})
    if 'httpproxy' in ip or 'httpsproxy' in ip:
        pr={}
        if 'httpproxy' in ip:
            pr['http']=ip['httpproxy']
        if 'httpsproxy' in ip:
            pr['https']=ip['httpsproxy']
        section.proxies=pr
    if nte:
        section.trust_env=False
    read=JSONParser.loadcookie(section)
    ud={}
    login=0
    if read==0 :
        read=biliLogin.tryok(section,ud)
        if read==True :
            if ns:
                print("登录校验成功！")
            login=1
        elif read==False :
            print('网络错误！校验失败！')
            exit()
        else :
            print("登录信息已过期！")
            login=2
    elif read==-1 :
        login=2
    else :
        print("文件读取错误！")
        login=2
    if login==2 :
        if os.path.exists('cookies.json') :
            os.remove('cookies.json')
        read=biliLogin.login(section,ud,ip)
        if read==0 :
            login=1
        elif read==1 :
            exit()
        else :
            exit()
    if not 'd' in ud:
        return -1
    ud['vip']=ud['d']['vipStatus']
    if sm :
        re=section.get('https://api.vc.bilibili.com/clip/v1/video/detail?video_id=%s&need_playurl=1'%(sid))
        re.encoding="utf8"
        re=re.json()
        if re['code']!=0 :
            print('%s %s'%(re['code'],re['message']))
            return -1
        inf=JSONParser.getsmi(re)
        if ns:
            PrintInfo.printInfo9(inf)
        cho5=False
        bs=True
        if not ns:
            bs=False
        read=JSONParser.getset(se,'cd')
        if read==True :
            bs=False
            cho5=True
        elif read==False:
            bs=False
        if 'ac' in ip :
            if ip['ac'] :
                bs=False
                cho5=True
            else :
                bs=False
                cho5=False
        while bs:
            inp=input('是否开启继续下载功能？(y/n)')
            if len(inp)>0 :
                if inp[0].lower()=='y' :
                    cho5=True
                    bs=False
                elif inp[0].lower()=='n' :
                    bs=False
        videodownload.smdownload(section,inf,cho5,se,ip)
        return 0
    if md :
        re=section.get('https://www.bilibili.com/bangumi/media/md%s'%(mid))
        re.encoding="utf8"
        rs=search(r'__INITIAL_STATE__=([^;]+)',re.text,I)
        if rs!=None :
            rs=rs.groups()[0]
            re=json.loads(rs)
            ip2=copyip(ip)
            if 'p' in ip :
                ip2['p']=ip['p']
            ip2['i']='ss%s'%(re['mediaInfo']['season_id'])
            read=main(ip2)
            if read!=0 :
                return read
        else :
            print('md号解析失败')
            return -1
        return 0
    if pl :
        if fid==-1 :
            af=False
            if JSONParser.getset(se,'af')==True :
                af=True
            if 'af' in ip :
                af=ip['af']
            re=section.get('https://api.bilibili.com/x/v3/fav/folder/created/list-all?up_mid=%s&jsonp=jsonp'%(uid))
            re.encoding='utf8'
            re=re.json()
            if re['code']!=0 :
                print('%s %s'%(re['code'],re['message']))
                return -1
            else :
                if 'data' in re and 'list' in re['data'] and re['data']['count']>0:
                    if af:
                        dc=re['data']['count']
                        if ns:
                            PrintInfo.printInfo8(re)
                        bs=True
                        f=True
                        while bs:
                            if f and 'afp' in ip:
                                f=False
                                inp=ip['afp']
                            elif ns:
                                inp=input('请输入你想选择的收藏夹编号，每两个编号间用,隔开，全部选择可输入a')
                            else :
                                print('请使用--afp <序号>选择收藏夹编号')
                                return -1
                            cho=[]
                            if len(inp)>0 and inp[0]=='a' :
                                if ns:
                                    print('您全选了所有收藏夹')
                                for i in range(1,dc+1) :
                                    cho.append(i)
                                    bs=False
                            elif len(inp)>0 :
                                inp=inp.split(',')
                                bb=True
                                for i in inp :
                                    if i.isnumeric() and int(i)>0 and int(i)<=dc and (not (int(i) in cho)) :
                                        cho.append(int(i))
                                    else :
                                        bb=False
                                if bb :
                                    bs=False
                                    for i in cho :
                                        if ns:
                                            print("您选中了第"+str(i)+"个收藏夹："+re['data']['list'][i-1]['title'])
                        for i in cho:
                            ip2=copyip(ip)
                            ip2['i']="https://space.bilibili.com/%s/favlist?fid=%s"%(uid,re['data']['list'][i-1]['id'])
                            read=main(ip2)
                            if read!=0 :
                                return read
                        return 0
                    else:
                        fid=re['data']['list'][0]['id']
                else :
                    print('获取收藏夹列表失败')
                    return -1
        i=1
        re=JSONParser.getpli(section,fid,i,pld)
        if re==-1 :
            return -1
        pli=JSONParser.getplinfo(re)
        if ns:
            PrintInfo.printInfo3(pli)
        n=ceil(pli['count']/20)
        plv=[]
        JSONParser.getpliv(plv,re)
        while i<n :
            i=i+1
            re=JSONParser.getpli(section,fid,i,pld)
            if re==-1 :
                return -1
            JSONParser.getpliv(plv,re)
        if len(plv)!=pli['count'] :
            print('视频数量不符，貌似BUG了？')
            return -1
        if ns:
            PrintInfo.printInfo4(plv)
        bs=True
        f=True
        while bs:
            if f and 'p' in ip:
                f=False
                inp=ip['p']
            elif ns :
                inp=input('请输入你想下载的视频编号，每两个编号间用,隔开，全部下载可输入a')
            else :
                print('请使用-p <p数>选择视频编号')
                return -1
            cho=[]
            if inp[0]=='a' :
                if ns:
                    print('您全选了所有视频')
                for i in range(1,pli['count']+1) :
                    cho.append(i)
                bs=False
            else :
                inp=inp.split(',')
                bb=True
                for i in inp :
                    if i.isnumeric() and int(i)>0 and int(i)<=pli['count'] and (not (int(i) in cho)) :
                        cho.append(int(i))
                    else :
                        bb=False
                if bb :
                    bs=False
                    for i in cho :
                        if ns:
                            print("您选中了第"+str(i)+"个视频："+plv[i-1]['title'])
        bs=True
        c1=False
        if not ns:
            bs=False
        read=JSONParser.getset(se,'da')
        if read!=None :
            c1=read
            bs=False
        if 'da' in ip :
            c1=ip['da']
            bs=False
        while bs :
            inp=input("是否自动下载每一个视频的所有分P？(y/n)")
            if len(inp)>0 :
                if inp[0].lower()=='y' :
                    c1=True
                    bs=False
                elif inp[0].lower()=='n' :
                    bs=False
        for i in cho:
            ip2=copyip(ip)
            ip2['i']=str(plv[i-1]['id'])
            if c1:
                ip2['p']='a'
            read=main(ip2)
            if read!=0 :
                return read
        return 0
    if ch :
        r=requests.Session()
        r.headers=copydict(section.headers)
        r.proxies=section.proxies
        if nte:
            r.trust_env=False
        read=JSONParser.loadcookie(r)
        if read!=0 :
            print("读取cookies.json出现错误")
            return -1
        r.cookies.set('CURRENT_QUALITY','120',domain='.bilibili.com',path='/')
        r.cookies.set('CURRENT_FNVAL','16',domain='.bilibili.com',path='/')
        r.cookies.set('laboratory','1-1',domain='.bilibili.com',path='/')
        r.cookies.set('stardustvideo','1',domain='.bilibili.com',path='/')
        if cid ==-1 :
            r.headers.update({'referer':'https://space.bilibili.com/%s/channel/index'%(uid)})
            re=r.get("https://api.bilibili.com/x/space/channel/list?mid=%s&guest=false&jsonp=jsonp"%(uid))
            re.encoding='utf8'
            re=re.json()
            if re['code']!=0 :
                print('%s %s'%(re['code'],re['message']))
                return -1
            chl=JSONParser.getchl(re)
            if ns:
                PrintInfo.printInfo5(chl)
            bs=True
            f=True
            while bs:
                if f and 'p' in ip:
                    f=False
                    inp=ip['p']
                elif ns :
                    inp=input('请输入你想下载的频道，每两个编号间用,隔开，全部下载可输入a')
                else :
                    print('请使用-p <p数>选择视频编号')
                    return -1
                cho=[]
                if inp[0]=='a' :
                    if ns:
                        print('您全选了所有频道')
                    for i in range(1,len(chl)+1) :
                        cho.append(i)
                    bs=False
                else :
                    inp=inp.split(',')
                    bb=True
                    for i in inp :
                        if i.isnumeric() and int(i)>0 and int(i)<=len(chl) and (not (int(i) in cho)) :
                            cho.append(int(i))
                        else :
                            bb=False
                    if bb :
                        bs=False
                        for i in cho :
                            if ns:
                                print("您选中了第"+str(i)+"个频道："+chl[i-1]['name'])
                for i in cho :
                    ip2=copyip(ip)
                    ip2['i']='https://space.bilibili.com/%s/channel/detail?cid=%s'%(uid,chl[i-1]['cid'])
                    read=main(ip2)
                    if read!=0 :
                        return read
            return 0
        r.headers.update({'referer':'https://space.bilibili.com/%s/channel/detail?cid=%s'%(uid,cid)})
        re=JSONParser.getchi(r,uid,cid,1)
        if re == -1:
            return -1
        chi=JSONParser.getchn(re)
        n=ceil(chi['count']/30)
        i=1
        chv=[]
        JSONParser.getchs(chv,re)
        while i<n :
            i=i+1
            re=JSONParser.getchi(r,uid,cid,i)
            if re==-1 :
                return -1
            JSONParser.getchs(chv,re)
        if chi['count'] != len(chv) :
            print('视频数量不符，貌似BUG了？')
            return -1
        if ns:
            PrintInfo.printInfo6(chv,chi)
        bs=True
        f=True
        while bs:
            if f and 'p' in ip:
                f=False
                inp=ip['p']
            elif ns:
                inp=input('请输入你想下载的视频编号，每两个编号间用,隔开，全部下载可输入a')
            else :
                print('请使用-p <p数>选择视频编号')
                return -1
            cho=[]
            if inp[0]=='a' :
                if ns:
                    print('您全选了所有视频')
                for i in range(1,chi['count']+1) :
                    cho.append(i)
                bs=False
            else :
                inp=inp.split(',')
                bb=True
                for i in inp :
                    if i.isnumeric() and int(i)>0 and int(i)<=chi['count'] and (not (int(i) in cho)) :
                        cho.append(int(i))
                    else :
                        bb=False
                if bb :
                    bs=False
                    for i in cho :
                        if ns:
                            print("您选中了第"+str(i)+"个视频："+chv[i-1]['title'])
        bs=True
        c1=False
        if not ns:
            bs=False
        read=JSONParser.getset(se,'da')
        if read!=None :
            c1=read
            bs=False
        if 'da' in ip :
            c1=ip['da']
            bs=False
        while bs :
            inp=input("是否自动下载每一个视频的所有分P？(y/n)")
            if len(inp)>0 :
                if inp[0].lower()=='y' :
                    c1=True
                    bs=False
                elif inp[0].lower()=='n' :
                    bs=False
        for i in cho:
            ip2=copyip(ip)
            ip2['i']=str(chv[i-1]['aid'])
            if c1:
                ip2['p']='a'
            read=main(ip2)
            if read!=0 :
                return read
        return 0
    if uv:
        re=JSONParser.getup(uid,section)
        if re==-1 :
            return -1
        up=JSONParser.getupi(re)
        re=JSONParser.getuvi(uid,1,uvd,section)
        if re==-1:
            return -1
        vn=re['data']['page']['count']
        n=ceil(vn/30)
        i=1
        vl=[]
        JSONParser.getuvl(re,vl)
        while i<n :
            i=i+1
            re=JSONParser.getuvi(uid,i,uvd,section)
            if re==-1 :
                return -1
            JSONParser.getuvl(re,vl)
        if len(vl) !=vn :
            print('视频数量不符，貌似BUG了？')
            return -1
        if ns:
            PrintInfo.printInfo7(up,vl)
        bs=True
        f=True
        while bs:
            if f and 'p' in ip:
                f=False
                inp=ip['p']
            elif ns:
                inp=input('请输入你想下载的视频编号，每两个编号间用,隔开，全部下载可输入a')
            else :
                print('请使用-p <p数>选择视频编号')
                return -1
            cho=[]
            if inp[0]=='a' :
                if 'ns':
                    print('您全选了所有视频')
                for i in range(1,vn+1) :
                    cho.append(i)
                bs=False
            else :
                inp=inp.split(',')
                bb=True
                for i in inp :
                    if i.isnumeric() and int(i)>0 and int(i)<=vn and (not (int(i) in cho)) :
                        cho.append(int(i))
                    else :
                        bb=False
                if bb :
                    bs=False
                    for i in cho :
                        if ns:
                            print("您选中了第"+str(i)+"个视频："+vl[i-1]['title'])
        bs=True
        c1=False
        if not ns:
            bs=False
        read=JSONParser.getset(se,'da')
        if read!=None :
            c1=read
            bs=False
        if 'da' in ip :
            c1=ip['da']
            bs=False
        while bs :
            inp=input("是否自动下载每一个视频的所有分P？(y/n)")
            if len(inp)>0 :
                if inp[0].lower()=='y' :
                    c1=True
                    bs=False
                elif inp[0].lower()=='n' :
                    bs=False
        for i in cho:
            ip2=copyip(ip)
            ip2['i']=str(vl[i-1]['aid'])
            if c1:
                ip2['p']='a'
            read=main(ip2)
            if read!=0 :
                return read
        return 0
    xml=0
    xmlc=[]
    read=biliPlayerXmlParser.loadXML()
    if read==-1 :
        xml=2
    else :
        xml=1
        xmlc=read
    if xml==1 :
        bs=True
        if not ns:
            bs=False
        read=JSONParser.getset(se,'dmgl')
        if read==True :
            bs=False
        elif read==False :
            bs=False
            xml=2
        if 'dm' in ip :
            if ip['dm']:
                bs=False
                xml=1
            else :
                bs=False
                xml=2
        while bs:
            yn=input("是否启用弹幕过滤(y/n)？")
            if yn[0].lower() =='y' :
                bs=False
            if yn[0].lower() =='n' :
                bs=False
                xml=2
    if lr: #直播回放
        r=requests.Session()
        r.headers=copydict(section.headers)
        r.proxies=section.proxies
        if nte:
            r.trust_env=False
        read=JSONParser.loadcookie(r)
        if read!=0 :
            print("读取cookies.json出现错误")
            return -1
        r.cookies.set('CURRENT_QUALITY','120',domain='.bilibili.com',path='/')
        r.cookies.set('CURRENT_FNVAL','16',domain='.bilibili.com',path='/')
        r.cookies.set('laboratory','1-1',domain='.bilibili.com',path='/')
        r.cookies.set('stardustvideo','1',domain='.bilibili.com',path='/')
        re=r.get('https://api.live.bilibili.com/xlive/web-room/v1/record/getInfoByLiveRecord?rid=%s'%(rid)) #直播回放信息
        re=re.json()
        if re['code']!=0 :
            print('%s %s'%(re['code'],re['message']))
            return -1
        ri=JSONParser.getlr1(re)
        re=r.get('https://api.live.bilibili.com/room/v1/Room/get_info?room_id=%s&from=room'%(ri['roomid'])) #直播房间信息
        re=re.json()
        if re['code']!=0 :
            print('%s %s'%(re['code'],re['message']))
            return -1
        JSONParser.getlr2(re,ri)
        re=r.get('https://api.bilibili.com/x/space/acc/info?mid=%s&jsonp=jsonp'%(ri['uid'])) #UP主信息
        re=re.json()
        if re['code']!=0 :
            print('%s %s'%(re['code'],re['message']))
            return -1
        JSONParser.getlr3(re,ri)
        if ns:
            PrintInfo.printlr(ri)
        bs=True
        f=True
        while bs:
            if f and 'd' in ip:
                inp=str(ip['d'])
                f=False
            elif ns:
                inp=input('请输入你要下载的方式：\n1.视频下载\n2.弹幕下载\n3.视频+弹幕下载')
            else :
                print('请使用-d <下载方式>选择下载方式')
                return -1
            if inp[0].isnumeric() and int(inp[0])>0 and int(inp[0])<4:
                cho=int(inp[0])
                bs=False
        if cho>1 :
            read=biliLiveDanmu.lrdownload(ri,section,ip,se,xml,xmlc)
            if read==-1 :
                return -1
        if cho==1 or cho==3 :
            bs=True
            cho3=False
            if not ns:
                bs=False
            read=JSONParser.getset(se,'mp')
            if read==True :
                bs=False
                cho3=True
            elif read==False :
                bs=False
            if 'm' in ip :
                if ip['m'] :
                    bs=False
                    cho3=True
                else :
                    bs=False
                    cho3=False
            while bs :
                inp=input('是否要默认下载最高画质（这样将不会询问具体画质）？(y/n)')
                if len(inp) > 0:
                    if inp[0].lower()=='y' :
                        cho3=True
                        bs=False
                    elif inp[0].lower()=='n' :
                        bs=False
            cho5=False
            bs=True
            if not ns:
                bs=False
            read=JSONParser.getset(se,'cd')
            if read==True :
                bs=False
                cho5=True
            elif read==False:
                bs=False
            if 'ac' in ip :
                if ip['ac'] :
                    bs=False
                    cho5=True
                else :
                    bs=False
                    cho5=False
            while bs:
                inp=input('是否开启继续下载功能？(y/n)')
                if len(inp)>0 :
                    if inp[0].lower()=='y' :
                        cho5=True
                        bs=False
                    elif inp[0].lower()=='n' :
                        bs=False
            read=videodownload.lrvideodownload(ri,section,cho3,cho5,se,ip)
            if read==-5 :
                return -1
        return 0
    re=section.get(s)
    parser=HTMLParser.Myparser()
    parser.feed(re.text)
    try :
        vd=json.loads(parser.videodata)
    except Exception:
        if av:
            re=search(r"av([0-9]+)",s,I).groups()[0]
            re=section.get("https://api.bilibili.com/x/web-interface/view/detail?bvid=&aid=%s&jsonp=jsonp"%(re))
            re.encoding='utf8'
            re=re.json()
            if re['code']!=0 :
                print('%s %s'%(re['code'],re['message']))
                return -1
            if 'data' in re and 'View' in re['data'] and 'redirect_url' in re['data']['View'] :
                ip2=copyip(ip)
                ip2['i']=re['data']['View']['redirect_url']
                if 'p' in ip :
                    ip2['p']=ip['p']
                read=main(ip2)
                if read!= 0 :
                    return read
                return 0
            print(traceback.format_exc())
            return -1
        elif ss:
            if re.status_code==404 :
                print('404了 找不到啦')
                return 0
            print(traceback.format_exc())
            return -1
        else :
            print(traceback.format_exc())
            return -1
    if 'error' in vd and 'code' in vd['error'] and 'message' in vd['error'] :
        print('%s %s'%(vd['error']['code'],vd['error']['message']))
        return -1
    if av :
        data=JSONParser.Myparser(parser.videodata)
        if data['videos']!=len(data['page']) :
            r=requests.Session()
            r.headers=copydict(section.headers)
            r.proxies=section.proxies
            if nte:
                r.trust_env=False
            read=JSONParser.loadcookie(r)
            if read!=0 :
                print("读取cookies.json出现错误")
                return -1
            r.headers.update({'referer':"https://www.bilibili.com/video/%s"%(data['bvid'])})
            r.cookies.set('CURRENT_QUALITY','120',domain='.bilibili.com',path='/')
            r.cookies.set('CURRENT_FNVAL','16',domain='.bilibili.com',path='/')
            r.cookies.set('laboratory','1-1',domain='.bilibili.com',path='/')
            r.cookies.set('stardustvideo','1',domain='.bilibili.com',path='/')
            re=r.get("https://api.bilibili.com/x/player.so?id=cid:%s&aid=%s&bvid=%s&buvid=%s"%(data['page'][0]['cid'],data['aid'],data['bvid'],r.cookies.get('buvid3')))
            re.encoding='utf8'
            rs=search(r"<interaction>(.+)</interaction>",re.text,I)
            if rs!=None :
                rs=rs.groups()[0]
                if rs!="" :
                    rs=json.loads(rs)
                    data['gv']=rs['graph_version']
                    hd=True
        if hd:
            read=getninfo(r,data)
            if read==-1 :
                return -1
        if ns:
            PrintInfo.printInfo(data)
        cho=[]
        if data['videos']==1 :
            cho.append(1)
        else :
            bs=True
            f=True
            while bs :
                if f and 'p' in ip :
                    f=False
                    inp=ip['p']
                elif ns:
                    inp=input('请输入你想下载弹幕/视频的视频编号，每两个编号间用,隔开，全部下载可输入a')
                else :
                    print('请使用-p <p数>选择视频编号')
                    return -1
                cho=[]
                if inp[0]=='a' :
                    if ns:
                        print('您全选了所有视频')
                    for i in range(1,data['videos']+1) :
                        cho.append(i)
                    bs=False
                else :
                    inp=inp.split(',')
                    bb=True
                    for i in inp :
                        if i.isnumeric() and int(i)>0 and int(i)<=data['videos'] and (not (int(i) in cho)) :
                            cho.append(int(i))
                        else :
                            bb=False
                    if bb :
                        bs=False
                        for i in cho :
                            if ns:
                                print("您选中了第"+str(i)+"P："+data['page'][i-1]['part'])
        cho2=0
        bs=True
        if 'd' in ip :
            bs=False
            cho2=ip['d']
        while bs :
            if not ns:
                print('请使用-d <下载方式>选择下载方式')
                return -1
            inp=input('请输入你要下载的方式：\n1.当前弹幕下载\n2.全弹幕下载\n3.视频下载\n4.当前弹幕+视频下载\n5.全弹幕+视频下载\n6.仅字幕下载')
            if inp[0].isnumeric() and int(inp[0])>0 and int(inp[0])<7 :
            	cho2=int(inp[0])
            	bs=False
        if cho2==1 or cho2==4 :
            for i in cho :
                read=biliDanmu.DanmuGetn(i,data,section,'av',xml,xmlc,ip,se)
                if read==-1 or read==-4 :
                    pass
                elif read==0 :
                    print('第'+str(i)+"P下载完成")
                else :
                    exit()
        if cho2==2 or cho2==5 :
            read=biliTime.equal(biliTime.getDate(data['pubdate']),biliTime.getNowDate())
            if read==0 or read==1 :
                print('不能下载该视频全弹幕！')
                exit()
            for i in cho :
                read=biliDanmu.DanmuGeta(i,data,section,'av',xml,xmlc,ip,se)
                if read==-2 :
                    pass
                elif read==0 :
                    print("第"+str(i)+"P下载完成")
                else :
                    exit()
        if cho2>2 and cho2<6:
            bs=True
            cho3=False
            if not ns:
                bs=False
            read=JSONParser.getset(se,'mp')
            if read==True :
                bs=False
                cho3=True
            elif read==False :
                bs=False
            if 'm' in ip :
                if ip['m'] :
                    bs=False
                    cho3=True
                else :
                    bs=False
                    cho3=False
            while bs :
                inp=input('是否要默认下载最高画质（这样将不会询问具体画质）？(y/n)')
                if len(inp) > 0:
                    if inp[0].lower()=='y' :
                        cho3=True
                        bs=False
                    elif inp[0].lower()=='n' :
                        bs=False
            cho5=False
            bs=True
            if not ns:
                bs=False
            read=JSONParser.getset(se,'cd')
            if read==True :
                bs=False
                cho5=True
            elif read==False:
                bs=False
            if 'ac' in ip :
                if ip['ac'] :
                    bs=False
                    cho5=True
                else :
                    bs=False
                    cho5=False
            while bs:
                inp=input('是否开启继续下载功能？(y/n)')
                if len(inp)>0 :
                    if inp[0].lower()=='y' :
                        cho5=True
                        bs=False
                    elif inp[0].lower()=='n' :
                        bs=False
            for i in cho :
                read=videodownload.avvideodownload(i,s,data,section,cho3,cho5,se,ip,ud)
                if read==-5 or read==-6 :
                    return -1
        if cho2==6:
            for i in cho:
                videodownload.avsubdownload(i,s,data,section,se,ip,ud)
    if ss or ep :
        if ep :
            epl='，仅下载输入的ep号可输入b'
        else :
            epl=''
        data=JSONParser.Myparser2(parser.videodata)
        le=PrintInfo.printInfo2(data,ns)
        rs=search(r'__PGC_USERSTATE__=([^<]+)',re.text)
        led=-1#上一次播放epid
        if rs!=None:
            rs=rs.groups()[0]
            pgc=json.loads(rs)
            if 'progress' in pgc and pgc['progress']!=None :
                if 'last_ep_id' in pgc['progress'] and pgc['progress']['last_ep_id']>-1:
                    led=pgc['progress']['last_ep_id']
        epr=""
        if led>-1 :
            epr='，下载上次观看的EP%s可输入l'%(led)
        cho=[]
        if le==1:
            cho.append(1)
            cho=chon.getcho(cho,data)
        else :
            bs=True
            f=True
            while bs :
                if f and 'p' in ip :
                    inp=ip['p']
                    f=False
                elif ns :
                    inp=input('请输入你想下载弹幕/视频的视频编号，每两个编号间用,隔开，全部下载可输入a%s%s'%(epl,epr))
                else :
                    print('请使用-p <p数>选择视频编号')
                    return -1
                cho=[]
                if len(inp)>0:
                    if inp[0]=='a' :
                        if ns:
                            print('你全选了所有视频')
                        for j in range(1,le+1) :
                            cho.append(j)
                        bs=False
                    elif ep and inp[0]=='b':
                        iii=1
                        co=True
                        if 'epList' in data:
                            for i in data['epList'] :
                                if i['loaded']:
                                    co=False
                                    break
                                iii=iii+1
                        if co and 'sections' in data :
                            for i in data['sections'] :
                                for j in i['epList'] :
                                    if j['loaded']:
                                        co=False
                                        break
                                    iii=iii+1
                        if not co:
                            cho.append(iii)
                            bs=False
                    elif led>-1 and inp[0]=='l':
                        iii=1
                        co=True
                        if 'epList' in data:
                            for i in data['epList'] :
                                if i['id']==led :
                                    co=False
                                    break
                                iii=iii+1
                        if co and 'sections' in data:
                            for i in data['sections'] :
                                for j in i['epList'] :
                                    if j['id']==led :
                                        co=False
                                        break
                                    iii=iii+1
                        if not co:
                            cho.append(iii)
                            bs=False
                    else :
                        inp=inp.split(',')
                        bb=True
                        for i in inp :
                            if i.isnumeric() and int(i)<=le and int(i)>0 and (not (int(i) in cho)) :
                                cho.append(int(i))
                            else :
                                bb=False
                        if bb:
                            bs=False
                cho=chon.getcho(cho,data)
                if ns:
                    PrintInfo.printcho(cho)
        cho2=0
        bs=True
        if 'd' in ip :
            bs=False
            cho2=ip['d']
        while bs :
            if not ns:
                print('请使用-d <下载方式>选择下载方式')
                return -1
            inp=input('请输入你要下载的方式：\n1.当前弹幕下载\n2.全弹幕下载\n3.视频下载\n4.当前弹幕+视频下载\n5.全弹幕+视频下载')
            if inp[0].isnumeric() and int(inp[0])>0 and int(inp[0])<6:
            	cho2=int(inp[0])
            	bs=False
        if cho2==1 or cho2==4 :
            for i in cho:
                read=biliDanmu.DanmuGetn(i,data,section,'ss',xml,xmlc,ip,se)
                if read==-1 or read==-4 :
                    pass
                elif read==0 :
                    print('%s下载完成' % (i['titleFormat']))
                else :
                    exit()
        if cho2==2 or cho2==5 :
            for i in cho :
                read=biliDanmu.DanmuGeta(i,data,section,'ss',xml,xmlc,ip,se)
                if read==0 :
                    print('%s下载完成' % (i['titleFormat']))
                else :
                    return -1
        if cho2>2 :
            bs=True
            cho3=False
            if not ns:
                bs=False
            read=JSONParser.getset(se,'mp')
            if read==True :
                bs=False
                cho3=True
            elif read==False :
                bs=False
            if 'm' in ip :
                if ip['m'] :
                    bs=False
                    cho3=True
                else :
                    bs=False
                    cho3=False
            while bs :
                inp=input('是否要默认下载最高画质（这样将不会询问具体画质）？(y/n)')
                if len(inp) > 0:
                    if inp[0].lower()=='y' :
                        cho3=True
                        bs=False
                    elif inp[0].lower()=='n' :
                        bs=False
            cho5=False
            bs=True
            if not ns:
                bs=False
            read=JSONParser.getset(se,'cd')
            if read==True :
                bs=False
                cho5=True
            elif read==False:
                bs=False
            if 'ac' in ip :
                if ip['ac'] :
                    bs=False
                    cho5=True
                else :
                    bs=False
                    cho5=False
            while bs:
                inp=input('是否开启继续下载功能？(y/n)')
                if len(inp)>0 :
                    if inp[0].lower()=='y' :
                        cho5=True
                        bs=False
                    elif inp[0].lower()=='n' :
                        bs=False
            for i in cho:
                read=videodownload.epvideodownload(i,"https://www.bilibili.com/bangumi/play/ss%s"%(data['mediaInfo']['ssId']),data,section,cho3,cho5,se,ip,ud)
                if read==-5 or read==-6 :
                    return -1
    return 0
if __name__=="__main__" :
    PrintInfo.pr()
    if len(sys.argv)==1 :
        main()
    else :
        main(gopt(sys.argv[1:]))
else :
    print("请运行根目录下的start.py")