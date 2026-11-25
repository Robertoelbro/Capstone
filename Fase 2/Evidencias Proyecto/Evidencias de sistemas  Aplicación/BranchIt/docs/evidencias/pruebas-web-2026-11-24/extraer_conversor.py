"""Read MSI tables and embedded cabinets as data only; never execute MSI actions."""
import ctypes as c
from ctypes import wintypes as w
from pathlib import Path
import subprocess
import sys

package=Path(sys.argv[1]).resolve()
target=package.parent/'lectura_archivo'
target.mkdir(exist_ok=True)
dll=c.WinDLL('msi.dll')
handle=w.UINT
def api(name,args):
    f=getattr(dll,name);f.argtypes=args;f.restype=w.UINT;return f
op=api('MsiOpenDatabaseW',[w.LPCWSTR,w.LPCWSTR,c.POINTER(handle)])
ov=api('MsiDatabaseOpenViewW',[handle,w.LPCWSTR,c.POINTER(handle)])
execute=api('MsiViewExecute',[handle,handle])
fetch=api('MsiViewFetch',[handle,c.POINTER(handle)])
getstr=api('MsiRecordGetStringW',[handle,w.UINT,w.LPWSTR,c.POINTER(w.DWORD)])
read=api('MsiRecordReadStream',[handle,w.UINT,c.c_void_p,c.POINTER(w.DWORD)])
close=api('MsiCloseHandle',[handle])
def check(code):
    if code:raise OSError(code)
db=handle();check(op(str(package),None,c.byref(db)))
def string(rec,i):
    n=w.DWORD(32768);buf=c.create_unicode_buffer(n.value)
    check(getstr(rec,i,buf,c.byref(n)));return buf.value
def query(sql,fields):
    view=handle();check(ov(db,sql,c.byref(view)));check(execute(view,0))
    out=[]
    while True:
        rec=handle();code=fetch(view,c.byref(rec))
        if code==259:break
        check(code);out.append(tuple(string(rec,i) for i in range(1,fields+1)));close(rec)
    close(view);return out
dirs={k:(parent,name) for k,parent,name in query('SELECT `Directory`,`Directory_Parent`,`DefaultDir` FROM `Directory`',3)}
components=dict(query('SELECT `Component`,`Directory_` FROM `Component`',2))
files=query('SELECT `File`,`Component_`,`FileName` FROM `File`',3)
cabinets=[x[0] for x in query('SELECT `Cabinet` FROM `Media`',1) if x[0].startswith('#')]
unpacked=target/'cabinet_data';unpacked.mkdir(exist_ok=True)
for cabinet in cabinets:
    name=cabinet[1:];view=handle();check(ov(db,"SELECT `Data` FROM `_Streams` WHERE `Name`='"+name.replace("'","''")+"'",c.byref(view)))
    check(execute(view,0));rec=handle();check(fetch(view,c.byref(rec)))
    cabpath=target/name
    with cabpath.open('wb') as stream:
        buf=c.create_string_buffer(4*1024*1024)
        while True:
            size=w.DWORD(len(buf));check(read(rec,1,buf,c.byref(size)))
            if not size.value:break
            stream.write(buf.raw[:size.value])
    close(rec);close(view)
    with (target/'descompresion.log').open('ab') as log:
        result=subprocess.run(['expand.exe','-F:*',str(cabpath),str(unpacked)],stdout=log,stderr=log,creationflags=0x08000000)
        if result.returncode:raise RuntimeError('No se pudo extraer el cabinet')
def directory(key):
    if key=='TARGETDIR' or not key:return Path()
    parent,name=dirs[key]
    name=name.split(':')[0].split('|')[-1]
    return directory(parent)/(name if name not in ['.','SourceDir'] else '')
for filekey,component,name in files:
    source=unpacked/filekey
    if not source.exists():continue
    destination=target/'programa'/directory(components[component])/name.split('|')[-1]
    destination.parent.mkdir(parents=True,exist_ok=True)
    source.replace(destination)
close(db)
print('Lectura completada sin ejecutar acciones del MSI',flush=True)
for p in (target/'programa').rglob('soffice.exe'):print(p,flush=True)
