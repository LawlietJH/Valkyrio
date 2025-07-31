import functools

class Cache:
    def __init__(self, name: str = 'Main', verb: bool = True):
        self._name = name
        self._verb = verb
        self.cache_data = {}

    @staticmethod
    def _is_self(obj, func):
        class_name = func.__qualname__.split('.')[0]
        method = func.__qualname__.split('.')[-1]
        return class_name in str(obj.__class__) and method in dir(obj)

    def _get_key(self, func, args, kwargs):
        if args and self._is_self(args[0], func):
            args = f'(self,{str(args[1:])[1:]}'
        return f'{__name__}.{func.__qualname__}({args},{kwargs})'

    def _is_no_cache(self, kwargs):
        no_cache = kwargs.get('no_cache')
        if no_cache != None:
            del kwargs['no_cache']
        return no_cache

    @property
    def cache(self):
        def inner(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if self._is_no_cache(kwargs):
                    return func(*args, **kwargs)
                key = self._get_key(func, args, kwargs)
                if key in self.cache_data:
                    return self.cache_data[key]
                results = func(*args, **kwargs)
                self.cache_data[key] = results
                if self._verb:
                    print(f'<{self._name}> Cache ID: {key} - inserted={self.quantity}')
                return results
            return wrapper
        return inner

    @property
    def quantity(self):
        return len(self.cache_data)
