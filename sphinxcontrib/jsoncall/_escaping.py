import htmlentitydefs
import re, string

PATTERN = re.compile(r"[&<>\"\x80-\xff]+")

ENTITY_MAP = {}
for i in range(256):
    ENTITY_MAP[chr(i)] = "&#%d;" % i

for entity, char in htmlentitydefs.entitydefs.items():
    if ENTITY_MAP.has_key(char):
        ENTITY_MAP[char] = "&%s;" % entity

def escape_entity(m, get=ENTITY_MAP.get):
    return string.join(map(get, m.group()), "")

def escape(string):
    return PATTERN.sub(escape_entity, str(string))

