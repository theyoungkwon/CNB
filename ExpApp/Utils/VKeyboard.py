from ExpApp.Utils.datacore_constants import SET7, KeyboardControl

config3 = [
    ["A", "B", "C"],
    ["D", "E", "F"],
    ["G", "H", "I"],
    ["J", "K", "L"],
    ["M", "N", "O"],
    ["P", "Q", "R"],
    ["S", "T", "U"],
    ["V", "W", "X"],
    ["Y", "Z", " "],
]


gesture_config_def = {
    "point": 1,
    "thumb": 2,
    "two": 2,
    "three": 3,
    "four": 3,
}




class VKeyboard:
    def __init__(self, config=None, max_votes=KeyboardControl.MAX_VOTES, gesture_config=None) -> None:
        super().__init__()
        if gesture_config is None:
            gesture_config = gesture_config_def
        if config is None:
            config = config3
        self.key_config = config
        self.blocks_num = len(self.key_config)
        self.block_size = len(self.key_config[0])
        self.gesture_config = gesture_config
        self.votes = [0] * self.block_size
        self.max_votes = max_votes
        self.current_block = 0

    def getBlockByAngle(self, angle, a_min, a_max):
        step = (a_max - a_min) / len(self.key_config)
        _angle = angle - a_min
        index = int(_angle / step)
        new_current_block = self.blocks_num - index - 1
        if new_current_block != self.current_block:
            self.votes = [0] * self.block_size
        self.current_block = new_current_block
        return self.key_config[self.current_block]

    def get_block_by_Index(self, index):
        new_current_block = index
        if new_current_block != self.current_block:
            self.votes = [0] * self.block_size
        self.current_block = new_current_block
        return self.key_config[self.current_block]

    def recordVote(self, gesture):
        if not gesture in self.gesture_config:
            return None
        vote = self.gesture_config[gesture]
        if vote > len(self.key_config[self.current_block]):
            return None
        self.votes[vote - 1] += 1
        if self.votes[vote - 1] == self.max_votes:
            self.votes = [0] * self.block_size
            return self.key_config[self.current_block][vote - 1]
        return None
