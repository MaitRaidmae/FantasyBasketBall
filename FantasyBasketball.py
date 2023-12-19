# -*- coding: utf-8 -*-
"""
Created on Sun Oct 29 13:11:46 2023

@author: hundi
"""

#%%
import gspread
from datetime import datetime
import string

gc = gspread.service_account('G:\DS\Secrets\service_account.json')
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

#%%
from espn_api.basketball import League
from espn_api.basketball import Matchup
from espn_api.basketball import Team
from espn_api.basketball.box_score import H2HCategoryBoxScore


def uploadLast7Table(roster, sheet, rangeName, statPeriod, statType):
    playersList = []
    relevantStats = ['FG%','FT%','AST','BLK','STL','REB','PTS','GP','GS','MIN','MPG','OREB','PF','TO','DREB','FGA','FGM','FTA','FTM']
    header = ['Full Name']
    header.extend(relevantStats)
    playersList.append(header)
    for player in roster:
        playerList = []
        playerList.append(player.name)
        periodStats = player.stats[statPeriod][statType]
        for stat in relevantStats:
            playerList.append(periodStats[stat])
        playersList.append(playerList)
    sheet.update(values=playersList, range_name=rangeName)

def uploadCurrentMatchup(matchUp: Matchup, sheet, rangeName: string):    
    relevantStats = ['3PTM','AST','BLK','FG%','FT%','PTS','REB','STL']
    matchUpList = []
    header = ['Team']
    header.extend(relevantStats)
    matchUpList.append(header)
    homeTeam = []
    awayTeam = []    
    awayTeam.append(matchUp.away_team.team_name)
    homeTeam.append(matchUp.home_team.team_name)
    for stat in relevantStats:
        awayTeam.append(matchUp.away_team_cats[stat]['score'])
        homeTeam.append(matchUp.home_team_cats[stat]['score'])
    
    if matchUp.away_team.team_name == 'Hundisabad PP':
        myTeam = awayTeam
        evilTeam = homeTeam
    else:
        myTeam = homeTeam
        evilTeam = awayTeam        
    
    matchUpList.append(myTeam)
    matchUpList.append(evilTeam)
    sheet.update(values=matchUpList, range_name=rangeName)

def getMyMatchUpBoxScores(boxScores: H2HCategoryBoxScore):
    for boxScore in boxScores:
        if boxScore.away_team.team_name == 'Hundisabad PP' or boxScore.home_team.team_name == 'Hundisabad PP':
            myMatchUp = boxScore
            break
    return myMatchUp    


def uploadBoxScores(myLeague: League, sheet):
    boxScores = myLeague.box_scores(matchup_total=True)
    relevantStats = ['3PTM','AST','BLK','FG%','FT%','PTS','REB','STL','FGM', 'FGA','FTM', 'FTA', 'GP']
    header = ['Full Name']
    header.extend(relevantStats)
    boxScoresList = []
    myMatchUp = getMyMatchUpBoxScores(boxScores)    
    boxScoresList.append([myMatchUp.home_team.team_name])
    boxScoresList.append(header)
    for playerBoxScore in myMatchUp.home_lineup:
        playerList = [playerBoxScore.name]
        for stat in relevantStats:
            playerList.append(playerBoxScore.points_breakdown[stat])
        boxScoresList.append(playerList)
    boxScoresList.append([
        "", '=SUM(B2:B18)'
        ])
    boxScoresList.append([myMatchUp.away_team.team_name])
    boxScoresList.append(header)
    for playerBoxScore in myMatchUp.away_lineup:
        playerList = [playerBoxScore.name]
        for stat in relevantStats:
            playerList.append(playerBoxScore.points_breakdown[stat])
        boxScoresList.append(playerList)
    boxScoresList.append([
        "", "=SUM(B2:B18)"
        ])
    sheet.update(values=boxScoresList, range_name='A1')

def uploadLastWeekStats(week):
    relevantStats = ['3PTM','AST','BLK','FG%','FT%','PTS','REB','STL','FGM','FGA' ,'FTM', 'FTA']
    header = ['Team name']
    header.extend(relevantStats)
    boxScores = myLeague.box_scores(week)
    weekScoreList = [header]
    for matchUpScores in boxScores:
        teamScoreList = [matchUpScores.home_team.team_name]
        for stat in relevantStats:
            teamScoreList.append(matchUpScores.home_stats[stat]['value'])
        weekScoreList.append(teamScoreList)
        teamScoreList = [matchUpScores.away_team.team_name]
        for stat in relevantStats:
            teamScoreList.append(matchUpScores.away_stats[stat]['value'])
        weekScoreList.append(teamScoreList)
    spreadsheet.worksheet("WeeklySummary").update(values=weekScoreList, range_name = "A1")

