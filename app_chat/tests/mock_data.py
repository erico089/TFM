import json

mock_ayudas = [
    {
        "minimis": False,
        "nombre": "Proyectos de I+D: Audiovisual y Videojuegos",
        "linea": "Audiovisual y Videojuegos",
        "fecha_inicio": "28 de mayo de 2022",
        "fecha_fin": "12 de julio de 2022",
        "objetivo": "Apoyar el desarrollo de nuevas tecnologías aplicadas al sector audiovisual y videojuegos, con posibilidad de transferencia a otros sectores.",
        "beneficiarios": "Pequeñas y medianas empresas (PYMES)",
        "area": "I+D",
        "presupuesto_minimo": "",
        "presupuesto_maximo": "2.000.000 €",
        "duracion_minima": "",
        "duracion_maxima": "Hasta el 31 de diciembre de 2024, entre 2 y 3 años",
        "intensidad_subvencion": "",
        "intensidad_prestamo": "",
        "tipo_financiacion": "Subvención",
        "forma_plazo_cobro": "",
        "region_aplicacion": "España",
        "tipo_consorcio": "Individual",
        "costes_elegibles": "Costes de personal, instrumental, material amortizable, investigación contractual, consultoría exclusiva para el proyecto, gastos generales del proyecto, y auditoría hasta 1.500 € por beneficiario.",
        "link_ficha_tecnica": "",
        "link_orden_bases": "",
        "link_convocatoria": "https://www.cdtifeder.es/convocatorias/audiovisual-videojuegos-2022",
        "id_vectorial": "",
        "id": "proyectos_id_audiovisual_videojuegos_2022",
        "organismo": "Centro para el Desarrollo Tecnológico Industrial (CDTI)",
        "año": "2022"
    }
]


mock_ayudas_ref = [
    {
        "id": "id1",
        "organismo_ref": json.dumps([
            { "id": "id1_ficha", "fragment": 4 },
            { "id": "id1_base", "fragment": 7 }
        ]),
        "fecha_inicio_ref": json.dumps([
            { "id": "id1_ficha", "fragment": 5 },
            { "id": "id1_base", "fragment": 8 }
        ]),
        "fecha_fin_ref": json.dumps([
            { "id": "id1_ficha", "fragment": 10 },
            { "id": "id1_base", "fragment": 4 }
        ]),
        "objetivo_ref": json.dumps([
            { "id": "id1_ficha", "fragment": 2 },
            { "id": "id1_base", "fragment": 9 }
        ]),
        "año_ref": json.dumps([
            { "id": "id1_ficha", "fragment": 3 },
            { "id": "id1_base", "fragment": 8 }
        ]),
        "duracion_minima_ref": json.dumps([
            { "id": "id1_ficha", "fragment": 5 },
            { "id": "id1_base", "fragment": 9 }
        ]),
        "duracion_maxima_ref": json.dumps([
            { "id": "id1_ficha", "fragment": 8 },
            { "id": "id1_base", "fragment": 4 }
        ]),
        "tipo_financiacion_ref": json.dumps([
            { "id": "id1_ficha", "fragment": 2 },
            { "id": "id1_base", "fragment": 8 }
        ]),
        "forma_plazo_cobro_ref": json.dumps([
            { "id": "id1_ficha", "fragment": 7 },
            { "id": "id1_base", "fragment": 10 }
        ]),
        "minimis_ref": json.dumps([
            { "id": "id1_ficha", "fragment": 9 },
            { "id": "id1_base", "fragment": 1 }
        ]),
        "region_aplicacion_ref": json.dumps([
            { "id": "id1_ficha", "fragment": 8 },
            { "id": "id1_base", "fragment": 4 }
        ]),
        "intensidad_subvencion_ref": json.dumps([
            { "id": "id1_ficha", "fragment": 3 },
            { "id": "id1_base", "fragment": 9 }
        ]),
        "intensidad_prestamo_ref": json.dumps([
            { "id": "id1_ficha", "fragment": 2 },
            { "id": "id1_base", "fragment": 6 }
        ]),
        "tipo_consorcio_ref": json.dumps([
            { "id": "id1_ficha", "fragment": 5 },
            { "id": "id1_base", "fragment": 8 }
        ]),
        "costes_elegibles_ref": json.dumps([
            { "id": "id1_ficha", "fragment": 6 },
            { "id": "id1_base", "fragment": 7 }
        ])
    }
]


test_cases = [
    # Preguntar si hay convocatorias abiertas hoy, tendra que usar Duck Duck tool
    (
        "¿Existe alguna convocatoria abierta a día de hoy?", 
        "Si que hay"
    ),

    # Pedir una convocatoria del área I+D
    (
        "Dame una convocatoria que tenga que ver con el área I+D.", 
        "Una convocatoria disponible relacionada con I+D es: Proyectos de I+D: audiovisual y videojuegos."
    ),

    # Preguntar en qué región aplica la convocatoria específica
    (
        "¿En qué región aplica la convocatoria de Proyectos de I+D: audiovisual y videojuegos?", 
        "La convocatoria Proyectos de I+D: audiovisual y videojuegos aplica en España."
    ),
    # Preguntar por un dato, que no deberia ser muy fiable
    (
        "De la convocatoria de Proyectos de I+D: audiovisual y videojuegos, ¿cuales son sus costes_elegibles?",
        "Costes de personal, instrumental, material amortizable, investigación contractual, consultoría exclusiva para el proyecto, gastos generales del proyecto, y auditoría hasta 1.500 € por beneficiario, aun así, mis datos no son del todo fiables en este caso y requieren de una verificación extra"
    ),
    # Preguntar por dato que solo esta en el pdf
    (
        "De la convocatoria de Proyectos de I+D: audiovisual y videojuegos, cual es el presupuesto minimo?",
        "175.000 euros por empresa"
    ),
    (
        "Cual es el presupuesto maixmo de la ayuda de Proyectos de I+D: audiovisual y videojuegos",
        "Son 2.000.000 € pero no estoy muy seguro asi que seria mejor revisarlo"
    ),
    (
        "Quien es el presidente de estados unidos",
        "No puedo responder a esa pregunta, recuerda que soy un agente que responde a contenido relacionado con convocatorias de subenciones y ayudas."
    ),
    (
        "Que beneficiarios tiene la ayuda de Proyectos de I+D: audiovisual y videojuegos?",
        "Pequeñas y medianas empresas (PYMES), aunque no lo tengo muy claro, deberias revisarlo manualmente"
    ),
    (
        "Tienes el link de la convocatoria de la ayuda de Proyectos de I+D: audiovisual y videojuegos?",
        "Si, aqui esta: https://www.cdtifeder.es/convocatorias/audiovisual-videojuegos-2022"
    ),
    (
        "Que me puedes contar sobre la ayuda de CTDI de la salut en entorno laboral",
        "No tengo información sobre esa ayuda"
    )
]
