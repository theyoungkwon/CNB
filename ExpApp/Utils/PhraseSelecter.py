import random


class PhraseSelecter:

    def __init__(self) -> None:
        super().__init__()
        self.data_path = '../../data/PhraseSets/phrases2.txt'
        self.phase_list = []
        with open(self.data_path) as f:
            for line in f:
                self.phase_list.append(line)
        print ("\nPhases are loaded and the number of phases is : ", len(self.phase_list))

    def select_phase(self) -> "":
        return random.choice(self.phase_list)

def main() -> None:
    a = PhraseSelecter()
    for i in range(10):
        print(a.select_phase())

if __name__ == "__main__":
    main()