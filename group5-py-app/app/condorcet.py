from collections import defaultdict

def condorcet_winner(rankings, candidates):
    """
    rankings: list of lists, each sublist is a ranking e.g. [3,1,2]
    candidates: list of candidate ids
    Returns pairwise matrix and winner id (or None)
    """
    wins = {a: {b:0 for b in candidates if b!=a} for a in candidates}
    for r in rankings:
        for i, a in enumerate(r):
            for b in r[i+1:]:
                wins[a][b] += 1

    for a in candidates:
        beats_all = True
        for b in candidates:
            if a==b: continue
            if wins[a].get(b,0) <= wins[b].get(a,0):
                beats_all = False
                break
        if beats_all:
            return a, wins
    return None, wins
