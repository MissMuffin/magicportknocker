import auth

seed = "skdfnksdjfn"
number_of_tickets = 10

tickets = auth.generate_tokens(seed, number_of_tickets)

print(tickets[-1])