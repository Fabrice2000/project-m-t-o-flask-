from collections import defaultdict, Counter
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class VoteValidationError(Exception):
    """Exception levée en cas d'erreur de validation d'un vote"""
    pass

@dataclass
class VoteResult:
    """Résultat d'un vote Condorcet"""
    winner: Optional[int]  # ID du gagnant Condorcet, None si pas de gagnant
    pairwise_matrix: Dict[int, Dict[int, int]]  # Matrice des comparaisons par paires
    vote_count: int  # Nombre total de votes
    candidates: List[int]  # Liste des candidats
    smith_set: List[int]  # Ensemble de Smith (plus petit ensemble de candidats qui battent tous les autres)
    ranking: List[int]  # Classement final (par ordre de préférence)
    ties: List[List[int]]  # Groupes de candidats à égalité
    margin_matrix: Dict[int, Dict[int, int]]  # Matrice des marges de victoire

@dataclass
class PairwiseComparison:
    """Comparaison entre deux candidats"""
    candidate_a: int
    candidate_b: int
    votes_for_a: int
    votes_for_b: int
    margin: int  # votes_for_a - votes_for_b
    
    @property
    def winner(self) -> Optional[int]:
        if self.votes_for_a > self.votes_for_b:
            return self.candidate_a
        elif self.votes_for_b > self.votes_for_a:
            return self.candidate_b
        return None

