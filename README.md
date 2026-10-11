# 📊 Relatório Financeiro

## 📌 O Problema de Negócio

Autônomos, micro e pequenas empresas frequentemente carecem de ferramentas acessíveis para analisar sua saúde financeira de forma profissional. Planilhas manuais não geram relatórios visuais, não calculam indicadores avançados (ROI, liquidez, margem) e não produzem documentos prontos para apresentação a investidores ou parceiros. Isso limita a capacidade de tomada de decisão e a credibilidade do negócio.

## 💡 A Solução

Desenvolvi um **sistema interativo em Streamlit** que permite o upload de dados financeiros (CSV), calcula automaticamente KPIs essenciais, gera gráficos interativos e produz **relatórios em PDF profissionais** com base em diferentes planos de acesso (Básico, Intermediário, Avançado). A ferramenta democratiza o acesso à análise financeira de qualidade para pequenos negócios.

## 🎯 Resultados e Impacto

- **Automatização completa** da geração de relatórios financeiros (de horas para minutos).
- **Cálculo automático de KPIs avançados:** Lucro, Margem, ROI, Liquidez, entre outros.
- **Visualizações interativas** que facilitam a identificação de tendências e anomalias.
- **Relatórios em PDF profissionais** prontos para apresentação a stakeholders.
- **Insights automáticos** sobre a saúde financeira da empresa, auxiliando na tomada de decisão.
- **Modelo de negócio escalável:** Diferentes planos de acesso (Básico, Intermediário, Avançado) permitem monetização do sistema.

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Finalidade |
| :--- | :--- |
| **Python 3.10+** | Linguagem base do projeto |
| **Streamlit** | Interface web interativa |
| **Pandas** | Processamento e análise de dados |
| **Plotly** | Visualizações gráficas interativas |
| **ReportLab** | Geração de relatórios em PDF |
| **Kaleido** | Exportação de gráficos para PDF |

## 📂 Estrutura do Projeto

relatorio_financeiro/
├── dashboard_financeiro.py # Aplicação principal (Streamlit)
├── executar_dashboard.bat # Executador automático para Windows
├── requirements.txt # Dependências do projeto
├── Instacao.txt # Instruções de instalação
└── README.md # Documentação


## 🚀 Como Executar

### Método 1: Executador Automático (Windows)
Basta dar um duplo clique no arquivo `executar_dashboard.bat`.

### Método 2: Execução Manual
```bash
# 1. Clone o repositório
git clone https://github.com/jeferson-data/relatorio_financeiro.git

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Execute o sistema
streamlit run dashboard_financeiro.py

Método 3: Ambiente Virtual (Recomendado)

# Criar ambiente
python -m venv venv

# Ativar (Windows)
venv\Scripts\activate

# Ativar (Mac/Linux)
source venv/bin/activate

# Instalar e executar
pip install -r requirements.txt
streamlit run dashboard_financeiro.py

📈 Funcionalidades Detalhadas
1. Upload e Processamento de Dados
Suporte para arquivos CSV com dados financeiros.

Conversão automática de datas em múltiplos formatos.

2. Análise e KPIs
Cálculo de indicadores essenciais: Lucro, Margem, ROI, Liquidez, etc.

Insights automáticos sobre a saúde financeira da empresa.

3. Visualização
Gráficos interativos com Plotly (receitas, despesas, evolução do saldo, etc.).

Filtros por período e plano contratado.

4. Geração de Relatórios
Exportação de relatórios em PDF com gráficos e indicadores.

Diferentes níveis de detalhe conforme o plano de acesso (Básico, Intermediário, Avançado).

🧰 Requisitos
Python 3.10 ou superior

Navegador Google Chrome (recomendado para exportação de gráficos)

Bibliotecas: Streamlit, Pandas, Plotly, ReportLab, Kaleido

🔧 Solução de Problemas
Erro	Causa	Solução
Erro ao carregar CSV	Formato incorreto	Verifique se o arquivo está no formato CSV
Gráficos não exportam para PDF	Kaleido não instalado	Instale o Kaleido: pip install kaleido
PDF não é gerado	ReportLab não instalado	Instale o ReportLab: pip install reportlab
Streamlit não abre	Porta em uso	Altere a porta: streamlit run app.py --server.port 8502
📬 Contato
Jeferson Gomes

LinkedIn: seu-linkedin

Email: jefe.gomes@outlook.com

GitHub: jeferson-data

⭐ Gostou do projeto? Deixe uma estrela no repositório e conecte-se comigo no LinkedIn!
