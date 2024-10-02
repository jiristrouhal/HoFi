import json
import dataclasses
import os

from te_tree.core.attributes import Currency_Code, Locale_Code  # type: ignore


LOCALIZATION_PATH = "./localization/"


@dataclasses.dataclass(frozen=True)
class HofiConfig:
    localization: Locale_Code
    allow_item_name_duplicates: bool
    currency: Currency_Code
    editor_precision: int = dataclasses.field()
    show_trailing_zeros: bool
    use_thousands_separator: bool

    def __post_init__(self) -> None:
        if self.currency not in Currency_Code.__args__:
            raise HofiConfig.ConfigurationError(
                f"Unknown currency code: {self.currency}. Allowed codes are: {Currency_Code.__args__}"
            )
        if self.localization not in Locale_Code.__args__:
            raise HofiConfig.ConfigurationError(
                f"Unknown locale code: {self.localization}. Allowed codes are: {Locale_Code.__args__}"
            )
        if self.editor_precision < 0:
            raise HofiConfig.ConfigurationError(
                f"Invalid precision value: {self.localization}. It must be non-negative integer"
            )

    class ConfigurationError(Exception):
        pass


def load_config(path: str) -> HofiConfig | None:
    abs_path = os.path.join(path)
    try:
        with open(abs_path) as c:
            config_dict = json.load(c)
            return HofiConfig(**config_dict)
    except FileNotFoundError:
        print(f"Configuration file was not found on path {abs_path}.")
        return None
    except Exception as e:
        print(f"Error when loading a configuration file: {e}")
        return None
