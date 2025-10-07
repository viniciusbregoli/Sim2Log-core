"""
Conversor de Excel para XES.

Converte planilhas Excel com dados de processos em formato XES
para uso com Sim2Log.
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict

import pandas as pd
import pm4py


class ExcelToXESConverter:
    """
    Converte planilhas Excel para formato XES.
    
    Detecta automaticamente:
    - Colunas de timestamp
    - Case ID
    - Atividades baseadas nos timestamps
    - Recursos
    
    Example:
        >>> converter = ExcelToXESConverter()
        >>> converter.convert("cirurgias.xlsx", "cirurgias.xes")
        ✓ 512 casos convertidos
    """
    
    def __init__(self, verbose: bool = True):
        """
        Args:
            verbose: Se True, imprime progresso
        """
        self.verbose = verbose
    
    def convert(
        self,
        excel_path: Path | str,
        output_xes: Path | str,
        case_id_column: Optional[str] = None,
        timestamp_columns: Optional[List[str]] = None,
        resource_column: Optional[str] = None,
        sheet_name: int | str = 0
    ):
        """
        Converte Excel para XES.
        
        Args:
            excel_path: Caminho do arquivo Excel
            output_xes: Caminho do arquivo XES de saída
            case_id_column: Nome da coluna de Case ID (None = auto-detect)
            timestamp_columns: Lista de colunas de timestamp (None = auto-detect)
            resource_column: Nome da coluna de recurso (None = auto-detect)
            sheet_name: Nome ou índice da aba (padrão: primeira aba)
        """
        excel_path = Path(excel_path)
        output_xes = Path(output_xes)
        
        if not excel_path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {excel_path}")
        
        self._log(f"Lendo Excel: {excel_path.name}...")
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        
        self._log(f"  Linhas: {len(df)}")
        self._log(f"  Colunas: {len(df.columns)}")
        
        # Auto-detecta colunas
        if case_id_column is None:
            case_id_column = self._detect_case_id_column(df)
        
        if timestamp_columns is None:
            timestamp_columns = self._detect_timestamp_columns(df)
        
        if resource_column is None:
            resource_column = self._detect_resource_column(df)
        
        self._log(f"\nConfigurações detectadas:")
        self._log(f"  Case ID: {case_id_column}")
        self._log(f"  Timestamps: {len(timestamp_columns)} colunas")
        self._log(f"  Recurso: {resource_column or 'N/A'}")
        
        # Converte para formato de eventos
        self._log(f"\nConvertendo para formato de eventos...")
        event_log_df = self._transform_to_events(
            df,
            case_id_column,
            timestamp_columns,
            resource_column
        )
        
        self._log(f"  Eventos criados: {len(event_log_df)}")
        
        # Formata como event log do PM4Py
        self._log(f"Formatando como event log...")
        event_log = pm4py.format_dataframe(
            event_log_df,
            case_id='case:concept:name',
            activity_key='concept:name',
            timestamp_key='time:timestamp'
        )
        
        # Converte para XES
        self._log(f"Salvando em XES: {output_xes}...")
        from pm4py.objects.conversion.log import converter as log_converter
        log = log_converter.apply(event_log)
        pm4py.write_xes(log, str(output_xes))
        
        # Adiciona classificador
        self._add_classifier(output_xes)
        
        num_cases = event_log_df['case:concept:name'].nunique()
        self._log(f"\n✓ Conversão concluída!")
        self._log(f"  Casos: {num_cases}")
        self._log(f"  Eventos: {len(event_log_df)}")
        self._log(f"  Arquivo: {output_xes}")
    
    def _detect_case_id_column(self, df: pd.DataFrame) -> str:
        """Detecta coluna de Case ID."""
        candidates = [
            'NR_CIRURGIA', 'NR_ATENDIMENTO', 'ID_CIRURGIA', 'CIRURGIA_ID',
            'CASE_ID', 'CASEID', 'ID', 'NR_CASO', 'CASO_ID'
        ]
        
        for col in df.columns:
            if col.upper() in candidates:
                self._log(f"  Case ID detectado: {col}")
                return col
        
        # Fallback: primeira coluna que parece ID
        for col in df.columns:
            if 'NR_' in col.upper() or 'ID' in col.upper():
                self._log(f"  Case ID detectado (fallback): {col}")
                return col
        
        raise ValueError(
            "Não foi possível detectar coluna de Case ID. "
            "Especifique manualmente com case_id_column='nome_coluna'"
        )
    
    def _detect_timestamp_columns(self, df: pd.DataFrame) -> List[str]:
        """Detecta colunas de timestamp."""
        timestamp_cols = []
        
        for col in df.columns:
            col_upper = col.upper()
            
            # Ignora colunas de data/hora de agendamento inicial
            if any(x in col_upper for x in ['DT_AGENDAMENTO', 'DT_NASCIMENTO']):
                continue
            
            # Detecta colunas que contêm data/hora de eventos
            if any(x in col_upper for x in ['CHAMADA', 'CHEGADA', 'ENTRADA', 'INICIO', 
                                            'TERMINO', 'SAIDA', 'ALTA', 'ENCAMINHAMENTO']):
                # Verifica se tem valores válidos
                if df[col].notna().any():
                    timestamp_cols.append(col)
        
        if not timestamp_cols:
            # Fallback: todas colunas com DT_ ou HR_ ou _DATA ou _HORA
            for col in df.columns:
                if any(x in col.upper() for x in ['DT_', 'HR_', 'DATA', 'HORA', 'TIME']):
                    if df[col].notna().any():
                        timestamp_cols.append(col)
        
        if not timestamp_cols:
            raise ValueError(
                "Não foi possível detectar colunas de timestamp. "
                "Especifique manualmente com timestamp_columns=['col1', 'col2']"
            )
        
        self._log(f"  Timestamps detectados: {timestamp_cols}")
        return timestamp_cols
    
    def _detect_resource_column(self, df: pd.DataFrame) -> Optional[str]:
        """Detecta coluna de recurso."""
        candidates = [
            'NM_CIRURGIAO', 'NM_ANESTESISTA', 'SALA', 'MEDICO',
            'RECURSO', 'RESOURCE', 'USUARIO', 'USER', 'EXECUTOR'
        ]
        
        for col in df.columns:
            if col.upper() in candidates:
                self._log(f"  Recurso detectado: {col}")
                return col
        
        # Fallback: primeira coluna com NM_ ou _NOME
        for col in df.columns:
            if 'NM_' in col.upper() or 'NOME' in col.upper():
                self._log(f"  Recurso detectado (fallback): {col}")
                return col
        
        return None
    
    def _transform_to_events(
        self,
        df: pd.DataFrame,
        case_id_col: str,
        timestamp_cols: List[str],
        resource_col: Optional[str]
    ) -> pd.DataFrame:
        """
        Transforma DataFrame wide (uma linha por caso) em format long (uma linha por evento).
        """
        events = []
        
        for idx, row in df.iterrows():
            case_id = str(row[case_id_col])
            
            # Para cada coluna de timestamp, cria um evento
            for ts_col in timestamp_cols:
                timestamp = row[ts_col]
                
                # Ignora timestamps vazios
                if pd.isna(timestamp):
                    continue
                
                # Normaliza timestamp
                timestamp = self._normalize_timestamp(timestamp, row, ts_col)
                
                if timestamp is None:
                    continue
                
                # Nome da atividade baseado no nome da coluna
                activity = self._column_to_activity_name(ts_col)
                
                # Cria evento
                event = {
                    'case:concept:name': case_id,
                    'concept:name': activity,
                    'time:timestamp': timestamp
                }
                
                # Adiciona recurso se disponível
                if resource_col and not pd.isna(row[resource_col]):
                    event['org:resource'] = str(row[resource_col])
                
                # Adiciona atributos adicionais relevantes
                if 'SALA' in df.columns and not pd.isna(row['SALA']):
                    event['sala'] = str(row['SALA'])
                
                if 'DS_PROCEDIMENTO' in df.columns and not pd.isna(row['DS_PROCEDIMENTO']):
                    event['procedimento'] = str(row['DS_PROCEDIMENTO'])[:100]
                
                events.append(event)
        
        # Converte para DataFrame e ordena por caso e timestamp
        events_df = pd.DataFrame(events)
        events_df = events_df.sort_values(['case:concept:name', 'time:timestamp'])
        
        return events_df
    
    def _normalize_timestamp(self, timestamp, row, col_name: str) -> Optional[datetime]:
        """Normaliza timestamp para datetime."""
        # Se já é datetime
        if isinstance(timestamp, pd.Timestamp) or isinstance(timestamp, datetime):
            return timestamp
        
        # Se é string, tenta converter
        if isinstance(timestamp, str):
            try:
                return pd.to_datetime(timestamp)
            except:
                pass
        
        # Se tem coluna de data e hora separadas
        if 'DT_' in col_name:
            # Procura coluna de hora correspondente
            hr_col = col_name.replace('DT_', 'HR_')
            if hr_col in row.index and not pd.isna(row[hr_col]):
                try:
                    date_part = pd.to_datetime(timestamp).date()
                    time_part = pd.to_datetime(row[hr_col]).time()
                    return datetime.combine(date_part, time_part)
                except:
                    pass
        
        # Tenta conversão genérica
        try:
            return pd.to_datetime(timestamp)
        except:
            return None
    
    def _column_to_activity_name(self, col_name: str) -> str:
        """Converte nome de coluna em nome de atividade legível."""
        # Remove prefixos comuns
        activity = col_name.replace('DT_', '').replace('HR_', '')
        
        # Converte underscores em espaços e capitaliza
        activity = activity.replace('_', ' ').title()
        
        # Traduções comuns (PT -> PT legível)
        translations = {
            'Chamada Cc': 'Chamada Centro Cirúrgico',
            'Chegada Cc': 'Chegada Centro Cirúrgico',
            'Saida Rpa Cc': 'Saída RPA',
            'Saida Morgue Cc': 'Saída Morgue',
            'Proc Cirurgico': 'Procedimento Cirúrgico',
            'Anest': 'Anestesia',
            'Inducao Anest': 'Indução Anestesia',
        }
        
        for old, new in translations.items():
            if old in activity:
                activity = activity.replace(old, new)
        
        return activity
    
    def _add_classifier(self, xes_path: Path):
        """Adiciona classificador ao XES."""
        with open(xes_path, 'r', encoding='utf-8') as f:
            contents = f.readlines()
        
        # Insere classificador após <log>
        if len(contents) > 5:
            contents.insert(5, '  <classifier name="Activity" keys="concept:name"/>\n')
        
        with open(xes_path, 'w', encoding='utf-8') as f:
            f.write("".join(contents))
    
    def _log(self, message: str):
        """Imprime mensagem se verbose."""
        if self.verbose:
            print(message)


def convert_cirurgias_xlsx_to_xes(
    excel_path: Path | str,
    output_xes: Optional[Path | str] = None
) -> Path:
    """
    Função auxiliar específica para logs de cirurgias.
    
    Args:
        excel_path: Caminho do Excel com dados de cirurgias
        output_xes: Caminho de saída (None = mesmo nome .xes)
        
    Returns:
        Path do arquivo XES gerado
    """
    excel_path = Path(excel_path)
    
    if output_xes is None:
        output_xes = excel_path.with_suffix('.xes')
    
    converter = ExcelToXESConverter()
    converter.convert(
        excel_path=excel_path,
        output_xes=output_xes,
        case_id_column='NR_CIRURGIA',  # Específico para cirurgias
        # timestamp_columns será detectado automaticamente
    )
    
    return Path(output_xes)


# Exemplo de uso
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python excel_to_xes.py arquivo.xlsx [saida.xes]")
        sys.exit(1)
    
    excel_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = convert_cirurgias_xlsx_to_xes(excel_file, output_file)
    print(f"\n✓ Conversão concluída: {result}")

