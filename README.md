# Sim2Log Core v2.0

Biblioteca Python para geração de logs sintéticos a partir de logs de processos reais usando **Process Mining** e **Simulação de Eventos Discretos**.

## 🎯 Características

- ✅ **100% Genérico** - Funciona com qualquer domínio (hospitalar, financeiro, varejo, etc)
- ✅ **Auto-Detecção** - Identifica automaticamente atributos e características do log
- ✅ **Robusto** - Fallbacks inteligentes para casos extremos
- ✅ **Profissional** - Código limpo, documentado, type hints completos
- ✅ **Extensível** - Arquitetura modular e bem estruturada

---

## 📦 Instalação

```bash
# Clone o repositório
cd /home/bregoli/Code/Sim2Log-main

# Ative o ambiente virtual
source venv/bin/activate

# As dependências já estão instaladas do requirements.txt principal
# Para usar apenas o core, veja requirements-core.txt
```

### Dependências Opcionais

Para converter Excel para XES:
```bash
pip install openpyxl
```

---

## 🚀 Uso Rápido

```python
from core import ProcessMiner, LogSimulator, SimulationConfig

# 1. Minera processo de um log XES
miner = ProcessMiner()
model = miner.mine_process("event_log.xes", auto_detect=True)

# 2. Configura e executa simulação
config = SimulationConfig(num_cases=100, random_seed=42)
simulator = LogSimulator(config)
result = simulator.simulate(model, output_dir="output")

# 3. Valida resultados
from core import LogValidator
validator = LogValidator()
validation = validator.validate("event_log.xes", result.xes_path)

print(f"Similaridade: {validation.similarity_percentage:.1f}%")
```

**Pronto! Apenas 3 passos para gerar logs sintéticos de qualquer processo.**

---

## 📚 Módulos Principais

### 1. **ProcessMiner** - Mineração de Processos

Extrai modelo de processo e estatísticas de logs XES.

```python
from core import ProcessMiner

miner = ProcessMiner(verbose=True)
model = miner.mine_process(
    log_path="input.xes",
    variant_filter=0.8,          # Mantém 80% variantes mais frequentes
    save_model_image="model.png", # Salva visualização
    auto_detect=True             # Detecta atributos automaticamente
)

# Informações extraídas
print(f"Domínio: {model.domain}")              # healthcare, finance, etc
print(f"Taxa de chegada: {model.arrival_rate} min/caso")
print(f"Atividades: {len(model.activities)}")
print(f"Qualidade: {model.quality_metrics}")
```

**Detecta automaticamente:**
- Atributos do log (atividade, timestamp, recursos)
- Domínio do processo (healthcare, finance, retail, etc)
- Distribuições estatísticas das durações
- Métricas de qualidade (fitness, precisão, simplicidade)

### 2. **LogSimulator** - Simulação

Gera logs sintéticos usando simulação de eventos discretos (SimPy).

```python
from core import LogSimulator, SimulationConfig

config = SimulationConfig(
    num_cases=100,                   # Casos a gerar
    arrival_rate=5.0,                # Minutos entre casos (None = usar do log)
    activity_durations={             # Durações customizadas (opcional)
        "Register Request": 120.0,
        "Examine Thoroughly": 300.0
    },
    random_seed=42                   # Reprodutibilidade
)

simulator = LogSimulator(config, verbose=True)
result = simulator.simulate(
    process_model=model,
    output_dir="output",
    output_prefix="simulated-logs"
)

print(f"Gerados: {result.num_cases_generated} casos")
print(f"CSV: {result.csv_path}")
print(f"XES: {result.xes_path}")
```

### 3. **LogValidator** - Validação

Valida qualidade dos logs sintéticos comparando com o original.

```python
from core import LogValidator

validator = LogValidator(verbose=True)
validation = validator.validate(
    original_log_path="original.xes",
    simulated_log_path="simulated.xes"
)

print(f"Fitness: {validation.fitness:.3f}")           # 0-1 (quanto maior melhor)
print(f"Custo: {validation.cost:.2f}")                # Quanto menor melhor
print(f"Similaridade: {validation.similarity_percentage:.1f}%")
```

### 4. **LogAnalyzer** - Análise de Logs

Analisa qualquer log e detecta suas características automaticamente.

