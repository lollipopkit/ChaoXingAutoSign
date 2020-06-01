# ChaoXingAutoSign
超星学习通**自动登录、签到**

## 20.6.1
新增`objectId`，自定义图片签到时使用的图片ID，此ID项可通过抓包获取，非必须修改

去除`debug`参数，需要调试请通过修改上课时间实现


## 20.5.22
新增`listen_time`参数，可设置每次监听时长

`except JSONDeoderError`，强化cookie失效策略


## 20.5.17
周末自动暂停运行脚本，有需求请修改`start_day`参数


## 20.5.16
优化，支持多种签到方式


## 20.5.12
优化监听机制，减少占用、流量


## 20.5.4
自动获取新cookie，防止cookie失效

修复了API错误的问题


## 声明
thanks to author 7z


@LollipopKit MIT license
