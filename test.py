from hospital_team1 import Calculator


def run_demo() -> None:
    calc = Calculator()
    print("VSCode test program is running.")
    print("1 + 2 =", calc.add(1, 2))
    print("9 - 4 =", calc.subtract(9, 4))
    print("3 * 7 =", calc.multiply(3, 7))
    print("12 / 3 =", calc.divide(12, 3))


if __name__ == "__main__":
    run_demo()

