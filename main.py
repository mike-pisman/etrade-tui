"""This Python script provides examples on using the E*TRADE API endpoints"""
from __future__ import print_function

import curses
import sys
import webbrowser

from blessed import Terminal
from rauth import OAuth1Service

from accounts.account import Account
from settings import *


def oauth():
    """Allows user authorization for the sample application with OAuth 1"""
    etrade = OAuth1Service(
        name="etrade",
        consumer_key=config["DEFAULT"]["CONSUMER_KEY"],
        consumer_secret=config["DEFAULT"]["CONSUMER_SECRET"],
        request_token_url="https://api.etrade.com/oauth/request_token",
        access_token_url="https://api.etrade.com/oauth/access_token",
        authorize_url="https://us.etrade.com/e/t/etws/authorize?key={}&token={}",
        base_url="https://api.etrade.com")

    base_url = config["DEFAULT"]["PROD_BASE_URL"]
    account_id = config["DEFAULT"]["ACCOUNT_NUMBER"]

    # Step 1: Get OAuth 1 request token and secret
    request_token, request_token_secret = etrade.get_request_token(params={"oauth_callback": "oob", "format": "json"})
    authorize_url = etrade.authorize_url.format(etrade.consumer_key, request_token)
    webbrowser.open(authorize_url)
    text_code = input("Please accept agreement and enter text code from browser: ")
    session = etrade.get_auth_session(request_token, request_token_secret, params={"oauth_verifier": text_code})
    return session, base_url, account_id


def main():
    s, u, a = oauth()
    account = Account(s, u, a)

    _ = curses.initscr()
    term = Terminal()
    assert term.hpa(1) != u'', (
        'Terminal does not support hpa (Horizontal position absolute)')

    with term.cbreak():
        # market = Market(session, base_url)
        # market.quotes()

        # print("Account Number: " + balance_data.get("accountId", ""))
        # print("Account Name: " + balance_data.get("accountDescription", ""))
        # print("Net Account Value: " + str('${:,.2f}'.format(balance)))
        # print("Margin Buying Power: " + str('${:,.2f}'.format(margin_bp)))
        # print("Cash Buying Power: " + str('${:,.2f}'.format(cash_bp)))

        # self.balance()
        # self.portfolio()
        # order = Order(self.session, self.account, self.base_url)
        # order.view_orders()

        while True:
            curses.curs_set(0)

            balance_data = account.balance()
            if "Computed" in balance_data:
                if "RealTimeValues" in balance_data["Computed"]:
                    balance = balance_data["Computed"]["RealTimeValues"].get("totalAccountValue", 0)
                margin_bp = balance_data["Computed"].get("marginBuyingPower", 0)
                cash_bp = balance_data["Computed"].get("cashBuyingPower", 0)

            sys.stderr.write(term.move_yx(0, 1) + "  ====| Account |====")
            sys.stderr.write(term.move_yx(1, 1) + "Account Number: " + balance_data.get("accountId", ""))
            sys.stderr.write(term.move_yx(2, 1) + "Account Name: " + balance_data.get("accountDescription", ""))
            sys.stderr.write(term.move_yx(3, 1) + "Net Account Value: " + str('${:,.2f}'.format(balance)))
            sys.stderr.write(term.move_yx(4, 1) + "Margin Buying Power: " + str('${:,.2f}'.format(margin_bp)))
            sys.stderr.write(term.move_yx(5, 1) + "Cash Buying Power: " + str('${:,.2f}'.format(cash_bp)))

            sys.stderr.flush()
            inp = term.inkey(1)
    print()


if __name__ == "__main__":
    main()
