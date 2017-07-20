# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse

from core.zabbix_api import ZabbixApi
import json


# Create your views here.
from screen.models import Follow


def render(data):
    return HttpResponse('callback(' + data + ')')


def group(request):
    zbx_api = ZabbixApi()
    return render(zbx_api.get_group())


def interface(request):
    params = request.GET.dict()
    zbx_api = ZabbixApi()
    return render(zbx_api.get_interface(params))


def host(request):
    params = request.GET.dict()
    zbx_api = ZabbixApi()
    return render(zbx_api.get_host(params))


def warning(request):
    params = request.GET.dict()
    zbx_api = ZabbixApi()
    return render(zbx_api.get_warning(params))


def acknowledge(request):
    params = request.GET.dict()
    zbx_api = ZabbixApi()
    result = zbx_api.get_event(params)
    ack_params = {'eventids': [(event['eventid']) for event in json.loads(result)['result']]}
    return render(zbx_api.acknowledge_event(ack_params))


def item(request):
    params = request.GET.dict()
    zbx_api = ZabbixApi()
    return render(zbx_api.get_item(params))


def history(request):
    params = request.GET.dict()
    params['itemids'] = request.GET.get('itemids').split(',')
    zbx_api = ZabbixApi()
    return render(zbx_api.get_history(params))


def screen(request):
    params = request.GET.dict()
    zbx_api = ZabbixApi()
    return render(zbx_api.get_screen(params))


def graph(request):
    zbx_api = ZabbixApi()
    para = request.GET.dict()
    if para.has_key('graphids'):
        para['graphids'] = request.GET.get('graphids').split(',')
    item_para = {}
    if para.has_key('time_from'):
        item_para['time_from'] = para['time_from']
        para.pop('time_from')
    if para.has_key('time_till'):
        item_para['time_till'] = para['time_till']
        para.pop('time_till')
    return_value = zbx_api.get_graph(para)
    if not para.has_key('graphids'):
        return render(return_value)

    return_value = json.loads(return_value)
    for g in return_value['result']:
        item_att = {}
        his_items = []
        for g_item in g['gitems']:
            for h_item in g['items']:
                if int(g_item['itemid']) == int(h_item['itemid']):
                    name = h_item['name']
                    key_ = h_item['key_']
                    if '$' in name:
                        index_from = key_.index('[')
                        index_till = key_.index(']')
                        k = key_[index_from+1:index_till]
                        k_args = k.split(',')
                        for i in range(0,len(k_args)):
                            mark = '$'+str(i+1)
                            if mark in name:
                                name = name.replace(mark, k_args[i])
                    g_item['name'] = name
                    g_item['key'] = key_
                    g_item['units'] = h_item['units']
                    g_item['items'] = []
                    if h_item['value_type'] not in item_att:
                        item_att[h_item['value_type']] = [h_item['itemid']]
                    else:
                        values = item_att[h_item['value_type']]
                        values.append(h_item['itemid'])
                        item_att[h_item['value_type']] = values

        for value_type in item_att.keys():
            item_para['history'] = value_type
            item_para['itemids'] = item_att[value_type]
            #his_items = json.loads(zbx_api.get_history(item_para))['result']
            his_items = zbx_api.get_graph_history(item_para)

        i = 0
        indexs = []
        for g_item in g['gitems']:
            for his_item in his_items:
                if int(his_item['itemid']) == int(g_item['itemid']):
                    items = g_item['items']
                    items.append(his_item)
                    g_item['items'] = items
            if g_item['items'] == []:          
                indexs.append(i)
            i += 1

        indexs.sort(reverse=True)
        for index in indexs: 
            g['gitems'].pop(index)

        g.pop('items')
    return render(json.dumps(return_value))


def follow_list(request):
    follow_data = Follow.objects.all()
    if follow_data:
        return render(json.dumps([(f.toDICT()) for f in follow_data]))
    return render("{}")


def follow_create(request):
    follows = request.GET.get('follows')
    if follows:
        for f in json.loads(follows):
            follow = Follow()
            follow.host_id = f['host_id']
            follow.host_name = f['host_name']
            follow.item_id = f['item_id']
            follow.item_name = f['item_name']
            follow.save()
    return render(json.dumps({'result': True}))


def follow_delete(request):
    pk = request.GET.get('id')
    if pk:
        ids = pk.split(',')
        Follow.objects.filter(id__in=ids).delete()
        return render(json.dumps({'result': True}))
    return render(json.dumps({'result': False}))
