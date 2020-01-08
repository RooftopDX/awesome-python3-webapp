import asyncio, os, inspect, logging, functools

# inspect.Parameter.POSITIONAL_OR_KEYWORD j=1
# inspect.Parameter.KEYWORD_ONLY b
# inspect.Parameter.VAR_POSITIONAL  *c
# inspect.Parameter.VAR_KEYWORD **f


async def handle_url_xxx(request):
    url_param = request.match_info['key']
    query_params = parse_qs(request.query_string)


    text = render('template',data)
    return web.Response(text.encode('utf-8'))

def get_required_kw_args(fn):
    args = []
    # inspect.signature(fn)将返回一个inspect.Signature类型的对象，值为fn这个函数的所有参数
    # inspect.Signature对象的paramerters属性是一个mappingproxy（映射）类型的对象，值为一个有序字典

    params = inspect.signature(fn).parameters
    for name,param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
            args.append(name)
        return tuple(args)

def get_named_kw_args(fn):
    args = []
    params = inspect.signature(fn).parameters
    for name,param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            args.append(name)
        return tuple(args)

def has_named_kw_args(fn):
    params = inspect.signature(fn).parameters
    for name,param in params.items():
        if param.kind == inspect.Parameter.KEYWORD_ONLY:
            return True

def has_var_kw_arg(fn):
    params = inspect.signature(fn).parameters
    for name,param in params:
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True

def has_request_arg(fn):
    sig = inspect.signature(fn)
    params = sig.parameters
    found = False
    for name,param in params.items():
        if name =='request':
            found = True
            contunue
        if found and (param.kind != inspect.Parameter.VAR_POSITIONAL and param.kind != inspect.Parameter.KEYWORD_ONLY and param.kind != inspect.Parameter.VAR_KEYWORD):
            raise ValueError('request parameter must be the last named parameter in function:%s%s'%(fn.__name__,str(sig)))
    return found


class RequestHandler(object):
    def __init__(self,app,fn):
        self._app = app
        self._func = fn
        self._has_request_arg = has_request_arg(fn)
        self._has_var_kw_arg = has_var_kw_arg(fn)
        self._has_named_kw_args = has_named_kw_args(fn)
        self._named_kw_args = get_named_kw_args(fn)
        self._required_kw_args = get_required_kw_args(fn)

    async def __call__(self,request):
        kw = None
        await self.__func(**kw)
        return r

def add_static(app):
    # os.path.join连接两个或更多的路径名组件
    # os.path.dirname去掉文件名，返回目录 

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'static')
    app.router.add_static('/static/',path)
    logging.info('add static %s => %s'%('/static/',path))

def add_route(app,fn):
    method = getattr(fn,'__method__',None)
    path = getattr(fn,'__route__',None)

    if path is None or method is None:
        raise ValueError('@get or @post not defined in %s.'%str(fn))

    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
        fn = asynicio.coroutine(fn)
    logging.info('add route %s %s => %s(%s)'%(method,path,fn.__name__,','.join(inspect.signature(fn).parameters.key())))
    
    # app.router.add_route('GET', '/', index)
    app.router.add_route(method,path,RequestHandler(app,fn))

def add_routes(app,module_name):
    #rfind() 返回字符串最后一次出现的位置(从右向左查询)

    n = module_name.rfind('.')
    if n == (-1):
        # import导入Python模块的时候，默认调用的是__import__()函数,一般用于动态加载模块

        mod = __import__(module_name,globals(),locals())
    else:
        name = module_name[n+1:]
        mod = getattr(__import__(module_name[:n],globals(),locals(),[name]),name)

    for attr in dir(mod):
        # startswith() 方法用于检查字符串是否是以指定子字符串开头
        if attr.startswith('_'):
            continue
        fn = getattr(mod,attr)

        # callable() 函数用于检查一个对象是否是可调用的
        if callable(fn):
            method = getattr(fn,'__methond__',None)
            path = getattr(fn,'__route__',None)
            if method and path:
                add_route(app,fn)

