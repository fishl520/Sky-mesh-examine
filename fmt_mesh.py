# Sky: Children of the Light (.mesh)
# Merged & Extended by AI based on Python Tool & Durik256 Plugin
from inc_noesis import *
import struct
import os
import binascii

def registerNoesisTypes():
    handle = noesis.register("Sky: Children of the Light", ".mesh")
    noesis.setHandlerTypeCheck(handle, noepyCheckType)
    noesis.setHandlerLoadModel(handle, noepyLoadModel)
    # noesis.logPopup()
    return 1

def noepyCheckType(data):
    if len(data) < 4:
        return 0
    return 1

def noepyLoadModel(data, mdlList):
    if 'ZipPos' in rapi.getInputName():
        noepyLoadZipModel(data, mdlList)
        return 1
        
    ctx = rapi.rpgCreateContext()
    magic = data[:4]
    filename = rapi.getLocalFileName(rapi.getInputName())
    bones = []

    try:
        if magic in (b'\x17\x00\x00\x00', b'\x18\x00\x00\x00'):
            bones = parse_17(data, filename)
        elif magic in (b'\x19\x00\x00\x00', b'\x1a\x00\x00\x00', b'\x1b\x00\x00\x00'):
            bones = parse_1A(data, filename)
        elif magic in (b'\x1c\x00\x00\x00', b'\x1d\x00\x00\x00'):
            bones = parse_1C(data, filename)
        elif magic == b'\x1e\x00\x00\x00':
            bones = parse_1E(data, filename)
        elif magic == b'\x1f\x00\x00\x00':
            bones = parse_1F20(data, filename, 0x1F)
        elif magic == b'\x20\x00\x00\x00':
            bones = parse_1F20(data, filename, 0x20)
        else:
            hex_magic = binascii.hexlify(magic).decode('ascii')
            print("Unknown magic header: " + hex_magic)
            return 0
    except Exception as e:
        print("Error parsing mesh: " + str(e))
        return 0

    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial('default','')]))
    if bones:
        mdl.setBones(bones)
        
    mdlList.append(mdl)
    return 1

# ======================= 解析各版本 =======================

def parse_17(data, filename):
    if "StripAnim" in filename: # 注意大小写
        vip = 0x4061; iip = 0x4065; vs = 0x408D
        vnum = struct.unpack('<I', data[vip:vip+4])[0]
        inum = struct.unpack('<I', data[iip:iip+4])[0]
        vbuf_len = vnum * 16
        
        vbuf = data[vs : vs+vbuf_len]
        gap = vbuf_len // 4
        us = vs + vbuf_len + gap
        uvbuf = data[us : us+vbuf_len]
        
        idx_s = us + vbuf_len + vnum * 8
        ibuf = data[idx_s : idx_s + inum*4]
    else:
        p01 = data.find(b'\x01')
        if p01 == -1: return []
        vip = p01 + 45; iip = 0x75; vs = 0x9D
        
        vnum = struct.unpack('<I', data[vip:vip+4])[0]
        inum = struct.unpack('<I', data[iip:iip+4])[0]
        vbuf_len = vnum * 16
        
        vbuf = data[vs : vs+vbuf_len]
        gap = vbuf_len // 4
        us = vs + vbuf_len + gap
        uvbuf = data[us : us+vbuf_len]
        
        idx_s = us + vbuf_len
        ibuf = data[idx_s : idx_s + inum*4]

    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 16)
    rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_FLOAT, 16)
    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_UINT, inum, noesis.RPGEO_TRIANGLE)
    return []

def parse_1A(data, filename):
    vco = 0x66; ico = 0x6A; vs = 0x92
    vnum = struct.unpack('<I', data[vco:vco+4])[0]
    inum = struct.unpack('<I', data[ico:ico+4])[0]
    vbuf_len = vnum * 16
    
    vbuf = data[vs : vs+vbuf_len]
    gap = vbuf_len // 4
    us = vs + vbuf_len + gap
    uvbuf = data[us : us+vbuf_len]
    
    fn_l = filename.lower()
    is_sp = ('anim' in fn_l or 'anc' in fn_l) and 'ancestor' not in fn_l
    idx_s = us + vbuf_len + (vnum * 8 if is_sp else 0)
    ibuf = data[idx_s : idx_s + inum*4]

    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 16)
    rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_FLOAT, 16)
    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_UINT, inum, noesis.RPGEO_TRIANGLE)
    return []