def uploadLastWeekRankings(week):
    relevantStats = ['3PTM','AST','BLK','FG%','FT%','PTS','REB','STL','FGM','FGA' ,'FTM', 'FTA']
    teamStats = {}
    boxScores = myLeague.box_scores(week)
    for matchUpScores in boxScores:
        for stat in relevantStats:
            if stat not in teamStats:
                teamStats[stat] = {}
            teamStats[stat][matchUpScores.home_team.team_name] = matchUpScores.home_stats[stat]['value']
            teamStats[stat][matchUpScores.away_team.team_name] = matchUpScores.away_stats[stat]['value']

    row = 14
    i=0
    for stat, teamValues in teamStats.items():       
       sortedValues = sorted(teamValues.items(), key=lambda x: (x[1], x[0]), reverse=True)
       itemList = [[stat]]         
       for teamValue in sortedValues:
           itemList.append(teamValue)
       spreadsheet.worksheet("WeeklySummary").update(values=itemList, range_name = gspread.utils.rowcol_to_a1(row, (i*2)+1))
       i=i+1

def sumBoxScores(lineup):
    relevantStats = ['3PTM','AST','BLK','FG%','FT%','PTS','REB','STL','FGM', 'FGA','FTM', 'FTA', 'GP']
    boxScores = {}
    for playerBoxScore in lineup:
        for stat in relevantStats:
            boxScores[stat] = (boxScores.get(stat) or 0) + playerBoxScore.points_breakdown[stat]
    boxScores['FG%'] = boxScores['FGM']/boxScores['FGA'] if boxScores.get('FGM') else 0
    boxScores['FT%'] = boxScores['FTM']/boxScores['FTA'] if boxScores.get('FTM') else 0
    return boxScores

def getBoxScoreTotals(myLeague: League):
    boxScores = myLeague.box_scores(matchup_total=True)
    myMatchUp = getMyMatchUpBoxScores(boxScores)
    homeScores = sumBoxScores(myMatchUp.home_lineup)
    awayScores = sumBoxScores(myMatchUp.away_lineup)
    boxScores = {
        'My Scores':  homeScores if myMatchUp.home_team.team_name == 'Hundisabad PP' else awayScores,
        'Evil Scores': awayScores if myMatchUp.home_team.team_name == 'Hundisabad PP' else homeScores
    }
    return boxScores

def uploadRosterProjections(
        team: Team, 
        range_name: str, 
        stat_type: str, 
        injury_list: dict, 
        matchup_start_time: datetime, 
        matchup_end_time: datetime, 
        sheet_name: str
        ):
    projectedList = []
    teamProjected = {}
    for player in team.roster:
        playerGames = 0
        projectedStats = {}
        for index, game in player.schedule.items():
            if game['date'] > matchup_start_time and game['date'] < matchup_end_time:
                playerGames=playerGames+1            
        injuryGames = injury_list.get(player.name) if injury_list.get(player.name) else 0
        playerGames = max(0, playerGames - injuryGames)                 
        print(player.name + ": " + str(playerGames))
        if stat_type in player.stats and 'avg' in player.stats[stat_type]:            
            stats = player.stats[stat_type]['avg']
            for stat in getProjectionStats():
                projectedStats[stat] = stats[stat]*playerGames
            projectedStats['FT%'] = projectedStats['FTM']/projectedStats['FTA'] if projectedStats['FTA'] > 0 else 0
            projectedStats['FG%'] = projectedStats['FGM']/projectedStats['FGA'] if projectedStats['FGA'] > 0 else 0
            teamProjected[player.name] = projectedStats
    header = ['Full Name']
    header.extend(getProjectionStats())
    projectedList.append(header)
    for playerName, stats in teamProjected.items():
        playerList = [playerName]
        for stat in getProjectionStats():
            playerList.append(stats[stat])
        projectedList.append(playerList)
    spreadsheet.worksheet(sheet_name).update(values=projectedList, range_name = range_name)

def getProjectionStats():
    return ['3PTM','AST','BLK','FG%','FT%','PTS','REB','STL','FGM','FGA' ,'FTM', 'FTA']
    
