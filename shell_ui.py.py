from data_model import Terminal

def main():
    terminal = Terminal()

    # Command registrieren

    print("<sys> Terminal gestartet. Tippe 'exit' zum Beenden.\n")

    while True:
        user_input = input(f"{terminal.path} <sys>> ")

        if user_input == "exit":
            break

        result = terminal.run_command(user_input)

        if result:
            print(result)

if __name__ == "__main__":
    main()