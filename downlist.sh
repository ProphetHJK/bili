#!/bin/bash
# -d <method>   下载方式：1.当前弹幕 2.全弹幕 3.视频 4.当前弹幕+视频 5.全弹幕+视频 6.仅字幕 7.仅封面图片 8.仅 音频
# -p <number>    要下载的P数（两个P数可用,连接（例如：1-25），使用a全选，输入为ep号时可用b选择该ep号，下载上次观看的视频可输入l）
# -o <dir>    设置下载文件夹位置
# -n  不覆盖重复文件
# -r <boolean>    是否在下载失败后重新下载
# --yr    相当于-r true
# --nr    相当于-r false
# -i <input>   AV/SS/EP/MD/BV号或者链接（可以使用","来分隔多个输入）
# --vf <format>   从ffmpeg输出的视频格式。默认值：mkv, mp4
# -m <boolean>    是否默认下载最高画质
# --ym    相当于-m true
# --nm    相当于-m false
# --ad <boolean>  是否在合并完成后删除无用文件
# --yad   相当于--ad true
# --nad   相当于--ad false
# --ac <boolean>  是否开启继续下载功能
# --yac   相当于--ac true
# --nac   相当于--ac false
# --da <boolean>  当输入收藏夹/频道/投稿链接时是否自动下载每一个视频的所有分P
# --yda   相当于--da true
# --nda   相当于--da false
# --bp    合并完成后删除无用文件时保留封面图片
# --lan <LANGUAGECODE>

python3 start.py -n --nr --ym --yad --yac --yda --bp -d 3 -p "1-5" -o "Download/" --lan "zh_CN" --vf "mp4" -i "https://space.bilibili.com/123456789/favlist?fid=123456789"