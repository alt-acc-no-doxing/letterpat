from typing import Tuple, NoReturn, Any, Optional
from functools import wraps
import re


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


class Patterns:
    wchr: str = '_'
    SIDES: Tuple[str, ...] = ('left', 'right',)
    DEBUG: bool = True

    def __init__(self, str_: str, pattern_length: int = 29):
        self.str_ = str_
        self.strlen = len(self.str_)
        self.patlen = pattern_length
        self.wsz: int = (self.patlen - self.strlen) if (self.patlen - self.strlen) > 0 else 0
        self.curstr = f"{self.str_}{self.wsz*self.wchr}"
        self.lines = []
        self.NON_WS_REX = re.compile(rf'[^{self.wchr}]+')

    @debug
    def plain(self, nlines: int):
        self.lines += [f"{self.str_}{self.wsz * self.wchr}"] * nlines
        self.curstr = self.lines[-1]

    @debug
    def wave_right(self, wavesize: int):
        wavesize = wavesize if wavesize <= self.wsz else self.wsz
        first_part = [f'{i * self.wchr}{self.str_}{(self.wsz-i)*self.wchr}' for i in range(wavesize)]
        second_part = [f'{i * self.wchr}{self.str_}{(self.wsz - i) * self.wchr}' for i in reversed(range(wavesize))]
        self.lines.extend(first_part + second_part)
        self.curstr = self.lines[-1]

    @debug
    def eat(self, side: str = 'left'):
        self._validate_side(side)
        if side == 'left':
            self.lines +=  [f'{self.str_[i:]}{(self.wsz+i)*self.wchr}' for i in range(self.strlen)]
        elif side == 'right':
            self.lines +=  [f'{(self.wsz + i) * self.wchr}{self.str_[:self.strlen - i]}' for i in range(self.strlen)]
        self.curstr = self.lines[-1]

    @debug
    def spew(self, side: str = 'left'):
        self._validate_side(side)
        if side == 'left':
            self.lines += [f'{self.str_[-i:]}{(self.patlen-i) * self.wchr}' for i in range(1, self.strlen+1)]
        elif side == 'right':
            self.lines += [f'{(self.patlen-i) * self.wchr}{self.str_[:i]}' for i in range(1, self.strlen+1)]
        self.curstr = self.lines[-1]

    @debug
    def shift_by_letter(self, side: str = 'left'):
        self._validate_side(side)
        try:
            pos = self.NON_WS_REX.search(self.curstr).start() if side == 'left' else self.NON_WS_REX.search(self.curstr).end()
        except AttributeError:
            pos = 0 if side == 'right' else self.strlen-1

    @debug
    def eatspew(self, side: str = 'left'):
        self.eat(side=side)
        self.spew(side=side)
        self.curstr = self.lines[-1]

    def _validate_side(self, side: str) -> NoReturn:
        if side not in self.SIDES:
            raise ValueError(f"Invalid side specification: {side}. Valid side specifications: {', '.join(self.SIDES)}.")

    def run_patterns(self):
        self.plain(10)
        self.wave_right(10)
        self.eat()
        self.spew()
        self.plain(10)
        self.shift_by_letter()
        self.print_lines()

    def print_lines(self):
        for line in self.lines:
            print(line)


if __name__ == '__main__':

    printer = Patterns("i'm bored", pattern_length=29)
    printer.run_patterns()