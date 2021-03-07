import matplotlib.pyplot as plt
import pandas as pd

confirmed = pd.read_csv('covid19_confirmed.csv')
deaths = pd.read_csv('covid19_deaths.csv')
recovered = pd.read_csv('covid19_recovered.csv')

confirmed = confirmed.drop(['Province/State', 'Lat', 'Long'], axis=1)
deaths = deaths.drop(['Province/State', 'Lat', 'Long'], axis=1)
recovered = recovered.drop(['Province/State', 'Lat', 'Long'], axis=1)

confirmed = confirmed.groupby(confirmed['Country/Region']).aggregate('sum')
deaths = deaths.groupby(deaths['Country/Region']).aggregate('sum')
recovered = recovered.groupby(recovered['Country/Region']).aggregate('sum')

# Get transpose form
confirmed = confirmed.T
deaths = deaths.T
recovered = recovered.T

new_cases = confirmed.copy()

for day in range(1, len(confirmed)):
    new_cases.iloc[day] = confirmed.iloc[day] - confirmed.iloc[day - 1]

growth_rate = confirmed.copy()

for day in range(1, len(confirmed)):
    growth_rate.iloc[day] = (new_cases.iloc[day] / confirmed.iloc[day - 1]) * 100

active_cases = confirmed.copy()

for day in range(0, len(confirmed)):
    active_cases.iloc[day] = confirmed.iloc[day] - deaths.iloc[day] - recovered.iloc[day]

overall_growth_rate = confirmed.copy()

for day in range(0, len(confirmed)):
    overall_growth_rate.iloc[day] = (
            (active_cases.iloc[day] - active_cases.iloc[day - 1]) / active_cases.iloc[day - 1] * 100)

death_rate = confirmed.copy()

for day in range(0, len(confirmed)):
    death_rate.iloc[day] = (deaths.iloc[day] / confirmed.iloc[day]) * 100

hospitalization_rate_estimate = 0.05

hospitalization_needed = confirmed.copy()

for day in range(0, len(confirmed)):
    hospitalization_needed.iloc[day] = active_cases.iloc[day] * hospitalization_rate_estimate

# Visualization

countries = ['Italy', 'Austria', 'US', 'France', 'Spain']

# ax = plt.subplot()
# ax.set_facecolor('black')
# ax.figure.set_facecolor('#121212')
# ax.tick_params(axis='x', colors='white')
# ax.tick_params(axis='y', colors='white')
# ax.set_title('Covid-19 total confirmed cases by country', color='white')

# for country in countries:
# starts at day 35
# confirmed[country][35:].plot(label=country)

# plt.legend(loc='upper left')
# plt.show()

# for country in countries:
# ax = plt.subplot()
# ax.set_facecolor('black')
# ax.figure.set_facecolor('#121212')
# ax.tick_params(axis='x', colors='white')
# ax.tick_params(axis='y', colors='white')
# ax.set_title(f'Covid-19 growth rate in {country}', color='white')
# growth_rate[country].plot.bar()
# plt.show()

# ax = plt.subplot()
# ax.set_facecolor('black')
# ax.figure.set_facecolor('#121212')
# ax.tick_params(axis='x', colors='white')
# ax.tick_params(axis='y', colors='white')
# ax.set_title('Covid-19 total deaths by country', color='white')

# for country in countries:
# deaths[country].plot(label=country)

# plt.legend(loc='upper left')
# plt.show()

# for country in countries:
# ax = plt.subplot()
# ax.set_facecolor('black')
# ax.figure.set_facecolor('#121212')
# ax.tick_params(axis='x', colors='white')
# ax.tick_params(axis='y', colors='white')
# ax.set_title(f'Covid-19 death rate in {country}', color='white')
# death_rate[country].plot.bar()
# plt.show()

# for country in countries:
# ax = plt.subplot()
# ax.set_facecolor('black')
# ax.figure.set_facecolor('#121212')
# ax.tick_params(axis='x', colors='white')
# ax.tick_params(axis='y', colors='white')
# ax.set_title(f'Covid-19 actual growth rate of active cases in {country}', color='white')
# overall_growth_rate[country].plot.bar()
# plt.show()

simulated_growth_rate = 0.10

dates = pd.date_range(start="1/30/2021", periods=40, freq='D')
dates = pd.Series(dates)
dates = dates.dt.strftime('%m/%d/%Y')

simulated = confirmed.copy()
simulated = simulated.append(pd.DataFrame(index=dates))

for day in range(len(confirmed), len(confirmed) + 40):
    simulated.iloc[day] = simulated.iloc[day - 1] * (1 + simulated_growth_rate)

ax = plt.subplot()
ax.set_facecolor('black')
ax.figure.set_facecolor('#121212')
ax.tick_params(axis='x', colors='white')
ax.tick_params(axis='y', colors='white')
ax.set_title('Future simulation for France', color='white')
# simulated['France'].plot()
# plt.show()

estimated_death_rate = 0.025

# infected * death_rate = deaths
# infected = deaths / death_rate

print(deaths['France'].tail()[4] / estimated_death_rate)
