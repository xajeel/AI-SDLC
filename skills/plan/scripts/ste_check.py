#!/usr/bin/env python3
"""Check markdown prose against the STE writing rules in skills/plan/ste.md.

Usage: python3 ste_check.py FILE [FILE ...]
Exit 0: no errors. Exit 1: errors found. Exit 2: bad usage or unreadable file.
Unofficial; not affiliated with or endorsed by ASD. ASD-STE100 is a trademark of ASD.
"""

import re
import sys

MAX_PROCEDURAL = 20
MAX_DESCRIPTIVE = 25
MAX_PARAGRAPH = 6

USAGE = "usage: ste_check.py FILE [FILE ...]"

FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}(\s|$)")
BREAK_RE = re.compile(r"^\s{0,3}([-*_=])(\s*\1){2,}\s*$")
LIST_RE = re.compile(r"^(\s*)([-*+]|\d{1,9}[.)])\s+(.*)$")
CHECKBOX_RE = re.compile(r"^\[[ xX]\]\s+")
QUOTE_RE = re.compile(r"^\s*(?:>\s?)+")
ENTITY_RE = re.compile(r"&#?\w+;")
TRACE_RE = re.compile("[→└├│]")
CONTRACTION_RE = re.compile(r"^[a-z]+(n't|'re|'ll|'ve|'m|'d|'s)$")
TOKEN_RE = re.compile(
    r"(?P<code>``.+?``|`[^`]+`)"
    r"|(?P<angle><[A-Za-z/!][^<>]*>)"
    r"|(?P<ref>\[[^\[\]]*\](?:\([^()\s]*\))?)"
    r"|(?P<word>[^\s`<\[]+)"
    r"|(?P<other>\S)"
)

LEAD = "([{\"'*_~“‘"
CLOSE = ")]}\"'*_~”’"
CLAUSE_END = ".,;:!?"
NO_SPLIT = {"e.g.", "i.e.", "vs.", "cf."}

LATIN = {
    "e.g.": 'write "for example"',
    "i.e.": 'write "that is"',
    "etc.": "list all the items",
    "vs.": 'write "compared to"',
}
S_CONTRACTIONS = {
    "it's", "that's", "there's", "here's", "what's", "who's",
    "he's", "she's", "let's", "where's", "how's",
}
EXPANSIONS = {"can't": "cannot", "won't": "will not", "shan't": "shall not", "let's": "let us"}
SUFFIXES = {"n't": " not", "'re": " are", "'ll": " will", "'ve": " have", "'m": " am", "'d": " would", "'s": " is"}

SWAPS = {
    "may": "can", "might": "can", "should": "must",
    "ensure": "make sure that", "ensures": "makes sure that",
    "utilize": "use", "utilizes": "uses", "utilise": "use",
    "perform": "do", "performs": "does",
    "begin": "start", "begins": "starts", "began": "started",
}
AUX = {"am", "is", "are", "was", "were", "be", "been", "being"}
ADVERBS = {"not", "also", "then", "only", "always", "never", "still", "already", "often", "now", "first"}
IRREGULAR = set(
    "done made written built sent found given known shown taken seen kept held chosen broken "
    "hidden driven drawn told said paid brought thought left lost meant begun gotten set put "
    "read run split".split()
)
ING_OK = set(
    "thing nothing something anything everything string during bring ring spring king ceiling "
    "morning evening ping sing wing swing sting fling sling cling bling "
    "pending warning setting existing".split()
)
IMPERATIVES = set(
    "add append apply ask avoid build call change check choose commit compare confirm copy "
    "create delete do edit ensure fill find fix follow get give go include install keep let "
    "list load log look make mark merge move never note open pass pick print push put read "
    "record remove rename replace report return run save search select send set show skip "
    "split start stop store tell test try update use verify wait write always only".split()
)
PHRASAL_VERBS = (
    ("set up", "set sets setting", "configure"),
    ("look up", "look looks looked looking", "find"),
    ("find out", "find finds found finding", "learn"),
    ("carry out", "carry carries carried carrying", "do"),
    ("figure out", "figure figures figured figuring", "find"),
    ("pick up", "pick picks picked picking", "get"),
    ("check out", "check checks checked checking", "examine"),
    ("point out", "point points pointed pointing", "show"),
    ("end up", "end ends ended ending", "become"),
    ("come up with", "come comes came coming", "find"),
)
PHRASALS = [(p, set(forms.split()), p.split()[1:], alt) for p, forms, alt in PHRASAL_VERBS]