def parse_1C(data, filename):
    cs = struct.unpack('<I', data[0x4E:0x52])[0]
    us = struct.unpack('<I', data[0x52:0x56])[0]
    dr = rapi.decompLZ4(data[0x56 : 0x56+cs], us)
    
    vco = 0x34; ico = 0x38; vs = 0x60
    vnum = struct.unpack('<I', dr[vco:vco+4])[0]
    inum = struct.unpack('<I', dr[ico:ico+4])[0]
    vbuf_len = vnum * 16
    
    vbuf = dr[vs : vs+vbuf_len]
    gap = vbuf_len // 4
    us_start = vs + vbuf_len + gap
    uvbuf = dr[us_start : us_start+vbuf_len]
    
    fn_l = filename.lower()
    is_sp = ('anim' in fn_l or 'anc' in fn_l) and 'ancestor' not in fn_l
    idx_s = us_start + vbuf_len + (vnum * 8 if is_sp else 0)
    ibuf = dr[idx_s : idx_s + inum*4]

    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 16)
    rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_FLOAT, 16)
    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_UINT, inum, noesis.RPGEO_TRIANGLE)
    return []

def parse_1E(data, filename):
    cs = struct.unpack('<I', data[0x4E:0x52])[0]
    us = struct.unpack('<I', data[0x52:0x56])[0]
    dr = rapi.decompLZ4(data[0x56 : 0x56+cs], us)
    
    vnum = struct.unpack('<I', dr[0x74:0x78])[0]
    inum = struct.unpack('<I', dr[0x78:0x7C])[0] # 这已经是index的个数了
    vs = 0xB3
    vbuf_len = vnum * 16
    vbuf = dr[vs : vs+vbuf_len]
    
    fn_l = filename.lower()
    is_sp = ('anim' in fn_l) or ('anc' in fn_l and 'ancestor' not in fn_l)
    
    if is_sp:
        gap = vbuf_len // 4
        us_start = vs + vbuf_len + gap
        uvsz = vbuf_len
        idx_s = us_start + uvsz + vnum * 8
    else:
        gap = vnum * 4 - 4
        us_start = vs + vbuf_len + gap
        uvsz = vnum * 16
        idx_s = us_start + uvsz + 4
        
    uvbuf = dr[us_start : us_start+uvsz]
    ibuf = dr[idx_s : idx_s + inum*2]

    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 16)
    # 1E版本使用的是 Half-Float (16位) 的UV数据，起始偏移量在16字节步长内的第4个字节
    rapi.rpgBindUV1BufferOfs(uvbuf, noesis.RPGEODATA_HALFFLOAT, 16, 4)
    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, inum, noesis.RPGEO_TRIANGLE)
    return []

