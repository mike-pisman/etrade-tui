import curses

TF = "{:1}{:^16}{:^8}{:^5}{:^20}{:^20}{:^16}{:^16}{:^16}{:^16}{:^16}"


class Term:
    def __init__(self):
        self.stream = []
        self.vposition = 0

        self.stdscr = curses.initscr()
        self.stdscr.keypad(True)
        self.stdscr.nodelay(True)
        self.stdscr.clear()

        curses.cbreak()
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        curses.noecho()

        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        curses.nocbreak()  # Turn off cbreak mode
        curses.echo()  # Turn echo back on
        curses.curs_set(1)  # Turn cursor back on
        curses.endwin()

    def tprint(self, text):
        self.stream.append(text)

    def get_portfolio_stream(self, portfolio):
        tp = self.tprint

        header = TF.format(" ", "Date", "Symbol", "Q", "Type", "Strike Prices", "Price Paid $", "Day Gain $",
                           "Day Gain %", "Total Gain $", "Total Gain %")

        # tp(self.ljust(self.bold(header)))
        tp(header)
        # tp(self.ljust('', self.width, '═'))

        for position in portfolio:
            spread_ids = []
            txt = TF.format("▼" if position.show_spreads else "▶", position.date.strftime("%b %d '%y"), position.symbol,
                            "", position.strategy, "", "",
                            position.days_gain, position.days_gain_pct,
                            position.total_gain, position.total_gain_pct)
            # tp(self.bold(self.ljust(txt)))
            tp(txt)

            if position.show_spreads:
                for s in position.spreads:
                    spread_ids.append(s.leg1.id)
                    spread_ids.append(s.leg2.id)

                    txt = TF.format('', '', "▼" if s.show_legs else "▶", s.quantity,
                                    s.option_type.capitalize() + " " + s.direction.capitalize() +
                                    " Spread" + "s" * int(s.quantity > 1),
                                    str(s.strikes[0]) + " / " + str(s.strikes[1]), s.price_paid,
                                    s.days_gain, s.days_gain_pct, s.total_gain, s.total_gain_pct)
                    tp(txt)

                    if s.show_legs:
                        tp(TF.format('', '', '', s.leg1.quantity, s.leg1.option_type, s.leg1.strike, s.leg1.price_paid,
                                     s.leg1.days_gain, s.leg1.days_gain_pct, s.leg1.total_gain, s.leg1.total_gain_pct))
                        tp(TF.format('', '', '', s.leg2.quantity, s.leg2.option_type, s.leg2.strike, s.leg2.price_paid,
                                     s.leg2.days_gain, s.leg2.days_gain_pct, s.leg2.total_gain, s.leg2.total_gain_pct))

                for leg in position.legs:
                    if leg.id not in spread_ids:
                        tp(TF.format('', '', '', leg.quantity, leg.option_type, leg.strike, leg.price_paid,
                                     leg.days_gain,
                                     leg.days_gain_pct, leg.total_gain, leg.total_gain_pct))

            # tp(self.ljust('', self.width, '─'))
        result = self.stream
        self.stream = []
        return result

    def show_portfolio(self, portfolio):
        pad = curses.newpad(1, 1)

        wh, ww = self.stdscr.getmaxyx()

        p = self.get_portfolio_stream(portfolio)
        pad.resize(len(p) + 1 + wh, len(p[0]) + 1)
        ph, pw = pad.getmaxyx()

        for y, i in enumerate(p):
            if y == self.vposition:
                pad.addstr(y, 0, i, curses.color_pair(1))
            else:
                pad.addstr(y, 0, i)

        pad_position = wh * (self.vposition // wh)
        pad.refresh(pad_position, 0, 0, 0, wh - 1, ww - 1)
        self.stdscr.refresh()
        c = self.stdscr.getch()
        if c == curses.KEY_DOWN:
            self.vposition += 1
        elif c == curses.KEY_UP:
            self.vposition -= 1
        elif c == ord(' '):
            portfolio[self.vposition - 1].show_spreads = not portfolio[self.vposition - 1].show_spreads

            self.vposition = max(min(self.vposition, ph - wh - 2), 1)
            # else:
            #    first_pass = False

            pad.erase()

    def show_balance(self, balance_data):
        pad = curses.newpad(80, 7)
        self.stream = []

        self.tprint("  ======|  Account  |======")
        self.tprint("Account Number: " + balance_data["account_nameId"])
        self.tprint("Account Name: " + balance_data["accountDescription"])
        self.tprint("Value: " + str('${:,.2f}'.format(balance_data["value"])))
        self.tprint("Margin: " + str('${:,.2f}'.format(balance_data["margin_bp"])))
        self.tprint("Cash: " + str('${:,.2f}'.format(balance_data["cash_bp"])))
        self.tprint("  ======| Portfolio |======")

        for y, i in enumerate(self.stream):
            pad.addstr(y, 0, i)
