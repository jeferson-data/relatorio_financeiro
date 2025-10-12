# dashboard_financeiro.py - CORREÇÃO COMPLETA DO PROBLEMA DE DATAS
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import tempfile
import os
import base64
from io import BytesIO
from reportlab.platypus import Image
import plotly.io as pio


def salvar_grafico_como_imagem(fig):
    buffer = BytesIO()
    pio.write_image(fig, buffer, format='png')
    buffer.seek(0)
    return buffer

# ============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================================


st.set_page_config(
    page_title="Dashboard Financeiro",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# SISTEMA DE PLANOS ATUALIZADO
# ============================================================================

PLANOS = {
    "Básico": {
        "kpis": ["receita_total", "despesa_total", "lucro_liquido", "margem_lucro", "total_transacoes"],
        "graficos": ["evolucao_mensal", "top_clientes", "top_fornecedores"],
        "relatorios": ["basico"],
        "descricao": "(Valores referentes ao fluxo de caixa - receita total, despesa total, saldo, top 10 clientes, top 10 fornecedores)"
    },
    "Intermediário": {
        "kpis": ["receita_total", "despesa_total", "lucro_liquido", "margem_lucro", "total_transacoes",
                 "contas_receber", "contas_pagar", "total_pago_recebido"],
        "graficos": ["evolucao_mensal", "top_clientes", "top_fornecedores",
                     "subcategorias_receita", "subcategorias_despesa"],
        "relatorios": ["basico", "intermediario"],
        "descricao": "Básico mais (valores referentes a top 10 subcategorias receita, top 10 subcategoria despesas, top 10 clientes, top 10 fornecedores)"
    },
    "Avançado": {
        "kpis": ["receita_total", "despesa_total", "lucro_liquido", "margem_lucro", "total_transacoes",
                 "contas_receber", "contas_pagar", "total_pago_recebido", "roi", "liquidez_corrente",
                 "crescimento_receita", "prazo_medio_recebimento", "ciclo_caixa"],
        "graficos": ["evolucao_mensal", "fluxo_caixa", "top_clientes", "top_fornecedores",
                     "subcategorias_receita", "subcategorias_despesa", "top_clientes_inadimplentes",
                     "top_fornecedores_pagos"],
        "relatorios": ["basico", "intermediario", "avancado"],
        "descricao": "Básico mais Intermediário mais (valores referentes a roi, margem de lucro, liquidez e crescimento e relatório gerencial)"
    }
}

# ============================================================================
# FUNÇÕES DE PROCESSAMENTO DE DADOS - CORRIGIDAS
# ============================================================================


def detectar_formato_data(coluna_data):
    """Detecta automaticamente o formato da data"""
    formatos_teste = [
        '%Y-%m-%d',      # 2024-01-15
        '%d/%m/%Y',      # 15/01/2024
        '%d/%m/%y',      # 15/01/24
        '%d-%m-%Y',      # 15-01-2024
        '%d-%m-%y',      # 15-01-24
        '%m/%d/%Y',      # 01/15/2024 (formato EUA)
        '%Y/%m/%d',      # 2024/01/15
        '%d.%m.%Y',      # 15.01.2024
        '%d de %B de %Y',  # 15 de Janeiro de 2024 (português)
        '%B %d, %Y',     # January 15, 2024 (inglês)
    ]

    amostra = coluna_data.dropna().head(10) if len(
        coluna_data) > 10 else coluna_data.dropna()

    for formato in formatos_teste:
        try:
            # Tenta converter uma amostra
            pd.to_datetime(amostra, format=formato, errors='raise')
            return formato
        except:
            continue

    return None


def converter_coluna_data(df, coluna_data):
    """Converte coluna de data com múltiplas tentativas"""
    # Primeiro, tenta detectar o formato
    formato_detectado = detectar_formato_data(df[coluna_data])

    if formato_detectado:
        st.sidebar.info(f"📅 Formato detectado: {formato_detectado}")
        try:
            df[coluna_data] = pd.to_datetime(
                df[coluna_data], format=formato_detectado, errors='coerce')
            return df
        except Exception as e:
            st.sidebar.warning(f"⚠️ Formato detectado não funcionou: {e}")

    # Se não detectou ou falhou, tenta métodos alternativos
    st.sidebar.info("🔄 Tentando conversão automática...")

    # Método 1: pd.to_datetime com infer_datetime_format
    try:
        df[coluna_data] = pd.to_datetime(
            df[coluna_data], infer_datetime_format=True, errors='coerce')
        if not df[coluna_data].isna().all():
            return df
    except:
        pass

    # Método 2: dayfirst para formato brasileiro
    try:
        df[coluna_data] = pd.to_datetime(
            df[coluna_data], dayfirst=True, errors='coerce')
        if not df[coluna_data].isna().all():
            return df
    except:
        pass

    # Método 3: Última tentativa - converter qualquer coisa
    try:
        df[coluna_data] = pd.to_datetime(df[coluna_data], errors='coerce')
    except Exception as e:
        st.error(f"❌ Erro crítico na conversão de datas: {e}")

    return df


def processar_dados(uploaded_file):
    """Processa o arquivo CSV e prepara os dados - VERSÃO CORRIGIDA"""
    try:
        # Ler o arquivo
        df = pd.read_csv(uploaded_file)

        # Mostrar informações do arquivo
        st.sidebar.success(f"✅ Arquivo carregado: {len(df)} transações")
        st.sidebar.info(
            f"📊 Colunas encontradas: {', '.join(df.columns.tolist())}")

        # Verificar colunas obrigatórias
        colunas_obrigatorias = ['Data', 'Valor']
        colunas_faltantes = [
            col for col in colunas_obrigatorias if col not in df.columns]
        if colunas_faltantes:
            st.error(
                f"❌ Colunas obrigatórias faltando: {', '.join(colunas_faltantes)}")
            st.info("💡 As colunas obrigatórias são: 'Data' e 'Valor'")
            return None

        # CONVERSÃO DE DATA - MÉTODO CORRIGIDO
        st.sidebar.info("🔄 Convertendo datas...")

        # Mostrar amostra das datas originais
        st.sidebar.write(f"📋 Amostra de datas: {df['Data'].head(3).tolist()}")

        # Converter coluna de data
        df = converter_coluna_data(df, 'Data')

        # Verificar se a conversão foi bem sucedida
        datas_invalidas = df['Data'].isna().sum()
        if datas_invalidas > 0:
            st.warning(
                f"⚠️ {datas_invalidas} datas não puderam ser convertidas e serão removidas")
            df = df.dropna(subset=['Data'])

        if len(df) == 0:
            st.error(
                "❌ Todas as datas são inválidas. Verifique o formato da coluna 'Data'.")
            return None

        # Criar colunas de data auxiliares
        df['mes'] = df['Data'].dt.to_period('M')
        df['ano'] = df['Data'].dt.year
        df['mes_ano'] = df['Data'].dt.strftime('%Y-%m')
        df['dia'] = df['Data'].dt.date

        # Garantir que valores numéricos estão corretos
        df['Valor'] = pd.to_numeric(df['Valor'], errors='coerce')
        valores_invalidos = df['Valor'].isna().sum()
        if valores_invalidos > 0:
            st.warning(
                f"⚠️ {valores_invalidos} valores inválidos na coluna 'Valor' serão definidos como 0")
            df['Valor'] = df['Valor'].fillna(0)

        # Processar coluna 'Pago' se existir
        if 'Pago' in df.columns:
            df['Pago'] = pd.to_numeric(df['Pago'], errors='coerce')
            df['Pago'] = df['Pago'].fillna(0)

        # Processar coluna 'A Vencer' se existir
        if 'A Vencer' in df.columns:
            df['A Vencer'] = pd.to_numeric(df['A Vencer'], errors='coerce')
            df['A Vencer'] = df['A Vencer'].fillna(0)

        # Converter colunas textuais para string e corrigir typo comum
        colunas_texto = []
        if 'Categotia' in df.columns:  # Nota: há um typo aqui na coluna original
            colunas_texto.append('Categotia')
            df.rename(columns={'Categotia': 'Categoria'}, inplace=True)

        colunas_texto.extend(['Categoria', 'Subcategoria', 'Tipo', 'Cliente'])

        for coluna in colunas_texto:
            if coluna in df.columns:
                df[coluna] = df[coluna].astype(str)
                df[coluna] = df[coluna].replace('nan', 'Não Informado')

        st.sidebar.success("✅ Dados processados com sucesso!")
        return df

    except Exception as e:
        st.error(f"❌ Erro ao processar arquivo: {e}")
        return None


def calcular_kpis_avancados(df):
    """Calcula KPIs financeiros avançados - CÁLCULOS CORRIGIDOS"""
    kpis = {}

    try:
        # KPIs básicos - CALCULADOS DA COLUNA VALOR
        receitas_df = df[df['Tipo'] == 'Receita']
        despesas_df = df[df['Tipo'] == 'Despesa']

        kpis['receita_total'] = receitas_df['Valor'].sum()
        kpis['despesa_total'] = despesas_df['Valor'].sum()
        kpis['lucro_liquido'] = kpis['receita_total'] - kpis['despesa_total']
        kpis['margem_lucro'] = (
            kpis['lucro_liquido'] / kpis['receita_total'] * 100) if kpis['receita_total'] > 0 else 0
        kpis['total_transacoes'] = len(df)
        kpis['valor_total'] = df['Valor'].sum()

        # Contas a Receber e Pagar - CALCULADOS DAS COLUNAS PAGO E A VENCER
        if 'Pago' in df.columns and 'A Vencer' in df.columns and 'Tipo' in df.columns:
            # Contas a Receber: Receitas com 'A Vencer' > 0
            kpis['contas_receber'] = df[(df['Tipo'] == 'Receita') & (
                df['A Vencer'] > 0)]['A Vencer'].sum()
            # Contas a Pagar: Despesas com 'A Vencer' > 0
            kpis['contas_pagar'] = df[(df['Tipo'] == 'Despesa') & (
                df['A Vencer'] > 0)]['A Vencer'].sum()
            # Total já pago/recebido
            kpis['total_pago_recebido'] = df['Pago'].sum()
        else:
            kpis['contas_receber'] = 0
            kpis['contas_pagar'] = 0
            kpis['total_pago_recebido'] = 0

        # KPIs avançados (apenas para plano Avançado) - CALCULADOS DA COLUNA VALOR
        # ROI (Return on Investment)
        kpis['roi'] = (kpis['lucro_liquido'] / kpis['despesa_total']
                       * 100) if kpis['despesa_total'] > 0 else 0

        # Liquidez Corrente
        kpis['liquidez_corrente'] = (kpis['contas_receber'] + kpis['total_pago_recebido']) / \
            kpis['contas_pagar'] if kpis['contas_pagar'] > 0 else 0

        # Crescimento da Receita - CORREÇÃO: VERIFICAR SE EXISTEM DATAS VÁLIDAS
        if 'mes_ano' in df.columns and not df.empty:
            receita_mensal = df[df['Tipo'] == 'Receita'].groupby('mes_ano')[
                'Valor'].sum()
            if len(receita_mensal) > 1:
                ultimo_mes = receita_mensal.iloc[-1]
                penultimo_mes = receita_mensal.iloc[-2]
                kpis['crescimento_receita'] = (
                    (ultimo_mes - penultimo_mes) / penultimo_mes * 100) if penultimo_mes > 0 else 0
            else:
                kpis['crescimento_receita'] = 0
        else:
            kpis['crescimento_receita'] = 0

        # Prazo Médio de Recebimento - CORREÇÃO: VERIFICAR SE EXISTEM DATAS VÁLIDAS
        if 'Data' in df.columns and 'Tipo' in df.columns and not df.empty:
            receitas_pendentes = df[(
                df['Tipo'] == 'Receita') & (df['A Vencer'] > 0)]
            if len(receitas_pendentes) > 0 and not receitas_pendentes['Data'].isna().all():
                # Garantir que as datas são válidas antes de calcular
                datas_validas = receitas_pendentes['Data'].dropna()
                if len(datas_validas) > 0:
                    hoje = datetime.now().date()
                    dias_vencimento = [
                        (hoje - data.date()).days for data in datas_validas]
                    kpis['prazo_medio_recebimento'] = sum(
                        dias_vencimento) / len(dias_vencimento)
                else:
                    kpis['prazo_medio_recebimento'] = 0
            else:
                kpis['prazo_medio_recebimento'] = 0
        else:
            kpis['prazo_medio_recebimento'] = 0

        # Ciclo de Caixa
        kpis['ciclo_caixa'] = kpis['prazo_medio_recebimento']

        return kpis

    except Exception as e:
        st.error(f"Erro ao calcular KPIs: {e}")
        # Retornar KPIs básicos em caso de erro
        return {
            'receita_total': df[df['Tipo'] == 'Receita']['Valor'].sum() if 'Tipo' in df.columns else 0,
            'despesa_total': df[df['Tipo'] == 'Despesa']['Valor'].sum() if 'Tipo' in df.columns else 0,
            'lucro_liquido': 0,
            'margem_lucro': 0,
            'total_transacoes': len(df),
            'valor_total': df['Valor'].sum() if 'Valor' in df.columns else 0,
            'contas_receber': 0,
            'contas_pagar': 0,
            'total_pago_recebido': 0
        }

# ============================================================================
# FUNÇÕES DE VISUALIZAÇÃO POR PLANO - GRÁFICOS CORRIGIDOS
# ============================================================================


def criar_grafico_fluxo_caixa(df):
    """Gráfico de fluxo de caixa"""
    if 'Pago' in df.columns and 'A Vencer' in df.columns and 'Tipo' in df.columns:
        try:
            contas_receber = df[(df['Tipo'] == 'Receita') & (
                df['A Vencer'] > 0)]['A Vencer'].sum()
            contas_pagar = df[(df['Tipo'] == 'Despesa') & (
                df['A Vencer'] > 0)]['A Vencer'].sum()
            total_pago_recebido = df['Pago'].sum()

            fluxo_data = {
                'Categoria': ['Contas a Receber', 'Contas a Pagar', 'Pago/Recebido'],
                'Valor': [contas_receber, contas_pagar, total_pago_recebido]
            }
            fluxo_df = pd.DataFrame(fluxo_data)

            fig = px.bar(fluxo_df, x='Categoria', y='Valor',
                         title='FLUXO DE CAIXA',
                         color='Categoria',
                         color_discrete_map={
                             'Contas a Receber': '#00CC96',
                             'Contas a Pagar': '#EF553B',
                             'Pago/Recebido': '#636EFA'
                         })
            return fig
        except:
            return None
    return None


def criar_grafico_evolucao_mensal(df):
    """Evolução Mensal - Receitas x Despesas x Saldo - Barras Verticais"""
    if 'mes_ano' in df.columns and 'Tipo' in df.columns:
        try:
            mensal = df.groupby('mes_ano').apply(
                lambda x: pd.Series({
                    'receita': x[x['Tipo'] == 'Receita']['Valor'].sum(),
                    'despesa': x[x['Tipo'] == 'Despesa']['Valor'].sum()
                })
            ).reset_index()

            mensal['saldo'] = mensal['receita'] - mensal['despesa']

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=mensal['mes_ano'], y=mensal['receita'], name='Receitas', marker_color='#00CC96'))
            fig.add_trace(go.Bar(
                x=mensal['mes_ano'], y=mensal['despesa'], name='Despesas', marker_color='#EF553B'))
            fig.add_trace(go.Bar(
                x=mensal['mes_ano'], y=mensal['saldo'], name='Saldo', marker_color='#636EFA'))

            fig.update_layout(
                title='EVOLUÇÃO MENSAL - Receitas x Despesas x Saldo',
                barmode='group',
                xaxis_title='Mês',
                yaxis_title='Valor (R$)'
            )
            return fig
        except:
            return None
    return None


