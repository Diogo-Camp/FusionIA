CREATE TABLE sessao (
    id UUID PRIMARY KEY,
    modelo VARCHAR(100),
    personalidade VARCHAR(100),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE mensagem (
    id SERIAL PRIMARY KEY,
    sessao_id UUID REFERENCES sessao(id),
    tipo VARCHAR(10),
    conteudo TEXT,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
