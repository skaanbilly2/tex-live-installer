import json


def extract(f):
    packages = []
    state = {}
    for line in f:
        if line == " /n":
            state = {}
            continue
        if line[0] == " ":
            continue

        words = line.strip().split(" ")
        tag = words[0]

        if tag == "name":
            if state.get("category", None) == "Package" and state != {}:
                packages.append(state)
            state = {}
            state["name"] = words[1]
        elif tag == "category":
            cat = words[1]
            if cat == "Package":
                state["category"] = "Package"
            else:
                state = {}
        elif tag == "revision":
            state["revision"] = words[1]
        elif tag.endswith("containerchecksum") or tag.endswith("containersize"):
            state[tag] = words[1]

    return packages


def main():
    with open("texlive.tlpdb.txt", encoding="utf-8") as f:
        packages = extract(f)
        with open("input.json", "w") as f:
            json.dump(packages, f)


if __name__ == "__main__":
    main()