class CondorcetVotingSystem:
    """
    Système de vote par la méthode Condorcet avec plusieurs algorithmes de résolution
    
    Implémente :
    - Vérification de gagnant Condorcet
    - Calcul de l'ensemble de Smith
    - Résolution des cycles par différentes méthodes
    - Validation des votes
    """
    
    def __init__(self, tie_breaking_method: str = "margin"):
        """
        Initialise le système de vote Condorcet
        
        Args:
            tie_breaking_method: Méthode de résolution des égalités
                - "margin": par marge de victoire
                - "copeland": score de Copeland
                - "borda": décompte Borda modifié
        """
        self.tie_breaking_method = tie_breaking_method
    
    def validate_rankings(self, rankings: List[List[int]], candidates: List[int]) -> bool:
        """
        Valide que les classements sont cohérents
        
        Args:
            rankings: Liste des classements de chaque votant
            candidates: Liste des candidats valides
            
        Returns:
            True si tous les votes sont valides
            
        Raises:
            VoteValidationError: Si un vote est invalide
        """
        candidate_set = set(candidates)
        
        for i, ranking in enumerate(rankings):
            # Vérifie que le classement ne contient que des candidats valides
            for candidate in ranking:
                if candidate not in candidate_set:
                    raise VoteValidationError(
                        f"Vote {i}: candidat {candidate} non valide. "
                        f"Candidats autorisés: {candidates}"
                    )
            
            # Vérifie qu'il n'y a pas de doublons dans le classement
            if len(ranking) != len(set(ranking)):
                duplicates = [x for x in ranking if ranking.count(x) > 1]
                raise VoteValidationError(
                    f"Vote {i}: candidats en double: {duplicates}"
                )
            
            # Optionnel : vérifie que tous les candidats sont classés
            # (permet les votes partiels si cette vérification est omise)
            # if set(ranking) != candidate_set:
            #     missing = candidate_set - set(ranking)
            #     raise VoteValidationError(f"Vote {i}: candidats manquants: {missing}")
        
        return True
    
    def compute_pairwise_matrix(self, rankings: List[List[int]], candidates: List[int]) -> Dict[int, Dict[int, int]]:
        """
        Calcule la matrice des comparaisons par paires
        
        Args:
            rankings: Liste des classements individuels
            candidates: Liste des candidats
            
        Returns:
            Matrice où matrix[a][b] = nombre de votes préférant a à b
        """
        # Initialise la matrice
        matrix = {a: {b: 0 for b in candidates if b != a} for a in candidates}
        
        for ranking in rankings:
            # Pour chaque paire de candidats dans ce vote
            for i, candidate_a in enumerate(ranking):
                # Vérifier que candidate_a est dans la liste des candidats
                if candidate_a not in candidates:
                    continue
                    
                for candidate_b in ranking[i + 1:]:
                    # Vérifier que candidate_b est dans la liste des candidats
                    if candidate_b not in candidates:
                        continue
                        
                    # candidate_a est préféré à candidate_b
                    if candidate_a in matrix and candidate_b in matrix[candidate_a]:
                        matrix[candidate_a][candidate_b] += 1
        
        return matrix
    
    def find_condorcet_winner(self, pairwise_matrix: Dict[int, Dict[int, int]], 
                            candidates: List[int]) -> Optional[int]:
        """
        Trouve le gagnant Condorcet s'il existe
        
        Un gagnant Condorcet bat tous les autres candidats en comparaison directe
        
        Args:
            pairwise_matrix: Matrice des comparaisons par paires
            candidates: Liste des candidats
            
        Returns:
            ID du gagnant Condorcet ou None s'il n'y en a pas
        """
        for candidate in candidates:
            is_condorcet_winner = True
            
            for opponent in candidates:
                if candidate == opponent:
                    continue
                
                # Vérifie si ce candidat bat l'opposant
                votes_for = pairwise_matrix[candidate].get(opponent, 0)
                votes_against = pairwise_matrix[opponent].get(candidate, 0)
                
                if votes_for <= votes_against:
                    is_condorcet_winner = False
                    break
            
            if is_condorcet_winner:
                logger.info(f"Gagnant Condorcet trouvé: candidat {candidate}")
                return candidate
        
        logger.info("Aucun gagnant Condorcet trouvé (paradoxe de Condorcet)")
        return None
    
    def compute_smith_set(self, pairwise_matrix: Dict[int, Dict[int, int]], 
                         candidates: List[int]) -> List[int]:
        """
        Calcule l'ensemble de Smith
        
        L'ensemble de Smith est le plus petit ensemble de candidats tel que
        chaque candidat de l'ensemble bat chaque candidat hors de l'ensemble
        
        Args:
            pairwise_matrix: Matrice des comparaisons par paires
            candidates: Liste des candidats
            
        Returns:
            Liste des candidats dans l'ensemble de Smith
        """
        def beats(a: int, b: int) -> bool:
            """Vérifie si le candidat a bat le candidat b"""
            votes_a = pairwise_matrix[a].get(b, 0)
            votes_b = pairwise_matrix[b].get(a, 0)
            return votes_a > votes_b
        
        def beats_all_outside(subset: Set[int], remaining: Set[int]) -> bool:
            """Vérifie si tous les candidats du subset battent tous ceux de remaining"""
            for inside in subset:
                for outside in remaining:
                    if not beats(inside, outside):
                        return False
            return True
        
        # Commence avec tous les candidats
        current_set = set(candidates)
        
        while True:
            # Trouve les candidats qui sont battus par au moins un candidat de l'ensemble
            to_remove = set()
            
            for candidate in current_set:
                remaining = current_set - {candidate}
                if remaining and beats_all_outside(remaining, {candidate}):
                    to_remove.add(candidate)
            
            if not to_remove:
                break
            
            current_set -= to_remove
        
        smith_set = list(current_set)
        logger.info(f"Ensemble de Smith: {smith_set}")
        return smith_set
    
    def compute_margin_matrix(self, pairwise_matrix: Dict[int, Dict[int, int]], 
                            candidates: List[int]) -> Dict[int, Dict[int, int]]:
        """
        Calcule la matrice des marges de victoire
        
        Args:
            pairwise_matrix: Matrice des comparaisons par paires
            candidates: Liste des candidats
            
        Returns:
            Matrice où margin[a][b] = votes_for_a - votes_for_b
        """
        margin_matrix = {}
        
        for a in candidates:
            margin_matrix[a] = {}
            for b in candidates:
                if a != b:
                    votes_a = pairwise_matrix[a].get(b, 0)
                    votes_b = pairwise_matrix[b].get(a, 0)
                    margin_matrix[a][b] = votes_a - votes_b
        
        return margin_matrix
    
    def resolve_ties_by_margin(self, candidates: List[int], 
                              margin_matrix: Dict[int, Dict[int, int]]) -> List[int]:
        """
        Résout les égalités en utilisant la méthode des marges (Minimax)
        
        Args:
            candidates: Candidats à départager
            margin_matrix: Matrice des marges
            
        Returns:
            Classement ordonné des candidats
        """
        scores = {}
        
        for candidate in candidates:
            # Score Minimax : la plus grande marge négative contre ce candidat
            worst_margin = 0
            for opponent in candidates:
                if candidate != opponent:
                    margin = margin_matrix[candidate][opponent]
                    if margin < worst_margin:
                        worst_margin = margin
            
            scores[candidate] = -worst_margin  # Plus c'est grand, mieux c'est
        
        # Trie par score décroissant
        ranked = sorted(candidates, key=lambda c: scores[c], reverse=True)
        
        logger.info(f"Classement par méthode des marges: {ranked}")
        return ranked
    
    def resolve_ties_by_copeland(self, candidates: List[int], 
                                pairwise_matrix: Dict[int, Dict[int, int]]) -> List[int]:
        """
        Résout les égalités par la méthode Copeland
        
        Score Copeland = nombre de victoires - nombre de défaites
        
        Args:
            candidates: Candidats à départager
            pairwise_matrix: Matrice des comparaisons
            
        Returns:
            Classement ordonné des candidats
        """
        scores = {}
        
        for candidate in candidates:
            wins = 0
            losses = 0
            
            for opponent in candidates:
                if candidate != opponent:
                    votes_for = pairwise_matrix[candidate].get(opponent, 0)
                    votes_against = pairwise_matrix[opponent].get(candidate, 0)
                    
                    if votes_for > votes_against:
                        wins += 1
                    elif votes_against > votes_for:
                        losses += 1
                    # Les égalités ne comptent ni comme victoire ni comme défaite
            
            scores[candidate] = wins - losses
        
        ranked = sorted(candidates, key=lambda c: scores[c], reverse=True)
        logger.info(f"Classement par méthode Copeland: {ranked}")
        return ranked
    
    def resolve_ties_by_borda(self, rankings: List[List[int]], 
                             candidates: List[int]) -> List[int]:
        """
        Résout les égalités par un décompte Borda modifié
        
        Args:
            rankings: Classements originaux des votants
            candidates: Candidats à départager
            
        Returns:
            Classement ordonné des candidats
        """
        scores = defaultdict(int)
        
        for ranking in rankings:
            n = len(ranking)
            for i, candidate in enumerate(ranking):
                if candidate in candidates:
                    # Points Borda : n-1 points pour le 1er, n-2 pour le 2e, etc.
                    scores[candidate] += n - i - 1
        
        ranked = sorted(candidates, key=lambda c: scores[c], reverse=True)
        logger.info(f"Classement par méthode Borda: {ranked}")
        return ranked
    
    def compute_full_ranking(self, rankings: List[List[int]], 
                           candidates: List[int]) -> List[int]:
        """
        Calcule un classement complet en gérant les cycles
        
        Args:
            rankings: Liste des classements individuels
            candidates: Liste des candidats
            
        Returns:
            Classement final ordonné
        """
        pairwise_matrix = self.compute_pairwise_matrix(rankings, candidates)
        margin_matrix = self.compute_margin_matrix(pairwise_matrix, candidates)
        
        # Vérifie s'il y a un gagnant Condorcet
        winner = self.find_condorcet_winner(pairwise_matrix, candidates)
        if winner:
            # S'il y a un gagnant Condorcet, classe les autres récursivement
            remaining = [c for c in candidates if c != winner]
            if remaining:
                rest_ranking = self.compute_full_ranking(
                    [r for r in rankings], remaining
                )
                return [winner] + rest_ranking
            else:
                return [winner]
        
        # Pas de gagnant Condorcet, utilise la méthode de résolution choisie
        if self.tie_breaking_method == "margin":
            return self.resolve_ties_by_margin(candidates, margin_matrix)
        elif self.tie_breaking_method == "copeland":
            return self.resolve_ties_by_copeland(candidates, pairwise_matrix)
        elif self.tie_breaking_method == "borda":
            return self.resolve_ties_by_borda(rankings, candidates)
        else:
            raise ValueError(f"Méthode de résolution inconnue: {self.tie_breaking_method}")
    
    def conduct_election(self, rankings: List[List[int]], 
                        candidates: List[int]) -> VoteResult:
        """
        Conduit une élection complète selon la méthode Condorcet
        
        Args:
            rankings: Liste des classements de chaque votant
            candidates: Liste des candidats valides
            
        Returns:
            Résultat complet de l'élection
        """
        logger.info(f"Début de l'élection Condorcet avec {len(rankings)} votes et {len(candidates)} candidats")
        
        # Validation des votes
        self.validate_rankings(rankings, candidates)
        
        # Calculs principaux
        pairwise_matrix = self.compute_pairwise_matrix(rankings, candidates)
        margin_matrix = self.compute_margin_matrix(pairwise_matrix, candidates)
        winner = self.find_condorcet_winner(pairwise_matrix, candidates)
        smith_set = self.compute_smith_set(pairwise_matrix, candidates)
        ranking = self.compute_full_ranking(rankings, candidates)
        
        # Identification des égalités
        ties = self._identify_ties(ranking, margin_matrix)
        
        result = VoteResult(
            winner=winner,
            pairwise_matrix=pairwise_matrix,
            vote_count=len(rankings),
            candidates=candidates,
            smith_set=smith_set,
            ranking=ranking,
            ties=ties,
            margin_matrix=margin_matrix
        )
        
        logger.info(f"Élection terminée. Gagnant: {winner}, Classement: {ranking}")
        return result
    
    def _identify_ties(self, ranking: List[int], 
                      margin_matrix: Dict[int, Dict[int, int]]) -> List[List[int]]:
        """
        Identifie les groupes de candidats à égalité dans le classement final
        
        Args:
            ranking: Classement final
            margin_matrix: Matrice des marges
            
        Returns:
            Liste des groupes de candidats à égalité
        """
        ties = []
        i = 0
        
        while i < len(ranking):
            tie_group = [ranking[i]]
            j = i + 1
            
            # Trouve tous les candidats suivants qui sont à égalité
            while j < len(ranking):
                candidate_a = ranking[i]
                candidate_b = ranking[j]
                
                # Vérifie s'ils sont vraiment à égalité (marge proche de zéro)
                margin_ab = margin_matrix[candidate_a][candidate_b]
                margin_ba = margin_matrix[candidate_b][candidate_a]
                
                if abs(margin_ab) <= 1 and abs(margin_ba) <= 1:  # Seuil d'égalité
                    tie_group.append(ranking[j])
                    j += 1
                else:
                    break
            
            if len(tie_group) > 1:
                ties.append(tie_group)
            
            i = j if j > i + 1 else i + 1
        
        return ties
    
    def get_pairwise_comparison(self, candidate_a: int, candidate_b: int, 
                              pairwise_matrix: Dict[int, Dict[int, int]]) -> PairwiseComparison:
        """
        Obtient la comparaison détaillée entre deux candidats
        
        Args:
            candidate_a: Premier candidat
            candidate_b: Deuxième candidat
            pairwise_matrix: Matrice des comparaisons
            
        Returns:
            Comparaison détaillée entre les deux candidats
        """
        votes_a = pairwise_matrix[candidate_a].get(candidate_b, 0)
        votes_b = pairwise_matrix[candidate_b].get(candidate_a, 0)
        
        return PairwiseComparison(
            candidate_a=candidate_a,
            candidate_b=candidate_b,
            votes_for_a=votes_a,
            votes_for_b=votes_b,
            margin=votes_a - votes_b
        )

