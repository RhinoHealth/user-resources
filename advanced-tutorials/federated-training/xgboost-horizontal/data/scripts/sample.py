import pandas as pd

if __name__ == "__main__":
    df = pd.read_csv("../credit_risk_dataset.csv")

    centralized = df.sample(300, random_state=42)
    test = df.sample(100, random_state=20)
    A = centralized.iloc[:210, :]
    B = centralized.iloc[210:, :]

    centralized.to_csv("../centralized.csv", index=False)
    test.to_csv("../test.csv", index=False)
    A.to_csv("../A.csv", index=False)
    B.to_csv("../B.csv", index=False)

    print("Done.")
