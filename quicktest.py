"""
Teste rápido do Sim2Log Core.
"""

from pathlib import Path
from core import ProcessMiner, LogSimulator, LogValidator, SimulationConfig

def quick_test():
    """Teste rápido com log de exemplo."""
    
    # Procura log de exemplo
    possible_logs = [
        Path("running-example.xes"),
        Path("../running-example.xes"),
        Path("sim2log/media/running-example.xes"),
    ]
    
    input_log = None
    for log_path in possible_logs:
        if log_path.exists():
            input_log = log_path
            break
    
    if not input_log:
        print("❌ Nenhum log XES encontrado para teste")
        print("Coloque um arquivo 'running-example.xes' no diretório atual")
        return False
    
    print(f"📄 Usando log: {input_log}")
    print()
    
    try:
        # 1. Minera processo
        print("⛏️  Minerando processo...")
        miner = ProcessMiner(verbose=False)
        model = miner.mine_process(input_log, variant_filter=0.8)
        print(f"   ✓ {len(model.activities)} atividades descobertas")
        print(f"   ✓ Taxa de chegada: {model.arrival_rate:.2f} min/caso")
        print()
        
        # 2. Simula (apenas 10 casos para teste rápido)
        print("🎮 Executando simulação (10 casos)...")
        config = SimulationConfig(num_cases=10, random_seed=42)
        simulator = LogSimulator(config, verbose=False)
        result = simulator.simulate(model, output_dir="test_output")
        print(f"   ✓ {result.num_cases_generated} casos gerados")
        print(f"   ✓ {result.num_events_generated} eventos")
        print(f"   ✓ Tempo: {result.simulation_time:.2f}s")
        print()
        
        # 3. Valida
        print("✅ Validando logs...")
        validator = LogValidator(verbose=False)
        validation = validator.validate(input_log, result.xes_path)
        print(f"   ✓ Fitness: {validation.fitness:.3f}")
        print(f"   ✓ Similaridade: {validation.similarity_percentage:.1f}%")
        print()
        
        print("=" * 60)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        print(f"\nArquivos gerados em: {result.csv_path.parent}")
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    success = quick_test()
    sys.exit(0 if success else 1)

