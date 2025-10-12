@echo off
chcp 65001 >nul
title Dashboard Financeiro - VERSÃO SIMPLIFICADA
color 0A

echo.
echo ========================================
echo    DASHBOARD FINANCEIRO - v2.0
echo ========================================
echo.
echo Iniciando o sistema...

:: Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRO: Python não encontrado!
    echo.
    echo Por favor, instale o Python em:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✅ Python encontrado!
echo.
echo 📦 Instalando/verificando dependências...

:: Instalar dependências
pip install streamlit pandas numpy plotly reportlab openpyxl --quiet

echo.
echo ✅ Tudo pronto!
echo 🌐 Abrindo no navegador...
echo.
echo ⏳ Aguarde alguns segundos...
echo.
echo 💡 INSTRUÇÕES RÁPIDAS:
echo    1. Faça upload de um arquivo CSV
echo    2. Use os filtros na barra lateral  
echo    3. Visualize gráficos e indicadores
echo    4. Gere relatórios em PDF
echo.

:: Executar o dashboard
streamlit run dasboard.py

pause