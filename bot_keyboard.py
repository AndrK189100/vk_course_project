from vk_api.keyboard import VkKeyboard, VkKeyboardButton, VkKeyboardColor

class BotKeyboard:
    """
    Класс содержащий различные клавиатуры для диалога с пользователем бота.
    """

    def empty_keyboard(self):
        return VkKeyboard.get_empty_keyboard()

    def cancel_keyboard(self):
        keyboard = VkKeyboard()
        keyboard.add_callback_button('Отмена', color=VkKeyboardColor.NEGATIVE, payload={'text': 'cancel'})
        return keyboard.get_keyboard()

    def cancel_favorite_keyboard(self):
        keyboard = VkKeyboard()
        keyboard.add_callback_button('Отмена', color=VkKeyboardColor.NEGATIVE, payload={'text': 'cancel'})
        keyboard.add_callback_button('Избранное', color=VkKeyboardColor.PRIMARY, payload={'text': 'favorite'})
        return keyboard.get_keyboard()

    def start_keyboard(self):
        keyboard = VkKeyboard()
        keyboard.add_callback_button('Начать', color=VkKeyboardColor.PRIMARY, payload={'text': 'start'})
        return keyboard.get_keyboard()

    def authorize_keyboard(self):
        keyboard = VkKeyboard()
        keyboard.add_callback_button('Отмена', color=VkKeyboardColor.NEGATIVE, payload={'text': 'cancel'})
        keyboard.add_callback_button('Авторизация', color=VkKeyboardColor.POSITIVE, payload={'text': 'authorize'})
        return keyboard.get_keyboard()

    def cancel_proceed_keyboard(self):
        keyboard = VkKeyboard()
        keyboard.add_callback_button('Отмена', color=VkKeyboardColor.NEGATIVE, payload={'text': 'cancel'})
        keyboard.add_callback_button('Продолжить', color=VkKeyboardColor.POSITIVE, payload={'text': 'proceed'})
        return keyboard.get_keyboard()

    def cancel_proceed_favorite_keyboard(self):
        keyboard = VkKeyboard()
        keyboard.add_callback_button('Отмена', color=VkKeyboardColor.NEGATIVE, payload={'text': 'cancel'})
        keyboard.add_callback_button('Продолжить', color=VkKeyboardColor.POSITIVE, payload={'text': 'proceed'})
        keyboard.add_line()
        keyboard.add_callback_button('Избранное', color=VkKeyboardColor.PRIMARY, payload={'text': 'favorite'})
        return keyboard.get_keyboard()

    def cancel_favorite_begin_keyboard(self):
        keyboard = VkKeyboard()
        keyboard.add_callback_button('Отмена', color=VkKeyboardColor.NEGATIVE, payload={'text': 'cancel'})
        keyboard.add_callback_button('Избранное', color=VkKeyboardColor.PRIMARY, payload={'text': 'favorite'})
        keyboard.add_callback_button('Продолжить', color=VkKeyboardColor.POSITIVE, payload={'text': 'begin'})
        return keyboard.get_keyboard()

    def cancel_input_proceed_keyboard(self):
        keyboard = VkKeyboard()
        keyboard.add_callback_button('Отмена', color=VkKeyboardColor.NEGATIVE, payload={'text': 'cancel'})
        keyboard.add_callback_button('Ввести', color=VkKeyboardColor.SECONDARY, payload={'text': 'input'})
        keyboard.add_callback_button('Продолжить', color=VkKeyboardColor.PRIMARY, payload={'text': 'proceed'})
        keyboard.add_line()
        keyboard.add_callback_button('Избранное', color=VkKeyboardColor.PRIMARY, payload={'text': 'favorite'})
        return keyboard.get_keyboard()

    def viewer_keyboard(self):
        keyboard = VkKeyboard()
        keyboard.add_callback_button('<<', VkKeyboardColor.PRIMARY, {'text': '<<'})
        keyboard.add_callback_button('В избранное', VkKeyboardColor.POSITIVE, {'text': '*'})
        keyboard.add_callback_button('>>', VkKeyboardColor.PRIMARY, {'text': '>>'})
        keyboard.add_line()
        keyboard.add_callback_button('Показать избранных', VkKeyboardColor.PRIMARY, {'text': 'favorite'})
        keyboard.add_line()
        keyboard.add_callback_button('Отмена', VkKeyboardColor.NEGATIVE, {'text': 'cancel'})
        return keyboard.get_keyboard()

    def cancel_change_keyboard(self):
        keyboard = VkKeyboard()
        keyboard.add_callback_button('Отмена', color=VkKeyboardColor.NEGATIVE, payload={'text': 'cancel'})
        keyboard.add_callback_button('Изменить', color=VkKeyboardColor.POSITIVE, payload={'text': 'change'})
        return keyboard.get_keyboard()

    def return_viewer_keyboard(self):
        keyboard = VkKeyboard()
        keyboard.add_callback_button('Отмена', color=VkKeyboardColor.NEGATIVE, payload={'text': 'cancel'})
        keyboard.add_callback_button('Назад', color=VkKeyboardColor.POSITIVE, payload={'text': 'back'})
        return keyboard.get_keyboard()