def uploadProjections(league: League, matchUp: Matchup, statType: string, endTime: string, sheetName: string, injuryList, start_time = datetime.now()):
    
    if matchUp.away_team.team_name == 'Hundisabad PP':
        myTeam = matchUp.away_team
        evilTeam = matchUp.home_team
    else:
        myTeam = matchUp.home_team
        evilTeam = matchUp.away_team 
    
    matchUpStartTime = start_time if start_time else datetime.now()
    matchUpEndTime = datetime.strptime(endTime, '%Y-%m-%d %H:%M:%S')
    uploadRosterProjections(myTeam, "A1", statType, injuryList, matchUpStartTime, matchUpEndTime, sheetName)
    uploadRosterProjections(evilTeam, "A18", statType, injuryList, matchUpStartTime, matchUpEndTime, sheetName)
    myTeamBoxScoreList = ['My Scores'];
    evilTeamBoxScoreList = ['Evil Scores'];
    boxScoreTotals = getBoxScoreTotals(myLeague)    
    for stat in getProjectionStats():
        myTeamBoxScoreList.append(boxScoreTotals['My Scores'][stat] if boxScoreTotals['My Scores'].get(stat) else 0)
        evilTeamBoxScoreList.append(boxScoreTotals['Evil Scores'][stat] if boxScoreTotals['Evil Scores'].get(stat) else 0)
    spreadsheet.worksheet(sheetName).update(values=[myTeamBoxScoreList], range_name = "A36")
    spreadsheet.worksheet(sheetName).update(values=[evilTeamBoxScoreList], range_name = "A37")   

def uploadWeekLeague(week: int):
    relevantStats = ['3PTM','AST','BLK','FG%','FT%','PTS','REB','STL']
    boxScores = myLeague.box_scores(week)
    weekScores = {}
    for matchUpScores in boxScores:
        weekScores[matchUpScores.home_team.team_name] = {}
        for stat in relevantStats:
            weekScores[matchUpScores.home_team.team_name][stat] = matchUpScores.home_stats[stat]['value']
        weekScores[matchUpScores.away_team.team_name] = {}
        for stat in relevantStats:
            weekScores[matchUpScores.away_team.team_name][stat] = matchUpScores.away_stats[stat]['value']
    results = {}        
    weekScores_o = weekScores        
    for team, t_stats in weekScores.items():
        results[team] = {}
        for o_team, o_stats in weekScores_o.items():        
            results[team][o_team] = {'wins':0, 'losses':0, 'draws': 0}
            for stat in relevantStats:
                if t_stats[stat] > o_stats[stat]:
                    results[team][o_team]['wins'] += 1
                elif t_stats[stat] < o_stats[stat]:
                    results[team][o_team]['losses'] += 1
                else:
                    results[team][o_team]['draws'] += 1
    resultsList = []
    header = [" "]                
    header.extend(list(results.keys()))
    header.extend(["wins", "losses", "draws"])
    resultsList.append(header)
    for team, t_results in results.items():
        totals = {'wins':0, 'losses':0, 'draws': 0}
        teamList = [team]
        for o_team, balance in t_results.items():
            totals['wins'] += balance['wins']
            totals['losses'] += balance['losses']
            totals['draws'] += balance['draws']
            teamList.append(str(balance['wins']) + "-" + str(balance['losses']) + "-" + str(balance['draws']))
        teamList.extend([totals['wins'],totals['losses'],totals['draws'] - 8])
        resultsList.append(teamList)
    spreadsheet.worksheet("WeekLeague_" + str(week)).update(values=resultsList, range_name = "A1")    

myLeague = League(league_id=1484695785, year=2024)
currentMatchupPeriod = myLeague.currentMatchupPeriod
scoreboard = myLeague.scoreboard(currentMatchupPeriod)
myTeam = myLeague.get_team_data(4)
roster = myTeam.roster
spreadsheet = gc.open('Fantasy_BBall')
#uploadLast7Table(roster, spreadsheet.sheet1, 'Last_7', '2024_last_7', 'avg')
#uploadCurrentMatchup(myTeam.schedule[4], spreadsheet.sheet1, 'Matchup_current')
uploadBoxScores(myLeague, spreadsheet.worksheet('BoxScores'))
#%%
uploadProjections(myLeague, myTeam.schedule[8], '2024_last_15', '2023-12-25 12:00:00', "Projected", {
    "Cameron Johnson": 1,
    "Sadiq Bay": 1,
    "Bojan Bogdanovic": 1,
    "LeBron James": 9,
    "James Harden": 9,
    "Fred VanVleet": 9,
    "Zion Williamson": 2    
    })
#%%
#uploadProjections(myLeague, myTeam.schedule[8], '2024_last_15', '2023-12-25 12:00:00', "ProjectedNextWeek", {
#    "Dereck Lively II": 1,
#    "Cameron Johnson": 1,
#    "Tim Hardaway Jr": 1
#    }, datetime.strptime('2023-12-18 12:00:00', '%Y-%m-%d %H:%M:%S'))
#%%
#uploadLastWeekStats(8)
#uploadLastWeekRankings(8)
#uploadWeekLeague(8)
#%%
