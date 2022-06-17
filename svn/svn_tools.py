#%%
import os
import re
import asyncio
from datetime import datetime
from pathlib import Path
from subprocess import run, PIPE, CalledProcessError
from xml.etree import ElementTree

from pprint import pprint

wc_path = Path("/home/simon/svn/test")
f_path = wc_path / "dir/lol.txt"
os.chdir(wc_path)

def svn(args: list):
    if not "svn" in args:
        args.insert(0, "svn")
    use_xml = "--xml" in args
    proc = run(args, check=False, stdout=PIPE, stderr=PIPE)
    try:
        proc.check_returncode()
    except CalledProcessError as exc:
        print(proc.stderr.decode("utf-8"))
        raise exc
    output = proc.stdout.decode("utf-8")
    if use_xml:
        return ElementTree.fromstring(output)
    else:
        return output

async def svn_async(args: list):
    if "svn" in args:
        args.remove("svn")
    use_xml = "--xml" in args
    proc = await asyncio.create_subprocess_exec(
        "svn",
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    print(f'{datetime.now()}: [PID {proc.pid}, Started {args!r}]')
    stdout, stderr = await proc.communicate()
    stdout = stdout.decode("utf-8")
    stderr = stderr.decode("utf-8")
    print(f'{datetime.now()}: [PID {proc.pid}, {args!r} exited with {proc.returncode}]')
    if proc.returncode != 0:
        print(stderr)
    if use_xml:
        return ElementTree.fromstring(stdout)
    else:
        return stdout

def parse_revisions(xml_data):
    revisions = []
    for logentry in xml_data.findall(".//logentry"):
        revision_number = int(logentry.attrib["revision"])
        author = logentry.find("author").text
        date = datetime.strptime(logentry.find("date").text, "%Y-%m-%dT%H:%M:%S.%f%z")
        msg = logentry.find("msg").text
        revision = {
            "revision": revision_number,
            "author": author,
            "date": date,
            "msg": msg,
        }
        revisions.append(revision)
    return revisions

def get_revisions(f_path):
    xml = svn(["log", "--xml", "-rHEAD:1", str(f_path)])
    return parse_revisions(xml)

async def get_revisions_async(f_path):
    xml = await svn_async(["log", "--xml", "-rHEAD:1", str(f_path)])
    return parse_revisions(xml)

def parse_contents(files_data, revisions, include_data=True, reg_ex=None):
    contents = []
    for file_data, revision in zip(files_data, revisions):
        print(f">>> {f_path}@REV{revision['revision']}")
        print(file_data)
        content = {
            "file": str(f_path),
            "revision_info": revision,
        }
        if include_data:
            content["data"] = file_data
        if reg_ex is not None:
            if not isinstance(reg_ex, re.Pattern):
                reg_ex = re.compile(reg_ex)
            reg_ex_result = reg_ex.search(file_data)
            if reg_ex_result:
                groups = reg_ex_result.groups()
            else:
                groups = tuple()
            content["groups"] = groups
        contents.append(content)
    return contents

def get_contents(f_path, include_data=True, reg_ex=None):
    revisions = get_revisions(f_path)
    files_data = []
    for revision in revisions:
        files_data.append(svn(["cat", f"-r{revision['revision']}", str(f_path)]))
    return parse_contents(files_data, revisions, include_data, reg_ex)

async def get_contents_async(
        f_path,
        include_data=True,
        reg_ex=None,
        max_subprocesses=10):
    revisions = await get_revisions_async(f_path)
    files_data = []
    for revision_slice in (revisions[i:i+max_subprocesses] for i in range(0, len(revisions), max_subprocesses)):
        proc_list = []
        for revision in revision_slice:
            proc_list.append(
                svn_async(["cat",  f"-r{revision['revision']}", str(f_path)]),
            )
        files_data += await asyncio.gather(*proc_list)
    return parse_contents(files_data, revisions, include_data, reg_ex)

async def main_async():
    contents = await get_contents_async(f_path, include_data=False, reg_ex=r"2022-(.*)")
    pprint(contents)

def main():
    print(os.getcwd())
    ret = svn(["info", "--xml"])
    contents = get_contents(f_path, reg_ex=r"2022-(.*)")
    for content in contents:
        print(content)

#%%
if __name__ == "__main__":
    start = datetime.now()
    # main()
    asyncio.run(main_async())
    end = datetime.now()
    print(f"Required time: {end - start}")
