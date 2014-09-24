import nfldb

def rush_pass_breakdown(db, q, team):
    """view the run/pass breakdown for drives as a function of score differential at the beginning of the drive"""
    # first grab all the team's games from the given query
    games = nfldb.QueryOR(db).game(home_team=team, away_team=team)
    q.andalso(games)
    drives = [ (d.gsis_id, d.drive_id) for d in q.as_drives() if d.pos_team == team ]
     
    # now separate drives by score differential
    score_diff_drives = {}
    for gsis_id, drive_id in drives:
        q = nfldb.Query(db).game(gsis_id=gsis_id).drive(drive_id__lt=drive_id).drive(pos_team=team).play(points__ge=0)
        team_score = sum(p.points for p in q.as_plays())
        q = nfldb.Query(db).game(gsis_id=gsis_id).drive(drive_id__lt=drive_id).drive(pos_team__ne=team).play(points__ge=0)
        opp_score = sum(p.points for p in q.as_plays())
        
        score_diff = team_score - opp_score
        if score_diff not in score_diff_drives:
            score_diff_drives[score_diff] = [(gsis_id, drive_id)]
        else:
            score_diff_drives[score_diff].append((gsis_id, drive_id))

    # now look at all plays for each drive and see the run/pass breakdown
    passing = {}
    rushing = {}
     
    for score_diff, drives in score_diff_drives.iteritems():
        for gsis_id, drive_id in drives:
            pass_att = len(nfldb.Query(db).game(gsis_id=gsis_id).drive(drive_id=drive_id).play_player(passing_att=1).as_plays())
            rush_att = len(nfldb.Query(db).game(gsis_id=gsis_id).drive(drive_id=drive_id).play_player(rushing_att=1).as_plays())
            if score_diff not in passing:
                passing[score_diff] = pass_att
            else:
                passing[score_diff] += pass_att
            if score_diff not in rushing:
                rushing[score_diff] = rush_att
            else:
                rushing[score_diff] += rush_att
     
    rushing_pct = {}
    passing_pct = {}
    for score_diff in score_diff_drives:
        rush_att = rushing[score_diff] if score_diff in rushing else 0
        pass_att = passing[score_diff] if score_diff in passing else 0
        total = rush_att + pass_att
        rushing_pct[score_diff] = rush_att * 100. / total
        passing_pct[score_diff] = pass_att * 100. / total
    
    return passing, rushing, passing_pct, rushing_pct
