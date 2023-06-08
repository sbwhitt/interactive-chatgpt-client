from subprocess import call

def run(raw: str):
    script = raw.split("```")[1]
    s = script.split("python")
    if len(s) > 1: script = s[1]
    with open("./scripts/script.py", "w") as fin:
        fin.write(script)
    fin.close()
    call(["python", "./scripts/script.py"])
