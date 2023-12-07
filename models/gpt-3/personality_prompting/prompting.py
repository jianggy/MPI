import openai
from gptworker import gpt3inventories
from consts import (
    vignettes,
    trait_words,
    p2_descriptions,
    p2_descriptions_reversed,
    trait_words_reversed,
    naive_prompt,
    trait_words_searched,
    trait_words_searched_reverse,
)
import os
import json

openai.api_key = os.environ["OPENAI_API_KEY"]


def get_p2_descriptions():
    words_template = """Given some key words of {trait} person: {d1}, {d2}, {d3}, {d4}, {d5}, and {d6}. A second-person view of {trait} person:"""
    t = 0.0

    descriptions = {}

    for trait, words in trait_words.items():
        d1, d2, d3, d4, d5, d6 = words
        result = words_template.format(
            trait=trait, d1=d1, d2=d2, d3=d3, d4=d4, d5=d5, d6=d6
        )
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=result,
            temperature=t,
            max_tokens=400,
            top_p=1.0,
        )
        descriptions[trait] = response["choices"][0]["text"]
    return descriptions


def get_p2_descriptions_negative():
    words_template = """Given some key words of {trait} person: {d1}, {d2}, {d3}, {d4}, {d5}, and {d6}. A second-person view of {trait} person:"""
    t = 0.0

    descriptions = {}

    for trait, words in trait_words_reversed.items():
        d1, d2, d3, d4, d5, d6 = words
        result = words_template.format(
            trait=trait, d1=d1, d2=d2, d3=d3, d4=d4, d5=d5, d6=d6
        )
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=result,
            temperature=t,
            max_tokens=400,
            top_p=1.0,
        )
        descriptions[trait] = response["choices"][0]["text"]
    return descriptions


def get_inventory_result(prompts, aux=""):
    for trait, prompt in prompts.items():
        print(trait)
        gpt3inventories(prompt, trait, aux)


def vignette_test_words(save_path="vignettes_auto.json"):
    save = {}
    words_prompt = dict(
        (k, f"You have the traits of {', '.join(v)}.")
        for k, v in trait_words_searched.items()
    )
    words_prompt_reversed = dict(
        (k, f"You have the traits of {', '.join(v)}.")
        for k, v in trait_words_searched_reverse.items()
    )

    vignette_template = """Context: {prompt}
Premise: {question}
Q: Describe how you would feel and what you would do in the situation.
A:"""

    vignette_template_neutral = """Premise: {question}
Q: Describe how you would feel and what you would do in the situation.
A:"""
    t = 0.7

    save["neutral"] = {}
    for trait, question in vignettes.items():
        prompt = vignette_template_neutral.format(question=question)
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=t,
            max_tokens=400,
            top_p=0.95,
            n=50,
        )
        save["neutral"][trait] = response

    save["positive"] = {}
    for trait, question in vignettes.items():
        prompt = vignette_template.format(prompt=words_prompt[trait], question=question)
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=t,
            max_tokens=400,
            top_p=0.95,
            n=50,
        )
        save["positive"][trait] = response

    save["negative"] = {}
    for trait, question in vignettes.items():
        prompt = vignette_template.format(
            prompt=words_prompt_reversed[trait], question=question
        )
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=t,
            max_tokens=400,
            top_p=0.95,
            n=50,
        )
        save["negative"][trait] = response

    with open(save_path, "w") as f:
        json.dump(save, f)


def vignette_test_p2(save_path="vignettes_p2.json"):
    save = {}

    vignette_template = """Context: {prompt}
Premise: {question}
Q: Describe how you would feel and what you would do in the situation.
A:"""

    vignette_template_neutral = """Premise: {question}
Q: Describe how you would feel and what you would do in the situation.
A:"""
    t = 0.7

    save["neutral"] = {}
    for trait, question in vignettes.items():
        prompt = vignette_template_neutral.format(question=question)
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=t,
            max_tokens=400,
            top_p=0.95,
            n=50,
        )
        save["neutral"][trait] = response

    save["positive"] = {}
    for trait, question in vignettes.items():
        prompt = vignette_template.format(
            prompt=p2_descriptions[trait], question=question
        )
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=t,
            max_tokens=400,
            top_p=0.95,
            n=50,
        )
        save["positive"][trait] = response

    save["negative"] = {}
    for trait, question in vignettes.items():
        prompt = vignette_template.format(
            prompt=p2_descriptions_reversed[trait], question=question
        )
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=t,
            max_tokens=400,
            top_p=0.95,
            n=50,
        )
        save["negative"][trait] = response

    with open(save_path, "w") as f:
        json.dump(save, f)


def get_opposite():
    for dim, words in trait_words.items():
        for word in words:
            result = f"Antonyms of {word} is:"
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=result,
                temperature=0,
                max_tokens=400,
                top_p=1.0,
            )
            print(result, response["choices"][0]["text"])


def words_prompt(trait_words_searched):
    return dict(
        (k, f"You have the traits of {', '.join(v)}.")
        for k, v in trait_words_searched.items()
    )


if __name__ == "__main__":
    get_inventory_result(naive_prompt, 'naive')  # naive prompting
    get_inventory_result(words_prompt(trait_words_searched), 'auto'))  # words auto prompting
    vignette_test_words(save_path="path-to-save.json")  # vignette test for words
    get_inventory_result(p2_descriptions, 'p2')  # P^2 prompting
    vignette_test_p2(save_path="path-to-save.json")  # vignette test for P^2
    
    # print(get_p2_descriptions()) # generate P^2 prompts from scratch
