import autocomplete
from autocorrect import Speller


class Dictionary:

    def __init__(self) -> None:
        with open('../../data/PhraseSets/big_mackenzie2.txt', 'r') as myfile:
            autocomplete.models.train_models(myfile.read())
        autocomplete.load()
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
        preds = autocomplete.predict(first_word, second_word, top_n=3)
        result = []
        for prediction in preds:
            result.append(prediction[0])
        return result

    def correct_word(self, word="") -> "":
        return self.speller.autocorrect_word(word)

    def get_checking_char_list(self, word="") -> []:
        return self.checking_char_dict2list[word]

    def predict_corrected_word(self, word="") -> []:
        preds = autocomplete.predict(first_word=word, second_word="", top_n=3)
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
                    temp_preds = autocomplete.predict(first_word="".join(word_l), second_word="", top_n=3)
                    if len(temp_preds) > 0:
                        for prediction in temp_preds:
                            result.append(prediction[0])
                        return result
        return []


def main() -> None:
    a = Dictionary()
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

if __name__ == "__main__":
    main()
