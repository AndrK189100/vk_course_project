from fastapi import FastAPI
import uvicorn

app = FastAPI()
code_buffer = {}

@app.get(path='/send_code/')
async def root(code: str, state: str):
    """
    Функция обработки GET запроса от Вконтакте для OAUTH авторизации.

    :param code: OAUTH код.
    :param state: Идентификатор пользователя бота.
    :return: Страницу можно закрыть.
    :rtype: str
    """
    if state in code_buffer:
        code_buffer.update({state: code})
    else:
        code_buffer[state] = code
    return 'Страницу можно закрыть....'


@app.get(path='/user_code/')
async def get_code(user_id: str):
    """
    Функция обработки GET запроса бота для получения кода OAUTH авторизации.

    :param user_id: Идентификатор пользователя.
    :return: Код для OAUTH авторизации.
    :rtype: str
    """
    if user_id in code_buffer:
        return code_buffer.pop(user_id)
    else:
        return False


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0')
