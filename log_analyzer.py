"""
Módulo de análise e profiling de logs de eventos.

Detecta automaticamente características de qualquer log XES para garantir
compatibilidade com diferentes domínios (hospitalar, financeiro, manufatura, etc).
"""

from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set

from pm4py.objects.log.importer.xes import importer as xes_importer


@dataclass
class LogProfile:
    """
    Perfil completo de um log de eventos.
    
    Contém todas as características detectadas automaticamente.
    """
    
    # Informações básicas
    num_traces: int
    num_events: int
    num_unique_activities: int
    
    # Atributos disponíveis
    trace_attributes: Set[str]
    event_attributes: Set[str]
    
    # Mapeamento de atributos-chave
    activity_key: str
    timestamp_key: str
    case_id_key: str
    resource_key: Optional[str] = None
    complete_timestamp_key: Optional[str] = None
    
    # Estatísticas de atividades
    activity_frequencies: Dict[str, int] = field(default_factory=dict)
    
    # Estatísticas de recursos (se disponível)
    resource_frequencies: Dict[str, int] = field(default_factory=dict)
    has_resources: bool = False
    
    # Características temporais
    has_complete_timestamps: bool = False
    has_lifecycle: bool = False
    
    # Características estruturais
    min_trace_length: int = 0
    max_trace_length: int = 0
    avg_trace_length: float = 0.0
    
    # Variantes
    num_variants: int = 0
    most_common_variants: List[tuple] = field(default_factory=list)
    
    # Domínio detectado (opcional)
    suggested_domain: Optional[str] = None
    domain_confidence: float = 0.0


