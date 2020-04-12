import zlib
s = "Hello World! Python is great!"
t = zlib.compress(s.encode("utf-8"))
print(t)
print(zlib.decompress(t))