def condorcet_winner(rankings: List[List[int]], candidates: List[int]) -> Tuple[Optional[int], Dict]:
    """
    Fonction de compatibilité avec l'ancienne API
    
    Args:
        rankings: Liste des classements
        candidates: Liste des candidats
        
    Returns:
        Tuple (gagnant, matrice des victoires)
    """
    voting_system = CondorcetVotingSystem()
    
    try:
        result = voting_system.conduct_election(rankings, candidates)
        return result.winner, result.pairwise_matrix
    except VoteValidationError as e:
        logger.error(f"Erreur de validation: {e}")
        return None, {}

def analyze_vote_stability(rankings: List[List[int]], candidates: List[int]) -> Dict:
    """
    Analyse la stabilité du vote en simulant l'ajout/suppression de votes
    
    Args:
        rankings: Classements actuels
        candidates: Liste des candidats
        
    Returns:
        Dictionnaire avec les métriques de stabilité
    """
    voting_system = CondorcetVotingSystem()
    base_result = voting_system.conduct_election(rankings, candidates)
    
    stability_metrics = {
        "base_winner": base_result.winner,
        "winner_stability": 0.0,  # Pourcentage de simulations où le gagnant reste le même
        "ranking_stability": 0.0,  # Stabilité du classement complet
        "condorcet_efficiency": 1.0 if base_result.winner else 0.0  # Y a-t-il un gagnant Condorcet
    }
    
    # Simulation : retire aléatoirement des votes et vérifie la stabilité
    import random
    simulations = 100
    stable_winner_count = 0
    
    for _ in range(simulations):
        # Retire aléatoirement 10% des votes
        sample_size = max(1, len(rankings) - len(rankings) // 10)
        sample_rankings = random.sample(rankings, sample_size)
        
        try:
            sim_result = voting_system.conduct_election(sample_rankings, candidates)
            if sim_result.winner == base_result.winner:
                stable_winner_count += 1
        except:
            continue
    
    stability_metrics["winner_stability"] = stable_winner_count / simulations
    
    return stability_metrics
