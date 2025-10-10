"""
Utilitários auxiliares para o Sim2Log Core.
"""

import re
from pathlib import Path
from typing import Dict, List


def sanitize_activity_name(name: str) -> str:
    """
    Sanitiza nome de atividade removendo caracteres especiais.
    
    Args:
        name: Nome original da atividade
        
    Returns:
        Nome sanitizado (apenas letras e números)
        
    Example:
        >>> sanitize_activity_name("Register Request!")
        'RegisterRequest'
    """
    return re.sub(r"[^A-Za-z0-9]", "", name)


def format_duration(seconds: float) -> str:
    """
    Formata duração em segundos para formato legível.
    
    Args:
        seconds: Duração em segundos
        
    Returns:
        String formatada (ex: "2m 30s", "1h 15m")
        
    Example:
        >>> format_duration(150)
        '2m 30s'
        >>> format_duration(3665)
        '1h 1m 5s'
    """
    if seconds < 60:
        return f"{seconds:.0f}s"
    
    minutes = seconds / 60
    if minutes < 60:
        mins = int(minutes)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s" if secs > 0 else f"{mins}m"
    
    hours = int(minutes / 60)
    mins = int(minutes % 60)
    secs = int(seconds % 60)
    
    parts = [f"{hours}h"]
    if mins > 0:
        parts.append(f"{mins}m")
    if secs > 0:
        parts.append(f"{secs}s")
    
    return " ".join(parts)


def ensure_directory(path: Path | str) -> Path:
    """
    Garante que um diretório existe, criando se necessário.
    
    Args:
        path: Caminho do diretório
        
    Returns:
        Path do diretório
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def summarize_model(model) -> Dict[str, any]:
    """
    Cria um resumo legível de um ProcessModel.
    
    Args:
        model: ProcessModel
        
    Returns:
        Dicionário com informações resumidas
    """
    from models import ProcessModel
    
    if not isinstance(model, ProcessModel):
        raise TypeError("model deve ser uma instância de ProcessModel")
    
    return {
        'num_cases': model.num_cases,
        'num_variants': model.num_variants,
        'num_activities': len(model.activities),
        'arrival_rate_min': model.arrival_rate,
        'median_duration': format_duration(model.median_case_duration),
        'quality': {
            k: f"{v:.1%}" for k, v in model.quality_metrics.items()
        },
        'activities': [
            {
                'name': name,
                'avg_duration': format_duration(stats.mean_duration),
                'distribution': stats.distribution_name
            }
            for name, stats in model.activities.items()
        ]
    }


def print_model_summary(model):
    """
    Imprime resumo formatado de um ProcessModel.
    
    Args:
        model: ProcessModel
    """
    summary = summarize_model(model)
    
    print("\n" + "=" * 70)
    print("RESUMO DO MODELO DE PROCESSO")
    print("=" * 70)
    print(f"\nCasos: {summary['num_cases']} → {summary['num_variants']} (após filtragem)")
    print(f"Atividades: {summary['num_activities']}")
    print(f"Taxa de chegada: {summary['arrival_rate_min']:.2f} min/caso")
    print(f"Duração mediana: {summary['median_duration']}")
    
    print("\nQualidade do Modelo:")
    for metric, value in summary['quality'].items():
        print(f"  {metric.capitalize()}: {value}")
    
    print("\nAtividades:")
    for act in summary['activities']:
        print(f"  • {act['name']}")
        print(f"    Duração: {act['avg_duration']} | Distribuição: {act['distribution']}")
    print()


def compare_logs(original_path: Path | str, simulated_path: Path | str) -> Dict:
    """
    Compara estatísticas básicas entre log original e simulado.
    
    Args:
        original_path: Caminho do log original
        simulated_path: Caminho do log simulado
        
    Returns:
        Dicionário com comparações
    """
    from pm4py.objects.log.importer.xes import importer as xes_importer
    from pm4py.statistics.traces.generic.log import case_statistics
    
    original = xes_importer.apply(str(original_path))
    simulated = xes_importer.apply(str(simulated_path))
    
    orig_duration = case_statistics.get_median_caseduration(original)
    sim_duration = case_statistics.get_median_caseduration(simulated)
    
    return {
        'num_cases': {
            'original': len(original),
            'simulated': len(simulated)
        },
        'median_duration': {
            'original': orig_duration,
            'simulated': sim_duration,
            'difference_pct': ((sim_duration - orig_duration) / orig_duration * 100)
        }
    }


def export_activities_table(model, output_file: Path | str):
    """
    Exporta tabela de atividades para CSV.
    
    Args:
        model: ProcessModel
        output_file: Caminho do arquivo de saída
    """
    import csv
    
    output_file = Path(output_file)
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Activity',
            'Mean Duration (s)',
            'Distribution',
            'P-Value',
            'Num Observations'
        ])
        
        for name, stats in model.activities.items():
            writer.writerow([
                name,
                f"{stats.mean_duration:.2f}",
                stats.distribution_name,
                f"{stats.p_value:.4f}",
                len(stats.durations)
            ])
    
    print(f"Tabela exportada para: {output_file}")

