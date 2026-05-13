"""Descarga resultados de Ironman y World Triathlon desde endpoints publicos.

El script guarda los CSVs siempre dentro de la carpeta `data`,
aunque se ejecute desde otra ubicacion. Si un CSV ya existe, no lo
vuelve a crear para evitar duplicados.
"""

from pathlib import Path
import time
import pandas as pd
import requests


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
IRONMAN_DIR = DATA_DIR / "ironman_2015_2025"
OLIMPICA_DIR = DATA_DIR / "olimpica_2016_2025"

IRONMAN_SOURCE_URL = "https://labs-v2.competitor.com/results/event/e798aa20-f278-e111-b16a-005056956277_Kona"
IRONMAN_API_URL = "https://labs-v2.competitor.com/api/results"
WORLD_TRIATHLON_BASE_URL = "https://events.triathlon.org"

HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": IRONMAN_SOURCE_URL}

IRONMAN_SUBEVENTS = [
    {"year": 2025, "name": "2025 IRONMAN World Championship - Women", "event_id": "e3bdd10e-80a5-48b3-bbf7-fda62ffb0824"},
    {"year": 2025, "name": "2025 IRONMAN World Championship - Men", "event_id": "13a8e2a2-e528-40a8-adb4-412b23364826"},
    {"year": 2024, "name": "2024 IRONMAN World Championship - Women", "event_id": "f2bd48fb-d595-4163-b090-f6b04089fa42"},
    {"year": 2024, "name": "2024 IRONMAN World Championship - Men", "event_id": "8ac0ab78-2ef7-4481-87da-044d8a032079"},
    {"year": 2023, "name": "2023 IRONMAN World Championship - Women", "event_id": "61a15e83-504c-43b5-8ff6-029b92ba5f2a"},
    {"year": 2023, "name": "2023 IRONMAN World Championship - Men", "event_id": "0209b19e-84e2-417e-be79-cb4dfdb02e3a"},
    {"year": 2022, "name": "2022 IRONMAN World Championship Thursday", "event_id": "1c0caffb-36cf-46f6-8f67-c1e7f7f428b8"},
    {"year": 2022, "name": "2022 IRONMAN World Championship Saturday", "event_id": "7e4970a2-c1e4-41d5-928c-46263005e39a"},
    {"year": 2021, "name": "2021 IRONMAN World Championship", "event_id": "0a7ac8ac-3bf4-4615-94f7-51ae16220699"},
    {"year": 2019, "name": "2019 IRONMAN World Championship Kukui Division", "event_id": "7b8fe9f3-87d2-ea11-a812-000d3a5a1cf8"},
    {"year": 2019, "name": "2019 IRONMAN World Championship", "event_id": "afaac1dc-73ba-e811-a967-000d3a37468c"},
    {"year": 2018, "name": "2018 IRONMAN World Championship", "event_id": "19c48b66-758e-e711-9419-005056951bf1"},
    {"year": 2017, "name": "2017 IRONMAN World Championship", "event_id": "a199a3a5-6674-e611-9410-005056951bf1"},
    {"year": 2016, "name": "2016 IRONMAN World Championship", "event_id": "9cb970f1-a951-e511-9409-005056951bf1"},
    {"year": 2015, "name": "2015 IRONMAN World Championship", "event_id": "d57bb0ac-432e-4d3e-a4ba-7ad7439b8b02"},
]

WORLD_TRIATHLON_EVENTS = [
    {"dataset": "olympic_games", "year": 2016, "slug": "2016-rio-de-janeiro-olympic-games", "event_id": 100636},
    {"dataset": "olympic_games", "year": 2020, "slug": "2020-tokyo-olympic-games", "event_id": 131299},
    {"dataset": "olympic_games", "year": 2024, "slug": "paris-2024-olympic-games", "event_id": 163893},
    {"dataset": "wtcs_final", "year": 2016, "slug": "2016-itu-world-triathlon-grand-final-cozumel", "event_id": 97645},
    {"dataset": "wtcs_final", "year": 2017, "slug": "2017-itu-world-triathlon-grand-final-rotterdam", "event_id": 107164},
    {"dataset": "wtcs_final", "year": 2018, "slug": "2018-itu-world-triathlon-grand-final-gold-coast", "event_id": 117107},
    {"dataset": "wtcs_final", "year": 2019, "slug": "2019-itu-world-triathlon-grand-final-lausanne", "event_id": 127488},
    {"dataset": "wtcs_final", "year": 2021, "slug": "2021-world-triathlon-grand-final-edmonton", "event_id": 130051},
    {"dataset": "wtcs_final", "year": 2022, "slug": "2022-world-triathlon-championship-finals-abu-dhabi", "event_id": 163568},
    {"dataset": "wtcs_final", "year": 2023, "slug": "2023-world-triathlon-championship-finals-pontevedra", "event_id": 170132},
    {"dataset": "wtcs_final", "year": 2024, "slug": "2024-world-triathlon-championship-finals-torremolinos", "event_id": 183767},
    {"dataset": "wtcs_final", "year": 2025, "slug": "2025-world-triathlon-championships-finals-wollongong", "event_id": 188992},
]


