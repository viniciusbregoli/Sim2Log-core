"""
Exemplo completo: Excel de Cirurgias → XES → Simulação

Demonstra o pipeline completo:
1. Converter Excel para XES
2. Analisar o log
3. Minerar processo
4. Simular novos casos
5. Validar
"""

from pathlib import Path
from core import ProcessMiner, LogSimulator, LogAnalyzer, SimulationConfig, LogValidator
from core.converters.excel_to_xes import convert_cirurgias_xlsx_to_xes


def processar_cirurgias(excel_path: Path | str):
    """
    Pipeline completo para processar dados de cirurgias.
    
    Args:
        excel_path: Caminho do arquivo Excel com dados de cirurgias
    """
    
    excel_path = Path(excel_path)
    
    if not excel_path.exists():
        print(f"❌ Arquivo não encontrado: {excel_path}")
        return
    
    print("=" * 70)
    print("PROCESSAMENTO DE DADOS DE CIRURGIAS")
    print("=" * 70)
    print(f"\n📄 Arquivo: {excel_path.name}\n")
    
    # ========================================================================
    # ETAPA 1: CONVERTER EXCEL PARA XES
    # ========================================================================
    print("🔄 ETAPA 1: Convertendo Excel para XES...")
    print("-" * 70)
    
    xes_path = excel_path.with_suffix('.xes')
    
    try:
        xes_path = convert_cirurgias_xlsx_to_xes(excel_path, xes_path)
        print(f"\n✓ Conversão concluída: {xes_path}")
    except Exception as e:
        print(f"❌ Erro na conversão: {e}")
        return
    
    # ========================================================================
    # ETAPA 2: ANALISAR O LOG GERADO
    # ========================================================================
    print("\n🔍 ETAPA 2: Analisando log de cirurgias...")
    print("-" * 70)
    
    analyzer = LogAnalyzer(verbose=True)
    profile = analyzer.analyze(xes_path)
    
    # Validar compatibilidade
    is_compatible, warnings = analyzer.validate_compatibility(profile)
    
    if not is_compatible:
        print("\n❌ Log incompatível:")
        for warning in warnings:
            print(f"  • {warning}")
        return
    
    # ========================================================================
    # ETAPA 3: MINERAR MODELO DE PROCESSO
    # ========================================================================
    print("\n⛏️  ETAPA 3: Minerando modelo de processo cirúrgico...")
    print("-" * 70)
    
    miner = ProcessMiner(verbose=False)
    model = miner.mine_process(
        log_path=xes_path,
        variant_filter=0.8,
        save_model_image=Path("output_cirurgias/modelo_processo.png"),
        auto_detect=True
    )
    
    print(f"✓ Modelo extraído!")
    print(f"  Domínio: {model.domain or 'Healthcare'}")
    print(f"  Atividades no processo: {len(model.activities)}")
    print(f"  Taxa de chegada: {model.arrival_rate:.2f} min/cirurgia")
    print(f"  Duração mediana: {model.median_case_duration/60:.1f} minutos")
    
    print(f"\n  Qualidade do modelo:")
    for metric, value in model.quality_metrics.items():
        print(f"    • {metric.capitalize()}: {value:.3f}")
    
    print(f"\n  Atividades detectadas:")
    for i, (activity, stats) in enumerate(list(model.activities.items())[:10], 1):
        print(f"    {i}. {activity}: {stats.mean_duration/60:.1f} min (média)")
    
    if len(model.activities) > 10:
        print(f"    ... e mais {len(model.activities) - 10} atividades")
    
    # ========================================================================
    # ETAPA 4: SIMULAÇÃO
    # ========================================================================
    print("\n🎮 ETAPA 4: Simulando novos casos de cirurgia...")
    print("-" * 70)
    
    # Simula 50 cirurgias sintéticas
    config = SimulationConfig(
        num_cases=50,
        arrival_rate=None,  # Usa a taxa do log original
        random_seed=42
    )
    
    simulator = LogSimulator(config, verbose=False)
    result = simulator.simulate(
        process_model=model,
        output_dir="output_cirurgias",
        output_prefix="cirurgias_simuladas"
    )
    
    print(f"✓ Simulação concluída!")
    print(f"  Cirurgias geradas: {result.num_cases_generated}")
    print(f"  Eventos totais: {result.num_events_generated}")
    print(f"  Tempo de simulação: {result.simulation_time:.2f}s")
    
    # ========================================================================
    # ETAPA 5: VALIDAÇÃO
    # ========================================================================
    print("\n✅ ETAPA 5: Validando logs gerados...")
    print("-" * 70)
    
    validator = LogValidator(verbose=False)
    validation = validator.validate(xes_path, result.xes_path)
    
    print(f"✓ Validação concluída!")
    print(f"  Fitness: {validation.fitness:.3f} ({validation.similarity_percentage:.1f}%)")
    print(f"  Custo de alinhamento: {validation.cost:.2f}")
    
    if validation.fitness >= 0.8:
        print(f"  → Excelente! Logs sintéticos muito similares aos reais")
    elif validation.fitness >= 0.6:
        print(f"  → Bom! Logs sintéticos apresentam boa similaridade")
    else:
        print(f"  → Regular. Considere ajustar parâmetros")
    
    # ========================================================================
    # RESUMO FINAL
    # ========================================================================
    print("\n" + "=" * 70)
    print("✅ PIPELINE CONCLUÍDO COM SUCESSO!")
    print("=" * 70)
    
    print(f"\n📊 Resumo do Processo:")
    print(f"  • Tipo: Processo de Centro Cirúrgico")
    print(f"  • Cirurgias analisadas: {profile.num_traces}")
    print(f"  • Etapas do processo: {profile.num_unique_activities}")
    print(f"  • Variantes do fluxo: {profile.num_variants}")
    
    print(f"\n📁 Arquivos Gerados:")
    print(f"  • Log XES: {xes_path}")
    print(f"  • Modelo visual: output_cirurgias/modelo_processo.png")
    print(f"  • Cirurgias simuladas (CSV): {result.csv_path}")
    print(f"  • Cirurgias simuladas (XES): {result.xes_path}")
    
    print(f"\n💡 Próximos Passos:")
    print(f"  1. Visualize o modelo: output_cirurgias/modelo_processo.png")
    print(f"  2. Analise os logs simulados: {result.csv_path}")
    print(f"  3. Use os logs para testes, treinamento, etc")
    print()


