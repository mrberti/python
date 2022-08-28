#%%
import os
import re
import asyncio
import argparse
import hashlib
from datetime import datetime
from pathlib import Path
from subprocess import run, PIPE, CalledProcessError
from xml.etree import ElementTree

from pprint import pprint

datetime_format = "%Y-%m-%dT%H:%M:%S.%f%z"
hash_type = "sha256"

wc_path_default = "/home/simon/svn/test"
f_path_default = "dir/lol.txt"

parser = argparse.ArgumentParser(description="Some SVN tools")
parser.add_argument(
    "-w",
    help="Path to working copy",
    default=wc_path_default,
)
parser.add_argument(
    "-f",
    help="File",
    default=f_path_default,
)
parser.add_argument(
    "-r",
    help="Regular expresstion",
    default=r"",
)
parser.add_argument(
    "-i",
    help="Include doc contents",
    action="store_true",
)

args = parser.parse_known_args()[0]
REG_EX = re.compile(args.r)
INCLUDE_CONTENT = args.i
print(args)

wc_path = Path(args.w)
f_path = wc_path / args.f
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
        # print(stderr)
        raise Exception(stderr)
    if use_xml:
        return ElementTree.fromstring(stdout)
    else:
        return stdout

def parse_revisions(xml_data):
    revisions = []
    for logentry in xml_data.findall(".//logentry"):
        revision_number = int(logentry.attrib["revision"])
        author = logentry.find("author").text
        date = datetime.strptime(logentry.find("date").text, datetime_format)
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
            hash_val = hashlib.new(hash_type, file_data.encode("utf-8")).hexdigest()
            content["data"] = file_data
            content["hash"] = f"{hash_type}+{hash_val}"
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

def get_files(repo=None, dirs_only=False):
    """Creates a list of dicts, containing the complete repository
    structure, including commit information, like author, revision and
    date.

    If `dirs_only == True`, only directories are returned.
    """
    if repo is None: repo = "."
    dir_xml = svn(["ls", "--depth", "infinity", "--xml", str(repo)])
    if dirs_only:
        entries = dir_xml.findall(".//entry[@kind='dir']")
    else:
        entries = dir_xml.findall(".//entry")
    dirs = []
    for entry in entries:
        name = entry.findtext("name")
        kind = entry.attrib["kind"]
        if kind == "dir":
            name += "/"
        revision = int(entry.find("commit").attrib["revision"])
        author = entry.findtext("commit/author")
        date = datetime.strptime(entry.findtext("commit/date"), datetime_format)
        data = {
            "name": name,
            "kind": kind,
            "revision": revision,
            "author": author,
            "date": date,
        }
        dirs.append(data)
    return dirs

def get_files_simple(repo=None, revision=None, dirs_only=False):
    """Returns a simple list which contains all filenames inside the
    repository.

    If `dirs_only == True`, only directories are returned."""
    if repo is None: repo = "."
    if revision is None: revision = "HEAD"
    dirs = svn(["ls", "--depth", "infinity", str(repo), f"-r{revision}"])
    if dirs_only:
        # Directories end with a '/'
        exp = r"(.+\/)$"
    else:
        exp = r"(.+)$"
    x = re.findall(exp, dirs, re.MULTILINE)
    return(x)

async def main_async():
    contents = await get_contents_async(f_path, include_data=INCLUDE_CONTENT, reg_ex=REG_EX)
    pprint(contents)

def main():
    print(os.getcwd())
    # ret = svn(["info", "--xml"])
    contents = get_contents(f_path, include_data=INCLUDE_CONTENT, reg_ex=REG_EX)
    for content in contents:
        print(content)
    # pprint(get_files_simple(dirs_only=False))
    # pprint(get_files(dirs_only=False))

#%%
if __name__ == "__main__":
    start = datetime.now()
    # main()
    asyncio.run(main_async())
    end = datetime.now()
    print(f"Required time: {end - start}")
