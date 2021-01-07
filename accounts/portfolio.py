class Spread:
    def __init__(self, leg1, leg2):
        self.leg1 = leg1  # Leg(leg1)
        self.leg2 = leg2  # Leg(leg2)

        self.date = self.leg1.date
        self.symbol = self.leg1.symbol
        self.quantity = abs(self.leg1.quantity)
        self.option_type = self.leg1.option_type
        self.direction = self.get_direction()
        self.strikes = (self.leg1.strike, self.leg2.strike)
        self.days_gain, self.days_gain_pct = self.get_days_gain()
        self.total_gain, self.total_gain_pct = self.get_total_gain()
        self.price_paid = self.get_price_paid()
        self.show_legs = False

    def get_direction(self):
        return "debit" if self.leg1.quantity < self.leg2.quantity and self.leg1.option_type == "PUT" else "credit"

    def get_days_gain(self):
        return round(self.leg1.days_gain + self.leg2.days_gain, 2), \
               round(self.leg1.days_gain_pct + self.leg2.days_gain_pct, 2)

    def get_total_gain(self):
        return round(self.leg1.total_gain + self.leg2.total_gain, 2), \
               round(self.leg1.total_gain_pct + self.leg2.total_gain_pct, 2)

    def get_price_paid(self):
        return round((self.leg1.price_paid * self.leg1.quantity + self.leg2.price_paid * self.leg2.quantity) * 100, 2)


class Leg:
    def __init__(self, leg):
        self.id = leg['positionId']
        self.date = leg['Date']
        self.symbol = leg['symbol']
        self.quantity = leg['quantity']
        self.option_type = leg['callPut']
        self.strike = leg['strikePrice']
        self.days_gain = round(leg['daysGain'], 2)
        self.days_gain_pct = round(leg['daysGainPct'], 2)
        self.total_gain = round(leg['totalGain'], 2)
        self.total_gain_pct = round(leg['totalGainPct'], 2)
        self.price_paid = leg['pricePaid']


class Position:
    def __init__(self, title, spreads, legs):
        self.spreads = spreads
        self.legs = legs
        self.date = title[0]
        self.symbol = title[1]
        self.strategy = ""
        self.days_gain, self.days_gain_pct = self.get_days_gain()
        self.total_gain, self.total_gain_pct = self.get_total_gain()
        self.show_spreads = False

    def get_days_gain(self):
        gain = 0
        gain_pct = 0
        for leg in self.legs:
            gain += leg.days_gain
            gain_pct += leg.days_gain_pct

        return round(gain, 2), round(gain_pct, 2)

    def get_total_gain(self):
        gain = 0
        gain_pct = 0
        for leg in self.legs:
            gain += leg.total_gain
            gain_pct += leg.total_gain_pct

        return round(gain, 2), round(gain_pct, 2)


def get_spreads(options_df):
    groups = options_df.groupby(['Date', 'symbol', 'callPut'])
    spreads = []

    for _, g in groups:
        g = g.sort_values('strikePrice').reset_index()
        l = list(g.index)

        for i in g.index:
            if g.loc[l[0], 'quantity'] + g.loc[i, 'quantity'] == 0:
                q = g.loc[l[0], 'quantity']
                s = Spread(Leg(g.loc[l[0], :]), Leg(g.loc[i, :]))

                spreads.append(s)
                l.remove(l[0])
                l.remove(i)
                if l:
                    i = 0
    return spreads
