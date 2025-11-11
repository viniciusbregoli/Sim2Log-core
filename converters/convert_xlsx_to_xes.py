#!/usr/bin/env python3
"""
Convert XLSX surgical data to XES format with room names as resources.
Usage: python convert_xlsx_to_xes.py <input.xlsx> <output.xes>
"""

import sys
import pandas as pd
from datetime import datetime
from xml.etree import ElementTree as ET
from xml.dom import minidom


def create_xes_structure():
    """Create base XES XML structure"""
    log = ET.Element('log', {
        'xes.version': '1849-2016',
        'xes.features': 'nested-attributes',
        'xmlns': 'http://www.xes-standard.org/'
    })

    # Add extensions
    ET.SubElement(log, 'extension', {
        'name': 'Concept',
        'prefix': 'concept',
        'uri': 'http://www.xes-standard.org/concept.xesext'
    })
    ET.SubElement(log, 'extension', {
        'name': 'Time',
        'prefix': 'time',
        'uri': 'http://www.xes-standard.org/time.xesext'
    })
    ET.SubElement(log, 'extension', {
        'name': 'Organizational',
        'prefix': 'org',
        'uri': 'http://www.xes-standard.org/org.xesext'
    })

    # Add classifier
    ET.SubElement(log, 'classifier', {
        'name': 'Activity',
        'keys': 'concept:name'
    })

    # Add origin
    ET.SubElement(log, 'string', {
        'key': 'origin',
        'value': 'xlsx'
    })

    return log


def parse_timestamp(date_val, time_val=None, allow_midnight=False):
    """Parse date and optional time into ISO format timestamp

    Args:
        date_val: Date value (string or datetime)
        time_val: Time value (string or datetime), optional
        allow_midnight: If True, returns date with 00:00:00 when time is missing
    """
    if pd.isna(date_val):
        return None

    if isinstance(date_val, str):
        # Parse string date
        date_parts = date_val.split('/')
        if len(date_parts) == 3:
            day, month, year = date_parts
            date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        else:
            return None
    else:
        # datetime object
        date_str = date_val.strftime('%Y-%m-%d')

    if time_val and not pd.isna(time_val):
        if isinstance(time_val, str):
            time_str = time_val
        else:
            time_str = time_val.strftime('%H:%M:%S')
        return f"{date_str}T{time_str}"
    else:
        # Se time_val é NaN mas allow_midnight=True, usa 00:00:00
        if allow_midnight:
            return f"{date_str}T00:00:00"
        return None


def create_event(concept_name, timestamp, resource, sala, procedimento, index):
    """Create an event element"""
    event = ET.Element('event')

    ET.SubElement(event, 'string', {
        'key': 'concept:name',
        'value': concept_name
    })

    if timestamp:
        ET.SubElement(event, 'date', {
            'key': 'time:timestamp',
            'value': timestamp
        })

    if resource and not pd.isna(resource):
        ET.SubElement(event, 'string', {
            'key': 'org:resource',
            'value': str(resource).strip()
        })

    if sala and not pd.isna(sala):
        ET.SubElement(event, 'string', {
            'key': 'sala',
            'value': str(sala).strip()
        })

    if procedimento and not pd.isna(procedimento):
        ET.SubElement(event, 'string', {
            'key': 'procedimento',
            'value': str(procedimento).strip()
        })

    ET.SubElement(event, 'int', {
        'key': '@@index',
        'value': str(index)
    })

    return event


