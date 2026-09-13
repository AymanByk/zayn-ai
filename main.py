from assistant import Assistant


def main():
    assistant = Assistant()

    assistant.greet()

    while assistant.chat():
        pass


if __name__ == "__main__":
    main()