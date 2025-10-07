# 🏥 Processamento de Dados de Cirurgias

## O Que Seus Dados Contêm

Seu arquivo Excel tem dados de **processos de centro cirúrgico** com:

### 📋 Identificadores
- **NR_CIRURGIA**: ID único da cirurgia
- **NR_ATENDIMENTO**: ID do atendimento
- **NOME_PACIENTE**: Nome do paciente

### ⏰ Timestamps das Etapas (Atividades)

Seu processo tem as seguintes etapas com timestamps:

| Etapa | Coluna | Descrição |
|-------|--------|-----------|
| 1. Chamada | `CHAMADA_CC` | Paciente chamado para o CC |
| 2. Chegada | `CHEGADA_CC` | Chegada no Centro Cirúrgico |
| 3. Entrada | `ENTRADA_SALA` | Entrada na sala cirúrgica |
| 4. Início Anestesia | `INICIO_ANESTESIA` | Começo da anestesia |
| 5. Término Indução | `TERMINO_INDUCAO_ANEST` | Fim da indução anestésica |
| 6. Início Cirurgia | `INICIO_PROC_CIRURGICO` | Início do procedimento |
| 7. Término Cirurgia | `TERMINO_PROC_CIRURGICO` | Fim do procedimento |
| 8. Término Anestesia | `TERMINO_ANESTESIA` | Fim da anestesia |
| 9. Entrada RPA | `ENTRADA_RPA` | Entrada na Recuperação Pós-Anestésica |
| 10. Saída RPA | `SAIDA_RPA_CC` | Saída da RPA |
| 11. Encaminhamento UTI | `ENCAMINHAMENTO_UTI` | Se foi para UTI |
| 12. Alta | `ALTA_HOSP` | Alta hospitalar |

### 👥 Recursos
- **NM_CIRURGIAO**: Cirurgião responsável
- **NM_ANESTESISTA**: Anestesista
- **SALA**: Sala cirúrgica

### 📊 Outros Atributos
- **DS_PROCEDIMENTO**: Descrição do procedimento
- **DS_STATUS_CIRURGIA**: Status (concluída, cancelada, etc)
- **DS_MOTIVO_CANCEL**: Se cancelada, o motivo
- **NR_MIN_DURACAO_REAL**: Duração em minutos

---

## 🚀 Como Usar

### 1. Instalação de Dependência Extra

```bash
pip install openpyxl  # Para ler arquivos Excel
```

### 2. Uso Básico

```bash
cd /home/bregoli/Code/Sim2Log-main
source venv/bin/activate

# Processa seus dados
PYTHONPATH=. python core/converters/example_cirurgias.py seu_arquivo.xlsx
```

### 3. Uso Programático

```python
from core.converters import convert_cirurgias_xlsx_to_xes
from core import ProcessMiner, LogSimulator, SimulationConfig

# 1. Converte Excel para XES
xes_path = convert_cirurgias_xlsx_to_xes("cirurgias.xlsx")

# 2. Minera processo
miner = ProcessMiner()
model = miner.mine_process(xes_path)

# 3. Simula novos casos
config = SimulationConfig(num_cases=100)
result = LogSimulator(config).simulate(model)

print(f"Geradas {result.num_cases_generated} cirurgias sintéticas!")
```

---

## 📊 O Que o Conversor Faz

### Transformação de Dados

**Antes (Excel - Formato Wide):**
```
NR_CIRURGIA | CHAMADA_CC          | ENTRADA_SALA        | INICIO_PROC_CIRURGICO | ...
-----------|---------------------|---------------------|----------------------|----
001        | 2024-01-15 08:00:00 | 2024-01-15 08:15:00 | 2024-01-15 08:30:00  | ...
002        | 2024-01-15 09:00:00 | 2024-01-15 09:12:00 | 2024-01-15 09:25:00  | ...
```

**Depois (XES - Formato Long - Event Log):**
```
Case ID | Activity                      | Timestamp           | Resource
--------|-------------------------------|---------------------|----------
001     | Chamada Centro Cirúrgico      | 2024-01-15 08:00:00 | Sala 1
001     | Entrada Sala                  | 2024-01-15 08:15:00 | Sala 1
001     | Início Procedimento Cirúrgico | 2024-01-15 08:30:00 | Dr. Silva
002     | Chamada Centro Cirúrgico      | 2024-01-15 09:00:00 | Sala 2
002     | Entrada Sala                  | 2024-01-15 09:12:00 | Sala 2
...
```

