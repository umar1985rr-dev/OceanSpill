from dataclasses import dataclass


@dataclass
class Alert:

    title: str

    message: str

    severity: str