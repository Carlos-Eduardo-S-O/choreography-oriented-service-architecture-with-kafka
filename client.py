from utilits import send_message, get_url_to_security_verification
from time import sleep
from random import randint, choice
from colored import fg as foreground, attr as attribute

RED   = foreground("red")
GREEN = foreground("green")
RESET = attribute("reset")

ERROR_PERCENT = 50

# t for tokens, h for headers and c for cryptography errors. "" for not error
ERROR_TYPE    = ["c", "h", "t"]
ERROR = {
    "c": "Erro de criptografia, o sistema apontará um erro na 1ª verificação", 
    "h": "Erro no cabeçalho, o sistema apontará um erro na 2ª verificação", 
    "t": "Erro no token, o sistema apontará um erro na 3ª verificação"
}

def radom_send_request():
    response = None
    random_percent = randint(0, 100)
    
    if random_percent <= ERROR_PERCENT:
        error = choice(ERROR_TYPE)
        print(f"{RED}Messagem com erro, porcentagem sorteada: {random_percent} {RESET}")
        print(f"Tipo do erro: {ERROR.get(error)}")
        
        url = get_url_to_security_verification(error)
        print(f"Requisição:{RED} {url} {RESET}")
        
        response = send_message(url)
    else:
        print(f"{GREEN}Messagem sem erros...{RESET}")
        
        url = get_url_to_security_verification("")
        print(f"Requisição:{GREEN} {url} {RESET}")
        
        response = send_message(url)
    return response


# Empty str for not error, c for cryptography, h for header and t for token error 
def send_request(option):
    response = None
    
    if option == "":
        print(f"{GREEN}Messagem sem erros...{RESET}")
        
        url = get_url_to_security_verification("")
        print(f"Requisição:{GREEN} {url} {RESET}")
        
        response = send_message(url)
    else:
        print(f"{RED}Messagem com erro{RESET}")
        print(f"Tipo do erro: {ERROR.get(option)}")
        
        url = get_url_to_security_verification(option)
        print(f"Requisição:{RED} {url} {RESET}")
        
        response = send_message(url)
    return response

def run_random_test():
    try:
        while True:
            space = " "
            lines = 127
            print("-" * lines)
            print(f"{space * 55}Enviando mensagem")
            print("-" * lines)
            
            response = radom_send_request()
            
            print()
            print(f"Resposta do sistema: {response}")
            print("-" * lines, "\n")
            
            sleep(10)
    except KeyboardInterrupt:
        print("\nParando o sistema...")
        sleep(2)
        print("Obrigado por utilizar os nossos serviços!!!")

def run_objective_test():
    tests = ERROR_TYPE
    tests.append("")
    
    try:
        for test in tests:
            space = " "
            lines = 127
            print("-" * lines)
            print(f"{space * 55}Enviando mensagem")
            print("-" * lines)
            
            response = send_request(test)
            
            print()
            print(f"Resposta do sistema: {response}")
            print("-" * lines, "\n")
            
            sleep(10)
    except KeyboardInterrupt:
        print("\nParando o sistema...")
        sleep(2)
        print("Obrigado por utilizar os nossos serviços!!!")

if __name__ == "__main__":
    run_random_test()