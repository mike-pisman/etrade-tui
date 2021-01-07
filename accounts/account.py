import json

import pandas as pd

from accounts.portfolio import *
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
            if data is not None and "AccountListResponse" in data and "Accounts" in data["AccountListResponse"]:
                if "Account" in data["AccountListResponse"]["Accounts"]:
                    accounts = data["AccountListResponse"]["Accounts"]["Account"]
                    accounts[:] = [d for d in accounts if d.get('accountStatus') != 'CLOSED']
                    for account in accounts:
                        if account["accountId"] == self.account_id:
                            return account

            error(response, "Error: AccountList API service error")

    def get_portfolio(self):
        """
        Call portfolio API to retrieve a list of positions held in the specified account
        :param self: Passes in parameter authenticated session and information on selected account
        """

        # URL for the API endpoint
        url = self.base_url + "/v1/accounts/" + self.account["accountIdKey"] + "/portfolio.json"

        # Make API call for GET request
        response = self.session.get(url, params={'view': 'COMPLETE'}, header_auth=True)
        logger.debug("Request Header: %s", response.request.headers)

        # Handle and parse response
        if response is not None:
            if response.status_code == 200:
                parsed = json.loads(response.text)
                logger.debug("Response Body: %s", json.dumps(parsed, indent=4, sort_keys=True))
                data = response.json()
                portfolio = []

                if data is not None and "PortfolioResponse" in data and "AccountPortfolio" in data["PortfolioResponse"]:
                    for p in data["PortfolioResponse"]["AccountPortfolio"]:
                        if p is not None and "Position" in p:
                            portfolio.extend(p["Position"])

                    df = pd.DataFrame(portfolio)
                    portfolio = []

                    options = df["Product"].apply(pd.Series)
                    options = options.loc[options['securityType'] == 'OPTN']
                    cols = ['positionId', 'quantity', 'pricePaid', 'daysGain', 'daysGainPct', 'totalGain',
                            'totalGainPct']
                    options[cols] = df[cols]

                    complete = df["Complete"].apply(pd.Series)
                    options['bid'] = complete['bid']
                    options['ask'] = complete['ask']
                    options = options.rename(columns={"expiryYear": "year", "expiryMonth": "month", "expiryDay": "day"})
                    options["Date"] = pd.to_datetime(options[["year", "month", "day"]])

                    group = options.groupby(['Date', 'symbol'])

                    for name, g in group:
                        spreads = get_spreads(g)
                        legs = [Leg(g.iloc[i, :]) for i in range(len(g))]

                        position = Position(name, spreads, legs)
                        position.strategy = "Complex Strategy"

                        if len(legs) == 1:
                            direction = "Long" if legs[0].quantity > 0 else "Short"
                            position.strategy = direction + " " + legs[0].option_type

                        elif len(legs) == 2:
                            if legs[0].quantity == legs[1].quantity:
                                direction = "Long" if legs[0].quantity > 0 else "Short"
                                strategy = "Straddle" if legs[0].strike == legs[1].strike else "Strangle"
                                position.strategy = direction + " " + strategy

                        elif len(legs) == 4:
                            if len(spreads) == 2:
                                s0, s1 = spreads[0], spreads[1]
                                if s0.option_type != s1.option_type and s0.direction == s1.direction:
                                    direction = "Long" if s0.direction == "debit" else "Short"
                                    if s0.strikes[0] in s1.strikes or s0.strikes[0] in spreads[1].strikes:
                                        strategy = "Butterfly"
                                    else:
                                        strategy = "Iron Condor"
                                    position.strategy = direction + " " + strategy
                        portfolio.append(position)
                    return portfolio

            if response.status_code == 204:
                print("No Positions found")

        error(response, "Error: Portfolio API service error")
        return None

    # def get_portfolio():
    #     df = pd.read_pickle("testing.pkl")
    #     portfolio = []
    #
    #     options = df["Product"].apply(pd.Series)
    #     options = options.loc[options['securityType'] == 'OPTN']
    #     cols = ['positionId', 'quantity', 'pricePaid', 'daysGain', 'daysGainPct', 'totalGain', 'totalGainPct']
    #     options[cols] = df[cols]
    #
    #
    #     complete = df["Complete"].apply(pd.Series)
    #     options['bid'] = complete['bid']
    #     options['ask'] = complete['ask']
    #     options = options.rename(columns={"expiryYear": "year", "expiryMonth": "month", "expiryDay": "day"})
    #     options["Date"] = pd.to_datetime(options[["year", "month", "day"]])
    #
    #     group = options.groupby(['Date', 'symbol'])
    #
    #     for name, g in group:
    #         spreads = get_spreads(g)
    #         legs = [Leg(g.iloc[i, :]) for i in range(len(g))]
    #
    #         position = Position(name, spreads, legs)
    #         position.strategy = "Complex Strategy"
    #
    #         if len(legs) == 1:
    #             direction = "Long" if legs[0].quantity > 0 else "Short"
    #             position.strategy = direction + " " + legs[0].option_type
    #
    #         elif len(legs) == 2:
    #             if legs[0].quantity == legs[1].quantity:
    #                 direction = "Long" if legs[0].quantity > 0 else "Short"
    #                 strategy = "Straddle" if legs[0].strike == legs[1].strike else "Strangle"
    #                 position.strategy = direction + " " + strategy
    #
    #         elif len(legs) == 4:
    #             if len(spreads) == 2:
    #                 s0, s1 = spreads[0], spreads[1]
    #                 if s0.option_type != s1.option_type and s0.direction == s1.direction:
    #                     direction = "Long" if s0.direction == "debit" < 0 else "Short"
    #                     if s0.strikes[0] in s1.strikes or s0.strikes[0] in spreads[1].strikes:
    #                         strategy = "Butterfly"
    #                     else:
    #                         strategy = "Iron Condor"
    #                     position.strategy = direction + " " + strategy
    #         portfolio.append(position)
    #     return portfolio

    def get_balance(self):
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
                balance_data = {}
                data = data["BalanceResponse"]
                if data is not None:
                    balance_data["account_number"] = data.get("accountId", "")
                    balance_data["account_name"] = data.get("accountDescription", "")

                    if "Computed" in data:
                        if "RealTimeValues" in data["Computed"]:
                            balance_data["value"] = data["Computed"]["RealTimeValues"].get("totalAccountValue", 0)
                        balance_data["margin_bp"] = data["Computed"].get("marginBuyingPower", 0)
                        balance_data["cash_bp"] = data["Computed"].get("cashBuyingPower", 0)

                    return balance_data

        error(response, "Error: Balance API service error")
