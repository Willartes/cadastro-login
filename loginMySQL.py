import getpass
import mysql.connector

# Dicionário para armazenar o nome de usuário e senha cadastrados
usuarios = {}

def verificar_forca_senha(senha):
    comprimento_minimo = 8
    tem_letra_maiuscula = False
    tem_letra_minuscula = False
    tem_numero = False
    tem_caractere_especial = False

    
    # Verificando se a senha está vazia
    if not senha:
        return "Digite uma senha!"

    # Verificando o comprimento da senha
    if len(senha) < comprimento_minimo:
        return f"Sua senha é muito curta. Recomenda-se no mínimo {comprimento_minimo} caracteres."

    # Verificando se a senha contém letras maiúsculas e minúsculas
    for caractere in senha:
        if caractere.isupper():
            tem_letra_maiuscula = True
        if caractere.islower():
            tem_letra_minuscula = True

    if not tem_letra_maiuscula or not tem_letra_minuscula:
        return "Sua senha deve conter pelo menos uma letra maiúscula e uma letra minúscula."

    # Verificando se a senha contém pelo menos um número
    if any(caractere.isdigit() for caractere in senha):
        tem_numero = True

    if not tem_numero:
        return "Sua senha deve conter pelo menos um número."

    # Verificando se a senha contém pelo menos um caractere especial
    caracteres_especiais = "!@#$%^&*()-_=+[{]}|;:',<.>/?"
    if any(caractere in caracteres_especiais for caractere in senha):
        tem_caractere_especial = True

    if not tem_caractere_especial:
        return "Sua senha deve conter pelo menos um caractere especial."

    # Se a senha atender a todos os critérios, é considerada forte
    return "Sua senha é forte!"

# Função para conectar ao banco de dados MySQL
def conectar_mysql():
    return mysql.connector.connect(
        host="",
        user="root",
        password="root",
        database="cadastro_usuario"
    )

# Função para criar a tabela de usuários no banco de dados
def criar_tabela_usuarios():
    conn = conectar_mysql()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios
                      (id INT AUTO_INCREMENT PRIMARY KEY, nome VARCHAR(255), senha VARCHAR(255))''')
    conn.commit()
    conn.close()

# Função para cadastrar um novo usuário no banco de dados
def cadastrar_usuario(nome_usuario, senha):
    conn = conectar_mysql()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (nome, senha) VALUES (%s, %s)", (nome_usuario, senha))
    conn.commit()
    conn.close()

# Função para cancelar a conta de um usuário e excluir do banco de dados
def cancelar_conta(nome_usuario):
    conn = conectar_mysql()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE nome = %s", (nome_usuario,))
    conn.commit()
    conn.close()
    print("Conta cancelada com sucesso!")

# Função para verificar se um usuário já existe no banco de dados
def verificar_usuario_existente(nome_usuario):
    conn = conectar_mysql()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM usuarios WHERE nome = %s", (nome_usuario,))
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

# Função para fazer login de um usuário
def login():
    nome_usuario = input("Digite seu nome de usuário: ")
    senha = getpass.getpass("Digite sua senha: ")

    conn = conectar_mysql()
    cursor = conn.cursor()
    cursor.execute("SELECT senha FROM usuarios WHERE nome = %s", (nome_usuario,))
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        senha_armazenada = resultado[0]
        if senha == senha_armazenada:
            print("Login bem-sucedido. Bem-vindo,", nome_usuario)
        else:
            print("Senha incorreta. Tente novamente.")
    else:
        print("Nome de usuário não encontrado.")

# Função para verificar se o formato do e-mail é válido
def verifica_email(nome_usuario):
    if '@' in nome_usuario:
        dominio = nome_usuario.split('@')[1]
        if '.com' in dominio or '.br' in dominio:
            return True
    return False

# Função para cadastrar um usuário com verificações
def cadastrar_usuario_com_verificacoes():
    nome_usuario = input("Digite seu nome de usuário: ")

    if not verifica_email(nome_usuario):
        print("Digite um email válido!")
        return cadastrar_usuario_com_verificacoes()

    if verificar_usuario_existente(nome_usuario):
        print("Nome de usuário já existe. Tente novamente com um nome diferente.")
        return cadastrar_usuario_com_verificacoes()

    while True:
        senha = getpass.getpass("Digite sua senha para cadastro ou 'exit' para sair: ")

        if senha.lower() == "exit":
            print("\nAté breve!")
            return

        resultado_senha = verificar_forca_senha(senha)

        if resultado_senha == "Sua senha é forte!":
            cadastrar_usuario(nome_usuario, senha)
            print("Usuário cadastrado com sucesso!")
            break
        else:
            print(resultado_senha)

# Função principal
if __name__ == "__main__":
    try:
        criar_tabela_usuarios()
        opcao = input("Digite 'cadastro' para cadastrar um novo usuário, 'login' para fazer login ou 'cancelar' para cancelar uma conta: ")

        if opcao == "cadastro":
            cadastrar_usuario_com_verificacoes()
        elif opcao == "login":
            login()
        elif opcao == "cancelar":
            nome_usuario = input("Digite o nome de usuário da conta a ser cancelada: ")
            if verificar_usuario_existente(nome_usuario):
                senha = getpass.getpass("Digite sua senha para confirmar o cancelamento da conta: ")
                conn = conectar_mysql()
                cursor = conn.cursor()
                cursor.execute("SELECT senha FROM usuarios WHERE nome = %s", (nome_usuario,))
                resultado = cursor.fetchone()
                conn.close()
                if resultado:
                    senha_armazenada = resultado[0]
                    if senha == senha_armazenada:
                        cancelar_conta(nome_usuario)
                    else:
                        print("Senha incorreta. O cancelamento da conta não foi efetuado.")
                else:
                    print("Nome de usuário não encontrado.")
            else:
                print("Nome de usuário não encontrado.")
        else:
            print("Opção inválida. Tente novamente.")
    except Exception as e:
        print("Ocorreu um erro:", e)