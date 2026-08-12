import argparse


def calculate_capacity(flow, head, efficiency=0.85):
    """Estimate hydropower capacity in MW using P = 9.81 * Q * H * η."""
    return 9.81 * flow * head * efficiency / 1000.0


def read_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Please enter a number.")


def parse_args():
    parser = argparse.ArgumentParser(description="Simple hydropower capacity calculator")
    parser.add_argument("--flow", "-q", type=float, help="Flow Q in m^3/s")
    parser.add_argument("--head", "-h", type=float, help="Head H in meters")
    parser.add_argument("--efficiency", "-e", type=float, default=0.85, help="Efficiency between 0 and 1")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.flow is not None and args.head is not None:
        Q = args.flow
        H = args.head
        eta = args.efficiency
    else:
        print("Simple hydropower capacity calculator")
        Q = read_float("Enter flow Q (m^3/s): ")
        H = read_float("Enter head H (m): ")
        eta_input = input("Enter efficiency (0-1) [default 0.85]: ").strip()
        try:
            eta = float(eta_input) if eta_input else 0.85
        except ValueError:
            eta = 0.85

    capacity_mw = calculate_capacity(Q, H, eta)
    capacity_kw = capacity_mw * 1000.0
    print(f"Estimated capacity: {capacity_kw:.1f} kW ({capacity_mw:.3f} MW) at efficiency {eta}")


if __name__ == '__main__':
    main()
