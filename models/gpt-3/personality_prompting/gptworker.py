import openai
import pandas as pd
import pickle
from tqdm import tqdm
import os

openai.api_key = os.environ["OPENAI_API_KEY"]

ITEMPATH = "../../../inventories/mpi_120.csv"
TEST_TYPE = None
LABEL_TYPE = None


def getItems(filename=ITEMPATH, item_type=None, label_type=LABEL_TYPE):
    data = pd.read_csv(filename)
    if label_type is not None:
        items = data[data["label_ocean"] == label_type]
    else:
        items = data
    return items


template = """Truth:
{prompt}

Question:
Given a statement of you: "You {item}."
Please choose from the following options to identify how accurately this statement describes you.
Options:
(A). Very Accurate
(B). Moderately Accurate
(C). Neither Accurate Nor Inaccurate
(D). Moderately Inaccurate
(E). Very Inaccurate

Answer:"""


def gpt3inventories(prompt, dim, aux):
    dataset = getItems(ITEMPATH, TEST_TYPE)
    # batchify request
    batch_size = 20
    result = []
    for i in tqdm(range(0, len(dataset), batch_size)):
        batch = dataset[i : i + batch_size]
        questions = [
            template.format(prompt=prompt, item=item["text"].lower())
            for _, item in batch.iterrows()
        ]
        responses = openai.Completion.create(
            engine="text-davinci-003",
            prompt=questions,
            temperature=0.0,
            max_tokens=100,
            top_p=0.95,
        )
        for j, response in enumerate(responses["choices"]):
            result.append((batch.iloc[j], questions[j], response))

    filename = f"GPT_3_MPI_{dim}_{aux}.pickle"
    with open(filename, "wb+") as f:
        pickle.dump(result, f)
