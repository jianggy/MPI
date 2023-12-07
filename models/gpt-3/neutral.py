import openai
import pandas as pd
import pickle
import os

openai.api_key = os.environ["OPENAI_API_KEY"]

ITEMPATH = "../../inventories/mpi_120.csv"
TEST_TYPE = None
LABEL_TYPE = None

def getItems(filename=ITEMPATH, item_type=None, label_type=LABEL_TYPE):
    data = pd.read_csv(filename)
    if label_type is not None:
        items = data[data["label_ocean"] == label_type]
    else:
        items = data
    return items


template = """Question:
Given a statement of you: "You {}."
Please choose from the following options to identify how accurately this statement describes you.
Options:
(A). Very Accurate
(B). Moderately Accurate
(C). Neither Accurate Nor Inaccurate
(D). Moderately Inaccurate
(E). Very Inaccurate

Answer:"""

import time

dataset = getItems(ITEMPATH, TEST_TYPE)

for temperature in [0]:
    # batchify request
    batch_size = 20
    result = []
    for i in range(0, len(dataset), batch_size):
        batch = dataset[i : i + batch_size]
        questions = [
            template.format(item["text"].lower()) for _, item in batch.iterrows()
        ]
        responses = openai.Completion.create(
            engine="text-davinci-003",
            prompt=questions,
            temperature=temperature,
            max_tokens=400,
            top_p=0.95,
        )
        for j, response in enumerate(responses["choices"]):
            result.append((batch.iloc[j], questions[j], response))
            print(response["text"], batch.iloc[j]["label_ocean"])

    with open(f"path-to-save.pickle", "wb+") as f:
        pickle.dump(result, f)
