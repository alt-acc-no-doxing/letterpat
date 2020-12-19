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
    def wave(self, wavesize: int, side: str):
        wavesize = wavesize if wavesize <= self.wsz else self.wsz
        if side == 'right':
            self.lines.extend([f'{i * self.wchr}{self.str_}{(self.wsz-i)*self.wchr}' for i in range(wavesize)])
        elif side == 'left':
            self.lines.extend([f'{i * self.wchr}{self.str_}{(self.wsz - i) * self.wchr}' for i in reversed(range(wavesize))])
        self.curstr = self.lines[-1]

    def wave_returning(self, wavesize: int, direction: str):
        if direction == 'right':
            self.wave(wavesize, 'right')
            self.wave(wavesize, 'left')
        elif direction == 'left':
            self.wave(wavesize, 'left')
            self.wave(wavesize, 'right')

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
        spos, endpos = self.NON_WS_REX.search(self.curstr).start(), self.NON_WS_REX.search(self.curstr).end()
        # try:
        #     pos = .start() if side == 'left' else self.NON_WS_REX.search(self.curstr).end()
        # except AttributeError:
        #     pos = 0 if side == 'right' else self.strlen-1
        shiftlines = []
        curstr_lst = list(self.curstr)

        for i in range(endpos, spos, -1):
            charpos = spos+i
            curchr = self.curstr[charpos]
            while charpos > 1+endpos-i:
                curstr_lst[charpos] = self.wchr
                curstr_lst[charpos-1] = curchr
                shiftlines.append(''.join(curstr_lst))
                charpos-=1
        self.lines += shiftlines

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
        self.wave_returning(10, direction='right')
        self.eat()
        self.spew()
        self.plain(10)
        self.wave(10, side='right')
        self.shift_by_letter()

        self.print_lines()

    def print_lines(self):
        for line in self.lines:
            print(line)


if __name__ == '__main__':

    printer = Patterns("i'm bored", pattern_length=29)
    printer.run_patterns()