```python
from core import LogAnalyzer, analyze_log

# Análise rápida
profile = analyze_log("any_log.xes")

print(f"Domínio: {profile.suggested_domain}")
print(f"Casos: {profile.num_traces}")
print(f"Atividades: {profile.num_unique_activities}")
print(f"Tem recursos: {profile.has_resources}")

# Análise detalhada
analyzer = LogAnalyzer()
profile = analyzer.analyze("log.xes")
is_compatible, warnings = analyzer.validate_compatibility(profile)
```

**Detecta automaticamente:**
- Atributos-chave (atividade, timestamp, case ID, recursos)
- Domínio do processo (7 domínios suportados)
- Características estruturais (comprimento de traces, variantes)
- Compatibilidade com Sim2Log

---

## 🔧 Modelos de Dados

### SimulationConfig

```python
@dataclass
class SimulationConfig:
    num_cases: int = 100
    arrival_rate: Optional[float] = None       # None = usar do log
    activity_durations: Optional[Dict] = None  # None = usar do log
    variant_filter_percentage: float = 0.8
    random_seed: int = 42
    max_trace_length: int = 1000
```

### ProcessModel

```python
@dataclass
class ProcessModel:
    petri_net: object                          # Rede de Petri
    initial_marking: object
    final_marking: object
    activities: Dict[str, ActivityStatistics]  # Estatísticas por atividade
    arrival_rate: float                        # Taxa de chegada (min)
    quality_metrics: Dict[str, float]          # Fitness, precision, etc
    log_profile: Optional[LogProfile]          # Perfil do log original
    domain: Optional[str]                      # Domínio detectado
```

### SimulationResult

```python
@dataclass
class SimulationResult:
    csv_path: Path
    xes_path: Path
    num_cases_generated: int
    num_events_generated: int
    simulation_time: float
    timestamp: datetime
```

---

## 🌍 Generalização - Funciona com Qualquer Log

O Sim2Log Core é **100% genérico** e funciona com logs de qualquer domínio.

### Atributos Detectados Automaticamente

| Informação | Atributos Suportados |
|------------|---------------------|
| **Atividade** | `concept:name`, `Activity`, `activity`, `event`, `task` |
| **Timestamp** | `time:timestamp`, `timestamp`, `Time`, `start_time` |
| **Case ID** | `concept:name`, `case_id`, `CaseID`, `Case` |
| **Recurso** | `org:resource`, `resource`, `user`, `actor`, `performer` |

### Domínios Detectados

- 🏥 **Healthcare**: patient, doctor, surgery, exam, treatment
- 💰 **Finance**: payment, invoice, transaction, loan, credit
- 🛒 **Retail**: order, shipping, delivery, purchase, customer
- 🏭 **Manufacturing**: assembly, production, quality, machine
- 📄 **Insurance**: claim, policy, premium, coverage
- ⚖️ **Legal**: case, court, hearing, verdict, filing
- 💻 **IT Service**: incident, ticket, request, escalation

### Exemplo Multi-Domínio

```python
from core import ProcessMiner

# Hospitalar
model_health = ProcessMiner().mine_process("hospital_log.xes")
print(model_health.domain)  # → "healthcare"

# Financeiro
model_finance = ProcessMiner().mine_process("bank_log.xes")
print(model_finance.domain)  # → "finance"

# Qualquer outro
model_custom = ProcessMiner().mine_process("custom_log.xes")
# Funciona mesmo sem detectar domínio específico!
```

---

## 📊 Conversão de Excel para XES

Para processar dados em Excel (ex: dados de cirurgias):

```python
from core.converters import convert_cirurgias_xlsx_to_xes
from core import ProcessMiner, LogSimulator, SimulationConfig

# 1. Converte Excel → XES
xes_path = convert_cirurgias_xlsx_to_xes("dados_cirurgias.xlsx")

# 2. Processa normalmente
model = ProcessMiner().mine_process(xes_path)
config = SimulationConfig(num_cases=100)
result = LogSimulator(config).simulate(model)
```

**Documentação completa:** `converters/README_CIRURGIAS.md`

---

## 🧪 Exemplos

### Exemplo Básico

```bash
PYTHONPATH=. python core/quicktest.py
```

Executa teste rápido (10 casos) para validar instalação.

### Exemplo Completo

```bash
PYTHONPATH=. python core/example.py
```

