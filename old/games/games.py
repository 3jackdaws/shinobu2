import random


WORD = {
    1:"one",
    2:"two",
    3:"three",
    4:"four",
    5:"five",
    6:"six",
}

def roll():
    roll_results = ""
    val = 0
    count = [0,0,0,0,0,0]
    largest = -1
    for i in range(5):
        roll_result = random.randint(1,6)
        roll_results += EMOJI[roll_result]
        val += roll_result
        count[i] += 1
        if count[i] > largest:
            largest = i

    game_result_string = "{}/30, ({})\n{}".format(val, val/30, roll_result)
    return game_result_string, val, 






