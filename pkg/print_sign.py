def print_sign(sign: str, size: str):
    slen = len(sign.encode("utf-8"))
    if size == "main":
        # print("\n")
        print("=" * (slen + 6))
        print("=" + " " * (slen + 4) + "=")
        print(f"=  {sign}  =")
        print("=" + " " * (slen + 4) + "=")
        print("=" * (slen + 6))
        # print("\n")
    elif size == "small":
        # print("\n")
        print("-" * slen + "\n" + sign + "\n" + "-" * slen)
        # print("\n")