def parse_1F20(data, filename, version):
    if version == 0x1F:
        hdr = struct.unpack('<18IH3I', data[:86])
        bf = hdr[18]; csz = hdr[20]; usz = hdr[21]; cds = 86
    else:
        hdr = struct.unpack('<18IH4I', data[:90])
        bf = hdr[18]; csz = hdr[21]; usz = hdr[22]; cds = 90
        
    comp = data[cds : cds+csz]
    dr = rapi.decompLZ4(comp, usz)
    bds = cds + csz
    
    bones = []
    if bf == 1:
        # 在压缩块后提取骨骼信息
        bs = NoeBitStream(data[bds:])
        bi = struct.unpack('<20I', bs.readBytes(80))
        b = bs.readUByte()
        ti = bs.readUInt()
        bc = bi[17] # 骨骼数量
        
        for x in range(bc):
            name_raw = bs.readBytes(64).split(b'\x00')[0]
            name = name_raw.decode('ascii', errors='ignore') if name_raw else "bone_{}".format(x)
            mat_data = bs.readBytes(64)
            mat = NoeMat44.fromBytes(mat_data).toMat43().inverse()
            parent_idx = bs.readUInt() - 1
            bones.append(NoeBone(x, name, mat, None, parent_idx))

    # 解析解压后的 Payload 数据
    vnum = struct.unpack('<I', dr[116:120])[0]
    inum = struct.unpack('<I', dr[120:124])[0]
    vbs = 179
    
    vbuf = dr[vbs : vbs + vnum*16]
    uvbuf = dr[vbs + vnum*20 : vbs + vnum*36]
    
    if bf == 1:
        wbuf = dr[vbs + vnum*36 : vbs + vnum*44]
        ibuf = dr[vbs + vnum*44 : vbs + vnum*44 + inum*2]
    else:
        wbuf = None
        ibuf = dr[vbs + vnum*36 : vbs + vnum*36 + inum*2]

    # Noesis 绑定
    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 16)
    rapi.rpgBindUV1Buffer(uvbuf, noesis.RPGEODATA_HALFFLOAT, 16)
    rapi.rpgBindUV2BufferOfs(uvbuf, noesis.RPGEODATA_HALFFLOAT, 16, 4)
    
    if bf == 1 and wbuf:
        # 重建骨架映射
        bonemap = list(range(-1, len(bones)))
        bonemap[0] = 0
        rapi.rpgSetBoneMap(bonemap)
        
        # 权重/索引在 wbuf 内：前4字节为Index，后4字节为Weight
        rapi.rpgBindBoneIndexBuffer(wbuf, noesis.RPGEODATA_UBYTE, 8, 4)
        rapi.rpgBindBoneWeightBufferOfs(wbuf, noesis.RPGEODATA_UBYTE, 8, 4, 4)
        
    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, inum, noesis.RPGEO_TRIANGLE)
    return bones

# ======================= 保留 ZipPos 旧逻辑 =======================

def noepyLoadZipModel(data, mdlList):
    bones = []
    if data[:4] == b'\x1F\x00\x00\x00':
        bs = NoeBitStream(data)
        h = bs.read('18IH')[17:] + bs.read('3I')
        data = rapi.decompLZ4(bs.read(h[3]), h[4])
        if h[1] == 1:
            binf = bs.read('20I')+bs.read('B')+bs.read('I')
            for x in range(binf[17]):
                name = bs.read(64).replace(b'\x00', b'').decode('ascii', errors='ignore')
                mat = NoeMat44.fromBytes(bs.read(64)).toMat43().inverse()
                index = bs.readUInt()-1
                bones.append(NoeBone(x,name,mat,None,index))

    bs = NoeBitStream(data)
    ctx = rapi.rpgCreateContext()

    bs.seek(116)
    vnum = bs.readUInt()
    bs.seek(120)
    inum = bs.readUInt()
    bs.seek(128)
    unum = bs.readUInt()
    bs.seek(179)
    if(len(bones)):
        bs.seek(vnum*8,1)
    ibuf = bs.read(inum*2)
    
    bs.seek(len(data)-vnum*4)
    vbuf = bs.read(vnum*4)
    vbuf = decompV(vbuf, vnum)

    rapi.rpgBindPositionBuffer(vbuf, noesis.RPGEODATA_FLOAT, 12)
    rapi.rpgCommitTriangles(ibuf, noesis.RPGEODATA_USHORT, inum, noesis.RPGEO_TRIANGLE)
    
    try:
        mdl = rapi.rpgConstructModel()
    except:
        mdl = NoeModel()
    
    mdl.setModelMaterials(NoeModelMaterials([], [NoeMaterial('default','')]))
    mdl.setBones(bones)
    mdlList.append(mdl)
    return 1
    
def decompV(vbuf, vnum):
    bs = NoeBitStream(vbuf)
    vbuf = b''
    for x in range(vnum):
        vbuf += unpack_bytes_to_vector3(bs)
    return vbuf

def unpack_bytes_to_vector3(bs):
    x, y, z, w = struct.unpack('<BBBB', bs.read(4))
    return noePack('3f', y, z, w)