Pipeline completo:
1. Mineração de processo
2. Configuração da simulação
3. Execução e geração de logs
4. Validação e interpretação

### Dados de Cirurgias (Excel)

```bash
pip install openpyxl  # Necessário para Excel
PYTHONPATH=. python core/converters/example_cirurgias.py seus_dados.xlsx
```

---

## 📁 Estrutura do Projeto

```
core/
├── __init__.py              # API principal
├── models.py                # Modelos de dados (dataclasses)
├── process_mining.py        # Mineração e extração de parâmetros
├── simulation.py            # Motor de simulação SimPy
├── validation.py            # Validação de logs
├── log_analyzer.py          # Análise automática de logs
├── utils.py                 # Utilitários auxiliares
│
├── example.py               # Exemplo completo de uso
├── quicktest.py             # Teste rápido (validação)
│
├── converters/              # Conversores de formatos
│   ├── __init__.py
│   ├── excel_to_xes.py      # Conversor Excel → XES
│   ├── example_cirurgias.py # Exemplo com dados de cirurgias
│   └── README_CIRURGIAS.md  # Documentação específica
│
├── requirements-core.txt    # Dependências mínimas
└── README.md                # Este arquivo
```

---

## 🔬 Fluxo de Dados

```
Log XES Original
      ↓
[LogAnalyzer]
   • Detecta atributos
   • Identifica domínio
   • Valida compatibilidade
      ↓
[ProcessMiner]
   • Inductive Miner → Rede de Petri
   • Extrai estatísticas temporais
   • Identifica distribuições (Normal, Log-Normal, Exponencial)
   • Avalia qualidade (Fitness, Precisão, Simplicidade)
      ↓
ProcessModel
      ↓
[LogSimulator]
   • Cria ambiente SimPy
   • Executa casos seguindo semântica da Rede de Petri
   • Registra eventos com timestamps
      ↓
CSV + XES Sintético
      ↓
[LogValidator]
   • Calcula alinhamentos (edit distance)
   • Computa fitness e custo
      ↓
ValidationResult
```

---

## 💡 Casos de Uso

### 1. Geração de Dados de Teste

```python
# Gera 1000 casos sintéticos para testes
config = SimulationConfig(num_cases=1000)
result = LogSimulator(config).simulate(model, output_dir="test_data")
```

### 2. Anonimização de Logs

```python
# Gera logs com mesmas características estruturais
# mas sem dados sensíveis do log original
model = ProcessMiner().mine_process("sensitive_log.xes")
result = LogSimulator(config).simulate(model, output_dir="anonymous")
```

### 3. Simulação de Cenários

```python
# "E se reduzirmos 50% o tempo de cada atividade?"
custom_durations = {
    activity: stats.mean_duration * 0.5
    for activity, stats in model.activities.items()
}
config = SimulationConfig(
    num_cases=100,
    activity_durations=custom_durations
)
result = LogSimulator(config).simulate(model)
```

### 4. Benchmark de Algoritmos

```python
# Gera datasets controlados para avaliar algoritmos
for seed in range(10):
    config = SimulationConfig(num_cases=500, random_seed=seed)
    result = LogSimulator(config).simulate(model, output_dir=f"dataset_{seed}")
```

### 5. Planejamento de Capacidade

```python
# Simula diferentes taxas de chegada
for arrival_rate in [1.0, 2.0, 5.0, 10.0]:
    config = SimulationConfig(
        num_cases=200,
        arrival_rate=arrival_rate
    )
    result = LogSimulator(config).simulate(model, output_dir=f"rate_{arrival_rate}")
```

---

## 🐛 Troubleshooting

### Erro: `InvalidVersion` do pm4py

**Solução:** Já resolvido automaticamente. O código faz patch no módulo `deprecation`.

### Erro: `ModuleNotFoundError: No module named 'core'`

**Solução:** Execute com `PYTHONPATH=.`:
```bash
PYTHONPATH=. python core/example.py
```

### Erro: Log não encontrado

**Solução:** Use caminhos absolutos ou relativos corretos:
```python
from pathlib import Path
log_path = Path("/caminho/completo/log.xes")
```

### Simulação muito lenta

**Solução:** Reduza número de casos ou aumente taxa de chegada:
```python
config = SimulationConfig(
    num_cases=10,       # Menos casos
    arrival_rate=0.1    # Chegadas mais rápidas
)
```