def _bare(raw):
    """Strip quotes, brackets, emphasis, and trailing punctuation from a word."""
    return raw.lstrip(LEAD).rstrip(CLOSE + CLAUSE_END).replace("’", "'")


def _clause_end(raw):
    return raw.rstrip(CLOSE)[-1:] in CLAUSE_END


def _ends_sentence(raw):
    text = raw.rstrip(CLOSE)
    return text[-1:] in (".", "!", "?") and text.lstrip(LEAD).lower() not in NO_SPLIT


def _is_word(token):
    kind, raw, _ = token
    return kind in ("code", "angle", "ref") or (kind == "word" and any(c.isalnum() for c in raw))


def _tokenize(text, number):
    return [(m.lastgroup, m.group(), number) for m in TOKEN_RE.finditer(text)]


def _imperative(text):
    """True when the first word of a list item is a common imperative verb."""
    for match in TOKEN_RE.finditer(text):
        if match.lastgroup != "word":
            return False
        word = _bare(match.group()).lower()
        if word:
            return word in IMPERATIVES
    return False


def _strip_comments(line, in_comment):
    """Remove HTML comments; return the remaining text and whether a comment stays open."""
    kept = []
    pos = 0
    while True:
        if in_comment:
            end = line.find("-->", pos)
            if end < 0:
                return "".join(kept), True
            pos, in_comment = end + 3, False
        else:
            start = line.find("<!--", pos)
            if start < 0:
                kept.append(line[pos:])
                return "".join(kept), False
            kept.append(line[pos:start])
            pos, in_comment = start + 4, True


def _frontmatter_end(lines):
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            if lines[index].strip() in ("---", "..."):
                return index + 1
    return 0


def _units(lines):
    """Split markdown lines into prose units: paragraphs and list items."""
    units = []
    current = None
    fence = None
    in_comment = False
    list_kind = None
    for index in range(_frontmatter_end(lines), len(lines)):
        raw = lines[index]
        if fence:
            stripped = raw.strip()
            if stripped and set(stripped) == {fence[0]} and len(stripped) >= len(fence):
                fence = None
            continue
        line, in_comment = _strip_comments(raw, in_comment)
        if not line.strip():
            if not raw.strip():
                current = None
            continue
        opening = FENCE_RE.match(line)
        if opening:
            fence, current = opening.group(1), None
            continue
        if (
            HEADING_RE.match(line)
            or BREAK_RE.match(line)
            or line.lstrip().startswith("|")
            or TRACE_RE.search(line)  # an ASCII trace or tree outside a fence, not prose
        ):
            current, list_kind = None, None
            continue
        line = QUOTE_RE.sub("", line)
        if not line.strip():
            current = None
            continue
        item = LIST_RE.match(line)
        if item:
            line = CHECKBOX_RE.sub("", item.group(3))
            list_kind = item.group(2)[0].isdigit() or _imperative(line)
            current = {"procedural": list_kind, "tokens": []}
            units.append(current)
        elif current is None:
            nested = list_kind is not None and raw[:1] in (" ", "\t")
            current = {"procedural": bool(nested and list_kind), "tokens": []}
            units.append(current)
            if not nested:
                list_kind = None
        current["tokens"].extend(_tokenize(line, index + 1))
    return units


def _sentences(tokens):
    sentence = []
    for token in tokens:
        sentence.append(token)
        if token[0] == "word" and _ends_sentence(token[1]):
            yield sentence
            sentence = []
    if sentence:
        yield sentence


def _expand(word):
    lower = word.lower()
    if lower in EXPANSIONS:
        full = EXPANSIONS[lower]
    else:
        suffix = CONTRACTION_RE.match(lower).group(1)
        full = word[: -len(suffix)] + SUFFIXES[suffix]
    return full[0].upper() + full[1:] if word[0].isupper() else full


