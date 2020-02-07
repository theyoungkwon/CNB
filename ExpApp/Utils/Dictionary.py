import autocomplete
from autocorrect import Speller


class Dictionary:

    def __init__(self) -> None:
        autocomplete.load()
        self.speller = Speller()
        super().__init__()

    def predict_word(self, first_word="", second_word="") -> []:
        preds = autocomplete.predict(first_word, second_word, top_n=3)
        result = []
        for prediction in preds:
            result.append(prediction[0])
        return result

    def correct_word(self, word="") -> "":
        return self.speller.autocorrect_word(word)
