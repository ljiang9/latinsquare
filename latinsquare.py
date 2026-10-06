"""拉丁方阵小玩具：随机生成 n×n 拉丁方阵，或补全残缺拉丁方阵。"""

import argparse
import random
import sys


def is_latin(grid):
    """检查 grid 是否为合法拉丁方阵（每行每列数字互不相同，值为 1..n）。"""
    n = len(grid)
    if n == 0:
        return False
    want = set(range(1, n + 1))
    for row in grid:
        if len(row) != n or set(row) != want:
            return False
    for c in range(n):
        if {grid[r][c] for r in range(n)} != want:
            return False
    return True


def random_latin(n, rng=None):
    """生成随机 n×n 拉丁方阵：随机行列置换 + 随机符号置换，打乱循环群表。"""
    rng = rng or random.Random()
    # 基础拉丁方：grid[i][j] = (i + j) % n + 1
    perm_rows = list(range(n))
    perm_cols = list(range(n))
    perm_syms = list(range(1, n + 1))
    rng.shuffle(perm_rows)
    rng.shuffle(perm_cols)
    rng.shuffle(perm_syms)
    return [
        [perm_syms[(perm_rows[i] + perm_cols[j]) % n] for j in range(n)]
        for i in range(n)
    ]


def complete(grid):
    """回溯补全残缺拉丁方阵（0 表示空格），返回第一个解，失败返回 None。

    输入必须矩形、n×n、已有数字互不冲突，否则返回 None。
    """
    n = len(grid)
    if n == 0 or any(len(row) != n for row in grid):
        return None
    for v in (v for row in grid for v in row):
        if not isinstance(v, int) or v < 0 or v > n:
            return None
    # 预检已有数字冲突
    rows = [set() for _ in range(n)]
    cols = [set() for _ in range(n)]
    for i in range(n):
        for j in range(n):
            v = grid[i][j]
            if v:
                if v in rows[i] or v in cols[j]:
                    return None
                rows[i].add(v)
                cols[j].add(v)
    empties = [(i, j) for i in range(n) for j in range(n) if grid[i][j] == 0]
    # MRV 排序静态化：每次选可选值最少的空格
    board = [row[:] for row in grid]

    def options(i, j):
        return [
            v for v in range(1, n + 1)
            if v not in rows[i] and v not in cols[j]
        ]

    def rec(k):
        if k == len(empties):
            return True
        # 找剩余空格中选项最少的
        best, best_opts = -1, None
        for t in range(k, len(empties)):
            i, j = empties[t]
            opts = options(i, j)
            if not opts:
                return False
            if best_opts is None or len(opts) < len(best_opts):
                best, best_opts = t, opts
                if len(best_opts) == 1:
                    break
        empties[k], empties[best] = empties[best], empties[k]
        i, j = empties[k]
        for v in best_opts:
            board[i][j] = v
            rows[i].add(v)
            cols[j].add(v)
            if rec(k + 1):
                return True
            rows[i].discard(v)
            cols[j].discard(v)
            board[i][j] = 0
        empties[k], empties[best] = empties[best], empties[k]
        return False

    return board if rec(0) else None


def render(grid):
    n = len(grid)
    width = len(str(n))
    lines = []
    for row in grid:
        cells = [str(v).rjust(width) if v else ".".rjust(width) for v in row]
        lines.append(" ".join(cells))
    return "\n".join(lines)


def parse_grid(text, n):
    """解析 n 行、每行 n 个数字（0 或 . 表示空格）的文本。"""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if len(lines) != n:
        raise ValueError(f"需要 {n} 行，实际 {len(lines)} 行")
    grid = []
    for ln in lines:
        toks = ln.replace(",", " ").split()
        if len(toks) != n:
            raise ValueError(f"每行需要 {n} 个数字，实际 {len(toks)} 个：{ln!r}")
        row = []
        for t in toks:
            if t == ".":
                row.append(0)
            else:
                try:
                    row.append(int(t))
                except ValueError:
                    raise ValueError(f"非法数字：{t!r}")
        grid.append(row)
    return grid


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="拉丁方阵小玩具：生成随机 n×n 拉丁方阵，或补全残缺方阵。"
    )
    ap.add_argument("--n", type=int, default=5, help="方阵阶数（3-9，默认 5）")
    ap.add_argument("--seed", type=int, default=None, help="随机种子")
    ap.add_argument(
        "--complete", action="store_true",
        help="补全模式：从 stdin 或 --file 读入残缺方阵（0 或 . 表示空格）",
    )
    ap.add_argument("--file", default=None, help="补全模式的输入文件（默认 stdin）")
    ap.add_argument("--check", action="store_true", help="仅校验输入是否为合法拉丁方阵")
    args = ap.parse_args(argv)

    n = args.n
    if not 3 <= n <= 9:
        print(f"错误：--n 必须在 3 到 9 之间，实际 {n}", file=sys.stderr)
        return 2
    rng = random.Random(args.seed)

    if args.complete or args.check:
        if args.file:
            try:
                text = open(args.file, encoding="utf-8").read()
            except OSError as e:
                print(f"错误：读文件失败：{e}", file=sys.stderr)
                return 2
        else:
            if sys.stdin.isatty():
                print(f"从 stdin 输入 {n} 行、每行 {n} 个数字（0 或 . 表示空格），Ctrl-D 结束：",
                      file=sys.stderr)
            text = sys.stdin.read()
        try:
            grid = parse_grid(text, n)
        except ValueError as e:
            print(f"错误：{e}", file=sys.stderr)
            return 2
        if args.check:
            ok = all(v != 0 for row in grid for v in row) and is_latin(grid)
            print("合法拉丁方阵 ✅" if ok else "不是合法拉丁方阵 ❌")
            return 0 if ok else 1
        sol = complete(grid)
        if sol is None:
            print("无解：输入存在冲突或无法补全。")
            return 1
        print(f"补全结果（{n}×{n}）：\n")
        print(render(sol))
        return 0

    grid = random_latin(n, rng)
    seed_info = f"，种子={args.seed}" if args.seed is not None else ""
    print(f"随机拉丁方阵 {n}×{n}{seed_info}：\n")
    print(render(grid))
    return 0


if __name__ == "__main__":
    sys.exit(main())
