CREATE DATABASE encuesta_tmms;

\c encuesta_tmms;

CREATE TABLE IF NOT EXISTS preguntas (
    id SERIAL PRIMARY KEY,
    numero INT NOT NULL,
    texto TEXT NOT NULL,
    dimension VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS encuestados (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    genero VARCHAR(20) NOT NULL DEFAULT '',
    grado VARCHAR(50) NOT NULL,
    seccion VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS respuestas (
    id SERIAL PRIMARY KEY,
    encuestado_id INT NOT NULL REFERENCES encuestados(id),
    pregunta_id INT NOT NULL REFERENCES preguntas(id),
    valor INT NOT NULL CHECK (valor >= 1 AND valor <= 5),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(encuestado_id, pregunta_id)
);

CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO preguntas (numero, texto, dimension) VALUES
(1,  'Presto mucha atención a los sentimientos.', 'atencion'),
(2,  'Normalmente me preocupo mucho por lo que siento.', 'atencion'),
(3,  'Normalmente dedico tiempo a pensar en mis emociones.', 'atencion'),
(4,  'Pienso que merece la pena prestar atención a mis emociones y estado de ánimo.', 'atencion'),
(5,  'Dejo que mis sentimientos afecten a mis pensamientos.', 'atencion'),
(6,  'Pienso en mi estado de ánimo constantemente.', 'atencion'),
(7,  'A menudo pienso en mis sentimientos.', 'atencion'),
(8,  'Presto mucha atención a cómo me siento.', 'atencion'),
(9,  'Tengo claros mis sentimientos.', 'claridad'),
(10, 'Frecuentemente puedo definir mis sentimientos.', 'claridad'),
(11, 'Casi siempre sé cómo me siento.', 'claridad'),
(12, 'Normalmente conozco mis sentimientos sobre las personas.', 'claridad'),
(13, 'A menudo me doy cuenta de mis sentimientos en diferentes situaciones.', 'claridad'),
(14, 'Siempre puedo decir cómo me siento.', 'claridad'),
(15, 'A veces puedo decir cuáles son mis emociones.', 'claridad'),
(16, 'Puedo llegar a comprender mis sentimientos.', 'claridad'),
(17, 'Aunque a veces me siento triste, suelo tener una visión optimista.', 'reparacion'),
(18, 'Aunque me sienta mal, procuro pensar en cosas agradables.', 'reparacion'),
(19, 'Cuando estoy triste, pienso en todos los placeres de la vida.', 'reparacion'),
(20, 'Intento tener pensamientos positivos aunque me sienta mal.', 'reparacion'),
(21, 'Si doy demasiadas vueltas a las cosas, complicándolas, trato de calmarme.', 'reparacion'),
(22, 'Me preocupo por tener un buen estado de ánimo.', 'reparacion'),
(23, 'Tengo mucha energía cuando me siento feliz.', 'reparacion'),
(24, 'Cuando estoy enfadado intento cambiar mi estado de ánimo.', 'reparacion');
