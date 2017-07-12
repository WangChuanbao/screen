# -*- coding: UTF-8 -*-
# author: star
# created_at: 17-6-29 10:26
import json
import MySQLdb
import settings
import time
from django.core.cache import cache

class ZabbixApi(object):

    url = 'http://10.10.10.11/htrd/api_jsonrpc.php'
    header = {'content-type': 'application/json'}
    auth = None
    auth_token = None
    auth_name = 'Admin'
    auth_password = 'zabbix'

    def __init__(self):
        if cache.has_key("auth_token"): 
            self.auth_token = cache.get("auth_token")
            print('------' + self.auth_token)
        else: 
            self.auth = self.get_login({
                    "user": self.auth_name,
                    "password": self.auth_password
                })
            self.auth_token = json.loads(self.auth)['result']
            print('=======' + self.auth_token)
            cache.add("auth_token", self.auth_token)

    def get_login(self, params):
        return self.__get_data("user.login", params)

    def get_item(self, params):
        return self.__get_data("item.get", params)

    def get_history(self, params):
        params["sortfield"] = "clock"
        params["sortorder"] = "DESC"
        # params['limit'] = 10
        print(params)
        return self.__get_data("history.get", params)

    def get_group(self):
        params = {
            "output": "extend",
            "selectTemplates": "count",
            "real_hosts": 1, 
            "selectHosts": ['hostid']
        }
        return self.__get_data("hostgroup.get", params)

    def get_interface(self, params):
        args = {
            'output': ['ip', 'hostid'],
            'filter': params
        }
        return self.__get_data('hostinterface.get', args)

    def get_host(self, params):
        params['output'] = ["name"]
        params['selectInterfaces'] = ["ip"]
        params['selectGroups'] = ['groupid']
        # params = {
        #     'output': 'name',
        #     'selectInterfaces': 'ip',
        #     'selectGroups': 'groupid'
        # }
        return self.__get_data("host.get", params)

    def get_warning(self, params):
        params['filter'] = {"value": 1}
        params['withUnacknowledgedEvents'] = 1
        params['selectHosts'] = ['name']
        # params = {
        #     'filter': {
        #         'value': 1
        #     },
        #     'withUnacknowledgedEvents': 1,
        #     'selectHosts': ['name']
        # }
        return self.__get_data("trigger.get", params)

    def get_event(self, params):
        params['filter'] = {'acknowledged': 0, 'value': 1}
        return self.__get_data('event.get', params)

    def acknowledge_event(self, params):
        params['message'] = 'Problem acknowledge'
        return self.__get_data('event.acknowledge', params)

    def get_screen(self, params):
        params['selectScreenItems'] = [
            'screenitemid',
            'resourcetype',
            'resourceid'
        ]
        # params = {
        #     'selectScreenItems': [
        #         "screenitemid",
        #         "resourcetype",
        #         "resourceid"
        #     ],
        #     # 'output': 'extend'
        # }
        return self.__get_data("screen.get", params)

    def get_graph(self, params):
        params['selectGraphItems'] = ["gitemid", "itemid", "color"]
        params['selectItems'] = ['name', 'key_', 'value_type', 'units']
        params['output'] = ["name", "graphtype"]
        return self.__get_data("graph.get", params)

    def __get_data(self, method, params):
        from requests import post, RequestException
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "auth": self.auth_token,
            "id": 1
        })
        try:
            r = post(self.url, data=data, headers=self.header)
            r.raise_for_status()
        except RequestException as e:
            return e
        else:
            return r.text

    def select_mysql(self, flag, itemid, time_from, time_till, item_type):
        if int(flag) == 1:
            host = settings.HISTORY_MYSQL.get('HOST')
            passwd = settings.HISTORY_MYSQL.get('PASSWD')
            user = settings.HISTORY_MYSQL.get('USER')
            db = settings.HISTORY_MYSQL.get('DB')
            port = settings.HISTORY_MYSQL.get('PORT')
            limit = settings.HISTORY_MYSQL.get('LIMIT')
        else:
            host = settings.SERVER_MYSQL.get('HOST')
            passwd = settings.SERVER_MYSQL.get('PASSWD')
            user = settings.SERVER_MYSQL.get('USER')
            db = settings.SERVER_MYSQL.get('DB')
            port = settings.SERVER_MYSQL.get('PORT')
            limit = settings.SERVER_MYSQL.get('LIMIT')

        conn = MySQLdb.connect(host=host, user=user, passwd=passwd, db=db, port=int(port))
        cur = conn.cursor(cursorclass=MySQLdb.cursors.DictCursor)

        if int(item_type) == 0:
            table = 'history'
        elif int(item_type) == 2:
            table = 'history_long'
        elif int(item_type) == 3:
            table = 'history_uint'
        sql_cout = 'select count(*) from ' + table + ' where itemid=' + str(itemid)
        sql = 'select itemid, ns, value, clock from (select ' + table + '.*, (@i:=@i+1) as i from (select (@i:=-1)) b,' + table + ' where itemid=' + str(itemid)
        if time_from != 0:
            sql = sql + ' and clock>' + str(time_from)
            sql_cout = sql_cout + ' and clock>' + str(time_from)
        if time_till != 0:
            sql = sql + ' and clock<' + str(time_till)
            sql_cout = sql_cout + ' and clock<' + str(time_till)

        cur.execute(sql_cout)
        count = (cur.fetchone()['count(*)'])
        mod = 1 if count < limit else count / limit

        sql = sql + ' order by clock desc) as t where t.i MOD ' + str(mod) + '=0;'
        cur.execute(sql)
        result = cur.fetchall()
        conn.close()
        print result
        return result

    def get_graph_history(self, params):
        itemids = params['itemids']
        item_type = params['history']
        time_from = 0
        time_till = 0
        local_time = long(time.time())
        response = ()

        if params.has_key('time_from'):
            time_from = long(params['time_from'])
            time_till = long(params['time_till'])
            if time_from > local_time - 2 * 60 * 60:
                for itemid in itemids:
                    response = response + self.select_mysql(0, itemid, time_from, time_till, item_type)
                return response
            if time_till < local_time -2*60*60:
                for itemid in itemids:
                    response = response + self.select_mysql(1, itemid, time_from, time_till, item_type)
                return response

        for itemid in itemids:
            response = response + self.select_mysql(0, itemid, time_from, time_till, item_type)
            response = response + self.select_mysql(1, itemid, time_from, time_till, item_type)

        return response
