import json

from settings import *


# Handle errors
def error(response, msg):
    logger.debug("Response Body: %s", response.text)
    if response is not None and response.headers['Content-Type'] == 'application/json' \
            and "Error" in response.json() and "message" in response.json()["Error"] \
            and response.json()["Error"]["message"] is not None:
        print("Error: " + response.json()["Error"]["message"])
    else:
        print(msg)


class Account:
    def __init__(self, session, base_url, account_id):
        """
        Initialize Accounts object with session and account information

        :param session: authenticated session
        """
        self.account_id = account_id
        self.session = session
        self.base_url = base_url
        self.account = self.get_account()

    def get_account(self):
        """
        Calls account list API to retrieve a list of the user's E*TRADE accounts

        :param self:Passes in parameter authenticated session
        """

        # URL for the API endpoint
        url = self.base_url + "/v1/accounts/list.json"

        # Make API call for GET request
        response = self.session.get(url, header_auth=True)
        logger.debug("Request Header: %s", response.request.headers)

        # Handle and parse response
        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            logger.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))

            data = response.json()
            if data is not None and "AccountListResponse" in data and "Accounts" in data[
                "AccountListResponse"] and "Account" in data["AccountListResponse"]["Accounts"]:
                accounts = data["AccountListResponse"]["Accounts"]["Account"]
                accounts[:] = [d for d in accounts if d.get('accountStatus') != 'CLOSED']
                for account in accounts:
                    if account["accountId"] == self.account_id:
                        return account

            error(response, "Error: AccountList API service error")

    def portfolio(self):
        """
        Call portfolio API to retrieve a list of positions held in the specified account

        :param self: Passes in parameter authenticated session and information on selected account
        """

        # URL for the API endpoint
        url = self.base_url + "/v1/accounts/" + self.account["accountIdKey"] + "/portfolio.json"

        # Make API call for GET request
        response = self.session.get(url, header_auth=True)
        logger.debug("Request Header: %s", response.request.headers)

        print("\nPortfolio:")

        # Handle and parse response
        if response is not None:
            if response.status_code == 200:
                parsed = json.loads(response.text)
                logger.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))
                data = response.json()

                if data is not None and "PortfolioResponse" in data and "AccountPortfolio" in data["PortfolioResponse"]:
                    for acctPortfolio in data["PortfolioResponse"]["AccountPortfolio"]:
                        if acctPortfolio is not None and "Position" in acctPortfolio:
                            for position in acctPortfolio["Position"]:
                                print_str = ""
                                if position is not None and "symbolDescription" in position:
                                    print_str = print_str + "Symbol: " + str(position["symbolDescription"])
                                if position is not None and "quantity" in position:
                                    print_str = print_str + " | " + "Quantity #: " + str(position["quantity"])
                                if position is not None and "Quick" in position and "lastTrade" in position["Quick"]:
                                    print_str = print_str + " | " + "Last Price: " \
                                                + str('${:,.2f}'.format(position["Quick"]["lastTrade"]))
                                if position is not None and "pricePaid" in position:
                                    print_str = print_str + " | " + "Price Paid: " \
                                                + str('${:,.2f}'.format(position["pricePaid"]))
                                if position is not None and "totalGain" in position:
                                    print_str = print_str + " | " + "Total Gain: " \
                                                + str('${:,.2f}'.format(position["totalGain"]))
                                if position is not None and "marketValue" in position:
                                    print_str = print_str + " | " + "Value: " \
                                                + str('${:,.2f}'.format(position["marketValue"]))
                                print(print_str)
                        else:
                            print("No positions")
            elif response.status_code == 204:
                print("No account")
        error(response, "Error: Portfolio API service error")

    def balance(self):
        """
        Calls account balance API to retrieve the current balance and related details for a specified account

        :param self: Pass in parameters authenticated session and information on selected account
        """

        # URL for the API endpoint
        url = self.base_url + "/v1/accounts/" + self.account["accountIdKey"] + "/balance.json"

        # Add parameters and header information
        params = {"instType": self.account["institutionType"], "realTimeNAV": "true"}
        headers = {"consumerkey": config["DEFAULT"]["CONSUMER_KEY"]}

        # Make API call for GET request
        response = self.session.get(url, header_auth=True, params=params, headers=headers)
        logger.debug("Request url: %s", url)
        logger.debug("Request Header: %s", response.request.headers)

        # Handle and parse response
        if response is not None and response.status_code == 200:
            parsed = json.loads(response.text)
            logger.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))
            data = response.json()
            if data is not None and "BalanceResponse" in data:
                balance_data = data["BalanceResponse"]
                if balance_data is not None:
                    return balance_data

        error(response, "Error: Balance API service error")
