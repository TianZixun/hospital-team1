from hospital_team1.calculator import Calculator


def main() -> None:
    calc = Calculator()
    print("Hospital Team 1 project is ready.")
    print(f"2 + 3 = {calc.add(2, 3)}")
    print(f"7 - 4 = {calc.subtract(7, 4)}")
    print(f"6 * 5 = {calc.multiply(6, 5)}")
    print(f"8 / 2 = {calc.divide(8, 2)}")


if __name__ == "__main__":
    main()
