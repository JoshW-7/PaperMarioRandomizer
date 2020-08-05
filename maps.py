import os


class Maps:

    def __init__(self):
        Maps.maps = {}

    @classmethod
    def get_maps(cls):
        return Maps.maps

    @classmethod
    def retrieve_maps(cls):
        Maps.maps = {filename.split(".")[0] for filename in os.listdir("./mod/map/src/") if filename.endswith(".mscr")}


MAPS = Maps()