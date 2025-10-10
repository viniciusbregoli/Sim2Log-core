import pandas as pd
import pm4py
from datetime import datetime

# Ler XLSX
df = pd.read_excel('bases/Agendamentos_CC (nova base) 10-25.xlsx')

# Transformar colunas de timestamp em eventos
events = []

timestamp_cols = {
    'DT_AGENDAMENTO': 'Agendamento',
    'CHAMADA_CC': 'Chamada CC',
    'CHEGADA_CC': 'Chegada CC',
    'ENTRADA_SALA': 'Entrada Sala',
    'INICIO_INDUCAO': 'Início Indução',
    'INCISÃO': 'Incisão',
    'TERMINO_PROC_CIRURGICO': 'Término Cirúrgico',
    'TERMINO_ANESTESIA': 'Término Anestesia',
    'ENTRADA_RPA': 'Entrada RPA',
    'ENCAMINHAMENTO_UTI': 'Encaminhamento UTI',
    'CHAMADA_UI': 'Chamada UI',
    'SAIDA_RPA_CC': 'Saída RPA',
    'SAIDA_MORGUE_CC': 'Saída Morgue',
    'ALTA_HOSP': 'Alta Hospitalar'
}

for idx, row in df.iterrows():
    case_id = row['NR_CIRURGIA']
    
    for col, activity in timestamp_cols.items():
        if pd.notna(row[col]):
            # Combinar data de início com hora se necessário
            if col == 'DT_AGENDAMENTO' and pd.notna(row.get('DT_INICIO')) and pd.notna(row.get('HR_INICIO')):
                timestamp = pd.to_datetime(f"{row['DT_INICIO']} {row['HR_INICIO']}")
            else:
                timestamp = pd.to_datetime(row[col])
            
            events.append({
                'case:concept:name': case_id,
                'concept:name': activity,
                'time:timestamp': timestamp,
                'paciente': row['NOME_PACIENTE'],
                'cirurgiao': row['NM_CIRURGIAO'],
                'anestesista': row['NM_ANESTESISTA'],
                'sala': row['SALA'],
                'procedimento': row['DS_PROCEDIMENTO'],
                'status': row['DS_STATUS_CIRURGIA']
            })

# Criar DataFrame de eventos
event_log = pd.DataFrame(events)
event_log = event_log.sort_values(['case:concept:name', 'time:timestamp'])

# Exportar para XES
pm4py.write_xes(event_log, 'cirurgias.xes')