def criar_grafico_top_10_clientes(df):
    """Top 10 Clientes - Cálculo da coluna Valor com condicional Receita"""
    if 'Cliente' in df.columns and 'Tipo' in df.columns:
        try:
            top_clientes = df[df['Tipo'] == 'Receita'].groupby(
                'Cliente')['Valor'].sum().nlargest(10)
            if len(top_clientes) > 0:
                fig = px.bar(x=top_clientes.values, y=top_clientes.index,
                             orientation='h',
                             title='TOP 10 CLIENTES - Maiores Receitas',
                             labels={'x': 'Valor (R$)', 'y': 'Cliente'},
                             color=top_clientes.values,
                             color_continuous_scale='Viridis')
                return fig
        except:
            return None
    return None


def criar_grafico_top_10_fornecedores(df):
    """Top 10 Fornecedores - Cálculo da coluna Valor com condicional Despesa"""
    if 'Cliente' in df.columns and 'Tipo' in df.columns:
        try:
            top_fornecedores = df[df['Tipo'] == 'Despesa'].groupby(
                'Cliente')['Valor'].sum().nlargest(10)
            if len(top_fornecedores) > 0:
                fig = px.bar(x=top_fornecedores.values, y=top_fornecedores.index,
                             orientation='h',
                             title='TOP 10 FORNECEDORES - Maiores Despesas',
                             labels={'x': 'Valor (R$)', 'y': 'Fornecedor'},
                             color=top_fornecedores.values,
                             color_continuous_scale='Reds')
                return fig
        except:
            return None
    return None


