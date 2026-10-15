"""Route a support inquiry to one team category.

Rules run first and need no network. A model is asked only when the rules
do not recognize the text. If that call fails, the rules result is kept.
"""

import json
import re
import sys

CATEGORIES = {
    "technical_problem": "Технически проблем",
    "access_or_registration": "Достъп или регистрация",
    "learning_content": "Учебно съдържание",
    "other": "Друго",
}

# Checked in this order. A loading failure stays technical even when the
# sentence also names a lesson.
RULES = {
    "technical_problem": (
        "не се зарежда",
        "не ми зарежда",
        "не зарежда",
        "не работи",
        "не ми работи",
        "грешка",
        "срив",
    ),
    "access_or_registration": (
        "логна",
        "логвам",
        "вляза",
        "влиз",
        "влез",
        "парол",
        "профил",
        "имейл",
        "регистрац",
    ),
    "learning_content": (
        "упражнен",
        "урок",
        "клас",
        "материал",
    ),
}


class ModelUnavailable(Exception):
    """The external classifier could not be reached."""


def mock_model(text):
    """Stand-in for an external model. Makes no network call."""
    return "other"


def _rules_category(text):
    for category, phrases in RULES.items():
        if any(phrase in text for phrase in phrases):
            return category
    return "other"


def classify(text, model=mock_model):
    """Classify one inquiry.

    Returns a dict ready for json.dumps. Invalid input sets ok to false
    and does not call the model.
    """
    if not isinstance(text, str):
        return _error("Запитването трябва да е текст.")

    cleaned = text.strip().lower() #remove spaces and make lowercase
    if not cleaned: #if the inquiry is empty, return an error
        return _error("Текстът на запитването е празен.")
    if re.search(r"[^\W_]", cleaned, flags=re.UNICODE) is None: #if the inquiry does not contain words, return an error
        return _error("Запитването не съдържа думи.")

    category = _rules_category(cleaned)
    method = "rules"
    if category == "other" and model is not None: #if the inquiry is not categorized by the rules, try to classify it with the model
        try:
            suggested = model(cleaned)
        except Exception:
            suggested = None
        else:
            method = "model"
        if suggested in CATEGORIES:
            category = suggested

    return {
        "ok": True,
        "category": category,
        "label": CATEGORIES[category],
        "method": method,
    }


def _error(message):
    return {
        "ok": False,
        "category": None,
        "label": None,
        "error": message,
    }


def main(argv): #main function that takes the arguments and prints the results
    if len(argv) > 1: #if there are arguments, print the results for each argument      
        for inquiry in argv[1:]:
            print(json.dumps(classify(inquiry), ensure_ascii=False)) #print the results for each argument
        return 0

    print("Type an inquiry and press Enter. Press Enter on an empty line to stop.") #print the prompt for the user to enter an inquiry
    while True:
        inquiry = input("> ") #take the inquiry from the user
        if not inquiry.strip():
            return 0 #if the inquiry is empty, stop the loop
        print(json.dumps(classify(inquiry), ensure_ascii=False)) 


if __name__ == "__main__":
    sys.exit(main(sys.argv))
