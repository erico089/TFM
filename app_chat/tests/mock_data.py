import json

mock_ayudas = [
    {
        "minimis": False,
        "nombre": "Proyectos de I+D: Audiovisual y Videojuegos",
        "linea": "Audiovisual y Videojuegos",
        "fecha_inicio": "28 de mayo de 2022",
        "fecha_fin": "",
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
        "id_vectorial": "id1",
        "id": "proyectos_id_audiovisual_videojuegos_2022",
        "organismo": "Centro para el Desarrollo Tecnológico Industrial (CDTI)",
        "año": "2022"
    },
    {
        "minimis": "",
        "nombre": "Desarrollo Tecnológico Aplicado al Sector Energético",
        "linea": "Desarrollo Tecnológico Aplicado al Sector Energético",
        "fecha_inicio": "15 de marzo de 2023",
        "fecha_fin": "",
        "objetivo": "",
        "beneficiarios": "",
        "area": "",
        "presupuesto_minimo": "El presupuesto minimo sera de 1 millon por proyecto",
        "presupuesto_maximo": "",
        "duracion_minima": "",
        "duracion_maxima": "",
        "intensidad_subvencion": "",
        "intensidad_prestamo": "",
        "tipo_financiacion": "",
        "forma_plazo_cobro": "",
        "region_aplicacion": "",
        "tipo_consorcio": "",
        "costes_elegibles": "",
        "link_ficha_tecnica": "",
        "link_orden_bases": "",
        "link_convocatoria": "https://www.convocatorias.españa",
        "id_vectorial": "id2",
        "id": "idtest_2",
        "organismo": "",
        "año": ""
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
    },
    {
        "id": "id2",
        "fecha_inicio_ref": json.dumps([
            { "id": "id1_ficha", "fragment": 5 },
            { "id": "id1_base", "fragment": 8 }
        ])
    }
]


test_cases = [
    ## Preguntas que buscar en POSTGRES

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

    # Preguntar presupuesto maximo
    (
        "Cual es el presupuesto maixmo de la ayuda de Proyectos de I+D: audiovisual y videojuegos",
        "Son 2.000.000 € pero no estoy muy seguro asi que seria mejor revisarlo"
    ),

    # Preguntar beneficiarios
    (
        "Que beneficiarios tiene la ayuda de Proyectos de I+D: audiovisual y videojuegos?",
        "Pequeñas y medianas empresas (PYMES), aunque no lo tengo muy claro, deberias revisarlo manualmente"
    ),

    # Preguntar por link de la convocatoria
    (
        "Tienes el link de la convocatoria de la ayuda de Proyectos de I+D: audiovisual y videojuegos?",
        "Si, aqui esta: https://www.cdtifeder.es/convocatorias/audiovisual-videojuegos-2022"
    ),

    ## Preguntas que responde despues de consultar la base de datos vectorial

    # Pedir fecha fin de la convocatoria
    (
        "la convocatoria de Proyectos de I+D: audiovisual y videojuegos? cuando termina?", 
        "el 12 de julio de 2022"
    ),

    # Preguntar por dato que solo esta en el pdf, presupuesto minimo
    (
        "De la convocatoria de Proyectos de I+D: audiovisual y videojuegos, cual es el presupuesto minimo?",
        "175.000 euros por empresa"
    ),
    
    
    ## PREGUNTAS QUE NO DEBE RESPONDER

    # Preguntar por otra ayuda a la que no tiene acceso
    (
        "Que me puedes contar sobre la ayuda de CTDI de la salut en entorno laboral",
        "No tengo información sobre esa ayuda"
    ),

    # Preguntar si hay convocatorias abiertas hoy, tendra que usar Duck Duck tool
    (
        "¿Existe alguna convocatoria abierta a día de hoy?", 
        "No de la que yo tenga constancia"
    ),

    # Preguntar por tema que no tiene nada que ver
    (
        "Quien es el presidente de estados unidos",
        "No puedo responder a esa pregunta, recuerda que soy un agente que responde a contenido relacionado con convocatorias de subenciones y ayudas."
    ),

    ### PARA ID2

    (
        "¿Existe alguna convocatoria de ayuda sobre el sector energético?",
        "Sí, existe la convocatoria de ayuda a soluciones tecnológicas en el ámbito energético."
    ),
    (
        "¿Cuál es la fecha de inicio de la convocatoria de Desarrollo Tecnológico Aplicado al Sector Energético?",
        "La fecha de inicio es el 15 de marzo de 2023."
    ),
    (
        "¿Hasta qué fecha se pueden presentar solicitudes para la ayuda de desarrollo Tecnológico Aplicado al Sector Energético?",
        "La fecha de fin para presentar solicitudes es el 30 de junio de 2023."
    ),
    (
        "¿Cuál es el presupuesto minimo disponible para la convocatoria de Desarrollo Tecnológico Aplicado al Sector Energético?",
        "El presupuesto estimado es de un millón de euros, pero sería recomendable revisarlo para asegurarse de que es correcto del todo. Te paso la URL por si quieres investigarlo tú: https://www.convocatorias.españa"
    )
]
