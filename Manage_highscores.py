def manage_highscore(player, name):

    highscore_list = open("highscores.txt", "r+")
    list = []
    score_total = 0

    for line in highscore_list:
        list.append(line.split())

    for line in list:
        line[0] = int(line[0])
    list.append([player.points, name])

    highscore_list.close()

    highscore_list = open("highscores.txt", "w")
    highscore_list.truncate()

    list.sort()
    list.reverse()

    for line in list:
        line[0] = str(line[0])
        if score_total < 12:
            highscore_list.write(line[0] + " " + line[1] + "\n")
            score_total += 1

    highscore_list.close()
    