def _check_word(raw, line, add):
    word = _bare(raw)
    lower = word.lower()
    if ";" in ENTITY_RE.sub("", raw):
        add(line, "ERROR", "semicolon", "semicolon in prose — write two sentences")
    latin = raw.strip("()[]{}\"'*_,;:").lower()
    latin = latin if latin.endswith(".") else latin + "."
    if latin in LATIN:
        add(line, "ERROR", "latin", f'"{latin}" — {LATIN[latin]}')
    match = CONTRACTION_RE.match(lower)
    if match and (match.group(1) != "'s" or lower in S_CONTRACTIONS):
        add(line, "ERROR", "contraction", f'"{word}" — write "{_expand(word)}"')
    if lower in SWAPS:
        add(line, "WARN", "word-choice", f'"{lower}" — use "{SWAPS[lower]}"')
    for part in lower.split("-"):
        if len(part) >= 5 and part.endswith("ing") and part.isalpha() and part not in ING_OK:
            add(line, "WARN", "ing-word", f'"{part}" — use a verb or a noun, not an -ing form')


def _participle(word):
    if word in IRREGULAR:
        return True
    return len(word) > 3 and word.isalpha() and word.endswith("ed") and not word.endswith("eed")


def _check_passive(words, add):
    for i, entry in enumerate(words):
        if not entry or entry[0] not in AUX or _clause_end(entry[1]):
            continue
        j = i + 1
        nxt = words[j] if j < len(words) else None
        if nxt and (nxt[0] in ADVERBS or nxt[0].endswith("ly")) and not _clause_end(nxt[1]):
            j += 1
        if j < len(words) and words[j] and _participle(words[j][0]):
            phrase = " ".join(w[0] for w in words[i : j + 1])
            add(entry[2], "WARN", "passive", f'probable passive "{phrase}" — use the active voice')


def _check_phrasal(words, add):
    for i, entry in enumerate(words):
        if not entry or _clause_end(entry[1]):
            continue
        for phrase, forms, particles, alt in PHRASALS:
            following = words[i + 1 : i + 1 + len(particles)]
            if entry[0] not in forms or len(following) < len(particles):
                continue
            if all(w and w[0] == p for w, p in zip(following, particles)) and not any(
                _clause_end(w[1]) for w in following[:-1]
            ):
                add(entry[2], "WARN", "phrasal-verb", f'"{phrase}" — use "{alt}"')


def _check_sentence(sentence, procedural, add):
    line = sentence[0][2]
    count = sum(1 for token in sentence if _is_word(token))
    if count > MAX_DESCRIPTIVE:
        add(line, "ERROR", "sentence-length", f"sentence has {count} words (max {MAX_DESCRIPTIVE})")
    elif procedural and count > MAX_PROCEDURAL:
        add(line, "WARN", "procedural-length", f"procedural sentence has {count} words (max {MAX_PROCEDURAL})")
    words = []
    for kind, raw, number in sentence:
        if kind == "word":
            _check_word(raw, number, add)
            words.append((_bare(raw).lower(), raw, number))
        else:
            words.append(None)
    _check_passive(words, add)
    _check_phrasal(words, add)


def check_text(text):
    """Return (line, level, rule, message) findings for one markdown document."""
    findings = []

    def add(line, level, rule, message):
        findings.append((line, level, rule, message))

    for unit in _units(text.lstrip("﻿").splitlines()):
        sentences = [s for s in _sentences(unit["tokens"]) if any(_is_word(t) for t in s)]
        if len(sentences) > MAX_PARAGRAPH:
            add(sentences[0][0][2], "ERROR", "paragraph-length",
                f"paragraph has {len(sentences)} sentences (max {MAX_PARAGRAPH})")
        for sentence in sentences:
            _check_sentence(sentence, unit["procedural"], add)
    findings.sort(key=lambda finding: finding[0])
    return findings


def main(argv=None):
    """Check each FILE; return 0 when clean, 1 on errors, 2 on bad usage or an unreadable file."""
    args = sys.argv[1:] if argv is None else list(argv)
    if args[:1] in (["-h"], ["--help"]):
        print(USAGE)
        return 0
    options = [arg for arg in args if arg.startswith("-")]
    if not args or options:
        print(USAGE, file=sys.stderr)
        if options:
            print(f"error: unknown option: {options[0]}", file=sys.stderr)
        return 2
    status = 0
    for name in args:
        try:
            with open(name, encoding="utf-8", errors="replace") as handle:
                text = handle.read()
        except OSError as exc:
            print(f"error: {name}: {exc.strerror or exc}", file=sys.stderr)
            status = 2
            continue
        findings = check_text(text)
        for line, level, rule, message in findings:
            print(f"{name}:{line}: {level} {rule}: {message}")
        errors = sum(1 for finding in findings if finding[1] == "ERROR")
        print(f"{name}: {errors} errors, {len(findings) - errors} warnings")
        if errors and status == 0:
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main())
