#!/usr/bin/python
# coding:utf-8
# Filename:IPLocate.py
# The Program Is Used To Locate IP.

from __future__ import print_function, division
import re
import socket
import struct

_unpack_S = lambda s: struct.unpack("12s", s)
_unpack_L = lambda l: struct.unpack("<L", l)
_unpack_Q = lambda q: struct.unpack("Q", q)


def _to_str(something):
    if isinstance(something, bytes):
        return something.decode('utf8')
    else:
        return something


class IP(object):
    def __init__(self, ):
        self.base_len = 64
        self.offset_addr = 0
        self.offset_owner = 0
        self.offset_info = None
        self.ip_re = re.compile('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$')

    def load_dat(self, fname):
        '''Load Dat File To Memory'''
        try:
            f = open(fname, "rb")
            finfo = f.read()
            self.offset_info = finfo[16:]
            self.offset_addr, = _unpack_Q(finfo[0:8])
            self.offset_owner, = _unpack_Q(finfo[8:16])
            f.close()
        except Exception as e:
            print(e)
            print("Loda File Fail.")
            exit(0)

    def locate_ip(self, ip):
        '''Locate IP'''
        if self.ip_re.match(ip):
            nip = socket.ntohl(struct.unpack("I", socket.inet_aton(str(ip)))[0])
        else:
            return ['Error IP']

        record_min = 0
        record_max = self.offset_addr // self.base_len - 1
        record_mid = (record_min + record_max) // 2
        while record_max - record_min >= 0:
            minip, = _unpack_L(self.offset_info[record_mid * self.base_len: record_mid * self.base_len + 4])
            maxip, = _unpack_L(self.offset_info[record_mid * self.base_len + 4: record_mid * self.base_len + 8])
            if nip < minip:
                record_max = record_mid - 1
            elif (nip == minip) or (nip > minip and nip < maxip) or (nip == maxip):
                addr_begin, = _unpack_Q(self.offset_info[record_mid * self.base_len + 8: record_mid * self.base_len + 16])
                addr_length, = _unpack_Q(self.offset_info[record_mid * self.base_len + 16: record_mid * self.base_len + 24])
                owner_begin, = _unpack_Q(self.offset_info[record_mid * self.base_len + 24: record_mid * self.base_len + 32])
                owner_length, = _unpack_Q(self.offset_info[record_mid * self.base_len + 32: record_mid * self.base_len + 40])
                wgs_lon, = _unpack_S(self.offset_info[record_mid * self.base_len + 40: record_mid * self.base_len + 52])
                wgs_lat, = _unpack_S(self.offset_info[record_mid * self.base_len + 52: record_mid * self.base_len + 64])
                addr_bundle = self.offset_info[addr_begin:addr_begin + addr_length]
                if isinstance(addr_bundle, bytes):  # python3 python2
                    addr_bundle = addr_bundle.decode('utf8')
                addr = addr_bundle.split("|")
                owner = self.offset_info[owner_begin:owner_begin + owner_length]

                tmp_list = [str(minip), str(maxip), addr[0], addr[1], addr[2], addr[3], addr[4], addr[5], addr[6], _to_str(wgs_lon), _to_str(wgs_lat), _to_str(owner)]
                res_list = []
                for item in tmp_list:
                    item = item.replace('\x00', '')
                    res_list.append(item)
                return res_list
            elif nip > maxip:
                record_min = record_mid + 1
            else:
                print("Error Case")
            record_mid = (record_min + record_max) // 2
        return ['Not Found.']


if __name__ == '__main__':
    test = IP()
    test.load_dat("test.dat")
    result = test.locate_ip('1.1.1.1')
    print(result)
