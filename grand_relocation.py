import requests
import json


def get_grand_relocation_data():
    url = (
        "https://www.grandrelocation.nl/"
        "rts/collections/public/7ee1bdb9/"
        "runtime/collection/EAZLEE/query-data"
    )

    query = (
        "(filters:!("
        "(field:division,operator:eq,value:property),"
        "(field:tmp_label,operator:NIN,value:!('*')),"
        "(field:id,operator:NE,value:'*'),"
        "(field:tmp_city,operator:NE,value:'*'),"
        "(field:tmp_streetAddress,operator:NE,value:'*'),"
        "(field:tmp_property_type_1,operator:NE,value:'*'),"
        "(field:tmp_property_type_2,operator:NE,value:'*'),"
        "(field:tmp_property_type_3,operator:NE,value:'*'),"
        "(field:tmp_num_bedrooms,operator:GTE,value:'0'),"
        "(field:tmp_interior,operator:NE,value:'*'),"
        "(field:tmp_surface,operator:GTE,value:'0'),"
        "(field:tmp_forsale_price,operator:GTE,value:'0'),"
        "(field:po-api,operator:NE,value:'*')"
        "),"
        "sortBy:!((direction:asc,field:ranking)))"
    )

    params = {
        "pageSize": 100,
        "pageNumber": 0,
        "query": query,
        "language": "DUTCH",
    }

    headers = {
        "accept": "*/*",
        "accept-language": "en-US,en;q=0.9",
        "referer": "https://www.grandrelocation.nl/woning-aanbod?offer=any",
        "sec-ch-ua": '"Chromium";v="151", "Not=A?Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"macOS"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/151.0.0.0 Safari/537.36"
        ),
    }

    # IMPORTANT:
    # Use the cookies from your browser request if the API requires them.
    cookies = {
        "_dm_entry_referrer": "https://www.google.com",
        "dm_timezone_offset": "-120",
        "dm_last_visit": "1790338659916",
        "dm_total_visits": "14",
        "dm_last_page_view": "1790339254204",
        "dm_this_page_view": "1790339259855",
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        cookies=cookies,
        timeout=30,
    )

    print("HTTP STATUS:", response.status_code)
    print("CONTENT TYPE:", response.headers.get("content-type"))
    print()
    print("RAW RESPONSE:")
    print("=" * 100)
    # print(response.text[:10000])
    print("=" * 100)

    if response.status_code != 200:
        return None

    try:
        data = response.json()

        print("\nJSON RESPONSE:")
        # print(json.dumps(data, indent=2, ensure_ascii=False)[:20000])

        return data

    except ValueError:
        print("\nResponse was not JSON.")
        return None

def grandreloc():
    data = get_grand_relocation_data()
    count = 0;
    for item in data["values"]:
    # print("geldi")
    # property = item.get("name", item)
    # print(property)
    
        tamitem = item["data"]
        address = tamitem["address"]
        price = tamitem["price"]
        label = tamitem["label"]
        description = tamitem["description"]
        if label != "Verhuurd" and "Garantstellers worden niet geaccepteerd" not in description and int(price)  <= 1750:
            count = count + 1
            return (
                f"New home available at {address} for {price} "
                "which is also available for students"
            )
    if count == 0:
        return "❌ No homes available at Grand Relocation."










