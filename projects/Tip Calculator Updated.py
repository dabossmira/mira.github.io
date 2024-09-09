# Tip Calculator by DabossMiRA
print("Welcome to the calculator!")
total_bill = input("What is the total bill? $")
total_bill = int(total_bill) #Changes the datatype from String to Integer
tip_percentage = float(input("How much tip would you like to give? 10, 12 or 15?" ))

# Calculate Tip Amount
tip_amount = (total_bill * tip_percentage) / 100

number_of_people = input("How many people are to split the bill?" )
number_of_people = int(number_of_people)
bill_amount = (total_bill / number_of_people) + (tip_amount/number_of_people)
print(f"Each person should pay ${bill_amount}") #Use of (f"string") to use multiple datatypes.
