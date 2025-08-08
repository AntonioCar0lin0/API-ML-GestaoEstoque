Para rodar a aplicação é necessário possuir um arquivo .env contendo as credenciais do banco de dados e a chave de API do Gemini. 
Realizar a criação de um ambiente virtual python -m venv venv 
cd venv 
cd Scripts
activate.bat
pip install -r requirements.txt para baixar as bibiliotecas necessárias
uvicorn app:app --reload --port 8001

