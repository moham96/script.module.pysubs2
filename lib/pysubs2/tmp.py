from __future__ import print_function, unicode_literals

import re
from .formatbase import FormatBase
from .ssaevent import SSAEvent
from .ssastyle import SSAStyle
from .substation import parse_tags
from .time import ms_to_times, make_time, TMPTIMESTAMP, tmptimestamp_to_ms 

#: Largest timestamp allowed in Tmp, ie. 99:59:59.
MAX_REPRESENTABLE_TIME = make_time(h=100) - 1

def ms_to_timestamp(ms):
    """Convert ms to 'HH:MM:SS'"""
    # XXX throw on overflow/underflow?
    if ms < 0: ms = 0
    if ms > MAX_REPRESENTABLE_TIME: ms = MAX_REPRESENTABLE_TIME
    h, m, s, ms = ms_to_times(ms)
    return "%02d:%02d:%02d" % (h, m, s)


class TmpFormat(FormatBase):
    @classmethod
    def guess_format(cls, text):
        if "[Script Info]" in text or "[V4+ Styles]" in text:
            # disambiguation vs. SSA/ASS
            return None

        for line in text.splitlines():
            if len(TMPTIMESTAMP.findall(line)) == 1:
                return "tmp"

    @classmethod
    def from_file(cls, subs, fp, format_, **kwargs):
        timestamps = [] # (start)
        following_lines = [] # contains lists of lines following each timestamp

        for line in fp:
            stamps = TMPTIMESTAMP.findall(line)[0]
            if len(stamps) == 3: # timestamp line
                start = tmptimestamp_to_ms(stamps)
                #calculate endtime from starttime + 2 seconds + 1 second per each space in string (which should roughly equal number of words)
                end = start + 3000 + (1000 * line.count(" "))
                timestamps.append((start, end))
                following_lines.append([])
            else:
                if timestamps:
                    following_lines[-1].append(line)

        def prepare_text(lines):
            s = "".join(lines).strip()
            s = re.sub(r"\n+ *\d+ *$", "", s) # strip number of next subtitle
            s = re.sub(r"< *i *>", r"{\i1}", s)
            s = re.sub(r"< */ *i *>", r"{\i0}", s)
            s = re.sub(r"< *s *>", r"{\s1}", s)
            s = re.sub(r"< */ *s *>", r"{\s0}", s)
            s = re.sub(r"< *u *>", "{\\u1}", s) # not r" for Python 2.7 compat, triggers unicodeescape
            s = re.sub(r"< */ *u *>", "{\\u0}", s)
            s = re.sub(r"< */? *[a-zA-Z][^>]*>", "", s) # strip other HTML tags
            s = re.sub(r"\n", r"\N", s) # convert newlines
            return s

        subs.events = [SSAEvent(start=start, end=end, text=prepare_text(lines))
                       for (start, end), lines in zip(timestamps, following_lines)]

    @classmethod
    def to_file(cls, subs, fp, format_, **kwargs):
        def prepare_text(text, style):
            body = []
            for fragment, sty in parse_tags(text, style, subs.styles):
                fragment = fragment.replace(r"\h", " ")
                fragment = fragment.replace(r"\n", "\n")
                fragment = fragment.replace(r"\N", "\n")
                if sty.italic: fragment = "<i>%s</i>" % fragment
                if sty.underline: fragment = "<u>%s</u>" % fragment
                if sty.strikeout: fragment = "<s>%s</s>" % fragment
                body.append(fragment)

            return re.sub("\n+", "\n", "".join(body).strip())

        visible_lines = (line for line in subs if not line.is_comment)

        for i, line in enumerate(visible_lines, 1):
            start = ms_to_timestamp(line.start)
            #end = ms_to_timestamp(line.end)
            text = prepare_text(line.text, subs.styles.get(line.style, SSAStyle.DEFAULT_STYLE))

            print("%d" % i, file=fp) # Python 2.7 compat
            print(start, text, end="\n", file=fp)
            #print(text, end="\n\n", file=fp)
