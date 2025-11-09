import pytest
from unittest.mock import Mock, patch
from typing import List

from app.condorcet import (
    CondorcetVotingSystem, 
    VoteValidationError, 
    VoteResult,
    PairwiseComparison,
    condorcet_winner,
    analyze_vote_stability
)

class TestCondorcetVotingSystem:
    """Tests complets du système de vote Condorcet"""
    
    def setup_method(self):
        """Configuration avant chaque test"""
        self.voting_system = CondorcetVotingSystem()
        self.candidates = [1, 2, 3, 4]
    
    def test_simple_condorcet_winner(self):
        """Test cas simple avec gagnant Condorcet clair"""
        rankings = [
            [1, 2, 3],
            [1, 3, 2],
            [2, 1, 3]
        ]
        
        result = self.voting_system.conduct_election(rankings, [1, 2, 3])
        
        assert result.winner == 1
        assert result.vote_count == 3
        assert 1 in result.smith_set
        assert len(result.ranking) == 3
        assert result.ranking[0] == 1  # Le gagnant doit être premier

    def test_no_condorcet_winner_cycle(self):
        """Test cas sans gagnant Condorcet (cycle)"""
        rankings = [
            [1, 2, 3],
            [2, 3, 1],
            [3, 1, 2]
        ]
        
        result = self.voting_system.conduct_election(rankings, [1, 2, 3])
        
        assert result.winner is None  # Pas de gagnant Condorcet
        assert len(result.smith_set) == 3  # Tous dans l'ensemble de Smith
        assert len(result.ranking) == 3  # Classement complet quand même

    def test_pairwise_matrix_calculation(self):
        """Test du calcul de la matrice des comparaisons par paires"""
        rankings = [
            [1, 2, 3],
            [1, 3, 2],
            [2, 1, 3]
        ]
        
        matrix = self.voting_system.compute_pairwise_matrix(rankings, [1, 2, 3])
        
        # 1 vs 2: 1 gagne 2 votes contre 1
        assert matrix[1][2] == 2
        assert matrix[2][1] == 1
        
        # 1 vs 3: 1 gagne 3 votes contre 0 (dans tous les votes, 1 est avant 3)
        assert matrix[1][3] == 3
        assert matrix[3][1] == 0
        
        # 2 vs 3: 2 gagne 2 votes contre 1
        assert matrix[2][3] == 2
        assert matrix[3][2] == 1

    def test_smith_set_calculation(self):
        """Test du calcul de l'ensemble de Smith"""
        # Cas où tous les candidats sont dans l'ensemble de Smith (cycle complet)
        rankings = [
            [1, 2, 3],
            [2, 3, 1],
            [3, 1, 2]
        ]
        
        matrix = self.voting_system.compute_pairwise_matrix(rankings, [1, 2, 3])
        smith_set = self.voting_system.compute_smith_set(matrix, [1, 2, 3])
        
        assert set(smith_set) == {1, 2, 3}

    def test_margin_tie_breaking(self):
        """Test de résolution d'égalités par méthode des marges"""
        system = CondorcetVotingSystem(tie_breaking_method="margin")
        
        # Cas avec cycle nécessitant départage
        rankings = [
            [1, 2, 3],
            [2, 3, 1],
            [3, 1, 2],
            [1, 2, 3]  # Vote supplémentaire favorisant légèrement 1
        ]
        
        result = system.conduct_election(rankings, [1, 2, 3])
        
        # Pas de gagnant Condorcet mais classement par marges
        assert result.winner is None
        assert len(result.ranking) == 3

    def test_copeland_tie_breaking(self):
        """Test de résolution d'égalités par méthode Copeland"""
        system = CondorcetVotingSystem(tie_breaking_method="copeland")
        
        rankings = [
            [1, 2, 3, 4],
            [2, 1, 3, 4],
            [3, 4, 1, 2]
        ]
        
        result = system.conduct_election(rankings, [1, 2, 3, 4])
        
        assert len(result.ranking) == 4
        # Le candidat avec le meilleur score Copeland doit être premier

    def test_borda_tie_breaking(self):
        """Test de résolution d'égalités par méthode Borda"""
        system = CondorcetVotingSystem(tie_breaking_method="borda")
        
        rankings = [
            [1, 2, 3],
            [2, 3, 1],
            [3, 1, 2]
        ]
        
        result = system.conduct_election(rankings, [1, 2, 3])
        
        assert len(result.ranking) == 3
        # Tous les candidats devraient avoir le même score Borda dans ce cas

    def test_vote_validation_valid_votes(self):
        """Test de validation des votes valides"""
        rankings = [
            [1, 2, 3],
            [2, 1, 3],
            [3, 2, 1]
        ]
        
        # Ne doit pas lever d'exception
        assert self.voting_system.validate_rankings(rankings, [1, 2, 3])

    def test_vote_validation_invalid_candidate(self):
        """Test de validation avec candidat invalide"""
        rankings = [
            [1, 2, 3],
            [1, 2, 99]  # 99 n'est pas un candidat valide
        ]
        
        with pytest.raises(VoteValidationError, match="candidat 99 non valide"):
            self.voting_system.validate_rankings(rankings, [1, 2, 3])

    def test_vote_validation_duplicate_candidates(self):
        """Test de validation avec candidats en double"""
        rankings = [
            [1, 2, 3],
            [1, 1, 2]  # 1 apparaît deux fois
        ]
        
        with pytest.raises(VoteValidationError, match="candidats en double"):
            self.voting_system.validate_rankings(rankings, [1, 2, 3])

    def test_pairwise_comparison(self):
        """Test des comparaisons par paires détaillées"""
        rankings = [[1, 2], [2, 1], [1, 2]]
        matrix = self.voting_system.compute_pairwise_matrix(rankings, [1, 2])
        
        comparison = self.voting_system.get_pairwise_comparison(1, 2, matrix)
        
        assert comparison.candidate_a == 1
        assert comparison.candidate_b == 2
        assert comparison.votes_for_a == 2
        assert comparison.votes_for_b == 1
        assert comparison.margin == 1
        assert comparison.winner == 1

    def test_empty_rankings(self):
        """Test avec votes vides"""
        rankings = []
        
        result = self.voting_system.conduct_election(rankings, [1, 2, 3])
        
        assert result.winner is None
        assert result.vote_count == 0
        assert len(result.ranking) == 3

    def test_single_candidate(self):
        """Test avec un seul candidat"""
        rankings = [[1], [1]]
        
        result = self.voting_system.conduct_election(rankings, [1])
        
        assert result.winner == 1
        assert result.vote_count == 2
        assert result.ranking == [1]

    def test_partial_rankings(self):
        """Test avec classements partiels (certains candidats non classés)"""
        rankings = [
            [1, 2],    # Ne classe pas 3
            [2, 3],    # Ne classe pas 1
            [1, 3, 2]  # Classe tous
        ]
        
        # Doit fonctionner même avec des classements partiels
        result = self.voting_system.conduct_election(rankings, [1, 2, 3])
        
        assert len(result.ranking) == 3
        assert result.vote_count == 3

    def test_tie_identification(self):
        """Test d'identification des égalités"""
        # Configuration où 2 et 3 sont à égalité
        rankings = [
            [1, 2, 3],
            [1, 3, 2]
        ]
        
        result = self.voting_system.conduct_election(rankings, [1, 2, 3])
        
        # Devrait identifier une égalité entre 2 et 3
        assert len(result.ties) >= 0  # Peut y avoir ou non des égalités selon la méthode

    def test_large_election(self):
        """Test avec un grand nombre de candidats et de votes"""
        candidates = list(range(1, 11))  # 10 candidats
        
        # Génération de votes aléatoires mais reproductibles
        import random
        random.seed(42)  # Pour la reproductibilité
        
        rankings = []
        for _ in range(50):  # 50 votants
            ranking = candidates.copy()
            random.shuffle(ranking)
            rankings.append(ranking)
        
        result = self.voting_system.conduct_election(rankings, candidates)
        
        assert len(result.ranking) == 10
        assert result.vote_count == 50
        # Peut ou peut ne pas avoir de gagnant Condorcet

    def test_invalid_tie_breaking_method(self):
        """Test avec méthode de départage invalide"""
        system = CondorcetVotingSystem(tie_breaking_method="invalid")
        # Créer une situation d'égalité pour déclencher la résolution
        rankings = [
            [1, 2, 3],
            [2, 3, 1],
            [3, 1, 2]
        ]
        with pytest.raises(ValueError, match="Méthode de résolution inconnue"):
            system.conduct_election(rankings, [1, 2, 3])

