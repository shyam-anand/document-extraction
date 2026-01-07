import pandas as pd

def main():
    print("Hello from docparsers!")
    df = pd.read_excel("local_data/test.xlsx")
    print(df.head())


if __name__ == "__main__":
    main()
