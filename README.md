# latinsquare 拉丁方阵小玩具

随机生成 n×n 拉丁方阵（n=3–9），或补全残缺拉丁方阵。纯标准库，中文界面。

## 玩法

拉丁方阵：n×n 方格，填入 1–n，每行每列数字互不重复。

```bash
# 生成 5×5 随机拉丁方阵
python3 -m latinsquare --n 5

# 固定种子，可复现
python3 -m latinsquare --n 6 --seed 42

# 补全残缺方阵（0 或 . 表示空格），从 stdin 读入
printf '1 0 0 0\n0 3 0 0\n0 0 1 0\n0 0 0 2\n' | python3 -m latinsquare --n 4 --complete

# 从文件读入补全
python3 -m latinsquare --n 4 --complete --file puzzle.txt

# 只校验是否为合法拉丁方阵
python3 -m latinsquare --n 3 --check < square.txt
```

补全示例（真实运行输出）：

```
补全结果（4×4）：

1 2 3 4
4 3 2 1
2 4 1 3
3 1 4 2
```

## 实现思路

- **生成**：从循环群表 `(i+j) mod n` 出发，做随机行置换、列置换、符号置换——数学上保证结果仍是拉丁方阵，且分布均匀。
- **补全**：回溯 + MRV 启发式（每次选可选值最少的空格），返回第一个解。
- **校验**：`is_latin` 独立检查行列互异。

## 验证记录（真实执行）

- `python3 -m py_compile latinsquare.py __main__.py` → 通过
- 20 个种子 × n=3–9，生成的方阵全部通过 `is_latin`，且各行互不相同
- 手工残缺 4×4 补全成功，解合法且尊重已填数字
- 冲突输入（同行/同列重复、真无解残缺）→ 返回"无解"，退出码 1
- 非矩形、非法数字、行列数不符 → 中文报错，退出码 2
- `--seed` 两次运行输出逐字节一致；`--file` / 直接 `python3 latinsquare.py` 均正常

## 已知局限

- 回溯补全只适合小棋盘（n≤9，默认 5）；n 再大搜索会明显变慢
- 补全只返回第一个解，不统计解的个数、不保证唯一解
- 生成器保证合法但不做难度分级
- 需要 Python 3.10+