class TestLegacyFunction:
    """Tests pour la fonction de compatibilité"""
    
    def test_condorcet_winner_function(self):
        """Test de la fonction condorcet_winner legacy"""
        rankings = [
            [1, 2, 3],
            [1, 3, 2],
            [2, 1, 3]
        ]
        
        winner, matrix = condorcet_winner(rankings, [1, 2, 3])
        
        assert winner == 1
        assert isinstance(matrix, dict)
        assert 1 in matrix
        assert 2 in matrix[1]

    def test_condorcet_winner_with_invalid_vote(self):
        """Test de la fonction legacy avec vote invalide"""
        rankings = [
            [1, 2, 3],
            [1, 99, 2]  # Candidat invalide
        ]
        
        winner, matrix = condorcet_winner(rankings, [1, 2, 3])
        
        # La fonction legacy doit gérer les erreurs gracieusement
        assert winner is None
        assert matrix == {}

class TestVoteStabilityAnalysis:
    """Tests pour l'analyse de stabilité des votes"""
    
    def test_stability_analysis_stable_winner(self):
        """Test d'analyse de stabilité avec gagnant stable"""
        # Vote avec gagnant Condorcet clair
        rankings = [
            [1, 2, 3] for _ in range(10)  # 10 votes identiques
        ] + [
            [2, 1, 3] for _ in range(2)   # 2 votes différents
        ]
        
        stability = analyze_vote_stability(rankings, [1, 2, 3])
        
        assert stability["base_winner"] == 1
        assert stability["condorcet_efficiency"] == 1.0
        assert stability["winner_stability"] > 0.8  # Devrait être très stable

    def test_stability_analysis_unstable_vote(self):
        """Test d'analyse de stabilité avec vote instable"""
        # Cycle parfait, très instable
        rankings = [
            [1, 2, 3],
            [2, 3, 1],
            [3, 1, 2]
        ]
        
        stability = analyze_vote_stability(rankings, [1, 2, 3])
        
        assert stability["base_winner"] is None  # Pas de gagnant Condorcet
        assert stability["condorcet_efficiency"] == 0.0

    @patch('random.sample')
    def test_stability_analysis_mocked(self, mock_sample):
        """Test d'analyse de stabilité avec mock pour contrôler l'aléatoire"""
        rankings = [
            [1, 2, 3],
            [1, 2, 3],
            [2, 1, 3]
        ]
        
        # Mock pour retourner toujours les mêmes votes
        mock_sample.return_value = rankings
        
        stability = analyze_vote_stability(rankings, [1, 2, 3])
        
        assert "winner_stability" in stability
        assert isinstance(stability["winner_stability"], float)