def exemplo_analise_rapida(excel_path: Path | str):
    """Análise rápida sem simulação."""
    
    excel_path = Path(excel_path)
    
    print("\n🔍 ANÁLISE RÁPIDA DE DADOS DE CIRURGIAS")
    print("=" * 70)
    
    # Converte
    xes_path = convert_cirurgias_xlsx_to_xes(excel_path)
    
    # Analisa
    analyzer = LogAnalyzer()
    profile = analyzer.analyze(xes_path)
    
    print(f"\n📊 Resumo Rápido:")
    print(f"  Cirurgias: {profile.num_traces}")
    print(f"  Etapas: {profile.num_unique_activities}")
    print(f"  Comprimento médio: {profile.avg_trace_length:.1f} etapas")
    print(f"  Tem recursos: {'Sim' if profile.has_resources else 'Não'}")


def main():
    """Exemplo de uso."""
    import sys
    
    if len(sys.argv) < 2:
        print("""
╔══════════════════════════════════════════════════════════════════╗
║  PROCESSADOR DE DADOS DE CIRURGIAS                               ║
╚══════════════════════════════════════════════════════════════════╝

Converte dados de cirurgias (Excel) em logs de processo e simula
novos casos usando Process Mining e Simulação de Eventos Discretos.

USO:
  python example_cirurgias.py arquivo.xlsx [--quick]

ARGUMENTOS:
  arquivo.xlsx    Arquivo Excel com dados de cirurgias
  --quick        Análise rápida (sem simulação)

COLUNAS ESPERADAS NO EXCEL:
  • NR_CIRURGIA: ID da cirurgia (obrigatório)
  • Colunas de timestamp: CHAMADA_CC, CHEGADA_CC, ENTRADA_SALA,
    INICIO_ANESTESIA, INICIO_PROC_CIRURGICO, TERMINO_PROC_CIRURGICO,
    SAIDA_RPA_CC, etc
  • Opcional: NM_CIRURGIAO, NM_ANESTESISTA, SALA

EXEMPLO:
  python example_cirurgias.py dados_cirurgias.xlsx

SAÍDA:
  • dados_cirurgias.xes (log convertido)
  • output_cirurgias/ (resultados da simulação)
  • modelo_processo.png (visualização do fluxo)

Desenvolvido com Sim2Log Core v2.0
        """)
        sys.exit(0)
    
    excel_file = sys.argv[1]
    quick = '--quick' in sys.argv
    
    if quick:
        exemplo_analise_rapida(excel_file)
    else:
        processar_cirurgias(excel_file)


if __name__ == "__main__":
    main()





