from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Carrega o .env
load_dotenv()

# Usa DATABASE_URL se estiver definida, senão monta a partir das variáveis separadas
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DB_DIALECT = os.getenv("DB_DIALECT", "postgresql")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME")

    if not all([DB_USER, DB_PASSWORD, DB_NAME]):
        raise ValueError("❌ Variáveis de banco de dados ausentes no .env!")

    # Adiciona sslmode=require no final da string
    DATABASE_URL = (
        f"{DB_DIALECT}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
    )

# Cria o engine com a URL final
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
