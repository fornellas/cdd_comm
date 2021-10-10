import csv
import datetime
from dataclasses import dataclass
from typing import Dict, Iterator, List, Optional, Set


@dataclass
class Address:
    street: Optional[str]
    city: Optional[str]
    po_box: Optional[str]
    region: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]
    extended_address: Optional[str]

    def __hash__(self) -> int:
        return id(self)


@dataclass
class Organization:
    name: Optional[str]
    yomi_name: Optional[str]
    title: Optional[str]
    department: Optional[str]
    symbol: Optional[str]
    location: Optional[str]
    job_description: Optional[str]

    def __hash__(self) -> int:
        return id(self)


@dataclass
class Contact:
    given_name: Optional[str]  # UI
    additional_name: Optional[str]  # UI
    family_name: Optional[str]  # UI
    given_name_yomi: Optional[str]  # UI
    additional_name_yomi: Optional[str]  # UI
    family_name_yomi: Optional[str]  # UI
    name_prefix: Optional[str]  # UI
    name_suffix: Optional[str]  # UI
    initials: Optional[str]
    nickname: Optional[str]  # UI
    short_name: Optional[str]
    maiden_name: Optional[str]
    birthday: Optional[datetime.date]  # UI
    gender: Optional[str]
    location: Optional[str]
    billing_information: Optional[str]
    directory_server: Optional[str]
    mileage: Optional[str]
    occupation: Optional[str]
    hobby: Optional[str]
    sensitivity: Optional[str]
    priority: Optional[str]
    subject: Optional[str]
    notes: Optional[str]  # UI
    language: Optional[str]
    photo: Optional[str]
    group_membership: Set[str]
    emails: Dict[str, Set[str]]  # UI
    ims: Dict[str, Set[str]]  # UI
    phones: Dict[str, Set[str]]  # UI
    addresses: Dict[str, Set[Address]]  # UI
    organizations: Dict[str, Set[Organization]]  # UI
    relations: Dict[str, Set[str]]  # UI
    websites: Dict[str, Set[str]]  # UI
    events: Dict[str, datetime.date]  # UI
    custom_fields: Dict[str, Set[str]]  # UI

    def __post_init__(self) -> None:
        assert self.given_name != ""
        assert self.additional_name != ""
        assert self.family_name != ""
        assert self.given_name_yomi != ""
        assert self.additional_name_yomi != ""
        assert self.family_name_yomi != ""
        assert self.name_prefix != ""
        assert self.name_suffix != ""
        assert self.initials != ""
        assert self.nickname != ""
        assert self.short_name != ""
        assert self.maiden_name != ""
        assert self.birthday != ""
        assert self.gender != ""
        assert self.location != ""
        assert self.billing_information != ""
        assert self.directory_server != ""
        assert self.mileage != ""
        assert self.occupation != ""
        assert self.hobby != ""
        assert self.sensitivity != ""
        assert self.priority != ""
        assert self.subject != ""
        assert self.notes != ""
        assert self.language != ""
        assert self.photo != ""
        assert self.group_membership != ""

    @property
    def name(self) -> str:
        name_str = ""
        if self.name_prefix is not None:
            name_str += f" {self.name_prefix}"
        if self.given_name is not None:
            name_str += f" {self.given_name}"
        if self.additional_name is not None:
            name_str += f" {self.additional_name}"
        if self.family_name is not None:
            name_str += f" {self.family_name}"
        if self.name_suffix is not None:
            name_str += f" {self.name_suffix}"
        return name_str

    @property
    def yomi_name(self) -> str:
        yomi_name_str = ""
        if self.given_name_yomi is not None:
            yomi_name_str += f" {self.given_name_yomi}"
        if self.additional_name_yomi is not None:
            yomi_name_str += f" {self.additional_name_yomi}"
        if self.family_name_yomi is not None:
            yomi_name_str += f" {self.family_name_yomi}"
        return yomi_name_str