def save_csv_if_missing(df: pd.DataFrame, path: Path) -> None:
    """Guarda un CSV solo si no existe ya en disco."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        print(f"Ya existe, no se duplica: {path.relative_to(ROOT_DIR)}")
        return
    df.to_csv(path, index=False, encoding="utf-8-sig")
    print(f"CSV creado: {path.relative_to(ROOT_DIR)} -> {df.shape}")


def get_ironman_results(event_id: str) -> list[dict]:
    response = requests.get(
        IRONMAN_API_URL,
        params={"wtc_eventid": event_id},
        headers=HEADERS,
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    return data["resultsJson"]["value"]


def normalize_ironman_row(row: dict, event: dict) -> dict:
    contact = row.get("wtc_ContactId") or {}
    country = row.get("wtc_CountryRepresentingId") or {}
    age_group = row.get("wtc_AgeGroupId") or {}

    return {
        "championship_year": event["year"],
        "event_name": event["name"],
        "event_id": event["event_id"],
        "source_url": IRONMAN_SOURCE_URL,
        "source_api_url": f"{IRONMAN_API_URL}?wtc_eventid={event['event_id']}",
        "athlete": row.get("athlete") or contact.get("fullname"),
        "first_name": contact.get("firstname"),
        "last_name": contact.get("lastname"),
        "bib": row.get("bib") or row.get("wtc_bibnumber"),
        "bib_display": row.get("wtc_bibnumber_v2"),
        "country_iso2": row.get("countryiso2") or country.get("wtc_iso2"),
        "country_iso3": country.get("wtc_iso3"),
        "country": country.get("wtc_name"),
        "gender": age_group.get("wtc_gender_formatted") or contact.get("gendercode_formatted"),
        "age_group": row.get("_wtc_agegroupid_value_formatted"),
        "finisher": row.get("wtc_finisher"),
        "dnf": row.get("wtc_dnf"),
        "dns": row.get("wtc_dns"),
        "dq": row.get("wtc_dq"),
        "finish_time": row.get("wtc_finishtimeformatted"),
        "finish_seconds": row.get("wtc_finishtime"),
        "swim_time": row.get("wtc_swimtimeformatted"),
        "swim_seconds": row.get("wtc_swimtime"),
        "t1_time": row.get("wtc_transition1timeformatted"),
        "t1_seconds": row.get("wtc_transition1time"),
        "bike_time": row.get("wtc_biketimeformatted"),
        "bike_seconds": row.get("wtc_biketime"),
        "t2_time": row.get("wtc_transitiontime2formatted"),
        "t2_seconds": row.get("wtc_transition2time"),
        "run_time": row.get("wtc_runtimeformatted"),
        "run_seconds": row.get("wtc_runtime"),
        "finish_rank_overall": row.get("wtc_finishrankoverall"),
        "finish_rank_gender": row.get("wtc_finishrankgender"),
        "finish_rank_group": row.get("wtc_finishrankgroup"),
        "swim_rank_overall": row.get("wtc_swimrankoverall"),
        "swim_rank_gender": row.get("wtc_swimrankgender"),
        "swim_rank_group": row.get("wtc_swimrankgroup"),
        "bike_rank_overall": row.get("wtc_bikerankoverall"),
        "bike_rank_gender": row.get("wtc_bikerankgender"),
        "bike_rank_group": row.get("wtc_bikerankgroup"),
        "run_rank_overall": row.get("wtc_runrankoverall"),
        "run_rank_gender": row.get("wtc_runrankgender"),
        "run_rank_group": row.get("wtc_runrankgroup"),
        "total_distance_completed_km": row.get("wtc_totaldistancecompleted"),
        "swim_distance_completed_km": row.get("wtc_swimdistancecompleted"),
        "bike_distance_completed_km": row.get("wtc_bikedistancecompleted"),
        "run_distance_completed_km": row.get("wtc_rundistancecompleted"),
        "result_id": row.get("wtc_resultid"),
        "created_on": row.get("createdon"),
        "modified_on": row.get("modifiedon"),
    }


def download_ironman() -> None:
    IRONMAN_DIR.mkdir(parents=True, exist_ok=True)
    combined_path = IRONMAN_DIR / "ironman_wc_2015_2025_all_results.csv"
    pro_path = IRONMAN_DIR / "ironman_wc_2015_2025_pro_results.csv"

    if combined_path.exists() and pro_path.exists():
        print("Ironman: los CSVs combinados ya existen. No se vuelven a descargar.")
        return

    all_rows = []
    for event in IRONMAN_SUBEVENTS:
        print(f"Descargando Ironman {event['year']} - {event['name']}")
        raw_results = get_ironman_results(event["event_id"])
        normalized_rows = [normalize_ironman_row(row, event) for row in raw_results]
        df_event = pd.DataFrame(normalized_rows)
        all_rows.extend(normalized_rows)

        for gender, df_gender in df_event.groupby("gender", dropna=False):
            gender_name = str(gender).lower() if pd.notna(gender) else "unknown"
            file_name = f"ironman_wc_{event['year']}_{gender_name}_results.csv"
            save_csv_if_missing(df_gender, IRONMAN_DIR / file_name)

        time.sleep(0.3)

    ironman_all = pd.DataFrame(all_rows)
    save_csv_if_missing(ironman_all, combined_path)

    ironman_pro = ironman_all[ironman_all["age_group"].isin(["MPRO", "FPRO"])]
    save_csv_if_missing(ironman_pro, pro_path)


def get_json(url: str) -> dict:
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
    response.raise_for_status()
    return response.json()


def get_programs(event_id: int) -> list[dict]:
    url = f"{WORLD_TRIATHLON_BASE_URL}/api/programs/{event_id}"
    return get_json(url)["data"]


def get_world_triathlon_results(event_id: int, program_id: int) -> dict:
    url = f"{WORLD_TRIATHLON_BASE_URL}/api/results/{event_id}/{program_id}"
    return get_json(url)["data"]


def normalize_world_triathlon_result(result_data: dict, event_info: dict) -> list[dict]:
    rows = []
    headers = result_data.get("headers") or []
    event = result_data.get("event") or {}

    for athlete in result_data.get("results") or []:
        row = {
            "dataset": event_info["dataset"],
            "championship_year": event_info["year"],
            "event_id": result_data.get("event_id"),
            "event_title": event.get("event_title"),
            "event_slug": event.get("event_slug"),
            "event_country": event.get("event_country"),
            "program_id": result_data.get("prog_id"),
            "program_name": result_data.get("prog_name"),
            "program_date": result_data.get("prog_date"),
            "gender": result_data.get("prog_gender"),
            "athlete_id": athlete.get("athlete_id"),
            "athlete_full_name": athlete.get("athlete_full_name"),
            "athlete_first": athlete.get("athlete_first"),
            "athlete_last": athlete.get("athlete_last"),
            "athlete_noc": athlete.get("athlete_noc"),
            "athlete_country_name": athlete.get("athlete_country_name"),
            "athlete_yob": athlete.get("athlete_yob"),
            "athlete_age": athlete.get("athlete_age"),
            "position": athlete.get("position"),
            "total_time": athlete.get("total_time"),
            "start_num": athlete.get("start_num"),
            "result_id": athlete.get("result_id"),
            "source_url": f"{WORLD_TRIATHLON_BASE_URL}/{event_info['slug']}/results?program={result_data.get('prog_id')}",
            "source_api_url": f"{WORLD_TRIATHLON_BASE_URL}/api/results/{result_data.get('event_id')}/{result_data.get('prog_id')}",
        }

        splits = athlete.get("splits") or []
        for index, header in enumerate(headers):
            segment_name = header.get("name", "").lower()
            if segment_name == "swim":
                row["swim"] = splits[index] if index < len(splits) else None
            elif segment_name == "t1":
                row["t1"] = splits[index] if index < len(splits) else None
            elif segment_name == "bike":
                row["bike"] = splits[index] if index < len(splits) else None
            elif segment_name == "t2":
                row["t2"] = splits[index] if index < len(splits) else None
            elif segment_name == "run":
                row["run"] = splits[index] if index < len(splits) else None

        rows.append(row)

    return rows


def download_world_triathlon() -> None:
    OLIMPICA_DIR.mkdir(parents=True, exist_ok=True)
    combined_path = OLIMPICA_DIR / "olimpica_2016_2025_all_results.csv"

    if combined_path.exists():
        print("World Triathlon: el CSV combinado ya existe. No se vuelve a descargar.")
        return

    all_rows = []
    for event_info in WORLD_TRIATHLON_EVENTS:
        print(f"Descargando World Triathlon {event_info['year']} - {event_info['slug']}")
        programs = get_programs(event_info["event_id"])
        elite_programs = [
            program for program in programs
            if program.get("prog_name") in ["Elite Men", "Elite Women"]
            and program.get("results") is True
        ]

        for program in elite_programs:
            result_data = get_world_triathlon_results(event_info["event_id"], program["prog_id"])
            rows = normalize_world_triathlon_result(result_data, event_info)
            df_program = pd.DataFrame(rows)
            all_rows.extend(rows)

            gender = result_data.get("prog_gender")
            file_name = f"{event_info['dataset']}_{event_info['year']}_{gender}_results.csv"
            save_csv_if_missing(df_program, OLIMPICA_DIR / file_name)
            time.sleep(0.3)

    olimpica_all = pd.DataFrame(all_rows)
    save_csv_if_missing(olimpica_all, combined_path)


def main() -> None:
    print(f"Raiz del proyecto: {ROOT_DIR}")
    print(f"Carpeta de datos: {DATA_DIR}")
    download_ironman()
    download_world_triathlon()


if __name__ == "__main__":
    main()
