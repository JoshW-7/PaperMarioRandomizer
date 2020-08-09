import os


class Maps:

    def __init__(self):
        Maps.maps = {}
        Maps.blacklist = [
            "end_00",
            "gv_01",
            "dgb_00",
            "hos_20",
            "hos_10",
            "hos_05",
            "iwa_11",
            "mac_06",
            "machi",
            "mgm_01",
            "mgm_02",
            "mgm_03",
            "osr_00",
            "osr_03",
            "osr_04",
            "pra_39",
            "pra_38",
            "pra_37",
            "pra_27",
            "pra_28",
            "pra_36",
            "tik_24",
            "tst_01",
            "tst_02",
            "tst_03",
            "tst_04",
            "tst_10",
            "tst_11",
            "tst_12",
            "tst_13",
            "tst_20",
            "kmr_23",
            "kmr_24",
            "kmr_30",
            "kmr_22",
            "kmr_21",
            "sam_04",
            "omo_16",
            "trd_05",
            "omo_15",
            "kkj_15",
            "kkj_14",
            "kkj_26",
            "kkj_27",
            "kkj_29",
        ]

    @classmethod
    def get_maps(cls):
        return Maps.maps

    @classmethod
    def retrieve_maps(cls):
        Maps.maps = {filename.split(".")[0] for filename in os.listdir("./mod/map/src/") if filename.endswith(".mscr")}
MAPS = Maps()