def criar_grafico_subcategorias_receita(df):
    """Top 10 Subcategorias Receita - Cálculo da coluna Valor com condicional Receita"""
    if 'Subcategoria' in df.columns and 'Tipo' in df.columns:
        try:
            subcategorias = df[df['Tipo'] == 'Receita'].groupby(
                'Subcategoria')['Valor'].sum().nlargest(10)
            if len(subcategorias) > 0:
                fig = px.pie(values=subcategorias.values, names=subcategorias.index,
                             title='TOP 10 SUBCATEGORIAS DE RECEITA',
                             color_discrete_sequence=px.colors.sequential.Viridis)
                return fig
        except:
            return None
    return None


def criar_grafico_subcategorias_despesa(df):
    """Top 10 Subcategorias Despesa - Cálculo da coluna Valor com condicional Despesa"""
    if 'Subcategoria' in df.columns and 'Tipo' in df.columns:
        try:
            subcategorias = df[df['Tipo'] == 'Despesa'].groupby(
                'Subcategoria')['Valor'].sum().nlargest(10)
            if len(subcategorias) > 0:
                fig = px.pie(values=subcategorias.values, names=subcategorias.index,
                             title='TOP 10 SUBCATEGORIAS DE DESPESA',
                             color_discrete_sequence=px.colors.sequential.Reds)
                return fig
        except:
            return None
    return None