class LogAnalyzer:
    """
    Analisador de logs que detecta automaticamente características.
    
    Garante que qualquer log XES pode ser processado, independente do domínio
    (hospitalar, financeiro, varejo, manufatura, etc).
    
    Example:
        >>> analyzer = LogAnalyzer()
        >>> profile = analyzer.analyze("any_log.xes")
        >>> print(f"Domínio detectado: {profile.suggested_domain}")
        >>> print(f"Atividades: {profile.num_unique_activities}")
    """
    
    # Palavras-chave para detecção de domínio
    DOMAIN_KEYWORDS = {
        'healthcare': ['patient', 'doctor', 'nurse', 'exam', 'surgery', 'treatment', 
                      'diagnosis', 'hospital', 'medical', 'clinic', 'medication'],
        'finance': ['payment', 'transaction', 'invoice', 'credit', 'debit', 'loan',
                   'account', 'transfer', 'approval', 'bank'],
        'retail': ['order', 'purchase', 'product', 'customer', 'shipping', 'delivery',
                  'cart', 'checkout', 'payment', 'return'],
        'manufacturing': ['assembly', 'production', 'quality', 'inspection', 'machine',
                         'defect', 'maintenance', 'material', 'warehouse'],
        'insurance': ['claim', 'policy', 'premium', 'coverage', 'damage', 'assessment',
                     'adjuster', 'settlement'],
        'legal': ['case', 'court', 'hearing', 'verdict', 'filing', 'motion', 'appeal',
                 'judgment', 'litigation'],
        'it_service': ['incident', 'ticket', 'request', 'escalation', 'resolution',
                      'service', 'support', 'user', 'system'],
    }
    
    def __init__(self, verbose: bool = True):
        """
        Args:
            verbose: Se True, imprime informações durante análise
        """
        self.verbose = verbose
    
    def analyze(self, log_path: Path | str) -> LogProfile:
        """
        Analisa um log e retorna seu perfil completo.
        
        Args:
            log_path: Caminho do arquivo XES
            
        Returns:
            LogProfile com todas as características detectadas
        """
        log_path = Path(log_path)
        
        if not log_path.exists():
            raise FileNotFoundError(f"Log não encontrado: {log_path}")
        
        self._log(f"Analisando log: {log_path.name}")
        
        # Carrega log
        log = xes_importer.apply(str(log_path))
        
        # Detecta atributos disponíveis
        trace_attrs, event_attrs = self._detect_attributes(log)
        
        # Mapeia atributos-chave
        activity_key = self._detect_activity_key(event_attrs)
        timestamp_key = self._detect_timestamp_key(event_attrs)
        case_id_key = self._detect_case_id_key(trace_attrs)
        resource_key = self._detect_resource_key(event_attrs)
        complete_timestamp_key = self._detect_complete_timestamp_key(event_attrs)
        
        # Coleta atividades
        activity_frequencies = Counter()
        resource_frequencies = Counter()
        trace_lengths = []
        variants = []
        
        for trace in log:
            trace_variant = []
            for event in trace:
                if activity_key in event:
                    activity = event[activity_key]
                    activity_frequencies[activity] += 1
                    trace_variant.append(activity)
                
                if resource_key and resource_key in event:
                    resource_frequencies[event[resource_key]] += 1
            
            trace_lengths.append(len(trace))
            variants.append(tuple(trace_variant))
        
        # Conta variantes
        variant_counts = Counter(variants)
        most_common_variants = variant_counts.most_common(10)
        
        # Detecta domínio
        suggested_domain, confidence = self._detect_domain(activity_frequencies.keys())
        
        profile = LogProfile(
            num_traces=len(log),
            num_events=sum(len(trace) for trace in log),
            num_unique_activities=len(activity_frequencies),
            trace_attributes=trace_attrs,
            event_attributes=event_attrs,
            activity_key=activity_key,
            timestamp_key=timestamp_key,
            case_id_key=case_id_key,
            resource_key=resource_key,
            complete_timestamp_key=complete_timestamp_key,
            activity_frequencies=dict(activity_frequencies),
            resource_frequencies=dict(resource_frequencies),
            has_resources=bool(resource_key and resource_frequencies),
            has_complete_timestamps=bool(complete_timestamp_key),
            has_lifecycle='lifecycle:transition' in event_attrs,
            min_trace_length=min(trace_lengths) if trace_lengths else 0,
            max_trace_length=max(trace_lengths) if trace_lengths else 0,
            avg_trace_length=sum(trace_lengths) / len(trace_lengths) if trace_lengths else 0,
            num_variants=len(variant_counts),
            most_common_variants=most_common_variants,
            suggested_domain=suggested_domain,
            domain_confidence=confidence
        )
        
        self._print_profile(profile)
        
        return profile
    
    def _detect_attributes(self, log) -> tuple[Set[str], Set[str]]:
        """Detecta todos os atributos disponíveis no log."""
        trace_attrs = set()
        event_attrs = set()
        
        for trace in log:
            trace_attrs.update(trace.attributes.keys())
            for event in trace:
                event_attrs.update(event.keys())
        
        return trace_attrs, event_attrs
    
    def _detect_activity_key(self, event_attrs: Set[str]) -> str:
        """Detecta qual atributo representa a atividade."""
        # Prioridades
        candidates = [
            'concept:name',
            'Activity',
            'activity',
            'event',
            'Event',
            'task',
            'Task',
        ]
        
        for candidate in candidates:
            if candidate in event_attrs:
                self._log(f"  Activity key detectado: {candidate}")
                return candidate
        
        # Fallback: primeiro atributo que parece ser nome
        for attr in event_attrs:
            if 'name' in attr.lower():
                self._log(f"  Activity key detectado (fallback): {attr}")
                return attr
        
        raise ValueError(
            "Não foi possível detectar atributo de atividade. "
            f"Atributos disponíveis: {event_attrs}"
        )
    
    def _detect_timestamp_key(self, event_attrs: Set[str]) -> str:
        """Detecta qual atributo representa o timestamp."""
        candidates = [
            'time:timestamp',
            'timestamp',
            'Timestamp',
            'time',
            'Time',
            'start_time',
            'start_timestamp',
        ]
        
        for candidate in candidates:
            if candidate in event_attrs:
                self._log(f"  Timestamp key detectado: {candidate}")
                return candidate
        
        raise ValueError(
            "Não foi possível detectar atributo de timestamp. "
            f"Atributos disponíveis: {event_attrs}"
        )
    
    def _detect_case_id_key(self, trace_attrs: Set[str]) -> str:
        """Detecta qual atributo representa o ID do caso."""
        candidates = [
            'concept:name',
            'case:concept:name',
            'case_id',
            'CaseID',
            'Case',
        ]
        
        for candidate in candidates:
            if candidate in trace_attrs:
                self._log(f"  Case ID key detectado: {candidate}")
                return candidate
        
        # Fallback: primeiro atributo que parece ser ID
        for attr in trace_attrs:
            if 'id' in attr.lower() or 'case' in attr.lower():
                self._log(f"  Case ID key detectado (fallback): {attr}")
                return attr
        
        return 'concept:name'  # Padrão XES
    
    def _detect_resource_key(self, event_attrs: Set[str]) -> Optional[str]:
        """Detecta qual atributo representa o recurso (se existir)."""
        candidates = [
            'org:resource',
            'resource',
            'Resource',
            'user',
            'User',
            'actor',
            'Actor',
            'performer',
        ]
        
        for candidate in candidates:
            if candidate in event_attrs:
                self._log(f"  Resource key detectado: {candidate}")
                return candidate
        
        return None
    
    def _detect_complete_timestamp_key(self, event_attrs: Set[str]) -> Optional[str]:
        """Detecta timestamp de conclusão (se existir)."""
        candidates = [
            'time:complete',
            'complete_time',
            'end_time',
            'end_timestamp',
            'completion_time',
        ]
        
        for candidate in candidates:
            if candidate in event_attrs:
                self._log(f"  Complete timestamp detectado: {candidate}")
                return candidate
        
        return None
    
    def _detect_domain(self, activities: List[str]) -> tuple[Optional[str], float]:
        """
        Tenta detectar o domínio do log baseado nos nomes das atividades.
        
        Returns:
            Tupla (domínio, confiança) onde confiança é 0-1
        """
        # Normaliza atividades para lowercase
        normalized_activities = ' '.join(activities).lower()
        
        # Conta matches para cada domínio
        domain_scores = {}
        
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            matches = sum(1 for keyword in keywords if keyword in normalized_activities)
            if matches > 0:
                domain_scores[domain] = matches
        
        if not domain_scores:
            return None, 0.0
        
        # Domínio com mais matches
        best_domain = max(domain_scores, key=domain_scores.get)
        confidence = min(domain_scores[best_domain] / 5, 1.0)  # Normaliza para 0-1
        
        self._log(f"  Domínio sugerido: {best_domain} (confiança: {confidence:.0%})")
        
        return best_domain, confidence
    
    def _print_profile(self, profile: LogProfile):
        """Imprime resumo do perfil."""
        if not self.verbose:
            return
        
        print("\n" + "=" * 70)
        print("PERFIL DO LOG")
        print("=" * 70)
        
        print(f"\n📊 Estatísticas Básicas:")
        print(f"  Casos (traces): {profile.num_traces}")
        print(f"  Eventos totais: {profile.num_events}")
        print(f"  Atividades únicas: {profile.num_unique_activities}")
        print(f"  Variantes: {profile.num_variants}")
        
        print(f"\n📏 Comprimento dos Traces:")
        print(f"  Mínimo: {profile.min_trace_length} eventos")
        print(f"  Máximo: {profile.max_trace_length} eventos")
        print(f"  Média: {profile.avg_trace_length:.1f} eventos")
        
        print(f"\n🔑 Atributos Detectados:")
        print(f"  Atividade: {profile.activity_key}")
        print(f"  Timestamp: {profile.timestamp_key}")
        print(f"  Case ID: {profile.case_id_key}")
        print(f"  Recurso: {profile.resource_key or 'N/A'}")
        print(f"  Complete timestamp: {profile.complete_timestamp_key or 'N/A'}")
        
        print(f"\n✨ Características:")
        print(f"  Tem recursos: {'✓' if profile.has_resources else '✗'}")
        print(f"  Tem timestamps de conclusão: {'✓' if profile.has_complete_timestamps else '✗'}")
        print(f"  Tem lifecycle: {'✓' if profile.has_lifecycle else '✗'}")
        
        if profile.suggested_domain:
            print(f"\n🏢 Domínio Sugerido:")
            print(f"  {profile.suggested_domain.title()} ({profile.domain_confidence:.0%} confiança)")
        
        print(f"\n🔝 Top 5 Atividades:")
        top_activities = sorted(
            profile.activity_frequencies.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        for activity, count in top_activities:
            pct = (count / profile.num_events) * 100
            print(f"  • {activity}: {count} ({pct:.1f}%)")
        
        if profile.has_resources:
            print(f"\n👥 Top 5 Recursos:")
            top_resources = sorted(
                profile.resource_frequencies.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            for resource, count in top_resources:
                print(f"  • {resource}: {count} eventos")
        
        print()
    
    def validate_compatibility(self, profile: LogProfile) -> tuple[bool, List[str]]:
        """
        Valida se o log é compatível com o Sim2Log.
        
        Args:
            profile: Perfil do log
            
        Returns:
            Tupla (é_compatível, lista_de_avisos)
        """
        warnings = []
        is_compatible = True
        
        # Verificações críticas
        if profile.num_traces < 2:
            warnings.append("CRÍTICO: Log deve ter pelo menos 2 casos")
            is_compatible = False
        
        if profile.num_unique_activities < 2:
            warnings.append("CRÍTICO: Log deve ter pelo menos 2 atividades diferentes")
            is_compatible = False
        
        # Verificações de aviso
        if profile.num_traces < 10:
            warnings.append("AVISO: Poucos casos para análise estatística confiável")
        
        if profile.max_trace_length > 500:
            warnings.append("AVISO: Traces muito longos podem tornar simulação lenta")
        
        if not profile.has_resources:
            warnings.append("INFO: Log não tem recursos - análise organizacional não disponível")
        
        if not profile.has_complete_timestamps:
            warnings.append("INFO: Sem timestamps de conclusão - usando diferença entre eventos")
        
        return is_compatible, warnings
    
    def _log(self, message: str):
        """Imprime mensagem se verbose."""
        if self.verbose:
            print(message)


def analyze_log(log_path: Path | str, verbose: bool = True) -> LogProfile:
    """
    Função auxiliar para análise rápida de log.
    
    Args:
        log_path: Caminho do arquivo XES
        verbose: Se True, imprime informações
        
    Returns:
        LogProfile com características do log
    """
    analyzer = LogAnalyzer(verbose=verbose)
    return analyzer.analyze(log_path)

