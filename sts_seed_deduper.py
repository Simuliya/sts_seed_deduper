#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import glob
import traceback
from collections import defaultdict
from datetime import datetime


def clean_duplicate_seed_runs():
    RUNS_DIR = r"E:\Steam\steamapps\common\SlayTheSpire\runs"

    print("=" * 70)
    print(" 杀戮尖塔 .run 文件去重工具（区分手动/自动种子 + 显示时间）")
    print("=" * 70)
    print()
    print("规则：")
    print(" - 每个角色单独处理")
    print(" - 同一角色下：")
    print("     · 相同种子仅保留 1 个手动（chose_seed:true）")
    print("     · 相同种子仅保留 1 个自动（chose_seed:false）")
    print(" - 不同角色的种子互不影响")
    print("=" * 70)
    print()

    if not os.path.exists(RUNS_DIR):
        print(f"❌ 路径不存在: {RUNS_DIR}")
        input("按回车退出...")
        return

    # 模式选择
    print("请选择模式:")
    print("  1. 仅预览（dry-run，不删除文件）")
    print("  2. 实际删除重复文件")
    mode = input("输入 1 或 2，然后回车: ").strip()
    dry_run = mode != "2"

    if dry_run:
        print("\n💡 当前为【预览模式】，不会删除任何文件。\n")
    else:
        print("\n⚠️ 当前为【删除模式】，将会修改文件。\n")
        confirm = input("确定要继续吗？(y/N): ").lower()
        if confirm != "y":
            print("操作已取消。")
            input("按回车退出...")
            return

    total_deleted = 0
    total_characters = 0
    total_candidates = 0

    try:
        # 遍历角色目录
        for character in os.listdir(RUNS_DIR):
            role_path = os.path.join(RUNS_DIR, character)
            if not os.path.isdir(role_path):
                continue

            run_files = glob.glob(os.path.join(role_path, "*.run"))
            if not run_files:
                continue

            total_characters += 1
            print(f"\n处理角色: {character}")
            print("-" * 70)

            # {seed: {"manual": [files], "auto": [files]}}
            seed_groups = defaultdict(lambda: {"manual": [], "auto": []})

            for file in run_files:
                try:
                    with open(file, "r", encoding="utf-8", errors="ignore") as f:
                        text = f.read()

                    seed_match = re.search(r'"seed_played"\s*:\s*"([^"]+)"', text)
                    chose_match = re.search(r'"chose_seed"\s*:\s*(true|false)', text)

                    if not seed_match or not chose_match:
                        continue

                    seed = seed_match.group(1)
                    chose = chose_match.group(1).lower() == "true"
                    mtime = os.path.getmtime(file)
                    mtime_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")

                    entry = {"file": file, "mtime": mtime, "mtime_str": mtime_str}

                    if chose:
                        seed_groups[seed]["manual"].append(entry)
                    else:
                        seed_groups[seed]["auto"].append(entry)

                except Exception as e:
                    print(f"  读取失败: {os.path.basename(file)} -> {e}")

            deleted = 0

            # 去重逻辑
            for seed, types in seed_groups.items():
                for mode_name, files in types.items():
                    if len(files) > 1:
                        files.sort(key=lambda x: x["mtime"], reverse=True)
                        keep = files[0]
                        keep_name = os.path.basename(keep["file"])
                        print(f"  种子 {seed} ({'手动' if mode_name=='manual' else '自动'})：")
                        print(f"    保留: {keep_name} [{keep['mtime_str']}]")

                        for old in files[1:]:
                            old_name = os.path.basename(old["file"])
                            old_time = old["mtime_str"]
                            total_candidates += 1
                            if dry_run:
                                print(f"    [预览] 将删除: {old_name} [{old_time}]")
                            else:
                                try:
                                    os.remove(old["file"])
                                    print(f"    删除: {old_name} [{old_time}]")
                                    total_deleted += 1
                                    deleted += 1
                                except Exception as e:
                                    print(f"    删除失败: {old_name} ({e})")

            if deleted == 0:
                print("  ✅ 无重复文件")
            else:
                print(f"  🗑️ 删除了 {deleted} 个重复文件")

    except Exception:
        print("\n❌ 未捕获异常：")
        print(traceback.format_exc())

    print("\n" + "=" * 70)
    if dry_run:
        print("✅ 预览完成（未删除任何文件）")
        print(f"检测到 {total_candidates} 个重复文件")
    else:
        print("✅ 清理完成")
        print(f"共删除 {total_deleted} 个重复文件")
    print(f"共处理 {total_characters} 个角色目录")
    print("=" * 70)
    input("按回车退出...")


if __name__ == "__main__":
    clean_duplicate_seed_runs()
