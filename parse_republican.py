import typing
import dataclasses
import json
import csv
import html2text
import opencc
import sys


class EnhancedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        return super().default(o)


@dataclasses.dataclass
class Definition:
    readings: typing.List[str]
    meanings: typing.List[str]


@dataclasses.dataclass
class Entry:
    word: str
    simplified_guess: str
    source_code: str
    definitions: typing.List[Definition]


occ = opencc.OpenCC('t2s')


text_maker = html2text.HTML2Text()
text_maker.ignore_emphasis = True
text_maker.body_width = None


def strip_number(l):
    maybe_num, _, rest = l.partition('\\. ')
    if maybe_num.isdigit():
        return rest
    return l


out = []

with open('republican.txt') as f:
    rd = csv.reader(f, delimiter="\t", quotechar='"')

    for row in rd:
        init, meaning = row
        word, reading = init.split('<br>', 1)
        word = text_maker.handle(word).strip()
        reading = text_maker.handle(reading).strip()
        meanings = [strip_number(l) for l in text_maker.handle(meaning.replace('<hr>', '')).replace('\n\n', '\n').strip().split('\n')]
        simplified_guess = occ.convert(word)

        entry = Entry(word, simplified_guess, 'r', [Definition([reading], meanings)])
        out.append(entry)


with open('dict.ndjson', 'a') as f:
    for entry in out:
        json.dump(entry, f, ensure_ascii=False, cls=EnhancedJSONEncoder)
        f.write('\n')