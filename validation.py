"""
Módulo de validação de logs sintéticos.

Compara logs originais com logs sintéticos para avaliar qualidade.
"""

import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

from pathlib import Path
from typing import Dict

from pm4py.algo.conformance.alignments.edit_distance import algorithm as logs_alignments
from pm4py.objects.log.importer.xes import importer as xes_importer

from models import ValidationResult


class LogValidator:
    """
    Validador de logs sintéticos.
    
    Compara logs originais com sintéticos usando métricas de alinhamento.
    
    Example:
        >>> validator = LogValidator()
        >>> result = validator.validate("original.xes", "simulated.xes")
        >>> print(f"Fitness: {result.fitness:.2%}")
        Fitness: 89.50%
    """
    
    def __init__(self, verbose: bool = True):
        """
        Args:
            verbose: Se True, imprime informações durante validação
        """
        self.verbose = verbose
    
    def validate(
        self,
        original_log_path: Path | str,
        simulated_log_path: Path | str
    ) -> ValidationResult:
        """
        Valida log simulado comparando com o original.
        
        Args:
            original_log_path: Caminho do log original
            simulated_log_path: Caminho do log simulado
            
        Returns:
            ValidationResult com métricas de qualidade
        """
        original_log_path = Path(original_log_path)
        simulated_log_path = Path(simulated_log_path)
        
        if not original_log_path.exists():
            raise FileNotFoundError(f"Log original não encontrado: {original_log_path}")
        if not simulated_log_path.exists():
            raise FileNotFoundError(f"Log simulado não encontrado: {simulated_log_path}")
        
        self._log("Carregando logs...")
        original_log = xes_importer.apply(str(original_log_path))
        simulated_log = xes_importer.apply(str(simulated_log_path))
        
        self._log(f"Log original: {len(original_log)} casos")
        self._log(f"Log simulado: {len(simulated_log)} casos")
        
        # Calcula alinhamentos
        self._log("Calculando alinhamentos (edit distance)...")
        alignments = logs_alignments.apply(original_log, simulated_log, parameters={})
        
        # Extrai métricas
        total_fitness = 0.0
        total_cost = 0.0
        num_alignments = len(alignments)
        
        fitness_distribution = []
        cost_distribution = []
        
        for alignment in alignments:
            for key, value in alignment.items():
                if key == 'fitness':
                    total_fitness += value
                    fitness_distribution.append(value)
                elif key == 'cost':
                    total_cost += value
                    cost_distribution.append(value)
        
        # Calcula médias
        avg_fitness = round(total_fitness / num_alignments, 3) if num_alignments > 0 else 0.0
        avg_cost = round(total_cost / num_alignments, 2) if num_alignments > 0 else 0.0
        similarity = round(avg_fitness * 100, 2)
        
        self._log(f"✓ Validação concluída")
        self._log(f"  Fitness médio: {avg_fitness:.3f} ({similarity:.1f}%)")
        self._log(f"  Custo médio: {avg_cost:.2f}")
        
        details = {
            'num_alignments': num_alignments,
            'fitness_min': min(fitness_distribution) if fitness_distribution else 0,
            'fitness_max': max(fitness_distribution) if fitness_distribution else 0,
            'cost_min': min(cost_distribution) if cost_distribution else 0,
            'cost_max': max(cost_distribution) if cost_distribution else 0,
        }
        
        return ValidationResult(
            fitness=avg_fitness,
            cost=avg_cost,
            similarity_percentage=similarity,
            details=details
        )
    
    def _log(self, message: str):
        """Imprime mensagem se verbose ativado."""
        if self.verbose:
            print(f"[LogValidator] {message}")

