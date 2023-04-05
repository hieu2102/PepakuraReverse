import struct
import codecs
import re

codepages = {
    "Sfhit-JIS": "shift_jis",
}


class ParseBuffer(object):
    def __init__(self, data):
        self.data = data
        self.i = 0
        self.key = None
        self.codepage = None

    @property
    def end(self):
        return self.i == len(self.data)

    def peek(self, size):
        return self.data[self.i : self.i + size]

    def read(self, size):
        self.i += size
        return self.data[self.i - size : self.i]

    def unpack(self, fmt):
        fmt = "<" + fmt
        ret = struct.unpack(fmt, self.read(struct.calcsize(fmt)))
        if len(ret) == 1:
            return ret[0]
        return ret

    @property
    def byte(self):
        return self.unpack("B")

    def bytes(self, size):
        return map(ord, self.read(size))

    @property
    def bool(self):
        return {0: False, 1: True}[
            self.byte
        ]  # Throws an exception if the byte is non 0/1

    @property
    def int16(self):
        return self.unpack("h")

    @property
    def uint16(self):
        return self.unpack("H")

    @property
    def int32(self):
        return self.unpack("i")

    @property
    def uint32(self):
        return self.unpack("I")

    @property
    def float(self):
        return self.unpack("f")

    @property
    def double(self):
        return self.unpack("d")

    def str(self, size: int = None):
        size = self.uint32 if size == None else size
        return self.read(size).decode("utf-8", errors="ignore")

    @property
    def wstr(self):
        if self.key is not None:
            data = "".join(chr((ord(x) - self.key + 256) % 256) for x in self.str())
        else:
            data = self.str()
        if self.codepage is None or self.codepage not in codepages:
            return data

        return codecs.decode(data, codepages[self.codepage]).encode("utf-8")


class Shape(object):
    def __init__(self, buf: ParseBuffer):
        self.textureIdx: int = buf.int32
        self.part: int = buf.uint32
        self.plane: list[float] = [buf.double, buf.double, buf.double, buf.double]
        self.points: list[Point] = []
        for i in range(buf.uint32):
            self.points.append(Point(buf=buf))


class Point(object):
    def __init__(self, buf: ParseBuffer):
        self.index: int = buf.uint32
        self.coord: list[float] = [buf.double, buf.double]
        self.unk13: list[float] = [buf.double, buf.double]
        self.need_tab: bool = buf.bool
        self.tab_height: float = buf.double
        self.tab_angles: list[float] = [buf.double, buf.double]
        self.tab_edge_color: list[float] = [buf.float, buf.float, buf.float]
        self.edge_color: list[float] = [buf.float, buf.float, buf.float]


class Geometry(object):
    def __init__(self, buf: ParseBuffer):
        self.name: str = buf.wstr
        self.unk8: bool = buf.bool
        self.vertices: list[list[float]] = []
        for i in range(buf.uint32):
            self.vertices.append([buf.double, buf.double, buf.double])
        self.shapes: list[Shape] = []
        for i in range(buf.uint32):
            self.shapes.append(Shape(buf=buf))
        self.edges: list[list] = []
        for j in range(buf.uint32):
            self.edges.append(
                [
                    buf.uint32,
                    buf.uint32,
                    buf.uint32,
                    buf.uint32,
                    buf.bool,
                    buf.bool,
                    buf.uint32,
                ]
            )


class PDO(object):
    def __init__(self, buf: ParseBuffer):
        self.locked: int = buf.uint32
        self.unk1: int = buf.uint32
        self.version: int = buf.uint32
        if self.locked == 5:
            self.software: str = re.sub(r"[\W]", " ", buf.wstr)
            self.key: int = buf.uint32
        self.locale: str = buf.wstr
        self.codepage: str = buf.wstr
        self.unk3: int = buf.uint32
        self.hexstring: str = buf.wstr
        if self.locked == 5:
            self.unk4: bool = buf.bool
            self.unk5: bool = buf.bool
        self.unk6: list[float] = [buf.double, buf.double, buf.double, buf.double]
        self.geometry: list[Geometry] = []
        for i in range(buf.uint32):
            self.geometry.append(Geometry(buf=buf))
