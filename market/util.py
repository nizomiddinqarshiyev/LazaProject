import os
from dotenv import load_dotenv

load_dotenv()
STEP = int(os.environ.get('STEP'))


def first_step(card_numbers: str):
    card_numbers = ''.join(str((int(x) + STEP) % 10) for x in card_numbers)
    return card_numbers


def second_step(card_numbers: str):
    letters = 'JABCDEFGHI'
    card_numbers = first_step(card_numbers)
    hashed_cards = []
    for i in range(len(card_numbers)):
        hashed_cards.append(letters[int(card_numbers[i])])
    return ''.join(hashed_cards)

def third_step(card_numbers: str):
    card_numbers = second_step(card_numbers)
    thrice_hashed = ''
    for i in card_numbers:
        thrice_hashed += str(ord(i))
    return thrice_hashed[::-1]

def decode_card_number(card_numbers: str):
    card_numbers = card_numbers[::-1]
    card_partition = [card_numbers[i]+card_numbers[i+1] for i in range(0, len(card_numbers)-1, 2)]
    numbers = ''
    for x in card_partition:
        n = int(x) - 64 - STEP
        if n < 0:
            n += 10
        numbers += str(n)
    return numbers


def collect_to_list(card_datas):
    cards_info = []
    for element in card_datas:
        id = element.id
        card_numbers = decode_card_number(element.card_number)
        card_expirations = element.card_expiration
        result = {
            'id': id,
            'card_number': card_numbers[:4] + '*'*8 + card_numbers[-4:],
            'card_expiration': card_expirations}
        cards_info.append(result)
    return cards_info