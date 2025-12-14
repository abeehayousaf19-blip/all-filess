class Dataset:
    """Represents a dataset in the platform."""

    def __init__(self, dataset_id: int, name: str, owner: str):
        self.__id = dataset_id
        self.__name = name
        self.__owner = owner

    def get_id(self) -> int:
        return self.__id

    def get_name(self) -> str:
        return self.__name

    def get_owner(self) -> str:
        return self.__owner

    def __str__(self) -> str:
        return f"Dataset {self.__id} - {self.__name} (Owner: {self.__owner})"

    @staticmethod
    def from_row(row: tuple) -> "Dataset":
        dataset_id, name, owner = row
        return Dataset(dataset_id, name, owner)