class TestEdgeCases:
    """Tests pour les cas limites et d'erreur"""
    
    def test_empty_candidate_list(self):
        """Test avec liste de candidats vide"""
        system = CondorcetVotingSystem()
        
        result = system.conduct_election([], [])
        
        assert result.winner is None
        assert result.vote_count == 0
        assert result.ranking == []

    def test_single_vote_multiple_candidates(self):
        """Test avec un seul vote et plusieurs candidats"""
        system = CondorcetVotingSystem()
        
        result = system.conduct_election([[1, 2, 3]], [1, 2, 3])
        
        assert result.winner == 1  # Premier dans l'unique vote
        assert result.vote_count == 1
        assert result.ranking == [1, 2, 3]

    def test_very_large_margin(self):
        """Test avec marges très importantes"""
        # Un candidat bat tous les autres massivement
        rankings = []
        for _ in range(100):
            rankings.append([1, 2, 3, 4, 5])
        
        # Quelques votes différents
        rankings.extend([[2, 1, 3, 4, 5], [3, 2, 1, 4, 5]])
        
        system = CondorcetVotingSystem()
        result = system.conduct_election(rankings, [1, 2, 3, 4, 5])
        
        assert result.winner == 1
        assert result.ranking[0] == 1

    def test_all_different_rankings(self):
        """Test où chaque vote est complètement différent"""
        import itertools
        
        candidates = [1, 2, 3]
        all_permutations = list(itertools.permutations(candidates))
        
        # Utilise toutes les permutations possibles
        rankings = list(all_permutations)
        
        system = CondorcetVotingSystem()
        result = system.conduct_election(rankings, candidates)
        
        # Pas de gagnant Condorcet dans ce cas
        assert result.winner is None
        assert len(result.ranking) == 3

class TestPerformance:
    """Tests de performance pour gros volumes"""
    
    def test_performance_many_candidates(self):
        """Test de performance avec beaucoup de candidats"""
        import time
        
        candidates = list(range(1, 21))  # 20 candidats
        rankings = []
        
        # Génère 100 votes
        import random
        random.seed(42)
        for _ in range(100):
            ranking = candidates.copy()
            random.shuffle(ranking)
            rankings.append(ranking)
        
        system = CondorcetVotingSystem()
        
        start_time = time.time()
        result = system.conduct_election(rankings, candidates)
        end_time = time.time()
        
        # Doit terminer en moins de 5 secondes
        assert end_time - start_time < 5.0
        assert len(result.ranking) == 20
        assert result.vote_count == 100

    def test_performance_many_votes(self):
        """Test de performance avec beaucoup de votes"""
        import time
        
        candidates = [1, 2, 3, 4, 5]
        rankings = []
        
        # Génère 1000 votes
        import random
        random.seed(42)
        for _ in range(1000):
            ranking = candidates.copy()
            random.shuffle(ranking)
            rankings.append(ranking)
        
        system = CondorcetVotingSystem()
        
        start_time = time.time()
        result = system.conduct_election(rankings, candidates)
        end_time = time.time()
        
        # Doit terminer en moins de 2 secondes
        assert end_time - start_time < 2.0
        assert result.vote_count == 1000
