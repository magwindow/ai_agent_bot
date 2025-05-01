from content import cards
from data_storage import user_test_states, user_states, user_card_messages
from keyboards.reply_keyboard import keyboard
from tests import tests


async def send_next_test_question(user_id, message):
    state = user_test_states[user_id]
    test = tests[user_states[user_id]]

    if state["index"] < len(test):
        q = test[state["index"]]
        options = "\n".join([f"{i + 1}. {opt}" for i, opt in enumerate(q["options"])])
        await message.answer(f"{q['question']}\n\n{options}")
    else:
        total = len(test)
        score = state["score"]
        await message.answer(f"✅ Тест завершён!\nРезультат: {score} из {total}")

        # Продолжим обучение с нужной карточки
        next_index = user_test_states[user_id]["next_card_index"]

        msg = await message.answer(cards[next_index], reply_markup=keyboard)
        user_states[user_id] = next_index + 1

        # Добавим в список сообщений карточек
        user_card_messages.setdefault(user_id, []).append(msg.message_id)

        # Удаляем состояние теста
        del user_test_states[user_id]
