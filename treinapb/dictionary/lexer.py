import re
import dictionary.Conversor as Conversor
import dictionary.Parser as Parser


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
