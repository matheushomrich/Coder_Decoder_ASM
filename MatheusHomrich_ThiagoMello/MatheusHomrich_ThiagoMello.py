# ASM Montator 2020
# Matheus Schreiner Homrich da Silva e Thiago Gomes Vidal de Mello

import os, shutil, sys

print("Bem vindo ao ASMMontator\nSE DIVIRTA")

flag = True
while flag == True:
    try: 
        print("Coloque aqui o nome do arquivo que voce deseja MONTAR(com .txt no final): ")
        montar = input()
        fileReadM = open(montar, "r") #COLOQUE O NOME DO SEU ARQUIVO PARA MONTAGEM AQUI
        flag = False
    except FileNotFoundError:
        print("Arquivo nao encontrado, tente novamente ")

flag2 = True 
while flag2 == True:
    try:
        print("Coloque aqui o nome do arquivo que voce deseja DESMONTAR(com .txt no final):")
        desmontar = input()
        fileReadD = open(desmontar, "r")  #COLOQUE O NOME DO SEU ARQUIVO PARA DESMOTAGEM AQUI
        flag2 = False
    except FileNotFoundError:
        print("Arquivo nao encontrado, tente novamente ")


fileCreateM = open("HexaToASM.asm","w+") #arquivo MONTADO
fileLinesM = fileReadM.readlines()

fileCreateD = open("ASMToHexa.asm","w+") #arquivo DESMONTADO
fileLinesD = fileReadD.readlines()
fileAuxLabelD = fileLinesD

def desmontagem(): #funcao principal para a desmontagem do codigo em texto 
    contLinhas = 2
    labels = []
    contLabels = 0
    for y in fileLinesD[2:]:  #for para iterar por cima das linhas do arquivo
        if ':' in y:
            split = y.split(':')
            
            labels.append((split[0], contLinhas))
            contLabels = contLabels + 1
        else:
            splitespaco = y.split(' ') #splits para pegarmos exatamente as partes necessarias da intrucao
            splitvirgula = y.split(',')
            splitparenteses = y.split('(')
            nomeinstrucao = splitespaco[0] 
            primeiro = splitvirgula[0].split(' ')[1].replace('$', '')
            segundo = ''
            terceiro = ''
            parenteses = ''
            if len(splitvirgula) >= 2:
                segundo = splitvirgula[1].replace('$', '')
            if len(splitvirgula) == 3:
                if '$' not in splitvirgula[2]:
                    terceiro = splitvirgula[2].replace(' ', '').replace('\n','')
                else:
                    terceiro = splitvirgula[2].replace('$', '')
            if len(splitparenteses) == 2:
                parenteses = splitparenteses[1].replace('$', '').replace(')', '')
        
            if nomeinstrucao == "syscall": #caso a instrucao seja syscall
                fileCreateD.write("0000000c\n")

            if nomeinstrucao == 'addu': #instrucoes do tipoR sendo conferidas e enviadas para a funcao tipoR com seu funct as difrenciando 
                tipoR(primeiro, segundo, terceiro, 33)
            if nomeinstrucao == 'xor':
                tipoR(primeiro, segundo, terceiro, 38)
            if nomeinstrucao == 'slt':
                tipoR(primeiro, segundo, terceiro, 42)
            if nomeinstrucao == 'and':
                tipoR(primeiro, segundo, terceiro, 36)
            if nomeinstrucao == 'sll':
                tipoR(primeiro, segundo, terceiro, 0)
            if nomeinstrucao == 'srl':
                tipoR(primeiro, segundo, terceiro, 2)

            if nomeinstrucao == 'addiu': #instrucoes do tipoI sendo conferidas e enviadas para a funcao do tipoI com seu opcode as diferenciando
                tipoI(9, primeiro, segundo, terceiro)
            if nomeinstrucao == 'lui':
                tipoI(15, primeiro, segundo, terceiro)
            if nomeinstrucao == 'lw':
                tipoI(35, primeiro, segundo, parenteses)
            if nomeinstrucao == 'sw':
                tipoI(43, primeiro, segundo, parenteses)
            if nomeinstrucao == 'beq':
                for l in labels:
                    if terceiro == l[0]:
                        deslocamento = l[1] - contLinhas - 1
                        terceiro = str(deslocamento)
                if 'label' in terceiro:
                    terceiro = labelAbaixo(contLinhas, terceiro) - contLinhas - 1
                tipoI(4, primeiro, segundo, terceiro)   
            if nomeinstrucao == 'bne':
                for l in labels:
                    if terceiro == l[0]:
                        deslocamento = l[1] - contLinhas - 1
                        terceiro = str(deslocamento)
                if 'label' in terceiro:
                    terceiro = labelAbaixo(contLinhas, terceiro) - contLinhas - 1
                tipoI(5, primeiro, segundo, terceiro)
            if nomeinstrucao == 'ori':
                tipoI(13, primeiro, segundo, terceiro)
            if nomeinstrucao == 'andi':
                tipoI(12, primeiro, segundo, terceiro)
        
            if nomeinstrucao == 'j': #caso especial dos jumps sendo enviado para a funcao jump com seus respectivos opcode
                for l in labels:
                    if primeiro == l[0]:
                        deslocamento = (1 - l[1]) * 4
                        primeiro = str(deslocamento)
                tipoJ(2, primeiro)
            if nomeinstrucao == 'jr':
                tipoJ(0, primeiro)
            contLinhas = contLinhas + 1

