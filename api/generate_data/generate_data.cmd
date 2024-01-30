cls
@echo off

choice /c RPB /n /m "Enter data file to process. for [r]oster, press [r]. for [p]athways, press [p]. for [b]oth files, press [b]"


IF ERRORLEVEL 3 goto handle_both
IF ERRORLEVEL 2 goto handle_pathway
IF ERRORLEVEL 1 goto handle_roster



:handle_pathway
python process_pathways_and_generate_files.py -c -p

exit /b 0

:handle_roster
python process_roster_and_generate_files.py -c -p

exit /b 0


:handle_both
call :handle_roster
call :handle_pathway

exit /b 0

