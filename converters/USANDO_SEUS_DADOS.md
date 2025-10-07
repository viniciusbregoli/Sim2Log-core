# 🎯 Guia: Usando Seus Dados de Cirurgias

## Resumo Rápido

Você tem um arquivo **Excel (.xlsx)** com dados de cirurgias. Criei um **conversor automático** que transforma esses dados em logs de processo e permite:

✅ Visualizar o fluxo cirúrgico  
✅ Identificar gargalos  
✅ Simular novos cenários  
✅ Gerar dados sintéticos  

---

## 🚀 Uso em 3 Passos

### 1. Instalar Dependência Extra

```bash
cd /home/bregoli/Code/Sim2Log-main
source venv/bin/activate
pip install openpyxl
```

### 2. Processar Seus Dados

```bash
# Coloque seu arquivo Excel no diretório
# Exemplo: cirurgias_2024.xlsx

PYTHONPATH=. python core/converters/example_cirurgias.py cirurgias_2024.xlsx
```

### 3. Ver Resultados

Arquivos gerados em `output_cirurgias/`:
- `modelo_processo.png` - Visualização do fluxo
- `cirurgias_simuladas.csv` - Dados sintéticos (CSV)
- `cirurgias_simuladas.xes` - Dados sintéticos (XES)

---

## 📊 O Que Seus Dados Contêm

### Colunas Identificadas

| Tipo | Colunas |
|------|---------|
| **ID** | `NR_CIRURGIA`, `NR_ATENDIMENTO` |
| **Timestamps** | `CHAMADA_CC`, `CHEGADA_CC`, `ENTRADA_SALA`, `INICIO_ANESTESIA`, `TERMINO_INDUCAO_ANEST`, `INICIO_PROC_CIRURGICO`, `TERMINO_PROC_CIRURGICO`, `TERMINO_ANESTESIA`, `ENTRADA_RPA`, `SAIDA_RPA_CC`, etc |
| **Recursos** | `NM_CIRURGIAO`, `NM_ANESTESISTA`, `SALA` |
| **Outros** | `DS_PROCEDIMENTO`, `DS_STATUS_CIRURGIA`, etc |

### Fluxo Típico Detectado

```
1. Chamada CC
   ↓
2. Chegada CC
   ↓
3. Entrada Sala
   ↓
4. Início Anestesia
   ↓
5. Término Indução
   ↓
6. Início Cirurgia
   ↓
7. Término Cirurgia
   ↓
8. Término Anestesia
   ↓
9. Entrada RPA
   ↓
10. Saída RPA
    ↓
11. Alta ou UTI
```

---

## 💻 Uso Programático

### Exemplo Básico

```python
from core.converters import convert_cirurgias_xlsx_to_xes
from core import ProcessMiner, LogSimulator, SimulationConfig

# 1. Converte Excel → XES
xes = convert_cirurgias_xlsx_to_xes("seus_dados.xlsx")

# 2. Minera processo
model = ProcessMiner().mine_process(xes, auto_detect=True)

# 3. Simula
config = SimulationConfig(num_cases=100)
result = LogSimulator(config).simulate(model)

print(f"✓ {result.num_cases_generated} cirurgias sintéticas geradas!")
```

### Análise Rápida

```python
from core import analyze_log

profile = analyze_log("seus_dados.xes")

print(f"Cirurgias: {profile.num_traces}")
print(f"Etapas: {profile.num_unique_activities}")
print(f"Duração média: {profile.avg_trace_length} etapas")
print(f"Domínio: {profile.suggested_domain}")
```

### Identificar Gargalos

```python
model = ProcessMiner().mine_process("seus_dados.xes")

# Lista etapas por duração (mais demoradas primeiro)
etapas = sorted(
    model.activities.items(),
    key=lambda x: x[1].mean_duration,
    reverse=True
)

print("Etapas mais demoradas:")
for nome, stats in etapas[:5]:
    print(f"  {nome}: {stats.mean_duration/60:.1f} minutos")
```

### Simular Cenários

```python
# Cenário: Reduzir 30% o tempo de cada etapa
tempos_otimizados = {
    atividade: stats.mean_duration * 0.7
    for atividade, stats in model.activities.items()
}

config = SimulationConfig(
    num_cases=200,
    activity_durations=tempos_otimizados
)

result = LogSimulator(config).simulate(model, output_dir="cenario_otimizado")
print(f"Simulação concluída: {result.xes_path}")
```

---

## 📈 Análises Possíveis

### 1. Taxa de Cirurgias

```python
model = ProcessMiner().mine_process("dados.xes")
print(f"Taxa: {60/model.arrival_rate:.1f} cirurgias/hora")
print(f"Ou: {24*60/model.arrival_rate:.0f} cirurgias/dia")
```

### 2. Duração por Etapa

```python
for atividade, stats in model.activities.items():
    print(f"{atividade}:")
    print(f"  Média: {stats.mean_duration/60:.1f} min")
    print(f"  Distribuição: {stats.distribution_name}")
```

