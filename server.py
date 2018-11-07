import auth

seed = "skdfnksdjfn"
number_of_tickets = 10

ticket = auth.generate_nth_token(seed, number_of_tickets)

print(ticket)