"""Day 4 challenge"""

# Built-in
import re

# Personal
from _shared import read_input


# --------------------------------------------------------------------------------
# > Helpers
# --------------------------------------------------------------------------------
class PassportForm:
    LINE_REGEX = r"([a-z]{3}):([^ ]+)"
    FIELDS = [
        ("byr", True),  # field_name, required
        ("iyr", True),
        ("eyr", True),
        ("hgt", True),
        ("hcl", True),
        ("ecl", True),
        ("pid", True),
        ("cid", False),
    ]

    def __init__(self, line):
        """
        Read the passport info to fill a PassportForm
        :param str line: Passport data from the input file
        """
        self.line = line
        self.fill_form()
        self.find_invalid_fields()

    def fill_form(self):
        """Parses the input file to set our form fields/values"""
        for match in re.finditer(self.LINE_REGEX, self.line):
            field = match.group(1)
            value = match.group(2)
            setattr(self, field, value)

    def find_invalid_fields(self):
        """
        Checks for missing fields
        :return: The required fields that are missing from our form
        :rtype: set
        """
        invalid_fields = set()
        for field_name, required in self.FIELDS:
            value = getattr(self, field_name, None)
            # Check required
            if required and value is None:
                invalid_fields.add(field_name)
            # Custom validation
            if value is not None:
                function_name = f"validate_{field_name}"
                field_validation_function = getattr(self, function_name)
                if not field_validation_function():
                    invalid_fields.add(field_name)
        self.invalid_fields = invalid_fields

    @property
    def is_valid(self):
        """
        :return: Whether the form is valid
        :rtype: bool
        """
        return len(self.invalid_fields) == 0

    def validate_byr(self):
        """
        :return: Whether BYR is within the range
        :rtype: bool
        """
        value = int(self.byr)
        return 1920 <= value <= 2002

    def validate_iyr(self):
        """
        :return: Whether IYR is within the range
        :rtype: bool
        """
        value = int(self.iyr)
        return 2010 <= value <= 2020

    def validate_eyr(self):
        """
        :return: Whether EYR is within the range
        :rtype: bool
        """
        value = int(self.eyr)
        return 2020 <= value <= 2030

    def validate_hgt(self):
        """
        Checks the HGT is valid and within the right range, depending on the unit of measure
        :return: Whether HGT is within the range
        :rtype: bool
        """
        regex = r"^(\d+)(cm|in)$"
        match = re.match(regex, self.hgt)
        if match is not None:
            value = int(match.group(1))
            units = match.group(2)
            if units == "cm":
                return 150 <= value <= 193
            else:
                return 59 <= value <= 76
        return False

    def validate_hcl(self):
        """
        :return: Whether the HCL format is valid
        :rtype: bool
        """
        regex = r"^#[a-f0-9]{6}$"
        return not re.match(regex, self.hcl) is None

    def validate_ecl(self):
        """
        :return: Whether the ECL value is in the list of accepted values
        :rtype: bool
        """
        return self.ecl in {
            "amb",
            "blu",
            "brn",
            "gry",
            "grn",
            "hzl",
            "oth",
        }

    def validate_pid(self):
        """
        :return: Whether PID is a chain of 9 digits
        :rtype: bool
        """
        regex = r"^\d{9}$"
        return not re.match(regex, self.pid) is None

    @staticmethod
    def validate_cid():
        """
        :return: No custom validation. Always valid
        :rtype: bool
        """
        return True


def get_passport_info_from_input():
    """
    Fetches the input file and rebuilds passport info as a one-liner
    :return: List string of passport info
    :rtype: [str]
    """
    passport_list = []
    text = ""
    for line in read_input("day_04.txt"):
        if line != "":
            text += f" {line}"
        else:
            passport_list.append(text[1:])
            text = ""
    passport_list.append(text[1:])  # Adding the last one
    return passport_list


# --------------------------------------------------------------------------------
# > Main
# --------------------------------------------------------------------------------
passport_info = get_passport_info_from_input()
passport_forms = [PassportForm(line) for line in passport_info]
valid_forms = [form for form in passport_forms if form.is_valid]
print(len(valid_forms))
