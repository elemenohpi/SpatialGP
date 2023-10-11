footballers_goals = {'Eusebio': 120, 'Cruyff': 104, 'Pele': 150, 'Ronaldo': 132, 'Messi': 125}
print(footballers_goals.items())
sorted_footballers_by_goals = sorted(footballers_goals.items(), key=lambda x: x[1], reverse=True)
print(sorted_footballers_by_goals)
