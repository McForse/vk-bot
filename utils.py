import pymorphy2
from pymorphy2.shapes import restore_capitalization


class Utils:

    @staticmethod
    def prepositional(text):
        morph = pymorphy2.MorphAnalyzer()
        tokens = text.split()
        inflected = [
            restore_capitalization(
                morph.parse(tok)[0].inflect({'loct'}).word,
                tok
            )
            for tok in tokens
        ]
        return " ".join(inflected)
