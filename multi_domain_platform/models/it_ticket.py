class ITTicket:
    """Represents an IT operations ticket in the platform."""

    def __init__(self, ticket_id: int, subject: str, status: str):
        self.__id = ticket_id
        self.__subject = subject
        self.__status = status

    def get_id(self) -> int:
        return self.__id

    def get_subject(self) -> str:
        return self.__subject

    def get_status(self) -> str:
        return self.__status

    def update_status(self, new_status: str) -> None:
        self.__status = new_status

    def __str__(self) -> str:
        return f"Ticket {self.__id} - {self.__subject} ({self.__status})"

    @staticmethod
    def from_row(row: tuple) -> "ITTicket":
        ticket_id, subject, status = row
        return ITTicket(ticket_id, subject, status)
