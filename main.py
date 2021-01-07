"""This Python script provides examples on using the E*TRADE API endpoints"""
from __future__ import print_function

import time
import webbrowser

from rauth import OAuth1Service

from accounts.account import Account
from settings import *
from terminal.terminal import Term


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

    request_token, request_token_secret = etrade.get_request_token(params={"oauth_callback": "oob", "format": "json"})
    authorize_url = etrade.authorize_url.format(etrade.consumer_key, request_token)

    webbrowser.open(authorize_url)

    text_code = input("Please accept agreement and enter text code from browser: ")
    session = etrade.get_auth_session(request_token, request_token_secret, params={"oauth_verifier": text_code})
    return session, base_url, account_id


def main():
    s, u, a = oauth()
    account = Account(s, u, a)

    portfolio_data = account.get_portfolio()
    # balance_data = account.get_balance()
    with Term() as term:
        c = term.stdscr.getch()

        t1 = time.perf_counter()
        while True:
            t2 = time.perf_counter()
            if t2 > t1 + 1:
                t1 = t2
                portfolio_data = account.get_portfolio()

            term.show_portfolio(portfolio_data)

            if c == ord('q'):
                break

    # market = Market(session, base_url)
    # market.quotes()
    #
    # order = Order(self.session, self.account, self.base_url)
    # order.view_orders()


if __name__ == "__main__":
    main()
