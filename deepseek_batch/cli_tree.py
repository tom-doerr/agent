import argparse
from . import TryTree


def _c(s, code):
    return f"\x1b[{code}m{s}\x1b[0m"


def main() -> None:
    p = argparse.ArgumentParser(prog="deepseek-tree")
    p.add_argument("text")
    p.add_argument("--init-n", type=int, default=4)
    p.add_argument("--expand-k", type=int, default=2)
    p.add_argument("--iters", type=int, default=2)
    p.add_argument("--model", default=None)
    p.add_argument("--temperature", type=float, default=None)
    args = p.parse_args()

    gen_params = ({"temperature": args.temperature} if args.temperature is not None else None)
    tree = TryTree(init_n=args.init_n, expand_k=args.expand_k, iters=args.iters, model=args.model, gen_params=gen_params)
    out = tree(args.text)
    print(_c("BEST", "36") + ": " + _c(out, "1;32"))


if __name__ == "__main__":
    main()
