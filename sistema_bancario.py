import textwrap
from datetime import datetime
from abc import ABC, abstractmethod


# Iterador de contas
class ContasIterador:
    def __init__(self, contas):
        self.contas = contas
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        try:
            conta = self.contas[self._index]
            return f"""
            Agência:\t{conta.agencia}
            Número:\t\t{conta.numero}
            Titular:\t{conta.cliente.nome}
            Saldo:\t\tR$ {conta.saldo:.2f}
            """
        except IndexError:
            raise StopIteration
        finally:
            self._index += 1


# Classes de Cliente e Pessoa Física 
class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


# Classe Conta e ContaCorrente 
class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("\n[ERRO] Saldo insuficiente.")
        elif valor > 0:
            self._saldo -= valor
            print("\nSaque realizado com sucesso!")
            return True
        else:
            print("\n[ERRO] Valor inválido.")
        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\nDepósito realizado com sucesso!")
            return True
        else:
            print("\n[ERRO] Valor inválido.")
            return False


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self._limite = limite
        self._limite_saques = limite_saques

    def sacar(self, valor):
        numero_saques = len(
            [t for t in self.historico.transacoes if t["tipo"] == Saque.__name__]
        )
        excedeu_limite = valor > self._limite
        excedeu_saques = numero_saques >= self._limite_saques

        if excedeu_limite:
            print("\n[ERRO] O valor excede o limite.")
        elif excedeu_saques:
            print("\n[ERRO] Número máximo de saques atingido.")
        else:
            return super().sacar(valor)
        return False

    def __str__(self):
        return f"""
            Agência:\t{self.agencia}
            Conta:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """


# Histórico de transações
class Historico:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
            "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        })

    def gerar_relatorio(self, tipo=None):
        for transacao in self._transacoes:
            if tipo is None or transacao["tipo"].lower() == tipo.lower():
                yield transacao


# Classe abstrata de Transação e subclasses
class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso = conta.sacar(self.valor)
        if sucesso:
            conta.historico.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso = conta.depositar(self.valor)
        if sucesso:
            conta.historico.adicionar_transacao(self)


# Decorador de log
def log_transacao(func):
    def wrapper(*args, **kwargs):
        resultado = func(*args, **kwargs)
        print(f"[LOG] {datetime.now()}: {func.__name__.upper()}")
        return resultado
    return wrapper


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
        print("\nSaque realizado com sucesso!")
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

    print("\nUsuário cadastrado com sucesso!")


# BUSCAR USUARIO
def buscar_usuario(cpf, lista_usuario):
    usuarios = [user for user in lista_usuario if user["cpf"] == cpf]
    return usuarios[0] if usuarios else None


# CRIAR CONTA 
def criar_nova_conta(agencia, numero_conta, usuarios):
    cpf = input("CPF do titular: ")
    usuario = buscar_usuario(cpf, usuarios)

    if usuario:
        print("\nConta criada com sucesso!")
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


# FUNÇÃO PRINCIPAL 
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


# EXECUÇÃO 
sistema_bancario()
