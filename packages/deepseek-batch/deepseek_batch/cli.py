import argparse
from . import batch_best


def main() -> None:
    p = argparse.ArgumentParser(prog="deepseek-batch")
    p.add_argument("text")
    p.add_argument("-n", "--num", type=int, default=4)
    p.add_argument("--model", default=None)
    p.add_argument("--temperature", type=float, default=None)
    p.add_argument("--no-include-original", action="store_true")
    args = p.parse_args()
    gen_params = ({"temperature": args.temperature} if args.temperature is not None else None)

    def _c(s, code):
        return f"\x1b[{code}m{s}\x1b[0m"

    out = batch_best(args.text, n=args.num, model=args.model, include_original=not args.no_include_original, gen_params=gen_params)
    print(_c("BEST", "36") + ": " + _c(out, "1;32"))


if __name__ == "__main__":
    main()

