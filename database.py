from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import DisconnectionError, OperationalError
from sqlalchemy.pool import Pool
import os
import logging
from dotenv import load_dotenv
from contextlib import contextmanager
import time

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carrega o .env
load_dotenv()

# Configuração da URL do banco
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
    
    DATABASE_URL = (
        f"{DB_DIALECT}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        "?sslmode=require&connect_timeout=30"
    )

# Configurações otimizadas para Render
ENGINE_CONFIG = {
    # Pool de conexões otimizado
    'pool_size': 5,           # Número base de conexões
    'max_overflow': 10,       # Conexões extras quando necessário
    'pool_timeout': 30,       # Timeout para obter conexão do pool
    'pool_recycle': 3600,     # Recicla conexões a cada 1 hora
    'pool_pre_ping': True,    # Testa conexões antes de usar
    
    # Configurações de reconexão
    'connect_args': {
        'sslmode': 'require',
        'connect_timeout': 30,
        'keepalives': 1,
        'keepalives_idle': 30,
        'keepalives_interval': 10,
        'keepalives_count': 5,
        'application_name': 'MyApp'  # Facilita debugging no Render
    },
    
    # Echo SQL queries em desenvolvimento
    'echo': os.getenv('DEBUG') == 'True'
}

# Cria o engine com configurações otimizadas
engine = create_engine(DATABASE_URL, **ENGINE_CONFIG)

# Event listener para reconexão automática
@event.listens_for(Pool, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Configura parâmetros da conexão"""
    logger.info("Nova conexão estabelecida com o banco")

@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    """Testa conexão antes de usar (forma compatível com psycopg2)"""
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
    except Exception as e:
        logger.warning(f"Conexão inválida detectada: {e}")
        raise DisconnectionError()

# SessionLocal com configurações otimizadas
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Evita problemas com objetos após commit
)

class DatabaseManager:
    """Gerenciador de banco com retry logic e tratamento de erros"""
    
    def __init__(self):
        self.max_retries = 3
        self.retry_delay = 2
    
    @contextmanager
    def get_session(self):
        """Context manager para sessões com retry logic"""
        session = None
        for attempt in range(self.max_retries):
            try:
                session = SessionLocal()
                yield session
                session.commit()
                break
                
            except (OperationalError, DisconnectionError) as e:
                logger.error(f"Erro de conexão (tentativa {attempt + 1}): {e}")
                
                if session:
                    session.rollback()
                    session.close()
                    session = None
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    logger.info(f"Tentando reconectar em {self.retry_delay * (2 ** attempt)}s...")
                else:
                    logger.error("Máximo de tentativas excedido")
                    raise e
                    
            except Exception as e:
                logger.error(f"Erro não relacionado à conexão: {e}")
                if session:
                    session.rollback()
                raise e
                
            finally:
                if session:
                    session.close()
    
    def execute_with_retry(self, operation, *args, **kwargs):
        """Executa operação com retry logic"""
        for attempt in range(self.max_retries):
            try:
                with self.get_session() as session:
                    return operation(session, *args, **kwargs)
                    
            except (OperationalError, DisconnectionError) as e:
                logger.error(f"Erro na operação (tentativa {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise e
    
    def test_connection(self) -> bool:
        """Testa se a conexão está funcionando"""
        try:
            with self.get_session() as session:
                result = session.execute("SELECT 1").scalar()
                return result == 1
        except Exception as e:
            logger.error(f"Teste de conexão falhou: {e}")
            return False
    
    def get_connection_info(self) -> dict:
        """Retorna informações sobre o pool de conexões"""
        try:
            pool = engine.pool
            return {
                'pool_size': pool.size(),
                'checked_in': pool.checkedin(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow(),
                'invalid': pool.invalid()
            }
        except Exception as e:
            logger.error(f"Erro ao obter info do pool: {e}")
            return {}

# Instância global do gerenciador
db_manager = DatabaseManager()

# Funções de conveniência
def get_session():
    """Retorna context manager para sessão"""
    return db_manager.get_session()

def test_connection() -> bool:
    """Testa conexão com banco"""
    return db_manager.test_connection()

def get_connection_info() -> dict:
    """Informações do pool de conexões"""
    return db_manager.get_connection_info()

def execute_with_retry(operation, *args, **kwargs):
    """Executa operação com retry"""
    return db_manager.execute_with_retry(operation, *args, **kwargs)

# Dependência para FastAPI (se estiver usando)
def get_db():
    """Dependência do FastAPI para injeção de sessão"""
    with get_session() as session:
        yield session

# Função para criar todas as tabelas
def create_tables():
    """Cria todas as tabelas definidas nos models"""
    try:
        from models import Base  # Importe seus models aqui
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tabelas criadas/verificadas com sucesso")
    except ImportError:
        logger.warning("⚠️  Arquivo models.py não encontrado")
    except Exception as e:
        logger.error(f"❌ Erro ao criar tabelas: {e}")

# Exemplo de uso e teste
if __name__ == "__main__":
    print("🔄 Testando conexão com banco de dados...")
    
    # Teste de conexão
    if test_connection():
        print("✅ Conexão com banco funcionando!")
        
        # Informações do pool
        pool_info = get_connection_info()
        print(f"📊 Pool info: {pool_info}")
        
        # Exemplo de uso da sessão
        def exemplo_query(session):
            # Substitua por uma query real do seu projeto
            result = session.execute("SELECT current_database(), version()").fetchone()
            return result
        
        try:
            resultado = execute_with_retry(exemplo_query)
            print(f"🗄️  Database: {resultado[0]}")
            print(f"🐘 PostgreSQL Version: {resultado[1][:50]}...")
        except Exception as e:
            print(f"❌ Erro na query de exemplo: {e}")
            
        # Tentar criar tabelas
        create_tables()
        
    else:
        print("❌ Falha na conexão com banco de dados")
        print("🔍 Verifique:")
        print("   - Se o DATABASE_URL está correto")
        print("   - Se o serviço no Render está ativo")
        print("   - Se não ultrapassou limite de conexões")
