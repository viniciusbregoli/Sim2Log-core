"""
Arquivo de teste para Sim2Log Core.

Este script executa o fluxo completo de mineração, simulação e validação de logs de eventos.
A partir de um arquivo XES real, o script irá:
  1. Minerar o modelo de processo usando algoritmo de descoberta
  2. Simular novos casos sintéticos baseados no modelo descoberto
  3. Validar a qualidade do log sintético comparando com o log original

Uso:
    python test.py <arquivo_xes>
    python test.py bases/running-example.xes
    python test.py bases/running-example.xes --num-cases 100
"""

import argparse
import subprocess
import sys
from pathlib import Path
from process_mining import ProcessMiner
from simulation import LogSimulator
from validation import LogValidator
from models import SimulationConfig


def show_image(image_path):
    """
    Tenta abrir a imagem do modelo de processo usando o visualizador padrão do sistema.
    
    Args:
        image_path: Caminho para o arquivo de imagem a ser aberto
    """
    try:
        subprocess.run(["xdg-open", str(image_path)], check=False)
        print(f"  Abrindo visualizador de imagens para: {image_path}")
    except Exception as e:
        print(f"  Não foi possível abrir a imagem automaticamente: {e}")


def test_basic_workflow(input_file, num_cases=50):
    """
    Executa o fluxo completo de trabalho: mineração -> simulação -> validação.
    
    Este teste realiza as três principais etapas do pipeline de process mining:
    1. Mineração: Extrai o modelo de processo do log de eventos original
    2. Simulação: Gera casos sintéticos baseados no modelo minerado
    3. Validação: Compara o log sintético com o original para avaliar qualidade
    
    Args:
        input_file: Caminho para o arquivo XES a ser processado
        num_cases: Número de casos sintéticos a serem gerados na simulação
    """
    input_file = Path(input_file)
    
    if not input_file.exists():
        print(f"Erro: O arquivo {input_file} não foi encontrado no sistema")
        if Path("bases").exists():
            print("\nArquivos XES disponíveis no diretório bases/:")
            for f in Path("bases").glob("*.xes"):
                print(f"  - {f}")
        sys.exit(1)
    
    print("="*60)
    print("ETAPA 1: MINERAÇÃO DE PROCESSOS")
    print("="*60)
    
    print("\n[1/3] Iniciando mineração do modelo de processo...")
    print("Analisando o log de eventos e descobrindo padrões de fluxo de trabalho...")
    model_image_path = Path("output/process-model.png")
    miner = ProcessMiner(verbose=True)
    model = miner.mine_process(
        input_file, 
        variant_filter=0.8,
        save_model_image=model_image_path
    )
    
    print("\nMineração concluída. Exibindo modelo de processo visual...")
    show_image(model_image_path)
    
    print("="*60)
    print("ETAPA 2: SIMULAÇÃO DE PROCESSOS")
    print("="*60)
    
    print(f"\n[2/3] Iniciando simulação de log sintético...")
    print(f"Gerando {num_cases} casos sintéticos baseados no modelo minerado...")
    config = SimulationConfig(num_cases=num_cases, random_seed=42)
    simulator = LogSimulator(config, verbose=True)
    result = simulator.simulate(
        model, 
        output_dir="output", 
        output_prefix="test-synthetic"
    )
    print("Simulação concluída. Arquivos salvos no diretório output/")
    
    print("="*60)
    print("ETAPA 3: VALIDAÇÃO DE PROCESSOS")
    print("="*60)
    
    print("\n[3/3] Iniciando validação de qualidade do log sintético...")
    print("Comparando o log sintético com o log original para avaliar similaridade...")
    validator = LogValidator(verbose=True)
    validation = validator.validate(input_file, result.xes_path)
    
    print("\n" + "="*60)
    print("RESULTADOS DO TESTE")
    print("="*60)
    print(f"\nCasos gerados: {result.num_cases_generated}")
    print(f"Eventos gerados: {result.num_events_generated}")
    print(f"Similaridade com log original: {validation.similarity_percentage:.1f}%")
    print(f"Fitness do modelo: {validation.fitness:.3f}")
    
    print("\n" + "-"*60)
    print("AVALIAÇÃO DE QUALIDADE")
    print("-"*60)
    if validation.fitness >= 0.7:
        print("TESTE APROVADO: Log sintético de boa qualidade foi gerado com sucesso.")
        print("O modelo minerado conseguiu replicar bem o comportamento do processo original.")
    else:
        print("AVISO: Baixa similaridade detectada entre logs original e sintético.")
        print("Considere ajustar os parâmetros de mineração ou aumentar o número de casos.")
    
    print("="*60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Gera logs de eventos sintéticos a partir de um arquivo XES real",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python test.py bases/running-example.xes
  python test.py bases/patient_treatment.xes --num-cases 100
  python test.py caminho/para/seu/log.xes
        """
    )
    parser.add_argument(
        "xes_file",
        type=str,
        help="Caminho para o arquivo XES de entrada"
    )
    parser.add_argument(
        "-n", "--num-cases",
        type=int,
        default=50,
        help="Número de casos sintéticos a serem gerados (padrão: 50)"
    )
    
    args = parser.parse_args()
    test_basic_workflow(args.xes_file, args.num_cases)

