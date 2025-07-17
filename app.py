import os
from dotenv import load_dotenv

load_dotenv()

def main():
    foo = os.getenv("FOO")
    print(f"The value of FOO is: {foo}")

if __name__ == "__main__":
    main()