class GoogleCSV:
    def __init__(self, path: str) -> None:
        self.path = path

    def _get_value(self, column: str, row: List[str]) -> Optional[str]:
        value = row[self.header.index(column)]
        if len(value) == 0:
            return None
        else:
            return value

    @staticmethod
    def _parse_date(date_str: str) -> datetime.date:
        year, month, day = date_str.split("-")
        return datetime.date(int(year), int(month), int(day))

    def _get_birthday(self, row: List[str]) -> Optional[datetime.date]:
        birthday: Optional[datetime.date] = None
        birthday_str = self._get_value("Birthday", row)
        if birthday_str is not None:
            birthday = self._parse_date(birthday_str)
        return birthday

    def _get_value_set(self, column: str, row: List[str]) -> Set[str]:
        values = self._get_value(column, row)
        if values is None:
            return set()
        else:
            return set(values.split(" ::: "))

    def _get_value_map(
        self, column: str, row: List[str], key: str = "Type", value: str = "Value"
    ) -> Dict[str, Set[str]]:
        index: int = 0
        data: Dict[str, Set[str]] = {}
        while True:
            index += 1
            try:
                k = row[self.header.index(f"{column} {index} - {key}")]
                v = row[self.header.index(f"{column} {index} - {value}")]
            except ValueError:
                break
            else:
                if k.startswith("* "):
                    k = k[2:]
                if len(k) or len(v):
                    if k not in data:
                        data[k] = set()
                    data[k].update(v.split(" ::: "))
        return data

    def _get_ims(self, row: List[str]) -> Dict[str, Set[str]]:
        index: int = 0
        data: Dict[str, Set[str]] = {}
        while True:
            index += 1
            try:
                k = row[self.header.index(f"IM {index} - Service")]
                v = row[self.header.index(f"IM {index} - Value")]
            except ValueError:
                break
            else:
                if len(k) or len(v):
                    services = k.split(" ::: ")
                    values = v.split(" ::: ")
                    for i in range(0, len(services)):
                        if services[i] not in data:
                            data[services[i]] = set()
                        data[services[i]].add(values[i])
        return data

    def _get_events(self, row: List[str]) -> Dict[str, datetime.date]:
        data: Dict[str, datetime.date] = {}
        for key, value in self._get_value_map("Event", row).items():
            assert len(value) == 1
            data[key] = self._parse_date(next(iter(value)))
        return data

    def _get_addresses(self, row: List[str]) -> Dict[str, Set[Address]]:
        index: int = 0
        data: Dict[str, Set[Address]] = {}
        while True:
            index += 1
            try:
                address_type = row[self.header.index(f"Address {index} - Type")]
                address_street = row[self.header.index(f"Address {index} - Street")]
                address_city = row[self.header.index(f"Address {index} - City")]
                address_po_box = row[self.header.index(f"Address {index} - PO Box")]
                address_region = row[self.header.index(f"Address {index} - Region")]
                address_postal_code = row[
                    self.header.index(f"Address {index} - Postal Code")
                ]
                address_country = row[self.header.index(f"Address {index} - Country")]
                address_extended_address = row[
                    self.header.index(f"Address {index} - Extended Address")
                ]
            except ValueError:
                break
            else:
                address_street_list = address_street.split(" ::: ")
                address_city_list = address_city.split(" ::: ")
                address_po_box_list = address_po_box.split(" ::: ")
                address_region_list = address_region.split(" ::: ")
                address_postal_code_list = address_postal_code.split(" ::: ")
                address_country_list = address_country.split(" ::: ")
                address_extended_address_list = address_extended_address.split(" ::: ")

                for i in range(0, len(address_street_list)):
                    if not (
                        address_street_list[i] != ""
                        or address_city_list[i] != ""
                        or address_po_box_list[i] != ""
                        or address_region_list[i] != ""
                        or address_postal_code_list[i] != ""
                        or address_country_list[i] != ""
                        or address_extended_address_list[i] != ""
                    ):
                        continue
                    if address_type not in data:
                        data[address_type] = set()
                    data[address_type].add(
                        Address(
                            street=address_street_list[i]
                            if address_street_list[i] != ""
                            else None,
                            city=address_city_list[i]
                            if address_city_list[i] != ""
                            else None,
                            po_box=address_po_box_list[i]
                            if address_po_box_list[i] != ""
                            else None,
                            region=address_region_list[i]
                            if address_region_list[i] != ""
                            else None,
                            postal_code=address_postal_code_list[i]
                            if address_postal_code_list[i] != ""
                            else None,
                            country=address_country_list[i]
                            if address_country_list[i] != ""
                            else None,
                            extended_address=address_extended_address_list[i]
                            if address_extended_address_list[i] != ""
                            else None,
                        )
                    )
        return data

    def _get_organizations(self, row: List[str]) -> Dict[str, Set[Organization]]:
        index: int = 0
        data: Dict[str, Set[Organization]] = {}
        while True:
            index += 1
            try:
                organization_type = row[
                    self.header.index(f"Organization {index} - Type")
                ]
                organization_name = row[
                    self.header.index(f"Organization {index} - Name")
                ]
                organization_yomi_name = row[
                    self.header.index(f"Organization {index} - Yomi Name")
                ]
                organization_title = row[
                    self.header.index(f"Organization {index} - Title")
                ]
                organization_department = row[
                    self.header.index(f"Organization {index} - Department")
                ]
                organization_symbol = row[
                    self.header.index(f"Organization {index} - Symbol")
                ]
                organization_location = row[
                    self.header.index(f"Organization {index} - Location")
                ]
                organization_job_description = row[
                    self.header.index(f"Organization {index} - Job Description")
                ]
            except ValueError:
                break
            else:
                organization_name_list = organization_name.split(" ::: ")
                organization_yomi_name_list = organization_yomi_name.split(" ::: ")
                organization_title_list = organization_title.split(" ::: ")
                organization_department_list = organization_department.split(" ::: ")
                organization_symbol_list = organization_symbol.split(" ::: ")
                organization_location_list = organization_location.split(" ::: ")
                organization_job_description_list = organization_job_description.split(
                    " ::: "
                )

                for i in range(0, len(organization_name_list)):
                    if not (
                        organization_name_list[i] != ""
                        or organization_yomi_name_list[i] != ""
                        or organization_title_list[i] != ""
                        or organization_department_list[i] != ""
                        or organization_symbol_list[i] != ""
                        or organization_location_list[i] != ""
                        or organization_job_description_list[i] != ""
                    ):
                        continue
                    if organization_type not in data:
                        data[organization_type] = set()
                    data[organization_type].add(
                        Organization(
                            name=organization_name_list[i]
                            if organization_name_list[i] != ""
                            else None,
                            yomi_name=organization_yomi_name_list[i]
                            if organization_yomi_name_list[i] != ""
                            else None,
                            title=organization_title_list[i]
                            if organization_title_list[i] != ""
                            else None,
                            department=organization_department_list[i]
                            if organization_department_list[i] != ""
                            else None,
                            symbol=organization_symbol_list[i]
                            if organization_symbol_list[i] != ""
                            else None,
                            location=organization_location_list[i]
                            if organization_location_list[i] != ""
                            else None,
                            job_description=organization_job_description_list[i]
                            if organization_job_description_list[i] != ""
                            else None,
                        )
                    )
        return data

    def parse(self) -> Iterator[Contact]:
        with open(self.path) as csvfile:
            csv_reader = csv.reader(csvfile)
            self.header = next(csv_reader)
            for row in csv_reader:
                yield Contact(
                    given_name=self._get_value("Given Name", row),
                    additional_name=self._get_value("Additional Name", row),
                    family_name=self._get_value("Family Name", row),
                    given_name_yomi=self._get_value("Given Name Yomi", row),
                    additional_name_yomi=self._get_value("Additional Name Yomi", row),
                    family_name_yomi=self._get_value("Family Name Yomi", row),
                    name_prefix=self._get_value("Name Prefix", row),
                    name_suffix=self._get_value("Name Suffix", row),
                    initials=self._get_value("Initials", row),
                    nickname=self._get_value("Nickname", row),
                    short_name=self._get_value("Short Name", row),
                    maiden_name=self._get_value("Maiden Name", row),
                    birthday=self._get_birthday(row),
                    gender=self._get_value("Gender", row),
                    location=self._get_value("Location", row),
                    billing_information=self._get_value("Billing Information", row),
                    directory_server=self._get_value("Directory Server", row),
                    mileage=self._get_value("Mileage", row),
                    occupation=self._get_value("Occupation", row),
                    hobby=self._get_value("Hobby", row),
                    sensitivity=self._get_value("Sensitivity", row),
                    priority=self._get_value("Priority", row),
                    subject=self._get_value("Subject", row),
                    notes=self._get_value("Notes", row),
                    language=self._get_value("Language", row),
                    photo=self._get_value("Photo", row),
                    group_membership=self._get_value_set("Group Membership", row),
                    emails=self._get_value_map("E-mail", row),
                    ims=self._get_ims(row),
                    phones=self._get_value_map("Phone", row),
                    addresses=self._get_addresses(row),
                    organizations=self._get_organizations(row),
                    relations=self._get_value_map("Relation", row),
                    websites=self._get_value_map("Website", row),
                    events=self._get_events(row),
                    custom_fields=self._get_value_map("Custom Field", row),
                )
