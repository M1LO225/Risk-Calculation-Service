# Risk-Calculation-Service
Risk Calculation Service
Visión General
El Risk Calculation Service es el último worker asincrónico dentro del flujo de evaluación de riesgos. Actúa como el "cerebro" de la operación, consumiendo eventos vulnerability.found desde Kafka y sintetizando toda la información recolectada previamente para producir una puntuación final y cuantificable del riesgo.

Su proceso es el siguiente:

Recibe un evento vulnerability.found.

Obtiene los datos de valuación del activo correspondiente (puntuaciones SCA) desde la base de datos de activos.

Aplica las fórmulas principales de riesgo definidas en la metodología del proyecto para calcular:

Impacto Cuantitativo (IC): El daño potencial que una vulnerabilidad podría causar a un activo específico.

Probabilidad Cuantitativa (PC): La probabilidad de que la vulnerabilidad sea explotada.

Nivel de Riesgo (NR): La puntuación final del riesgo, calculada como NR = IC * PC.

Guarda el registro de riesgo calculado en la base de datos.

Publica un evento final risk.calculated, que indica al frontend/dashboard que hay nuevos resultados disponibles para visualizar.

Tecnologías Utilizadas
Lenguaje: Python 3.11+

Mensajería: Apache Kafka

Base de datos: PostgreSQL

Contenerización: Docker

Lógica Central: Fórmulas de Riesgo
Este servicio implementa directamente el núcleo matemático de la metodología:

Impacto Cuantitativo (IC): Calculado combinando las puntuaciones CIA dimensionales del activo (SCA_C, SCA_I, SCA_D) con el impacto dimensional de la vulnerabilidad según su puntuación CVSS.

Probabilidad Cuantitativa (PC): Calculada usando la severidad base de la vulnerabilidad (puntuación CVSS) y un valor estimado de la efectividad de los controles existentes (EC). PC = (SV / 10) * (1 - EC).

Nivel de Riesgo (NR): El producto de ambos valores, NR = IC * PC, resultando en una puntuación final del 0 al 10.

Arquitectura
Este servicio es un worker sin interfaz gráfica, basado en los principios de Clean Architecture:

Dominio: Define la entidad Risk y las interfaces abstractas de los repositorios.

Aplicación: Contiene el CalculateRiskUseCase y el servicio central RiskFormulaService.

Infraestructura: Proporciona las implementaciones concretas para los repositorios PostgreSQL y el productor Kafka. Es único porque lee de una base de datos (asset_db) y escribe en otra (risk_db).

Worker: Es el proceso principal que ejecuta el consumidor de Kafka.