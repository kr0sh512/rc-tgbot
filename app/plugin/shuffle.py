from plugin.user import User, users_reg
from typing import List, Tuple
import random

already_matched: List[Tuple[User, User]] = []


def Shuffle() -> List[Tuple[User, User]]:
    users = users_reg.copy()
    random.shuffle(users)
    pairs = []

    if len(users) % 2 != 0:
        pairs.append((users.pop(), None))

    # Step 1: Match men with women by compatibility and age
    for user in users:
        for potential_match in users:
            if user == potential_match:
                continue
            if (
                user.gender != potential_match.gender
                and potential_match.type in compatibility[user.type]
                and abs(user.age - potential_match.age) <= 5
                and (user, potential_match) not in already_matched
                and (potential_match, user) not in already_matched
            ):
                pairs.append((user, potential_match))
                users.remove(user)
                users.remove(potential_match)
                break

    # Step 2: Match men with women with compatibility
    for user in users:
        for potential_match in users:
            if user == potential_match:
                continue
            if (
                user.gender != potential_match.gender
                and potential_match.type in compatibility[user.type]
                and (user, potential_match) not in already_matched
                and (potential_match, user) not in already_matched
            ):
                pairs.append((user, potential_match))
                users.remove(user)
                users.remove(potential_match)
                break

    # Step 3: Match men with women
    for user in users:
        for potential_match in users:
            if user == potential_match:
                continue
            if (
                user.gender != potential_match.gender
                and (user, potential_match) not in already_matched
                and (potential_match, user) not in already_matched
            ):
                pairs.append((user, potential_match))
                users.remove(user)
                users.remove(potential_match)
                break

    # Step 4: Match people of the same age
    for user in users:
        for potential_match in users:
            if user == potential_match:
                continue
            if (
                user.age == potential_match.age
                and (user, potential_match) not in already_matched
                and (potential_match, user) not in already_matched
            ):
                pairs.append((user, potential_match))
                users.remove(user)
                users.remove(potential_match)
                break

    # Step 5: Pair all remaining users
    while len(users) > 1:
        pairs.append((users.pop(), users.pop()))

    already_matched.extend(pairs)

    return pairs


compatibility = {
    "INTJ": (
        "ENFP",
        "ENTP",
    ),
    "INTP": (
        "ENTJ",
        "ESTJ",
    ),
    "INFJ": (
        "ENFP",
        "ENTP",
    ),
    "INFP": (
        "ENFJ",
        "ENTJ",
    ),
    "ISTJ": (
        "ESFP",
        "ESTP",
    ),
    "ISTP": (
        "ESFJ",
        "ESTJ",
    ),
    "ISFJ": (
        "ESFP",
        "ESTP",
    ),
    "ISFP": (
        "ENFJ",
        "ESFJ",
        "ESTJ",
    ),
    "ENTJ": (
        "INFP",
        "INTP",
    ),
    "ENTP": (
        "INTJ",
        "ENTP",
    ),
    "ENFJ": (
        "INFP",
        "ISFP",
        "ENFJ",
    ),
    "ENFP": (
        "INFJ",
        "INTJ",
    ),
    "ESTJ": (
        "ISFP",
        "ISTP",
    ),
    "ESTP": (
        "ISFJ",
        "ISTJ",
    ),
    "ESFJ": (
        "ISFP",
        "ISTP",
    ),
    "ESFP": (
        "ISTJ",
        "ISFJ",
    ),
}
