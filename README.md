# Home Energy Dashboard

An open-source dashboard for a home solar-and-battery system. It shows how much energy the panels produce, how much the house uses, how much comes from or goes to the grid, and how the battery behaves through the day.

**[Live demo](https://avocadosaretheperfectfood.github.io/home-energy-dashboard/)**, which shows invented data for a fictional home.

> The demo uses generated sample data only. No real household data is, or will be, published in this repository.

## What the dashboard shows

- **Summary cards** for the last 30 days, 90 days, or year: solar produced, home use, share of home use covered without the grid, energy sent to the grid, and average battery output.
- **Daily energy chart** of solar, home use, energy from the grid, and energy to the grid. Longer ranges show weekly averages.
- **Battery chart** of energy charged and used each day.
- **Typical day by hour**, for warm months (June to September) and cool months (October to May), with the battery's charge level on a second axis.
- **Recent days, hour by hour**, with a date picker.
- **Honest gaps.** When the system reports no data, the charts show a gap, not a misleading zero.

## Design choices

- **Privacy first.** The page shows no dollar amounts and nothing finer than hourly detail, and real deployments are meant to show data with a delay. Secrets, configuration, and raw data are kept out of the repository by design.
- **Accessible.** The colors come from the Okabe-Ito palette, which stays distinguishable for most kinds of color blindness. The page follows the system's light or dark setting and works on phones. Each chart has a text description for screen readers.
- **Simple to host.** It's a static page with no build step and no server. The page reads a single data file.

## Run it yourself

You need Python 3.8 or newer (the standard library is enough) and a web browser.

    git clone https://github.com/AvocadosAreThePerfectFood/home-energy-dashboard.git
    cd home-energy-dashboard
    python3 tools/make_sample_data.py
    open docs/index.html

On Windows or Linux, open `docs/index.html` in your browser instead of using the last command. The page loads the Chart.js library from a public CDN, so it needs an internet connection.

## How the sample data works

`tools/make_sample_data.py` simulates a year for a fictional home with a 6.5 kW solar array and a 13 kWh battery. It models seasonal day length, cloudy days, morning and evening demand, a summer afternoon cooling load, a battery that stores surplus solar and covers the 4 to 9 p.m. window, and an 8-day outage. The generator uses a fixed random seed, so it produces the same data every time. Everything it produces is invented.

## Project layout

    docs/index.html            the dashboard page
    docs/site-data/data.js     the data the page reads (sample data)
    tools/make_sample_data.py  generates the sample data

## Status and roadmap

**Done**
- Dashboard front end
- Sample-data generator

**In progress**
- Data collection from the Enphase Enlighten API (free developer tier) and from a utility's Green Button CSV download
- Time-of-use rate-period labeling
- Rule-based alerts for system performance
- A daily plain-English summary written with a free-tier AI model

The collection and analysis code will be published as generic tools. Credentials, rate details, and personal data stay in private configuration and are never committed here.

## Notes

This project is independent. It isn't affiliated with or endorsed by Enphase Energy or any utility. Enphase is a trademark of Enphase Energy, Inc. Charts are drawn with [Chart.js](https://www.chartjs.org/) (MIT license).

## License

MIT. See [LICENSE](LICENSE).
