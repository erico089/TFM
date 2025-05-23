CREATE TABLE IF NOT EXISTS ayudas (
    minimis TEXT,
    nombre TEXT,
    linea TEXT,
    fecha_inicio TEXT,
    fecha_fin TEXT,
    objetivo TEXT,
    beneficiarios TEXT,
    area TEXT,
    presupuesto_minimo TEXT,
    presupuesto_maximo TEXT,
    duracion_minima TEXT,
    duracion_maxima TEXT,
    intensidad_subvencion TEXT,
    intensidad_prestamo TEXT,
    tipo_financiacion TEXT,
    forma_plazo_cobro TEXT,
    region_aplicacion TEXT,
    tipo_consorcio TEXT,
    costes_elegibles TEXT,
    link_ficha_tecnica TEXT,
    link_orden_bases TEXT,
    link_convocatoria TEXT,
    id_vectorial TEXT,
    id TEXT PRIMARY KEY,
    organismo TEXT,
    año TEXT
);

CREATE TABLE IF NOT EXISTS ayudas_ref (
    id TEXT PRIMARY KEY,
    organismo_ref TEXT,
    fecha_inicio_ref TEXT,
    fecha_fin_ref TEXT,
    objetivo_ref TEXT,
    beneficiarios_ref TEXT,
    año_ref TEXT,
    presupuesto_minimo_ref TEXT,
    presupuesto_maximo_ref TEXT,
    duracion_minima_ref TEXT,
    duracion_maxima_ref TEXT,
    tipo_financiacion_ref TEXT,
    forma_plazo_cobro_ref TEXT,
    minimis_ref TEXT,
    region_aplicacion_ref TEXT,
    intensidad_subvencion_ref TEXT,
    intensidad_prestamo_ref TEXT,
    tipo_consorcio_ref TEXT,
    costes_elegibles_ref TEXT
);

CREATE TABLE IF NOT EXISTS ayudas_mock (
    minimis TEXT,
    nombre TEXT,
    linea TEXT,
    fecha_inicio TEXT,
    fecha_fin TEXT,
    objetivo TEXT,
    beneficiarios TEXT,
    area TEXT,
    presupuesto_minimo TEXT,
    presupuesto_maximo TEXT,
    duracion_minima TEXT,
    duracion_maxima TEXT,
    intensidad_subvencion TEXT,
    intensidad_prestamo TEXT,
    tipo_financiacion TEXT,
    forma_plazo_cobro TEXT,
    region_aplicacion TEXT,
    tipo_consorcio TEXT,
    costes_elegibles TEXT,
    link_ficha_tecnica TEXT,
    link_orden_bases TEXT,
    link_convocatoria TEXT,
    id_vectorial TEXT,
    id TEXT PRIMARY KEY,
    organismo TEXT,
    año TEXT
);

CREATE TABLE IF NOT EXISTS ayudas_mock_ref (
    id TEXT PRIMARY KEY,
    organismo_ref TEXT,
    fecha_inicio_ref TEXT,
    fecha_fin_ref TEXT,
    objetivo_ref TEXT,
    beneficiarios_ref TEXT,
    año_ref TEXT,
    presupuesto_minimo_ref TEXT,
    presupuesto_maximo_ref TEXT,
    duracion_minima_ref TEXT,
    duracion_maxima_ref TEXT,
    tipo_financiacion_ref TEXT,
    forma_plazo_cobro_ref TEXT,
    minimis_ref TEXT,
    region_aplicacion_ref TEXT,
    intensidad_subvencion_ref TEXT,
    intensidad_prestamo_ref TEXT,
    tipo_consorcio_ref TEXT,
    costes_elegibles_ref TEXT
);
