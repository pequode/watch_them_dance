from hr_game.llm.utils import get_llm
def main():
    print("Hello from hr-game!",get_llm().invoke("Hello tell me a joke"))


if __name__ == "__main__":
    main()
