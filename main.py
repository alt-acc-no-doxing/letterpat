# Author abiogenejesus in response to 60k_Risk

from typing import Tuple, NoReturn, Optional
import re
from decorators import debug


class StringPatternPrinter:
    wchr: str = ' '
    SIDES: Tuple[str, ...] = ('left', 'right',)
    DEBUG: bool = True
    REX: Optional[re.Pattern] = None

    #!TODO Some patterns still missing
    #!TODO More elegant and consistent approach to some of the methods.
    #!TODO Docstrings

    def __init__(self, content_string: str, pattern_length: int = 29):
        """No docs yet"""
        self.initial_content = content_string
        self.initial_content_len = len(self.initial_content)
        self.init_wchr_idx = [i for i, _ in enumerate(self.initial_content) if i == self.wchr]

        self.entire_len = pattern_length if self.initial_content_len < pattern_length else self.initial_content_len+20

        self.init_wsz: int = \
            (self.entire_len - self.initial_content_len) if (self.entire_len - self.initial_content_len) > 0 else 0
        self.whitespace_len: int = self.init_wsz

        self.str_ = f"{self.initial_content}"
        self.str_len = len(self.str_)

        self.entire_string = f"{self.initial_content}{self.init_wsz * self.wchr}"

        self.lines = []

        # Regex for firstpart, current string, and trailing part.
        self.REX = re.compile(rf'^(?P<pre>(?:{self.wchr}?)+)(?P<curstr>.+?)(?P<post>(?:{self.wchr}+)?$)')

    def update(self):
        """Updates current string, lengths, etc."""
        self.entire_string = self.lines[-1]
        self.str_ = self.REX.search(self.entire_string)['curstr']
        self.str_len = len(self.str_)
        self.whitespace_len = len(self.entire_string) - len(self.str_)

    def duplicate(self, mode: str = 'fill'):
        """
        Duplicates current string in the direction with the most room character by character until the maximum
        size is reached.

        :param mode: string, default = 'fill' (currently no other modes are implemented)
        """
        found = self.REX.search(self.entire_string)
        spos, endpos = found.regs[2]
        direction = 'right' if len(found['pre']) <= len(found['post']) else 'left'

        if direction == 'right':
            condition = 'endpos + totalcnt < self.entire_len'
            strcopy = f"{self.wchr}{found['curstr']}"
        elif direction == 'left':
            strcopy = f"{self.wchr}{found['curstr'][::-1]}{self.wchr}"
            condition = "len(found['pre']) > 1"
        else:
            raise ValueError(f"Invalid direction {direction}")
        if mode == 'fill':
            cnt = 0
            totalcnt = cnt
            while eval(condition):
                found = self.REX.search(self.entire_string)
                if direction == 'right':
                    self.lines.append(f"{found['pre']}{found['curstr']}{strcopy[cnt]}{found['post'][:-1]}")
                elif direction == 'left':
                    addition = f"{strcopy[cnt]}{found['curstr']}{found['post']}"
                    self.lines.append(f"{(self.entire_len - len(addition)) * self.wchr}{addition}")
                self.update()
                if cnt >= len(strcopy) - 1:
                    cnt = 0
                totalcnt += 1
                cnt += 1

    def plain(self, nlines: int):
        self.lines += [f"{self.str_}{self.whitespace_len * self.wchr}"] * nlines
        self.update()

    def wave(self, side: str, wavesize: Optional[int] = None):
        spos, endpos = self.REX.search(self.entire_string).regs[2]


        if side == 'right':
            wavesize = wavesize or self.entire_len-endpos
            wavesize = wavesize if wavesize <= self.entire_len-endpos else self.entire_len-endpos
            self.lines.extend([f'{(i+spos) * self.wchr}{self.str_}{self.entire_len * self.wchr}'[:self.entire_len]
                               for i in range(wavesize + 1)])
        elif side == 'left':
            wavesize = wavesize or self.entire_len-spos
            wavesize = wavesize if wavesize <= self.entire_len-spos else self.entire_len-spos
            self.lines.extend([f'{i * self.wchr}{self.entire_string[spos:endpos]}{(self.whitespace_len - i) * self.wchr}'
                               for i in range(spos, spos-wavesize, -1)])
        self.update()

    def wave_returning(self, wavesize: int, direction: str):
        if direction == 'right':
            self.wave('right', wavesize)
            self.wave('left', wavesize)
        elif direction == 'left':
            self.wave('left', wavesize)
            self.wave('right', wavesize)

    def eat(self, side: str = 'left'):
        self._validate_side(side)
        if side == 'left':
            self.lines += [f'{self.str_[i:]}{(self.whitespace_len + i) * self.wchr}' for i in range(self.initial_content_len)]
        elif side == 'right':
            self.lines += [f'{(self.whitespace_len + i) * self.wchr}{self.initial_content[:self.initial_content_len - i]}' for i in range(self.initial_content_len)]
        self.update()

    def spew(self, side: str = 'left'):
        self._validate_side(side)
        if side == 'left':
            self.lines += [f'{self.initial_content[-i:]}{(self.entire_len - i) * self.wchr}' for i in range(1, self.initial_content_len + 1)]
        elif side == 'right':
            self.lines += [f'{(self.entire_len - i) * self.wchr}{self.initial_content[:i]}' for i in range(1, self.initial_content_len + 1)]
        self.update()

    def shift_letter_by_letter(self, side: str = 'left'):
        spos, endpos = self.REX.search(self.entire_string).regs[2]
        nmoves = 0
        self.lines.append(self.entire_string)
        slst = list(self.entire_string)
        if side == 'left':
            for charpos, char in enumerate(slst[spos:endpos], start=spos):
                submoves = 1
                slst[charpos] = self.wchr
                while charpos-submoves >= nmoves:
                    if char != self.wchr:
                        slst[charpos - submoves] = char
                        slst[charpos - submoves + 1] = self.wchr
                        self.lines.append(''.join(slst))
                    submoves += 1
                nmoves += 1
        elif side == 'right':
            for charpos, char in zip(range(endpos, spos, -1), reversed(slst[spos:endpos])):
                submoves = 1
                slst[charpos - 1] = self.wchr
                if char == self.wchr:
                    nmoves += 1
                    continue
                while charpos + submoves < self.entire_len - nmoves:
                    slst[charpos + submoves] = char
                    slst[charpos + submoves - 1] = self.wchr
                    submoves += 1
                    self.lines.append(''.join(slst))
                nmoves += 1
        self.update()

    def interweave(self):
        self.lines.append(self.entire_string)
        grps = self.REX.search(self.entire_string)
        spos, endpos = grps.regs[2]
        num_blanks = len(grps['curstr']) - len(grps['curstr'].replace(self.wchr, ''))
        init_chars = self.entire_string[spos:endpos]
        slst = list(init_chars)

        inspos, num_ins = 1, 0
        while len(slst) < (len(init_chars)*2)-1-num_blanks*2:
            if slst[inspos] != self.wchr:
                num_ins += 1
                slst.insert(inspos, self.wchr)
                curline = f"""{(spos - num_ins) * self.wchr}{''.join(slst)}"""
                self.lines.append(f'{curline}{(self.entire_len - len(curline)) * self.wchr}')
                self.update()
            inspos += 2

    def restore(self, direction: str = 'right'):
        grps = self.REX.search(self.entire_string)

        curstr = grps['curstr']
        curpos = 0
        while curstr != self.initial_content:
            if curstr[curpos] != self.initial_content[curpos]:
                curstr = curstr[:curpos] + curstr[1+curpos:]
                self.str_ = curstr
                if direction == 'left':
                    self.lines.append(f"{curstr}{(self.entire_len - len(self.str_)) * self.wchr}")
                elif direction == 'right':
                    self.lines.append(f"{(self.entire_len - len(self.str_)) * self.wchr}{curstr}")

                continue
            curpos += 1

    def eatspew(self, side: str = 'left'):
        self.eat(side=side)
        self.spew(side=side)
        self.entire_string = self.lines[-1]

    @debug
    def run_patterns(self):
        self.plain(10)
        self.wave_returning(10, direction='right')
        self.eat()
        self.spew()
        self.plain(10)
        self.wave('right', 20)
        self.wave('left', 10)
        self.wave('right', 15)
        self.shift_letter_by_letter(side='left')
        self.wave(side='right')
        self.interweave()
        self.wave('left')
        self.restore('left')
        self.wave('right')
        self.eat('right')
        self.spew('right')
        self.duplicate()

        self.print_lines()

    def _validate_side(self, side: str) -> NoReturn:
        if side not in self.SIDES:
            raise ValueError(f"Invalid side specification: {side}. Valid side specifications: {', '.join(self.SIDES)}.")

    def print_lines(self):
        for line in self.lines:
            print('\t',line)


if __name__ == '__main__':

    printer = StringPatternPrinter(content_string="I guess you're right 60k_Risk", pattern_length=29)
    printer.run_patterns()
