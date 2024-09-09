# Tip Calculator by DabossMiRA
print("Welcome to the calculator!")
total_bill = float(input("What is the total bill? $")) #Changes the datatype from String to Float since we're dealing with currencies
tip_percentage = int(input("How much tip would you like to give? 10, 12 or 15? "))

# Calculate Tip Amount
tip_amount = (total_bill * tip_percentage) / 100

number_of_people = int(input("How many people are to split the bill? "))
bill_amount = (total_bill / number_of_people) + (tip_amount/number_of_people)
final_bill = round(bill_amount, 2)
print(f"Each person should pay: ${final_bill}") #Use of (f"string") to use multiple datatypes.
