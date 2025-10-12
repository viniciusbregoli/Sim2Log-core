# Interface Web Sim2Log

Interface web interativa para executar mineração, simulação e validação de logs de eventos.

## Instalação

Instale as dependências adicionais para a interface web:

```bash
pip install streamlit Pillow
```

Ou use o arquivo de requirements:

```bash
pip install -r app/requirements.txt
```

## Como Executar

No diretório raiz do projeto (`/home/bregoli/Code/core`), execute:

```bash
streamlit run app/app.py
```

A aplicação será aberta automaticamente no seu navegador em `http://localhost:8501`

## Funcionalidades

### 1. Upload de Arquivo
- Carregue arquivos XES pela barra lateral
- Suporte para arquivos de qualquer domínio

### 2. Modos de Execução

#### Modo "Executar Tudo"
- Executa todas as 4 etapas de uma vez:
  1. Análise do log
  2. Mineração do processo
  3. Simulação de casos
  4. Validação dos resultados
- Ideal para execução rápida e completa

#### Modo "Por Etapas"
- Controle individual de cada etapa
- 4 tabs separadas para cada fase
- Visualize resultados de cada etapa antes de prosseguir
- Ideal para análise detalhada e ajustes

### 3. Configurações Ajustáveis

**Mineração:**
- Filtro de variantes (0.0 - 1.0)

**Simulação:**
- Número de casos a gerar
- Taxa de chegada customizada (opcional)

### 4. Visualizações

**Análise do Log:**
- Métricas: casos, eventos, atividades, variantes
- Atributos detectados automaticamente
- Top 5 atividades mais frequentes

**Mineração:**
- Métricas de qualidade (fitness, precision, simplicity)
- Diagrama da Rede de Petri (visual)
- Estatísticas de atividades e durações

**Simulação:**
- Casos e eventos gerados
- Tempo de execução
- Download de arquivos CSV e XES

**Validação:**
- Fitness, custo e similaridade
- Interpretação automática dos resultados
- Detalhes dos alinhamentos

## Estrutura de Pastas

```
app/
├── app.py              # Aplicação principal
├── requirements.txt    # Dependências
├── README.md          # Este arquivo
├── uploads/           # Arquivos XES carregados (criado automaticamente)
└── outputs/           # Resultados gerados (criado automaticamente)
```

## Exemplos de Uso

### Caso de Uso 1: Análise Rápida
1. Upload do arquivo XES
2. Escolha "Executar Tudo"
3. Clique em "Executar Pipeline Completo"
4. Visualize todos os resultados

### Caso de Uso 2: Ajuste Fino
1. Upload do arquivo XES
2. Escolha "Por Etapas"
3. Execute análise e mineração
4. Ajuste parâmetros de simulação conforme necessário
5. Execute simulação e validação
6. Repita ajustando parâmetros se necessário

### Caso de Uso 3: Exploração de Parâmetros
1. Execute com diferentes filtros de variantes
2. Compare diagramas de Petri gerados
3. Teste diferentes quantidades de casos
4. Analise impacto na qualidade (fitness)

## Atalhos do Streamlit

- `R` - Recarregar aplicação
- `C` - Limpar cache
- `Ctrl+C` (no terminal) - Parar servidor

## Troubleshooting

**Erro ao carregar arquivo:**
- Verifique se o arquivo é XES válido
- Certifique-se que o arquivo não está corrompido

**Interface lenta:**
- Reduza o número de casos na simulação
- Use filtro de variantes mais agressivo (ex: 0.9)

**Diagrama não aparece:**
- Verifique se a mineração foi executada
- Confirme se graphviz está instalado no sistema

**Erro de módulo não encontrado:**
- Execute do diretório raiz do projeto
- Verifique se todas as dependências estão instaladas

## Notas

- Arquivos carregados ficam em `app/uploads/`
- Resultados são salvos em `app/outputs/`
- Cada execução gera arquivos com timestamp único
- Arquivos antigos não são deletados automaticamente

