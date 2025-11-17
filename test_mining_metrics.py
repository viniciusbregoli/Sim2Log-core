"""
Script para testar e debugar métricas de qualidade do modelo.

Se as métricas (fitness, precision, simplicity) aparecem como 0 no Streamlit,
execute este script para ver os erros detalhados.
"""

import sys
from pathlib import Path

# Adiciona o diretório ao path
sys.path.insert(0, str(Path(__file__).parent))

from process_mining import ProcessMiner
import warnings
warnings.filterwarnings('ignore')


def test_mining(log_path: str):
    """
    Testa mineração e exibe erros detalhados.

    Args:
        log_path: Caminho do arquivo XES
    """
    print("=" * 70)
    print("TESTE DE MÉTRICAS DE QUALIDADE")
    print("=" * 70)
    print(f"\nLog: {log_path}\n")

    # Minera com verbose ativado
    miner = ProcessMiner(verbose=True)

    try:
        model = miner.mine_process(
            log_path=log_path,
            variant_filter=0.8,
            auto_detect=True
        )

        print("\n" + "=" * 70)
        print("RESULTADOS")
        print("=" * 70)

        print(f"\nCasos minerados: {model.num_cases}")
        print(f"Variantes: {model.num_variants}")
        print(f"Atividades: {len(model.activities)}")

        print("\n--- MÉTRICAS DE QUALIDADE ---")
        print(f"Fitness:     {model.quality_metrics.get('fitness', 0):.3f}")
        print(f"Precision:   {model.quality_metrics.get('precision', 0):.3f}")
        print(f"Simplicity:  {model.quality_metrics.get('simplicity', 0):.3f}")

        # Diagnóstico
        print("\n--- DIAGNÓSTICO ---")
        if model.quality_metrics.get('fitness', 0) == 0:
            print("❌ Fitness = 0: Problema no cálculo de fitness")
            print("   Possíveis causas:")
            print("   - Log muito complexo ou ruidoso")
            print("   - Incompatibilidade com PM4Py")
            print("   - Modelo não consegue reproduzir o log")
        else:
            print(f"✓ Fitness OK: {model.quality_metrics.get('fitness', 0):.3f}")

        if model.quality_metrics.get('precision', 0) == 0:
            print("❌ Precision = 0: Problema no cálculo de precision")
            print("   Possíveis causas:")
            print("   - Modelo muito generalista")
            print("   - Erro no algoritmo de precision")
        else:
            print(f"✓ Precision OK: {model.quality_metrics.get('precision', 0):.3f}")

        if model.quality_metrics.get('simplicity', 0) == 0:
            print("❌ Simplicity = 0: Problema no cálculo de simplicity")
            print("   Possíveis causas:")
            print("   - Rede de Petri vazia ou mal formada")
            print("   - Erro no algoritmo")
        else:
            print(f"✓ Simplicity OK: {model.quality_metrics.get('simplicity', 0):.3f}")

        # Informações da rede de Petri
        print("\n--- ESTRUTURA DA REDE DE PETRI ---")
        print(f"Places: {len(model.petri_net.places)}")
        print(f"Transitions: {len(model.petri_net.transitions)}")
        print(f"Arcs: {len(model.petri_net.arcs)}")

        if len(model.petri_net.places) == 0 or len(model.petri_net.transitions) == 0:
            print("⚠️  PROBLEMA: Rede de Petri vazia!")
            print("   O log pode estar mal formatado ou sem dados suficientes.")

        print("\n" + "=" * 70)
        print("TESTE CONCLUÍDO")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ ERRO na mineração: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Uso: uv run python test_mining_metrics.py <caminho_do_log.xes>")
        print("\nExemplo:")
        print("  uv run python test_mining_metrics.py ../bases/seu_log.xes")
        sys.exit(1)

    log_path = sys.argv[1]

    if not Path(log_path).exists():
        print(f"❌ Arquivo não encontrado: {log_path}")
        sys.exit(1)

    test_mining(log_path)
