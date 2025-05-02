from easy_shopping import Calculator

def main():
    # Create calculator instance
    calc = Calculator()
    
    # Test case 1: 7+5
    print("7 + 5 =", calc.add(7, 5))
    
    # Test case 2: 34-21
    print("34 - 21 =", calc.subtract(34, 21))
    
    # Test case 3: 54*2
    print("54 * 2 =", calc.multiply(54, 2))
    
    # Test case 4: 144/2
    print("144 / 2 =", calc.divide(144, 2))
    
    # Test case 5: 45/0
    try:
        result = calc.divide(45, 0)
        print("5. 45 / 0 =", result)
    except ZeroDivisionError as e:
        print("5. 45 / 0 = Error:", str(e))

if __name__ == "__main__":
    main()