def tipoJ(opcode, primeiro): #tratamento da desmontagem dos jumps 
    label = 0
    if opcode == 2:
        opcode = bin(int(opcode))[2:].zfill(6)
        pc = "0x00400000"
        pc = int(pc,16) + int(primeiro)
        pc = str(hex(pc))[2:].zfill(8)
        label = bin(int(pc, 16))[2:].zfill(32)
        label = label[4:30]
        binario = str(opcode) + str(label)
    if opcode == 0:
        opcode = bin(int(opcode))[2:].zfill(6)
        rs = bin(int(primeiro))[2:].zfill(5)
        label = bin(int(label))[2:].zfill(16)
        funct = bin(int(8))[2:].zfill(5)
        binario = str(opcode) + str(rs) + str(label) + str(funct)

    hexa = hex(int(binario, 2))[2:].zfill(8)
    fileCreateD.write(str(hexa)+"\n")

def labelAbaixo(linha, label):
    counter = linha
    for lin in fileAuxLabelD[linha:]:
        if ':' in lin:
            split = lin.split(':')
            if split[0] == label:
                return counter

        counter = counter + 1


def tipoR(primeiro, segundo, terceiro, funct):  #tratamendo da demsontagem das intrucoes de tipoR
    rs = 0
    rt = 0
    shamt = 0
    binario = "000000" 
    rd = bin(int(primeiro))[2:].zfill(5)                
    
    #verifica o funct para saber a ordem dos argumentos em linguagem asm

    if funct == 0 or funct == 2: #tratamento dos shifts sll / srl
        rs = bin(rs)[2:].zfill(5)
        rt = bin(int(segundo))[2:].zfill(5)
        shamt = bin(int(terceiro))[2:].zfill(5) 
    else:
        shamt = bin(shamt)[2:].zfill(5)
        rs = bin(int(segundo))[2:].zfill(5)
        rt = bin(int(terceiro))[2:].zfill(5)

    funct = bin(int(funct))[2:].zfill(6)

    binario = binario + str(rs) + str(rt) + str(rd) + str(shamt) + str(funct)
    hexa = hex(int(binario, 2))[2:].zfill(8)
    fileCreateD.write(str(hexa)+"\n")

def tipoI(opcode, primeiro, segundo, terceiro): #tratamento da desmontagem das intrucoes do tipoI
    rt = 0
    rs = 0
    imm = 0                         #verifica o opcode para saber a ordem dos argumentos em linguagem asm
    if opcode == 35 or opcode==43:
        rt = bin(int(primeiro))[2:].zfill(5)
        imm = bin(int(segundo[2:10], 16))[2:].zfill(16)
        rs = bin(int(terceiro))[2:].zfill(5)
        
    if opcode == 15:
        rs = bin(rs)[2:].zfill(5)
        rt = bin(int(primeiro))[2:].zfill(5)
        imm = bin(int(segundo[2:], 16))[2:].zfill(16)

    if opcode == 4 or opcode == 5:          #branches
        rs = bin(int(primeiro))[2:].zfill(5)
        rt = bin(int(segundo))[2:].zfill(5)
        imm = bin(int(terceiro) & 0b1111111111111111)[2:]

    if opcode == 9 or opcode == 13 or opcode == 12:
        rt = bin(int(primeiro))[2:].zfill(5)
        rs = bin(int(segundo))[2:].zfill(5)
        imm = bin(int(terceiro[2:10], 16))[2:].zfill(16)

    opcode = bin(int(opcode))[2:].zfill(6)
    binario = str(opcode) + str(rs) + str(rt) + str(imm)
    hexa = hex(int(binario, 2))[2:].zfill(8)
    fileCreateD.write(str(hexa)+"\n")

# ---------------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------------------------------


labelss = [] #lista de tuplas para adicionar os labels na montagem

def montagem(): #funcao principal para a montagem 
    contLinhas = 1
    fileCreateM.write(".text\n.globl label_0\n")
    contlabel = 0
    for x in fileLinesM: #iteracao em cima das linhas do arquivo a ser montado
        dec = int(x, 16)
        binario = bin(dec)[2:].zfill(32)
        opcode = binario[:6]
        opcodedec = int(opcode, 2)
        syscall = int(binario, 2)
        if opcodedec == 0:
            typeR(binario)
        if syscall == 12:
            fileCreateM.write("syscall\n") 
        typeI(binario, contLinhas, contlabel)
        contLinhas = contLinhas + 1