def criar_grafico_top_clientes_inadimplentes(df):
    """Top 10 Clientes Inadimplentes - Cálculo da coluna A Vencer com condicional Receita"""
    if 'Cliente' in df.columns and 'Tipo' in df.columns and 'A Vencer' in df.columns:
        try:
            clientes_inadimplentes = df[(df['Tipo'] == 'Receita') & (
                df['A Vencer'] > 0)].groupby('Cliente')['A Vencer'].sum().nlargest(10)
            if len(clientes_inadimplentes) > 0:
                fig = px.bar(x=clientes_inadimplentes.values, y=clientes_inadimplentes.index,
                             orientation='h',
                             title='TOP 10 CLIENTES INADIMPLENTES',
                             labels={
                                 'x': 'Valor a Receber (R$)', 'y': 'Cliente'},
                             color=clientes_inadimplentes.values,
                             color_continuous_scale='Oranges')
                return fig
        except:
            return None
    return None


def criar_grafico_top_fornecedores_pagos(df):
    """Top 10 Fornecedores Mais Pagos - Cálculo da coluna Pago com condicional Despesa"""
    if 'Cliente' in df.columns and 'Tipo' in df.columns and 'Pago' in df.columns:
        try:
            fornecedores_pagos = df[(df['Tipo'] == 'Despesa') & (
                df['Pago'] > 0)].groupby('Cliente')['Pago'].sum().nlargest(10)
            if len(fornecedores_pagos) > 0:
                fig = px.bar(x=fornecedores_pagos.values, y=fornecedores_pagos.index,
                             orientation='h',
                             title='TOP 10 FORNECEDORES MAIS PAGOS',
                             labels={
                                 'x': 'Valor Pago (R$)', 'y': 'Fornecedor'},
                             color=fornecedores_pagos.values,
                             color_continuous_scale='Greens')
                return fig
        except:
            return None
    return None


