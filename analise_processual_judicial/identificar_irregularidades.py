#!/usr/bin/env python3
"""
Analisa linha do tempo de processo judicial e identifica irregularidades processuais.
Recebe JSON de extrair_dados.py e produz JSON com irregularidades detectadas.
"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path


def parse_data(data_str):
    try:
        return datetime.strptime(data_str, "%d/%m/%Y")
    except ValueError:
        return None


def diff_dias(d1, d2):
    return (d2 - d1).days


def buscar_evento(linha_tempo, tipos, apos_data=None, antes_data=None, campo_busca='tipo'):
    """Busca primeiro evento que combine com tipos e filtros de data."""
    for item in linha_tempo:
        texto_busca = item.get(campo_busca, '').upper()
        if campo_busca != 'tipo':
            texto_busca += ' ' + item.get('tipo', '').upper()
        if any(t.upper() in texto_busca for t in tipos):
            dt = parse_data(item['data'])
            if dt is None:
                continue
            if apos_data and dt < apos_data:
                continue
            if antes_data and dt > antes_data:
                continue
            return item, dt
    return None, None


def identificar_irregularidades(dados):
    irregularidades = []
    meta = dados.get('metadados', {})
    linha = dados.get('linha_do_tempo', [])
    indice = dados.get('indice_documentos', [])
    distrib = parse_data(meta.get('data_distribuicao', ''))
    prioridade = meta.get('prioridade', '')
    classe = meta.get('classe', '')

    if not linha:
        return irregularidades

    # 1. CITAÇÃO: Juizado Especial Cível - citação em até 30 dias da distribuição (Lei 9.099/95, art. 16)
    if 'Juizado Especial' in classe and distrib:
        citacao, dt_citacao = buscar_evento(linha, ['Citação'])
        if citacao:
            dias = diff_dias(distrib, dt_citacao)
            if dias > 30:
                irregularidades.append({
                    'gravidade': 'MEDIA',
                    'categoria': 'CITAÇÃO',
                    'descricao': f'Citação realizada em {dias} dias após distribuição (limite: 30 dias para JEC).',
                    'fundamento': 'Lei 9.099/1995, art. 16.',
                    'data_ocorrencia': citacao['data'],
                    'recomendacao': 'Verificar se houve justificativa para atraso ou se a parte foi prejudicada.'
                })
        else:
            hoje = datetime.now()
            dias = diff_dias(distrib, hoje)
            if dias > 30:
                irregularidades.append({
                    'gravidade': 'ALTA',
                    'categoria': 'CITAÇÃO',
                    'descricao': f'Não houve citação efetivada até o momento. Distribuição há {dias} dias.',
                    'fundamento': 'Lei 9.099/1995, art. 16.',
                    'data_ocorrencia': meta.get('data_distribuicao'),
                    'recomendacao': 'Requerer citação imediata ou verificar se há impedimento processual.'
                })

    # 2. PRIORIDADE IDOSO: tramitação prioritária (EC 103/2019; Estatuto do Idoso, art. 71)
    if 'IDOSO' in prioridade.upper():
        # Verificar se houve alguma movimentação que indique atraso injustificado
        # Critério simples: se houve mais de 60 dias entre duas movimentações significativas sem decisão
        eventos_sig = [e for e in linha if e.get('tipo', '') not in ['Outros', 'Comprovante Residência']]
        for i in range(len(eventos_sig) - 1):
            d1 = parse_data(eventos_sig[i]['data'])
            d2 = parse_data(eventos_sig[i+1]['data'])
            if d1 and d2 and diff_dias(d1, d2) > 60:
                irregularidades.append({
                    'gravidade': 'MEDIA',
                    'categoria': 'PRIORIDADE DE TRAMITAÇÃO',
                    'descricao': f'Intervalo de {diff_dias(d1,d2)} dias entre andamentos ({eventos_sig[i]["tipo"]} em {eventos_sig[i]["data"]} e {eventos_sig[i+1]["tipo"]} em {eventos_sig[i+1]["data"]}), podendo indicar descumprimento da prioridade de tramitação para idoso.',
                    'fundamento': 'EC 103/2019, art. 2º; Estatuto do Idoso (Lei 10.741/2003), art. 71; CPC/2015, art. 12, §1º.',
                    'data_ocorrencia': eventos_sig[i+1]['data'],
                    'recomendacao': 'Requerer prioridade na tramitação e intimação das partes para audiência/designação de novo ato processual.'
                })
                break  # evitar repetir

    # 3. TUTELA ANTECIPADA: decisão em até 48h quando houver periculum in mora (CPC/2015, art. 300)
    peticao_inicial = next((e for e in linha if 'Petição Inicial' in e.get('tipo', '')), None)
    if peticao_inicial:
        dt_pi = parse_data(peticao_inicial['data'])
        if dt_pi:
            # Buscar primeira decisão/despacho após petição inicial
            decisao, dt_dec = buscar_evento(linha, ['Decisão', 'Despacho', 'Ato Ordinatório'], apos_data=dt_pi)
            if decisao:
                dias = diff_dias(dt_pi, dt_dec)
                # Se pedido de tutela e primeira decisão levou mais de 15 dias úteis (~21 corridos)
                texto_pi = ' '.join([e.get('documento', '') for e in indice if 'Petição Inicial' in e.get('tipo', '')]).upper()
                if 'TUTELA' in texto_pi or 'LIMINAR' in texto_pi or 'ANTECIPADA' in texto_pi:
                    if dias > 21:
                        irregularidades.append({
                            'gravidade': 'ALTA',
                            'categoria': 'TUTELA ANTECIPADA',
                            'descricao': f'Primeira decisão sobre pedido de tutela antecipada em {dias} dias após a petição inicial.',
                            'fundamento': 'CPC/2015, art. 300; Súmula 634/STJ.',
                            'data_ocorrencia': decisao['data'],
                            'recomendacao': 'Requerer decisão liminar com urgência, considerando o periculum in mora alegado.'
                        })
            else:
                hoje = datetime.now()
                if diff_dias(dt_pi, hoje) > 30:
                    irregularidades.append({
                        'gravidade': 'ALTA',
                        'categoria': 'TUTELA ANTECIPADA',
                        'descricao': 'Pedido de tutela antecipada sem decisão há mais de 30 dias.',
                        'fundamento': 'CPC/2015, art. 300.',
                        'data_ocorrencia': peticao_inicial['data'],
                        'recomendacao': 'Requerer decisão liminar, considerando a urgência do caso.'
                    })

    # 4. CONTESTAÇÃO: prazo de 15 dias após citação (CPC/2015, art. 335)
    citacao_evento, dt_cit = buscar_evento(linha, ['Citação'])
    contestacao, dt_cont = buscar_evento(linha, ['Contestação', 'CONTESTACAO', 'contestacao', 'contestação'], apos_data=dt_cit, campo_busca='documento')
    if citacao_evento and contestacao and dt_cit and dt_cont:
        dias = diff_dias(dt_cit, dt_cont)
        if dias > 20:  # 15 dias úteis ≈ 20 corridos
            irregularidades.append({
                'gravidade': 'MEDIA',
                'categoria': 'CONTESTAÇÃO',
                'descricao': f'Contestação apresentada em {dias} dias após citação (prazo: 15 dias úteis).',
                'fundamento': 'CPC/2015, art. 335.',
                'data_ocorrencia': contestacao['data'],
                'recomendacao': 'Verificar se houve prorrogação ou se deve ser declarada intempestiva.'
            })

    # 5. INTIMAÇÃO: verificar se houve intimação da parte autora sobre contestação
    if contestacao and dt_cont:
        intimacao, dt_int = buscar_evento(linha, ['Citação', 'Intimação', 'Ato Ordinatório', 'Certidão', 'intimacao', 'intimação'], apos_data=dt_cont, campo_busca='documento')
        if not intimacao:
            hoje = datetime.now()
            if diff_dias(dt_cont, hoje) > 30:
                irregularidades.append({
                    'gravidade': 'MEDIA',
                    'categoria': 'INTIMAÇÃO',
                    'descricao': 'Não houve intimação da parte autora sobre a contestação após mais de 30 dias.',
                    'fundamento': 'CPC/2015, art. 339; art. 5º, §2º.',
                    'data_ocorrencia': contestacao['data'],
                    'recomendacao': 'Requerer intimação para manifestação sobre a contestação, se ainda não houver réplica.'
                })

    # 6. AUDIÊNCIA: em JEC, audiência de conciliação deve ser realizada em até 60 dias da citação (Lei 9.099/95, art. 20)
    if 'Juizado Especial' in classe and citacao_evento and dt_cit:
        audiencia, dt_aud = buscar_evento(linha, ['Audiência', 'Termo de Audiência'], apos_data=dt_cit)
        if audiencia and dt_aud:
            dias = diff_dias(dt_cit, dt_aud)
            if dias > 60:
                irregularidades.append({
                    'gravidade': 'MEDIA',
                    'categoria': 'AUDIÊNCIA',
                    'descricao': f'Audiência realizada em {dias} dias após citação (limite: 60 dias para JEC).',
                    'fundamento': 'Lei 9.099/1995, art. 20.',
                    'data_ocorrencia': audiencia['data'],
                    'recomendacao': 'Verificar se houve justificativa ou se a parte foi prejudicada pelo atraso.'
                })
        else:
            hoje = datetime.now()
            if diff_dias(dt_cit, hoje) > 60:
                irregularidades.append({
                    'gravidade': 'ALTA',
                    'categoria': 'AUDIÊNCIA',
                    'descricao': 'Audiência de conciliação não designada/realizada após 60 dias da citação.',
                    'fundamento': 'Lei 9.099/1995, art. 20.',
                    'data_ocorrencia': citacao_evento['data'],
                    'recomendacao': 'Requerer designação imediata de audiência de conciliação.'
                })

    # 7. SENTENÇA: em JEC, sentença deve ser proferida em até 15 dias da audiência (Lei 9.099/95, art. 22)
    if 'Juizado Especial' in classe:
        audiencia, dt_aud = buscar_evento(linha, ['Termo de Audiência', 'Audiência', 'audiencia', 'audiência'], campo_busca='documento')
        if audiencia and dt_aud:
            sentenca, dt_sent = buscar_evento(linha, ['Sentença', 'sentença', 'sentenca'], apos_data=dt_aud, campo_busca='documento')
            if sentenca and dt_sent:
                dias = diff_dias(dt_aud, dt_sent)
                if dias > 20:  # 15 dias corridos ≈ 20 para margem
                    irregularidades.append({
                        'gravidade': 'BAIXA',
                        'categoria': 'SENTENÇA',
                        'descricao': f'Sentença proferida em {dias} dias após audiência (prazo legal: 15 dias corridos no JEC).',
                        'fundamento': 'Lei 9.099/1995, art. 22.',
                        'data_ocorrencia': sentenca['data'],
                        'recomendacao': 'Registrar o atraso para eventual recurso ou execução.'
                    })

    # 8. RECURSO: prazo de 15 dias para interposição (CPC/2015, art. 1.003)
    sentenca, dt_sent = buscar_evento(linha, ['Sentença', 'sentença', 'sentenca'], campo_busca='documento')
    if sentenca and dt_sent:
        recurso, dt_rec = buscar_evento(linha, ['Agravo', 'Apelação', 'Recurso', 'agravo', 'apelação', 'recurso'], apos_data=dt_sent, campo_busca='documento')
        if recurso and dt_rec:
            dias = diff_dias(dt_sent, dt_rec)
            if dias > 20:  # 15 dias úteis
                irregularidades.append({
                    'gravidade': 'ALTA',
                    'categoria': 'RECURSO',
                    'descricao': f'Recurso interposto em {dias} dias após sentença (prazo: 15 dias úteis).',
                    'fundamento': 'CPC/2015, art. 1.003.',
                    'data_ocorrencia': recurso['data'],
                    'recomendacao': 'Verificar se o recurso é tempestivo ou se houve decadência do prazo.'
                })

    # 9. CONCLUSÃO: autos conclusos sem decisão por mais de 30 dias
    conclusao, dt_conc = buscar_evento(linha, ['Conclusão'])
    if conclusao and dt_conc:
        hoje = datetime.now()
        dias = diff_dias(dt_conc, hoje)
        if dias > 30:
            irregularidades.append({
                'gravidade': 'MEDIA',
                'categoria': 'CONCLUSÃO',
                'descricao': f'Autos conclusos para decisão há {dias} dias sem manifestação judicial.',
                'fundamento': 'Resolução CNJ 185/2013; CPC/2015, art. 162.',
                'data_ocorrencia': conclusao['data'],
                'recomendacao': 'Requerer manifestação judicial ou intimação do juiz sobre o estado dos autos.'
            })

    # 10. GRATUIDADE DE JUSTIÇA: verificar se foi deferida quando pleiteada
    texto_completo = ' '.join([e.get('documento', '') for e in indice]).upper()
    if 'GRATUIDADE' in texto_completo or 'GRATUITA' in texto_completo or 'JUSTIÇA' in texto_completo:
        # Verificar se há alguma decisão sobre gratuidade nos andamentos
        tem_decisao_gj = any('GRATUIDADE' in a.get('resumo', '').upper() or 'GRATUITA' in a.get('resumo', '').upper() for a in dados.get('andamentos_detectados', []))
        if not tem_decisao_gj:
            irregularidades.append({
                'gravidade': 'BAIXA',
                'categoria': 'GRATUIDADE DE JUSTIÇA',
                'descricao': 'Pedido de gratuidade de justiça apresentado, mas sem decisão explícita detectada nos andamentos.',
                'fundamento': 'CPC/2015, art. 98 e 99.',
                'data_ocorrencia': None,
                'recomendacao': 'Verificar se houve deferimento tácito ou se é necessário requerer decisão expressa.'
            })

    return sorted(irregularidades, key=lambda x: ({'ALTA': 0, 'MEDIA': 1, 'BAIXA': 2}.get(x['gravidade'], 3)))


def main():
    if len(sys.argv) < 2:
        print("Uso: python identificar_irregularidades.py <dados.json> [saida.json]")
        sys.exit(1)
    entrada = Path(sys.argv[1])
    saida = Path(sys.argv[2]) if len(sys.argv) > 2 else entrada.with_name(entrada.stem + '_irregularidades.json')

    with open(entrada, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    irregularidades = identificar_irregularidades(dados)

    resultado = {
        'numero_processo': dados.get('metadados', {}).get('numero_processo'),
        'total_irregularidades': len(irregularidades),
        'irregularidades': irregularidades
    }

    with open(saida, 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    print(f"Irregularidades identificadas: {len(irregularidades)}. Salvo em: {saida}")


if __name__ == '__main__':
    main()
