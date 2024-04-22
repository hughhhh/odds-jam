from typing import Any, Dict, Optional
from prettytable import PrettyTable
from datetime import datetime
from time import sleep

import csv
import click
import requests
import typing
import json


def f_get(data: Dict[Any, Any], path: str) -> Optional[Any]:
    """
    Retrieves a value from a nested dictionary using a dot-separated key path.

    Parameters:
        data (dict): The dictionary from which to retrieve the value.
        path (str): The dot-separated path to the value in the dictionary.

    Returns:
        The value at the specified path if it exists, None otherwise.
    """
    keys = path.split(".")
    try:
        for key in keys:
            if isinstance(data, list):
                # Convert key to integer index for list access
                key = int(key)
            data = data[key]
        return data
    except (KeyError, TypeError, ValueError, IndexError):
        return None


@click.group()
def cli():
    pass


def fetch_sportsbooks_data(
    url: str, params: Dict[str, Any], headers: Dict[str, Any], timeout: int = 10
):
    try:
        response = requests.get(
            url=url,
            params=params,
            headers=headers,
            timeout=timeout,  # Timeout for the request in seconds
        )
        # Check if the request was successful
        response.raise_for_status()
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Error connecting: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Error during request: {req_err}")
    else:
        print("Request successful. Response:", response)
    return response.json()


def fetch_draftkings_sportbook():
    sportbook = "draftkings"
    sport = "basketball"
    data = fetch_sportsbooks_data(
        url="https://sportsbook-nash-usny.draftkings.com/sites/US-NY-SB/api/v5/eventgroups/42648",
        params={
            "format": "json",
        },
        headers={
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        },
    )

    fieldnames = [
        "sportbookName",
        "sportName",
        "league",
        "eventName",
        "gameTime",
        "marketName",
        "retrievedAt",
        "betSelection",
        "priceSelection",
        "isLocked",
    ]
    FILENAME = 'draftkings.csv'
    with open(FILENAME, "w", newline="") as file:
        # intialize csv class
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        league = f_get(data, "eventGroup.nameIdentifier")
        offers = f_get(
            data,
            "eventGroup.offerCategories.0.offerSubcategoryDescriptors.0.offerSubcategory.offers",
        )
        for idx, offer in enumerate(offers):
            odds = []
            favorite = None
            for item in offer:
                is_open = f_get(item, "isOpen")
                outcomes = f_get(item, "outcomes")
                for outcome in outcomes:
                    # the ordering of the odds will always be this for the odds list
                    # spread - odds[:1], totals - odds[1:2], moneline odds[2:3]
                    odds.append(
                        (
                            outcome.get("participant") or outcome.get("label"),
                            outcome.get("line"),
                            outcome.get("oddsAmerican"),
                        )
                    )
            market_odds = {
                "totals": odds[:2],
                "spreads": odds[2:4],
                "money_line": odds[4:],
            }
            start_time = f_get(data, f"eventGroup.events.{idx}.startDate")
            event_name = f_get(data, f"eventGroup.events.{idx}.nameIdentifier")
            for market, odds in market_odds.items():
                for odd in odds:
                    writer.writerow(
                        {
                            "sportbookName": sportbook,
                            "sportName": sport,
                            "league": league,
                            "gameTime": start_time,
                            "marketName": market,
                            "retrievedAt": datetime.now(),
                            "eventName": event_name,
                            "betSelection": (
                                f"{odd[0]} {odd[1]}"
                                if market != "money_line"
                                else odd[0]
                            ),
                            "priceSelection": odd[2],
                            "isLocked": is_open,
                        }
                    )

@click.command()
@click.option("--poll", is_flag=True, help="Poll updating the csv every 5 seconds")
def draftkings(poll: bool):
    while poll:
        # Stay in while loop while grabbing data and writing 
        # to csv wait for 5 seconds before executing again
        fetch_draftkings_sportbook()
        print(f"Updating csv ...")
        sleep(5)

    # run only once!
    fetch_draftkings_sportbook()
    print(f"Successfully pulled the odds for draftkings please take look at csv for the results 🚀")

cli.add_command(draftkings)

if __name__ == "__main__":
    cli()