### Detecções Automáticas

O conversor detecta automaticamente:

1. ✅ **Case ID**: `NR_CIRURGIA` ou `NR_ATENDIMENTO`
2. ✅ **Timestamps**: Todas colunas com `CHAMADA`, `CHEGADA`, `ENTRADA`, `INICIO`, `TERMINO`, `SAIDA`
3. ✅ **Recursos**: `NM_CIRURGIAO`, `NM_ANESTESISTA`, `SALA`
4. ✅ **Atributos extras**: Procedimento, status, sala

---

## 🔍 Análises Possíveis

Depois de converter para XES, você pode:

### 1. Visualizar o Fluxo do Processo

```python
miner = ProcessMiner()
model = miner.mine_process(
    "cirurgias.xes",
    save_model_image="fluxo_cirurgico.png"
)
# Gera imagem do fluxo cirúrgico
```

### 2. Identificar Gargalos

```python
for activity, stats in model.activities.items():
    print(f"{activity}: {stats.mean_duration/60:.1f} min (média)")
```

**Exemplo de saída:**
```
Chamada Centro Cirúrgico: 5.2 min
Entrada Sala: 12.5 min
Início Anestesia: 8.3 min
Início Procedimento Cirúrgico: 15.7 min ← GARGALO!
Término Procedimento Cirúrgico: 85.3 min
```

### 3. Simular Cenários

```python
# E se reduzirmos 30% o tempo de cada etapa?
custom_durations = {
    activity: stats.mean_duration * 0.7
    for activity, stats in model.activities.items()
}

config = SimulationConfig(
    num_cases=200,
    activity_durations=custom_durations
)

result = LogSimulator(config).simulate(model)
# Simula 200 cirurgias com tempos reduzidos
```

### 4. Análise de Variantes

```python
from core import analyze_log

profile = analyze_log("cirurgias.xes")
print(f"Variantes do fluxo: {profile.num_variants}")

# Mostra variantes mais comuns
for variant, count in profile.most_common_variants[:5]:
    print(f"  {variant}: {count} casos")
```

**Exemplo:**
```
Variantes do fluxo: 23

Top variantes:
  1. Chamada → Entrada → Anestesia → Cirurgia → RPA → Alta: 156 casos
  2. Chamada → Entrada → Anestesia → Cirurgia → RPA → UTI: 45 casos
  3. Chamada → Entrada → Cancelamento: 12 casos
  ...
```

### 5. Análise de Recursos

```python
print(f"Recursos: {model.resources}")

# Exemplo de saída:
# {
#   'Início Procedimento Cirúrgico': ['Dr. Silva', 'Dr. Santos', 'Dr. Lima'],
#   'Início Anestesia': ['Dr. Costa', 'Dr. Almeida'],
#   ...
# }
```

---

## 📈 Métricas Extraídas

Ao processar seus dados, o Sim2Log calcula:

### Métricas Temporais
- ⏱️ **Taxa de chegada**: Quantas cirurgias entram por hora/dia
- ⏱️ **Duração média**: Tempo médio de cada etapa
- ⏱️ **Duração total**: Tempo do início ao fim
- ⏱️ **Tempo entre etapas**: Esperas/atrasos

### Métricas de Processo
- 📊 **Fitness**: Qualidade do modelo (0-1)
- 📊 **Precisão**: Quão preciso é o modelo
- 📊 **Complexidade**: Número de variantes

### Métricas de Recursos
- 👥 **Utilização**: Quem faz o quê
- 👥 **Carga de trabalho**: Quantas cirurgias por cirurgião
- 👥 **Disponibilidade**: Recursos disponíveis

---

## 🎯 Casos de Uso

### 1. Planejamento de Capacidade

```python
# Quantas cirurgias conseguimos fazer por dia?
model = ProcessMiner().mine_process("cirurgias.xes")
print(f"Taxa atual: {60/model.arrival_rate:.1f} cirurgias/hora")

# Simula cenário com 50% mais cirurgias
config = SimulationConfig(
    num_cases=300,
    arrival_rate=model.arrival_rate * 0.5  # Metade do tempo entre chegadas
)
result = LogSimulator(config).simulate(model)
```

