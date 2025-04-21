import os

import ujson
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


class QueryData(BaseModel):
    user_name: str
    data_source: str
    progress_no: int


class SaveData(QueryData):
    data: dict


app = FastAPI()

# 静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")


# 首页
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    with open("static/index.html") as f:
        html = f.read()
    return html


# 后端API接口
@app.post('/query-data')
async def query_data(query: QueryData):
    # print(query.user_name)
    source_dir = f'./unlabeled_data/{query.data_source}'
    target_dir = f'./labeled_data/{query.data_source}/{query.user_name}'
    os.makedirs(target_dir, exist_ok=True)
    labeled_files = os.listdir(target_dir)
    all_files = os.listdir(source_dir)

    labeled_files = [int(el.split('.')[0]) for el in labeled_files]
    labeled_files = sorted(labeled_files)
    all_files = [int(el.split('.')[0]) for el in all_files]
    all_files = sorted(all_files)
    if len(labeled_files) == len(all_files):
        return {
            'responseCode': 200,
            'data': {'text': 'finished'}
        }
    if query.progress_no == 0:
        for element in all_files:
            if element not in labeled_files:
                break
        
        current_idx = element
        with open(f'{source_dir}/{current_idx}.json', 'r', encoding='utf-8') as f:
            data = ujson.load(f)
        assert current_idx == data['idx']
    else:
        if query.progress_no not in labeled_files:
            with open(f'{source_dir}/{query.progress_no}.json', 'r', encoding='utf-8') as f:
                data = ujson.load(f)
            assert query.progress_no == data['idx']
        else:
            finished_idx = labeled_files[-1]
            current_idx = finished_idx + 1
            with open(f'{source_dir}/{current_idx}.json', 'r', encoding='utf-8') as f:
                data = ujson.load(f)
            assert current_idx == data['idx']

    return {
        'responseCode': 200,
        'data': data
    }


@app.post('/save-data')
async def save_data(query: SaveData):
    target_dir = f'./labeled_data/{query.data_source}/{query.user_name}'
    idx = query.data['idx']
    
    with open(f'{target_dir}/{idx}.json', 'w',
              encoding='utf-8') as f:
        ujson.dump(query.data, f, ensure_ascii=False, indent=2)

    return {'responseCode': 200, 'responseMsg': 'File Successfully Saved'}


if __name__ == '__main__':
    import uvicorn

    # 生产环境，请启用0.0.0.0
    # nohup python -u annotation.py > annotation.log &
    # uvicorn.run(app, host='0.0.0.0', port=8000)
    # 测试环境使用，并在index中修改调用URL
    uvicorn.run(app, host='127.0.0.1', port=8000)
    
