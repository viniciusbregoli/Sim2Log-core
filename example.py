"""
Exemplo de uso da biblioteca Sim2Log Core.

Este exemplo demonstra o fluxo completo:
1. Mineração de processo
2. Configuração da simulação
3. Execução da simulação
4. Validação dos resultados
"""

from pathlib import Path

from core import ProcessMiner, LogSimulator, LogValidator, SimulationConfig


def main():
    """Exemplo completo de uso."""
    
    print("=" * 70)
    print("SIM2LOG CORE - EXEMPLO DE USO")
    print("=" * 70)
    print()
    
    # Caminhos
    input_log = Path("running-example.xes")
    output_dir = Path("output")
    model_image = output_dir / "process_model.png"
    
    # Verifica se log existe
    if not input_log.exists():
        print(f"ERRO: Log não encontrado: {input_log}")
        print("Certifique-se de ter um arquivo XES de exemplo.")
        return
    
    # ========================================================================
    # ETAPA 1: MINERAÇÃO DE PROCESSO
    # ========================================================================
    print("\n" + "=" * 70)
    print("ETAPA 1: MINERAÇÃO DE PROCESSO")
    print("=" * 70 + "\n")
    
    miner = ProcessMiner(verbose=True)
    process_model = miner.mine_process(
        log_path=input_log,
        variant_filter=0.8,  # Mantém 80% das variantes mais frequentes
        save_model_image=model_image
    )
    
    # Exibe informações do modelo
    print("\n--- INFORMAÇÕES DO MODELO ---")
    print(f"Casos no log original: {process_model.num_cases}")
    print(f"Casos após filtragem: {process_model.num_variants}")
    print(f"Taxa de chegada: {process_model.arrival_rate:.2f} min/caso")
    print(f"Taxa de dispersão: {process_model.dispersion_rate:.2f} min/caso")
    print(f"Duração mediana dos casos: {process_model.median_case_duration:.0f}s")
    
    print("\n--- QUALIDADE DO MODELO ---")
    for metric, value in process_model.quality_metrics.items():
        print(f"{metric.capitalize()}: {value:.3f}")
    
    print("\n--- ATIVIDADES DESCOBERTAS ---")
    for activity_name, stats in process_model.activities.items():
        print(f"{activity_name}:")
        print(f"  Duração média: {stats.mean_duration:.2f}s")
        print(f"  Distribuição: {stats.distribution_name} (p={stats.p_value:.3f})")
    
    # ========================================================================
    # ETAPA 2: CONFIGURAÇÃO DA SIMULAÇÃO
    # ========================================================================
    print("\n" + "=" * 70)
    print("ETAPA 2: CONFIGURAÇÃO DA SIMULAÇÃO")
    print("=" * 70 + "\n")
    
    config = SimulationConfig(
        num_cases=100,              # Gerar 100 casos
        arrival_rate=None,          # Usar taxa do log original
        activity_durations=None,    # Usar durações originais
        variant_filter_percentage=0.8,
        random_seed=42,
        max_trace_length=1000
    )
    
    print("Configuração:")
    print(f"  Casos a gerar: {config.num_cases}")
    print(f"  Taxa de chegada: {'Auto (do log)' if config.arrival_rate is None else f'{config.arrival_rate} min'}")
    print(f"  Seed aleatória: {config.random_seed}")
    
    # ========================================================================
    # ETAPA 3: EXECUÇÃO DA SIMULAÇÃO
    # ========================================================================
    print("\n" + "=" * 70)
    print("ETAPA 3: EXECUÇÃO DA SIMULAÇÃO")
    print("=" * 70 + "\n")
    
    simulator = LogSimulator(config, verbose=True)
    simulation_result = simulator.simulate(
        process_model=process_model,
        output_dir=output_dir,
        output_prefix="simulated-logs"
    )
    
    print("\n--- RESULTADOS DA SIMULAÇÃO ---")
    print(f"Casos gerados: {simulation_result.num_cases_generated}")
    print(f"Eventos gerados: {simulation_result.num_events_generated}")
    print(f"Tempo de simulação: {simulation_result.simulation_time:.2f}s")
    print(f"Arquivo CSV: {simulation_result.csv_path}")
    print(f"Arquivo XES: {simulation_result.xes_path}")
    
    # ========================================================================
    # ETAPA 4: VALIDAÇÃO
    # ========================================================================
    print("\n" + "=" * 70)
    print("ETAPA 4: VALIDAÇÃO DOS LOGS GERADOS")
    print("=" * 70 + "\n")
    
    validator = LogValidator(verbose=True)
    validation_result = validator.validate(
        original_log_path=input_log,
        simulated_log_path=simulation_result.xes_path
    )
    
    print("\n--- MÉTRICAS DE VALIDAÇÃO ---")
    print(f"Fitness: {validation_result.fitness:.3f} ({validation_result.similarity_percentage:.1f}%)")
    print(f"Custo de alinhamento: {validation_result.cost:.2f}")
    print(f"\nInterpretação:")
    if validation_result.fitness >= 0.9:
        print("  ✓ EXCELENTE: Logs muito similares ao original")
    elif validation_result.fitness >= 0.7:
        print("  ✓ BOM: Logs apresentam boa similaridade")
    elif validation_result.fitness >= 0.5:
        print("  ⚠ REGULAR: Logs apresentam diferenças significativas")
    else:
        print("  ✗ RUIM: Logs muito diferentes do original")
    
    # ========================================================================
    # RESUMO FINAL
    # ========================================================================
    print("\n" + "=" * 70)
    print("RESUMO FINAL")
    print("=" * 70)
    print(f"\n✓ Processo minerado com sucesso")
    print(f"✓ {simulation_result.num_cases_generated} casos sintéticos gerados")
    print(f"✓ Similaridade: {validation_result.similarity_percentage:.1f}%")
    print(f"\nArquivos gerados:")
    print(f"  - Modelo: {model_image}")
    print(f"  - CSV: {simulation_result.csv_path}")
    print(f"  - XES: {simulation_result.xes_path}")
    print()


