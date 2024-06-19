import logging
import re

from lsprotocol import types

from pygls.server import LanguageServer
from pygls.workspace import TextDocument


def text2obj(lines):
    """
    テキストをオブジェクトのリストに変換する関数

    Args:
      text: テキスト

    Returns:
      オブジェクトのリスト
    """
    headRegExp = re.compile(r"h(\d+)\. (.+)")
    paragRegExp = re.compile(r"p\(\. (.+)")
    res = []
    for i, line in enumerate(lines):
        h_match = headRegExp.match(line)
        p_match = paragRegExp.match(line)
        if h_match:
            res.append(
                {
                    "id": i + 1,
                    "head": 0,
                    "title": h_match.group(2),
                    "type": "header",
                    "level": int(h_match.group(1)),
                    "start_linum": i,
                    "end_column": len(line.strip()),
                    "end_linum": len(lines),
                }
            )
        elif p_match:
            res.append(
                {
                    "id": i + 1,
                    "head": 0,
                    "title": p_match.group(1),
                    "type": "paragraph",
                    "start_linum": i,
                    "end_column": len(line.strip()),
                    "end_linum": len(lines),
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
    return res


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

    return lines


class SymbolsLanguageServer(LanguageServer):
    """Language server demonstrating the document and workspace symbol methods in the LSP
    specification."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = {}

    def parse(self, doc: TextDocument):
        lines_ = text2obj(doc.lines)

        lines = parseTextile(lines_, 1, 0, [])
        lines = set_end_nums(lines)

        symbols = {}

        for i, line in enumerate(lines):
            symbols[line["id"]] = dict(
                range_=types.Range(
                    start=types.Position(line=line["start_linum"], character=0),
                    end=types.Position(
                        line=line["start_linum"], character=line["end_column"]
                    ),
                ),
                title=types.StringValue(line["title"]),
                end_linum=types.StringValue(str(line["end_linum"])),
                head=types.StringValue(str(line["head"])),
            )

        self.index[doc.uri] = {"symbols": symbols}
        logging.info("Index: %s", self.index)


server = SymbolsLanguageServer("lsp-textile", "v1")


@server.feature(types.TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: SymbolsLanguageServer, params: types.DidOpenTextDocumentParams):
    # logging.info(
    #     "Run: =========== TEXT_DOCUMENT_DID_OPEN ============= \n%s",
    #     params.text_document.uri,
    # )
    """Parse each document when it is opened"""
    doc = ls.workspace.get_text_document(params.text_document.uri)
    # logging.info("XXX%sXXX", ls.index.keys())
    ls.parse(doc)


@server.feature(types.TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: SymbolsLanguageServer, params: types.DidOpenTextDocumentParams):
    # logging.info("Run: =========== TEXT_DOCUMENT_DID_CHANGE =============")
    """Parse each document when it is changed"""
    doc = ls.workspace.get_text_document(params.text_document.uri)
    ls.parse(doc)


@server.feature(types.TEXT_DOCUMENT_DOCUMENT_SYMBOL)
def document_symbol(ls: SymbolsLanguageServer, params: types.DocumentSymbolParams):
    """Return all the symbols defined in the given document."""
    if (index := ls.index.get(params.text_document.uri)) is None:
        # logging.info("=========== > None")
        return None
    # logging.info("=========== > %s", ls.index)

    def _createSymbols(index, current_node="0"):
        res = []
        for node_id, info in index.get("symbols", {}).items():
            if info["head"].value != current_node:
                continue

            range_ = info["range_"]
            end = int(info["end_linum"].value)
            name = info["title"].value

            symbol = types.DocumentSymbol(
                name=name,
                kind=types.SymbolKind.String,
                range=types.Range(
                    start=types.Position(line=range_.start.line, character=0),
                    end=types.Position(line=end - 1, character=0),
                ),
                selection_range=range_,
                children=_createSymbols(index, str(node_id)),
            )

            res.append(symbol)

        return res

    symbols = _createSymbols(index)
    logging.info("Symbols: %s", symbols)

    return symbols


def main():
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    # logging.info("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    server.start_io()
