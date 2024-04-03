from typing import List
import csv

from tsc.types import ChargerType, Station


def to_csv(stations: List[Station], filepath: str):
    with open(filepath, "wt") as f:
        wr = csv.writer(f)
        wr.writerow(
            [
                "충전소명",
                "위도",
                "경도",
                "연중 무휴 여부",
                "충전기 타입",
                "충전 속도",
                "충전기 개수",
                "지번 주소",
                "도로명 주소",
            ]
        )

        for station in stations:
            charger_type_text = (
                "수퍼차저"
                if station.charger_type == ChargerType.SUPERCHARGER
                else "데스티네이션"
            )

            for charger in station.chargers:
                wr.writerow(
                    [
                        station.name,
                        station.coordinate.latitude,
                        station.coordinate.longitude,
                        "O" if station.is_always else "X",
                        charger_type_text,
                        int(charger.charging_speed),
                        charger.charger_count,
                        "",
                        "",
                    ]
                )
