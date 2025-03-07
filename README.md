"# findex_vis" 




python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

fastapi dev main.py
http://127.0.0.1:8000/docs


#run app
uvicorn app.main:app --reload
pytest app/test.py

#run docker
docker-compose up -d --build
docker-compose exec app pytest test/test.py
docker-compose exec db psql --username=fastapi --dbname=fastapi_dev
http://127.0.0.1:8000/docs

#after done with venv
deactivate
rmdir /s /q venv #to delete venv after use