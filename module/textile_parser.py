import re


def text2obj(text):
    """
    テキストをオブジェクトのリストに変換する関数

    Args:
      text: テキスト

    Returns:
      オブジェクトのリスト
    """
    lines = text.split("\n")
    headRegExp = re.compile(r"h(\d+)\. .+")
    paragRegExp = re.compile(r"p\(\. .+")
    res = []
    for i, line in enumerate(lines):
        if re.match(headRegExp, line):
            res.append(
                {
                    "id": i + 1,
                    "head": 0,
                    "text": line,
                    "type": "header",
                    "level": int(re.match(headRegExp, line).group(1)),
                    "start_linum": i,
                    "end_linum": len(lines) - 1,
                }
            )
        elif re.match(paragRegExp, line):
            res.append(
                {
                    "id": i + 1,
                    "head": 0,
                    "text": line,
                    "type": "paragraph",
                    "start_linum": i,
                    "end_linum": len(lines) - 1,
                }
            )
        else:
            pass
            # res.append({
            #   "id": i + 1,
            #   "head": None,
            #   "text": line,
            #   "type": "text",
            # })
    return res


def parseTextile(lines, level, head_id, watched=[]):
    """
    テキストオブジェクトのリストを解析する関数

    Args:
      lines: テキストオブジェクトのリスト
      level: 現在のレベル
      head_id: 親ヘッダーのID
      res: 解析結果のリスト
      watched: 処理済みのオブジェクトのIDリスト

    Returns:
      解析結果のリスト
    """

    res = []
    for i, line in enumerate(lines):
        if line["id"] in watched:
            continue
        if line["type"] == "header":
            if line["level"] == level:
                line["head"] = head_id
                res.append(line)
                watched.append(line["id"])
                res_ = parseTextile(lines, level + 1, line["id"], watched)
                for r in res_:
                    res.append(r)
                    watched.append(r["id"])
            elif line["level"] < level:
                return res
        elif line["type"] == "paragraph":
            line["head"] = head_id
            res.append(line)
            watched.append(line["id"])
    return lines


def set_end_nums(lines):
    max_linum = 0
    for i in range(len(lines)):
        l = lines[i]
        # 次の同レベル似合わせる
        for j in range(len(lines)):
            ll = lines[j]
            if (
                l["head"] == ll["head"]
                and l["id"] < ll["id"]
                and l["end_linum"] > ll["start_linum"]
            ):
                l["end_linum"] = ll["start_linum"]
        if l["end_linum"] > max_linum:
            max_linum = l["end_linum"]

    for i in range(len(lines)):
        l = lines[i]
        if l["end_linum"] != max_linum:
            continue
        for j in range(len(lines)):
            ll = lines[j]
            if l["head"] == ll["id"]:
                l["end_linum"] = ll["end_linum"]

    return res


# テキスト例
text = """
h1. Header1

title

h2. Header2
p(. paragraph1

p(. paragraph2

h3. Header3

h2. Header2
p(. paragraph1

h3. Header23
h2. Header24

"""

# テキストをオブジェクトに変換
objects = text2obj(text)

# オブジェクトを解析
res = parseTextile(objects, 1, 0)

res = set_end_nums(res)

# print(objects)
# print(res)

# 解析結果を出力
for r in res:
    print(r)
