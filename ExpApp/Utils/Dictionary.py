import sys
sys.path.insert(1, './yd_auto_complete')
from __init__ import *
from autocomplete import *
from autocorrect import Speller
import copy


class Dictionary:

    def __init__(self,load_path=None) -> None:
        load(load_path)
        self.speller = Speller()
        super().__init__()
        self.checking_char_dict2list = {
            'q': ['a', 'z'], 'a': ['q', 'z'], 'z': ['a', 'q'],
            'w': ['s', 'x'], 's': ['w', 'x'], 'x': ['s', 'w'],
            'e': ['d', 'c'], 'd': ['e', 'c'], 'c': ['d', 'e'],
            'r': ['f', 'v'], 'f': ['r', 'v'], 'v': ['f', 'r'],
            't': ['g', 'b'], 'g': ['t', 'b'], 'b': ['g', 't'],
            'y': ['h', 'n'], 'h': ['y', 'n'], 'n': ['h', 'y'],
            'u': ['j', 'm'], 'j': ['u', 'm'], 'm': ['j', 'u'],
            'i': ['k'], 'k': ['i'], 'p': [],
            'o': ['l'], 'l': ['o']
        }

    def predict_word(self, first_word="", second_word="") -> []:
        preds = predict(first_word, second_word, top_n=3)
        result = []
        for prediction in preds:
            result.append(prediction[0])
        return result

    def correct_word(self, word="") -> "":
        return self.speller.autocorrect_word(word)

    def get_checking_char_list(self, word="") -> []:
        return self.checking_char_dict2list[word]

    def predict_corrected_word(self, word="") -> []:
        preds = predict(first_word=word, second_word="", top_n=3)
        result = []
        # if preds list is not empty
        if len(preds) != 0:
            for prediction in preds:
                result.append(prediction[0])
            return result
        else:  # if preds list is empty, recheck all characters
            for i in range(1, len(word) + 1):
                char = word[-i]
                checking_char_list = self.get_checking_char_list(char)
                for checking_char in checking_char_list:
                    word_l = list(word)
                    word_l[-i] = checking_char
                    temp_preds = predict(first_word="".join(word_l), second_word="", top_n=3)
                    if len(temp_preds) > 0:
                        for prediction in temp_preds:
                            result.append(prediction[0])
                        return result
        return []


def main() -> None:
    a = Dictionary('big_mackenzie2')
    print("TESTING:: Dictionary.predict_word(I, shl) // Dictionary.predict_corrected_word(I, shl)")
    print(a.predict_word("I", "shl"))
    print(a.predict_corrected_word("shl"))

    print("TESTING:: Dictionary.predict_word(we, bd) // Dictionary.predict_corrected_word(we, bd)")
    print(a.predict_word("we", "bd"))
    print(a.predict_corrected_word("bd"))

    print("TESTING:: Dictionary.predict_word(go, x) // Dictionary.predict_corrected_word(go, x)")
    print(a.predict_word("go", "x"))
    print(a.predict_corrected_word("xh"))

    print(a.predict_corrected_word("weqt"))

    ##### Example Phrases #####
    # flashing red light means stop
    # dashing through the snow
    # please provide your date of birth
    # the opposing team is over there
    # obligations must be met first
    # prevailing wind from the east
    # I am going to a music lesson
    # please keep this confidential
    # it is very windy today

    ##### prediction below #####
    print(a.predict_word("flashing", "re"))
    print(a.predict_word("light", "me" ))
    print(a.predict_word("dashing", "th"))
    print(a.predict_word("the", "sn"))
    print(a.predict_word("please", "pr"))
    print(a.predict_word("your", "da"))
    print(a.predict_word("opposing", "te"))
    print(a.predict_word("obligations", "mu"))
    print(a.predict_word("met", "fi"))
    print(a.predict_word("prevailing", "wi"))
    print(a.predict_word("music", "le"))
    print(a.predict_word("please", "ke"))
    print(a.predict_word("very", "wi"))

    print(a.predict_word("fl",""))
    print(a.predict_word("li",""))
    print(a.predict_word("da",""))
    print(a.predict_word("th",""))
    print(a.predict_word("pl",""))
    print(a.predict_word("yo",""))
    print(a.predict_word("op",""))
    print(a.predict_word("ob",""))
    print(a.predict_word("me",""))
    print(a.predict_word("pr",""))
    print(a.predict_word("mu",""))
    print(a.predict_word("pl",""))
    print(a.predict_word("ve",""))

if __name__ == "__main__":
    main()
