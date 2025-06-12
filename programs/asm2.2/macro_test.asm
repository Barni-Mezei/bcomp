;asm 2.2

#loadStr "Macro test:\n" 0
#printStr 0 20 20

#forLoop 0 5 :log 0
#reverseForLoop 0 5 :log 0
hlt

:log
out RA, 1
rtn