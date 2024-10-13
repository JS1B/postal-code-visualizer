import math


def group_by_place(data):
    places = {}
    for row in data[1:]:
        place = row[1]
        if place not in places:
            places[place] = 0

        places[place] += 1

    return places