### 3. Variantes do Fluxo

```python
from core import LogAnalyzer

analyzer = LogAnalyzer()
profile = analyzer.analyze("dados.xes")

print(f"Total de variantes: {profile.num_variants}")
print(f"\nTop 5 mais comuns:")
for variante, freq in profile.most_common_variants[:5]:
    print(f"  {len(variante)} etapas: {freq} casos")
```

### 4. Utilização de Recursos

```python
model = ProcessMiner().mine_process("dados.xes")

for atividade, recursos in model.resources.items():
    print(f"{atividade}:")
    print(f"  Recursos: {', '.join(recursos)}")
```

---

## 🔧 Configurações Avançadas

### Especificar Colunas Manualmente

Se a auto-detecção não funcionar:

```python
from core.converters import ExcelToXESConverter

converter = ExcelToXESConverter()
converter.convert(
    excel_path="dados.xlsx",
    output_xes="dados.xes",
    case_id_column="NR_CIRURGIA",
    timestamp_columns=[
        "CHAMADA_CC",
        "CHEGADA_CC",
        "ENTRADA_SALA",
        "INICIO_ANESTESIA",
        # ... adicione todas as colunas de timestamp
    ],
    resource_column="NM_CIRURGIAO"
)
```

### Filtrar Variantes Raras

```python
# Mantém apenas 95% das variantes mais frequentes
model = ProcessMiner().mine_process(
    "dados.xes",
    variant_filter=0.95
)
```

### Simulação com Taxa Customizada

```python
config = SimulationConfig(
    num_cases=500,
    arrival_rate=15.0,  # 15 minutos entre cirurgias
    random_seed=42
)
```

---

## 📂 Estrutura de Arquivos

Após executar, você terá:

```
/home/bregoli/Code/Sim2Log-main/
├── seus_dados.xlsx                    # Seu arquivo original
├── seus_dados.xes                     # Log convertido
└── output_cirurgias/
    ├── modelo_processo.png            # Visualização do fluxo
    ├── cirurgias_simuladas.csv        # Dados sintéticos (CSV)
    └── cirurgias_simuladas.xes        # Dados sintéticos (XES)
```

---

## 🎯 Casos de Uso

### 1. Planejamento de Capacidade

"Quantas cirurgias conseguimos fazer por dia?"

```python
model = ProcessMiner().mine_process("dados.xes")
taxa_por_dia = 24 * 60 / model.arrival_rate
print(f"Capacidade atual: ~{taxa_por_dia:.0f} cirurgias/dia")
```

### 2. Análise de Tempos de Espera

```python
# Tempo entre chegada e início da anestesia
# (calcule diferença entre timestamps)
```

### 3. Otimização de Recursos

```python
# Identifica quais cirurgiões fazem mais cirurgias
for cirurgiao, count in profile.resource_frequencies.items():
    print(f"{cirurgiao}: {count} cirurgias")
```

### 4. Dados para Treinamento/Testes

```python
# Gera 1000 cirurgias sintéticas para treinar ML
config = SimulationConfig(num_cases=1000)
result = LogSimulator(config).simulate(model)

# Usa CSV para ML
import pandas as pd
df = pd.read_csv(result.csv_path)
# Treina modelo, testa sistema, etc
```

---

## 🐛 Problemas Comuns

### "Não encontrou coluna de timestamp"

**Solução:** Especifique manualmente (veja "Configurações Avançadas")

### "Muitas variantes"

**Solução:** Aumente o filtro:
```python
model = ProcessMiner().mine_process("dados.xes", variant_filter=0.9)
```

### "Dados faltando"

Timestamps vazios são ignorados automaticamente. É normal ter alguns vazios.

---

## 📚 Documentação Adicional

- **`README_CIRURGIAS.md`**: Guia detalhado sobre dados de cirurgia
- **`core/README.md`**: Documentação completa do Sim2Log Core
- **`core/GUIDE.md`**: Guia técnico detalhado
- **`core/GENERALIZATION.md`**: Como funciona a generalização

---

## ✅ Checklist

- [ ] Instalar `openpyxl`: `pip install openpyxl`
- [ ] Colocar arquivo Excel no diretório
- [ ] Executar: `python core/converters/example_cirurgias.py seu_arquivo.xlsx`
- [ ] Ver resultados em `output_cirurgias/`
- [ ] Analisar modelo visual: `modelo_processo.png`
- [ ] Usar dados sintéticos conforme necessário

---

## 🎉 Pronto!

Seu arquivo Excel de cirurgias agora pode ser:
- ✅ Convertido automaticamente para XES
- ✅ Analisado com Process Mining
- ✅ Visualizado como fluxo de processo
- ✅ Simulado para gerar novos cenários
- ✅ Usado para gerar dados sintéticos

**Tudo automaticamente e genérico!** 🚀

---

**Dúvidas?** Execute com `--help`:
```bash
python core/converters/example_cirurgias.py --help
```

