# -*- coding: utf-8 -*-
"""
Created on Sat Dec 16 08:17:39 2023

@author: hundi
"""

#%%
import gspread
from datetime import datetime
import string
import json

gc = gspread.service_account('G:\DS\Secrets\service_account.json')
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
spreadsheet = gc.open('Fantasy_BBall')
#%%
from espn_api.basketball import League
from espn_api.basketball import Matchup
from espn_api.basketball import Team
from espn_api.basketball.box_score import H2HCategoryBoxScore

league = League(league_id=1484695785, year=2024)
#%%
import pathlib
rankingsPath = "G:/DS/rankings/"
paths = [f for f in pathlib.Path(rankingsPath).iterdir() if f.is_file()]
files = []
for path in paths:
    files.append(path.name)
fileName = sorted(files, reverse = True)[0]
#%%
playerTeams = {}
for team in league.teams:
    for player in team.roster:
        playerTeams[player.name] = team.team_name

with open("G:/DS/rankings/" + fileName, "r") as read_file:
    rankingsJson = json.load(read_file)
#%%
draft = league.draft
players = rankingsJson["players"]

playerRatings = {}

for player in players:
    playerRatings[player["player"]["fullName"]] = player["ratings"]['0']['totalRating']
#%% Drafts
teamDrafts = {}
for pick in draft:
    teamName = pick.team.team_name
    if teamName not in teamDrafts:
        teamDrafts[teamName] = []
    currentTeam = playerTeams.get(pick.playerName) if playerTeams.get(pick.playerName) else 'NA'    
    teamDrafts[teamName].append({"player": pick.playerName, "rating": playerRatings[pick.playerName], "currentTeam": currentTeam})
#%%
draftsAsStr = json.dumps(teamDrafts, indent=4)
draftsFilePath = "rankings/drafts/" + fileName
with open(draftsFilePath, "w") as outfile:
    outfile.write(draftsAsStr)  
#%% Upload Drafts
i = 0
row = 1
totals = {}
for teamName, draftRatings in teamDrafts.items():
    teamList = [[teamName]]
    totalRanking = 0
    ratings = []
    totals[teamName] = {}
    for rankings in draftRatings:        
        teamList.append([rankings["player"], rankings["rating"], rankings["currentTeam"]])
        totalRanking += rankings["rating"]
        ratings.append(rankings["rating"])
    sortedDown = sorted(ratings, reverse=True)
    top5 = sum(sortedDown[:5])
    top10 = sum(sortedDown[:10])
    teamList.append(["Total", totalRanking])    
    teamList.append(["Best 5", top5])
    teamList.append(["Best 10", top10])
    totals[teamName]["Total"] = totalRanking
    totals[teamName]["Best 5"] = top5
    totals[teamName]["Best 10"] = top10
    spreadsheet.worksheet("Drafts").update(values=teamList, range_name = gspread.utils.rowcol_to_a1(row, (i*3)+1))
    i = i + 1
    if (i == 5):
        i = 0
        row = 19
    
#%%
namesList = [""]
totalList = ["Total"]
top10List = ["Top 10"]
top5List = ["Top 5"]
for teamName, stats in totals.items():
    namesList.append(teamName)
    totalList.append(stats["Total"])
    top10List.append(stats["Best 10"])
    top5List.append(stats["Best 5"])
totalsList = [namesList, totalList, top10List, top5List]    
spreadsheet.worksheet("Drafts").update(values=totalsList, range_name = "A38")