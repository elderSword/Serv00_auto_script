# Serv00 - 自动续期脚本，Fork自bg8ixz/bg8ixz/Serv00_auto_script
# Fork该项目主要对TG的消息发送做了修改，原来脚本没成功

# TG消息 [步骤参考](https://blog.mado.us.kg/post/Serv00-jian-kong-bao-huo-%EF%BC%8C-fa-song-tong-zhi-dao-telegram.html)

青龙面板，serv00保活并发消息到TG。需要复制上面两个文件到青龙脚本根目录。
**需要注意：.sh 脚本文件中的信息需要填写你的**

然后设置定时任务
./Serv00-Renew.sh

cron : 0 */15 * * * ?   这个是每15min检测
