"""
Modulo encargado de JSON paciente repositorio.
Utiliza `json` para serializar y deserializar cargas JSON; `pathlib.Path` para manejar rutas multiplataforma; `typing` para contratos explicitos; modelos del dominio ubicados en `src.core.models`; puertos que definen interfaces para el nucleo del negocio.
Este modulo sigue SOLID: Single Responsibility mantiene el enfoque, Open/Closed deja la puerta abierta y Dependency Inversion depende de abstracciones en lugar de detalles.
"""

import json
from pathlib import Path
from typing import Iterable

from ...core.models import PatientRecord
from ...core.ports import PatientRepository


class JsonPatientRepository(PatientRepository):
    """
    Representa JSON paciente repositorio y mantiene Single Responsibility
    para ese concepto del dominio, permitiendo extender el comportamiento
    sin modificar su contrato (Open/Closed) y apoyandose en abstracciones
    (Dependency Inversion).
    """

    def __init__(self, source: Path, dataset_key: str = "pacientes"):
        """
        Encapsula init, manteniendo Single Responsibility y dejando el contrato
        abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        self.source = source
        self.dataset_key = dataset_key

    def list_patients(self) -> Iterable[PatientRecord]:
        """
        Encapsula list patients, manteniendo Single Responsibility y dejando el
        contrato abierto para nuevas versiones (Open/Closed) mientras depende de
        abstracciones (Dependency Inversion).
        """

        with self.source.open(encoding="utf-8") as stream:
            payload = json.load(stream)
            table = payload.get(self.dataset_key, [])
            for raw in table:
                yield PatientRecord.from_dict(raw)
