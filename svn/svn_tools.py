#%%
import os
import re
from datetime import datetime
from pathlib import Path
from subprocess import run, PIPE, CalledProcessError
from xml.etree import ElementTree

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
        print(output)
        return ElementTree.fromstring(output)
    else:
        return output

def get_revisions(f_path):
    xml = svn(["log", "--xml", "-rHEAD:1", str(f_path)])
    revisions = []
    for logentry in xml.findall(".//logentry"):
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

def get_contents(f_path, include_data=True, reg_ex=None):
    revisions = get_revisions(f_path)
    contents = []
    for revision in revisions:
        r = f"-r{revision['revision']}"
        print(f">>> {f_path}@{r}")
        file_data = svn(["cat", r, str(f_path)])
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

#%%
if __name__ == "__main__":
    print(os.getcwd())
    # ret = svn(["info", "--xml"])
    # contents = get_contents(f_path, reg_ex=re.compile(r"2022-(.*)"))
    contents = get_contents(f_path, reg_ex=r"2022-(.*)")
    for content in contents:
        print(content)