def convert_xlsx_to_xes(xlsx_path, xes_path):
    """Convert XLSX to XES format"""
    print(f"Reading {xlsx_path}...")
    df = pd.read_excel(xlsx_path)

    print(f"Processing {len(df)} cases...")

    # Event mapping: column name -> activity name
    event_mapping = [
        ('DT_INICIO', 'HR_INICIO', 'Inicio'),
        ('DT_INICIO', 'CHAMADA_CC', 'Chamada Centro Cirúrgico'),
        ('DT_INICIO', 'CHEGADA_CC', 'Chegada Centro Cirúrgico'),
        ('DT_INICIO', 'ENTRADA_SALA', 'Entrada Sala'),
        ('DT_INICIO', 'INICIO_ANESTESIA', 'Inicio Anestesiaesia'),
        ('DT_INICIO', 'INICIO_PROC_CIRURGICO', 'Inicio Procedimento Cirúrgico'),
        ('DT_INICIO', 'TERMINO_PROC_CIRURGICO', 'Termino Procedimento Cirúrgico'),
        ('DT_INICIO', 'TERMINO_ANESTESIA', 'Termino Anestesiaesia'),
        ('DT_INICIO', 'ENTRADA_RPA', 'Entrada Rpa'),
        ('DT_INICIO', 'ENCAMINHAMENTO_UTI', 'Encaminhamento Uti'),
        ('DT_INICIO', 'CHAMADA_UI', 'Chamada Ui'),
        ('DT_INICIO', 'SAIDA_RPA_CC', 'Saida Rpa Cc'),
        ('DT_INICIO', 'SAIDA_MORGUE_CC', 'Saida Morgue Cc'),
        ('ALTA_HOSP', None, 'Alta Hospitalar'),
    ]

    # Create XES structure
    log = create_xes_structure()

    skipped_events = 0
    total_events = 0

    # Process each case
    for _, row in df.iterrows():
        case_id = str(int(row['NR_CIRURGIA'])) if not pd.isna(row['NR_CIRURGIA']) else 'unknown'
        sala = row['SALA'] if not pd.isna(row['SALA']) else ''
        procedimento = row['DS_PROCEDIMENTO'] if not pd.isna(row['DS_PROCEDIMENTO']) else ''

        # Use SALA como recurso
        resource = sala

        # Create trace
        trace = ET.SubElement(log, 'trace')
        ET.SubElement(trace, 'string', {
            'key': 'concept:name',
            'value': case_id
        })

        # Coletar eventos com timestamps válidos
        events_with_timestamps = []

        for date_col, time_col, activity_name in event_mapping:
            if date_col in row and not pd.isna(row[date_col]):
                time_val = row[time_col] if time_col and time_col in row else None
                timestamp = parse_timestamp(row[date_col], time_val)

                if timestamp:
                    events_with_timestamps.append({
                        'activity': activity_name,
                        'timestamp': timestamp,
                        'resource': resource,
                        'sala': sala,
                        'procedimento': procedimento
                    })
                    total_events += 1
                else:
                    skipped_events += 1

        # Pular traces vazios (casos cancelados ou sem dados)
        if len(events_with_timestamps) == 0:
            log.remove(trace)
            continue

        # Ordenar eventos por timestamp
        events_with_timestamps.sort(key=lambda x: x['timestamp'])

        # Adicionar eventos ordenados ao trace
        for index, event_data in enumerate(events_with_timestamps):
            event = create_event(
                event_data['activity'],
                event_data['timestamp'],
                event_data['resource'],
                event_data['sala'],
                event_data['procedimento'],
                index
            )
            trace.append(event)

    # Write XES file with pretty formatting
    print(f"Writing {xes_path}...")
    print(f"Total events created: {total_events}")
    print(f"Events skipped (missing timestamps): {skipped_events}")

    xml_str = minidom.parseString(ET.tostring(log, encoding='utf-8')).toprettyxml(indent="\t")

    with open(xes_path, 'w', encoding='utf-8') as f:
        f.write(xml_str)

    print(f"Conversion complete! Generated {xes_path}")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python convert_xlsx_to_xes.py <input.xlsx> <output.xes>")
        print("Example: python convert_xlsx_to_xes.py bases/CirurgiasMarcoHuc.xlsx media/CirurgiasMarcoHuc_converted.xes")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    convert_xlsx_to_xes(input_file, output_file)
