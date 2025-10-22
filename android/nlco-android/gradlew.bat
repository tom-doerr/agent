@echo off
REM ##########################################################
REM
REM Gradle startup script for Windows
REM
REM ##########################################################

set DIRNAME=%~dp0
if "%DIRNAME%" == "" set DIRNAME=.
set APP_HOME=%DIRNAME%

set DEFAULT_JVM_OPTS="-Xmx64m" "-Xms64m"

if defined JAVA_HOME goto findJavaFromJavaHome

set JAVA_EXE=java.exe
%JAVA_EXE% -version >NUL 2>&1
if "%ERRORLEVEL%" == "0" goto execute

echo.
echo ERROR: JAVA_HOME is not set and no 'java' command could be found in your PATH.
echo.
echo Please set the JAVA_HOME variable in your environment to match the
 - location of your Java installation.

goto fail

:findJavaFromJavaHome
set JAVA_HOME=%JAVA_HOME:"=%
set JAVA_EXE=%JAVA_HOME%\bin\java.exe

if exist "%JAVA_EXE%" goto execute

echo.
echo ERROR: JAVA_HOME is set to an invalid directory: %JAVA_HOME%
echo.
echo Please set the JAVA_HOME variable in your environment to match the
 - location of your Java installation.

goto fail

:execute
set CLASSPATH=%APP_HOME%\gradle\wrapper\gradle-wrapper.jar

set LAUNCHER=org.gradle.wrapper.GradleWrapperMain

set CMD_LINE_ARGS=
set _SKIP=2

:parseArgs
if "%~1"=="" goto argsDone
set ARG="%~1"
set CMD_LINE_ARGS=%CMD_LINE_ARGS% %ARG%
shift
goto parseArgs

:argsDone
"%JAVA_EXE%" %DEFAULT_JVM_OPTS% -classpath "%CLASSPATH%" %LAUNCHER% %CMD_LINE_ARGS%

:fail
exit /b 1
