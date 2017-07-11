# -*- coding: UTF-8 -*-
# author: star
# created_at: 17-6-29 11:30
from channels.channel import Group
from core.zabbix_api import ZabbixApi
import django.dispatch
import json
import hashlib

args = []

pizza_done = django.dispatch.Signal(providing_args=["toppings", "size"])


def callback(sender, **kwargs):
    toppings = kwargs['toppings']
    data = json.loads(toppings)['data']
    if not args:
        return
    for path in args:
        s = hashlib.md5()
        s.update(path)
        group = s.hexdigest()

        path_list = path.split('-')
        pre_type = path_list[0]
        arg = path_list[1]
        argList = arg.split(',')
        
        if pre_type == "item":
            filterItemData(group, argList, data)
        if pre_type == "chart":
            filterChartData(group, argList, data)


pizza_done.connect(callback)


def filterItemData(group, item_ids, data):
    for item in data:
        item_id = item['itemid']
        if str(item_id) in item_ids:
            Group(group).send({'text': json.dumps(item)})


def filterChartData(group, graph_ids, data):
    zbx_api = ZabbixApi()
    return_value = zbx_api.get_graph({'graphids': graph_ids})
    r = json.loads(return_value)
    result = r['result']
    for g in result:
        g_items = g['gitems']
        for i in g_items:
            item_id = i['itemid']
            i.pop('itemid')
            i['item'] = []
            for item in data:
                if int(item_id) == item['itemid']:
                    i['item'] = [item]
                    Group(group).send({'text': json.dumps(r)})


def ws_connect(message):
    message.reply_channel.send({'accept':True})
    global args
    path = str(message.content['path'].strip("/"))
    s = hashlib.md5()
    s.update(path)
    group = s.hexdigest()
    args.append(path)
    Group(group).add(message.reply_channel)


def ws_receive(message):
    pass


def ws_disconnect(message):
    path = message.content['path'].strip("/")
    s = hashlib.md5()
    s.update(path)
    group = s.hexdigest()
    args.remove(path)
    Group(group).discard(message.reply_channel)

