import random


class PhraseSelector:

    def __init__(self) -> None:
        super().__init__()
        self.data_path = '../../data/PhraseSets/phrases2.txt'
        self.phase_list = []
        with open(self.data_path) as f:
            for line in f:
                self.phase_list.append(line)
        print("\nPhrases are loaded and the number of phases is : ", len(self.phase_list))

    def select_phrase(self) -> "":
        return random.choice(self.phase_list).strip()

    def select_word(self) -> "":
        while (1):
            phrase = random.choice(self.phase_list)
            word_list = phrase.strip().split()
            for word in word_list:
                if len(word) == 5:
                    return word.lower()


def main() -> None:
    a = PhraseSelector()
    print("TESTING:: PhraseSelector.select_phrase()")
    for i in range(10):
        print(a.select_phrase())

    print("\nTESTING:: PhraseSelector.select_word()")
    for i in range(10):
        print(a.select_word())


if __name__ == "__main__":
    main()