def example_custom_parameters():
    """
    Exemplo com parâmetros customizados.
    
    Demonstra como modificar durações de atividades e taxa de chegada.
    """
    print("\n" + "=" * 70)
    print("EXEMPLO: SIMULAÇÃO COM PARÂMETROS CUSTOMIZADOS")
    print("=" * 70 + "\n")
    
    input_log = Path("running-example.xes")
    
    if not input_log.exists():
        print(f"ERRO: Log não encontrado: {input_log}")
        return
    
    # Minera processo
    miner = ProcessMiner(verbose=False)
    process_model = miner.mine_process(input_log)
    
    # Configuração customizada
    custom_durations = {}
    for activity_name, stats in process_model.activities.items():
        # Reduz duração em 50%
        custom_durations[activity_name] = stats.mean_duration * 0.5
    
    config = SimulationConfig(
        num_cases=50,
        arrival_rate=2.0,  # 2 minutos entre casos (mais rápido)
        activity_durations=custom_durations,  # Durações reduzidas
        random_seed=123
    )
    
    print("Modificações aplicadas:")
    print("  - Taxa de chegada: 2.0 min (customizada)")
    print("  - Durações de atividades: 50% das originais")
    print()
    
    # Simula
    simulator = LogSimulator(config, verbose=True)
    result = simulator.simulate(
        process_model=process_model,
        output_dir=Path("output_custom"),
        output_prefix="custom-simulation"
    )
    
    print(f"\n✓ Simulação customizada concluída!")
    print(f"  Arquivo: {result.xes_path}")


if __name__ == "__main__":
    # Executa exemplo principal
    main()
    
    # Descomente para executar exemplo com parâmetros customizados
    # example_custom_parameters()

