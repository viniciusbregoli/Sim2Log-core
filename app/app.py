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

from process_mining import ProcessMiner
from simulation import LogSimulator
from validation import LogValidator
from models import SimulationConfig
from log_analyzer import LogAnalyzer


# Configuração da página
st.set_page_config(
    page_title="Sim2Log - Process Mining",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_session_state():
    """Inicializa o estado da sessão."""
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'log_path' not in st.session_state:
        st.session_state.log_path = None
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


def run_simulation(model, num_cases, arrival_rate):
    """Executa simulação de log."""
    with st.spinner(f"Simulando {num_cases} casos..."):
        output_dir = Path("app/outputs")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        config = SimulationConfig(
            num_cases=num_cases,
            arrival_rate=arrival_rate if arrival_rate > 0 else None,
            random_seed=42
        )
        
        simulator = LogSimulator(config, verbose=False)
        result = simulator.simulate(
            model,
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


def display_log_profile(profile):
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
    
    # Exibe diagrama de Petri
    if model_image_path and model_image_path.exists():
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
    
    # Estatísticas de atividades
    with st.expander("Estatísticas das Atividades"):
        st.write(f"**Taxa de chegada:** {model.arrival_rate:.2f} minutos/caso")
        st.write(f"**Duração mediana:** {model.median_case_duration:.2f} segundos")
        
        st.write("\n**Durações por Atividade:**")
        for activity, stats in model.activities.items():
            st.write(f"- **{activity}**: {stats.mean_duration:.2f}s (distribuição: {stats.distribution_name})")


def display_simulation_results(result):
    """Exibe resultados da simulação."""
    st.subheader("Resultados da Simulação")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Casos Gerados", result.num_cases_generated)
    with col2:
        st.metric("Eventos Gerados", result.num_events_generated)
    with col3:
        st.metric("Tempo de Simulação", f"{result.simulation_time:.2f}s")
    
    # Visualização do CSV
    if result.csv_path.exists():
        st.write("**Prévia dos Dados Gerados:**")
        
        import pandas as pd
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
        tab1, tab2, tab3 = st.tabs(["Dados Completos", "Primeiros Registros", "Estatísticas"])
        
        with tab1:
            st.dataframe(df, use_container_width=True, height=400)
        
        with tab2:
            num_rows = st.slider("Número de linhas para visualizar", 5, 100, 20, key="preview_rows")
            st.dataframe(df.head(num_rows), use_container_width=True)
        
        with tab3:
            st.write("**Frequência de Atividades:**")
            activity_counts = df['activity'].value_counts()
            st.bar_chart(activity_counts)
            
            st.write("**Casos por Ordem:**")
            case_counts = df.groupby('case_id').size()
            st.write(f"- Média de eventos por caso: {case_counts.mean():.2f}")
            st.write(f"- Mínimo de eventos por caso: {case_counts.min()}")
            st.write(f"- Máximo de eventos por caso: {case_counts.max()}")
    
    # Botões de download
    st.write("**Download dos Arquivos Gerados:**")
    col1, col2 = st.columns(2)
    
    with col1:
        if result.csv_path.exists():
            with open(result.csv_path, "rb") as f:
                st.download_button(
                    label="📥 Download CSV",
                    data=f,
                    file_name=result.csv_path.name,
                    mime="text/csv",
                    use_container_width=True
                )
    
    with col2:
        if result.xes_path.exists():
            with open(result.xes_path, "rb") as f:
                st.download_button(
                    label="📥 Download XES",
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


def main():
    """Função principal da aplicação."""
    init_session_state()
    
    # Cabeçalho
    st.title("Sim2Log - Process Mining & Simulation")
    st.markdown("Sistema de mineração de processos, simulação e validação de logs de eventos")
    
    # Sidebar para configurações
    with st.sidebar:
        st.header("Configurações")
        
        # Upload de arquivo
        uploaded_file = st.file_uploader(
            "Upload do arquivo XES",
            type=['xes'],
            help="Selecione um arquivo XES para análise"
        )
        
        if uploaded_file is not None:
            if st.session_state.uploaded_file != uploaded_file.name:
                st.session_state.uploaded_file = uploaded_file.name
                st.session_state.log_path = save_uploaded_file(uploaded_file)
                st.session_state.model = None
                st.session_state.simulation_result = None
                st.session_state.validation_result = None
                st.session_state.log_profile = None
                st.success(f"Arquivo '{uploaded_file.name}' carregado!")
        
        st.divider()
        
        # Modo de execução
        st.header("Modo de Execução")
        execution_mode = st.radio(
            "Escolha o modo:",
            ["Executar Tudo", "Por Etapas"],
            help="Execute todas as etapas de uma vez ou controle cada etapa individualmente"
        )
        
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
            value=50,
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
    
    # Área principal
    if st.session_state.log_path is None:
        st.info("👆 Faça upload de um arquivo XES na barra lateral para começar")
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
    if execution_mode == "Executar Tudo":
        st.header("Execução Completa")
        
        if st.button("Executar Pipeline Completo", type="primary", use_container_width=True):
            # 1. Análise
            st.write("### Etapa 1: Análise do Log")
            profile = analyze_log(st.session_state.log_path)
            display_log_profile(profile)
            
            # 2. Mineração
            st.write("### Etapa 2: Mineração de Processo")
            model, model_image_path = run_mining(st.session_state.log_path, variant_filter)
            display_mining_results(model, model_image_path)
            
            # 3. Simulação
            st.write("### Etapa 3: Simulação de Log")
            result = run_simulation(model, num_cases, arrival_rate)
            display_simulation_results(result)
            
            # 4. Validação
            st.write("### Etapa 4: Validação")
            validation = run_validation(st.session_state.log_path, result.xes_path)
            display_validation_results(validation)
            
            st.success("Pipeline completo executado com sucesso!")
    
    else:  # Por Etapas
        tab1, tab2, tab3, tab4 = st.tabs([
            "1. Análise",
            "2. Mineração",
            "3. Simulação",
            "4. Validação"
        ])
        
        with tab1:
            st.header("Análise do Log")
            
            if st.button("Executar Análise", type="primary"):
                profile = analyze_log(st.session_state.log_path)
                st.success("Análise concluída!")
            
            if st.session_state.log_profile:
                display_log_profile(st.session_state.log_profile)
        
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
                    result = run_simulation(st.session_state.model, num_cases, arrival_rate)
                    st.success("Simulação concluída!")
            
            if st.session_state.simulation_result:
                display_simulation_results(st.session_state.simulation_result)
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


if __name__ == "__main__":
    main()

