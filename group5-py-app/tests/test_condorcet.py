from app.condorcet import condorcet_winner

def test_simple_condorcet():
    rankings = [
        [1,2,3],
        [1,3,2],
        [2,1,3]
    ]
    winner, matrix = condorcet_winner(rankings, [1,2,3])
    assert winner == 1
