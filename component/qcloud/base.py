# -*- coding: utf-8 -*-
import json
import logging

from .exceptions import ComponentAPIException


logger = logging.getLogger('component')


class ComponentAPI(object):
    """Single API for Component"""

    HTTP_STATUS_OK = 200

    def __init__(self, client, method, path=None, description='', default_return_value=None):
        from . import conf
        host = conf.COMPONENT_SYSTEM_HOST
        # Do not use join, use "+" because path may starts with '/'
        # path都是以斜杠开头，为了避免斜杠重复，去掉host右侧的斜杠
        self.url = host.rstrip('/') + path
        self.client = client
        self.method = method
        self.default_return_value = default_return_value

    def __call__(self, *args, **kwargs):
        try:
            return self._call(*args, **kwargs)
        except ComponentAPIException, e:
            # Combine log message
            log_message = [e.error_message, ]
            log_message.append('url=%(url)s' % {'url': e.api_obj.url})
            if e.resp:
                log_message.append('content: %s' % e.resp.text)

            logger.exception('\n'.join(log_message))

            # Try return error message from remote service
            if e.resp is not None:
                try:
                    return e.resp.json()
                except:
                    pass
            return {'result': False, 'message': e.error_message, 'data': None}

    def _call(self, *args, **kwargs):
        params, data = {}, {}
        if args and isinstance(args[0], dict):
            params = args[0]
        params.update(kwargs)

        # Validate params for POST request
        if self.method == 'POST':
            data = params
            params = None
            try:
                json.dumps(data)
            except Exception:
                raise ComponentAPIException(self, u"请求参数错误（请传入一个字典或者json字符串）")

        # Request remote server
        try:
            resp = self.client.request(self.method, self.url, params=params, data=data)
        except Exception, e:
            logger.exception('Error occurred when requesting method=%s url=%s',
                             self.method, self.url)
            raise ComponentAPIException(self, u"组件调用出错, Exception: %s" % str(e))

        # Parse result
        if resp.status_code != self.HTTP_STATUS_OK:
            message = u"请求出现错误,错误状态：%s" % resp.status_code
            raise ComponentAPIException(self, message, resp=resp)
        try:
            # Parse response
            json_resp = resp.json()

            # 根据用户需求，用户想要得到request_id
            # request_id = json_resp.pop('request_id', None)
            if not json_resp['result']:
                # 组件返回错误时，记录相应的 request_id
                log_message = (u"组件返回错误信息: %(message)s, request_id=%(request_id)s "
                               u"url=%(url)s params=%(params)s data=%(data)s") % {
                    'request_id': json_resp.get('request_id'),
                    'message': json_resp['message'],
                    'url': self.url,
                    'params': params,
                    'data': data
                }
                logger.error(log_message)

            # Return default return value
            if not json_resp and self.default_return_value is not None:
                return self.default_return_value
            return json_resp
        except:
            raise ComponentAPIException(self, u"返回数据格式不正确，统一为json.", resp=resp)
