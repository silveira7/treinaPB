import re
import treinapb.dictionary.Conversor as Conversor
import treinapb.dictionary.Parser as Parser


def convert(text):
    lexer = Parser.PhonemeLexer()
    converter = Conversor.Conversor()
    text = converter.convert_sentence(text)
    text = re.sub(
        " +",
        " ",
        " ".join(map(lambda x: x.value, lexer.tokenize(text))).replace(",", ""),
    )
    return text
