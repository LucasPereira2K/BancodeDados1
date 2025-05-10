import os
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Float, func
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Configuração do banco de dados
engine = create_engine("sqlite:///database.db")
Session = sessionmaker(bind=engine)
base = declarative_base()

# Tabela Usuario
class Usuario(base):
    __tablename__ = 'Usuario'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    vendas = relationship("Venda", back_populates="cliente")

# Tabela Medicamento
class Medicamento(base):
    __tablename__ = 'Medicamento'
    id = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    itens = relationship("ItemVenda", back_populates="medicamento")

# Tabela Venda
class Venda(base):
    __tablename__ = 'Venda'
    id = Column(Integer, primary_key=True)
    cliente_id = Column(Integer, ForeignKey('Usuario.id'))
    cliente = relationship("Usuario", back_populates="vendas")
    itens = relationship("ItemVenda", back_populates="venda")

# Tabela ItemVenda
class ItemVenda(base):
    __tablename__ = 'ItemVenda'
    id = Column(Integer, primary_key=True)
    venda_id = Column(Integer, ForeignKey('Venda.id'))
    medicamento_id = Column(Integer, ForeignKey('Medicamento.id'))
    quantidade = Column(Integer, nullable=False)

    venda = relationship("Venda", back_populates="itens")
    medicamento = relationship("Medicamento", back_populates="itens")

# Função para inserir usuários
def insert_usuario(nome_usuario, tipo_usuario):
    session = Session()
    try:
        if all([nome_usuario, tipo_usuario]):
            usuario = Usuario(nome=nome_usuario, tipo=tipo_usuario)
            nu = session.query(Usuario).filter(Usuario.nome == nome_usuario).first()
            if nu:
                return None
            session.add(usuario)
            session.commit()
            print(f'Usuário {nome_usuario} cadastrado com sucesso!')
        else:
            print('Obrigatório nome do usuário!')
    except Exception as e:
        session.rollback()
        print(f'Erro ao adicionar usuário {nome_usuario}: {e}')
    finally:
        session.close()

# Inserção de medicamentos
def insert_medicamentos():
    session = Session()
    medicamentos = [
        ('Dipirona', 5.00),
        ('Anador', 8.50),
        ('Propranolol', 12.00),
        ('Losartana', 10.00)
    ]
    for nome, preco in medicamentos:
        if not session.query(Medicamento).filter_by(nome=nome).first():
            session.add(Medicamento(nome=nome, preco=preco))
    session.commit()
    session.close()

# Inserir venda de exemplo
def insert_venda_exemplo():
    session = Session()
    cliente = session.query(Usuario).filter(Usuario.tipo == 'Cliente').first()
    medicamento1 = session.query(Medicamento).filter_by(nome='Dipirona').first()
    medicamento2 = session.query(Medicamento).filter_by(nome='Anador').first()

    if cliente and medicamento1 and medicamento2:
        venda = Venda(cliente=cliente)
        session.add(venda)
        session.flush()  # para pegar o id da venda

        item1 = ItemVenda(venda_id=venda.id, medicamento_id=medicamento1.id, quantidade=2)
        item2 = ItemVenda(venda_id=venda.id, medicamento_id=medicamento2.id, quantidade=1)

        session.add_all([item1, item2])
        session.commit()
        print("Venda inserida com sucesso!")
    session.close()

# Consultas JOIN e GROUP BY
def relatorios():
    session = Session()

    print("\nTotal gasto por cliente:")
    results = session.query(
        Usuario.nome,
        func.sum(Medicamento.preco * ItemVenda.quantidade).label('total_gasto')
    ).join(Venda, Usuario.id == Venda.cliente_id
    ).join(ItemVenda, Venda.id == ItemVenda.venda_id
    ).join(Medicamento, Medicamento.id == ItemVenda.medicamento_id
    ).group_by(Usuario.nome).all()

    for nome, total in results:
        print(f"{nome}: R$ {total:.2f}")

    print("\nMedicamento mais vendido:")
    result = session.query(
        Medicamento.nome,
        func.sum(ItemVenda.quantidade).label('total_vendido')
    ).join(ItemVenda
    ).group_by(Medicamento.nome
    ).order_by(func.sum(ItemVenda.quantidade).desc()
    ).first()

    if result:
        print(f"{result[0]} - Quantidade vendida: {result[1]}")

    session.close()

# Atualizar preço de um medicamento
def atualizar_preco(nome_medicamento, novo_preco):
    session = Session()
    medicamento = session.query(Medicamento).filter_by(nome=nome_medicamento).first()
    if medicamento:
        medicamento.preco = novo_preco
        session.commit()
        print(f"Preço de {nome_medicamento} atualizado para R$ {novo_preco}")
    session.close()

# Deletar medicamento
def deletar_medicamento(nome_medicamento):
    session = Session()
    medicamento = session.query(Medicamento).filter_by(nome=nome_medicamento).first()
    if medicamento:
        session.delete(medicamento)
        session.commit()
        print(f"{nome_medicamento} deletado com sucesso.")
    session.close()

# Execução principal
if __name__ == '__main__':
    os.system("cls" if os.name == "nt" else "clear")
    base.metadata.create_all(engine)

    insert_usuario('Lucas Raphael', 'Dono da Farmacia')
    insert_usuario('Lucas Anderson', 'Cliente')
    insert_usuario('Matheus Henryque', 'Cliente')
    insert_usuario('João Silva', 'Cliente')  # Terceiro cliente

    insert_medicamentos()
    insert_venda_exemplo()
    relatorios()
    atualizar_preco("Anador", 9.00)
    deletar_medicamento("Propranolol")