### Muitas variantes no log

**Solução:** Aumente a filtragem:
```python
model = ProcessMiner().mine_process(
    "log.xes",
    variant_filter=0.95  # Mantém apenas 95% mais frequentes
)
```

---

## 📊 Métricas e Interpretação

### Métricas de Mineração

| Métrica | Faixa | Interpretação |
|---------|-------|---------------|
| **Fitness** | 0-1 | Quão bem o modelo explica o log |
| | >0.9 | Excelente |
| | 0.7-0.9 | Bom |
| | <0.7 | Ruim - modelo inadequado |
| **Precisão** | 0-1 | Quão preciso é o modelo |
| | >0.8 | Modelo preciso |
| | <0.5 | Modelo muito genérico |
| **Simplicidade** | 0-1 | Simplicidade estrutural |
| | >0.7 | Modelo simples |
| | <0.4 | Modelo complexo |

### Métricas de Validação

| Métrica | Interpretação |
|---------|---------------|
| **Fitness** | Similaridade entre log original e simulado |
| >0.9 | Logs muito similares |
| 0.7-0.9 | Boa similaridade |
| <0.5 | Logs diferentes |
| **Cost** | Custo de alinhamento (menor = melhor) |
| 0 | Logs idênticos |
| <10 | Muito similares |
| >50 | Diferentes |

---

## 🔧 Configurações Avançadas

### Customizar Durações Específicas

```python
config = SimulationConfig(
    num_cases=100,
    activity_durations={
        "Register Request": 60.0,    # 60 segundos
        "Examine": 300.0,            # 5 minutos
        "Decide": 120.0              # 2 minutos
        # Outras atividades usam valor do log
    }
)
```

### Desabilitar Auto-Detecção

```python
# Se você sabe que seu log é padrão XES
model = ProcessMiner().mine_process(
    "log.xes",
    auto_detect=False  # Pula análise automática
)
```

### Controlar Reprodutibilidade

```python
config = SimulationConfig(
    num_cases=100,
    random_seed=42  # Mesma seed = mesmos resultados
)
```

---

## 📖 Publicações e Referências

### Técnicas Utilizadas

1. **Process Mining**: van der Aalst, W. (2016). Process Mining: Data Science in Action
2. **Inductive Miner**: Leemans, S. J. J., et al. (2013). Discovering Block-Structured Process Models
3. **Petri Nets**: Peterson, J. L. (1981). Petri Net Theory and the Modeling of Systems
4. **Discrete Event Simulation**: Team SimPy (2020). SimPy Documentation
5. **PM4Py**: Berti, A., et al. (2019). PM4Py: A Process Mining Library

### Bibliotecas

- **pm4py** - Process mining e manipulação de logs
- **simpy** - Simulação de eventos discretos
- **scipy** - Análise estatística e distribuições
- **pandas** - Manipulação de dados

---

## 🤝 Contribuindo

Este é um projeto de pesquisa. Para contribuir:

1. Mantenha o código limpo e documentado
2. Adicione type hints em todas as funções
3. Escreva docstrings completas
4. Teste com múltiplos domínios
5. Mantenha compatibilidade com logs XES padrão

---

## 📝 Licença

Mesmo do projeto original. Ver `LICENSE` no diretório raiz.

---

## 🎓 Autores

- **Projeto Original**: Sim2Log (estudo de caso hospitalar)
- **Core v2.0 (Refatorado)**: Versão genérica, modular e profissional

---

## 📞 Suporte

Para questões ou problemas:

1. Consulte esta documentação
2. Execute `python core/quicktest.py` para validar instalação
3. Veja exemplos em `core/example.py`
4. Para dados de cirurgias: `core/converters/README_CIRURGIAS.md`

---

## 🎉 Conclusão

O Sim2Log Core v2.0 é uma biblioteca **profissional**, **genérica** e **robusta** para:

✅ Minerar processos de qualquer domínio  
✅ Gerar logs sintéticos realistas  
✅ Validar qualidade dos logs  
✅ Simular cenários alternativos  
✅ Processar dados em diferentes formatos  

**Pronto para produção e uso em pesquisa!**

---

**Início Rápido:**

```bash
cd /home/bregoli/Code/Sim2Log-main
source venv/bin/activate
PYTHONPATH=. python core/quicktest.py
```

**Happy Process Mining!** 🚀
