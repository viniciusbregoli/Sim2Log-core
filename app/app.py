"""
Interface Web para Sim2Log Core

Aplicação Streamlit para executar mineração, simulação e validação de logs XES.
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path para importar os módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import tempfile
import shutil
from datetime import datetime
from PIL import Image
import pandas as pd

from process_mining import ProcessMiner
from simulation import LogSimulator
from validation import LogValidator
from models import SimulationConfig
from log_analyzer import LogAnalyzer
from ore_indicators import ORECalculator, OREMetrics, calculate_ore_scenarios


# Configuração da página
st.set_page_config(
    page_title="Process Mining",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """Inicializa o estado da sessão."""
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'log_path' not in st.session_state:
        st.session_state.log_path = None
    if 'xes_path' not in st.session_state:
        st.session_state.xes_path = None
    if 'model' not in st.session_state:
        st.session_state.model = None
    if 'simulation_result' not in st.session_state:
        st.session_state.simulation_result = None
    if 'validation_result' not in st.session_state:
        st.session_state.validation_result = None
    if 'log_profile' not in st.session_state:
        st.session_state.log_profile = None
    if 'model_image_path' not in st.session_state:
        st.session_state.model_image_path = None
    if 'saved_simulations' not in st.session_state:
        st.session_state.saved_simulations = []
    if 'date_filter_enabled' not in st.session_state:
        st.session_state.date_filter_enabled = False
    if 'date_filter_start' not in st.session_state:
        st.session_state.date_filter_start = None
    if 'date_filter_end' not in st.session_state:
        st.session_state.date_filter_end = None
    if 'log_min_date' not in st.session_state:
        st.session_state.log_min_date = None
    if 'log_max_date' not in st.session_state:
        st.session_state.log_max_date = None
    if 'ore_metrics' not in st.session_state:
        st.session_state.ore_metrics = None


def save_uploaded_file(uploaded_file):
    """Salva arquivo carregado temporariamente."""
    try:
        upload_dir = Path("app/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)

        file_path = upload_dir / uploaded_file.name
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        return file_path
    except Exception as e:
        st.error(f"Erro ao salvar arquivo: {e}")
        return None


def extract_log_date_range(log_path):
    """Extrai os timestamps mínimo e máximo do log XES."""
    from pm4py.objects.log.importer.xes import importer as xes_importer

    try:
        log = xes_importer.apply(str(log_path))

        timestamps = []
        for trace in log:
            for event in trace:
                if 'time:timestamp' in event:
                    timestamps.append(event['time:timestamp'])

        if timestamps:
            min_date = min(timestamps).date()
            max_date = max(timestamps).date()
            return min_date, max_date
        else:
            return None, None
    except Exception as e:
        st.warning(f"Erro ao extrair intervalo de datas do log: {e}")
        return None, None


def filter_dataframe_by_date(df, timestamp_column='timestamp'):
    """Filtra dataframe por intervalo de datas se o filtro estiver habilitado."""
    if not st.session_state.date_filter_enabled:
        return df

    if timestamp_column not in df.columns:
        return df

    date_start = st.session_state.date_filter_start
    date_end = st.session_state.date_filter_end

    if not date_start or not date_end:
        return df

    try:
        # Converte coluna de timestamp para datetime se necessário
        if not pd.api.types.is_datetime64_any_dtype(df[timestamp_column]):
            df_filtered = df.copy()
            df_filtered[timestamp_column] = pd.to_datetime(df_filtered[timestamp_column])
        else:
            df_filtered = df.copy()

        # Converte date_start e date_end para datetime
        start_datetime = pd.to_datetime(date_start)
        end_datetime = pd.to_datetime(date_end) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

        # Filtra
        mask = (df_filtered[timestamp_column] >= start_datetime) & (df_filtered[timestamp_column] <= end_datetime)
        df_filtered = df_filtered[mask]

        return df_filtered
    except Exception as e:
        st.warning(f"Erro ao aplicar filtro de datas: {e}")
        return df


def analyze_log(log_path):
    """Analisa o log XES."""
    with st.spinner("Analisando log XES..."):
        analyzer = LogAnalyzer(verbose=False)
        profile = analyzer.analyze(log_path)
        st.session_state.log_profile = profile
        return profile


def run_mining(log_path, variant_filter):
    """Executa mineração de processo."""
    with st.spinner("Executando mineração de processo..."):
        output_dir = Path("app/outputs")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        model_image_path = output_dir / f"process_model_{timestamp}.png"
        
        miner = ProcessMiner(verbose=False)
        model = miner.mine_process(
            log_path,
            variant_filter=variant_filter,
            save_model_image=model_image_path,
            auto_detect=True
        )
        
        st.session_state.model = model
        st.session_state.model_image_path = model_image_path
        
        return model, model_image_path


def run_simulation(model, num_cases, arrival_rate, custom_resources=None):
    """Executa simulação de log."""
    with st.spinner(f"Simulando {num_cases} casos..."):
        output_dir = Path("app/outputs")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Se há recursos customizados, cria uma cópia do modelo com os novos recursos
        if custom_resources:
            from copy import deepcopy
            model_copy = deepcopy(model)
            
            # Filtra recursos vazios antes de usar
            filtered_resources = {}
            for activity, resources in custom_resources.items():
                valid_resources = [r for r in resources if r and str(r).strip()]
                if valid_resources:
                    filtered_resources[activity] = valid_resources
                else:
                    # Se não há recursos válidos, usa os originais
                    filtered_resources[activity] = model.resources.get(activity, [])
            
            model_copy.resources = filtered_resources
            model_to_use = model_copy
            
            # Mostra resumo dos recursos que serão usados
            total_custom = sum(len(r) for r in filtered_resources.values())
            st.info(f"Usando recursos customizados na simulação: {total_custom} recursos em {len(filtered_resources)} atividades")
        else:
            model_to_use = model
        
        config = SimulationConfig(
            num_cases=num_cases,
            arrival_rate=arrival_rate if arrival_rate > 0 else None,
            random_seed=42
        )
        
        simulator = LogSimulator(config, verbose=False)
        result = simulator.simulate(
            model_to_use,
            output_dir=output_dir,
            output_prefix=f"simulated_{timestamp}"
        )
        
        st.session_state.simulation_result = result
        
        return result


def run_validation(original_log_path, simulated_log_path):
    """Executa validação do log simulado."""
    with st.spinner("Validando qualidade do log sintético..."):
        validator = LogValidator(verbose=False)
        validation = validator.validate(original_log_path, simulated_log_path)
        
        st.session_state.validation_result = validation
        
        return validation


def analyze_resource_workload(log_path):
    """Analisa a carga de trabalho dos recursos."""
    from pm4py.objects.log.importer.xes import importer as xes_importer

    try:
        # Carrega o log
        log = xes_importer.apply(str(log_path))

        # Extrai dados de recursos
        resource_data = []
        for trace in log:
            for event in trace:
                if 'org:resource' in event and 'concept:name' in event:
                    resource_data.append({
                        'resource': event['org:resource'],
                        'activity': event['concept:name'],
                        'timestamp': event.get('time:timestamp', None)
                    })

        if not resource_data:
            return None
    except Exception as e:
        st.warning(f"Erro ao analisar recursos: {str(e)}")
        return None

    df = pd.DataFrame(resource_data)

    # Aplica filtro de datas se habilitado
    df = filter_dataframe_by_date(df, 'timestamp')

    # Análises
    workload_analysis = {
        'total_events': df.groupby('resource').size().sort_values(ascending=False),
        'activities_per_resource': df.groupby('resource')['activity'].nunique(),
        'resource_by_activity': df.groupby(['activity', 'resource']).size(),
        'unique_resources': df['resource'].nunique(),
        'dataframe': df
    }

    return workload_analysis


def display_log_profile(profile, log_path=None):
    """Exibe informações do perfil do log."""
    st.subheader("Análise do Log")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Casos", profile.num_traces)
    with col2:
        st.metric("Eventos", profile.num_events)
    with col3:
        st.metric("Atividades", profile.num_unique_activities)
    with col4:
        st.metric("Variantes", profile.num_variants)
    
    with st.expander("Detalhes do Log"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Atributos Detectados:**")
            st.write(f"- Atividade: `{profile.activity_key}`")
            st.write(f"- Timestamp: `{profile.timestamp_key}`")
            st.write(f"- Case ID: `{profile.case_id_key}`")
            st.write(f"- Recurso: `{profile.resource_key or 'N/A'}`")
        
        with col2:
            st.write("**Características:**")
            st.write(f"- Tem recursos: {'Sim' if profile.has_resources else 'Não'}")
            st.write(f"- Tem timestamps de conclusão: {'Sim' if profile.has_complete_timestamps else 'Não'}")
            st.write(f"- Comprimento médio: {profile.avg_trace_length:.1f} eventos")
            st.write(f"- Comprimento máximo: {profile.max_trace_length} eventos")
        
        if profile.activity_frequencies:
            st.write("**Top 5 Atividades:**")
            top_activities = sorted(
                profile.activity_frequencies.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            for activity, count in top_activities:
                pct = (count / profile.num_events) * 100
                st.write(f"- {activity}: {count} ({pct:.1f}%)")
    
    # Análise de Carga de Trabalho dos Recursos
    if log_path and profile.has_resources:
        st.write("---")
        st.subheader("Análise de Carga de Trabalho dos Recursos")

        # Aviso de filtro de datas ativo
        if st.session_state.date_filter_enabled and st.session_state.date_filter_start and st.session_state.date_filter_end:
            st.info(f"Filtro de datas ativo: {st.session_state.date_filter_start} até {st.session_state.date_filter_end}")

        with st.spinner("Analisando carga de trabalho dos recursos..."):
            workload = analyze_resource_workload(log_path)
        
        if workload:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Recursos Únicos", workload['unique_resources'])
            with col2:
                avg_events = workload['total_events'].mean()
                st.metric("Média de Eventos/Recurso", f"{avg_events:.1f}")
            with col3:
                busiest_resource = workload['total_events'].idxmax()
                max_events = workload['total_events'].max()
                st.metric("Recurso Mais Ocupado", f"{busiest_resource}", delta=f"{max_events} eventos")
            
            # Tabs para diferentes visualizações
            tab1, tab2, tab3, tab4 = st.tabs([
                "Ranking Geral",
                "Distribuição de Carga",
                "Por Atividade",
                "Detalhes"
            ])
            
            with tab1:
                st.write("**Top 20 Recursos Mais Ocupados:**")
                top_resources = workload['total_events'].head(20)
                st.bar_chart(top_resources)
                
                # Tabela com detalhes
                top_df = pd.DataFrame({
                    'Recurso': top_resources.index,
                    'Total de Eventos': top_resources.values,
                    'Atividades Diferentes': [workload['activities_per_resource'][r] for r in top_resources.index],
                    '% do Total': [f"{(v/profile.num_events)*100:.1f}%" for v in top_resources.values]
                })
                st.dataframe(top_df, use_container_width=True)
            
            with tab2:
                st.write("**Distribuição de Carga de Trabalho:**")
                
                # Categoriza recursos por carga
                events_per_resource = workload['total_events']
                median_events = events_per_resource.median()
                mean_events = events_per_resource.mean()
                
                # Define categorias
                overloaded = events_per_resource[events_per_resource > mean_events * 1.5]
                high_load = events_per_resource[(events_per_resource > mean_events) & (events_per_resource <= mean_events * 1.5)]
                normal_load = events_per_resource[(events_per_resource >= median_events) & (events_per_resource <= mean_events)]
                low_load = events_per_resource[events_per_resource < median_events]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Categorias de Carga:**")
                    categories = pd.DataFrame({
                        'Categoria': ['Sobrecarregados', 'Carga Alta', 'Carga Normal', 'Carga Baixa'],
                        'Quantidade': [len(overloaded), len(high_load), len(normal_load), len(low_load)],
                        'Critério': [
                            f'> {mean_events*1.5:.0f} eventos',
                            f'{mean_events:.0f} - {mean_events*1.5:.0f} eventos',
                            f'{median_events:.0f} - {mean_events:.0f} eventos',
                            f'< {median_events:.0f} eventos'
                        ]
                    })
                    st.dataframe(categories, use_container_width=True)
                
                with col2:
                    # Gráfico de pizza
                    st.write("**Proporção:**")
                    pie_data = pd.DataFrame({
                        'Categoria': ['Sobrecarregados', 'Carga Alta', 'Normal', 'Baixa'],
                        'Quantidade': [len(overloaded), len(high_load), len(normal_load), len(low_load)]
                    })
                    st.bar_chart(pie_data.set_index('Categoria'))
                
                # Alerta para recursos sobrecarregados
                if len(overloaded) > 0:
                    st.warning(f"{len(overloaded)} recurso(s) sobrecarregado(s) detectado(s)!")
                    with st.expander("Ver recursos sobrecarregados"):
                        for resource, count in overloaded.items():
                            st.write(f"- **{resource}**: {count} eventos ({(count/profile.num_events)*100:.1f}% do total)")
            
            with tab3:
                st.write("**Distribuição de Recursos por Atividade:**")
                
                # Agrupa por atividade
                activity_resource_counts = workload['dataframe'].groupby('activity')['resource'].agg(['count', 'nunique'])
                activity_resource_counts.columns = ['Total Eventos', 'Recursos Únicos']
                activity_resource_counts['Eventos/Recurso'] = (
                    activity_resource_counts['Total Eventos'] / activity_resource_counts['Recursos Únicos']
                ).round(1)
                activity_resource_counts = activity_resource_counts.sort_values('Total Eventos', ascending=False)
                
                st.dataframe(activity_resource_counts, use_container_width=True)
                
                # Detalhe por atividade selecionada
                selected_activity = st.selectbox(
                    "Selecione uma atividade para ver detalhes:",
                    options=activity_resource_counts.index.tolist()
                )
                
                if selected_activity:
                    st.write(f"**Recursos que executaram '{selected_activity}':**")
                    activity_resources = workload['dataframe'][
                        workload['dataframe']['activity'] == selected_activity
                    ]['resource'].value_counts()
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.bar_chart(activity_resources.head(15))
                    with col2:
                        st.write("**Top 10:**")
                        for idx, (resource, count) in enumerate(activity_resources.head(10).items(), 1):
                            st.write(f"{idx}. {resource}: {count}x")
            
            with tab4:
                st.write("**Busca Detalhada de Recurso:**")
                
                # Busca por recurso específico
                all_resources = sorted(workload['total_events'].index.tolist())
                selected_resource = st.selectbox(
                    "Selecione um recurso para análise detalhada:",
                    options=all_resources
                )
                
                if selected_resource:
                    resource_df = workload['dataframe'][workload['dataframe']['resource'] == selected_resource]
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total de Eventos", len(resource_df))
                    with col2:
                        st.metric("Atividades Diferentes", resource_df['activity'].nunique())
                    with col3:
                        pct = (len(resource_df) / profile.num_events) * 100
                        st.metric("% do Total", f"{pct:.2f}%")
                    
                    st.write("**Distribuição de Atividades:**")
                    activity_dist = resource_df['activity'].value_counts()
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.bar_chart(activity_dist)
                    with col2:
                        for activity, count in activity_dist.items():
                            pct = (count / len(resource_df)) * 100
                            st.write(f"**{activity}**")
                            st.write(f"{count} eventos ({pct:.1f}%)")
        else:
            st.info("Este log não contém informações de recursos para análise de carga de trabalho")


def display_mining_results(model, model_image_path):
    """Exibe resultados da mineração."""
    st.subheader("Resultados da Mineração")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Casos Minerados", model.num_cases)
    with col2:
        st.metric("Variantes", model.num_variants)
    with col3:
        st.metric("Atividades", len(model.activities))
    
    # Métricas de qualidade
    st.write("**Métricas de Qualidade do Modelo:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fitness = model.quality_metrics.get('fitness', 0)
        st.metric("Fitness", f"{fitness:.3f}", help="Quão bem o modelo explica o log (0-1)")
    with col2:
        precision = model.quality_metrics.get('precision', 0)
        st.metric("Precision", f"{precision:.3f}", help="Quão preciso é o modelo (0-1)")
    with col3:
        simplicity = model.quality_metrics.get('simplicity', 0)
        st.metric("Simplicity", f"{simplicity:.3f}", help="Simplicidade do modelo (0-1)")
    
    # Tabs para visualizações do modelo
    if model_image_path and model_image_path.exists():
        # Verifica se existe Process Tree
        tree_image_path = model_image_path.parent / f"{model_image_path.stem}_tree{model_image_path.suffix}"

        if tree_image_path.exists():
            # Exibe tabs com ambas visualizações
            viz_tab1, viz_tab2 = st.tabs(["Rede de Petri", "Process Tree"])

            with viz_tab1:
                st.write("**Diagrama de Rede de Petri:**")

                # Adiciona CSS para fundo branco na imagem
                st.markdown(
                    """
                    <style>
                    .stImage {
                        background-color: white;
                        padding: 20px;
                        border-radius: 5px;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True
                )

                image = Image.open(model_image_path)
                st.image(image, caption="Modelo de Processo Descoberto", use_container_width=True)

            with viz_tab2:
                st.write("**Process Tree:**")
                st.caption("Representação hierárquica do processo descoberto")

                tree_image = Image.open(tree_image_path)
                st.image(tree_image, caption="Process Tree", use_container_width=True)

                # Explica a notação
                with st.expander("Entendendo a Process Tree"):
                    st.write("""
                    **Operadores:**
                    - **→ (seq)**: Sequência - atividades executadas em ordem
                    - **× (xor)**: Escolha exclusiva - apenas um caminho é seguido
                    - **+ (and)**: Paralelismo - atividades podem ser intercaladas
                    - **↻ (loop)**: Loop - atividades podem se repetir
                    - **τ (tau)**: Transição silenciosa (invisível)

                    **Como ler:**
                    A árvore mostra a estrutura lógica do processo de cima para baixo.
                    Cada nó representa um operador que controla como as atividades filhas são executadas.
                    """)
        else:
            # Só mostra Petri Net se não houver Process Tree
            st.write("**Diagrama de Rede de Petri:**")

            st.markdown(
                """
                <style>
                .stImage {
                    background-color: white;
                    padding: 20px;
                    border-radius: 5px;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

            image = Image.open(model_image_path)
            st.image(image, caption="Modelo de Processo Descoberto", use_container_width=True)

    # Estatísticas de atividades
    with st.expander("Estatísticas das Atividades"):
        st.write(f"**Taxa de chegada:** {model.arrival_rate:.2f} minutos/caso")
        st.write(f"**Duração mediana:** {model.median_case_duration:.2f} segundos")
        
        st.write("\n**Durações por Atividade:**")
        for activity, stats in model.activities.items():
            st.write(f"- **{activity}**: {stats.mean_duration:.2f}s (distribuição: {stats.distribution_name})")


def display_simulation_results(result, custom_resources=None, original_model=None):
    """Exibe resultados da simulação."""
    st.subheader("Resultados da Simulação")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Casos Gerados", result.num_cases_generated)
    with col2:
        st.metric("Eventos Gerados", result.num_events_generated)
    with col3:
        st.metric("Tempo de Simulação", f"{result.simulation_time:.2f}s")
    with col4:
        # Botão para salvar simulação para comparação
        if st.button("Salvar para Comparar", use_container_width=True):
            df = pd.read_csv(result.csv_path)
            
            simulation_data = {
                'name': f"Simulação {len(st.session_state.saved_simulations) + 1}",
                'timestamp': result.timestamp.strftime("%H:%M:%S"),
                'num_cases': result.num_cases_generated,
                'num_events': result.num_events_generated,
                'csv_path': str(result.csv_path),
                'xes_path': str(result.xes_path),
                'custom_resources': custom_resources,
                'dataframe': df
            }
            st.session_state.saved_simulations.append(simulation_data)
            st.success(f"Simulação salva! Total: {len(st.session_state.saved_simulations)}")
    
    # Exibe comparação de recursos se foram modificados
    if custom_resources and original_model:
        with st.expander("Comparação de Recursos (Original vs Customizado)"):
            changes_found = False
            for activity in sorted(custom_resources.keys()):
                original = original_model.resources.get(activity, [])
                # Filtra apenas recursos válidos
                original = [r for r in original if r and isinstance(r, str)]
                custom = custom_resources.get(activity, [])
                
                if set(original) != set(custom):
                    changes_found = True
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**{activity}**")
                        st.write(f"Original: {', '.join(original) if original else 'Nenhum'}")
                    with col2:
                        st.write("　")  # Espaço para alinhamento
                        st.write(f"Customizado: {', '.join(custom) if custom else 'Nenhum'}")
                    st.divider()
            
            if not changes_found:
                st.info("Nenhuma alteração de recursos foi aplicada")
    
    # Visualização do CSV
    if result.csv_path.exists():
        st.write("**Prévia dos Dados Gerados:**")
        
        df = pd.read_csv(result.csv_path)
        
        # Estatísticas rápidas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Linhas", len(df))
        with col2:
            st.metric("Casos Únicos", df['case_id'].nunique())
        with col3:
            st.metric("Atividades Únicas", df['activity'].nunique())
        
        # Tabs para diferentes visualizações
        tab1, tab2 = st.tabs(["Dados Completos", "Estatísticas"])
        
        with tab1:
            st.dataframe(df, use_container_width=True, height=400)
        
        with tab2:
            st.write("**Frequência de Atividades:**")
            activity_counts = df['activity'].value_counts()
            st.bar_chart(activity_counts)
            
            # Mostra recursos se a coluna existir
            if 'resource' in df.columns:
                st.write("**Recursos Utilizados:**")
                resource_counts = df['resource'].value_counts()
                st.bar_chart(resource_counts)
                
                st.write("**Distribuição de Recursos por Atividade:**")
                for activity in df['activity'].unique():
                    activity_df = df[df['activity'] == activity]
                    if 'resource' in activity_df.columns:
                        resources = activity_df['resource'].value_counts()
                        if len(resources) > 0:
                            st.write(f"- **{activity}**: {', '.join([f'{r} ({c}x)' for r, c in resources.items()])}")
            
            st.write("**Estatísticas de Casos:**")
            case_counts = df.groupby('case_id').size()
            st.write(f"- Média de eventos por caso: {case_counts.mean():.2f}")
            st.write(f"- Mínimo de eventos por caso: {case_counts.min()}")
            st.write(f"- Máximo de eventos por caso: {case_counts.max()}")
    
    # Análise de Carga de Trabalho dos Recursos Simulados
    if result.xes_path.exists() and 'resource' in df.columns and not df['resource'].isna().all():
        st.write("---")
        st.subheader("Análise de Carga de Trabalho (Log Sintético)")

        # Aviso de filtro de datas ativo
        if st.session_state.date_filter_enabled and st.session_state.date_filter_start and st.session_state.date_filter_end:
            st.info(f"Filtro de datas ativo: {st.session_state.date_filter_start} até {st.session_state.date_filter_end}")

        with st.spinner("Analisando distribuição de recursos na simulação..."):
            workload = analyze_resource_workload(result.xes_path)
        
        if workload:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Recursos Utilizados", workload['unique_resources'])
            with col2:
                avg_events = workload['total_events'].mean()
                st.metric("Média Eventos/Recurso", f"{avg_events:.1f}")
            with col3:
                busiest_resource = workload['total_events'].idxmax()
                max_events = workload['total_events'].max()
                st.metric("Recurso Mais Usado", f"{busiest_resource}", delta=f"{max_events} eventos")
            
            # Tabs para visualizações
            tab1, tab2, tab3, tab4 = st.tabs([
                "Distribuição",
                "Por Atividade",
                "Balanceamento",
                "Busca Detalhada"
            ])
            
            with tab1:
                st.write("**Eventos por Recurso:**")
                resource_events = workload['total_events'].sort_values(ascending=False)
                st.bar_chart(resource_events)
                
                # Tabela resumo
                summary_df = pd.DataFrame({
                    'Recurso': resource_events.index,
                    'Eventos': resource_events.values,
                    '% do Total': [f"{(v/result.num_events_generated)*100:.1f}%" for v in resource_events.values]
                })
                st.dataframe(summary_df, use_container_width=True)
            
            with tab2:
                st.write("**Recursos por Atividade:**")
                
                # Agrupa por atividade
                activity_stats = workload['dataframe'].groupby('activity')['resource'].agg(['count', 'nunique'])
                activity_stats.columns = ['Total Eventos', 'Recursos Diferentes']
                activity_stats['Eventos/Recurso'] = (activity_stats['Total Eventos'] / activity_stats['Recursos Diferentes']).round(1)
                activity_stats = activity_stats.sort_values('Total Eventos', ascending=False)
                
                st.dataframe(activity_stats, use_container_width=True)
                
                # Selecionar atividade
                selected_activity = st.selectbox(
                    "Ver detalhes de:",
                    options=activity_stats.index.tolist(),
                    key="sim_activity_select"
                )
                
                if selected_activity:
                    st.write(f"**Distribuição de '{selected_activity}':**")
                    activity_resources = workload['dataframe'][
                        workload['dataframe']['activity'] == selected_activity
                    ]['resource'].value_counts()
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.bar_chart(activity_resources)
                    with col2:
                        for resource, count in activity_resources.items():
                            st.write(f"**{resource}**: {count}x")
            
            with tab3:
                st.write("**Análise de Balanceamento:**")
                
                events_per_resource = workload['total_events']
                mean_events = events_per_resource.mean()
                std_events = events_per_resource.std()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Desvio Padrão", f"{std_events:.1f}")
                    st.metric("Coeficiente de Variação", f"{(std_events/mean_events)*100:.1f}%")
                    
                    # Interpretação
                    cv = (std_events/mean_events)*100
                    if cv < 20:
                        st.success("Carga bem balanceada (CV < 20%)")
                    elif cv < 40:
                        st.info("Carga moderadamente balanceada (CV 20-40%)")
                    else:
                        st.warning("Carga desbalanceada (CV > 40%)")
                
                with col2:
                    st.write("**Distribuição:**")
                    st.write(f"- Mínimo: {events_per_resource.min()} eventos")
                    st.write(f"- Mediana: {events_per_resource.median():.0f} eventos")
                    st.write(f"- Média: {mean_events:.1f} eventos")
                    st.write(f"- Máximo: {events_per_resource.max()} eventos")
                
                # Histograma de distribuição
                st.write("**Histograma de Distribuição:**")
                hist_data = pd.DataFrame({
                    'Eventos': events_per_resource.values
                })
                st.bar_chart(hist_data['Eventos'].value_counts().sort_index())
            
            with tab4:
                st.write("**Busca Detalhada de Recurso:**")
                
                # Busca por recurso específico
                all_resources = sorted(workload['total_events'].index.tolist())
                selected_resource = st.selectbox(
                    "Selecione um recurso para análise detalhada:",
                    options=all_resources,
                    key="sim_resource_select"
                )
                
                if selected_resource:
                    resource_df = workload['dataframe'][workload['dataframe']['resource'] == selected_resource]
                    
                    # Métricas do recurso
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total de Eventos", len(resource_df))
                    with col2:
                        st.metric("Atividades Diferentes", resource_df['activity'].nunique())
                    with col3:
                        pct = (len(resource_df) / result.num_events_generated) * 100
                        st.metric("% do Total", f"{pct:.2f}%")
                    
                    # Comparação com média
                    resource_events_count = len(resource_df)
                    avg_events_all = workload['total_events'].mean()
                    diff = resource_events_count - avg_events_all
                    
                    if abs(diff) > avg_events_all * 0.2:  # Mais de 20% de diferença
                        if diff > 0:
                            st.warning(f"Este recurso está {diff:.0f} eventos acima da média ({avg_events_all:.1f})")
                        else:
                            st.info(f"Este recurso está {abs(diff):.0f} eventos abaixo da média ({avg_events_all:.1f})")
                    else:
                        st.success(f"Este recurso está próximo da média ({avg_events_all:.1f} eventos)")
                    
                    # Distribuição de atividades do recurso
                    st.write("---")
                    st.write("**Distribuição de Atividades:**")
                    activity_dist = resource_df['activity'].value_counts()
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        st.bar_chart(activity_dist)
                    with col2:
                        st.write("**Detalhamento:**")
                        for activity, count in activity_dist.items():
                            pct = (count / len(resource_df)) * 100
                            st.write(f"**{activity}**")
                            st.write(f"{count} eventos ({pct:.1f}%)")
                            st.write("")
                    
                    # Análise de especialização
                    st.write("---")
                    st.write("**Análise de Especialização:**")
                    
                    num_activities = resource_df['activity'].nunique()
                    total_activities = workload['dataframe']['activity'].nunique()
                    specialization = (1 - (num_activities / total_activities)) * 100
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Executa X de Y atividades", f"{num_activities} / {total_activities}")
                        st.metric("Índice de Especialização", f"{specialization:.1f}%")
                    
                    with col2:
                        if specialization > 70:
                            st.info("Recurso altamente especializado (foca em poucas atividades)")
                        elif specialization > 40:
                            st.info("Recurso moderadamente especializado")
                        else:
                            st.info("Recurso generalista (executa muitas atividades diferentes)")
    
    # Botões de download
    st.write("**Download dos Arquivos Gerados:**")
    col1, col2 = st.columns(2)
    
    with col1:
        if result.csv_path.exists():
            with open(result.csv_path, "rb") as f:
                st.download_button(
                    label="Download CSV",
                    data=f,
                    file_name=result.csv_path.name,
                    mime="text/csv",
                    use_container_width=True
                )
    
    with col2:
        if result.xes_path.exists():
            with open(result.xes_path, "rb") as f:
                st.download_button(
                    label="Download XES",
                    data=f,
                    file_name=result.xes_path.name,
                    mime="application/xml",
                    use_container_width=True
                )


def display_validation_results(validation):
    """Exibe resultados da validação."""
    st.subheader("Resultados da Validação")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Fitness", f"{validation.fitness:.3f}")
    with col2:
        st.metric("Custo", f"{validation.cost:.2f}")
    with col3:
        st.metric("Similaridade", f"{validation.similarity_percentage:.1f}%")

    # Interpretação
    if validation.fitness >= 0.9:
        st.success("Excelente! Log sintético muito similar ao original.")
    elif validation.fitness >= 0.7:
        st.success("Bom! Log sintético tem boa similaridade com o original.")
    elif validation.fitness >= 0.5:
        st.warning("Moderado. Considere ajustar os parâmetros de simulação.")
    else:
        st.error("Baixa similaridade. Revise os parâmetros de mineração e simulação.")

    with st.expander("Detalhes da Validação"):
        st.write(f"**Número de alinhamentos:** {validation.details.get('num_alignments', 0)}")
        st.write(f"**Fitness mínimo:** {validation.details.get('fitness_min', 0):.3f}")
        st.write(f"**Fitness máximo:** {validation.details.get('fitness_max', 0):.3f}")


def calculate_ore_indicators(log_path: Path) -> OREMetrics:
    """Calcula indicadores ORE de um log XES."""
    with st.spinner("Calculando indicadores ORE..."):
        calculator = ORECalculator(verbose=False)
        metrics = calculator.calculate_from_log(log_path)
        st.session_state.ore_metrics = metrics
        return metrics


def display_ore_results(metrics: OREMetrics):
    """Exibe resultados dos indicadores ORE."""
    st.subheader("Indicadores ORE (Operating Room Effectiveness)")

    # Informações de debug (expander colapsado)
    with st.expander("Detalhes do Cálculo"):
        st.write(f"**Dados base:**")
        st.write(f"- Cirurgias analisadas: {metrics.num_surgeries_scheduled}")
        st.write(f"- TTA (Tempo Total Disponível): {metrics.total_time_available:.1f}h")
        st.write(f"- Setup/Limpeza limitado a 15% do TTA: máx {metrics.total_time_available * 0.15:.1f}h")

        # Cálculo inverso para mostrar quantos dias operacionais foram detectados
        if metrics.loss_setup > 0:
            setup_minutes = 15  # valor padrão atual
            estimated_op_days = (metrics.loss_setup * 60) / setup_minutes
            st.write(f"- Dias operacionais estimados (dia×sala): ~{estimated_op_days:.0f}")

    # Índices principais
    st.write("### Índices Principais")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("ORE Total", f"{metrics.ore:.1f}%", help="Overall ORE: Disponibilidade × Desempenho × Qualidade")
    with col2:
        st.metric("Disponibilidade", f"{metrics.availability:.1f}%", help="TTS / TTA")
    with col3:
        st.metric("Desempenho", f"{metrics.performance:.1f}%", help="TTU / TTS")
    with col4:
        st.metric("Qualidade", f"{metrics.quality:.1f}%", help="TTAV / TTU")

    # Interpretação do ORE
    if metrics.ore >= 85:
        st.success("Excelente! Sala de cirurgia operando em alta efetividade.")
    elif metrics.ore >= 70:
        st.success("Bom! Desempenho satisfatório da sala de cirurgia.")
    elif metrics.ore >= 50:
        st.warning("Moderado. Há oportunidades significativas de melhoria.")
    else:
        st.error("Baixo. Recomenda-se análise detalhada das perdas e ações de melhoria.")

    # Tempos
    st.write("### Tempos (horas)")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Tempo Total Disponível", f"{metrics.total_time_available:.1f}h", help="Tempo Total Disponível")
    with col2:
        st.metric("Tempo Total Agendado", f"{metrics.total_time_scheduled:.1f}h", help="Tempo Total Agendado")
    with col3:
        st.metric("Tempo Total Usado", f"{metrics.total_time_used:.1f}h", help="Tempo Total Usado")
    with col4:
        st.metric("Tempo de Valor Agregado", f"{metrics.total_time_added_value:.1f}h", help="Tempo de Valor Agregado")

    # Perdas por categoria
    st.write("### Perdas por Categoria")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**Perdas de Disponibilidade**")
        st.metric("Falhas de Equipamento", f"{metrics.loss_equipment_failure:.1f}h")
        st.metric("Setup/Limpeza", f"{metrics.loss_setup:.1f}h")
        st.metric("Não Agendamento", f"{metrics.loss_not_scheduling:.1f}h")
        total_disp = metrics.loss_equipment_failure + metrics.loss_setup + metrics.loss_not_scheduling
        st.caption(f"Total: {total_disp:.1f}h")

    with col2:
        st.write("**Perdas de Desempenho**")
        st.metric("Pequenas Paradas", f"{metrics.loss_small_shutdowns:.1f}h")
        st.metric("Variação Tempo Cirurgia", f"{metrics.loss_surgery_time_variation:.1f}h")
        st.metric("Cancelamentos", f"{metrics.loss_cancellations:.1f}h")
        total_perf = metrics.loss_small_shutdowns + metrics.loss_surgery_time_variation + metrics.loss_cancellations
        st.caption(f"Total: {total_perf:.1f}h")

    with col3:
        st.write("**Perdas de Qualidade**")
        st.metric("Reintervenções", f"{metrics.loss_reinterventions:.1f}h")
        st.caption(f"Total: {metrics.loss_reinterventions:.1f}h")

    # Estatísticas de cirurgias
    st.write("### Estatísticas de Cirurgias")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Cirurgias Agendadas", metrics.num_surgeries_scheduled)
    with col2:
        st.metric("Cirurgias Realizadas", metrics.num_surgeries_completed)
    with col3:
        st.metric("Cirurgias Canceladas", metrics.num_surgeries_cancelled)
    with col4:
        st.metric("Taxa de Cancelamento", f"{metrics.cancellation_rate:.1f}%")
    

def main():
    """Função principal da aplicação."""
    init_session_state()
    
    # Cabeçalho
    st.title("Process Mining & Simulation")
    st.markdown("Sistema de mineração de processos, simulação e validação de logs de eventos")
    
    # Sidebar para configurações
    with st.sidebar:
        st.header("Configurações")
        
        # Seletor de Arquivo de Demonstração
        st.subheader("Arquivo de Demonstração")
        
        demo_files = {
            "Demo": Path("/home/bregoli/Code/Sim2Log-core/bases/xes/patient_treatment.xes"),
            "Cirurgias Marco Huc": Path("/home/bregoli/Code/Sim2Log-core/bases/xes/CirurgiasMarcoHucEnriched.xes")
        }
        
        selected_demo = st.selectbox(
            "Selecione o log para análise:",
            options=list(demo_files.keys()),
            index=0
        )
        
        # Lógica de carregamento e troca de arquivo
        selected_path = demo_files[selected_demo]
        
        # Se mudou o arquivo ou ainda não carregou nada
        if st.session_state.log_path != selected_path:
            if selected_path.exists():
                st.session_state.uploaded_file = selected_demo
                st.session_state.log_path = selected_path
                st.session_state.xes_path = selected_path
                
                # Reset de estados
                st.session_state.model = None
                st.session_state.simulation_result = None
                st.session_state.validation_result = None
                st.session_state.log_profile = None
                st.session_state.ore_metrics = None
                st.session_state.saved_simulations = []
                
                # Extrai datas
                min_date, max_date = extract_log_date_range(selected_path)
                st.session_state.log_min_date = min_date
                st.session_state.log_max_date = max_date
                
                st.toast(f"Carregado: {selected_demo}", icon="📂")
                
                # Auto-cálculo para demonstração
                with st.spinner("Processando dados iniciais..."):
                    analyze_log(selected_path)
                    # Só calcula ORE se não for "Demo"
                    if selected_demo != "Demo":
                        calculate_ore_indicators(selected_path)
            else:
                st.error(f"Arquivo não encontrado: {selected_path}")

        if st.session_state.log_min_date and st.session_state.log_max_date:
            st.info(f"Período: {st.session_state.log_min_date} até {st.session_state.log_max_date}")
        
        st.divider()
        
        # Parâmetros de mineração
        st.header("Parâmetros de Mineração")
        variant_filter = st.slider(
            "Filtro de Variantes",
            min_value=0.0,
            max_value=1.0,
            value=0.8,
            step=0.05,
            help="Percentual de variantes mais frequentes a manter (0.8 = 80%)"
        )
        
        st.divider()
        
        # Parâmetros de simulação
        st.header("Parâmetros de Simulação")
        num_cases = st.number_input(
            "Número de Casos",
            min_value=1,
            max_value=10000,
            value=1400,
            step=10,
            help="Quantidade de casos sintéticos a gerar"
        )
        
        use_custom_arrival = st.checkbox("Taxa de chegada customizada")
        arrival_rate = 0.0
        if use_custom_arrival:
            arrival_rate = st.number_input(
                "Taxa de Chegada (min/caso)",
                min_value=0.1,
                max_value=60.0,
                value=5.0,
                step=0.5,
                help="Intervalo entre chegadas de casos em minutos"
            )

        st.divider()

        # Filtro de datas (só aparece se o log foi carregado)
        if st.session_state.log_path and st.session_state.log_min_date and st.session_state.log_max_date:
            st.header("Filtro de Datas")
            date_filter_enabled = st.checkbox(
                "Habilitar filtro de datas",
                help="Filtra as visualizações por intervalo de datas (não afeta mineração/simulação)"
            )

            if date_filter_enabled:
                st.caption("Filtra apenas a visualização dos dados")
                st.caption(f"Período disponível: {st.session_state.log_min_date} até {st.session_state.log_max_date}")

                col1, col2 = st.columns(2)
                with col1:
                    date_start = st.date_input(
                        "Data Inicial",
                        value=st.session_state.log_min_date,
                        min_value=st.session_state.log_min_date,
                        max_value=st.session_state.log_max_date,
                        help="Data inicial para filtro (inclusivo)"
                    )
                with col2:
                    date_end = st.date_input(
                        "Data Final",
                        value=st.session_state.log_max_date,
                        min_value=st.session_state.log_min_date,
                        max_value=st.session_state.log_max_date,
                        help="Data final para filtro (inclusivo)"
                    )

                st.session_state.date_filter_enabled = date_filter_enabled
                st.session_state.date_filter_start = date_start
                st.session_state.date_filter_end = date_end

                if date_start and date_end:
                    if date_start > date_end:
                        st.error("Data inicial não pode ser maior que data final")
                    else:
                        st.success(f"Filtro ativo: {date_start} até {date_end}")
            else:
                st.session_state.date_filter_enabled = False
                st.session_state.date_filter_start = None
                st.session_state.date_filter_end = None

            st.divider()

        # Configuração de recursos
        st.header("Configuração de Recursos")
        modify_resources = st.checkbox(
            "Modificar recursos",
            help="Permite alterar os recursos disponíveis para cada atividade"
        )
        
        custom_resources = None
        if modify_resources and st.session_state.model is not None:
            st.write("**Configure os recursos por atividade:**")
            st.caption("Marque/desmarque os recursos que deseja usar em cada atividade")
            
            custom_resources = {}
            
            # Coleta todos os recursos únicos do modelo
            all_resources = set()
            for resources_list in st.session_state.model.resources.values():
                # Filtra apenas recursos válidos (strings não vazias)
                valid_resources = [r for r in resources_list if r and isinstance(r, str)]
                all_resources.update(valid_resources)
            all_resources = sorted(all_resources)
            
            for activity in sorted(st.session_state.model.activities.keys()):
                with st.expander(f"{activity}"):
                    original_resources = st.session_state.model.resources.get(activity, [])
                    # Filtra apenas recursos válidos
                    original_resources = [r for r in original_resources if r and isinstance(r, str)]
                    
                    # Mostra quantos recursos estão ativos
                    st.caption(f"Original: {len(original_resources)} recurso(s)")
                    
                    selected_resources = []
                    
                    # Cria checkboxes para cada recurso
                    if all_resources:
                        st.write("**Recursos disponíveis:**")
                        
                        # Organiza em colunas para melhor layout
                        num_cols = 2 if len(all_resources) > 4 else 1
                        cols = st.columns(num_cols)
                        
                        for idx, resource in enumerate(all_resources):
                            col = cols[idx % num_cols]
                            with col:
                                # Marca o checkbox se o recurso estava originalmente na atividade
                                is_checked = resource in original_resources
                                
                                if st.checkbox(
                                    resource,
                                    value=is_checked,
                                    key=f"resource_{activity}_{resource}"
                                ):
                                    selected_resources.append(resource)
                    
                    # Permite adicionar novos recursos
                    st.write("**Adicionar novo recurso:**")
                    new_resource = st.text_input(
                        "Nome do recurso",
                        key=f"new_resource_{activity}",
                        placeholder="Digite o nome e pressione Enter",
                        help="Adicione um recurso que não existe na lista"
                    )
                    
                    if new_resource and new_resource.strip():
                        new_resource_name = new_resource.strip()
                        if st.checkbox(
                            f"Adicionar '{new_resource_name}'",
                            value=True,
                            key=f"add_{activity}_{new_resource_name}"
                        ):
                            if new_resource_name not in selected_resources:
                                selected_resources.append(new_resource_name)
                    
                    custom_resources[activity] = selected_resources
                    
                    # Mostra resumo da atividade
                    if len(selected_resources) == 0:
                        st.warning(f"Nenhum recurso selecionado! Serão usados os originais na simulação.")
                    elif set(selected_resources) != set(original_resources):
                        st.info(f"Mudança: {len(original_resources)} → {len(selected_resources)} recursos")
            
            # Resumo geral de mudanças
            st.write("---")
            st.write("**Resumo das alterações:**")
            changes = 0
            total_resources_original = 0
            total_resources_new = 0
            
            for activity, new_res in custom_resources.items():
                original = st.session_state.model.resources.get(activity, [])
                # Filtra apenas recursos válidos
                original = [r for r in original if r and isinstance(r, str)]
                total_resources_original += len(original)
                total_resources_new += len(new_res)
                
                if set(new_res) != set(original):
                    changes += 1
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Atividades modificadas", changes)
            with col2:
                st.metric("Recursos (Original)", total_resources_original)
            with col3:
                st.metric("Recursos (Novo)", total_resources_new)
            
            if changes > 0:
                st.success(f"{changes} atividade(s) com recursos modificados")
            else:
                st.info("Nenhuma alteração nos recursos")
    
    # Área principal
    if st.session_state.log_path is None:
        st.info("Faça upload de um arquivo XES na barra lateral para começar")
        st.markdown("""
        ### Como usar:
        
        1. **Upload**: Carregue um arquivo XES na barra lateral
        2. **Configuração**: Ajuste os parâmetros conforme necessário
        3. **Execução**: Escolha executar tudo de uma vez ou por etapas
        4. **Resultados**: Visualize os resultados e faça download dos arquivos gerados
        
        ### Etapas do Processo:
        
        - **Análise**: Detecta automaticamente características do log
        - **Mineração**: Descobre o modelo de processo (Rede de Petri)
        - **Simulação**: Gera casos sintéticos baseados no modelo
        - **Validação**: Compara log original com log sintético
        """)
        return
    
    # Tabs para organizar o conteúdo
    # Determina se deve mostrar a aba ORE (não mostrar para "Demo")
    show_ore_tab = selected_demo != "Demo"
    
    if show_ore_tab:
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "1. Análise",
            "2. Mineração",
            "3. Simulação",
            "4. Validação",
            "5. Comparação",
            "6. ORE Indicators"
        ])
    else:
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "1. Análise",
            "2. Mineração",
            "3. Simulação",
            "4. Validação",
            "5. Comparação"
        ])
        tab6 = None
    
    with tab1:
        st.header("Análise do Log")
        
        if st.button("Executar Análise", type="primary"):
            profile = analyze_log(st.session_state.log_path)
            st.success("Análise concluída!")
        
        if st.session_state.log_profile:
            display_log_profile(st.session_state.log_profile, st.session_state.log_path)
    
    with tab2:
        st.header("Mineração de Processo")
        
        if st.button("Executar Mineração", type="primary"):
            model, model_image_path = run_mining(st.session_state.log_path, variant_filter)
            st.success("Mineração concluída!")
        
        if st.session_state.model:
            display_mining_results(st.session_state.model, st.session_state.model_image_path)
        else:
            st.info("Execute a mineração para ver os resultados")
    
    with tab3:
        st.header("Simulação de Log")
        
        if st.session_state.model is None:
            st.warning("Execute a mineração primeiro antes de simular")
        else:
            if st.button("Executar Simulação", type="primary"):
                result = run_simulation(st.session_state.model, num_cases, arrival_rate, custom_resources)
                st.success("Simulação concluída!")
        
        if st.session_state.simulation_result:
            display_simulation_results(st.session_state.simulation_result, custom_resources, st.session_state.model)
        else:
            if st.session_state.model:
                st.info("Execute a simulação para ver os resultados")
    
    with tab4:
        st.header("Validação")
        
        if st.session_state.simulation_result is None:
            st.warning("Execute a simulação primeiro antes de validar")
        else:
            if st.button("Executar Validação", type="primary"):
                validation = run_validation(
                    st.session_state.log_path,
                    st.session_state.simulation_result.xes_path
                )
                st.success("Validação concluída!")
        
        if st.session_state.validation_result:
            display_validation_results(st.session_state.validation_result)
        else:
            if st.session_state.simulation_result:
                st.info("Execute a validação para ver os resultados")
    
    with tab5:
        st.header("Comparação: Log Original vs Simulação")

        # Aviso de filtro de datas ativo
        if st.session_state.date_filter_enabled and st.session_state.date_filter_start and st.session_state.date_filter_end:
            st.info(f"Filtro de datas ativo: {st.session_state.date_filter_start} até {st.session_state.date_filter_end}")

        if not st.session_state.log_profile:
            st.warning("Execute a análise do log original primeiro")
        elif len(st.session_state.saved_simulations) == 0:
            st.info("Nenhuma simulação salva para comparar. Execute simulações e clique em 'Salvar para Comparar'")
        else:
            # Seleção de simulação
            col1, col2 = st.columns([3, 1])

            with col1:
                simulation_names = [f"{s['name']} - {s['timestamp']}" for s in st.session_state.saved_simulations]
                selected_sim_idx = st.selectbox(
                    "Selecione a simulação para comparar com o log original:",
                    range(len(st.session_state.saved_simulations)),
                    format_func=lambda i: simulation_names[i]
                )

            with col2:
                st.write("")  # Espaçamento
                st.write("")
                if st.button("Limpar Simulações"):
                    st.session_state.saved_simulations = []
                    st.rerun()

            selected_sim = st.session_state.saved_simulations[selected_sim_idx]
            sim_df = selected_sim['dataframe'].copy()

            # Aplica filtro de datas na simulação
            sim_df = filter_dataframe_by_date(sim_df, 'timestamp')

            st.write("---")
            
            # Comparação de métricas gerais
            st.subheader("Métricas Gerais")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("### Log Original")
                original_profile = st.session_state.log_profile
                
                st.metric("Total de Casos", original_profile.num_traces)
                st.metric("Total de Eventos", original_profile.num_events)
                st.metric("Atividades Únicas", original_profile.num_unique_activities)
                
                avg_events_orig = original_profile.num_events / original_profile.num_traces
                st.metric("Eventos por Caso (média)", f"{avg_events_orig:.1f}")
            
            with col2:
                st.write("### Simulação")
                
                st.metric("Total de Casos", selected_sim['num_cases'])
                st.metric("Total de Eventos", selected_sim['num_events'])
                st.metric("Atividades Únicas", sim_df['activity'].nunique())
                
                avg_events_sim = sim_df.groupby('case_id').size().mean()
                st.metric("Eventos por Caso (média)", f"{avg_events_sim:.1f}")
            
            # Comparação de atividades
            st.write("---")
            st.subheader("Distribuição de Atividades")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Log Original:**")
                orig_activities = pd.DataFrame.from_dict(
                    original_profile.activity_frequencies,
                    orient='index',
                    columns=['Frequência']
                ).sort_values('Frequência', ascending=False)
                st.bar_chart(orig_activities)
            
            with col2:
                st.write("**Simulação:**")
                sim_activities = sim_df['activity'].value_counts()
                st.bar_chart(sim_activities)
            
            # Tabela comparativa de atividades
            st.write("**Tabela Comparativa:**")
            comparison_activities = []
            
            all_activities = set(original_profile.activity_frequencies.keys()) | set(sim_df['activity'].unique())
            
            for activity in sorted(all_activities):
                orig_count = original_profile.activity_frequencies.get(activity, 0)
                sim_count = sim_df[sim_df['activity'] == activity].shape[0]
                
                orig_pct = (orig_count / original_profile.num_events * 100) if original_profile.num_events > 0 else 0
                sim_pct = (sim_count / selected_sim['num_events'] * 100) if selected_sim['num_events'] > 0 else 0
                
                diff_pct = sim_pct - orig_pct
                
                comparison_activities.append({
                    'Atividade': activity,
                    'Original': orig_count,
                    '% Orig': f"{orig_pct:.1f}%",
                    'Simulação': sim_count,
                    '% Sim': f"{sim_pct:.1f}%",
                    'Diferença %': f"{diff_pct:+.1f}%"
                })
            
            comparison_df = pd.DataFrame(comparison_activities)
            st.dataframe(comparison_df, use_container_width=True)
            
            # Comparação de recursos
            st.write("---")
            st.subheader("Análise de Recursos")
            
            # Analisa workload do original e da simulação
            with st.spinner("Analisando recursos..."):

                
                original_workload = None
                sim_workload = None
                
                if st.session_state.xes_path:
                    xes_path = Path(st.session_state.xes_path)
                    original_workload = analyze_resource_workload(xes_path)
                
                if 'resource' in sim_df.columns and not sim_df['resource'].isna().all():
                    # Cria XES temporário da simulação se necessário
                    sim_xes_path = Path(selected_sim.get('xes_path', ''))
                    if sim_xes_path.exists():
                        sim_workload = analyze_resource_workload(sim_xes_path)
            
            if original_workload and sim_workload:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("### Log Original")
                    
                    # Métricas principais
                    total_events_orig = len(original_workload['dataframe'])
                    st.metric("Total de Eventos", total_events_orig)
                    st.metric("Recursos Únicos", original_workload['unique_resources'])
                    avg_events_orig = original_workload['total_events'].mean()
                    st.metric("Média Eventos/Recurso", f"{avg_events_orig:.1f}")
                    
                    # Recurso mais usado
                    busiest_resource_orig = original_workload['total_events'].idxmax()
                    max_events_orig = original_workload['total_events'].max()
                    st.metric("Recurso Mais Usado", f"{busiest_resource_orig}", delta=f"{max_events_orig} eventos")
                    
                    st.write("**Top 10 Recursos:**")
                    top_orig = original_workload['total_events'].sort_values(ascending=False).head(10)
                    st.bar_chart(top_orig)
                
                with col2:
                    st.write("### Simulação")
                    
                    # Métricas principais
                    total_events_sim = len(sim_workload['dataframe'])
                    st.metric("Total de Eventos", total_events_sim)
                    st.metric("Recursos Únicos", sim_workload['unique_resources'])
                    avg_events_sim = sim_workload['total_events'].mean()
                    st.metric("Média Eventos/Recurso", f"{avg_events_sim:.1f}")
                    
                    # Recurso mais usado
                    busiest_resource_sim = sim_workload['total_events'].idxmax()
                    max_events_sim = sim_workload['total_events'].max()
                    st.metric("Recurso Mais Usado", f"{busiest_resource_sim}", delta=f"{max_events_sim} eventos")
                    
                    st.write("**Top 10 Recursos:**")
                    top_sim = sim_workload['total_events'].sort_values(ascending=False).head(10)
                    st.bar_chart(top_sim)
                
                # Alerta se houver grande disparidade
                st.write("---")
                ratio = total_events_sim / total_events_orig if total_events_orig > 0 else 0
                if ratio > 5:
                    st.warning(f"A simulação gerou {ratio:.1f}x mais eventos que o log original. Considere ajustar o número de casos simulados para uma comparação mais justa.")
                elif ratio < 0.2:
                    st.warning(f"A simulação gerou apenas {ratio:.1%} dos eventos do log original. Considere aumentar o número de casos simulados.")
                
                # Análise de balanceamento
                st.write("---")
                st.write("### Balanceamento de Carga")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Original:**")
                    orig_std = original_workload['total_events'].std()
                    orig_mean = original_workload['total_events'].mean()
                    orig_cv = (orig_std / orig_mean * 100) if orig_mean > 0 else 0
                    
                    st.metric("Desvio Padrão", f"{orig_std:.1f}")
                    st.metric("Coef. Variação", f"{orig_cv:.1f}%")
                    
                    if orig_cv < 20:
                        st.success("Bem balanceado")
                    elif orig_cv < 40:
                        st.info("Moderadamente balanceado")
                    else:
                        st.warning("Desbalanceado")
                
                with col2:
                    st.write("**Simulação:**")
                    sim_std = sim_workload['total_events'].std()
                    sim_mean = sim_workload['total_events'].mean()
                    sim_cv = (sim_std / sim_mean * 100) if sim_mean > 0 else 0
                    
                    st.metric("Desvio Padrão", f"{sim_std:.1f}")
                    st.metric("Coef. Variação", f"{sim_cv:.1f}%")
                    
                    if sim_cv < 20:
                        st.success("Bem balanceado")
                    elif sim_cv < 40:
                        st.info("Moderadamente balanceado")
                    else:
                        st.warning("Desbalanceado")
            
            elif not original_workload:
                st.info("Log original não possui informações de recursos para comparar")
            elif not sim_workload:
                st.info("Simulação não possui informações de recursos para comparar")

    if tab6 is not None:
        with tab6:
            st.header("Indicadores ORE")
            st.caption("Operating Room Effectiveness - Indicadores de Efetividade de Sala Cirúrgica")


            with st.expander("Sobre os Indicadores ORE"):
                st.write("""
                Os **Indicadores ORE (Operating Room Effectiveness)** são baseados na metodologia Lean Healthcare
                e adaptados do OEE (Overall Equipment Effectiveness) da manufatura.

                **Três pilares principais:**

                1. **Disponibilidade**: Quanto tempo agendado em relação ao tempo total disponível
                   - Perdas: Falhas de equipamento, Setup/limpeza, Não agendamento

                2. **Desempenho**: Quanto tempo foi efetivamente usado em relação ao agendado
                   - Perdas: Pequenas paradas, Variação no tempo de cirurgia, Cancelamentos

                3. **Qualidade**: Quanto tempo agregou valor em relação ao tempo usado
                   - Perdas: Reintervenções

                **Fórmula:**

                ORE = Disponibilidade × Desempenho × Qualidade

                **Referência:**
                Souza, T. A., Vaccaro, G. L. R., & Lima, R. M. (2020).
                Operating room effectiveness: a lean health-care performance indicator.
                """)

            if st.button("Calcular Indicadores ORE", type="primary"):
                calculate_ore_indicators(st.session_state.log_path)
                st.success("Indicadores ORE calculados com sucesso!")

            if st.session_state.ore_metrics:
                display_ore_results(st.session_state.ore_metrics)
            else:
                st.info("Clique no botão acima para calcular os indicadores ORE do log carregado")


if __name__ == "__main__":
    main()

