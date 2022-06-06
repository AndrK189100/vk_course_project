from fastapi import FastAPI
import uvicorn


app = FastAPI()
code_buffer = {}
@app.get(path='/')
async def root(code: str, state: str):
    if state in code_buffer:
        code_buffer.update({state: code})
    else:
        code_buffer[state] = code
    return 'Страницу можно закрыть....'
@app.get(path='/user_code/')
async def get_code(user_id: str):
    if user_id in code_buffer:
        return code_buffer.pop(user_id)
    else:
        return False



if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0')