def gerar_insights(kpis):
    insights = []

    if kpis.get('lucro_liquido', 0) < 0:
        insights.append(
            "⚠️ A empresa está operando com prejuízo neste período.")

    if kpis.get('margem_lucro', 0) < 10:
        insights.append(
            "⚠️ Margem de lucro considerada baixa. Avalie os custos operacionais.")

    if kpis.get('crescimento_receita', 0) < 0:
        insights.append(
            "⚠️ Receita caiu em relação ao mês anterior. Verifique causas.")

    if kpis.get('liquidez_corrente', 0) < 1:
        insights.append(
            "⚠️ Liquidez abaixo do ideal. Risco de falta de caixa para pagar obrigações.")

    if kpis.get('roi', 0) > 20:
        insights.append(
            "✅ Excelente retorno sobre investimento. Estratégias estão gerando bons resultados.")

    if kpis.get('crescimento_receita', 0) > 10:
        insights.append("✅ Receita em expansão. Bom desempenho comercial.")

    if kpis.get('prazo_medio_recebimento', 999) < 30:
        insights.append(
            "✅ Boa eficiência na cobrança. Clientes estão pagando rápido.")

    return insights


# ============================================================================
# FUNÇÕES DE RELATÓRIOS POR PLANO ATUALIZADAS
# ============================================================================