def typeR(binario): #funcao de tratamento da montagem do arquivo das intrucoes do tipoR
    if(int(binario[12:],2) == 8 ): #verificando se é instrução jr
        jr(binario)
    else:       #separa a string binario em partes e depois verifica funct para descobrir a instrução
        rs = binario[6:11]
        rstext = "$"+str(int(rs, 2))
        rt = binario[11:16]
        rttext = "$"+str(int(rt, 2))
        rd = binario[16:21]
        rdtext = "$"+str(int(rd, 2))
        registers = rdtext+", "+rstext+", "+rttext
        shamt = binario[21:26]
        funct = binario[26:]
        if(int(funct,2) == 0): #shift
            registers = rdtext+", "+rttext+", "+str(int(shamt, 2))
            fileCreateM.write("sll"+" "+registers+"\n")
        if(int(funct,2) == 2): #shift
            registers = rdtext+", "+rttext+", "+str(int(shamt, 2))
            fileCreateM.write("srl"+" "+registers+"\n")
        if(int(funct,2) == 33):
            fileCreateM.write("addu"+" "+registers+"\n")
        if(int(funct,2) == 36):
            fileCreateM.write("and"+" "+registers+"\n")
        if(int(funct,2) == 38):
            fileCreateM.write("xor"+" "+registers+"\n")
        if(int(funct,2) == 42):
            fileCreateM.write("slt"+" "+registers+"\n")
        
def typeI(binario, contLinhas, contlabel): #funcao de tratamento da montagem dos arquivos de tipoI
    if(int(binario[:6], 2) == 2): #verificando se é intrução j
        jump(binario, contlabel)
    else:       #separa a string binario em partes e depois verifica opcode para descobrir a instrução
        opcode=binario[:6]
        rs = binario[6:11]
        rstext = "$"+str(int(rs, 2))
        rt = binario[11:16]
        rttext = "$"+str(int(rt, 2))
        imm = binario[16:]
        imediato = int(imm, 2)
        immediate = "0x"+str(hex(imediato)[2:].zfill(8))
        if(int(opcode, 2) == 4):
            if immediate[7] == 'f':
                imm = imm.replace('0', ' ').replace('1','0')
                imm = imm.replace(' ', '1') 
                imediato = int(imm, 2) + 1
                imediato = imediato * -1
            
            linha = contLinhas + imediato
            
            registers = rstext+", "+rttext + ", " + "label_" + str(linha)
            fileCreateM.write("beq"+" "+registers+"\n")
            labelss.append((linha, "label_" + str(linha)))

        if(int(opcode, 2) == 5):
            if immediate[7] == 'f':
                imm = imm.replace('0', ' ').replace('1','0')
                imm = imm.replace(' ', '1') 
                imediato = int(imm, 2) + 1
                imediato = imediato * -1
            
            linha = contLinhas + imediato
            
            registers = rstext+", "+rttext + ", " + "label_" + str(linha)
            fileCreateM.write("bne"+" "+registers+"\n")
            labelss.append((linha, "label_" + str(linha)))
        if(int(opcode, 2) == 9):
            registers = rttext+", "+rstext+", "+ immediate
            fileCreateM.write("addiu"+" "+registers+"\n")
        if(int(opcode, 2) == 12):
            registers = rttext+", "+rstext+", "+ immediate
            fileCreateM.write("andi"+" "+registers+"\n")
        if(int(opcode, 2) == 13):
            registers = rttext+", "+rstext+", "+ immediate
            fileCreateM.write("ori"+" "+registers+"\n")
        if(int(opcode, 2) == 15):
            registers = rttext+", "+ immediate
            fileCreateM.write("lui" + " " + registers + "\n")
        if(int(opcode, 2) == 35):
            registers = rttext+", " + immediate +"(" + rstext + ")"
            fileCreateM.write("lw" + " " + registers + "\n")
        if(int(opcode, 2) == 43):
            registers = rttext + ", "+ immediate + "(" + rstext+")"
            fileCreateM.write("sw" + " " + registers + "\n")
        
def jump(binario, contlabel): #funcao para a montagem do jump 'j'
    tar = "0000" + binario[6:] + "00"
    pc = "0x00400000"
    pc = int(tar, 2) - int(pc, 16)
    pc = int(pc / 4)
    for labs in labelss:
        if labs[0] == pc + 1:
            label = labs[1]
        else:
            label = pc
            
    label = "label_" + str(pc+1)
    fileCreateM.write("j"+" "+label+"\n")
    labelss.append((pc+1, "label_" + str(pc+1)))
    

def jr(binario): #funcao para a montagem do jump 'jr'
    rs = binario[6:11]
    rstext = "$"+str(int(rs, 2))
    fileCreateM.write("jr"+" "+rstext+"\n")


montagem() #chama a funcao montagem para executar
desmontagem() #chama a funcao desmontagem para executar

fileCreateD.close()
fileCreateM.close()
fileReadD.close()
fileReadM.close()
    
with open("HexaToASM.asm", 'r') as file:
    data = file.readlines()

for l in labelss:
    for linha in data[l[0]+2:]:
        if linha[:5] != "label":
            novaLinha = l[1] + ': ' + linha
            data[l[0]+2] = novaLinha
        break


with open("HexaToASM.asm", 'w') as file:
    file.writelines(data)
    

os.mkdir("OUTPUT")

shutil.move("HexaToASM.asm", "OUTPUT")
shutil.move("ASMToHexa.asm", "OUTPUT")