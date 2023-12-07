MODEL_PATH = "/path/to/alpaca/"
ITEMPATH = "../inventories/mpi_120.csv"
TEST_TYPE = None
SCORES = {
    "A": 5,
    "B": 4,
    "C": 3,
    "D": 2,
    "E": 1,
}

template = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
Given a statement of you. Please choose from the following options to identify how accurately this statement describes you.

### Input:
Statement: "You {}."

Options:
(A). Very Accurate
(B). Moderately Accurate
(C). Neither Accurate Nor Inaccurate
(D). Moderately Inaccurate
(E). Very Inaccurate

### Response:
"""


global_result = {}
global_cnt = {}

import pandas as pd
import torch
import numpy as np
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM
import re
from pprint import pprint

device = torch.device("cuda:0") if torch.cuda.is_available() else "cpu"
global_result = {}
global_cnt = {}


def getItems(filename=ITEMPATH, item_type=None):
    data = pd.read_csv(filename)
    if item_type is not None:
        items = data[data["instrument"] == item_type]
    else:
        items = data
    return items


def loadModel(pretrained_model=MODEL_PATH):
    tokenizer = AutoTokenizer.from_pretrained(pretrained_model)
    model = AutoModelForCausalLM.from_pretrained(pretrained_model).half().to(device)
    return tokenizer, model


def generateAnswer(tokenizer, model, dataset, template, scores=SCORES):
    global_result = {}
    global_cnt = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0, "UNK": 0}
    for _, item in dataset.iterrows():
        question = item["text"].lower()
        prompt = template.format(question)
        inputs = tokenizer.encode(prompt, return_tensors="pt").to(device)
        outputs = model.generate(
            inputs,
            temperature=0.0,
            max_new_tokens=20,
            top_p=0.95,
            # top_k=0,
        )
        output_text = tokenizer.decode(outputs[0])

        answer = output_text.split("\n")[-1]
        print(answer)
        label = item["label_ocean"]
        key = item["key"]
        parsed_result = re.search(r"[abcdeABCDE][^a-zA-Z]", answer[:6], flags=0)
        if parsed_result:
            parsed_result = parsed_result.group()[0].upper()

            score = scores[parsed_result]
            if label not in global_result:
                global_result[label] = []

            global_cnt[parsed_result] += 1
            if key == 1:
                global_result[label].append(score)
            else:
                global_result[label].append(6 - score)
        else:
            global_cnt["UNK"] += 1

    return global_result, global_cnt


def calc_mean_and_var(result):
    mean = {}
    std = {}
    for key, item in result.items():
        mean[key] = np.mean(np.array(item))
        std[key] = np.std(np.array(item))

    return {
        "mean": list(sorted(mean.items(), key=lambda item: item[0])),
        "std": list(sorted(std.items(), key=lambda item: item[0])),
    }


def main():
    tokenizer, model = loadModel()
    dataset = getItems(ITEMPATH, TEST_TYPE)
    print("-" * 40)
    print(f"Current Prompt: {template}")

    result, count = generateAnswer(tokenizer, model, dataset, template)

    mean_var = calc_mean_and_var(result)
    pprint(result)
    pprint(count)
    pprint(mean_var)


if __name__ == "__main__":
    main()