### 2. Análise de Cancelamentos

```python
# Identifica padrões de cancelamento
analyzer = LogAnalyzer()
profile = analyzer.analyze("cirurgias.xes")

# Filtra apenas cirurgias canceladas
# (adicione lógica para filtrar status)
```

### 3. Otimização de Fluxo

```python
# Identifica etapas mais demoradas
durations = {
    activity: stats.mean_duration
    for activity, stats in model.activities.items()
}

sorted_durations = sorted(durations.items(), key=lambda x: x[1], reverse=True)
print("Etapas mais demoradas:")
for activity, duration in sorted_durations[:5]:
    print(f"  {activity}: {duration/60:.1f} min")
```

### 4. Treinamento e Testes

```python
# Gera dados sintéticos para treinar sistemas
config = SimulationConfig(num_cases=1000)
result = LogSimulator(config).simulate(model)

# Use result.csv_path para ML, testes, etc
df = pd.read_csv(result.csv_path)
```

---

## 🐛 Troubleshooting

### Problema: "Coluna não encontrada"

**Solução**: Especifique manualmente as colunas:

```python
from core.converters import ExcelToXESConverter

converter = ExcelToXESConverter()
converter.convert(
    "cirurgias.xlsx",
    "cirurgias.xes",
    case_id_column="SUA_COLUNA_ID",
    timestamp_columns=["COL1", "COL2", "COL3"],
    resource_column="SUA_COLUNA_RECURSO"
)
```

### Problema: "Timestamps inválidos"

Verifique o formato das datas no Excel. Devem ser:
- Formato de data: `DD/MM/YYYY` ou `YYYY-MM-DD`
- Formato de hora: `HH:MM:SS`

### Problema: "Muitas variantes"

Se houver muitas variantes (>100), use filtragem:

```python
model = ProcessMiner().mine_process(
    "cirurgias.xes",
    variant_filter=0.9  # Mantém apenas 90% mais frequentes
)
```

---

## 📚 Exemplo Completo

```python
#!/usr/bin/env python3
"""
Pipeline completo de análise de cirurgias.
"""

from pathlib import Path
from core.converters import convert_cirurgias_xlsx_to_xes
from core import (
    ProcessMiner,
    LogSimulator,
    LogValidator,
    LogAnalyzer,
    SimulationConfig
)

# 1. CONVERTE
print("Convertendo Excel...")
xes_path = convert_cirurgias_xlsx_to_xes("dados_cirurgias.xlsx")

# 2. ANALISA
print("Analisando...")
profile = LogAnalyzer().analyze(xes_path)
print(f"  {profile.num_traces} cirurgias")
print(f"  {profile.num_unique_activities} etapas")

# 3. MINERA
print("Minerando processo...")
model = ProcessMiner().mine_process(
    xes_path,
    save_model_image="fluxo_cirurgico.png"
)
print(f"  Fitness: {model.quality_metrics['fitness']:.2%}")

# 4. SIMULA
print("Simulando 100 cirurgias...")
config = SimulationConfig(num_cases=100)
result = LogSimulator(config).simulate(model, output_dir="resultados")

# 5. VALIDA
print("Validando...")
validation = LogValidator().validate(xes_path, result.xes_path)
print(f"  Similaridade: {validation.similarity_percentage:.1f}%")

print("\n✓ Pipeline concluído!")
print(f"  Modelo: fluxo_cirurgico.png")
print(f"  Simulação: {result.xes_path}")
```

---

## 🎉 Resultado Final

Após processar seus dados, você terá:

1. **Log XES** com todas as cirurgias em formato padronizado
2. **Modelo visual** do fluxo cirúrgico (Rede de Petri)
3. **Estatísticas** de cada etapa (duração, frequência)
4. **Logs sintéticos** para testes, treinamento, etc
5. **Métricas de qualidade** do processo

Tudo isso **automaticamente** a partir do seu Excel! 🚀

---

## 💡 Próximos Passos

1. **Coloque seu arquivo Excel** no diretório
2. **Execute o conversor**: `python core/converters/example_cirurgias.py seu_arquivo.xlsx`
3. **Veja os resultados** em `output_cirurgias/`
4. **Use os logs sintéticos** para o que precisar!

**Dúvidas?** Veja a documentação completa em `core/README.md` e `core/GUIDE.md`





