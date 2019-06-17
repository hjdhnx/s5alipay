from django.shortcuts import render, redirect, HttpResponse
from utils.pay import AliPay
import json
import time
from datetime import datetime

def get_ali_object():
    # 沙箱环境地址：https://openhome.alipay.com/platform/appDaily.htm?tab=info
    app_id = "2016092800616977"  #  APPID （沙箱应用）

    # 支付完成后，支付偷偷向这里地址发送一个post请求，识别公网IP,如果是 192.168.20.13局域网IP ,支付宝找不到，def page2() 接收不到这个请求
    # notify_url = "http://47.94.172.250:8804/page2/"
    notify_url = "http://127.0.0.1:8000/page2/"
    # notify_url = "http://127.0.0.1:8804/page2/"

    # 支付完成后，跳转的地址。
    return_url = "http://127.0.0.1:8000/page2/"

    merchant_private_key_path = "keys/app_private_2048.txt" # 应用私钥
    alipay_public_key_path = "keys/alipay_public_2048.txt"  # 支付宝公钥

    alipay = AliPay(
        appid=app_id,
        app_notify_url=notify_url,
        return_url=return_url,
        app_private_key_path=merchant_private_key_path,
        alipay_public_key_path=alipay_public_key_path,  # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥
        debug=True,  # 默认False,
    )
    return alipay

def index(request):
    return render(request,'index.html')
def home(request):
    return HttpResponse("<h >这是达神改进的一个主页面</h><br><hr><br><div style='color:white;background:pink;width:400px'><span>如果在使用过程中有什么不懂的地方\
    欢迎联系达神</span><br><span>QQ:434857005</span></div><br>接下来，你可以<a href='/index/'>点击测试支付</a>")
def page1(request):
    # 根据当前用户的配置，生成URL，并跳转。
    goods_dir = {"拿铁":1.00,"咖啡":2.00,"奶茶":3.00}
    # money = float(request.POST.get('money'))
    goods = request.POST.get('choose goods')
    print(goods)
    if goods!="":
        money = goods_dir[goods]
        alipay = get_ali_object()
        subject = "达神的商品: 一杯%s"%goods
        out_trade_no = "x2" + str(time.time())
        global payinfo
        payinfo = {"金额": money, "商品": subject,"订单号": out_trade_no,"商品名":goods}
        # 生成支付的url
        query_params = alipay.direct_pay(
            subject=subject,# 商品简单描述
            out_trade_no=out_trade_no,# 用户购买的商品订单号（每次不一样） 20180301073422891
            total_amount=money,# 交易金额(单位: 元 保留俩位小数)
        )
        pay_url = "https://openapi.alipaydev.com/gateway.do?{0}".format(query_params)  # 支付宝网关地址（沙箱应用）
        return redirect(pay_url)

def page1_1(request):
    # 根据当前用户的配置，生成URL，并跳转。
    money = float(request.POST.get('money'))
    alipay = get_ali_object()

    # 生成支付的url
    query_params = alipay.direct_pay(
        subject="达神互联的自定义商品",  # 商品简单描述
        out_trade_no="x2" + str(time.time()),  # 用户购买的商品订单号（每次不一样） 20180301073422891
        total_amount=money,  # 交易金额(单位: 元 保留俩位小数)
    )

    pay_url = "https://openapi.alipaydev.com/gateway.do?{0}".format(query_params)  # 支付宝网关地址（沙箱应用）

    return redirect(pay_url)

def page2(request):
    alipay = get_ali_object()
    if request.method == "POST":
        # 检测是否支付成功
        # 去请求体中获取所有返回的数据：状态/订单号
        from urllib.parse import parse_qs
        # name&age=123....
        body_str = request.body.decode('utf-8')
        post_data = parse_qs(body_str)

        post_dict = {}
        for k, v in post_data.items():
            post_dict[k] = v[0]

        # post_dict有10key： 9 ，1
        sign = post_dict.pop('sign', None)
        status = alipay.verify(post_dict, sign)
        print('------------------开始------------------')
        print('POST验证', status)
        print(post_dict)
        out_trade_no = post_dict['out_trade_no']

        # 修改订单状态
        # models.Order.objects.filter(trade_no=out_trade_no).update(status=2)
        print('------------------结束------------------')
        # 修改订单状态：获取订单号
        return HttpResponse('POST返回')

    else:
        params = request.GET.dict()
        sign = params.pop('sign', None)
        status = alipay.verify(params, sign)
        print('==================开始==================')
        print('GET验证', status)
        print('==================结束==================')
        # return HttpResponse('支付成功')
        seller = "达神互联科技有限公司"
        payway = "支付宝"
        i = datetime.now()
        trade_time = "{}年{}月{}日{}时{}分{}秒".format(i.year, i.month, i.day, i.hour, i.minute, i.second)
        print(trade_time)
        global payinfo
        html = "支付成功!付款信息如下:<br>\
        <table border='1'>\
        <tr><td>商品名</td> <td>{}</td></tr>\
        <tr><td>商品详情</td> <td>{}</td></tr>\
        <tr><td>订单号</td> <td>{}</td></tr>\
        <tr><td>付款金额</td> <td>{}</td></tr>\
        <tr><td>收款方</td> <td>{}</td></tr>\
        <tr><td>交易时间</td> <td>{}</td></tr>\
        <tr><td>付款方式</td> <td>{}</td></tr>\
        </table>".format(payinfo["商品名"],payinfo["商品"],payinfo["订单号"],payinfo["金额"],seller,trade_time,payway)
        return HttpResponse(html)


