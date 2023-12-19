# -*- coding: utf-8 -*-
"""
Created on Sat Dec  9 11:31:55 2023

@author: hundi
"""
import urllib.request
import json
from datetime import datetime

request = urllib.request.Request(url="https://lm-api-reads.fantasy.espn.com/apis/v3/games/fba/seasons/2024/segments/0/leagues/1484695785?view=kona_player_info&view=mStatRatings", headers={
     "x-fantasy-filter": '{"players":{"filterSlotIds":{"value":[0,1,2,3,4,5,6,7,8,9,10,11]},"limit":2000,"offset":0,"sortRating":{"additionalValue":null,"sortAsc":false,"sortPriority":1,"value":0},"filterRanksForScoringPeriodIds":{"value":[54]},"filterRanksForRankTypes":{"value":["STANDARD"]},"filterStatsForTopScoringPeriodIds":{"value":5,"additionalValue":["002024","102024","002023","012024","022024","032024","042024"]}}}'
    })

with urllib.request.urlopen(request) as response:
    dataJson = json.loads(response.read())
asStr = json.dumps(dataJson, indent=4)
filePath = "rankings/" + datetime.now().strftime("%y-%m-%d_%H_%M_%S") + ".json"
with open(filePath, "w") as outfile:
    outfile.write(asStr)