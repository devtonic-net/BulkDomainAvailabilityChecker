import os
import re
import logging
import unicodedata
import random
import requests

# Project directory
BASE_DIR = os.path.realpath(os.path.dirname(__file__))

log_file_path = os.path.join(BASE_DIR, "log.log")
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)


class Eureg:
    """
    Class for interacting with the Eureg web API.
    """

    def __init__(self) -> None:
        """
        Initialize the Eureg object with API endpoints and headers.
        """
        # The TLDs the Eureg web API is able to lookup
        self.available_tlds = ["ro", "eu", "com", "net", "info", "org"]
        self.preferred_tlds = None
        self.max_domain_name_length = 63
        self.registration_endpoint = "https://www.eureg.ro/ro/inregistreaza/verifica-domeniu"
        self.multidomains_endpoint = "https://www.eureg.ro/ro/web-api/check-multi"
        self.user_agents = [
            "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
            "Mozilla/5.0 (Linux; Android 11; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Mobile Safari/537.36"
        ]
        self.headers = {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Alt-Used": "www.eureg.ro",
            "Connection": "keep-alive",
            "Referer": self.registration_endpoint,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        }

    def get_status(self, domain_names: list, preferred_tlds: list = None, return_available_only: bool = True) -> (list | None):
        """
        Get available data for the given domain name(s): registration status, registration and renewal prices
        and its overall value (if it's considered premium or not). For every domain name included in the list,
        it will check for up to 6 variations: mydomain.ro | *.eu | *.com | *.net | *.info | *.org. Limit the
        search to you preferred extensions by setting the 'preferred_tlds' parameter.
        
        Args:       
            domain_names (list): A list of domain name ideas (up to 70 elements).
            preferred_tlds (list): List of preferred TLDs: ["ro", "eu", "com", "net", "info", "org"]. Default is None.
            return_available_only (bool): Specify whether to return only 'available' domains. Default is True.

        Returns:
            list[dict] or None: A list of dictionaries containing details for each web domain, or None in case of an error.
        
        If any domain has the registration status 'pending', up to 10 checks are performed to overcome the
        standard response. If the status is still 'pending', the response is returned as such.

        Example of data returned by Eureg for a single webdomain: 
            {   
                'code': 'DOM12M',
                'idn': 'my-seo-domain.ro',
                'name': 'my-seo-domain.ro',
                'premium': 0,               # whether it's a premium domain name or not
                'price': '14.00',           # 'buy now' price, in Euros
                'registry_id': 17,
                'renew': '14.00',           # renewal price, in Euros
                'status': 'AVAILABLE',      # or 'NOT_AVAILABLE', or 'PENDING'
                'unit_price': '14.00'
            }
        """
        self.preferred_tlds = preferred_tlds
        domain_names = domain_names[:70]
        try_limit = 10

        for _ in range(try_limit):
            try:
                if not self._is_status_pending(domain_names):
                    results = self._check_domains(domain_names).get("data")
                    if results and return_available_only:
                        return [result for result in results if result.get("status", "").lower() == "available"]
                    return results
            except Exception as error:
                logging.error(f"Error gettig domain status: {error}")
                return None
        results = self._check_domains(domain_names).get("data")
        
        # Perform one final search
        if results and return_available_only:
            return [result for result in results if result.get("status", "").lower() == "available"]
        return self._check_domains(domain_names, preferred_tlds).get("data")
    
    def _get_cookies(self) -> requests.cookies.RequestsCookieJar:
        """
        Get the cookies for the session.
        
        Returns:
            requests.cookies.RequestsCookieJar: The cookie jar containing session cookies.
        """
        session = requests.Session()
        session.get(self.registration_endpoint)
        return session.cookies

    def _prepare_domains(self, domain_names: list) -> str:
        """
        Prepare domain names with different top-level domains (TLDs).
        
        Args:
            domain_names (list): A list of domain names.
        
        Returns:
            str: A string containing the comma-separated domain names with different TLDs.
        """
        web_domains = []
        for domain_name in domain_names:
            domain_slug = self._slugify(domain_name)
            if self.preferred_tlds is not None:                
                for pref_tld in self.preferred_tlds:
                    if pref_tld in self.available_tlds:
                        web_domains.append(f"{domain_slug}.{pref_tld}")
            else:
                for tld in self.available_tlds:
                    web_domains.append(f"{domain_slug}.{tld}")
        return ",".join(web_domains)

    
    def _is_status_pending(self, domain_names) -> bool:
        """
        Checks if any of the given domain names has status 'pending'.
        
        Args:
            domain_names (list): A list of domain names.
        
        Returns:
            bool: True if any domain is pending, False otherwise.
        """
        try:
            result = self._check_domains(domain_names)
            domain_dicts = result["data"]
            for domain_dict in domain_dicts:
                if domain_dict["status"].lower() == "pending":
                    return True
            return False
        except KeyError as error:
            logging.error(f"Error analyzing domain status: {error}")
            return False

    def _check_domains(self, domain_names: list) -> (list | None):
        """
        Check the status of the given domain names.
        
        Args:
            domain_names (list): A list of domain names.
        
        Returns:
            dict: JSON response containing domain status data.
        """
        try:
            cookies = self._get_cookies()
            names = self._prepare_domains(domain_names)
            params = {
                "names": names
            }

            response = requests.get(
                url=self.multidomains_endpoint,
                params=params,
                cookies=cookies,
                headers=self.headers,
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as error:
            logging.error(f"Error checking domain names: {error}")
            return None

    def _normalize_text(self, input: str) -> str:
        """
        Returns the normalized form (only compatible characters) of a Unicode string.
        Asian, Arabic and other special characters are returned as "/".

        Args:
            input (str): text to be processed.
        Returns:
            str: Text in normalized form
        """
        return unicodedata.normalize("NFKD", str(input)).encode("ascii", "ignore").decode("ascii")

    def _slugify(self, input_string: str) -> str:
        """
        Returns the 'clean slug' version of a given string.

        Args:
            input_string (str): string to be slugged.

        Returns:
            str: The slugified version of the input string.

        Replaces spaces, underscores and single quote marks. Removes any non-alphanumeric
        text and special characters. Converts string to lowercase. Removes leading and
        trailing whitespace.

        Example: 'Thë Best Sitè' will become 'the-best-site'
        """
        input_string = str(input_string)
        input_string = self._normalize_text(input_string)
        input_string = input_string[:self.max_domain_name_length]
        # Remove all non-word and non-space chars, replace white spaces with '-'
        input_string = re.sub(r"[^\w\s-]", "", input_string.lower())
        input_string = re.sub(r"[-\s]+", "-", input_string).strip("-_")
        return input_string
