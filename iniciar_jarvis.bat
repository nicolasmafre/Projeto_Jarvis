@echo off
title Jarvis Launcher

rem --- Verificação e Ativação do Ambiente Conda ---
echo Ativando o ambiente Conda 'Projeto_Jarvis'...
rem O comando 'call' é essencial para que a ativação do ambiente afete este script.
call conda.bat activate Projeto_Jarvis

rem Verifica se a ativação foi bem-sucedida.
if not "%CONDA_DEFAULT_ENV%"=="Projeto_Jarvis" (
    echo.
    echo ERRO: Nao foi possivel ativar o ambiente Conda 'Projeto_Jarvis'.
    echo Verifique se o ambiente existe (usando 'conda env list') e se o Conda esta no PATH do sistema.
    echo.
    pause
    exit /b
)

:menu
cls
echo =================================
echo      INICIAR PROJETO JARVIS
echo =================================
echo.
echo Ambiente Conda '%CONDA_DEFAULT_ENV%' ativado.
echo.
echo Escolha uma opcao:
echo.
echo   [1] Iniciar Interface CLI (Terminal)
echo   [2] Iniciar Interface Web (Navegador)
echo.

rem O comando 'choice' aguarda o usuário pressionar 1 ou 2.
choice /c 12 /n /m "Digite 1 para CLI ou 2 para Web: "

rem O 'errorlevel' corresponde à posição da tecla na lista /c (1 para '1', 2 para '2').
if errorlevel 2 goto web
if errorlevel 1 goto cli

:cli
cls
echo Iniciando a interface CLI...
echo Pressione CTRL+C para sair.
echo.
python app.py
goto end

:web
cls

echo Abrindo o navegador...
rem O comando 'start' abre a URL no navegador padrão.
start http://localhost:5000

echo.
echo O servidor web foi iniciado em uma nova janela.
echo Aguardando 3 segundos para o servidor iniciar antes de abrir o navegador...
rem Pausa para dar tempo ao servidor Flask de iniciar.
timeout /t 3 /nobreak >nul

echo Iniciando a interface Web...
rem Inicia o servidor Flask em uma nova janela para não bloquear o script.
start "Jarvis Web Server" python app.py --web
goto end

:end
echo.
echo Script finalizado. Pressione qualquer tecla para fechar esta janela.
pause >nul