def gerar_relatorio_por_plano(kpis, df, filtros, plano_selecionado):
    """Gera relatório específico para cada plano"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            filename = tmp_file.name

        doc = SimpleDocTemplate(filename, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()

        # Cabeçalho do relatório
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=16,
            spaceAfter=20,
            alignment=1,
            textColor=colors.black
        )

        if plano_selecionado == "Básico":
            title = Paragraph(
                f"RELATÓRIO FINANCEIRO - PLANO BÁSICO", title_style)
        elif plano_selecionado == "Intermediário":
            title = Paragraph(
                f"RELATÓRIO FINANCEIRO - PLANO INTERMEDIÁRIO", title_style)
        else:
            title = Paragraph(
                f"RELATÓRIO FINANCEIRO - PLANO AVANÇADO", title_style)

        elements.append(title)

        # Descrição do plano
        desc_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            alignment=1,
            textColor=colors.black
        )

        plano_desc = PLANOS[plano_selecionado]["descricao"]
        elements.append(Paragraph(plano_desc, desc_style))
        elements.append(Spacer(1, 10))

        # Data e período
        data_text = f"Período: {filtros.get('periodo', 'Todo o período')} | Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}"
        elements.append(Paragraph(data_text, desc_style))
        elements.append(Spacer(1, 20))

        # KPIs conforme o plano
        kpi_style = ParagraphStyle(
            'CustomHeading2',
            parent=styles['Heading2'],
            fontSize=12,
            spaceAfter=12,
            textColor=colors.HexColor('#2E86AB')
        )

        elements.append(Paragraph("INDICADORES PRINCIPAIS", kpi_style))

        # Tabela de KPIs baseada no plano
        kpi_data = [['INDICADOR', 'VALOR']]

        plano_config = PLANOS[plano_selecionado]

        for kpi in plano_config["kpis"]:
            if kpi in kpis:
                if kpi in ['receita_total', 'despesa_total', 'lucro_liquido', 'contas_receber', 'contas_pagar', 'total_pago_recebido']:
                    valor = f"R$ {kpis[kpi]:,.2f}"
                elif kpi in ['margem_lucro', 'roi', 'crescimento_receita']:
                    valor = f"{kpis[kpi]:.1f}%"
                elif kpi == 'liquidez_corrente':
                    valor = f"{kpis[kpi]:.2f}"
                elif kpi in ['prazo_medio_recebimento', 'ciclo_caixa']:
                    valor = f"{kpis[kpi]:.0f} dias"
                else:
                    valor = f"{kpis[kpi]:,}"

                nome_kpi = kpi.replace('_', ' ').title()
                kpi_data.append([nome_kpi, valor])

        kpi_table = Table(kpi_data)
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 1), (-1, -1), 9)
        ]))
        elements.append(kpi_table)
        elements.append(Spacer(1, 20))

        # INSIGHTS AUTOMÁTICOS
        elements.append(Paragraph("ANÁLISE PRÉVIA", kpi_style))
        insights = gerar_insights(kpis)

        if insights:
            for texto in insights:
                elements.append(Paragraph(texto, styles['Normal']))
        else:
            elements.append(Paragraph(
                "Nenhum alerta ou destaque relevante para este período.", styles['Normal']))

        elements.append(Spacer(1, 20))

        # Informação sobre gráficos
        elements.append(Paragraph("GRÁFICOS DISPONÍVEIS", kpi_style))
        graficos_info = ", ".join([g.replace('_', ' ').title()
                                  for g in plano_config["graficos"]])
        elements.append(Paragraph(
            f"Este plano inclui os seguintes gráficos: {graficos_info}", styles['Normal']))
        elements.append(Paragraph(
            "Os gráficos estão disponíveis para visualização no dashboard online.", styles['Normal']))
        elements.append(Spacer(1, 20))

        # Inserir gráficos no PDF
        elements.append(Paragraph("VISUALIZAÇÕES GRÁFICAS", kpi_style))

        for grafico_nome in plano_config["graficos"]:
            try:
                if grafico_nome == "evolucao_mensal":
                    fig = criar_grafico_evolucao_mensal(df)
                elif grafico_nome == "fluxo_caixa":
                    fig = criar_grafico_fluxo_caixa(df)
                elif grafico_nome == "top_clientes":
                    fig = criar_grafico_top_10_clientes(df)
                elif grafico_nome == "top_fornecedores":
                    fig = criar_grafico_top_10_fornecedores(df)
                elif grafico_nome == "subcategorias_receita":
                    fig = criar_grafico_subcategorias_receita(df)
                elif grafico_nome == "subcategorias_despesa":
                    fig = criar_grafico_subcategorias_despesa(df)
                elif grafico_nome == "top_clientes_inadimplentes":
                    fig = criar_grafico_top_clientes_inadimplentes(df)
                elif grafico_nome == "top_fornecedores_pagos":
                    fig = criar_grafico_top_fornecedores_pagos(df)
                else:
                    fig = None

                if fig:
                    img_buffer = salvar_grafico_como_imagem(fig)
                    grafico_img = Image(img_buffer, width=400, height=250)
                    elements.append(Spacer(1, 10))
                    elements.append(grafico_img)
                    elements.append(Spacer(1, 20))
            except Exception as e:
                st.warning(f"Erro ao gerar gráfico {grafico_nome}: {e}")

        # Finaliza e salva o PDF
        doc.build(elements)
        return filename
    except Exception as e:
        st.error(f"Erro ao gerar relatório: {e}")
        return None


# ============================================================================
# FUNÇÕES DE FILTROS
# ============================================================================


def criar_filtros_sidebar():
    """Cria filtros na sidebar"""
    st.sidebar.header("🔧 Configurações")

    filtros = {}

    # SELEÇÃO DO PLANO
    st.sidebar.subheader("📋 Plano Contratual")
    plano_selecionado = st.sidebar.selectbox(
        "Selecione o plano:",
        options=list(PLANOS.keys()),
        help="Escolha conforme o contrato do cliente"
    )

    # Mostrar descrição do plano selecionado
    plano_desc = PLANOS[plano_selecionado]["descricao"]
    st.sidebar.info(f"**{plano_selecionado}:** {plano_desc}")

    # FILTRO DE PERÍODO
    st.sidebar.subheader("📅 Período")
    periodo_opcoes = {
        "7 dias": 7,
        "15 dias": 15,
        "3 meses": 90,
        "Este ano": 365
    }

    periodo_selecionado = st.sidebar.selectbox(
        "Selecione o período:",
        options=list(periodo_opcoes.keys())
    )

    hoje = datetime.now().date()
    dias = periodo_opcoes[periodo_selecionado]

    if periodo_selecionado == "Este ano":
        date_range = (hoje.replace(month=1, day=1), hoje)
    else:
        date_range = (hoje - timedelta(days=dias), hoje)

    filtros['data_inicio'] = date_range[0]
    filtros['data_fim'] = date_range[1]
    filtros['periodo'] = periodo_selecionado
    filtros['plano'] = plano_selecionado

    return filtros


def aplicar_filtros_dataframe(df, filtros):
    """Aplica filtros ao DataFrame"""
    df_filtrado = df.copy()

    # Filtro de período
    if 'data_inicio' in filtros and 'data_fim' in filtros:
        df_filtrado = df_filtrado[
            (df_filtrado['Data'].dt.date >= filtros['data_inicio']) &
            (df_filtrado['Data'].dt.date <= filtros['data_fim'])
        ]

    return df_filtrado

# ============================================================================
# INTERFACE PRINCIPAL - CORRIGIDA
# ============================================================================


def mostrar_tela_inicial():
    """Tela inicial simplificada"""
    st.markdown("""
    <div style='background-color: #f0f2f6; padding: 30px; border-radius: 10px; text-align: center;'>
        <h1 style='color: #1f77b4; margin-bottom: 20px;'>💰 Dashboard Financeiro</h1>
        <p style='font-size: 18px; color: black;'>Sistema de relatórios por plano contratual</p>
    </div>
    """, unsafe_allow_html=True)

    st.info("👆 **Use o menu lateral para configurar o plano e fazer upload do arquivo**")


def mostrar_dashboard_por_plano(df_filtrado, kpis, filtros):
    """Mostra dashboard conforme o plano selecionado - CORRIGIDA"""
    plano_selecionado = filtros['plano']
    plano_config = PLANOS[plano_selecionado]

    st.header(f"📊 Dashboard - Plano {plano_selecionado}")
    st.write(f"**{plano_config['descricao']}**")

    # KPIs PRINCIPAIS
    st.subheader("📈 Indicadores do Plano")

    # Organizar KPIs em colunas
    kpis_para_mostrar = [kpi for kpi in plano_config["kpis"] if kpi in kpis]

    # Criar colunas dinamicamente
    num_cols = min(4, len(kpis_para_mostrar))
    cols = st.columns(num_cols)

    for i, kpi in enumerate(kpis_para_mostrar):
        col = cols[i % num_cols]
        with col:
            if kpi in ['receita_total', 'despesa_total', 'lucro_liquido', 'contas_receber', 'contas_pagar', 'total_pago_recebido']:
                valor = f"R$ {kpis[kpi]:,.2f}"
            elif kpi in ['margem_lucro', 'roi', 'crescimento_receita']:
                valor = f"{kpis[kpi]:.1f}%"
            elif kpi == 'liquidez_corrente':
                valor = f"{kpis[kpi]:.2f}"
            elif kpi in ['prazo_medio_recebimento', 'ciclo_caixa']:
                valor = f"{kpis[kpi]:.0f} dias"
            else:
                valor = f"{kpis[kpi]:,}"

            nome_kpi = kpi.replace('_', ' ').title()
            st.metric(nome_kpi, valor)

    st.markdown("---")

    # GRÁFICOS CONFORME O PLANO - CORRIGIDA
    st.subheader("📊 Gráficos do Plano")

    # Dicionário de funções de gráfico
    funcoes_graficos = {
        "fluxo_caixa": criar_grafico_fluxo_caixa,
        "evolucao_mensal": criar_grafico_evolucao_mensal,
        "top_clientes": criar_grafico_top_10_clientes,
        "top_fornecedores": criar_grafico_top_10_fornecedores,
        "subcategorias_receita": criar_grafico_subcategorias_receita,
        "subcategorias_despesa": criar_grafico_subcategorias_despesa,
        "top_clientes_inadimplentes": criar_grafico_top_clientes_inadimplentes,
        "top_fornecedores_pagos": criar_grafico_top_fornecedores_pagos
    }

    # Criar gráficos com containers únicos
    graficos_exibidos = 0

    for i, grafico in enumerate(plano_config["graficos"]):
        if grafico in funcoes_graficos:
            # Criar um container único para cada gráfico
            with st.container():
                fig = funcoes_graficos[grafico](df_filtrado)
                if fig:
                    # Usar uma chave única para cada gráfico
                    st.plotly_chart(fig, use_container_width=True,
                                    key=f"grafico_{i}_{grafico}")
                    graficos_exibidos += 1
                else:
                    st.info(
                        f"📊 Dados insuficientes para {grafico.replace('_', ' ').title()}")

    if graficos_exibidos == 0:
        st.info("📊 Nenhum gráfico pode ser gerado com os dados disponíveis.")

    # BOTÃO DE RELATÓRIO
    st.markdown("---")
    st.subheader("📋 Relatório")

    if st.button("📄 Gerar Relatório PDF", key="btn_relatorio"):
        with st.spinner("Gerando relatório..."):
            relatorio_path = gerar_relatorio_por_plano(
                kpis, df_filtrado, filtros, plano_selecionado)

            if relatorio_path:
                with open(relatorio_path, "rb") as f:
                    relatorio_bytes = f.read()

                st.download_button(
                    label="📥 Download do Relatório",
                    data=relatorio_bytes,
                    file_name=f"relatorio_financeiro_{plano_selecionado.lower()}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    key="btn_download"
                )

                # Limpar arquivo temporário
                os.unlink(relatorio_path)
            else:
                st.error("❌ Erro ao gerar relatório")

# ============================================================================
# APLICAÇÃO PRINCIPAL
# ============================================================================


def main():
    # Tela inicial
    mostrar_tela_inicial()

    # Sidebar com filtros
    filtros = criar_filtros_sidebar()

    # Upload de arquivo
    st.sidebar.subheader("📁 Upload de Dados")
    uploaded_file = st.sidebar.file_uploader(
        "Faça upload do arquivo CSV",
        type=['csv'],
        help="Arquivo deve conter colunas: Data, Valor, Tipo",
        key="file_uploader"
    )

    if uploaded_file is not None:
        # Processar dados
        df = processar_dados(uploaded_file)

        if df is not None:
            # Aplicar filtros
            df_filtrado = aplicar_filtros_dataframe(df, filtros)

            if len(df_filtrado) == 0:
                st.warning(
                    "⚠️ Nenhum dado encontrado para os filtros aplicados")
                return

            # Calcular KPIs
            kpis = calcular_kpis_avancados(df_filtrado)

            # Mostrar dashboard conforme plano
            mostrar_dashboard_por_plano(df_filtrado, kpis, filtros)

            # Mostrar dados brutos (opcional)
            with st.expander("📋 Visualizar Dados Brutos (Filtrados)"):
                st.dataframe(df_filtrado)

    else:
        st.info("👆 Faça upload de um arquivo CSV para começar")

        # Exemplo de estrutura
        with st.expander("📋 Exemplo de Estrutura do Arquivo CSV"):
            st.markdown("""
            **Colunas obrigatórias:**
            - `Data`: Data da transação (qualquer formato)
            - `Valor`: Valor numérico da transação

            **Colunas opcionais:**
            - `Tipo`: "Receita" ou "Despesa"
            - `Categoria`: Categoria da transação
            - `Subcategoria`: Subcategoria da transação
            - `Cliente`: Nome do cliente/fornecedor
            - `Pago`: Valor já pago/recebido
            - `A Vencer`: Valor a pagar/receber

            **Exemplo:**
            ```csv
            Data,Valor,Tipo,Categoria,Subcategoria,Cliente,Pago,A Vencer
            15/01/2024,1500.00,Receita,Vendas,Produto A,Cliente X,1500.00,0
            20/01/2024,300.00,Despesa,Fornecedor,Matéria-prima,Fornecedor Y,300.00,0
            ```
            """)


if __name__ == "__main__":
    main()
