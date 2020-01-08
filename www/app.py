import logging; logging.basicConfig(level=logging.INFO)

import asyncio, os, json, time
from datetime import datetime
from jinja2 import Environment,FileSystemLoader
from coroweb import add_routes, add_static

from aiohttp import web

def init_jinja2(app,**kw):
    logging.info('init jinja2...')
    options = dict(
        autoescape = kw.get('autoescape',True),
        block_start_string = kw.get('block_start_string','{%'),
        block_end_string = kw.get('block_end_string','%}'),
        variable_start_string = kw.get('variable_start_string','{{'),
        variable_end_string = kw.get('variable_end_string','}}'),
        auto_reload = kw.get('auto_reload',True)
        )
    path = kw.get('path',None)
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'templates')
    logging.info('set jinja2 template path:%s'%path)
    env = Environment(loader = FileSystemLoader(path),**options)
    filters = kw.get('filters',None)
    if filters is not None:
        for name,f in filters.items():
            env.filters['name'] = f
    app['__templating__'] = env

def datetime_filter(t):
    delta = int(time.time()-t)
    if delta < 60:
        return u'1分钟前'

    if delta < 3600:
        return u'%s分钟前'%(delta//60)

    if delta < 86400:
        return u'%s小时前'(delta//3600)

    if delta < 604800:
        return u'%天前'(delta//86400)

    dt = datetime.fromtimestamp(t)
    return u'%s年%s月%s日'%(dt.year, dt.month, dt.day)


async def logger_factory(app,handler):

    async def logger(request):
        logging.info('Request:%s %s'%(request.method,request.path))

        return (await handler(request))

    return logger

async def response_factory(app,handler):

    async def response(request):

        r = await handler(request)
        if isinstance(r,web.StreamResponse):
            return r
        if isinstance(r,bytes):
            resp = web.Response(body = r)
            resp.content_type = 'application/octet-stream'
            return resp
        if isinstance(r,str):
            resp = web.Response(body = r.encode('utf-8'))
            resp.content_type = 'text/html;charset = utf-8'
            return resp
        if isinstance(r,dict):
            pass

        if isinstance(r,int) and r >= 100 and r < 600:
            pass

        if isinstance(r,tuple) and len(r) == 2:
            pass

        #default:
        resp = web.Response(body = str(r).encode('utf-8'))
        resp.content_type = 'text/plain;charset=utf-8'
        return resp

    return response


def index(request):
    return web.Response(body=b'<h1>Awesome</h1>',content_type='text/html')


async def init(loop):
    app = web.Application(middlewares = [logger_factory,response_factory])
    
    init_jinja2(app,filters = dict(datatime = datetime_filter))
    add_routes(app,'handlers')
    add_static(app)

    app_runner = web.AppRunner(app)
    await app_runner.setup() 
    srv = await loop.create_server(app_runner.server, '127.0.0.1', 9000) 
    logging.info('server started at http://127.0.0.1:9000...') 
    return srv

loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
