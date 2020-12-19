from functools import wraps
from typing import Optional, Any


def debug(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs) -> Optional[Any]:
        try:
            if self.DEBUG:
                self.lines.append(f"""## PATTERN {func.__name__} START (args = {', '.join(str(x) for x in args)})""")
                func(self, *args, **kwargs)
                self.lines.append(f"""## PATTERN {func.__name__} END""")
        except AttributeError:
            return func(self, *args, **kwargs)
    return wrapper