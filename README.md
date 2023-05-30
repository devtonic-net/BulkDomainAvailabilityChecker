# Bulk Domain Availability Checker

![Bulk Domain Availability Checker](https://i.imgur.com/NP4FxGT.png)

This script is a powerful tool that allows you to perform bulk availability checks for up to 420 web domains using the Eureg.ro web API.
By leveraging reverse engineering techniques, it interacts with the Eureg server to retrieve domain registration status for multiple domains at once.
It provides information about the registration status, registration and renewal prices, and overall value of each domain.

## Features

- Bulk check domain availability: Easily check the availability of up to 420 web domains (70 keywords with 6 separate TLDs each) in a single request.
- Supports six top-level domains (TLDs): ".ro", ".eu", ".com", ".net", ".info", and ".org".
- Option to specify preferred TLDs for a more focused search.
- Returns detailed information for each domain, including the status (available, not available, or pending), price, premium status, and more.
- Reverse-engineered API integration: Utilizes reverse engineering techniques to interact with the Eureg web API and fetch accurate registration status information.
- Handles cases where the registration status is pending, making multiple attempts to retrieve the final status.
- Customizable and extensible: Modify and extend the script to suit your specific requirements and integrate with your existing systems.
- Error handling: Implements error handling mechanisms to handle potential exceptions during the API interaction.
- Logs errors to a file for debugging purposes.

## Installation

1. Clone or download the repository.
2. Install the only required dependency by running the following command:

```pip install requests```

## Example Usage

1. Import the Eureg class from the script:
```from eureg import Eureg```

2. Create an instance of the Eureg class:
```eureg = Eureg()```

3. Use the ```get_status``` method to check the availability of domain names:

```keyword_ideas = ["science blog", "how to make money"]```

```python
results = eureg.get_status(domain_names=keyword_ideas, preferred_tlds=["ro", "com"], return_available_only=False
```

- Optional parameters:
```preferred_tlds```: List of preferred TLDs to narrow down the search (e.g., ["ro", "com"]). Default is None.
```return_available_only```: Specify whether to return only available domains. Default is True.

- The get_status method returns a list of dictionaries, with each dictionary containing details for a domain. Example structure:

## Example result

```python
[
    {
        'code': 'DOM12M',
        'idn': 'science-blog.ro',
        'name': 'science-blog.ro',
        'premium': 0,               # whether it's a premium domain name or not
        'price': '9.00',            # domain price, in Euros
        'registry_id': 0,
        'status': 'AVAILABLE',      # or 'NOT_AVAILABLE', or 'PENDING'
        'unit_price': '9.00'
    },
    {
        'idn': 'science-blog.com',
        'name': 'science-blog.com',
        'status': 'NOT_AVAILABLE'
    },
    {
        'code': 'DOM12M',
        'idn': 'how-to-make-money.ro',
        'name': 'how-to-make-money.ro',
        'premium': 0,
        'price': '9.00',
        'registry_id': 0,
        'status': 'AVAILABLE',
        'unit_price': '9.00'},
    {
        'idn': 'how-to-make-money.com',
        'name': 'how-to-make-money.com',
        'status': 'NOT_AVAILABLE'
    },
]
```

## Logging

The script logs any errors encountered during domain status checks to a log file (log.log) located in the same directory as the script. This helps in troubleshooting and debugging issues.

## Notes

- The Eureg web API limits the number of domain names that can be checked in a single request to 70. If the provided list exceeds this limit, the surplus elements will be discarded before calling the API.
- In case a domain has the registration status 'pending', the script will make up to 10 attempts to retrieve the final status. If the status remains 'pending' after all attempts, the response will indicate this.

## License

This project is licensed under the MIT License.

**Note**: Please ensure compliance with Eureg's terms of service and usage policies when utilizing this script.
