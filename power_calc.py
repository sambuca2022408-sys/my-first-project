def read_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Please enter a number.")


def main():
    print("Simple hydropower capacity calculator")
    Q = read_float("Enter flow Q (m^3/s): ")
    H = read_float("Enter head H (m): ")
    eta = input("Enter efficiency (0-1) [default 0.85]: ").strip()
    try:
        eta = float(eta) if eta else 0.85
    except ValueError:
        eta = 0.85

    # Using P (kW) = 9.81 * Q * H * eta, convert to MW
    P_kw = 9.81 * Q * H * eta
    P_mw = P_kw / 1000.0

    print(f"Estimated capacity: {P_kw:.1f} kW ({P_mw:.3f} MW) at efficiency {eta}")


if __name__ == '__main__':
    main()
