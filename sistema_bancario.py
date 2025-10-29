import textwrap

# MENU PRINCIPAL 
def exibir_menu():
    menu = """\n
    |--------MENU--------|
    [1]\tDepositar
    [2]\tSacar
    [3]\tExtrato
    [4]\tCadastrar cliente 
    [5]\tCadastrar conta 
    [6]\tListar contas
    [0]\tSair  
    => """
    return input(textwrap.dedent(menu))

# DEPÓSITO
def deposito(saldo_atual, valor, historico, /):
    if valor > 0:
        saldo_atual += valor
        historico += f"Depósito: \tR$ {valor:.2f}\n"
        print("\nDepósito efetuado com sucesso!")
    else:
        print("\n[ERRO] Valor inválido, tente novamente.")
    return saldo_atual, historico

# SAQUE
def realizar_saque(*, saldo, valor, historico, limite, qtd_saques, limite_saques):
    sem_saldo = valor > saldo
    acima_do_limite = valor > limite
    limite_excedido = qtd_saques >= limite_saques

    if sem_saldo:
        print("\n[ERRO] Saldo insuficiente.")
    elif acima_do_limite:
        print("\n[ERRO] o Valor do saque é acima do limite permitido.")
    elif limite_excedido:
        print("\n[ERRO] Número máximo de saques atingido")
    elif valor > 0:
        saldo -= valor
        historico += f"Saque: \t\tR$ {valor:.2f}\n"
        qtd_saques += 1 
        print("\n Saque realizado com sucesso!")
    else:
        print("\n[ERRO] Valor inválido. Digite novamente.")

    return saldo, historico, qtd_saques

# EXTRATO 
def mostrar_saldo(saldo, /, *, historico):
    print("\n EXTRATO ")
    print("Sem movimentações registradas." if not historico else historico)
    print(f"\nSaldo atual: \tR$ {saldo:.2f}")

# CRIAR USUÁRIO 
def cadastrar_usuario(lista_usuarios):
    cpf = input("Informe o CPF (somente números): ")
    usuario = buscar_usuario(cpf, lista_usuarios)

    if usuario:
        print("\n[ERRO] Já existe um usuário com esse CPF.")
        return

    nome = input("Nome completo: ")
    data_nascimento = input("Data de nascimento (dd-mm-aaaa): ")
    endereco = input("Endereço (rua, nº - bairro - cidade/UF): ")

    lista_usuarios.append({
        "nome": nome,
        "data_nascimento": data_nascimento,
        "cpf": cpf,
        "endereco": endereco
    })       

    print("\n Usuário cadastrado com sucesso!")


# BUSCAR USUARIO
def buscar_usuario(cpf, lista_usuario):
    usuarios = [user for user in lista_usuario if user["cpf"] == cpf]
    return usuarios[0] if usuarios else None

# CRIAR CONTA 
def criar_nova_conta(agencia, numero_conta, usuarios):
    cpf = input("CPF do titular: ")
    usuario = buscar_usuario(cpf, usuarios)

    if usuario:
        print("\n Conta criada com sucesso!")
        return {"agencia": agencia, "numero_conta": numero_conta, "titular": usuario}
    
    print("\n[ERRO] Usuário não encontrado. Criação de conta cancelada")

# LISTAR CONTAS 
def exibir_contas(contas):
    for conta in contas:
        dados = f"""
            Agência: \t{conta['agencia']}
            Conta:\t\t{conta['numero_conta']}
            Titular:\t{conta['titular']['nome']}
        """
        print("\n" + textwrap.dedent(dados))

# FUNÇÂO PRINCIPAL 
def sistema_bancario():
    LIMITE_SAQUES = 3
    AGENCIA_PADRAO = "0001"

    saldo = 0
    limite_saque = 500
    extrato = ""
    numero_saques = 0
    usuarios = []
    contas = []
    qtd_saques = numero_saques

    while True:
        menu = exibir_menu()

        if menu == "1":
            valor = float(input("Valor do depósito: R$ "))
            saldo, extrato = deposito(saldo, valor, extrato)

        elif menu == "2":
            valor = float(input("Valor do saque: R$ "))
            saldo, extrato = realizar_saque(
                saldo=saldo,
                valor=valor,
                historico=extrato,
                limite=limite_saque,
                qtd_saques=numero_saques,
                limite_saques=LIMITE_SAQUES
            ) 

        elif menu == "3":
            mostrar_saldo(saldo, historico=extrato)

        elif menu == "4":
            cadastrar_usuario(usuarios)

        elif menu == "5":
            numero_conta = len(contas) + 1
            nova_conta = criar_nova_conta(AGENCIA_PADRAO, numero_conta, usuarios)
            if nova_conta:
                contas.append(nova_conta)
        
        elif menu == "6":
            exibir_contas(contas)

        elif menu == "0":
            print("\nEncerrando o sistema... Até logo!")
            break
        else:
            print("\n[ERRO] Opção inválida. Tente novamente.")

# EXECUÇÂO 
sistema_bancario()

        