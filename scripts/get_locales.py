import os
import json
import subprocess

PTH = "src/locales"

def load_json(json_path):

    try:
        with open(json_path, "r", encoding="utf-8") as json_file:
            return json.load(json_file)
        
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{json_path}' was not found.")


def update_locales() -> None:

    src = load_json(f"{PTH}/src.json")

    res: dict[str , str] = {"ru": [], "en": []}

    for key, value in src.items():

        for _, code in res.items():
            code.append(f"# {key}")

        for k, v in value.items():
            for lang_code, data in v.items():
                formatted_data = data.replace('\n', '\n    ')
                res[lang_code].append(f"{key.split('_')[1]}-{k} = {formatted_data}")

        for lc in list(res.keys()):
            res[lc].append("\n")

    
    for k, v in res.items():
        pth_to_loc = f"{PTH}/{k}"
        if not os.path.exists(pth_to_loc):
            os.makedirs(pth_to_loc)

        with open(f"{pth_to_loc}/txt.ftl", 'w') as file:
            file.write("\n".join(v))


if __name__ == "__main__":

    update_locales()
    subprocess.run(["fluentogram", "-f", "src/locales/ru/txt.ftl", "-o", "src/locales/stub.pyi"])
    print("Locales has been updated")

    # i18n -ftl src/locales/en/txt.ftl -stub src/locales/stub.pyi