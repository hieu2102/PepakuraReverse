import zlib
import math, sys
from PIL import Image
from PDO import ParseBuffer
import os
from contextlib import redirect_stdout
import re


def arr(*x):
    return "[%s]" % (", ".join(map(repr, x)))


def parse(data, file_name: str):
    file_name_without_ext: str = file_name.replace(".pdo", "")
    # create image output dir
    if not os.path.exists(file_name_without_ext):
        os.mkdir(file_name_without_ext)
    buf: ParseBuffer = ParseBuffer(data)
    assert buf.str(10) == "version 3\n"
    with open(f"{file_name_without_ext}/line.yaml", "w") as f:
        with redirect_stdout(f):
            locked = buf.uint32  # 4 == unlocked, 5 == locked
            print("locked:", locked)
            print("unk1:", buf.uint32)
            print("version:", buf.uint32)
            print()

            if locked == 5:
                print("software:", re.sub(r"[\W]", " ", buf.wstr))  # Empty for en-us
                buf.key = buf.uint32
                print("key:", buf.key)
                print()

            print(
                "locale:", buf.wstr
            )  # Should always be empty for en-us, according to the codepage bug
            buf.codepage = buf.wstr
            print("codepage:", buf.codepage)
            print("unk3:", buf.uint32)
            print("hexstring:", buf.wstr)
            print()

            if locked == 5:
                print("unk4:", buf.bool)
                print("unk5:", buf.bool)
                print()

            print("unk6:", arr(buf.double, buf.double, buf.double, buf.double))
            print("geometry:")
            for i in range(buf.uint32):
                print("  - name:", buf.wstr)
                print("    unk8:", buf.bool)
                print("    vertices:")
                for j in range(buf.uint32):
                    print("      -", arr(buf.double, buf.double, buf.double))
                print()
                print("    shapes:")
                for j in range(buf.uint32):
                    print("      - textureIdx:", buf.int32)
                    print("        part:", buf.uint32)
                    print(
                        "        plane:",
                        arr(buf.double, buf.double, buf.double, buf.double),
                    )
                    print("        points:")
                    for k in range(buf.uint32):
                        print("          - index:", buf.uint32)
                        print("            coord:", arr(buf.double, buf.double))
                        print("            unk13:", arr(buf.double, buf.double))
                        print("            may_need_tab:", buf.bool)
                        print("            tab_height:", buf.double)
                        print("            tab_angles:", arr(buf.double, buf.double))
                        print(
                            "            tab_edge_color:",
                            arr(
                                buf.float,
                                buf.float,
                                buf.float,
                            ),
                        )
                        print(
                            "            edge_color:",
                            arr(
                                buf.float,
                                buf.float,
                                buf.float,
                            ),
                        )
                    print()
                print()
                print("    unk17:")
                for j in range(buf.uint32):
                    print(
                        "      -",
                        arr(
                            buf.uint32,
                            buf.uint32,
                            buf.uint32,
                            buf.uint32,
                            buf.bool,
                            buf.bool,
                            buf.uint32,
                        ),
                    )
                print()
            print()

            print("textures:")
            for i in range(buf.uint32):
                print("  - name:", buf.wstr)
                print("    unk20:", arr(buf.float, buf.float, buf.float, buf.float))
                print("    unk21:", arr(buf.float, buf.float, buf.float, buf.float))
                print("    unk22:", arr(buf.float, buf.float, buf.float, buf.float))
                print("    unk23:", arr(buf.float, buf.float, buf.float, buf.float))
                print("    unk24:", arr(buf.float, buf.float, buf.float, buf.float))
                has_image = buf.bool
                print("    has_image:", has_image)
                if has_image:
                    w, h = buf.uint32, buf.uint32
                    print("    width:", w)
                    print("    height:", h)
                    csize = buf.uint32
                    print("    csize:", csize)
                    cbuf = buf.read(csize)
                    cbuf = zlib.decompress(cbuf)
                    im = Image.frombuffer("RGB", (w, h), cbuf)
                    im.save(f"{file_name_without_ext}/texture-{i}.png")
                    print("    fn: texture-%i.png" % i)
                print()
            print()

            if buf.bool:
                print("unk26:", buf.double)
                print("unk27:", buf.bool)
                print("unk28:", arr(buf.double, buf.double, buf.double, buf.double))

                print("unk29:")
                for i in range(buf.uint32):
                    print(
                        "  - unk30:",
                        arr(buf.uint32, buf.double, buf.double, buf.double, buf.double),
                    )
                    if locked == 5:
                        print("    unk31:", buf.wstr)
                    print("    unk32:")
                    for j in range(buf.uint32):
                        print("      - unk33:", arr(buf.bool, buf.uint32))
                        if buf.bool:
                            print("        unk34:", arr(buf.uint32, buf.uint32))
                        if buf.bool:
                            print("        unk35:", arr(buf.uint32, buf.uint32))
                    print()
                print()

                print("text_display:")
                for i in range(buf.uint32):
                    print(
                        "  - unk37:",
                        arr(buf.double, buf.double, buf.double, buf.double, buf.double),
                    )
                    print("    unk38:", arr(buf.uint32, buf.uint32))
                    print("    font:", buf.wstr)
                    print("    lines:")
                    for j in range(buf.uint32):
                        print("      -", buf.wstr)
                    print()

                print("unk39:")
                for i in range(buf.uint32):
                    print(
                        "  - unk40:",
                        arr(buf.double, buf.double, buf.double, buf.double),
                    )
                    print("    unk41:", arr(buf.uint32, buf.uint32))
                    cbuf = buf.read(buf.uint32)
                    dbuf = zlib.decompress(cbuf)
                    print("    decompressed_size:", len(dbuf))
                    print()
                print()

                print("unk42:")
                for i in range(buf.uint32):
                    print(
                        "  - unk43:",
                        arr(buf.double, buf.double, buf.double, buf.double),
                    )
                    print("    unk44:", arr(buf.uint32, buf.uint32))
                    cbuf = buf.read(buf.uint32)
                    dbuf = zlib.decompress(cbuf)
                    print("    decompressed_size:", len(dbuf))
                    print()

            print("unk45:", arr(buf.bool, buf.bool, buf.bool, buf.bool, buf.bool))
            print(
                "unk46:",
                arr(
                    buf.uint32, buf.bool, buf.uint32, buf.uint32, buf.uint32, buf.uint32
                ),
            )

            unk = buf.uint32
            if unk == 0x0B:
                print("unk47:", arr(buf.double, buf.double))
            else:
                print("unk48:", unk)
            print()

            print("unk49:", arr(buf.uint32, buf.uint32, buf.uint32))
            print(
                "unk50:",
                arr(
                    buf.double,
                    buf.double,
                    buf.double,
                    buf.double,
                    buf.double,
                    buf.double,
                ),
            )
            print(
                "unk51:",
                arr(
                    buf.double,
                    buf.double,
                    buf.double,
                    buf.double,
                    buf.double,
                    buf.double,
                ),
            )

            print("unk52:", arr(buf.bool, buf.double))
            if locked == 5:
                print("unk53:", '"' + buf.wstr + '"')
                print("unk54:", '"' + buf.wstr + '"')

    assert buf.uint32 == 0x270F
    assert buf.end
    f.close()


if __name__ == "__main__":
    data = open(sys.argv[1], "rb").read()
    parse(data, file_name=sys.argv[1])
