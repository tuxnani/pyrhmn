import zlib
s = "Helllo World! Python is great!"
t = zlib.compress(s.encode("utf-8"))
print(len(t),"\n")
print(t,"\n")
print(len(s),"\n")
print(zlib.decompress(t))
