
sex = {
    1: 'женский',
    2: 'мужской',
    0: 'какой-то гендер из 39'
}

class DialogMsg:
    """
    Класс содержащий ответы бота для диалога с пользователем бота.
    """
    def begin(*args):
        return f'Привет {args[0]}. Для Продолжения необходимо авторизоваться\n'

    def authorized_begin(*args):
        return f'{args[0]}, Я тебя узнал. Просто нажми "Продолжить"'

    def wrong_input(*args):
        return 'Неверный ввод, попробуй еще раз.'

    def cancel(*args):
        return 'Пока'

    def pre_authorize(*args):
        return 'Нажми продолжить.'


    def authorize(*args):
        return 'Авторизация прошла успешно.'

    def authorize_wrong(*args):
        return 'Авторизация не удалась. Пока.'

    def cancel_start(*args):
        return f'Я определил, вероятную область поиска, как {args[0]}, {args[1]}. ' \
               f'Будем искать здесь или введешь данные вручную?'

    def not_city(*args):
        return 'У тебя в контактах не указано место жительства. Не могу определить область поиска.\n' \
               'Необходимо ввести данные вручную...\n\n' \
               'Отправь название страны.'

    def select_city_input_method(*args):
        return 'Хорошо, будем искать по месту жительства.\n\n' \
               '!ВНИМАНИЕ!, есть некоторые ограничения\n' \
               'Минимальный возраст объекта 16 лет. Максимальный 90 лет.\n' \
               'Максимальная разница между минимальным и максимальным возрастом 10 лет.\n\n' \
               'Введи минимальный возраст объекта'

    def select_city_input_method_2(*args):
        return 'Отправь название страны или нажми отмена для завершения диалога.'

    def get_country(*args):
        return 'Теперь отправь название населенного пункта'

    def get_country_2(*args):
        return 'Такую страну я не нашел. Попробуй еще раз.'

    def get_city(*args):
        return 'Такой город я не нашел. Попробуй еще раз.'

    def get_city_2(*args):
        return 'Слишком много результатов поиска. Попробуй еще раз.'

    def get_city_3(*args):
        return 'Теперь отправь номер города из списка.'

    def get_city_4(*args):
        msg = ''

        for i, arg in enumerate(args[0], start=1):
            msg += (f'{i}. {arg["title"]}')
            if 'area' in arg:
                msg += f' {arg["area"]}'
            if 'region' in arg:
                msg += f' {arg["region"]}'
            msg += '\n\n'

        return msg


    def select_city(*args):
        return 'Я получил всю необходимую информацию об ариале обитания объекта поиска.\n' \
               'Теперь необходимо ввести ТТХ непосредственно объекта\n\n' \
               '!ВНИМАНИЕ!, есть некоторые ограничения\n' \
               'Минимальный возраст объекта 16 лет. Максимальный 90 лет.\n' \
               'Максимальная разница между минимальным и максимальным возрастом 10 лет.'

    def select_city_2(*args):
        return 'Отправь минимальный возраст объекта.'

    def get_age_from(*args):
        return 'Отправь максимальный возраст.'

    def get_age_to(*args):
        return 'Теперь отправь пол объекта поиска в виде цифры.\n' \
               '1. Женский\n' \
               '2. Мужской\n' \
               '0. Я широкого профиля'

    def get_age_to_2(*args):
        return 'Слишком большая разница между минимальным и максимальным возрастом объекта\n\n' \
               'Попробуй еще раз\n' \
               'Отправь минимальный возраст объекта'

    def get_sex(*args):
        return f'Вся необходимая информация по целевому объекту получена\n\n' \
               f'Итак:\n' \
               f'Ареал обитания: {args[0]}\n' \
               f'Пол: {sex.get(args[1])}\n' \
               f'Возраст от {args[2]} до {args[3]}'

    def one_moment(*args):
        return 'Минуту....'

    def list_unstruction(*args):
        return 'Кнопки со стрелками позволяют двигаться по найденым объектам вперед и назад\n' \
               'Конопка "В избранное" добавляет объект в список избранных'

    def searh_output(*args):
        return f'{args[0]} {args[1]}\n' \
               f'Страница: {args[2]}'

    def begin_of_list(*args):
        return 'Список в самом начале, больше назад двигаться нельзя...'

    def added(*args):
        return 'Добавил.'

    def bot_broken(*args):
        return 'Я сломался. Работать не могу'

    def not_found_users(*args):
        return 'Я ничего не нашел. Измени параметры поиска.'

    def end_of_list(*args):
        return 'Больше ничего нет...'

    def empty(*args):
        return 'Тут пока ничего нет.'

    def favorite(*args):
        return 'САМЫЕ-САМЫЕ'
    def favorite_end(*args):
        return 'Больше в избранном ничего нет('
